#!/usr/bin/env python3
"""Create templates/book-template.docx — Hebrew RTL reference template for pandoc.

Run from repo root: python scripts/create-template.py

Starts from pandoc's own default reference.docx (so every style pandoc emits
exists — Title, Subtitle, Block Text, Footnote Text, TOC Heading, ...) and
restyles it for a Hebrew sefer: David, RTL, justified, A4.

templates/book-template.docx is the output. It is NOT committed:
scripts/build-docx.sh regenerates it automatically when it is missing or
older than this script, so editing this file is all it takes to restyle.
A single book can override it with books/<book>/reference.docx.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    from docx.enum.style import WD_STYLE_TYPE
    from docx.shared import Cm
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
              page_break=False, indent_cm=None, first_line_cm=None,
              align=None):
    """Apply a standard set of properties to a style element (s = style._element)."""
    # --- Run properties ---
    rPr = goa(s, 'w:rPr')
    # Font
    rf = goa(rPr, 'w:rFonts')
    # Theme fonts (asciiTheme, cstheme, ...) inherited from pandoc's reference
    # styles override explicit names: headings came out in Times New Roman.
    for attr in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
        rf.attrib.pop(qn(attr), None)
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
    if italic:
        goa(rPr, 'w:i')
        goa(rPr, 'w:iCs')
    else:
        for tag in ('w:i', 'w:iCs'):
            elem = rPr.find(qn(tag))
            if elem is not None:
                rPr.remove(elem)
    # Color
    if color_auto:
        col = goa(rPr, 'w:color')
        col.set(qn('w:val'), 'auto')
        # A theme colour wins over val: headings came out in Word's accent blue.
        for attr in ('w:themeColor', 'w:themeShade', 'w:themeTint'):
            col.attrib.pop(qn(attr), None)
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
    elif align:
        goa(pPr, 'w:jc').set(qn('w:val'), align)
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
    if first_line_cm is not None:
        goa(pPr, 'w:ind').set(qn('w:firstLine'), str(int(first_line_cm * 567)))


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

with tempfile.TemporaryDirectory() as tmp:
    base = Path(tmp) / "reference.docx"
    with open(base, "wb") as fh:
        subprocess.run(["pandoc", "--print-default-data-file", "reference.docx"],
                       stdout=fh, check=True)
    doc = Document(str(base))

BODY_PT = 13

# Document defaults: pandoc's reference sets theme fonts here (Times New
# Roman for Hebrew) and Arabic as the right-to-left language. Anything whose
# style names no font, such as the table of contents Word generates, falls
# back to these.
defaults = doc.styles.element.find(qn('w:docDefaults'))
d_rPr = goa(goa(defaults, 'w:rPrDefault'), 'w:rPr')
d_fonts = goa(d_rPr, 'w:rFonts')
for attr in ('w:asciiTheme', 'w:hAnsiTheme', 'w:eastAsiaTheme', 'w:cstheme'):
    d_fonts.attrib.pop(qn(attr), None)
for attr in ('w:ascii', 'w:hAnsi', 'w:cs'):
    d_fonts.set(qn(attr), HEBREW_FONT)
goa(d_rPr, 'w:lang').set(qn('w:bidi'), 'he-IL')

# Links (table of contents entries, footnote links) print in the text colour.
link = doc.styles['Hyperlink'].element if 'Hyperlink' in [s.name for s in doc.styles] else None
if link is not None:
    l_col = goa(goa(link, 'w:rPr'), 'w:color')
    l_col.set(qn('w:val'), 'auto')
    for attr in ('w:themeColor', 'w:themeShade', 'w:themeTint'):
        l_col.attrib.pop(qn(attr), None)

# Normal — base for everything
configure(doc.styles['Normal']._element,
          size_pt=BODY_PT, rtl=True, justify=True, spacing_factor=1.6,
          space_before_pt=0, space_after_pt=6)

# Body paragraphs. First Paragraph (right after a heading) gets no indent;
# following paragraphs get a classic first-line indent.
for name, indent in (('First Paragraph', None), ('Body Text', 0.8), ('Compact', None)):
    configure(get_or_create_style(doc, name)._element,
              size_pt=BODY_PT, rtl=True, justify=True, spacing_factor=1.6,
              space_before_pt=0, space_after_pt=6, first_line_cm=indent)

# Title page (pandoc renders metadata title/subtitle/author/date with these)
configure(get_or_create_style(doc, 'Title')._element,
          size_pt=30, bold=True, rtl=True, align='center',
          space_before_pt=120, space_after_pt=12)
configure(get_or_create_style(doc, 'Subtitle')._element,
          size_pt=15, italic=True, rtl=True, align='center',
          space_before_pt=0, space_after_pt=24)
for name in ('Author', 'Date'):
    configure(get_or_create_style(doc, name)._element,
              size_pt=14, rtl=True, align='center',
              space_before_pt=6, space_after_pt=6)

# Heading 1 — chapter / lesson title; always starts a new page
configure(get_or_create_style(doc, 'Heading 1')._element,
          size_pt=22, bold=True, rtl=True,
          page_break=True, space_before_pt=12, space_after_pt=10)
configure(get_or_create_style(doc, 'Heading 2')._element,
          size_pt=16, bold=True, rtl=True,
          space_before_pt=14, space_after_pt=6)
configure(get_or_create_style(doc, 'Heading 3')._element,
          size_pt=14, bold=True, rtl=True,
          space_before_pt=10, space_after_pt=4)

# Block Text — pandoc uses this for blockquotes (source text)
configure(get_or_create_style(doc, 'Block Text', 'Normal')._element,
          size_pt=12, italic=True, rtl=True, justify=True, indent_cm=1.0,
          spacing_factor=1.5, space_before_pt=4, space_after_pt=8)

# Commentary — the voicenote ביאור inside its box, smaller than the source
# text. Applied by scripts/polish-docx.py for books that set
# `polish: commentary_box: true`.
configure(get_or_create_style(doc, 'Commentary', 'Normal')._element,
          size_pt=11, rtl=True, justify=True, spacing_factor=1.3,
          space_before_pt=0, space_after_pt=4)

# Footnotes
configure(get_or_create_style(doc, 'Footnote Text')._element,
          size_pt=10.5, rtl=True, justify=True, spacing_factor=1.15,
          space_before_pt=0, space_after_pt=2)

# Table of contents heading
configure(get_or_create_style(doc, 'TOC Heading')._element,
          size_pt=20, bold=True, rtl=True, align='center',
          space_before_pt=12, space_after_pt=12)

# Table of contents entries. Word fills the TOC field with its built-in
# "toc N" styles (lower case); a custom "TOC N" is ignored and Word's own
# definition, in Times New Roman, is used instead. So these must carry the
# built-in names.
for level in (1, 2, 3):
    st = get_or_create_style(doc, f'TOC {level}')._element
    goa(st, 'w:name').set(qn('w:val'), f'toc {level}')
    st.attrib.pop(qn('w:customStyle'), None)
    configure(st, size_pt=BODY_PT, rtl=True, space_before_pt=0, space_after_pt=4)

# Page: A4, 2.5 cm margins, RTL section
section = doc.sections[0]
section.page_height = Cm(29.7)
section.page_width = Cm(21.0)
for side in ('top_margin', 'bottom_margin', 'left_margin', 'right_margin'):
    setattr(section, side, Cm(2.5))
goa(section._sectPr, 'w:bidi')

# Page numbers: Hebrew letters (א, ב, ... טו, טז), centred in the footer, in
# the running-matter style of the pamphlets; none on the title page. pandoc
# carries the reference document's footers into every book.
goa(section._sectPr, 'w:pgNumType').set(qn('w:fmt'), 'hebrew1')
section.different_first_page_header_footer = True
configure(get_or_create_style(doc, 'Footer')._element,
          size_pt=11, rtl=True, align='center', space_before_pt=0, space_after_pt=0)
footer_p = section.footer.paragraphs[0]
footer_p.style = doc.styles['Footer']
goa(goa(footer_p._p, 'w:pPr'), 'w:bidi')
page_field = OxmlElement('w:fldSimple')
page_field.set(qn('w:instr'), 'PAGE')
run = OxmlElement('w:r')
text = OxmlElement('w:t')
text.text = '1'
run.append(text)
page_field.append(run)
footer_p._p.append(page_field)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(str(OUT))
print(f"Created: {OUT}  ({OUT.stat().st_size:,} bytes)")
print(f"Font: {HEBREW_FONT}  |  Direction: RTL  |  Page: A4")
