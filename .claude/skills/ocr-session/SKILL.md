---
name: ocr-session
description: OCR a session's page photos into ocr.md, strip by strip at full resolution, with a line-count check and a second pass, then match it against the voicenote. Use when the user says "OCR", "OCR this session", "read the photo", "redo the OCR", or adds or replaces a photo in a session's images/. Argument - the session path, e.g. discourses/003-breishis/sessions/002.
---

OCR every photo in `$ARGUMENTS/images/` into `$ARGUMENTS/ocr.md`. Dropped and misread
words come from reading a whole page at once, scaled down; this procedure never does.

1. **Cut strips.** `python scripts/ocr-strips.py $ARGUMENTS`. It prints each strip with the
   printed lines it holds ("lines 6–11 of 45"). Look at the first strip: if the photo holds
   two full columns, rerun with `--columns 2` (right column first).

2. **Read strip by strip into a line draft.** Read every strip image, in order. Write
   `output/strips/<discourse>-<session>/lines.txt`: one printed line per line, exactly as
   printed, a blank line where the print starts a new paragraph (indent, or a large
   opening word), and `## <photo name>` before each photo's lines. Each strip after the
   first repeats the last line of the one before: use it to join, never write it twice.
   - Exactly as printed: spelling (no plene normalization), abbreviations with their
     marks (ע"י, בחי'), parentheses, punctuation.
   - A line cut by the photo's edge: write what shows, and `...` where it is cut off.
   - Text you cannot read: `<!-- UNCLEAR: <what you see> -->` in place. Never guess.
   - Ignore letters of the facing column at the edges.
   - Words the author underlined by hand: `[text]{.underline}`.
   - The print's footnotes: after the text, under a `[Footnotes:]` line.

3. **Count.** The draft must have exactly the number of lines `ocr-strips.py` reported for
   each photo. A difference is a skipped or doubled line: find it before going on.

4. **Write `ocr.md`.** Frontmatter (`session`, `discourse`), then per photo
   `## Image: <file name>`, a one-line `<!-- -->` note on what the photo shows (cut edges,
   columns, footnotes), then the text: each paragraph's lines joined with spaces, a blank
   line between paragraphs. When a photo replaces an earlier one, its section replaces the
   old one; a deleted photo's section goes.

5. **Second pass.** Read every strip again against `lines.txt`, line by line, word by
   word: dropped words, letters confused (ה/ח, ב/כ, ו/ז/י, ר/ד, ם/ס), abbreviation marks.
   Fix both files.

6. **Match against the voicenote** when it is transcribed:
   `python scripts/ocr-match.py $ARGUMENTS`, then work through `ocr-match.md` as in
   Step 2 of `prompts/02-ingest-session.md`: every entry checked against the strip that
   holds it. If Whisper is still running, say so and stop here.

7. **Check.** `python scripts/check-session.py $ARGUMENTS` reports one `## Image:` per photo.

Report: lines per photo, UNCLEAR flags with what each shows, and the second pass's fixes.
Never edit the photos. Once the session's `section.md` is built, `ocr.md` is final.
