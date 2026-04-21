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
> 4. On success, confirm the output path: `output/book.docx`, plus the file size.
