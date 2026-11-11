#!/usr/bin/env python3
"""Look up a passage in the reference works kept in sources/.

Usage:
    python scripts/source-lookup.py 'ע"ח שמ"ט פ"ה'               # a citation as our texts write it
    python scripts/source-lookup.py etz-chaim 49.5               # a Sefaria address (gate.chapter[.paragraph])
    python scripts/source-lookup.py --find 'אלו הלבושים'         # every place a phrase occurs
    python scripts/source-lookup.py --find 'גלות השכינה' etz-chaim 26
    python scripts/source-lookup.py --gates etz-chaim            # each gate's address and name
    python scripts/source-lookup.py --page zohar 2 229b          # a printed page (volume, page) of the Zohar
    python scripts/source-lookup.py --page mikdash-melekh 1 36b  # ... or of Mikdash Melekh on that page

A citation prints the whole chapter it names, paragraph by paragraph with
addresses, plus the work's numbering notes: older editions number some gates
and chapters differently, so check that the passage the citation quotes is
there (--find on its words settles it). --find matches on letters only
(niqqud, quote marks and punctuation ignored) and prints each hit with
context, the match in 【】.

Works and their files: sources/sources.yaml.
"""
from __future__ import annotations

import sys

import sourcelib as S

CONTEXT = 220


def show(work: str, address: str) -> int:
    rows = S.under(work, address)
    if not rows:
        print(f"{work}: nothing at {address}")
        return 1
    entry = S.catalog()[work]
    print(f"# {entry['title']} {address} — {S.gate_title(work, address)}\n")
    for a, t in rows:
        print(f"[{a}] {t}\n")
    for n in entry.get("numbering", []):
        print(f"· {n}")
    return 0


def find(phrase: str, work: str | None, prefix: str) -> int:
    works = [work] if work else list(S.catalog())
    n = 0
    for w in works:
        for a, s, e in S.find(w, phrase, prefix):
            t = S.text(w, a)
            print(f"--- {w} {a}  ({S.gate_title(w, a)})")
            print(("…" if s > CONTEXT else "") + t[max(0, s - CONTEXT):s] + "【" + t[s:e] + "】"
                  + t[e:e + CONTEXT] + ("…" if e + CONTEXT < len(t) else "") + "\n")
            n += 1
    print(f"{n} match(es)")
    return 0 if n else 1


def gates(work: str) -> int:
    named = S.named_gates(work)
    keys = named or sorted({a.split(".")[0] for a in S.paragraphs(work)}, key=lambda k: (not k.isdigit(), int(k) if k.isdigit() else 0, k))
    for i, k in enumerate(keys, 1):
        print(f"{i:>3}  {k:<45} {S.gate_title(work, k)}")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--find":
        if len(argv) < 2:
            print("--find needs a phrase")
            return 2
        return find(argv[1], argv[2] if len(argv) > 2 else None, argv[3] if len(argv) > 3 else "")
    if argv[0] == "--page":
        if len(argv) < 4:
            print("--page needs a work, a volume and a page, e.g. --page zohar 2 229b")
            return 2
        rows = S.page_rows(argv[1], int(argv[2]), argv[3])
        if not rows:
            print(f"{argv[1]}: nothing on volume {argv[2]} page {argv[3]}")
            return 1
        print(f"# {S.catalog()[argv[1]]['title']} — volume {argv[2]}, page {argv[3]}\n")
        for a, t in rows:
            print(f"[{a}] {t}\n")
        return 0
    if argv[0] == "--gates":
        return gates(argv[1] if len(argv) > 1 else "etz-chaim")
    if argv[0] in S.catalog():
        if len(argv) < 2:
            print("give an address, e.g. 49.5")
            return 2
        return show(argv[0], argv[1])
    try:
        work, address = S.parse_cite(" ".join(argv))
    except ValueError as e:
        print(e)
        return 2
    return show(work, address)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
