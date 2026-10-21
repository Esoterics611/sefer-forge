---
name: grow-glossary
description: Find Whisper mis-hearings corrected again and again across sessions and propose them for glossary/whisper-fixes.yaml, so later transcripts start cleaner. Use when the user says "grow the glossary", "update whisper fixes", or after several sessions were cleaned.
---

1. Run `python scripts/glossary-candidates.py` (`--min 1` for single corrections too).
2. Sort its candidates into three groups and show them to the user:
   - **mis-hearings** (הסכל → השכל, הנער → הנהר): the point of the glossary. Its
     auto/review suggestion holds: `review` when the wrong form is a real word here.
   - **spelling style** (חוכמה → חכמה, עניין → ענין): the cleanup's spelling, not a
     mis-hearing. Leave out unless the user wants spelling normalized automatically.
   - **one-off or context fixes** (זה → הוא, אז → ואז): never glossary material.
3. On the user's approval, add the chosen entries to `glossary/whisper-fixes.yaml` under
   the right list and section, or to `discourses/<NNN-slug>/whisper-fixes.yaml` when the
   term belongs to one discourse. Never put a real word under `auto:`.
4. Run `python scripts/apply-fixes.py <session>` on the sessions concerned, to confirm
   the new entries fire.
