#!/usr/bin/env python3
"""Apply the recurring Whisper corrections to a session's raw transcripts.

Usage:
    python scripts/apply-fixes.py discourses/002-shaar-hayichud/sessions/013

For every voicenotes/<audio>.raw.txt writes <audio>.fixed.txt (regenerated on
every run — the .raw.txt itself is never touched), then prints:
  - how many times each `auto` fix fired
  - every `review` hit with surrounding context, for the cleanup pass

Fix lists: glossary/whisper-fixes.yaml, plus the optional
discourses/<NNN-slug>/whisper-fixes.yaml (merged after it).
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml")
    sys.exit(1)

GLOBAL_FIXES = Path("glossary/whisper-fixes.yaml")
HEB = "א-ת"
PREFIX = "[ושהבכלמד]{0,3}"  # Hebrew prefix letters kept in front of a fix
CONTEXT = 30
MAX_REVIEW_HITS = 6


def load_fixes(session: Path) -> tuple[dict[str, str], dict[str, str]]:
    auto: dict[str, str] = {}
    review: dict[str, str] = {}
    sources = [GLOBAL_FIXES]
    # session = discourses/<d>/sessions/<NNN> → discourse-level list
    if session.parent.name == "sessions":
        sources.append(session.parent.parent / "whisper-fixes.yaml")
    for src in sources:
        if src.exists():
            data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
            auto.update(data.get("auto") or {})
            review.update(data.get("review") or {})
    return auto, review


def pattern(wrong: str) -> re.Pattern:
    words = r"\s+".join(re.escape(w) for w in wrong.split())
    return re.compile(rf"(?<![{HEB}])({PREFIX})({words})(?![{HEB}])")


def apply_auto(text: str, auto: dict[str, str]) -> tuple[str, Counter]:
    counts: Counter = Counter()
    # Longest first, so "ממהל כל" wins over any shorter overlapping entry.
    for wrong in sorted(auto, key=len, reverse=True):
        right = auto[wrong]

        def sub(m: re.Match, right=right, wrong=wrong) -> str:
            counts[f"{wrong} → {right}"] += 1
            return m.group(1) + right

        text = pattern(wrong).sub(sub, text)
    return text, counts


def review_hits(text: str, review: dict[str, str]) -> list[str]:
    lines: list[str] = []
    for wrong, right in review.items():
        hits = list(pattern(wrong).finditer(text))
        if not hits:
            continue
        lines.append(f"  {wrong} (usually {right}) — {len(hits)} hit(s)")
        for m in hits[:MAX_REVIEW_HITS]:
            a, b = max(0, m.start() - CONTEXT), m.end() + CONTEXT
            snippet = text[a:m.start()] + "⟦" + m.group(0) + "⟧" + text[m.end():b]
            lines.append("      …" + snippet.replace("\n", " ") + "…")
        if len(hits) > MAX_REVIEW_HITS:
            lines.append(f"      (+{len(hits) - MAX_REVIEW_HITS} more)")
    return lines


def process(raw: Path, auto: dict[str, str], review: dict[str, str]) -> Path:
    text = raw.read_text(encoding="utf-8")
    fixed, counts = apply_auto(text, auto)
    out = raw.with_name(raw.name[: -len(".raw.txt")] + ".fixed.txt")
    out.write_text(fixed, encoding="utf-8")

    print(f"{raw.name} → {out.name}")
    print(f"  auto fixes: {sum(counts.values())}")
    for fix, n in counts.most_common():
        print(f"    {n:3d} × {fix}")
    hits = review_hits(fixed, review)
    if hits:
        print("  review (decide from context; not changed):")
        print("\n".join(hits))
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/apply-fixes.py <session-path>")
        return 1
    session = Path(sys.argv[1])
    raws = sorted((session / "voicenotes").glob("*.raw.txt"))
    if not raws:
        print(f"No *.raw.txt under {session / 'voicenotes'} — run transcribe.py first.")
        return 1
    auto, review = load_fixes(session)
    for raw in raws:
        process(raw, auto, review)
    return 0


if __name__ == "__main__":
    sys.exit(main())
