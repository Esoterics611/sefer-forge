# Agentic and autonomous development

How the work in this repo gets done by an AI agent (Claude Code), what keeps
that work trustworthy, and the next steps toward running it on its own.

## The idea

**Agentic** here means: you name the goal ("ingest session 3", "proof the
pamphlet", "fix the old transcripts"), and Claude Code carries out every step
itself: it reads the photos, runs the scripts, writes the files, checks its
own work, rebuilds, and reports. You supply the sources, make the decisions
only you can make, and accept or reject the result.

**Autonomous** means the same work starts without a request: a new recording
appears, or a schedule fires, and the agent advances everything it safely can,
stopping at the points that need you.

What makes either possible is that the knowledge lives in the repo, not in
anyone's head or in one chat:

| Where | What it holds |
|---|---|
| `CLAUDE.md` | The rules every session follows: what may never be edited, the file formats, which skill answers which request |
| `prompts/` | The full procedures (ingest a photo session, a voice session; the transcript review rules; the readability pass) |
| `.claude/skills/` | One skill per workflow, each a short recipe that points at the procedure and the scripts |
| `scripts/` | The deterministic work and the checks: transcription, OCR strips, matching, building, proofing, status |
| `.claude/settings.json` | A hook that runs `check-session.py` after every edit of a session file |
| `docs/print-standard.md` | What a finished page must look like, and the proof every PDF passes |
| `docs/backlog.md` | Work found and deliberately deferred, with how to do it |
| Claude's memory | Standing preferences learned from you (the paired layout, the author's name) |

## The workflows today

### One session, from recording to accepted pamphlet

```
photos + recording
      │
      ▼
 new-session ──► transcribe.py (GPU, in the background, resumable)
      │                     │
      ▼                     ▼
 ocr-session          .raw.txt + .timed.txt ──► apply-fixes (glossary) ──► .fixed.txt
 (strip by strip,           │
  line count,               ▼
  second pass)     ocr-match: which printed words the speaker read, and where
      │                     │
      └────────► cleanup under the review rules ──► commentary.md / transcript.md
                            │                         transcript-diff: every changed word
                            ▼
                 section-plan.yaml ──► build-section.py ──► section.md (paired)
                            │
                            ▼
              build-pamphlet.py ──► proof-pdf.py + visual review ──► readability pass
                            │                                         (edits:)
                            ▼
                      style pass: the spoken Hebrew made written (style:)
                            │
                            ▼
                    you: acceptance
```

| Workflow | Say | Skill | Main scripts | Produces | Stops for you when |
|---|---|---|---|---|---|
| Where things stand | "status", "what's next" | `session-status` | `session-status.py` | each session's next step | never |
| New session | "new session" + files | `new-session` | `new-session.sh`, `transcribe.py` | folder, Whisper started | files are missing |
| OCR | "OCR" | `ocr-session` | `ocr-strips.py`, `ocr-match.py` | `ocr.md`, `ocr-match.md` | text cannot be read (flagged) |
| Photo session | "ingest session" | `ingest-session` | all of the above, `build-section.py` | `commentary.md`, `section.md`, pamphlet | always, at acceptance |
| Recorded shiur | "ingest voice session" | `ingest-voice-session` | `transcribe.py`, `transcript-diff.py` | `transcript.md`, the book | always, at acceptance |
| Paired layout | "text on top, explanation below" | `paired-layout` | `build-section.py`, `build-pamphlet.py` | paired pages | at acceptance |
| Pamphlet | "pamphlet", "publish session N" | `publish-pamphlet` | `build-pamphlet.py` | A5 PDF | at acceptance |
| Proof | "proof", before any hand-over | `proof-pdf` | `proof-pdf.py` | proof report, spread images | at acceptance |
| Readability pass | "words that don't make sense" | (prompt) | the plan's or transcript's `edits:` | cleaner print | a segment longer than a sentence |
| Style pass (last) | "less conversational" | (prompt `style-pass.md`) | the plan's or transcript's `style:` | written, not spoken, Hebrew | a rewrite that would change a claim |
| Discourse | "assemble discourse" | `assemble-discourse` | `assemble-discourse.py` | `discourse.md` | before overwriting hand edits |
| Chapter | "add to chapter" | `assign-chapter` | `structure.yaml` | the book's order | the placement is yours |
| Book | "build book" | `build-book` | `build-all.sh`, `docx-to-pdf.sh` | DOCX and PDF | at acceptance |
| Glossary | "grow the glossary" | `grow-glossary` | `glossary-candidates.py` | `whisper-fixes.yaml` entries | each proposal |

Every workflow resumes after a crash or a restart: the session's files show
how far it got, and `session-status.py` names the next step.

## What keeps the work trustworthy

The agent cannot hear the recording, and it can misread a photo. The
process is built so that its mistakes show up rather than hide:

- **Evidence, not invention.** A transcript changes only under
  `prompts/transcript-review-rules.md`: every correction needs a source in the
  repo (the OCR, the glossary, a verse being quoted). Anything doubtful stays as
  heard, with an `UNCLEAR` flag and a time for you to re-listen.
  `transcript-diff.py` lists every word changed against Whisper; a word added
  without a rule is an error.
- **Faithful record, separate print decisions.** `commentary.md` and
  `transcript.md` keep what was said. What the printed page corrects, leaves
  out or rewrites from speech into writing is a list of `edits:` and `style:`
  (in the session plan, or the transcript's frontmatter), each one visible and
  reversible; the quoted readings that place each explanation never change.
- **Built files are never hand-edited.** `section.md` is rebuilt from its plan;
  `compiled/` and `output/` from the sources.
- **Checks run by themselves.** The hook runs `check-session.py` after every
  edit of a session; the builders run it too.
- **Nothing is handed over unproofed.** Every PDF passes `proof-pdf.py` (fonts,
  colours, margins, leaks, page numbers) and a page-by-page visual review, then
  the readability pass.
- **Decisions are measured.** A setting changes when a test on real sessions
  shows it is better, and the result is written down (Whisper's model and
  precision, hotwords, VAD: `TRANSCRIPTION.md`).
- **Git stays clean.** Work goes on a branch and reaches `main` through a pull
  request; commits and pushes are under Esoterics611; photos and recordings
  never leave this machine (`.gitignore`).

## Where you decide

The agent stops and asks, rather than acting, for:

- accepting a PDF;
- replacing a source of truth (`*.raw.txt`, a finished `ocr.md`);
- overwriting a hand-edited `discourse.md`;
- a readability fix longer than a sentence, or one that would change the
  argument;
- anything that leaves the machine or cannot be undone: merging to `main`,
  rewriting history, deleting files.

## Running in the background

Long steps already run without anyone watching:

- `transcribe.py` runs detached on the GPU (about 0.9× the recording's
  length), saves each segment as it is heard, and resumes after a crash;
  `session-status.py` shows its progress and time left.
- A Claude Code session can itself run as a background job: it works through
  a request, keeps going while you are away, and ends with a report of what was
  done and what waits for you.

## Next steps: from agentic to autonomous

| Level | Who starts the work | Who checks it | Here |
|---|---|---|---|
| 1. Assisted | you, step by step | you | the start |
| 2. Agentic sessions | you name the goal; the agent runs the whole workflow | scripts, proofs, then you | **now** |
| 3. Event-driven | a new recording or photo starts the session | the same | next |
| 4. Scheduled | a recurring run advances every session whose next step is mechanical | the same; you review pull requests | after that |
| 5. Autonomous with gates | the agent works through new material and the backlog, one pull request per piece | you, at acceptance and in review | the goal |

The concrete steps, in order:

1. **An intake folder.** Recordings and photos land in one gitignored folder
   (synced from the phone). A small `scripts/intake.py` sorts each batch into a
   new session and starts Whisper; the `new-session` skill already describes
   the steps. Because the sources stay on this machine, intake runs here, not
   in the cloud: a scheduled task that calls Claude Code headless
   (`claude -p "check the intake folder"`).
2. **A status-driven runner.** One command reads `session-status.py` and runs
   each session's next step while that step is mechanical (transcribe, match,
   diff, build, print, proof), and stops at the first step that needs judgment
   or you. Run on a schedule, it keeps every session moving.
3. **Checks on GitHub.** A GitHub Action runs `check-session.py` and the book
   build on every pull request. It works without the photos and recordings,
   since every check reads the text files.
4. **Acceptance where you already look.** The pull request for a session links
   a review page with its pamphlet spreads; your comments there come back to
   the agent as the next round of fixes.
5. **A standing quality test.** Keep a few finished sessions (Breishis 001 and
   002) as a fixed test set, and score any change to transcription, OCR or
   cleanup against it before adopting it, as was done for the Whisper settings.
6. **The glossary grows itself.** After each cleaned session, `grow-glossary`
   proposes new Whisper fixes in the same pull request.
7. **Agents in parallel.** OCR and transcript cleanup of one session are
   independent; separate agents in separate worktrees can do them at once, with
   one agent assembling the result.
8. **The backlog burns down on its own.** A scheduled run takes the top item
   of `docs/backlog.md`, does it on a branch, and opens a pull request.

**Limits to keep in view.** The agent cannot hear the audio, so `UNCLEAR`
flags still need your ear. Prompting Whisper with terms produced
plausible-looking wrong text, which is worse than garble; the same risk
applies to any shortcut that makes text look cleaner without evidence. The
machine has 8 GB of memory, so heavy steps run one at a time. And sources stay
local, so anything that needs them runs here.

## Read next

- `README.md`: the quick start.
- `CLAUDE.md`: the rules.
- `prompts/02-ingest-session.md`, `prompts/02v-ingest-voice-session.md`: the
  two main procedures.
- `docs/print-standard.md`: the finished page and the proof.
- `docs/backlog.md`: what is waiting.
