# Reviewing the explanation (ביאור): how a sitting is processed

The explanation in `../biur.md` (PDF: `output/biur/004-levushei-haneshama-biur.pdf`) is Claude's reading of
the הגהה. Ronnie studies it and says where he agrees, where it is wrong, where he reads otherwise. This folder
holds what he says; `../corrections.yaml` is the register of every remark and what was done with it.

**Places.** Every paragraph of the explanation is numbered in print and in `biur.md`: `[12.3]` = section 12,
paragraph 3; the lettered parts `[ב׳.2]`, the foreword `[פתח.1]`. A remark names its place ("שתים עשרה, שלוש").

## A sitting

1. `review/<NNN>/voicenotes/` — the recording (local only, never in git) — or a written note in chat.
2. `python scripts/transcribe.py discourses/004-levushei-haneshama/biur/review/<NNN>` → `.raw.txt`,
   `.timed.txt`, `.fixed.txt` beside the audio (committed; never edited).
3. `review/<NNN>/transcript.md` — the recording cleaned faithfully (`prompts/transcript-review-rules.md`):
   his words, nothing added. This is the record of what he said.
4. Each remark becomes an item in `../corrections.yaml` (format there), sorted by kind:
   - **error** — the explanation misreads the text or a source, or a source is wrong. Fixed in
     `../biur.src.md` and rebuilt; the item records what was changed.
   - **reading** — he reads it otherwise and the text bears both. Nothing is chosen for him: both
     readings are kept, with the evidence for each; the explanation gets a note where they part.
   - **own** — the explanation caught something he had wrong (e.g. "אבל ירידתן משם"). Recorded so that
     later sessions, and later recordings, do not repeat it.
   - **question** — answered from `sources/` where it can be, else listed as open.
   - **term** — how he explains a term: into the lexicon entry's `teacher:` with this sitting as `where`
     (`knowledge/lexicon/`, skill `chassidus-context`); an entry he confirms becomes `status: checked`.
5. Nothing in the explanation changes without an item in the register. A change of meaning that he did
   not ask for is proposed to him first.
6. Rebuild (`python scripts/build-biur.py discourses/004-levushei-haneshama/biur --pdf`), proof
   (`python scripts/proof-pdf.py output/biur/004-levushei-haneshama-biur.pdf --profile biur`), commit.

The independent check's findings, before his review, are in `../check.md`; the serious ones print as the
explanation's last part (ז) and mark the paragraphs they touch ("בדיקה N"), from `../checks.yaml`: when one
is settled in the register, set its `settled:` there and rebuild, and its mark leaves the print; the first Fable session's
comparison of his earlier teaching with its own first version is `../comparison.md`.
