"""Shared helpers for the session scripts (session-status, check-session,
ocr-match, build-section, ocr-strips, glossary-candidates).

Run the scripts from the repo root (`python scripts/<name>.py ...`); Python
puts scripts/ on the path, so `import forgelib` works from each of them.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install -r requirements.txt")
    sys.exit(1)

DISCOURSES = Path("discourses")
AUDIO_EXTS = {".m4a", ".mp3", ".wav", ".ogg", ".flac", ".aac"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".webp"}

NIQQUD = re.compile(r"[֑-ׇ]")
BIDI_MARKS = re.compile("[‎‏‪-‮⁦-⁩]")
COMMENT = re.compile(r"<!--.*?-->", re.S)
FRONTMATTER = re.compile(r"\A---\n([\s\S]*?)\n---[ \t]*\n?")
FINALS = str.maketrans("ךםןףץ", "כמנפצ")
QUOTES = "\"'״׳“”„‘’`"
PUNCT = "[]{}()*>_:;,.!?|…—–-" + QUOTES
PREFIXES = "ושהבכלמד"
HEB = "א-ת"


# --- sessions --------------------------------------------------------------

def load_script(name: str):
    """Import a hyphenated script from scripts/ as a module (e.g. transcript-diff)."""
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod              # dataclasses look their module up here
    spec.loader.exec_module(mod)
    return mod


def is_session(p: Path) -> bool:
    return p.is_dir() and p.parent.name == "sessions" and p.name.isdigit()


def discourse_of(session: Path) -> Path:
    return session.parent.parent


def meta(discourse: Path) -> dict:
    f = discourse / "meta.yaml"
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


def voice_only(session: Path) -> bool:
    return meta(discourse_of(session)).get("type") == "voice-only"


def find_discourse(name: str) -> Path | None:
    p = Path(name)
    if p.is_dir() and (p / "sessions").is_dir():
        return p
    hits = sorted(DISCOURSES.glob(f"*-{name}")) or sorted(DISCOURSES.glob(f"*{name}*"))
    return hits[0] if hits else None


def sessions_of(discourse: Path) -> list[Path]:
    d = discourse / "sessions"
    return sorted(p for p in d.iterdir() if is_session(p)) if d.is_dir() else []


def resolve_sessions(args: list[str]) -> list[Path]:
    """Session paths, discourse paths/slugs, or nothing (= every session)."""
    if not args:
        return [s for d in sorted(DISCOURSES.glob("[0-9]*-*")) for s in sessions_of(d)]
    out: list[Path] = []
    for a in args:
        p = Path(a.rstrip("/"))
        if is_session(p):
            out.append(p)
        elif (d := find_discourse(a.rstrip("/"))) is not None:
            out += sessions_of(d)
        else:
            sys.exit(f"Not a session or discourse: {a}")
    return out


def audio_files(session: Path) -> list[Path]:
    d = session / "voicenotes"
    return sorted(p for p in d.iterdir() if p.suffix.lower() in AUDIO_EXTS) if d.is_dir() else []


def image_files(session: Path) -> list[Path]:
    d = session / "images"
    return sorted(p for p in d.iterdir() if p.suffix.lower() in IMAGE_EXTS) if d.is_dir() else []


def sidecar(audio: Path, kind: str) -> Path:
    """<audio>.raw.txt, <audio>.timed.txt, <audio>.fixed.txt, <audio>.partial.txt, <audio>.lock"""
    return audio.with_name(f"{audio.name}.{kind}")


# --- markdown --------------------------------------------------------------

def split_frontmatter(text: str) -> tuple[dict | None, str, str | None]:
    """(frontmatter or None, body, YAML error or None)."""
    m = FRONTMATTER.match(text)
    if not m:
        return None, text, None
    try:
        return (yaml.safe_load(m.group(1)) or {}), text[m.end():], None
    except yaml.YAMLError as e:
        return None, text[m.end():], str(e).replace("\n", " ")


def ocr_body(session: Path) -> str:
    """ocr.md without frontmatter, image headings and comments: the printed text only."""
    f = session / "ocr.md"
    if not f.exists():
        return ""
    _, body, _ = split_frontmatter(f.read_text(encoding="utf-8"))
    body = re.sub(r"^## Image:.*$", "", body, flags=re.M)
    return COMMENT.sub(" ", body)


def ocr_paragraphs(session: Path, notes: bool = True) -> list[str]:
    """ocr.md's paragraphs, flags kept, image headings and the photo notes dropped.
    notes=False leaves out each photo's printed footnotes too (its `[Footnotes:]`
    block, up to the next photo): the text as it reads, across photos, where a
    paragraph a photo leaves mid-sentence goes on in the next photo's first."""
    _, body, _ = split_frontmatter((session / "ocr.md").read_text(encoding="utf-8"))
    paras, in_notes, new_photo = [], False, False
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if block.startswith("## Image:"):
            in_notes, new_photo = False, bool(paras)
        if block.startswith("[Footnotes:]"):
            in_notes = True
        if not block or block.startswith("## Image:") or (in_notes and not notes):
            continue
        if re.fullmatch(r"<!--.*?-->", block, flags=re.S):    # a note about the photo, not text
            continue
        text = " ".join(block.split())
        if new_photo and not notes and not re.search(r"[.:?!][\"'״׳)\]]*$", COMMENT.sub("", paras[-1]).strip()):
            paras[-1] += " " + text
        else:
            paras.append(text)
        new_photo = False
    return paras


def printed(paragraph: str) -> str:
    """An OCR paragraph as the נוסח prints it: without a reader's hand underlines,
    the print's note numbers (^15^) and its bold (the plan's `bold:` and
    `footnotes:` set those)."""
    p = re.sub(r"\[([^\]]*)\]\{\.underline\}", r"\1", paragraph)
    p = re.sub(r"\^\d+\^", "", p)
    return p.replace("**", "")


def ocr_text(session: Path) -> str:
    """The printed text of ocr.md (F.printed), footnotes and comments left out, across photos."""
    return COMMENT.sub(" ", "\n\n".join(printed(p) for p in ocr_paragraphs(session, notes=False)))


# --- words -----------------------------------------------------------------

def strip_marks(text: str) -> str:
    return BIDI_MARKS.sub("", NIQQUD.sub("", text))


def words(text: str) -> list[str]:
    """Words of a markdown text as transcript-diff.py counts them: no frontmatter,
    comments, footnotes, headings, {attributes}, niqqud or punctuation."""
    text = FRONTMATTER.sub("", text, count=1)
    text = COMMENT.sub(" ", text)
    text = re.sub(r"^\[\^[^\]]+\]:.*$", " ", text, flags=re.M)
    text = re.sub(r"\[\^[^\]]+\]", " ", text)
    text = re.sub(r"^#+ .*$", " ", text, flags=re.M)
    text = re.sub(r"\{[^}]*\}", " ", text)
    text = strip_marks(text)
    return [w for w in (t.strip(PUNCT) for t in text.split()) if w]


def is_abbrev(token: str) -> bool:
    """ע"י, כו', בחי' — a quote mark inside or at the end of a Hebrew word."""
    t = strip_marks(token).strip("[](){}.,:;!?*")
    return bool(re.search(rf"[{HEB}][\"'״׳]", t))


def plain(token: str) -> str:
    """Letters only: niqqud, quote marks and punctuation removed."""
    t = strip_marks(token)
    return "".join(ch for ch in t if "א" <= ch <= "ת")


def skeleton(token: str) -> str:
    """Spelling-blind key: letters only, final forms folded, and ו/י dropped after
    the first letter, so חכמה = חוכמה and תפלה = תפילה."""
    t = plain(token).translate(FINALS)
    if not t:
        return ""
    t = t[0] + re.sub("[וי]", "", t[1:])
    if t.startswith("אלה"):                # אלהים / אלקים, as the speaker says it
        t = "אלק" + t[3:]
    return t


# --- abbreviations ---------------------------------------------------------

_ABBREV: dict[str, list[list[str]]] | None = None


def abbreviations() -> dict[str, list[list[str]]]:
    """glossary/abbreviations.yaml as {plain key: [[skeleton words], ...]}."""
    global _ABBREV
    if _ABBREV is None:
        f = Path("glossary/abbreviations.yaml")
        data = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}
        _ABBREV = {}
        for k, exps in data.items():
            _ABBREV[plain(k).translate(FINALS)] = [[skeleton(w) for w in e.split()] for e in exps]
    return _ABBREV


def expansions(token: str) -> list[list[str]]:
    """Spoken forms of an abbreviation, as skeleton word lists, prefix letters
    carried onto the first word: וכמ"ש → [[וכמ, שכתב], ...]."""
    key = plain(token).translate(FINALS)
    table = abbreviations()
    for cut in range(0, 3):
        pre, base = key[:cut], key[cut:]
        if any(c not in PREFIXES for c in pre):
            break
        if base in table:
            return [[skeleton(pre + e[0])] + e[1:] for e in table[base]]
    return []


def _initials_fit(letters: str, heard: list[str]) -> bool:
    """Do the spoken words fit the abbreviation's letters? Each word must begin
    (after optional prefix letters) with the next letter, and may also use up
    following letters that continue it: כמ"ש = כמו שכתוב, ואח"כ = ואחר כך."""
    p = 0
    for i, w in enumerate(heard):
        w = plain(w).translate(FINALS)
        if not w or p >= len(letters):
            return False
        j = 0
        while j < len(w) - 1 and w[j] != letters[p] and w[j] in PREFIXES and j < 2:
            j += 1
        if w[j] != letters[p]:
            return False
        p += 1
        j += 1
        while p < len(letters) and j < len(w) and w[j] == letters[p]:
            p += 1
            j += 1
    return p == len(letters)


def abbrev_match(token: str, heard: list[str]) -> int:
    """How many of the heard words (1–4) an abbreviation accounts for; 0 = none."""
    sk = [skeleton(w) for w in heard]
    for exp in expansions(token):
        if sk[:len(exp)] == exp:
            return len(exp)
    letters = plain(token).translate(FINALS)
    if not letters:
        return 0
    if strip_marks(token).rstrip(".,:;").endswith(("'", "׳")):      # truncation: בחי' → בחינת
        stem = skeleton(token)
        if not sk or not stem:
            return 0
        # The speaker may add or drop a prefix letter: השתל' → ההשתלשלות.
        for a in range(0, 3):
            for b in range(0, 3):
                s, h = stem[a:], sk[0][b:]
                if (len(s) >= 2 or a == 0) and s and h.startswith(s) and all(c in PREFIXES for c in stem[:a] + sk[0][:b]):
                    return 1
        return 0
    for n in range(1, min(4, len(heard)) + 1):                      # acronym: ע"י → על ידי
        if _initials_fit(letters, heard[:n]):
            return n
    return 0


# --- the voicenote ---------------------------------------------------------

def stamp(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def parse_stamp(s: str) -> int:
    parts = [int(x) for x in s.split(":")]
    return parts[0] * 60 + parts[1] if len(parts) == 2 else parts[0] * 3600 + parts[1] * 60 + parts[2]


def timed_words(session: Path) -> list[tuple[str, str]]:
    """Every Whisper word of the session's voicenotes with the start time of its
    .timed.txt line ("04:12", or "2·04:12" in a session's second voicenote),
    the glossary's auto fixes applied as in .fixed.txt."""
    fixes = load_script("apply-fixes")
    auto, _ = fixes.load_fixes(session)
    out: list[tuple[str, str]] = []
    audios = [a for a in audio_files(session) if sidecar(a, "timed.txt").exists()]
    for n, audio in enumerate(audios, 1):
        for line in sidecar(audio, "timed.txt").read_text(encoding="utf-8").splitlines():
            m = re.match(r"\[(\d+:\d+(?::\d+)?)\]\s*(.*)", line)
            if not m:
                continue
            when = m.group(1) if len(audios) == 1 else f"{n}·{m.group(1)}"
            text, _ = fixes.apply_auto(strip_marks(m.group(2)), auto)
            out += [(w, when) for w in text.split() if w.strip(PUNCT)]
    return out


# --- transcription in progress ------------------------------------------------

def _alive(pid: int) -> bool:
    return pid > 0 and Path(f"/proc/{pid}").exists()


def _proc_started(pid: int) -> float | None:
    """Epoch seconds a process started (Linux /proc), or None."""
    try:
        ticks = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])
        btime = next(int(l.split()[1]) for l in Path("/proc/stat").read_text().splitlines()
                     if l.startswith("btime"))
        import os
        return btime + ticks / os.sysconf("SC_CLK_TCK")
    except (OSError, ValueError, StopIteration, IndexError):
        return None


def _old_style_run(session: Path) -> int | None:
    """A transcribe.py process for this session that predates lock files."""
    for proc in Path("/proc").glob("[0-9]*"):
        try:
            cmd = (proc / "cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        args = [c.decode("utf-8", "replace") for c in cmd if c]
        if any(a.endswith("transcribe.py") for a in args) and \
                any(a.rstrip("/") == str(session) for a in args):
            return int(proc.name)
    return None


def audio_seconds(audio: Path) -> float | None:
    """The recording's length, by ffprobe when it is installed."""
    import shutil
    import subprocess
    if not shutil.which("ffprobe"):
        return None
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        str(audio)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return None


def transcription(audio: Path, session: Path) -> dict:
    """{"state": done|running|interrupted|none, "at": seconds heard, "of": length,
    "started": epoch, "pid": pid, "device": where Whisper runs} for one recording."""
    if sidecar(audio, "raw.txt").exists():
        return {"state": "done"}
    info: dict = {"state": "none"}
    partial, lock = sidecar(audio, "partial.txt"), sidecar(audio, "lock")
    if partial.exists():
        lines = [l for l in partial.read_text(encoding="utf-8").splitlines() if l.count("\t") >= 2]
        info["at"] = float(lines[-1].split("\t")[1]) if lines else 0.0
        info["state"] = "interrupted"
    if lock.exists():
        fields = dict(l.split(":", 1) for l in lock.read_text(encoding="utf-8").splitlines() if ":" in l)
        pid = int(fields.get("pid", "0").strip() or 0)
        info["of"] = float(fields.get("duration", "0") or 0)
        info["device"] = fields.get("device", "cpu int8").strip()
        if _alive(pid):
            info.update(state="running", pid=pid, started=_proc_started(pid))
    if info["state"] != "running" and (pid := _old_style_run(session)):
        info.update(state="running", pid=pid, started=_proc_started(pid))
        info.setdefault("of", audio_seconds(audio))
    return info


# --- print edits: the readability pass (`edits:`) and the style pass (`style:`) ----------

class EditError(Exception):
    pass


def edit_pattern(src: str) -> re.Pattern:
    """`src` as written in the plan, matched in a paragraph that may carry
    <!-- --> flags between or right after its words (a flag on edited words
    goes with them)."""
    flag = r"(?:\s*<!--(?:(?!-->).)*-->)?"           # one comment: never runs past its own end
    toks = []
    for tok in src.split():
        m = re.match(r"(.*?)([,.:;?!]*)$", tok)          # a flag may sit before trailing punctuation
        core, punct = m.group(1), m.group(2)
        toks.append(re.escape(core) + (flag + re.escape(punct) if punct else ""))
    return re.compile((flag + r"\s+").join(toks) + flag, re.S)


def apply_edits(paras: list[str], edits: list[dict], where: str = "commentary.md") -> tuple[list[str], int]:
    """The readability pass (prompts/readability-pass.md): each edit replaces
    one exact stretch of the explanation (`from`) with `to` (empty: removed).
    Every `from` must occur exactly once. Returns the edited paragraphs and the
    number of edits applied."""
    out = list(paras)
    for e in edits or []:
        src, dst = str(e.get("from") or "").strip(), str(e.get("to") or "").strip()
        if not src:
            raise EditError(f"edit with no `from`: {e}")
        pat = edit_pattern(src)
        hits = [(i, m) for i, p in enumerate(out) for m in pat.finditer(p)]
        if len(hits) != 1:
            raise EditError(f"edit “{src}” matches {len(hits)} places in {where}; it must match one")
        i, m = hits[0]
        p = out[i][:m.start()] + dst + out[i][m.end():]
        out[i] = re.sub(r"[ \t]+([,.:;?!])", r"\1", re.sub(r"[ \t]{2,}", " ", p)).strip()
        out[i] = re.sub(r"^[,;:]\s*", "", out[i])
    return [p for p in out if p], len(edits or [])


def edit_transcript(body: str, edits: list[dict]) -> tuple[str, int]:
    """A voice-only transcript's body with its print edits (the frontmatter's
    `edits:` and `style:`, F.print_edits) applied block by block: what prints. The
    transcript itself keeps what Whisper heard."""
    blocks, n = apply_edits(re.split(r"\n\s*\n", body.strip()), edits, "transcript.md")
    return "\n\n".join(blocks) + "\n", n


def print_edits(d: dict | None) -> list[dict]:
    """The edits that print, in order: the readability pass (`edits:`,
    prompts/readability-pass.md), then the style pass (`style:`,
    prompts/style-pass.md), whose `from` is the text after the first."""
    d = d or {}
    return list(d.get("edits") or []) + list(d.get("style") or [])


def edit_counts(d: dict | None) -> str:
    """'N readability edit(s)', plus ', M style edit(s)' when there are any."""
    d = d or {}
    n, m = len(d.get("edits") or []), len(d.get("style") or [])
    return f"{n} readability edit(s)" + (f", {m} style edit(s)" if m else "")


def load_yaml(f: Path) -> dict:
    """A YAML file as a dict; {} when it is missing or empty."""
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


def plan_edits(session: Path) -> list[dict]:
    f = session / "section-plan.yaml"
    if not f.exists():
        return []
    return print_edits(yaml.safe_load(f.read_text(encoding="utf-8")))
