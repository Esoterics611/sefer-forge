#!/usr/bin/env python3
"""Build a session's reading pack: its text, broken after each citation, with
the cited passage set below it (context before and after, the words the
citation refers to highlighted). The lesson is recorded over this document.

Usage:
    python scripts/build-references.py discourses/004-levushei-haneshama/sessions/001
    python scripts/build-references.py <session> --png      # also page images for checking
    python scripts/build-references.py <session> --marked-text <file.md>
                                     # also the text alone, each citation marked with
                                     # its box's letter, for a pamphlet's opening part

Reads <session>/references.yaml (the plan; its header documents the keys) and
<session>/ocr.md (the text). Passages come from the works in sources/
(sources/sources.yaml), quoted exactly; only the highlighting is added.
Writes <session>/references.md, output/references/<discourse>-<session>.pdf,
the HTML it printed from under output/references/html/, and with --png one
image per page under output/references/png/. Run from the repo root.

The build stops, naming the place, when:
  - a citation's `at` words are not in the text (in order);
  - a citation in the text (ע"ח, פע"ח, שער ..., זוהר, גלגולים ...) is in
    neither `cites` nor `others`, so nothing the text cites is skipped unseen;
  - an excerpt's `from`/`to` words are not in the passage, or a `mark` is
    not in the excerpt;
  - a `see` points at a box without that `mark`.

Rendering: Chrome's headless print-to-PDF, styled by templates/references.css
(A4, Frank Ruhl Libre from templates/fonts/). CHROME overrides the browser.
Proof the PDF with scripts/proof-pdf.py (profile references) before handing it over.
"""
from __future__ import annotations

import html
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

import forgelib as F
import sourcelib as S

CSS = Path("templates/references.css")
OUT = Path("output/references")
WIN_CHROME = "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
# A citation in the text: a work's name or a gate number (ש"מ, של"ט, שער, ש').
SCAN = re.compile(r'פע"ח|ע"ח|(?<![א-ת])שער(?![א-ת])|(?<![א-ת])ש\' |(?<![א-ת])ש[א-ת]?"[א-ת](?![א-ת])'
                  r'|גלגולים|זוהר|לק"ת|טעמי|(?<![א-ת])[בו]?כוונות|מק"מ|הסבא')
NOT_CITES = {'ש"י', 'שא"א'}               # תפלין ש"י (של יד), שא"א (שאי אפשר): not gates
ONES, TENS = "אבגדהוזחט", "יכלמנסעפצ"


class PlanError(Exception):
    pass


def heb(n: int) -> str:
    """6 → ו', 49 → מ"ט, 15 → ט"ו."""
    if n in (15, 16):
        s = "טו" if n == 15 else "טז"
    else:
        s = (TENS[n // 10 - 1] if n >= 10 else "") + (ONES[n % 10 - 1] if n % 10 else "")
    return s + "'" if len(s) == 1 else s[:-1] + '"' + s[-1]


def esc(s: str) -> str:
    return html.escape(s, quote=False)


# --- the text ------------------------------------------------------------------

def place(text: str, phrase: str, start: int, what: str) -> tuple[int, int]:
    m = S.locate(text, phrase, start)
    if m is None:
        raise PlanError(f"{what}: “{phrase}” not in the text" + (" after the previous citation" if start else ""))
    return m


def sentence_end(text: str, at: int) -> int:
    m = re.compile(r'[.:]').search(text, at)
    end = m.end() if m else len(text)
    while end < len(text) and text[end] in ")]":
        end += 1
    return end


def anchors(text: str, plan: dict) -> tuple[list[dict], list[tuple[int, int]]]:
    """Each cite with its span and cut in the text; the spans of `others`."""
    cites, pos = [], 0
    for i, c in enumerate(plan.get("cites") or [], 1):
        s, e = place(text, c["at"], pos, f"cite {i}")
        if c.get("cut_after"):
            cut = place(text, c["cut_after"], s, f"cite {i} cut_after")[1]
            while cut < len(text) and text[cut] in ".:)]":
                cut += 1
        else:
            cut = sentence_end(text, e)
        if cites:
            cut = max(cut, cites[-1]["cut"])
        cites.append({**c, "n": i, "span": (s, e), "cut": cut})
        pos = e
    others = []
    for o in plan.get("others") or []:
        for phrase in ([o["at"]] if isinstance(o["at"], str) else o["at"]):
            others.append(place(text, phrase, 0, "others"))
    return cites, others


def uncovered(text: str, spans: list[tuple[int, int]]) -> list[str]:
    """Citations the scan finds outside every planned span."""
    hits: list[list[int]] = []
    for m in SCAN.finditer(text):
        if m.group().strip() in NOT_CITES or any(s <= m.start() < e for s, e in spans):
            continue
        if hits and m.start() - hits[-1][1] <= 12:        # ע"ח של"ט: one citation, two hits
            hits[-1][1] = m.end()
        else:
            hits.append([m.start(), m.end()])
    return ["…" + text[max(0, s - 25):e + 25].replace("\n", " ") + "…" for s, e in hits]


# --- excerpts -----------------------------------------------------------------

def excerpt(ex: dict, where: str) -> dict:
    work = ex["work"]
    refs = ex["ref"] if isinstance(ex["ref"], list) else [ex["ref"]]
    paras = []
    for r in refs:
        try:
            paras.append(S.text(work, str(r)))
        except KeyError as e:
            raise PlanError(f"{where}: {e}") from None
    s, e = 0, len(paras[-1])
    if ex.get("from"):
        m = S.locate(paras[0], ex["from"])
        if m is None:
            raise PlanError(f"{where}: from “{ex['from']}” not in {work} {refs[0]}")
        s = m[0]
    if ex.get("to"):
        m = S.locate(paras[-1], ex["to"], s if len(refs) == 1 else 0)
        if m is None:
            raise PlanError(f"{where}: to “{ex['to']}” not in {work} {refs[-1]}")
        e = m[1]
        while e < len(paras[-1]) and paras[-1][e] in ".:)]":
            e += 1
    if len(paras) == 1:
        parts = [paras[0][s:e]]
    else:
        parts = [paras[0][s:], *paras[1:-1], paras[-1][:e]]
    marks = ex.get("mark") or []
    spans = [[] for _ in parts]
    for mk in marks:
        found = False
        for k, p in enumerate(parts):
            at = 0
            while (m := S.locate(p, mk, at)) is not None:
                spans[k].append(m)
                at, found = m[1], True
        if not found:
            raise PlanError(f"{where}: mark “{mk}” not in the excerpt")
    return {"work": work, "ref": str(refs[0]), "parts": parts, "spans": [merge(x) for x in spans],
            "lead": s > 0, "tail": e < len(paras[-1])}


def merge(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    out: list[list[int]] = []
    for s, e in sorted(spans):
        if out and s <= out[-1][1]:
            out[-1][1] = max(out[-1][1], e)
        else:
            out.append([s, e])
    return [tuple(x) for x in out]


def marked(text: str, spans, open_: str, close: str, escape=esc) -> str:
    out, at = [], 0
    for s, e in spans:
        out += [escape(text[at:s]), open_, escape(text[s:e]), close]
        at = e
    out.append(escape(text[at:]))
    return "".join(out)


def label(ex: dict) -> str:
    work, ref = ex["work"], ex["ref"]
    entry = S.catalog()[work]
    bits = ref.split(".")
    gate = S.gate_title(work, ref).removeprefix("שער ").strip()
    if S.named_gates(work):
        head = f"שער {gate}" if gate else bits[0]
    else:
        head = f"שער {heb(int(bits[0]))}" + (f" ({gate})" if gate else "")
    out = f"{entry['title']} · {head}"
    if len(bits) > 1 and bits[1].isdigit():
        unit = "דרוש" if work == "etz-chaim" and bits[0] in ("39", "40") else "פרק"
        out += f" · {unit} {heb(int(bits[1]))}"
    return out


def boxes(cites: list[dict]) -> None:
    for c in cites:
        where = f"cite {c['n']} ({c['at']})"
        if c.get("see"):
            target = next((x for x in cites if x["n"] == c["see"]), None)
            if not target or not target.get("excerpts_built"):
                raise PlanError(f"{where}: see {c['see']} is not an earlier box with a passage")
            body = " ".join(" ".join(x["parts"]) for x in target["excerpts_built"])
            for mk in c.get("mark") or []:
                if S.locate(body, mk) is None:
                    raise PlanError(f"{where}: mark “{mk}” not in box {c['see']}")
            c["label_text"] = c.get("label") or target["label_text"]
            continue
        exs = c.get("excerpts") or [{k: c[k] for k in ("work", "ref", "from", "to", "mark") if k in c}]
        c["excerpts_built"] = [excerpt(x, where) for x in exs]
        c["label_text"] = c.get("label") or label(c["excerpts_built"][0])


# --- output -------------------------------------------------------------------

def gloss(text: str, a: int, b: int, cites: list[dict], fmt, escape=lambda s: s) -> list[str]:
    """Paragraphs of text[a:b], escaped, with the citations in it marked by fmt(cite, words)."""
    out, at = [], a
    for c in cites:
        s, e = c["span"]
        if a <= s < b:
            out += [escape(text[at:s]), fmt(c, text[s:e])]
            at = e
    out.append(escape(text[at:b]))
    return [p.strip() for p in "".join(out).split("\n\n") if p.strip()]


def divides(plan: dict, paragraph: str) -> bool:
    """Whether a paragraph opens with the plan's `divider_before` words (a new maamar)."""
    words = plan.get("divider_before")
    m = S.locate(paragraph, words) if words else None
    return m is not None and m[0] == 0


def segments(text: str, cites: list[dict]):
    """(start, end, cites boxed after it) in text order; the tail after the last cut has none."""
    at = 0
    for cut in sorted({c["cut"] for c in cites}):
        yield at, cut, [c for c in cites if c["cut"] == cut]
        at = cut
    if at < len(text):
        yield at, len(text), []


def to_html(plan: dict, text: str, cites: list[dict], css: str) -> str:
    def cite_html(c, words):
        return f'<span class="cite">{esc(words)}<sup>{c["n"]}</sup></span>'

    body = [f'<h1>{esc(plan["title"])}</h1>']
    if plan.get("subtitle"):
        body.append(f'<p class="sub">{esc(plan["subtitle"])}</p>')
    if plan.get("source"):
        body.append(f'<p class="src">{esc(plan["source"])}</p>')
    body.append('<p class="legend">המספר שליד המובאה מוביל לתיבה שאחרי הקטע. בתיבה — המקור, עם שורות לפניו ואחריו; '
                '<mark>מסומן</mark> — המילים שההגהה מביאה או רומזת אליהן.</p>')
    for a, b, here in segments(text, cites):
        for p in gloss(text, a, b, cites, cite_html, esc):
            if divides(plan, p):
                body.append('<div class="divider"></div>')
            body.append(f'<p class="text">{p}</p>')
        for c in here:
            body.append(box_html(c))
    if plan.get("others"):
        body.append('<div class="others"><h2>מקורות אחרים שבהגהה (לא הובאו כאן)</h2><ul>')
        body += [f'<li>{esc(o["what"])}</li>' for o in plan["others"]]
        body.append("</ul></div>")
    return ('<!doctype html><html lang="he" dir="rtl"><head><meta charset="utf-8">'
            f'<title>{esc(plan["title"])}</title><style>{css}</style></head><body>'
            + "\n".join(body) + "</body></html>")


def skipped(before: dict, after: dict) -> bool:
    """Whether text between two excerpts of one box is left out unmarked: neither
    excerpt shows "…" at the join (whole paragraphs skipped)."""
    return not before["tail"] and not after["lead"]


def box_html(c: dict) -> str:
    head = f'<div class="head"><span class="n">{c["n"]}</span> {esc(c["label_text"])}</div>'
    note = f'<div class="note">{esc(c["note"])}</div>' if c.get("note") else ""
    if c.get("see"):
        marks = " · ".join(f"<mark>{esc(m)}</mark>" for m in c.get("mark") or [])
        return (f'<div class="box">{head}<div class="see">הקטע בתיבה {c["see"]} לעיל'
                + (f": {marks}" if marks else "") + f"</div>{note}</div>")
    parts, prev = [], c["label_text"]
    exs = c["excerpts_built"]
    for i, ex in enumerate(exs):
        if i and label(ex) != prev:
            parts.append(f'<div class="sublabel">{esc(label(ex))}</div>')
        elif i and skipped(exs[i - 1], ex):
            parts.append('<p class="gap">…</p>')
        prev = label(ex)
        n = len(ex["parts"])
        for k, (p, sp) in enumerate(zip(ex["parts"], ex["spans"])):
            pre = "…" if k == 0 and ex["lead"] else ""
            post = "…" if k == n - 1 and ex["tail"] else ""
            parts.append(f'<p>{pre}{marked(p, sp, "<mark>", "</mark>")}{post}</p>')
    return f'<div class="box">{head}{note}<div class="ex">{"".join(parts)}</div></div>'


def to_md(plan: dict, text: str, cites: list[dict], session: Path) -> str:
    def cite_md(c, words):
        return f"**{words}**^[{c['n']}]^"

    out = ["---", f"title: {yaml.safe_dump(plan['title'], allow_unicode=True).strip().splitlines()[0]}",
           f"session: {session.name}", "built_from: references.yaml", "---", "",
           "<!-- Built by scripts/build-references.py from references.yaml and ocr.md. Edit the plan and rebuild. -->", ""]
    for a, b, here in segments(text, cites):
        for p in gloss(text, a, b, cites, cite_md):
            if divides(plan, p):
                out.append("* * *\n")
            out.append(p + "\n")
        for c in here:
            out.append(f"> **[{c['n']}] {c['label_text']}**")
            if c.get("note"):
                out.append(f">\n> _{c['note']}_")
            if c.get("see"):
                out.append(f">\n> הקטע בתיבה {c['see']} לעיל" +
                           (": " + " · ".join(f"**{m}**" for m in c.get("mark") or []) if c.get("mark") else ""))
            else:
                prev = c["label_text"]
                exs = c["excerpts_built"]
                for i, ex in enumerate(exs):
                    if i and label(ex) != prev:
                        out.append(f">\n> _{label(ex)}_")
                    elif i and skipped(exs[i - 1], ex):
                        out.append(">\n> …")
                    prev = label(ex)
                    n = len(ex["parts"])
                    for k, (p, sp) in enumerate(zip(ex["parts"], ex["spans"])):
                        pre = "…" if k == 0 and ex["lead"] else ""
                        post = "…" if k == n - 1 and ex["tail"] else ""
                        out.append(">\n> " + pre + marked(p, sp, "**", "**", lambda x: x) + post)
            out.append("")
    if plan.get("others"):
        out += ["## מקורות אחרים שבהגהה (לא הובאו כאן)", ""] + [f"- {o['what']}" for o in plan["others"]] + [""]
    return "\n".join(out)


def marked_text(plan: dict, text: str, cites: list[dict], session: Path) -> str:
    """The text up to `divider_before` (what follows is another maamar), each
    citation followed by its box's letter as a superscript, as a transcript-style
    file: its title becomes the part's heading, each paragraph a quoted passage."""
    end = len(text)
    if plan.get("divider_before") and (m := S.locate(text, plan["divider_before"])):
        end = m[0]
    out, at = [], 0
    for c in cites:
        s, e = c["span"]
        if e > end:
            break
        out += [text[at:e], f'^{heb(c["n"]).replace(chr(39), "")}^']
        at = e
    out.append(text[at:end])
    paras = [p.strip() for p in "".join(out).split("\n\n") if p.strip()]
    fm = {"title": plan.get("text_title") or plan["title"]}
    if plan.get("text_subtitle"):
        fm["subtitle"] = plan["text_subtitle"]
    return ("---\n" + yaml.safe_dump(fm, allow_unicode=True, width=10000) + "---\n\n"
            + f"<!-- Generated by scripts/build-references.py {session} --marked-text: the text of "
              f"{session}/ocr.md, each citation marked with its box in references.yaml. Do not edit. -->\n\n"
            + "\n\n".join("> " + p for p in paras) + "\n")


def chrome() -> str:
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    if Path(WIN_CHROME).exists():
        return WIN_CHROME
    for name in ("google-chrome", "chromium", "chromium-browser"):
        if shutil.which(name):
            return name
    sys.exit("No Chrome found: set CHROME to the browser's path")


def print_pdf(html_path: Path, pdf_path: Path) -> None:
    exe = chrome()
    src, dst = html_path.resolve(), pdf_path.resolve()
    if exe.endswith(".exe"):          # Windows Chrome from WSL needs Windows paths
        src, dst = (subprocess.run(["wslpath", "-w", str(p)], capture_output=True, text=True,
                                   check=True).stdout.strip() for p in (src, dst))
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--no-sandbox",
                    "--allow-file-access-from-files", f"--print-to-pdf={dst}", str(src)],
                   check=True, capture_output=True)
    if not pdf_path.exists():
        sys.exit(f"Chrome wrote no PDF for {html_path}")


def main(argv: list[str]) -> int:
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--marked-text")]
    if len(args) != 1:
        print(__doc__)
        return 2
    session = Path(args[0].rstrip("/"))
    plan_f = session / "references.yaml"
    if not plan_f.exists() or not (session / "ocr.md").exists():
        print(f"{session}: needs references.yaml and ocr.md")
        return 1
    plan = yaml.safe_load(plan_f.read_text(encoding="utf-8"))
    text = F.ocr_text(session)
    try:
        cites, others = anchors(text, plan)
        missed = uncovered(text, [c["span"] for c in cites] + others)
        if missed:
            raise PlanError("citations in the text that the plan does not list (add to cites or others):\n  "
                            + "\n  ".join(missed))
        boxes(cites)
    except PlanError as e:
        print(f"{plan_f}: {e}")
        return 1

    (session / "references.md").write_text(to_md(plan, text, cites, session), encoding="utf-8")
    if "--marked-text" in argv:
        k = argv.index("--marked-text")
        if k + 1 >= len(argv):
            print("--marked-text needs a file path")
            return 2
        Path(argv[k + 1]).write_text(marked_text(plan, text, cites, session), encoding="utf-8")
        print(f"marked text: {argv[k + 1]}")
    name = f"{F.discourse_of(session).name}-{session.name}"
    (OUT / "html").mkdir(parents=True, exist_ok=True)
    html_path, pdf = OUT / "html" / f"{name}.html", OUT / f"{name}.pdf"
    html_path.write_text(to_html(plan, text, cites, CSS.read_text(encoding="utf-8")), encoding="utf-8")
    print_pdf(html_path, pdf)
    pages = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                                        text=True).stdout)
    n_boxes = sum(1 for c in cites if not c.get("see"))
    print(f"{pdf}: {pages.group(1) if pages else '?'} pages · {len(cites)} citations "
          f"({n_boxes} passages) · {len(plan.get('others') or [])} other works listed")
    print(f"{session / 'references.md'}")
    if "--png" in argv:
        png = OUT / "png"
        png.mkdir(parents=True, exist_ok=True)
        for old in png.glob(f"{name}-*.png"):
            old.unlink()
        subprocess.run(["pdftoppm", "-png", "-r", "80", str(pdf), str(png / name)], check=True)
        print(f"page images: {png}/{name}-*.png")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
