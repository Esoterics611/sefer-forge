# Fable: Shacharit after the Rashash, level 2 (discourse 005)

A prompt for a Claude Fable 5.2 session (written 2026-11-12), to run **after** level 1
(`prompts/fable-005-arizal.md`) is written. It explains Shacharit as the Rashash reads it,
from his own words in נהר שלום, on top of level 1, section by section. About one session
(the Rashash's material is about 410K characters); if it runs over, the same prompt
continues from `HANDOFF.md`. The Opus session after it: `prompts/opus-after-fable-005.md`.

## How to use

1. Make sure level 1 (`discourses/005-kavanot-shacharit/biur-arizal/`) is written, and its
   branch is merged or checked out.
2. Start a new Claude Code session on this repo, environment `sefer-forge`, **Fable 5.2**,
   effort **high**.
3. Paste everything below the line.

---

I'm Ronnie. I teach Chassidus and Kabbalah; this repo turns my teaching and study into printed Hebrew books (CLAUDE.md). Discourse 005, `discourses/005-kavanot-shacharit`, explains Shacharit in two levels. The first level, the basics after the Arizal, is written in `biur-arizal/`. I want you to write the second: Shacharit after the Rashash, in `biur-rashash/`.

**Your whole job is the reading and the writing.** The sources are already cut and arranged for you; don't search for others, and don't spend time on code, builds, formatting or checks. An Opus session does those after you. If a directive is awkward, write your best, mark it `<!-- CHECK -->`, and keep writing.

## Start here

Read `discourses/005-kavanot-shacharit/biur-rashash/HANDOFF.md`: the state, and the reading order. Read `prompts/biur-rules.md`. Then read level 1, `biur-arizal/biur.src.md`, with its `notes/argument-map.md` and `notes/terms.md`. This explanation stands on it.

## What to read

In this order (all under `discourses/005-kavanot-shacharit/reading/rashash/`):
1. `R1-hakdamat-rechovot-hanahar.md`: his foundations. Read it whole.
2. `00-yesodot.md`: the source of souls, the three prayers, the four repairs of prayer (ד' תיקוני התפלה).
3. The stage files 01–10, in order.
4. `R2-sheelot-utshuvot.md` (questions sent to him and his answers) and `R3-klalim-vehagahot.md` (the דעת, כללים, and his glosses on שער הכוונות). Read their index first; read in full where a stage needs them.

The parenthesised folios in נהר שלום ("(מ"ח ע"א)") belong to the book he is speaking about, not to נהר שלום. Where he refers to a passage of שער הכוונות, it is in `reading/arizal/` or `scripts/source-lookup.py shaar-hakavanot`. His siddur's charts (the names themselves) are not available; explain from his prose, and note in `notes/open-questions.md` where a chart would be needed.

Don't read whole works in `sources/md/`, and don't read `biur.md` (it is generated).

## What to write

In `biur-rashash/biur.src.md`, under the headings already there (§N here is the same stage as §N of level 1):

- **מבוא:** what the Rashash adds to the frame of level 1, from רחובות הנהר. The inner and outer worlds (אבי"ע דפנימיות / דחיצוניות and their nesting). The partzufim of every world, and the נרנח"י of every partzuf. The four repairs of prayer. Why each day of the week is different. What the kavanah "draws" at each stage (mochin, צלמים). Build it up slowly enough that a reader of level 1 can follow it.
- **§1–§10:** for each stage, open from what §N of level 1 established, in a sentence. Then:
  - what the Rashash adds, changes or makes precise, set in from נהר שלום by `@source` (`work="nahar-shalom"`, addresses page.paragraph, e.g. `ref="27a.7"`);
  - how his scheme turns the Arizal's kavanah into a precise one;
  - where he answers a difficulty in שער הכוונות (his glosses, his answers in R2).

  Don't repeat level 1.
- **סיכום:** the morning in the Rashash's terms, and what level 2 changes in how level 1 reads.

Write in clear Hebrew, impersonal, for a reader who has studied level 1. Every claim about what a text says rests on a passage you can point to. Being wrong is worse than being incomplete. Never invent a source, a quotation or an address. Hebrew stays Hebrew.

## Keeping it to the session

- **After each section:** `git add` the discourse's `biur-rashash/` folder, commit, and push to this session's branch.
- **Notes as you go** (`biur-rashash/notes/`): `terms.md`, `argument-map.md`, `citations.md`, `open-questions.md`.
- **Before stopping, or if your early context is being summarized:** update `HANDOFF.md` with the stopping point, what is settled, and the claims to check. Then commit and push.
- **No subagents.**

You may do these without asking: read anything listed above; write `biur-rashash/` (the explanation, the notes, `HANDOFF.md`); commit and push to this session's branch. Ask me first before you change level 1 or anything else, publish anything, or merge into `main`. If level 1 seems wrong somewhere, say so in `HANDOFF.md` and in the report; don't edit it.

## The report

In plain English, with Hebrew for the Torah content: what the Rashash adds, in a few sentences; what each section says, briefly; where level 1 needs correcting, if anywhere; what you most want checked; what remains open.
