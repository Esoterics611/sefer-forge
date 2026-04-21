# START PROMPT — ASSEMBLE DISCOURSE

Use this once all sessions for a discourse have been ingested and reviewed.

Replace `<DISCOURSE_PATH>` (e.g. `discourses/001-teshuvah-intro`).

---

> Assemble discourse `<DISCOURSE_PATH>`.
>
> 1. Run `python scripts/assemble-discourse.py <DISCOURSE_PATH>`.
>    - If it succeeds, `discourse.md` now contains every session's `section.md` concatenated in order.
>    - If it refuses (because `discourse.md` has hand-edited content), show me the current `discourse.md` body and ask whether to `--force` overwrite or merge manually.
>
> 2. Once assembled, read `<DISCOURSE_PATH>/discourse.md` end to end. List (do NOT edit yet) cross-session issues to address:
>    - Rough transitions between sessions
>    - Repetitions of the same point in different sessions
>    - Continuity gaps (e.g. a topic introduced in one session but dropped)
>    - Places where the order of sessions would flow better if rearranged
>    - Minor copy-editing suggestions in the commentary (not the blockquoted source)
>
> 3. Wait for my approval on specific items, then apply only those edits. Keep the `<!-- session: NNN -->` markers so we can trace content back to its source session.
>
> 4. Update `<DISCOURSE_PATH>/meta.yaml` → set `status: ready`.
>
> 5. Tell me the next step: assign to a chapter via `prompts/04-assign-to-chapter.md`.
