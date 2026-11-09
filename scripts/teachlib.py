"""The teaching pass (prompts/teaching-pass.md): its draft file and its checks,
shared by scripts/apply-teaching.py and scripts/check-teaching.py.

The draft is the explanation as it prints by default (after `edits:` and
`style:`), one block per paragraph, in order, under comment lines (`#`) that
name the cut of the text each paragraph explains. The writer replaces every
block with its teaching text, or with a lone `—` to drop it, and leaves the
comment lines alone.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import forgelib as F

DROP = "—"
TARGET = (0.35, 0.65)          # teaching words / default words: about half
LONG_SENTENCE = 40             # words
SHINGLE = 5                    # words in a phrase counted as a repeat

# Speech that a written commentary does not use. Warnings: each one is read in
# its sentence and kept only when it is the right word there.
SPEECH = [
    ("אני", "first person: a commentary speaks of the text, not of the speaker"),
    ("אנחנו", "first person plural: say what the text or the idea does"),
    ("אז", "spoken connective: use ולכן / ואם כן / נמצא, or nothing"),
    ("פה", "spoken: כאן"),
    ("עכשיו", "spoken: the lesson's time, not the text's"),
    ("בעצם", "filler"),
    ("באמת", "filler"),
    ("ממש", "filler unless it means 'literally'"),
    ("כאילו", "filler"),
    ("בוא", "addresses the listener"),
    ("תחשבו", "addresses the listener"),
    ("זאת אומרת", "spoken: כלומר, or say it directly"),
    ("על כל פנים", "spoken resumption"),
    ("אמרנו", "refers to the lesson: name the place (לעיל, בהערה א')"),
    ("בפעם הקודמת", "refers to a lesson: name the place in the book"),
    ("עוד מעט", "refers to the lesson's time: להלן"),
    ("קודם", "vague: לעיל, or name the place"),
    ("נכון", "a question to the listener"),
]
PREFIX = "[וש]{0,2}"             # ואז, שבעצם — not ל/מ/ב, which make other words (לממש, מאז)


def module(name: str, file: str):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).parent / file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def letters(s: str) -> str:
    s = F.COMMENT.sub("", s)
    return re.sub(r"[^א-ת]", "", s).translate(str.maketrans("ךםןףץ", "כמנפצ"))


def units(session: Path, paras: list[str]) -> list[tuple[str, list[int]]]:
    """[(heading, paragraph indexes)]: the cut each paragraph explains (a laid-out
    session), else the transcript's own labels, else one group."""
    plan_f = session / "section-plan.yaml"
    if plan_f.exists():
        BS = module("build_section", "build-section.py")
        plan = F.load_yaml(plan_f)
        nusach = BS.Nusach(plan, session)
        out, k = [], 0
        for n, (text, expl) in enumerate(BS.pairs(nusach, paras), 1):
            body = " ".join(p for p in text if ".src-label" not in p)
            words = F.words(re.sub(r"\{[^}]*\}|[\[\]]", " ", body))
            head = f"cut {n} — the text: «{' '.join(words[:7])} … {' '.join(words[-6:])}»"
            out.append((head, list(range(k, k + len(expl)))))
            k += len(expl)
        return out
    src = session / ("transcript.md" if F.voice_only(session) else "commentary.md")
    _, body, _ = F.split_frontmatter(src.read_text(encoding="utf-8"))
    out, k, label = [], 0, None
    for b in re.split(r"\n\s*\n", body.strip()):
        if b.lstrip().startswith("#"):
            label = b.strip().lstrip("#").strip()
            continue
        if F.prose(b) and k < len(paras):
            if not out or out[-1][0] != (label or "the explanation"):
                out.append((label or "the explanation", []))
            out[-1][1].append(k)
            k += 1
    return out


def write_draft(session: Path, target: Path) -> int:
    paras, holder, where = F.printed_paragraphs(session)
    # The teaching text recorded for each paragraph that still reads as it did;
    # a paragraph changed since (an edit, a style rewrite) starts from its new
    # lesson text and is marked, so only it is redone.
    table: dict[str, list[str]] = {}
    for e in holder.get("teaching") or []:
        table.setdefault(F.para_key(str(e.get("from") or "")), []).append(F.para_key(str(e.get("to") or "")))
    current, changed = [], set()
    for i, p in enumerate(paras):
        if holder.get("teaching") and table.get(F.para_key(p)):
            current.append(table[F.para_key(p)].pop(0) or DROP)
        else:
            current.append(p)
            if holder.get("teaching"):
                changed.add(i)
    if changed:
        print(f"  {len(changed)} paragraph(s) changed since the teaching pass, marked in the draft: "
              + ", ".join(f"¶{i + 1}" for i in sorted(changed)))
    lines = [f"# Teaching-pass draft for {session} ({len(paras)} paragraphs; {where.name} holds the result).",
             "# Replace each paragraph with its teaching text, or with a lone — to drop it. Keep the order",
             "# and the # lines. Then: python scripts/apply-teaching.py " + f"{session} {target}", ""]
    for head, idx in units(session, paras):
        lines += [f"# ── {head}", ""]
        for i in idx:
            if i in changed:
                lines += [f"# ¶{i + 1}: changed since the teaching pass — the lesson text below; rewrite it"]
            lines += [current[i], ""]
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {target}: {len(paras)} paragraphs, {len(F.words(' '.join(paras)))} words")
    return 0


def read_draft(f: Path) -> list[str]:
    text = "\n".join(ln for ln in f.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#"))
    return [" ".join(b.split()) for b in re.split(r"\n\s*\n", text) if b.strip()]


def corpus(session: Path) -> str:
    """Letters of everything a quotation may come from: the discourse's texts."""
    d = F.discourse_of(session)
    parts = []
    for s in sorted((d / "sessions").iterdir()):
        if (s / "ocr.md").exists():
            parts.append(F.ocr_body(s))
        if (s / "transcript.md").exists():
            _, body, _ = F.split_frontmatter((s / "transcript.md").read_text(encoding="utf-8"))
            parts += [b for b in re.split(r"\n\s*\n", body) if b.lstrip().startswith(">")]
    for f in sorted(d.glob("*.md")):
        if f.name not in ("discourse.md", "notes.md") and ".teaching." not in f.name:
            parts.append(f.read_text(encoding="utf-8"))
    return letters(" ".join(parts))


QUOTE = re.compile(r'(?:(?<=^)|(?<=[\s(—]))"(?=[א-ת])(.+?)(?<=[א-ת.,\'])"(?=[\s.,:;)—]|$)')


def check(session: Path, before: list[str], after: list[str | None]) -> tuple[list[str], list[str], dict]:
    """(errors, warnings, stats) for one session's teaching text."""
    errors, warns = [], []
    text = corpus(session)
    n_before = sum(len(F.words(p)) for p in before)
    n_after = sum(len(F.words(p)) for p in after if p)
    for i, (a, t) in enumerate(zip(before, after), 1):
        if not t:
            continue
        where = f"¶{i}"
        if re.search(r"[A-Za-z]", t):
            errors.append(f"{where}: Latin letters — {' '.join(re.findall(r'[A-Za-z]+', t))}")
        if t.count("(") != t.count(")"):
            errors.append(f"{where}: unbalanced parentheses")
        loose = len(re.findall(r'(?<![א-ת])"|"(?![א-ת])', t))
        if loose % 2:
            errors.append(f"{where}: an unclosed quotation mark")
        for q in QUOTE.findall(t):
            if len(q.split()) >= 3 and letters(q) not in text and letters(q) not in letters(a):
                errors.append(f"{where}: quotation not in the text (nor in the paragraph it replaces): “{q}”")
        for s in re.split(r"(?<=[.:;?!])\s+", t):
            if len(s.split()) > LONG_SENTENCE:
                warns.append(f"{where}: a sentence of {len(s.split())} words — “{' '.join(s.split()[:8])}…”")
        for word, why in SPEECH:
            for m in re.finditer(rf"(?<![א-ת\"']){PREFIX}{word}(?![א-ת\"'])", t):
                ctx = t[max(0, m.start() - 25):m.end() + 25].replace("\n", " ")
                warns.append(f"{where}: “{word}” ({why}) — …{ctx}…")
    stats = {"paragraphs": len(before), "kept": sum(1 for t in after if t), "before": n_before, "after": n_after}
    ratio = n_after / max(1, n_before)
    if not TARGET[0] <= ratio <= TARGET[1]:
        warns.append(f"length: {n_after} words of {n_before} ({ratio:.0%}); the pass aims at about half "
                     f"({TARGET[0]:.0%}–{TARGET[1]:.0%}) — check nothing was lost, or that nothing is left to cut")
    return errors, warns, stats


def repeats(named_texts: list[tuple[str, str]]) -> list[str]:
    """Phrases of SHINGLE words that occur in two places (another paragraph or
    another part), quotations of the text included."""
    seen: dict[tuple[str, ...], str] = {}
    out, reported = [], set()
    for where, t in named_texts:
        toks = [(letters(w), w) for w in F.words(t)]
        toks = [x for x in toks if x[0]]
        local = set()
        for j in range(len(toks) - SHINGLE + 1):
            g = tuple(x[0] for x in toks[j:j + SHINGLE])
            if g in local:
                continue
            local.add(g)
            if g in seen and seen[g] != where and (seen[g], where) not in reported:
                reported.add((seen[g], where))
                raw = " ".join(x[1] for x in toks[j:j + SHINGLE + 3])
                out.append(f"{seen[g]} and {where} share “{raw}…”")
            seen.setdefault(g, where)
    return out
