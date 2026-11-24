#!/usr/bin/env python3
"""The lean-ביאור check (skill `lean-biur`, Ronnie 2026-11-24): in a woven ביאור the words of the
text run in bold, and what follows a stretch of bold must add something the bold does not say: a term
explained, a source brought in context. A gloss that only says the bold again in other words is cut.

For every gloss (the plain words between one bold stretch and the next) this lists how many of its
content words already stand in the bold text of its section, and whether it carries a source (a
footnote, a quotation with its address, an @source after it). It cannot judge a paraphrase in other
words; it shows where to look. The writer judges each gloss by the skill's three questions.

  python scripts/check-restatement.py <biur folder | biur.src.md> [...]  [--all] [--max N]

  --all     list every gloss, not only the flagged ones
  --max N   exit 1 when more than N glosses are flagged (default: report only)

Flagged: a gloss of 3+ content words, no source, and half or more of its content words in the bold,
or a gloss of 6+ words of which none is new (a pure restatement in its own words is often this).
"""
import re
import sys
from pathlib import Path

NIQQUD = re.compile(r"[֑-ׇ]")
FOOTNOTE = re.compile(r"\[[^\[\]]*(?:\[[^\]]*\][^\[\]]*)*\]\{\.fn\}")
ADDRESS = re.compile(r"\((?:[^()]*?(?:פרק|דף|ע\"[אב]|משלי|תהלים|ישעיה|בראשית|שמות|דברים|איוב|"
                     r"זוהר|זהר|עץ חיים|תניא|גמרא|חגיגה|ברכות|שער|סימן|פסוק|[א-ת]{1,3}, [א-ת]{1,3})[^()]*)\)")
STOP = set("""
של את הוא היא הם הן זה זו זאת אלה אלו כל לא אין יש עם על אל מן מכל כי גם רק אם כמו אבל עוד בו בה
בהם להם לו לה ממנו ממנה אותו אותה אותם שהוא שהיא שהם וזה וזו והוא והיא ולא כלומר היינו פירוש אלא
אך עדיין כבר כאן שם כך כן מה מי איך למה אשר עצמו עצמה עצמם בתוך לפי אחר אחרי לפני עד בין אף כאשר
ואם ואין ויש וכל וגם וכן וכך שאין שיש שכל שלא כדי מפני משום לכן לכך ולכן ובכל זהו וזהו הרי והרי
אחד אחת שני שתי ומה ממה שבו שבה שבהם בכך בזה מזה לזה כזה דבר דברים ענין עניין
""".split())
PREFIXES = "והבלמשכ"


def words(s: str) -> list[str]:
    s = NIQQUD.sub("", s)
    s = re.sub(r"[\"'׳״]", "", s)
    return re.findall(r"[א-ת]+", s)


def stem(w: str) -> set[str]:
    """The word and its forms with up to two prefix letters taken off."""
    out = {w}
    for _ in range(2):
        out |= {x[1:] for x in out if len(x) > 3 and x[0] in PREFIXES}
    return out


def content(ws: list[str]) -> list[str]:
    return [w for w in ws if w not in STOP and len(w) > 1]


def body_of(src: str) -> str:
    if src.startswith("---"):
        src = src.split("\n---", 1)[1]
    return src


def glosses(body: str):
    """Yield (section heading, bold before, gloss, has_source) for each gloss of the woven text."""
    section, section_bold = "", []
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("#"):
            section, section_bold = line.lstrip("# ").strip(), []
            continue
        if "**" not in line or line.startswith(("@", ":::", "|", "[")):
            continue
        nxt = next((l for l in lines[i + 1:] if l.strip()), "")
        src_after = nxt.startswith("@source") or nxt.startswith("@file")
        parts = re.split(r"(\*\*.+?\*\*)", line)
        prev_bold = ""
        for j, p in enumerate(parts):
            if p.startswith("**") and p.endswith("**"):
                prev_bold = p[2:-2]
                section_bold += words(prev_bold)
                continue
            if not prev_bold:
                continue
            has_fn = bool(FOOTNOTE.search(p))
            plain = FOOTNOTE.sub(" ", p)
            last = j == len(parts) - 1
            has_src = has_fn or bool(ADDRESS.search(plain)) or (last and src_after) or "\"" in re.sub(r"[א-ת]\"[א-ת]", "", plain)
            yield i + 1, section, prev_bold, plain.strip(" :;,.–—"), has_src, list(section_bold)


def tally(body: str) -> tuple[int, int, list[str]]:
    """(glosses, flagged, report rows) for the body of a woven biur.src.md."""
    flagged = total = 0
    rows = []
    for no, section, bold, gloss, has_src, sec_bold in glosses(body):
        cw = content(words(gloss))
        if not cw:
            continue
        total += 1
        pool = set()
        for w in sec_bold:
            pool |= stem(w)
        share = sum(1 for w in cw if stem(w) & pool) / len(cw)
        flag = not has_src and ((len(cw) >= 3 and share >= 0.5) or (len(cw) >= 6 and share == 1))
        flagged += flag
        mark = "RESTATES?" if flag else ("source" if has_src else "ok")
        rows.append((flag, f"  {mark:9} {int(share * 100):3}%  line {no:4}  [{section[:28]}]  "
                           f"**{bold[-40:]}** → {gloss[:110]}"))
    return total, flagged, rows


def check(path: Path, show_all: bool) -> int:
    src = path / "biur.src.md" if path.is_dir() else path
    total, flagged, rows = tally(body_of(src.read_text(encoding="utf-8")))
    print(f"{src}: {total} gloss(es), {flagged} flagged as restating the bold")
    print("\n".join(r for f, r in rows if f or show_all))
    return flagged


def main(argv: list[str]) -> int:
    show_all = "--all" in argv
    cap = None
    if "--max" in argv:
        cap = int(argv[argv.index("--max") + 1])
        argv = argv[:argv.index("--max")] + argv[argv.index("--max") + 2:]
    paths = [Path(a) for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    n = sum(check(p, show_all) for p in paths)
    return 1 if cap is not None and n > cap else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
