#!/usr/bin/env python3
"""Read a selection of Shivchei HaBesht stories aloud, as narration for a video.

Usage:
    python scripts/build-narration.py booklets/narration/<name>.yaml
    python scripts/build-narration.py <plan> --script            # script.txt only, no audio
    python scripts/build-narration.py <plan> --voice bm_george   # another voice than the plan's
    python scripts/build-narration.py <plan> --video             # the video again, from the reading made
    python scripts/build-narration.py <plan> --frame             # only the picture with its titles, to look at
    python scripts/build-narration.py <plan> --sample am_michael,bm_george,af_heart
    python scripts/build-narration.py --say Gershon Ghershon     # how the voice says words
    python scripts/build-narration.py --say --lang fr "Na'hman"  # ... in French
    python scripts/build-narration.py <plan> --names             # how it says every name in the plan

A plan (booklets/narration/*.yaml) names the stories, in the order they are
read, from the English or French booklet text (shivchei-habesht-simple-en.md /
-fr.md), with the paragraphs left out (`cut:`), the brackets that explain a word left
out (`drop:`, by their opening words), the changes that make the text
read aloud well (`edits:`: the booklet's bracketed explanations of words left
out, its other brackets turned into spoken phrases) and how the voice says the
names (`say:`, over the shared booklets/narration/say-<lang>.yaml). Nothing of the booklet's contents or glossary is read: only the
plan's short `intro:`, the stories and its `outro:`. The build stops when a cut
or an edit no longer matches the story, or a bracket is left in what is read.

Writes output/narration/<name>/:
    script.txt     what is read, paragraph by paragraph
    narration.wav  the reading; narration.mp3 as well (levelled for online video) when ffmpeg is installed
    narration.srt  subtitles, a cue per sentence (long ones split), timed to the reading
    chapters.txt   the start of each story, for a video description
    video.mp4      for YouTube: one picture (frame.png) for the whole reading
    thumbnail.jpg  the picture at 1280x720, for the video's thumbnail
The picture is the plan's `image:` (a JPG/PNG, or an SVG drawing, which headless
Chrome renders: CHROME names the browser, by default Windows Chrome reached from
WSL or the container's Chromium), darkened below for the series and the
narration's title; without an image, a title card in the booklets' colours and
EB Garamond (templates/fonts).
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
# -16 LUFS, the usual loudness for spoken audio online.
LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=11"
SERIES = Path("booklets/booklets.yaml")    # the series title and subtitle per language
SAY = "booklets/narration/say-{}.yaml"      # respellings shared by every plan, per language
FONTS = Path("templates/fonts")
CHROME = os.environ.get("CHROME") or next(
    (c for c in ("/mnt/c/Program Files/Google/Chrome/Application/chrome.exe", "/opt/pw-browsers/chromium")
     if Path(c).exists()), "google-chrome")
VIDEO = (1920, 1080)
GOLD, CREAM, DARK = (201, 164, 92), (239, 230, 210), (14, 11, 8)


def load_sections(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    sections = re.split(r"^(?=## )", text, flags=re.M)[1:]   # [0] is the file header
    if len(sections) != STORY_COUNT:
        sys.exit(f"{path}: expected {STORY_COUNT} '## ' sections, found {len(sections)}")
    return sections


def plain(s: str) -> str:
    """Markdown to the words read: no blockquote marks, emphasis or line breaks."""
    s = re.sub(r"^>\s?", "", s, flags=re.M)
    s = " ".join(s.replace("*", "").split())
    # French puts a space before » : ; ? ! and after «: keep the mark with its word.
    return re.sub(r" ([»:;?!])", "\u00a0\\1", s).replace("« ", "«\u00a0")


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
    for opening in entry.get("drop") or []:
        # A bracket that explains, named by its opening words: dropped to its closing bracket.
        found = text.count(opening)
        if found != 1 or not opening.startswith("("):
            sys.exit(f"story {n}: drop {opening[:60]!r} found {found} times, not 1 (it starts with its bracket)")
        start, depth = text.index(opening), 0
        for end in range(start, len(text)):
            depth += {"(": 1, ")": -1}.get(text[end], 0)
            if depth == 0:
                break
        text = text[:start].rstrip(" ") + text[end + 1:]
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
        blocks.append({"text": plain(plan["intro"]), "pause": PAUSE["story"], "chapter": None})
    for entry in plan["stories"]:
        if "MATURE:" in sections[entry["n"]]:
            sys.exit(f"story {entry['n']} is flagged MATURE: not for narration (prompts/narration-rules.md)")
        title, paras = story_paragraphs(sections[entry["n"]], entry, lang)
        blocks.append({"text": title.rstrip(".") + ".", "pause": PAUSE["title"], "chapter": title})
        blocks += [{"text": p, "pause": PAUSE["paragraph"], "chapter": None} for p in paras]
        blocks[-1]["pause"] = PAUSE["story"]
    if plan.get("outro"):
        blocks.append({"text": plain(plan["outro"]), "pause": 0.0, "chapter": None})
    left = [b["text"] for b in blocks if re.search(r"[()\[\]{}<>]", b["text"])]
    if left:
        sys.exit("brackets left in what is read; with an edit, drop the explanation or reword the aside:\n  "
                 + "\n  ".join(t[:100] for t in left))
    return blocks


def sentences(paragraph: str) -> list[str]:
    # A sentence ends at . ! ? (and a closing quote), never before a lowercase word ('K.Z." is mentioned').
    return [s for s in re.split(r'(?:(?<=[.!?])|(?<=[.!?]["”»])|(?<=[.!?]\u00a0»)) (?![a-zà-ÿ])', paragraph) if s]


def spoken(text: str, say: dict, lang: str) -> str:
    # A lowercase entry (tzaddik) also covers the word opening a sentence or a title (Tzaddik).
    say = {**{w[0].upper() + w[1:]: v[0].upper() + v[1:] for w, v in say.items() if w[:1].islower()}, **say}
    for word in sorted(say, key=len, reverse=True):
        text = re.sub(rf"(?<!\w){re.escape(word)}(?!\w)", say[word], text)
    if lang.startswith("fr"):
        # 'h writes the Hebrew ח (Na'hman, Pessa'h, 'hazan): the French r is the
        # nearest sound. Not after an elided l' d' t' m' n' j' s' c' (l'homme).
        text = re.sub(r"(?<!\b[lLdDtTmMnNjJsScC])(?<!ujourd)'([hH])",
                      lambda m: "r" if m.group(1) == "h" else "R", text)
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
            samples, rate = model.create(spoken(s, say, lang), voice=voice, speed=speed, lang=lang)
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
    # The MP3 and the video are levelled; the WAV is left as read.
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", LOUDNORM,
                    "-ar", "44100", "-codec:a", "libmp3lame", "-b:a", "160k", str(mp3)], check=True)
    return mp3


def cover(img, size: tuple[int, int]):
    """Scale and crop a picture to fill `size`."""
    w, h = size
    scale = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)))
    left, top = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def render_svg(svg: Path, png: Path) -> None:
    """An SVG drawing to a PNG at the video's size, by headless Chrome."""
    src, dst = svg.resolve(), png.resolve()
    if CHROME.endswith(".exe"):       # Windows Chrome from WSL needs Windows paths
        src, dst = (subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True,
                                   check=True).stdout.strip() for p in (src, dst))
    # Linux Chrome refuses to run as root (a container) without --no-sandbox.
    sandbox = ["--no-sandbox"] if hasattr(os, "geteuid") and os.geteuid() == 0 else []
    png.unlink(missing_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", *sandbox,
                    f"--window-size={VIDEO[0]},{VIDEO[1]}", f"--screenshot={dst}", str(src)],
                   check=True, capture_output=True)
    if not png.exists():
        sys.exit(f"Chrome wrote no picture for {svg}")


def make_frame(plan: dict, out: Path) -> Path:
    """The picture shown for the whole video, and its thumbnail."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        sys.exit("Missing dependency. Install with: pip install pillow")
    series = yaml.safe_load(SERIES.read_text(encoding="utf-8"))["languages"][plan["lang"]]
    # Typographic apostrophes, as the booklets print them.
    series = {k: re.sub(r"(?<=\w)'", "\u2019", v) for k, v in series.items()}
    plan = {**plan, "title": re.sub(r"(?<=\w)'", "\u2019", plan["title"])}
    W, H = VIDEO
    if plan.get("image"):
        picture = Path(plan["image"])
        if picture.suffix == ".svg":
            render_svg(picture, out / "picture.png")
            picture = out / "picture.png"
        frame = cover(Image.open(picture).convert("RGB"), VIDEO)
        # Darken the lower part, where the titles go.
        shade = Image.linear_gradient("L").resize(VIDEO).point(lambda v: min(235, int(max(0, v - 60) * 1.6)))
        frame = Image.composite(Image.new("RGB", VIDEO, DARK), frame, shade)
    else:
        frame = Image.composite(Image.new("RGB", VIDEO, DARK), Image.new("RGB", VIDEO, (52, 40, 28)),
                                Image.radial_gradient("L").resize(VIDEO))
    draw = ImageDraw.Draw(frame)
    font = lambda name, size: ImageFont.truetype(str(FONTS / f"EBGaramond-{name}.ttf"), size)
    small, sub = font("Regular", 40), font("Italic", 46)
    # The title on one line, a little smaller if need be; else two even lines.
    words = plan["title"].split()
    for size in range(116, 91, -4):
        big = font("SemiBold", size)
        if draw.textlength(plan["title"], font=big) <= W - 300:
            lines = [plan["title"]]
            break
    else:
        size = 116
        while True:
            big = font("SemiBold", size)
            width = lambda k: max(draw.textlength(" ".join(words[:k]), font=big),
                                  draw.textlength(" ".join(words[k:]), font=big))
            k = min(range(1, len(words)), key=width)
            if width(k) <= W - 300 or size <= 72:
                lines = [" ".join(words[:k]), " ".join(words[k:])]
                break
            size -= 8

    def centred(y: float, text: str, f, fill, tracking: int = 0) -> None:
        widths = [draw.textlength(c, font=f) for c in text] if tracking else [draw.textlength(text, font=f)]
        x = (W - sum(widths) - tracking * (len(widths) - 1)) / 2
        for c, w in zip(text if tracking else [text], widths):
            draw.text((x, y), c, font=f, fill=fill)
            x += w + tracking

    gap = size * 1.18
    block = 40 + 70 + gap * len(lines) + 30 + 46
    y = H - 110 - block if plan.get("image") else (H - block) / 2
    centred(y, series["series"].upper(), small, GOLD, tracking=6)
    cx, oy = W / 2, y + 40 + 35
    draw.line([(cx - 170, oy), (cx - 22, oy)], fill=GOLD, width=2)
    draw.line([(cx + 22, oy), (cx + 170, oy)], fill=GOLD, width=2)
    draw.polygon([(cx, oy - 9), (cx + 9, oy), (cx, oy + 9), (cx - 9, oy)], fill=GOLD)
    y += 40 + 70
    for line in lines:
        centred(y, line, big, CREAM)
        y += gap
    centred(y + 30, series["subtitle"], sub, GOLD)
    if not plan.get("image"):
        draw.rectangle([48, 48, W - 49, H - 49], outline=GOLD, width=2)
        draw.rectangle([62, 62, W - 63, H - 63], outline=GOLD, width=1)
    path = out / "frame.png"
    frame.save(path)
    frame.resize((1280, 720), Image.LANCZOS).save(out / "thumbnail.jpg", quality=90)
    return path


def make_video(out: Path) -> Path:
    """One picture for the whole reading, as an MP4 for YouTube."""
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is needed for the video")
    video = out / "video.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "24",
                    "-i", str(out / "frame.png"), "-i", str(out / "narration.wav"),
                    "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-af", LOUDNORM, "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(video)], check=True)
    return video


def fits(text: str) -> bool:
    return len(textwrap.wrap(text, SUB_LINE, break_on_hyphens=False)) <= 2


def cue_pieces(text: str) -> list[str]:
    """Split a sentence into subtitle cues of at most two lines, of even length,
    at a comma where one is near."""
    pieces, words = [], text.split(" ")
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
        if b["chapter"]:
            lines.append(f"# {b['text']}")
        else:
            lines.append(textwrap.fill(b["text"], 90, break_on_hyphens=False))
    path.write_text("\n\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> None:
    if argv[:1] == ["--say"]:
        lang, words = "en-us", argv[1:]
        if words[:1] == ["--lang"]:
            lang, words = {"en": "en-us", "fr": "fr-fr"}.get(words[1], words[1]), words[2:]
        model = load_model()
        for w in words:
            print(f"{w:20} {model.tokenizer.phonemize(spoken(w, {}, lang), lang)}")
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
    shared = Path(SAY.format(plan["lang"]))
    say = {**(yaml.safe_load(shared.read_text(encoding="utf-8")) or {} if shared.exists() else {}),
           **(plan.get("say") or {})}

    sections = load_sections(Path(SOURCES[plan["lang"]]))
    blocks = build_blocks(plan, sections)
    out = OUT / plan_path.stem
    out.mkdir(parents=True, exist_ok=True)
    write_script(blocks, out / "script.txt")
    words = sum(len(b["text"].split()) for b in blocks)
    print(f"  {out / 'script.txt'}  ({words} words, about {words / 175:.0f} minutes)")
    if "--script" in argv:
        return
    if "--names" in argv:
        model, lang = load_model(), voice_lang(voice)
        names = sorted({w for b in blocks for w in re.findall(r"(?<![\w'])(?:[A-ZÀ-Ý]|'[hH])[\w'-]*", b["text"])})
        for w in names:
            ph = model.tokenizer.phonemize(spoken(w, say, lang), lang)
            flag = "  <- read as another language" if "(" in ph else ""
            print(f"  {w:22} {spoken(w, say, lang):22} {ph}{flag}")
        return
    if "--frame" in argv:
        print(f"  {make_frame(plan, out)}")
        return
    if "--video" in argv:
        if not (out / "narration.wav").exists():
            sys.exit(f"{out / 'narration.wav'}: no reading yet; build without --video first")
        make_frame(plan, out)
        print(f"  {make_video(out)}")
        return

    model = load_model()
    if samples_for:
        first = next(i for i, b in enumerate(blocks) if b["chapter"])
        for v in samples_for:
            audio, rate, _ = synthesize(model, blocks[:first + 2], v, plan.get("speed", 1.0), say)
            print(f"  {write_audio(audio, rate, out / f'sample-{v}.wav')}")
        return

    audio, rate, cues = synthesize(model, blocks, voice, plan.get("speed", 1.0), say)
    print(f"  {write_audio(audio, rate, out / 'narration.wav')}  ({len(audio) / rate / 60:.1f} minutes, voice {voice})")
    write_srt(cues, out / "narration.srt")
    print(f"  {out / 'narration.srt'}")
    # A video's chapters start at 0:00, so the intro belongs to the first story.
    chapters = [(b["start"], b["chapter"]) for b in blocks if b["chapter"]]
    chapters[0] = (0.0, chapters[0][1])
    (out / "chapters.txt").write_text("".join(f"{stamp(t, srt=False)} {c}\n" for t, c in chapters), encoding="utf-8")
    print(f"  {out / 'chapters.txt'}")
    make_frame(plan, out)
    print(f"  {make_video(out)}")


if __name__ == "__main__":
    main(sys.argv[1:])
