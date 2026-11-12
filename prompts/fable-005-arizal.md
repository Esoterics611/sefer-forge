# Fable: Shacharit after the Arizal, level 1 — one limited session (discourse 005)

A prompt for **one** Claude Fable 5.2 session with a fixed scope (written 2026-11-12, limited
the same day at Ronnie's request). It writes the frame of the explanation and the part of the
morning that is in עולם העשיה: the מבוא (stage 00) and sections 1–4 (stage 01 rising and the
morning blessings, 02 ציצית, 03 תפילין, 04 the קרבנות). Then it stops. The later parts (5–9 and
10–13 with the סיכום) are separate sessions with this same prompt, each started only when
Ronnie decides; `HANDOFF.md` says which part is next. Everything mechanical was done before
(sources, reading pack, skeleton) or is left to Opus after (`prompts/opus-after-fable-005.md`).

## How to use

1. Start a new Claude Code session on this repo, environment `sefer-forge`, **Fable 5.2**,
   effort **high**.
2. Paste everything below the line.
3. When it reports, run `prompts/opus-after-fable-005.md` on `biur-arizal`, or start the
   next part with this prompt.

---

I'm Ronnie. I teach Chassidus and Kabbalah; this repo turns my teaching and study into printed Hebrew books (CLAUDE.md). Discourse 005, `discourses/005-kavanot-shacharit`, explains Shacharit, the morning prayer, in two levels. You are writing part of the first level, the basics after the Arizal, from שער הכוונות and פרי עץ חיים. A second level, after the Rashash, will be built on it section by section, so this is the frame for both.

## Your scope in this session, and nothing more

Read `discourses/005-kavanot-shacharit/biur-arizal/HANDOFF.md`: it names the part to write now. If nothing is written yet, the part is:
- **the מבוא** (stage 00), the frame of the whole prayer;
- **§1–§4**, stages 01–04.

When those sections are written and committed, update `HANDOFF.md`, report, and stop. Don't start the next part, even if you have context left.

**Your whole job is the reading and the writing.** The sources are already cut and arranged; don't search for others, and don't spend time on code, builds, formatting or checks. If a directive is awkward, write your best, mark it `<!-- CHECK -->`, and go on.

## What to read, in this order, and only this

1. `biur-arizal/HANDOFF.md`, `prompts/biur-rules.md`, and the headings in `biur-arizal/biur.src.md`.
2. For each stage of your scope, its file `discourses/005-kavanot-shacharit/reading/arizal/NN-<slug>.md`:
   - the index first;
   - then the **שער הכוונות** part, in full: it is the main text;
   - then **פרי עץ חיים** by its index only, reading in full at most three passages per section: those that carry the stage's main teaching, or say what שער הכוונות leaves unclear.
3. A cited passage of עץ חיים, only where the explanation needs it: `python scripts/source-lookup.py etz-chaim <address>`.

Don't read whole works in `sources/md/`, `biur.md`, the Rashash's files, or other discourses.

## What to write

In `biur-arizal/biur.src.md`, under the headings already there:

- **מבוא:** why the morning has the order it has: from the start to ברוך שאמר is עשיה, to יוצר is יצירה, to the עמידה is בריאה, and the עמידה is אצילות. Deed and speech (מעשה ודיבור). What rises and what is drawn down. Which partzufim and which union are involved, and why on a weekday. Every later section stands on this, so make it exact.
- **§1–§4:** for each:
  - what the stage does in that frame: the world, what it repairs or raises, which partzufim, and why it comes at this point;
  - its main kavanot, with the key passages set in by `@source` (work, address, from/to words, `mark=` on the words that matter);
  - how it leads into the next stage.

  The level is the basics. Bring a name or a gematria where it carries the idea, not every one. Where the two redactions differ, say so and show both.

Write in clear Hebrew, impersonal, for a reader who knows the Arizal's terms but not these gates. Every claim rests on a passage you can point to. Being wrong is worse than being incomplete. Never invent a source, a quotation or an address. Hebrew stays Hebrew.

## Working

- **After each section:** `git add` the discourse's `biur-arizal/` folder, commit, and push to this session's branch.
- **Notes** (`biur-arizal/notes/`, not the explanation): `terms.md` (term, meaning, address), `argument-map.md` (the frame), `citations.md` (each `@source` and how sure its reading is), `open-questions.md`.
- **Before stopping:** in `HANDOFF.md`, the part written, the next part, what is settled, the claims most worth checking, and every `<!-- CHECK -->`. Commit and push.
- **No subagents.** The checking is done afterwards, by Opus.

You may do these without asking: read what is listed above; write in `biur-arizal/`; commit and push to this session's branch. Ask me before you change anything else, publish anything, or merge into `main`.

## The report

In plain English, with Hebrew for the Torah content, short: what the מבוא establishes, what each section says in a sentence or two, what you most want checked, what is open, and the next part.
