---
name: voice-note-to-text
description: Turn a voice note Ronnie records for Claude (not a lesson to ingest - a note explaining why a text matters, what an introduction should say, how he wants a work done) into text, in passes - fetch it (Google Drive, large files by a share link), transcribe it with Whisper, write the faithful transcript, then textbook Hebrew, then clear to a newcomer, then polished with nothing generated-sounding - and use it where he says (an introduction, a note to follow). Set on 2026-11-24 with the הקדמה of פדה בשלום. Use when the user says "I uploaded a voice note", "this is a note to you", "turn the voice note into text", "make it the introduction", "send me the transcript".
---

# A voice note to Claude, into text

The model: `discourses/006-padah-beshalom/biur/review/intro-note/` (the voice note became the הקדמה).

## 1. Fetch

- Find it in Drive: `search_files` with `modifiedTime > '<today>' and mimeType contains 'audio/'`.
- Up to about 3.5 MB the Drive connector can download it. Larger files break the connector: ask Ronnie
  (one question) to let you share it "anyone with the link", share it (`share_file`, `anyoneWithLink`,
  reader), and fetch
  `https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t` with curl. Check the
  byte size and `ffprobe`. Remind him at the end to set it back to Restricted.
- Put it where audio stays out of git: `discourses/<NNN>-<slug>/biur/review/<name>/voicenotes/` (a
  session's own `voicenotes/` for session material). Confirm with `git check-ignore -v`.

## 2. Transcribe

`python scripts/transcribe.py discourses/<NNN>-<slug>/biur/review/<name>` in the background (the first run
downloads the model). Never transcribe by listening in chat. The `.raw.txt` and `.timed.txt` are
committed, the audio never.

## 3. The passes (each saved beside the audio, Ronnie may ask to see any)

1. `transcript.md`, **faithful**: his words; only Whisper's mishearings corrected (names, terms, quoted
   verses and sayings restored to their form). A doubtful spot is marked `<!-- UNCLEAR [mm:ss] ... -->`,
   never guessed. Send it to him when he asks.
2. `intro-2-textbook.md`: everything he said, in his order, as written Hebrew. Nothing added.
3. `intro-3-clear.md`: each term a newcomer would stop at said once in plain words where it first
   appears. Still nothing he did not say.
4. `intro-4-final.md`: read sentence by sentence; cut what sells, explains for its own sake or repeats;
   no "imagine", no slogans he did not say, nothing that sounds generated. This is what prints.

A saying he cites that is not in `sources/` prints as his teaching, without quotation marks, until he
gives its place; list such sayings for him.

## 4. Use it

Where he says: as the הקדמה before the מבוא (skill `biur-booklet`), a note to follow, a page of the site.
A slogan he asks for comes from his own words in the note. Commit the transcripts and passes; push.
