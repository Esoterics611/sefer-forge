#!/usr/bin/env python3
"""Concatenate a discourse's sessions into discourse.md.

Usage:
    python scripts/assemble-discourse.py <discourse-dir> [--force]

Each session contributes one of:
  - section.md     (image + voicenote sessions)
  - transcript.md  (voice-only sessions). Its frontmatter `title` becomes a
                   '#' heading (a new page in the book) and `subtitle` an
                   italic line under it; its `edits:` (the readability pass,
                   prompts/readability-pass.md) are applied.

Optional keys in <discourse-dir>/meta.yaml:
    intro: introduction.md       # placed before the first session; rendered
                                 #   like a transcript (title → heading)
    skip_sessions: ["000"]       # sessions left out of discourse.md

Markdown footnote labels ([^1]) are prefixed with the session number so
labels from different sessions never collide in the book.

Refuses to overwrite a discourse.md that has hand-edited content (anything
beyond the YAML frontmatter) unless --force is passed — except for
`type: voice-only` discourses, whose discourse.md is purely generated (edit
the sessions' transcript.md instead). compile.py re-assembles those on every
build.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency. Install with: pip install pyyaml")
    sys.exit(1)

import forgelib as F

FRONTMATTER_RE = re.compile(r"^---\n([\s\S]*?)\n---\s*")
FOOTNOTE_RE = re.compile(r"\[\^([^\]\s]+)\]")


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def extract_frontmatter(text: str) -> str | None:
    m = FRONTMATTER_RE.match(text)
    return f"---\n{m.group(1)}\n---" if m else None


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def namespace_footnotes(body: str, prefix: str) -> str:
    return FOOTNOTE_RE.sub(lambda m: f"[^{prefix}-{m.group(1)}]", body)


def render_transcript(text: str, label: str) -> str:
    """A transcript as it prints: its readability edits (frontmatter `edits:`)
    applied, footnotes namespaced, title and subtitle on top."""
    fm = parse_frontmatter(text)
    body, _ = F.edit_transcript(strip_frontmatter(text), fm.get("edits") or [])
    body = namespace_footnotes(body.strip(), f"s{label}")
    head = []
    if fm.get("title"):
        head.append(f"# {fm['title']}")
    if fm.get("subtitle"):
        head.append(f"*{fm['subtitle']}*")
    return "\n\n".join(head + [body])


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

    meta_path = discourse / "meta.yaml"
    meta = (yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}) if meta_path.exists() else {}
    skip = {str(s).zfill(3) for s in meta.get("skip_sessions") or []}
    generated = meta.get("type") == "voice-only"
    force = force or generated

    fragments: list[tuple[str, str]] = []
    if meta.get("intro"):
        intro = discourse / meta["intro"]
        if not intro.exists():
            print(f"meta.yaml intro not found: {intro}")
            return 1
        fragments.append((intro.name, render_transcript(intro.read_text(encoding="utf-8"), "intro")))

    skipped: list[str] = []
    for s in sorted(sessions_dir.iterdir()):
        if not s.is_dir():
            continue
        if s.name in skip:
            skipped.append(s.name)
            continue
        section = s / "section.md"
        transcript = s / "transcript.md"
        if section.exists():
            fragments.append((s.name, strip_frontmatter(section.read_text(encoding="utf-8")).strip()))
        elif transcript.exists():
            fragments.append((s.name, render_transcript(transcript.read_text(encoding="utf-8"), s.name)))

    if not fragments:
        print("No section.md / transcript.md files found.")
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
                print(f"  - {name}")
            return 2

    if not existing_fm:
        existing_fm = f"---\ndiscourse: {discourse.name}\n---"

    parts: list[str] = [existing_fm, ""]
    if generated:
        parts += ["<!-- GENERATED by scripts/assemble-discourse.py on every build."
                  " Edit sessions/*/transcript.md (or the intro), not this file. -->", ""]
    for name, content in fragments:
        parts.append(f"<!-- session: {name} -->")
        parts.append(content)
        parts.append("")

    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Assembled {target} from {len(fragments)} part(s):")
    for name, _ in fragments:
        print(f"  - {name}")
    if skipped:
        print(f"Skipped (meta.yaml skip_sessions): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
