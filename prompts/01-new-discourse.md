# START PROMPT — NEW DISCOURSE

Use this when you're beginning a new lecture/essay that will become a discourse (later → chapter).

**Before pasting:** decide on a kebab-case slug (e.g. `teshuvah-intro`) and a Hebrew title.

---

Replace `<SLUG>` and `<TITLE>` below, then paste into a fresh Claude Code session at the repo root:

> I'm starting a new discourse.
>
> - Slug: `<SLUG>`
> - Title (Hebrew): `<TITLE>`
>
> Please:
> 1. Run `./scripts/new-discourse.sh <SLUG>` to scaffold the folder.
> 2. Update the new `meta.yaml` → set `title:` to `<TITLE>`.
> 3. Update the new `discourse.md` frontmatter → set `title:` to `<TITLE>`.
> 4. Report the folder path so I can start adding sessions.
