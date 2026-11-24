---
name: lean-biur
description: The rule for every ביאור, set by Ronnie on 2026-11-24 and refined the same day - every gloss after a stretch of the text gets a decision - does it repeat what the text said (cut), explain it (keep, to what the text does not say), or tie it to its context (keep) - and every long stretch gets a question - has the student still understood, or should it be split into sentences, each with its explanation. The middle way between a ביאור that restates the bold and one with no ביאור left. Only the explanation along the text is reviewed; the opening (מבוא, outline, tables, chapter summaries) and the סיכום stay as they are unless Ronnie says otherwise. Use when writing or revising any ביאור (woven or by @text stretches), when the user says "the biur repeats the text", "it restates the bold", "lean", "cut the paraphrase", "don't write for the sake of writing", or before a ביאור's student read and proof. Argument - a biur folder (e.g. discourses/007-shaar-hayichud-perushim/biur-perek-01), or a discourse for all its folders, one at a time.
---

# The lean ביאור: the middle way

Ronnie, 2026-11-24, on שער היחוד עם פירושים: "in most cases the biur is restating the bold text
without adding anything. If it is repeating the bold text then leave it out; don't force yourself to
write something for the sake of writing. Only explain terms, or if quoting from another source bring
the source in brief and in context; otherwise, if you are restating the main text, don't write
anything."

And the same day, after a pass on פדה בשלום that cut too much: "you took out biurim that were good,
explaining the sentence before. Include a decision on each: is it repeating what was said, or is it
explaining or tying to context. And a question: has the reader still understood; should I split it up
into multiple sentences with explanation. Find the middle way between removing the biur and just
repeating the bold."

So the aim is neither the most glosses nor the fewest: it is a text the student can follow, with
nothing said twice. This holds for every ביאור, beside `prompts/biur-rules.md`.

## What this reviews, and what it does not

Only the explanation woven along the text (the glosses between stretches of bold, and the footnotes).
The opening of the document (מבוא, מושגי יסוד, the outline, tables, the chapter summaries) and the סיכום
are not cut by this skill: they are Ronnie's frame, and stay unless he says otherwise.

## A decision for every gloss

Read the bold, then the gloss, and decide which it is:

1. **Repeats.** It says again what the bold has just said, in its words or in others, and the student
   would have understood the bold without it ("**X**: in other words, X"). → **Cut.** Keep the
   punctuation it carried (see below).
2. **Explains.** The bold is hard, and the gloss gives what the student would not get alone:
   - a term (a technical word, a פרצוף, a ספירה within a ספירה, Aramaic or Yiddish translated);
   - a compressed or archaic sentence said once in plain words, when it cannot be read without it;
   - the reason (the "because") that the text assumes and does not state;
   - a source the text cites or alludes to, briefly and in context, with its address;
   - where a כנ"ל, לעיל or a closing parenthesis points.
   → **Keep**, trimmed to the part that explains. If half of it repeats and half explains, cut the half
   that repeats.
3. **Ties to context.** It joins this stretch to the argument: what the question is before the text
   answers it, what a משל means in its נמשל, that this is the example of what came before, where the
   text is going ("ותחילה משל", "הדוגמה לכך מן היסודות", "מכאן תשובה לשאלה..."), or the point a student
   would miss at the end of a step. → **Keep**, short. Not a summary of what the text already concluded
   in its own words.

When unsure between repeats and explains, ask: **would a student, reading only the bold, have understood
this?** If yes, it repeats. If no, it explains.

## A question for every long stretch

After the decisions, read each run of bold that now stands without a gloss and ask: **has the student
still understood?** A long run (several clauses, a reasoning, a משל and its נמשל, a list of verses) that
a student would lose the thread of is split: break it into sentences at the text's own joints (ולכן,
אך, והנה, a new verse), and after the sentence that needs it give a short explanation of kind 2 or 3.
Do not split for the sake of splitting: a run that reads clearly stays whole.

## The sentence breaks between stretches

The writer's punctuation between two stretches of bold (a period, a comma, a colon) breaks the text,
which has almost none of its own, into readable sentences. When a gloss is cut, its punctuation stays,
and the next stretch begins a new sentence. Two stretches are joined into one bold run only when no
break is needed there.

## Steps (one chapter, one folder, at a time; each a standalone work)

1. `python scripts/check-restatement.py <folder> --all`: the inventory of every gloss, the ones whose
   words already stand in the bold flagged `RESTATES?`. The script cannot see a paraphrase in other
   words, and cannot see that a gloss explains; it shows where to look.
2. Decide every gloss (repeats / explains / ties) and record the decision with a few words of reason in
   `<folder>/notes/lean-decisions.md` (one line each: section, the gloss's first words, the decision,
   why). Ronnie reads this list.
3. Ask the long-stretch question; record each split there too.
4. Edit `biur.src.md`: cut what repeats (keeping its punctuation), trim what half-repeats, add the splits.
   Never touch the words of the text (the build holds them to `text_file`, word for word).
5. `python scripts/build-biur.py <folder> --check`, then `--pdf`. The build's notes report the gloss
   count and how many are still flagged.
6. The student read (`prompts/student-read.md`): is a term left unexplained, a source without its
   point, a pointer that does not land, a stretch the student cannot follow?
7. Proof (skill `proof-pdf`) and hand over the PDF with the count: glosses kept / trimmed / cut, splits
   added, words of explanation before → after.

Keep a line per chapter in `<folder>/notes/lean.md`: the date, the counts, and anything left for Ronnie
(a term not found in a source, a doubtful reading).
