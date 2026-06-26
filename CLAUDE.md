# sefer-forge — conventions for Claude sessions

## What this repo produces
A Hebrew book assembled from **discourses**. Each discourse is built up across multiple **sessions** of image+voicenote ingestion. A discourse later becomes (typically) a **chapter** in the final book.

## Unit hierarchy
- **session** = one ingestion batch (~N images + 1 Hebrew voicenote).
  Location: `discourses/<NNN>-<slug>/sessions/<MMM>/`
  Outputs in that folder: `ocr.md`, `commentary.md`, `section.md`.
- **discourse** = 1..N sessions woven into a cohesive essay.
  Location: `discourses/<NNN>-<slug>/discourse.md`
- **chapter** = 1..N discourses assigned in `book/structure.yaml`.
- **book** = compiled at `compiled/book.md` → rendered at `output/book.docx`.

## Source-of-truth rules
- **Never edit**: raw audio (`.m4a` etc.), image files, `*.raw.txt` (raw Whisper), `ocr.md`.
- **Generated but editable**: `commentary.md`, `section.md`.
- **Hand-edit freely**: `discourse.md` — this is where you polish for flow across sessions.
- **Never hand-edit**: anything in `compiled/` or `output/`.

## Markdown conventions
- **Snapshot marker**: leading/trailing `...` on text that was cut off in the photo.
- **RTL wrapping**: every Hebrew paragraph is wrapped in `[text]{dir="rtl"}`.
- **`section.md` layout = three named sections:**
  1. `## הַנֹּסַח הָעִקָּרִי` — full OCR text as flowing `[...]{dir="rtl"}` paragraphs; bold key transitional words; preserve `...` snapshot markers and `<!-- UNCLEAR: ... -->` flags; no `{.underline}` markup here.
  2. `## נְקֻדּוֹת מַפְתֵּחַ` — 5–8 bold topic labels each followed by a `>` blockquote of the key source passage, both in `{dir="rtl"}`.
  3. `## בֵּיאוּר וּפֵירוּשׁ` — sequence of single-column `+---+` grid-table boxes, one per voicenote topic, each headed `**[■ ביאור — <topic>]{dir="rtl"}**` with the cleaned voicenote commentary.
- **YAML frontmatter** on every `section.md` and `discourse.md`.
- Hebrew stays Hebrew — never translate unless explicitly asked.

## Hard DOs and DON'Ts

- ❌ **Do NOT invoke docx/pptx/xlsx skills.** All rendering goes through `scripts/build-docx.sh` (pandoc). Wasting tokens on those skills is explicitly what we're avoiding.
- ❌ **Do NOT transcribe audio via chat.** Always run `python scripts/transcribe.py <session>` first; you then clean up the `.raw.txt` output.
- ❌ **Do NOT hand-edit `compiled/` or `output/`.**
- ❌ **Do NOT auto-overwrite `discourse.md`** if it has content beyond the frontmatter skeleton (the assemble script enforces this; respect it).
- ✅ **DO** preserve `[...]{.underline}` markers and `...` snapshot markers verbatim.
- ✅ **DO** flag unclear text in `ocr.md` as `<!-- UNCLEAR: ... -->` rather than guessing.

## When the user says...
- "new discourse" → use `prompts/01-new-discourse.md`.
- "ingest session" / "process this session" → use `prompts/02-ingest-session.md`.
- "assemble discourse" → use `prompts/03-assemble-discourse.md`.
- "add to chapter" / "assign to chapter" → use `prompts/04-assign-to-chapter.md`.
- "build book" / "render" → use `prompts/05-build-book.md`.
