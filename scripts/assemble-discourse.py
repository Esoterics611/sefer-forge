#!/usr/bin/env python3
"""Concatenate a discourse's sessions into discourse.md.

Usage:
    python scripts/assemble-discourse.py <discourse-dir> [--force]
    python scripts/assemble-discourse.py <discourse-dir> --lesson     # discourse.lesson.md

Each session contributes one of:
  - section.md     (image + voicenote sessions)
  - transcript.md  (voice-only sessions). Its frontmatter `title` becomes a
                   '#' heading (a new page in the book) and `subtitle` an
                   italic line under it; its `edits:` (the readability pass,
                   prompts/readability-pass.md) are applied.

Optional keys in <discourse-dir>/meta.yaml:
    intro: introduction.md       # placed before the first session; rendered
                                 #   like a transcript (title → heading); a list
                                 #   of files makes one opening part each
    skip_sessions: ["000"]       # sessions left out of discourse.md
    addendum: ["005"]            # sessions printed whole at the end, as an addendum
                                 #   (נספח), after every other part; in a session's
                                 #   own place, its inline.md: the basics, pointing
                                 #   to the addendum
    keys: end                    # the key points (נקודות מפתח) of every part
                                 #   gathered into one list at the very end, instead
                                 #   of closing each part; `keys: none` leaves them
                                 #   out of discourse.md altogether

Markdown footnote labels ([^1]) are prefixed with the session number so
labels from different sessions never collide in the book.

The teaching text prints (prompts/teaching-pass.md, the last step of every
narration): each opening file's <name>.teaching.md and each session's
section.teaching.md where they exist, and a transcript with its `teaching:`
applied; the lesson text where a part has no teaching pass. --lesson writes
discourse.lesson.md with the lesson text throughout (before the teaching
pass), generated every time: the way back to that version.

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
NIQQUD = re.compile(r"[\u0591-\u05c7]")
KICKER_RE = re.compile(r'^\*\*\[(.+?)\]\{dir="rtl"\}\*\*$', re.M)
ADDENDUM_MARK = "<!-- addendum -->"       # build-pamphlet.py: the parts after it are the addendum
KEYS_PART = "keys"                         # the key points of every part, gathered (meta.yaml keys: end)


def take_keys(fragment: str) -> tuple[str, str]:
    """A section's '## נקודות מפתח' cut out: (the section without it, its body)."""
    heads = list(re.finditer(r"^## (.+)$", fragment, re.M))
    for i, m in enumerate(heads):
        if NIQQUD.sub("", m.group(1)).strip() == "נקדות מפתח":
            end = heads[i + 1].start() if i + 1 < len(heads) else len(fragment)
            return (fragment[:m.start()] + fragment[end:]).strip(), fragment[m.end():end].strip()
    return fragment, ""


def gathered_keys(groups: list[tuple[str, str]]) -> str:
    """One list of key points, a heading for each part they come from."""
    out = ["## נְקֻדּוֹת מַפְתֵּחַ"]
    for title, keys in groups:
        out += [f'### [{title}]{{dir="rtl"}}', keys]
    return "\n\n".join(out)


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


def render_transcript(text: str, label: str, teaching: bool = False) -> str:
    """A transcript as it prints: its print edits (frontmatter `edits:`, `style:`)
    applied — with `teaching`, its teaching pass too — footnotes namespaced,
    title and subtitle on top."""
    fm = parse_frontmatter(text)
    body, _ = F.edit_transcript(strip_frontmatter(text), F.print_edits(fm))
    if teaching and fm.get("teaching"):
        body = F.teach_blocks(body, fm["teaching"])
    body = namespace_footnotes(body.strip(), f"s{label}")
    head = []
    if fm.get("title"):
        head.append(f"# {fm['title']}")
    if fm.get("subtitle"):
        head.append(f"*{fm['subtitle']}*")
    return "\n\n".join(head + [body])


def tail_parts(fragments: list[tuple[str, str]], addenda: list[tuple[str, str]],
               groups: list[tuple[str, str]]) -> list[str]:
    """The parts in print order: the body, then the addendum, then the gathered key points."""
    out: list[str] = []
    for name, content in fragments:
        out += [f"<!-- session: {name} -->", content, ""]
    if addenda:
        out += [ADDENDUM_MARK, ""]
        for name, content in addenda:
            out += [f"<!-- session: {name} -->", content, ""]
    if groups:
        out += [f"<!-- session: {KEYS_PART} -->", gathered_keys(groups), ""]
    return out


def listing(fragments: list, addenda: list, groups: list) -> None:
    for name, _ in fragments:
        print(f"  - {name}")
    for name, _ in addenda:
        print(f"  - {name} (addendum, meta.yaml addendum:)")
    if groups:
        print(f"  - key points of {len(groups)} part(s), gathered at the end (meta.yaml keys: end)")


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    force = "--force" in sys.argv
    lesson = "--lesson" in sys.argv          # the text before the teaching pass
    teaching = not lesson

    if len(args) != 1:
        print("Usage: python scripts/assemble-discourse.py <discourse-dir> [--force | --lesson]")
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
    intros = meta.get("intro") or []
    for k, name in enumerate([intros] if isinstance(intros, str) else intros):
        intro = discourse / name
        if teaching and (discourse / name).with_suffix(".teaching.md").exists():
            intro = (discourse / name).with_suffix(".teaching.md")
        if not intro.exists():
            print(f"meta.yaml intro not found: {intro}")
            return 1
        label = "intro" if k == 0 else f"intro{k + 1}"
        fragments.append((intro.name, render_transcript(intro.read_text(encoding="utf-8"), label)))

    addendum = {str(s).zfill(3) for s in meta.get("addendum") or []}
    addenda: list[tuple[str, str]] = []
    skipped: list[str] = []
    for s in sorted(sessions_dir.iterdir()):
        if not s.is_dir():
            continue
        if s.name in skip:
            skipped.append(s.name)
            continue
        section = s / "section.md"
        if teaching and (s / "section.teaching.md").exists():
            section = s / "section.teaching.md"
        transcript = s / "transcript.md"
        if section.exists():
            content = strip_frontmatter(section.read_text(encoding="utf-8")).strip()
        elif transcript.exists():
            content = render_transcript(transcript.read_text(encoding="utf-8"), s.name, teaching)
        else:
            continue
        if s.name in addendum:
            inline = s / "inline.md"
            if not inline.exists():
                print(f"meta.yaml addendum: {s.name} has no inline.md (the basics printed in its place)")
                return 1
            fragments.append((f"{s.name}/inline.md", strip_frontmatter(inline.read_text(encoding="utf-8")).strip()))
            addenda.append((s.name, content))
        else:
            fragments.append((s.name, content))

    groups: list[tuple[str, str]] = []
    if meta.get("keys") in ("end", "none"):
        for k, (name, content) in enumerate(fragments + addenda):
            rest, keys = take_keys(content)
            if keys:
                m = KICKER_RE.search(content)
                groups.append((m.group(1) if m else name, keys))
            if k < len(fragments):
                fragments[k] = (name, rest)
            else:
                addenda[k - len(fragments)] = (name, rest)
        if meta.get("keys") == "none":
            print(f"Key points of {len(groups)} part(s) left out (meta.yaml keys: none)")
            groups = []

    if not fragments:
        print("No section.md / transcript.md files found.")
        return 1

    target = discourse / "discourse.md"
    existing_fm: str | None = None
    if lesson:                        # generated every time from the sessions
        fm = extract_frontmatter(target.read_text(encoding="utf-8")) if target.exists() else None
        parts = [fm or f"---\ndiscourse: {discourse.name}\n---", "",
                 "<!-- GENERATED by scripts/assemble-discourse.py --lesson: the lesson text, before the "
                 "teaching pass (prompts/teaching-pass.md). Not the printed text; not for editing. -->", ""]
        parts += tail_parts(fragments, addenda, groups)
        out = discourse / "discourse.lesson.md"
        out.write_text("\n".join(parts) + "\n", encoding="utf-8")
        print(f"Assembled {out} (the lesson text) from {len(fragments)} part(s):")
        listing(fragments, addenda, groups)
        return 0

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
    parts += tail_parts(fragments, addenda, groups)

    target.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"Assembled {target} from {len(fragments)} part(s):")
    listing(fragments, addenda, groups)
    if skipped:
        print(f"Skipped (meta.yaml skip_sessions): {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
