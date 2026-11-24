# The explanation (ביאור) as a final product: what prints, and what does not

Set by Ronnie on 2026-11-12, reading the explanation of the הגהה in discourse 004. An explanation is
**explanation, and the connection of the texts to one another**: the text, its sources in their own words,
and what makes them clear together. Everything else the writer used to get there is apparatus. It is kept
in the working notes (`biur/notes/`), never printed. Any session that writes or revises an explanation
(Fable or Opus) follows these rules. `python scripts/build-biur.py` refuses a source that breaks the ones a
script can see.

## Not in the explanation

1. **Opened abbreviations.** No "**ראשי התיבות:** ע"ח = עץ חיים. שמ"ט פ"ה = שער מ"ט..." lines, and no
   glosses like "אדמו"ר = אדוננו מורנו ורבנו". The reader knows them.
2. **"Where one can go wrong."** No "**היכן אפשר לטעות.**" paragraphs or lists of misreadings ("אפשר
   לקרוא... כאילו... ההפך: ..."). If a reading needs to be set right, the explanation states the right one
   in its place.
3. **Certainty notes.** No "**מידת הוודאות.**" paragraphs, no "מפורש / מוכרח מן ההקשר / השערה" grading, no
   "(השערה)" tags. Where the text is genuinely open, say so in one plain clause where it matters
   ("ההגהה אינה מפרשת"; "אפשר ש... ואפשר ש...").
4. **The writer.** No first person and no account of the work: "לפניי", "אינו לפניי", "לא מצאתי",
   "הבנתי", "אני קורא", "נראה לי", "איני יודע", "כתבתי", "אכתוב". A source the repo lacks is named where it
   is cited ("כך בשער הגלגולים, המקביל לספר הגלגולים"); how it was searched for belongs in the notes.
5. **Instructions to the reader.** No "שים לב", "כדאי לראות", "כך נבנה הביאור", lists of how to read.
6. **Headings that describe the method.** No "פתח דבר: מה יש כאן, ואיך לקרוא", "א. ההגהה במקומה: על
   איזו שאלה היא עונה", "ב. מהלך ההגהה בקצרה", "ג. לאורך הטקסט". The only headings are the title, **מבוא**,
   the numbered sections along the text (`### N. <its subject>`), and **סיכום**.
7. **Labels inside the explanation.** No "**ביאור.**" before a paragraph. The traditional קושיה / תירוץ may
   stay where they are the shape of the argument.
8. **Working parts.** No open-questions part, no list of missing sources, no notes on how a source was
   obtained, no "עד כאן מגיע מאמר... שלפניי". They live in `biur/notes/` (`open-questions.md`,
   `removed-from-final.md`).

## Nothing said twice, nothing the student needs left out (Ronnie, 2026-11-24)

Every gloss after a stretch of the text gets a decision: it **repeats** what the text said (cut, keeping
its punctuation), it **explains** what the student would not get from the text alone (a term, a hard
sentence in plain words, the reason the text assumes, a source in context, where a "כנ"ל" points: kept,
trimmed to that), or it **ties** the stretch to its context (the question before the answer, the נמשל of a
משל, where the argument goes: kept, short). And every long stretch is asked whether the student still
follows it; if not, it is split into sentences, each with its explanation. Nothing is written for the
sake of writing, and nothing that explains is cut for the sake of cutting. The opening and the סיכום are
not reviewed this way. The procedure: skill `lean-biur` (`.claude/skills/lean-biur/SKILL.md`), the
decisions recorded in `notes/lean-decisions.md`; `python scripts/check-restatement.py <folder>` lists the
glosses, and the build reports how many still read as restatements.

## In the explanation

- The text of the הגהה, complete, stretch by stretch (`@text`).
- Every source it relies on, in its own words, the words that matter marked (`@source`, `@file`).
- The explanation: what the source says, what the text does with it, and how this part connects to what
  came before and what follows. Plain, impersonal Hebrew.
- Nothing about how it was made: no byline, no paragraph numbers, no check marks, no mention of the
  repository or its copies of the sources ("בעותק שבמאגר"): name a source as the printed books do.
  Ronnie deploys the finished document as his own work, on his command (CLAUDE.md).
- For review only, never the finished document: `--review` prints a copy (`output/biur/review/`) with
  paragraph numbers and the independent check's open findings (`biur/checks.yaml`) marked "בדיקה N" and
  listed at the end.

## For the writer

The apparatus is useful while writing and checking: certainty, misreadings to avoid, what is missing.
Write it in `biur/notes/` (one file per kind), not in `biur.src.md`. A checker reads the notes beside the
explanation; the reader of the explanation never sees them.

Before the proof, every ביאור is read once more as its student will read it (`prompts/student-read.md`,
Ronnie, 2026-11-21): the built `biur.md` from title to סיכום, each term, reference and step checked for
whether a student meeting the text for the first time can follow it; the findings and fixes in
`notes/student-read.md`.

## The meaning layer ("בנפש האדם")

Added at Ronnie's word on 2026-11-16 ("explain the Arizal and the Rashash according to how I define the
terms; another section on each page"). An explanation may carry, after a paragraph, a block that applies
what that paragraph says to the soul and the service of prayer, in the meanings Ronnie gives the terms:

```
::: {.meaning}
<plain, impersonal Hebrew: the same sentence, read in the soul>
:::
```

- The meanings come from `knowledge/teacher/terms.yaml` (`TERMS.md`): what he said (`said:`, quoted and
  checked) and, where he has not defined a term, Claude's application of his frame (`applied:`, printed
  "(יישום)" in the key, to be confirmed). Nothing from memory, nothing from another school.
- The rules above hold inside the block: no first person, no instructions, no certainty notes.
- The build labels each block "בנפש האדם" and appends **מפתח המושגים**: every term the blocks use, his
  meaning, and the shiur it comes from. `--no-meaning` prints the explanation without the layer
  (`output/biur/plain/`).
- Each block follows its paragraph; a paragraph that leads into a source with ":" gets its block after
  the source. Not every paragraph needs one: a lead-in, or a bare list of addresses, can stand without.
