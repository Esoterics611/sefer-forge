# sefer-forge

Hebrew book publishing pipeline. Images of book pages + Hebrew voicenotes (or recorded shiurim) → Markdown → print-ready DOCX (later: EPUB, PDF). One repo, many books.

## Start here

👉 [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) — prerequisites + the daily workflow prompts.

## Unit hierarchy

- **session** = one ingestion batch (N images + 1 voicenote, or one recorded shiur)
- **discourse** = 1..N sessions woven into a cohesive essay (built up over time)
- **chapter** = 1..N discourses assigned via `books/<book>/structure.yaml`
- **book** = `books/<book>/` → `compiled/<book>.md` → `output/<book>.docx`

Books today: `ls books/` — `shaar-hayichud` (שער היחוד shiurim), `siddur` (סדר תפילות — שער לג בעומר).

## Workflow A — a recorded shiur (voice-only, e.g. שער היחוד)

```bash
./scripts/new-session.sh shaar-hayichud
#   → discourses/002-shaar-hayichud/sessions/013/voicenotes/   (drop the .m4a here)
python scripts/transcribe.py discourses/002-shaar-hayichud/sessions/013
#   → .raw.txt (Whisper) + .fixed.txt (glossary/whisper-fixes.yaml applied)
```

Then tell Claude: **"ingest voice session discourses/002-shaar-hayichud/sessions/013"**
→ writes `transcript.md`, grows the fixes glossary, and rebuilds `output/shaar-hayichud.docx`.

That's it — the new lesson appears as the next chapter automatically. To fix a typo later, edit that session's `transcript.md` and run `bash scripts/build-all.sh shaar-hayichud`.

## Workflow B — photos of a sefer + a voicenote

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
# Writes .raw.txt + .fixed.txt next to the audio file. Must exist before Claude ingests.
```

### Step D — Ingest in Claude
Tell Claude: **"ingest session discourses/NNN-\<slug\>/sessions/MMM"**
Claude reads `prompts/02-ingest-session.md` and writes three files:
- `ocr.md` — full OCR of every image
- `commentary.md` — cleaned voicenote transcript
- `section.md` — paired spreads (source chunk + voicenote commentary + explained terms)

Repeat A–D for each session in a discourse, then:
5. **Assemble discourse** — tell Claude: `"assemble discourse discourses/NNN-<slug>"` → `discourse.md`
6. **Assign to chapter** — tell Claude: `"add to chapter"` → edits `books/<book>/structure.yaml`
7. **Build** — `bash scripts/build-all.sh <book>` → `output/<book>.docx`

## Starting something new

```bash
./scripts/new-discourse.sh my-slug                # photos + voicenote discourse
./scripts/new-discourse.sh my-slug --voice-only   # recorded-shiur discourse
./scripts/new-book.sh my-book "שם הספר"           # a new book: books/my-book/
bash scripts/build-all.sh                         # build every book
```

## Directory map

| Path | Purpose |
|------|---------|
| `discourses/` | WIP discourses, each with its own sessions |
| `books/<book>/` | `structure.yaml`, `metadata.yaml` (title, typography `polish:`), front/back matter |
| `glossary/whisper-fixes.yaml` | Recurring Whisper mis-hearings → corrections (grows every lesson) |
| `compiled/` | Auto-assembled `<book>.md` (do not edit) |
| `output/` | Rendered `<book>.docx` (gitignored) |
| `templates/` | Word reference template (`create-template.py` regenerates it) + shared pandoc defaults |
| `scripts/` | Pipeline scripts |
| `prompts/` | Paste-into-Claude session prompts |

## Dependencies

- `pandoc` ≥ 3.0
- `python` ≥ 3.10 (+ `requirements.txt`; Whisper setup in `TRANSCRIPTION.md`)
- `git-lfs`
