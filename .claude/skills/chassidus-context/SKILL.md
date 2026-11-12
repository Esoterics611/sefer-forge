---
name: chassidus-context
description: Load what the repo already understands of a Chassidus or Kabbalah text before working on it, and add what was learned after - the lexicon of terms (knowledge/lexicon/, each meaning resting on exact words in sources/), checked by script. Use before explaining a text, writing a ביאור, planning a teaching pass, helping draft or write Chassidus, checking what the teacher recorded, or answering what a term means; and at the end of such work to add the terms it met. Also when the user says "lexicon", "knowledge layer", "what does X mean here", "add to the lexicon". Argument - a file or a term.
---

The layer is described in `knowledge/README.md`; today it holds the lexicon.

## Before the work

1. `python scripts/lexicon.py --in <the text's file>` (an `ocr.md`, a `transcript.md`, a pasted text saved
   to a file): the known terms the text uses.
2. For each term that matters to the task, `python scripts/lexicon.py <term>`: its meanings, each with its
   source quoted in context. Read the `caution:` and `open:` lines: they say where readers go wrong and
   what is not settled.
3. Treat a `draft` entry as Claude's reading with checked quotations, not as settled. If the text uses the
   term in a sense the entry lacks, that is a new sense, not a reason to stretch the old one.
4. Anything the entry does not cover is looked up in `sources/` (`scripts/source-lookup.py --find`), never
   answered from memory.

## After the work

1. Add each term the work had to explain and the lexicon lacks: a new `knowledge/lexicon/<slug>.yaml`
   (format in `knowledge/README.md`), its meaning in Hebrew, resting on the exact words at an address found
   with `source-lookup.py`. A source outside `sources/` goes in as `cite:`; an unsettled point under `open:`.
2. Correct an entry the work showed to be wrong or narrow: a new sense or a `caution:`, with its source.
3. What the teacher said of a term goes under `teacher:` with the session it comes from, never into the
   meaning.
4. `python scripts/lexicon.py --check` until it reports 0 errors (it rewrites `knowledge/lexicon/INDEX.md`).
   Every quote must be found at its address; a miss means the words or the address are wrong; fix them, do
   not drop the check.
5. `status: checked` only after the meaning was read against the sources by the teacher or by a subagent
   that did not see the writer's reasoning.
