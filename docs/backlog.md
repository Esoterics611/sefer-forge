# Backlog

Work found and deliberately left for a fresh session. Each item says what is
wrong, how it was found, and how to do it.

## Re-clean the old transcripts under the review rules (found 2026-10-21)

**In progress (2026-10-21, branch `transcript-reclean`).** Cause found: every
old `.raw.txt` came from openai-whisper *medium* (June 2026), with no
`.timed.txt`. The nine recordings were re-transcribed with ivrit.ai large-v3
on the GPU; where the new text is better it becomes `.raw.txt` /
`.timed.txt` and the medium text stays beside it as `<audio>.medium.txt`.
Done (2026-10-22): Shaar HaYichud 000–003 and 010–012 re-cleaned (added 0,
readability edits in the frontmatter); 010–012 printed and proofed, the book
and the whole-discourse pamphlet rebuilt and proofed; 000–003 left unprinted
at the user's word. Lag BaOmer 001 and 002: OCR re-read in full, commentary
re-cleaned from the new transcripts (1,533 and 1,773 words, added 0), paired
sections with readability edits, pamphlets 11 and 17 pages, proofs clean.
Old sessions get no style pass (prompts/style-pass.md) unless the user asks.

**Still open:** Lag BaOmer's `discourse.md` (printed in the siddur book) is
the old hand-edited one, built from the summarized commentary. Re-assembling
it from the new sessions overwrites those hand edits, so it waits for the
user's approval (`python scripts/assemble-discourse.py
discourses/001-lag-baomer --force`, then `build-all.sh siddur` and the proof).

`python scripts/check-session.py` flags them. The transcripts were cleaned
before `prompts/transcript-review-rules.md` existed, from the `.raw.txt` files
still in the repo (committed together, never regenerated), and they do not
follow the speech:

- **Shaar HaYichud 000–003, 010–012** (`transcript.md`): 3–13 added word
  runs per lesson, and far more inside the "replaced" entries. The text was
  rewritten and reordered: source passages Whisper never heard were inserted
  (012: "ממשיך הרב" became a long quotation from the book), the speaker's
  own reading was moved, and garbled words were reconstructed
  ("והכולשו" → "והקדוש ברוך הוא חד ותלמודה", years added in 010).
  Removing the flagged additions alone leaves broken text.
- **Lag BaOmer 001, 002** (`commentary.md`): summarized, not transcribed
  (001: 547 words for Whisper's 1,469), with added runs. Its `section.md`
  is the pre-2026-10-15 layout (grid tables, pointed נוסח) and the siddur
  book prints it through a hand-edited `discourse.md`.

**How:** for each session, re-clean from `voicenotes/*.fixed.txt` and
`*.timed.txt` under the rules, as Breishis 002 was (prompt 02 step 3 / 02v
step 2): the full speech, corrections only where attested, timed UNCLEAR flags
for the rest. Keep the old version's sound structure (topic headings, readings
as quotations, source footnotes) where it matches the speech. Loop
`transcript-diff.py` to added 0. Then rebuild the books and proof them.
Shaar HaYichud 000–003 are skipped from the book (`skip_sessions`), so the
book changes only through 010–012. For Lag BaOmer, also move the sessions to
the paired layout (`.claude/skills/paired-layout`), which needs ocr-match on
its OCR (107 UNCLEAR flags, English photo notes as plain text: clean those
first), and re-assemble `discourse.md` with the user's approval.

## Readability pass for voice-only lessons (found 2026-10-21)

**Done (2026-10-21):** `edits:` (and now `style:`) in `transcript.md`'s frontmatter,
applied by assemble-discourse and build-pamphlet, checked by check-session.

Photo sessions record the readability pass (`prompts/readability-pass.md`) as
`edits:` in `section-plan.yaml`. Voice-only lessons print `transcript.md`
directly and have no plan, so the pass has no home yet. When the Shaar
HaYichud transcripts are re-cleaned (above), give the edits one: an `edits:`
list in the transcript's frontmatter, applied by `assemble-discourse.py` and
`build-pamphlet.py`, checked by `check-session.py`.
