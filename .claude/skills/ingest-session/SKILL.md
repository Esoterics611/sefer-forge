---
name: ingest-session
description: Ingest one images+voice session end to end (OCR, match the OCR to the voicenote, clean the transcript, plan and build section.md, check, pamphlet preview), resuming from wherever the session stands after a crash or restart. Use when the user says "ingest session <path>", "process this session", "continue session N", or "pick up where we left off" on a photo session. Argument - the session path, e.g. discourses/003-breishis/sessions/002.
---

Follow `prompts/02-ingest-session.md` exactly, with `<SESSION_PATH>` = `$ARGUMENTS`.

If `$ARGUMENTS` is empty, run `python scripts/session-status.py` and take the images+voice
session whose next step is not "done"; confirm it with the user before starting.

For a `type: voice-only` discourse, use the `ingest-voice-session` skill instead.

Always begin with `python scripts/session-status.py <SESSION_PATH>` and continue from the
first unfinished step. Start Whisper in the background (Bash `run_in_background`) if it
has not run, and do the OCR meanwhile; you are notified when it finishes.
