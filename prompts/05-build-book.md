# START PROMPT — BUILD BOOK

Use this whenever you want to render the current state of the book to DOCX.

---

> Build the book.
>
> 1. Run `./scripts/build-all.sh`.
> 2. Report any pandoc warnings verbatim (don't summarize).
> 3. If the build fails, diagnose before retrying. Common causes:
>    - `templates/book-template.docx` missing → tell me to follow `templates/README.md` (one-time Word setup).
>    - A discourse slug in `structure.yaml` doesn't match any folder in `discourses/` → tell me which slug is unresolved and list the available discourse folders.
>    - Malformed YAML frontmatter in some `section.md` or `discourse.md` → show me the offending file and the parse error.
>    - Missing pandoc on PATH → tell me to install.
> 4. The build script automatically runs `scripts/polish-docx.py` to fix paragraph spacing, line-height (1.35 body), and callout-box margins. If that step is skipped with a warning, tell me and suggest installing python-docx.
> 5. **Readability check.** Open `output/book.docx` mentally and audit the first three pages:
>    - Are paragraphs visibly separated (not clumped)?
>    - Do section headings have breathing room above and below?
>    - Are framed callout boxes spaced away from surrounding text?
>    - Is the title block centered with generous whitespace on page 1?
>    If anything still feels cramped, tune the spacing constants at the top of `scripts/polish-docx.py` (`BODY_SPACE_AFTER_PT`, `BODY_LINE_SPACING`, `H1_*`, `H2_*`, `QUOTE_*`, `TABLE_*`) and re-run. Don't touch `templates/book-template.docx` for spacing — do it in the polish script so it's reproducible.
> 6. On success, confirm the output path: `output/book.docx`, plus the file size, and give me a 1-line layout verdict ("spacing good" / "need to loosen X").
