#!/usr/bin/env python3
"""List every word the transcript cleanup changed, relative to Whisper.

Usage:
    python scripts/transcript-diff.py discourses/003-breishis/sessions/001

Compares voicenotes/*.fixed.txt (Whisper + glossary fixes) with the cleaned
text — transcript.md for voice-only sessions, else commentary.md — word by
word, ignoring punctuation, niqqud and markdown. For photo sessions it also
checks that the explanation in section.md is commentary.md with exactly the
readability edits listed in section-plan.yaml (prompts/readability-pass.md).

Writes <session>/review.md: a counts line, then every Added, Replaced and
Removed passage with a few words of context. Added entries (words with
nothing removed beside them) come first: prompts/transcript-review-rules.md
allows almost none.

Skipped as format, not speech: frontmatter, headings, footnotes, box labels,
<!-- --> flags, {attribute} blocks.
"""
from __future__ import annotations

import difflib
import re
import sys
from pathlib import Path

FILLERS = {"אה", "אהה", "אמ", "אממ", "הממ", "מממ", "אההה"}
CONTEXT = 5
PUNCT = "[]{}()*>_:;,.!?\"'“”„‘’`—–-…|"
NIQQUD = re.compile(r"[֑-ׇ]")
BIDI_MARKS = re.compile("[‎‏‪-‮⁦-⁩]")
BOX = re.compile(r'^::: \{custom-style="Commentary"\}\n(.*?)\n:::', re.M | re.S)


def words(text: str) -> list[str]:
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"^\[\^[^\]]+\]:.*$", " ", text, flags=re.M)
    text = re.sub(r"\[\^[^\]]+\]", " ", text)
    text = re.sub(r"^#+ .*$", " ", text, flags=re.M)
    text = re.sub(r"\{[^}]*\}", " ", text)
    text = BIDI_MARKS.sub("", NIQQUD.sub("", text))
    return [w for w in (t.strip(PUNCT) for t in text.split()) if w]


def diff(before: list[str], after: list[str]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {"added": [], "replaced": [], "removed": [], "fillers": []}
    sm = difflib.SequenceMatcher(None, before, after, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        old, new = " ".join(before[i1:i2]), " ".join(after[j1:j2])
        ctx_a = " ".join(after[max(0, j1 - CONTEXT):j1])
        ctx_b = " ".join(after[j2:j2 + CONTEXT])
        if op == "delete" and all(w in FILLERS for w in before[i1:i2]):
            out["fillers"].append(old)
        elif op == "insert":
            out["added"].append(f"…{ctx_a} **{new}** {ctx_b}…")
        elif op == "replace":
            out["replaced"].append(f"~~{old}~~ → **{new}** — …{ctx_a} ⟨ ⟩ {ctx_b}…")
        else:
            out["removed"].append(f"~~{old}~~ — …{ctx_a} ⟨ ⟩ {ctx_b}…")
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/transcript-diff.py <session-path>")
        return 1
    session = Path(sys.argv[1])
    fixed = sorted((session / "voicenotes").glob("*.fixed.txt"))
    raws = sorted((session / "voicenotes").glob("*.raw.txt"))
    cleaned = next((p for p in (session / "transcript.md", session / "commentary.md") if p.exists()), None)
    if not (fixed or raws) or cleaned is None:
        print(f"Need voicenotes/*.raw.txt and transcript.md or commentary.md in {session}")
        return 1

    if fixed:
        whisper = " ".join(p.read_text(encoding="utf-8") for p in fixed)
    else:
        # .fixed.txt is regenerated and gitignored: apply the glossary's auto fixes here.
        sys.path.insert(0, str(Path(__file__).parent))
        import forgelib
        fixes = forgelib.load_script("apply-fixes")
        auto, _ = fixes.load_fixes(session)
        whisper = " ".join(fixes.apply_auto(p.read_text(encoding="utf-8"), auto)[0] for p in raws)
        fixed = raws
    before = words(whisper)
    after = words(cleaned.read_text(encoding="utf-8"))
    d = diff(before, after)
    counts = (f"Whisper {len(before)} words · {cleaned.name} {len(after)} words · "
              f"fillers removed {len(d['fillers'])} · removed {len(d['removed'])} · "
              f"replaced {len(d['replaced'])} · **added {len(d['added'])}**")

    lines = [f"# Transcript review — {session}", "",
             f"Before: {', '.join(p.name for p in fixed)} · After: {cleaned.name}", "", counts, ""]
    for key, title in (("added", "Added (nothing removed beside it — check each)"),
                       ("replaced", "Replaced"), ("removed", "Removed")):
        lines += [f"## {title}", ""] + [f"{n}. {e}" for n, e in enumerate(d[key], 1)] + [""]

    section = session / "section.md"
    if cleaned.name == "commentary.md" and section.exists():
        boxes = BOX.findall(section.read_text(encoding="utf-8"))
        if boxes:
            body = "\n".join(ln for b in boxes for ln in b.splitlines() if "■" not in ln)
            # The plan's readability edits (prompts/readability-pass.md) are part of the section.
            sys.path.insert(0, str(Path(__file__).parent))
            import forgelib
            text = cleaned.read_text(encoding="utf-8")
            text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
            paras = [" ".join(x.split()) for x in re.split(r"\n\s*\n", text) if x.strip()]
            try:
                paras, _ = forgelib.apply_edits(paras, forgelib.plan_edits(session))
            except forgelib.EditError as e:
                print(f"section-plan.yaml edits: {e}")
            sd = diff(words("\n\n".join(paras)), words(body))
            changed = sum(len(sd[k]) for k in ("added", "replaced", "removed", "fillers"))
            lines += ["## section.md boxes vs commentary.md", ""]
            if changed:
                lines += [f"{changed} differences:", ""]
                for key in ("added", "replaced", "removed", "fillers"):
                    lines += [f"- {key}: {e}" for e in sd[key]]
            else:
                lines += ["identical"]
            lines += [""]
            counts += f" · section.md boxes: {'identical' if not changed else f'{changed} differences'}"

    out = session / "review.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(counts.replace("**", ""))
    print(f"-> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
