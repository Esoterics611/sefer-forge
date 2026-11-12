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

    @file path="sources/md/..." section="..." from="..." to="..." label="..."
        A passage of a markdown file (a transcription): `section` is a
        heading of the file (the text under it), optional.

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
        addr = refs[0] if len(refs) == 1 else f"{refs[0]}–{refs[-1].rsplit('.', 1)[-1]}"
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
        raw = re.sub(r"(?m)^#{1,6} .*$", " ", raw)
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
        if line.startswith("### ") and j < len(lines) and lines[j].startswith("::: {.nusach}"):
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


def lint(body: str, first_line: int) -> list[str]:
    """The lines of the hand-written source that break prompts/biur-rules.md (quotations excepted)."""
    errs = []
    for no, line in enumerate(body.split("\n"), first_line):
        if line.startswith("@") or line.startswith("# "):
            continue
        prose = re.sub(r'"[^"\n]*"|״[^״\n]*״', '""', line)          # what is quoted is not the writer's
        for pat, why in FORBIDDEN:
            if pat.search(prose if not why.startswith("method") else line):
                errs.append(f"line {no}: {why}: {line.strip()[:70]!r}")
                break
    return errs


def build(src: Path, with_checks: bool = False) -> tuple[str, dict, list[str]]:
    raw = src.read_text(encoding="utf-8")
    meta, body = {}, raw
    if raw.startswith("---"):
        _, fm, body = raw.split("---", 2)
        meta = yaml.safe_load(fm) or {}
    errs = lint(body, raw[: len(raw) - len(body)].count("\n") + 1)
    if errs:
        raise BuildError("the source breaks prompts/biur-rules.md:\n  " + "\n  ".join(errs))
    cursor = TextCursor(meta)
    out, notes, n_src = [], [], 0
    for no, line in enumerate(body.split("\n"), raw[: len(raw) - len(body)].count("\n") + 1):
        m = DIRECTIVE.match(line)
        if not m:
            out.append(line)
            continue
        kind, d = m.group(1), args_of(m.group(2), no)
        where = f"line {no}"
        if kind == "text":
            t = cursor.take(d, where)
            out += ['::: {.nusach}', bold(t, d.get("mark"), where), ":::"]
            continue
        text, label = source_text(d, where) if kind == "source" else file_text(d, where)
        passage, head, tail = cut(text, d.get("from"), d.get("to"), where)
        passage = bold(passage, d.get("mark"), where)
        passage = ("… " if head else "") + passage + (" …" if tail else "")
        n_src += 1
        out += ['::: {.makor}', f"[{label}]{{.addr}}", "", passage]
        if d.get("note"):
            out += ["", f"[{d['note']}]{{.makor-note}}"]
        out.append(":::")
    notes.append(f"{n_src} source passage(s) set in")
    out, n_par = number_paragraphs(out)
    notes.append(f"{n_par} paragraph(s) of explanation numbered")
    out = group_openings(out)
    checks = src.parent / "checks.yaml"
    if with_checks and checks.is_file():
        out, n_flag = add_checks(out, yaml.safe_load(checks.read_text(encoding="utf-8")) or {})
        notes.append(f"{n_flag} paragraph(s) marked from checks.yaml")
    if cursor.text:
        notes.append(cursor.report())
    meta_out = dict(meta)
    meta_out["built_from"] = src.name
    front = "---\n" + yaml.safe_dump(meta_out, allow_unicode=True, sort_keys=False, width=1000) + "---\n"
    return front + "\n".join(out), meta, notes


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
    cmd = ["pandoc", str(md), "-f", "markdown+fenced_divs+bracketed_spans+pipe_tables-smart", "-t", "html5", "--standalone",
           "--metadata", f"pagetitle={title}", "--metadata", "lang=he", "--metadata", "dir=rtl",
           "--css", os.path.relpath(CSS, htm.parent), "-o", str(htm)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise BuildError("pandoc: " + r.stderr.strip()[-800:])
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
        text, meta, notes = build(src)
        if "--check" not in argv:
            (folder / "biur.md").write_text(text + "\n", encoding="utf-8")
            print(f"wrote {(folder / 'biur.md').relative_to(ROOT)}")
        for n in notes:
            print(" ·", n)
        if "--pdf" in argv:
            name = meta.get("pdf_name") or folder.parent.name
            if review:      # paragraph numbers and the open findings of a check: a copy for review only
                text, _, _ = build(src, with_checks=True)
                pdf = ROOT / "output" / "biur" / "review" / f"{name}.pdf"
            else:           # the finished document: no numbers, no marks
                text = PNUM_TAG.sub("", text)
                pdf = ROOT / "output" / "biur" / f"{name}.pdf"
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
