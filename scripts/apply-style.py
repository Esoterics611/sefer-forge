#!/usr/bin/env python3
"""Record a style pass given as whole paragraphs: the explanation as it should read,
paragraph by paragraph, becomes the session's `style:` list.

Usage:
    python scripts/apply-style.py <session> <paragraphs.txt>
    python scripts/apply-style.py <session> <paragraphs.txt> --check   # check, write nothing

<paragraphs.txt> holds the explanation's paragraphs after the style pass
(prompts/style-pass.md), one per blank-line-separated block, in the order of
commentary.md's paragraphs (its `#` labels and comment-only blocks are not
paragraphs). Each paragraph that differs from the text after the readability
edits becomes one `style:` entry, `from` that whole paragraph. The list replaces
the session's `style:`: in section-plan.yaml when the session is laid out, else
in commentary.md's frontmatter (a narration not yet laid out). `edits:` stay as
they are.

Refused, writing nothing, when the paragraph counts differ, or when a reading
in quotation marks (four words or more) is not in its paragraph's new text
word for word: the readings never change. Then run build-section.py (laid out)
or refined-text.py.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

import forgelib as F

# A quotation: opens after a space or the line start and before a letter, closes
# after a letter and before a space, punctuation or the end. The quote mark of an
# abbreviation (ע"ח, אדמו"ר) sits between letters, so it neither opens nor closes.
QUOTE = re.compile(r'(?:(?<=^)|(?<=[\s(—]))"(?=[א-ת])(.+?)(?<=[א-ת.,\'])"(?=[\s.,:;)—]|$)')


def body_paragraphs(body: str) -> list[str]:
    return [" ".join(p.split()) for p in re.split(r"\n\s*\n", body)
            if p.strip() and not p.lstrip().startswith("#") and not re.fullmatch(r"\s*<!--.*?-->\s*", p, re.S)]


def readings(text: str) -> list[str]:
    return [m.group(1) for m in QUOTE.finditer(F.COMMENT.sub("", text)) if len(m.group(1).split()) >= 4]


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    session, src = Path(args[0].rstrip("/")), Path(args[1])
    com = session / "commentary.md"
    plan_f = session / "section-plan.yaml"
    fm, body, err = F.split_frontmatter(com.read_text(encoding="utf-8"))
    if err:
        print(f"{com}: frontmatter: {err}")
        return 1
    fm = fm or {}
    holder = F.load_yaml(plan_f) if plan_f.exists() else fm
    try:
        after, _ = F.apply_edits(body_paragraphs(body), holder.get("edits") or [])
    except F.EditError as e:
        print(f"edits: {e}")
        return 1
    after = [F.COMMENT.sub("", p).strip() for p in after]
    after = [re.sub(r"[ \t]{2,}", " ", p) for p in after]
    new = [" ".join(p.split()) for p in src.read_text(encoding="utf-8").split("\n\n") if p.strip()]
    if len(new) != len(after):
        print(f"{src}: {len(new)} paragraphs; the explanation has {len(after)}")
        return 1
    style, lost = [], []
    for i, (a, b) in enumerate(zip(after, new), 1):
        lost += [f"¶{i}: “{r}”" for r in readings(a) if f'"{r}"' not in b]
        if a != b:
            style.append({"from": a, "to": b})
    if lost:
        print("readings changed or dropped (they must stay word for word):\n  " + "\n  ".join(lost))
        return 1
    where = plan_f.name if plan_f.exists() else f"{com.name}'s frontmatter"
    print(f"{len(style)} style edit(s) for {len(after)} paragraphs → {where}"
          f"; readings kept: {sum(len(readings(a)) for a in after)}")
    if "--check" in argv:
        return 0
    if plan_f.exists():
        text = plan_f.read_text(encoding="utf-8")
        head = "".join(ln for ln in text.splitlines(True) if ln.startswith("#"))
        plan = yaml.safe_load(text) or {}
        plan["style"] = style
        plan_f.write_text(head + yaml.safe_dump(plan, allow_unicode=True, sort_keys=False, width=10000),
                          encoding="utf-8")
    else:
        fm["style"] = style
        com.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=10000)
                       + "---\n" + body, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
