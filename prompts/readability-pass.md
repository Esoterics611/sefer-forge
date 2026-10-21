# Readability pass

Applies after a session's pamphlet is printed and proofed (prompt 02 step 5,
prompt 02v step 6, the `publish-pamphlet` and `proof-pdf` skills), and earlier
wherever a garbled segment is plain to see. It is not part of the transcript
cleanup: `commentary.md` (or a voice-only lesson's `transcript.md`) stays the
faithful record of what Whisper heard, under
`prompts/transcript-review-rules.md`. This pass decides what the printed
explanation leaves out or corrects, and records every decision.

About 98% of a cleaned explanation reads well. The rest is a phrase or a short
sentence Whisper mangled (usually one carrying an UNCLEAR flag) that leaves a
reader confused. Each such segment gets one of three answers:

- **Correct it** when the intended words are clear from the context, the
  source being read, a verse or saying being quoted, or the speaker's own
  wording elsewhere: "נשע בהמית" → "נפש הבהמית", "הבשם טוב" → "הבעל שם טוב".
  The correction says what he meant, in his words; it never adds an idea.
- **Remove it** when it cannot be recovered and the sentence around it reads
  whole without it: "רוח הוואי, מה שנקרא, ונחל עבור החוואי". Remove the
  least that clears the confusion: a word, a phrase, at most a sentence.
- **Leave it** when it is odd speech but its meaning comes through. Spoken
  style, repetition that carries emphasis, and loose grammar stay.

Never: rephrase intelligible speech for style, summarize, reorder, add an
idea, or remove anything a reader needs. A segment longer than a sentence, or
one whose removal would change the argument, is not this pass's to decide:
list it for the user.

## How

Read the pamphlet's explanation from start to finish as its reader will, with
`commentary.md`'s UNCLEAR flags beside it. For each segment to fix, add an
entry to the session's `section-plan.yaml`:

    edits:
      - from: נשע בהמית          # the exact words in commentary.md; must occur once
        to: נפש הבהמית           # empty to remove
        why: Whisper; the term is plain from the context

A flag on the edited words goes with them. Then rebuild and recheck:
`python scripts/build-section.py <session>` (it runs `check-session.py`,
which compares the explanation with `commentary.md` plus these edits),
`python scripts/build-pamphlet.py <session>`, and the proof.

**Voice-only lessons** have no plan: the same `edits:` list goes in
`transcript.md`'s frontmatter (`from` = the exact words in the transcript's
body). The book (`assemble-discourse.py`) and the pamphlet apply them;
`transcript-diff.py` still compares the transcript itself with Whisper;
`python scripts/check-session.py <session>` checks that each `from` matches
once. Then rebuild the book and the pamphlet, and proof both.

Report: how many segments were corrected and how many removed, and every one
left for the user.

After this pass comes the last one, the style pass (`prompts/style-pass.md`):
the speech made into written Hebrew, as `style:` beside `edits:`.
