#!/usr/bin/env python3
"""Join the built chapters of a ביאור written chapter by chapter into one book: a title page, a contents
page (each chapter's folios, its topics and the page it starts on), the chapters in order, each opening
on a new page, and the colophon once at the end. Prints with WeasyPrint through build-biur's to_pdf, so
the layout is that of the single chapters (templates/biur-woven.css), plus templates/biur-book.css.

Usage:
    python scripts/combine-biur.py <discourse> <folder-glob> <pdf-name> "<title>" "<subtitle>"
    e.g. python scripts/combine-biur.py discourses/007-shaar-hayichud-perushim "biur-perek-*" \
         007-shaar-hayichud-complete "שער היחוד" "מאמר כ\"ק אדמו\"ר האמצעי · נר מצוה ותורה אור · עם ביאור"

Reads each folder's built biur.md (build every chapter first: build-biur.py <folder>); writes
output/biur/<pdf-name>.md and .pdf. Nothing in the discourse is changed.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("build_biur", ROOT / "scripts" / "build-biur.py")
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)

FRONT = re.compile(r"\A---\n.*?\n---\n", re.S)
WORKS = re.compile(r"^::: \{\.works\}\n.*?^:::\n?", re.S | re.M)


def chapter(md: str, n: int) -> tuple[str, str, str, list[str], str]:
    """The chapter's body for the book, and what the contents page needs: its name, folios, topics."""
    body = FRONT.sub("", md)
    body = bb.PNUM_TAG.sub("", body)
    works = (WORKS.search(body) or [""])[0]
    body = WORKS.sub("", body)
    body = re.sub(r"^\[בס\"ד\]\{\.bsd\}\n", "", body, flags=re.M)
    body = re.sub(r"^\[\[SEFER FORGE\]\{\.wordmark\}.*\{\.brand\}\n", "", body, flags=re.M)
    h1 = re.search(r"^# (.+)$", body, re.M)
    name = h1.group(1).split("·")[-1].strip()                     # "פרק א"
    body = body.replace(h1.group(0), f'# {h1.group(1)} {{#perek-{n:02d} .chapter data-short="{name}"}}', 1)
    sub = re.search(r"·\s*(דף [^·]+?)\s*·", body)
    folios = sub.group(1).strip() if sub else ""
    topics = []
    out = re.search(r"::: \{\.outline\}\n(.*?)\n:::", body, re.S)
    if out:
        for row in out.group(1).splitlines()[2:]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 3:
                topics.append(cells[2])
    return body.strip() + "\n", name, folios, topics, works


def main(argv: list[str]) -> int:
    if len(argv) < 5:
        print(__doc__)
        return 2
    disc, pattern, pdf_name, title, subtitle = argv[:5]
    folders = sorted((ROOT / disc).glob(pattern))
    parts, toc, works = [], [], ""
    for n, f in enumerate(folders, 1):
        md = (f / "biur.md")
        if not md.is_file():
            print(f"ERROR: {md.relative_to(ROOT)} not built")
            return 1
        text = md.read_text(encoding="utf-8")
        body, name, folios, topics, w = chapter(text, n)
        works = w or works
        parts.append(body)
        topic = " · ".join(topics)
        toc.append(f'[[{name}]{{.tn}} [{folios}]{{.tf}} [{topic}]{{.tt}}](#perek-{n:02d}){{.toc-line}}\n')
    span = f"פרקים א–{bb.heb_num(len(folders)).replace(chr(34), '')}"
    head = [
        "---", f"title: '{title}'", "lang: he", "---", "",
        '[בס"ד]{.bsd}', "",
        f"# {title} {{.booktitle}}", "",
        f"[{subtitle}]{{.subtitle}}", "",
        f"[{span} · {len(folders)} פרקים]{{.subtitle .span}}", "",
        "[[SEFER FORGE]{.wordmark} · The inner Torah, explained and taught · esoterics611.github.io]{.brand}", "",
        "::: {.toc}", "## תוכן העניינים {.toc-head}", "",
        *[line for t in toc for line in (t, "")],
        ":::", "",
    ]
    book = "\n".join(head) + "\n\n".join(parts) + "\n" + works
    out = ROOT / "output" / "biur" / f"{pdf_name}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(book, encoding="utf-8")
    meta = {"title": title, "engine": "weasyprint", "css": ["templates/biur-woven.css", "templates/biur-book.css"]}
    pdf = out.with_suffix(".pdf")
    bb.to_pdf(out, meta, pdf)
    print(f"wrote {pdf.relative_to(ROOT)} ({len(folders)} chapters)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
