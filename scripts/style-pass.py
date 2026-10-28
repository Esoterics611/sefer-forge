#!/usr/bin/env python3
"""The style pass (prompts/style-pass.md): draft the explanation as written
Hebrew, and record the draft as the `style:` list that prints it.

Usage:
    python scripts/style-pass.py <session> --draft <file>   # the explanation as it prints now
    python scripts/style-pass.py <session> <file>           # `style:` rebuilt from the edited draft

The draft holds one paragraph per block: a photo session's explanation, or a
voice-only lesson's transcript body, as it prints now (after `edits:` and any
`style:` already there). Rewrite it in place, leaving the readings in
quotation marks, headings, `>` readings and footnotes as they are, with no
paragraph merged, split or removed, and hand it back. The `style:` list is
then rebuilt from the text after `edits:` to the draft, one exact
replacement per run of changed sentences, so a sentence changes in one step
however many rounds the pass takes. It goes into section-plan.yaml (or
transcript.md's frontmatter), and the session is rebuilt and checked:
build-section.py fails if the list changes a reading or moves the pairing,
check-session.py if it changes a voice-only lesson's headings, readings or
footnotes, and warns of speech left behind. Keep the draft out of the
session folder: it is a working file.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import forgelib as F
import yaml

HEAD = ["# Style pass (prompts/style-pass.md): the spoken explanation as written Hebrew.\n",
        "# Applied after `edits:`; the readings in quotation marks are untouched.\n"]


def blocks(text: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]


def texts(session: Path, styled: bool) -> tuple[Path, dict, list[str]]:
    """(the file holding `style:`, its data, the explanation after `edits:`,
    or with `style:` too when `styled`: as it prints now)."""
    if F.voice_only(session):
        f = session / "transcript.md"
        fm, body, err = F.split_frontmatter(f.read_text(encoding="utf-8"))
        if err or fm is None:
            sys.exit(f"{f}: no valid frontmatter{' — ' + err if err else ''}")
        text, _ = F.edit_transcript(body, F.print_edits(fm) if styled else fm.get("edits") or [])
        return f, fm, blocks(text)
    f = session / "section-plan.yaml"
    if not f.exists():
        sys.exit(f"No {f}: the style pass comes after the section is built")
    plan = F.load_yaml(f)
    paras = F.load_script("build-section").commentary_paragraphs(session)
    text, _ = F.apply_edits(paras, F.print_edits(plan) if styled else plan.get("edits") or [])
    return f, plan, text


def put_style(f: Path, entries: list[dict]) -> None:
    """Replace the `style:` list (and the comment over it) in the plan, or in
    transcript.md's frontmatter; add one at the end when there is none."""
    text = f.read_text(encoding="utf-8")
    m = F.FRONTMATTER.match(text) if f.suffix == ".md" else None
    data, rest = (text[:m.end(1)] + "\n", text[m.end(1) + 1:]) if m else (text, "")
    out, inside = [], False
    for ln in data.splitlines(keepends=True):
        if ln.startswith("style:"):
            inside = True
            while out and out[-1] in HEAD:
                out.pop()
            continue
        if inside and (ln[:1] in ("-", " ", "\n") or not ln.strip()):
            continue
        inside = False
        out.append(ln)
    data = "".join(out).rstrip("\n") + "\n"
    if entries:
        dump = yaml.safe_dump(entries, allow_unicode=True, sort_keys=False, width=100000)
        if m:                                             # frontmatter lists are indented
            dump = "".join("  " + ln for ln in dump.splitlines(keepends=True))
        data += "\n" + "".join(HEAD) + "style:\n" + dump
    f.write_text(data + rest, encoding="utf-8")


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--draft"]
    if len(args) != 2:
        print(__doc__.split("\n\n")[1])
        return 1
    session, draft = Path(args[0].rstrip("/")), Path(args[1])
    words = lambda ps: sum(len(F.words(p)) for p in ps)
    if "--draft" in argv:
        f, data, printed = texts(session, styled=True)
        draft.write_text("\n\n".join(printed) + "\n", encoding="utf-8")
        print(f"{draft}: {len(printed)} paragraphs, {words(printed)} words as the explanation prints now "
              f"({len(data.get('style') or [])} style edit(s))")
        return 0
    f, _, plain = texts(session, styled=False)
    wanted = blocks(draft.read_text(encoding="utf-8"))
    try:
        entries = F.style_list(plain, wanted, f.name)
    except F.EditError as e:
        print(f"Draft problem — {e}")
        return 1
    put_style(f, entries)
    print(f"{f}: {len(entries)} style edit(s); {words(plain)} words → {words(wanted)}")
    script = "check-session.py" if F.voice_only(session) else "build-section.py"
    return subprocess.run([sys.executable, f"scripts/{script}", str(session)]).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
