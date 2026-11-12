#!/usr/bin/env python3
"""Where each discourse's English narration stands, and the next step.

Usage:
    python scripts/narration-status.py [discourses/<NNN>-<slug>]

For every discourse with an English rendering, or a voice-only one (its
shiurim are what the English episodes read), lists each part, in order:
the introduction when meta.yaml has `intro:` (it stands for the sessions in
`skip_sessions:`), then each other session with a transcript.md. For each:
  English   missing / current / STALE (its Hebrew changed after it was rendered)
  episode   the narration plan whose `parts:` reads it, and that plan's state:
            awaiting approval (`approved:` not set) / approved, to build /
            built / on YouTube (booklets/narration/youtube.yaml)
Then the next step. The workflow: prompts/render-english.md.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PLANS = ROOT / "booklets/narration"
RECORD = PLANS / "youtube.yaml"
OUT = ROOT / "output/narration"
EPISODE_WORDS = 7000            # about 40 minutes read: start a new episode beyond this


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return (yaml.safe_load(text.split("---")[1]) or {}) if text.startswith("---") else {}


def parts_of(discourse: Path) -> list[tuple[str, Path, Path]]:
    """(label, Hebrew source, English rendering) of each part, in reading order."""
    meta = yaml.safe_load((discourse / "meta.yaml").read_text(encoding="utf-8")) or {}
    out, skip = [], set(meta.get("skip_sessions") or [])
    if meta.get("intro"):
        src = discourse / meta["intro"]
        out.append(("introduction", src, src.with_name(src.stem + "-en.md")))
    for s in sorted(p for p in (discourse / "sessions").iterdir() if p.is_dir()):
        if s.name in skip or not (s / "transcript.md").exists():
            continue
        out.append((f"session {s.name}", s / "transcript.md", s / "transcript-en.md"))
    return out


def english_state(src: Path, en: Path) -> str:
    if not en.exists():
        return "missing"
    sha = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
    return "current" if frontmatter(en).get("source_sha256") == sha else "STALE"


def plans() -> dict[str, tuple[str, dict]]:
    """English rendering path (relative to the repo) -> (plan name, plan)."""
    out = {}
    for p in sorted(PLANS.glob("*.yaml")):
        plan = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        for part in plan.get("parts") or [] if isinstance(plan, dict) else []:
            out[part] = (p.stem, plan)
    return out


def plan_state(name: str, plan: dict, uploaded: dict) -> str:
    if name in uploaded:
        return f"on YouTube https://youtu.be/{uploaded[name]['id']}"
    if (OUT / name / "video.mp4").exists():
        return "built, to publish"
    if plan.get("approved"):
        return f"approved {plan['approved']}, to build"
    return "awaiting Ronnie's approval of the English"


def words(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").split("---", 2)[-1].split())


def main(argv: list[str]) -> None:
    discourses = [ROOT / a for a in argv] or sorted(p for p in (ROOT / "discourses").iterdir() if p.is_dir())
    uploaded = (yaml.safe_load(RECORD.read_text(encoding="utf-8")) or {}).get("uploaded", {}) if RECORD.exists() else {}
    by_part = plans()
    for d in discourses:
        if not (d / "meta.yaml").exists():
            continue
        meta = yaml.safe_load((d / "meta.yaml").read_text(encoding="utf-8")) or {}
        parts = parts_of(d)
        if meta.get("type") != "voice-only" and not any(en.exists() for _, _, en in parts):
            continue
        print(f"\n{d.relative_to(ROOT)}  ({meta.get('title', '')})")
        todo, pending, unplaced = [], 0, []
        for label, src, en in parts:
            state = english_state(src, en)
            rel = str(en.relative_to(ROOT))
            plan = by_part.get(rel)
            episode = f"{plan[0]}: {plan_state(plan[0], plan[1], uploaded)}" if plan else "no episode yet"
            print(f"  {label:14} English {state:8}  {episode}")
            if state != "current":
                todo.append(f"render {label} into English ({rel})" if state == "missing"
                            else f"bring {rel} up to date with its Hebrew")
            elif not plan:
                unplaced.append(rel)
                pending += words(en)
        if unplaced:
            todo.append(f"add {len(unplaced)} rendered part(s) (about {pending // 165} minutes) to the next episode"
                        + (" (a new plan: past one episode's length)" if pending > EPISODE_WORDS else ""))
        for name, plan in {v[0]: v[1] for k, v in by_part.items() if k.startswith(str(d.relative_to(ROOT)))}.items():
            state = plan_state(name, plan, uploaded)
            if state.startswith("awaiting"):
                todo.append(f"Ronnie reads and approves {name} (then `approved: <date>` in its plan)")
            elif state.startswith("approved"):
                todo.append(f"build {name}: python scripts/build-narration.py booklets/narration/{name}.yaml")
            elif state.startswith("built"):
                todo.append(f"publish {name}: python scripts/youtube-publish.py publish {name}")
        print("  next: " + ("; ".join(todo) if todo else "nothing: every part is on YouTube"))


if __name__ == "__main__":
    main(sys.argv[1:])
