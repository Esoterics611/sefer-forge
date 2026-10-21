---
name: proof-pdf
description: Proof a printed PDF (pamphlet, booklet, or the book exported from Word) against docs/print-standard.md - fonts, colours, markup leaks, margins, stranded headings, thin pages, page numbers - then a visual review of every spread, fixing and rebuilding until clean, before anything is handed to the user for acceptance testing. Use after building any PDF, when the user says "proof", "review the PDF", "check formatting", or before saying a PDF is ready. Argument - the PDF path.
---

The gate between "built" and "ready for acceptance testing". Never hand over a PDF that
has not passed it. The standard is `docs/print-standard.md`; read it first.

1. **Automatic proof.** `python scripts/proof-pdf.py $ARGUMENTS`. For the book, export the
   PDF first: `bash scripts/docx-to-pdf.sh output/<book>.docx`. Every error must be fixed:
   - a font outside the house fonts names the characters that fell back: fix the font
     stack in the stylesheet (`templates/pamphlet.css`, `booklet.css`) or the style in
     `scripts/create-template.py` (book), never by changing the text;
   - a colour outside the palette: the stylesheet or template, not the build output;
   - markup in the print (`{dir=`, `:::`, `**`, UNCLEAR...): the source file;
   - a heading at a page foot, a line in the margin: the stylesheet.
   Warnings are judged one by one: fix, or say in the hand-over why it stays.

2. **Visual review.** Read every spread image the proof lists (`<pdf folder>/proof/`),
   in order, against the list in `docs/print-standard.md` step 2: cover, hierarchy, text
   (rivers, punctuation at line starts, brackets and quotes facing the right way,
   niqqud, split abbreviations), boxes, pages, running matter, readability. Note each
   finding with its page.

3. **Readability pass** (`prompts/readability-pass.md`) for a session pamphlet: the short
   garbled segments of the explanation, corrected or removed as `edits:` in the plan.

4. **Fix, rebuild, re-proof** until steps 1–3 are clean. Write what was found and
   fixed under "Visual review" in the `.proof.md` report.

5. **Hand over** for acceptance testing, in one message: the PDF path and page count, the
   proof summary line, the visual findings fixed, and anything left with its reason.
   Say plainly that it is ready for the user's acceptance test, and nothing more.
