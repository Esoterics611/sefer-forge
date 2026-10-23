---
name: ingest-voice-session
description: Turn one recorded shiur (voice-only session, e.g. a שער היחוד lesson) into a clean Hebrew transcript.md and rebuild its book. Use when the user says "ingest voice session <path>", "new lesson", "process lesson N", or drops a voicenote into a voice-only discourse. Argument - the session path, e.g. discourses/002-shaar-hayichud/sessions/013.
---

Follow `prompts/02v-ingest-voice-session.md` exactly, with `<SESSION_PATH>` = `$ARGUMENTS`.

If `$ARGUMENTS` is empty, run `python scripts/session-status.py` and take the voice-only
session whose next step is not "done"; confirm it with the user before starting.

Begin with `python scripts/session-status.py <SESSION_PATH>` and continue from the first
unfinished step. If the recording is not transcribed, start
`python scripts/transcribe.py <SESSION_PATH>` with Bash `run_in_background` (never
transcribe audio in the chat; an interrupted run resumes where it stopped) and continue
when it finishes. Before the build, `python scripts/check-session.py <SESSION_PATH>` must
report no errors.

The lesson finishes, after its pamphlet is proofed, with the readability pass and then the
style pass (`prompts/style-pass.md`): both as lists in `transcript.md`'s frontmatter.
