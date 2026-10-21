#!/usr/bin/env python3
"""Build a session's section.md from ocr.md, commentary.md and section-plan.yaml.

Usage:
    python scripts/build-section.py discourses/003-breishis/sessions/002 --init   # starter plan
    python scripts/build-section.py discourses/003-breishis/sessions/002          # build

The plan holds only the decisions; the text comes from the session's files,
so the נוסח is ocr.md word for word and the ביאור boxes are commentary.md
word for word, by construction:

    title: פרשת בראשית — ארץ קדמה לשמים          # frontmatter title
    heading: פָּרָשַׁת בְּרֵאשִׁית                   # bold line of the title block
    lines:                                       # subject lines under the ◆
      - אֶרֶץ קָדְמָה לְשָׁמַיִם
    nusach:
      start: והנה בבחי' זו        # first words of the printed range (default: OCR start)
      end: פנימית עתיק כנ"ל       # last words (default: OCR end)
      breaks:                     # extra paragraph starts, beyond the print's own
        - וצ"ל קדימת
      bold: [והנה, ובישר]         # bolded where they open a printed paragraph
    footnotes:                    # the print's notes, marked after their words
      - after: אותם בכח
        text: >-
          שו"ה אותם — בכח: נתקן ע"פ הערות ותיקונים
    keys:                         # 5–8, each quoting the נוסח verbatim
      - label: ארץ קדמה לשמים
        quote: ארץ הוא בחי' רצוא שבתפלה
    boxes:                        # one per topic, in order, covering every paragraph
      - label: ארץ ושמים — רצוא ושוב
        from: 1                   # commentary.md paragraph number, or its opening words

Write values unquoted: Hebrew's ' and " are fine in plain YAML. A value that
contains ": " or starts with a quote mark goes on its own line under `>-`,
as the footnote text above.

Range, breaks and quotes are matched word for word against the OCR,
ignoring punctuation and niqqud. A range that cuts into a sentence gets the
`...` snapshot marker; one that cuts between sentences does not. UNCLEAR flags travel with their words. ocr.md is
never changed: text outside the range stays there as the record.

Writes section.md with `built_from: section-plan.yaml` in its frontmatter,
and rebuilds such a file freely; a hand-made section.md is left alone unless
--force. Then refreshes review.md (transcript-diff.py) and runs
check-session.py on the session. --init writes a starter
plan (range from ocr-match.md when present, one box per paragraph) for the
decisions to be filled in.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import forgelib as F
import yaml

PLAN = "section-plan.yaml"
DESCRIPTOR = "נֹסַח עִקָּרִי עִם בֵּיאוּר וּפֵירוּשׁ"
SNAP = "..."


class PlanError(Exception):
    pass


# --- the OCR as tokens -----------------------------------------------------

def tokenize(paragraph: str) -> list[tuple[str, list[str]]]:
    """[(token text with any attached <!-- --> flag, its words)] for one OCR paragraph.
    A flag sticks to the word it touches (or, standing alone, to the word before
    it), so it moves with that word."""
    flags: list[str] = []

    def hold(m: re.Match) -> str:
        flags.append(m.group(0))
        return f"\x00{len(flags) - 1}\x00"

    raw = re.sub(r"<!--.*?-->", hold, paragraph, flags=re.S).split()
    toks: list[str] = []
    for r in raw:
        if re.fullmatch(r"\x00\d+\x00", r) and toks:
            toks[-1] += " " + r
        else:
            toks.append(r)
    restore = lambda s: re.sub(r"\x00(\d+)\x00", lambda m: flags[int(m.group(1))], s)
    return [(restore(x), F.words(restore(x))) for x in toks]


def ocr_tokens(session: Path) -> list[list[tuple[str, list[str]]]]:
    """ocr.md's paragraphs as token lists; the printed footnotes block is left out."""
    paras = []
    for p in F.ocr_paragraphs(session):
        if p.startswith("[Footnotes:]"):
            break
        paras.append(tokenize(p))
    return paras


def flat_words(paras) -> tuple[list[str], list[tuple[int, int]]]:
    """All words in order, with (paragraph, token) for each."""
    words, where = [], []
    for pi, toks in enumerate(paras):
        for ti, (_, ws) in enumerate(toks):
            for w in ws:
                words.append(w)
                where.append((pi, ti))
    return words, where


def locate(words: list[str], phrase: str, what: str, lo: int = 0, hi: int | None = None) -> int:
    """Word index where phrase occurs (exactly once) in words[lo:hi]."""
    target = F.words(phrase)
    if not target:
        raise PlanError(f"{what}: “{phrase}” has no words")
    hi = len(words) if hi is None else hi
    hits = [i for i in range(lo, hi - len(target) + 1) if words[i:i + len(target)] == target]
    if not hits:
        raise PlanError(f"{what}: “{phrase}” is not in the OCR text, word for word")
    if len(hits) > 1:
        raise PlanError(f"{what}: “{phrase}” occurs {len(hits)} times; give more words")
    return hits[0]


# --- building ----------------------------------------------------------------

def span(text: str) -> str:
    return f"[{text}]{{dir=\"rtl\"}}"


def nusach_paragraphs(plan: dict, session: Path) -> tuple[list[str], list[str]]:
    """The printed range as markdown paragraphs, and its words (for the key quotes)."""
    paras = ocr_tokens(session)
    words, where = flat_words(paras)
    if not words:
        raise PlanError("ocr.md has no text")
    n = plan.get("nusach") or {}
    a = locate(words, n["start"], "nusach.start") if n.get("start") else 0
    if n.get("end"):
        e = locate(words, n["end"], "nusach.end", lo=a)
        b = e + len(F.words(n["end"])) - 1
    else:
        b = len(words) - 1
    (pa, ta), (pb, tb) = where[a], where[b]

    # The range as (paragraph, token) runs, split again at the plan's breaks.
    marks: dict[tuple[int, int], str] = {}
    notes = []
    for k, fn in enumerate(plan.get("footnotes") or [], 1):
        i = locate(words, fn["after"], "footnotes.after", lo=a, hi=b + 1)
        j = i + len(F.words(fn["after"])) - 1
        label = f"{session.name}-{k}"
        marks[where[j]] = marks.get(where[j], "") + f"[^{label}]"
        text = fn["text"].replace("[", "\\[").replace("]", "\\]")
        notes.append(f"[^{label}]: {span(text)}")
    starts = set()
    for br in n.get("breaks") or []:
        i = locate(words, br, "nusach.breaks", lo=a, hi=b + 1)
        starts.add(where[i])
    out_paras: list[list[str]] = []
    printed: list[bool] = []               # does this paragraph open a printed paragraph?
    for pi in range(pa, pb + 1):
        toks = paras[pi]
        t0 = ta if pi == pa else 0
        t1 = tb if pi == pb else len(toks) - 1
        cur: list[str] = []
        printed.append(t0 == 0)
        for ti in range(t0, t1 + 1):
            if (pi, ti) in starts and cur:
                out_paras.append(cur)
                printed.append(False)
                cur = []
            cur.append(toks[ti][0] + marks.get((pi, ti), ""))
        out_paras.append(cur)
    # A range that cuts into a printed sentence is marked like a photo's edge;
    # one that cuts between sentences leaves a whole text and needs no mark.
    def ends_sentence(tok: str) -> bool:
        return F.COMMENT.sub("", tok).rstrip().endswith((".", ":", "?"))

    if ta > 0 and not ends_sentence(paras[pa][ta - 1][0]) and not out_paras[0][0].startswith(SNAP):
        out_paras[0][0] = SNAP + out_paras[0][0]
    if tb < len(paras[pb]) - 1 and not ends_sentence(paras[pb][tb][0]) and not out_paras[-1][-1].endswith(SNAP):
        out_paras[-1][-1] += SNAP

    bold = [F.words(x) for x in (n.get("bold") or [])]
    md = []
    for toks, opens in zip(out_paras, printed):
        for bw in (bold if opens else []):
            k = len(bw)
            head = [w for t in toks[:k] for w in F.words(t)]
            if head[:k] == bw and len(head) >= k:
                lead = SNAP if toks[0].startswith(SNAP) else ""
                toks = [f"{lead}**{toks[0][len(lead):]}"] + toks[1:]
                toks[k - 1] = toks[k - 1] + "**"
                break
        md.append(span(" ".join(toks)))
    return md + notes, words[a:b + 1]


def key_points(plan: dict, nusach_words: list[str], nusach_md: list[str]) -> list[str]:
    keys = plan.get("keys") or []
    body = [p for p in nusach_md if not p.startswith("[^")]          # notes are not quotable
    tokens = [t for p in body for t in re.sub(r'^\[|\]\{dir="rtl"\}$', "", p).split(" ")]
    tok_words = [(t, F.words(t)) for t in tokens]
    flat, owner = [], []
    for i, (_, ws) in enumerate(tok_words):
        for w in ws:
            flat.append(w)
            owner.append(i)
    out = []
    for k in keys:
        if not k.get("label") or not k.get("quote"):
            raise PlanError(f"keys: each needs a label and a quote ({k})")
        i = locate(flat, k["quote"], f"keys “{k['label']}”")
        j = i + len(F.words(k["quote"])) - 1
        quote = " ".join(tokens[owner[i]:owner[j] + 1])
        quote = F.COMMENT.sub("", quote).replace("**", "").strip().rstrip(".,:;")
        quote = quote.strip(SNAP + " ") if quote.startswith(SNAP) or quote.endswith(SNAP) else quote
        out += [f"**{span(k['label'])}**", "", f"> {span(quote)}", ""]
    return out


def commentary_paragraphs(session: Path) -> list[str]:
    f = session / "commentary.md"
    if not f.exists():
        raise PlanError("no commentary.md yet")
    _, body, err = F.split_frontmatter(f.read_text(encoding="utf-8"))
    if err:
        raise PlanError(f"commentary.md frontmatter: {err}")
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", body) if p.strip()]


def boxes(plan: dict, session: Path) -> list[str]:
    paras = commentary_paragraphs(session)
    spec = plan.get("boxes") or []
    if not spec:
        raise PlanError("boxes: none planned")
    starts = []
    for b in spec:
        f = b.get("from")
        if isinstance(f, int):
            if not 1 <= f <= len(paras):
                raise PlanError(f"boxes “{b.get('label')}”: paragraph {f} — commentary.md has {len(paras)}")
            starts.append(f - 1)
        else:
            want = F.words(str(f))
            hits = [i for i, p in enumerate(paras) if F.words(p)[:len(want)] == want]
            if len(hits) != 1:
                raise PlanError(f"boxes “{b.get('label')}”: {len(hits)} paragraphs open with “{f}”")
            starts.append(hits[0])
    if starts[0] != 0:
        raise PlanError(f"boxes: paragraphs 1–{starts[0]} of commentary.md are in no box")
    if starts != sorted(set(starts)):
        raise PlanError("boxes: starting paragraphs must rise, one box each")
    out = []
    for n, (b, s) in enumerate(zip(spec, starts)):
        e = starts[n + 1] if n + 1 < len(starts) else len(paras)
        out += ['::: {custom-style="Commentary"}', f"**{span('■ ביאור — ' + b['label'])}**", ""]
        for p in paras[s:e]:
            out += [span(p), ""]
        out[-1] = ":::"
        out.append("")
    return out


def build(session: Path, plan: dict) -> str:
    fm = {"session": session.name, "discourse": F.discourse_of(session).name,
          "title": plan.get("title") or "", "built_from": PLAN}
    head = ["---", yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip(), "---", ""]
    if plan.get("heading"):
        head += [f"**{span(plan['heading'])}**", "", "--------- ◆ ---------", ""]
    for ln in plan.get("lines") or []:
        head += [span(ln), ""]
    version = plan.get("version") or "גִּרְסָה א'"
    head += [span(DESCRIPTOR), "", f"*{span(f'{version} · סֶשְׁן {session.name} · עִם בֵּיאוּר הַקּוֹל')}*", "", "---", ""]

    nusach_md, nusach_words = nusach_paragraphs(plan, session)
    body = ["## הַנֹּסַח הָעִקָּרִי", ""]
    for p in nusach_md:
        body += [p, ""]
    body += ["---", "", "## נְקֻדּוֹת מַפְתֵּחַ", ""]
    body += key_points(plan, nusach_words, nusach_md)
    body += ["---", "", "## בֵּיאוּר וּפֵירוּשׁ", ""]
    body += boxes(plan, session)
    return "\n".join(head + body).rstrip() + "\n"


# --- a starter plan ----------------------------------------------------------

def yval(s: str | None) -> str:
    """A YAML value written plainly when that is safe, as the plan's docs ask."""
    if s is None:
        return "null"
    s = str(s)
    if s and ": " not in s and " #" not in s and s[0] not in "'\"[]{}&*!|>%@`-?,:#" and s == s.strip():
        return s
    return yaml.safe_dump(s, allow_unicode=True, width=1000).splitlines()[0]


def init(session: Path) -> int:
    target = session / PLAN
    if target.exists():
        print(f"{target} exists; edit it")
        return 1
    start = end = None
    m = session / "ocr-match.md"
    if m.exists():
        t = m.read_text(encoding="utf-8")
        if s := re.search(r"\*\*Starts\*\*.*?: “(.+?)…”", t):
            start = " ".join(s.group(1).split()[:5])
        if e := re.search(r"\*\*Ends\*\*.*?: “…(.+?)”", t):
            end = " ".join(e.group(1).split()[-5:])
    try:
        paras = commentary_paragraphs(session)
    except PlanError:
        paras = []
    sec = session / "section.md"
    title = ""
    if sec.exists():
        fm, _, _ = F.split_frontmatter(sec.read_text(encoding="utf-8"))
        title = (fm or {}).get("title", "")
    lines = [
        "# Decisions for section.md. Text comes from ocr.md and commentary.md;",
        "# rebuild with: python scripts/build-section.py " + str(session),
        f"title: {yval(title) if title else chr(39) * 2}",
        "heading: ''",
        "lines: []",
        "nusach:",
        f"  start: {yval(start)}",
        f"  end: {yval(end)}",
        "  breaks: []",
        "  bold: [והנה]",
        "keys: []",
        "boxes:",
    ]
    for i, p in enumerate(paras, 1):
        opening = " ".join(F.strip_marks(F.COMMENT.sub("", p)).split()[:6])
        lines += [f"  - label: TODO   # {i}: {opening}…", f"    from: {i}"]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {target}: fill in the title, heading, lines, breaks, keys and box labels; "
          "merge boxes by deleting entries")
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print("Usage: python scripts/build-section.py <session-path> [--init | --force]")
        return 1
    session = Path(args[0].rstrip("/"))
    if "--init" in argv:
        return init(session)
    plan_file = session / PLAN
    if not plan_file.exists():
        print(f"No {plan_file}: start one with --init")
        return 1
    try:
        plan = yaml.safe_load(plan_file.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"{plan_file} is not valid YAML — {str(e).splitlines()[-1].strip()}\n"
              "Hint: write values unquoted; one containing \": \" or starting with a quote mark "
              "goes on the next line under `key: >-`.")
        return 1
    target = session / "section.md"
    if target.exists() and "--force" not in argv:
        fm, _, _ = F.split_frontmatter(target.read_text(encoding="utf-8"))
        if (fm or {}).get("built_from") != PLAN:
            print(f"{target} was not built from {PLAN} (hand-made); pass --force to replace it")
            return 2
    try:
        text = build(session, plan)
    except PlanError as e:
        print(f"Plan problem — {e}")
        return 1
    target.write_text(text, encoding="utf-8")
    print(f"Wrote {target}", flush=True)
    # review.md records the box check too: refresh it, then check the session.
    here = Path(__file__).parent
    subprocess.call([sys.executable, str(here / "transcript-diff.py"), str(session)], stdout=subprocess.DEVNULL)
    return subprocess.call([sys.executable, str(here / "check-session.py"), str(session)])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
