---
name: biur-booklet
description: Turn a finished woven ביאור (biur/biur.src.md, build-biur) into the printed booklet Ronnie folds and staples - cover with slogan and sub-slogan, a הקדמה from his voice note, the מבוא as the text's points, the chapter summaries explained for a newcomer, the ביאור, the סיכום, a glossary of the terms, Sefer Forge on the back cover - with the abbreviations opened in print (אדמו"ר, כ"ק and names kept), the page count a multiple of four, every quotation checked, proofed and read spread by spread. Set by Ronnie on 2026-11-24 on פדה בשלום (discourse 006), the model for every booklet after it. Use when the user says "booklet", "print it folded", "the cover", "slogan", "open the abbreviations", "glossary", "summaries a layman can understand", "the Sefer Forge pages", "it prints on the inside of the back", or asks for a ביאור as a printed edition. Argument - the biur folder, e.g. discourses/006-padah-beshalom/biur.
---

# A ביאור as a printed booklet

The model is `discourses/006-padah-beshalom/biur/` (its `biur.src.md`, `abbreviations.yaml`,
`notes/lean.md`, `review/intro-note/`). What Ronnie asked for there, and why, is the rule here.

## The order of the booklet

1. **Cover** (page 1, with the start of the הקדמה): title; the subtitle (the work, where printed, no folios);
   a **slogan** and **sub-slogan** (`[...]{.slogan}`, `[...]{.msub}`): bottom line up front, why this text
   matters, **taken from Ronnie's own words** (his voice note, his earlier phrasing) or the text itself.
   No selling: it must be evident from the content. The Sefer Forge band (`{.brand}`).
2. **הקדמה** (declare it in `headings:`): why the text matters, from Ronnie's voice note to Claude (skill
   `voice-note-to-text`). His words, in his order; nothing added.
3. **מבוא**: where the text is printed and its verse, then its main points as bullets, each quoting the
   text. No added connections, no "relatable" opening, no teaser.
4. **תמצית הפרקים**: short, true to the source, built of the text's own quotations, and **understood by a
   newcomer** (below). No outline table or table of levels unless asked (Ronnie removed both).
5. **המאמר עם ביאור**: the woven text with its glosses, reviewed by skill `lean-biur` (the middle way).
6. **סיכום**.
7. **מילון המונחים** (`::: {.glossary}`, two columns, one page if it can): every term the summaries
   explain, alphabetical, each defined in a sentence or two from the text and its footnotes.
8. **Back cover** (`::: {.works}`): Sefer Forge on **one** page, the outside of the back.

Change only the part asked for. Ronnie's frame (the opening, the summaries) is never cut or rewritten
when he asked about another part (the lean pass of 2026-11-24 that cut the summaries was undone).

## Summaries a newcomer understands

Keep each point and its quotations; make each point understood by someone who has never learned
Chassidus. Work in passes, and record nothing as done until the last:

1. **Read as the newcomer** and list what stops him: Aramaic untranslated; a term used before it is said
   (נפש בהמית, בירור, מקיף, יחידה, חיצונים, ביטול המיעוט ברוב, השתוות, יש ואין...); a verse quoted
   without its meaning; a step skipped (why evil feeds on the good).
2. **Rewrite**: the term said once, in plain words, where it first appears ("בירור, כלומר הוצאת הטוב
   מתוך הרע"); a longer explanation in a footnote (`[...]{.fn}`); the verse translated in a clause.
   Precise, not "relatable"; no selling, no "imagine", no slogans; flowing, not long.
3. **Check**: every quotation exact (`python scripts/check-quotes.py <folder>`: quotations not in the
   text are listed: a verse quoted from elsewhere is fine, anything else is fixed); then read again for
   flow and length.

## Abbreviations opened in print

`open_abbreviations: abbreviations.yaml` in the front matter (build-biur): the text stays as written in
`biur.src.md` and `ocr.md`, so the woven check still holds; only what prints is opened.
- `words:` an abbreviation → its words (found with or without prefix letters); `phrases:` a reading by
  context, applied first ("ב' רוחות" → "שתי רוחות", "כ"א" as "כי אם", folios); `keep:` printed as
  written. The build fails on an abbreviation in none of them.
- **Kept as written** (Ronnie): אדמו"ר, כ"ק, the names (רש"י, האר"י, הבעש"ט), ה' and הוי"ה, כו', בס"ד,
  letters named as letters, a notarikon the text explains, a reading he left open (עי"ת). "חסידות
  חב"ד" (the movement) stays; inside the text חב"ד is the three faculties.
- `[...]{.asis}` prints a span as written (an example of an abbreviation, a name).
- Ask Ronnie for any reading in doubt; never guess one into print. After opening, run
  `check-quotes.py`: it lists doubled words ("ואם לא לא") that an opening produced.

## Folded print: a multiple of four

`fold: true`: the build pads to a multiple of four with blank pages **before** the back cover, so the
back cover is the outside of the back. Blank pages are a last resort. To fit, in this order:
- the **Sefer Forge pages are the elastic** (Ronnie): one page (the back cover) is the minimum; the
  "מכאן והלאה" page and "עוד מעבודותינו" can be added as filler pages, or dropped;
- a page Ronnie allowed to go (he named עיקרי המאמר);
- last, the type: a booklet's own `print.css` beside `biur.src.md` (`css: [templates/biur-woven.css, ...]`),
  never the shared stylesheet (54 chapters of שער היחוד use it).
The build prints `fold: N pages, K blank...` when it pads.

## Proof, every time

`python scripts/proof-pdf.py output/biur/<name>.pdf --profile biur-woven` (0 errors; the warnings are the
English brand and the bare back pages), then read **every spread** (`output/biur/proof/`), then
`check-quotes.py`. Record what was found under "Visual review" in the `.proof.md`. Send the PDF with the
page count and what changed. Only Hebrew unless Ronnie asks for the English edition too.

## Tools

`scripts/build-biur.py` (`fold`, `open_abbreviations`, `[...]{.asis}`, the woven and lean checks),
`templates/biur-woven.css` (`.slogan`, `.msub`, `.glossary`, `.works`, `.blankpage`, the bare back page),
`scripts/make-qr.py <url> <out.svg>` (the QR code on the back cover), `scripts/check-quotes.py`.
