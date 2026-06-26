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
> **Step 1 — OCR every image.**
> Read every image in `<SESSION_PATH>/images/`. OCR the full Hebrew text exactly as printed — all images, every paragraph, in reading order. Preserve paragraph breaks. Mark text the author underlined in the photo as `[text]{.underline}`. If a page starts or ends mid-sentence (partial snapshot), prefix or suffix with `...`. Write the combined OCR to `<SESSION_PATH>/ocr.md` with one `## Image: <filename>` heading per image. If any text is unclear, flag it inline as `<!-- UNCLEAR: <what you see> -->` rather than guessing.
>
> **Step 2 — Clean the transcript.**
> Read every `*.raw.txt` in `<SESSION_PATH>/voicenotes/`. Clean up Whisper's output: remove fillers (אה, אמ, repetitions, false starts); fix obvious transcription errors using the Hebrew source in `ocr.md` for context (e.g. proper names, technical terms the voicenote references); preserve the speaker's voice, structure, and meaning — do not paraphrase or summarize. Write to `<SESSION_PATH>/commentary.md`.
>
> **Step 3 — Assemble `section.md`.**
>
> Output layout — three sections, in this exact order:
>
> 1. **YAML frontmatter** — `session`, `discourse`, `title` (Hebrew), any other metadata you can infer.
>
> 2. **Title block** — bold gate title, a `--------- ◆ ---------` separator, then one-line subject lines naming עניין/נושא/גרסה. Each Hebrew line as its own paragraph wrapped in `[text]{dir="rtl"}`.
>
> 3. **`## הַנֹּסַח הָעִקָּרִי`** — The full OCR text as flowing Hebrew paragraphs. Rules:
>    - Each paragraph wrapped in `[text]{dir="rtl"}`.
>    - Bold key transitional words exactly as they appear bold in the source (e.g. `**וְהִנֵּה**`, `**אַךְ**`, `**וּבֵיאוּר הַדְּבָרִים**`).
>    - Preserve leading/trailing `...` snapshot markers for cut-off text.
>    - Preserve `<!-- UNCLEAR: ... -->` inline for illegible passages — do not guess.
>    - Do NOT use `{.underline}` here — the nusach section is plain flowing text.
>
> 4. **`## נְקֻדּוֹת מַפְתֵּחַ`** — 5–8 key phrases that anchor the session's main ideas. Format: bold Hebrew topic label on its own line, then a `>` blockquote with the exact source passage, all in `{dir="rtl"}`:
>    ```
>    **[תְּשׁוּבָה לְאֻמּוֹת הָעוֹלָם]{dir="rtl"}**
>
>    > [exact source phrase]{dir="rtl"}
>    ```
>
> 5. **`## בֵּיאוּר וּפֵירוּשׁ`** — A sequence of single-column pandoc grid-table commentary boxes, one per topical section of the voicenote. Each box:
>    ```
>    +--------------------------------------------------------------------+
>    | **[■ ביאור — <topic label in plain Hebrew>]{dir="rtl"}**           |
>    |                                                                    |
>    | [voicenote paragraph(s) for this topic, cleaned from commentary.md]|
>    | [each paragraph as its own {dir="rtl"} span]{dir="rtl"}           |
>    +--------------------------------------------------------------------+
>    ```
>    - One box per distinct topic from `commentary.md`. Keep the speaker's voice — do not summarize or shorten.
>    - Every paragraph of `commentary.md` must appear in exactly one box. Nothing dropped, nothing duplicated.
>
> **Rules:**
> - Hebrew stays Hebrew — never translate.
> - Plain markdown only. Do NOT invoke any docx/pptx/xlsx skill.
> - Do NOT transcribe audio yourself — use only the existing `.raw.txt`.
> - When done, show me `## הַנֹּסַח הָעִקָּרִי` so I can spot-check before you write the rest.
