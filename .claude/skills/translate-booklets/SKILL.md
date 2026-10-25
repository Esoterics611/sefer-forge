---
name: translate-booklets
description: Translate the Shivchei HaBesht stories (the themed Hebrew booklets) into English or French, check the translation against the Hebrew, and print the booklets in that language. Use when the user says "translate the booklets", "English booklets", "French booklets", "continue the French", or a Hebrew story changed and the translations must follow. Argument - the language (en or fr), optionally story or booklet numbers.
---

The translations are `shivchei-habesht-simple-en.md` and `-fr.md`: the text of
`shivchei-habesht-simple.md` (211 sections: the author's introduction and stories
1–210), carried over sentence by sentence. Rules, names and terms:
`prompts/translate-stories-rules.md`; read it whole before translating.

1. **Translate in batches.** Work through the stories in order, a batch of stories at a
   time, appending to the language's file. Read each Hebrew story whole first; where
   it is unclear, read the same place in `shivchei-habesht.md` and follow the reading
   the simple text chose. Never translate from `shivchei-habesht-english.md`. For
   French, translate from the Hebrew; the English is beside it only to keep names and
   terms the same. A name or term missing from the rules' tables is added there
   before it is used, so every story spells it the same way.
2. **Check after every batch.** `python scripts/check-translation.py <file>` holds the
   file to the Hebrew: headings and story numbers, paragraphs and `>` quotes in the same
   places, the summary paragraph, MATURE flags verbatim, no Hebrew letters, the closing
   line. A partial file reports how many sections it has; errors are fixed before the
   next batch. Then read the batch once against the Hebrew for meaning: nothing added,
   nothing dropped, who says and does what unchanged.
3. **Commit each batch** (`English translation: stories 179-192`), so a crash loses
   at most one batch.
4. **Glossary.** Every term the text keeps untranslated (rules' tables) has an entry
   in `booklets/glossary-<lang>.yaml` (`term`, `forms` for plurals and variants,
   `def`). An entry prints in a booklet only when one of its forms occurs there.
   `--lang fr` needs `glossary-fr.yaml` before it builds.
5. **Build.** `python scripts/build-booklets.py --lang en|fr [N ...]` →
   `output/booklets/<lang>/`. Booklet titles are the `en:` / `fr:` lines in
   `booklets/booklets.yaml`. Layout changes go in `templates/booklet-latin.css`
   (over `booklet.css`, which the Hebrew booklets share: a change there is checked
   on a Hebrew booklet too). Chrome: set `CHROME` if it is not on the path.
6. **Proof** every booklet by the `proof-pdf` skill (the proof picks the
   `booklet-latin` profile for `output/booklets/en|fr/`): 0 errors, then the
   spreads read, until clean. Hand over the folder (or a zip of it) with the page
   counts and proof lines.

A change to a Hebrew story is carried into both translations, then the booklet
holding it is rebuilt and proofed in all three languages.
