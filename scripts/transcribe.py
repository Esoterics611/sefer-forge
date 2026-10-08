#!/usr/bin/env python3
"""Transcribe voicenote(s) in a session folder using Whisper (Hebrew).

Usage:
    python scripts/transcribe.py discourses/001-my-slug/sessions/001

Produces `<audio>.raw.txt` next to each audio file. Skips files that
already have a transcript. Never overwrites — delete the .raw.txt if
you want to retranscribe.

Then runs scripts/apply-fixes.py on the session, producing
`<audio>.fixed.txt` with the recurring corrections from
glossary/whisper-fixes.yaml already applied.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    import whisper  # type: ignore
except ImportError:
    print("Missing dependency. Install with: pip install -U openai-whisper")
    print("(Whisper also requires ffmpeg on PATH.)")
    sys.exit(1)

AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg", ".flac", ".aac"}

def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/transcribe.py <session-path>")
        return 1

    session = Path(sys.argv[1])
    vn_dir = session / "voicenotes"
    if not vn_dir.is_dir():
        print(f"No voicenotes/ dir in {session}")
        return 1

    audios = [p for p in sorted(vn_dir.iterdir()) if p.suffix.lower() in AUDIO_EXTS]
    if not audios:
        print(f"No audio files found in {vn_dir}")
        return 0

    print(f"Loading Whisper model (medium)...")
    model = whisper.load_model("medium")

    for audio in audios:
        out = audio.with_suffix(audio.suffix + ".raw.txt")
        if out.exists():
            print(f"Skip (transcript exists): {out.name}")
            continue
        print(f"Transcribing {audio.name}...")
        result = model.transcribe(str(audio), language="he")
        out.write_text(result["text"], encoding="utf-8")
        print(f"  -> {out.name}  ({len(result['text'])} chars)")

    print()
    fixer = Path(__file__).with_name("apply-fixes.py")
    return subprocess.call([sys.executable, str(fixer), str(session)])


if __name__ == "__main__":
    sys.exit(main())
