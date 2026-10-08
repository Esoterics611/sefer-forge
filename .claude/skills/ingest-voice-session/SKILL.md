---
name: ingest-voice-session
description: Turn one recorded shiur (voice-only session, e.g. a שער היחוד lesson) into a clean Hebrew transcript.md and rebuild its book. Use when the user says "ingest voice session <path>", "new lesson", "process lesson N", or drops a voicenote into a voice-only discourse. Argument - the session path, e.g. discourses/002-shaar-hayichud/sessions/013.
---

Follow `prompts/02v-ingest-voice-session.md` exactly, with `<SESSION_PATH>` = `$ARGUMENTS`.

If `$ARGUMENTS` is empty, find the highest-numbered session under a `type: voice-only`
discourse that has a `voicenotes/*.raw.txt` but no `transcript.md`, and confirm it
with the user before starting.

If the session has audio but no `.raw.txt`, stop: the user must run
`python scripts/transcribe.py <session>` locally first (never transcribe audio via chat).
