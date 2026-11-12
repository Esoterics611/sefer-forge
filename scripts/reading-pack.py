#!/usr/bin/env python3
"""Build a reading pack: the sources of a subject cut by address from sources/ and set
in the order a plan gives (e.g. the stages of Shacharit), so a writing session reads
each stage in one file instead of hunting through whole works.

Usage:
    python scripts/reading-pack.py discourses/005-kavanot-shacharit/reading           # build
    python scripts/reading-pack.py discourses/005-kavanot-shacharit/reading --check   # stale?

The plan (`plan.yaml` in that folder) lists stages; each stage lists passages by
address: `ref:` (everything at or under an address) or `from:` / `to:` (address
prefixes, inclusive, in book order). Lists named in LEVELS become folders:

    stages[].arizal             → arizal/<id>-<slug>.md
    stages[].rashash            → rashash/<id>-<slug>.md
    rashash_foundations[]       → rashash/<id>-<slug>.md
    chasdei_david[]             → chasdei-david/<id>-<slug>.md

Each file opens with an index (address, length, opening words of every paragraph),
then the text, every paragraph headed by its address, exactly as scripts/source-lookup.py
gives it. README.md lists every file with its size. Everything here is generated: change
the plan and rebuild, never the files.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

import sourcelib as S

INCIPIT_WORDS = 14


def select(p: dict) -> list[tuple[str, str]]:
    rows = list(S.paragraphs(p["work"]).items())
    under = lambda a, pre: a == pre or a.startswith(pre + ".")  # noqa: E731
    if "ref" in p:
        out = [(a, r) for a, r in rows if under(a, p["ref"])]
    else:
        start = next((i for i, (a, _) in enumerate(rows) if under(a, p["from"])), None)
        last = [i for i, (a, _) in enumerate(rows) if under(a, p["to"])]
        if start is None or not last:
            raise SystemExit(f"{p['work']}: no paragraph at {p.get('from')} or {p.get('to')}")
        out = rows[start:last[-1] + 1]
    if not out:
        raise SystemExit(f"{p['work']}: nothing at {p}")
    return [(a, S.clean(r)) for a, r in out]


def label(p: dict) -> str:
    title = S.catalog()[p["work"]]["title"]
    first = p.get("ref") or p["from"]
    gate = S.gate_title(p["work"], first)
    where = p["ref"] if "ref" in p else f"{p['from']} – {p['to']}"
    return f"{title}{' — ' + gate if gate and gate != title else ''} ({where})"


def incipit(t: str) -> str:
    w = t.split()
    return " ".join(w[:INCIPIT_WORDS]) + (" …" if len(w) > INCIPIT_WORDS else "")


def render(entry: dict, passages: list[dict], level: str, plan_rel: str) -> tuple[str, int, dict]:
    chosen = [(p, select(p)) for p in passages]
    sizes: dict[str, int] = {}
    for p, rows in chosen:
        sizes[p["work"]] = sizes.get(p["work"], 0) + sum(len(t) for _, t in rows)
    total = sum(sizes.values())
    head = [
        "---",
        f'stage: "{entry["id"]}"',
        f'title: "{entry["title"].replace(chr(34), chr(92) + chr(34))}"',
        f"level: {level}",
        f"plan: {plan_rel}",
        "generated_by: scripts/reading-pack.py (do not edit; change the plan and rebuild)",
        "---",
        "",
        f"# {entry['id']}. {entry['title']}",
        "",
    ]
    if entry.get("covers"):
        head += [f"*{entry['covers']}*", ""]
    head += ["Size: " + ", ".join(f"{S.catalog()[w]['title']} {n:,} chars" for w, n in sizes.items())
             + f"; total {total:,}.", ""]
    index = ["## מפתח", ""]
    body = ["## הטקסט", ""]
    for p, rows in chosen:
        index += [f"### {label(p)}" + (f" — {p['note']}" if p.get("note") else ""), ""]
        body += [f"### {label(p)}", ""]
        for a, t in rows:
            if len(t) < 40:                       # a heading line: "דרוש ב':"
                index.append(f"- **{t}** [{a}]")
            else:
                index.append(f"- [{a}] ({len(t):,}) {incipit(t)}")
            body += [f"**[{a}]** {t}", ""]
        index.append("")
    return "\n".join(head + index + body).rstrip() + "\n", total, sizes


def build(folder: Path, check: bool) -> int:
    plan = yaml.safe_load((folder / "plan.yaml").read_text(encoding="utf-8"))
    plan_rel = (folder / "plan.yaml").relative_to(S.ROOT).as_posix()
    jobs = []
    for st in plan.get("stages", []):
        for level in ("arizal", "rashash"):
            if st.get(level):
                jobs.append((level, st, st[level]))
    for st in plan.get("rashash_foundations", []):
        jobs.append(("rashash", st, st["passages"]))
    for st in plan.get("chasdei_david", []):
        jobs.append(("chasdei-david", st, st["passages"]))
    order = ["arizal", "rashash", "chasdei-david"]
    jobs.sort(key=lambda j: order.index(j[0]))           # stable: the plan's order inside a level

    readme = [
        "---",
        "generated_by: scripts/reading-pack.py (do not edit; change plan.yaml and rebuild)",
        "---",
        "",
        "# The reading pack",
        "",
        "Every file: an index (address, length in characters, opening words of each paragraph),",
        "then the text, each paragraph headed by the address `scripts/source-lookup.py` and the",
        "`@source` directive of `scripts/build-biur.py` use. Read the index first, then the text.",
        "",
    ]
    stale = 0
    current_level = None
    for level, st, passages in jobs:
        text, total, sizes = render(st, passages, level, plan_rel)
        path = folder / level / f"{st['id']}-{st['slug']}.md"
        if level != current_level:
            readme += ["", f"## {level}", "", "| file | stage | chars |", "|---|---|---|"]
            current_level = level
        split = " · ".join(f"{S.catalog()[w]['title']} {n:,}" for w, n in sizes.items())
        readme.append(f"| [{path.name}]({level}/{path.name}) | {st['title']} | {total:,} ({split}) |")
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                print(f"stale or missing: {path.relative_to(S.ROOT)}")
                stale += 1
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    readme_text = "\n".join(readme) + "\n"
    rp = folder / "README.md"
    if check:
        if not rp.exists() or rp.read_text(encoding="utf-8") != readme_text:
            print(f"stale or missing: {rp.relative_to(S.ROOT)}")
            stale += 1
        print(f"{stale} file(s) to rebuild" if stale else "reading pack is up to date")
        return 1 if stale else 0
    rp.write_text(readme_text, encoding="utf-8")
    print(f"{len(jobs)} file(s) written under {folder.relative_to(S.ROOT)}/")
    return 0


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    folder = Path(args[0]).resolve()
    return build(folder, "--check" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
