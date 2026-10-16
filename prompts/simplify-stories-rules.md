# Simplified-story rules

Applies when Claude rewrites the stories of `shivchei-habesht.md` into
`shivchei-habesht-simple.md`: modern Hebrew a high-school student reads
unaided, each story followed by a summary. The rewrite changes the language
and never the story.

Work from the Hebrew source only, never from `shivchei-habesht-english.md`.

## Allowed

- Modern vocabulary and syntax, short sentences, paragraph breaks.
- Expanding abbreviations (`פ"א` → `פעם אחת`, `ר'` → `רבי`, `הנ"ל` → the
  name it points to).
- Dropping honorifics and pious interjections (`ז"ל`, `זיע"א`, `זללה"ה`,
  `ח"ו`, `ר"ל`).
- One short form per person, used throughout the story (`הרב הק' מ' יחיאל
  מיכל מזלאטשוב` → `רבי מיכל מזלוטשוב`, then `רבי מיכל`). The Besht is
  always `הבעל שם טוב`.
- Place names in their common modern Hebrew spelling (`מעזיבוז` →
  `מז'יבוז'`, `בראד` → `ברודי`, `נעמרוב` → `נמירוב`); otherwise as the
  source spells them.
- A gloss in parentheses for a foreign word, measure, object or term the
  reader cannot know: `ווקילאק (מין זאב-אדם)`, `פרסה (כמה קילומטרים)`. A
  gloss explains a word; it never adds to the plot.
- Splitting a run-on sentence, and turning reported speech into direct
  quotation, provided the speaker stays the same.
- A short title after the story number in each heading.

## Not allowed

- Adding an event, motive, description, feeling, line of dialogue, or reason
  why something happened.
- Adding a lesson. The author's introduction says he deliberately left the
  lesson of each story to the reader; the rewrite and the summary do the same.
- Dropping an event, a line of dialogue that moves the story, the chain of who
  told it (`שמעתי מ...`), or a side note or alternate version the author or
  printer inserted.
- Reordering events, or moving a side note away from where the source has it.
- Changing what anyone says, believes or does; softening the supernatural;
  resolving what the source leaves open (an unclear "he", an unstated reason).

## Side notes

A parenthesised side note stays in parentheses at the same point. One longer
than a paragraph is set as a `>` blockquote.

## Flags

Where the source is garbled or its meaning uncertain, write the most literal
reading and flag it:

    <!-- UNCLEAR: <source words> | <what the rewrite says and why it is uncertain> -->

Content a parent or teacher may want to see before a child reads it (crude
bodily detail, sexual content, graphic violence) stays in the story, worded
plainly and modestly, and is flagged:

    <!-- MATURE: <one line> -->

## Per story

1. **Beats.** Before rewriting, list the story's beats in order in
   `shivchei-habesht-simple-beats.md` under the same heading: who told it,
   each event, each line of dialogue that moves the story, each side note,
   the ending. One line each.
2. **Rewrite** from the source text, not from the beats.
3. **Check** the rewrite against the beats: every beat present and in order;
   nothing in the rewrite without a beat except glosses and the title. Fix
   until both hold.
4. **Summary** under `**סיכום:**`: two to four sentences on what happens and
   how it ends. No lesson.

## Per batch

- The simple file's `##` headings match the source's one to one, in order.
- A story whose rewrite is under 40% of the source's length is re-read
  against its beats.
- The report lists every UNCLEAR and MATURE flag added.
