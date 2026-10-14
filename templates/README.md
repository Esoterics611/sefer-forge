# Word reference template

Pandoc uses `book-template.docx` as the **style source** for every book
(a single book can override it with `books/<book>/reference.docx`).

It is **generated**, not hand-made, and not committed — `scripts/build-docx.sh`
creates it on the first build and again whenever `scripts/create-template.py`
changes. To regenerate by hand:

```bash
python scripts/create-template.py
```

The script starts from pandoc's own default reference document (so every style
pandoc emits exists) and restyles it for a Hebrew sefer: David font, RTL,
justified body with first-line indent, italic indented blockquotes, chapter
headings that start a new page, footnotes, A4 with 2.5 cm margins. Change
typography there and re-run — don't edit the .docx by hand.

Paragraph *spacing* is applied after rendering by `scripts/polish-docx.py`;
per-book overrides go in a `polish:` block in `books/<book>/metadata.yaml`.

`defaults.yaml` holds pandoc metadata shared by every book (language,
direction, the Hebrew TOC title); each book's `metadata.yaml` is applied
after it.

`book-template.before-rebuild.docx` is an older hand-made template kept for
reference only; the build does not use it.
