#!/usr/bin/env python3
"""Build a study explanation (ביאור) of a text: the text itself, the sources it
cites and the explanation, in one document.

Usage:
    python scripts/build-biur.py discourses/004-levushei-haneshama/biur          # biur.src.md → biur.md
    python scripts/build-biur.py discourses/004-levushei-haneshama/biur --pdf    # ... and output/biur/<discourse>.pdf
    python scripts/build-biur.py <dir> --check                                   # only the checks
    python scripts/build-biur.py <dir> --pdf --review                            # a review copy (output/biur/review/):
        paragraph numbers, and the open findings of an independent check (checks.yaml) marked and listed at the end.
        The plain --pdf is the finished document: neither numbers nor marks.

A ביאור lives in its own folder beside the discourse's sessions (`<discourse>/biur/`)
and is printed by this script, to `output/biur/`. It is kept apart from the
teacher's sessions until he commands it deployed as his own work (CLAUDE.md).

`biur.src.md` is what is written by hand: the explanation, with one-line
directives where a text is to stand. The build replaces each directive by the
text itself, taken from the copies kept in `sources/` — so every quotation is
exact, and can be traced to its address. `biur.md` is generated (front matter
`built_from: biur.src.md`): edit the source and rebuild.

Directives (each alone on a line; values in double quotes):

    @text from="..." to="..."
        The next stretch of the text being explained (the front matter's
        `text_file`, between `text_from` and `text_to`). Stretches must follow
        one another: the build fails if words of the text are skipped, and
        reports how much of the text is covered.

    @source work="etz-chaim" ref="49.5.1" from="..." to="..." mark="...|..." label="..." note="..."
        A passage of a work in sources/sources.yaml. `ref` is an address or
        several consecutive ones ("39.11.7,39.11.8"); `from`/`to` are its first
        and last words (omit for the paragraph's start or end); `mark` are
        phrases to set in bold (the words the text cites), separated by |.
        `page="2:229b"` instead of `ref` takes a printed page (Zohar, Mikdash
        Melekh); several pages: "2:229a,2:229b".
        `emend="נמות>נפשות"` corrects a slip of the copy in what prints (the
        copy in sources/ is untouched; record each one in the biur's check.md).
        The word must occur once in the passage; several: "a>b|c>d".

    @file path="sources/md/..." section="..." from="..." to="..." label="..."
        A passage of a markdown file (a transcription): `section` is a
        heading of the file (the text under it), optional.

The meaning layer (Ronnie's word, 2026-11-16): a block

    ::: {.meaning}
    The paragraph above, in the soul of a person: the terms as Ronnie defines them (knowledge/teacher/terms.yaml).
    :::

prints after the paragraph it explains, labelled "בנפש האדם", and the build appends "מפתח המושגים": every term of
terms.yaml the blocks use, with its meaning and the shiur it comes from. `--no-meaning` prints without the layer
(output/biur/plain/).

A woven explanation (front matter `woven: true`, with `text_file`): instead of @text stretches, the
words of the text run inside the explanation in bold (**...**), the plain meaning woven between them.
The build reads the bold words in order (footnotes, headings and meaning blocks aside) and fails unless
they are the text itself, word for word; it reports how much of the text they cover. A text_file's HTML
comments (a session's ocr.md: notes, column marks) are not part of the text.

An English translation (front matter `lang: en`, set left to right; headings Introduction, Summary and those declared
in `headings:`) can hold itself to the original with `mirror: <the original's biur.src.md>`: section by section, the
same number of stretches of the text (bold) and of footnotes, or the build fails.

Printing: `engine: weasyprint` prints with WeasyPrint instead of Chrome, for footnotes at the foot of
the page (`[...]{.fn}`); `css:` names stylesheets laid over templates/biur.css (a path, or a list).
`fold: true` (a woven explanation printed folded and stapled as a booklet): blank pages before the closing
page (`::: {.works}`) bring the count to a multiple of four, so the closing page is the outside of the back.
`open_abbreviations: <yaml>` (beside biur.src.md) prints every abbreviation it lists in full words, in the text
and the explanation alike; the source keeps them, so the text is still checked word for word against text_file.

Checks: every directive resolves; the @text stretches cover the text in order;
no directive is left in the output.
"""
from __future__ import annotations

import html
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

import sourcelib as S

ROOT = S.ROOT
LONG_STRETCH = 1200        # characters: a stretch of the text longer than this may break across pages
CSS = ROOT / "templates" / "biur.css"
DIRECTIVE = re.compile(r"^@(text|source|file)\b(.*)$")


class BuildError(Exception):
    pass


def args_of(rest: str, line_no: int) -> dict:
    try:
        tokens = shlex.split(rest)
    except ValueError as e:
        raise BuildError(f"line {line_no}: {e}") from None
    out = {}
    for tok in tokens:
        if "=" not in tok:
            raise BuildError(f"line {line_no}: expected key=\"value\", got {tok!r}")
        k, v = tok.split("=", 1)
        out[k] = v
    return out


def cut(text: str, frm: str | None, to: str | None, where: str) -> tuple[str, bool, bool]:
    """(the stretch of text from `frm` through `to`, cut at start?, cut at end?)."""
    a, b = 0, len(text)
    if frm:
        m = S.locate(text, frm)
        if not m:
            raise BuildError(f"{where}: from= words not found: {frm!r}")
        a = m[0]
    if to:
        m = S.locate(text, to, a)
        if not m:
            raise BuildError(f"{where}: to= words not found after from=: {to!r}")
        b = m[1]
        while b < len(text) and text[b] in ".,:;)]":
            b += 1
    return text[a:b].strip(), a > 0, b < len(text.rstrip())


def emend(text: str, fixes: str | None, where: str) -> str:
    """A slip of the copy, printed corrected (the copy itself is not changed)."""
    if not fixes:
        return text
    for pair in fixes.split("|"):
        if ">" not in pair:
            raise BuildError(f"{where}: emend= expects old>new, got {pair!r}")
        old, new = (x.strip().replace("״", '"').replace("׳", "'") for x in pair.split(">", 1))
        hits = [m.start() for m in re.finditer(rf"(?<![\u05d0-\u05ea]){re.escape(old)}(?![\u05d0-\u05ea\"'])", text)]
        if len(hits) != 1:
            raise BuildError(f"{where}: emend= word {old!r} occurs {len(hits)} times in the passage (must be once)")
        i = hits[0]
        text = text[:i] + new + text[i + len(old):]
    return text


def bold(text: str, marks: str | None, where: str) -> str:
    if not marks:
        return text
    spans = []
    for phrase in marks.split("|"):
        m = S.locate(text, phrase.strip())
        if not m:
            raise BuildError(f"{where}: mark= words not found: {phrase!r}")
        spans.append(m)
    spans.sort()
    out, at = [], 0
    for a, b in spans:
        if a < at:
            continue
        out += [text[at:a], "**", text[a:b], "**"]
        at = b
    out.append(text[at:])
    return "".join(out)


def strip_niqqud(s: str) -> str:
    """Without vowel points and cantillation; the maqaf (־) that joins words is kept."""
    return re.sub(r"[\u0591-\u05BD\u05BF-\u05C7]", "", s)


def source_text(d: dict, where: str) -> tuple[str, str]:
    """(passage, default label) for a @source directive."""
    work = d.get("work")
    if work not in S.catalog():
        raise BuildError(f"{where}: unknown work {work!r} (sources/sources.yaml)")
    entry = S.catalog()[work]
    if "page" in d:
        rows = []
        for p in d["page"].split(","):
            vol, page = p.strip().split(":")
            got = S.page_rows(work, int(vol), page)
            if not got:
                raise BuildError(f"{where}: nothing on {work} {p}")
            rows += got
        seen, texts = set(), []
        for a, t in rows:
            texts.append(t)
        addr = d["page"]
        text = " ".join(texts)
        label = f"{entry['title']} · {page_label(d['page'])}"
    else:
        refs = [r.strip() for r in d.get("ref", "").split(",") if r.strip()]
        if not refs:
            raise BuildError(f"{where}: @source needs ref= or page=")
        texts = []
        for r in refs:
            try:
                texts.append(S.text(work, r))
            except KeyError:
                raise BuildError(f"{where}: {work} has no paragraph {r}") from None
        text = " ".join(texts)
        gate = S.gate_title(work, refs[0])
        if len(refs) == 1:
            addr = refs[0]
        elif refs[0].rsplit(".", 1)[0] == refs[-1].rsplit(".", 1)[0]:
            addr = f"{refs[0]}–{refs[-1].rsplit('.', 1)[-1]}"       # same page or chapter: 12a.4–8
        else:
            addr = f"{refs[0]}–{refs[-1]}"                          # across a page: 19a.10–19b.2
        label = " · ".join(x for x in (entry["title"], gate) if x)
    if d.get("niqqud", "no") != "yes":
        text = strip_niqqud(text)
    return text, f"{d.get('label') or label}]{{.makor-label}} [{work} {addr}"


HEB = "אבגדהוזחטיכלמנסעפצקרשת"


def heb_num(n: int) -> str:
    ones = ["", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט"]
    tens = ["", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ"]
    hund = ["", "ק", "ר", "ש", "ת"]
    h, t, o = n // 100, (n % 100) // 10, n % 10
    s = hund[h] + ("טו" if (t, o) == (1, 5) else "טז" if (t, o) == (1, 6) else tens[t] + ones[o])
    return s + "'" if len(s) == 1 else s[:-1] + '"' + s[-1]


def page_label(pages: str) -> str:
    out = []
    for p in pages.split(","):
        vol, page = p.strip().split(":")
        out.append(f"ח\"{HEB[int(vol) - 1]} דף {heb_num(int(page[:-1]))} ע\"{'א' if page[-1] == 'a' else 'ב'}")
    return ", ".join(out)


def file_text(d: dict, where: str) -> tuple[str, str]:
    path = ROOT / d.get("path", "")
    if not path.is_file():
        raise BuildError(f"{where}: no file {d.get('path')!r}")
    raw = path.read_text(encoding="utf-8")
    if raw.startswith("---"):
        raw = raw.split("---", 2)[2]
    if d.get("section"):
        parts = re.split(r"(?m)^(#{1,6} .*)$", raw)
        body = None
        for i in range(1, len(parts), 2):
            if d["section"] in parts[i]:
                body = parts[i + 1]
                break
        if body is None:
            raise BuildError(f"{where}: no heading containing {d['section']!r} in {d['path']}")
        raw = body
    raw = re.sub(r"(?m)^#{1,6} .*$", " ", raw)
    text = re.sub(r"\s+", " ", re.sub(r"[*_]", "", raw)).strip()
    return text, f"{d.get('label') or path.stem}]{{.makor-label}} [{d['path']}"


class TextCursor:
    """The text being explained, consumed in order by @text directives."""

    def __init__(self, meta: dict):
        self.text = ""
        self.at = 0
        self.used = 0
        if not meta.get("text_file"):
            return
        raw = (ROOT / meta["text_file"]).read_text(encoding="utf-8")
        if raw.startswith("---"):
            raw = raw.split("---", 2)[2]
        raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.S)    # a session's ocr.md: its notes and column marks
        raw = re.sub(r"(?m)^#{1,6} .*$", " ", raw)
        raw = re.sub(r"\*\*\[[^\]\n]+\]\*\*", " ", raw)     # the address tags of a generated sources/md file
        text = re.sub(r"\s+", " ", re.sub(r"[*_]", "", raw)).strip()
        self.text, _, _ = cut(text, meta.get("text_from"), meta.get("text_to"), "front matter text_from/text_to")

    def take(self, d: dict, where: str) -> str:
        if not self.text:
            raise BuildError(f"{where}: @text needs text_file in the front matter")
        m = S.locate(self.text, d["from"], self.at) if d.get("from") else (self.at, self.at)
        if not m:
            raise BuildError(f"{where}: @text from= words not found after the previous stretch: {d['from']!r}")
        gap = self.text[self.at:m[0]].strip()
        if gap:
            raise BuildError(f"{where}: words of the text skipped before this stretch: {gap[:120]!r}")
        a = m[0]
        if d.get("to"):
            e = S.locate(self.text, d["to"], a)
            if not e:
                raise BuildError(f"{where}: @text to= words not found: {d['to']!r}")
            b = e[1]
            while b < len(self.text) and self.text[b] in ".,:;)]":
                b += 1
        else:
            b = len(self.text)
        self.at = b
        self.used += b - a
        return self.text[a:b].strip()

    def report(self) -> str:
        if not self.text:
            return ""
        left = self.text[self.at:].strip()
        pct = 100 * self.used // max(1, len(self.text))
        return f"text covered: {pct}%" + (f"; NOT yet reached: {len(left)} characters from {left[:60]!r}" if left else " (whole)")


SECTION_H3 = re.compile(r"^### (\d+)\.")
SECTION_H2 = re.compile(r"^## ([א-ת])\.")
LIST_ITEM = re.compile(r"^(\s*(?:[-*]|\d+\.) )(.*)$")


def number_paragraphs(lines: list[str]) -> tuple[list[str], int]:
    """Number each paragraph of the explanation, per section: [12.3] = section 12, paragraph 3
    (the lettered parts: [ב׳.2]; the foreword: [פתח.1]). The text and the sources (fenced divs),
    headings, tables and blockquotes are not numbered. A remark on the explanation points to its
    place by this number (biur/corrections.yaml)."""
    out, key, n, total, depth, prev = [], None, 0, 0, 0, ""
    for line in lines:
        if line.startswith(":::"):
            depth = depth + 1 if line.strip() != ":::" else max(0, depth - 1)
            out.append(line)
            prev = line
            continue
        if m := SECTION_H3.match(line):
            key, n = m.group(1), 0
        elif m := SECTION_H2.match(line):
            key, n = m.group(1) + "׳", 0
        elif line.startswith("## "):
            h = line[3:].strip()
            key, n = ("פתח" if "פתח דבר" in h else h if len(h.split()) == 1 else None), 0
        starts = prev.strip() == "" or LIST_ITEM.match(line)
        prose = line.strip() and not line.startswith(("#", "|", ">", "[", "<!--")) and not line.strip().startswith("@")
        if key and depth == 0 and starts and prose:
            n += 1
            total += 1
            tag = f"[{key}.{n}]{{.pnum}} "
            m = LIST_ITEM.match(line)
            line = (m.group(1) + tag + m.group(2)) if m else tag + line
        out.append(line)
        prev = line
    return out, total


PNUM = re.compile(r"\[([^\]]+)\]\{\.pnum\}")
PNUM_TAG = re.compile(r"\[[^\]]+\]\{\.pnum\} ")


def group_openings(lines: list[str]) -> list[str]:
    """Keep a section's opening together on one page: its heading, the stretch of the text that
    follows it, and the abbreviations opened right after (a :::: {.opening} block the print keeps
    whole). Only when the heading is followed directly by the text."""
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if line.startswith("### ") and j < len(lines) and lines[j].startswith("::: {.nusach"):
            k = j
            while k < len(lines) and lines[k].strip() != ":::":
                k += 1
            end = k + 1
            m = end
            while m < len(lines) and not lines[m].strip():
                m += 1
            if m < len(lines) and "ראשי התיבות" in lines[m][:80]:
                end = m + 1
            out += [":::: {.opening}", line, ""] + lines[j:end] + ["::::"]
            i = end
            continue
        if line.startswith("### ") and j < len(lines) and lines[j].strip() and not lines[j].startswith(("@", ":::", "#", "|")):
            # A heading followed by prose: keep it with its first paragraph (Chrome ignores
            # break-after: avoid before a paragraph).
            end = j
            while end < len(lines) and lines[end].strip():
                end += 1
            # A one-line lead-in ("...:") belongs with the source it introduces.
            m = end
            while m < len(lines) and not lines[m].strip():
                m += 1
            if lines[end - 1].rstrip().endswith(":") and m < len(lines) and lines[m].startswith("::: {.makor}"):
                k = m
                while k < len(lines) and lines[k].strip() != ":::":
                    k += 1
                end = k + 1
            out += [":::: {.opening}", line, ""] + lines[j:end] + ["::::"]
            i = end
            continue
        out.append(line)
        i += 1
    return out


def add_checks(lines: list[str], data: dict) -> tuple[list[str], int]:
    """Mark each paragraph an open finding of an independent check touches ([⚑ 3]) and print the
    findings as the last part (ז). checks.yaml says which; the explanation's sentences are untouched."""
    findings = [f for f in data.get("findings") or [] if not f.get("settled")]
    if not findings:
        return lines, 0
    marks: dict[str, list[int]] = {}
    for f in findings:
        for p in f.get("places") or []:
            marks.setdefault(str(p), []).append(f["id"])
    seen, out = set(), []
    for line in lines:
        m = PNUM.search(line)
        if m and m.group(1) in marks:
            line = line.rstrip() + " [בדיקה " + ", ".join(str(i) for i in marks[m.group(1)]) + "]{.flag}"
            seen.add(m.group(1))
        out.append(line)
    missing = sorted(set(marks) - seen)
    if missing:
        raise BuildError(f"checks.yaml: no paragraph numbered {', '.join(missing)}")
    out += ["", ":::: {.findings-part}", "## ז. ממצאי הבדיקה העצמאית", ""]
    if data.get("intro"):
        out += [" ".join(str(data["intro"]).split()), ""]
    for f in findings:
        out += ['::: {.finding}', f"**בדיקה {f['id']}. {f['title']}**", "", " ".join(str(f['body']).split()), ""]
        places = ", ".join(str(p) for p in f.get("places") or [])
        out += [f"[מקור: {f.get('evidence', '')} · פסקאות: {places}]{{.finding-meta}}", ":::", ""]
    out.append("::::")
    return out, len(seen)


FORBIDDEN = [   # prompts/biur-rules.md: what never prints in an explanation
    (re.compile(r"\*\*ראשי התיבות:?\*\*"), "opened abbreviations (rule 1)"),
    (re.compile(r"\*\*היכן אפשר לטעות"), "'where one can go wrong' (rule 2)"),
    (re.compile(r"\*\*מידת הוודאות"), "certainty note (rule 3)"),
    (re.compile(r"\((?:זו )?השערה[^)]{0,20}\)|מוכרח מן ההקשר"), "certainty tag (rule 3)"),
    (re.compile(r"לפניי|הבנתי|לא מצאתי|נראה לי|איני יודע|אני קורא|אכתוב|(?<!כמו ש)כתבתי|זיהיתי|ביקשתי|(?<![א-ת])(?:שלי|אני|ראיתי)(?![א-ת])"), "the writer in the first person (rule 4)"),
    (re.compile(r"שים לב|כדאי לראות|נבנה הביאור"), "instruction to the reader (rule 5)"),
    (re.compile(r"Claude|בינה מלאכותית|במאגר|שבמאגר|\bsources/|\{\.byline\}"), "how it was made: byline, repository (rules: In the explanation)"),
    (re.compile(r"^## (?!מבוא$|סיכום$|ז\. )"), "method heading: only מבוא, the numbered sections and סיכום (rule 6)"),
    (re.compile(r"^\*\*ביאור[^*]{0,20}\.\*\*"), "label inside the explanation (rule 7)"),
]


EN_HEADING = re.compile(r"^## (?!Introduction$|Summary$)")      # an English explanation (lang: en)


def lint(body: str, first_line: int, headings: list[str] | None = None, english: bool = False) -> list[str]:
    """The lines of the hand-written source that break prompts/biur-rules.md (quotations excepted).
    `headings`: part headings the document declares besides מבוא and סיכום (front matter `headings:`)."""
    errs = []
    allowed = {f"## {h}" for h in headings or []}
    for no, line in enumerate(body.split("\n"), first_line):
        if line.startswith("@") or line.startswith("# ") or re.sub(r"\s*\{[^{}]*\}\s*$", "", line.strip()) in allowed:
            continue
        prose = re.sub(r"\*\*.+?\*\*", " ", line)                    # a woven text's own words (bold) are not the writer's
        prose = re.sub(r'(?<=[א-ת])["״](?=[א-ת](?![א-ת]))', "", prose)  # the gershayim of an abbreviation, before its last letter (ע"א, דא"ס), is not a quote mark
        prose = re.sub(r'"[^"\n]*"|״[^״\n]*״', '""', prose)          # what is quoted is not the writer's
        for pat, why in FORBIDDEN:
            if why.startswith("method") and english:
                pat = EN_HEADING
            head = re.sub(r"\s*\{[^{}]*\}\s*$", "", line) if line.startswith("#") else line  # a heading's {.class}: layout only
            if pat.search(prose if not why.startswith("method") else head):
                errs.append(f"line {no}: {why}: {line.strip()[:70]!r}")
                break
    return errs


MEANING_OPEN = "::: {.meaning}"

FOOTNOTE = re.compile(r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]\{\.fn\}")


def section_counts(body: str) -> dict[str, tuple[int, int]]:
    """For each numbered section (### N.), the number of bold stretches and of footnotes."""
    out, key = {}, None
    # A stretch continued in a new paragraph (a translation may break a long sentence of the text into
    # paragraphs) is marked so: "…**", blank line, "<!--cont-->**…". It counts as one stretch.
    body = re.sub(r"\*\*[ \t]*\n[ \t]*\n[ \t]*<!--cont-->\*\*", " ", body)
    for part in re.split(r"(?m)^(### \d+\.)", strip_meaning(body)):
        m = re.match(r"### (\d+)\.", part)
        if m:
            key = m.group(1)
            continue
        if key:
            fns = len(FOOTNOTE.findall(part))
            out[key] = (len(re.findall(r"\*\*(.+?)\*\*", FOOTNOTE.sub(" ", part), flags=re.S)), fns)
    return out


def mirror_check(body: str, original: Path) -> str:
    """A translation of a woven explanation (front matter `mirror:` = the original's biur.src.md): section by
    section, the same number of stretches of the text (bold) and of footnotes as the original, so that no
    stretch is skipped or merged."""
    raw = original.read_text(encoding="utf-8")
    want = section_counts(raw.split("---", 2)[2] if raw.startswith("---") else raw)
    got = section_counts(body)
    bad = [f"§{k}: {got.get(k, (0, 0))} for {want[k]}" for k in want if got.get(k) != want[k] and k in got]
    missing = [k for k in want if k not in got]
    if bad:
        raise BuildError("mirror: (stretches, footnotes) differ from the original in " + "; ".join(bad))
    return f"mirror: {len(got)} of {len(want)} sections match the original" + (f"; not yet: §{missing[0]}–§{missing[-1]}" if missing else "")


def woven_check(body: str, text: str) -> str:
    """A woven explanation (front matter `woven: true`): the words of the text are set in bold
    (**...**) inside the explanation, in order. Every bold word, read in order, must be the text
    itself, word for word and whole; the footnotes, headings and meaning blocks are not read."""
    prose = strip_meaning(body)
    prose = FOOTNOTE.sub(" ", prose)
    prose = "\n".join(l for l in prose.split("\n") if not l.startswith("#"))
    got = " ".join(re.findall(r"\*\*(.+?)\*\*", prose, flags=re.S)).split()
    want = text.split()
    for i, (g, w) in enumerate(zip(got, want)):
        if g != w:
            raise BuildError(f"woven text: word {i + 1} is {g!r}, the text has {w!r}: "
                             f"…{' '.join(want[max(0, i - 6):i])} [{w}] {' '.join(want[i + 1:i + 6])}…")
    if len(got) > len(want):
        raise BuildError(f"woven text: {len(got) - len(want)} bold word(s) after the end of the text: {' '.join(got[len(want):])[:80]!r}")
    pct = 100 * len(got) // max(1, len(want))
    left = " ".join(want[len(got):])
    return f"woven text: {len(got)} of {len(want)} words ({pct}%)" + (f"; NOT yet reached from {left[:60]!r}" if left else ", whole and in order")


def meaning_blocks(body: str) -> list[str]:
    return re.findall(r"^::: \{\.meaning\}\n(.*?)\n:::$", body, flags=re.S | re.M)


def strip_meaning(body: str) -> str:
    return re.sub(r"\n?^::: \{\.meaning\}\n.*?\n:::$\n?", "\n", body, flags=re.S | re.M)


def terms_key(blocks: list[str]) -> list[str]:
    """The key of the terms the meaning layer uses, from knowledge/teacher/terms.yaml."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("teacher_terms", ROOT / "scripts" / "teacher-terms.py")
    tt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tt)
    d = tt.load()
    used = tt.uses(d, "\n".join(blocks))
    if not used:
        return []
    out = ["", "## מפתח המושגים", "",
           "[המושגים כפי שהם בנפש האדם, כפי שהם מתבארים בשיעורי שער היחוד ולבושי הנשמה. "
           "\"יישום\": החלת אותה מסגרת על מושג שלא נתבאר שם בפירוש.]{.terms-intro}", ""]
    for t in used:
        if t.get("said"):
            where = "; ".join(dict.fromkeys(tt.label(x["where"]) for x in t["said"]))
            out += [f"**{t['term']}**: {' '.join(t['soul'].split())} [{where}]{{.terms-src}}", ""]
        else:
            out += [f"**{t['term']}** (יישום): {' '.join(t['applied'].split())}", ""]
    return out


def build(src: Path, with_checks: bool = False, meaning: bool = True) -> tuple[str, dict, list[str]]:
    raw = src.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    blocks = meaning_blocks(body)
    if not meaning:
        head_len = len(raw) - len(body)
        body = strip_meaning(body)
        raw = raw[:head_len] + body
    errs = lint(body, raw[: len(raw) - len(body)].count("\n") + 1, meta.get("headings"), meta.get("lang") == "en")
    if errs:
        raise BuildError("the source breaks prompts/biur-rules.md:\n  " + "\n  ".join(errs))
    cursor = TextCursor(meta)
    out, notes, n_src = [], [], 0
    if meta.get("mirror"):
        notes.append(mirror_check(body, (src.parent / meta["mirror"]).resolve()))
    if meta.get("woven"):
        if not cursor.text:
            raise BuildError("woven: true needs text_file in the front matter")
        notes.append(woven_check(body, cursor.text))
        # Skill lean-biur (Ronnie, 2026-11-24): a gloss gives a term or a source, never the text again.
        import importlib.util
        spec = importlib.util.spec_from_file_location("restate", Path(__file__).with_name("check-restatement.py"))
        restate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(restate)
        n_gl, n_flag, _ = restate.tally(body)
        notes.append(f"lean check: {n_gl} gloss(es), {n_flag} read as restating the text"
                     + (" (python scripts/check-restatement.py; skill lean-biur)" if n_flag else ""))
    for no, line in enumerate(body.split("\n"), raw[: len(raw) - len(body)].count("\n") + 1):
        m = DIRECTIVE.match(line)
        if not m:
            out.append(line)
            if line.strip() == MEANING_OPEN:
                out += ["[בנפש האדם]{.meaning-label}", ""]
            continue
        kind, d = m.group(1), args_of(m.group(2), no)
        where = f"line {no}"
        if kind == "text":
            t = cursor.take(d, where)
            # A long stretch may break across pages (`.long`); a short one is kept whole.
            cls = "{.nusach .long}" if len(t) > LONG_STRETCH else "{.nusach}"
            out += [f'::: {cls}', bold(t, d.get("mark"), where), ":::"]
            continue
        text, label = source_text(d, where) if kind == "source" else file_text(d, where)
        passage, head, tail = cut(text, d.get("from"), d.get("to"), where)
        passage = bold(passage, d.get("mark"), where)
        passage = emend(passage, d.get("emend"), where)
        passage = ("… " if head else "") + passage + (" …" if tail else "")
        n_src += 1
        out += ['::: {.makor}', f"[{label}]{{.addr}}", "", passage]
        if d.get("note"):
            out += ["", f"[{d['note']}]{{.makor-note}}"]
        out.append(":::")
    notes.append(f"{n_src} source passage(s) set in")
    if meaning and blocks:
        key = terms_key(blocks)
        out += key
        notes.append(f"{len(blocks)} meaning block(s); {sum(1 for k in key if k.startswith('**'))} term(s) in the key")
    if meta.get("open_abbreviations"):
        out, n_open = open_abbreviations(out, src.parent / meta["open_abbreviations"])
        notes.append(f"{n_open} abbreviation(s) printed in full words")
    if meta.get("woven"):
        # A line must not open with the punctuation that follows a stretch of the text or a footnote call:
        # a word joiner (U+2060, not printed) binds it to what precedes it.
        out = [re.sub(r"(?<=\S)(\*\*|\]\{\.fn\})(?=[.:;,)\[])", "\\1\u2060", l) for l in out]
    out, n_par = number_paragraphs(out)
    notes.append(f"{n_par} paragraph(s) of explanation numbered")
    out = group_openings(out)
    checks = src.parent / "checks.yaml"
    if with_checks and checks.is_file():
        out, n_flag = add_checks(out, yaml.safe_load(checks.read_text(encoding="utf-8")) or {})
        notes.append(f"{n_flag} paragraph(s) marked from checks.yaml")
    if cursor.text and not meta.get("woven"):
        notes.append(cursor.report())
    meta_out = dict(meta)
    meta_out["built_from"] = src.name
    front = "---\n" + yaml.safe_dump(meta_out, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
    return front + "\n".join(out), meta, notes


HEB = "\u05d0-\u05ea"
# An abbreviation: gershayim before its last letter, or a geresh after it. A quotation mark may stand beside it
# ("אפי' ... שבשמי'"), but not one that joins it to a word (ו"שעת).
ABBR = re.compile(rf"(?<![{HEB}'])(?<![{HEB}]\")[{HEB}]*(?:[{HEB}]\"[{HEB}]|[{HEB}]')(?![{HEB}']|\"[{HEB}])")
PREFIXES = "ובכלמשהד"


def open_abbreviations(lines: list[str], table_file: Path) -> tuple[list[str], int]:
    """Every abbreviation printed in its full words, from a table (front matter `open_abbreviations:`): its
    `phrases` (a reading that depends on the words around it) first, then each abbreviation by its `words`,
    found with or without prefix letters; `keep` prints as written, and so does a `[...]{.asis}` span. One that is in
    none of them fails the build."""
    t = yaml.safe_load(table_file.read_text(encoding="utf-8")) or {}
    words, keep = t.get("words") or {}, set(t.get("keep") or [])
    phrases = sorted((t.get("phrases") or {}).items(), key=lambda kv: -len(kv[0]))
    count, unknown = 0, set()

    def word(m: re.Match) -> str:
        nonlocal count
        tok = m.group(0)
        for i in range(0, 4):
            pre, base = tok[:i], tok[i:]
            if i and pre[-1] not in PREFIXES:
                break
            if base in keep:
                return tok
            if base in words:
                count += 1
                return pre + words[base]
        unknown.add(tok)
        return tok

    def open_part(part: str) -> str:
        nonlocal count
        for a, b in phrases:
            part, n = re.subn(rf"(?<![{HEB}]){re.escape(a)}(?![{HEB}])", b, part)
            count += n
        return ABBR.sub(word, part)

    out = []
    for line in lines:
        # `[...]{.asis}` prints as written: an abbreviation shown as an abbreviation.
        parts = re.split(r"(\[[^\[\]]*\]\{\.asis\})", line)
        out.append("".join(p if i % 2 else open_part(p) for i, p in enumerate(parts)))
    if unknown:
        raise BuildError(f"open_abbreviations: not in {table_file.name}: " + " ".join(sorted(unknown)))
    return out, count


def chrome() -> str:
    for name in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(name):
            return shutil.which(name)
    raise BuildError("Chrome not found on the PATH")


def to_pdf(md: Path, meta: dict, pdf: Path) -> None:
    pdf.parent.mkdir(parents=True, exist_ok=True)
    htm = pdf.with_suffix(".html")
    title = meta.get("title", md.stem)
    import os
    cmd = ["pandoc", str(md), "-f", "markdown+fenced_divs+bracketed_spans+pipe_tables-smart", "-t", "html5", "--standalone", "--wrap=none",
           "--metadata", f"pagetitle={title}", "--metadata", f"lang={meta.get('lang', 'he')}", "--metadata", f"dir={'ltr' if meta.get('lang') == 'en' else 'rtl'}",
           "--css", os.path.relpath(CSS, htm.parent), "-o", str(htm)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise BuildError("pandoc: " + r.stderr.strip()[-800:])
    extra = [ROOT / c for c in ([meta["css"]] if isinstance(meta.get("css"), str) else meta.get("css") or [])]
    if meta.get("engine") == "weasyprint":
        # WeasyPrint sets footnotes at the foot of the page ([...]{.fn}, `float: footnote`), which Chrome cannot.
        from weasyprint import CSS as WCSS, HTML
        from weasyprint.text.fonts import FontConfiguration
        fc = FontConfiguration()
        page = re.sub(r'<link rel="stylesheet"[^>]*>', "", htm.read_text(encoding="utf-8"))
        page = re.sub(r"<style>.*?</style>", "", page, flags=re.S)
        sheets = [WCSS(filename=str(f), font_config=fc) for f in [CSS] + extra]
        doc = HTML(string=page, base_url=str(CSS.parent)).render(stylesheets=sheets, font_config=fc)
        n = len(doc.pages)
        if meta.get("fold") and n % 4 and 'class="works"' in page:
            # Printed as a folded, stapled booklet: the pages must come to a multiple of four, or the printer
            # adds blank pages after the closing page and it lands inside the back cover. Blank pages go
            # before it instead, so the closing page is the outside of the back.
            blanks = '<div class="blankpage">&#160;</div>' * (4 - n % 4)
            page = page.replace('<div class="works">', blanks + '<div class="works">', 1)
            doc = HTML(string=page, base_url=str(CSS.parent)).render(stylesheets=sheets, font_config=fc)
            print(f" · fold: {n} pages, {4 - n % 4} blank before the closing page → {len(doc.pages)}")
        doc.write_pdf(pdf)
        return
    if extra:
        page = htm.read_text(encoding="utf-8")
        links = "".join(f'<link rel="stylesheet" href="{os.path.relpath(f, htm.parent)}" />' for f in extra)
        htm.write_text(page.replace("</head>", links + "</head>"), encoding="utf-8")
    r = subprocess.run([chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--allow-file-access-from-files", f"--print-to-pdf={pdf}", str(htm)],
                       capture_output=True, text=True, timeout=600)
    if not pdf.exists():
        raise BuildError("Chrome did not write the PDF: " + r.stderr.strip()[-600:])


def main(argv: list[str]) -> int:
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    folder = (ROOT / paths[0]) if not Path(paths[0]).is_absolute() else Path(paths[0])
    src = folder / "biur.src.md"
    if not src.is_file():
        print(f"no {src}")
        return 2
    try:
        review = "--review" in argv or "--checks" in argv
        meaning = "--no-meaning" not in argv
        text, meta, notes = build(src, meaning=meaning)
        if "--check" not in argv and meaning:
            (folder / "biur.md").write_text(text + "\n", encoding="utf-8")
            print(f"wrote {(folder / 'biur.md').relative_to(ROOT)}")
        for n in notes:
            print(" ·", n)
        if "--pdf" in argv:
            name = meta.get("pdf_name") or folder.parent.name
            if review:      # paragraph numbers and the open findings of a check: a copy for review only
                text, _, _ = build(src, with_checks=True, meaning=meaning)
                pdf = ROOT / "output" / "biur" / "review" / f"{name}.pdf"
            else:           # the finished document: no numbers, no marks
                text = PNUM_TAG.sub("", text)
                pdf = ROOT / "output" / "biur" / ("" if meaning else "plain") / f"{name}.pdf"
            md = pdf.with_suffix(".md")
            pdf.parent.mkdir(parents=True, exist_ok=True)
            md.write_text(text + "\n", encoding="utf-8")
            to_pdf(md, meta, pdf)
            print(f"wrote {pdf.relative_to(ROOT)}")
    except BuildError as e:
        print(f"ERROR: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
