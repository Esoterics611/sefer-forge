---
name: references-pack
description: Before a lesson is recorded, set every source a text cites (Etz Chaim, Pri Etz Chaim, by gate and chapter) under the citation - the passage with lines before and after, the words it refers to highlighted - as one A4 PDF to read from while recording. Use when the user says "bring the Etz Chaim references", "the sources he cites", "references", "sources pack", "before I record", or pastes a text and asks for its sources. Argument - the session path, or the text and the discourse it belongs to.
---

Follow `prompts/references-pack.md`, steps 1–6, for the session `$ARGUMENTS`.

- No session yet: make one (`bash scripts/new-discourse.sh <slug>` if the text starts a
  new discourse, then `bash scripts/new-session.sh <slug>`), and put a pasted text in its
  `ocr.md` under `## Source: <url>` sections, exactly as given.
- Passages come only from `sources/` (`scripts/source-lookup.py`); quote nothing from
  memory. A cited work that is not there is listed under `others:`.
- Step 6, the check against the request, is part of the job: do it before saying the
  PDF is ready, and report its counts and the uncertain boxes when handing it over.
