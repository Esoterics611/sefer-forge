#!/usr/bin/env python3
"""Check the words a ביאור quotes outside the bold text, and the built text for doubled words.

    python scripts/check-quotes.py <biur folder> [--all]

1. Quotations. Every "..." in the plain (non-bold) prose of biur.src.md (the opening, the מבוא, the
   chapter summaries, the glossary, the glosses) is looked up in the document's text_file (the maamar as
   given, abbreviations as written). A quotation split by "..." is checked piece by piece; HTML comments
   and "## Source:" lines of the text are ignored, whitespace is normalized. Reported: each quotation
   not found. Verses and sayings quoted from elsewhere (not from the text) are reported too: judge them.
2. Doubled words. In the built biur.md (abbreviations opened), the same word twice in a row ("לא לא"),
   which opening an abbreviation can produce ("וא"ל לא" → "ואם לא לא"). A few doublings that are the
   text's own (נצחי נצחי, יותר יותר) are skipped.

Exit 1 if anything is found, so it can gate a build. Part of skill `biur-booklet`.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
FN = re.compile(r"\[(?:[^\[\]]|\[[^\[\]]*\])*\]\{\.fn\}")
TEXT_DOUBLES = {"נצחי", "יותר", "מעלה", "מטה", "וחד", "ואחד", "הן", "שלום", "פרטי", "רבים"}


def norm(s: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"(?m)^## Source:.*$", " ", s)
    return re.sub(r"\s+", " ", s)


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    folder = ROOT / args[0]
    src = (folder / "biur.src.md").read_text(encoding="utf-8")
    meta = yaml.safe_load(src.split("---", 2)[1]) or {}
    body = src.split("---", 2)[2]
    found = 0
    if meta.get("text_file"):
        text = norm((ROOT / meta["text_file"]).read_text(encoding="utf-8"))
        prose = re.sub(r"\*\*.+?\*\*", " ", body, flags=re.S)
        prose = re.sub(r"\[[^\]]*\]\{\.asis\}", " ", prose)
        if "--all" not in argv:
            prose = FN.sub(" ", prose)
        quotes = re.findall(r'"((?:[^"\n])+?)"(?=[\s,.;:)\]]|$)', prose)
        missing = []
        for q in quotes:
            for piece in re.split(r"\.\.\.|…", q):
                piece = piece.strip()
                if len(piece) > 2 and piece not in text:
                    missing.append(q)
                    break
        for q in dict.fromkeys(missing):
            print(f'  not in the text: "{q}"')
        print(f"quotations: {len(quotes)} checked, {len(set(missing))} not found in {meta['text_file']}")
        found += len(set(missing))
    built = folder / "biur.md"
    if built.is_file():
        t = built.read_text(encoding="utf-8").split("---", 2)[2]
        t = re.sub(r"\*\*|\{[^}]*\}|[\[\]]|⁠", "", t)
        doubles = []
        for m in re.finditer(r"(?<![א-ת])([א-ת\"']{2,}) \1(?![א-ת])", t):
            if m.group(1) not in TEXT_DOUBLES:
                doubles.append(t[max(0, m.start() - 30):m.end() + 20].replace("\n", " "))
        for d in doubles:
            print(f"  doubled word: …{d}…")
        print(f"doubled words in biur.md: {len(doubles)}")
        found += len(doubles)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
