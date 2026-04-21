# sefer-forge

Hebrew book publishing pipeline. Images of book pages + Hebrew voicenotes → Markdown → print-ready DOCX (later: EPUB, PDF).

## Start here

👉 [SETUP_GUIDE.md](SETUP_GUIDE.md) — prerequisites + the 5 daily workflow prompts.

## Unit hierarchy

- **session** = one ingestion batch (N images + 1 voicenote)
- **discourse** = 1..N sessions woven into a cohesive essay (built up over time)
- **chapter** = 1..N discourses assigned via `book/structure.yaml`
- **book** = compiled + rendered output

## Daily workflow in 60 seconds

1. **Capture** on phone — photos of pages (with your underlines) + Hebrew voicenote explaining them.
2. **Scaffold** — `./scripts/new-discourse.sh my-slug` once per discourse; `./scripts/new-session.sh my-slug` for each session.
3. **Drop** images into `discourses/NNN-my-slug/sessions/MMM/images/` and audio into `.../voicenotes/`.
4. **Transcribe** — `python scripts/transcribe.py discourses/NNN-my-slug/sessions/MMM`.
5. **Ingest in Claude** — paste `prompts/02-ingest-session.md`. Claude writes `ocr.md`, `commentary.md`, `section.md`.
6. **Repeat** 1–5 until the discourse is done.
7. **Assemble discourse** — `prompts/03-assemble-discourse.md`.
8. **Assign to chapter** — `prompts/04-assign-to-chapter.md`.
9. **Build** — `./scripts/build-all.sh` → `output/book.docx`.

## Directory map

| Path | Purpose |
|------|---------|
| `discourses/` | WIP discourses, each with its own sessions |
| `book/` | `structure.yaml` + front/back matter |
| `compiled/` | Auto-assembled `book.md` (do not edit) |
| `output/` | Rendered `.docx` / `.epub` / `.pdf` (gitignored) |
| `templates/` | Word reference template + pandoc metadata |
| `scripts/` | Pipeline scripts |
| `prompts/` | Paste-into-Claude session prompts |

## Dependencies

- `pandoc` ≥ 3.0
- `python` ≥ 3.10 (+ `requirements.txt`)
- `ffmpeg` (for Whisper)
- `git-lfs`
