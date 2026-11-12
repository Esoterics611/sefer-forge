"""Reference works kept in sources/ (Etz Chaim, Pri Etz Chaim, ...): loading,
addressing, citation parsing and loose phrase matching.

Used by scripts/source-lookup.py and scripts/build-references.py. The catalog
is sources/sources.yaml; each work is a Sefaria export JSON, kept unedited.

Addresses are Sefaria's: a dotted path into the work's text, e.g. "49.5.1" =
Etz Chaim gate 49, chapter 5, paragraph 1; "Gate of Prayer.7.3" for Pri Etz
Chaim. A paragraph is the unit Sefaria stores (often a whole chapter).
"""
from __future__ import annotations

import html
import json
import re
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "sources" / "sources.yaml"
NIQQUD = re.compile(r"[֑-ׇ]")
TAG = re.compile(r"<[^>]+>")
LETTER = re.compile(r"[א-ת]")
QUOTES = "\"'״׳"
VALUES = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90,
                                                 100, 200, 300, 400]))
VALUES.update({"ך": 20, "ם": 40, "ן": 50, "ף": 80, "ץ": 90})


@lru_cache(None)
def catalog() -> dict:
    return yaml.safe_load(CATALOG.read_text(encoding="utf-8"))["works"]


@lru_cache(None)
def load(work: str) -> dict:
    return json.loads((ROOT / catalog()[work]["file"]).read_text(encoding="utf-8"))


@lru_cache(None)
def paragraphs(work: str) -> dict[str, str]:
    """{address: raw paragraph} for one work, in book order."""
    data = load(work)
    out: dict[str, str] = {}

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, path + [k] if k else path)
        elif isinstance(node, list):
            for i, v in enumerate(node, 1):
                walk(v, path + [str(i)])
        elif isinstance(node, str) and node.strip():
            out[".".join(path)] = node

    walk(data["text"], [])
    return out


def clean(raw: str) -> str:
    """A paragraph as it reads: no HTML tags or entities, single spaces."""
    return re.sub(r"\s+", " ", html.unescape(TAG.sub(" ", raw))).strip()


def text(work: str, address: str) -> str:
    try:
        return clean(paragraphs(work)[address])
    except KeyError:
        raise KeyError(f"{work}: no paragraph {address}") from None


def under(work: str, prefix: str) -> list[tuple[str, str]]:
    """[(address, text)] of every paragraph at or under an address prefix."""
    return [(a, clean(t)) for a, t in paragraphs(work).items() if a == prefix or a.startswith(prefix + ".")]


# --- loose matching ---------------------------------------------------------
# Phrases from a plan are matched on letters only (no niqqud, quote marks or
# punctuation), so a phrase copied with slightly different punctuation still
# finds its place; the match is returned as offsets into the real text.

def letters(s: str) -> tuple[str, list[int]]:
    """(letters and single spaces, index in s of each kept character)."""
    out, idx = [], []
    for i, ch in enumerate(s):
        if ch == "ﬠ":                 # Hebrew letter alternative ayin (Sefaria's Tanya): read as ע
            ch = "ע"
        if LETTER.match(ch):
            out.append(ch)
            idx.append(i)
        elif ch in QUOTES or NIQQUD.match(ch):
            continue
        elif out and out[-1] != " ":
            out.append(" ")
            idx.append(i)
    return "".join(out), idx


def locate(s: str, phrase: str, start: int = 0) -> tuple[int, int] | None:
    """(start, end) in s of phrase's first loose match at or after start."""
    hay, idx = letters(s)
    needle = letters(phrase)[0].strip()
    if not needle:
        return None
    pos = 0
    while True:
        k = hay.find(needle, pos)
        if k < 0:
            return None
        before_ok = k == 0 or hay[k - 1] == " "
        end = k + len(needle)
        after_ok = end >= len(hay) or hay[end] == " "
        if idx[k] >= start and before_ok and after_ok:
            e = idx[end - 1] + 1
            while e < len(s) and s[e] in QUOTES:      # the ' of כו', בחי' belongs to the word
                e += 1
            return idx[k], e
        pos = k + 1


def find(work: str, phrase: str, prefix: str = "") -> list[tuple[str, int, int]]:
    """[(address, start, end)] of every loose match of phrase in the work."""
    hits = []
    for a, raw in paragraphs(work).items():
        if prefix and not (a == prefix or a.startswith(prefix + ".")):
            continue
        t = clean(raw)
        at = 0
        while (m := locate(t, phrase, at)) is not None:
            hits.append((a, *m))
            at = m[1]
    return hits


# --- citations ----------------------------------------------------------------

def numeral(s: str) -> int:
    """Hebrew letters → number (מ"ט → 49, י"ד → 14)."""
    return sum(VALUES.get(c, 0) for c in s if c not in QUOTES)


def work_of(token: str) -> str | None:
    t = token.replace("״", '"')
    for wid, entry in catalog().items():
        if t in entry.get("cite_as", []):
            return wid
    return None


def parse_cite(cite: str) -> tuple[str, str]:
    """'ע"ח שמ"ט פ"ה' → ('etz-chaim', '49.5'); 'פע"ח ש"א פ"ו' → ('pri-etz-chaim', 'Gate of Prayer.6').
    Gate and chapter as the citation writes them: an older edition's numbering
    can differ from Sefaria's (see the work's `numbering:` notes)."""
    tokens = cite.replace("״", '"').replace("׳", "'").split()
    if not tokens or not (wid := work_of(tokens[0])):
        raise ValueError(f"unknown work in {cite!r} (sources/sources.yaml cite_as)")
    gate = chapter = None
    rest = tokens[1:]
    i = 0
    while i < len(rest):
        tok = rest[i]
        if tok in ("שער", "ש'", "הקדמה") and i + 1 < len(rest):
            gate, i = numeral(rest[i + 1]), i + 2
            continue
        if tok in ("פרק", "דרוש", "פ'") and i + 1 < len(rest):
            chapter, i = numeral(rest[i + 1]), i + 2
            continue
        if gate is None and tok.startswith("ש") and len(tok) > 1:
            gate = numeral(tok[1:])
        elif tok.startswith(("ספ", "בס")) and len(tok) > 2:
            chapter = numeral(tok[2:])
        elif tok.startswith("פ") and len(tok) > 1:
            chapter = numeral(tok[1:])
        i += 1
    if gate is None:
        raise ValueError(f"no gate in {cite!r}")
    named = named_gates(wid)
    head = named[gate - 1] if named else str(gate)
    return wid, head if chapter is None else f"{head}.{chapter}"


def named_gates(work: str) -> list[str]:
    """Gate keys in order for a work whose gates are named (Pri Etz Chaim's
    "Gate of Prayer", ...); empty for a work whose gates are numbered."""
    if catalog()[work].get("gates") == "numbered":
        return []
    nodes = load(work).get("schema", {}).get("nodes", [])
    return [n["enTitle"] for n in nodes if n.get("enTitle")]


def gate_title(work: str, address: str) -> str:
    """The gate's Hebrew name for labels: the work's schema title for a named
    gate (Pri Etz Chaim), else the "שער ..." in the gate's opening line."""
    gate = address.split(".")[0]
    for node in load(work).get("schema", {}).get("nodes", []):
        if node.get("enTitle") == gate and node.get("heTitle"):
            return node["heTitle"]
    rows = under(work, gate)
    if not rows:
        return ""
    names = re.findall(r"(שער (?:(?!שער )[^:.])+?)\s+(?:ובו|ויתחלק|ונחלק)", rows[0][1])
    return names[-1] if names else ""


# --- printed pages --------------------------------------------------------------
# The Zohar's export marks the printed (Vilna) pages inside the text; Mikdash
# Melekh is arranged by them. pages() gives a printed page's text for either.

PAGE_MARK = re.compile(r'<i data-overlay="Vilna Pages" data-value="([0-9]+[ab])"></i>')
ZOHAR_VOLUMES = (("Shemot", 2), ("Vayikra", 3))      # the parashah that opens volumes 2 and 3


def page_rows(work: str, volume: int, page: str) -> list[tuple[str, str]]:
    """[(address, text)] of what stands on a printed page (e.g. volume 2, '229b').
    A paragraph that runs across pages is cut at the page marks."""
    data = load(work)["text"]
    if isinstance(data, list):                       # arranged by page: volume, page index, paragraph
        n = (int(page[:-1]) - 1) * 2 + (1 if page[-1] == "a" else 2)
        return under(work, f"{volume}.{n}")
    out, vol, cur = [], 1, None
    for key, chapters in data.items():
        vol = next((v for k, v in ZOHAR_VOLUMES if k == key), vol)
        if not isinstance(chapters, list):
            continue
        cur = None
        for ci, chapter in enumerate(chapters, 1):
            for pi, raw in enumerate(chapter if isinstance(chapter, list) else [chapter], 1):
                parts = PAGE_MARK.split(raw)
                for k, seg in enumerate(parts):
                    if k % 2:
                        cur = seg
                    elif vol == volume and cur == page and clean(seg):
                        out.append((f"{key}.{ci}.{pi}", clean(seg)))
    return out
