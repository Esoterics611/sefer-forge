# Opus: after Fable writes — build, check, print and hand over an explanation of discourse 005

A prompt for the Opus session that follows any of the Fable prompts for discourse 005
(`prompts/fable-005-arizal.md`, `fable-005-rashash.md`). For leftovers of the preparing session, `prompts/opus-tidy-005.md`.
Fable wrote; this session does everything mechanical. **It does not rewrite Fable's
explanation.** It fixes directives and formatting, checks claims, and reports; a change of
meaning is proposed to Ronnie, not made. Run it once per explanation (the folder is named
in the first line of the prompt below).

Start a Claude Code session on this repo (environment `sefer-forge`, Opus), on the branch
Fable pushed to (or `main` after it is merged), and paste below the line, filling in the folder.

---

A Fable session has just finished writing the explanation in `discourses/005-kavanot-shacharit/<biur-arizal | biur-rashash | biur-chasdei-david>/`. Read its `HANDOFF.md` and Fable's last commits first. Your job is everything mechanical, so that I get a proofed PDF to study. List these steps in the task list and work through them:

1. **Build.**
   - Run `python scripts/build-biur.py <folder> --check`, then without `--check`.
   - Fix every directive that fails: from/to words, addresses, `mark=`. For חסדי דוד, also gaps or overlaps in the `@text` stretches; the build must cover 100% of the text.
   - Fix every `<!-- CHECK -->` Fable left. Look the words up with `scripts/source-lookup.py`.
   - Change only directives and formatting, never the explanation's sentences.
2. **Independent check.**
   - Give each part of the explanation (about a third each) to a subagent that has not seen the writing. It gets only the built text and the sources, and tries to break each claim about what a text says: a misquoted line, a wrong address, a reading the passage does not bear.
   - Check first the claims Fable listed in `HANDOFF.md`.
   - For the Rashash level, also check that each §N agrees with §N of level 1, or says where it departs.
   - Don't edit the explanation. Write the findings to `<folder>/check.md`: claim, problem, evidence, how serious. Clear slips (a wrong address, a typo in a quote) may be fixed in the directives; note each one there. Record the open findings in `<folder>/checks.yaml` for `--review`.
3. **Lexicon.** Turn the terms in `<folder>/notes/terms.md` into entries in `knowledge/lexicon/` (skill `chassidus-context`). `python scripts/lexicon.py --check` must report 0 errors.
4. **PDF.**
   - Build with `--pdf`, and a review copy with `--pdf --review`.
   - Proof it with skill `proof-pdf` until it is clean.
5. **Hand over.**
   - Commit and push.
   - Send me the PDF (`output/` is not in git).
   - Report in plain English: the build (passages, coverage), what the check found (the serious points first), what you fixed, and what waits for me.
