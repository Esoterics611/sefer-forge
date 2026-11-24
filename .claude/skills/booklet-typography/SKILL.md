---
name: booklet-typography
description: Lay out a printed booklet for how it is really read - black and white, A4 sheets folded in half and stapled at the spine, so every page is A5 - with type big enough to read at that size and a page that catches the eye - parts opening a page, the verse displayed, an overview as numbered steps with titles, chapters as black tabs, square bullets, key sentences in bold - all from the content, never decoration. Set by Ronnie on 2026-11-24 on פדה בשלום (discourse 006) ("the overview is too boring, we need to capture the reader's eye ... it will be printed black and white folded into booklets stapled in the middle spine, the fonts need to be big"). Use when the user says "booklet", "folded", "stapled", "fonts too small", "too boring", "capture the eye", "formatting", "styles", "readability of the print", or before any ביאור booklet (skill biur-booklet) is handed over. Argument - the biur folder, e.g. discourses/006-padah-beshalom/biur.
---

# Booklet typography: black and white, folded, A5

The model: `discourses/006-padah-beshalom/biur/` with `templates/biur-booklet.css`. This skill is the
look of the page; what the pages say is skill `biur-booklet` (order, summaries, abbreviations) and
`lean-biur` (the glosses). Change the look, never the words, unless Ronnie asks.

## 1. The page is the size it prints at

Ronnie prints the PDF in booklet mode: two pages on each side of an A4 sheet, folded, stapled at the
spine. An A4 PDF printed that way shrinks to 71% (13pt reads as 9pt). So the booklet is set **A5**
(`css: [templates/biur-woven.css, templates/biur-booklet.css]`), and every size is the size on paper:

| what | size |
|---|---|
| body (explanation, David Libre) and the text (Frank Ruhl Libre Bold) | 12pt, leading 1.62 |
| footnotes | 9.5pt, `footnote-policy: auto` (`line` strands headings on near-empty A5 pages) |
| part heading (`##`) | 19pt, centred, heavy rule, opens a page |
| heading in a part (`###`) | 14pt, heavy rule above; `{.part}` for the opening's headings (16pt, centred) |
| chapter of the summaries (`####`) | 13pt, `[פרק א׳]{.ch}` as a black tab |
| running head, page number | 8-8.5pt, 10.5pt; nothing smaller than 8pt anywhere |

Margins 16/15/17/15mm. The page count is a multiple of four (`fold: true`; filler pages per
`biur-booklet`).

## 2. Black and white only

Black ink, white paper, one grey (#333 for the running head; `#eee` at most for a fill). Structure comes
from **weight, size, rules, black shapes and white space**: a heavy rule (1.2-1.6pt) under a part
heading, a black disc or tab with white type, a square bullet, a framed box. Never colour, never a tint
that a photocopier loses, never type on a grey fill.

## 3. Catch the eye with the content itself

Each device shows something true about the text; none is ornament:
- **Cover on its own page**: title 34pt, the subtitle, the slogan between two heavy rules (break it at its
  colon so no word sits alone), the sub-slogan, the brand at the foot.
- **The verse the text is built on, displayed**: `[...]{.verse}` 17pt bold, centred, its reference under it
  (`{.vref}`).
- **The overview as numbered steps** (`::: {.steps}` around the list): the step's number in a black disc,
  a short title from the text's own terms (`[...]{.st}`), then the paragraph. The paragraph must not
  repeat its title: drop an opening that only restates it ("זהו 'פדה בשלום נפשי':" under the title
  "פדה בשלום נפשי").
- **Chapters as tabs** in the summaries; points with square bullets.
- **Key sentences in bold** inside a long prose part (the הקדמה): the topic sentence of a paragraph as
  `[...]{.pk}`, three or four in a part, the writer's own sentences, unchanged.
- **Parts open a page**; a short part may follow on the page where the last one ended (`## מבוא {.flow}`)
  instead of leaving two lines alone on a page.

Bold `**...**` is the text itself in a woven ביאור (the woven check reads it): emphasis outside the text
uses spans (`{.pk}`, `{.st}`), never `**`. A heading's `{.class}` is layout only (the lint ignores it).

## 4. Check at paper size

1. `python scripts/build-biur.py <folder> --pdf`; read the `fold:` line (blank pages = fit with the
   Sefer Forge filler pages, `biur-booklet`).
2. `python scripts/proof-pdf.py output/biur/<name>.pdf --profile biur-booklet`: 0 errors; the warnings
   are the English brand and the bare back pages. A page that "holds only N lines" is fixed, not
   accepted (a part that may flow on, a heading kept with its text, a filler page).
3. Read **every spread** in `output/biur/proof/` as the folded booklet: the cover alone; no heading at a
   page's foot; no word alone on a line of a display; tabs, discs and rules black and crisp; the back
   cover on one page, outside of the back.
4. `python scripts/check-quotes.py <folder>`.

Send the PDF with the page count, the sheets it takes (pages / 4), and what changed in the look.

## Files

`templates/biur-booklet.css` (generic for every booklet: change it here, not per booklet; a booklet's own
exception goes in a `print.css` beside its source), the `biur-booklet` profile in `scripts/proof-pdf.py`,
the lint's heading attributes in `scripts/build-biur.py`.
