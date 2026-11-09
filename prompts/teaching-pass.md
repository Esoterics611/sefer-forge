# Teaching pass

The last step of every narration (`prompts/02-ingest-session.md` step 7,
`prompts/02v-ingest-voice-session.md` step 8), after the style pass
(`prompts/style-pass.md`). The style pass leaves the explanation as a lesson
in written Hebrew: the speaker's voice, his order, his returns to a point.
This pass rewrites it as a written commentary on the text printed above it, a
ביאור a reader studies, not the record of a lesson. Expect it at about half
the length.

The teaching text is what prints: the pamphlet, the discourse and the book.
The lesson text before it stays in the session (`section.md`, the transcript's
`style:`), and prints with `--lesson` into its own folder: the version to
compare against or go back to. A session ingested before 2026-11-08 takes the
pass only when asked (`session-status.py` marks it so).

## What the result reads like

- **A commentary on these words.** Under each cut of the text, the
  explanation starts from the text. It quotes a few exact words (like a
  דיבור המתחיל) and says what they mean. Then it gives the speaker's
  explanation, and then his own additions: his parallels, applications and
  conclusions.
- **Impersonal and present.** Use third person and plain statements: "כאן
  מבאר", "כלומר", "נמצא", "ומכאן". Never "אני" or "אנחנו", never the listener,
  never the lesson's clock ("עכשיו", "בפעם הקודמת", "עוד מעט"). A reference
  names a place in the book: לעיל, להלן, בהקדמה, בהערה א'.
- **Each idea once, where it belongs.** An idea is stated under the cut it
  explains. A later mention is a few words that point back ("כאמור בהערה
  א'"), or it is dropped.
- **About half the words of the default text.** The length goes by cutting
  speech, repetition, retellings of the text above, hedges and extra
  examples. It never goes by cutting an idea.
- **Plain, exact Hebrew.**
  - Define a term at its first use where the speaker defined it (נר"ן, צלם,
    קליפת נוגה, מ"ן).
  - No foreign words. Use the speaker's Hebrew word, or the accepted one:
    סייקי → הנפש, קומפלקסים → תסביכים.
  - Keep sentences to 40 words at most.
  - Every pronoun has a clear referent.
  - Gender and number agree (הנשמה, השכינה, הצורה are feminine; הצלם,
    הלבוש are masculine).

## Keep

- **Every idea of substance**, every example he needs, and every source and
  reference he gives. His own readings of the text count: his parallels from
  psychology, the collective, history. They are the commentary, not
  digressions.
- **His conclusions, and the order of ideas within each cut.**
- **Corrections the speaker confirmed**: the `edits:` marked "the speaker's
  correction".
- **The pairing.** Each paragraph stays under the cut of the text it explains;
  the draft's `#` headings show which. Content may merge within a cut, never
  move to another. The cuts themselves are fixed before this pass, so they
  cannot move.

## Remove

- **Speech that outlived the style pass**: lesson management, "כמו שאמרנו",
  rhetorical questions (state the answer instead).
- **Repetition**: within a paragraph, a session, and the whole discourse (the
  הקדמה and the other parts included). The inventory in step 1 finds it.
- **Retelling the text above.** It is printed on the same page, so quote the
  few words the point turns on, not the passage.
- **Re-reading aloud.** The speaker's full readings in quotation marks become
  a short exact quote, or go when the explanation follows the passage
  directly.
- **Hedges and fillers** that carry nothing: כמובן, ממש, באמת, בעצם; and
  "נראה ש…" when nothing is uncertain.

## Never

- **Add** an idea, source, example, conclusion or connection he did not make.
  A sentence linking two of his ideas may only state the link he made.
- **Change what a sentence claims.** When unsure what he meant, keep his
  wording for that sentence and record the doubt in the notes for the
  speaker.
- **Settle a doubtful claim by your own view**, for example one that seems to
  contradict the text. Keep it as said, or ask.
- **Misquote.** A quotation is the text's words exactly as printed (or exactly
  as he quoted them in the paragraph being replaced). The checks refuse
  anything else.
- **Touch anything else**: the text (נוסח), the Etz Chaim passages, the key
  points, `commentary.md`, or the earlier passes.

## Steps

**0. Before.** The readability and style passes are done, the session builds,
and its pamphlet is proofed. The pass is recorded against the text as it now
prints. A later change to `edits:` or `style:` makes it stale; the checks say
so, and the changed paragraphs are redone from a fresh draft.

**1. Understand it, in writing, before rewriting a word.** Read each cut of
the text, its source (the Etz Chaim passage; `references.md`), and the
explanation under it; open `commentary.md` wherever the meaning is in doubt.
Then write `<session>/teaching-notes.md`:

- **a. What this part teaches.** Three to six sentences in your own words:
  what the text says, what the speaker draws from it, how it follows from the
  parts before. If you cannot write this plainly, you do not understand it
  yet. Read again and check the source. If it is still unclear, write the
  question down for the speaker instead of guessing.
- **b. Idea inventory.** Every distinct idea, numbered, one line each, in
  order, with its paragraph and cut, for example
  `4. (¶2, cut 1) נפש אלוקית ונפש בהמית שבחסידות אינן הנר"ן אלא לבושיו`.
  Mark each **keep**, **repeat of N** (and where N is kept), or **drop**
  (with the reason: speech, retelling of the text, already in the הקדמה).
  Read the discourse's other parts (their notes, or their text) to catch
  repeats across parts.
- **c. Doubts.** Sentences whose meaning is unclear or contested, and how each
  is handled.

**2. Draft.** Run `python scripts/apply-teaching.py <session> --draft <file>`
(the file goes in the scratchpad). The draft holds the explanation as it
prints by default, one block per paragraph under a `#` heading naming its cut.
Rewrite each block in place. A block whose content moved into another block
of the same cut becomes a lone `—`. Within a cut, write in this order:
1. what the text says, from its words;
2. the speaker's explanation;
3. his additions;
4. where needed, his link to what follows.

**3. Mechanical check.** Run
`python scripts/apply-teaching.py <session> <file> --check`. Every error must
be fixed:
- Latin letters;
- an unbalanced quotation mark or parenthesis;
- a quotation of three or more words found neither in the discourse's texts
  nor in the paragraph it replaces;
- a block count that differs from the paragraphs.

Each warning is read in its sentence: speech words, sentences over 40 words,
a length outside 35–65% of the default. Change it, or keep it on purpose.

**4. Record and build.**
- Run the same command without `--check`. It writes `teaching:` beside
  `style:`.
- A laid-out session: run `python scripts/build-section.py <session>`. It
  writes `section.teaching.md` beside `section.md`, with the same cuts and key
  points.
- A narration not yet laid out: run `python scripts/refined-text.py <session>`
  to get `refined.teaching.md`. For an opening part made from a session (like
  `introduction.md`), run `python scripts/sync-opening.py <session>
  <discourse>/<name>.md`: it carries the paragraphs of `refined.md` into
  `<name>.md` and those of `refined.teaching.md` into `<name>.teaching.md`.

**5. Discourse check.** Run `python scripts/check-teaching.py <discourse>`. It
covers every session and the opening parts, and reports any five-word phrase
that occurs in two places. Decide each one: one place says it, and the other
points back or drops it. Repeat steps 2–4 until it shows no errors and no
repeat you have not decided on.

**6. Read it back: the self-check that matters.** Reassemble the discourse
(`python scripts/assemble-discourse.py <discourse> --force` when its
`discourse.md` is only the assembled sessions; a hand-polished one is merged by
hand), print it with `python scripts/build-pamphlet.py <discourse> --png`, and
proof it with `python scripts/proof-pdf.py output/pamphlets/<name>.pdf`. Then
read every page as a reader who has only the page:

- Under each cut, does the explanation explain this text? Can it be followed
  without having heard the lesson?
- Is every sentence clear on first reading? Is every term known by the time
  it appears?
- Is anything said twice, on the page, in the part, or in the pamphlet?
- Does anything contradict the text above it or its source?
- Are grammar, agreement, spelling, punctuation and quotation marks right?
- Go down the inventory. Every **keep** must appear exactly once; note where.
  Every **drop** needs its reason. Write this tally into the notes as
  **d. Coverage**.
- Where meaning could have shifted, compare against `commentary.md`.

Fix what you find (redraft, record, rebuild) and read again, until a full read
finds nothing.

**7. Report.** Give, for each part:
- the words before and after;
- what was cut as repetition, and where the idea is kept;
- judgement calls and open questions for the speaker;
- the PDF's path, and the lesson version's (`--lesson`) when the user may
  want to compare.

## Recording and printing

    teaching:          # section-plan.yaml after style:, or the transcript's frontmatter
      - from: <a paragraph as it prints by default, whole>
        to: <its teaching text; empty when the paragraph is dropped>

There is one entry for every paragraph. It is written by `apply-teaching.py`
from the draft, never by hand.

| Tool | Writes |
|---|---|
| Tool | Writes or prints |
|---|---|
| `build-section.py` | `section.teaching.md` beside `section.md` (the lesson text) |
| `refined-text.py` | `refined.teaching.md` beside `refined.md` |
| `assemble-discourse.py <discourse>` | `discourse.md` from the teaching text where a part has it |
| `assemble-discourse.py <discourse> --lesson` | `discourse.lesson.md`: the lesson text throughout |
| `build-pamphlet.py <path>` | the teaching text, into `output/pamphlets/` |
| `build-pamphlet.py <path> --lesson` | the lesson text, into `output/pamphlets/lesson/` |
| `session-status.py` | the pass as a session's last step |
| `check-session.py` | reports a teaching pass that is stale or not rebuilt |
| `check-teaching.py` | reports on the writing |

A part without `teaching:` prints its lesson text, as before.

**Going back:**
- To see or print the lesson version, use `--lesson`.
- To drop a session's teaching text, remove `teaching:` from its plan (or
  frontmatter) and rebuild. `build-section.py` then removes
  `section.teaching.md`.

## An example (הערה א', cut 2)

Default (after the style pass: two paragraphs, 86 words):

> הלבושים האלה כלולים מטוב ורע, "אחר שנתערב על ידי חטא אדם הראשון". בקטעים
> הבאים בעץ חיים ובמאמר נראה באריכות מהו הבירור: האם הלבושים קיימים וצריך
> לבררם, או שאנו יוצרים אותם; האם הם עצמם צריכים תיקון, או שבבירורם אנו
> ממשיכים מדרגות שלמעלה. ורעיון העלאת מ"ן, ההתעוררות מלמטה, יבואר בהמשך
> המאמרים.
>
> וזהו עניין "כתנות עור" בעי"ן: בתורתו של רבי מאיר מצאו כתוב "כתנות אור"
> באל"ף (בראשית רבה כ, יב). הלבושים האלה היו פעם מאירים, ועתה העור "עיוור":
> העולם הגשמי, הנתפס בחושים, מסתיר מאיתנו את ה"אור", את המימד הרוחני.

Teaching pass (one paragraph, 48 words; the second block is `—`):

> "כלול מטוב ורע": מחטא אדם הראשון נתערב בלבושים רע, ולכן הם "כתנות עור"
> בעי"ן; ובתורתו של רבי מאיר נכתב "כתנות אור" באל"ף (בראשית רבה כ, יב).
> הלבושים היו מאירים, ועתה העור מסתיר את האור. אם הלבושים מתבררים או
> נוצרים, ומה נמשך בבירורם (העלאת מ"ן), יתבאר להלן.

The text's words open it, and the source and every idea are kept. What goes
is "נראה באריכות", two of the four questions (the text below answers the one
that matters, so it is kept), and the second wording of the עור/עיוור image.
The two paragraphs become one because they explain the same cut.
