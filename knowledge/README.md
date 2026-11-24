# knowledge/ — what the repo understands of Chassidus and Kabbalah

A Claude session starts knowing nothing of this repo. What it should not have to
re-learn every time (what a term means in these texts, where the Arizal says it,
which citations point where, how the teacher explains it) is kept here, small
enough to read at the start of a task, and every line of it traceable to a
source. `sources/` is the library (the full works, searched, not read); this
folder is the understanding built on it.

## The four parts

| Part | Where | What | State |
|---|---|---|---|
| **Lexicon** | `lexicon/<slug>.yaml`, index `lexicon/INDEX.md` | one entry per term: its meanings in these texts, each resting on exact words at an address in `sources/` | **started** (2026-11-12, from discourse 004; 100 terms on 2026-11-24, with 006 פדה בשלום and 007 שער היחוד) |
| Concepts | `concepts/<slug>.md` | a page or two per recurring teaching (מ"ן ומ"ד, בירור הלבושים, פנימיות וחיצוניות…): the argument, its key passages by address, the lexicon terms it uses | planned |
| Citations | `citations.yaml` | every citation met in any text → the address it resolves to, how sure, and the edition's numbering where it differs | planned (today: `sources/sources.yaml` `numbering:` and each discourse's `biur/notes/citations.md`) |
| The teacher | `teacher/terms.yaml`, generated `teacher/TERMS.md` | Ronnie's meaning of each term in the soul and in service (the second dimension of every term, 002 introduction): `said:` his words, quoted from the shiur and checked; `applied:` Claude's application of his frame, to confirm. Read by `scripts/teacher-terms.py` (`--check`, `--in <file>`; a plain run writes TERMS.md and syncs each lexicon entry's `teacher:`); printed as the "בנפש האדם" layer of an explanation (`prompts/biur-rules.md`) | **started** (2026-11-16, from 002 and 004) |

Two rules hold across all four:

1. **What the sources say and what the teacher says are kept apart.** A lexicon
   meaning rests on `sources/`; the teacher's way of putting it goes under the
   entry's `teacher:` (with the session it comes from) or in `teacher/`, never
   mixed into the meaning. Claude's own reading is marked as such (`status: draft`).
2. **Nothing from memory.** Every quotation is set by address and checked by
   script. Where no source is in hand, say so (`open:`, or a `cite:` outside
   `sources/`), never fill the gap.

## The lexicon

One file per term, `lexicon/<slug>.yaml`, the slug a lowercase transliteration
(`mayin-nukvin`, `tzelem-deima`). The format:

```yaml
term: 'מ"ן (מיין נוקבין)'        # the heading form
forms: ['מ"ן', 'מ"נ', 'מיין נוקבין']   # how texts write it: --in finds the term in a text by these
abbrev: {'מ"ן': 'מיין נוקבין'}   # optional: abbreviations opened
category: 'מ"ן ומ"ד והזיווג'      # the index groups by this
senses:                           # one or more meanings, as these texts use the term
  - meaning: >-
      What it means, in Hebrew, in plain words. Claude's or the teacher's
      explanation; the words below are what it rests on.
    rests_on:
      - work: etz-chaim           # a work in sources/sources.yaml
        ref: '39.1.2'             # its address (a prefix is fine: 39.1 = the whole chapter)
        quote: 'הם הנשמות הקדושות ממש'   # the exact words (checked; niqqud and punctuation ignored)
        note: optional
      - work: zohar
        page: '2 210b'            # or a printed page (volume and page) for the Zohar / Mikdash Melekh
        quote: '...'
      - cite: 'ספר הגלגולים פ"ז'  # a source not in sources/: listed, not checked
    note: optional
related: [mayin-duchrin, nukva]   # other entries
caution: >-                       # optional: where a reader goes wrong
open: >-                          # optional: what is not settled, and what would settle it
teacher:                          # optional: how the teacher explains it (kept apart from the meaning)
  - said: '...'
    where: discourses/004-levushei-haneshama/sessions/005
status: draft                     # draft = Claude's reading, quotes checked by script
                                  # checked = also read against the sources by the teacher or an independent check
learned_from: [discourses/004-levushei-haneshama]
```

## Using it

    python scripts/lexicon.py --in <file>      # which known terms a text uses (start of any new text)
    python scripts/lexicon.py צלם             # the entry, every source quoted in context from sources/
    python scripts/lexicon.py --check         # after any change: addresses, quotes, related terms; rewrites INDEX.md

Skill `chassidus-context` says when: before explaining a text, planning a
teaching pass, drafting with the teacher, or checking what he recorded, read the
entries for the terms the text uses; and at the end of such work, add the terms
it met and correct the entries it found wrong.

## From one discourse into the next

What a discourse learns is carried to the next in four steps, at the close of the work on it (skill
`chassidus-context`, "After the work"):

1. **Its text becomes a source.** A text taken in from chabadlibrary.org (a session's `ocr.md`, final once
   ingested) is registered in `sources/sources.yaml` (`importer: chabadlibrary`; `raw:` the ocr.md, or a
   glob of them with `address: chapter` for a work taken in chapter by chapter) and turned into a JSON by
   `python scripts/chabadlibrary-import.py`. From then on it is looked up and quoted like עץ חיים:
   `source-lookup.py --find '...' padah-beshalom`, `source-lookup.py shaar-hayichud 12` (פרק יב).
2. **Its terms enter the lexicon,** each meaning resting on the text's exact words at their address, so the
   check holds them: what פדה בשלום says of היחידה is `padah-beshalom 52a.1`, not a paraphrase.
3. **The teacher's meaning joins the entry.** A term Ronnie defined in a shiur (`teacher/terms.yaml`,
   `lexicon:` naming the entry) is copied into the entry's `teacher:` by `teacher-terms.py`: both dimensions,
   the sources and the soul, in one place.
4. **The next discourse starts from it.** `lexicon.py --in <its text>` and `teacher-terms.py --in` list the
   terms it shares with everything before it; a gloss, a footnote or a glossary entry starts from the entry
   (a booklet's מילון המונחים, skill `biur-booklet`), and a sense the new text adds is a new sense with its
   own address.

## Growing it

- A term enters when a text needs it explained, with the passages that settle
  its meaning there. Several meanings are several `senses`, not one blurred one.
- A meaning that a later text shows to be too narrow gets a new sense or a
  `caution:`; nothing is rewritten silently. Git keeps the history.
- `status: checked` only after a reading against the sources by someone other
  than the writer (the teacher, or a subagent that did not see the reasoning).
