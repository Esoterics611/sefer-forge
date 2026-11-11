# Fable: from print shop to study house

A prompt for one long Claude Fable 5.2 session (written 2026-11-11). It aims
Fable at what it does better than Opus: reading a dense text together with its
sources and getting it right, judging a printed page by eye, and running for
hours while checking its own work. Routine sessions stay on Opus.

## How to use

1. Start a new Claude Code session on this repo, in the `sefer-forge`
   environment, with **Fable 5.2** selected and effort **high**.
2. Paste everything below the line.
3. Expect a long run. Fable costs twice what Opus does per token, so the
   prompt tells it to send mechanical work to cheaper models.

---

I'm Ronnie. I teach Chassidus and Kabbalah, and this repo turns my teaching into printed Hebrew pamphlets and books. I photograph a text (or paste it from chabadlibrary.org) and record myself explaining it in Hebrew. The pipeline then transcribes, cleans, lays out, edits and prints it. It works. Read CLAUDE.md, docs/agentic-development.md, docs/print-standard.md and discourses/004-levushei-haneshama/notes.md to see how.

I'm bringing you in instead of Opus for three things Opus doesn't do well. First, reading a terse, abbreviation-dense Kabbalistic text together with its sources, and getting it right. Second, looking at a printed page the way a book designer does. Third, working for hours on your own and checking your own work until a large job is finished. Routine sessions, such as ingesting a recording or rebuilding a pamphlet, will stay on Opus. So leave the repo in a state where those sessions run better, not worse.

## Why now

This week the weak point showed. Discourse 004 is the Alter Rebbe's הגהה "לשון אדמו"ר נ"ע בעצמו". In session 005 I recorded my explanation of "אבל ירידתן משם…" and I had it backwards. I gave the refining of the garments to prayer and the world to the mitzvot. I read "ואינו אלא" as a negation, and "ולא תפלה לבדה דרבנן היא" as "although prayer is only rabbinic". The text says the reverse. By prayer the נר"ן rise from the kelipot as מ"ן, and others can do that for them. Their descent into the body is for the practical mitzvot, not for prayer alone, and it is only to repair their own garments, which no one else can do. I made the same slip when I summed up הערה ג' (session 004). Its print was aligned afterwards and I confirmed it.

The pipeline caught the mistake only after transcription, layout and the teaching pass, and then it patched it. Most of 005's printed explanation is now Claude's wording, standing in as "the speaker's correction" (the `edits:` in sessions/005/section-plan.yaml). I'm going to re-record it. The printed pamphlet also still isn't good enough (examples below).

The lesson: the pipeline spends its intelligence on mechanics and very little on understanding. That is what I want to change.

## What I want at the end

These are in order of priority. Where pieces are independent, work on them in parallel.

1. **Ready to re-record, and ready for the re-recording.**
   - A study brief for the stretch I'm re-recording, in Hebrew, as an A4 PDF like the reading pack. It should give what the Alter Rebbe says clause by clause, with the abbreviations expanded and the sources he cites open in full, not as snippets. It should show where my first recording went wrong and why the text can't mean that, and what in it still holds.
   - A fidelity audit of everything already recorded in 004: the introduction, הערות א'–ג' and session 005. List every place where my spoken explanation says the text or a source says something it doesn't. Rank them by weight, and give the evidence and your recommendation for each: leave it, fix one word, or re-record that cut. The point is that I re-record everything that needs it in one sitting. My own framing (the psychology, Jung, my analogies) is mine. Flag it only where I attribute it to the text.
   - A way for the repo to take a re-recording. Today a session can be extended (skill `extend-session`) but not re-recorded. The new recording should replace the old one as the session's source. The old transcript and the edits that patched it are retired, not lost; whether git history or a folder of their own keeps them is your call. Every pass is redone from my new words. The parts that refer to the session are reread (הערה ג' says "יתבאר להלן"). Then the discourse is reassembled, printed and proofed.

2. **A study partner before every recording.** Make the same kind of brief a standard stage of the pipeline, before I record each box of a reading pack. It covers:
   - the plain meaning and the argument;
   - the cited passages in full, in the edition the author used (sources/sources.yaml records where editions number differently);
   - how the box connects to what I've already taught in the discourse;
   - the readings a careful learner could get wrong, and the open questions.

   Make briefs for the next five boxes of 004, from box 4 on. Later boxes get theirs when they're started. When a cited work isn't in sources/, find it and add it the way sources/README.md describes. Look on Sefaria first. If a scanned edition (for example on hebrewbooks.org) is the only form, read it from the page images, and keep the scans out of git like my photos. For 004, the missing works are ספר הגלגולים (the repo has only a parallel for it, שער הגלגולים), טעמי המצוות, ליקוטי תורה, מקדש מלך, the כוונות and the Zohar.

3. **Review for meaning, not only for words.** After a recording is transcribed and before it is laid out, check what I said against the text and the brief. Divergences come to me as questions with the evidence, not as rewrites. My printed teaching is mine. `edits:` fix a slip of a word or a sentence. When the main line of a cut is wrong, the remedy is that I re-record the cut. Change the ingest procedure, the teaching pass and anything else that needs it, so that this is how it works from now on.

4. **Print at the level of a real sefer.** Look at every spread of every pamphlet, and of the book, the way a Hebrew typesetter would. Fix what's wrong in the templates and scripts, not page by page. Here is what I see in output/pamphlets/004-levushei-haneshama.pdf:
   - A sentence of the Alter Rebbe is broken across pages 23–24, with one line alone at the top of page 24.
   - The label "לשון אדמו"ר נ"ע" stands above every cut.
   - The key points at the end of a part repeat, word for word, what was printed a page earlier.
   - Three שער הגלגולים excerpts run over two pages before their one paragraph of explanation.

   proof-pdf.py passed that pamphlet, so teach it to catch what it missed. Fix defects without asking. Where it's a matter of taste (how the key points should work, how sources sit beside the text), render the options as sample spreads and let me choose. Show me before and after.

5. **Instructions written for you, and a memory.**
   - CLAUDE.md, prompts/, the skills and docs/print-standard.md hold about 155 KB of rules and step-by-step procedures, written for earlier models. Much of it spells out every step where a goal and a check would do. Rewrite them to say what each job is for, what done looks like and how it's checked. Keep every rule I decided, with its reason.
   - Mine the commit history, the notes.md files and the teaching notes for my decisions and corrections, and keep them in docs/lessons/. Write one lesson per file, with a one-line summary on top. Record corrections and confirmed approaches alike, with why they mattered. Update an existing note rather than add a duplicate, and delete a note that turns out to be wrong. Make every session read them.
   - Before you finish, have a reader who hasn't seen your work map every rule in the old instructions to where it lives in the new ones, or say why it's gone. Then have an Opus subagent run a real task from the new instructions alone, such as the status of every session or a pamphlet rebuild, to show they still work for Opus.

## How to work

The tooling in this repo (scripts, templates, skills, prompts, CLAUDE.md) is yours. How it's built is your call, and you'll keep building on it. The content is not yours. My recordings and what I said in them belong to me, and the texts and sources belong to their authors. CLAUDE.md's rules about sources of truth hold: never edit the raw audio, the images, the *.raw.txt files or the source exports; ocr.md is final once it has been matched; photos and audio never go into git; every commit is under the Esoterics611 identity. CLAUDE.md's procedures only describe how things are done today. Where one is in your way, change it and say so.

This is Torah, and being wrong in print is worse than being incomplete. Every claim about what a text means carries the line it rests on. Say how sure you are. Where the text is genuinely open, or the commentators differ, say so instead of choosing. Never invent a source, a quotation or a chapter number. Hebrew stays Hebrew. The briefs prepare me; they are not a script for me to read. Nothing you write goes into print as my words.

Check your work with fresh eyes. Before a brief, an audit finding or a layout change counts as done, give it to a subagent that hasn't seen your reasoning. That subagent checks it against the sources or the rendered pages and tries to break it. Before you report progress, check each claim against a tool result from this session. If something isn't verified, say so.

Delegate where the work is independent: a brief per box, the history mining, the spread-by-spread review. Keep working while subagents run. Spend Fable where Fable is needed: reading the texts, judging the print, verifying. Builds, sweeps and mechanical checks can run on Opus or Sonnet subagents. Every subagent adds cost, so don't start one for what a few tool calls can do.

You may do these without asking: build, rebuild and proof anything; change scripts, templates, skills, prompts, docs and CLAUDE.md; add works to sources/; add new skills; commit each finished piece and push it to this session's branch; ask for network access to a host you need.

Ask me first before you do any of these: change the printed teaching of a finished session, other than its layout; decide a disputed reading; delete anything of mine (retiring a recording I have re-recorded is fine); publish anything, such as to YouTube; merge into main.

## Finishing

Don't stop while you still owe work from this list. Status notes are welcome, and so are questions about open decisions, but carry on with everything that doesn't depend on my answer. You will meet ordinary obstacles: a failing script, a timeout, an empty search, a blocked host. Diagnose them and work through them: retry, fix the request, or use another source. Real blockers are few. Only I can make the re-recording, only I can decide a disputed reading, and I may decline a host. When you hit one, say what you found and go on with the rest. Hand me the PDFs you make, because output/ isn't in git.

## The report

When you finish, write for someone who hasn't seen any of your work: me, coming back from teaching. Lead with what changed and what I need to do, such as what to re-record and which choices are mine. Then give the details. Write in plain English and full sentences, and use Hebrew for the Torah content. Don't use labels or abbreviations you invented along the way. For each file or skill you mention, say in a plain clause what it is or what changed.
