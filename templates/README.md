# Word reference template

Pandoc uses `book-template.docx` as the **style source** when rendering the book. You create it once, in Word, then every `build-docx.sh` run inherits its styles.

## One-time setup

1. Open Word → blank document.
2. **File → Options → Language** → add **Hebrew** as an editing language.
3. Set the default paragraph direction to **right-to-left**.
4. Open the **Styles** pane (Home tab → Styles launcher arrow).
5. Modify these styles for Hebrew book typography:

| Style | Used for | Suggested settings |
|-------|----------|-------------------|
| Normal / Body | body text (commentary) | 12pt, 1.5 spacing, justified, Hebrew font (David, Frank Ruehl CLM, SBL Hebrew, or Taamey Frank CLM) |
| Quote | blockquotes (source text) | 11pt, left+right indent 0.5", same Hebrew font, optional left border |
| Heading 1 | chapter titles | 24pt bold, page break before, spacing above/below |
| Heading 2 | discourse / major section titles | 18pt bold |
| Heading 3 | sub-sections | 14pt bold |
| Emphasis | (pandoc renders `[x]{.underline}` as this) | underline on, color #000000 |

6. Delete any placeholder content — pandoc only reads the styles, not the body.
7. Save as **`templates/book-template.docx`** (inside this repo).

## Verifying the template

From the repo root:

```bash
printf '# Test\n\n> Source quote in Hebrew: שלום.\n\nCommentary paragraph.\n' > /tmp/test.md
pandoc /tmp/test.md -o /tmp/test.docx --reference-doc=templates/book-template.docx
start /tmp/test.docx   # or: open (mac) / xdg-open (linux)
```

Open the result and confirm:
- Body paragraphs use your chosen Hebrew font and size
- The blockquote has the indent/border you set
- Direction is RTL

## Notes

- Don't put content in the template itself. It's a style carrier.
- If you change the template later, every future build picks up the new styles automatically — no source-file changes needed.
- For `epub` later, pandoc uses a separate CSS file; we'll add that when we get there.
