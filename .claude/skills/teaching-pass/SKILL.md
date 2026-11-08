---
name: teaching-pass
description: The last step of every narration - the explanation rewritten from a lesson transcript into a written commentary on the text (impersonal, each idea once, about half the length); it is what prints, and the lesson text stays available with --lesson. Self-checked - an understanding note and idea inventory first, mechanical checks, a repeat scan across the discourse, and a page-by-page read-back. Use when the user says "teaching pass", "make it instructional", "turn it into a commentary", "from conversational to teaching", "not a transcript of a lesson", or "cut it by half". Argument - a session path, or a discourse path for all its sessions.
---

Follow `prompts/teaching-pass.md`, steps 0–7, for `$ARGUMENTS` (a discourse: every
session with an explanation, and its opening parts).

- Step 1 comes first and is written down (`<session>/teaching-notes.md`): what the part
  teaches in your own words, the numbered idea inventory with keep / repeat / drop, and
  the doubts. Writing before understanding is the failure this pass exists to prevent.
- Drafts go through `scripts/apply-teaching.py` (`--draft`, then `--check`, then record);
  never edit `teaching:` by hand. The cuts never move: content stays under its cut.
- Never misquote, never add an idea, never settle a doubtful claim yourself: keep it as
  said and list it for the speaker.
- The teaching text is what prints (`build-pamphlet.py`, `output/pamphlets/`); the lesson
  text prints with `--lesson` into `output/pamphlets/lesson/`. Report words before → after
  per part, what was cut as repetition, and the open questions.
