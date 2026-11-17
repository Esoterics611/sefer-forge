#!/usr/bin/env python3
"""Page images of the website's samples (site/samples/).

    python scripts/site-samples.py            # every sample whose PDF is built
    python scripts/site-samples.py handout-he # one of them, by key in SAMPLES

The home page (site/index.html, and the Hebrew page site/he/index.html) shows
the work page by page in one viewer. Each sample here is a printed PDF and the
pages of it the viewer shows:

    site/samples/<dir>/<prefix>-NN.webp   (+ <prefix>-NN-t.webp, the thumbnail)
    site/samples/<dir>/<pdf name>         (when the sample publishes its PDF)

The samples (2026-11-17):
- biur: chosen pages of the ביאור of 005, the morning prayer after the Arizal
  (deployed at Ronnie's word; the PDF is not published while §9-§13 are
  unwritten). Its section openings move when the text grows: check them
  against the PDF's headings before rerunning.
- handout-he, handout-en: the four-page class handout on the garments of the
  soul (004), in Hebrew and in English, every page and the PDFs.

Build and proof the PDFs first (CLAUDE.md: no PDF goes out unproofed):

    python scripts/build-biur.py discourses/005-kavanot-shacharit/biur-arizal --pdf
    python scripts/proof-pdf.py output/biur/005-kavanot-shacharit-arizal.pdf --profile biur
    python scripts/build-handout.py discourses/004-levushei-haneshama/handouts/levushei-haneshama-mavo.md
    python scripts/build-handout.py discourses/004-levushei-haneshama/handouts/levushei-haneshama-mavo-en.md
    python scripts/proof-pdf.py output/handouts/levushei-haneshama-mavo.pdf
    python scripts/proof-pdf.py output/handouts/levushei-haneshama-mavo-en.pdf

then run this, check that the page captions in both pages' scripts (DOCS)
still describe the pages it prints, and publish with scripts/deploy-site.sh.
Made in a cloud container, the pages show the preview fonts
(scripts/setup-cloud.sh); made at home, the house fonts.

site/samples/levushei-haneshama/pack-closeup.webp (the process section's
close-up of a reading pack) was cut from the 8 Nov reading pack and is kept as
it is.
"""
from __future__ import annotations

import io
import shutil
import sys
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
THUMB_WIDTH = 220

# key -> (PDF, folder under site/samples, file prefix, pages (None = all),
#         width of the full-size image, published name of the PDF or None)
SAMPLES = {
    "biur": (ROOT / "output/biur/005-kavanot-shacharit-arizal.pdf", "kavanot-shacharit", "biur",
             [1, 2, 11, 18, 25, 39, 53, 57], 1240, None),
    "handout-he": (ROOT / "output/handouts/levushei-haneshama-mavo.pdf", "levushei-haneshama",
                   "handout-he", None, 1240, "levushei-haneshama-handout.pdf"),
    "handout-en": (ROOT / "output/handouts/levushei-haneshama-mavo-en.pdf", "levushei-haneshama",
                   "handout-en", None, 1240, "levushei-haneshama-handout-en.pdf"),
}


def render(page: pymupdf.Page, width: int) -> Image.Image:
    zoom = width / page.rect.width
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    return Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGB")


def build(key: str) -> bool:
    pdf, folder, prefix, pages, width, published = SAMPLES[key]
    if not pdf.exists():
        print(f"{key}: build this first (see the header of this script): {pdf.relative_to(ROOT)}")
        return False
    out = ROOT / "site" / "samples" / folder
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob(f"{prefix}-*.webp"):
        old.unlink()
    doc = pymupdf.open(pdf)
    chosen = pages or list(range(1, doc.page_count + 1))
    for n, page_no in enumerate(chosen, 1):
        im = render(doc[page_no - 1], width)
        im.save(out / f"{prefix}-{n:02d}.webp", "WEBP", quality=82, method=6)
        thumb = im.copy()
        thumb.thumbnail((THUMB_WIDTH, THUMB_WIDTH * 2))
        thumb.save(out / f"{prefix}-{n:02d}-t.webp", "WEBP", quality=72, method=6)
    if published:
        shutil.copyfile(pdf, out / published)
    print(f"{key}: {len(chosen)} of {doc.page_count} pages"
          + (f", PDF as {folder}/{published}" if published else ""))
    return True


def main(argv: list[str]) -> int:
    keys = argv or list(SAMPLES)
    unknown = [k for k in keys if k not in SAMPLES]
    if unknown:
        print("unknown sample(s): " + ", ".join(unknown) + "; known: " + ", ".join(SAMPLES))
        return 2
    ok = [build(k) for k in keys]
    print("Now check the page captions (DOCS) in site/index.html and site/he/index.html.")
    return 0 if all(ok) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
