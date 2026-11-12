# Hand-off: the explanation of Shacharit after the Arizal (005, level 1)

Read this first, every session. Update it before you stop.

## State
2026-11-12: prepared, nothing written. `biur.src.md` holds the front matter and the headings
only: מבוא (stage 00), sections 1–13 (stages 01–13), סיכום. Builds clean (0 passages).

**Next:** part 1, below.

## What it is
The basics of Shacharit after the Arizal, stage by stage in the order of the prayer: what
each stage repairs or raises, in which world, which partzufim and which union (זיווג) it
brings about, what makes it necessary at that point, and its main kavanot, with the key
passages set in by `@source`. The level-2 explanation (the Rashash, `../biur-rashash/`)
builds on this one section by section (§N there = §N here), so the structure here is the
frame for both.

## Reading
- One file per stage: `../reading/arizal/NN-<slug>.md` (index first, then the text).
  Sizes in `../reading/README.md`.
- שער הכוונות is the main text: read the stage's part of it in full.
- פרי עץ חיים is the other redaction, worded differently throughout (nothing to skip by
  machine): read its index, then the paragraphs that carry the stage's main teaching, or
  say what שער הכוונות leaves unclear.
- A term or a cited passage of עץ חיים: `python scripts/source-lookup.py etz-chaim <address>`
  or `--find '<words>'`; the lexicon: `python scripts/lexicon.py <term>`.

## The parts (one Fable session each, `prompts/fable-005-arizal.md`, started by Ronnie)
| Part | Writes | שער הכוונות to read | Status |
|---|---|---|---|
| 1 | מבוא (00), §1–§4: עולם העשיה | 172K chars | **next** |
| 2 | §5–§8: קדיש, פסוקי דזמרה, ברכות ק"ש, ק"ש | 189K | |
| 3 | §9–§13, סיכום: the עמידה to the end | 300K | |
פרי עץ חיים by its index, at most three passages in full per section.

## Where things go
- `notes/terms.md`: term, meaning, address (for the lexicon, `knowledge/lexicon/`).
- `notes/argument-map.md`: the frame (worlds, partzufim, what each stage does), kept current.
- `notes/citations.md`: every `@source` and how sure its reading is.
- `notes/open-questions.md`: what stays open, and the sources not found.
- This file: the stopping point, what is settled, the claims to check, every `<!-- CHECK -->`.
