#!/usr/bin/env python3
"""Read book/structure.yaml and assemble everything into compiled/book.md.

Run from the repo root. Warns (non-fatal) on missing pieces so you can
still test builds while the book is incomplete.
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml")
    sys.exit(1)


def main() -> int:
    struct_path = Path("book/structure.yaml")
    if not struct_path.exists():
        print(f"Missing: {struct_path}")
        return 1

    struct = yaml.safe_load(struct_path.read_text(encoding="utf-8")) or {}
    parts: list[str] = []
    warnings: list[str] = []

    # Front matter
    for fm in struct.get("front_matter") or []:
        p = Path("book/front-matter") / fm
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
        else:
            warnings.append(f"missing front-matter: {p}")

    # Chapters
    for i, ch in enumerate(struct.get("chapters") or [], start=1):
        title = ch.get("title") or f"Chapter {i}"
        parts.append(f"\n\n# {title}\n")
        intro = ch.get("intro")
        if intro:
            ip = Path("book/chapters") / intro
            if ip.exists():
                parts.append(ip.read_text(encoding="utf-8"))
            else:
                warnings.append(f"missing chapter intro: {ip}")
        for slug in ch.get("discourses") or []:
            matches = sorted(Path("discourses").glob(f"*-{slug}"))
            if not matches:
                matches = sorted(Path("discourses").glob(f"*{slug}*"))
            if not matches:
                warnings.append(f"discourse not found for slug: {slug}")
                continue
            dd = matches[0]
            dmd = dd / "discourse.md"
            if dmd.exists():
                parts.append(dmd.read_text(encoding="utf-8"))
            else:
                warnings.append(f"missing discourse.md in {dd}")

    # Back matter
    for bm in struct.get("back_matter") or []:
        p = Path("book/back-matter") / bm
        if p.exists():
            parts.append(p.read_text(encoding="utf-8"))
        else:
            warnings.append(f"missing back-matter: {p}")

    out = Path("compiled/book.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n\n".join(parts), encoding="utf-8")
    print(f"Wrote {out} ({len(parts)} segments, {out.stat().st_size} bytes)")

    if warnings:
        print(f"\n{len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
