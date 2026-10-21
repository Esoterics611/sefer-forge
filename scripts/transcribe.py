#!/usr/bin/env python3
"""Transcribe voicenote(s) in a session folder using Whisper (Hebrew).

Usage:
    python scripts/transcribe.py discourses/001-my-slug/sessions/001 [more sessions]
    python scripts/transcribe.py --pending     # every session with audio and no transcript

Model: MODEL below, run by faster-whisper on an NVIDIA GPU (int8_float16)
when there is one and requirements-gpu.txt is installed, otherwise on the CPU
(int8, about 2.7 times slower; same text). WHISPER_DEVICE=cpu forces the CPU.
The first run downloads the model (about 3 GB, cached in
~/.cache/huggingface). Transcription quality is the point. See TRANSCRIPTION.md.

Produces next to each audio file:
  <audio>.raw.txt    Whisper's text (never edited)
  <audio>.timed.txt  the same text, one segment per line with its start time
                     ([mm:ss]); UNCLEAR flags in the cleanup cite these times
Skips files that already have a .raw.txt. Never overwrites — delete the
.raw.txt and .timed.txt to retranscribe.

While it runs, each segment is saved to <audio>.partial.txt as it is heard,
and <audio>.lock names the process and the recording's length (that is how
scripts/session-status.py shows progress). If the run dies — a crash, a
reboot, Ctrl-C — run the same command again: it resumes after the last saved
segment. .raw.txt is written last, so its presence means the run finished.

Then runs scripts/apply-fixes.py on the session, producing
`<audio>.fixed.txt` with the recurring corrections from
glossary/whisper-fixes.yaml already applied.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import sysconfig
from datetime import datetime
from pathlib import Path


def cuda_libs_on_path() -> None:
    """The GPU needs cuBLAS and cuDNN (requirements-gpu.txt). Their wheels put
    the libraries under site-packages/nvidia/*/lib, where the loader does not
    look, so restart once with those folders on LD_LIBRARY_PATH."""
    if sys.platform != "linux":
        return
    libs = sorted(str(d) for d in Path(sysconfig.get_paths()["purelib"]).glob("nvidia/*/lib"))
    have = [d for d in os.environ.get("LD_LIBRARY_PATH", "").split(os.pathsep) if d]
    if any(d not in have for d in libs):
        os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(libs + [d for d in have if d not in libs])
        os.execv(sys.executable, [sys.executable, *sys.argv])


cuda_libs_on_path()

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Missing dependency. Install with: pip install -r requirements.txt")
    sys.exit(1)

import forgelib as F

MODEL = "ivrit-ai/whisper-large-v3-ct2"   # ivrit.ai's Hebrew fine-tune of large-v3
# Whisper sometimes emits invisible bidi marks (mostly U+202B) mid-phrase;
# they stop multi-word glossary fixes from matching.
BIDI_MARKS = re.compile("[‎‏‪-‮⁦-⁩]")
CONTEXT_CHARS = 200        # text from before a resume point, given to Whisper as context


def stamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def load_partial(path: Path) -> list[tuple[float, float, str]]:
    """Segments saved by an earlier, interrupted run: "start<TAB>end<TAB>text" lines."""
    segs = []
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t", 2)
            if len(parts) == 3:
                segs.append((float(parts[0]), float(parts[1]), parts[2]))
    return segs


def load_model() -> tuple[WhisperModel, str]:
    """The model on the GPU in int8_float16 when there is one, else on the CPU
    in int8: the same int8 weights, so the same text (float16 was measured no
    better and slower; TRANSCRIPTION.md). A second of silence is transcribed
    first, because a missing CUDA library or a full GPU only shows when the
    model runs. Returns the model and where it runs."""
    import ctranslate2
    import numpy as np
    if os.environ.get("WHISPER_DEVICE", "").lower() != "cpu" and ctranslate2.get_cuda_device_count():
        try:
            model = WhisperModel(MODEL, device="cuda", compute_type="int8_float16")
            list(model.transcribe(np.zeros(16000, dtype=np.float32), language="he", beam_size=5)[0])
            return model, "cuda int8_float16"
        except (RuntimeError, ValueError) as e:
            model = None
            print(f"  GPU failed ({str(e).splitlines()[0]}); using the CPU (TRANSCRIPTION.md, GPU)")
    model = WhisperModel(MODEL, device="cpu", compute_type="int8",
                         cpu_threads=max(1, (os.cpu_count() or 2) // 2))
    return model, "cpu int8"


def transcribe(model: WhisperModel, device: str, audio: Path) -> None:
    partial, lock = F.sidecar(audio, "partial.txt"), F.sidecar(audio, "lock")
    done = load_partial(partial)
    resume_at = done[-1][1] if done else 0.0
    kwargs: dict = {"language": "he", "beam_size": 5}
    if resume_at:
        kwargs["clip_timestamps"] = [resume_at]
        kwargs["initial_prompt"] = " ".join(t for _, _, t in done)[-CONTEXT_CHARS:]
        print(f"Resuming {audio.name} at {stamp(resume_at)} ({len(done)} segments saved)...")
    else:
        print(f"Transcribing {audio.name}...")

    segments, info = model.transcribe(str(audio), **kwargs)
    lock.write_text(f"pid: {os.getpid()}\nstarted: {datetime.now().isoformat(timespec='seconds')}\n"
                    f"duration: {info.duration:.1f}\nresumed_at: {resume_at:.1f}\ndevice: {device}\n",
                    encoding="utf-8")
    with partial.open("a", encoding="utf-8") as out:
        for seg in segments:
            text = BIDI_MARKS.sub("", seg.text).strip()
            if not text:
                continue
            out.write(f"{seg.start:.2f}\t{seg.end:.2f}\t{text}\n")
            out.flush()
            done.append((seg.start, seg.end, text))
            print(f"  {stamp(seg.end)} / {stamp(info.duration)}", end="\r", flush=True)

    plain = [t for _, _, t in done]
    F.sidecar(audio, "timed.txt").write_text(
        "\n".join(f"[{stamp(s)}] {t}" for s, _, t in done) + "\n", encoding="utf-8")
    raw = F.sidecar(audio, "raw.txt")
    tmp = raw.with_name(raw.name + ".tmp")
    tmp.write_text(" ".join(plain), encoding="utf-8")
    tmp.replace(raw)                   # last: a .raw.txt means the run finished
    partial.unlink(missing_ok=True)
    lock.unlink(missing_ok=True)
    print(f"  -> {raw.name} + .timed.txt  ({len(' '.join(plain))} chars)")


def running_elsewhere(audio: Path) -> int | None:
    """pid of another live process transcribing this audio, if any."""
    lock = F.sidecar(audio, "lock")
    if not lock.exists():
        return None
    m = re.search(r"^pid:\s*(\d+)", lock.read_text(encoding="utf-8"), flags=re.M)
    pid = int(m.group(1)) if m else 0
    return pid if pid and pid != os.getpid() and Path(f"/proc/{pid}").exists() else None


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python scripts/transcribe.py <session-path> [...] | --pending")
        return 1
    if "--pending" in argv:
        sessions = [s for s in F.resolve_sessions([])
                    if any(not F.sidecar(a, "raw.txt").exists() for a in F.audio_files(s))]
        if not sessions:
            print("Nothing pending: every recording has a transcript.")
            return 0
    else:
        sessions = [Path(a.rstrip("/")) for a in argv]

    model, device = None, ""
    status = 0
    for session in sessions:
        if not (session / "voicenotes").is_dir():
            print(f"No voicenotes/ dir in {session}")
            status = 1
            continue
        audios = F.audio_files(session)
        if not audios:
            print(f"No audio files found in {session / 'voicenotes'}")
            continue
        pending = []
        for audio in audios:
            if F.sidecar(audio, "raw.txt").exists():
                print(f"Skip (transcript exists): {audio.name}")
            elif (pid := running_elsewhere(audio)):
                print(f"Skip (already being transcribed by process {pid}): {audio.name}")
            else:
                pending.append(audio)
        if pending and model is None:
            print(f"Loading Whisper model ({MODEL})...")
            model, device = load_model()
            print(f"  running on {device}")
        for audio in pending:
            transcribe(model, device, audio)
        print()
        fixer = Path(__file__).with_name("apply-fixes.py")
        if any(F.sidecar(a, "raw.txt").exists() for a in audios):
            status |= subprocess.call([sys.executable, str(fixer), str(session)])
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
