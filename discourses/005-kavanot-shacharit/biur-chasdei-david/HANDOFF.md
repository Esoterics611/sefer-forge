# Hand-off: the explanation of קונטרס חסדי דוד (005)

## State on 2026-11-12: written, built, proofed
Written in one Opus session (at Ronnie's request, instead of Fable). `biur.src.md`: מבוא,
24 sections over the הקדמה and כללים (א)–(קכ), סיכום. Build: 100% of the text covered, 9
source passages, 148 paragraphs. PDF `output/biur/005-chasdei-david.pdf`, 67 pages, proof 0
errors, 0 warnings, visual review in `output/biur/005-chasdei-david.proof.md`.

## What was checked, and how
- Every `@text`, `@source` and `mark=` resolves (the build).
- Every phrase quoted inside the prose (241) was matched against the קונטרס, נהר שלום and עץ
  חיים by script; the 26 that did not match letter for letter were corrected to the text's own
  spelling or taken out of quotation marks (2026-11-12).
- Each section's claims were reread against its כללים by the writer. **No independent check
  yet** (a reader who has not seen the writing): that is the first job of
  `prompts/opus-tidy-005.md`.

## Claims most worth an independent check
1. §8: that כללים (יז)–(כ) follow the Rashash's "בפרטות לבד" (נהר שלום 2a.1); the קונטרס does
   not cite him there.
2. §13: the reading of the four kinds of זיווג (שלים / לא שלים, twice) as the place of the
   partzuf and the degree of the union inside it; the table's assignments are the text's, the
   reading is the writer's.
3. §16: the table of the two זיווגים (vessel at night, "אחד" / "בשכמל"ו"; birth by day,
   "שמע" / "שים שלום") — from (עז), checked; the sentence on Shabbat and weekdays from (עט).
4. §17: the table of sparks per king (פג–פח) and the note on why נה"י are not counted (פז).
5. §22: the summary of (קיח) — the three worlds, their numbers, the copyist's notes (א"ה) —
   is compressed; nothing in it is meant to go beyond the text.
6. §1: "אמת ליעקב" is read as the name of the copyist's book ("כנראה").

## Not done
- The lexicon: the terms in `notes/terms.md` are not yet entries in `knowledge/lexicon/`.
- No comparison with Ronnie's teaching (none recorded on this text).
