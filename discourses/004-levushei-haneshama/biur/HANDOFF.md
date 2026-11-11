# Hand-off: the ביאור on "לשון אדמו"ר נ"ע בעצמו" (discourse 004)

Written 2026-11-11 by the session that started the work, for whoever continues it (a new Claude session or
the owner). Everything named here is committed on branch `claude/friendly-dirac-oufk91`.

## What was asked
An explanation in Hebrew of the whole הגהה (תורה אור, חיי שרה, טז ע"ג – יז ע"א), Claude's own, from the text and
its sources only; the text and every source passage carried complete; then a short separate list of where the
owner's teaching (introduction, הערות א'–ג', session 005) differs; a proofed PDF; working notes kept in files;
all Kabbalah sources checked, stored as markdown and understood; and a detailed plan for a growing source
library / lexicon / knowledge system for the repo. Rule kept so far: **the owner's transcripts and teaching
texts in sessions 001–005 have NOT been read** (only `sessions/001/ocr.md` and `references.yaml`). Do not read
them until the explanation is finished.

## Where things are (updated at the end of the first session)
| What | Where | State |
|---|---|---|
| The explanation, hand-written source | `biur/biur.src.md` | **Complete**: preface, context, overview, §1–§19, summary, open questions, sources. |
| The explanation, built | `biur/biur.md`; PDF `output/biur/004-levushei-haneshama-biur.pdf` (`python scripts/build-biur.py discourses/004-levushei-haneshama/biur --pdf`) | Builds; the whole הגהה covered; 79 source passages; proof (`--profile biur`) 0 errors |
| Comparison with the owner's teaching | `biur/comparison.md` | Written (seven items) after the explanation was finished |
| Independent check | an examiner agent that had not seen the reasoning | Run at the end of the session; its findings and what was done about them are in `biur/notes/examiner.md` if that file exists; if it does not, the check has still to be resolved |
| Working notes | `biur/notes/` (`segments.md`, `argument-map.md`, `citations.md`, `terms.md`, `open-questions.md`) | First-reading notes; where they differ from `biur.src.md`, the explanation is later and governs |
| Source library | `sources/` (JSON) and `sources/md/` (markdown, `scripts/source-export.py`) | עץ חיים, פרי עץ חיים, שער הגלגולים, שער הכוונות, שער המצוות, זוהר, מקדש מלך, תניא, תורה אור + הערות |
| The Tzemach Tzedek's maamar on the הגהה | `sources/md/torah-or/tzemach-tzedek-biur-al-hahagaha.md` | Transcribed from three photos; needs a human proofread |
| The plan for the repo | `docs/knowledge-plan.md` | Written |

## What the reading has established (short)
1. Two בירורים. Souls are clarified by rising from the kelipot to be מ"נ in נוקבא דז"א, before birth, by others'
   prayers and mitzvot. The soul's descent into a body is "דוגמת גלות השכינה": only to clarify its own garments,
   by Torah and practical mitzvot; that is why mitzvot are "חיוב יותר" than prayer (prayer דרבנן; garments
   cannot be repaired by others). The Tzemach Tzedek says exactly this ("כל נשמה הבאה לעוה"ז כבר ניתקנה קודם
   בואה... וירידתה לעוה"ז הוא כמו גלות השכינה לברר לבושים"), and sums up three kinds: (א) מ"ן עצמן דנוקבא =
   souls not included in Adam: by prayer only; (ב) souls included in Adam: by prayers and also by mitzvot (prayer
   in פנימיות); (ג) every person's garments: only by Torah and mitzvot.
2. Clarification is by מ"ד (the male); garments are clarified by מ"ד דז"א = the ה' חסדים (מ"ע).
3. The garments = צלם דאימא, inner and surrounding (חשמל), clarified from קליפת נוגה.
4. "והשתא א"ש": the garment comes from אימא (עוה"ב) but is not עוה"ב; it lets the soul bear the light.
5. "יפה שעה אחת": גן עדן is of בריאה; mitzvot work a זיווג in אצילות (מו"ס דא"א, י"ג חיוורתא); proofs from the
   weekday descent of זו"נ, ציצית/תפילין/נט"י, the names intended in blessings and in מקרא–משנה–תלמוד.
The Alter Rebbe's own parallels: תניא, קונטרס אחרון essays 2 and 4 (`sources/md/tanya/05-…`).

## Settled since `open-questions.md` was written (fold these in)
- "חיוב יותר" = Torah and mitzvot are more obligatory than prayer (צ"צ, explicitly).
- ליקוטי תורה (האריז"ל) פ' עקב is quoted in the צ"צ's maamar; the הגהה originally read "גם כשאוכל בלא ברכה
  **כאכילת העכו"ם**" (dropped in print by the censor — the edition's note).
- Numbering: the צ"צ says his עץ חיים ("דפוס דובראוונע") has שער כ"ה for כ"ו, של"ח for ל"ט, של"ט for ש"מ; פע"ח
  ש"א "פ"ו" is "פ"ז"; טעמי המצוות, סוף ההקדמה = "ד"ה סוד מציאות המצות כולם".
- "ובגלגולים פ"ב": the Kehot note (Chayei Sara.16.46) says לקו"ת במדבר ב, ב cites it as פרק עשרים.
- "שער מ"ד פ"ד ופ"ה" is almost certainly שער מ"ז (47.4.2, 47.5.1).
- Text: the site reads "מבפנים ומבחוץ"; `sessions/001/ocr.md` lost the ו (owner's file; not changed).
- The צ"צ's maamar as printed stops after "כמ"ש בטעמי מצות שם" (my §10): §11–§19 have no commentary from him.

## Not found (say so in the explanation)
ספר הגלגולים (פ"א, פ"ב/כ', פ"ז, פי"ד, after פל"ה) — only its parallel שער הגלגולים (12–13, 6–7, 39); טעמי המצוות
(parallel: שער המצוות הקדמה 2.7, 2.9; the צ"צ quotes its heading); זוהר הרקיע פ"ג ע"א; the folio of מקדש מלך
"ק"ב ע"ב" (the words are at Zohar I 36b); the Shklov/Dubrowna עץ חיים itself. hebrewbooks.org blocks automated
readers (do not work around it); a search helper was started for these and stopped unfinished.

## Next steps, in order
1. Resolve anything the examiner found that is still open (see `biur/notes/examiner.md`), rebuild, re-proof, resend the PDF.
2. The owner rules on each item of `biur/comparison.md`; nothing in the sessions was changed.
3. Bring the missing books as scans (ספר הגלגולים first) and fold them into §5, §8, §9, §13, §15; proofread the Tzemach Tzedek transcription against the book.
4. Start phase 1 of `docs/knowledge-plan.md` (registers, check scripts, lexicon seed, wanted list).
