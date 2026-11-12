#!/usr/bin/env python3
"""The lexicon of the knowledge layer (knowledge/lexicon/): look a term up,
find the terms a text uses, check every entry against sources/, and write the
index.

Usage:
    python scripts/lexicon.py צלם                      # an entry (by term or any of its forms), its sources quoted in context
    python scripts/lexicon.py --in discourses/004-levushei-haneshama/sessions/001/ocr.md
                                                       # the lexicon's terms that a text uses, most frequent first
    python scripts/lexicon.py --check                  # every entry: format, addresses, quoted words, related terms
    python scripts/lexicon.py --index                  # write knowledge/lexicon/INDEX.md (also done by --check when clean)
    python scripts/lexicon.py --list                   # one line per entry

An entry is one YAML file, knowledge/lexicon/<slug>.yaml (knowledge/README.md
gives the format). Its meanings are an explanation; what each rests on is a
line in sources/ given by address with the exact words, so --check can show
that the words are there. A meaning that rests on nothing in sources/ says so
under `open:`.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import yaml

import sourcelib as S

ROOT = S.ROOT
LEXICON = ROOT / "knowledge" / "lexicon"
INDEX = LEXICON / "INDEX.md"
STATUSES = ("draft", "checked")
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
KEYS = {"term", "forms", "category", "abbrev", "senses", "related", "caution", "open", "status",
        "learned_from", "teacher"}
SENSE_KEYS = {"meaning", "rests_on", "note"}
SOURCE_KEYS = {"work", "ref", "page", "quote", "note", "cite"}
CONTEXT = 120
PREFIX = "ובלהמשכ"          # letters that join the front of a Hebrew word


def norm(s: str) -> str:
    """Niqqud off, quote marks unified (״ → ", ׳ → ')."""
    return S.NIQQUD.sub("", s).replace("״", '"').replace("׳", "'").replace("”", '"').replace("’", "'")


def entries() -> dict[str, dict]:
    out = {}
    for f in sorted(LEXICON.glob("*.yaml")):
        out[f.stem] = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    return out


def forms_of(e: dict) -> list[str]:
    fs = [e.get("term", "")] + list(e.get("forms") or [])
    return [norm(f).strip() for f in fs if f and norm(f).strip()]


def form_pattern(form: str) -> re.Pattern:
    """A form as a whole word, with up to three joined prefix letters (ובמ"ן, לצלם)."""
    body = r"\s+".join(re.escape(w) for w in form.split())
    return re.compile(rf"(?<![א-ת\"'])[{PREFIX}]{{0,3}}{body}(?![א-ת])")


# --- sources ------------------------------------------------------------------

def rows_for(src: dict) -> list[tuple[str, str]]:
    work = src.get("work")
    if src.get("page"):
        vol, page = str(src["page"]).split()
        return S.page_rows(work, int(vol), page)
    return S.under(work, str(src["ref"]))


def locate(src: dict) -> tuple[str, str, int, int] | None:
    """(address, text, start, end) of the quote inside the rows the source names."""
    for a, t in rows_for(src):
        m = S.locate(t, src["quote"])
        if m:
            return a, t, m[0], m[1]
    return None


def where(src: dict) -> str:
    if not src.get("work"):
        return src.get("cite", "?")
    title = S.catalog()[src["work"]]["title"]
    return f"{title} {('דף ' + str(src['page'])) if src.get('page') else src.get('ref')}"


# --- check --------------------------------------------------------------------

def check() -> int:
    errors, warnings = [], []
    es = entries()
    seen_forms: dict[str, str] = {}
    works = S.catalog()
    for slug, e in es.items():
        here = f"{slug}.yaml"
        if not SLUG.match(slug):
            errors.append(f"{here}: file name must be a lowercase transliteration with hyphens (e.g. mayin-nukvin)")
        if not isinstance(e, dict):
            errors.append(f"{here}: not a mapping")
            continue
        for k in set(e) - KEYS:
            errors.append(f"{here}: unknown key {k!r}")
        for k in ("term", "senses", "status", "category"):
            if not e.get(k):
                errors.append(f"{here}: missing {k!r}")
        if e.get("status") and e["status"] not in STATUSES:
            errors.append(f"{here}: status must be one of {STATUSES}")
        for f in forms_of(e):
            if f in seen_forms and seen_forms[f] != slug:
                warnings.append(f"{here}: form {f!r} is also in {seen_forms[f]}.yaml")
            seen_forms.setdefault(f, slug)
        for r in e.get("related") or []:
            if r not in es:
                errors.append(f"{here}: related term {r!r} has no entry")
        for i, sense in enumerate(e.get("senses") or [], 1):
            tag = f"{here} sense {i}"
            if not isinstance(sense, dict) or not sense.get("meaning"):
                errors.append(f"{tag}: needs a meaning")
                continue
            for k in set(sense) - SENSE_KEYS:
                errors.append(f"{tag}: unknown key {k!r}")
            srcs = sense.get("rests_on") or []
            if not srcs and not e.get("open"):
                errors.append(f"{tag}: rests on nothing; give sources or say why under 'open:'")
            for j, src in enumerate(srcs, 1):
                stag = f"{tag} source {j}"
                for k in set(src) - SOURCE_KEYS:
                    errors.append(f"{stag}: unknown key {k!r}")
                if not src.get("work"):
                    if not src.get("cite"):
                        errors.append(f"{stag}: a source outside sources/ needs 'cite:' (and is not checked)")
                    else:
                        warnings.append(f"{stag}: {src['cite']!r} is not in sources/; not checked")
                    continue
                if src["work"] not in works:
                    errors.append(f"{stag}: unknown work {src['work']!r} (sources/sources.yaml)")
                    continue
                if not (src.get("ref") or src.get("page")):
                    errors.append(f"{stag}: needs 'ref:' (an address) or 'page:' (volume and printed page)")
                    continue
                if not src.get("quote"):
                    errors.append(f"{stag}: needs 'quote:', the exact words")
                    continue
                if not rows_for(src):
                    errors.append(f"{stag}: nothing at {where(src)}")
                elif not locate(src):
                    hits = S.find(src["work"], src["quote"])
                    hint = f"; the words are at {', '.join(a for a, _, _ in hits[:3])}" if hits else "; not found anywhere in the work"
                    errors.append(f"{stag}: {src['quote']!r} is not at {where(src)}{hint}")
    for w in warnings:
        print(f"warning: {w}")
    for err in errors:
        print(f"ERROR: {err}")
    n_src = sum(len(s.get("rests_on") or []) for e in es.values() if isinstance(e, dict) for s in e.get("senses") or [] if isinstance(s, dict))
    print(f"{len(es)} entries, {n_src} source passages: {len(errors)} error(s), {len(warnings)} warning(s)")
    if not errors:
        write_index(es)
    return 1 if errors else 0


# --- index --------------------------------------------------------------------

def gloss(e: dict) -> str:
    m = " ".join(str(e["senses"][0]["meaning"]).split())
    return m if len(m) <= 110 else m[:107].rsplit(" ", 1)[0] + "…"


def write_index(es: dict[str, dict]) -> None:
    by_cat: dict[str, list[tuple[str, dict]]] = {}
    for slug, e in es.items():
        by_cat.setdefault(e.get("category", "—"), []).append((slug, e))
    lines = ["---", "generated_by: scripts/lexicon.py --index", "---", "",
             "# הלקסיקון — index", "",
             "Generated; do not edit. One line per entry: the term, the file, the first meaning.",
             "Read the entry itself (`python scripts/lexicon.py <term>`) before relying on it.", ""]
    for cat in sorted(by_cat):
        lines += [f"## {cat}", ""]
        for slug, e in sorted(by_cat[cat], key=lambda x: norm(x[1]["term"])):
            mark = "" if e.get("status") == "checked" else " *(draft)*"
            lines.append(f"- [{e['term']}]{{dir=\"rtl\"}} — `{slug}`{mark}: [{gloss(e)}]{{dir=\"rtl\"}}")
        lines.append("")
    INDEX.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {INDEX.relative_to(ROOT)}")


# --- look-up ------------------------------------------------------------------

def find_entries(word: str) -> list[str]:
    w = norm(word).strip()
    es = entries()
    exact = [s for s, e in es.items() if w in forms_of(e) or w == s]
    if exact:
        return exact
    return [s for s, e in es.items() if any(w in f for f in forms_of(e))]


def show(slug: str) -> None:
    e = entries()[slug]
    print(f"# {e['term']}   ({slug}, {e.get('status')}; {e.get('category')})")
    if e.get("forms"):
        print("forms: " + " · ".join(e["forms"]))
    for k, v in (e.get("abbrev") or {}).items():
        print(f"  {k} = {v}")
    for i, sense in enumerate(e["senses"], 1):
        print(f"\n{i}. {' '.join(str(sense['meaning']).split())}")
        if sense.get("note"):
            print(f"   ({' '.join(str(sense['note']).split())})")
        for src in sense.get("rests_on") or []:
            if not src.get("work"):
                print(f"   — {src.get('cite')}  [not in sources/]")
                continue
            hit = locate(src) if src.get("quote") else None
            if not hit:
                print(f"   — {where(src)}: {src.get('quote')}  [NOT FOUND: run --check]")
                continue
            a, t, s, en = hit
            ctx = ("…" if s > CONTEXT else "") + t[max(0, s - CONTEXT):s] + "【" + t[s:en] + "】" + t[en:en + CONTEXT] + "…"
            print(f"   — {S.catalog()[src['work']]['title']} {a}: {ctx}")
            if src.get("note"):
                print(f"     ({src['note']})")
    for k, label in (("caution", "caution"), ("open", "open")):
        if e.get(k):
            print(f"\n{label}: {' '.join(str(e[k]).split())}")
    for t in e.get("teacher") or []:
        print(f"\nteacher: {' '.join(str(t.get('said', '')).split())}  ({t.get('where', '')})")
    if e.get("related"):
        print("\nrelated: " + ", ".join(e["related"]))
    if e.get("learned_from"):
        print("learned from: " + ", ".join(e["learned_from"]))


def in_text(path: str) -> int:
    text = norm(Path(path).read_text(encoding="utf-8"))
    counts: Counter = Counter()
    es = entries()
    for slug, e in es.items():
        for f in set(forms_of(e)):
            counts[slug] += len(form_pattern(f).findall(text))
    used = [(s, n) for s, n in counts.most_common() if n]
    for s, n in used:
        print(f"{n:>4}  {es[s]['term']:<30} {s}")
    print(f"{len(used)} of {len(es)} lexicon terms occur in {path}")
    return 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--check":
        return check()
    if argv[0] == "--index":
        write_index(entries())
        return 0
    if argv[0] == "--list":
        for slug, e in entries().items():
            print(f"{slug:<28} {e.get('status', ''):<8} {e.get('term')}")
        return 0
    if argv[0] == "--in":
        return in_text(argv[1])
    hits = find_entries(" ".join(argv))
    if not hits:
        print(f"no entry for {' '.join(argv)!r} — add one (knowledge/README.md)")
        return 1
    for i, slug in enumerate(hits):
        if i:
            print("\n" + "-" * 60 + "\n")
        show(slug)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
