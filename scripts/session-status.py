#!/usr/bin/env python3
"""Where every session stands, and its next step.

Usage:
    python scripts/session-status.py                      # one line per session
    python scripts/session-status.py discourses/003-breishis/sessions/002   # checklist
    python scripts/session-status.py discourses/003-breishis              # checklists

A session's steps, in order (voice-only sessions skip the photo steps):

    inputs        photos in images/, the recording in voicenotes/
    transcribe    <audio>.raw.txt  (running: progress and time left;
                  interrupted: rerun transcribe.py to resume)
    ocr           ocr.md, one "## Image:" per photo
    ocr-match     ocr-match.md, newer than ocr.md and the transcript
    cleanup       commentary.md (transcript.md for voice-only)
    review        review.md, newer than the cleaned text
    plan          section-plan.yaml (sessions whose section.md is hand-made skip it)
    section       section.md, rebuilt since the plan and its sources changed
    checks        scripts/check-session.py finds no errors

OCR and transcription are independent: the next step offered while Whisper
runs is the OCR. Nothing here changes a file.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path

import forgelib as F

CHECK = F.load_script("check-session")
SPEED = 2.4            # Whisper on this CPU: minutes of work per minute of audio (TRANSCRIPTION.md)


def mtime(p: Path) -> float:
    return p.stat().st_mtime if p.exists() else 0.0


def fmt_min(seconds: float) -> str:
    return f"{max(1, round(seconds / 60))} min"


def transcribe_step(s: Path) -> tuple[str, str, str]:
    """(mark, detail, next step or '') for the recordings."""
    audios = F.audio_files(s)
    states = [(a, F.transcription(a, s)) for a in audios]
    if all(st["state"] == "done" for _, st in states):
        return "✓", f"transcribed ({len(audios)} recording{'s' * (len(audios) > 1)})", ""
    for a, st in states:
        if st["state"] == "running":
            of, at, started = st.get("of"), st.get("at"), st.get("started")
            if at and of:
                left = (of - at) * SPEED
                return "…", f"transcribing {a.name}: {F.stamp(at)} of {F.stamp(of)}, ~{fmt_min(left)} left", \
                    "wait for Whisper"
            if of and started:
                left = started + of * SPEED - time.time()
                when = time.strftime("%H:%M", time.localtime(started + of * SPEED))
                if left > 0:
                    return "…", f"transcribing {a.name} (pid {st['pid']}), expected done ~{when}, " \
                                f"~{fmt_min(left)} left", "wait for Whisper"
                ran = (time.time() - started) / 60
                return "…", (f"transcribing {a.name} (pid {st['pid']}) for {ran:.0f} min, past the "
                             f"~{when} estimate; this run keeps no progress file"), "wait for Whisper"
            return "…", f"transcribing {a.name} (pid {st['pid']})", "wait for Whisper"
    for a, st in states:
        if st["state"] == "interrupted":
            return "✗", f"{a.name}: interrupted at {F.stamp(st.get('at', 0))}", \
                f"python scripts/transcribe.py {s}   (resumes at {F.stamp(st.get('at', 0))})"
    return "–", "not transcribed", f"python scripts/transcribe.py {s}   (run it in the background)"


def steps(s: Path) -> list[tuple[str, str, str]]:
    """[(mark, what, next step)] in order; the first non-empty next step is the session's."""
    out: list[tuple[str, str, str]] = []
    skip = {str(x).zfill(3) for x in F.meta(F.discourse_of(s)).get("skip_sessions") or []}
    if s.name in skip:
        return [("·", "left out of the discourse (meta.yaml skip_sessions)", "")]
    voice = F.voice_only(s)
    photos, audios = F.image_files(s), F.audio_files(s)

    if voice:
        out.append(("✓" if audios else "–", "recording" if audios else "no recording in voicenotes/",
                    "" if audios else f"put the shiur recording in {s}/voicenotes/"))
    else:
        missing = [x for x, ok in (("photos", photos), ("voicenote", audios)) if not ok]
        out.append(("–" if missing else "✓",
                    f"{len(photos)} photo(s), {len(audios)} voicenote(s)",
                    f"put the {' and '.join(missing)} in {s}/" if missing else ""))
    if not audios:
        return out
    t_mark, t_detail, t_next = transcribe_step(s)
    transcribed = t_mark == "✓"
    timed = max((mtime(F.sidecar(a, "timed.txt")) for a in audios), default=0)

    if voice:
        out.append((t_mark, t_detail, t_next))
        cleaned = s / "transcript.md"
    else:
        ocr = s / "ocr.md"
        heads = re.findall(r"^## Image:\s*(.+?)\s*$", ocr.read_text(encoding="utf-8"), re.M) if ocr.exists() else []
        todo = [p.name for p in photos if p.name not in heads]
        if not ocr.exists():
            out.append(("–", "no ocr.md", f"OCR the photos: /ocr-session {s}"))
        elif todo:
            out.append(("✗", f"ocr.md lacks {', '.join(todo)}", f"OCR the new photo(s): /ocr-session {s}"))
        else:
            out.append(("✓", f"ocr.md ({len(heads)} photo(s))", ""))
        out.append((t_mark, t_detail, t_next))
        if not transcribed or not ocr.exists():
            return out
        match = s / "ocr-match.md"
        if (s / "section.md").exists() and not (s / "section-plan.yaml").exists() and not match.exists():
            out.append(("·", "no ocr-match.md (section.md was made without it)", ""))
        elif not match.exists() or mtime(match) < max(mtime(ocr), timed):
            out.append(("–" if not match.exists() else "✗",
                        "no ocr-match.md" if not match.exists() else "ocr-match.md older than its inputs",
                        f"python scripts/ocr-match.py {s}"))
        else:
            out.append(("✓", "ocr-match.md", ""))
        cleaned = s / "commentary.md"

    if not transcribed:
        return out
    if not cleaned.exists():
        out.append(("–", f"no {cleaned.name}",
                    f"clean the transcript into {cleaned.name} (prompts/transcript-review-rules.md)"))
        return out
    out.append(("✓", cleaned.name, ""))
    review = s / "review.md"
    if mtime(review) < mtime(cleaned):
        out.append(("–" if not review.exists() else "✗",
                    "no review.md" if not review.exists() else "review.md older than " + cleaned.name,
                    f"python scripts/transcript-diff.py {s}"))
    else:
        out.append(("✓", "review.md", ""))

    if not voice:
        plan, section = s / "section-plan.yaml", s / "section.md"
        hand_made = section.exists() and not plan.exists()
        if hand_made:
            out.append(("✓", "section.md (hand-made, no plan)", ""))
        elif not plan.exists():
            out.append(("–", "no section-plan.yaml",
                        f"python scripts/build-section.py {s} --init, then fill in the plan"))
            return out
        else:
            out.append(("✓", "section-plan.yaml", ""))
            newest = max(mtime(plan), mtime(s / "ocr.md"), mtime(cleaned))
            if mtime(section) < newest:
                out.append(("–" if not section.exists() else "✗",
                            "no section.md" if not section.exists() else "section.md older than its plan or sources",
                            f"python scripts/build-section.py {s}"))
                return out
            out.append(("✓", "section.md", ""))

    report = CHECK.check(s)
    errors = [m for k, m in report.lines if k == "✗"]
    warns = [m for k, m in report.lines if k == "!"]
    if errors:
        out.append(("✗", f"checks: {len(errors)} error(s) — {errors[0][:110]}",
                    f"fix it, then: python scripts/check-session.py {s}"))
    else:
        out.append(("✓" if not warns else "!", "checks pass" + (f", {len(warns)} warning(s)" if warns else ""), ""))
    return out


def next_step(st: list[tuple[str, str, str]]) -> str:
    return next((n for _, _, n in st if n), "")


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    sessions = F.resolve_sessions(args)
    if not args:
        for s in sessions:
            st = steps(s)
            nxt = next_step(st)
            last = next((f"{m} {w}" for m, w, n in st if n), f"{st[-1][0]} {st[-1][1]}")
            print(f"{str(s):45} {last[:70]}" + (f"\n{'':45} → {nxt}" if nxt else ""))
        return 0
    for s in sessions:
        kind = "voice-only" if F.voice_only(s) else "images+voice"
        print(f"{s}  ({kind})")
        st = steps(s)
        for m, w, _ in st:
            print(f"  {m} {w}")
        nxt = next_step(st)
        print(f"  → next: {nxt}" if nxt else "  → done: preview (scripts/preview-session.sh), pamphlet "
                                           "(/publish-pamphlet), or assemble the discourse")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
