#!/usr/bin/env python3
"""Print the themed Shivchei HaBesht booklets to PDF.

Usage:
    python scripts/build-booklets.py          # every booklet
    python scripts/build-booklets.py 1 5      # booklets 1 and 5 only

Reads booklets/booklets.yaml (which stories go in which booklet) and
booklets/glossary.yaml, cuts the stories out of shivchei-habesht-simple.md,
and writes output/booklets/<NN> - <title>.pdf (A5) plus the HTML it printed
from under output/booklets/html/. Run from the repo root.

Rendering is pandoc (markdown -> HTML) plus Chrome's headless print-to-PDF,
styled by templates/booklet.css. CHROME overrides the browser path; the
default is the Windows install reached from WSL, whose paths are passed
through `wslpath -w`.

Each booklet: cover, contents with an "about" note, the stories in ascending
order (UNCLEAR/MATURE comments stripped; MATURE stories get a printed
"תוכן לבוגרים" label), and a glossary of the terms that occur in it.

To print as folded booklets: Acrobat Reader > Print > Booklet, binding Right
(Hebrew opens from the right), on A4 duplex; fold and staple.
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
GLOSSARY = Path("booklets/glossary.yaml")
CSS = Path("templates/booklet.css")
OUT = Path("output/booklets")
CHROME = os.environ.get("CHROME", "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe")
STORY_COUNT = 211          # הקדמת הכותב + stories 1-210
MATURE_LABEL = "תוכן לבוגרים"
COLOPHON = re.compile(r"^תם ונשלם.*$", re.M)   # the book's closing line, printed at the end of the last booklet
HEB = "א-ת"


def load_sections(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^(?=## )", text, flags=re.M)[1:]   # [0] is the file header
    if len(sections) != STORY_COUNT:
        sys.exit(f"{path}: expected {STORY_COUNT} '## ' sections, found {len(sections)}")
    return sections


def check_coverage(booklets: list[dict]) -> None:
    seen: dict[int, int] = {}
    for i, b in enumerate(booklets, 1):
        for s in b["stories"]:
            if s in seen:
                sys.exit(f"{CONFIG}: story {s} is in booklets {seen[s]} and {i}")
            seen[s] = i
    missing = sorted(set(range(STORY_COUNT)) - set(seen))
    if missing:
        sys.exit(f"{CONFIG}: stories in no booklet: {missing}")


def parse_section(raw: str) -> tuple[str, str, str, bool]:
    """Return (number, title, markdown body, mature) for one '## ' section."""
    head, _, body = raw.partition("\n")
    head = head[3:].strip()
    num, sep, title = head.partition(" — ")
    if not sep:                       # הקדמת הכותב has no number
        num, title = "", head
    mature = "MATURE:" in body
    body = COLOPHON.sub("", body)
    body = re.sub(r"\s*<!--.*?-->", "", body, flags=re.S)
    # The one-line summary becomes a framed box.
    body = re.sub(r"^\*\*סיכום:\*\* ?(.*)$", r"::: summary\n**סיכום**\n\n\1\n:::", body, flags=re.M)
    return num, title, body.strip(), mature


def story_heading(num: str, title: str, mature: bool, first: bool) -> str:
    cls = "story first" if first else "story"
    parts = [f'<h2 class="{cls}">']
    if num:
        parts.append(f'<span class="num">סיפור {html.escape(num)}</span>')
    parts.append(f'<span class="title">{html.escape(title)}</span>')
    if mature:
        parts.append(f'<span class="mature">{MATURE_LABEL}</span>')
    parts.append("</h2>")
    return "".join(parts)


def to_html(markdown: str) -> str:
    # -smart keeps the plain " and ' of the Hebrew text (curly quotes face the
    # wrong way in RTL, and ' is also the geresh in ה' and מז'יבוז').
    return subprocess.run(
        ["pandoc", "-f", "markdown-smart", "-t", "html5", "--wrap=none"],
        input=markdown, capture_output=True, text=True, check=True,
    ).stdout


def glossary_entries(entries: list[dict], text: str) -> list[dict]:
    found = []
    for e in entries:
        for form in e.get("forms", [e["term"]]):
            if re.search(rf"(?<![{HEB}])[והבלמשכ]{{0,3}}{re.escape(form)}(?![{HEB}])", text):
                found.append(e)
                break
    return sorted(found, key=lambda e: e["term"])


def css_string(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_html(n: int, total: int, cfg: dict, booklet: dict, sections: list[str],
               glossary: list[dict], css: str, colophon: str) -> str:
    stories = [parse_section(sections[s]) for s in sorted(booklet["stories"])]
    numbered = sum(1 for num, *_ in stories if num)

    toc = "".join(
        f'<li><span class="tnum">{html.escape(num)}</span>{html.escape(title)}'
        + (f' <span class="mature">{MATURE_LABEL}</span>' if mature else "")
        + "</li>"
        for num, title, _, mature in stories
    )
    md = []
    for i, (num, title, body, mature) in enumerate(stories):
        md.append(story_heading(num, title, mature, first=(i == 0)))
        md.append(body)
    stories_html = to_html("\n\n".join(md))

    plain = " ".join(body for _, _, body, _ in stories)
    terms = glossary_entries(glossary, plain)
    gloss_html = ""
    if terms:
        items = "".join(f"<dt>{html.escape(e['term'])}</dt><dd>{html.escape(e['def'])}</dd>" for e in terms)
        gloss_html = f'<section class="glossary"><h2 class="front-title">מילון קצר</h2><dl>{items}</dl></section>'

    about = [
        f'הסיפורים בחוברת לקוחים מהספר "{cfg["series"]}", ונכתבו מחדש בעברית של ימינו, '
        "בלי להוסיף ובלי להחסיר מן המעשים. אחרי כל סיפור בא סיכום קצר. "
        "המספר שליד כל סיפור הוא מספרו בספר המקורי.",
    ]
    if any(m for *_, m in stories):
        about.append(f'סיפור שמסומן "{MATURE_LABEL}" כולל תיאורים של חטאים בענייני אישות, '
                     "של אלימות, של עלילות דם או של פרטים גופניים בוטים.")
    if terms:
        about.append("מילים קשות מוסברות במילון הקצר שבסוף החוברת.")
    about_html = "".join(f"<p>{html.escape(p)}</p>" for p in about)

    count = f"{numbered} סיפורים" if numbered != 1 else "סיפור אחד"
    if numbered < len(stories):
        count = "הקדמת הכותב ו־" + count
    header = css_string(f'{cfg["series"]}  |  {booklet["title"]}')
    title = html.escape(f'{cfg["series"]} {n}: {booklet["title"]}')

    return f"""<!doctype html>
<html dir="rtl" lang="he"><head><meta charset="utf-8"><title>{title}</title>
<style>
{css}
@page {{ @top-center {{ content: {header}; font-family: "David"; font-size: 10pt; color: #333; }} }}
@page :first {{ @top-center {{ content: none; }} }}
</style></head><body>
<section class="cover">
  <div class="series">{html.escape(cfg["series"])}</div>
  <div class="subtitle">{html.escape(cfg["subtitle"])}</div>
  <div class="rule"></div>
  <div class="no">חוברת {n} מתוך {total}</div>
  <h1>{html.escape(booklet["title"])}</h1>
  <div class="count">{count}</div>
</section>
<section class="front">
  <h2 class="front-title">בחוברת זו</h2>
  <ol class="toc">{toc}</ol>
  <div class="about">{about_html}</div>
</section>
{stories_html}
{f'<p class="colophon">{html.escape(colophon)}</p>' if n == total else ''}
{gloss_html}
</body></html>
"""


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


def safe_name(s: str) -> str:
    return re.sub(r'["\'/\\:,]', "", s).strip()


def main(argv: list[str]) -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    booklets = cfg["booklets"]
    check_coverage(booklets)
    sections = load_sections(Path(cfg["source"]))
    glossary = yaml.safe_load(GLOSSARY.read_text(encoding="utf-8"))
    css = CSS.read_text(encoding="utf-8")
    colophon = COLOPHON.search(sections[-1]).group(0).strip()

    wanted = [int(a) for a in argv] or range(1, len(booklets) + 1)
    (OUT / "html").mkdir(parents=True, exist_ok=True)
    for n in wanted:
        b = booklets[n - 1]
        html_path = OUT / "html" / f"{n:02d}.html"
        html_path.write_text(build_html(n, len(booklets), cfg, b, sections, glossary, css, colophon), encoding="utf-8")
        tmp = OUT / f"{n:02d}.pdf"                 # ASCII name for Chrome, renamed below
        tmp.unlink(missing_ok=True)
        print_pdf(html_path, tmp)
        final = OUT / f"{n:02d} - {safe_name(b['title'])}.pdf"
        tmp.replace(final)
        print(f"  {final}")


if __name__ == "__main__":
    main(sys.argv[1:])
