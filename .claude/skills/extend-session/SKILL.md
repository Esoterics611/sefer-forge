---
name: extend-session
description: Add a new recording to a session that is already done (an addition to the introduction, to a הערה, to a lesson) and carry it through every step the session went through - transcript, readability, style and teaching passes, the opening part it prints in, reassembly, print and proof - without disturbing what is already finished. Use when the user says "add this voice note to the introduction", "this goes as part of <part>", "an addition to session N", "add to an existing section", or uploads a recording that continues a part already ingested. Argument - the recording's name, and the part or session it belongs to.
---

An addition is a new labelled part at the end of a finished session. Everything
already in the session stays as it is: its transcript, its `edits:` / `style:` /
`teaching:` entries, its cuts. The new part goes through the same steps, and its
entries are appended after the existing ones. The rule that holds it together:
**append, never rewrite.** The earlier entries match the earlier text exactly, so
they keep printing as before. First done 2026-11-09: `לבאר ענין הצלם.m4a` →
`discourses/004-levushei-haneshama/sessions/001` (part ג' of the introduction).
Its commit is the worked example.

0. **Which session, and that it is clean.** The part names the session. An
   opening part (`meta.yaml` `intro:`, e.g. `introduction.md`) is made from a
   session that `skip_sessions:` keeps out of the discourse; its header comment
   and the discourse's `notes.md` say which. Ask when unclear. Ask too when the
   recording could be a new session instead (one narration per box of a reading
   pack is a new session: skill `new-session`). Then run
   `python scripts/session-status.py <session>`, `python scripts/check-session.py
   <session>` and `python scripts/check-teaching.py <discourse>`. They must be
   clean before you touch the session, so that every later error is the
   addition's.
1. **The recording.** Copy it into the session's `voicenotes/` under its own
   name (Drive: skill `new-session`, step 2; the connector managed 3.5 MB through
   a subagent). The audio stays out of git.
2. **Whisper.** `python scripts/transcribe.py <session>` in the background. It
   skips the recordings already transcribed.
   - In a cloud container, `bash scripts/setup-cloud.sh` first if
     `faster_whisper` is missing.
   - The model downloads from huggingface.co, which only the `sefer-forge`
     environment allows. A session on Default is refused (proxy 403). Move it
     there with the environment tools: `get_environment`, then
     `switch_environment` to the one in `saved_for_session_repositories`.
3. **Does it read the text?** `python scripts/ocr-match.py <session>`.
   - "No reading found": an explanation only, like the introduction's parts.
   - A reading: in a laid-out session it makes a new cut (step 6). Note its
     range.
4. **Clean it, as a new part.** Follow `prompts/transcript-review-rules.md`.
   - Append it to `commentary.md` (voice-only: `transcript.md`) under the next
     label in the session's own pattern, e.g. `## הקדמה — חלק ג'`, with a comment
     naming the recording and the date.
   - Add the file to `source:`.
   - Never edit the earlier parts' body: their entries are matched against it.
   - A stretch the speaker sets aside ("למחוק", "כל זה כבר לא שייך") leaves the
     body, kept word for word in a comment, as part 1's 01:45 cut was.
   - Run `python scripts/transcript-diff.py <session>` and read every new
     Replaced and Removed entry. Added must stay 0.
5. **The passes, appended.**
   - **Readability** (`prompts/readability-pass.md`): one entry per new UNCLEAR
     flag, corrected or removed, at the end of `edits:`.
   - **Style** (`prompts/style-pass.md`): the new paragraphs only, at the end of
     `style:` (before `teaching:`). Each `from` is the text after the edits.
   - Where the passes live:
     - a narration not yet laid out: `commentary.md`'s frontmatter, then
       `python scripts/refined-text.py <session>`;
     - a laid-out session: `section-plan.yaml`, then
       `python scripts/build-section.py <session>`;
     - voice-only: `transcript.md`'s frontmatter, then `check-session.py`.
   - Until step 6, the check reports the new paragraphs as having no teaching
     entry. That error is expected; any other is not.
6. **Teaching pass** (`prompts/teaching-pass.md`, skill `teaching-pass`), for the
   new paragraphs.
   - First extend `teaching-notes.md`: the part's paragraph in **a**, the
     inventory in **b** continuing the numbering, the doubts in **c**.
   - `python scripts/apply-teaching.py <session> --draft <scratch file>` marks
     only the new paragraphs as changed. Rewrite those and leave the rest.
   - Run `--check`, then record.
   - Run `python scripts/check-teaching.py <discourse>`. The addition may now be
     the first place an idea or a name appears. Where a later part repeats it,
     that part points back or shortens (the 2026-11-09 example: Jung's full name
     moved to the introduction, so הערה ב' says "יונג"). That is the only edit to
     another session; record it through its own draft.
   - A laid-out session: confirm that the old cuts did not move.
7. **The opening part.** For a session that prints through an opening part, run
   `python scripts/sync-opening.py <session> <discourse>/<name>.md`. It writes
   `<name>.md` and `<name>.teaching.md`. For an addition it must report the
   earlier paragraphs "kept" and only new ones "added". A "changed" paragraph
   means an earlier entry moved: find out why before going on.
8. **Reassemble, print, proof.**
   - `python scripts/assemble-discourse.py <discourse> --force`, and again with
     `--lesson --force` (when `discourse.md` is only the assembled parts).
   - `python scripts/build-pamphlet.py <discourse> --png`, and `--lesson`.
   - Proof with the `proof-pdf` skill. Read the new pages closely: stretched
     lines, a lone word on a last line. Then read every later spread: the pages
     after the addition move to the other side of the spread.
   - Fix by rewording through the passes, never in the built files.
   - In a cloud container, the font errors for the stand-ins (David Libre,
     Frank Ruhl Libre) are expected.
9. **Record and hand over.**
   - Add a line on the addition to the discourse's `notes.md`, then
     `teaching-notes.md` **d**, the coverage.
   - Commit the transcripts (`*.raw.txt`, `*.timed.txt`) and the text, never
     the audio. Push.
   - Send the PDFs, since `output/` is not in git.
   - Report:
     - where the part went;
     - the `review.md` counts, with the new Replaced and Removed entries;
     - each UNCLEAR flag with its time, and the readability decisions;
     - a style sample;
     - the teaching words, before → after;
     - any change to another part;
     - the proof line;
     - the questions for the speaker: a stretch left out at his word, a
       garbled phrase removed.
