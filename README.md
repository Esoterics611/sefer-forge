# sefer-forge

Hebrew book publishing pipeline. Photos of a sefer's pages and a Hebrew
voicenote explaining them (or a recorded shiur) become print-ready books and
pamphlets: each page carries a passage of the original text on top and the
speaker's explanation of it below. One repo, many books.

## Start here

- [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md): prerequisites and the daily workflow.
- [docs/agentic-development.md](docs/agentic-development.md): how the AI agent
  does the work, what keeps it trustworthy, and the next steps toward running
  it autonomously.
- [CLAUDE.md](CLAUDE.md): the rules every Claude session follows.

## The process

```
photos of the page ──► OCR, strip by strip ──► ocr.md ─────────────┐
                                                                    ├─► match: what was read where
recording ──► Whisper (local, GPU) ──► .raw.txt / .timed.txt ──────┘
                                              │
                                              ▼
                      cleanup under the review rules ──► commentary.md / transcript.md
                                              │
                                              ▼
           section plan ──► section.md: each passage paired with its explanation
                                              │
             ┌────────────────────────────────┼─────────────────────────────┐
             ▼                                ▼                             ▼
   A5 pamphlet (PDF)              discourse.md ──► chapter ──► book    proof + readability pass
                                                         (DOCX, PDF)        ──► your acceptance
```

1. **Capture.** You photograph the pages and record yourself reading and
   explaining them. Photos and recordings stay on this machine; git ignores them.
   A text taken from a digital edition (chabadlibrary.org) is pasted in instead
   of photographed. Before recording, a reading pack sets every source the text
   cites (עץ חיים, פרי עץ חיים) under its citation, from the copies in `sources/`
   (`prompts/references-pack.md`).
2. **Transcribe.** `scripts/transcribe.py` runs ivrit.ai's Hebrew Whisper
   locally, on the GPU when there is one (about 0.9× the recording's length),
   and saves its progress so a crash loses nothing.
3. **OCR.** The agent reads each photo in strips at full resolution, counts the
   lines, and reads everything a second time.
4. **Match.** `scripts/ocr-match.py` finds which printed words you read aloud
   and when, which fixes both the OCR and the transcript.
5. **Clean up.** The transcript is corrected only where the repo holds evidence
   (the OCR, the glossary, a verse being quoted); anything doubtful is flagged
   with its time for you to re-listen. `scripts/transcript-diff.py` lists every
   changed word.
6. **Pair.** A short plan cuts the text where your explanation of it begins;
   `scripts/build-section.py` builds `section.md` from it.
7. **Print and proof.** A session prints as an A5 pamphlet; discourses gather
   into chapters and books (pandoc to DOCX). Every PDF passes
   `scripts/proof-pdf.py` and a page-by-page review against
   `docs/print-standard.md`, then a readability pass (garbled words) and a
   last style pass that turns the spoken explanation into written Hebrew,
   before it reaches you.

## Agentic development

The work is done by Claude Code acting as an agent: you name a goal ("ingest
session 3", "proof the pamphlet") and it carries out every step, running the
scripts, writing the files, checking its own work and reporting what needs
you. The repo holds what makes this repeatable:

- **Rules** in `CLAUDE.md`: what is never edited, the formats, which skill
  answers which request.
- **Procedures** in `prompts/`, and **skills** in `.claude/skills/` (one per
  workflow: `new-session`, `ocr-session`, `ingest-session`,
  `ingest-voice-session`, `paired-layout`, `publish-pamphlet`, `proof-pdf`,
  `assemble-discourse`, `assign-chapter`, `build-book`, `grow-glossary`,
  `session-status`, `translate-booklets`, `narrate-video`).
- **Checks**: `check-session.py` runs after every edit (a project hook),
  `transcript-diff.py` after every cleanup, `proof-pdf.py` before every
  hand-over.
- **Gates**: the agent stops for your decision on acceptance, on replacing any
  source of truth, and on anything that cannot be undone or leaves the machine.

Long steps run in the background, and every workflow resumes where it stopped:
`python scripts/session-status.py` names each session's next step. The next
steps toward autonomy (an intake folder, a scheduled runner, checks on GitHub,
acceptance in pull requests) are in
[docs/agentic-development.md](docs/agentic-development.md).

## Quick start

**A recorded shiur** (voice-only, e.g. שער היחוד):

```bash
./scripts/new-session.sh shaar-hayichud          # → discourses/002-shaar-hayichud/sessions/NNN/
# drop the recording into its voicenotes/
```

Then tell Claude: **"ingest voice session discourses/002-shaar-hayichud/sessions/NNN"**.
It transcribes, writes `transcript.md`, rebuilds the book, and prints and
proofs the lesson's pamphlet.

**Photos of a sefer and a voicenote:**

Tell Claude: **"new session for 003-breishis"** and name the photos and the
recording. It makes the session, starts Whisper, reads the photos meanwhile,
and continues with **"ingest session …"**: OCR, matching, cleanup, the paired
`section.md`, the pamphlet and its proof.

Then, when a discourse's sessions are done: **"assemble discourse"**,
**"add to chapter"**, **"build book"**. Anytime: **"status"**.

## Narrated videos (YouTube)

Two kinds of episode go up on the channel, private, as plain title-card
videos (בס"ד, dark ink on warm paper) with chapters, subtitles, a
description linking to the Sefer Forge site, and a playlist per series:

- **Shivchei HaBesht stories**, from the English and French booklets (Hebrew
  waits for a Hebrew voice): one English and one French a day, uploaded by a
  daily scheduled run. Skill `narrate-video`, rules
  `prompts/narration-rules.md`.
- **Shiurim in English** (first: שער היחוד, "The Gate of Unity"): each
  shiur is rendered in English beside its Hebrew (`transcript-en.md`), a few
  parts make one ~40-minute episode, and nothing is recorded before you
  approve the English and hear the pronunciation samples. As new sessions
  are ingested, the English follows:

  ```bash
  python scripts/narration-status.py      # per discourse: English missing / current / stale,
                                          # which episode, built, on YouTube; the next step
  ```

  Tell Claude **"English episode"** or **"next shiur in English"**; the
  procedure is `prompts/render-english.md`.

Building: `scripts/build-narration.py` (Kokoro voice; Hebrew terms said as
`booklets/narration/say-en.yaml` spells them). Publishing:
`scripts/youtube-publish.py`, setup and daily routine in
`docs/youtube-publishing.md`.

**Starting something new:**

```bash
./scripts/new-discourse.sh my-slug                # photos + voicenote discourse
./scripts/new-discourse.sh my-slug --voice-only   # recorded-shiur discourse
./scripts/new-book.sh my-book "שם הספר"           # a new book: books/my-book/
bash scripts/build-all.sh                         # build every book
```

## Unit hierarchy

- **session** = one batch: N photos and one voicenote, or one recorded shiur
- **discourse** = 1..N sessions woven into one essay
- **chapter** = 1..N discourses, placed in `books/<book>/structure.yaml`
- **book** = `books/<book>/` → `compiled/<book>.md` → `output/<book>.docx`

Books today (`ls books/`): `shaar-hayichud` (שער היחוד shiurim), `siddur`
(סדר תפילות — שער לג בעומר), `kitzur-lt-to` (קיצור ליקוטי תורה ותורה אור).

## Directory map

| Path | Purpose |
|------|---------|
| `discourses/` | Discourses and their sessions (photos and recordings local only) |
| `books/<book>/` | `structure.yaml`, `metadata.yaml` (title, typography `polish:`), front and back matter |
| `sources/` | The books our texts cite (עץ חיים, פרי עץ חיים; Sefaria exports, never edited), looked up with `scripts/source-lookup.py` |
| `glossary/` | `whisper-fixes.yaml` (recurring mis-hearings, grows every lesson), `abbreviations.yaml` |
| `prompts/` | The procedures: ingest, review rules, readability pass |
| `.claude/skills/` | One skill per workflow |
| `scripts/` | Transcription, OCR, matching, building, proofing, status |
| `templates/` | Word reference template (`create-template.py`), pamphlet, booklet and reading-pack CSS |
| `docs/` | Setup, print standard, agentic development, backlog |
| `compiled/` | Assembled `<book>.md` (generated; never edit) |
| `booklets/narration/` | Narration plans (one per episode), respellings for the voice, the YouTube record `youtube.yaml` |
| `site/` | The Sefer Forge website (https://esoterics611.github.io/), published by `scripts/deploy-site.sh` |
| `output/` | DOCX, PDFs, pamphlets, narrations (gitignored) |

## Dependencies

- `pandoc` ≥ 3.0
- `python` ≥ 3.10 with `requirements.txt` (and `requirements-gpu.txt` with an
  NVIDIA GPU); Whisper setup in `TRANSCRIPTION.md`
- Google Chrome (prints the pamphlets and booklets)
- `requirements-narration.txt` (Kokoro voice for `build-narration.py`; the model downloads on first use)
- `git-lfs` (the repo's Word files)
