# Transcription setup

Whisper (Hebrew, medium model) is managed inside this repo via a Python virtual environment.

## One-time setup

Requires Python 3.12 and ffmpeg.

**Python** — install from [python.org](https://www.python.org/downloads/) if not present.  
The expected path on this machine is:
```
C:\Users\Nexus\AppData\Local\Programs\Python\Python312\python.exe
```

**ffmpeg** — install once via winget (already done on this machine):
```powershell
winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
```
Then open a fresh terminal so ffmpeg lands on PATH.

**Virtual environment + deps:**
```powershell
# From the repo root
C:\Users\Nexus\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` pins `torch==2.2.2+cpu` (CPU-only build, no CUDA needed) and `numpy<2`.
The Whisper medium model (~1.4 GB) downloads automatically on first transcription and is cached
in `%USERPROFILE%\.cache\whisper\`.

## Running a transcription

```powershell
# Activate the venv first (once per terminal session)
.venv\Scripts\Activate.ps1

# Then transcribe a session
python scripts/transcribe.py discourses/<NNN>-<slug>/sessions/<MMM>
```

Output is written as `<audio-file>.raw.txt` in the same `voicenotes/` folder.
The script skips files that already have a transcript — delete the `.raw.txt` to retranscribe.

## Why these version pins

| Package | Version | Reason |
|---------|---------|--------|
| `torch` | `2.2.2+cpu` | Newer builds (2.11+) fail with `WinError 1114` on this machine — likely a CUDA DLL loaded even in non-CUDA builds. CPU build from the PyTorch CPU index avoids it. |
| `numpy` | `<2` | torch 2.2.x was compiled against NumPy 1.x; NumPy 2.x causes import warnings and potential instability. |

## After cloning on a new machine

Same steps as one-time setup above. The venv is gitignored — each machine runs its own.
