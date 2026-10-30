#!/usr/bin/env python3
"""Write the French narration plan of an English one, carrying its decisions over by position.

Usage:
    python scripts/narration-french-plan.py booklets/narration/<english>.yaml <french-name> "<French title>"

The French booklet text (shivchei-habesht-simple-fr.md) is the English one's
translation, paragraph by paragraph, with its brackets at the same points
(prompts/translate-stories-rules.md, held by check-translation.py). So:
  cut:   the English paragraph's place gives the French paragraph to cut
  drop:  the English bracket's place among the story's brackets gives the
         French bracket to drop
  edits: an English edit that unbrackets an aside unbrackets the French
         bracket in the same place
An edit that is not about a bracket (a reworded opening, "I also heard" →
"I heard"), or a story whose French brackets do not match the English in
number, is written as a TODO comment: finish those by hand, then build the
plan with --script, which stops on any bracket left.

Writes booklets/narration/<french-name>.yaml, with the English plan's picture.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml

spec = importlib.util.spec_from_file_location("bn", Path(__file__).with_name("build-narration.py"))
bn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bn)


def body(section: str, lang: str) -> str:
    text = section.partition("\n")[2]
    text = re.sub(r"\s*<!--.*?-->", "", text, flags=re.S)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    paras = [p for p in paras if not re.match(bn.SUMMARY[lang], p) and not re.match(bn.COLOPHON[lang], p)]
    return "\n\n".join(paras)


def brackets(text: str) -> list[tuple[int, int]]:
    """(start, end) of each top-level bracket, in order."""
    out, depth, start = [], 0, 0
    for i, c in enumerate(text):
        if c == "(":
            start = i if depth == 0 else start
            depth += 1
        elif c == ")" and depth:
            depth -= 1
            if depth == 0:
                out.append((start, i + 1))
    return out


def opening(text: str, start: int, end: int) -> str:
    """The shortest opening of the bracket at start that is unique in text."""
    for n in range(12, end - start + 1):
        if text.count(text[start:start + n]) == 1:
            return text[start:start + n]
    return text[start:end]


def which(text: str, spans: list[tuple[int, int]], pos: int) -> int | None:
    return next((k for k, (a, b) in enumerate(spans) if a <= pos < b), None)


def unbracket(text: str, start: int, end: int) -> tuple[str, str]:
    """from/to for an aside that becomes part of the sentence."""
    inner = text[start + 1:end - 1]
    before = text[:start]
    if not before.strip() or re.search(r"[.!?»\"]\s*$", before):     # a sentence of its own
        return text[start:end], inner
    after = text[end:end + 1]
    lead = before[-1:] if before.endswith(" ") else ""
    frm = (lead + text[start:end] + after).lstrip()
    to = ("," + lead + inner + ("" if after in ",.;:" else ",") + after).lstrip(" ")
    if lead:
        frm, to = " " + frm.lstrip(), "," + " " + inner + ("" if after in ",.;:" else ",") + after
    return frm, to


def main(argv: list[str]) -> None:
    if len(argv) != 3:
        sys.exit(__doc__)
    en_path, name, title = Path(argv[0]), argv[1], argv[2]
    plan = yaml.safe_load(en_path.read_text(encoding="utf-8"))
    en = bn.load_sections(Path(bn.SOURCES["en"]))
    fr = bn.load_sections(Path(bn.SOURCES["fr"]))
    out, todo = [], 0
    for entry in plan["stories"]:
        n = entry["n"]
        e, f = body(en[n], "en"), body(fr[n], "fr")
        ep, fp = re.split(r"\n\n", e), re.split(r"\n\n", f)
        eb, fb = brackets(e), brackets(f)
        lines = [f"  - n: {n}"]
        cuts, drops, edits, notes = [], [], [], []
        if len(ep) != len(fp):
            notes.append(f"paragraphs differ (English {len(ep)}, French {len(fp)}): do this story by hand")
        for c in entry.get("cut") or []:
            k = next(i for i, p in enumerate(ep) if p.startswith(c))
            words = fp[k].split()
            op = next(" ".join(words[:m]) for m in range(3, len(words) + 1)
                      if sum(p.startswith(" ".join(words[:m])) for p in fp) == 1)
            cuts.append(op)
        same = len(eb) == len(fb)
        if not same and (entry.get("drop") or entry.get("edits")):
            notes.append(f"brackets differ (English {len(eb)}, French {len(fb)}): map them by hand; French brackets: "
                         + " | ".join(f[a:b][:50] for a, b in fb))
        for d in entry.get("drop") or []:
            k = which(e, eb, e.index(d))
            if same and k is not None:
                a, b = fb[k]
                drops.append(opening(f, a, b))
        for ed in entry.get("edits") or []:
            frm = ed["from"]
            pos = e.index(frm)
            inside = [k for k, (a, b) in enumerate(eb) if pos <= a and b <= pos + len(frm)]
            folded = ed["to"] == re.sub(r"[()]", "", frm)      # "the rabbi (of Polonne)" -> "the rabbi of Polonne"
            commas = ed["to"].count(",") > frm.count(",")        # "came (after his death) to" -> "came, after his death, to"
            if same and len(inside) == 1 and (folded or commas or not ed["to"].strip()):
                a, b = fb[inside[0]]
                if folded:
                    ff, ft = f[a:b], f[a + 1:b - 1]
                    if f.count(ff) > 1:
                        ff, ft = f[a - 20:b], f[a - 20:a] + f[a + 1:b - 1]
                elif commas:
                    ff, ft = unbracket(f, a, b)
                else:                                       # the bracket left out
                    ff, ft = (" " if f[a - 1:a] == " " else "") + f[a:b], ""
                if f.count(ff) == 1:
                    edits.append((ff, ft, None))
                    continue
            edits.append((None, None, f"{frm!r} -> {ed['to']!r}"))
        for note in notes:
            lines.append(f"    # TODO: {note}")
            todo += 1
        if cuts:
            lines.append("    cut:")
            lines += [f"      - {yaml.safe_dump(c, allow_unicode=True, width=1000).strip().removesuffix(chr(10) + '...')}" for c in cuts]
        if drops:
            lines.append("    drop:")
            lines += [f"      - {yaml.safe_dump(d, allow_unicode=True, width=1000).strip().removesuffix(chr(10) + '...')}" for d in drops]
        real = [x for x in edits if x[0]]
        if real:
            lines.append("    edits:")
            for ff, ft, _ in real:
                lines.append(f"      - from: {yaml.safe_dump(ff, allow_unicode=True, width=1000).strip().removesuffix(chr(10) + '...')}")
                lines.append(f"        to: {yaml.safe_dump(ft, allow_unicode=True, width=1000).strip().removesuffix(chr(10) + '...')}")
        for _, _, english in [x for x in edits if not x[0]]:
            lines.append(f"    # TODO: the English edit {english}: write it in French")
            todo += 1
        out.append("\n".join(lines))
    head = f"""# A narration for video, in French: the stories of {en_path.name}, from the French
# booklets (shivchei-habesht-simple-fr.md). Rules: prompts/narration-rules.md.
# Written by scripts/narration-french-plan.py from the English plan, then finished by hand.
#
# Built by: python scripts/build-narration.py booklets/narration/{name}.yaml
#
# cut: paragraphs left out, by their opening words. drop: brackets that
# explain a word, by their opening words. edits: `from` -> `to`, each `from`
# found once in the story; the other brackets become part of the sentence.
# Respellings for the voice: booklets/narration/say-fr.yaml; 'h is read as
# the French r. Summaries are not read.

title: {yaml.safe_dump(title, allow_unicode=True).strip().removesuffix(chr(10) + '...')}
lang: fr
voice: ff_siwis
speed: 1.0

# The same drawing as the English episode.
image: {plan['image']}

intro: >
  Les louanges du Baal Chem Tov, racontées en français d'aujourd'hui.

outro: >
  Ici s'achèvent ces récits des Louanges du Baal Chem Tov.

stories:
"""
    path = Path(f"booklets/narration/{name}.yaml")
    path.write_text(head + "\n\n".join(out) + "\n", encoding="utf-8")
    print(f"  {path}  ({todo} TODO)")


if __name__ == "__main__":
    main(sys.argv[1:])
