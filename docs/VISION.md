# sefer-forge — Architecture, Vision & Growth Roadmap

## What Is This, Actually?

sefer-forge is a **local-first, AI-assisted Hebrew publishing pipeline**. A person learns, teaches, or annotates a sacred text. They photograph the pages and leave a Hebrew voicenote with their commentary. The system transforms that raw material — photos + voice — into a structured, typeset book, session by session, discourse by discourse.

It is not a notes app. It is a *production studio* for Torah scholarship.

---

## How the Pipeline Works Today

```
[Book pages] → OCR (Claude vision)
[Hebrew voicenote] → Whisper (local STT) → raw.txt → Claude cleanup
                                              ↓
                                        commentary.md
OCR + commentary → Claude interleave → section.md
N sessions → assemble-discourse.py → discourse.md
N discourses → compile.py + pandoc → book.docx
```

### Whisper
[Whisper](https://github.com/openai/whisper) is OpenAI's open-source speech-to-text model, running **fully locally** on your machine — no API call, no data leaves the room. We use ivrit.ai's Hebrew fine-tune of Whisper large-v3, on the GPU when there is one (see `TRANSCRIPTION.md`). The first run downloads about 3 GB. It produces a `.raw.txt` that Claude then cleans against the OCR'd source text (proper nouns, technical terms, diacritics).

### Claude (via Claude Code)
Claude Code drives the session: it reads images, OCRs the Hebrew, cleans the Whisper transcript, and assembles `section.md`. All outputs are plain markdown — the session is reviewable and editable by the author at every stage.

### Pandoc
`scripts/build-docx.sh` calls pandoc with a Word reference template, producing a properly typeset `.docx` with Hebrew RTL support.

---

## MCP — What It Is, Can We Use It?

**MCP (Model Context Protocol)** is Anthropic's open standard for giving AI assistants structured access to tools and data sources. In Claude Code, MCP servers appear as extra tools Claude can call during a session.

**"mcpo"** likely refers to [mcpo](https://github.com/open-webui/mcpo) — an MCP proxy that wraps any MCP server behind an OpenAI-compatible API, making it usable from non-Claude frontends too.

### What MCP could do for sefer-forge

| Capability | Current | With MCP |
|---|---|---|
| Transcription | `python scripts/transcribe.py` (manual) | MCP Whisper server → Claude calls it inline |
| File watching | Manual drop + tell Claude | MCP filesystem watcher → auto-trigger ingest |
| Git operations | Manual | MCP git server → Claude commits each session automatically |
| Book compilation | Manual script call | MCP build server → Claude triggers pandoc inline |
| Search across discourses | Manual grep | MCP search server → Claude queries the whole corpus |

Concretely, there is an existing **MCP Whisper server** (e.g. `mcp-whisper`) that exposes transcription as a tool. Plugging it into `.claude/mcp.json` would let Claude call transcription directly rather than requiring the user to run a script first — removing the "drop files, then tell me, then I transcribe" step.

---

## Vision: Agentic Production Studio

The current workflow is **human-initiated, Claude-assisted**. The ceiling is much higher.

### Phase 1 — Smooth the current loop (near-term)
- MCP Whisper: transcription happens inline, no manual script step
- File watcher MCP: dropping files into `sessions/NNN/` auto-triggers the ingest agent
- Auto-commit: each completed session gets a signed git commit with structured metadata
- Review UI: lightweight local web viewer of `section.md` before it's locked

### Phase 2 — Multi-session intelligence
- Cross-session reference: Claude knows the whole discourse corpus and can flag when a new session revisits a concept from session 003 two months ago
- Source library: a structured index of sefarim referenced across all discourses
- Glossary extraction: named entities (Rebbes, texts, concepts) accumulated into a `glossary.yaml`

### Phase 3 — Multi-contributor DAO model

This is where sefer-forge connects to the **chayolei** model:

- Each contributor (transcriber, editor, reviewer, typesetter) submits signed work via git
- Contributions are tracked at the session/discourse/chapter level in a structured ledger
- Smart contracts (or a simpler off-chain ledger) assign attribution tokens per contribution
- The book's provenance is fully auditable: who OCR'd page 12, who cleaned the voicenote, who approved the final discourse

This matches exactly what chayolei built for task tracking and reward distribution. sefer-forge is the *content production layer*; chayolei is the *contribution accounting layer*. They belong together.

### Phase 4 — Collaborative authorship at scale
- Multiple teachers → multiple discourse streams → single structured book
- Each teacher has a `contributors/<name>/` subtree
- Editors merge discourse branches via PR (with Claude Code reviewing for consistency)
- A `book/structure.yaml` edited collaboratively assigns discourses to chapters across contributors
- Scheduled agents run nightly builds and post diffs to a review channel

---

## Immediate Next Steps (to track)

- [ ] Add MCP Whisper server to `.claude/mcp.json`
- [ ] Write a file-watcher script (or MCP server) that auto-detects new session drops
- [ ] Define contribution metadata schema (`contributors.yaml` per session)
- [ ] Sketch the chayolei ↔ sefer-forge integration interface
- [ ] Evaluate mcpo as a bridge for non-Claude collaborators using the same pipeline

---

## Key Design Principles to Preserve

1. **Local-first** — no content leaves the machine unless the author chooses. Whisper runs locally. Git is the transport.
2. **Human in the loop at every stage** — Claude proposes, author approves. No auto-overwrite of `discourse.md`.
3. **Plain text as the substrate** — every artifact is markdown. No proprietary formats. Pandoc renders; everything else is portable.
4. **Attribution by design** — every session is a git commit. Provenance is structural, not an afterthought.
