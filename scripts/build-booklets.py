#!/usr/bin/env python3
"""Print the themed Shivchei HaBesht booklets to PDF.

Usage:
    python scripts/build-booklets.py              # every booklet, Hebrew
    python scripts/build-booklets.py 1 5          # booklets 1 and 5 only
    python scripts/build-booklets.py --lang en    # the English booklets
    python scripts/build-booklets.py --lang fr 3  # French booklet 3

Reads booklets/booklets.yaml (which stories go in which booklet, the titles
in each language) and the language's glossary, cuts the stories out of the
language's source, and writes output/booklets/<NN> - <title>.pdf (A5) plus
the HTML it printed from under output/booklets/html/; for --lang en|fr under
output/booklets/<lang>/. Run from the repo root.

  he  shivchei-habesht-simple.md      booklets/glossary.yaml     right to left
  en  shivchei-habesht-simple-en.md   booklets/glossary-en.yaml  left to right
  fr  shivchei-habesht-simple-fr.md   booklets/glossary-fr.yaml  left to right

The English and French sources are translations of the Hebrew one
(prompts/translate-stories-rules.md; checked by scripts/check-translation.py).

Rendering is pandoc (markdown -> HTML) plus Chrome's headless print-to-PDF,
styled by templates/booklet.css, and for English and French also
templates/booklet-latin.css (EB Garamond, from templates/fonts/). CHROME
overrides the browser path; the default is the Windows install reached from
WSL, whose paths are passed through `wslpath -w`.

Each booklet: cover, contents with an "about" note, the stories in ascending
order (UNCLEAR/MATURE comments stripped; MATURE stories get a printed
"תוכן לבוגרים" / "For mature readers" label), and a glossary of the terms
that occur in it.

To print as folded booklets: Acrobat Reader > Print > Booklet, on A4 duplex,
binding Right for Hebrew (it opens from the right) and Left for English and
French; fold and staple.
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

CONFIG = Path("booklets/booklets.yaml")
CSS = Path("templates/booklet.css")
LATIN_CSS = Path("templates/booklet-latin.css")
FONTS = Path("templates/fonts")
OUT = Path("output/booklets")
CHROME = os.environ.get("CHROME", "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
STORY_COUNT = 211          # the author's introduction + stories 1-210
GLOSSARY_FIT = ["", "tight", "tighter"]   # glossary classes in booklet-latin.css, tried in turn
HEB = "א-ת"

# Everything that differs between the languages. Series, subtitle and the
# booklet titles are in booklets.yaml; the rest is here.
LANGS = {
    "he": {
        "source": "shivchei-habesht-simple.md", "glossary": "booklets/glossary.yaml",
        "dir": "rtl", "font": "David", "header_size": "10pt", "latin": False,
        # the book's closing line, printed at the end of the last booklet
        "colophon": r"^תם ונשלם.*$",
        "summary": r"^\*\*סיכום:\*\* ?(.*)$", "summary_label": "סיכום",
        "mature": "תוכן לבוגרים",
        "story": "סיפור {}", "contents": "בחוברת זו", "glossary_title": "מילון קצר",
        "booklet_no": "חוברת {} מתוך {}",
        "count": "{} סיפורים", "count_one": "סיפור אחד", "count_intro": "הקדמת הכותב ו־{}",
        "about": 'הסיפורים בחוברת לקוחים מהספר "{series}", ונכתבו מחדש בעברית של ימינו, '
                 "בלי להוסיף ובלי להחסיר מן המעשים. אחרי כל סיפור בא סיכום קצר. "
                 "המספר שליד כל סיפור הוא מספרו בספר המקורי.",
        "about_mature": 'סיפור שמסומן "{mature}" כולל תיאורים של חטאים בענייני אישות, '
                        "של אלימות, של עלילות דם או של פרטים גופניים בוטים.",
        "about_glossary": "מילים קשות מוסברות במילון הקצר שבסוף החוברת.",
    },
    "en": {
        "source": "shivchei-habesht-simple-en.md", "glossary": "booklets/glossary-en.yaml",
        "dir": "ltr", "font": "EB Garamond", "header_size": "9.5pt", "latin": True,
        "colophon": r"^Finished and complete\..*$",
        "summary": r"^\*\*Summary:\*\* ?(.*)$", "summary_label": "Summary",
        "mature": "For mature readers",
        "story": "Story {}", "contents": "In This Booklet", "glossary_title": "Glossary",
        "booklet_no": "Booklet {} of {}",
        "count": "{} stories", "count_one": "One story", "count_intro": "The author's introduction and {}",
        "about": "The stories in this booklet come from the book *Shivchei HaBesht* "
                 "(In Praise of the Baal Shem Tov). They were retold in modern Hebrew without "
                 "adding to the events or taking anything away, and translated from that retelling "
                 "into English. Each story is followed by a short summary. The number beside each "
                 "story is its number in the original book.",
        "about_mature": 'A story marked "{mature}" contains descriptions of sexual sins, '
                        "of violence, of blood libels or of crude bodily details.",
        "about_glossary": "Hard words are explained in the short glossary at the back of the booklet.",
    },
    "fr": {
        "source": "shivchei-habesht-simple-fr.md", "glossary": "booklets/glossary-fr.yaml",
        "dir": "ltr", "font": "EB Garamond", "header_size": "9.5pt", "latin": True,
        "colophon": r"^Fin\. Louange.*$",
        "summary": r"^\*\*Résumé :\*\* ?(.*)$", "summary_label": "Résumé",
        "mature": "Pour lecteurs adultes",
        "story": "Récit {}", "contents": "Dans ce livret", "glossary_title": "Petit glossaire",
        "booklet_no": "Livret {} sur {}",
        "count": "{} récits", "count_one": "Un récit", "count_intro": "L'introduction de l'auteur et {}",
        "about": "Les récits de ce livret sont tirés du livre *Shivhei HaBesht* "
                 "(Les louanges du Baal Chem Tov). Ils ont été racontés à nouveau en hébreu moderne, "
                 "sans rien ajouter aux événements ni rien en retrancher, puis traduits en français "
                 "à partir de ce texte. Chaque récit est suivi d'un court résumé. Le numéro qui "
                 "accompagne chaque récit est son numéro dans le livre original.",
        "about_mature": "Un récit marqué « {mature} » contient des descriptions de fautes d'ordre "
                        "sexuel, de violence, d'accusations de meurtre rituel ou de détails "
                        "corporels crus.",
        "about_glossary": "Les mots difficiles sont expliqués dans le petit glossaire à la fin du livret.",
    },
}


def french_spacing(s: str) -> str:
    """No-break spaces where French typography wants them: before ; : ! ? and
    inside « ». (EB Garamond has no narrow no-break space, so U+00A0.)"""
    s = re.sub(r" ([;:!?»])", " \\1", s)
    return s.replace("« ", "« ")


def load_sections(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^(?=## )", text, flags=re.M)[1:]   # [0] is the file header
    if len(sections) != STORY_COUNT:
        sys.exit(f"{path}: expected {STORY_COUNT} '## ' sections, found {len(sections)}")
    return sections


def check_coverage(booklets: list[dict], lang: str) -> None:
    seen: dict[int, int] = {}
    for i, b in enumerate(booklets, 1):
        if lang != "he" and not b.get(lang):
            sys.exit(f"{CONFIG}: booklet {i} has no '{lang}' title")
        for s in b["stories"]:
            if s in seen:
                sys.exit(f"{CONFIG}: story {s} is in booklets {seen[s]} and {i}")
            seen[s] = i
    missing = sorted(set(range(STORY_COUNT)) - set(seen))
    if missing:
        sys.exit(f"{CONFIG}: stories in no booklet: {missing}")


def parse_section(raw: str, L: dict) -> tuple[str, str, str, bool]:
    """Return (number, title, markdown body, mature) for one '## ' section."""
    head, _, body = raw.partition("\n")
    head = head[3:].strip()
    num, sep, title = head.partition(" — ")
    if not sep:                       # the author's introduction has no number
        num, title = "", head
    mature = "MATURE:" in body
    body = re.sub(L["colophon"], "", body, flags=re.M)
    body = re.sub(r"\s*<!--.*?-->", "", body, flags=re.S)
    # The one-line summary becomes a framed box.
    body = re.sub(L["summary"], rf"::: summary\n**{L['summary_label']}**\n\n\1\n:::", body, flags=re.M)
    if L is LANGS["fr"]:
        title, body = french_spacing(title), french_spacing(body)
    return num, title, body.strip(), mature


def story_heading(num: str, title: str, mature: bool, first: bool, L: dict) -> str:
    cls = "story first" if first else "story"
    parts = [f'<h2 class="{cls}">']
    if num:
        parts.append(f'<span class="num">{html.escape(L["story"].format(num))}</span>')
    parts.append(f'<span class="title">{smart(title, L)}</span>')
    if mature:
        parts.append(f'<span class="mature">{html.escape(L["mature"])}</span>')
    parts.append("</h2>")
    return "".join(parts)


def to_html(markdown: str, L: dict) -> str:
    # Hebrew: -smart keeps the plain " and ' of the text (curly quotes face the
    # wrong way in RTL, and ' is also the geresh in ה' and מז'יבוז'). English
    # and French: +smart for curly quotes and apostrophes.
    fmt = "markdown+smart" if L["latin"] else "markdown-smart"
    return subprocess.run(
        ["pandoc", "-f", fmt, "-t", "html5", "--wrap=none"],
        input=markdown, capture_output=True, text=True, check=True,
    ).stdout


def smart(text: str, L: dict) -> str:
    """Inline text (a title, a line of the contents) as HTML, with curly quotes
    in English and French."""
    if not L["latin"]:
        return html.escape(text)
    out = to_html(text, L).strip()
    return re.sub(r"^<p>(.*)</p>$", r"\1", out, flags=re.S)


def glossary_entries(entries: list[dict], text: str, L: dict) -> list[dict]:
    found = []
    for e in entries:
        for form in e.get("forms", [e["term"]]):
            if L["latin"]:
                pattern = rf"(?<!\w){re.escape(form)}(?!\w)"
                hit = re.search(pattern, text, flags=re.I)
            else:
                hit = re.search(rf"(?<![{HEB}])[והבלמשכ]{{0,3}}{re.escape(form)}(?![{HEB}])", text)
            if hit:
                found.append(e)
                break
    return sorted(found, key=lambda e: e["term"].casefold())


def css_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_html(n: int, total: int, cfg: dict, booklet: dict, sections: list[str],
               glossary: list[dict], css: str, colophon: str, L: dict, lang: str, fit: str = "") -> str:
    series, subtitle = cfg["series"], cfg["subtitle"]
    btitle = booklet["title"] if lang == "he" else booklet[lang]
    if lang == "fr":
        series, subtitle, btitle = french_spacing(series), french_spacing(subtitle), french_spacing(btitle)
    stories = [parse_section(sections[s], L) for s in sorted(booklet["stories"])]
    numbered = sum(1 for num, *_ in stories if num)

    toc = "".join(
        f'<li><span class="tnum">{html.escape(num)}</span>{smart(title, L)}'
        + (f' <span class="mature">{html.escape(L["mature"])}</span>' if mature else "")
        + "</li>"
        for num, title, _, mature in stories
    )
    md = []
    for i, (num, title, body, mature) in enumerate(stories):
        md.append(story_heading(num, title, mature, first=(i == 0), L=L))
        md.append(body)
    stories_html = to_html("\n\n".join(md), L)

    plain = " ".join(body for _, _, body, _ in stories)
    terms = glossary_entries(glossary, plain, L)
    gloss_html = ""
    if terms:
        items = "".join(f"<dt>{smart(e['term'], L)}</dt><dd>{smart(e['def'], L)}</dd>" for e in terms)
        # After the book's closing line (the last booklet) the glossary may share its page.
        cls = " ".join(c for c in ("glossary", "after-colophon" if n == total else "", fit) if c)
        gloss_html = (f'<section class="{cls}"><h2 class="front-title">{html.escape(L["glossary_title"])}'
                      f'</h2><dl>{items}</dl></section>')

    about = [L["about"].format(series=series)]
    if any(m for *_, m in stories):
        about.append(L["about_mature"].format(mature=L["mature"]))
    if terms:
        about.append(L["about_glossary"])
    if lang == "fr":
        about = [french_spacing(p) for p in about]
    about_html = "".join(f"<p>{smart(p, L)}</p>" for p in about)

    count = L["count"].format(numbered) if numbered != 1 else L["count_one"]
    if numbered < len(stories):
        count = L["count_intro"].format(count if numbered != 1 else count.lower())
    header = css_string(f'{series}  |  {btitle}')
    title = html.escape(f'{series} {n}: {btitle}')
    lang_attr = "he" if lang == "he" else lang

    return f"""<!doctype html>
<html dir="{L['dir']}" lang="{lang_attr}"><head><meta charset="utf-8"><title>{title}</title>
<style>
{css}
@page {{ @top-center {{ content: {header}; font-family: "{L['font']}"; font-size: {L['header_size']}; color: #333; }} }}
@page :first {{ @top-center {{ content: none; }} }}
</style></head><body>
<section class="cover">
  <div class="series">{html.escape(series)}</div>
  <div class="subtitle">{html.escape(subtitle)}</div>
  <div class="rule"></div>
  <div class="no">{html.escape(L["booklet_no"].format(n, total))}</div>
  <h1>{smart(btitle, L)}</h1>
  <div class="count">{smart(count, L)}</div>
</section>
<section class="front">
  <h2 class="front-title">{html.escape(L["contents"])}</h2>
  <ol class="toc">{toc}</ol>
  <div class="about">{about_html}</div>
</section>
{stories_html}
{f'<p class="colophon">{smart(colophon, L)}</p>' if n == total else ''}
{gloss_html}
</body></html>
"""


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    src, dst = html_path.resolve(), pdf_path.resolve()
    if CHROME.endswith(".exe"):       # Windows Chrome from WSL needs Windows paths
        src, dst = (subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True,
                                   check=True).stdout.strip() for p in (src, dst))
    # Linux Chrome refuses to run as root (a container) without --no-sandbox.
    sandbox = ["--no-sandbox"] if hasattr(os, "geteuid") and os.geteuid() == 0 else []
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", *sandbox,
                    f"--print-to-pdf={dst}", str(src)],
                   check=True, capture_output=True)
    if not pdf_path.exists():
        sys.exit(f"Chrome wrote no PDF for {html_path}")


def thin_last_page(pdf_path: Path) -> bool:
    """True if the PDF's last page holds only a line or two of text (between
    the running header and the page number)."""
    try:
        import pymupdf
    except ImportError:
        return False
    page = pymupdf.open(pdf_path)[-1]
    top, bottom = 17 * 72 / 25.4, page.rect.height - 18 * 72 / 25.4
    lines = [l for b in page.get_text("dict")["blocks"] for l in b.get("lines", [])
             if top < l["bbox"][1] and l["bbox"][3] < bottom and "".join(s["text"] for s in l["spans"]).strip()]
    return len(lines) <= 2


def safe_name(s: str, lang: str) -> str:
    # Hebrew titles lose their quotes and geresh; English and French keep the apostrophe.
    chars = r'["/\\:,]' if lang != "he" else r'["\'/\\:,]'
    return re.sub(chars, "", s).strip()


def main(argv: list[str]) -> None:
    lang = "he"
    if "--lang" in argv:
        i = argv.index("--lang")
        lang = argv[i + 1] if i + 1 < len(argv) else ""
        argv = argv[:i] + argv[i + 2:]
    if lang not in LANGS:
        sys.exit(f"--lang must be one of: {', '.join(LANGS)}")
    L = LANGS[lang]
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    if lang != "he":
        cfg = {**cfg, **cfg["languages"][lang]}
    booklets = cfg["booklets"]
    check_coverage(booklets, lang)
    sections = load_sections(Path(cfg["source"] if lang == "he" else L["source"]))
    glossary = yaml.safe_load(Path(L["glossary"]).read_text(encoding="utf-8"))
    out = OUT if lang == "he" else OUT / lang
    (out / "html").mkdir(parents=True, exist_ok=True)
    css = CSS.read_text(encoding="utf-8")
    if L["latin"]:
        fonts = Path(os.path.relpath(FONTS.resolve(), (out / "html").resolve())).as_posix()
        css += "\n" + LATIN_CSS.read_text(encoding="utf-8").replace("FONTS_DIR", fonts)
    colophon = re.search(L["colophon"], sections[-1], flags=re.M).group(0).strip()
    if lang == "fr":
        colophon = french_spacing(colophon)

    wanted = [int(a) for a in argv] or range(1, len(booklets) + 1)
    for n in wanted:
        b = booklets[n - 1]
        html_path = out / "html" / f"{n:02d}.html"
        tmp = out / f"{n:02d}.pdf"                 # ASCII name for Chrome, renamed below
        # English and French: when the last page would hold only a line or two
        # (a glossary entry carried over), print again with a tighter glossary.
        for fit in (GLOSSARY_FIT if L["latin"] else [""]):
            html_path.write_text(build_html(n, len(booklets), cfg, b, sections, glossary, css, colophon, L, lang,
                                            fit), encoding="utf-8")
            tmp.unlink(missing_ok=True)
            print_pdf(html_path, tmp)
            if not thin_last_page(tmp):
                break
        final = out / f"{n:02d} - {safe_name(b['title'] if lang == 'he' else b[lang], lang)}.pdf"
        tmp.replace(final)
        print(f"  {final}")


if __name__ == "__main__":
    main(sys.argv[1:])
