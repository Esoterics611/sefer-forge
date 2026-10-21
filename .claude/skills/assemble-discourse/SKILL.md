---
name: assemble-discourse
description: Join a discourse's finished sessions into discourse.md and list cross-session issues for polishing. Use when the user says "assemble discourse", "put the sessions together", or a discourse's sessions are all done. Argument - the discourse path, e.g. discourses/003-breishis.
---

First run `python scripts/session-status.py $ARGUMENTS` and name any session that is not
done: assembling skips nothing, so an unfinished session goes in as it is. Ask before
going on if one is unfinished.

Then follow `prompts/03-assemble-discourse.md` exactly, with `<DISCOURSE_PATH>` = `$ARGUMENTS`.
