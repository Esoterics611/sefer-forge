# discourses/

Each discourse is a folder `NNN-<slug>/` containing:

```
NNN-<slug>/
├── meta.yaml           # title, status (draft|ready|published), chapter assignment
├── notes.md            # your personal notes (sources, ideas)
├── discourse.md        # polished assembly of all sessions — hand-edit freely
└── sessions/
    ├── 001/
    │   ├── images/              # book page photos you captured
    │   ├── voicenotes/          # .m4a + .raw.txt (Whisper output)
    │   ├── ocr.md               # Claude's OCR of the images (NEVER edit)
    │   ├── commentary.md        # cleaned voicenote (editable)
    │   └── section.md           # session output: frontmatter + paired spreads (source chunk / voicenote commentary / underlined terms footer)
    ├── 002/
    └── ...
```

## Lifecycle

- `status: draft` — actively ingesting sessions
- `status: ready` — assembled, polished, ready to be placed in a chapter
- `status: published` — included in a compiled book

## Commands

```bash
./scripts/new-discourse.sh my-slug                     # create a new discourse
./scripts/new-session.sh my-slug                       # add next session
python scripts/transcribe.py discourses/001-my-slug/sessions/001
python scripts/assemble-discourse.py discourses/001-my-slug
```
