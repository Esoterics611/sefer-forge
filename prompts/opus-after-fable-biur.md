# Opus: after Fable writes — build, check, print and hand over the explanation (discourse 004)

A prompt for the Opus session that follows `prompts/fable-finish-biur.md`. Fable
wrote the explanation of the הגהה "לשון אדמו"ר נ"ע בעצמו" in
`discourses/004-levushei-haneshama/biur/biur.src.md` and did nothing mechanical.
This session does the rest. **It does not rewrite Fable's explanation.** It
fixes directives and formatting, checks claims, and reports. A change of
meaning is proposed to Ronnie, not made.

Start a Claude Code session on this repo (environment `sefer-forge`, Opus), on
the branch Fable pushed to (or `main` after it is merged), and paste below the line.

---

A Fable session has just finished writing the explanation of the הגהה in `discourses/004-levushei-haneshama/biur/`. Read `biur/HANDOFF.md` and Fable's last commits first. Your job is everything mechanical, so that I get a proofed PDF to study and a place to record my corrections. List these steps in the task list and work through them:

1. **Build.** Run `python scripts/build-biur.py discourses/004-levushei-haneshama/biur --check`, then without `--check`. Fix every directive that fails: from/to words, addresses, `mark=`, and gaps or overlaps in the `@text` stretches. Fix also every `<!-- CHECK -->` Fable left. Look the words up with `scripts/source-lookup.py`. The build must cover 100% of the text. Change only directives and formatting, never the explanation's sentences.
2. **Independent check.**
   - Give each third of the explanation (sections 1–7, 8–13, 14–19 and the close) to a subagent that has not seen the writing. It gets only the built text and `sources/`, and tries to break each claim about what a text says: a misquoted line, a wrong address, a reading the passage does not bear.
   - Check the claims Fable listed in `HANDOFF.md` first.
   - Do not edit the explanation. Write the findings to `biur/check.md`: claim, problem, evidence, how serious. Clear slips (a wrong address, a typo in a quote) may be fixed in the directives; note each one there.
3. **Lexicon.** Turn the new terms in `biur/notes/terms.md` into entries in `knowledge/lexicon/` (skill `chassidus-context`). `python scripts/lexicon.py --check` must report 0 errors.
4. **PDF.**
   - Write `templates/biur.css`, in the house style of `templates/pamphlet.css`, A5 or A4, whichever reads better for study.
   - Number every paragraph of the explanation (§4.3 = section 4, paragraph 3), so a remark can point to its place.
   - Build with `--pdf`.
   - Proof it with skill `proof-pdf` until clean.
5. **Review setup.** Follow the scheme agreed on 2026-11-12:
   - `biur/review/` holds one folder per sitting: my voicenote (local only), the transcript (committed) and a faithful cleaned copy.
   - `biur/corrections.yaml` is the register. Each item has: place, what the explanation says, what I say, source, kind (error / different reading / my own correction / question) and status (applied / disputed / open).
   - Add a short `biur/review/README.md` that says how a sitting is processed.
6. **Hand over.**
   - Commit and push.
   - Send me the PDF (`output/` is not in git).
   - Report in plain English: the build's coverage, what the check found (the serious points first), what you fixed, and what waits for me.
