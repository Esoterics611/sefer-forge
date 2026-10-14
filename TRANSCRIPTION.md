# Transcription setup

Hebrew speech → text runs **on your own PC**, free, with
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) and
[ivrit.ai](https://huggingface.co/ivrit-ai)'s Hebrew fine-tune of Whisper.

## How it works (and what Hugging Face does)

Hugging Face is just the **download site** for the model — like an app store
for AI model files. Nothing is sent to it and it runs nothing for you:

1. The first time you transcribe, `faster-whisper` downloads the model files
   (`ivrit-ai/whisper-large-v3-turbo-ct2`, ~1.6 GB) from Hugging Face and
   caches them in `%USERPROFILE%\.cache\huggingface\`.
2. From then on everything runs locally, offline — your audio never leaves the PC.
3. No account, no token, no credit card.

ivrit.ai trained Whisper on thousands of hours of Hebrew, so it gets far more
words right than OpenAI's generic model (which is what we used before).

| Option | Model | Size | Notes |
|---|---|---|---|
| default | `ivrit-ai/whisper-large-v3-turbo-ct2` | ~1.6 GB | Fast, runs fine on a normal CPU |
| `--best` | `ivrit-ai/whisper-large-v3-ct2` | ~3 GB | A bit more accurate, ~3–4× slower; worth it with an NVIDIA GPU |

An NVIDIA GPU is used automatically if present; otherwise the CPU (int8).
On a CPU, expect very roughly 1/3–1× the recording's length for the default
model (a 1-hour shiur ≈ 20–60 min, depending on the PC). It prints progress.

## One-time setup (Windows)

Requires Python 3.10+ ([python.org](https://www.python.org/downloads/)).
**No ffmpeg and no torch needed** — faster-whisper decodes `.m4a` itself.
(This also avoids the old `torch` `WinError 1114` problem on this machine.)

```powershell
# From the repo root
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you already have an old `.venv` from the torch/openai-whisper setup, delete
the `.venv` folder and run the three lines above again.

## Running a transcription

```powershell
.venv\Scripts\Activate.ps1          # once per terminal

python scripts/transcribe.py discourses/002-shaar-hayichud/sessions/013
python scripts/transcribe.py discourses/002-shaar-hayichud/sessions/013 --best   # slower, best
```

Writes `<audio>.raw.txt` (Whisper's output, never edited) and then
`<audio>.fixed.txt` (recurring mistakes from `glossary/whisper-fixes.yaml`
fixed). Skips audio that already has a `.raw.txt` — delete it to redo.

Then commit + push, and tell Claude (on the web or locally):
**"ingest voice session discourses/002-shaar-hayichud/sessions/013"**.

## No PC handy? Free cloud alternative

Google Colab gives a free GPU with just a Google account (no credit card):
open a notebook, set *Runtime → Change runtime type → T4 GPU*, then

```python
!git clone https://github.com/Esoterics611/sefer-forge   # private repo: use a token URL
%cd sefer-forge
!pip install -q faster-whisper pyyaml
# upload the .m4a into discourses/<...>/sessions/<MMM>/voicenotes/ (Files pane), then:
!python scripts/transcribe.py discourses/002-shaar-hayichud/sessions/013 --best
```

and download the `.raw.txt` (or push it with a GitHub token).
