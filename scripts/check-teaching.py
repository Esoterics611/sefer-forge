#!/usr/bin/env python3
"""Check the teaching pass (prompts/teaching-pass.md) of a session, or of every
session of a discourse, as it stands recorded.

Usage:
    python scripts/check-teaching.py discourses/004-levushei-haneshama
    python scripts/check-teaching.py discourses/004-levushei-haneshama/sessions/002

Per session: the `teaching:` entries still match the explanation (nothing changed
upstream since), the mechanical checks of apply-teaching.py, words before and
after, and — laid out — that every cut of the text still has an explanation
under it. Across the discourse (the sessions' teaching text and the opening
parts' *.teaching.md): phrases of five words that occur in two places, the
repeats a read-through must decide on.

Exit 1 on an error. Warnings are for the read-through (step 5 of the prompt):
each one is looked at in its sentence, and fixed or left knowingly.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import forgelib as F
import teachlib as T


def session_check(s: Path, texts: list[tuple[str, str]], scan: bool = True) -> tuple[int, int, dict | None]:
    try:
        paras, holder, where = F.printed_paragraphs(s)
    except F.EditError as e:
        print(f"{s.name}: ✗ {e}")
        return 1, 0, None
    if not holder.get("teaching"):
        return 0, 0, None
    print(f"{s.name}  ({where.name})")
    try:
        after = F.apply_teaching(paras, holder["teaching"])
    except F.EditError as e:
        print(f"  ✗ {e}")
        return 1, 0, None
    errors, warns, st = T.check(s, paras, after)
    sec = s / "section.teaching.md"
    if (s / "section-plan.yaml").exists():
        if not sec.exists():
            errors.append("no section.teaching.md: run build-section.py")
        else:
            body = sec.read_text(encoding="utf-8")
            kinds = re.findall(r'^::: \{custom-style="(Nusach|Commentary)"\}', body, flags=re.M)
            lone = sum(1 for k, nxt in zip(kinds, kinds[1:] + ["Nusach"]) if k == "Nusach" and nxt == "Nusach")
            if lone:
                warns.append(f"{lone} cut(s) of the text with no explanation under them in the teaching text")
            printed = [F.para_key(re.sub(r'^\[|\]\{dir="rtl"\}$', "", ln.strip()))
                       for blk in re.findall(r'^::: \{custom-style="Commentary"\}\n(.*?)\n:::', body, re.M | re.S)
                       for ln in blk.split("\n\n") if ln.strip()]
            if printed != [t for t in after if t]:
                errors.append("section.teaching.md is out of date: run build-section.py")
    for e in errors:
        print("  ✗", e)
    for w in warns:
        print("  ⚠", w)
    print(f"  {st['paragraphs']} paragraphs → {st['kept']} · {st['before']} words → {st['after']} "
          f"({st['after'] / max(1, st['before']):.0%})")
    if scan:                     # a session left out of the discourse prints through its opening file
        texts += [(f"{s.name} ¶{i}", t) for i, t in enumerate(after, 1) if t]
    return len(errors), len(warns), st


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    target = Path(argv[0].rstrip("/"))
    sessions = sorted(p for p in (target / "sessions").iterdir() if p.is_dir()) if (target / "sessions").is_dir() \
        else [target]
    discourse = target if (target / "sessions").is_dir() else F.discourse_of(target)
    meta = F.load_yaml(discourse / "meta.yaml")
    skip = {str(x).zfill(3) for x in meta.get("skip_sessions") or []}
    texts: list[tuple[str, str]] = []
    n_err = n_warn = 0
    before = after = 0
    for s in sessions:
        e, w, st = session_check(s, texts, scan=s.name not in skip)
        n_err, n_warn = n_err + e, n_warn + w
        if st:
            before, after = before + st["before"], after + st["after"]
    for f in sorted(discourse.glob("*.teaching.md")):
        if f.name.startswith(("discourse", "section")):
            continue
        _, body, _ = F.split_frontmatter(f.read_text(encoding="utf-8"))
        texts += [(f"{f.name} ¶{i}", F.para_key(b)) for i, b in
                  enumerate([b for b in re.split(r"\n\s*\n", body) if F.prose(b)], 1)]
    if not texts:
        print(f"{target}: no teaching pass recorded")
        return 0
    reps = T.repeats(texts)
    if reps:
        print("repeated phrases (each: one place says it, the other refers to it or drops it):")
        for r in reps:
            print("  ⚠", r)
    print(f"total: {before} words → {after} ({after / max(1, before):.0%}) · {n_err} error(s) · "
          f"{n_warn + len(reps)} warning(s)")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
