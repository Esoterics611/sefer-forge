# Fable: Shacharit after the Arizal, level 1 (discourse 005)

A prompt for Claude Fable 5.2 sessions (written 2026-11-12). The same prompt serves every
session of this explanation: each reads `HANDOFF.md`, writes the next sections, and hands
off. About three sessions (the split is in `discourses/005-kavanot-shacharit/biur-arizal/HANDOFF.md`).
Everything mechanical was done beforehand (the sources, the reading pack, the skeleton) or
is left to the Opus session after it (`prompts/opus-after-fable-005.md`).

## How to use

1. Start a new Claude Code session on this repo, environment `sefer-forge`, **Fable 5.2**,
   effort **high**.
2. Paste everything below the line.
3. When `HANDOFF.md` says the explanation is written, run `prompts/opus-after-fable-005.md`.

---

I'm Ronnie. I teach Chassidus and Kabbalah; this repo turns my teaching and study into printed Hebrew books (CLAUDE.md). Discourse 005, `discourses/005-kavanot-shacharit`, is new: an explanation of Shacharit, the morning prayer, in two levels. This explanation is the first level, the basics after the Arizal, from שער הכוונות and פרי עץ חיים. A second explanation, after the Rashash, will be built on it section by section, so this one is the frame for both.

**Your whole job is the reading and the writing.** The sources are already cut and arranged for you; don't search for others, and don't spend time on code, builds, formatting or checks. An Opus session does those after you. If a directive is awkward, write your best, mark it `<!-- CHECK -->`, and keep writing.

## Start here

Read `discourses/005-kavanot-shacharit/biur-arizal/HANDOFF.md`. It says where the work stands, which sections are next, and what was settled. Read `prompts/biur-rules.md` (what prints and what goes in the notes). If sections are already written, read the מבוא and the last section written to take up the voice. Read others only where you refer back.

## What to read

- One file per stage, `discourses/005-kavanot-shacharit/reading/arizal/NN-<slug>.md`. Read its index first. Then read the שער הכוונות part in full: it is the main text.
- פרי עץ חיים is the other redaction of the same teachings. It is worded differently throughout, so nothing in it could be marked as a duplicate. Read its index, then the paragraphs that carry the stage's main teaching or explain what שער הכוונות leaves unclear.
- For anything they cite: `python scripts/source-lookup.py <work> <address>` and `--find '<words>'`; the lexicon: `python scripts/lexicon.py <term>`.
- Don't read whole works in `sources/md/`, and don't read `biur.md` (it is generated from `biur.src.md`).

## What to write

In `biur-arizal/biur.src.md`, under the headings already there:

- **מבוא** (stage 00): the frame of the whole prayer. Why the order is what it is: from the start to ברוך שאמר is עשיה, to יוצר is יצירה, to the עמידה is בריאה, and the עמידה is אצילות. Deed and speech (מעשה ודיבור). What rises and what is drawn down, which partzufim, which union, and why on a weekday. Every later section stands on this, so write it first and make it exact.
- **§1–§13**, one per stage, in the order of the prayer. For each:
  - what this stage does in the frame: the world, what it repairs or raises, which partzufim and which union it brings about, and why it comes at this point;
  - its main kavanot, with the key passages set in by `@source` (work, address, from/to words, `mark=` on the words that matter);
  - how it connects to the stage before and the one after.

  The level is the basics, and the coverage is the whole prayer. Bring a name or a gematria where it carries the idea, not every one. Where the two redactions differ, say so and show both.
- **סיכום**: the morning as one movement, in a page or two.

Write in clear Hebrew, impersonal, for a reader who knows the Arizal's terms but not these gates. Every claim about what a text says rests on a passage you can point to. Being wrong is worse than being incomplete. Never invent a source, a quotation or an address. Hebrew stays Hebrew.

## Keeping it to the session

- **After each section:** `git add` the discourse's `biur-arizal/` folder, commit, and push to this session's branch. That is the only mechanical step.
- **Notes as you go** (`biur-arizal/notes/`, not the explanation): `terms.md` (term, meaning, address), `argument-map.md` (the frame, kept current), `citations.md` (each `@source` and how sure its reading is), `open-questions.md`.
- **Before stopping, or if your early context is being summarized:** update `HANDOFF.md` with the exact stopping point, what is settled, and the claims you most want checked. Then commit and push.
- **No subagents.** The independent checking is done afterwards, in the Opus session.

You may do these without asking: read anything listed above; write `biur.src.md`, the notes and `HANDOFF.md`; commit and push to this session's branch. Ask me first before you change anything else, publish anything, or merge into `main`.

## The report

In plain English, with Hebrew for the Torah content, for someone who hasn't seen your work: which sections you wrote and what each says in a sentence or two, what you most want checked, what remains open, and where the next session starts.
