#!/usr/bin/env python3
"""Record the teaching pass (prompts/teaching-pass.md): the explanation rewritten
as a written commentary, paragraph by paragraph, becomes the session's
`teaching:` list.

Usage:
    python scripts/apply-teaching.py <session> --draft <file>     # start (or reopen) a draft
    python scripts/apply-teaching.py <session> <file> --check     # check, write nothing
    python scripts/apply-teaching.py <session> <file>             # check and record

The draft (written by --draft) is the explanation as it prints by default, one
block per paragraph under `#` lines naming the cut of the text it explains;
reopened, it shows the teaching text already recorded. Replace each block with
its teaching text, or with a lone `—` to drop it (its content merged into a
neighbour under the same cut, or a repeat). The count and order of blocks stay.

Refused, writing nothing, when the count differs or a check fails: Latin
letters, an unbalanced quotation mark or parenthesis, or a quotation of three
words or more found neither in the discourse's texts nor in the paragraph it
replaces. Warnings (speech words, long sentences, length outside about half,
repeated phrases) are listed for the read-through; they do not block.

Records `teaching:` beside `style:` (section-plan.yaml, else the transcript's
frontmatter). Then: build-section.py (laid out) or refined-text.py, and
check-teaching.py on the discourse.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

import forgelib as F
import teachlib as T


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if "--draft" in argv:
        if len(args) != 2:
            print(__doc__)
            return 2
        return T.write_draft(Path(args[0].rstrip("/")), Path(args[1]))
    if len(args) != 2:
        print(__doc__)
        return 2
    session, src = Path(args[0].rstrip("/")), Path(args[1])
    try:
        paras, holder, where = F.printed_paragraphs(session)
    except F.EditError as e:
        print(e)
        return 1
    new = T.read_draft(src)
    if len(new) != len(paras):
        print(f"{src}: {len(new)} blocks; the explanation has {len(paras)} paragraphs (drop one with a lone {T.DROP})")
        return 1
    after = [None if b in (T.DROP, "-", "–") else b for b in new]
    errors, warns, st = T.check(session, paras, after)
    for w in warns:
        print("  ⚠", w)
    for e in errors:
        print("  ✗", e)
    print(f"{st['paragraphs']} paragraphs → {st['kept']} · {st['before']} words → {st['after']} "
          f"({st['after'] / max(1, st['before']):.0%}) → {where.name}")
    if errors:
        print("Not recorded: fix the errors above.")
        return 1
    if "--check" in argv:
        return 0
    entries = [{"from": p, "to": t or ""} for p, t in zip(paras, after)]
    if where.name == "section-plan.yaml":
        text = where.read_text(encoding="utf-8")
        head = "".join(ln for ln in text.splitlines(True) if ln.startswith("#"))
        plan = yaml.safe_load(text) or {}
        plan["teaching"] = entries
        where.write_text(head + yaml.safe_dump(plan, allow_unicode=True, sort_keys=False, width=10000),
                         encoding="utf-8")
    else:
        fm, body, _ = F.split_frontmatter(where.read_text(encoding="utf-8"))
        fm = fm or {}
        fm["teaching"] = entries
        where.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=10000)
                         + "---\n" + body, encoding="utf-8")
    nxt = "build-section.py" if where.name == "section-plan.yaml" else "refined-text.py"
    print(f"Recorded. Next: python scripts/{nxt} {session}; python scripts/check-teaching.py {F.discourse_of(session)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
