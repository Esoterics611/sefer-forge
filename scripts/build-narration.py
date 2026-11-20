#!/usr/bin/env python3
"""Read a selection of Shivchei HaBesht stories aloud, as narration for a video.

Usage:
    python scripts/build-narration.py booklets/narration/<name>.yaml
    python scripts/build-narration.py <plan> --script            # script.txt only, no audio
    python scripts/build-narration.py <plan> --voice bm_george   # another voice than the plan's
    python scripts/build-narration.py <plan> --video             # the video again, from the reading made
    python scripts/build-narration.py <plan> --frame             # only the picture with its titles, to look at
    python scripts/build-narration.py <plan> --thumbnail         # only the thumbnail
    python scripts/build-narration.py <plan> --sample am_michael,bm_george,af_heart
    python scripts/build-narration.py --say Gershon Ghershon     # how the voice says words
    python scripts/build-narration.py --say --lang fr "Na'hman"  # ... in French
    python scripts/build-narration.py <plan> --names             # how it says every name in the plan

A plan (booklets/narration/*.yaml) names the stories, in the order they are
read, from the English, French or Hebrew booklet text (shivchei-habesht-simple-en.md /
-fr.md / shivchei-habesht-simple.md), with the paragraphs left out (`cut:`), the brackets that explain a word left
out (`drop:`, by their opening words), the changes that make the text
read aloud well (`edits:`: the booklet's bracketed explanations of words left
out, its other brackets turned into spoken phrases) and how the voice says the
names. A plan may read English renderings of shiurim instead (`parts:`, the
*-en.md files beside a discourse's Hebrew, whose "## " sections are its
chapters; prompts/render-english.md), with its own `series:` and `subtitle:`
for the title card and `about:`, `tags:`, `hashtags:` for YouTube (`say:`, over the shared booklets/narration/say-<lang>.yaml).
A plan may also read a written explanation whole (`biur:`, a built biur.md, with `read:` the stretches
read): a read-along, its words burned into a dark screen as they are read (readalong.ass; the rules'
"Read-along videos"), `--preview <seconds>` one still of it. Nothing of the booklet's contents or glossary is read: only the
plan's short `intro:`, the stories and its `outro:`. The build stops when a cut
or an edit no longer matches the story, or a bracket is left in what is read.

Writes output/narration/<name>/:
    script.txt     what is read, paragraph by paragraph
    narration.wav  the reading; narration.mp3 as well (levelled for online video) when ffmpeg is installed
    narration.srt  subtitles, a cue per sentence (long ones split), timed to the reading
    chapters.txt   the start of each story, for a video description
    video.mp4      for YouTube: one picture (frame.png) for the whole reading
    thumbnail.jpg  the same picture at 1280x720
The picture is the same plain title card for every episode (title_card()): בס"ד,
the series, the title in large letters and the subtitle, in EB Garamond
(templates/fonts), dark ink on warm off-white. A plan's `image:` is no longer used.
--sample writes sample-<voice>.wav/.mp3 (the intro and the first paragraph) for
each voice named, to choose one by ear.

The voice is Kokoro (Apache 2.0, free to use in a published video), run on the
CPU through kokoro-onnx: pip install -r requirements-narration.txt. The model
files (about 350 MB) are downloaded on first use into KOKORO_DIR, by default
~/.cache/sefer-forge/kokoro. Voices: am_* American and bm_* British men,
af_* / bf_* women, ff_siwis French. Kokoro has no Hebrew voice.

Hebrew (`lang: he`) is read by Google Cloud Text-to-Speech, a Chirp 3 HD voice
(`voice: he-IL-Chirp3-HD-<name>`), with the API key GOOGLE_TTS_API_KEY (an
environment secret: a key of the sefer-forge Google Cloud project, limited to
the Text-to-Speech API). Free up to 1 million characters a month; the build
counts what it sends in booklets/narration/tts-usage.yaml and refuses an
episode that would pass TTS_MONTHLY_LIMIT, so it never costs money.
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

SOURCES = {"en": "shivchei-habesht-simple-en.md", "fr": "shivchei-habesht-simple-fr.md",
           "he": "shivchei-habesht-simple.md"}
SUMMARY = {"en": r"\*\*Summary:\*\*", "fr": r"\*\*Résumé :\*\*", "he": r"\*\*סיכום:\*\*"}
COLOPHON = {"en": r"Finished and complete\.", "fr": r"Fin\. Louange", "he": r"תם ונשלם"}
STORY_COUNT = 211          # the author's introduction + stories 1-210
OUT = Path("output/narration")
MODEL_DIR = Path(os.environ.get("KOKORO_DIR", Path.home() / ".cache" / "sefer-forge" / "kokoro"))
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
MODEL_FILES = ("kokoro-v1.0.onnx", "voices-v1.0.bin")
VOICE_LANG = {"a": "en-us", "b": "en-gb", "f": "fr-fr"}   # by the voice name's first letter
GOOGLE_TTS = "https://texttospeech.googleapis.com/v1/text:synthesize"
TTS_USAGE = Path("booklets/narration/tts-usage.yaml")      # characters sent to Google, per month
TTS_MONTHLY_LIMIT = 900_000  # Chirp 3 HD is free up to 1,000,000 characters a month
# Silence, in seconds, after a sentence, a paragraph, a story's title, a story.
PAUSE = {"sentence": 0.3, "paragraph": 0.8, "title": 1.0, "story": 2.0}
SUB_LINE = 42              # characters per subtitle line, two lines per cue
# -16 LUFS, the usual loudness for spoken audio online.
LOUDNORM = "loudnorm=I=-16:TP=-1.5:LRA=11"
SERIES = Path("booklets/booklets.yaml")    # the series title and subtitle per language
SAY = "booklets/narration/say-{}.yaml"      # respellings shared by every plan, per language
FONTS = Path("templates/fonts")
VIDEO = (1920, 1080)


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


def rendering_is_current(path: Path) -> tuple[bool, dict]:
    """An English rendering (*-en.md beside its Hebrew): (whether its Hebrew is unchanged since, its frontmatter)."""
    import hashlib
    text = path.read_text(encoding="utf-8")
    meta = yaml.safe_load(text.split("---")[1]) if text.startswith("---") else {}
    # rendered_from is relative to the discourse folder (introduction.md, sessions/010/transcript.md).
    discourse = Path(str(path).split("/sessions/")[0]) if "/sessions/" in str(path) else path.parent
    source = discourse / meta.get("rendered_from", "")
    current = source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest()[:16] == meta.get("source_sha256")
    return current, meta


def text_sections(path: Path) -> list[tuple[str, list[str]]]:
    """An English rendering (a plan's `parts:`): its "## " sections as (title, paragraphs), comments left out."""
    current, meta = rendering_is_current(path)
    if not current:
        sys.exit(f"{path}: its Hebrew ({meta.get('rendered_from')}) changed after it was rendered: bring the English "
                 f"up to date, then set source_sha256 (prompts/render-english.md)")
    text = path.read_text(encoding="utf-8").split("---", 2)[2]
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for part in re.split(r"^## ", text, flags=re.M)[1:]:
        title, _, body = part.partition("\n")
        paras = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        out.append((plain(title), [plain(p) for p in paras]))
    return out


def build_blocks(plan: dict, sections: list[str]) -> list[dict]:
    """The narration as blocks: {text, pause after it, chapter it opens or None}."""
    lang = plan["lang"]
    blocks = []
    if plan.get("intro"):
        blocks.append({"text": plain(plan["intro"]), "pause": PAUSE["story"], "chapter": None})
    for part in plan.get("parts") or []:
        # An English rendering of a shiur, not booklet stories: each section is a chapter.
        for title, paras in text_sections(Path(part)):
            blocks.append({"text": title.rstrip(".") + ".", "pause": PAUSE["title"], "chapter": title})
            blocks += [{"text": p, "pause": PAUSE["paragraph"], "chapter": None} for p in paras]
            blocks[-1]["pause"] = PAUSE["story"]
    for entry in plan.get("stories") or []:
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


class GoogleVoice:
    """Google Cloud Text-to-Speech, with the same create() as Kokoro."""

    def __init__(self) -> None:
        self.key = os.environ.get("GOOGLE_TTS_API_KEY")
        if not self.key:
            sys.exit("GOOGLE_TTS_API_KEY is not set: the Hebrew voice is Google Cloud Text-to-Speech "
                     "(docs/youtube-publishing.md, Hebrew voice)")
        self.sent = 0

    def create(self, text: str, voice: str, speed: float, lang: str):
        import json
        import time
        import numpy as np
        body = json.dumps({"input": {"text": text},
                           "voice": {"languageCode": voice[:5], "name": voice},
                           "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000,
                                           "speakingRate": speed}}).encode()
        for attempt in range(6):
            req = urllib.request.Request(f"{GOOGLE_TTS}?key={self.key}", data=body,
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    audio = json.load(r)["audioContent"]
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 503) and attempt < 5:
                    time.sleep(5 * (attempt + 1))
                    continue
                sys.exit(f"Google Text-to-Speech: {e.code} {e.read().decode()[:400]}")
        import base64
        import io
        self.sent += len(text)
        with wave.open(io.BytesIO(base64.b64decode(audio))) as w:
            rate = w.getframerate()
            pcm = np.frombuffer(w.readframes(w.getnframes()), "<i2")
        return pcm.astype(np.float32) / 32768, rate


def tts_budget(blocks: list[dict], say: dict) -> int:
    """The characters this episode sends to Google; stop if the month's free allowance would be passed."""
    import datetime as dt
    month = dt.date.today().strftime("%Y-%m")
    used = (yaml.safe_load(TTS_USAGE.read_text(encoding="utf-8")) or {}) if TTS_USAGE.exists() else {}
    need = sum(len(spoken(s, say, "he")) for b in blocks for s in sentences(b["text"]))
    if used.get(month, 0) + need > TTS_MONTHLY_LIMIT:
        sys.exit(f"Google Text-to-Speech: {used.get(month, 0):,} characters used in {month}, this episode needs "
                 f"{need:,}: over the {TTS_MONTHLY_LIMIT:,} kept free. It waits for next month.")
    return need


def count_tts(sent: int) -> None:
    import datetime as dt
    month = dt.date.today().strftime("%Y-%m")
    used = (yaml.safe_load(TTS_USAGE.read_text(encoding="utf-8")) or {}) if TTS_USAGE.exists() else {}
    used[month] = used.get(month, 0) + sent
    TTS_USAGE.write_text("# Characters sent to Google Text-to-Speech (the Hebrew voice), per month; written by\n"
                         "# build-narration.py, which stops before TTS_MONTHLY_LIMIT. Commit it with the record.\n"
                         + yaml.safe_dump(used, sort_keys=True), encoding="utf-8")


def load_model(lang: str = "en"):
    if lang == "he":
        return GoogleVoice()
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
    if voice.startswith("he-IL-"):
        return "he"
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


def make_frame(plan: dict, out: Path) -> Path:
    """The picture shown for the whole video (frame.png) and its thumbnail: the same title card."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Missing dependency. Install with: pip install pillow")
    series = yaml.safe_load(SERIES.read_text(encoding="utf-8"))["languages"][plan["lang"]]
    if plan.get("series"):                      # a series of its own (a plan of `parts:`)
        series = {"series": plan["series"], "subtitle": plan.get("subtitle", "")}
    # Typographic apostrophes, as the booklets print them.
    series = {k: re.sub(r"(?<=\w)'", "\u2019", v) for k, v in series.items()}
    plan = {**plan, "title": re.sub(r"(?<=\w)'", "\u2019", plan["title"])}
    frame = title_card(plan, series, VIDEO)
    path = out / "frame.png"
    frame.save(path)
    frame.resize(THUMB, Image.LANCZOS).save(out / "thumbnail.jpg", quality=92)
    return path


# The title card: the same plain card for every episode, as the video's picture
# and its thumbnail, read at a glance and restful to look at for the whole
# reading: dark brown ink on warm off-white paper (title 11.7:1, neither pure
# black nor pure white), a muted bronze for the rest; בס"ד top right, the series
# in capitals over a short rule, the title large (one line, or two even lines),
# the series' subtitle in italic. No picture, no border, nothing that moves.
THUMB = (1280, 720)
PAPER, INK, BRONZE = (239, 232, 218), (47, 42, 36), (128, 100, 62)
HEBREW_FONTS = ["templates/fonts/FrankRuhlLibre.ttf", "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
                "/mnt/c/Windows/Fonts/davidbd.ttf", "C:/Windows/Fonts/davidbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def title_card(plan: dict, series: dict, size: tuple[int, int]):
    from PIL import Image, ImageDraw, ImageFont, features
    W, H = size
    k = W / THUMB[0]                                    # laid out at 1280x720, scaled
    # A read-along (a plan with `biur:`) has the same card in its own colours: light on dark.
    paper, ink, bronze = (DARK_BG, DARK_INK, DARK_GOLD) if plan.get("biur") else (PAPER, INK, BRONZE)
    img = Image.new("RGB", size, paper)
    draw = ImageDraw.Draw(img)
    def font(name: str, pt: float):
        if plan["lang"] != "he":
            return ImageFont.truetype(str(FONTS / f"EBGaramond-{name}.ttf"), round(pt * k))
        # Hebrew: Frank Ruhl Libre (no italic; its weights by name), a little larger for the same weight.
        f = ImageFont.truetype(str(FONTS / "FrankRuhlLibre.ttf"), round(pt * k * 1.05))
        f.set_variation_by_name({"SemiBold": "Bold", "Italic": "Regular"}.get(name, name))
        return f
    hebrew = next((f for f in HEBREW_FONTS if Path(f).exists()), None)
    if not hebrew:
        sys.exit("No Hebrew font for בס\"ד on the title card: " + ", ".join(HEBREW_FONTS))
    # בס"ד, top right; Pillow without raqm lays out no right-to-left text, so the letters go in reversed.
    bsd = 'בס"ד' if features.check("raqm") else 'בס"ד'[::-1]
    bsd_font = font("SemiBold", 38) if plan["lang"] == "he" else ImageFont.truetype(hebrew, round(40 * k))
    draw.text((W - 56 * k, 40 * k), bsd, font=bsd_font, fill=bronze, anchor="ra")


    def centred(y: float, text: str, f, fill, tracking: float = 0) -> None:
        widths = [draw.textlength(c, font=f) for c in text] if tracking else [draw.textlength(text, font=f)]
        x = (W - sum(widths) - tracking * (len(widths) - 1)) / 2
        for c, w in zip(text if tracking else [text], widths):
            draw.text((x, y), c, font=f, fill=fill)
            x += w + tracking

    # The title: one line as large as fits, else two even lines.
    words, room = plan["title"].split(), W - 160 * k
    for pt in range(150, 111, -6):
        big = font("SemiBold", pt)
        if draw.textlength(plan["title"], font=big) <= room:
            lines = [plan["title"]]
            break
    else:
        for pt in range(140, 71, -6):
            big = font("SemiBold", pt)
            width = lambda n: max(draw.textlength(" ".join(words[:n]), font=big),
                                  draw.textlength(" ".join(words[n:]), font=big))
            n = min(range(1, len(words)), key=width)
            if width(n) <= room:
                break
        lines = [" ".join(words[:n]), " ".join(words[n:])]
    size_px = pt * k
    gap = size_px * 1.12
    y = (H - (gap * (len(lines) - 1) + size_px)) / 2 + 10 * k
    centred(y - 120 * k, series["series"].upper(), font("Regular", 38), bronze,
            tracking=0 if plan["lang"] == "he" else 5 * k)        # spaced letters break Hebrew
    draw.line([(W / 2 - 90 * k, y - 52 * k), (W / 2 + 90 * k, y - 52 * k)], fill=bronze, width=max(2, round(2 * k)))
    for line in lines:
        centred(y - size_px * 0.18, line, big, ink)
        y += gap
    centred(y - gap + size_px + 40 * k, series["subtitle"], font("Italic", 44), bronze)
    return img


# --- Read-along: a written explanation (a ביאור) read aloud with its words on the screen ----------
#
# A plan with `biur:` (a built biur.md) reads the stretches its `read:` names
# and shows every word as it is read, burned into the picture: light letters on
# a dark ground (asked for 2026-11-20: to read along, and to fall asleep by,
# without a bright screen). The words of the text itself (bold in the print)
# are in a soft gold, the explanation in ivory, a note (a footnote of the
# print, read after its paragraph) in a dimmer italic; the section read is
# named small at the top. Citations in brackets are left out of voice and
# screen alike; a quotation inside one stays.

DARK_BG, DARK_INK, DARK_GOLD, DARK_NOTE, DARK_BRONZE = (26, 23, 20), (226, 218, 202), (226, 196, 138), \
    (172, 163, 148), (160, 136, 98)
SCREEN_LINE, SCREEN_LINES = 54, 3          # what one cue holds: three lines, wrapped wider by libass (EB Garamond 68)
_BOOK = r"(?:I{1,2} )?[A-Z][\w’']*(?: (?:of|[A-Z][\w’']*))*(?: [IVX]+)?"
REF = _BOOK + r",? (?:chapters? )?\d+[ab]?(?:[:.]\d+[ab]?)?(?:[–-]\d+[ab]?(?::\d+)?)?(?:, \d+[ab]?(?::\d+)?)*"


def biur_markdown(s: str) -> str:
    """A biur paragraph's markdown, as read: no numbers, comments or citations."""
    s = re.sub(r"\[[^\]]*\]\{\.pnum\}\s*", "", s)
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"\(\d{1,2}\) ?", "", s)                                   # the discourse's chapter numbers
    s = re.sub(rf"\((?:{REF}; )*{REF}: ", "(", s)                          # (Shabbat 114a: “...”) -> (“...”)
    s = re.sub(rf"\s*\((?:{REF}; )*{REF}\)", "", s)                        # (Psalms 92:10)
    s = re.sub(r"\s*\(\d+:\d+\)", "", s)                                       # Psalms (55:19)
    s = re.sub(rf",?(”),? {REF}\)", r"\1)", s)                                   # (“...,” Ecclesiastes 7:14)
    s = re.sub(r"\*\*\s*\*\*", " ", s)                                     # a bold run closed and reopened
    return " ".join(s.split())


def styled(md: str) -> tuple[str, list[int]]:
    """Markdown emphasis to (plain text, a style per character): 1 bold (the text), 2 italic."""
    text, styles, bold, italic = [], [], False, False
    for tok in re.split(r"(\*\*|\*)", md):
        if tok == "**":
            bold = not bold
        elif tok == "*":
            italic = not italic
        else:
            text.append(tok)
            styles += [bold | (italic << 1)] * len(tok)
    plain_text = "".join(text)
    # Spaces left at the edges by a removed citation.
    return plain_text, styles


def footnotes(md: str) -> tuple[str, list[str]]:
    """Take the [ ... ]{.fn} notes out of a paragraph (brackets inside them balanced)."""
    notes, out, i = [], [], 0
    while True:
        j = md.find("{.fn}", i)
        if j < 0:
            out.append(md[i:])
            break
        depth, k = 0, j - 1
        while k >= i:
            depth += {"]": 1, "[": -1}.get(md[k], 0)
            if depth == 0:
                break
            k -= 1
        out.append(md[i:k])
        notes.append(md[k + 1:j - 1])
        i = j + len("{.fn}")
    return "".join(out), notes


def biur_blocks(plan: dict) -> list[dict]:
    """The read-along as blocks: {text, styles, kind (title, heading, para, note), pause, chapter}."""
    src = Path(plan["biur"]).read_text(encoding="utf-8")
    src = src.split("---", 2)[2] if src.startswith("---") else src
    blocks = []

    def add(md: str, kind: str, chapter=None, pause=PAUSE["paragraph"]):
        text, styles = styled(biur_markdown(md))
        if text.strip():
            lead = len(text) - len(text.lstrip())
            text, styles = text.strip(), styles[lead:lead + len(text.strip())]
            blocks.append({"text": text, "styles": styles, "kind": kind, "pause": pause, "chapter": chapter})

    if plan.get("intro"):
        add(plan["intro"], "title", pause=PAUSE["story"])
    for stretch in plan["read"]:
        start = src.find(stretch["from"])
        end = src.find(stretch["to"], start + 1)
        if start < 0 or end < 0:
            sys.exit(f"{plan['biur']}: read from {stretch['from']!r} to {stretch['to']!r} not found")
        body = src[start:end]
        body = body.partition("\n")[2]           # its own heading: the chapter's name, or none
        if stretch.get("chapter"):
            add(stretch["chapter"], "heading", chapter=stretch["chapter"], pause=PAUSE["title"])
        for para in re.split(r"\n\s*\n", body):
            para = "\n".join(l for l in para.splitlines() if not l.startswith(":::")).strip()
            if not para or para.startswith("|"):
                continue
            if para.startswith("#"):
                title = para.lstrip("#").strip()
                add(title, "heading", chapter=plain(title), pause=PAUSE["title"])
                continue
            md, notes = footnotes(para)
            add(md, "para")
            for n in notes:
                add(n, "note")
        if blocks:
            blocks[-1]["pause"] = PAUSE["story"]
    if plan.get("outro"):
        add(plan["outro"], "title", pause=0.0)
    return blocks


def clauses(sentence: str) -> list[str]:
    """A sentence too long for one screen, said in parts at its ; and : (each part said whole)."""
    if fits_screen(sentence):
        return [sentence]
    parts = [p for p in re.split(r"(?<=[;:]) ", sentence) if p]
    out = [parts[0]]
    for p in parts[1:]:
        if fits_screen(out[-1] + " " + p):
            out[-1] += " " + p
        else:
            out.append(p)
    return out


def fits_screen(text: str) -> bool:
    return len(textwrap.wrap(text, SCREEN_LINE, break_on_hyphens=False)) <= SCREEN_LINES


def screen_pieces(text: str) -> list[str]:
    """A part too long for one screen, shown in even pieces, at a comma where one is near."""
    pieces, words = [], text.split(" ")
    while not fits_screen(" ".join(words)):
        rest = " ".join(words)
        target = len(rest) / math.ceil(len(rest) / (SCREEN_LINE * SCREEN_LINES - 20))
        best = None
        for take in range(1, len(words)):
            head = " ".join(words[:take])
            if not fits_screen(head):
                break
            score = abs(len(head) - target) - (25 if head[-1] in ",;:—" else 0)
            if best is None or score < best[0]:
                best = (score, take)
        pieces.append(" ".join(words[:best[1]]))
        words = words[best[1]:]
    return pieces + [" ".join(words)]


def synthesize_readalong(model, blocks: list[dict], voice: str, speed: float, say: dict):
    """Read the blocks part by part; return (samples, rate, cues), a cue (start, end, block, from, to) per screen."""
    import numpy as np
    lang, rate, t = voice_lang(voice), 24000, 0.0
    audio, cues = [], []
    for bi, b in enumerate(blocks):
        if b["chapter"]:
            print(f"  {b['chapter']}", flush=True)
        b["start"] = t
        parts = [c for s in sentences(b["text"]) for c in clauses(s)]
        at = 0
        for j, part in enumerate(parts):
            at = b["text"].index(part, at)
            said = re.sub(r"[\[\]()]", "", spoken(part, say, lang))
            samples, rate = model.create(said, voice=voice, speed=speed, lang=lang)
            length = len(samples) / rate
            pieces = screen_pieces(part)
            total, u, p_at = sum(len(p) for p in pieces), t, at
            for p in pieces:
                p_at = b["text"].index(p, p_at)
                d = length * len(p) / total
                cues.append((u, u + d, bi, p_at, p_at + len(p)))
                u, p_at = u + d, p_at + len(p)
            last = j == len(parts) - 1
            gap = np.zeros(int((b["pause"] if last else PAUSE["sentence"]) * rate), np.float32)
            audio += [samples, gap]
            t += length + len(gap) / rate
            at += len(part)
    return np.concatenate(audio), rate, cues


def ass_colour(rgb: tuple[int, int, int]) -> str:
    return "&H00%02X%02X%02X" % (rgb[2], rgb[1], rgb[0])


def write_readalong(blocks: list[dict], cues: list, out: Path) -> None:
    """The words on the screen (readalong.ass, burned in) and the same cues as narration.srt."""
    W, H = VIDEO
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Body,EB Garamond,68,{ass_colour(DARK_INK)},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,230,230,40,1
Style: Note,EB Garamond,60,{ass_colour(DARK_NOTE)},&H000000FF,&H00000000,&H00000000,0,1,0,0,100,100,0,0,1,0,0,5,260,260,40,1
Style: Heading,EB Garamond,72,{ass_colour(DARK_GOLD)},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,200,200,40,1
Style: Top,EB Garamond,36,{ass_colour(DARK_BRONZE)},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,8,200,200,64,1
Style: Label,EB Garamond,32,{ass_colour(DARK_BRONZE)},&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,0,5,200,200,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    def ts(t: float) -> str:
        cs = int(round(t * 100))
        return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"

    def esc(s: str) -> str:
        return s.replace("\\", "∖").replace("{", "(").replace("}", ")")

    def runs(b: dict, a: int, z: int) -> str:
        """The text from a to z with its colours: the text's own words gold, the explanation ivory."""
        out, cur = [], None
        for i in range(a, z):
            st = b["styles"][i]
            if b["kind"] == "para" and st != cur:
                colour = DARK_GOLD if st & 1 else DARK_INK
                out.append("{\\c%s\\i%d}" % (ass_colour(colour)[2:] + "&", 1 if st & 2 else 0))
                cur = st
            elif b["kind"] == "note" and st != cur:
                out.append("{\\i%d}" % (0 if st & 2 else 1))     # a term set off in a note: upright
                cur = st
            out.append(esc(b["text"][i]))
        return "".join(out)

    events, srt, chapter_spans = [], [], []
    starts = [(b["start"], plain(b["chapter"])) for b in blocks if b["chapter"]]
    for (t0, name), nxt in zip(starts, starts[1:] + [(cues[-1][1] + 5, None)]):
        chapter_spans.append((t0, nxt[0], name))
    for t0, t1, name in chapter_spans:
        events.append(f"Dialogue: 0,{ts(t0)},{ts(t1)},Top,,0,0,0,,{esc(name.upper())}")
    for n, (c0, c1, bi, a, z) in enumerate(cues):
        b = blocks[bi]
        if b["kind"] == "title" and bi == 0:
            continue                         # the opening words: the title card says them
        # Each cue stays up until the next one comes (through the pauses), so the screen is never empty.
        end = cues[n + 1][0] if n + 1 < len(cues) else c1 + 4
        style = {"para": "Body", "note": "Note", "heading": "Heading", "title": "Heading"}[b["kind"]]
        text = runs(b, a, z)
        if b["kind"] == "note":
            text = "{\\fs30\\c%s\\i0\\fsp3}NOTE{\\r}\\N" % (ass_colour(DARK_BRONZE)[2:] + "&") + text
        events.append(f"Dialogue: 1,{ts(c0)},{ts(end)},{style},,0,0,0,,{{\\fad(220,220)}}{text}")
        srt.append(f"{n + 1}\n{stamp(c0)} --> {stamp(c1)}\n"
                   + "\n".join(textwrap.wrap(b["text"][a:z], SUB_LINE, break_on_hyphens=False)) + "\n")
    (out / "readalong.ass").write_text(head + "\n".join(events) + "\n", encoding="utf-8")
    (out / "narration.srt").write_text("\n".join(srt), encoding="utf-8")


def make_readalong_video(out: Path, title_until: float) -> Path:
    """The dark ground with the words burned in; the title card for the opening words, fading out."""
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is needed for the video")
    video = out / "video.mp4"
    bg = "0x%02X%02X%02X" % DARK_BG
    fade = max(0.0, title_until - 1.0)
    graph = (f"[1]format=rgba,fade=t=out:st={fade:.2f}:d=1:alpha=1[card];"
             f"[0][card]overlay=eof_action=pass:shortest=0[v];"
             f"[v]ass={out / 'readalong.ass'}:fontsdir={FONTS},format=yuv420p[out]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-f", "lavfi", "-i", f"color=c={bg}:s={VIDEO[0]}x{VIDEO[1]}:r=10",
                    "-loop", "1", "-framerate", "10", "-t", f"{title_until + 0.5:.2f}", "-i", str(out / "frame.png"),
                    "-i", str(out / "narration.wav"),
                    "-filter_complex", graph, "-map", "[out]", "-map", "2:a",
                    "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-crf", "22", "-g", "100",
                    "-af", LOUDNORM, "-ar", "48000", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(video)], check=True)
    return video


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
    if "# TODO" in plan_path.read_text(encoding="utf-8"):
        sys.exit(f"{plan_path}: finish its TODOs first (prompts/narration-rules.md)")
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    if plan["lang"] not in SOURCES:
        sys.exit(f"{plan_path}: lang must be one of {', '.join(SOURCES)}")
    voice, samples_for = plan["voice"], []
    if "--voice" in argv:
        voice = argv[argv.index("--voice") + 1]
    if "--sample" in argv:
        samples_for = argv[argv.index("--sample") + 1].split(",")
    shared = Path(SAY.format(plan["lang"]))
    say = {**(yaml.safe_load(shared.read_text(encoding="utf-8")) or {} if shared.exists() else {}),
           **(plan.get("say") or {})}

    if plan.get("biur"):
        return readalong(plan, plan_path, argv, voice, say, samples_for)
    sections = [] if plan.get("parts") else load_sections(Path(SOURCES[plan["lang"]]))
    blocks = build_blocks(plan, sections)
    out = OUT / plan_path.stem
    out.mkdir(parents=True, exist_ok=True)
    write_script(blocks, out / "script.txt")
    words = sum(len(b["text"].split()) for b in blocks)
    print(f"  {out / 'script.txt'}  ({words} words, about {words / 175:.0f} minutes)")
    if "--script" in argv:
        return
    if "--names" in argv:
        if plan["lang"] == "he":
            sys.exit("--names: Kokoro only (English, French); listen to a Hebrew --sample instead")
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
    if "--thumbnail" in argv:
        make_frame(plan, out)
        print(f"  {out / 'thumbnail.jpg'}")
        return
    if "--video" in argv:
        if not (out / "narration.wav").exists():
            sys.exit(f"{out / 'narration.wav'}: no reading yet; build without --video first")
        make_frame(plan, out)
        print(f"  {make_video(out)}")
        return

    if plan.get("parts") and not plan.get("approved") and not samples_for:
        sys.exit(f"{plan_path}: Ronnie has not approved its English yet (`approved: <date>` in the plan, "
                 f"prompts/render-english.md); --script, --frame and --sample work meanwhile")
    model = load_model(plan["lang"])
    if samples_for:
        first = next(i for i, b in enumerate(blocks) if b["chapter"])
        if plan["lang"] == "he":
            tts_budget(blocks[:first + 2], say)
        for v in samples_for:
            audio, rate, _ = synthesize(model, blocks[:first + 2], v, plan.get("speed", 1.0), say)
            print(f"  {write_audio(audio, rate, out / f'sample-{v}.wav')}")
        if plan["lang"] == "he":
            count_tts(model.sent)
        return

    if plan["lang"] == "he":
        print(f"  Google Text-to-Speech: {tts_budget(blocks, say):,} characters")
    audio, rate, cues = synthesize(model, blocks, voice, plan.get("speed", 1.0), say)
    if plan["lang"] == "he":
        count_tts(model.sent)
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


def readalong(plan: dict, plan_path: Path, argv: list[str], voice: str, say: dict, samples_for: list[str]) -> None:
    """A plan with `biur:`: the explanation read aloud, its words on a dark screen."""
    blocks = biur_blocks(plan)
    out = OUT / plan_path.stem
    out.mkdir(parents=True, exist_ok=True)
    lines = []
    for b in blocks:
        if b["kind"] == "heading":
            lines.append(f"# {b['text']}")
        else:
            lines.append(("NOTE: " if b["kind"] == "note" else "")
                         + textwrap.fill(b["text"], 90, break_on_hyphens=False))
    (out / "script.txt").write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    words = sum(len(b["text"].split()) for b in blocks)
    print(f"  {out / 'script.txt'}  ({words} words, {sum(1 for b in blocks if b['chapter'])} chapters, "
          f"about {words / 165 / plan.get('speed', 1.0):.0f} minutes)")
    if "--script" in argv:
        return
    if "--names" in argv:
        model, lang = load_model(), voice_lang(voice)
        names = sorted({w for b in blocks for w in re.findall(r"(?<![\w'’])[A-Z][\w'’‑-]*", b["text"])})
        # The italic words too: the Hebrew terms.
        italic = sorted({m.strip(" ,.;:“”") for b in blocks for m in
                         re.findall(r"\S+", "".join(c if s & 2 else " " for c, s in zip(b["text"], b["styles"])))})
        for w in sorted(set(names) | set(italic)):
            ph = model.tokenizer.phonemize(spoken(w, say, lang), lang)
            print(f"  {w:22} {spoken(w, say, lang):22} {ph}")
        return
    if "--frame" in argv or "--thumbnail" in argv:
        print(f"  {make_frame(plan, out)}")
        return
    model = load_model(plan["lang"])
    if samples_for:
        first = next(i for i, b in enumerate(blocks) if b["kind"] == "para")
        for v in samples_for:
            audio, rate, _ = synthesize_readalong(model, blocks[:first + 3], v, plan.get("speed", 1.0), say)
            print(f"  {write_audio(audio, rate, out / f'sample-{v}.wav')}")
        return
    if "--video" not in argv:
        audio, rate, cues = synthesize_readalong(model, blocks, voice, plan.get("speed", 1.0), say)
        print(f"  {write_audio(audio, rate, out / 'narration.wav')}  ({len(audio) / rate / 60:.1f} minutes, voice {voice})")
        import json
        (out / "cues.json").write_text(json.dumps({"cues": cues, "starts": [b.get("start") for b in blocks]}),
                                       encoding="utf-8")
    else:
        import json
        if not (out / "cues.json").exists():
            sys.exit(f"{out / 'cues.json'}: no reading yet; build without --video first")
        saved = json.loads((out / "cues.json").read_text(encoding="utf-8"))
        cues = [tuple(c) for c in saved["cues"]]
        for b, s in zip(blocks, saved["starts"]):
            b["start"] = s
    write_readalong(blocks, cues, out)
    print(f"  {out / 'narration.srt'}")
    chapters = [(b["start"], plain(b["chapter"])) for b in blocks if b["chapter"]]
    chapters[0] = (0.0, chapters[0][1])
    (out / "chapters.txt").write_text("".join(f"{stamp(t, srt=False)} {c}\n" for t, c in chapters), encoding="utf-8")
    print(f"  {out / 'chapters.txt'}")
    make_frame(plan, out)
    # The title card stays up while the opening words are read.
    title_until = next(c[0] for c in cues if blocks[c[2]]["kind"] != "title")
    if "--preview" in argv:          # a minute from where --preview says (seconds), to look at
        at = float(argv[argv.index("--preview") + 1])
        print(f"  {make_preview(out, at)}")
        return
    print(f"  {make_readalong_video(out, title_until)}")


def make_preview(out: Path, at: float) -> Path:
    """Stills of the read-along screen at a moment, without making the whole video."""
    bg = "0x%02X%02X%02X" % DARK_BG
    path = out / f"preview-{int(at)}.png"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    f"color=c={bg}:s={VIDEO[0]}x{VIDEO[1]}:r=10:d={at + 1}",
                    "-vf", f"ass={out / 'readalong.ass'}:fontsdir={FONTS}", "-ss", str(at), "-frames:v", "1",
                    str(path)], check=True)
    return path


if __name__ == "__main__":
    main(sys.argv[1:])
