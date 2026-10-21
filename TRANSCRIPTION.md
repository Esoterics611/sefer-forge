# Transcription setup

`scripts/transcribe.py` runs Whisper through faster-whisper with ivrit.ai's
Hebrew fine-tune of Whisper large-v3 (`ivrit-ai/whisper-large-v3-ct2`, set as
`MODEL` in the script): on an NVIDIA GPU in int8_float16 when there is one,
otherwise on the CPU in int8. Both use the same int8 weights and give the same
text (see "Settings measured"). Quality is the priority over speed.

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

### GPU

With an NVIDIA GPU (Linux / WSL; the driver alone, no CUDA toolkit), also run
`pip install -r requirements-gpu.txt` (with `uv`: `uv pip install --python
.venv/bin/python -r requirements-gpu.txt`). It installs the cuBLAS and cuDNN 9
libraries CTranslate2 loads, about 2.2 GB, under `.venv/.../site-packages/nvidia/`;
`transcribe.py` puts them on `LD_LIBRARY_PATH` itself (it restarts once to do so).
The script says where it runs (`running on cuda int8_float16`). If the GPU fails
(a library missing, the card's memory taken) it says why and uses the CPU;
`WHISPER_DEVICE=cpu` forces the CPU.

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

Measured on the WSL host (i7-10750H, 7.6 GB, Quadro T1000 with 4 GB):

| Where | Time per minute of audio | Memory | Measured |
|---|---|---|---|
| GPU, int8_float16 | about 0.9 min (a one-hour shiur: under an hour) | 2 GB on the card; RAM peaks at 3.2 GB while loading | 2026-10-21, 3.9-minute voicenote |
| CPU, int8 (4 threads) | about 2.4 min (a one-hour shiur: about 2.5 hours) | 6.6 GB resident and about 1 GB of swap | 2026-10-15, 11.4-minute voicenote |

`session-status.py` uses these figures for its time-left estimate. Run one
transcription at a time: `transcribe.py` skips a recording another live process
is already transcribing. On the CPU the machine is close to its memory limit
(a CPU run started beside other work was killed for memory on 2026-10-21).

## Settings measured (2026-10-21)

On Breishis session 001 (3.9 minutes), scored against its cleaned
`commentary.md` and read difference by difference:

| Setting | Result |
|---|---|
| CPU int8 (the old default) | the reference the cleanup was made from |
| GPU float16 (full precision) | no better: 8 places differ, none a clear gain (it lost `נוקבין` and `ריי"ץ`); 3.8 min per minute (it takes 3.8 of the card's 4 GB) |
| GPU int8_float16 | the same quality as CPU int8 (the same int8 weights; the differences are word-level noise); 0.9 min per minute |
| `vad_filter=True` | worse: new garbage (`ההתעררררררה זם שלך`) where it cut the audio |
| `hotwords` = the glossary's 51 correct forms | unusable: the transcript lost half its words (192 of 379) |

So quantizing the weights costs nothing measurable with this model, and the
model choice (below) and the cleanup are what decide quality.

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
garbled one. Retried with the glossary's terms on 2026-10-21, it dropped half
the text (above).

## Pins

| Package | Pin | Reason |
|---------|-----|--------|
| `av` | `<15` | faster-whisper 1.2.1 calls `av.open(metadata_errors=...)`, which PyAV 19 rejects. 14.2 verified. |
| `nvidia-cudnn-cu12` | `==9.*` | CTranslate2 4.x loads cuDNN 9 (`requirements-gpu.txt`); 9.27 with cuBLAS 12.9 verified. |
