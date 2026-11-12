#!/usr/bin/env python3
"""Write the reference works in sources/ as markdown, one file per gate or parashah.

Usage:
    python scripts/source-export.py                 # every work in sources/sources.yaml
    python scripts/source-export.py etz-chaim zohar # only these works
    python scripts/source-export.py --check         # report files that are missing or stale

The JSON exports in sources/ stay the copy the scripts read (never edited). The
markdown under sources/md/<work>/ is the same text for people and for agents to
read, search and link to: each paragraph carries its address, the one
`scripts/source-lookup.py` uses, so a quotation anywhere in the repo can point
at the line it came from. The files are generated; change nothing in them by
hand (a correction is a note where the passage is quoted).

A work kept only as a transcription (no JSON export: a scanned edition read
from its page images) lives under sources/md/<work>/ too, written by hand with
the same front matter and `source: transcription`; this script leaves such
files alone.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import sourcelib as S

OUT = S.ROOT / "sources" / "md"
HEB_ONES = ["", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט"]
HEB_TENS = ["", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ"]
HEB_HUNDREDS = ["", "ק", "ר", "ש", "ת", "תק", "תר", "תש", "תת", "תתק"]


def heb(n: int) -> str:
    """49 → מ"ט, 15 → ט"ו, 5 → ה'."""
    h, t, o = n // 100, (n % 100) // 10, n % 10
    s = HEB_HUNDREDS[h] + ("טו" if (t, o) == (1, 5) else "טז" if (t, o) == (1, 6) else HEB_TENS[t] + HEB_ONES[o])
    return s + "'" if len(s) == 1 else s[:-1] + '"' + s[-1]


def page_label(mark: str) -> str:
    return f"דף {heb(int(mark[:-1]))} ע\"{'א' if mark[-1] == 'a' else 'ב'}"


def body(raw: str) -> str:
    """A paragraph as markdown text: page marks kept as ⟦דף …⟧, other tags dropped."""
    raw = S.PAGE_MARK.sub(lambda m: f" ⟦{page_label(m.group(1))}⟧ ", raw)
    return S.clean(raw)


def slug(key: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", key.lower()).strip("-")


def parts(work: str) -> list[tuple[str, list[tuple[str, str]]]]:
    """[(part key, [(address, raw paragraph)])] in book order; a part is the first
    element of the address (a gate, a parashah, a volume)."""
    out: dict[str, list[tuple[str, str]]] = {}
    for a, raw in S.paragraphs(work).items():
        out.setdefault(a.split(".")[0], []).append((a, raw))
    return list(out.items())


def render(work: str, index: int, key: str, rows: list[tuple[str, str]]) -> tuple[Path, str]:
    entry = S.catalog()[work]
    title = S.gate_title(work, key)
    by_page = isinstance(S.load(work)["text"], list)
    head = f"{entry['title']} — {title}" if title else f"{entry['title']} — {key}"
    name = f"{index:02d}-{slug(key)}.md" if not key.isdigit() else f"{int(key):02d}.md"
    lines = [
        "---",
        f"work: {work}",
        f'title: "{entry["title"]}"',
        f'part: "{key}"',
        *([f'part_title: "{title}"'] if title else []),
        f'from: "{entry.get("sefaria", entry.get("from", ""))}"',
        f'version: {yaml_str(entry.get("version", ""))}',
        f"fetched: {entry.get('fetched', '')}",
        f"generated_from: {entry['file']}",
        "generated_by: scripts/source-export.py (do not edit; rerun the script)",
        "---",
        "",
        f"# {head}",
        "",
    ]
    last = None
    for a, raw in rows:
        bits = a.split(".")
        section = ".".join(bits[:2]) if len(bits) > 2 else None
        if section and section != last:
            n = bits[1]
            if by_page and n.isdigit():
                page = (int(n) + 1) // 2
                label = f"דף {heb(page)} ע\"{'א' if int(n) % 2 else 'ב'}"
            else:
                label = heb(int(n)) if n.isdigit() else n
            lines += [f"## {label} ({section})", ""]
            last = section
        lines += [f"**[{a}]** {body(raw)}", ""]
    return OUT / work / name, "\n".join(lines)


def render_whole(work: str, units: list[tuple[str, list[tuple[str, str]]]]) -> tuple[Path, str]:
    """The whole work in one file, a `##` heading per part (catalog `md: one-file`)."""
    entry = S.catalog()[work]
    lines = [
        "---",
        f"work: {work}",
        f'title: "{entry["title"]}"',
        f'from: "{entry.get("from", "")}"',
        f'version: {yaml_str(entry.get("version", ""))}',
        f"fetched: {entry.get('fetched', '')}",
        f"generated_from: {entry['file']}",
        "generated_by: scripts/source-export.py (do not edit; rerun the script)",
        "---",
        "",
        f"# {entry['title']}",
        "",
    ]
    for key, rows in units:
        lines += [f"## {S.gate_title(work, key) or key} ({key})", ""]
        for a, raw in rows:
            lines += [f"**[{a}]** {body(raw)}", ""]
    return OUT / work / f"{work}.md", "\n".join(lines)


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main(argv: list[str]) -> int:
    check = "--check" in argv
    works = [a for a in argv if not a.startswith("--")] or list(S.catalog())
    stale = written = 0
    for work in works:
        if work not in S.catalog():
            print(f"unknown work: {work} (sources/sources.yaml)")
            return 2
        if not S.catalog()[work].get("file", "").endswith(".json"):
            continue                                   # a transcription kept as markdown
        units = parts(work)
        if S.catalog()[work].get("md") == "one-file":     # a work addressed by printed page (grimoar imports)
            units = [(None, units)]
        for i, (key, rows) in enumerate(units, 1):
            path, text = render(work, i, key, rows) if key is not None else render_whole(work, rows)
            if path.exists() and path.read_text(encoding="utf-8") == text:
                continue
            if check:
                print(f"stale or missing: {path.relative_to(S.ROOT)}")
                stale += 1
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            written += 1
    if check:
        print(f"{stale} file(s) to regenerate" if stale else "sources/md is up to date")
        return 1 if stale else 0
    print(f"{written} file(s) written under sources/md/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
