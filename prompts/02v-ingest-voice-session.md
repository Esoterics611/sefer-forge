# START PROMPT — INGEST VOICE-ONLY SESSION (a spoken shiur, no photos)

Use this for discourses with `type: voice-only` in `meta.yaml` (e.g. `002-shaar-hayichud`).
One session = one recorded shiur → one `transcript.md` → one chapter (new page) in the book.

**Before pasting** (on your machine, from the repo root):
1. `./scripts/new-session.sh <slug>` → creates the next `discourses/NNN-<slug>/sessions/MMM/`
2. Drop the `.m4a` into `sessions/MMM/voicenotes/`
3. `python scripts/transcribe.py discourses/NNN-<slug>/sessions/MMM` (Claude can start it in the background; an interrupted run resumes)
   → writes `.raw.txt` (Whisper) **and** `.fixed.txt` (recurring fixes from `glossary/whisper-fixes.yaml` already applied)
4. Commit + push if you'll run Claude in the cloud.

Or just say: **"ingest voice session discourses/NNN-<slug>/sessions/MMM"** — the `ingest-voice-session` skill loads this prompt.

---

> Ingest voice-only session `<SESSION_PATH>`.
>
> **Read only:** `prompts/transcript-review-rules.md` (first — it governs every change to Whisper's text); the session's `voicenotes/*.fixed.txt` and `*.timed.txt`; the `transcript.md` of the most recent *previous* session (style reference only — shape, rhythm, footnotes; don't absorb its content); `glossary/whisper-fixes.yaml`. Nothing else is needed. No build scripts to write — the book is rendered by pandoc.
>
> **Step 1 — Fixes report.** Run `python scripts/apply-fixes.py <SESSION_PATH>` (regenerates `.fixed.txt` if the raw text exists but the fixed one doesn't) and keep its output: the `auto` fixes are done; every `review` hit must be decided from context during cleanup.
>
> **Step 2 — Write `<SESSION_PATH>/transcript.md`.**
> YAML frontmatter (valid YAML — escape `"` inside double-quoted values as `\"`, e.g. `חב\"ד`):
> `title` (e.g. `"שער היחוד — פרק ד'"` — becomes the chapter heading in the book), `subtitle`, `discourse`, `session`, `date`, `source: "voicenotes/<file>.m4a"`, `language: he`, `note` (one line listing **every** correction you made beyond the auto fixes: `raw→fixed; raw→fixed; …`).
>
> Hebrew body:
> - The **full** shiur, in the speaker's voice. Never summarize, reorder, smooth, or translate.
> - Paragraphs at meaning/topic shifts, not per sentence. `##` headings at natural topic boundaries (they become sub-headings in the book).
> - Quotations from the text being taught (ר' הלל / אדמו"ר האמצעי) → blockquotes `>`. Pesukim and short citations → straight quotes `"..."`.
> - Source citations as markdown footnotes: `[^1]` inline, definitions at the very end (`[^1]: מסכת סוכה כח ע"ב.`). Numbering restarts per session — the build keeps them unique.
> - Fix Whisper errors: decide every `review` hit; fix homophones, word-boundary splits/merges, mangled Aramaic and pesukim, abbreviations (`הנל`→`הנ"ל`) — each only where the review rules allow it.
> - Foreign-language engine noise (Russian/Spanish fragments) and lost audio → `<!-- UNCLEAR mm:ss: inaudible -->`; never reconstruct it. Uncertain words → keep Whisper's text and flag `<!-- UNCLEAR mm:ss: <whisper> → <best guess> -->`, time from `.timed.txt`. Never invent.
> - Preserve `[...]{.underline}` and `...` snapshot markers verbatim if present.
>
> **Step 3 — Double read-through** (the step most often skipped and most often regretted).
> Pass 1: every sentence — wrong words that "look right" but make no sense in context, half-cleaned phrases, missed terms.
> Pass 2: remove meaningless leftovers, dittographies, dangling fragments. Check term consistency against earlier sessions (`מוחין` not `מוכין`, `זעיר אנפין` not `ז"א` unless spoken so). Update `note:` for both passes.
> Then run `python scripts/transcript-diff.py <SESSION_PATH>`, read `<SESSION_PATH>/review.md`, and revert every change the rules do not allow. Re-run until it is clean. Then `python scripts/check-session.py <SESSION_PATH>` must report no errors (frontmatter, footnotes, Added count, UNCLEAR times).
>
> **Step 4 — Grow the glossary.** For each correction that is a *recurring* Whisper habit (not a one-off), add it to `glossary/whisper-fixes.yaml`: under `auto:` only if the wrong form is never a real word in these shiurim, otherwise under `review:`. Discourse-specific terms can go in `discourses/NNN-<slug>/whisper-fixes.yaml`.
>
> **Step 5 — Build and verify.**
> Run `bash scripts/build-all.sh <book>` (the book whose `structure.yaml` lists this discourse; `ls books/`). It re-assembles `discourse.md` automatically. Report: pandoc warnings verbatim, output path + size, and confirm the new lesson's title appears in `compiled/<book>.md`.
>
> **Hard constraints:** Hebrew stays Hebrew. Never edit `.raw.txt`, audio, `compiled/`, or `output/`. Do not invoke docx/pptx/xlsx skills. Do not hand-edit `discourse.md` of a voice-only discourse — it is regenerated; edit `transcript.md`. Don't overwrite an existing `transcript.md` that already has body content — ask first.
>
> End with one message: transcript path, output path, count of auto fixes / review decisions / glossary additions, the counts line from `review.md` with every Added entry and its reason, and any `UNCLEAR` spots (with times) for me to listen to.
