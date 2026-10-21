---
name: new-session
description: Start a new session in a discourse - make the folder, copy in the photos and voicenote the user names, start Whisper in the background, and begin the OCR while it runs. Use when the user says "new session", "here are the photos and the recording for ...", or drops new files for a discourse. Argument - the discourse slug or path, then any file paths.
---

1. **Folder.** `./scripts/new-session.sh <discourse>` creates the next `sessions/MMM/`
   (with `images/` for photo discourses). If the user's files are already in an existing
   empty session folder, use that one.
2. **Files.** Copy (never move) the photos the user names into `images/` and the
   recording into `voicenotes/`. Keep their names. Ask for any that are missing.
3. **Whisper.** Start `python scripts/transcribe.py <session>` with Bash
   `run_in_background`. Run one at a time (on the CPU Whisper needs most of the machine's memory): if
   `python scripts/session-status.py` shows another transcription running, don't start a
   second; queue this one with `python scripts/transcribe.py --pending` once that ends.
4. **OCR meanwhile** (photo discourses): follow the `ocr-session` skill up to its step 5.
5. When Whisper finishes, continue with the `ingest-session` skill (or
   `ingest-voice-session` for a voice-only discourse).

Report the session path, the files copied, and when Whisper should finish (`session-status.py`
shows the estimate: about 0.9× the recording's length on the GPU, 2.4× on the CPU).
