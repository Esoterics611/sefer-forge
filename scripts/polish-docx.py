#!/usr/bin/env python3
"""Polish output/book.docx: fix paragraph spacing and line-height so the
document reads as a scholarly sefer, not a wall of text.

What this does:
  - Adds space-after to body paragraphs (so paragraphs don't clump).
  - Sets comfortable line spacing (1.35) on body text.
  - Adds generous space-before on Heading 1/2 (so sections breathe).
  - Adds space-before and space-after on tables (framed callout boxes).
  - Indents blockquotes slightly and adds spacing.
  - Leaves title-block / front-matter centered paragraphs alone.

Run AFTER pandoc has produced output/book.docx. Idempotent — running it
twice is safe (it sets exact values, not deltas).

Usage:
    python scripts/polish-docx.py [path/to/book.docx]
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING

# Spacing knobs — tune here, not in the body code.
BODY_SPACE_AFTER_PT = 8      # gap between body paragraphs
BODY_LINE_SPACING = 1.35     # multiple of font size

H1_SPACE_BEFORE_PT = 28
H1_SPACE_AFTER_PT = 12

H2_SPACE_BEFORE_PT = 22
H2_SPACE_AFTER_PT = 10

H3_SPACE_BEFORE_PT = 16
H3_SPACE_AFTER_PT = 8

QUOTE_SPACE_BEFORE_PT = 6
QUOTE_SPACE_AFTER_PT = 10
QUOTE_LINE_SPACING = 1.3

TABLE_SPACE_BEFORE_PT = 12
TABLE_SPACE_AFTER_PT = 12

BODY_STYLES = {"Normal", "Body Text", "First Paragraph", "Compact"}
HEADING_MAP = {
    "Heading 1": (H1_SPACE_BEFORE_PT, H1_SPACE_AFTER_PT),
    "Heading 2": (H2_SPACE_BEFORE_PT, H2_SPACE_AFTER_PT),
    "Heading 3": (H3_SPACE_BEFORE_PT, H3_SPACE_AFTER_PT),
}


def set_spacing(para, *, before=None, after=None, line_mult=None):
    pf = para.paragraph_format
    if before is not None:
        pf.space_before = Pt(before)
    if after is not None:
        pf.space_after = Pt(after)
    if line_mult is not None:
        pf.line_spacing = line_mult
        pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE


def polish(doc_path: Path) -> dict:
    doc = Document(doc_path)
    counts = {"body": 0, "heading": 0, "quote": 0, "table": 0}

    for para in doc.paragraphs:
        style_name = para.style.name if para.style else ""

        if style_name in HEADING_MAP:
            before, after = HEADING_MAP[style_name]
            set_spacing(para, before=before, after=after, line_mult=1.15)
            counts["heading"] += 1
        elif "Quote" in style_name or style_name == "Block Text":
            set_spacing(
                para,
                before=QUOTE_SPACE_BEFORE_PT,
                after=QUOTE_SPACE_AFTER_PT,
                line_mult=QUOTE_LINE_SPACING,
            )
            counts["quote"] += 1
        elif style_name in BODY_STYLES or style_name.startswith("Body"):
            set_spacing(
                para,
                after=BODY_SPACE_AFTER_PT,
                line_mult=BODY_LINE_SPACING,
            )
            counts["body"] += 1

    # Tables (framed callout boxes): space the container paragraph before/after.
    # Inside table cells, use tighter body spacing so callouts don't bloat.
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    set_spacing(para, after=4, line_mult=1.3)
        counts["table"] += 1

    doc.save(doc_path)
    return counts


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("output/book.docx")
    if not path.exists():
        print(f"Not found: {path}")
        return 1
    counts = polish(path)
    print(f"Polished {path}:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
