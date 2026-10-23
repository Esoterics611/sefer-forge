---
name: paired-layout
description: Lay out a session (or move an older one) in the house standard - each page opens with a cut of the original text and carries below it the speaker's explanation of that passage, matched by his reading, with no boxes - then print, proof and run the readability pass. Use when the user says "pair the text and the explanation", "text on top, explanation below", "apply the new layout", "fix it retroactively", or when a session's section.md is still in the old three-section layout. Argument - a session path, or a discourse path for every session in it.
---

The standard (docs/print-standard.md): the passage on top of the page, its explanation
below, on the same page; the explanation never boxed. The pairing is found, not
chosen: the speaker reads a passage and then explains it, so the explanation that
follows a reading belongs to it ("the same words are in both").

For each session in `$ARGUMENTS` (images+voice sessions; `python scripts/session-status.py`
shows which are done):

1. **The plan.** If the session has no `section-plan.yaml`, write one from its current
   `section.md`: `title` (frontmatter), `heading` and `lines` (the title block),
   `nusach.start`/`end` (the printed range: its first and last words), `breaks` (the
   first words of each paragraph the old section split out beyond the print's own),
   `bold`, `footnotes` (the print's notes and the words they follow), and `keys` (the
   key points). Drop any `boxes:`: the pairing replaces them.
2. **Build.** `python scripts/build-section.py <session> --force` (once, to replace a
   hand-made section.md; after that without `--force`). It cuts the text where the
   speaker reads, snaps each cut to a sentence or clause end, and pairs each cut with
   the explanation that follows it; `check-session.py` must pass.
3. **Print.** `python scripts/build-pamphlet.py <session>`: the page engine measures every
   cut and explanation piece, fills each page text first, opens a page that continues
   an explanation with a "המשך הביאור על" line, and checks no page spills. It reports
   the paired pages and the renders the page check took.
4. **Proof** by the `proof-pdf` skill, then the **readability pass**
   (`prompts/readability-pass.md`): read the explanation as its reader will, and
   correct or remove the short garbled segments, as `edits:` in the plan. Rebuild
   (steps 2–3) and proof again.
5. **Style pass** (`prompts/style-pass.md`), for a new session (older sessions only when
   the user asks): read the explanation once more and make its spoken Hebrew written,
   as `style:` in the plan, leaving the quoted readings exactly as they are. Rebuild,
   confirm the cuts did not move, proof again.

**Voice-only lessons** (a `transcript.md`) need no plan: `build-pamphlet.py` pairs each
topic heading (`##`) and the passage read (`>`) on top with the explanation that follows
them below; a lead-in line between a heading and its passage opens the explanation. A
lesson that quotes nothing prints as running text. In a whole-discourse pamphlet each
lesson's title shares its first page with its first passage.

Report per session: the cuts and explanations paired, pages, edits (corrected /
removed / left for the user), and the proof summary line.
