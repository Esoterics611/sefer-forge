#!/usr/bin/env python3
"""Assemble one book's sources into compiled/<book>.md.

Usage:
    python scripts/compile.py <book>        # e.g. shaar-hayichud
    python scripts/compile.py --list        # show available books

Reads books/<book>/structure.yaml. Run from the repo root. Warns (non-fatal)
on missing pieces so you can still test builds while a book is incomplete.

structure.yaml keys:
    front_matter: [files under books/<book>/front-matter/]
    chapters:
      - title: "..."          # optional; omit when the discourse supplies
        intro: file.md        #   its own '#' headings. intro is optional,
        discourses: [slug]    #   under books/<book>/chapters/
    back_matter:  [files under books/<book>/back-matter/]
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml")
    sys.exit(1)

BOOKS = Path("books")


def strip_yaml_frontmatter(text: str) -> str:
    # Every part has its own frontmatter; left in place, pandoc would merge it
    # into the book's metadata (e.g. overwrite the book title).
    return re.sub(r"^---[\s\S]*?---\s*\n?", "", text, count=1)


def list_books() -> list[str]:
    return sorted(p.parent.name for p in BOOKS.glob("*/structure.yaml"))


def find_discourse(slug: str) -> Path | None:
    matches = sorted(Path("discourses").glob(f"*-{slug}"))
    if not matches:
        matches = sorted(Path("discourses").glob(f"*{slug}*"))
    return matches[0] if matches else None


def refresh_if_generated(dd: Path) -> None:
    """Voice-only discourses are generated from their transcripts: rebuild
    discourse.md first so the book always has the latest lessons."""
    meta = dd / "meta.yaml"
    if not meta.exists():
        return
    if (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("type") != "voice-only":
        return
    script = Path(__file__).with_name("assemble-discourse.py")
    subprocess.run([sys.executable, str(script), str(dd)], check=True)


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("--list", "-l"):
        print("Usage: python scripts/compile.py <book>")
        print("Books:", ", ".join(list_books()) or "(none)")
        return 0 if args else 1

    book = args[0]
    root = BOOKS / book
    struct_path = root / "structure.yaml"
    if not struct_path.exists():
        print(f"Missing: {struct_path}")
        print("Books:", ", ".join(list_books()) or "(none)")
        return 1

    struct = yaml.safe_load(struct_path.read_text(encoding="utf-8")) or {}
    parts: list[str] = []
    warnings: list[str] = []

    def add_file(p: Path, what: str) -> None:
        if p.exists():
            parts.append(strip_yaml_frontmatter(p.read_text(encoding="utf-8")))
        else:
            warnings.append(f"missing {what}: {p}")

    for fm in struct.get("front_matter") or []:
        add_file(root / "front-matter" / fm, "front-matter")

    for ch in struct.get("chapters") or []:
        if ch.get("title"):
            parts.append(f"# {ch['title']}\n")
        if ch.get("intro"):
            add_file(root / "chapters" / ch["intro"], "chapter intro")
        for slug in ch.get("discourses") or []:
            dd = find_discourse(slug)
            if dd is None:
                warnings.append(f"discourse not found for slug: {slug}")
                continue
            refresh_if_generated(dd)
            add_file(dd / "discourse.md", "discourse.md")

    for bm in struct.get("back_matter") or []:
        add_file(root / "back-matter" / bm, "back-matter")

    out = Path("compiled") / f"{book}.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n\n".join(p.strip() for p in parts) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(parts)} segments, {out.stat().st_size} bytes)")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
