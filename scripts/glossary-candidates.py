#!/usr/bin/env python3
"""Find recurring Whisper corrections worth adding to glossary/whisper-fixes.yaml.

Usage:
    python scripts/glossary-candidates.py            # corrections made 2+ times
    python scripts/glossary-candidates.py --min 1    # every correction

Compares each session's Whisper text (the .raw.txt with today's auto fixes
applied) with its cleaned text (commentary.md or transcript.md), word for
word as transcript-diff.py does, and collects every short replacement
(up to three words on each side). Corrections already in the glossary, and
ones that only change punctuation, are left out.

Each candidate gets a suggested list: `review` when the wrong form also
stands uncorrected somewhere in the cleaned texts (it is a real word here,
so it must be decided case by case), else `auto`. Prints a table, then
YAML lines ready to paste under `auto:` / `review:`. Changes no file.
"""
from __future__ import annotations

import difflib
import sys
from collections import defaultdict
from pathlib import Path

import forgelib as F
import yaml

DIFF = F.load_script("transcript-diff")
FIXES = F.load_script("apply-fixes")
MAX_WORDS = 3


def cleaned_file(session: Path) -> Path | None:
    for name in ("transcript.md", "commentary.md"):
        if (session / name).exists():
            return session / name
    return None


def covered(old: str, known: set[str]) -> bool:
    """Already in the glossary, which matches across prefix letters (ו ה ב ...)."""
    return any(old[k:] in known for k in range(0, 4) if all(c in F.PREFIXES for c in old[:k]))


def main(argv: list[str]) -> int:
    least = int(argv[argv.index("--min") + 1]) if "--min" in argv else 2
    glossary = yaml.safe_load(Path("glossary/whisper-fixes.yaml").read_text(encoding="utf-8")) or {}
    known = set((glossary.get("auto") or {}) | (glossary.get("review") or {}))

    pairs: dict[tuple[str, str], list[str]] = defaultdict(list)
    vocabulary: set[str] = set()
    for s in F.resolve_sessions([]):
        raws = sorted((s / "voicenotes").glob("*.raw.txt"))
        cleaned = cleaned_file(s)
        if not raws or cleaned is None:
            continue
        auto, _ = FIXES.load_fixes(s)
        before = DIFF.words(" ".join(FIXES.apply_auto(p.read_text(encoding="utf-8"), auto)[0] for p in raws))
        after = DIFF.words(cleaned.read_text(encoding="utf-8"))
        vocabulary.update(after)
        sm = difflib.SequenceMatcher(None, before, after, autojunk=False)
        for op, i1, i2, j1, j2 in sm.get_opcodes():
            if op != "replace" or i2 - i1 > MAX_WORDS or j2 - j1 > MAX_WORDS:
                continue
            old, new = " ".join(before[i1:i2]), " ".join(after[j1:j2])
            if F.plain(old) == F.plain(new) or covered(old, known):
                continue
            pairs[(old, new)].append(f"{F.discourse_of(s).name.split('-', 1)[0]}/{s.name}")

    rows = sorted(((len(v), k, v) for k, v in pairs.items() if len(v) >= least), key=lambda r: (-r[0], r[1]))
    if not rows:
        print(f"No correction made {least}+ times that the glossary lacks.")
        return 0
    auto_lines, review_lines = [], []
    print(f"{'times':>5}  {'Whisper → cleaned':40}  list    sessions")
    for n, (old, new), where in rows:
        real = all(w in vocabulary for w in old.split())
        kind = "review" if real else "auto"
        print(f"{n:>5}  {old + ' → ' + new:40}  {kind:6}  {', '.join(sorted(set(where)))}")
        line = f'  {yaml.safe_dump(old, allow_unicode=True).splitlines()[0]}: ' \
               f'{yaml.safe_dump(new, allow_unicode=True).splitlines()[0]}'
        (review_lines if real else auto_lines).append(line)
    print("\n# under auto:")
    print("\n".join(auto_lines) or "  (none)")
    print("# under review:")
    print("\n".join(review_lines) or "  (none)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
