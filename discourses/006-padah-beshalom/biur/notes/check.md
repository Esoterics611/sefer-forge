# Working notes: how the explanation was checked (not printed)

Written 2026-11-19 from the text (sessions/001/ocr.md) at Ronnie's request: break the maamar into sections, the
plain meaning running along each sentence in a different face, concepts explained in footnotes in plain, formal
Hebrew, print for black and white, Sefer Forge branding (in English, at his word).

## Mechanical
- Woven text: every bold word, in order, is the maamar's text (`woven: true`, build-biur.py): 9649 of 9649 words.
- Rules of prompts/biur-rules.md: the build's lint passes. The English brand (title band, running head, colophon) is
  by Ronnie's instruction for this document.
- Proof: `python scripts/proof-pdf.py output/biur/006-padah-beshalom.pdf --profile biur-woven`: 0 errors; the two
  warnings are the English brand (p.1) and colophon (last page).

## Read against the text (corrections made in the review)
- §6: a closing sentence said the text "hints" here that victory is not complete; the text does not say so there
  (ch. 2 says a full victory is "שפת אמת תכון לעד"; the limit comes in ch. 7). Removed.
- §30: "כלב" glossed as the root of the animal soul; made exact: the yechidah of the animal soul, nullified before
  the yechidah of the divine soul.
- §21: the midrash number for "מיכאל שר של אש וגבריאל שר של מים" was not certain; replaced by the verse it explains
  (איוב כה, ב).
- §11: "כלשון המדרש" on "תבא האם ותקנח צואת בנה" removed (source not confirmed).
- Footnote on צל"ם: checked in עץ חיים, שער מוחין דצלם פ"א (23.1.2) and שער המוחין (20.5.2), now quoted.
- §27: the sentence on נגע / ענג rewritten for clarity.

## Open (for Ronnie)
- Verse and Talmud references in the explanation were given where certain; they were not checked against a text in
  sources/ (no Tanakh or Talmud there). Worth a glance in print.
- Ch. 9 speaks of "חיה יחידה שבנה"ב", and §32 ("בא"ז זלע"ז חסר בחי' יחידה") says the other side lacks a yechidah.
  The explanation reports both as the maamar says them, without reconciling them.
- An independent check (a reader who did not write it) has not been made yet.

## 2026-11-19, second round (one document)
- The cliff notes (summary, outline, the four levels, chapter by chapter) now open the ביאור, under the מבוא; the
  outline gained a column pointing to the explanation's sections. Part heading "המאמר עם ביאור" declared in the front
  matter (`headings:`). A closing page: the brand, our other works, links to the site.
- Tables re-laid out (column widths on the `col` elements; the section ranges set left to right).
- Footnotes 10pt (from 9.6) for reading comfort.
- Language review, read as a student: §11 and §36 had the divine soul soiled in "its own garments"; the text says
  "בלבושים צואים דנה"ב": corrected. §24 used "נסיון" for everyday experience, a clash with the maamar's term: reworded.
  §12, §14, §18, §41: ambiguous reference or gender, corrected. §6, §7, §25 and the בני חיי ומזוני note polished.
