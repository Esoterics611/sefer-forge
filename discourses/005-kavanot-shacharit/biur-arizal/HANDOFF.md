# Hand-off: the explanation of Shacharit after the Arizal (005, level 1)

Read this first, every session. Update it before you stop.

## State
2026-11-12: **part 1 written** (the מבוא and §1–§4), in one Fable session, on branch
`claude/loving-curie-yubxz5` (which carries the preparation branch `claude/busy-planck-pec3bg`;
neither is in `main`). `biur.src.md`: 68 passages set in, all resolving
(`build-biur.py --check`). §5–§13 and the סיכום are headings only. Built, proofed and checked afterwards: see the next part.

**Next:** part 2 (§5–§8), when Ronnie starts it. See "For part 2" below.

## After part 1: built, checked, printed (Opus, 2026-11-13)
- Built: 68 passages, 119 paragraphs; PDF `output/biur/005-kavanot-shacharit-arizal.pdf` (28 pages)
  and review copy `output/biur/review/` (31 pages, findings marked), both proofed clean.
- PEC labels: 7.3, 7.5 "פרק ו׳" (the attested correspondence); every other PEC passage is named by the
  ד״ה of the discussion it stands in.
- The independent check (two examiners): `check.md`, main findings in `checks.yaml`. **Two errors
  wait for Ronnie**: מבוא.10 ("אלא אל ראשה" is contradicted by the rising itself) and §1.13 (the count
  of the eighteen blessings in שער הברכות). Ten points are imprecise. Nothing in the explanation was
  changed on them; part 2 can correct them if Ronnie says so.
- The quotations in the prose (61) were matched letter for letter by script; one spelling aligned
  ("תפלה לדוד").
- Lexicon: 17 terms of part 1 entered (`knowledge/lexicon/`), `--check` 0 errors.

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
| 1 | מבוא (00), §1–§4: עולם העשיה | 172K chars | **written 2026-11-12** |
| 2 | §5–§8: קדיש, פסוקי דזמרה, ברכות ק"ש, ק"ש | 189K | **next** |
| 3 | §9–§13, סיכום: the עמידה to the end | 300K | |
פרי עץ חיים by its index, at most three passages in full per section.

## Where things go
- `notes/terms.md`: term, meaning, address (for the lexicon, `knowledge/lexicon/`).
- `notes/argument-map.md`: the frame (worlds, partzufim, what each stage does), kept current.
- `notes/citations.md`: every `@source` and how sure its reading is.
- `notes/open-questions.md`: what stays open, and the sources not found.
- This file: the stopping point, what is settled, the claims to check, every `<!-- CHECK -->`.

## Part 1: what is settled
The frame every later section stands on (in full in `notes/argument-map.md`):
- Prayer belongs to the מלכות; its purpose on a weekday is to build זו"ן דאצילות as full
  partzufim and turn them פב"פ in their place below, so that they unite and sift the kings
  (PEC שער התפילה 7.1–7.5, 6.12).
- Four parts = four worlds; in each the souls of that world rise, not the world; then the
  descent of the שפע from אשרי to עלינו (SK דרוש א').
- Two passes over the four worlds: **deed** (נטילה and יפנה, the two tallitot, תש"י, תש"ר)
  fixes the outer of each world in its place, the lowest three sefirot of each, the blessing
  making the מקיף; **speech** raises world into world through the souls (SK דרושים ב–ג).
- The union: ק"ש brings מוחין פנימיים to ז"א and Leah; the עמידה the מקיפים and the union of
  Yaakov and Rachel פב"פ, he in נצח, she in הוד (SK דרוש ב'; PEC 7.46, 7.54).
- §1 נטילה, יפנה and the blessings along the partzufim of עשיה; §2 ציצית as the מקיף of עיבור
  and יניקה and the מקיף of Rachel; §3 tefillin as yesterday's רשימו, and Rachel's keter-point
  at ז"א's arm; §4 the תמיד, the קטורת, אנא בכח and איזהו מקומן as the completion of עשיה.

## The claims most worth checking
1. **מבוא, the head-to-head joining of עשיה and יצירה** (citations 5): the reading of the
   run-on sentence in SK Prayers.1.2.
2. **מבוא, "המעשה מתקן... את שלוש האחרונות של כל עולם, והעליונות של העולם שתחתיו ממילא"**: a
   compression of SK Prayers.3.2–3.4; check each world's line against the table in
   `notes/argument-map.md` §3.
3. **מבוא, that the union of PEC 7.46/7.54 is the union of the עמידה**, and the sentence on
   ישראל/יעקב and the chest (from 7.47, read but not quoted).
4. **מבוא against PEC שער התפילה ch. 8**, which was not read and by its index gives another
   account of what the deeds make (open-questions, "Not read").
5. **§1, the count of the eighteen blessings** in the two works (open-questions 6).
6. **§2, the four fringes as the four fillings** (citations 38): the passage has more in it
   than the explanation gives; and the sentence that the tallit katan is "היצירה בקטנותה".
7. **§3, the night and the morning of Rachel** (the paragraph before citation 50): a
   compression of SK Tefillin.5.3–5.6; and the paragraph that sets the דרוש's own
   contradiction beside SK Prayers.2.2 (open-questions 2).
8. **§3, Rashi and Rabbenu Tam**: only one of the three accounts in SK Tefillin.6.2 is given.
9. **§4, the two "changes" of עשיה** (3.6–3.7) and the six levels of אנא בכח.
10. The grade-C sentences in `notes/citations.md` (28–29, 54, 65).

## `<!-- CHECK -->` marks
None: every directive resolved. What needs checking is listed above and in the notes.

## For Opus (mechanical)
- PEC labels for **שער התפילה** and **שער הברכות** carry no chapter (the file's chapter numbers
  are not the print's); set the printed chapter (`notes/citations.md`, "Labels").
- The explanation uses section cross-references in words ("סעיף 1", "סעיפים 7–8"); keep them in
  step if a heading changes.
- Quotations inside the prose (in "..."), not set by directive, were copied from the reading
  pack: מבוא ("וברכת אבות הוא ראש הבריאה...", "לפי שעיקר הכונה...", "כי כל מצוה הנעשית
  בדיבור...", "עד עתה ע"י המעשה..."), §1 ("לפי שכולם הם רמזים נפלאים..."), §4 ("והנה בעלית
  העולמות..."). Check them letter for letter or turn them into `@source`.
- Lexicon: `notes/terms.md` has 27 terms with addresses, not yet entered.

## For part 2 (§5–§8)
- §4 ends: עשיה complete, the inner of its ג"ר in נה"י דיצירה; "מכאן, דרך הקדיש ו'הודו', שהוא
  ראש העשיה, באים אל 'ברוך שאמר', ראש היצירה". §5 (the קדיש) picks up there.
- Already said in part 1, to build on and not repeat: the 13 "ברוך" of ברוך שאמר and its 87
  words (SK Prayers.1.2, not quoted); the 18 names of יהי כבוד = ח"י ברכאן דיסוד דיצירה; after
  ברוך שאמר the outer of ג"ר דעשיה joins their inner (3.6); ק"ש as in the מבוא.
- To settle there: open-questions 1, 2, 7. SK Tzitzit דרוש ג (the sixteen מוחין) is the
  preface to ק"ש: "דרוש ג' בענין הציצית וק"ש וב' מקושרים יחד".
- Method that worked: the SK part of each stage in full, PEC by index and three or four short
  passages; one `--check` after each section (seconds), fixing only marks that did not match.

