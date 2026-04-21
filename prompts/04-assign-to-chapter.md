# START PROMPT — ASSIGN DISCOURSE TO CHAPTER

Use this when a discourse is `status: ready` and you want to place it in the book's chapter order.

Replace `<DISCOURSE_SLUG>` (the `<slug>` portion, not the numeric prefix) and `<CHAPTER_NUM>` (1-based index, or `new` to create a new chapter).

---

> Assign discourse `<DISCOURSE_SLUG>` to chapter `<CHAPTER_NUM>`.
>
> 1. Read `book/structure.yaml`.
> 2. If `<CHAPTER_NUM>` is `new`, ask me for the Hebrew chapter title, then append a new chapter entry to `chapters:`.
> 3. Otherwise, append `<DISCOURSE_SLUG>` to the `discourses:` list of chapter `<CHAPTER_NUM>` (1-based). Verify the slug isn't already there; don't add duplicates.
> 4. Update the discourse's `meta.yaml` → set `chapter: <CHAPTER_NUM>` (or the new chapter's 1-based index).
> 5. Show me:
>    - The updated `book/structure.yaml` excerpt for that chapter.
>    - The updated `meta.yaml`.
> 6. Remind me to run `prompts/05-build-book.md` to produce the docx.
