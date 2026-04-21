#!/usr/bin/env python3
"""Concatenate all session.md files in a discourse into discourse.md.

Usage:
    python scripts/assemble-discourse.py <discourse-dir> [--force]

Refuses to overwrite a discourse.md that has hand-edited content (anything
beyond the YAML frontmatter) unless --force is passed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---[\s\S]*?---\s*", "", text, count=1)


def extract_frontmatter(text: str) -> str | None:
    m = re.match(r"^(---[\s\S]*?---)\s*", text)
    return m.group(1) if m else None


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv

    if len(args) != 1:
        print("Usage: python scripts/assemble-discourse.py <discourse-dir> [--force]")
        return 1

    discourse = Path(args[0])
    if not discourse.is_dir():
        print(f"Not a directory: {discourse}")
        return 1

    sessions_dir = discourse / "sessions"
    if not sessions_dir.is_dir():
        print(f"No sessions dir: {sessions_dir}")
        return 1

    fragments: list[tuple[str, str]] = []
    for s in sorted(sessions_dir.iterdir()):
        if not s.is_dir():
            continue
        section = s / "section.md"
        if section.exists():
            fragments.append((s.name, section.read_text(encoding="utf-8")))

    if not fragments:
        print("No session.md files found.")
        return 1

    target = discourse / "discourse.md"
    existing_fm: str | None = None

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        existing_fm = extract_frontmatter(existing)
        body = strip_frontmatter(existing).strip()
        if body and not force:
            print(f"{target} has content beyond the frontmatter ({len(body)} chars).")
            print("Refusing to overwrite. Pass --force, or merge manually.")
            print("Session fragments available:")
            for name, _ in fragments:
                print(f"  - {discourse}/sessions/{name}/section.md")
            return 2

    if not existing_fm:
        existing_fm = f"---\ndiscourse: {discourse.name}\n---"

    parts: list[str] = [existing_fm, ""]
    for name, content in fragments:
        parts.append(f"<!-- session: {name} -->")
        parts.append(strip_frontmatter(content).strip())
        parts.append("")

    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Assembled {target} from {len(fragments)} session(s):")
    for name, _ in fragments:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
