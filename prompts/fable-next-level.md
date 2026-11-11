# Fable: an explanation of the whole הגהה, to read before recording

A prompt for one long Claude Fable 5.2 session (written 2026-11-11, revised the
same day). Fable reads the Alter Rebbe's הגהה in discourse 004 and every
source it cites, in full and all together, and writes its own explanation for
Ronnie to study before he records anything more. It uses what Fable does
better than Opus: holding a long, difficult text and its sources in mind at
once, reasoning through it, and checking itself.

## How to use

1. Start a new Claude Code session on this repo, in the `sefer-forge`
   environment, with **Fable 5.2** selected and effort **high** (or **xhigh**
   for more care, which is slower and costs more).
2. Paste everything below the line.
3. Expect a long run. Fable costs twice what Opus does per token, so the
   prompt sends mechanical work to cheaper models.

(The first version of this prompt also covered the print and the repo's
instructions. It is in git history, in commit "A prompt for a long Fable
session".)

---

I'm Ronnie. I teach Chassidus and Kabbalah, and this repo turns my teaching into printed Hebrew pamphlets and books. CLAUDE.md explains how it works.

I'm studying a הגהה of the Alter Rebbe, "לשון אדמו"ר נ"ע בעצמו". It is discourse 004, in discourses/004-levushei-haneshama, and its notes.md says where everything is. It is a dense note on the garments of the soul made by Torah and mitzvot, full of abbreviations and of citations of עץ חיים, פרי עץ חיים, ספר הגלגולים, the Zohar and more. The full text is in sessions/001/ocr.md. An earlier model placed 26 of its citations in sessions/001/references.yaml; check each placement rather than trust it. sources/ holds עץ חיים, פרי עץ חיים and שער הגלגולים (see sources/README.md and scripts/source-lookup.py).

I have already recorded explanations of parts of it, and in at least one key passage ("אבל ירידתן משם…") I misread it. I'm not recording anything more until I understand the whole text properly. So I'm asking you, not Opus, because this needs what you do better: holding a long, difficult text and all its sources in mind at once, reasoning through it carefully, and checking yourself.

## What I want

Your own explanation of the entire הגהה, in Hebrew, for me to read and study.

- **Understand it whole.** Read the whole text, and every source it cites as the whole passage or chapter, not just the few lines around the citation. Keep all of it in view while you write, so that each part is explained in light of the whole. Where a cited work isn't in sources/, find it and add it the way sources/README.md describes. This includes ספר הגלגולים (the repo has only a parallel for it, שער הגלגולים), טעמי המצוות, ליקוטי תורה, מקדש מלך, the כוונות and the Zohar. Look on Sefaria first. If a scanned edition (for example on hebrewbooks.org) is the only form, read it from the page images, and keep the scans out of git like my photos. Where editions number differently, find the exact place the Alter Rebbe means. sources/sources.yaml records what has been found so far, and he himself mentions the Shklov print.
- **Keep it whole.** The explanation carries the original text complete, and every source passage it relies on complete. I want to read the Alter Rebbe, his sources and your explanation together without looking anything up. Keep the full chapters behind those passages in the repo as well, so I can check anything.
- **Explain it for me.** I know Chassidus and the Arizal's terms, but not this text. Start with what question the הגהה answers and how its argument moves, first briefly and then along the text. Expand every abbreviation. Explain each term where it first matters. Say what each source says and how the Alter Rebbe uses it. Point out where a reader is likely to go wrong. Make it as long as the text needs, written to be studied, in clear Hebrew.
- **Make it your own.** Work from the text and the sources only. Until your explanation is finished, don't read my transcripts, teaching texts or teaching notes in sessions 001–005, so that they don't shape your reading.
- **Then compare.** Once the explanation is finished, read what I have taught so far: the introduction, הערות א'–ג' and session 005. Write a short, separate list of the places where my teaching differs from your reading. Give the evidence for each, and say how much it matters.

Keep your working understanding in files as you go: the terms, a map of the argument, notes on each citation, and the open questions. The session may run long enough that its early context is summarized. Later sessions will also use your explanation as the reference when they check what I record.

Put the explanation in the repo as markdown, separate from my sessions and from discourse.md. It is not my words and never prints as mine. Also make a PDF of it that I can read, and proof it like every PDF here (skill `proof-pdf`). Hand me the PDF, because output/ isn't in git.

## How to work

This is Torah, and being wrong is worse than being incomplete. Every claim about what a text means rests on a line you can point to. Say how sure you are. Where the text is genuinely open, or the commentators differ, say so instead of choosing. Never invent a source, a quotation or a chapter number. Hebrew stays Hebrew.

Write the explanation yourself, as one line of thought; it has to hold together. Use subagents for the work that can be split off: finding and placing sources, and checking. Before a part counts as done, give it to a subagent that hasn't seen your reasoning. That subagent checks the part's claims against the sources and tries to break them. Resolve what it finds, or report it. Spend Fable on the reading, the writing and the checking. Fetching, building and proofing can run on Opus or Sonnet subagents. Every subagent adds cost, so don't start one for what a few tool calls can do.

The tooling (scripts, templates, skills) is yours to change if printing the explanation needs it. My material is not: don't change my sessions, their transcripts or discourse.md. CLAUDE.md's rules about sources of truth hold.

You may do these without asking: read anything in the repo; add works to sources/; write the explanation and your notes; add the scripts and templates needed to print it; build and proof; commit as you go and push to this session's branch; ask for network access to a host you need. Ask me first before you change anything of mine, publish anything, or merge into main.

## Finishing

Don't stop while you still owe work from this list. Status notes are welcome, but carry on with everything that doesn't depend on my answer. You will meet ordinary obstacles: a failing script, a timeout, a source that is hard to find, a blocked host. Diagnose them and work through them: retry, fix the request, or use another source. If a source can't be found at all, say so in the explanation, explain from what you have, and go on.

## The report

When you finish, write for someone who hasn't seen any of your work. Start with where the explanation is and what the הגהה says, in a few sentences. Then list the open questions, the sources you couldn't find, and what the comparison with my teaching found. Write in plain English and full sentences, and use Hebrew for the Torah content. Don't use labels or abbreviations you invented along the way.
