---
name: new-session
description: Start a new session in a discourse - make the folder, copy in the photos and voicenote the user names, start Whisper in the background, and begin the OCR while it runs. Use when the user says "new session", "here are the photos and the recording for ...", or drops new files for a discourse. Argument - the discourse slug or path, then any file paths.
---

1. **Folder.** `./scripts/new-session.sh <discourse>` creates the next `sessions/MMM/`
   (with `images/` for photo discourses). If the user's files are already in an existing
   empty session folder, use that one. A narration of a box of the discourse's reading
   pack (one per הערה, `prompts/references-pack.md`, "After") starts instead with
   `python scripts/box-session.py <discourse> <box>`: the session with its `ocr.md` and a
   starter plan; its OCR step is done. Which box: the recording's name (e.g. "עץ חיים 3")
   or the discourse's `notes.md`; ask when unclear.
2. **Files.** Copy (never move) the photos the user names into `images/` and the
   recording into `voicenotes/`. Keep their names. Ask for any that are missing.
   A recording the user uploaded to Google Drive: find it with the Drive connector's
   search. Up to about 3 MB, download it with the connector, through a subagent, since the
   base64 result is large: the subagent saves the result as JSON and writes the file with
   `python scripts/drive-decode.py <result.json> <session>/voicenotes/<name>`. A larger file breaks the connector's connection. With the user's
   agreement, share it "anyone with the link" and fetch
   `https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t`
   with curl (that host is on the sefer-forge environment's allowlist). The connector cannot
   take a link back: tell the user to set the file to Restricted, or empty it from the trash.
   Check the byte size and `ffprobe` before using it, and trash the Drive copy only after the
   transcripts are committed and pushed, when the user asked for that.
3. **Whisper.** Start `python scripts/transcribe.py <session>` with Bash
   `run_in_background`. Run one at a time (on the CPU Whisper needs most of the machine's memory): if
   `python scripts/session-status.py` shows another transcription running, don't start a
   second; queue this one with `python scripts/transcribe.py --pending` once that ends.
4. **OCR meanwhile** (photo discourses): follow the `ocr-session` skill up to its step 5.
   A text pasted from a digital edition instead of photographed goes into `ocr.md` as given,
   one `## Source: <url>` section per page (no OCR); its sources are set out before the
   recording with the `references-pack` skill.
5. When Whisper finishes, continue with the `ingest-session` skill (or
   `ingest-voice-session` for a voice-only discourse).

Report the session path, the files copied, and when Whisper should finish (`session-status.py`
shows the estimate: about 0.9× the recording's length on the GPU, 2.4× on the CPU).
