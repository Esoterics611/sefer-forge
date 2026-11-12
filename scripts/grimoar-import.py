#!/usr/bin/env python3
"""Turn a work saved from hebrew.grimoar.cz (one HTML page, printed pages marked
"דף X עמוד Y") into a JSON the source scripts read, shaped like a Sefaria export.

Usage:
    python scripts/grimoar-import.py nahar-shalom chasdei-david     # works named in sources/sources.yaml
    python scripts/grimoar-import.py --check                        # every grimoar work: JSON up to date?

The HTML is kept exactly as downloaded (`raw:` in sources.yaml, never edited);
the JSON (`file:`) is generated from it by this script, so it is never edited
either. Sefaria's own exports of Etz Chaim, Pri Etz Chaim and Shaar HaKavanot
came from the same site.

Addresses are page.paragraph: "48a.3" is the third paragraph on דף מ"ח ע"א of
the edition the site transcribed. The site breaks paragraphs at the page, so a
sentence can run from the last paragraph of one page into the first of the
next: quote it with both addresses ("48a.9,48b.1").
"""
from __future__ import annotations

import html
import json
import re
import sys

import sourcelib as S

PAGE = re.compile(r"<b>\s*(?:[^<]*?-\s*)?דף\s+([א-ת]+)\s+עמוד\s+([אב])\s*</b>")


def heb_label(n: int, side: str) -> str:
    ones = ["", "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט"]
    tens = ["", "י", "כ", "ל", "מ", "נ", "ס", "ע", "פ", "צ"]
    hund = ["", "ק", "ר", "ש", "ת"]
    h, t, o = n // 100, (n % 100) // 10, n % 10
    s = hund[h] + ("טו" if (t, o) == (1, 5) else "טז" if (t, o) == (1, 6) else tens[t] + ones[o])
    s = s + "'" if len(s) == 1 else s[:-1] + '"' + s[-1]
    return f'דף {s} ע"{side}'


def paragraphs_of(chunk: str) -> list[str]:
    out = []
    for p in re.split(r"(?i)<p[^>]*>|<br\s*/?>", chunk):
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", p)).replace("\xa0", " ")).strip()
        if t:
            out.append(t)
    return out


def build(work: str) -> dict:
    entry = S.catalog()[work]
    raw = (S.ROOT / entry["raw"]).read_bytes().decode(entry.get("encoding", "windows-1255"))
    raw = re.split(r"(?i)</body>", raw)[0]
    marks = list(PAGE.finditer(raw))
    if not marks:
        raise SystemExit(f"{work}: no page marks found in {entry['raw']}")
    text: dict[str, list[str]] = {}
    nodes = []
    for i, m in enumerate(marks):
        n = S.numeral(m.group(1))
        side = m.group(2)
        key = f"{n}{'a' if side == 'א' else 'b'}"
        if key in text:
            raise SystemExit(f"{work}: page {key} appears twice")
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        text[key] = paragraphs_of(raw[m.end():end])
        nodes.append({"enTitle": key, "heTitle": heb_label(n, side)})
    return {
        "title": entry.get("en_title", work),
        "heTitle": entry["title"],
        "language": "he",
        "versionTitle": entry.get("version", ""),
        "versionSource": entry.get("from", ""),
        "generated_by": "scripts/grimoar-import.py (do not edit; rerun the script)",
        "generated_from": entry["raw"],
        "schema": {"nodes": nodes},
        "text": text,
    }


def main(argv: list[str]) -> int:
    check = "--check" in argv
    works = [a for a in argv if not a.startswith("--")] or [
        w for w, e in S.catalog().items() if e.get("raw", "").endswith(".htm")]
    bad = 0
    for work in works:
        data = build(work)
        path = S.ROOT / S.catalog()[work]["file"]
        out = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != out:
                print(f"stale or missing: {path.relative_to(S.ROOT)}")
                bad += 1
            continue
        path.write_text(out, encoding="utf-8")
        paras = sum(len(v) for v in data["text"].values())
        print(f"{work}: {len(data['text'])} pages, {paras} paragraphs → {path.relative_to(S.ROOT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
