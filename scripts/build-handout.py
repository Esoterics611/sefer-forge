#!/usr/bin/env python3
"""Print a class handout: a short Hebrew text with footnotes at the foot of each page.

Usage:
    python scripts/build-handout.py discourses/004-levushei-haneshama/handouts/levushei-haneshama-mavo.md

The handout is markdown (pandoc) with front matter (`title`, `subtitle`, `pages`). A footnote is an
inline span, `[עץ חיים, שער כ"ו, פרק א'.]{.fn}`, set at the foot of its page (WeasyPrint's
`float: footnote`; `pip install weasyprint`). Layout: templates/handout.css. When `pages:` is given,
`lang: en` (or fr) prints left to right in EB Garamond (templates/handout-latin.css). The build
chooses the largest type size (14pt down to 10pt) at which the handout fits in that many
pages, so it fills them. Writes output/handouts/<name>.pdf; proof it with scripts/proof-pdf.py.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "templates" / "handout.css"
CSS_LATIN = ROOT / "templates" / "handout-latin.css"      # English or French: over handout.css


def html_of(md: Path, lang: str) -> str:
    r = subprocess.run(["pandoc", str(md), "-f", "markdown+fenced_divs+bracketed_spans" + ("-smart" if lang == "he" else "+smart"), "-t", "html5",
                        "--standalone", "--wrap=none", "--metadata", f"lang={lang}", "--metadata", f"dir={'rtl' if lang == 'he' else 'ltr'}"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("pandoc: " + r.stderr[-800:])
    import re
    return re.sub(r"<style>.*?</style>", "", r.stdout, flags=re.S)      # pandoc's own defaults out: the stylesheet decides


def render(html: str, base: float, lang: str = "he"):
    from weasyprint import CSS as WCSS, HTML
    from weasyprint.text.fonts import FontConfiguration
    fc = FontConfiguration()            # without it the stylesheets' @font-face (templates/fonts/) is not loaded
    sheets = [CSS] + ([] if lang == "he" else [CSS_LATIN])
    doc = HTML(string=html, base_url=str(CSS.parent)).render(
        stylesheets=[WCSS(filename=str(f), font_config=fc) for f in sheets]
        + [WCSS(string=f"body {{ font-size: {base}pt; }}", font_config=fc)], font_config=fc)
    return doc


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    md = Path(argv[0])
    text = md.read_text(encoding="utf-8")
    meta = yaml.safe_load(text.split("---", 2)[1]) if text.startswith("---") else {}
    lang = meta.get("lang", "he")
    html = html_of(md, lang)
    target = meta.get("pages")
    sizes = [14.0 - 0.25 * i for i in range(17)] if target else [12.0]
    chosen = None
    for base in sizes:
        doc = render(html, base, lang)
        if not target or len(doc.pages) <= target:
            chosen = (base, doc)
            break
    if chosen is None:
        print(f"does not fit in {target} pages even at {sizes[-1]}pt: shorten it")
        chosen = (sizes[-1], render(html, sizes[-1], lang))
    base, doc = chosen
    out = ROOT / "output" / "handouts" / f"{md.stem}.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.write_pdf(out)
    print(f"wrote {out.relative_to(ROOT)}: {len(doc.pages)} page(s) at {base}pt")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
