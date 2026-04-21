# MEGAPROMPT — INITIAL SETUP (already run)

This prompt scaffolds the entire `sefer-forge` repo from an empty directory. It was already run to create this repo — keep here in case you want to recreate the structure in a parallel project.

---

## How to use (if you ever need to)

1. Create a new empty directory (e.g. `C:\code\another-book-project`).
2. Open Claude Code in that directory.
3. Paste the block below (starting with `>`).
4. Confirm Claude's plan. ~26 files and directories will be created.

---

> Scaffold a new Hebrew book publishing repo here. The unit of work is a **discourse** (built from N **sessions** of image+voicenote ingestion); discourses are later assigned to **chapters** in a final book. Do NOT invoke any docx/pptx/xlsx skill — plain file writes only. Do NOT transcribe audio via chat.
>
> **Directory tree:**
> ```
> <repo>/
> ├── discourses/               # each: NNN-<slug>/{meta.yaml, notes.md, discourse.md, sessions/MMM/{images,voicenotes,ocr.md,commentary.md,section.md}}
> ├── book/
> │   ├── structure.yaml        # chapter ordering, discourse assignments
> │   ├── front-matter/         # title page, intro
> │   ├── chapters/             # optional chapter intros
> │   └── back-matter/          # bibliography, index
> ├── compiled/                 # generated book.md (do not edit)
> ├── output/                   # rendered docx/epub/pdf (gitignored)
> ├── templates/                # book-template.docx (reference), metadata.yaml
> ├── scripts/
> └── prompts/
> ```
>
> **Scripts to write:**
> - `new-discourse.sh <slug>` — scaffold `discourses/NNN-<slug>/` with meta.yaml, notes.md, discourse.md skeleton
> - `new-session.sh <slug-or-path>` — add `sessions/MMM/{images,voicenotes}` to an existing discourse
> - `transcribe.py <session>` — Whisper Hebrew transcription, writes `.raw.txt` alongside each audio
> - `assemble-discourse.py <discourse> [--force]` — concat all `sessions/*/section.md` into `discourse.md`; refuse overwrite if discourse.md has content past frontmatter
> - `compile.py` — read `book/structure.yaml`, assemble `compiled/book.md`
> - `build-docx.sh` — pandoc render with `templates/book-template.docx` as reference
> - `build-all.sh` — compile + build
>
> **Prompts to write** (`prompts/`):
> - `00-megaprompt-setup.md` (this)
> - `01-new-discourse.md`
> - `02-ingest-session.md` (OCR images → ocr.md, clean .raw.txt → commentary.md, assemble section.md with blockquoted source + body commentary)
> - `03-assemble-discourse.md`
> - `04-assign-to-chapter.md`
> - `05-build-book.md`
>
> **Top-level docs:** `README.md` (quickstart), `CLAUDE.md` (conventions for future AI sessions), `SETUP_GUIDE.md` (prerequisites + workflow), `.gitattributes` (LFS for audio/images/docx), `.gitignore` (output/, __pycache__), `requirements.txt` (openai-whisper, pyyaml, python-docx).
>
> **Markdown conventions:** `[text]{.underline}` for underlines, `...` for snapshot markers at edges of partial OCR, blockquotes for source text, body paragraphs for commentary, YAML frontmatter on section.md and discourse.md.
>
> **After scaffolding:** `git init`, `git lfs install`, `chmod +x scripts/*.sh`, print the directory tree so I can verify.
