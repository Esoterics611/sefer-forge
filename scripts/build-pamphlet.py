#!/usr/bin/env python3
"""Print one session, or a whole discourse, as a standalone A5 pamphlet (PDF).

Usage:
    python scripts/build-pamphlet.py discourses/003-breishis/sessions/002
    python scripts/build-pamphlet.py discourses/003-breishis          # every session
    python scripts/build-pamphlet.py <path> --png                     # also page images

A session prints from its section.md (images+voice) or transcript.md
(voice-only). A discourse prints from its discourse.md, the hand-polished
text (assembled first when the discourse is voice-only), one part per
`<!-- session: NNN -->` marker, behind a contents page.

Writes output/pamphlets/<discourse>[-<session>].pdf, the HTML it printed
from under output/pamphlets/html/, and with --png one image per page under
output/pamphlets/png/ for checking the layout. Run from the repo root.

Cover and running-header text: the book whose structure.yaml lists the
discourse supplies series/author/date; a `pamphlet:` block in the
discourse's meta.yaml overrides any of them:

    pamphlet:
      series: "קיצור ליקוטי תורה ותורה אור"   # top line of the cover
      author: "רני רנדל"
      date: "תשפ\"ז · 2026"
      title: "..."         # whole-discourse cover only (default: meta title)
      subtitle: "..."      # whole-discourse cover only
      dedication: "..."    # optional page after the cover

Rendering is pandoc (markdown -> HTML) plus Chrome's headless print-to-PDF,
styled by templates/pamphlet.css, as in build-booklets.py. CHROME overrides
the browser path. UNCLEAR flags are invisible in print; the build counts
them so nothing unresolved goes out unnoticed.

To print as a folded booklet: Acrobat Reader > Print > Booklet, binding
Right, on A4 duplex; fold and staple.
"""
from __future__ import annotations

import html
import os
from dataclasses import dataclass, field
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml")
    sys.exit(1)

CSS = Path("templates/pamphlet.css")
OUT = Path("output/pamphlets")
CHROME = os.environ.get("CHROME", "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
NIQQUD = re.compile(r"[֑-ׇ]")
FRONTMATTER = re.compile(r"\A---\n([\s\S]*?)\n---\s*\n?")
COMMENT = re.compile(r"\s*<!--.*?-->", re.S)
SESSION_MARK = re.compile(r"^<!-- session: (\S+) -->$", re.M)
SPAN = r'\[(.+?)\]\{dir="rtl"\}'
BOX_LABEL = re.compile(r'^\*\*\[■ ביאור — (.+?)\]\{dir="rtl"\}\*\*$', re.M)
# section.md's three named sections → a class for each in pamphlet.css
PARTS = {"הנסח העקרי": "nusach", "נקדות מפתח": "keys", "ביאור ופירוש": "biur"}
DESCRIPTOR = "נסח עקרי עם ביאור ופירוש"     # fixed title-block line from prompts/02
ORN = "◆ ◆ ◆"


def plain(s: str) -> str:
    return NIQQUD.sub("", s).strip()


UNCLEAR_COUNT = 0


def unflag(md: str) -> str:
    """Drop <!-- --> comments (UNCLEAR flags and the like), counting the UNCLEAR ones."""
    global UNCLEAR_COUNT
    UNCLEAR_COUNT += len(re.findall(r"<!--\s*UNCLEAR", md))
    return COMMENT.sub("", md)


def frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER.match(text)
    return ((yaml.safe_load(m.group(1)) or {}), text[m.end():]) if m else ({}, text)


def config(discourse: Path) -> dict:
    """series/author/date from the book that lists this discourse, then meta.yaml's pamphlet:."""
    meta = yaml.safe_load((discourse / "meta.yaml").read_text(encoding="utf-8")) or {}
    slug = meta.get("slug") or discourse.name.split("-", 1)[-1]
    cfg: dict = {"title": meta.get("title") or ""}
    for structure in sorted(Path("books").glob("*/structure.yaml")):
        data = yaml.safe_load(structure.read_text(encoding="utf-8")) or {}
        if any(slug in (ch.get("discourses") or []) for ch in data.get("chapters") or []):
            book = yaml.safe_load((structure.parent / "metadata.yaml").read_text(encoding="utf-8")) or {}
            cfg.update(series=book.get("title", ""), author=book.get("author", ""), date=book.get("date", ""))
            break
    cfg.update({k: v for k, v in (meta.get("pamphlet") or {}).items() if v})
    cfg["meta"] = meta
    return cfg


class Part:
    """One session's text: a title (kicker + lines) and a markdown body. A
    session in the paired layout carries its pairs instead, and its body is
    made by the page engine (paginate)."""

    def __init__(self, kicker: str, lines: list[str], descriptor: str, body: str, talk: bool,
                 pairs: list | None = None, tail: str = ""):
        self.kicker, self.lines, self.descriptor, self.body, self.talk = kicker, lines, descriptor, body, talk
        self.pairs, self.tail = pairs, tail


DIV = re.compile(r'^::: \{custom-style="(Nusach|Commentary)"\}\n(.*?)\n:::', re.M | re.S)


def paragraphs(md: str) -> list[str]:
    return [" ".join(x.split()) for x in re.split(r"\n\s*\n", md) if x.strip()]


def section_part(md: str) -> Part:
    """section.md: title block, then ## הנוסח העיקרי / נקודות מפתח / ביאור ופירוש."""
    m = re.search(r"^## ", md, re.M)
    head, body = (md[:m.start()], md[m.start():]) if m else ("", md)
    kicker, lines, descriptor = "", [], ""
    for ln in head.splitlines():
        ln = ln.strip()
        if m := re.fullmatch(r"\*\*" + SPAN + r"\*\*", ln):
            kicker = m.group(1)
        elif re.fullmatch(r"\*" + SPAN + r"\*", ln):
            continue                                  # "גרסה א' · סשן 002" — working metadata
        elif m := re.fullmatch(SPAN, ln):
            if m.group(1).replace("•", "").strip() == "":
                continue                                  # the title block's • • • separator
            if plain(m.group(1)) == DESCRIPTOR:
                descriptor = m.group(1)
            else:
                lines.append(m.group(1))
    body = re.sub(r"^---\s*$", "", body, flags=re.M)  # the headings already separate the parts

    sections = re.split(r"^## (.+)$", body, flags=re.M)        # ['', name, text, name, text...]
    named = {plain(n): s for n, s in zip(sections[1::2], sections[2::2])}
    if "הנסח והביאור" in named:                                # the paired layout
        paired = named["הנסח והביאור"]
        pairs: list = []
        for kind, content in DIV.findall(paired):
            if kind == "Nusach":
                pairs.append((paragraphs(content), []))
            elif pairs:
                pairs[-1][1].extend(paragraphs(content))
        notes = "\n\n".join(ln for ln in paired.splitlines() if ln.startswith("[^"))
        keys = named.get("נקדות מפתח", "")
        tail = notes + (f"\n\n## [◆]{{.orn}}נְקֻדּוֹת מַפְתֵּחַ[◆]{{.orn}} {{.part .keys}}\n\n{keys}" if keys else "")
        return Part(kicker, lines, descriptor, "", talk=False, pairs=pairs, tail=tail)

    def heading(m: re.Match) -> str:
        cls = PARTS.get(plain(m.group(1)))
        if not cls:
            return m.group(0)
        return f"## [◆]{{.orn}}{m.group(1)}[◆]{{.orn}} {{.part .{cls}}}"

    body = re.sub(r"^## (.+)$", heading, body, flags=re.M)
    body = BOX_LABEL.sub(lambda m: f'<p class="box-label"><span class="kind">ביאור</span>'
                                   f'{html.escape(m.group(1))}</p>', body)
    return Part(kicker, lines, descriptor, body, talk=False)


def talk_part(title: str, subtitle: str, body: str) -> Part:
    """transcript.md (voice-only): title, subtitle, ## topics, > quotes, footnotes.
    A lesson that quotes the text it teaches is paired like a session: each
    topic heading and passage read (the `>` quotes) on top, the explanation
    that follows them below."""
    part = Part(title, [subtitle] if subtitle else [], "", f"::: talk\n{body.strip()}\n:::", talk=True)
    pairs, notes = talk_pairs(body)
    if pairs:
        part.pairs, part.tail = pairs, notes
    return part


def talk_pairs(body: str) -> tuple[list, str]:
    """[(heading and quoted passage, explanation paragraphs)] of a transcript."""
    pairs: list = []
    notes: list[str] = []
    pending: list[str] = []                 # explanation before anything quoted
    for block in [b.strip() for b in re.split(r"\n\s*\n", body) if b.strip()]:
        if block.startswith("[^"):
            notes.append(block)
        elif block.startswith("## "):
            if pairs and not pairs[-1][1] and not any(x.startswith(">") for x in pairs[-1][0]):
                pairs[-1][0].append("### " + block[3:])          # headings in a row
            else:
                pairs.append((["### " + block[3:]], []))
        elif block.startswith(">"):
            # A passage joins its topic's heading on top, even past a lead-in
            # line ("עכשיו נראה..."), which then opens the explanation.
            quoted = pairs and any(x.startswith(">") for x in pairs[-1][0])
            if pairs and (not quoted or not pairs[-1][1]):
                pairs[-1][0].append(block)
            else:
                pairs.append(([block], []))
        elif pairs:
            pairs[-1][1].append(" ".join(block.split()))
        else:
            pending.append(" ".join(block.split()))
    if not any(any(x.startswith(">") for x in text) for text, _ in pairs):
        return [], ""                       # nothing quoted: a talk, printed as it runs
    if pending:
        pairs[0][1][:0] = pending
    return pairs, "\n\n".join(notes)


def parse_part(md: str) -> Part:
    """A fragment of discourse.md: an assembled transcript starts with '# title'."""
    md = md.strip()
    if md.startswith("# "):
        title, _, rest = md.partition("\n")
        rest = rest.lstrip("\n")
        sub = ""
        if m := re.match(r"\*(.+)\*\n", rest):
            sub, rest = m.group(1), rest[m.end():]
        return talk_part(title[2:].strip(), sub, rest)
    return section_part(md)


def session_parts(session: Path) -> list[Part]:
    for name in ("section.md", "transcript.md"):
        f = session / name
        if f.exists():
            fm, body = frontmatter(f.read_text(encoding="utf-8"))
            body = unflag(body)
            if name == "section.md":
                return [section_part(body)]
            return [talk_part(fm.get("title", ""), fm.get("subtitle", ""), body)]
    sys.exit(f"{session}: no section.md or transcript.md yet")


def discourse_parts(discourse: Path, meta: dict) -> list[Part]:
    if meta.get("type") == "voice-only":
        subprocess.run([sys.executable, "scripts/assemble-discourse.py", str(discourse)],
                       check=True, capture_output=True)
    _, body = frontmatter((discourse / "discourse.md").read_text(encoding="utf-8"))
    chunks = SESSION_MARK.split(body)[1:]            # [name, text, name, text, ...]
    if not chunks:
        sys.exit(f"{discourse}/discourse.md has no sessions; run scripts/assemble-discourse.py first")
    return [parse_part(unflag(text)) for text in chunks[1::2]]


SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def to_html(markdown: str) -> str:
    # Superscript digits (note marks in older OCR) are in neither house font:
    # set them as real superscripts.
    markdown = re.sub(r"[⁰¹²³⁴-⁹]+", lambda m: f"^{m.group(0).translate(SUPERSCRIPT)}^", markdown)
    # A dash belongs to the word before it: never let a line start with one.
    markdown = re.sub(r" (?=[—–] )", "\u00a0", markdown)
    # -smart keeps the plain " and ' of the Hebrew (ה' and ע"פ are not quotes).
    return subprocess.run(
        ["pandoc", "-f", "markdown-smart", "-t", "html5", "--wrap=none", "--section-divs"],
        input=markdown, capture_output=True, text=True, check=True,
    ).stdout


# --- the page engine: each page holds a cut of the text and its explanation ---------------

PIECE_WORDS = 45          # explanation pieces: sentences grouped up to this many words
MARK_COLOUR = "#fe0102"   # measuring and checking only; never in the final PDF
MEASURE_MM = 5000         # height of the tall page the pieces are measured on
SLACK_PT = 4              # packing margin; the page check repacks any page that still spills
# Markers read the top of the line where their piece starts and move nothing.
# At a paragraph's start: out of the flow (.mk, absolute in its place). Inside a
# paragraph: a box of no width or height whose text overflows it (.mki), since
# Chrome drops an absolute marker that falls on a line break. Each kind fails
# where the other works.
MARK_CSS = (f"\n.mk, .mki {{ font-size: 2pt; color: {MARK_COLOUR}; unicode-bidi: isolate; white-space: nowrap; }}"
            "\n.mk { position: absolute; }"
            "\n.mki { display: inline-block; width: 0; height: 0; overflow: visible; vertical-align: top; "
            "line-height: 0; }\n")
TEXT_SHARE = 0.5          # the text at a page's top stays under this share


@dataclass
class Piece:
    md: str               # RTL markdown of a whole paragraph, or of sentences of one
    para: int             # paragraph id: pieces of one paragraph merge on a page
    h: float = 0.0


@dataclass
class Unit:
    text: list[str]       # the text cut's paragraphs (RTL markdown)
    pieces: list[Piece]   # its explanation, in pieces
    lead: str = ""        # its first words, for the continuation line
    text_h: float = 0.0
    text_pieces: list[Piece] = field(default_factory=list)   # a cut with no explanation, split


def inner(md: str) -> str:
    m = re.fullmatch(r'\[(.*)\]\{dir="rtl"[^}]*\}', md.strip(), flags=re.S)
    return m.group(1) if m else md


def rtl(text: str, cls: str = "") -> str:
    return f'[{text}]{{dir="rtl"{" ." + cls if cls else ""}}}'


def split_paragraph(md: str, para: int) -> list[Piece]:
    """A paragraph as pieces of whole sentences, up to PIECE_WORDS words each."""
    sentences = re.split(r"(?<=[.?!:])\s+(?=\S)", inner(md))
    pieces, cur = [], []
    for s in sentences:
        if cur and len(" ".join(cur + [s]).split()) > PIECE_WORDS:
            pieces.append(" ".join(cur))
            cur = []
        cur.append(s)
    if cur:
        pieces.append(" ".join(cur))
    return [Piece(rtl(x), para) for x in pieces]


def make_units(part: Part, start_para: int) -> tuple[list[Unit], int]:
    units, para = [], start_para
    for text, expl in part.pairs:
        pieces = []
        for md in expl:
            pieces += split_paragraph(md, para)
            para += 1
        # The continuation line quotes the passage itself (a quote, not its heading).
        quoted = [x for x in text if x.startswith(">")] or text
        words = re.sub(r"\*\*|\[\^[^\]]+\]|^(#+|>)\s*", "", " ".join(inner(x) for x in quoted)).split()
        lead = " ".join(words[:6]) + ("…" if len(words) > 6 else "")
        u = Unit(text, pieces, lead)
        if not pieces:                       # text with no explanation may run over pages
            for md in text:
                u.text_pieces += split_paragraph(md, para)
                para += 1
        units.append(u)
    return units, para


def mark(md: str, label: str) -> str:
    """Put an invisible position marker at the start of a paragraph's text."""
    tag = f'<span class="mk" dir="ltr">{label}</span>'
    m = re.match(r"(#+ |> ?|\[)", md)
    return md[:m.end()] + tag + md[m.end():] if m else tag + md


def marked_paragraphs(pieces: list[Piece], prefix: str) -> list[str]:
    """Pieces joined back into their paragraphs, as the page sets them, with a
    marker where each piece starts: piece heights then add up exactly."""
    out, last = [], None
    for k, pc in enumerate(pieces):
        cls = "mki" if pc.para == last else "mk"
        bit = f'<span class="{cls}" dir="ltr">{prefix}{k}</span>' + inner(pc.md)
        if pc.para == last:
            out[-1] = rtl(inner(out[-1]) + " " + bit)
        else:
            out.append(rtl(bit))
        last = pc.para
    return out


def cont_head(u: Unit) -> str:
    return (f'<p class="cont-head"><span class="label">המשך הביאור על</span> '
            f'“{esc(re.sub(r"<[^>]+>", "", u.lead))}”</p>')


def page_md(units: list[Unit], page: dict, markers: bool, label: str) -> str:
    """One page group: the text cut(s) on top, the explanation below."""
    top: list[str] = []
    if page["cont"] is not None:
        top.append(cont_head(units[page["cont"]]))
    for ui in page["texts"]:
        for md in units[ui].text:
            if ".cont" in md.split("]{")[-1] and top and not top[-1].startswith("<"):
                top[-1] = rtl(inner(top[-1]) + " " + inner(md))          # one printed paragraph
            else:
                top.append(md)
    for pc in page["text_pieces"]:
        top.append(pc.md)
    if markers:
        if top and top[0].startswith("<p"):
            top[0] = top[0].replace("<p class=\"cont-head\">", f'<p class="cont-head"><span class="mk" dir="ltr">{label}</span>', 1)
        elif top:
            top[0] = mark(top[0], label)
    expl: list[str] = []
    last_para = None
    for pc in page["pieces"]:
        if pc.para == last_para:
            expl[-1] = rtl(inner(expl[-1]) + " " + inner(pc.md))
        else:
            expl.append(pc.md)
        last_para = pc.para
    out = ["::: {.pg}", "::: {.nusach}", *[x + "\n" for x in top], ":::"]
    if expl:
        out += ["::: {.biur}", *[x + "\n" for x in expl], ":::"]
    out.append(":::")
    return "\n".join(out)


def measure(units: list[Unit], css: str, work: Path, notes: list[str] | None = None,
            openers: dict[str, str] | None = None) -> float:
    """Render every text cut and piece once on a tall page at the true width and
    read their heights from the marker positions. Returns the continuation
    line's height."""
    notes = notes or []
    md = [f'<div class="opener first"><span class="mk" dir="ltr">O{k}</span>{h}</div>\n'
          f'::: {{.pg}}\n<p><span class="mk" dir="ltr">Q{k}</span></p>\n:::' for k, h in (openers or {}).items()]
    for ui, u in enumerate(units):
        body = ["::: {.pg}", "::: {.nusach}", cont_head(u).replace('<p class="cont-head">',
                f'<p class="cont-head"><span class="mk" dir="ltr">C{ui}</span>', 1) + "\n"]
        if u.text_pieces:
            body += [x + "\n" for x in marked_paragraphs(u.text_pieces, f"X{ui}.")]
        else:
            body += [(mark(x, f"T{ui}") if i == 0 else x) + "\n" for i, x in enumerate(u.text)]
        body.append(":::")
        if u.pieces:
            body += ["::: {.biur}"] + [x + "\n" for x in marked_paragraphs(u.pieces, f"P{ui}.")] + [":::"]
        body.append(":::")
        md.append("\n".join(body))
    md.append('::: {.pg}\n<p><span class="mk" dir="ltr">END</span></p>\n:::')
    md += notes
    # The pamphlet's own width and side margins: a marker at a line's right end
    # (where a Hebrew line starts) must land in the margin, not off the page.
    extra = (f"@page {{ size: 148mm {MEASURE_MM}mm; margin: 0 16mm; "
             "@top-center { content: none; } @bottom-center { content: none; } }\n"
             ".pg { break-before: auto !important; break-inside: avoid; }\n"
             + MARK_CSS)
    doc = f"""<!doctype html><html dir="rtl" lang="he"><head><meta charset="utf-8">
<style>{css}\n{extra}</style></head><body>{to_html(chr(10).join(md))}</body></html>"""
    pos = render_marks(doc, work / "measure")
    page_h = MEASURE_MM * 72 / 25.4
    y = {k: pg * page_h + yy for k, (pg, yy) in pos.items()}
    order = sorted(y, key=y.get)
    nxt = {a: b for a, b in zip(order, order[1:])}

    def gap(label: str) -> float:
        return y[nxt[label]] - y[label] if label in nxt else 0.0

    for ui, u in enumerate(units):
        # The text block: from its first line to the first explanation piece, which
        # takes in the block's rule and the space under it. (C, the continuation line
        # measured above it, is not part of it.)
        u.text_h = y[f"P{ui}.0"] - y[f"T{ui}"] if u.pieces else 0.0
        for k, pc in enumerate(u.pieces):
            pc.h = gap(f"P{ui}.{k}")
        for k, pc in enumerate(u.text_pieces):
            pc.h = gap(f"X{ui}.{k}")
    cont = [y[f"T{ui}"] - y[f"C{ui}"] for ui in range(len(units)) if f"T{ui}" in y]
    for k in (openers or {}):
        OPENER_H[k] = y[f"Q{k}"] - y[f"O{k}"]
    return max(cont) if cont else 0.0


OPENER_H: dict[str, float] = {}       # a part's title block, when it shares the first page


def render_marks(doc: str, stem: Path) -> dict[str, tuple[int, float]]:
    """Print an HTML page and return each marker's (page, y) in points."""
    import pymupdf
    html_path, pdf = stem.with_suffix(".html"), stem.with_suffix(".pdf")
    html_path.write_text(doc, encoding="utf-8")
    pdf.unlink(missing_ok=True)
    print_pdf(html_path, pdf)
    want = int(MARK_COLOUR[1:], 16)
    pos: dict[str, tuple[int, float]] = {}
    for pno, page in enumerate(pymupdf.open(pdf)):
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                # Bidi can cut one marker into touching runs ("T", "0"); a line can also
                # hold two markers. Join runs that touch, keep the others apart.
                bits = sorted((s for s in l["spans"] if s["color"] == want and s["text"].strip()),
                              key=lambda s: s["bbox"][0])
                groups: list[list] = []
                for s in bits:
                    if groups and s["bbox"][0] - groups[-1][-1]["bbox"][2] < 0.6:
                        groups[-1].append(s)
                    else:
                        groups.append([s])
                for g in groups:
                    pos.setdefault("".join(s["text"].strip() for s in g), (pno, min(s["bbox"][1] for s in g)))
    return pos


def pack(units: list[Unit], cont_h: float, budgets: dict[int, float], area: float) -> list[dict]:
    """Fill pages: each opens with the text its explanation needs, then the explanation.
    budgets[n] narrows page n after a spill."""
    pages: list[dict] = []

    def new(cont: int | None = None) -> dict:
        p = {"texts": [], "text_pieces": [], "pieces": [], "cont": cont, "h": cont_h if cont is not None else 0.0,
             "text_h": 0.0}
        pages.append(p)
        return p

    def room(p: dict) -> float:
        return budgets.get(pages.index(p), area - SLACK_PT) - p["h"]

    page = new()
    for ui, u in enumerate(units):
        if u.pieces:
            need = u.text_h + u.pieces[0].h
            crowded = page["text_h"] and page["text_h"] + u.text_h > area * TEXT_SHARE
            if (page["texts"] or page["pieces"] or page["text_pieces"]) and (need > room(page) or crowded):
                page = new()
            page["texts"].append(ui)
            page["h"] += u.text_h
            page["text_h"] += u.text_h
            for pc in u.pieces:
                if pc.h > room(page) and page["pieces"]:
                    page = new(cont=ui)
                page["pieces"].append(pc)
                page["h"] += pc.h
        else:
            # Text with no explanation (read past, or never read) follows the
            # explanation on pages of its own: on top of another passage's
            # explanation it would read as the passage explained.
            if page["pieces"]:
                page = new()
            for pc in u.text_pieces:
                if pc.h > room(page) and (page["texts"] or page["pieces"] or page["text_pieces"]):
                    page = new()
                page["text_pieces"].append(pc)
                page["h"] += pc.h
                page["text_h"] += pc.h
    return [p for p in pages if p["texts"] or p["pieces"] or p["text_pieces"] or p["cont"] is not None]


def text_area(css: str) -> float:
    """Height of the page's text area in points, from the stylesheet's @page margins."""
    m = re.search(r"@page\s*\{[^}]*?margin:\s*([\d.]+)mm\s+[\d.]+mm\s+([\d.]+)mm", css, re.S)
    top, bottom = (float(m.group(1)), float(m.group(2))) if m else (18.0, 19.0)
    return (210 - top - bottom) * 72 / 25.4


def paginate(cfg: dict, parts: list[Part], whole: bool, css: str, work: Path) -> int:
    """Lay out every paired part page by page, verify that no page group spills,
    and set each part's body. Returns the number of paired pages."""
    paired = [p for p in parts if p.pairs]
    if not paired:
        return 0
    para, plan = 0, []
    for p in paired:
        units, para = make_units(p, para)
        plan.append(units)
    all_units = [u for us in plan for u in us]
    notes = [ln for p in paired for ln in p.tail.splitlines() if ln.startswith("[^")]
    openers = {str(i): opener_html(p) for i, p in enumerate(paired) if whole and p.kicker}
    cont_h = measure(all_units, css, work, notes, openers)
    area = text_area(css)
    budgets: list[dict[int, float]] = [dict() for _ in plan]
    for k in openers:                     # the title block takes the top of the first page
        budgets[int(k)][0] = area - SLACK_PT - OPENER_H[k]
    for attempt in range(8):
        layouts = [pack(us, cont_h, budgets[i], area) for i, us in enumerate(plan)]
        for i, (p, units, pages) in enumerate(zip(paired, plan, layouts)):
            p.body = "\n\n".join(page_md(units, pg, True, f"G{i}.{n}") for n, pg in enumerate(pages)) \
                + f'\n\n<p><span class="mk" dir="ltr">G{i}.end</span></p>\n\n' + p.tail
        doc, _ = build_html(cfg, parts, whole, css + MARK_CSS)
        pos = render_marks(doc, work / "verify")
        if not pos:
            sys.exit("page check found no markers: the layout cannot be verified")
        spilled = False
        for i, pages in enumerate(layouts):
            starts = [pos.get(f"G{i}.{n}", (None, 0))[0] for n in range(len(pages))] + [pos.get(f"G{i}.end", (None, 0))[0]]
            for n in range(len(pages)):
                a, b = starts[n], starts[n + 1]
                if a is None or b is None:
                    continue
                last_group = n + 1 == len(pages)
                if (b > a) if last_group else (b - a != 1):
                    spilled = True
                    used = pages[n]["h"]
                    last = (pages[n]["pieces"] or pages[n]["text_pieces"] or [Piece("", -1, used * 0.1)])[-1].h
                    budgets[i][n] = min(budgets[i].get(n, area - SLACK_PT - OPENER_H.get(str(i), 0) * (n == 0)),
                                        used - last - 0.5)
        if not spilled:
            break
    for p, units, pages in zip(paired, plan, layouts):
        p.body = "\n\n".join(page_md(units, pg, False, "") for pg in pages) + "\n\n" + p.tail
    print(f"  page check: {attempt + 1} render(s)" + (", a page group still spills: check the pages" if spilled else ", every page holds its text and explanation"))
    return sum(len(x) for x in layouts)


def css_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def esc(s: str) -> str:
    return html.escape(s)


def opener_html(p: Part) -> str:
    """A part's title block in a whole-discourse pamphlet."""
    out = [f'<div class="kicker">{esc(p.kicker)}</div>'] if p.kicker else []
    if p.lines:
        out.append(f'<div class="orn">{ORN}</div>')
        out += [f'<div class="line">{esc(ln)}</div>' for ln in p.lines]
    return "".join(out)


def build_html(cfg: dict, parts: list[Part], whole: bool, css: str) -> tuple[str, str]:
    if whole:
        h1 = cfg.get("title") or parts[0].kicker
        lines = [cfg["subtitle"]] if cfg.get("subtitle") else []
        descriptor = ""
    else:
        h1, lines, descriptor = parts[0].kicker, parts[0].lines, parts[0].descriptor
    series = cfg.get("series", "")

    cover = ['<section class="cover">']
    if series:
        cover.append(f'<div class="series">{esc(series)}</div><div class="top-rule"></div>')
    cover.append('<div class="middle">')
    cover.append(f"<h1>{esc(h1)}</h1>")
    if lines:
        cover.append(f'<div class="orn">{ORN}</div>')
        cover += [f'<div class="line">{esc(ln)}</div>' for ln in lines]
    if descriptor:
        cover.append(f'<div class="descriptor">{esc(descriptor)}</div>')
    cover.append("</div>")
    if cfg.get("author"):
        cover.append(f'<div class="byline">{esc(cfg["author"])}</div>')
    if cfg.get("date"):
        cover.append(f'<div class="date">{esc(cfg["date"])}</div>')
    cover.append("</section>")

    front = []
    if cfg.get("dedication"):
        front.append(f'<section class="dedication"><div>{esc(cfg["dedication"])}</div></section>')
    if whole and sum(1 for p in parts if p.kicker) > 1:
        items = "".join(
            f"<li>{esc(p.kicker)}" + (f'<span class="sub">{esc(" · ".join(p.lines))}</span>' if p.lines else "")
            + "</li>" for p in parts if p.kicker)
        front.append(f'<section class="contents"><h2>תוכן</h2><ol>{items}</ol></section>')

    md = []
    for i, p in enumerate(parts):
        if whole:
            first = " first" if i == 0 and not front else ""
            if not p.kicker and i > 0:
                # No title: the session continues the one before, on the same page.
                md.append(f'<div class="opener cont"><div class="orn">{ORN}</div></div>')
                md.append(p.body)
                continue
            md.append(f'<div class="opener{first}{" paired" if p.pairs else ""}">{opener_html(p)}</div>')
        md.append(p.body)
    body = to_html("\n\n".join(md))

    parts = [x for x in (series, h1) if x]
    if len(parts) == 2 and plain(parts[0]) == plain(parts[1]):
        parts = parts[:1]                      # a book named like its discourse
    header = css_string(" · ".join(parts))
    doc = f"""<!doctype html>
<html dir="rtl" lang="he"><head><meta charset="utf-8"><title>{esc(h1)}</title>
<style>
{css}
@page {{ @top-center {{ content: {header}; font-family: "David"; font-size: 9.5pt; color: #5a5246; }} }}
@page :first {{ @top-center {{ content: none; }} }}
</style></head><body>
{"".join(cover)}
{"".join(front)}
{body}
<div class="finis">{ORN}</div>
</body></html>
"""
    return doc, h1


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    src, dst = html_path.resolve(), pdf_path.resolve()
    if CHROME.endswith(".exe"):       # Windows Chrome from WSL needs Windows paths
        src, dst = (subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True,
                                   check=True).stdout.strip() for p in (src, dst))
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={dst}", str(src)],
                   check=True, capture_output=True)
    if not pdf_path.exists():
        sys.exit(f"Chrome wrote no PDF for {html_path}")


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__.split("\n\n")[1])
        return 1
    target = Path(args[0].rstrip("/"))
    whole = (target / "sessions").is_dir()
    discourse = target if whole else target.parent.parent
    cfg = config(discourse)
    parts = discourse_parts(discourse, cfg["meta"]) if whole else session_parts(target)

    # Preflight: what a printed product should not carry unnoticed.
    if not whole and not parts[0].talk and not parts[0].pairs and 'custom-style="Commentary"' not in parts[0].body:
        print("  note: no explanation in section.md yet; the session is not fully ingested")
    if UNCLEAR_COUNT:
        print(f"  note: {UNCLEAR_COUNT} UNCLEAR flag(s) in the text (not printed); resolve before publishing")

    css = CSS.read_text(encoding="utf-8")
    name = discourse.name if whole else f"{discourse.name}-{target.name}"
    (OUT / "html").mkdir(parents=True, exist_ok=True)
    work = OUT / "html" / f".{name}"
    work.mkdir(exist_ok=True)
    paired_pages = paginate(cfg, parts, whole, css, work)
    if paired_pages:
        print(f"  paired layout: {paired_pages} pages of text with its explanation")
    doc, title = build_html(cfg, parts, whole, css)
    html_path = OUT / "html" / f"{name}.html"
    html_path.write_text(doc, encoding="utf-8")
    pdf = OUT / f"{name}.pdf"
    pdf.unlink(missing_ok=True)
    print_pdf(html_path, pdf)
    pages = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                                         text=True).stdout)
    print(f"Built: {pdf}  ({pages.group(1) if pages else '?'} pages · {title})")

    if "--png" in argv:
        png_dir = OUT / "png"
        png_dir.mkdir(exist_ok=True)
        for old in png_dir.glob(f"{name}-*.png"):
            old.unlink()
        subprocess.run(["pdftoppm", "-png", "-r", "80", str(pdf), str(png_dir / name)], check=True)
        print(f"Pages: {png_dir}/{name}-*.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
