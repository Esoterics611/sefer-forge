#!/usr/bin/env python3
"""Check a session's files against the repo's rules.

Usage:
    python scripts/check-session.py discourses/003-breishis/sessions/002
    python scripts/check-session.py discourses/003-breishis      # every session
    python scripts/check-session.py                              # every session
    python scripts/check-session.py <path> --quiet               # problems only

Images+voice sessions:
  ocr.md        valid frontmatter; one "## Image:" per photo, none for a
                photo that is gone
  commentary.md every word traceable to Whisper (transcript-diff's Added
                count), UNCLEAR flags carry their time, review.md up to date
  section.md    valid frontmatter with a title; the three named sections in
                order; the נוסח is a stretch of ocr.md word for word, with no
                {.underline}; 5–8 key points, each quoting the נוסח verbatim;
                every ביאור box opens with its label and the boxes carry
                commentary.md word for word; every paragraph RTL-wrapped; no
                grid tables; footnote references and definitions match
Voice-only sessions:
  transcript.md valid frontmatter with title and source, footnotes match,
                its readability `edits:` each match once,
                Added count, UNCLEAR times, review.md up to date

Prints ✗ for errors, ! for warnings, · for notes. Exits 1 if any error.
Sessions still at an earlier step are only checked for what exists.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import forgelib as F

DIFF = F.load_script("transcript-diff")
SECTIONS = ["הנסח העקרי", "נקדות מפתח", "ביאור ופירוש"]
PAIRED = ["הנסח והביאור", "נקדות מפתח"]          # layout: paired (docs/print-standard.md)
BOX = re.compile(r'^::: \{custom-style="Commentary"\}\n(.*?)\n:::', re.M | re.S)
DIV = re.compile(r'^::: \{custom-style="(Nusach|Commentary)"\}\n(.*?)\n:::', re.M | re.S)
BOX_LABEL = re.compile(r'^\*\*\[■ ביאור — .+\]\{dir="rtl"\}\*\*$')
RTL_END = re.compile(r'\]\{dir="rtl"[^}]*\}\**\s*$')


class Report:
    def __init__(self, session: Path):
        self.session, self.lines = session, []

    def error(self, msg: str) -> None:
        self.lines.append(("✗", msg))

    def warn(self, msg: str) -> None:
        self.lines.append(("!", msg))

    def note(self, msg: str) -> None:
        self.lines.append(("·", msg))

    @property
    def errors(self) -> int:
        return sum(1 for k, _ in self.lines if k == "✗")


def heading_key(line: str) -> str:
    return F.strip_marks(line.lstrip("#").strip())


def find_run(hay: list[str], needle: list[str]) -> int:
    """Index where needle occurs in hay as a contiguous run, or -1."""
    if not needle:
        return -1
    first = needle[0]
    for i in range(len(hay) - len(needle) + 1):
        if hay[i] == first and hay[i:i + len(needle)] == needle:
            return i
    return -1


def divergence(source: list[str], text: list[str], name: str = "OCR") -> str:
    """Where a text stops following its source: the longest opening stretch of
    the text found in the source, and the first word after it on each side."""
    lo, hi, at = 0, len(text), -1
    while lo < hi:                                  # longest prefix of text found in source
        mid = (lo + hi + 1) // 2
        pos = find_run(source, text[:mid])
        if pos >= 0:
            lo, at = mid, pos
        else:
            hi = mid - 1
    if at < 0:
        return f"its first word “{text[0]}” is not in the {name}"
    k = lo
    before = " ".join(text[max(0, k - 5):k])
    here = " ".join(text[k:k + 3]) or "(end)"
    there = " ".join(source[at + k:at + k + 3]) or "(end)"
    return f"after “…{before}” it has “{here}” where the {name} has “{there}”"


def check_frontmatter(r: Report, f: Path, need: tuple[str, ...] = ()) -> tuple[dict, str]:
    fm, body, err = F.split_frontmatter(f.read_text(encoding="utf-8"))
    if err:
        r.error(f"{f.name}: frontmatter is not valid YAML — {err[:120]}")
        return {}, body
    if fm is None:
        r.error(f"{f.name}: no YAML frontmatter")
        return {}, body
    for k in need:
        if not fm.get(k):
            r.error(f"{f.name}: frontmatter has no `{k}`")
    return fm, body


def check_unclear_times(r: Report, f: Path, text: str) -> None:
    flags = re.findall(r"<!--\s*UNCLEAR(.*?)-->", text, flags=re.S)
    untimed = [x for x in flags if not re.match(r"\s*\d+:\d+", x)]
    has_timed = any(F.sidecar(a, "timed.txt").exists() for a in F.audio_files(r.session))
    if flags:
        r.note(f"{f.name}: {len(flags)} UNCLEAR flag(s) to listen to")
    if untimed and has_timed:
        r.warn(f"{f.name}: {len(untimed)} UNCLEAR flag(s) without a time (`<!-- UNCLEAR mm:ss: ... -->`)")


def check_cleanup(r: Report, cleaned: Path) -> None:
    """The Added count of transcript-diff, and whether review.md is current."""
    raws = sorted((r.session / "voicenotes").glob("*.raw.txt"))
    if not raws:
        return
    fixes = F.load_script("apply-fixes")
    auto, _ = fixes.load_fixes(r.session)
    whisper = " ".join(fixes.apply_auto(p.read_text(encoding="utf-8"), auto)[0] for p in raws)
    before = DIFF.words(whisper)
    after = DIFF.words(cleaned.read_text(encoding="utf-8"))
    d = DIFF.diff(before, after)
    if d["added"]:
        r.warn(f"{cleaned.name}: {len(d['added'])} added word run(s) not in Whisper — each needs a rule or a revert: "
               + "; ".join(d["added"][:3]))
    r.note(f"{cleaned.name}: Whisper {len(before)} words → {len(after)} · replaced {len(d['replaced'])} · "
           f"removed {len(d['removed'])} · fillers {len(d['fillers'])} · added {len(d['added'])}")
    review = r.session / "review.md"
    newest = max(p.stat().st_mtime for p in [cleaned, r.session / "section.md"] if p.exists())
    if not review.exists():
        r.warn("no review.md: run scripts/transcript-diff.py")
    elif review.stat().st_mtime < newest:
        r.warn("review.md is older than the text it reviews: re-run scripts/transcript-diff.py")


def check_footnotes(r: Report, name: str, body: str) -> None:
    refs = set(re.findall(r"\[\^([^\]\s]+)\](?!:)", body))
    defs = set(re.findall(r"^\[\^([^\]\s]+)\]:", body, flags=re.M))
    if refs - defs:
        r.error(f"{name}: footnote(s) used but not defined: {', '.join(sorted(refs - defs))}")
    if defs - refs:
        r.warn(f"{name}: footnote(s) defined but never used: {', '.join(sorted(defs - refs))}")


def check_ocr(r: Report) -> list[str]:
    f = r.session / "ocr.md"
    check_frontmatter(r, f)
    text = f.read_text(encoding="utf-8")
    heads = re.findall(r"^## Image:\s*(.+?)\s*$", text, flags=re.M)
    photos = [p.name for p in F.image_files(r.session)]
    for p in photos:
        if p not in heads:
            r.error(f"ocr.md: no “## Image: {p}” section: that photo was never OCR'd")
    for h in heads:
        if h not in photos:
            r.error(f"ocr.md: “## Image: {h}” but images/ has no such photo")
    n = len(re.findall(r"<!--\s*UNCLEAR", text))
    if n:
        r.note(f"ocr.md: {n} UNCLEAR flag(s)")
    return F.words(F.ocr_body(r.session))


def section_parts(body: str) -> dict[str, str]:
    """section.md's ## sections by niqqud-free name ('' = the title block)."""
    parts, name, buf = {}, "", []
    for line in body.splitlines():
        if line.startswith("## "):
            parts[name] = "\n".join(buf)
            name, buf = heading_key(line), []
        else:
            buf.append(line)
    parts[name] = "\n".join(buf)
    return parts


def check_rtl(r: Report, where: str, text: str) -> None:
    bad = 0
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or not re.search("[א-ת]", F.strip_marks(block)):
            continue
        if block.startswith((":::", "<!--")) or block == "---":
            continue
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith(":::") or not re.search("[א-ת]", line):
                continue
            if not (RTL_END.search(line) or line.startswith("<!--")):
                bad += 1
                break
    if bad:
        r.warn(f"section.md {where}: {bad} paragraph(s) not wrapped in [ ]{{dir=\"rtl\"}}")


def check_paired(r: Report, body: str, parts: dict, ocr_words: list[str] | None) -> None:
    """layout: paired — cuts of the text, each followed by its explanation."""
    found = [k for k in parts if k]
    for s in PAIRED:
        if s not in found:
            r.error(f"section.md: no “## {s}” section")
    if [s for s in found if s in PAIRED] != [s for s in PAIRED if s in found]:
        r.error("section.md: sections out of order")
    check_footnotes(r, "section.md", body)
    paired = parts.get(PAIRED[0], "")
    divs = DIV.findall(paired)
    kinds = [k for k, _ in divs]
    if not kinds or kinds[0] != "Nusach":
        r.error("section.md: the paired section must open with a cut of the text (Nusach)")
    if any(a == b == "Commentary" for a, b in zip(kinds, kinds[1:])):
        r.error("section.md: two explanations in a row with no text between them")
    if "■" in paired or re.search(r"^\s*(\+-{3,}|\|)", paired, flags=re.M):
        r.error("section.md: boxes or box labels in the paired layout (the explanation is never boxed)")
    check_rtl(r, "הנוסח והביאור", paired)
    text = "\n".join(c for k, c in divs if k == "Nusach")
    if "{.underline}" in text:
        r.error("section.md נוסח: has {.underline} markup (the נוסח is plain flowing text)")
    n_words = F.words(text)
    if ocr_words is not None and n_words:
        at = find_run(ocr_words, n_words)
        if at < 0:
            r.error("section.md נוסח: does not follow ocr.md word for word — " + divergence(ocr_words, n_words))
        else:
            r.note(f"נוסח = OCR words {at + 1}–{at + len(n_words)} of {len(ocr_words)}, "
                   f"in {kinds.count('Nusach')} cuts with {kinds.count('Commentary')} explanations")
    com = r.session / "commentary.md"
    if com.exists():
        expl = "\n".join(c for k, c in divs if k == "Commentary")
        _, cbody, _ = F.split_frontmatter(com.read_text(encoding="utf-8"))
        cparas = [" ".join(x.split()) for x in re.split(r"\n\s*\n", cbody) if x.strip()]
        try:
            cparas, n_edits = F.apply_edits(cparas, F.plan_edits(r.session))
        except F.EditError as e:
            r.error(f"section-plan.yaml edits/style: {e}")
            n_edits = 0
        if n_edits:
            r.note(f"{F.edit_counts(F.load_yaml(r.session / 'section-plan.yaml'))} from section-plan.yaml")
        sd = DIFF.diff(DIFF.words("\n\n".join(cparas)), DIFF.words(expl))
        n = sum(len(sd[k]) for k in ("added", "replaced", "removed", "fillers"))
        if n:
            sample = (sd["removed"] + sd["replaced"] + sd["added"] + sd["fillers"])[:3]
            r.error(f"section.md: the explanations differ from commentary.md (with the plan's edits) in {n} place(s) — "
                    + "; ".join(sample))
        else:
            r.note("explanations carry commentary.md word for word" + (", with the plan's edits" if n_edits else ""))
    keys = parts.get(PAIRED[1], "")
    if keys:
        check_keys(r, keys, n_words)


def check_keys(r: Report, keys: str, n_words: list[str]) -> None:
    check_rtl(r, "נקודות מפתח", keys)
    labels = re.findall(r'^\*\*\[.+?\]\{dir="rtl"\}\*\*\s*$', keys, flags=re.M)
    quotes = re.findall(r'^>\s*(.+)$', keys, flags=re.M)
    if not 5 <= len(labels) <= 8:
        r.warn(f"section.md נקודות מפתח: {len(labels)} key points (the rule is 5–8)")
    if len(quotes) < len(labels):
        r.error(f"section.md נקודות מפתח: {len(labels)} labels but {len(quotes)} quoted passages")
    for q in quotes:
        qw = [w for w in F.words(q) if w.strip(".")]
        if qw and find_run(n_words, qw) < 0:
            r.error(f"section.md נקודות מפתח: quote not verbatim in the נוסח — “{' '.join(qw[:6])}…”: "
                    + divergence(n_words, qw, "נוסח"))


def check_section(r: Report, ocr_words: list[str] | None) -> None:
    f = r.session / "section.md"
    fm, body = check_frontmatter(r, f, need=("title",))
    parts = section_parts(body)
    if (fm or {}).get("layout") == "paired":
        check_paired(r, body, parts, ocr_words)
        return
    if fm is not None and r.session.joinpath("section-plan.yaml").exists():
        r.warn("section.md: built in the old three-section layout; rebuild it "
               "(python scripts/build-section.py) for the paired layout")
    found = [k for k in parts if k]
    legacy = re.search(r"^\+-{3,}", body, flags=re.M) and 'custom-style="Commentary"' not in body
    order = [s for s in found if s in SECTIONS]
    for s in SECTIONS:
        if s not in found:
            r.error(f"section.md: no “## {s}” section")
    if order != [s for s in SECTIONS if s in order]:
        r.error(f"section.md: sections out of order: {' → '.join(order)}")
    check_footnotes(r, "section.md", body)

    nusach = parts.get(SECTIONS[0], "")
    if legacy:
        r.note("section.md: ingested before 2026-10-15 (grid tables); נוסח and key points not compared")
        ocr_words = None
    if nusach:
        if "{.underline}" in nusach:
            r.error("section.md נוסח: has {.underline} markup (the נוסח is plain flowing text)")
        check_rtl(r, "נוסח", nusach)
        n_words = F.words(nusach)
        if ocr_words is not None and n_words:
            at = find_run(ocr_words, n_words)
            if at < 0:
                r.error("section.md נוסח: does not follow ocr.md word for word — " + divergence(ocr_words, n_words))
            else:
                r.note(f"נוסח = OCR words {at + 1}–{at + len(n_words)} of {len(ocr_words)}")

    keys = parts.get(SECTIONS[1], "")
    if keys:
        check_rtl(r, "נקודות מפתח", keys)
        labels = re.findall(r'^\*\*\[.+?\]\{dir="rtl"\}\*\*\s*$', keys, flags=re.M)
        quotes = re.findall(r'^>\s*(.+)$', keys, flags=re.M)
        if not 5 <= len(labels) <= 8:
            r.warn(f"section.md נקודות מפתח: {len(labels)} key points (the rule is 5–8)")
        if len(quotes) < len(labels):
            r.error(f"section.md נקודות מפתח: {len(labels)} labels but {len(quotes)} quoted passages")
        n_words = F.words(nusach)
        for q in quotes if not legacy else []:
            qw = [w for w in F.words(q) if w.strip(".")]
            if qw and find_run(n_words, qw) < 0:
                r.error(f"section.md נקודות מפתח: quote not verbatim in the נוסח — “{' '.join(qw[:6])}…”: "
                        + divergence(n_words, qw, "נוסח"))

    biur = parts.get(SECTIONS[2], "")
    if biur:
        if legacy:
            return
        if re.search(r"^\s*(\+-{3,}|\|)", biur, flags=re.M):
            r.error("section.md ביאור: grid table lines (+---+ or |); use ::: Commentary boxes")
        boxes = BOX.findall(body)
        if not boxes:
            r.error("section.md ביאור: no ::: {custom-style=\"Commentary\"} boxes")
        for i, b in enumerate(boxes, 1):
            first = next((ln for ln in b.splitlines() if ln.strip()), "")
            if not BOX_LABEL.match(first.strip()):
                r.error(f"section.md ביאור box {i}: does not open with **[■ ביאור — <topic>]{{dir=\"rtl\"}}**")
        check_rtl(r, "ביאור", biur)
        com = r.session / "commentary.md"
        if com.exists() and boxes:
            text = "\n".join(ln for b in boxes for ln in b.splitlines() if "■" not in ln)
            sd = DIFF.diff(DIFF.words(com.read_text(encoding="utf-8")), DIFF.words(text))
            n = sum(len(sd[k]) for k in ("added", "replaced", "removed", "fillers"))
            if n:
                sample = (sd["removed"] + sd["replaced"] + sd["added"] + sd["fillers"])[:3]
                r.error(f"section.md ביאור: boxes differ from commentary.md in {n} place(s) — " + "; ".join(sample))
            else:
                r.note(f"ביאור: {len(boxes)} boxes carry commentary.md word for word")


def check(session: Path) -> Report:
    r = Report(session)
    if F.voice_only(session):
        if not F.audio_files(session):
            r.warn("no recording in voicenotes/")
        t = session / "transcript.md"
        if t.exists():
            fm, body = check_frontmatter(r, t, need=("title", "source"))
            check_footnotes(r, "transcript.md", body)
            try:
                _, n_edits = F.edit_transcript(body, F.print_edits(fm))
                if n_edits:
                    r.note(f"{F.edit_counts(fm)} in the frontmatter")
            except F.EditError as e:
                r.error(f"transcript.md edits/style: {e}")
            check_unclear_times(r, t, body)
            check_cleanup(r, t)
        return r

    if not F.image_files(session):
        r.warn("no photos in images/")
    if not F.audio_files(session):
        r.warn("no voicenote in voicenotes/")
    ocr_words = check_ocr(r) if (session / "ocr.md").exists() else None
    com = session / "commentary.md"
    if com.exists():
        check_frontmatter(r, com)
        check_unclear_times(r, com, com.read_text(encoding="utf-8"))
        check_cleanup(r, com)
    if (session / "section.md").exists():
        check_section(r, ocr_words)
    return r


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    sessions = F.resolve_sessions([a for a in argv if not a.startswith("--")])
    failed = 0
    for s in sessions:
        r = check(s)
        failed += r.errors > 0
        shown = [(k, m) for k, m in r.lines if not quiet or k != "·"]
        if quiet and not shown:
            continue
        kind = "voice-only" if F.voice_only(s) else "images+voice"
        print(f"{s}  ({kind})" + ("" if shown else "  ✓"))
        for k, m in shown:
            print(f"  {k} {m}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
