#!/usr/bin/env python3
"""Transcribe voicenote(s) in a session folder using Whisper (Hebrew).

Usage:
    python scripts/transcribe.py discourses/001-my-slug/sessions/001

Model: MODEL below, run by faster-whisper on the CPU in int8. The first run
downloads it (about 3 GB, cached in ~/.cache/huggingface). It is slow;
transcription quality is the point. See TRANSCRIPTION.md.

Produces next to each audio file:
  <audio>.raw.txt    Whisper's text (never edited)
  <audio>.timed.txt  the same text, one segment per line with its start time
                     ([mm:ss]); UNCLEAR flags in the cleanup cite these times
Skips files that already have a .raw.txt. Never overwrites — delete the
.raw.txt and .timed.txt to retranscribe.

Then runs scripts/apply-fixes.py on the session, producing
`<audio>.fixed.txt` with the recurring corrections from
glossary/whisper-fixes.yaml already applied.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Missing dependency. Install with: pip install -r requirements.txt")
    sys.exit(1)

MODEL = "ivrit-ai/whisper-large-v3-ct2"   # ivrit.ai's Hebrew fine-tune of large-v3
AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg", ".flac", ".aac"}
# Whisper sometimes emits invisible bidi marks (mostly U+202B) mid-phrase;
# they stop multi-word glossary fixes from matching.
BIDI_MARKS = re.compile("[‎‏‪-‮⁦-⁩]")


def stamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


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

    pending = []
    for audio in audios:
        if audio.with_suffix(audio.suffix + ".raw.txt").exists():
            print(f"Skip (transcript exists): {audio.name}")
        else:
            pending.append(audio)

    if pending:
        print(f"Loading Whisper model ({MODEL})...")
        model = WhisperModel(MODEL, device="cpu", compute_type="int8",
                             cpu_threads=max(1, (os.cpu_count() or 2) // 2))

    for audio in pending:
        print(f"Transcribing {audio.name}...")
        segments, info = model.transcribe(str(audio), language="he", beam_size=5)
        plain, timed = [], []
        for seg in segments:
            text = BIDI_MARKS.sub("", seg.text).strip()
            plain.append(text)
            timed.append(f"[{stamp(seg.start)}] {text}")
            print(f"  {stamp(seg.end)} / {stamp(info.duration)}", end="\r", flush=True)
        out = audio.with_suffix(audio.suffix + ".raw.txt")
        out.write_text(" ".join(plain), encoding="utf-8")
        audio.with_suffix(audio.suffix + ".timed.txt").write_text("\n".join(timed) + "\n", encoding="utf-8")
        print(f"  -> {out.name} + .timed.txt  ({len(' '.join(plain))} chars)")

    print()
    fixer = Path(__file__).with_name("apply-fixes.py")
    return subprocess.call([sys.executable, str(fixer), str(session)])


if __name__ == "__main__":
    sys.exit(main())
