# sefer-forge

Hebrew book publishing pipeline. Images of book pages + Hebrew voicenotes → Markdown → print-ready DOCX (later: EPUB, PDF).

## Start here

👉 [SETUP_GUIDE.md](SETUP_GUIDE.md) — prerequisites + the 5 daily workflow prompts.

## Unit hierarchy

- **session** = one ingestion batch (N images + 1 voicenote)
- **discourse** = 1..N sessions woven into a cohesive essay (built up over time)
- **chapter** = 1..N discourses assigned via `book/structure.yaml`
- **book** = compiled + rendered output

## Daily workflow — adding a new session

### Step A — Create the session folder
```bash
./scripts/new-session.sh <slug>
# e.g. ./scripts/new-session.sh lag-baomer
# Creates discourses/NNN-<slug>/sessions/MMM/ with empty images/ and voicenotes/ subfolders.
```

### Step B — Drop your files in
- Photos → `discourses/NNN-<slug>/sessions/MMM/images/`
- Voicenote (`.m4a` etc.) → `discourses/NNN-<slug>/sessions/MMM/voicenotes/`

### Step C — Transcribe
```bash
python scripts/transcribe.py discourses/NNN-<slug>/sessions/MMM
# Writes a .raw.txt next to the audio file (Hebrew-tuned ivrit.ai Whisper — see TRANSCRIPTION.md).
# Must exist before Claude ingests.
```

### Step D — Ingest in Claude
Tell Claude: **"ingest session discourses/NNN-\<slug\>/sessions/MMM"**
Claude reads `prompts/02-ingest-session.md` and writes three files:
- `ocr.md` — full OCR of every image
- `commentary.md` — cleaned voicenote transcript
- `section.md` — paired spreads (source chunk + voicenote commentary + explained terms)

Repeat A–D for each session in a discourse.

### After all sessions are done
5. **Assemble discourse** — tell Claude: `"assemble discourse discourses/NNN-<slug>"` → `discourse.md`
6. **Assign to chapter** — tell Claude: `"add to chapter"` → edits `book/structure.yaml`
7. **Build** — `./scripts/build-all.sh` → `output/book.docx`

### Starting a brand-new discourse
```bash
./scripts/new-discourse.sh my-slug   # only needed once per new topic
```
Then follow Steps A–D above.

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
- `faster-whisper` (via requirements.txt; see TRANSCRIPTION.md)
- `git-lfs`
