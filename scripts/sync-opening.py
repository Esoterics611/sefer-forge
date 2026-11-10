#!/usr/bin/env python3
"""Carry a session's refined text into an opening part of its discourse.

Usage:
    python scripts/sync-opening.py <session> <opening.md> [--check]
    python scripts/sync-opening.py discourses/004-levushei-haneshama/sessions/001 \\
        discourses/004-levushei-haneshama/introduction.md

An opening part (meta.yaml `intro:`, e.g. introduction.md) prints before the
discourse's sessions. When it is made from a session's recordings, it holds that
session's text as it reads after the passes, without the recording-part labels:
the paragraphs of <session>/refined.md go into <opening>.md, and those of
<session>/refined.teaching.md (the teaching pass, prompts/teaching-pass.md) into
<opening>.teaching.md. Both come from scripts/refined-text.py.

The opening file keeps its own frontmatter and its header comment; only the
paragraphs after them are replaced. It reports, per file, how many paragraphs
are kept, changed and added, and shows each changed one: an addition to a
session (skill extend-session) should only add paragraphs at the end, so a
changed paragraph means an earlier part's passes moved, which is a decision to
look at, not to let through unread.

--check writes nothing and exits 1 when a file is not in step with the session.
Then: scripts/assemble-discourse.py <discourse> --force (and --lesson --force).
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path


def paragraphs(text: str) -> list[str]:
    """The prose blocks of a refined file: no frontmatter, headings or comments."""
    if text.startswith("---\n"):
        text = text.split("\n---\n", 1)[1]
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return [b for b in blocks if not b.startswith(("#", "<!--"))]


def split_opening(text: str) -> tuple[str, list[str]]:
    """An opening file as its header (frontmatter, then leading comments) and its paragraphs."""
    head, rest = "", text
    if text.startswith("---\n"):
        fm, rest = text[4:].split("\n---\n", 1)
        head = "---\n" + fm + "\n---\n"
    blocks = [b.strip() for b in re.split(r"\n\s*\n", rest) if b.strip()]
    lead = []
    while blocks and blocks[0].startswith("<!--"):
        lead.append(blocks.pop(0))
    if lead:
        head += "\n" + "\n\n".join(lead) + "\n"
    return head, blocks


def short(p: str, n: int = 70) -> str:
    return p if len(p) <= n else p[:n] + "…"


def sync(src: Path, dst: Path, check: bool) -> bool:
    """Bring dst's paragraphs in line with src's. True when they already were."""
    new = paragraphs(src.read_text(encoding="utf-8"))
    head, old = split_opening(dst.read_text(encoding="utf-8"))
    same, notes = 0, []
    changed = added = removed = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes():
        if op == "equal":
            same += i2 - i1
            continue
        pairs = min(i2 - i1, j2 - j1) if op == "replace" else 0
        changed += pairs
        removed += (i2 - i1) - pairs
        added += (j2 - j1) - pairs
        for k in range(i1, i2):
            notes.append(f"  ¶{k + 1} was: {short(old[k])}")
        for k in range(j1, j2):
            notes.append(f"  ¶{k + 1} now: {short(new[k])}")
    ok = old == new
    state = "in step" if ok else ("out of step" if check else "updated")
    print(f"{dst}: {state} — {len(old)} → {len(new)} paragraph(s): "
          f"{same} kept, {changed} changed, {added} added, {removed} removed")
    print("\n".join(notes)) if notes else None
    if not ok and not check:
        dst.write_text(head + "\n" + "\n\n".join(new) + "\n", encoding="utf-8")
    return ok


def main(argv: list[str]) -> int:
    check = "--check" in argv
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    session, opening = Path(args[0].rstrip("/")), Path(args[1])
    pairs = [(session / "refined.md", opening)]
    taught = session / "refined.teaching.md"
    if taught.exists():
        pairs.append((taught, opening.with_suffix(".teaching.md")))
    ok = True
    for src, dst in pairs:
        if not src.exists():
            print(f"{src}: missing — run python scripts/refined-text.py {session}")
            return 1
        if not dst.exists():
            print(f"{dst}: missing — make it first: frontmatter (title:) and a header comment naming its source")
            return 1
        ok = sync(src, dst, check) and ok
    if not taught.exists() and opening.with_suffix(".teaching.md").exists():
        print(f"{opening.with_suffix('.teaching.md')}: the session has no teaching pass any more; remove this file")
        ok = False
    return 0 if ok or not check else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
