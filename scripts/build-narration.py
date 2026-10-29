#!/usr/bin/env python3
"""Read a selection of Shivchei HaBesht stories aloud, as narration for a video.

Usage:
    python scripts/build-narration.py booklets/narration/<name>.yaml
    python scripts/build-narration.py <plan> --script            # script.txt only, no audio
    python scripts/build-narration.py <plan> --voice bm_george   # another voice than the plan's
    python scripts/build-narration.py <plan> --sample am_michael,bm_george,af_heart
    python scripts/build-narration.py --say Gershon Ghershon     # how the voice says words

A plan (booklets/narration/*.yaml) names the stories, in the order they are
read, from the English or French booklet text (shivchei-habesht-simple-en.md /
-fr.md), with the paragraphs left out (`cut:`), the changes that make the text
read aloud well (`edits:`, mostly brackets turned into spoken phrases) and how
the voice says the names (`say:`). The build stops when a cut or an edit no
longer matches the story, or a bracket is left in what is read.

Writes output/narration/<name>/:
    script.txt     what is read, paragraph by paragraph
    narration.wav  the reading; narration.mp3 as well (levelled for online video) when ffmpeg is installed
    narration.srt  subtitles, a cue per sentence (long ones split), timed to the reading
    chapters.txt   the start of each story, for a video description
--sample writes sample-<voice>.wav/.mp3 (the intro and the first paragraph) for
each voice named, to choose one by ear.

The voice is Kokoro (Apache 2.0, free to use in a published video), run on the
CPU through kokoro-onnx: pip install -r requirements-narration.txt. The model
files (about 350 MB) are downloaded on first use into KOKORO_DIR, by default
~/.cache/sefer-forge/kokoro. Voices: am_* American and bm_* British men,
af_* / bf_* women, ff_siwis French. Kokoro has no Hebrew voice.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.request
import wave
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml")
    sys.exit(1)

SOURCES = {"en": "shivchei-habesht-simple-en.md", "fr": "shivchei-habesht-simple-fr.md"}
SUMMARY = {"en": r"\*\*Summary:\*\*", "fr": r"\*\*Résumé :\*\*"}
COLOPHON = {"en": r"Finished and complete\.", "fr": r"Fin\. Louange"}
STORY_COUNT = 211          # the author's introduction + stories 1-210
OUT = Path("output/narration")
MODEL_DIR = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "sefer-forge" / "kokoro"))
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
VOICE_LANG = {"a": "en-us", "b": "en-gb", "f": "fr-fr"}   # by the voice name's first letter
# Silence, in seconds, after a sentence, a paragraph, a story's title, a story.
PAUSE = {"sentence": 0.3, "paragraph": 0.8, "title": 1.0, "story": 2.0}
SUB_LINE = 42              # characters per subtitle line, two lines per cue


def load_sections(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^(?=## )", text, flags=re.M)[1:]   # [0] is the file header
    if len(sections) != STORY_COUNT:
        sys.exit(f"{path}: expected {STORY_COUNT} '## ' sections, found {len(sections)}")
    return sections


def plain(s: str) -> str:
    """Markdown to the words read: no blockquote marks, emphasis or line breaks."""
    s = re.sub(r"^>\s?", "", s, flags=re.M)
    return " ".join(s.replace("*", "").split())


def story_paragraphs(section: str, entry: dict, lang: str) -> tuple[str, list[str]]:
    """Return (title, paragraphs read) for one story of the plan."""
    n = entry["n"]
    head, _, body = section.partition("\n")
    _, sep, title = head[3:].strip().partition(" — ")
    title = title if sep else head[3:].strip()
    body = re.sub(r"\s*<!--.*?-->", "", body, flags=re.S)
    paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
    paras = [p for p in paras if not re.match(SUMMARY[lang], p) and not re.match(COLOPHON[lang], p)]
    for cut in entry.get("cut") or []:
        hits = [p for p in paras if p.startswith(cut)]
        if len(hits) != 1:
            sys.exit(f"story {n}: cut {cut!r} opens {len(hits)} paragraphs, not 1")
        paras.remove(hits[0])
    text = "\n\n".join(paras)
    for e in entry.get("edits") or []:
        found = text.count(e["from"])
        if found != 1:
            sys.exit(f"story {n}: edit from {e['from'][:60]!r} found {found} times, not 1")
        text = text.replace(e["from"], e["to"])
    return plain(title), [plain(p) for p in re.split(r"\n\s*\n", text) if p.strip()]


def build_blocks(plan: dict, sections: list[str]) -> list[dict]:
    """The narration as blocks: {text, pause after it, chapter it opens or None}."""
    lang = plan["lang"]
    blocks = []
    if plan.get("intro"):
        blocks.append({"text": plain(plan["intro"]), "pause": PAUSE["story"], "chapter": "Introduction"})
    for entry in plan["stories"]:
        title, paras = story_paragraphs(sections[entry["n"]], entry, lang)
        blocks.append({"text": title.rstrip(".") + ".", "pause": PAUSE["title"], "chapter": title})
        blocks += [{"text": p, "pause": PAUSE["paragraph"], "chapter": None} for p in paras]
        blocks[-1]["pause"] = PAUSE["story"]
    if plan.get("outro"):
        blocks.append({"text": plain(plan["outro"]), "pause": 0.0, "chapter": None})
    left = [b["text"] for b in blocks if re.search(r"[()\[\]{}<>]", b["text"])]
    if left:
        sys.exit("brackets left in what is read; turn them into words with an edit:\n  "
                 + "\n  ".join(t[:100] for t in left))
    return blocks


def sentences(paragraph: str) -> list[str]:
    return [s for s in re.split(r'(?<=[.!?])\s+|(?<=[.!?]["»])\s+', paragraph) if s]


def spoken(text: str, say: dict) -> str:
    for word in sorted(say, key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(word)}(?!\w)", say[word], text)
    return text


def load_model():
    try:
        from kokoro_onnx import Kokoro
    except ImportError:
        sys.exit("Missing dependency. Install with: pip install -r requirements-narration.txt")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    for name in MODEL_FILES:
        path = MODEL_DIR / name
        if not path.exists():
            print(f"  downloading {name} into {MODEL_DIR} ...")
            part = path.with_name(name + ".part")
            urllib.request.urlretrieve(MODEL_URL + name, part)
            part.replace(path)
    return Kokoro(str(MODEL_DIR / MODEL_FILES[0]), str(MODEL_DIR / MODEL_FILES[1]))


def voice_lang(voice: str) -> str:
    if voice[:1] not in VOICE_LANG:
        sys.exit(f"voice {voice!r}: expected a Kokoro voice name such as am_michael or bm_george")
    return VOICE_LANG[voice[0]]


def synthesize(model, blocks: list[dict], voice: str, speed: float, say: dict):
    """Read the blocks; return (samples, rate, cues), a cue (start, end, text) per sentence."""
    import numpy as np
    lang, rate, t = voice_lang(voice), 24000, 0.0
    audio, cues = [], []
    for b in blocks:
        if b["chapter"]:
            print(f"  {b['chapter']}")
        b["start"] = t
        parts = sentences(b["text"])
        for j, s in enumerate(parts):
            samples, rate = model.create(spoken(s, say), voice=voice, speed=speed, lang=lang)
            cues.append((t, t + len(samples) / rate, s))
            gap = np.zeros(int((b["pause"] if j == len(parts) - 1 else PAUSE["sentence"]) * rate), np.float32)
            audio += [samples, gap]
            t += (len(samples) + len(gap)) / rate
    return np.concatenate(audio), rate, cues


def write_audio(samples, rate: int, wav: Path) -> Path:
    import numpy as np
    pcm = (np.clip(samples, -1.0, 1.0) * 32767).astype("<i2").tobytes()
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    if not shutil.which("ffmpeg"):
        return wav
    mp3 = wav.with_suffix(".mp3")
    # Levelled to -16 LUFS, the usual loudness for spoken audio online; the WAV is left as read.
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)], check=True)
    return mp3


def fits(text: str) -> bool:
    return len(textwrap.wrap(text, SUB_LINE, break_on_hyphens=False)) <= 2


def cue_pieces(text: str) -> list[str]:
    """Split a sentence into subtitle cues of at most two lines, of even length,
    at a comma where one is near."""
    pieces, words = [], text.split()
    while not fits(" ".join(words)):
        rest = " ".join(words)
        target = len(rest) / max(2, math.ceil(len(rest) / (2 * SUB_LINE - 6)))
        best = None
        for take in range(1, len(words)):
            head = " ".join(words[:take])
            if not fits(head):
                break
            score = abs(len(head) - target) - (15 if head[-1] in ",;:" else 0)
            if best is None or score < best[0]:
                best = (score, take)
        pieces.append(" ".join(words[:best[1]]))
        words = words[best[1]:]
    return pieces + [" ".join(words)]


def stamp(t: float, srt: bool = True) -> str:
    h, rem = divmod(int(t), 3600)
    m, s = divmod(rem, 60)
    if srt:
        return f"{h:02d}:{m:02d}:{s:02d},{int(round((t - int(t)) * 1000)) % 1000:03d}"
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def write_srt(cues: list[tuple[float, float, str]], path: Path) -> None:
    out, n = [], 0
    for start, end, text in cues:
        pieces = cue_pieces(text)
        total = sum(len(p) for p in pieces)
        t = start
        for p in pieces:
            d = (end - start) * len(p) / total
            n += 1
            out.append(f"{n}\n{stamp(t)} --> {stamp(t + d)}\n" + "\n".join(textwrap.wrap(p, SUB_LINE, break_on_hyphens=False)) + "\n")
            t += d
    path.write_text("\n".join(out), encoding="utf-8")


def write_script(blocks: list[dict], path: Path) -> None:
    lines = []
    for b in blocks:
        if b["chapter"] and b["chapter"] != "Introduction":
            lines.append(f"# {b['text']}")
        else:
            lines.append(textwrap.fill(b["text"], 90, break_on_hyphens=False))
    path.write_text("\n\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    if argv[:1] == ["--say"]:
        model = load_model()
        for w in argv[1:]:
            print(f"{w:20} {model.tokenizer.phonemize(w, 'en-us')}")
        return
    if not argv or argv[0].startswith("--"):
        sys.exit(__doc__)
    plan_path = Path(argv[0])
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    if plan["lang"] not in SOURCES:
        sys.exit(f"{plan_path}: lang must be one of {', '.join(SOURCES)} (Kokoro has no Hebrew voice)")
    voice, samples_for = plan["voice"], []
    if "--voice" in argv:
        voice = argv[argv.index("--voice") + 1]
    if "--sample" in argv:
        samples_for = argv[argv.index("--sample") + 1].split(",")
    say = plan.get("say") or {}

    sections = load_sections(Path(SOURCES[plan["lang"]]))
    blocks = build_blocks(plan, sections)
    out = OUT / plan_path.stem
    out.mkdir(parents=True, exist_ok=True)
    write_script(blocks, out / "script.txt")
    words = sum(len(b["text"].split()) for b in blocks)
    print(f"  {out / 'script.txt'}  ({words} words, about {words / 150:.0f} minutes)")
    if "--script" in argv:
        return

    model = load_model()
    if samples_for:
        first = next(i for i, b in enumerate(blocks) if b["chapter"] not in (None, "Introduction"))
        for v in samples_for:
            audio, rate, _ = synthesize(model, blocks[:first + 2], v, plan.get("speed", 1.0), say)
            print(f"  {write_audio(audio, rate, out / f'sample-{v}.wav')}")
        return

    audio, rate, cues = synthesize(model, blocks, voice, plan.get("speed", 1.0), say)
    print(f"  {write_audio(audio, rate, out / 'narration.wav')}  ({len(audio) / rate / 60:.1f} minutes, voice {voice})")
    write_srt(cues, out / "narration.srt")
    print(f"  {out / 'narration.srt'}")
    chapters = [f"{stamp(b['start'], srt=False)} {b['chapter']}" for b in blocks if b["chapter"]]
    (out / "chapters.txt").write_text("\n".join(chapters) + "\n", encoding="utf-8")
    print(f"  {out / 'chapters.txt'}")


if __name__ == "__main__":
    main(sys.argv[1:])
