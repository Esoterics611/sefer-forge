# Notes — כוונות תפילת השחר (005-kavanot-shacharit)

A new discourse (2026-11-12), unrelated to 004. Its first product is three written
explanations (ביאור), each written by a Fable session from the sources and kept apart
from Ronnie's own teaching until he commands it deployed (CLAUDE.md):

| Folder | What | Reads |
|---|---|---|
| `biur-arizal/` | Level 1: Shacharit after the Arizal, the basics, stage by stage | `reading/arizal/` |
| `biur-rashash/` | Level 2: Shacharit after the Rashash, built on level 1 (§N there = §N here) | `reading/rashash/`, and `biur-arizal/biur.src.md` |
| `biur-chasdei-david/` | קונטרס חסדי דוד, the whole text explained | `reading/chasdei-david/` |

Each folder: `biur.src.md` (written), `HANDOFF.md` (state and plan; read first),
`notes/` (the writer's apparatus: terms, argument map, citations, open questions).
Build: `python scripts/build-biur.py discourses/005-kavanot-shacharit/<folder> [--pdf]`.
The prompts for the sessions: `prompts/fable-005-*.md`, then `prompts/opus-after-fable-005.md`.

## The sources

- **שער הכוונות** and **פרי עץ חיים** (Sefaria exports, `sources/arizal/`): two redactions of
  the same teachings. Compared word by word (5-word sequences, 2026-11-12) they share almost
  nothing verbatim, so both are read: שער הכוונות as the main text, פרי עץ חיים where it adds.
- **נהר שלום** with **הקדמת רחובות הנהר** (the Rashash), and **קונטרס חסדי דוד** (R. David
  Magar), from hebrew.grimoar.cz, kept as downloaded in `sources/sharabi/*.grimoar.htm`,
  read through `sources/sharabi/*.he.json` (`scripts/grimoar-import.py`), addresses
  page.paragraph (`27a.7`).
- **Not available:** the Rashash's siddur itself (the charts of kavanot: סידור הרש"ש,
  נהר שלום / רחובות הנהר editions with the כוונות). Only in print and in scans
  (hebrewbooks.org blocks automated readers). נהר שלום is his prose explanation of them.
  A scan or PDF supplied by hand could be added under `sources/scans/` (local only).

## The reading pack: `reading/`

`reading/plan.yaml` sets the sources of every stage of Shacharit by address;
`python scripts/reading-pack.py discourses/005-kavanot-shacharit/reading` builds one file
per stage and level (an index of every paragraph with its opening words and length, then
the text, every paragraph under its address). `reading/README.md` lists the files and sizes.

Stages (the same numbers in both explanations): 00 foundations · 01 rising and the morning
blessings · 02 ציצית · 03 תפילין · 04 קרבנות · 05 קדיש and אמן · 06 פסוקי דזמרה · 07 ברכות
ק"ש · 08 ק"ש · 09 עמידה · 10 חזרה and קדושה · 11 וידוי and י"ג מידות · 12 נפילת אפים ·
13 קריאת התורה to the end. נהר שלום has nothing on 11–13; it adds R1 הקדמת רחובות הנהר,
R2 questions and answers, R3 the דעת, כללים and his glosses on שער הכוונות.
