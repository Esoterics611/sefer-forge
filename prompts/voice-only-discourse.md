# Voice-only discourse — transcript + Hebrew & English typeset Word docs

Use this when a discourse has **only a voicenote** (no images, no OCR). It bypasses the regular `section.md` / `commentary.md` / `discourse.md` pipeline entirely.

Folder layout assumed:
```
discourses/<NNN>-<slug>/sessions/<MMM>/voicenotes/*.m4a
```

---

## Prompt to paste

> New voice-only discourse at `discourses/NNN-slug/sessions/MMM/`. Do exactly the following — nothing more.
>
> **Do NOT** explore the repo, read CLAUDE.md / other prompts, invoke `docx` / `pptx` / `xlsx` skills, use `pandoc` or `scripts/build-docx.sh`, or spawn agents. The voicenote is the only input that matters.
>
> ### Step 1 — transcript (any model)
> Run `python scripts/transcribe.py discourses/NNN-slug/sessions/MMM`. Then write `discourses/NNN-slug/sessions/MMM/transcript.md`:
> - YAML frontmatter: `title`, `subtitle`, `discourse`, `session`, `date`, `source`, `language: he`, `note` (a one-liner listing the Whisper artifact fixes you made — e.g. `זרן פין→זעיר אנפין, מוכין→מוחין, לכבד→דחב"ד, ביורים→ביאורים`).
> - Body: the **full flowing Hebrew transcript**. Fix **only** clear Whisper artifacts — mis-heard technical Chabad/Kabbalah terms, word-boundary errors, obvious punctuation. **Do NOT** add section headings, block quotes, commentary, or any reorganization. **Do NOT** smooth the speaker's voice. **Do NOT** translate.
> - Mark genuinely unintelligible bits with `[brackets]` or `[?]`. Never guess.
>
> **Then stop and wait — I will switch the model to Opus before Step 2.**
>
> ### Step 2 — Hebrew + English Word documents (Opus)
> Write one Python script at `discourses/NNN-slug/build-docs.py` using `python-docx`. Run it. Outputs go to `discourses/NNN-slug/output/`.
>
> **Hebrew doc — `<slug>-<label>-he.docx`:**
> - Font **David** throughout. Body 13pt, line-spacing 1.6–1.7, justified, first-line indent ~0.8 cm.
> - Title ~30pt bold centered; italic subtitle beneath.
> - RTL applied at both section and paragraph level (`w:bidi`), and complex-script font set on every run (`w:rFonts w:cs` + `w:szCs`) or Word will render Hebrew in a fallback font.
> - **Section headings added purely for print navigation** (16pt bold centered). The body text under each heading must be identical to `transcript.md` — structure is additive only, not a rewrite.
> - `מראי מקומות` section at the end listing the quoted sources that actually appear in the discourse (e.g. משנה אבות, זוהר, פסוקים, ראשי תיבות).
>
> **English doc — `<slug>-<label>-en.docx`:**
> - Font **Garamond**. Body 12pt, line-spacing 1.5, justified.
> - Same section structure as the Hebrew, translated.
> - **Preserve Kabbalistic terminology in transliteration**: Chochmah, Binah, Daas, Chabad, Zeir Anpin, Malchus, partzuf, mochin, hisbonenus, bittul, Nukva, Atzilus, Yisrael Saba, Tvunah, Akudim, Nekudim, Berudim, Adam Kadmon, barak ha'mavrik, ruach hakodesh, etc. Do **not** invent explanations. Do **not** smooth in ways that change meaning. Bracket `[ ]` anything the speaker implies but does not explicitly say.
> - `Sources & Notes` section at end: the same references plus short glosses on the key transliterated terms.
>
> ### Hard constraints
> - Run the build script once; if Word rendering is off, fix the script — never hand-edit the `.docx`.
> - Never alter the source's meaning. No editorial additions.
> - This is deep Chabad Chassidus — give it maximum attention. Every technical term must be rendered correctly in both the transcript and both Word docs.

---

## Why this exists separately from the main workflow

- The main workflow (`prompts/02-ingest-session.md` etc.) assumes images + audio and builds `section.md` / `commentary.md` / `discourse.md` for later chapter assembly.
- Voice-only discourses skip OCR, the three-section `section.md` layout, and the pandoc pipeline. The deliverables are directly publishable Word docs — no book compilation.
- Keeping this prompt unnumbered (not `06-…`) makes clear it is an **alternate** flow, not a step that follows `05-build-book.md`.
