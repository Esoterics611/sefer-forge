# The source library, the lexicon and the knowledge of the repo: a plan

Written 2026-11-11, out of the work on discourse 004 (the הגהה "לשון אדמו"ר נ"ע בעצמו"). It says what that
work showed, what should be built so that every later text starts from more than the last one did, and in
what order. It continues `docs/agentic-development.md` and `docs/VISION.md`.

## 1. What the work on discourse 004 showed

1. **A lesson was recorded on a sentence that had been misread** ("אבל ירידתן משם"), because nobody had read
   the whole text with all its sources before the recording. The reading pack set sources beside citations,
   but did not say what the text *does* with them.
2. **Citations placed by a model could not be trusted, and nothing in the repo could tell.** Of 26 placements
   one was wrong (שער מ"ד for מ"ז), several rested on an unverified chapter number, and two citations are
   still unresolved. The check was done by hand, once, in a chat.
3. **What a session learns evaporates.** That the Alter Rebbe's "פע"ח ש"א פ"ו" is chapter 7 of our copy, that
   "כוונות עיוה"כ" is in פרי עץ חיים and not in שער הכוונות, that ספר הגלגולים is not שער הגלגולים: each of
   these cost an hour and belongs to every future text, not to one conversation.
4. **The commentary that settles the reading was in a printed book only** (the Tzemach Tzedek's maamar), and
   the main library of scans refuses automated readers.
5. **The AI's reading and the owner's teaching must be kept apart and then compared**, deliberately. Mixing
   them early would have hidden exactly the differences that mattered.

## 2. The design: four layers, each with its own rule

Everything the repo knows falls into one of four layers. They differ in who may write them and in how far
they are trusted. A statement in a higher layer always points at the lines of a lower layer it rests on.

| Layer | What it holds | Where | Who writes | Rule |
|---|---|---|---|---|
| 1. **Texts** | What the books say | `sources/` (JSON as fetched; `sources/md/` generated; transcriptions of scans) | Librarian agent; scripts | Never edited. Every paragraph has a stable address. Every file says where it came from and under what licence. |
| 2. **Bridges** | How one text points at another: each citation resolved to an address; how editions number; which works are parallel | `knowledge/citations/`, `sources/sources.yaml` (`numbering:`, new `parallels:`) | Citation agent; checked by script | A citation is "verified" only with the words found at the address. Otherwise "by sense" or "unresolved", said openly. |
| 3. **Understanding** | What the texts mean: terms, topics, full explanations | `knowledge/lexicon/`, `knowledge/topics/`, `<discourse>/biur/` | Reader agent (the strongest model); examined by an agent that has not seen the reasoning | Every claim cites a line. Three degrees of certainty. Never printed as the owner's words. |
| 4. **The owner's Torah** | What he taught: recordings, transcripts, teaching texts; and his rulings | `discourses/*/sessions/`, new `knowledge/taught/`, `knowledge/rulings.md` | The owner; agents only clean and lay out, as today | Its content changes only at his word. Agents index it; they do not correct it. |

The integration of the AI with the owner's knowledge happens **between layers 3 and 4**, in two directions:

- *Before he records*: layer 3 is prepared for the text he is about to teach, and he studies it.
- *After he records*: his teaching is compared with layer 3, the differences are listed with their evidence,
  and **he rules** on each: corrected, or "this is my חידוש, keep it", or "the sources are read wrongly, fix
  the explanation". The ruling is recorded and binds later sessions.

So the AI neither overrides him nor merely transcribes him. It holds the sources, and he holds the Torah.

## 3. What exists after this session (the prototypes)

| Piece | Prototype | Becomes |
|---|---|---|
| Text layer | `sources/` with ten works; `scripts/source-export.py` (markdown per gate, address on every paragraph); `scripts/source-lookup.py --page` (printed pages of the Zohar) | The library; grows by the wanted list (§6) |
| Transcription of a scan | `sources/md/torah-or/tzemach-tzedek-biur-al-hahagaha.md` (front matter: from what, by whom, not yet proofread) | The format for every scan-only work |
| Numbering notes | `sources/sources.yaml`, `numbering:` | An editions concordance |
| Citation register | `discourses/004…/biur/notes/citations.md` (a table) | `knowledge/citations/004.yaml`, machine-checked |
| Lexicon | `…/biur/notes/terms.md` (25 terms, each with its lines) | `knowledge/lexicon/` |
| Explanation with exact quotations | `scripts/build-biur.py` (`@text`, `@source`, `@file`; fails if the text is not wholly covered) | The standard way to write any explanation |
| Open questions | `…/biur/notes/open-questions.md` | `knowledge/open-questions.yaml`, one register for the repo |
| Comparison | `…/biur/comparison.md` | The differences register, with a column for the owner's ruling |
| Hand-off between sessions | `…/biur/HANDOFF.md` | A fixed file every long task keeps |

## 4. What to build

### 4.1 Registers (plain files, checked by script)

- **`knowledge/citations/<discourse>.yaml`**: one entry per citation in a text we study: the words as written,
  the work and address, the evidence words found there, `status: verified | by-sense | unresolved`, a note
  (edition differences), who checked and when. `scripts/check-citations.py` re-finds every evidence phrase at
  its address; it runs in the session hook. The reading pack (`references.yaml`) is then *generated from* this
  register, so a pack can no longer carry an unverified placement silently.
- **`sources/sources.yaml`**: add `parallels:` (ספר הגלגולים פ"א ≈ שער הגלגולים 13.1; טעמי המצוות הקדמה ≈
  שער המצוות Introduction.2) and `editions:` (Dubrowna/Shklov שער כ"ה = שער כ"ו; ל"ח = ל"ט; ל"ט = מ').
- **`sources/wanted.yaml`**: works cited and not held, with who cites them, where a scan exists, and how to get
  it (§6).
- **`knowledge/open-questions.yaml`**: every unresolved point, where it arose, what would settle it. Agents try
  the list again whenever a new work enters the library.

### 4.2 The lexicon

`knowledge/lexicon/<term>.md`, one file per term (צלם, חשמל, מ"ן, בירור, הבל דגרמי…). Front matter: the term,
its abbreviations and aliases, related terms. Body: **senses**, each with the lines that show it (address and
words), the texts in which it has that sense, and, separately, **how the owner uses and explains it** (links
into `knowledge/taught/`, including his own bridges such as the psychological reading of the צלם, marked as
his). `scripts/check-lexicon.py`: every sense has at least one address that resolves and contains the quoted
words. `glossary/abbreviations.yaml` stays the one list of abbreviations; the lexicon links to it.

Use: the reader agent loads the entries for the terms in a new text; the teaching pass and the pamphlets can
print a glossary from it; the comparison uses it to notice when a term is taught in a sense the sources do
not carry.

### 4.3 The index of what was taught

`knowledge/taught/<discourse>.yaml`, built by an agent from the transcripts and teaching texts (never the
other way round): for each term, citation and passage, what the owner said and where (session, timestamp).
It gives later sessions his language and his line of thought, and it is the second input of the comparison.

### 4.4 The study pack: how an agent is given the repo's knowledge

`scripts/study-pack.py <text>` assembles, for one text: the text; every citation with its resolved passage and
the whole chapter's path; the lexicon entries for its terms; earlier explanations that touch the same
passages; the open questions on them; and (only for the comparison step) the taught index. This is what a
reader agent is handed. It is deterministic and inspectable. A vector index is **not** needed at this size and
would hide where an answer came from; revisit when the library passes a few hundred works.

### 4.5 The workflow: study before recording, check before printing

A new first stage for every text, as a skill (`study-text`, `prompts/00-study-text.md`):

1. **Librarian**: fetch what the text cites; record the wanted.
2. **Citation agent**: resolve every citation into the register; words decide.
3. **Reader** (strongest model): read each cited chapter whole; write the explanation (`biur.src.md`) with
   terms, the argument first briefly and then along the text, places a reader goes wrong, degrees of certainty.
4. **Examiner** (strongest model, has not seen the reasoning): try to break it; findings resolved or reported.
5. **Print and proof**; the owner studies it. *Then* he records.
6. After the ingest and the teaching pass: **comparison** against the explanation; the owner rules; the rulings
   enter `knowledge/rulings.md`; lexicon and taught index are updated.

Stage 6 becomes a gate like the proof: no teaching text prints without a comparison report.

### 4.6 Roles and models

| Role | Reads | Writes | Model |
|---|---|---|---|
| Librarian / scan reader | the web, scans | `sources/`, `wanted.yaml` | mid; scans double-read, flagged "not proofread" until a person checks |
| Citation agent | text, `sources/` | citation register | mid, with script check |
| Reader | study pack (no layer 4) | `biur/`, lexicon drafts | strongest |
| Examiner | the explanation and `sources/` only | findings | strongest |
| Comparer | explanation + taught index | differences register | strongest |
| Indexer | transcripts | `knowledge/taught/` | mid |
| Builder / proofer | built files | `output/` | small |

## 5. Guards

- **No invented source**: quotations enter documents only by address (`build-biur.py`); a citation is verified
  only by words found; the examiner checks labels against addresses.
- **No drift**: `source-export.py --check`, `check-citations.py`, `check-lexicon.py` in the hook; a checksum of
  each source file in the catalog.
- **No blending**: the reader never sees layer 4; layer 3 never prints as the owner's; differences are ruled by
  him.
- **Honest gaps**: `unresolved`, `by-sense`, `not proofread`, `licence unknown` are states, not embarrassments.
- **Licences**: every work has a licence line. Open now: the vocalized Zohar (unknown), the Kehot texts as on
  Sefaria (not stated). The owner decides whether they stay in a repository that may become public.
- **Size**: the library is now about 60 MB (JSON and markdown). Add whole works when a text cites them; keep
  scans out of git.

## 6. Getting the books that are scans only

Wanted now: ספר הגלגולים (Frankfurt 1684 / Przemysl 1875), טעמי המצוות and ליקוטי תורה of the Arizal (Zolkiew
1775), זוהר הרקיע, the Shklov or Dubrowna עץ חיים, the Amsterdam מקדש מלך, אור התורה (בראשית), and the pages of
תורה אור with the Tzemach Tzedek's maamar (held as a transcription from three phone photographs; a clean scan
would let it be proofread). hebrewbooks.org refuses automated readers and that is not to be worked around. The
route that works: the owner downloads the PDF (or photographs the pages) and puts it in Google Drive; the
`new-session` route (`scripts/drive-decode.py`) brings it in; the scan reader transcribes the chapters needed,
strip by strip, into `sources/md/<work>/` with the transcription front matter. Sefaria still holds, unfetched:
שער ההקדמות, שער מאמרי רשב"י, שער הפסוקים, שער רוח הקודש, תיקוני זוהר, זוהר חדש, ליקוטי תורה (Chabad), דרך
מצוותיך.

## 7. Order of work

1. **Next session**: move this discourse's notes into the registers (§4.1), write the two check scripts, seed
   the lexicon from `terms.md`, write `wanted.yaml`, have the Tzemach Tzedek transcription proofread. Done
   when: the checks pass in the hook and the reading pack for 004 is regenerated from the register.
2. **Then**: `study-pack.py`, the `study-text` skill, the taught index for 004 and the differences register
   with the owner's rulings. Done when: the next text of 004 (or the next הערה) is prepared, studied, recorded
   and compared through the skill without hand-holding.
3. **Then**: run the citation agent over discourses 001–003 (their citations were never verified); grow the
   lexicon across discourses; topic notes for the subjects that recur (לבושים, בירורים, מ"ן ומ"ד).
4. **Later, autonomy**: a new text or recording in Drive starts stages 1–2 on its own; each new work in the
   library re-opens the open questions it might settle; a weekly consistency run.

## 8. What the owner decides

Whether the licence-unknown works stay; which differences in a comparison are errors and which are his own
teaching; which scans to bring; whether the lexicon prints in the pamphlets; and when a layer-3 explanation is
good enough to study from.
