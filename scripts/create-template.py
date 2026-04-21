#!/usr/bin/env python3
"""Create templates/book-template.docx — Hebrew RTL reference template for pandoc.

Run from repo root: python scripts/create-template.py

Re-run any time to regenerate. Templates/book-template.docx is the output;
commit it (tracked via git-lfs) so every checkout gets a working template.
"""
import sys
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.enum.style import WD_STYLE_TYPE
except ImportError:
    print("Missing dependency. Run: pip install python-docx")
    sys.exit(1)

HEBREW_FONT = "David"   # built-in on Windows; alternatives: "Frank Ruehl CLM", "SBL Hebrew"
OUT = Path("templates/book-template.docx")


# ---------------------------------------------------------------------------
# Low-level XML helpers (python-docx doesn't expose all Word properties natively)
# ---------------------------------------------------------------------------

def goa(parent, tag):
    """Get or add child element by tag (idempotent)."""
    elem = parent.find(qn(tag))
    if elem is None:
        elem = OxmlElement(tag)
        parent.append(elem)
    return elem


def configure(s,
              font=HEBREW_FONT, size_pt=12,
              bold=False, italic=False, color_auto=True,
              rtl=True, justify=False,
              spacing_factor=None, space_before_pt=None, space_after_pt=None,
              page_break=False, indent_cm=None):
    """Apply a standard set of properties to a style element (s = style._element)."""
    # --- Run properties ---
    rPr = goa(s, 'w:rPr')
    # Font
    rf = goa(rPr, 'w:rFonts')
    rf.set(qn('w:ascii'), font)
    rf.set(qn('w:hAnsi'), font)
    rf.set(qn('w:cs'), font)   # Complex Script = Hebrew
    # Size (half-points)
    hp = str(int(size_pt * 2))
    goa(rPr, 'w:sz').set(qn('w:val'), hp)
    goa(rPr, 'w:szCs').set(qn('w:val'), hp)
    # Bold
    if bold:
        goa(rPr, 'w:b')
        goa(rPr, 'w:bCs')
    else:
        for tag in ('w:b', 'w:bCs'):
            elem = rPr.find(qn(tag))
            if elem is not None:
                rPr.remove(elem)
    # Italic — remove from headings if inherited
    if not italic:
        for tag in ('w:i', 'w:iCs'):
            elem = rPr.find(qn(tag))
            if elem is not None:
                rPr.remove(elem)
    # Color
    if color_auto:
        goa(rPr, 'w:color').set(qn('w:val'), 'auto')
    # RTL run direction
    if rtl:
        goa(rPr, 'w:rtl')

    # --- Paragraph properties ---
    pPr = goa(s, 'w:pPr')
    # Bidi (RTL paragraph)
    if rtl:
        goa(pPr, 'w:bidi')
    # Justification
    if justify:
        goa(pPr, 'w:jc').set(qn('w:val'), 'both')
    # Line spacing
    if spacing_factor:
        sp = goa(pPr, 'w:spacing')
        sp.set(qn('w:line'), str(int(spacing_factor * 240)))
        sp.set(qn('w:lineRule'), 'auto')
    # Space before/after
    if space_before_pt is not None or space_after_pt is not None:
        sp = goa(pPr, 'w:spacing')
        if space_before_pt is not None:
            sp.set(qn('w:before'), str(int(space_before_pt * 20)))
        if space_after_pt is not None:
            sp.set(qn('w:after'), str(int(space_after_pt * 20)))
    # Page break before
    if page_break:
        goa(pPr, 'w:pageBreakBefore').set(qn('w:val'), '1')
    # Indent (for blockquote)
    if indent_cm is not None:
        ind = goa(pPr, 'w:ind')
        twips = str(int(indent_cm * 567))
        ind.set(qn('w:start'), twips)
        ind.set(qn('w:end'), twips)


def get_or_create_style(doc, name, based_on='Normal'):
    try:
        return doc.styles[name]
    except KeyError:
        st = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        try:
            st.base_style = doc.styles[based_on]
        except KeyError:
            pass
        return st


# ---------------------------------------------------------------------------
# Build the document
# ---------------------------------------------------------------------------

doc = Document()

# Normal (body text)
configure(doc.styles['Normal']._element,
          size_pt=12, rtl=True, justify=True, spacing_factor=1.5,
          space_before_pt=0, space_after_pt=6)

# Heading 1 — chapter title
configure(get_or_create_style(doc, 'Heading 1')._element,
          size_pt=24, bold=True, rtl=True,
          page_break=True, space_before_pt=12, space_after_pt=6)

# Heading 2 — discourse / major section
configure(get_or_create_style(doc, 'Heading 2')._element,
          size_pt=18, bold=True, rtl=True,
          space_before_pt=10, space_after_pt=4)

# Heading 3 — subsection
configure(get_or_create_style(doc, 'Heading 3')._element,
          size_pt=14, bold=True, rtl=True,
          space_before_pt=8, space_after_pt=4)

# Block Text — pandoc uses this for blockquotes (source text)
configure(get_or_create_style(doc, 'Block Text', 'Normal')._element,
          size_pt=11, rtl=True, justify=True, indent_cm=1.5,
          space_before_pt=4, space_after_pt=4)

# Body Text — alternate paragraph style (some pandoc templates)
configure(get_or_create_style(doc, 'Body Text', 'Normal')._element,
          size_pt=12, rtl=True, justify=True, spacing_factor=1.5)

# Compact — tight paragraphs (pandoc tight lists)
configure(get_or_create_style(doc, 'Compact', 'Normal')._element,
          size_pt=12, rtl=True, justify=True,
          space_before_pt=0, space_after_pt=2)

# First Paragraph (pandoc may use this for the first para in a block)
configure(get_or_create_style(doc, 'First Paragraph', 'Normal')._element,
          size_pt=12, rtl=True, justify=True, spacing_factor=1.5)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT))
sz = OUT.stat().st_size
print(f"Created: {OUT}  ({sz:,} bytes)")
print(f"Font: {HEBREW_FONT}  |  Direction: RTL  |  Styles: Normal, Heading 1-3, Block Text, Body Text, Compact")
print()
print("To test the template:")
print('  pandoc --print-default-data-file reference.docx > /tmp/ref.docx  # baseline comparison')
print(f"  pandoc compiled/book.md -o output/test.docx --reference-doc={OUT}")
