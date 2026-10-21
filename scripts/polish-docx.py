#!/usr/bin/env python3
"""Polish output/<book>.docx: fix paragraph spacing and line-height so the
document reads as a scholarly sefer, not a wall of text.

What this does:
  - Adds space-after to body paragraphs (so paragraphs don't clump).
  - Sets comfortable line spacing (1.35) on body text.
  - Adds generous space-before on Heading 1/2 (so sections breathe).
  - Adds space-before and space-after on tables (framed callout boxes).
  - Indents blockquotes slightly and adds spacing.
  - Frames each ביאור (paragraphs in the Commentary style, written as
    ::: {custom-style="Commentary"} divs) in a bordered, shaded box.
  - Keeps every heading with its text (and a short lead-in line with what
    it introduces), so no heading ends a page.
  - Leaves title-block / front-matter centered paragraphs alone.

Run AFTER pandoc has produced output/<book>.docx. Idempotent — running it
twice is safe (it sets exact values, not deltas).

Any knob below can be overridden per book with a `polish:` block in
books/<book>/metadata.yaml, using the lowercase knob name, e.g.

    polish:
      body_line_spacing: 1.7

Usage:
    python scripts/polish-docx.py output/<book>.docx
"""
from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

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

# A paragraph after a heading shorter than this is a lead-in ("ממשיך:"):
# it is kept with what follows, so heading and lead-in never end a page alone.
LEAD_IN_MAX_CHARS = 90

TABLE_SPACE_BEFORE_PT = 12
TABLE_SPACE_AFTER_PT = 12

# ביאור boxes. A Commentary paragraph starting with BOX_LABEL opens a box.
BOX_LABEL = "■"
BOX_BORDER_COLOR = "A39E93"   # warm grey, 0.75 pt
BOX_FILL = "F7F5F0"           # light parchment
BOX_GAP_PT = 10               # between consecutive boxes

BODY_STYLES = {"Normal", "Body Text", "First Paragraph", "Compact"}
HEADING_MAP = {
    "Heading 1": (H1_SPACE_BEFORE_PT, H1_SPACE_AFTER_PT),
    "Heading 2": (H2_SPACE_BEFORE_PT, H2_SPACE_AFTER_PT),
    "Heading 3": (H3_SPACE_BEFORE_PT, H3_SPACE_AFTER_PT),
}


def apply_book_overrides(doc_path: Path) -> list[str]:
    """Override the module-level knobs from books/<book>/metadata.yaml."""
    meta = Path("books") / doc_path.stem / "metadata.yaml"
    if not meta.exists():
        return []
    import yaml

    knobs = (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("polish") or {}
    applied = []
    for key, value in knobs.items():
        name = key.upper()
        if name not in globals() or not name.endswith(("_PT", "_SPACING")):
            print(f"WARN: unknown polish knob in {meta}: {key}")
            continue
        globals()[name] = value
        applied.append(f"{key}={value}")
    global HEADING_MAP
    HEADING_MAP = {
        "Heading 1": (H1_SPACE_BEFORE_PT, H1_SPACE_AFTER_PT),
        "Heading 2": (H2_SPACE_BEFORE_PT, H2_SPACE_AFTER_PT),
        "Heading 3": (H3_SPACE_BEFORE_PT, H3_SPACE_AFTER_PT),
    }
    return applied


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

    counts["box"] = box_commentary(doc)
    counts["kept"] = keep_headings_with_text(doc)

    doc.save(doc_path)
    return counts


def _keep_next(para) -> None:
    pPr = para._p.get_or_add_pPr()
    if pPr.find(qn("w:keepNext")) is None:
        pPr.append(OxmlElement("w:keepNext"))


def keep_headings_with_text(doc) -> int:
    """Every heading keeps with the next paragraph; a short lead-in after a
    heading keeps with the one after it, so a heading is never stranded at a
    page foot with a line of text and the rest overleaf."""
    paras = doc.paragraphs
    kept = 0
    for i, para in enumerate(paras):
        if (para.style.name if para.style else "") not in HEADING_MAP:
            continue
        _keep_next(para)
        kept += 1
        if i + 1 < len(paras) and len(paras[i + 1].text.strip()) < LEAD_IN_MAX_CHARS:
            _keep_next(paras[i + 1])
    return kept


def _el(tag: str, **attrs) -> OxmlElement:
    el = OxmlElement(tag)
    for key, value in attrs.items():
        el.set(qn(f"w:{key}"), str(value))
    return el


def box_commentary(doc) -> int:
    """Wrap each ביאור in a single-cell box: full width, RTL, thin border,
    light fill, inner padding.

    Pandoc emits a ::: {custom-style="Commentary"} div as bare paragraphs in
    the Commentary style, so the div's edges are gone; a new box starts at
    every paragraph opening with BOX_LABEL, or after any other content.
    Consecutive boxes get an empty paragraph between them, since Word merges
    tables that touch. Books without Commentary paragraphs are untouched.
    """
    try:
        style_id = doc.styles["Commentary"].style_id
    except KeyError:
        return 0

    groups: list[list] = []
    current: list = []
    for el in list(doc.element.body):
        style = el.find(f"{qn('w:pPr')}/{qn('w:pStyle')}") if el.tag == qn("w:p") else None
        if style is None or style.get(qn("w:val")) != style_id:
            if current:
                groups.append(current)
                current = []
            continue
        text = "".join(t.text or "" for t in el.iter(qn("w:t"))).strip()
        if text.startswith(BOX_LABEL) and current:
            groups.append(current)
            current = []
        current.append(el)
    if current:
        groups.append(current)

    for paras in groups:
        tbl = _el("w:tbl")
        tblPr = _el("w:tblPr")
        tblPr.append(_el("w:bidiVisual"))
        tblPr.append(_el("w:tblW", w=5000, type="pct"))
        borders = _el("w:tblBorders")
        for side in ("top", "left", "bottom", "right"):
            borders.append(_el(f"w:{side}", val="single", sz=6, space=0, color=BOX_BORDER_COLOR))
        tblPr.append(borders)
        margins = _el("w:tblCellMar")
        for side, twips in (("top", 140), ("left", 260), ("bottom", 100), ("right", 260)):
            margins.append(_el(f"w:{side}", w=twips, type="dxa"))
        tblPr.append(margins)
        tbl.append(tblPr)
        grid = _el("w:tblGrid")
        grid.append(_el("w:gridCol", w=9071))
        tbl.append(grid)

        tc = _el("w:tc")
        tcPr = _el("w:tcPr")
        tcPr.append(_el("w:tcW", w=5000, type="pct"))
        tcPr.append(_el("w:shd", val="clear", color="auto", fill=BOX_FILL))
        tc.append(tcPr)
        paras[0].addprevious(tbl)
        for p in paras:
            tc.append(p)
        tr = _el("w:tr")
        tr.append(tc)
        tbl.append(tr)

        label = Paragraph(paras[0], None)
        if label.text.strip().startswith(BOX_LABEL):
            label.paragraph_format.keep_with_next = True
            label.paragraph_format.space_after = Pt(6)

        if tbl.getprevious() is not None and tbl.getprevious().tag == qn("w:tbl"):
            gap = _el("w:p")
            gap_pPr = _el("w:pPr")
            gap_pPr.append(_el("w:spacing", before=0, after=0, line=int(BOX_GAP_PT * 20), lineRule="exact"))
            gap.append(gap_pPr)
            tbl.addprevious(gap)

    return len(groups)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/polish-docx.py output/<book>.docx")
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Not found: {path}")
        return 1
    overrides = apply_book_overrides(path)
    if overrides:
        print("Book overrides:", ", ".join(overrides))
    counts = polish(path)
    print(f"Polished {path}:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
