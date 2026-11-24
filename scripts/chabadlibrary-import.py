#!/usr/bin/env python3
"""Turn a text taken from chabadlibrary.org (kept as a session's ocr.md: one "## Source: <url>" section
per printed column, each marked <!-- מט ע"א -->) into a JSON the source scripts read, shaped like a
Sefaria export, so that the lexicon and the ביאורים can quote it by address and have the quotation checked.

Usage:
    python scripts/chabadlibrary-import.py padah-beshalom      # works named in sources/sources.yaml
    python scripts/chabadlibrary-import.py --check             # every such work: JSON up to date?

The text stays where it was taken in (`raw:` in sources.yaml, the session's ocr.md, final once ingested,
never edited); the JSON (`file:`) is generated from it, so it is never edited either. A work enters
sources/ this way when a discourse made from it is done, so the next discourse can lean on it.

Addresses are folio and column: "49a" is מט ע"א, "49c" מט ע"ג (four columns to a folio, as the
edition prints them), then the paragraph: "49c.2". The site breaks columns where the print does, often
mid-sentence: a quotation that runs over a column break takes both addresses ("49c.3,49d.1").

A work taken in chapter by chapter, one session each (`raw:` a glob, `address: chapter`), is addressed by
chapter and printed page within it: "12.2" is the second page of פרק יב (its heading names the page, 'פרק
יב, קיט ע"ב'), so a citation "שער היחוד פי"ב" is ref "12". Sessions are read in order, the Nth is פרק N.
"""
from __future__ import annotations

import json
import re
import sys

import sourcelib as S

COLUMN = re.compile(r"<!--\s*([א-ת\"']+)\s+ע\"([אבגד])\s*-->")
SIDES = {"א": "a", "ב": "b", "ג": "c", "ד": "d"}


def heb(n: int) -> str:
    ones, tens = " אבגדהוזחט", " יכלמנסעפצ"
    s = ("טו" if n % 100 == 15 else "טז" if n % 100 == 16 else (tens[n % 100 // 10] + ones[n % 10]).replace(" ", ""))
    return "ק" * (n // 100) + s


def pages(raw: str):
    marks = list(COLUMN.finditer(raw))
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        chunk = re.sub(r"(?m)^## Source:.*$", "", raw[m.end():end])
        chunk = re.sub(r"<!--.*?-->", "", chunk, flags=re.S)
        yield m, " ".join(re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", chunk) if p.strip())


def build_chapters(work: str, entry: dict) -> tuple[dict, list]:
    files = sorted(S.ROOT.glob(entry["raw"]))
    if not files:
        raise SystemExit(f"{work}: no files match {entry['raw']}")
    text, nodes = {}, []
    for n, f in enumerate(files, 1):
        parts = [(m, t) for m, t in pages(f.read_text(encoding="utf-8")) if t]
        if not parts:
            raise SystemExit(f"{work}: no page marks in {f}")
        text[str(n)] = [t for _, t in parts]
        first, last = parts[0][0], parts[-1][0]
        span = f'{first.group(1)} ע"{first.group(2)}' + (f' – {last.group(1)} ע"{last.group(2)}' if last is not first else "")
        nodes.append({"enTitle": str(n), "heTitle": f"פרק {heb(n)}, {span}"})
    return text, nodes


def build(work: str) -> dict:
    entry = S.catalog()[work]
    if entry.get("address") == "chapter":
        text, nodes = build_chapters(work, entry)
        return {"title": entry.get("en_title", work), "heTitle": entry["title"], "language": "he",
                "versionTitle": entry.get("version", ""), "versionSource": entry.get("from", ""),
                "generated_by": "scripts/chabadlibrary-import.py (do not edit; rerun the script)",
                "generated_from": entry["raw"], "schema": {"nodes": nodes}, "text": text}
    raw = (S.ROOT / entry["raw"]).read_text(encoding="utf-8")
    marks = list(COLUMN.finditer(raw))
    if not marks:
        raise SystemExit(f"{work}: no column marks (<!-- מט ע\"א -->) in {entry['raw']}")
    text: dict[str, list[str]] = {}
    nodes = []
    for i, m in enumerate(marks):
        n = S.numeral(m.group(1).replace('"', "").replace("'", ""))
        key = f"{n}{SIDES[m.group(2)]}"
        if key in text:
            raise SystemExit(f"{work}: column {key} appears twice")
        end = marks[i + 1].start() if i + 1 < len(marks) else len(raw)
        chunk = re.sub(r"(?m)^## Source:.*$", "", raw[m.end():end])
        chunk = re.sub(r"<!--.*?-->", "", chunk, flags=re.S)
        text[key] = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", chunk) if p.strip()]
        nodes.append({"enTitle": key, "heTitle": f'{m.group(1)} ע"{m.group(2)}'})
    return {
        "title": entry.get("en_title", work),
        "heTitle": entry["title"],
        "language": "he",
        "versionTitle": entry.get("version", ""),
        "versionSource": entry.get("from", ""),
        "generated_by": "scripts/chabadlibrary-import.py (do not edit; rerun the script)",
        "generated_from": entry["raw"],
        "schema": {"nodes": nodes},
        "text": text,
    }


def main(argv: list[str]) -> int:
    check = "--check" in argv
    works = [a for a in argv if not a.startswith("--")] or [
        w for w, e in S.catalog().items() if e.get("importer") == "chabadlibrary"]
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(out, encoding="utf-8")
        paras = sum(len(v) for v in data["text"].values())
        print(f"{work}: {len(data["text"])} parts, {paras} paragraphs → {path.relative_to(S.ROOT)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
