# Reading pack — a text with the sources it cites, before the lesson is recorded

A text studied in a session (a הגהה, a maamar) often cites other books: עץ חיים,
פרי עץ חיים, often by gate and chapter only, often with a few words and "כו'".
Before recording, the speaker needs the text with each cited passage set below
the citation: the passage, a few lines before and after, and the words the
citation points to highlighted. He reads the text and the sources from this
document as he explains them.

Skill: `references-pack`. Example: `discourses/004-levushei-haneshama/sessions/001`.

## 1. The text

The session's `ocr.md`. Photos are OCR'd as usual (`ocr-session`). A text taken
from a digital edition (pasted from chabadlibrary.org, say) goes in as given: one
`## Source: <url>` section per page, the words exactly as pasted, a comment saying
where it came from. No photos; `session-status.py` and `check-session.py` accept
such a session. After the recording the session continues with `ingest-session`
from Step 2 (matching the text to the reading).

## 2. Every citation

Read the whole text and list every citation: a work named (ע"ח, פע"ח, בגלגולים,
בזוהר...), a gate or chapter only (שער מ"ט, ש"מ, ספ"ג), and a source quoted or
paraphrased without a name ("וכן מ"ש דציצית ביצירה..."). A plan with only
`title:` and no `cites:` makes `build-references.py` list every citation its scan
finds; use that list to check yours, not to replace reading the text.

## 3. Place each one

For a work in `sources/` (`sources/sources.yaml`):

    python scripts/source-lookup.py 'ע"ח שמ"ט פ"ה'          # the chapter, paragraph by paragraph
    python scripts/source-lookup.py --find 'אלו הלבושים'      # where the words are

The words the citation quotes decide the place, not its numbers: the editions
our texts cite number some gates, chapters and derushim differently from the
file (the work's `numbering:` notes in `sources.yaml`; add every new difference
you find). When the quoted words are not in the cited chapter, search the whole
work, then the neighbouring work (ע"ח ↔ פע"ח). A citation that gives no words
is placed by its subject: read the chapter and find the passage that says what
the text says it says. Unnamed sources: search their key phrase.

A work not in `sources/` is listed under `others:` and not quoted. If it will be
needed again, add it to `sources/` first (`sources/README.md`).

## 4. The plan: `references.yaml` in the session

Its header lists the keys. For each citation:

- **The excerpt**: the passage the citation points to with a few sentences before
  and after it (two to four lines of the source each way), cut at sentence ends.
  A passage longer than half a page is split into two `excerpts:` around what
  the citation uses, the stretch between left out.
- **`mark`**: the words the citation quotes or paraphrases, and the words that
  carry the point the text takes from the passage. Phrases, not paragraphs.
- **`cut_after`**: the end of the clause the source supports. Without it the box
  goes after the sentence's full stop, and a long sentence pushes several boxes
  past the citations they belong to.
- **`note`**: only what the reader needs to find his way. That is a numbering difference
  ("בהגהה "פ"ו"; בקובץ זה פרק ז'"), an uncertain identification and its
  grounds, an error in the source file, or the box that already holds a passage. Never a
  summary or an explanation of the content: the explaining is the speaker's.
- **`see`**: a citation whose passage is already in an earlier box points there,
  with its own `mark`.

## 5. Build and proof

    python scripts/build-references.py <session> --png
    python scripts/proof-pdf.py output/references/<discourse>-<session>.pdf

The build stops on a citation the plan does not account for, on `from`/`to`/`mark`
words not in the source, and on a `see` whose box lacks the mark. The proof
must report no errors (the chabadlibrary address on page 1 is a known warning). Then look at every spread: each box
right after its citation, no box carried to a later sentence, no runaway
excerpt, notes one or two lines.

## 6. Check the result against the request

Before handing anything over:

1. **All there.** The build's count of citations equals your list from step 2;
   each is a box or in "others".
2. **Each box answers its citation.** Read the citation and the highlighted words
   together, box by box. If the highlight is not what the citation refers to,
   place it again.
3. **Nothing invented.** The text is `ocr.md` as given; the excerpts are the
   source file's words (the build takes them from there); the only added words
   are the title, the one-line legend, the box labels and the notes.
4. **No filler.** Read the PDF once as the speaker will. Cut any note that
   explains, summarises or repeats a label.
5. **The request.** Re-read what the user asked for, and check the document
   does that: the original text, every reference to the works asked about,
   context before and after, the related words highlighted.

Hand over the PDF (`output/` is not in git) with: the number of citations and of
passages quoted, the ones whose identification is uncertain (by box number), and
what is listed but not quoted, with the reason. Commit `ocr.md`, `references.yaml`,
`references.md` and any addition to `sources/`.

## After: one narration per box

The speaker may record the lesson one box at a time (a narration per הערה).
Each narration gets its own session, started by
`python scripts/box-session.py <discourse> <box> [<box> ...]`: its `ocr.md` is the
stretch of the text the box stands under plus the box's passage, exactly as the
pack prints them, and a starter `section-plan.yaml` names both sources
(`text_label` in `references.yaml` labels the text). The recording goes into its
`voicenotes/`, and the session is ingested like any other (`ingest-session`),
ending with the teaching pass. The discourse's opening parts (the text with the
box letters, `build-references.py --marked-text`, and an introduction) are set in
its `meta.yaml` `intro:`.
