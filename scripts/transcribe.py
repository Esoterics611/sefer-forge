#!/usr/bin/env python3
"""Transcribe voicenote(s) in a session folder (Hebrew speech → text).

Usage:
    python scripts/transcribe.py <session-path> [--best] [--model NAME]

    python scripts/transcribe.py discourses/002-shaar-hayichud/sessions/013
    python scripts/transcribe.py discourses/002-shaar-hayichud/sessions/013 --best

Engine: faster-whisper running ivrit.ai's Hebrew fine-tune of Whisper,
downloaded once from Hugging Face (cached in ~/.cache/huggingface) and then
run entirely on this machine — no account, no API key, nothing uploaded.

    default  ivrit-ai/whisper-large-v3-turbo-ct2   (~1.6 GB, fast; fine on a CPU)
    --best   ivrit-ai/whisper-large-v3-ct2         (~3 GB, a bit more accurate,
                                                    ~3-4x slower; best with a GPU)

Uses an NVIDIA GPU automatically if one is available, otherwise the CPU.
If faster-whisper isn't installed, falls back to OpenAI's original
whisper package (generic "medium" model; noticeably worse on Hebrew).

Produces `<audio>.raw.txt` next to each audio file. Skips files that
already have a transcript. Never overwrites — delete the .raw.txt if
you want to retranscribe.

Then runs scripts/apply-fixes.py on the session, producing
`<audio>.fixed.txt` with the recurring corrections from
glossary/whisper-fixes.yaml already applied.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg", ".flac", ".aac", ".opus"}
FAST_MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"
BEST_MODEL = "ivrit-ai/whisper-large-v3-ct2"


def has_cuda() -> bool:
    try:
        import ctranslate2

        return ctranslate2.get_cuda_device_count() > 0
    except Exception:
        return False


def faster_whisper_engine(model_name: str):
    from faster_whisper import WhisperModel

    if has_cuda():
        device, compute = "cuda", "float16"
    else:
        device, compute = "cpu", "int8"
    print(f"Loading {model_name} on {device} ({compute}) — first run downloads it...")
    model = WhisperModel(model_name, device=device, compute_type=compute)

    def transcribe(audio: Path) -> str:
        segments, info = model.transcribe(
            str(audio), language="he", beam_size=5, vad_filter=True
        )
        parts = []
        for seg in segments:  # generator: transcription happens while iterating
            parts.append(seg.text.strip())
            done = seg.end / info.duration * 100 if info.duration else 0
            print(f"\r  {done:5.1f}%  ({seg.end / 60:5.1f} / {info.duration / 60:.1f} min)",
                  end="", flush=True)
        print()
        return " ".join(p for p in parts if p)

    return transcribe


def openai_whisper_engine():
    import whisper  # type: ignore

    print("faster-whisper not installed — falling back to openai-whisper 'medium'.")
    print("For much better Hebrew: pip install faster-whisper")
    model = whisper.load_model("medium")
    return lambda audio: model.transcribe(str(audio), language="he")["text"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Transcribe a session's voicenotes.")
    ap.add_argument("session")
    ap.add_argument("--best", action="store_true", help=f"use {BEST_MODEL}")
    ap.add_argument("--model", help="any faster-whisper model name or local path")
    args = ap.parse_args()

    session = Path(args.session)
    vn_dir = session / "voicenotes"
    if not vn_dir.is_dir():
        print(f"No voicenotes/ dir in {session}")
        return 1

    audios = [p for p in sorted(vn_dir.iterdir()) if p.suffix.lower() in AUDIO_EXTS]
    todo = [a for a in audios if not a.with_suffix(a.suffix + ".raw.txt").exists()]
    for a in sorted(set(audios) - set(todo)):
        print(f"Skip (transcript exists): {a.name}")
    if not audios:
        print(f"No audio files found in {vn_dir}")
        return 0

    if todo:
        try:
            import faster_whisper  # noqa: F401
            transcribe = faster_whisper_engine(args.model or (BEST_MODEL if args.best else FAST_MODEL))
        except ImportError:
            try:
                transcribe = openai_whisper_engine()
            except ImportError:
                print("No Whisper engine installed. Run: pip install faster-whisper")
                return 1

        for audio in todo:
            out = audio.with_suffix(audio.suffix + ".raw.txt")
            print(f"Transcribing {audio.name}...")
            t0 = time.time()
            text = transcribe(audio)
            out.write_text(text, encoding="utf-8")
            print(f"  -> {out.name}  ({len(text)} chars, {(time.time() - t0) / 60:.1f} min)")

    print()
    fixer = Path(__file__).with_name("apply-fixes.py")
    return subprocess.call([sys.executable, str(fixer), str(session)])


if __name__ == "__main__":
    sys.exit(main())
