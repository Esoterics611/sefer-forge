# discourses/

Each discourse is a folder `NNN-<slug>/` containing:

```
NNN-<slug>/
├── meta.yaml           # title, status (draft|ready|published), type (images+voice|voice-only), chapter
├── notes.md            # your personal notes (sources, ideas)
├── discourse.md        # polished assembly of all sessions — hand-edit freely
└── sessions/
    ├── 001/
    │   ├── images/              # book page photos you captured
    │   ├── voicenotes/          # .m4a + .raw.txt (Whisper) + .fixed.txt (glossary fixes, regenerated)
    │   ├── ocr.md               # Claude's OCR of the images (NEVER edit)
    │   ├── commentary.md        # cleaned voicenote (editable)
    │   └── section.md           # session output: frontmatter + paired spreads (source chunk / voicenote commentary / underlined terms footer)
    ├── 002/
    └── ...
```

### Voice-only discourses (`type: voice-only`)

Each session holds just `voicenotes/` + `transcript.md` (one recorded shiur).
`discourse.md` is **generated** on every build from the transcripts — edit
`transcript.md`, not `discourse.md`. Optional `meta.yaml` keys:

```yaml
intro: introduction.md          # placed first (its frontmatter title → heading)
skip_sessions: ["000", "001"]   # sessions left out of the book
```

## Lifecycle

- `status: draft` — actively ingesting sessions
- `status: ready` — assembled, polished, ready to be placed in a chapter
- `status: published` — included in a compiled book

## Commands

```bash
./scripts/new-discourse.sh my-slug [--voice-only]      # create a new discourse
./scripts/new-session.sh my-slug                       # add next session
python scripts/transcribe.py discourses/001-my-slug/sessions/001
python scripts/assemble-discourse.py discourses/001-my-slug
```
