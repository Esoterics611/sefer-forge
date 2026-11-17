#!/usr/bin/env python3
"""Page images of the website's sample project (site/samples/).

    python scripts/site-samples.py

The home page (site/index.html) shows one discourse as a sample project: every
page of its pamphlet and of its reading pack in a page viewer, a close-up or
two, and the two PDFs to download. This renders them from the printed PDFs:

    site/samples/<name>/pamphlet-NN.webp   (+ pamphlet-NN-t.webp, the thumbnail)
    site/samples/<name>/pack-NN.webp       (+ pack-NN-t.webp)
    site/samples/<name>/<crop>.webp        (the close-ups in CROPS)
    site/samples/<name>/<name>-pamphlet.pdf, <name>-reading-pack.pdf

and, for the Tefillah program, chosen pages of the ביאור of 005 (deployed at
Ronnie's word, 2026-11-17; the PDF itself is not published while §9-§13 are
unwritten):

    site/samples/kavanot-shacharit/biur-NN.webp   (+ biur-NN-t.webp)

Build and proof the PDFs first (CLAUDE.md: no PDF goes out unproofed):

    python scripts/build-pamphlet.py discourses/004-levushei-haneshama
    python scripts/build-references.py discourses/004-levushei-haneshama/sessions/001
    python scripts/proof-pdf.py output/pamphlets/004-levushei-haneshama.pdf
    python scripts/build-biur.py discourses/005-kavanot-shacharit/biur-arizal --pdf
    python scripts/proof-pdf.py output/biur/005-kavanot-shacharit-arizal.pdf --profile biur

then run this, check that the page captions in site/index.html (PAGES in its
script) still describe the pages it prints, and publish with
scripts/deploy-site.sh. Made in a cloud container, the pages show the preview
fonts (scripts/setup-cloud.sh); made at home, the house fonts.
"""
from __future__ import annotations

import io
import shutil
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
NAME = "levushei-haneshama"
OUT = ROOT / "site" / "samples" / NAME

# kind -> (PDF, width of the full-size page image in pixels)
DOCS = {
    "pamphlet": (ROOT / "output/pamphlets/004-levushei-haneshama.pdf", 1240),
    "pack": (ROOT / "output/references/004-levushei-haneshama-001.pdf", 1500),
}
THUMB_WIDTH = 220
# Close-ups: name -> (kind, page, (left, top, right, bottom) as fractions of the page)
CROPS = {
    "pack-closeup": ("pack", 1, (0.08, 0.214, 0.92, 0.565)),
}
# The Tefillah sample: chosen pages of the ביאור, in this order (captions in
# site/index.html, DOCS.biur in its script). Its section openings move when the
# text grows: check them against the PDF's headings before rerunning.
BIUR_PDF = ROOT / "output/biur/005-kavanot-shacharit-arizal.pdf"
BIUR_OUT = ROOT / "site" / "samples" / "kavanot-shacharit"
BIUR_PAGES = [1, 2, 11, 18, 25, 39, 53, 57]
BIUR_WIDTH = 1240


def render(page: fitz.Page, width: int) -> Image.Image:
    zoom = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def main() -> int:
    missing = [str(p.relative_to(ROOT)) for p, _ in DOCS.values() if not p.exists()]
    if missing:
        print("Build these first (see the header of this script): " + ", ".join(missing))
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.webp"):
        old.unlink()

    pages: dict[str, list[Image.Image]] = {}
    for kind, (pdf, width) in DOCS.items():
        doc = fitz.open(pdf)
        pages[kind] = []
        size = 0
        for n, page in enumerate(doc, 1):
            im = render(page, width)
            pages[kind].append(im)
            full = OUT / f"{kind}-{n:02d}.webp"
            im.save(full, "WEBP", quality=82, method=6)
            thumb = im.copy()
            thumb.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 2))
            thumb.save(OUT / f"{kind}-{n:02d}-t.webp", "WEBP", quality=72, method=6)
            size += full.stat().st_size
        print(f"{kind}: {doc.page_count} pages, {size // 1024} KB  ({pdf.relative_to(ROOT)})")

    for name, (kind, n, (l, t, r, b)) in CROPS.items():
        im = pages[kind][n - 1]
        w, h = im.size
        im.crop((int(l * w), int(t * h), int(r * w), int(b * h))).save(
            OUT / f"{name}.webp", "WEBP", quality=84, method=6)
        print(f"close-up: {name}.webp ({kind} p. {n})")

    shutil.copyfile(DOCS["pamphlet"][0], OUT / f"{NAME}-pamphlet.pdf")
    shutil.copyfile(DOCS["pack"][0], OUT / f"{NAME}-reading-pack.pdf")
    print(f"PDFs copied. Now check the captions in site/index.html against "
          f"{len(pages['pamphlet'])} pamphlet and {len(pages['pack'])} reading-pack pages.")
    return biur()


def biur() -> int:
    if not BIUR_PDF.exists():
        print(f"Build this first (see the header of this script): {BIUR_PDF.relative_to(ROOT)}")
        return 1
    BIUR_OUT.mkdir(parents=True, exist_ok=True)
    for old in BIUR_OUT.glob("*.webp"):
        old.unlink()
    doc = fitz.open(BIUR_PDF)
    for n, page_no in enumerate(BIUR_PAGES, 1):
        im = render(doc[page_no - 1], BIUR_WIDTH)
        im.save(BIUR_OUT / f"biur-{n:02d}.webp", "WEBP", quality=82, method=6)
        thumb = im.copy()
        thumb.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 2))
        thumb.save(BIUR_OUT / f"biur-{n:02d}-t.webp", "WEBP", quality=72, method=6)
    print(f"biur: {len(BIUR_PAGES)} of {doc.page_count} pages ({', '.join(map(str, BIUR_PAGES))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
