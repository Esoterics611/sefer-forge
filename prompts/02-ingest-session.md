# START PROMPT — INGEST SESSION (photos + voicenote)

Use this once per ingestion batch. One session = one set of book-page photos + one Hebrew voicenote in which the speaker reads the photographed text aloud and explains it.

Or just say **"ingest session discourses/NNN-<slug>/sessions/MMM"**: the `ingest-session` skill loads this prompt and resumes from wherever the session stands. `/new-session <slug>` makes the folder, takes the files and starts Whisper.

**Before:** the photos are in `<SESSION_PATH>/images/`, the voicenote in `<SESSION_PATH>/voicenotes/`.

---

> Ingest session `<SESSION_PATH>`.
>
> **Step 0 — Where it stands.** Run `python scripts/session-status.py <SESSION_PATH>` and start at the first step that is not done. Never redo a finished step: a crash or a restart leaves finished files in place. If the voicenote is not transcribed, start Whisper now, in the background: `python scripts/transcribe.py <SESSION_PATH>` (an interrupted run resumes where it stopped). It takes about 0.9× the recording's length on the GPU, 2.4× on the CPU (`session-status.py` shows the estimate), so do the OCR while it runs.
>
> **Step 1 — OCR** (skip if `ocr.md` covers every photo). Follow `.claude/skills/ocr-session/SKILL.md`: cut the photos into strips with `scripts/ocr-strips.py`, read them strip by strip into a line-by-line draft, check the line count, write `ocr.md`, then a second pass against the strips.
>
> **Step 2 — Match the OCR to the reading** (once Whisper is done). Run `python scripts/ocr-match.py <SESSION_PATH>` and read `<SESSION_PATH>/ocr-match.md`.
> - For every *heard, not in OCR*, *in OCR, not heard* and *differs* entry, look at the strip that holds the line. If the photo shows the OCR missed or misread something, correct `ocr.md` now. If the photo agrees with the OCR, the speaker added, skipped or misread: leave it.
> - Of the *spelling-level* entries, check only those that could be OCR errors; the rest are Whisper's.
> - Re-run until every remaining entry is explained. `ocr.md` is final after this step.
> - Note the **reading range**. The נוסח printed for this session is the text the speaker reads; OCR text outside the range stays in `ocr.md` as the record, and the plan leaves it out.
>
> **Step 3 — Clean the transcript.** Read `prompts/transcript-review-rules.md` first. Clean the `*.fixed.txt` (with its `*.timed.txt`) into `<SESSION_PATH>/commentary.md`: the full voicenote, in the speaker's words. Where he reads the text, his words are a quotation of `ocr.md`: correct Whisper's mis-hearings of it from there, and put the reading in quotation marks. The *commentary stretches* in `ocr-match.md` show where reading stops and explaining begins. Then run `python scripts/transcript-diff.py <SESSION_PATH>`, read `review.md`, and revert every change the rules do not allow. Re-run until it is clean.
>
> **Step 4 — Plan and build `section.md`.** Run `python scripts/build-section.py <SESSION_PATH> --init` and fill in `section-plan.yaml` (its header and the script's docstring show every field):
> - `title`, `heading`, `lines`: the title block. `heading` is the parsha or gate; `lines` name the session's subject in a few words each.
> - `nusach.start` / `end`: the reading range from Step 2. `breaks`: split the print's long paragraphs at sentence boundaries where the argument turns, every 3–8 printed lines. `bold`: the print's large opening words.
> - `footnotes`: the print's notes, if `ocr.md` has a `[Footnotes:]` block.
> - `keys`: 5–8 passages that carry the session's argument, each a verbatim stretch of the נוסח, with a short Hebrew label.
> - No pairing to decide: the build cuts the text where the speaker reads and pairs each cut with the explanation that follows it (`docs/print-standard.md`).
>
> Write values unquoted; a value containing `: ` goes under `key: >-` on the next line. Run `python scripts/build-section.py <SESSION_PATH>`. It writes `section.md` and runs `scripts/check-session.py`, which must report no errors.
>
> **Step 5 — Read it through.** Read `section.md` from top to bottom, as its reader will: does each explanation follow the passage it explains, are the key points the passages the argument turns on, does the title say what the session is about? Fix in the plan and rebuild. Then print it, `python scripts/build-pamphlet.py <SESSION_PATH>`, and proof the PDF by the `proof-pdf` skill (`docs/print-standard.md`): `python scripts/proof-pdf.py output/pamphlets/<discourse>-<session>.pdf` with no errors, then every spread read and every finding fixed. Then the **readability pass** (`prompts/readability-pass.md`): correct or remove the short segments Whisper garbled, as `edits:` in the plan; rebuild and proof again.
>
> **Step 6 — Style pass** (the last step; `prompts/style-pass.md`). Read the explanation through once more and turn the spoken Hebrew into written Hebrew: speech markers, self-corrections, false starts and restatements go; meaning, examples, sources and order stay; the readings in quotation marks are never touched. Draft it with `python scripts/style-pass.py <SESSION_PATH> --draft <scratch>/draft.txt`, rewrite the draft, and hand it back (`python scripts/style-pass.py <SESSION_PATH> <scratch>/draft.txt`): the script records it as `style:` in the plan and rebuilds, and the build fails if a reading changed or the cuts moved. Fix every speech warning or say why it stays; print, proof, and read every spread.
>
> **Step 7 — Report**, in one message:
> - the `session-status.py` line for the session;
> - the reading range, and every correction made to `ocr.md` from the match, each with what the photo shows;
> - the speaker's departures from the text that were left as spoken;
> - the counts line from `review.md`, every Added entry with its reason, and every UNCLEAR flag with its time;
> - the readability edits (corrected / removed / left for the user), and the style edits with a short before/after sample;
> - the `check-session.py` result, the pamphlet's path and its proof summary line, and the visual findings fixed or left.
>
> **Rules:**
> - Hebrew stays Hebrew — never translate.
> - Plain markdown only. Do NOT invoke any docx/pptx/xlsx skill.
> - Do NOT transcribe audio yourself — only `scripts/transcribe.py`, and use only its `.fixed.txt` / `.timed.txt`.
> - Never edit the photos, the audio, `*.raw.txt`, or `ocr.md` after Step 2.
> - `section.md` is built from the plan: change the plan and rebuild, never the built file.
