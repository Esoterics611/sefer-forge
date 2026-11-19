# Working notes: the English translation (not printed)

2026-11-19, at Ronnie's request: an English translation of the whole document (the outline and cliff notes, the
maamar with its explanation, the summary, the closing page), with the same branding.

- The maamar's stretches (bold) are translated from the text itself (sessions/001/ocr.md, as woven in
  ../biur/biur.src.md), faithfully, abbreviations opened as the sense requires ("as explained above", "and the wise
  will understand", "etc."); the explanation and the footnotes are translated from the Hebrew ביאור.
- Structure held by the build: `mirror: ../biur/biur.src.md`: 43 of 43 sections with the same number of stretches
  and footnotes as the Hebrew.
- The cliff notes come from handouts/padah-beshalom-notes-en.md (already reviewed against the Hebrew), without their
  Hebrew-wording footnotes, as in the Hebrew document.
- Terms kept in transliteration, in italics, where English has no exact word: Nefesh, Ruach, Neshamah, Chayah,
  Yechidah, kelipah, itkafya, ithapcha, Havayah, Elokim, Malchut, Keter, Atik, Gulgalta, mayin nukvin.
- Proof: `python scripts/proof-pdf.py output/biur/006-padah-beshalom-en.pdf --profile biur-woven-en`: 0 errors,
  0 warnings.
- Open: no independent reading of the translation against the Hebrew yet.
