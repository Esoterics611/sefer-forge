# Fable: finish the explanation of the הגהה (discourse 004), in one session

A prompt for one Claude Fable 5.2 session (written 2026-11-12). The first Fable
session (`prompts/fable-next-level.md`) read the הגהה "לשון אדמו"ר נ"ע בעצמו" with
its sources, planned all 19 sections of an explanation and wrote sections 1–10
(26% of the text). This session writes sections 11–19 and the close, in the
same voice, and nothing else, so that it fits in one session.

## How to use

1. Make sure `main` has the knowledge layer (`knowledge/`, skill `chassidus-context`).
2. Start a new Claude Code session on this repo, in the `sefer-forge` environment,
   with **Fable 5.2** selected and effort **high**.
3. Paste everything below the line.

Left for a later (Opus) session: the PDF and its proof, the comparison with
Ronnie's teaching, and setting up his review of the explanation.

---

I'm Ronnie. I teach Chassidus and Kabbalah; this repo turns my teaching into printed Hebrew pamphlets and books (CLAUDE.md). A previous Fable session began its own explanation of the Alter Rebbe's הגהה "לשון אדמו"ר נ"ע בעצמו" (תורה אור, חיי שרה) in `discourses/004-levushei-haneshama/biur/`. I've read the first half and find it excellent. I want you to finish it, sections 11 to 19 and the close, in the same voice, as one line of thought with what is written.

## What to read, and what not to

This must fit in one session, so read only what the writing needs, in this order:

1. `biur/HANDOFF.md`: the state of the work and what the reading has established.
2. `biur/notes/segments.md`, sections יא–יט: the plan and first reading of each section still to write. This is your outline.
3. `biur/notes/argument-map.md`, `biur/notes/open-questions.md`, and the parts of `biur/notes/citations.md` that sections 11–19 use.
4. `biur/biur.src.md`: the front matter, פתח דבר, sections א and ב, section 1 and section 10. That is enough to take up the voice, the layout and the directives. Read the other sections only where a later section refers back to them.
5. The `scripts/build-biur.py` docstring (the `@text`, `@source` and `@file` directives).
6. `knowledge/lexicon/INDEX.md`, and `python scripts/lexicon.py <term>` for the terms you use (skill `chassidus-context`).

**Do not read:**
- `biur/biur.md`. It is generated from `biur.src.md`, so it only repeats it (90 KB).
- Whole works in `sources/md/`. Take each passage with `python scripts/source-lookup.py <work> <address>` (one chapter) or `--find '<words>'`.
- My sessions, transcripts and teaching texts in `discourses/004-levushei-haneshama/sessions/` (other than `001/ocr.md`), `introduction*.md`, and `discourse*.md`. The explanation stays independent of my teaching until it is finished.

**Do not search again for works that are missing.** ספר הגלגולים, טעמי המצוות and זוהר הרקיע are not available (checked 2026-11-11 and 2026-11-12; see `sources/sources.yaml`). Explain from the parallels already found, and say so where it matters.

## What to write

- **Sections 11–19 in `biur.src.md`, following `segments.md`.** For each section:
  - the stretch of the text (`@text`, contiguous with the last one; the build fails if a word is skipped);
  - the abbreviations it opens;
  - every source the section relies on, set in with `@source`, quoted complete and with the words that matter marked;
  - your explanation.

  The first reading in `segments.md` is a plan, not a result. Where the sources say otherwise, follow them and correct the notes.
- **Section 19 most of all.** The closing stretch ("ע"ש היטב הדק … וצ"ע. אך זה אינו …") is the most compressed. Work out who the subject of each clause is and what exactly "אך זה אינו" rejects. Where it stays open, say what the possibilities are and what would decide between them.
- **The close:**
  - a short summary of the whole הגהה as the explanation now reads it;
  - the open questions, folded in from `open-questions.md` and the "settled since" list in `HANDOFF.md`;
  - the sources not found, and what was used instead.
- **Accuracy first.** Being wrong is worse than being incomplete. Every claim about what a text means rests on a line you can point to. Say how sure you are. Never invent a source, a quotation or a chapter number. Hebrew stays Hebrew.

## How to work within one session

- **After each section:** run `python scripts/build-biur.py discourses/004-levushei-haneshama/biur`, commit, and push to this session's branch. A session cut short then loses nothing.
- **Three independent checks:** after sections 13, 16 and 19, give the built text of those sections to a Sonnet subagent that has not seen your reasoning. It gets the passages, the addresses and `sources/`, and tries to break each claim. Ask it for a short list (claim, problem, evidence). Resolve each point, or record it among the open questions. No other subagents.
- **If your early context gets summarized:** first update `HANDOFF.md` with the exact stopping point and what is settled, then commit.
- **At the end:**
  - add the terms the second half needed and the lexicon lacks (skill `chassidus-context`; `python scripts/lexicon.py --check` must report 0 errors);
  - update `HANDOFF.md` for the next session (PDF, comparison, review);
  - commit and push.

You may do these without asking: read what is listed above; write `biur.src.md` and the notes; add lexicon entries; fix `build-biur.py` if the writing needs it; commit and push to this session's branch. Ask me first before you change anything of mine, publish anything, or merge into `main`.

## The report

Write for someone who hasn't seen your work, in plain English, with Hebrew for the Torah content:
- what sections 11–19 say, in a few sentences;
- how the close reads the whole הגהה;
- what the independent checks found and what you did about it;
- what remains open.
