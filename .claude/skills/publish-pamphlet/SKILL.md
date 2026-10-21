---
name: publish-pamphlet
description: Print one session, or a whole discourse, as a standalone A5 pamphlet PDF (cover, נוסח, key points, framed ביאור boxes). Use when the user says "pamphlet", "standalone", "publish session N on its own", or "print the whole discourse as a booklet". Argument - a session path (discourses/003-breishis/sessions/002) or a discourse path (discourses/003-breishis).
---

1. Run `python scripts/build-pamphlet.py $ARGUMENTS --png`.
   - A session prints from its `section.md` / `transcript.md`; a discourse from its
     `discourse.md`. An images+voice discourse must be assembled first
     (`prompts/03-assemble-discourse.md`); the script says so if it is not.
2. Proof it by the `proof-pdf` skill: `python scripts/proof-pdf.py output/pamphlets/<name>.pdf`
   with no errors, then every spread read against `docs/print-standard.md`. Layout
   changes go in `templates/pamphlet.css`, never in the HTML or the PDF. Rebuild and
   re-proof until clean.
3. Cover text comes from the book that lists the discourse, overridden by the
   `pamphlet:` block in the discourse's `meta.yaml` (series, author, date, title,
   subtitle, dedication). If the cover is missing a line, ask for it there.
4. Report: the PDF path and page count, the proof summary line and the visual findings,
   and every `note:` line the build printed (unfinished ingest, UNCLEAR flags still in
   the text). A pamphlet with UNCLEAR flags is a proof, not a print copy: say so.
