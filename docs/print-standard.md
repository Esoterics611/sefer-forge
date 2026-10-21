# Print standard

Every PDF that leaves this repo for a reader (a session or discourse pamphlet,
a Shivchei HaBesht booklet, a book page proof) meets this standard. A PDF is
handed over for acceptance testing only after it has passed the proof below;
the hand-over names what was checked.

## The page: the text with its explanation

Every session prints in the paired layout: each page opens with a cut of the
original text, and below a thin rule carries what the speaker says about that
passage, so the reader always has the passage and its explanation together.
The cuts follow the reading (the speaker reads a passage, then explains it;
the same words are in both), snapped to sentence or clause ends. A page whose
explanation continues from the page before opens with a short "המשך הביאור על"
line naming the passage. The explanation is plain text, never framed in a box.
`scripts/build-section.py` pairs; `scripts/build-pamphlet.py` lays out the
pages and checks that no page spills (skill `paired-layout`). Voice-only
lessons pair the same way: each topic heading and the passage read (the
transcript's `>` quotes) on top, the explanation that follows below. In the
Word book the pairs flow (each cut over a rule, its explanation after it);
only the pamphlet is set page by page.

## House style: pamphlets (`templates/pamphlet.css`)

| | |
|---|---|
| Page | A5, margins 18 mm top, 16 mm sides, 19 mm bottom |
| Source text (נוסח, quoted passages) | Guttman Frank 13 pt, line height 1.62, justified, paragraphs indented 5 mm |
| Explanation | David 11.8 pt, line height 1.55, justified, plain (no box) |
| Titles and section headings | Guttman Frank bold: cover 30 pt, part openers 20 pt, sections 16 pt |
| Running matter | header: series · title, David 9.5 pt; page numbers in Hebrew letters, David 10.5 pt; none on the cover |
| Ornaments | ◆ in Guttman Frank, rule colour |
| Fonts in the PDF | David, David-Bold, GuttmanFrank, GuttmanFrank-Bold, and nothing else |

Palette (the stylesheet's `:root` tokens; nothing else appears on the page):

| Token | Colour | Use |
|---|---|---|
| `--ink` | `#1b1b1b` | text |
| `--soft` | `#5a5246` | running header, page numbers, secondary lines |
| `--rule` | `#8c7a5b` | rules, ornaments, the cover frame |
| `--box-fill` | `#f6f2e9` | (older layouts only) |
| `--box-edge` | `#b9a77f` | (older layouts only) |

Booklets follow `templates/booklet.css` (David only, black and greys).
Typography changes go in the stylesheet, never in a PDF or the generated HTML.
A glyph missing from both fonts makes Chrome pull in a third font; that is a
defect, fixed in the stylesheet's font stacks.

## The proof

1. **Automatic:** `python scripts/proof-pdf.py <pdf>` must report no errors.
   It checks, page by page: page size; that only the house fonts are used
   (and which characters fell back to another font); that every text and
   drawing colour is in the palette; markup leaking into print (`{dir=`,
   `:::`, `**`, `[^`, `<!--`, UNCLEAR, TODO); text running into the margins;
   a heading or box label stranded at the foot of a page; blank and
   near-empty pages; the running header and the page-number sequence; Latin
   words in the Hebrew text. It writes `<pdf>.proof.md` and two-page spread
   images (right-to-left, as the printed pamphlet opens) for step 2.

2. **By eye:** read every spread at proof resolution against this list.
   - **Cover:** balanced and centred; the title breaks where the phrase
     breaks; series, author and date present and right.
   - **Hierarchy:** source text, key points and commentary are told apart at
     a glance; headings of one level look alike everywhere.
   - **Text:** justified without rivers or stretched lines; no line starts
     with punctuation; brackets, quotes and maqaf face the right way in
     right-to-left text; niqqud does not collide; abbreviations (ע"י, בחי')
     are never split.
   - **Pairing:** every page's explanation is about the passage above it; a
     continued explanation opens with its "המשך" line; no page ends with a
     passage and no explanation of it.
   - **Pages:** no heading alone at a foot; no page with a line or two; no
     single widowed line at a page top where a reflow can avoid it.
   - **Running matter:** header on every page but the cover; page numbers in
     sequence; the header text right for every part.
   - **Readability:** comfortable line length and density; white space
     enough that the page breathes; nothing that reads as a mistake.

3. **Fix and repeat:** fix each finding in the stylesheet or the source
   (plan, transcript, meta.yaml), rebuild, and proof again until clean.
   Record what was found and fixed under "Visual review" in the proof report.

   **Readability pass** (`prompts/readability-pass.md`): read the explanation
   through as its reader will; correct or remove each short segment Whisper
   garbled, as `edits:` in the session plan (the transcript keeps what was
   heard), then rebuild and proof again.

4. **Hand over** for acceptance testing with: the PDF path and page count,
   the proof summary line, the visual findings fixed, and anything left as it
   is with the reason.
