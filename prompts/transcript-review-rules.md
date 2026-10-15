# Transcript review rules

Applies whenever Claude turns Whisper output (`voicenotes/*.fixed.txt`) into
`commentary.md` (photo sessions, `prompts/02-ingest-session.md`) or
`transcript.md` (voice-only sessions, `prompts/02v-ingest-voice-session.md`).

Claude cannot hear the audio. Every change rests on evidence in the repo, or
it is not made.

## Allowed

- Remove fillers (אה, אמ, אממ), false starts, and immediate repetitions.
- Fix spelling, and words Whisper split or merged.
- Replace a mis-heard word when the correct form is attested in the session's
  `ocr.md`, in `glossary/whisper-fixes.yaml`, or in a pasuk, maamar or source
  the speaker is plainly quoting. The replacement must sound like what Whisper
  wrote.
- Punctuation, quotation marks, abbreviations (`הנל` → `הנ"ל`), paragraph
  breaks.
- Numbers Whisper wrote as digits, spelled out (`ה-70 שרים` → `השבעים שרים`).
- Format the prompt requires: `##` headings and footnote citations in
  `transcript.md`; box labels in `section.md`. These are not speech and the
  diff skips them.

## Not allowed

- Adding a word, idea, transition or example that is not in the Whisper text.
- Completing a sentence the speaker left unfinished.
- Rephrasing for style, reordering, summarizing, shortening.
- Correcting what the speaker said (a misquote, a slip, an opinion). Only what
  Whisper heard is corrected.
- Aligning a quotation with `ocr.md` when the speaker paraphrased it.

## When unsure

Keep Whisper's words and put a flag right after them:

    <!-- UNCLEAR 04:12: <what Whisper wrote> → <best guess> -->

`04:12` is the start time of the `.timed.txt` line containing the passage, so
the user can re-listen there. Sessions transcribed before `.timed.txt`
existed omit the time.

Lost audio (noise, foreign-language fragments, nonsense) is flagged
`<!-- UNCLEAR 04:12: inaudible -->`. Its content is never reconstructed.

## Check

After writing, run `python scripts/transcript-diff.py <SESSION_PATH>` and read
`<SESSION_PATH>/review.md`. It lists every word removed, replaced or added
relative to Whisper.

- Every **Added** entry (words with nothing removed beside them) is either a
  rule above, named in the final report, or reverted.
- Every **Replaced** entry must fit an Allowed rule; revert the rest.
- For photo sessions, the section.md check must read "identical": the ביאור
  boxes carry `commentary.md` word for word.

Report in the final message: the counts line from `review.md`, each Added
entry with its reason, and each UNCLEAR flag with its time.
