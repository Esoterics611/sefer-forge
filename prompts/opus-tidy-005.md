# Opus: tidy up the leftovers of discourse 005 (כוונות תפילת השחר)

A prompt for one Opus session (written 2026-11-12), at any time after the session that
prepared discourse 005 and wrote the explanation of קונטרס חסדי דוד. It finishes what that
session left: the independent check of the חסדי דוד explanation, the lexicon, and the
repo's own documentation of the new tools. It does not write or rewrite explanations; a
change of meaning is proposed to Ronnie, not made. (After a Fable part of the Shacharit
explanations, use `prompts/opus-after-fable-005.md` instead.)

Start a Claude Code session on this repo (environment `sefer-forge`, Opus), on branch
`claude/busy-planck-pec3bg` (or `main` after it is merged), and paste below the line.

---

Discourse 005 (`discourses/005-kavanot-shacharit`) was prepared in one session: the sources (נהר שלום and קונטרס חסדי דוד added to `sources/`), a reading pack by stage of Shacharit (`reading/`), three explanation folders, and the חסדי דוד explanation, written, built and proofed. Read `discourses/005-kavanot-shacharit/notes.md` and `biur-chasdei-david/HANDOFF.md` first. List these steps in the task list and work through them:

1. **Independent check of the חסדי דוד explanation.**
   - Give each third of `biur-chasdei-david/biur.md` (§1–§8, §9–§16, §17–§24 and the סיכום) to a subagent that has not seen the writing or its notes. It gets the built text and `sources/`, and tries to break every claim about what the קונטרס or a source says: a misread כלל, a wrong number, a reading the words don't bear.
   - Check first the claims listed in `HANDOFF.md`.
   - Don't edit the explanation's meaning. Write the findings to `biur-chasdei-david/check.md` (claim, problem, evidence, how serious) and the open ones to `checks.yaml`. Clear slips (a typo, a wrong address) may be fixed; note each one.
   - Build a review copy: `python scripts/build-biur.py discourses/005-kavanot-shacharit/biur-chasdei-david --pdf --review`. Proof it with skill `proof-pdf`.
2. **Lexicon.** Turn `biur-chasdei-david/notes/terms.md` into entries in `knowledge/lexicon/` (skill `chassidus-context`), each meaning resting on the exact words at an address. `python scripts/lexicon.py --check` must report 0 errors.
3. **Documentation of the new tools.** Add to CLAUDE.md, briefly and in its style:
   - `scripts/grimoar-import.py` (works kept as downloaded HTML);
   - `scripts/reading-pack.py` (a reading pack by address from a plan);
   - the `md: one-file` export;
   - the `.long` / `.keep` print rules of `scripts/build-biur.py` and `templates/biur.css`;
   - the `text_blocks` proof rule.

   Check that `python scripts/source-export.py --check`, `python scripts/grimoar-import.py --check` and `python scripts/reading-pack.py discourses/005-kavanot-shacharit/reading --check` all pass. Rebuild discourse 004's explanation PDF and proof it, to confirm the print changes did not disturb it.
4. **Open questions** in `biur-chasdei-david/notes/open-questions.md`:
   - whether the printed קונטרס goes on beyond (קכ): the transcription ends there;
   - the copyist's references.

   Look only in sources reachable without working around a block (Sefaria, Wikisource, archive.org). Record what you find. Don't change the explanation.
5. **Hand over.**
   - Commit and push.
   - Send me the review PDF.
   - Report in plain English: what the check found (the serious points first), what you fixed, and what waits for me.

Ask me before merging into `main`, opening a pull request, or publishing anything.
