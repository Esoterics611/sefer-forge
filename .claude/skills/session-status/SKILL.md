---
name: session-status
description: Show where every session (or one session or discourse) stands and its next step, including a transcription running or interrupted. Use when the user asks "where are we", "status", "what's next", "what's left", after a crash or restart, or before starting work on a session.
---

1. Run `python scripts/session-status.py $ARGUMENTS` (no argument: one line per session;
   a session or discourse path: its checklist).
2. Tell the user, briefly, which sessions are unfinished and each one's next step, in the
   script's words. A transcription in progress shows its time left; an interrupted one is
   resumed by rerunning `scripts/transcribe.py` on the session.
3. Offer to take the next step. On a yes, use the matching skill: `ocr-session`,
   `ingest-session` (photo sessions), `ingest-voice-session` (voice-only), or the command
   the status line names.

The script changes nothing; it is safe to run at any time.
