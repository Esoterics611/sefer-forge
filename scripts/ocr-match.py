#!/usr/bin/env python3
"""Line up a session's OCR with the speaker reading it in the voicenote.

Usage:
    python scripts/ocr-match.py discourses/003-breishis/sessions/002

The speaker reads the photographed text aloud and stops to explain it. This
finds the stretches he reads, and reports in <session>/ocr-match.md:

  - the reading range: where in ocr.md he starts and stops, with times. OCR
    text outside it is in the photo but not in the voicenote, the candidate
    for trimming from the session's נוסח;
  - differences inside the range, each with its time and context:
      heard, not in OCR  — words he read that the OCR lacks: an OCR miss
                           (check the photo) or a word he added;
      in OCR, not heard  — OCR words he skipped, or OCR text that is wrong;
      differs            — a word read differently from the OCR;
    then spelling-level differences (most are Whisper's);
  - the commentary stretches between readings: the material of commentary.md,
    and the natural boundaries of its ביאור boxes.

Abbreviations in the OCR (ע"י, בחי', כמ"ש) match their spoken forms through
glossary/abbreviations.yaml, or when the spoken words fit their letters.
Whisper's text is read from voicenotes/*.timed.txt with the glossary's auto
fixes applied, so every finding has a time to re-listen at.
"""
from __future__ import annotations

import difflib
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import forgelib as F

MIN_BLOCK = 3          # words in a row that count as reading
ISOLATED = 30          # a short match this far from other reading is commentary quoting it
SHORT = 5              # ... where "short" is fewer words than this
INTERLUDE = 6          # this many extra spoken words in a row are commentary, not a difference
OPEN, EXTEND = 1.0, 0.05


@dataclass
class Tok:
    text: str          # as printed / as Whisper wrote it
    sk: str            # skeleton for matching
    when: str = ""     # heard words: start time of their .timed.txt line


def ocr_tokens(session: Path) -> list[Tok]:
    text = F.ocr_text(session)
    text = re.sub(r"\{[^}]*\}", " ", text).replace("**", "")
    toks = []
    for raw in text.split():
        t = raw.strip("[]()")
        if F.plain(t):
            toks.append(Tok(t, F.skeleton(t)))
    return toks


def heard_tokens(session: Path) -> list[Tok]:
    return [Tok(w, F.skeleton(w), when) for w, when in F.timed_words(session) if F.plain(w)]


def match_seq(ocr: list[Tok]) -> tuple[list[str], list[int]]:
    """OCR skeletons for SequenceMatcher, abbreviations replaced by their usual
    spoken form, with each entry's OCR token index."""
    seq, idx = [], []
    for i, t in enumerate(ocr):
        exps = F.expansions(t.text) if F.is_abbrev(t.text) else []
        for w in (exps[0] if exps else [t.sk]):
            seq.append(w)
            idx.append(i)
    return seq, idx


def near(a: str, b: str) -> bool:
    """One letter apart, on words long enough for that to mean a mis-hearing."""
    if min(len(a), len(b)) < 3:
        return False
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.75


def align(o: list[Tok], h: list[Tok]) -> list[tuple[str, list[int], list[int]]]:
    """Gotoh-style alignment of a gap: ops are ("eq"|"abbr"|"near"|"del"|"ins",
    OCR indexes, heard indexes). Runs of spoken words cost little once opened,
    so commentary stays in one piece instead of absorbing stray matches."""
    INF = float("inf")
    n, m = len(o), len(h)
    # cost[x][y][s]: s=0 after a match or deletion, s=1 inside a run of heard words
    cost = [[[INF, INF] for _ in range(m + 1)] for _ in range(n + 1)]
    back: dict = {}
    cost[0][0][0] = 0.0
    for x in range(n + 1):
        for y in range(m + 1):
            for s in (0, 1):
                c = cost[x][y][s]
                if c == INF:
                    continue
                if y < m:                                          # a heard word not in the OCR
                    nc = c + (EXTEND if s == 1 else OPEN)
                    if nc < cost[x][y + 1][1]:
                        cost[x][y + 1][1] = nc
                        back[(x, y + 1, 1)] = (x, y, s, "ins", 1)
                if x < n:                                          # an OCR word not heard
                    nc = c + 1.0
                    if nc < cost[x + 1][y][0]:
                        cost[x + 1][y][0] = nc
                        back[(x + 1, y, 0)] = (x, y, s, "del", 0)
                if x < n and y < m:
                    k, op, add = 0, "", 0.0
                    if o[x].sk == h[y].sk:
                        k, op = 1, "eq"
                    elif F.is_abbrev(o[x].text) and (k := F.abbrev_match(o[x].text, [t.text for t in h[y:y + 4]])):
                        op = "abbr"
                    elif near(o[x].sk, h[y].sk):
                        k, op, add = 1, "near", 0.4
                    if k:
                        nc = c + add
                        if nc < cost[x + 1][y + k][0]:
                            cost[x + 1][y + k][0] = nc
                            back[(x + 1, y + k, 0)] = (x, y, s, op, k)
    s = 0 if cost[n][m][0] <= cost[n][m][1] else 1
    x, y, ops = n, m, []
    while (x, y) != (0, 0):
        px, py, ps, op, k = back[(x, y, s)]
        ops.append((op, list(range(px, x)), list(range(py, y))))
        x, y, s = px, py, ps
    return ops[::-1]


def extend(ocr: list[Tok], heard: list[Tok], block: tuple, forward: bool) -> tuple | None:
    """Reading often starts or ends with words Whisper mangled, too few in a row
    to anchor. Align outward from the first (or last) firm match and move the
    edge to any run of two matched words in a row that lies within a few OCR
    words of the reading, with no commentary run in between."""
    if forward:
        o1, h1 = block[1] + 1, block[3] + 1
        oa, ha = o1, h1
        ops = align(ocr[o1:o1 + 25], heard[h1:h1 + 40])
    else:
        o1, h1 = block[0], block[2]
        oa, ha = max(0, o1 - 25), max(0, h1 - 40)
        ops = align(ocr[oa:o1], heard[ha:h1])[::-1]
    best, run_ins, streak, since = None, 0, [], 0
    for op, os_, hs in ops:
        if op == "ins":
            run_ins += 1
            if run_ins >= INTERLUDE:
                break
            continue
        run_ins = 0
        since += 1
        if since > 8:
            break
        if op in ("eq", "abbr"):
            streak.append((os_, hs))
            if len(streak) >= 2:
                (o_a, h_a), (o_b, h_b) = streak[0], streak[-1]
                lo, hi = sorted((o_a[0], o_b[-1]))
                hlo, hhi = sorted((h_a[0], h_b[-1]))
                best = (oa + lo, oa + hi, ha + hlo, ha + hhi, len(streak))
                since = 0
        else:
            streak = []
    return best


def find_reading(ocr: list[Tok], heard: list[Tok]) -> list[tuple]:
    """The stretches where the heard text reads the OCR, in order:
    (ocr first, ocr last, heard first, heard last, words). Used by
    build-section.py too, with commentary.md as the heard text."""
    seq, idx = match_seq(ocr)
    sm = difflib.SequenceMatcher(None, seq, [t.sk for t in heard], autojunk=False)
    blocks = [(idx[i], idx[i + n - 1], j, j + n - 1, n) for i, j, n in sm.get_matching_blocks() if n >= MIN_BLOCK]
    # Drop short matches far from any other reading: commentary quoting the text.
    kept = []
    for b_i, b in enumerate(blocks):
        prev_gap = b[0] - blocks[b_i - 1][1] if b_i else 10**6
        next_gap = blocks[b_i + 1][0] - b[1] if b_i + 1 < len(blocks) else 10**6
        if b[4] >= SHORT or min(prev_gap, next_gap) <= ISOLATED:
            kept.append(b)
    if not kept:
        return []
    if (edge := extend(ocr, heard, kept[0], forward=False)):
        kept.insert(0, edge)
    if (edge := extend(ocr, heard, kept[-1], forward=True)):
        kept.append(edge)
    return kept


def ctx(toks: list[Tok], i: int, j: int, k: int = 4) -> str:
    before = " ".join(t.text for t in toks[max(0, i - k):i])
    mid = " ".join(t.text for t in toks[i:j])
    after = " ".join(t.text for t in toks[j:j + k])
    return f"…{before} ⟨{mid}⟩ {after}…"


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/ocr-match.py <session-path>")
        return 1
    session = Path(sys.argv[1].rstrip("/"))
    if not (session / "ocr.md").exists():
        print(f"No ocr.md in {session}")
        return 1
    ocr, heard = ocr_tokens(session), heard_tokens(session)
    if not heard:
        print(f"No voicenotes/*.timed.txt in {session}: run scripts/transcribe.py first")
        return 1

    kept = find_reading(ocr, heard)
    if not kept:
        print("No reading found: the voicenote never reads three OCR words in a row.")
        return 1

    findings: list[tuple[str, str, str]] = []      # (kind, time, text)
    minor: list[tuple[str, str]] = []
    interludes: list[tuple[str, str, int, str]] = []
    heard_in_reading = sum(b[4] for b in kept)

    def interlude(j1: int, j2: int, after: str) -> None:
        if j2 > j1:
            interludes.append((heard[j1].when, heard[j2 - 1].when, j2 - j1, after))

    interlude(0, kept[0][2], "before the reading")
    for (a_o1, a_o2, a_h1, a_h2, _), (b_o1, b_o2, b_h1, b_h2, _) in zip(kept, kept[1:]):
        o_gap, h_gap = ocr[a_o2 + 1:b_o1], heard[a_h2 + 1:b_h1]
        if not o_gap and not h_gap:
            continue
        ops = align(o_gap, h_gap)
        o0, h0 = a_o2 + 1, a_h2 + 1
        dels: list[int] = []
        ins: list[int] = []
        last_o, last_h = -1, -1

        def close() -> None:
            """One run of unmatched words between matches → findings / commentary."""
            at_o = o0 + last_o + 1                    # OCR position where the run sits
            when = heard[h0 + ins[0]].when if ins else heard[min(h0 + last_h + 1, len(heard) - 1)].when
            if len(ins) >= INTERLUDE:
                before = " ".join(t.text for t in ocr[max(0, at_o - 4):at_o])
                interlude(h0 + ins[0], h0 + ins[-1] + 1, f"after “{before}”")
                if dels:
                    findings.append(("in OCR, not heard", when, ctx(ocr, o0 + dels[0], o0 + dels[-1] + 1)))
            elif dels and ins:
                o_txt = " ".join(ocr[o0 + i].text for i in dels)
                h_txt = " ".join(heard[h0 + i].text for i in ins)
                findings.append(("differs", when, f"OCR **{o_txt}** / heard **{h_txt}** — "
                                 + ctx(ocr, o0 + dels[0], o0 + dels[-1] + 1)))
            elif dels:
                findings.append(("in OCR, not heard", when, ctx(ocr, o0 + dels[0], o0 + dels[-1] + 1)))
            elif ins:
                h_txt = " ".join(heard[h0 + i].text for i in ins)
                findings.append(("heard, not in OCR", when, f"**{h_txt}** — " + ctx(ocr, at_o, at_o)))
            dels.clear()
            ins.clear()

        for op, os_, hs in ops:
            if op == "del":
                dels += os_
            elif op == "ins":
                ins += hs
            else:
                if dels or ins:
                    close()
                if op == "near":
                    minor.append((heard[h0 + hs[0]].when, f"OCR **{ocr[o0 + os_[0]].text}** / heard "
                                  f"**{heard[h0 + hs[0]].text}** — " + ctx(ocr, o0 + os_[0], o0 + os_[0] + 1)))
                last_o, last_h = os_[-1], hs[-1]
        if dels or ins:
            close()
    interlude(kept[-1][3] + 1, len(heard), "after the reading")

    start, end = kept[0][0], kept[-1][1]
    out = render(session, ocr, heard, start, end, heard_in_reading, kept, findings, minor, interludes)
    (session / "ocr-match.md").write_text(out, encoding="utf-8")
    print(f"OCR {len(ocr)} words · read {start + 1}–{end + 1} · {len(findings)} differences, "
          f"{len(minor)} spelling-level · {len(interludes)} commentary stretches")
    print(f"-> {session / 'ocr-match.md'}")
    return 0


def render(session, ocr, heard, start, end, read_words, kept, findings, minor, interludes) -> str:
    def words(a, b):
        return " ".join(t.text for t in ocr[a:b])

    lines = [f"# OCR ↔ reading — {session}", "",
             f"OCR {len(ocr)} words · read aloud: words {start + 1}–{end + 1} "
             f"({read_words} matched in {len(kept)} stretches) · Whisper {len(heard)} words", "",
             "## Reading range", "",
             f"- **Starts** at OCR word {start + 1}, heard at {heard[kept[0][2]].when}: “{words(start, start + 8)}…”",
             f"- **Ends** at OCR word {end + 1}, heard at {heard[kept[-1][3]].when}: “…{words(max(start, end - 7), end + 1)}”"]
    if start > 0:
        lines.append(f"- **Not read, before the start** ({start} words): “{words(0, start)}”")
    if end < len(ocr) - 1:
        lines.append(f"- **Not read, after the end** ({len(ocr) - end - 1} words): “{words(end + 1, len(ocr))}”")
    lines += ["", "For section-plan.yaml: `start:` and `end:` take a few words from the lines above.", ""]

    order = {"heard, not in OCR": 0, "in OCR, not heard": 1, "differs": 2}
    lines += ["## Differences inside the reading — check each against the photo", ""]
    if findings:
        for n, (kind, when, text) in enumerate(sorted(findings, key=lambda f: (order[f[0]], f[1])), 1):
            lines.append(f"{n}. [{when}] {kind}: {text}")
    else:
        lines.append("none")
    lines += ["", "## Spelling-level (one letter or so; usually Whisper)", ""]
    lines += [f"{n}. [{w}] {t}" for n, (w, t) in enumerate(minor, 1)] or ["none"]
    lines += ["", "## Commentary stretches", ""]
    lines += [f"- {a}–{b} ({n} words) {after}" for a, b, n, after in interludes] or ["none"]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
