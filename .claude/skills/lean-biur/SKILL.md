---
name: lean-biur
description: The rule for every ביאור, set by Ronnie on 2026-11-24 - after a stretch of the text, write only what the text does not say itself - a term explained, or a source it cites brought briefly and in its context (and where a reference such as כנ"ל points, when that is not plain). A gloss that restates the bold text in other words is cut, and a stretch that needs nothing gets nothing. Use when writing or revising any ביאור (woven or by @text stretches), when the user says "the biur repeats the text", "it restates the bold", "lean", "cut the paraphrase", "don't write for the sake of writing", or before a ביאור's student read and proof. Argument - a biur folder (e.g. discourses/007-shaar-hayichud-perushim/biur-perek-01), or a discourse for all its folders, one at a time.
---

# The lean ביאור

Ronnie, 2026-11-24, on שער היחוד עם פירושים: "in most cases the biur is restating the bold text
without adding anything. If it is repeating the bold text then leave it out; don't force yourself to
write something for the sake of writing. Only explain terms, or if quoting from another source bring
the source in brief and in context; otherwise, if you are restating the main text, don't write
anything." This holds for every ביאור from now on, beside `prompts/biur-rules.md`.

## What may follow a stretch of the text

Only these, each as short as it can be:

1. **A term.** A word the reader of the text may not know: a technical term (היולי, תפסן), a פרצוף or
   a ספירה within a ספירה (ישראל סבא, אימא תתאה, כתר דבינה), a phrase of Aramaic or Yiddish (translated),
   a rare usage. Explain the **term**, in a few words, not the sentence it stands in. A term the text
   itself explains a line later gets nothing. Resting on the text or a source, never on memory
   (skill `chassidus-context`, the lexicon).
2. **A source.** A verse, a saying of the Gemara or the Zohar, the Arizal's writings, the Tanya, that
   the text quotes, alludes to (כמ"ש, כידוע, בכתבים, בזוהר) or rests on: its words briefly, with its
   address, and in its context — the one clause that shows what in it the text uses. A longer passage by
   `@source` with `mark=` on the words that matter; a short one inline; background in a footnote. Not the
   source retold, and not the text's point said again after it.
3. **A pointer.** Where a "כנ"ל", "לעיל", "כמ"ש למעלה" or the close of a parenthesis points, when the
   reader cannot see it (a few words: "בסעיף 4", "בפרק א").

## What is cut

- A paraphrase of the bold: "**X**: in other words, X." Whatever re-says the stretch, in its words or in
  others, goes — even when it reads smoothly.
- Signposts and connectives that carry the text along: "ומכאן קושיא", "והתשובה", "והנמשל", "ועכשיו
  חוזר", "ומכאן חידוש", "זו הגדרת התבונה". The text has its own ואמנם, אך, ולפי"ז.
- A conclusion drawn after the text drew it, a summary of a paragraph, a "the point here is".
- In the frame: a מבוא that retells the chapter (keep only how it joins what came before, two or
  three sentences, or nothing); a table of the chapter's terms in its own words; a סיכום that retells it.
  The outline (מהלך הפרק), being navigation, may stay.

When a stretch needs nothing, the bold runs on into the next stretch: join them into one bold run
(`**...**`), with the text's punctuation inside it. Long runs of plain text are right. Do not add a
gloss to break them.

## The test, for every gloss

Read the bold, then the gloss, and ask: **what does the gloss give that the bold does not?** A term's
meaning, a source's words, where a pointer points: keep, and cut it to that. Anything else: delete.
When unsure, delete; the text was written to be understood.

## Steps (one chapter, one folder, at a time — each a standalone work)

1. `python scripts/check-restatement.py <folder> --all` — the inventory of every gloss, the ones whose
   words already stand in the bold flagged `RESTATES?`. The script cannot see a paraphrase in other
   words; it shows where to look. Every gloss is judged by the test above, not only the flagged ones.
2. Edit `biur.src.md`: cut, join the bold runs, shorten what stays to its term or source. Never touch
   the words of the text (the build holds them to `text_file`, word for word).
3. `python scripts/build-biur.py <folder> --check`, then `--pdf` (a standalone PDF of the chapter).
   The build's notes report the gloss count and how many are still flagged.
4. The student read (`prompts/student-read.md`) asks only: is a term left unexplained, a source left
   without its point, a pointer that does not land? It adds nothing else.
5. Proof (skill `proof-pdf`, `--profile biur`) and hand over the chapter's PDF with the count: glosses
   before → after, words of explanation before → after.

Keep a line per chapter in `<folder>/notes/lean.md`: the date, glosses before → after, and anything left
for Ronnie (a term not found in a source, a doubtful reading).
