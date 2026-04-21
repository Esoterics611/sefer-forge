# START PROMPT — INGEST SESSION

Use this once per ingestion batch. One session = one set of book-page photos + one Hebrew voicenote.

**Before pasting:**
1. Images are already in `<SESSION_PATH>/images/`.
2. Voicenote (`.m4a` etc.) is already in `<SESSION_PATH>/voicenotes/`.
3. You have already run `python scripts/transcribe.py <SESSION_PATH>` and a `.raw.txt` exists next to the audio file.

Replace `<SESSION_PATH>` (e.g. `discourses/001-teshuvah-intro/sessions/003`).

---

> Ingest session `<SESSION_PATH>`.
>
> **Step 1 — OCR the images.**
> Read every image in `<SESSION_PATH>/images/`. OCR the Hebrew text exactly as printed. Preserve paragraph breaks. Mark text the author underlined in the photo as `[text]{.underline}`. If a page starts or ends mid-sentence (partial snapshot), prefix or suffix with `...`. Write the combined OCR to `<SESSION_PATH>/ocr.md` with one `## Image: <filename>` heading per image. If any text is unclear, flag it inline as `<!-- UNCLEAR: <what you see> -->` rather than guessing.
>
> **Step 2 — Clean the transcript.**
> Read every `*.raw.txt` in `<SESSION_PATH>/voicenotes/`. Clean up Whisper's output: remove fillers (אה, אמ, repetitions, false starts); fix obvious transcription errors using the Hebrew source in `ocr.md` for context (e.g. proper names, technical terms the voicenote references); preserve the speaker's voice, structure, and meaning — do not paraphrase or summarize. Write to `<SESSION_PATH>/commentary.md`.
>
> **Step 3 — Assemble section.md.**
> Write `<SESSION_PATH>/section.md` with:
> - YAML frontmatter: `session` (the NNN from the path), `discourse` (parent folder name), any title you can infer.
> - **Three-part structure** (in this order):
>   1. **מקור — Source text** (`## מקור`): The full OCR'd source text as one contiguous blockquote. Present every passage from `ocr.md` in reading order; keep `<!-- UNCLEAR: ... -->` flags inline where they appear. Do not interleave commentary here.
>   2. **נקודות מפתח — Key highlights** (`## נקודות מפתח`): Pull 3–6 short phrases or sentences from the source that the speaker's commentary turns on. Each as its own blockquote line, with a one-line bold label naming the concept (e.g. `**חידוש הבריאה:**`).
>   3. **ביאור — Commentary** (`## ביאור`): The full cleaned commentary from `commentary.md`, in plain paragraphs, in the order the speaker develops the ideas.
> - Preserve every `[...]{.underline}` marker and every `...` snapshot marker verbatim.
>
> **Rules:**
> - Hebrew stays Hebrew — never translate.
> - Plain markdown writes only. Do NOT invoke any docx/pptx/xlsx skill.
> - Do NOT transcribe audio yourself — use only the existing `.raw.txt`.
> - When done, show me the first ~30 lines of `section.md` so I can spot-check.
