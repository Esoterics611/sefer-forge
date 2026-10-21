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
    """One session's text: a title (kicker + lines) and a markdown body."""

    def __init__(self, kicker: str, lines: list[str], descriptor: str, body: str, talk: bool):
        self.kicker, self.lines, self.descriptor, self.body, self.talk = kicker, lines, descriptor, body, talk


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
            if plain(m.group(1)) == DESCRIPTOR:
                descriptor = m.group(1)
            else:
                lines.append(m.group(1))
    body = re.sub(r"^---\s*$", "", body, flags=re.M)  # the headings already separate the parts

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
    """transcript.md (voice-only): title, subtitle, ## topics, > quotes, footnotes."""
    return Part(title, [subtitle] if subtitle else [], "", f"::: talk\n{body.strip()}\n:::", talk=True)


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


def to_html(markdown: str) -> str:
    # -smart keeps the plain " and ' of the Hebrew (ה' and ע"פ are not quotes).
    return subprocess.run(
        ["pandoc", "-f", "markdown-smart", "-t", "html5", "--wrap=none", "--section-divs"],
        input=markdown, capture_output=True, text=True, check=True,
    ).stdout


def css_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def esc(s: str) -> str:
    return html.escape(s)


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
            opener = [f'<div class="opener{first}">']
            if p.kicker:
                opener.append(f'<div class="kicker">{esc(p.kicker)}</div>')
            if p.lines:
                opener.append(f'<div class="orn">{ORN}</div>')
                opener += [f'<div class="line">{esc(ln)}</div>' for ln in p.lines]
            opener.append("</div>")
            md.append("\n".join(opener))
        md.append(p.body)
    body = to_html("\n\n".join(md))

    header = css_string(" · ".join(x for x in (series, h1) if x))
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
    if not whole and not parts[0].talk and 'custom-style="Commentary"' not in parts[0].body:
        print("  note: no ביאור boxes yet; the session is not fully ingested")
    if UNCLEAR_COUNT:
        print(f"  note: {UNCLEAR_COUNT} UNCLEAR flag(s) in the text (not printed); resolve before publishing")

    doc, title = build_html(cfg, parts, whole, CSS.read_text(encoding="utf-8"))
    name = discourse.name if whole else f"{discourse.name}-{target.name}"
    (OUT / "html").mkdir(parents=True, exist_ok=True)
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
