# Transcription setup

`scripts/transcribe.py` runs Whisper through faster-whisper on the CPU, in int8,
with ivrit.ai's Hebrew fine-tune of Whisper large-v3
(`ivrit-ai/whisper-large-v3-ct2`, set as `MODEL` in the script). Quality is the
priority over speed.

## One-time setup

Python 3.10+ in a virtual environment at the repo root (gitignored; each machine
runs its own):

```bash
# Linux / WSL
sudo apt install -y python3-venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

```powershell
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No ffmpeg and no torch: faster-whisper decodes audio itself (PyAV) and runs on
CTranslate2. The model (about 3 GB) downloads on the first transcription and is
cached in `~/.cache/huggingface/`.

## Running a transcription

```bash
source .venv/bin/activate        # once per terminal
python scripts/transcribe.py discourses/<NNN>-<slug>/sessions/<MMM>
python scripts/transcribe.py --pending     # every session with audio and no transcript
```

Writes next to each audio file in `voicenotes/`:

| File | Content |
|------|---------|
| `<audio>.raw.txt` | Whisper's text; never edited |
| `<audio>.timed.txt` | the same text, one segment per line with its `[mm:ss]` start time |
| `<audio>.fixed.txt` | `.raw.txt` with `glossary/whisper-fixes.yaml` applied (regenerated, gitignored) |

The script skips audio that already has a `.raw.txt`; delete the `.raw.txt` and
`.timed.txt` to retranscribe.

While it runs, every segment is saved to `<audio>.partial.txt` as it is heard,
and `<audio>.lock` names the process and the recording's length. If the run dies
(a crash, a reboot, Ctrl-C), run the same command again: it resumes after the
last saved segment, with the text before it given to Whisper as context. The
`.raw.txt` is written last, so its presence means the run finished.
`python scripts/session-status.py <session>` shows a run's progress and time
left, or where an interrupted run stopped.

The cleanup that follows (Claude, under `prompts/transcript-review-rules.md`)
reads `.fixed.txt` and `.timed.txt`; `python scripts/transcript-diff.py <session>`
then lists every word it changed in `<session>/review.md`.

## Speed and memory

Measured on the WSL host (i7-10750H, 7.6 GB, 2026-10-15) with an 11.4-minute
voicenote: 27.6 minutes, about 2.4 × the recording's length, so a one-hour
shiur takes about 2.5 hours. The process peaks at about 6.6 GB resident and
spills about 1 GB into swap, so run one transcription at a time:
`transcribe.py` skips a recording another live process is already transcribing.

## Model choice

Compared on the same voicenote (lag-baomer session 001) against
`Systran/faster-whisper-large-v3` (same speed) and the old openai-whisper
`medium` output. ivrit.ai's model got more Hebrew and Chassidus terms right
(`גלות השכינה`, `על כל פנים`, `בעל הסידור`, `תשובה ניצחת לאומות העולם`)
in the passages compared, where the standard large-v3 also inserted a phrase
that was not spoken (`הוא מאוד קצר`).
All three garble Chabad names (`אדמו"ר הזקן`, `הצמח צדק`); the glossary
and the review step handle those.

faster-whisper's `hotwords` / `initial_prompt` with a list of those names was
tried on a 50-second clip and is not used: it fixed `הצמח צדק` and `אור התורה`
but turned `אדמו"ר הזקן` into the plausible-looking `אור התורה זקן` and broke
`המשל והנמשל`. A plausible wrong phrase is harder to catch in review than a
garbled one.

## Pins

| Package | Pin | Reason |
|---------|-----|--------|
| `av` | `<15` | faster-whisper 1.2.1 calls `av.open(metadata_errors=...)`, which PyAV 19 rejects. 14.2 verified. |
