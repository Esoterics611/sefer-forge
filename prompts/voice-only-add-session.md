# Voice-only discourse — add a follow-up session

Use this when a voice-only discourse **already exists** (see `voice-only-discourse.md`) and the user drops a new voicenote into the next numbered session folder. It extends the existing `build-docs.py` with another shiur block instead of creating a new document.

Folder layout assumed:
```
discourses/<NNN>-<slug>/
  build-docs.py          # already exists, produced shiur 1 (and possibly more)
  output/                # already has *-he.docx / *-en.docx
  sessions/001/          # transcript.md + voicenotes/
  sessions/MMM/          # <-- new: voicenotes/*.m4a (+ optional *.raw.txt from transcribe.py)
```

---

## Prompt to paste

> Additional voice-only session at `discourses/NNN-slug/sessions/MMM/`. The raw Whisper transcript is already present as `voicenotes/*.m4a.raw.txt`. Do exactly the following — nothing more.
>
> **Do NOT** explore the repo, read CLAUDE.md / other prompts, invoke `docx` / `pptx` / `xlsx` skills, use `pandoc` or `scripts/build-docx.sh`, or spawn agents. Do NOT over-plan or mark chapters. Just ship the transcript and rebuild the docx.
>
> ### Step 1 — transcript (deep thinking pass)
> Read `discourses/NNN-slug/sessions/001/transcript.md` first — match its voice, paragraph structure (~8–12 substantive blocks), and YAML frontmatter keys exactly.
> Write `discourses/NNN-slug/sessions/MMM/transcript.md`:
> - YAML frontmatter: `title`, `subtitle` (bump the shiur ordinal — e.g. שיעור ב'), `discourse`, `session`, `date`, `source`, `language: he`, `note` (one-liner listing the Whisper artifact fixes you made — `raw→fixed, raw→fixed, ...`).
> - Body: the **full flowing Hebrew transcript**. Fix **only** clear Whisper artifacts — mis-heard Chabad/Kabbalah/Tanach terms, word-boundary errors, obvious punctuation. Common classes: garbled Aramaic (`אמין סדמים`→`עלמין סתימין`, `אמין דהית גליה`→`עלמין דאתגליין`), merged/split words, biblical phrases mangled (`יפוצו מעיונותיך`→`יפוצו מעיינותיך`), numeric abbreviations (`רמך`→`רמ"ח`), English code-switches that corrupted whole clauses.
> - Split the flow into clean paragraphs at real topic shifts. Do NOT add section headings, block quotes, or editorial commentary. Do NOT smooth the speaker's voice or re-order. Do NOT translate.
> - Mark genuinely unintelligible bits with `[brackets]` or `[?]`. Never guess a phrase out of nothing.
>
> ### Step 2 — extend `build-docs.py`
> Open `discourses/NNN-slug/build-docs.py`. It already defines `SECTIONS_HE` / `SECTIONS_EN` for shiur 1 (and perhaps `SECTIONS_HE_2`, etc.). You will:
> 1. Keep title/subtitle generic — strip any trailing `· שיעור א'` / `· Shiur 1` from the subtitle constants if still present.
> 2. Ensure shiur-label constants exist: `SHIUR1_HE = "שיעור א'"`, `SHIUR1_EN = "Shiur 1"`, and add the next one (e.g. `SHIUR_N_HE = "שיעור ב'"` / `SHIUR_N_EN = "Shiur 2"`).
> 3. Add `SECTIONS_HE_<N>` and `SECTIONS_EN_<N>` lists with 8–12 `(heading, [paragraphs])` tuples derived from your new `transcript.md`. Headings are for print navigation only — they must NOT change the body text. Preserve all Kabbalistic transliterations: Chochmah, Binah, Daas, Chabad, Zeir Anpin, Malchus, partzuf, mochin, hisbonenus, bittul, Nukva, Atzilus, Beriah, Yetzirah, Asiyah, Yisrael Saba, Tvunah, Akudim, Nekudim, Berudim, Adam Kadmon, barak ha'mavrik, ruach hakodesh, yichuda ila'a / tata'a, olmin setimin / d'isgalyan, ma'ayan, etc.
> 4. Refactor `build_hebrew` / `build_english` to iterate both (or all) shiurim through a single `emit_shiur(title, sections)` helper. The shiur-title line is larger and heavier than a section heading (Hebrew 22pt bold / English 20pt bold, centered, generous space_before).
> 5. Extend `SOURCES_HE` / `SOURCES_EN` with any **new** scriptural / rabbinic sources the new shiur cites (Tanach verses, Mishnah, Zohar, Tanya, etc.). Keep existing entries.
> 6. At the bottom of the script, output filenames must be stable across shiurim — drop any `-01` suffix: `output/<slug>-he.docx` and `output/<slug>-en.docx`. Delete the stale `-01-` files from `output/` if they still exist.
>
> ### Step 3 — build and verify
> - Run `python discourses/NNN-slug/build-docs.py`. Fix any errors in the script, never hand-edit the `.docx`.
> - Spot-check: open the Hebrew and English `.docx` with `python-docx` and print (a) all short paragraphs to confirm the shiur divider + every new heading appears in order, and (b) lengths of a few new body paragraphs to confirm they were actually emitted (not just headings).
>
> ### Step 4 — deep read-through
> Read the final Hebrew doc end to end (not scan — read). You are looking for: a Whisper-artifact you missed; a Kabbalistic term rendered inconsistently between shiurim (e.g. `מוחין` vs `מוכין`, `זעיר אנפין` vs `ז"א`); a misquoted posuk; a paragraph split in an awkward place; a mistranslation in the English. Fix in `transcript.md` + `build-docs.py` (never in the `.docx`) and rebuild.
>
> ### Hard constraints
> - Do NOT touch `sessions/001/`. It is frozen.
> - Do NOT rename prior shiur constants or outputs except the filename `-01` drop described above.
> - Never alter the source's meaning. No editorial additions.
> - This is deep Chabad Chassidus — give it maximum attention. Every technical term must be rendered correctly in the transcript, in Hebrew output, and in English output.
> - One deliverable message at the end: transcript path, output paths, 1-line list of fixes.

---

## Why this exists separately from `voice-only-discourse.md`

- `voice-only-discourse.md` creates a fresh discourse folder and a fresh `build-docs.py`. This prompt **extends** an existing one.
- It codifies the rename `-01-` → no-suffix (once a discourse has more than one shiur, the old `-01` filename is misleading).
- It adds a deep read-through step, which is the step most often skipped and most often regretted.
