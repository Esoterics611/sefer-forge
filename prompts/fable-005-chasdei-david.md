# Fable: an explanation of קונטרס חסדי דוד (discourse 005)

A prompt for one Claude Fable 5.2 session (written 2026-11-12). R. David Magar's קונטרס
(a הקדמה and 120 numbered כללים, about 85K characters) is explained whole, as a
commentary on the text, stretch by stretch. It is not tied to Shacharit, and it can run
before or after the two Shacharit explanations. If it is run first, it is a good
foundation for the Rashash level. The Opus session after it: `prompts/opus-after-fable-005.md`.

## How to use

1. Start a new Claude Code session on this repo, environment `sefer-forge`, **Fable 5.2**,
   effort **high**.
2. Paste everything below the line.

---

I'm Ronnie. I teach Chassidus and Kabbalah; this repo turns my teaching and study into printed Hebrew books (CLAUDE.md). I want an explanation of קונטרס חסדי דוד by R. David Magar: 120 numbered כללים that set out the whole system as the Rashash teaches it, from אור אין סוף and the צמצום down through the worlds. It belongs to discourse 005 (`discourses/005-kavanot-shacharit/biur-chasdei-david/`), but it stands on its own.

**Your whole job is the reading and the writing.** Don't spend time on code, builds, formatting or checks; an Opus session does those after you. If a directive is awkward, write your best, mark it `<!-- CHECK -->`, and keep writing.

## Start here

Read `biur-chasdei-david/HANDOFF.md` and `prompts/biur-rules.md`. Then read the whole קונטרס in `discourses/005-kavanot-shacharit/reading/chasdei-david/CD-chasdei-david.md`: the index, then the text. Read it through once before writing anything.

## What to write

1. **The plan first,** in `biur-chasdei-david/notes/segments.md`. Group the כללים into sections by subject: אין סוף and the צמצום, the circles and the line, א"ק and its lights, the נקודים and the breaking, the partzufim of אצילות, the worlds, and so on, as the text actually divides. Give each section its first and last words, and a line on what it says. Commit.
2. **The explanation,** in `biur-chasdei-david/biur.src.md`:
   - a **מבוא**: what the קונטרס is, what it assumes, and how its כללים build on one another;
   - **numbered sections** (`### N. <subject>`), each opening with the stretch of the text it explains (`@text from="…" to="…"`, carrying on from the last one, so the whole text is covered in order). Then the explanation: every כלל, what it says, and what in עץ חיים or in the Rashash it rests on. Set the key source passages in with `@source` (`work="etz-chaim"`, `work="nahar-shalom"`, …). Explain each term where it first matters, and show how this כלל prepares the next;
   - a **סיכום**.

   Look sources up with `python scripts/source-lookup.py <work> <address>` and `--find '<words>'`. נהר שלום (`nahar-shalom`, addresses page.paragraph) has his foundations in `reading/rashash/R1-hakdamat-rechovot-hanahar.md`. The lexicon: `python scripts/lexicon.py <term>`.

Write in clear Hebrew, impersonal, for a reader who knows the Arizal's terms but not the Rashash's. Every claim rests on a passage you can point to. Being wrong is worse than being incomplete. Never invent a source, a quotation or an address. Hebrew stays Hebrew.

## Keeping it to the session

- **After each section:** `git add` the folder, commit, and push to this session's branch.
- **Notes as you go** (`biur-chasdei-david/notes/`): `terms.md`, `citations.md`, `open-questions.md`.
- **Before stopping, or if your early context is being summarized:** update `HANDOFF.md` with the stopping point and the claims to check. Then commit and push.
- **No subagents.**

You may do these without asking: read anything in the repo; write `biur-chasdei-david/`; commit and push to this session's branch. Ask me first before you change anything else, publish anything, or merge into `main`.

## The report

In plain English, with Hebrew for the Torah content: what the קונטרס says as a whole, in a few sentences; the sections; what you most want checked; what remains open.
