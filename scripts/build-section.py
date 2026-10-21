#!/usr/bin/env python3
"""Build a session's section.md from ocr.md, commentary.md and section-plan.yaml.

Usage:
    python scripts/build-section.py discourses/003-breishis/sessions/002 --init   # starter plan
    python scripts/build-section.py discourses/003-breishis/sessions/002          # build

The layout pairs the text with its explanation (docs/print-standard.md): the
session's נוסח is cut where the speaker reads, and each cut is followed by
what he says about it, so a reader always has the passage and its
explanation together. The pairing is found, not chosen: commentary.md is lined
up against the OCR (scripts/ocr-match.py's reading finder), every
explanation paragraph is anchored to the furthest OCR word read by its end,
and a new pair starts wherever the reading moves on. Explanation before the
first reading joins the first pair; text after the last reading closes the
section on its own.

The plan holds only the decisions; the text comes from the session's files,
so the נוסח is ocr.md word for word and the explanation is commentary.md word
for word, by construction:

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
    edits:                        # the readability pass (prompts/readability-pass.md)
      - from: נשע בהמית           # exact words of commentary.md, found once
        to: נפש הבהמית            # empty: the words are removed
        why: Whisper; the term is plain from the context

Write values unquoted: Hebrew's ' and " are fine in plain YAML. A value that
contains ": " or starts with a quote mark goes on its own line under `>-`,
as the footnote text above.

commentary.md stays the faithful transcript; the plan's `edits` (a short garbled
segment corrected or removed, each with its reason) apply on the way into
section.md, and the checks compare the explanation with commentary.md plus them.

section.md:  title block · "## הַנֹּסַח וְהַבֵּיאוּר" as pairs of
::: {custom-style="Nusach"} (a cut of the text) and ::: {custom-style="Commentary"}
(its explanation, unboxed) · the print's notes · "## נְקֻדּוֹת מַפְתֵּחַ".

Range, breaks and quotes are matched word for word against the OCR,
ignoring punctuation and niqqud. A range that cuts into a sentence gets the
`...` snapshot marker; one that cuts between sentences does not. UNCLEAR
flags travel with their words. ocr.md is never changed: text outside the
range stays there as the record.

Writes section.md with `built_from: section-plan.yaml` in its frontmatter,
and rebuilds such a file freely; a hand-made section.md is left alone unless
--force. Then refreshes review.md (transcript-diff.py) and runs
check-session.py on the session. --init writes a starter plan (range from
ocr-match.md when present).
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import forgelib as F
import yaml

OM = F.load_script("ocr-match")

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


class Nusach:
    """The printed range as a flat run of tokens, each knowing whether it opens a
    paragraph (and whether the print opened it), plus the range's words."""

    def __init__(self, plan: dict, session: Path):
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

        marks: dict[tuple[int, int], str] = {}
        self.notes: list[str] = []
        for k, fn in enumerate(plan.get("footnotes") or [], 1):
            i = locate(words, fn["after"], "footnotes.after", lo=a, hi=b + 1)
            j = i + len(F.words(fn["after"])) - 1
            label = f"{session.name}-{k}"
            marks[where[j]] = marks.get(where[j], "") + f"[^{label}]"
            text = fn["text"].replace("[", "\\[").replace("]", "\\]")
            self.notes.append(f"[^{label}]: {span(text)}")
        breaks = {where[locate(words, br, "nusach.breaks", lo=a, hi=b + 1)] for br in n.get("breaks") or []}

        # tokens: [text, para_start, printed_start]
        self.tokens: list[list] = []
        self.word_tok: list[int] = []          # range word index -> token index
        for pi in range(pa, pb + 1):
            toks = paras[pi]
            t0 = ta if pi == pa else 0
            t1 = tb if pi == pb else len(toks) - 1
            for ti in range(t0, t1 + 1):
                text, ws = toks[ti]
                first = ti == t0
                self.tokens.append([text + marks.get((pi, ti), ""), first or (pi, ti) in breaks,
                                    first and t0 == 0])
                self.word_tok += [len(self.tokens) - 1] * len(ws)
        self.words = words[a:b + 1]

        # A range that cuts into a printed sentence is marked like a photo's edge;
        # one that cuts between sentences leaves a whole text and needs no mark.
        def ends_sentence(tok: str) -> bool:
            return F.COMMENT.sub("", tok).rstrip().endswith((".", ":", "?"))

        if ta > 0 and not ends_sentence(paras[pa][ta - 1][0]) and not self.tokens[0][0].startswith(SNAP):
            self.tokens[0][0] = SNAP + self.tokens[0][0]
        if tb < len(paras[pb]) - 1 and not ends_sentence(paras[pb][tb][0]) and not self.tokens[-1][0].endswith(SNAP):
            self.tokens[-1][0] += SNAP
        self.bold = [F.words(x) for x in (n.get("bold") or [])]

    def markdown(self, t0: int, t1: int) -> list[str]:
        """Tokens t0..t1 as RTL paragraphs; the first always opens a paragraph."""
        paras: list[tuple[list[str], bool, bool]] = []
        for i in range(t0, t1 + 1):
            text, para_start, printed = self.tokens[i]
            if para_start or i == t0:
                # A cut that begins inside a paragraph continues it (.cont): the
                # pamphlet rejoins the two when they share a page.
                paras.append(([], printed, not para_start))
            paras[-1][0].append(text)
        out = []
        for toks, printed, cont in paras:
            for bw in (self.bold if printed else []):
                k = len(bw)
                head = [w for tk in toks[:k] for w in F.words(tk)]
                if head[:k] == bw:
                    lead = SNAP if toks[0].startswith(SNAP) else ""
                    toks = [f"{lead}**{toks[0][len(lead):]}"] + toks[1:]
                    toks[k - 1] = toks[k - 1] + "**"
                    break
            out.append(span(" ".join(toks)) if not cont else f'[{" ".join(toks)}]{{dir="rtl" .cont}}')
        return out


def commentary_paragraphs(session: Path) -> list[str]:
    f = session / "commentary.md"
    if not f.exists():
        raise PlanError("no commentary.md yet")
    _, body, err = F.split_frontmatter(f.read_text(encoding="utf-8"))
    if err:
        raise PlanError(f"commentary.md frontmatter: {err}")
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", body) if p.strip()]


def anchors(nusach: Nusach, paras: list[str]) -> list[int]:
    """For each explanation paragraph, the furthest נוסח word read by its end
    (-1 before any reading), never moving back."""
    ocr = [OM.Tok(w, F.skeleton(w)) for w in nusach.words]
    heard, owner = [], []
    for k, p in enumerate(paras):
        for w in F.words(p):
            if F.plain(w):
                heard.append(OM.Tok(w, F.skeleton(w), str(k)))
                owner.append(k)
    reach = [-1] * len(paras)
    for o1, o2, h1, h2, _ in OM.find_reading(ocr, heard):
        for j in range(h1, h2 + 1):           # spread the block over its paragraphs
            o = o1 + round((j - h1) * (o2 - o1) / max(1, h2 - h1))
            reach[owner[j]] = max(reach[owner[j]], o)
    out, best = [], -1
    for r in reach:
        best = max(best, r)
        out.append(best)
    return out


def pairs(nusach: Nusach, paras: list[str]) -> list[tuple[list[str], list[str]]]:
    """[(text markdown, explanation paragraphs)] in reading order."""
    reach = anchors(nusach, paras)
    units: list[tuple[int, list[str]]] = []          # (last word of the text cut, paragraphs)
    done = -1
    pending: list[str] = []                          # explanation before the first reading
    for p, r in zip(paras, reach):
        if r > done:
            units.append((r, pending + [p]))
            pending, done = [], r
        elif units:
            units[-1][1].append(p)
        else:
            pending.append(p)
    if pending:                                      # never read: all of it with all the text
        units.append((len(nusach.words) - 1, pending))
    if not units or units[-1][0] < len(nusach.words) - 1:
        units.append((len(nusach.words) - 1, []))    # text past the last reading, on its own
    out, t_next = [], 0
    for n, (last_word, ps) in enumerate(units):
        t_last = nusach.word_tok[last_word]
        if n < len(units) - 1:
            t_last = snap(nusach, t_last, t_next)
        if t_last < t_next:                           # nothing new to show: join the pair before
            if out:
                out[-1][1].extend(ps)
            continue
        out.append((nusach.markdown(t_next, t_last), ps))
        t_next = t_last + 1
    return out


SNAP_REACH = 5        # tokens a cut may move to land on a sentence end
CLAUSE_REACH = 3     # ... or before a clause or citation opener, or after a comma
# Words that open a clause or a citation in this literature: a cut just before
# one leaves both halves whole.
OPENERS = {"אבל", "אך", "כי", "הנה", "והנה", "דהנה", "ולכן", "לכן", "וכן", "והוא", "והן", "ומה",
           "דהיינו", "היינו", "שהרי", "ואז", "וזהו", "וזו", "וזה", "משא\"כ", "כמ\"ש", "וכמ\"ש",
           "כמאמר", "וכמאמר", "וז\"ש", "דכתיב", "כדכתיב", "שנאמר", "פי'", "ופי'", "אלא"}
# Words that close what came before: never the first word of a cut.
CLOSERS = {"כו'", "וגו'", "וכו'"}


def snap(nusach: Nusach, t_last: int, t_first: int) -> int:
    """Move a cut to where the text breaks naturally, within reach: a sentence
    end first; else just before a clause or citation opener, or after a comma.
    The reading's edge is approximate (the speaker re-reads, Whisper drops
    words); a phrase cut in half is not acceptable."""
    def bare(i: int) -> str:
        return re.sub(r"\[\^[^\]]+\]", "", F.COMMENT.sub("", nusach.tokens[i][0])).strip().strip("*")

    last = len(nusach.tokens) - 2                 # never swallow the whole remainder

    def ok(i: int) -> bool:
        return t_first <= i <= last and bare(i + 1).rstrip(".:,;") not in CLOSERS

    def sentence_end(i: int) -> bool:
        return bare(i).endswith((".", ":", ";", "?")) and not bare(i).endswith(SNAP)

    def clause_break(i: int) -> bool:
        return bare(i).endswith(",") or bare(i + 1) in OPENERS

    for test, reach in ((sentence_end, SNAP_REACH), (clause_break, CLAUSE_REACH)):
        for d in range(0, reach + 1):
            for i in (t_last + d, t_last - d):
                if ok(i) and test(i):
                    return i
    while t_last < last and not ok(t_last):       # at least don't strand a closer
        t_last += 1
    return t_last


def key_points(plan: dict, nusach: Nusach) -> list[str]:
    keys = plan.get("keys") or []
    tokens = [tk[0] for tk in nusach.tokens]
    flat, owner = [], []
    for i, tk in enumerate(tokens):
        for w in F.words(tk):
            flat.append(w)
            owner.append(i)
    out = []
    for k in keys:
        if not k.get("label") or not k.get("quote"):
            raise PlanError(f"keys: each needs a label and a quote ({k})")
        i = locate(flat, k["quote"], f"keys “{k['label']}”")
        j = i + len(F.words(k["quote"])) - 1
        quote = " ".join(tokens[owner[i]:owner[j] + 1])
        quote = F.COMMENT.sub("", quote).replace("**", "")
        quote = re.sub(r"\[\^[^\]]+\]", "", quote).strip().rstrip(".,:;")
        quote = quote.strip(SNAP + " ") if quote.startswith(SNAP) or quote.endswith(SNAP) else quote
        out += [f"**{span(k['label'])}**", "", f"> {span(quote)}", ""]
    return out


def build(session: Path, plan: dict) -> str:
    if plan.get("boxes"):
        print("  note: the plan's boxes are no longer used — text and explanation are paired by the reading")
    fm = {"session": session.name, "discourse": F.discourse_of(session).name,
          "title": plan.get("title") or "", "layout": "paired", "built_from": PLAN}
    head = ["---", yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000).strip(), "---", ""]
    if plan.get("heading"):
        head += [f"**{span(plan['heading'])}**", "", span("• • •"), ""]   # David has "•", not "◆"
    for ln in plan.get("lines") or []:
        head += [span(ln), ""]
    version = plan.get("version") or "גִּרְסָה א'"
    head += [span(DESCRIPTOR), "", f"*{span(f'{version} · סֶשְׁן {session.name} · עִם בֵּיאוּר הַקּוֹל')}*", ""]

    nusach = Nusach(plan, session)
    try:
        explained, _ = F.apply_edits(commentary_paragraphs(session), F.print_edits(plan))
    except F.EditError as e:
        raise PlanError(str(e))
    body = ["## הַנֹּסַח וְהַבֵּיאוּר", ""]
    for text, explanation in pairs(nusach, explained):
        body += ['::: {custom-style="Nusach"}'] + [ln for p in text for ln in (p, "")]
        body[-1] = ":::"
        body.append("")
        if explanation:
            body += ['::: {custom-style="Commentary"}'] + [ln for p in explanation for ln in (span(p), "")]
            body[-1] = ":::"
            body.append("")
    for note in nusach.notes:
        body += [note, ""]
    # No --- rules between sections: the headings part them, and Word draws
    # a rule as a grey line outside the palette.
    body += ["## נְקֻדּוֹת מַפְתֵּחַ", ""]
    body += key_points(plan, nusach)
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
    ]
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {target}: fill in the title, heading, lines, breaks and keys")
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
