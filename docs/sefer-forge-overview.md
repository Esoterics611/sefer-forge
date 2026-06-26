# sefer-forge: AI-Augmented Torah Publishing — and Where It's Going

*An invitation to AI enthusiasts and Torah learners*

---

## The Problem We're Solving

A Torah teacher sits with a sefer. He marks it up, reads it aloud, thinks out loud into a voice memo. Over weeks and months, those sessions accumulate into a genuine discourse — a piece of Torah scholarship that belongs in a book.

But the gap between "raw learning session" and "publishable chapter" has always required enormous editorial labor: transcription, OCR, cleanup, structuring, layout. Most of it never makes it to print.

**sefer-forge closes that gap.**

---

## What It Is

sefer-forge is a local-first, AI-augmented publishing pipeline. It turns:

- **Photos of book pages** (any sefer, any print quality)
- **A Hebrew voice memo** (the teacher's oral commentary, recorded on a phone)

...into a structured, typeset, print-ready chapter — session by session, discourse by discourse, book by book.

The AI doesn't replace the teacher. It does the mechanical work between *learning* and *publishing*.

---

## How the Pipeline Works

```
[Book page photos]   →   OCR (Claude vision)  ─────────────────────┐
                                                                     ↓
[Hebrew voice memo]  →   Whisper (local STT)  →   AI cleanup   →   section.md
                              ↑
                     runs fully on your machine
                     (no data leaves the room)
```

Then:

```
N sessions  →  assemble-discourse  →  discourse.md
N discourses →  compile + pandoc   →  book.docx
```

### The three artifacts per session

Every ingestion session produces three markdown files:

1. **`ocr.md`** — full Hebrew OCR of the page photos, with underlines and snapshot markers preserved, unclear passages flagged (never guessed)
2. **`commentary.md`** — the voice memo cleaned up: fillers removed, transcription errors corrected against the OCR'd source text, the speaker's voice preserved
3. **`section.md`** — the session output: the source text, key-point anchors, and commentary boxes woven together in a structured layout ready for the book

These are plain markdown. The author can read, edit, and approve every line before anything gets assembled.

### The unit hierarchy

| Unit | What it is |
|---|---|
| **Session** | One batch: N page photos + one voice memo |
| **Discourse** | 1–N sessions woven into a coherent essay |
| **Chapter** | 1–N discourses assigned in a book structure file |
| **Book** | Compiled markdown → pandoc → `.docx` (with Hebrew RTL support) |

### Key technology choices

- **Claude Code** — drives the AI work: OCR, transcript cleanup, assembly. All via a local CLI session; no cloud upload of the raw content unless you choose it.
- **Whisper (OpenAI, open-source)** — local speech-to-text for Hebrew. Runs on your machine. First run downloads ~1.4 GB; no API key, no data sent anywhere.
- **Pandoc** — renders the final markdown to a properly typeset Word document with Hebrew RTL layout.
- **Git** — every session is a commit. Provenance is structural, not an afterthought.

---

## Human in the Loop, Always

This is not an autonomous system. The design is deliberate:

- Claude **proposes**; the author **approves**.
- Raw source files (audio, images) are never modified.
- `discourse.md` — where the real editorial voice lives — is **never auto-overwritten** once the author has started working in it.
- Every artifact is plain text. No proprietary formats. Nothing is locked in.

The teacher controls the sefer. The AI handles the labor.

---

## Where This Is Going — The Chayolei DAO Connection

sefer-forge is the **content production layer** of a larger vision. The natural partner is the **Chayolei DAO** model: a system for tracking contributions, assigning attribution, and distributing recognition across a network of collaborators.

Torah publishing has always been collaborative — editors, printers, proofreaders, patrons. The tooling has never reflected that reality. We're building toward a world where it does.

### Phase 1 — Smooth the solo workflow (near-term)
- Inline transcription (no manual script step)
- Auto file-watching: drop files into the session folder, ingest begins automatically
- Auto-commit with structured metadata per session

### Phase 2 — Multi-session intelligence
- Cross-session memory: the AI knows the full discourse corpus and flags when a new session revisits a concept from months ago
- Structured glossary: named entities (Rebbes, texts, concepts) accumulate into a searchable index
- Source library: a living index of sefarim referenced across all discourses

### Phase 3 — Multi-contributor model (sefer-forge × Chayolei DAO)

This is where the two projects converge:

- Each contributor (transcriber, editor, reviewer, typesetter) submits signed work via git
- Contributions are tracked at the session / discourse / chapter level in a structured ledger
- Attribution tokens assigned per contribution — who OCR'd page 12, who cleaned the voicenote, who approved the final discourse
- The book's provenance is fully auditable, end to end

Chayolei built the contribution accounting layer. sefer-forge is the content production layer. Together they make it possible to publish a book the same way open-source builds software: distributed, attributed, verifiable.

### Phase 4 — Collaborative authorship at scale
- Multiple teachers → multiple discourse streams → single structured book
- Editors merge discourse branches via pull request (with AI reviewing for consistency)
- Scheduled agents run nightly builds and post diffs to a review channel
- Any contributor with git access can propose a session, a correction, or a discourse

---

## The Deeper Point

Most Torah scholarship that happens in the world — at a shtender, in a shiur, in a rebbe's room — never makes it to a book. The barrier isn't the ideas; it's the production work.

AI changes the ratio. A teacher who records a voice memo after learning can, with a small amount of setup, watch that memo become a typeset chapter. A network of contributors can build a book the same way a team builds software.

sefer-forge is the first working piece of that infrastructure. The pipeline runs today, on real content, in a real git repository.

---

## What We're Looking For

**If you are an AI engineer or tools builder:**
- We're close to wiring in an MCP Whisper server so transcription happens inline — want to help build that?
- A lightweight file-watcher MCP that auto-triggers ingest on file drop would remove a manual step
- The contribution metadata schema (per-session `contributors.yaml`) needs design work

**If you are a Torah learner, teacher, or editor:**
- Have a sefer you're learning? Have a voice memo? That's a session. We can run the pipeline together.
- Know a Torah teacher who is sitting on years of recordings? This was built for exactly that situation.
- Interested in editing or reviewing discourses? Git-based review workflows are already there.

**If you are interested in decentralized attribution and DAO infrastructure:**
- The Chayolei integration design is an open question — what does "contribution accounting for Torah publishing" actually look like?
- We're thinking about it in terms of git provenance + a structured ledger. Come think with us.

---

## Design Principles

1. **Local-first** — no content leaves the machine unless the author chooses it. Whisper runs locally. Git is the transport.
2. **Human in the loop at every stage** — the AI proposes, the author approves. No auto-overwrite of the editorial layer.
3. **Plain text as the substrate** — every artifact is markdown. No proprietary formats. Pandoc renders; everything else is portable.
4. **Attribution by design** — every session is a git commit. Provenance is structural, not an afterthought.
5. **The sefer is sovereign** — the teacher's voice and the source text are preserved exactly. The AI does not interpret; it transcribes, structures, and presents.

---

*sefer-forge is open and in active development. Reach out if any of this resonates.*
