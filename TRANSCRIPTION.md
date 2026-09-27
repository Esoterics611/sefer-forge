# Transcription setup

Voicenotes are transcribed by `scripts/transcribe.py` using **faster-whisper** with
**`ivrit-ai/whisper-large-v3-turbo-ct2`** — Whisper large-v3-turbo fine-tuned on Hebrew
by [ivrit.ai](https://huggingface.co/ivrit-ai). This replaced stock Whisper `medium`,
which garbled a lot of Hebrew (e.g. "שוקים את הקדוש בר חושב" for "שהקדוש ברוך הוא").

What the script does beyond plain Whisper:
- **Domain vocabulary** — `scripts/transcribe-vocab.txt` is passed as the initial prompt so
  terms like תניא / אדמו"ר הזקן / השתלשלות are spelled right. **Add terms there** whenever
  you see the same word misspelled across sessions.
- **Voice-activity detection** — skips silences, which stops Whisper from hallucinating
  repeated phrases.
- **Paragraph breaks** at pauses > 1.5 s, instead of one giant line.

## Running a transcription

```bash
python scripts/transcribe.py discourses/<NNN>-<slug>/sessions/<MMM>
# or a single file / several targets:
python scripts/transcribe.py "path/to/Voice 123.m4a" another/session
```

Output is `<audio-file>.raw.txt` in the same `voicenotes/` folder. The script skips files
that already have a transcript — delete the `.raw.txt` to retranscribe (e.g. to redo an
old session with the better model).

Options: `--model ivrit-ai/whisper-large-v3-ct2` (slower, occasionally better),
`--beam 8` (slower, slightly better), `--no-vocab`.

## Setup — Windows PC (one time)

```powershell
# From the repo root
C:\Users\Nexus\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No torch and no ffmpeg needed any more — faster-whisper decodes `.m4a` itself.
The model (~1.6 GB) downloads from Hugging Face on first run and is cached in
`%USERPROFILE%\.cache\huggingface\`. Speed on CPU: roughly real-time or faster
(an 11-minute voicenote ≈ 5–15 min depending on the machine).

## Setup — Claude Code cloud sessions

`.claude/hooks/session-start.sh` runs automatically in cloud sessions and installs
faster-whisper + git-lfs. Two things must be true:

1. **The voicenote is pushed** to GitHub (it's stored in Git LFS). In the session, fetch
   just that audio: `git lfs pull --include="discourses/<NNN>-<slug>/sessions/<MMM>/voicenotes/*"`.
2. **The environment's network access allows Hugging Face** so the model can download.
   In the cloud environment settings (environment menu in the session title bar → Edit),
   add these to the allowed domains, or pick a broader access level:
   `huggingface.co`, `cdn-lfs.huggingface.co`, `cas-bridge.xethub.hf.co`, `*.hf.co`.

Cloud containers are CPU-only (4 cores), so expect roughly real-time speed there too.
