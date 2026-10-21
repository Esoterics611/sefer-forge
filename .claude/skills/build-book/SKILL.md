---
name: build-book
description: Render a book (or all books) to DOCX through the pandoc pipeline and audit the layout. Use when the user says "build book", "render", "make the docx". Argument - the book folder under books/, or nothing for all.
---

Follow `prompts/05-build-book.md` exactly, with `<BOOK>` = `$ARGUMENTS`.

Before building, run `python scripts/check-session.py <discourse>` on each discourse the
book lists (`books/<BOOK>/structure.yaml`) and report errors first: a session that fails
its checks prints wrong in the book.
