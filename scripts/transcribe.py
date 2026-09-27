#!/usr/bin/env python3
"""Transcribe Hebrew voicenote(s) with a Hebrew-fine-tuned Whisper model.

Usage:
    python scripts/transcribe.py <session-path | audio-file> [...]
        [--model MODEL] [--beam N] [--no-vocab]

Examples:
    python scripts/transcribe.py discourses/001-lag-baomer/sessions/003
    python scripts/transcribe.py "discourses/002-shaar-hayichud/sessions/011/voicenotes/Voice 1.m4a"

Engine: faster-whisper (CTranslate2) — ~4x faster than openai-whisper on CPU,
no torch/ffmpeg install needed (audio decoding is bundled via PyAV).

Default model: ivrit-ai/whisper-large-v3-turbo-ct2 — Whisper large-v3-turbo
fine-tuned on thousands of hours of Hebrew by ivrit.ai. Far more accurate on
Hebrew than stock Whisper "medium" (which this script used before). Downloads
~1.6 GB from Hugging Face on first run, cached afterwards.

Other useful --model values:
    ivrit-ai/whisper-large-v3-ct2   slower, sometimes slightly more accurate
    large-v3                        stock OpenAI model (not Hebrew-tuned)

Accuracy aids:
    * scripts/transcribe-vocab.txt is passed as the initial prompt so Chassidic
      terms (תניא, אדמו"ר הזקן, השתלשלות, ...) come out spelled correctly.
      Add terms there as you notice repeated misspellings.
    * Voice-activity detection drops silences (prevents hallucinated loops).
    * Output keeps paragraph breaks at natural pauses instead of one huge line.

Produces `<audio>.raw.txt` next to each audio file. Skips files that already
have a transcript. Never overwrites — delete the .raw.txt to retranscribe.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

try:
    from faster_whisper import WhisperModel  # type: ignore
except ImportError:
    print("Missing dependency. Install with: pip install -U faster-whisper")
    sys.exit(1)

AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg", ".flac", ".aac", ".opus"}
DEFAULT_MODEL = "ivrit-ai/whisper-large-v3-turbo-ct2"
VOCAB_FILE = Path(__file__).with_name("transcribe-vocab.txt")
PARAGRAPH_GAP_S = 1.5  # silence longer than this starts a new paragraph


def find_audio(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    vn_dir = target / "voicenotes"
    if not vn_dir.is_dir():
        print(f"No voicenotes/ dir in {target}")
        return []
    return [p for p in sorted(vn_dir.iterdir()) if p.suffix.lower() in AUDIO_EXTS]


def is_lfs_pointer(p: Path) -> bool:
    if p.stat().st_size > 1024:
        return False
    return p.read_bytes().startswith(b"version https://git-lfs")


def load_vocab() -> str | None:
    if not VOCAB_FILE.exists():
        return None
    terms = [
        ln.strip() for ln in VOCAB_FILE.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    return ", ".join(terms) + "." if terms else None


def pick_device() -> tuple[str, str]:
    try:
        import ctranslate2  # type: ignore
        if ctranslate2.get_cuda_device_count() > 0:
            return "cuda", "float16"
    except Exception:
        pass
    return "cpu", "int8"


def transcribe(model: WhisperModel, audio: Path, beam: int, prompt: str | None) -> str:
    segments, info = model.transcribe(
        str(audio),
        language="he",
        beam_size=beam,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        initial_prompt=prompt,
        condition_on_previous_text=False,  # avoids runaway repetition loops
    )
    paragraphs: list[list[str]] = [[]]
    last_end = 0.0
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        if paragraphs[-1] and seg.start - last_end > PARAGRAPH_GAP_S:
            paragraphs.append([])
        paragraphs[-1].append(text)
        last_end = seg.end
        print(f"  [{seg.end / 60:5.1f}/{info.duration / 60:.1f} min]", end="\r", flush=True)
    print()
    return "\n\n".join(" ".join(p) for p in paragraphs if p) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("targets", nargs="+", type=Path, help="session folder(s) or audio file(s)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--beam", type=int, default=5, help="beam size (higher = slower, slightly better)")
    ap.add_argument("--no-vocab", action="store_true", help="don't pass transcribe-vocab.txt as prompt")
    args = ap.parse_args()

    todo: list[Path] = []
    for t in args.targets:
        for audio in find_audio(t):
            out = audio.with_suffix(audio.suffix + ".raw.txt")
            if out.exists():
                print(f"Skip (transcript exists): {out}")
            elif is_lfs_pointer(audio):
                print(f"Skip (Git LFS pointer, audio not downloaded — run `git lfs pull`): {audio}")
            else:
                todo.append(audio)
    if not todo:
        return 0

    device, compute = pick_device()
    print(f"Loading {args.model} on {device} ({compute})...")
    model = WhisperModel(args.model, device=device, compute_type=compute)
    prompt = None if args.no_vocab else load_vocab()

    for audio in todo:
        out = audio.with_suffix(audio.suffix + ".raw.txt")
        print(f"Transcribing {audio}...")
        t0 = time.time()
        text = transcribe(model, audio, args.beam, prompt)
        out.write_text(text, encoding="utf-8")
        print(f"  -> {out.name}  ({len(text)} chars, {time.time() - t0:.0f}s)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
