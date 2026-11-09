#!/usr/bin/env python3
"""Start the session of a narration that explains one box of a reading pack
(prompts/references-pack.md): its ocr.md and a starter section-plan.yaml.

Usage:
    python scripts/box-session.py discourses/004-levushei-haneshama 3          # box 3 → the next session
    python scripts/box-session.py discourses/004-levushei-haneshama 5 6        # one narration, two boxes
    python scripts/box-session.py <discourse> 3 --session 004                  # a given session number
    python scripts/box-session.py <discourse> 3 --dry-run                      # print, write nothing

A discourse whose text was set out with its sources (references.yaml in one of
its sessions) is recorded one narration per box: the speaker reads the stretch
of the text that cites the box, then the box's passage, and explains them. The
narration's session has no photos; its ocr.md holds the words it reads, as
"## Source:" sections, exactly as the reading pack prints them:

  1. the stretch of the text the box stands under (from the citation before it
     to its own), from the session that holds references.yaml;
  2. the box's passage (each excerpt of it), from sources/, with "..." where it
     is cut out of a longer paragraph.

The starter plan names the two sources, so the printed page labels them
(`sources:`: the text's label from references.yaml `text_label`, default
"הנוסח"; the box's heading, set apart as quoted), and fills title and heading
("הערה N — עץ חיים, שער …, פרק …"). The rest of the plan (nusach.end, lines,
keys) is filled at ingest Step 4, once the narration is matched. Then the
session goes through the ingest (prompts/02-ingest-session.md) like any other.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml

import forgelib as F
import sourcelib as S

spec = importlib.util.spec_from_file_location("build_references", Path(__file__).parent / "build-references.py")
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


def pack_session(discourse: Path) -> Path:
    for s in sorted((discourse / "sessions").iterdir()):
        if (s / "references.yaml").exists():
            return s
    sys.exit(f"{discourse}: no session has references.yaml (prompts/references-pack.md)")


def page_of(pack: Path, stretch: str) -> str:
    """The "## Source:" page of the pack session's ocr.md that holds a stretch of its text."""
    body = (pack / "ocr.md").read_text(encoding="utf-8")
    probe = S.letters(" ".join(stretch.split()[:8]))[0]
    for m in re.finditer(r"^## Source:\s*(.+?)\s*$([\s\S]*?)(?=^## |\Z)", body, re.M):
        if probe and probe in S.letters(m.group(2))[0]:
            return re.sub(r"^https?://", "", m.group(1))
    return F.meta(F.discourse_of(pack)).get("source") or "the text"


def short(label: str) -> str:
    """'עץ חיים · שער כ"ו (הצלם) · פרק א'' → 'עץ חיים, שער כ"ו, פרק א''."""
    return ", ".join(re.sub(r"\s*\([^)]*\)", "", p).strip() for p in label.split(" · "))


def passage(ex: dict) -> str:
    parts = list(ex["parts"])
    if ex["lead"]:
        parts[0] = "..." + parts[0].lstrip()
    if ex["tail"]:
        parts[-1] = parts[-1].rstrip() + "..."
    return "\n\n".join(p.strip() for p in parts)


def main(argv: list[str]) -> int:
    session_arg = argv[argv.index("--session") + 1] if "--session" in argv else None
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--session")]
    if len(args) < 2 or not all(a.isdigit() for a in args[1:]):
        print(__doc__)
        return 2
    discourse, wanted = Path(args[0].rstrip("/")), [int(a) for a in args[1:]]
    pack = pack_session(discourse)
    plan = yaml.safe_load((pack / "references.yaml").read_text(encoding="utf-8"))
    text = F.ocr_text(pack)
    try:
        cites, _ = R.anchors(text, plan)
        R.boxes(cites)
    except R.PlanError as e:
        sys.exit(f"{pack}/references.yaml: {e}")
    by_n = {c["n"]: c for c in cites}
    if missing := [n for n in wanted if n not in by_n]:
        sys.exit(f"no box {missing[0]}: the reading pack has boxes 1–{len(cites)}")

    sessions = sorted(p.name for p in (discourse / "sessions").iterdir() if p.is_dir() and p.name.isdigit())
    name = session_arg.zfill(3) if session_arg else f"{int(sessions[-1]) + 1:03d}"
    target = discourse / "sessions" / name
    if (target / "ocr.md").exists() and "--dry-run" not in argv:
        sys.exit(f"{target}/ocr.md exists: this session is started already")

    # 1. the stretches of the text the boxes stand under, each once, in order
    sections, seen, wheres = [], set(), []
    for a, b, boxed in R.segments(text, cites):
        if not any(c["n"] in wanted for c in boxed) or (a, b) in seen:
            continue
        seen.add((a, b))
        before = [c["n"] for c in cites if c["cut"] == a]
        last = max(c["n"] for c in boxed)
        where = f"citation {max(before)} to citation {last}" if before else f"to citation {last}"
        wheres.append(f"from citation {max(before)} to citation {last}" if before else f"up to citation {last}")
        stretch = " ".join(text[a:b].split())
        sections.append(f"## Source: {page_of(pack, stretch)} (session {pack.name}, ocr.md), {where}\n\n{stretch}")
    # 2. the boxes' passages
    labels = []
    for n in wanted:
        c = by_n[n]
        exs = c.get("excerpts_built") or by_n[c["see"]]["excerpts_built"]
        for k, ex in enumerate(exs):
            lab = c["label_text"] if k == 0 else R.label(ex)
            labels.append(lab)
            file = S.catalog()[ex["work"]]["file"]
            sections.append(f"## Source: {lab} — {file} {ex['ref']}\n\n{passage(ex)}")

    boxes = " and ".join(str(n) for n in wanted)
    noun = "box" if len(wanted) == 1 else "boxes"
    what = f"הערה {boxes}" if len(wanted) == 1 else f"הערות {boxes}"
    ocr = (f"---\nsession: '{name}'\ndiscourse: {discourse.name}\n---\n\n"
           f"<!-- No photos: {what} of the reading pack (session {pack.name}'s references.yaml, {noun} {boxes}), "
           f"the words the narration reads from. Section 1 is session {pack.name}'s text {wheres[0]}"
           f"; section 2 is the box's passage from sources/, exactly as the reading pack prints it "
           f"(\"...\" where it is cut out of a longer paragraph). -->\n\n"
           + "\n\n".join(sections) + "\n")

    first = labels[0]
    head_n = " ו".join(R.heb(n) for n in wanted)
    plan_text = "\n".join([
        "# Decisions for section.md. Text comes from ocr.md and commentary.md;",
        f"# rebuild with: python scripts/build-section.py {target}",
        f"# Started by scripts/box-session.py: the narration of {noun} {boxes} of the reading pack.",
        "# Fill nusach.end (the last sentence read), lines and keys at ingest Step 4.",
        yaml.safe_dump({
            "title": f"{'הערה' if len(wanted) == 1 else 'הערות'} {boxes} — {short(first)}",
            "heading": f"{'הערה' if len(wanted) == 1 else 'הערות'} {head_n} — {short(first)}",
            "lines": [],
            "sources": [{"label": plan.get("text_label") or "הנוסח"}]
                       + [{"label": lab, "quoted": True} for lab in labels],
            "nusach": {},
            "keys": [],
        }, allow_unicode=True, sort_keys=False, width=1000).strip(), ""])

    if "--dry-run" in argv:
        print(f"=== {target}/ocr.md\n{ocr}\n=== {target}/section-plan.yaml\n{plan_text}")
        return 0
    target.mkdir(parents=True, exist_ok=True)
    for sub in ("images", "voicenotes"):
        (target / sub).mkdir(exist_ok=True)
    (target / "ocr.md").write_text(ocr, encoding="utf-8")
    if not (target / "section-plan.yaml").exists():
        (target / "section-plan.yaml").write_text(plan_text, encoding="utf-8")
    print(f"Started {target}: ocr.md ({len(sections)} source sections) and a starter section-plan.yaml.\n"
          f"Next: the recording into {target}/voicenotes/, then the ingest (skill ingest-session).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
