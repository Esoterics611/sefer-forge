# Style pass

The last step of a session, after the pamphlet is printed, proofed and through
the readability pass (`prompts/readability-pass.md`). The explanation reads
well by then, but it is still speech: "אז", "עכשיו", "בוא נגיד ככה",
restatements, self-corrections, the speaker managing his lesson. This pass
turns it into written Hebrew, factual and direct, without touching what is
said.

It is a reading pass, done by reading the printed explanation through,
paragraph by paragraph, never by search and replace. What already reads as
writing stays; everything that reads as talk changes. The bar: a reader of the
pamphlet cannot tell the explanation was spoken. Removing the obvious markers
is not enough (Breishis 002's first pass did only that and still read as a
transcript).

## Change

- Speech markers and tics: אז, עכשיו, כן?, בוא נגיד ככה, זאת אומרת (as
  filler), עוד פעם, דרך אגב, כאילו, ממש (as filler), "נגיד", וכולי, סתם.
- The speaker running the lesson: "אני קופץ קצת וממשיך", "נמשיך עוד קצת",
  "בדיוק כמו שאמרנו", "תסתכלו ב..." (→ "ראה ..."); openers that announce
  what comes ("בקצרה,", "בפרטים:", "והנקודה כאן היא", "כאן הוא אומר ש" →
  "כאן מבואר ש"); back-references to the lesson ("שאמרנו", "כמו שאמרנו
  למעלה" → "לעיל", "כנזכר", or nothing when the point is plain).
- Self-corrections: keep what he corrected to and drop what he took back
  ("סליחה, זה העניין: ..." keeps only the corrected statement).
- False starts and restatements that say again, in other words, what the
  sentence before or after says in full: remove the weaker copy.
- Spoken syntax: "זה עניין של" → "זהו עניין", "שזה" chains and "זה" as a
  copula ("זה הבירור הראשון", "וזה עניין הגאולה") → a clear subject and
  verb ("זהו", "הוא"), a rhetorical question → the statement it asks for,
  "בן אדם" → "אדם", "פה" → "כאן", "עניינים של ניסים" → "ניסים".

## Keep

- Every idea, example, story, source and reference, in the speaker's order,
  and the argument's flow from one paragraph to the next.
- The readings: the words of the text he reads aloud, in quotation marks, stay
  exactly as they are. They place each explanation under its passage on the
  page; a paragraph that holds a reading is never removed.
- His terms and his voice where it carries meaning: an image, an emphasis, a
  personal example.
- Hebrew stays Hebrew; Aramaic and quoted verses stay as quoted.

## Never

Add an idea, a source, a conclusion or a transition he did not make; correct
what he said (a slip in a reference stays); merge, split or reorder
paragraphs; summarize. When a rewrite would change what a sentence claims,
leave the sentence as it is.

## How

The pass is recorded, like the readability pass, as a list of exact
replacements, so `commentary.md` (or a voice-only `transcript.md`) stays the
faithful record of what was said:

    style:                       # in section-plan.yaml, after `edits:`
      - from: אז זה העניין של התפילה, שעל זה מתפללים, שזה העניינים הארציים,
        to: על העניינים הארציים האלה מתפללים,

`from` is the text as it reads after the readability edits (and after the
style edits above it), and must occur once. A voice-only lesson puts the same
`style:` list in `transcript.md`'s frontmatter. Then:

1. `python scripts/build-section.py <session>` (its check compares the
   explanation with `commentary.md` plus `edits:` and `style:`), or for a
   voice-only lesson `python scripts/check-session.py <session>`;
2. confirm the pairing did not move: the cuts and their explanations are the
   same as before the pass;
3. `python scripts/build-pamphlet.py <session>`, the proof
   (`proof-pdf`), and a last read of every spread.

Report the number of style edits and a short before/after sample, and list any
sentence left conversational on purpose.
