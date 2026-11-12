# Fable: finish the explanation of the הגהה (discourse 004), in one session

A prompt for one Claude Fable 5.2 session (written 2026-11-12). The first Fable
session (`prompts/fable-next-level.md`) read the הגהה "לשון אדמו"ר נ"ע בעצמו" with
its sources, planned all 19 sections of an explanation and wrote sections 1–10
(26% of the text). This session only writes: sections 11–19 and the close, in
the same voice. Everything mechanical (building, fixing directives, checks,
lexicon entries, PDF, proof) is handed to an Opus session afterwards:
`prompts/opus-after-fable-biur.md`.

## How to use

1. Make sure `main` has the knowledge layer (`knowledge/`) and this prompt.
2. Start a new Claude Code session on this repo, in the `sefer-forge` environment,
   with **Fable 5.2** selected and effort **high**.
3. Paste everything below the line.
4. When it is done, start an Opus session with `prompts/opus-after-fable-biur.md`.

---

I'm Ronnie. I teach Chassidus and Kabbalah; this repo turns my teaching into printed Hebrew pamphlets and books (CLAUDE.md). A previous Fable session began its own explanation of the Alter Rebbe's הגהה "לשון אדמו"ר נ"ע בעצמו" (תורה אור, חיי שרה) in `discourses/004-levushei-haneshama/biur/`. I've read the first half and find it excellent. I want you to finish it, sections 11 to 19 and the close, in the same voice, as one line of thought with what is written.

**Your whole job is the reading and the writing.** Don't spend time on code, builds, formatting, checks or tooling. An Opus session does all of that after you (`prompts/opus-after-fable-biur.md`). If a script fails or a directive is awkward, leave it as it is, note it in `HANDOFF.md`, and keep writing.

## What to read, and what not to

Read only what the writing needs, in this order:

1. `biur/HANDOFF.md`: the state of the work and what the reading has established.
2. `biur/notes/segments.md`, sections יא–יט: the plan and first reading of each section still to write. This is your outline.
3. `biur/notes/argument-map.md`, `biur/notes/open-questions.md`, and the parts of `biur/notes/citations.md` that sections 11–19 use.
4. `biur/biur.src.md`: the front matter, פתח דבר, sections א and ב, section 1 and section 10. That is enough to take up the voice and the layout. Read the other sections only where a later section refers back to them.
5. `knowledge/lexicon/INDEX.md`, and `python scripts/lexicon.py <term>` for a term you want the sources of.

For each source passage, use `python scripts/source-lookup.py <work> <address>` (one chapter) or `--find '<words>'`. These are your reading tools; use them freely.

**Do not read:**
- `biur/biur.md`. It is generated from `biur.src.md`, so it only repeats it (90 KB).
- Whole works in `sources/md/`.
- My sessions, transcripts and teaching texts in `discourses/004-levushei-haneshama/sessions/` (other than `001/ocr.md`), `introduction*.md`, and `discourse*.md`. The explanation stays independent of my teaching until it is finished.

**Do not search again for works that are missing.** ספר הגלגולים, טעמי המצוות and זוהר הרקיע are not available (checked 2026-11-11 and 2026-11-12). Explain from the parallels already found, and say so where it matters.

## What to write

- **Sections 11–19 in `biur.src.md`, following `segments.md`.** For each section:
  - the stretch of the text (`@text`, carrying on from the last one);
  - the abbreviations it opens;
  - the sources it relies on, set in with `@source`, the words that matter marked;
  - your explanation.

  Write the directives as sections 1–10 do. If you are unsure of an exact from/to, write your best and mark it `<!-- CHECK -->`; Opus will fix it.

  The first reading in `segments.md` is a plan, not a result. Where the sources say otherwise, follow them.
- **Section 19 most of all.** The closing stretch ("ע"ש היטב הדק … וצ"ע. אך זה אינו …") is the most compressed. Work out who the subject of each clause is and what exactly "אך זה אינו" rejects. Where it stays open, say what the possibilities are and what would decide between them.
- **The close:**
  - a short summary of the whole הגהה as the explanation now reads it;
  - the open questions, folded in from `open-questions.md` and the "settled since" list in `HANDOFF.md`;
  - the sources not found, and what was used instead.
- **Accuracy first.** Being wrong is worse than being incomplete. Every claim about what a text means rests on a line you can point to. Say how sure you are. Never invent a source, a quotation or a chapter number. Hebrew stays Hebrew.
- **For the Opus session, notes only (no formatting work):**
  - in `biur/notes/terms.md`, under a new heading, the terms the second half needed: term, meaning, address;
  - in `HANDOFF.md`, the claims you most want checked against the sources, and anything left marked `<!-- CHECK -->`.

## Keeping it to one session

- **After each section:** `git add` the biur folder, commit, and push to this session's branch. A session cut short then loses nothing. That is the only mechanical step.
- **If your early context gets summarized:** first update `HANDOFF.md` with the exact stopping point and what is settled, then commit.
- **No subagents.** The independent checking is done afterwards, in the Opus session.

You may do these without asking: read what is listed above; write `biur.src.md`, the notes and `HANDOFF.md`; commit and push to this session's branch. Ask me first before you change anything of mine, publish anything, or merge into `main`.

## The report

Write for someone who hasn't seen your work, in plain English, with Hebrew for the Torah content:
- what sections 11–19 say, in a few sentences;
- how the close reads the whole הגהה;
- what you most want checked;
- what remains open.
