#!/usr/bin/env python3
"""Proof a printed PDF against docs/print-standard.md before anyone reads it.

Usage:
    python scripts/proof-pdf.py output/pamphlets/003-breishis-002.pdf
    python scripts/proof-pdf.py <pdf> --profile booklet      # pamphlet | booklet | booklet-latin | book
    python scripts/proof-pdf.py <pdf> --no-images            # skip the spread images

The profile follows the PDF's folder (output/pamphlets → pamphlet,
output/booklets → booklet, output/booklets/en|fr → booklet-latin, the English
and French booklets, left to right; otherwise book). Fonts, palette and margins come
from the profile's stylesheet, so the proof always checks the design as it
stands. Page by page it checks:

  page size        every page the profile's size
  fonts            only the house fonts; for any other, which characters fell
                   back to it (a glyph missing from the house fonts); Type 3
                   fonts (bitmap-like, poor in print)
  colours          every text and drawing colour in the stylesheet's palette
  markup leaks     {dir=  ]{  :::  **  [^  <!--  -->  \\[  >  #  UNCLEAR  TODO in the text
  margins          body text running past the side margins; body-size text in
                   the header or footer band
  stranded heads   a heading or ביאור label in the lowest quarter of a page
                   with fewer than two lines after it there
  thin pages       blank pages; pages with a line or two; a last page of
                   one or two lines
  running matter   a header on every page but the first; page numbers in
                   sequence (Hebrew letters for pamphlets)
  line starts      a line beginning with a dash, comma, full stop, colon or
                   semicolon
  Latin words      in the Hebrew text (not for booklet-latin)

Writes <pdf without .pdf>.proof.md (findings, fonts, sizes and colours used,
and a "Visual review" section for step 2 of the proof) and, unless
--no-images, two-page spreads at proof resolution under <pdf folder>/proof/,
as the printed pamphlet opens: right page first, or left page first for a
left-to-right booklet. Prints the summary; exits 1
on any error.
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import pymupdf
except ImportError:
    print("Missing dependency. Install with: pip install -r requirements.txt")
    sys.exit(1)

MM = 72 / 25.4
SIZES = {"A5": (419.5, 595.3), "A4": (595.3, 841.9)}
PROFILES = {
    "pamphlet": {"css": "templates/pamphlet.css", "script": "scripts/build-pamphlet.py", "page": "A5", "numerals": "hebrew",
                 "fonts": {"David", "David-Bold", "GuttmanFrank", "GuttmanFrank-Bold"}, "heading": 15.5},
    "booklet": {"css": "templates/booklet.css", "script": "scripts/build-booklets.py", "page": "A5", "numerals": "decimal",
                "fonts": {"David", "David-Bold"}, "heading": 17.5},
    # The English and French booklets: booklet.css plus booklet-latin.css, EB Garamond.
    "booklet-latin": {"css": "templates/booklet.css",
                      "script": ["scripts/build-booklets.py", "templates/booklet-latin.css"],
                      "page": "A5", "numerals": "decimal", "rtl": False,
                      "fonts": {"EBGaramond-Regular", "EBGaramond-SemiBold",
                                "EBGaramond-Italic", "EBGaramond-SemiBoldIt"},
                      "heading": 16.5},
    # Word PDFs: no stylesheet; black text, and polish-docx.py's box colours.
    "book": {"css": None, "script": ["scripts/polish-docx.py", "scripts/create-template.py"],
             "palette": ["#000000"], "page": "A4",
             # Word reports line-end glyph boxes a few points into the margin.
             "margins_mm": (25, 25, 25, 25), "margin_slack": 8.0, "running_header": False,
             "numerals": "hebrew",
             "fonts": {"David", "David-Bold"}, "heading": 15.0},
}
LEAKS = re.compile(r'\{dir|\]\{|\{\.|:::|\*\*|\[\^|<!--|-->|\\\[|\\\]|custom-style|UNCLEAR|TODO'
                   r'|(?:^|\s)(?:>|#{1,4})(?:\s|$)')        # a blockquote or heading marker printed
LATIN = re.compile(r"[A-Za-z]{2,}")
HEB_ONES = "אבגדהוזחט"
HEB_TENS = "יכלמנסעפצ"
HEB_HUNDREDS = "קרשת"
DPI = 110


def hebrew_numeral(n: int) -> str:
    out = ""
    while n >= 400:
        out += "ת"
        n -= 400
    if n >= 100:
        out += HEB_HUNDREDS[n // 100 - 1]
        n %= 100
    if n in (15, 16):
        return out + ("טו" if n == 15 else "טז")
    if n >= 10:
        out += HEB_TENS[n // 10 - 1]
        n %= 10
    if n:
        out += HEB_ONES[n - 1]
    return out


def css_palette(css: str) -> set[tuple[int, int, int]]:
    cols = {(255, 255, 255)}
    for h in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b|[\"']([0-9A-F]{6})[\"']", css):
        h = h[0] or h[1]
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        cols.add(tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)))
    return cols


def css_margins(css: str) -> tuple[float, float, float, float] | None:
    """@page margin: top right bottom left, in points."""
    m = re.search(r"@page\s*\{[^}]*?margin:\s*([\d.]+)mm\s+([\d.]+)mm\s+([\d.]+)mm\s+([\d.]+)mm", css, re.S)
    return tuple(float(x) * MM for x in m.groups()) if m else None


def near(c: tuple[int, int, int], palette: set) -> bool:
    return any(all(abs(a - b) <= 3 for a, b in zip(c, p)) for p in palette)


def rgb(v) -> tuple[int, int, int]:
    if isinstance(v, int):
        return (v >> 16 & 255, v >> 8 & 255, v & 255)
    if len(v) == 1:                      # grey
        g = round(v[0] * 255)
        return (g, g, g)
    if len(v) == 4:                      # CMYK
        c, m, y, k = v
        return tuple(round(255 * (1 - x) * (1 - k)) for x in (c, m, y))
    return tuple(round(x * 255) for x in v)


def hexs(c) -> str:
    return "#%02x%02x%02x" % c


def snippet(s: str, n: int = 40) -> str:
    s = " ".join(s.split())
    return s if len(s) <= n else s[:n] + "…"


def line_starts(page, top: float, bottom: float, rtl: bool = True) -> list[tuple[str, str]]:
    """(first glyph, line text) for each body line, where "first" is the
    rightmost glyph: a right-to-left line starts at its right edge. (Text
    order from the PDF puts a line-final full stop first, so it can't be used.)
    For a left-to-right booklet, the leftmost glyph of a line with Latin
    letters. A "..." snapshot marker is not punctuation out of place."""
    out = []
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            chars = [c for s in line["spans"] for c in s["chars"] if not c["c"].isspace()]
            if not chars or line["bbox"][1] < top or line["bbox"][3] > bottom:
                continue
            text = "".join(c["c"] for s in line["spans"] for c in s["chars"])
            right = sorted(chars, key=lambda c: -c["bbox"][2]) if rtl else \
                sorted(chars, key=lambda c: c["bbox"][0])
            if not re.search("[א-ת]" if rtl else "[A-Za-z]", text):
                continue
            if "".join(c["c"] for c in right[:3]) == "...":
                continue
            out.append((right[0]["c"], text.strip()))
    return out


def proof(pdf: Path, profile_name: str) -> tuple[list, list, dict]:
    prof = PROFILES[profile_name]
    css = Path(prof["css"]).read_text(encoding="utf-8") if prof["css"] else ""
    # The build script adds styles of its own (running header, box fill): its colours count too.
    scripts = prof.get("script") or []
    scripts = [scripts] if isinstance(scripts, str) else scripts
    extra = "".join(Path(s).read_text(encoding="utf-8") for s in scripts)
    extra += " ".join(prof.get("palette", []))
    palette = css_palette(css + extra) if (css or extra) else None
    margins = css_margins(css) if css else \
        (tuple(m * MM for m in prof["margins_mm"]) if prof.get("margins_mm") else None)
    doc = pymupdf.open(pdf)
    errors: list[str] = []
    warns: list[str] = []
    stats = {"fonts": Counter(), "sizes": Counter(), "colors": Counter(), "fills": Counter(),
             "pages": doc.page_count}
    fallback: dict[str, dict] = defaultdict(lambda: {"chars": set(), "pages": set()})
    bad_text_col: dict[str, set] = defaultdict(set)
    bad_draw_col: dict[str, set] = defaultdict(set)
    want_w, want_h = SIZES[prof["page"]]

    for pno, page in enumerate(doc, 1):
        W, H = page.rect.width, page.rect.height
        if abs(W - want_w) > 2 or abs(H - want_h) > 2:
            errors.append(f"p.{pno}: page is {W:.0f}×{H:.0f} pt, not {prof['page']}")
        top, right, bottom, left = margins or (0, 0, 0, 0)
        body_lines, header, footer = [], [], []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                spans = [s for s in line["spans"] if s["text"].strip()]
                if not spans:
                    continue
                text = "".join(s["text"] for s in line["spans"])
                size = max(s["size"] for s in spans)
                x0, y0, x1, y1 = line["bbox"]
                for s in spans:
                    font = s["font"]
                    stats["fonts"][font] += 1
                    stats["sizes"][round(s["size"], 1)] += 1
                    col = rgb(s["color"])
                    stats["colors"][hexs(col)] += 1
                    if font not in prof["fonts"]:
                        fb = fallback[font]
                        fb["chars"].update(ch for ch in s["text"] if not ch.isspace())
                        fb["pages"].add(pno)
                    if palette and not near(col, palette):
                        bad_text_col[hexs(col)].add(f"p.{pno} “{snippet(s['text'], 20)}”")
                if LEAKS.search(text):
                    errors.append(f"p.{pno}: markup in the print — “{snippet(text, 60)}”")
                entry = (y0, y1, x0, x1, size, text, spans)
                if margins and y1 <= top + 1:
                    header.append(entry)
                elif margins and y0 >= H - bottom - 1:
                    footer.append(entry)
                else:
                    body_lines.append(entry)
        if palette:
            for d in page.get_drawings():
                for key in ("fill", "color"):
                    if d.get(key) is not None:
                        col = rgb(d[key])
                        stats["fills"][hexs(col)] += 1
                        if not near(col, palette):
                            bad_draw_col[hexs(col)].add(f"p.{pno}")

        # Margins and bands.
        if margins:
            for y0, y1, x0, x1, size, text, _ in body_lines:
                slack = prof.get("margin_slack", 1.5)
                if x0 < left - slack or x1 > W - right + slack:
                    errors.append(f"p.{pno}: line runs into the side margin — “{snippet(text)}”")
            for y0, y1, x0, x1, size, text, _ in header + footer:
                if size > 11.5:
                    errors.append(f"p.{pno}: body-size text in the {'header' if y1 <= top + 1 else 'footer'} "
                                  f"band — “{snippet(text)}”")
        body_lines.sort()
        # Chrome PDFs only: Word places punctuation after a footnote mark at odd positions.
        for first, text in (line_starts(page, top, H - bottom if margins else H, prof.get("rtl", True))
                            if css else []):
            if first in "—–,.:;":
                warns.append(f"p.{pno}: a line starts with “{first}” — “{snippet(text, 30)}”")
        latin = sorted({w for *_, text, _ in body_lines for w in LATIN.findall(text)}) \
            if prof.get("rtl", True) else []
        if latin:
            warns.append(f"p.{pno}: Latin words in the text — {', '.join(latin[:8])}")

        # Thin pages and stranded headings (the cover page is free-form).
        if pno > 1:
            n = len(body_lines)
            if n == 0:
                errors.append(f"p.{pno}: blank page")
            elif pno == doc.page_count and n <= 2:
                warns.append(f"p.{pno}: the last page holds only {n} line(s)")
            elif pno < doc.page_count and n < 4:
                warns.append(f"p.{pno}: holds only {n} line(s)")
            body_top, body_bottom = (top, H - bottom) if margins else (0, H)
            sizes = Counter(round(e[4]) for e in body_lines)
            body_size = sizes.most_common(1)[0][0] if sizes else 0
            for i, (y0, y1, x0, x1, size, text, spans) in enumerate(body_lines):
                is_head = size >= prof["heading"]
                is_label = text.strip().startswith("ביאור") and any("Bold" in s["font"] for s in spans)
                if not (is_head or is_label):
                    continue
                # Footnotes and other small print below don't count as the heading's text.
                after = sum(1 for e in body_lines[i + 1:] if e[0] >= y1 - 1 and e[4] >= 0.9 * body_size)
                low = (y1 - body_top) / max(1, body_bottom - body_top) > 0.75
                if low and after < 2:
                    msg = f"p.{pno}: {'heading' if is_head else 'box label'} at the foot of the page " \
                          f"with {after} line(s) after it — “{snippet(text)}”"
                    (errors if is_head else warns).append(msg)

        # Running matter.
        if pno > 1 and prof["numerals"]:
            nums = [t.strip() for *_, t, _ in footer]
            want = hebrew_numeral(pno) if prof["numerals"] == "hebrew" else str(pno)
            if want not in nums:
                warns.append(f"p.{pno}: page number should read “{want}”, found {nums or 'none'}")
            if not header and prof.get("running_header", True):
                warns.append(f"p.{pno}: no running header")
        if pno == 1 and footer and prof["numerals"]:
            warns.append("p.1: the cover carries a page number")

    for font, fb in sorted(fallback.items()):
        chars = " ".join(f"“{c}” U+{ord(c):04X}" for c in sorted(fb["chars"])[:8])
        kind = "Type 3 (bitmap-like) font" if font.startswith("Type3") else f"font {font}"
        errors.append(f"{kind} outside the house fonts, for {chars} on p. "
                      f"{', '.join(map(str, sorted(fb['pages'])[:10]))}: a glyph the house fonts lack — "
                      "fix the stylesheet's font stack")
    for col, where in sorted(bad_text_col.items()):
        errors.append(f"text colour {col} is not in the palette: {', '.join(sorted(where)[:4])}")
    for col, where in sorted(bad_draw_col.items()):
        errors.append(f"drawing colour {col} is not in the palette: {', '.join(sorted(where)[:6])}")
    return errors, warns, stats


def spreads(pdf: Path, rtl: bool = True) -> list[Path]:
    """Two-page spreads, right page first, as a right-to-left pamphlet opens
    (left page first for a left-to-right booklet): the cover alone, then
    (2,3), (4,5), ..."""
    from PIL import Image
    doc = pymupdf.open(pdf)
    out = pdf.parent / "proof"
    out.mkdir(exist_ok=True)
    for old in out.glob(f"{pdf.stem}-*.png"):
        old.unlink()
    pages = []
    for p in doc:
        pix = p.get_pixmap(dpi=DPI)
        pages.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
    groups = [[0]] + [[i, i + 1] if i + 1 < len(pages) else [i] for i in range(1, len(pages), 2)]
    files = []
    for g in groups:
        w, h = pages[0].size
        sheet = Image.new("RGB", (w * 2 + 12, h), (120, 120, 120))
        # Right-to-left: the lower page number on the right; left to right, on the
        # left, and a page alone on its own side (odd pages on the right).
        first, second = ((w + 12, 0), (0, 0)) if rtl else ((0, 0), (w + 12, 0))
        if not rtl and len(g) == 1 and g[0] % 2 == 0:
            first = (w + 12, 0)
        sheet.paste(pages[g[0]], first)
        if len(g) > 1:
            sheet.paste(pages[g[1]], second)
        name = out / (f"{pdf.stem}-{g[0] + 1:02d}" + (f"-{g[1] + 1:02d}" if len(g) > 1 else "") + ".png")
        sheet.save(name)
        files.append(name)
    return files


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if "--profile" in argv:
        profile = argv[argv.index("--profile") + 1]
        args = [a for a in args if a != profile]
    else:
        profile = None
    if len(args) != 1:
        print("Usage: python scripts/proof-pdf.py <pdf> [--profile pamphlet|booklet|booklet-latin|book] [--no-images]")
        return 1
    pdf = Path(args[0])
    if not pdf.exists():
        print(f"No such PDF: {pdf}")
        return 1
    profile = profile or ("pamphlet" if "pamphlets" in pdf.parts else
                          "booklet-latin" if "booklets" in pdf.parts and pdf.parent.name in ("en", "fr") else
                          "booklet" if "booklets" in pdf.parts else "book")
    errors, warns, stats = proof(pdf, profile)
    images = [] if "--no-images" in argv else spreads(pdf, PROFILES[profile].get("rtl", True))

    summary = (f"{pdf.name}: {stats['pages']} pages · profile {profile} · "
               f"{len(errors)} error(s) · {len(warns)} warning(s)")
    lines = [f"# Proof — {pdf}", "", summary, "",
             "## Errors", ""] + [f"- {e}" for e in errors] + (["none"] if not errors else []) + \
            ["", "## Warnings", ""] + [f"- {w}" for w in warns] + (["none"] if not warns else []) + \
            ["", "## In the PDF", "",
             "Fonts: " + ", ".join(f"{f} ({n})" for f, n in stats["fonts"].most_common()),
             "",
             "Text sizes (pt): " + ", ".join(f"{s} ({n})" for s, n in sorted(stats["sizes"].items())),
             "",
             "Text colours: " + ", ".join(f"{c} ({n})" for c, n in stats["colors"].most_common()),
             "",
             "Drawing colours: " + (", ".join(f"{c} ({n})" for c, n in stats["fills"].most_common()) or "none"),
             "", "## Spreads for the visual review", ""] + \
            [f"- {p}" for p in images] + (["(not rendered)"] if not images else []) + \
            ["", "## Visual review", "",
             "(Step 2 of docs/print-standard.md: findings per spread, and what was fixed.)", ""]
    report = pdf.with_suffix(".proof.md")
    report.write_text("\n".join(lines), encoding="utf-8")
    print(summary)
    for e in errors:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ! {w}")
    print(f"-> {report}" + (f"  ·  {len(images)} spreads in {images[0].parent}" if images else ""))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
