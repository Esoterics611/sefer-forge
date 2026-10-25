#!/usr/bin/env python3
"""Check a translation of shivchei-habesht-simple.md against the Hebrew.

Usage:
    python scripts/check-translation.py shivchei-habesht-simple-en.md
    python scripts/check-translation.py shivchei-habesht-simple-fr.md

The rules are prompts/translate-stories-rules.md. Checks every `## ` section
the translation has so far (a partial file is checked as far as it goes):

  headings     the sections in the Hebrew order; the introduction first, then
               `## <n> — <title>` with n the story's number
  shape        per story, the same sequence of paragraphs (p), blockquote
               paragraphs (q) and the summary (s) as the Hebrew
  summary      the last paragraph opens with the language's summary label
  flags        the same MATURE flags, verbatim, in the same paragraph
  Hebrew       no Hebrew letters outside comments
  digits       the numbers written in digits in the Hebrew story are in the
               translation too
  closing      the book's closing line after the last summary

Prints one line per problem and a summary; exits 1 on any error.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HEBREW = Path("shivchei-habesht-simple.md")
LANGS = {
    "en": {"intro": "The Author's Introduction", "summary": "**Summary:**",
           "closing": "Finished and complete. Praise to God, Creator of the world."},
    "fr": {"intro": "Introduction de l'auteur", "summary": "**Résumé :**",
           "closing": "Fin. Louange à Dieu, Créateur du monde."},
}
HE_SUMMARY = "**סיכום:**"
HE_CLOSING = re.compile(r"^תם ונשלם.*$", re.M)
HEB_LETTERS = re.compile(r"[א-ת]")
COMMENT = re.compile(r"<!--.*?-->", re.S)
MATURE = re.compile(r"<!--\s*MATURE:.*?-->", re.S)
HEB_VALUES = {**{c: i + 1 for i, c in enumerate("אבגדהוזחט")},
              **{c: (i + 1) * 10 for i, c in enumerate("יכלמנסעפצ")},
              **{c: (i + 1) * 100 for i, c in enumerate("קרשת")}}


def sections(text: str) -> list[str]:
    return re.split(r"^(?=## )", text, flags=re.M)[1:]


def hebrew_number(head: str) -> int | None:
    num, sep, _ = head.partition(" — ")
    if not sep:
        return None
    return sum(HEB_VALUES.get(c, 0) for c in num)


def blocks(body: str) -> list[tuple[str, str]]:
    """(kind, text) per paragraph: p, q (a blockquote paragraph) or s (summary)."""
    out = []
    for block in re.split(r"\n\s*\n", body.strip()):
        block = block.strip()
        if not block or not COMMENT.sub("", block).strip():
            continue
        if block.startswith(">"):
            lines = [re.sub(r"^> ?", "", ln) for ln in block.splitlines()]
            for para in re.split(r"\n\s*\n", "\n".join(lines)):
                if para.strip():
                    out.append(("q", para.strip()))
        else:
            out.append(("p", block))
    return out


def shape(paras: list[tuple[str, str]], label: str) -> list[str]:
    kinds = [k for k, _ in paras]
    if paras and paras[-1][1].startswith(label):
        kinds[-1] = "s"
    return kinds


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.split("\n\n")[1])
        return 1
    path = Path(argv[0])
    lang = re.search(r"-(\w\w)\.md$", path.name)
    if not lang or lang.group(1) not in LANGS:
        print(f"{path}: name it shivchei-habesht-simple-<{'|'.join(LANGS)}>.md")
        return 1
    L = LANGS[lang.group(1)]
    he = sections(HEBREW.read_text(encoding="utf-8"))
    tr_text = path.read_text(encoding="utf-8")
    tr = sections(tr_text)
    errors: list[str] = []
    warns: list[str] = []
    if len(tr) > len(he):
        errors.append(f"{len(tr)} sections, the Hebrew has {len(he)}")

    for i, (h, t) in enumerate(zip(he, tr)):
        h_head, _, h_body = h.partition("\n")
        t_head, _, t_body = t.partition("\n")
        h_body = HE_CLOSING.sub("", h_body)
        t_head = t_head[3:].strip()
        where = "intro" if i == 0 else f"§{i}"
        n = hebrew_number(h_head[3:].strip())
        if n is None:
            if t_head != L["intro"]:
                errors.append(f"{where}: heading should be '{L['intro']}', is '{t_head}'")
        else:
            m = re.match(r"(\d+) — \S", t_head)
            if not m or int(m.group(1)) != n:
                errors.append(f"{where}: heading should be '{n} — <title>', is '{t_head}'")
        if i == len(he) - 1:
            if L["closing"] not in t_body:
                errors.append(f"{where}: the closing line '{L['closing']}' is missing")
            t_body = t_body.replace(L["closing"], "")

        hp, tp = blocks(h_body), blocks(t_body)
        hs, ts = shape(hp, HE_SUMMARY), shape(tp, L["summary"])
        if hs != ts:
            errors.append(f"{where}: paragraphs {''.join(ts)} but the Hebrew has {''.join(hs)}")
        elif ts and ts[-1] != "s":
            errors.append(f"{where}: no summary line '{L['summary']}'")
        if hs == ts:
            for j, ((_, hx), (_, tx)) in enumerate(zip(hp, tp)):
                if MATURE.findall(hx) != MATURE.findall(tx):
                    errors.append(f"{where}: paragraph {j + 1}: MATURE flags differ from the Hebrew")
        elif MATURE.findall(h_body) != MATURE.findall(t_body):
            errors.append(f"{where}: MATURE flags differ from the Hebrew")
        heb = HEB_LETTERS.findall(COMMENT.sub("", t))
        if heb:
            errors.append(f"{where}: Hebrew letters in the text ({''.join(heb[:12])})")
        h_digits = Counter(re.findall(r"\d+", COMMENT.sub("", h_body)))
        t_digits = Counter(re.findall(r"\d+", COMMENT.sub("", t_body)))
        missing = h_digits - t_digits
        if missing:
            warns.append(f"{where}: numbers in the Hebrew not in the translation: {', '.join(missing)}")

    done = len(tr)
    print(f"{path}: {done} of {len(he)} sections · {len(errors)} error(s) · {len(warns)} warning(s)")
    for e in errors:
        print(f"  ✗ {e}")
    for w in warns:
        print(f"  ! {w}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
