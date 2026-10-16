# sefer-forge — conventions for Claude sessions

## What this repo produces
Hebrew **books** (several — one folder each under `books/`) assembled from **discourses**. Each discourse is built up across multiple **sessions**. A discourse later becomes (typically) a **chapter** in a book.

Two kinds of discourse (`type:` in its `meta.yaml`):
- **images+voice** (default) — photos of a sefer + a voicenote → `ocr.md`, `commentary.md`, `section.md`.
- **voice-only** — a recorded shiur, no photos → `transcript.md` per session (e.g. `002-shaar-hayichud`).

## Unit hierarchy
- **session** = one ingestion batch (~N images + 1 Hebrew voicenote, or 1 recorded shiur).
  Location: `discourses/<NNN>-<slug>/sessions/<MMM>/`
  Outputs: `ocr.md`, `commentary.md`, `section.md` — or, voice-only, `transcript.md`.
- **discourse** = 1..N sessions woven into a cohesive essay.
  Location: `discourses/<NNN>-<slug>/discourse.md`
- **chapter** = 1..N discourses assigned in `books/<book>/structure.yaml`.
- **book** = `books/<book>/` (structure, metadata, front/back matter) → compiled at `compiled/<book>.md` → rendered at `output/<book>.docx` by `bash scripts/build-all.sh <book>`.

## Source-of-truth rules
- **Never edit**: raw audio (`.m4a` etc.), image files, `*.raw.txt` (raw Whisper), `ocr.md`.
- **Generated but editable**: `commentary.md`, `section.md`.
- **Hand-edit freely**: `discourse.md` — this is where you polish for flow across sessions.
  **Exception — voice-only discourses:** `discourse.md` is regenerated on every build from `sessions/*/transcript.md` (+ `intro:` / `skip_sessions:` in `meta.yaml`). Edit the transcripts, never that `discourse.md`.
- **Whisper corrections**: `glossary/whisper-fixes.yaml` (shared) — `transcribe.py` / `apply-fixes.py` turn `*.raw.txt` into `*.fixed.txt`. Add recurring mis-hearings there.
- **Transcript cleanup** (`.fixed.txt` → `commentary.md` / `transcript.md`) follows `prompts/transcript-review-rules.md`; `python scripts/transcript-diff.py <session>` writes `<session>/review.md` listing every word changed relative to Whisper.
- **Never hand-edit**: anything in `compiled/` or `output/`.

## Markdown conventions
- **Snapshot marker**: leading/trailing `...` on text that was cut off in the photo.
- **RTL wrapping**: every Hebrew paragraph is wrapped in `[text]{dir="rtl"}`.
- **`section.md` layout = three named sections:**
  1. `## הַנֹּסַח הָעִקָּרִי` — full OCR text as flowing `[...]{dir="rtl"}` paragraphs; bold key transitional words; preserve `...` snapshot markers and `<!-- UNCLEAR: ... -->` flags; no `{.underline}` markup here.
  2. `## נְקֻדּוֹת מַפְתֵּחַ` — 5–8 bold topic labels each followed by a `>` blockquote of the key source passage, both in `{dir="rtl"}`.
  3. `## בֵּיאוּר וּפֵירוּשׁ` — sequence of `::: {custom-style="Commentary"}` fenced divs, one per voicenote topic, each opening with `**[■ ביאור — <topic>]{dir="rtl"}**` followed by the cleaned voicenote commentary. `scripts/polish-docx.py` renders each as a framed box in smaller type. (Sessions ingested before 2026-10-15 use single-column `+---+` grid tables; leave them as they are.)
- **YAML frontmatter** on every `section.md`, `transcript.md` and `discourse.md` — must be valid YAML (escape `"` inside double-quoted values: `חב\"ד`).
- **`transcript.md`** (voice-only): frontmatter `title` becomes a `#` chapter heading (new page), `subtitle` an italic line; body uses `##` sub-headings, `>` for quoted source text, `[^N]` footnotes (numbering restarts per session; the build keeps them unique).
- Hebrew stays Hebrew — never translate unless explicitly asked.

## Hard DOs and DON'Ts

- ❌ **Do NOT invoke docx/pptx/xlsx skills, and do not write per-discourse python-docx build scripts.** All rendering goes through `scripts/build-all.sh <book>` (pandoc + `templates/book-template.docx` + `scripts/polish-docx.py`). Typography changes go in `scripts/create-template.py` or a book's `polish:` block in `metadata.yaml`. The one exception is the Shivchei HaBesht booklets (below), which print to PDF through Chrome.
- ❌ **Do NOT transcribe audio via chat.** Always run `python scripts/transcribe.py <session>` first; you then clean up the `.raw.txt` output.
- ❌ **Do NOT hand-edit `compiled/` or `output/`.**
- ❌ **Do NOT edit `*.raw.txt`.** `*.fixed.txt` is regenerated — don't edit it either.
- ❌ **Do NOT auto-overwrite `discourse.md`** if it has content beyond the frontmatter skeleton (the assemble script enforces this; respect it).
- ✅ **DO** preserve `[...]{.underline}` markers and `...` snapshot markers verbatim.
- ✅ **DO** flag unclear text in `ocr.md` as `<!-- UNCLEAR: ... -->` rather than guessing.

## When the user says...
- "new discourse" → use `prompts/01-new-discourse.md`.
- "ingest session" / "process this session" → use `prompts/02-ingest-session.md` (images+voice) or, for a voice-only discourse, `prompts/02v-ingest-voice-session.md` (skill: `ingest-voice-session`).
- "new lesson" / "ingest voice session" / "next shiur" → `prompts/02v-ingest-voice-session.md`.
- "assemble discourse" → use `prompts/03-assemble-discourse.md`.
- "add to chapter" / "assign to chapter" → use `prompts/04-assign-to-chapter.md`.
- "build book" / "render" → use `prompts/05-build-book.md` (`bash scripts/build-all.sh [book]`; no book = all books).
- "build booklets" → `python scripts/build-booklets.py [N ...]`: themed A5 PDFs of `shivchei-habesht-simple.md` in `output/booklets/`. Grouping in `booklets/booklets.yaml`, glossary in `booklets/glossary.yaml`, layout in `templates/booklet.css`.
- "new book" → `./scripts/new-book.sh <slug> "<title>"`, then fill `books/<slug>/structure.yaml`.
