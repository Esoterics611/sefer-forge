# SETUP GUIDE — sefer-forge

## 1. One-time: prerequisites

Install on your machine:

```bash
winget install --id JohnMacFarlane.Pandoc       # pandoc 3+
winget install Gyan.FFmpeg                      # ffmpeg (Whisper needs it)
pip install -r requirements.txt                 # python deps (openai-whisper, pyyaml)
git lfs install                                 # once per machine (LFS already init'd here)
```

The Word reference template is generated automatically on the first build (`scripts/create-template.py`; edit that script to change typography).

## 2. The 5 process prompts

The **megaprompt** (`prompts/00-megaprompt-setup.md`) was already run to scaffold this repo. You won't run it again unless you want a parallel project.

Your daily workflow uses these five paste-into-Claude prompts:

| # | Prompt | When to use |
|---|--------|-------------|
| 1 | `prompts/01-new-discourse.md` | Starting a new lecture/essay |
| 2 | `prompts/02-ingest-session.md` | You have images + voicenote for one batch |
| 2v | `prompts/02v-ingest-voice-session.md` | A recorded shiur for a voice-only discourse (say "ingest voice session <path>") |
| 3 | `prompts/03-assemble-discourse.md` | All sessions for a discourse are done |
| 4 | `prompts/04-assign-to-chapter.md` | A discourse is ready to place in the book |
| 5 | `prompts/05-build-book.md` | Render the current state to `.docx` |

Each prompt file tells you exactly what to replace (`<SLUG>`, `<SESSION_PATH>`, etc.) before pasting.

## 3. Script cheat sheet

| Task | Run |
|------|-----|
| Create new discourse | `./scripts/new-discourse.sh my-slug` |
| Add a session to a discourse | `./scripts/new-session.sh my-slug` |
| Transcribe voicenote(s) in a session | `python scripts/transcribe.py discourses/001-my-slug/sessions/001` |
| Assemble discourse from sessions | `python scripts/assemble-discourse.py discourses/001-my-slug` |
| Compile + render | `./scripts/build-all.sh` |

## 4. First end-to-end smoke test

Do this once to verify everything works before committing to real content:

1. `./scripts/new-discourse.sh smoke-test`
2. `./scripts/new-session.sh smoke-test`
3. Drop one photo into `discourses/001-smoke-test/sessions/001/images/`.
4. Record a 30-second Hebrew voicenote about it; drop into `.../voicenotes/`.
5. `python scripts/transcribe.py discourses/001-smoke-test/sessions/001`
6. Open Claude Code in this repo. Paste `prompts/02-ingest-session.md`, replacing `<SESSION_PATH>` with `discourses/001-smoke-test/sessions/001`.
7. Verify `section.md` looks right.
8. `python scripts/assemble-discourse.py discourses/001-smoke-test`
9. Verify `discourse.md` looks right.
10. Edit `books/<book>/structure.yaml` → add `smoke-test` to Chapter 1's `discourses:` list.
11. `bash scripts/build-all.sh <book>` → open `output/<book>.docx`.

If all 11 steps pass, the pipeline is good. Delete the smoke-test discourse when done.

## 5. Flow diagram

```
   [phone: photos + Hebrew voicenote]
                  │
                  ▼
   [drop into sessions/MMM/{images,voicenotes}/]
                  │
                  ▼
   python scripts/transcribe.py  ──►  *.raw.txt
                  │
                  ▼
   Claude session + prompts/02-ingest-session.md
                  │
                  ▼
    ocr.md + commentary.md + section.md
                  │
                  ▼  (repeat for each session)
                  │
                  ▼
   python scripts/assemble-discourse.py  ──►  discourse.md
                  │
                  ▼
   edit books/<book>/structure.yaml (assign to chapter)
                  │
                  ▼
   bash scripts/build-all.sh <book>  ──►  output/<book>.docx
```
