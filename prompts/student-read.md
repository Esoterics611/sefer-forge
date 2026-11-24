# The student read: a ביאור read as its student will read it

Set by Ronnie on 2026-11-21 ("add an additional read as student; it should be part of the workflow"),
after the ביאור of שער היחוד פרק א. A step of every ביאור (`prompts/biur-rules.md`), and of every
reading or teaching PDF made from one (a pamphlet, a handout): after the build is clean (`--check`
covers the whole text) and before the proof (skill `proof-pdf`). It does not replace the independent
check of claims (`prompts/opus-after-fable-biur.md` step 2); it asks a different question: not "is it
true?" but "can a student follow it?"

## The reader

A student who reads Hebrew well, has learned some Chassidus (knows that there are ten ספירות, that
חכמה בינה ודעת are the mind, that the soul has levels), and has never seen this text or its sources.
Read `biur.md` (the built file, with the text and the sources set in), not `biur.src.md`, from the
title to the סיכום, in order, at the pace of study. Where the session can run a reader that has not
seen the writing (a subagent given only the built file), that reader is better; otherwise the writer
reads, deliberately as this student.

## What stops a student (check each paragraph)

1. **A term not explained**: used before it is explained, or never; a name of a פרצוף, a ספירה within
   a ספירה, a technical word (היולי, תפסן), a phrase of Aramaic or Yiddish. Explain it in place in a few
   words, or in a footnote if it needs more, resting on the text or a source (nothing from memory).
2. **A reference that does not land**: "כנ"ל", "לעיל", "בסעיף N", "כפי שיתבאר": does it point where it
   says, and is what it points to recognisable from here?
3. **A pointer that cannot be followed**: the text says "כנ"ל" or closes a parenthesis and the reader
   cannot find where. Say where, in a few words. The text's own steps are not retold (skill `lean-biur`).
4. **A gloss that does not explain**: it repeats the words, or names a source without saying what
   the source adds here.
5. **A source set in without its point**: after reading the quoted passage, is it clear which words
   matter and what they show? (Mark them with `mark=`; say it in the sentence after.)
6. **A gloss that restates**: whatever re-says the bold, in its words or in others, is cut, and the
   text runs on (skill `lean-biur`). The student read never adds a gloss that is not a term, a source
   or a pointer.
7. **A claim the student cannot check**: a statement about a letter, a number or a verse that the text
   does not make and no source given supports. Take it out or give the source.

## Record and fix

- Write the findings to `<biur folder>/notes/student-read.md`: section, what stopped the reader, and
  the fix (applied, or left, with the reason). One line each.
- Fix in `biur.src.md`. The fixes follow `prompts/biur-rules.md` like every other sentence: no first
  person, no instructions to the reader, no "שים לב".
- Rebuild (`python scripts/build-biur.py <folder> --check`, then `--pdf`) and go on to the proof.
- Add to the lexicon the terms the read found missing (skill `chassidus-context`, "After the work").
