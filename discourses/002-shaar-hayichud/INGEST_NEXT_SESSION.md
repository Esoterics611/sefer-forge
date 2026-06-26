# Ingest next session — שער הייחוד (paste-as-prompt)

Save this template for the next session of שער הייחוד. To use, replace
`<NNN>` and `<voicenote-name>.m4a.raw.txt` and paste into Claude Code.

---

```
RAW_PATH = C:\code\sefer-forge\discourses\002-shaar-hayichud\sessions\<NNN>\voicenotes\<voicenote-name>.m4a.raw.txt

═══════════════════════════════════════════════════════════════════════
STOP. READ THIS BLOCK BEFORE ANY OTHER ACTION.
═══════════════════════════════════════════════════════════════════════

Before each Read / Glob / Grep call, ask: "Is the target on the allowed
list below?" If NO, do not call the tool. If unsure, ASK the user.

ALLOWED reads (only these):
  1. RAW_PATH itself.
  2. The single most-recent sessions/<earlier-NNN>/transcript.md as a
     style reference (one file).
  3. discourses/002-shaar-hayichud/sessions/010/build.py — the ONLY
     build script you may consult, for RTL/footnote OOXML primitives.

FORBIDDEN reads — these are CONTEXT POISON:
  ✗ discourses/002-shaar-hayichud/build.py                ← most common trap
  ✗ Any sessions/<other-NNN>/build.py
  ✗ Any session's transcript.md beyond the single style reference
  ✗ Anything in discourses/002-shaar-hayichud/output/
  ✗ Anything outside discourses/002-shaar-hayichud/
  ✗ The existing introduction.md (do not absorb its content)

The discourse-level build.py contains text from prior sessions; reading
it pollutes your context with stale output and biases the new build.
You will be tempted because "I just want to see what already exists" —
DO NOT. Write the new build.py from scratch using only session 010's
primitives. If the file already exists, OVERWRITE it without reading.

═══════════════════════════════════════════════════════════════════════

Process this new session of שער הייחוד and update the cumulative
Hebrew Word document, following exactly the pipeline established in
session 010.

Step 1 — locate, plan, confirm
  - From RAW_PATH derive <NNN> (session folder) and confirm the .m4a
    sits alongside the .raw.txt under sessions/<NNN>/voicenotes/.
  - Read the raw transcript.
  - Read the chosen style-reference transcript.md (most recent prior
    session) — for frontmatter shape / paragraph rhythm / footnote
    convention only. Do NOT absorb its content.
  - Read sessions/010/build.py — for RTL/footnote XML helpers and
    parsing logic only. Do NOT import; copy primitives.
  - Use TodoWrite. Show the plan in a single message before writing.

Step 2 — build sessions/<NNN>/transcript.md
  YAML frontmatter:
    title, subtitle, discourse: 002-shaar-hayichud, session: <NNN>,
    date, source: voicenotes/<filename>.m4a, language: he,
    note: list EVERY Whisper word-correction made (one comma-
    separated line).

  Hebrew body:
    - Paragraphs by meaning/topic shift, NOT by sentence.
    - Source quotations (R' Hillel / Mitteler Rebbe) → blockquotes (>).
    - Pesukim and short citations → straight quotes "...".
    - Section headings (##) at natural meaning-chunk boundaries.
    - Apply Whisper word-error corrections. Common ones:
        אורן סוף → אור אין סוף
        מוכין → מוחין
        זרן פין → זעיר אנפין
        הקדשבורח → הקב"ה
        סכל → שכל
        מוסכל / מוסקל → מושכל
        פתימיות / פתימאיות → פנימיות
        פכינה → בחינה
        נביאה / נביאת → נביעה / נביעת
        אתיק → עתיק
        אורח / עורך → אורך
        מבער / מבייר → מבאר
        ביירנו → ביארנו
        בעלמה → בעלמא
        שער הנון → שער הנו"ן
        העמקת הדת → העמקת הדעת
        דרהר → דערהֶר
        ככ ידוע / כרגוע → כידוע
        אלמין / ענמין / העמים → עלמין
        ממה לכל / ממהל כל → ממלא כל
        שמדנות → שם אדנות
        התאבות → התהוות
        הזור → הזוהר
        הסחל / הסכת / הסכס → השכל
        הבכן / הבעד / הבועד → הב"כן (or הבינה / חכמה ובינה
                                       depending on context)
      Extend as needed; list EVERY actual correction in the note.
    - Light bridging / elaboration ONLY when strictly faithful.
    - Genuinely lost audio → <!-- UNCLEAR: ... --> with best-guess
      context. Never silently invent.

    SOURCE CITATIONS AS FOOTNOTES:
      Inline marker: [^N]  (numeric, in order of first appearance)
      Definitions block at the very end of the file:
        [^1]: מסכת סוכה כח ע"ב.
        [^2]: ישעיה יא:ט.
        ...

  CRITICAL DOUBLE READ-THROUGH BEFORE PROCEEDING TO STEP 3:
    Pass 1: Read every sentence. Fix:
      - Broken sentences with wrong words.
      - Words that look right but make no sense in context (Whisper
        homophones — e.g. "מסעסמה" should be "סיסמה"; "אום כדקולה"
        should be "עומקא דכולא"; etc).
      - Half-cleaned phrases where Whisper substituted a foreign-
        language word (Russian/Spanish snippets) — drop the noise and
        reconstruct from surrounding Hebrew.
    Pass 2: Re-read again. Remove:
      - Meaningless leftover words (artifacts I "preserved" that don't
        actually mean anything in context).
      - Dittographies (the Hebrew equivalent of "ועד זה ועד זה").
      - Dangling sentence fragments where I didn't notice the
        speaker's sentence wasn't complete.
    Update the `note:` field to reflect every correction made in both
    passes.

Step 3 — overwrite discourses/002-shaar-hayichud/build.py
  Whether or not the file exists, you are creating a fresh one from
  session 010's primitives. DO NOT READ the existing file. The new
  build.py MUST:
    - Walk discourses/002-shaar-hayichud/sessions/*/transcript.md in
      numeric order (no hard-coded session list).
    - For each session: emit title (frontmatter), subtitle, then
      parsed blocks (h2, quote, para). Page-break between sessions.
    - Maintain a SINGLE running global footnote counter; each
      session's local [^N] is renumbered to a unique global ID.
    - Output: discourses/002-shaar-hayichud/output/shaar-hayichud-he.docx
      (cumulative — overwritten each run).
    - Page setup: A4 (29.7×21.0 cm), 2.5cm margins all around.
    - RTL on section, every paragraph, every run.
    - David font everywhere. 30pt title / 16pt headings / 13pt body.
    - Body: justified, line-spacing 1.7, 0.8cm first-line indent.
    - Blockquote: justified, line-spacing 1.5, 1cm side indents,
      italic.
    - Footnotes via direct OOXML — same approach as session 010
      (parse_xml + StoryPart + relate_to FOOTNOTES;
      <w:footnoteReference w:id="N"/>).
    - DO NOT import any other build-*.py.
    - DO NOT invoke docx/pptx/xlsx skills (per CLAUDE.md).

Step 4 — run & verify
  - Run `python build.py` from discourses/002-shaar-hayichud/.
  - Confirm the .docx exists; report path + size.
  - Spot-check that footnote IDs run consecutively across the entire
    document (extract footnotes.xml and document.xml from the .docx;
    verify every <w:footnoteReference> has a matching <w:footnote>
    and that IDs are 1..N with no gaps).

Hard constraints
  - Hebrew stays Hebrew. Never translate.
  - Preserve [...]{.underline} and ... snapshot markers verbatim.
  - Do NOT auto-overwrite a transcript.md that already has body
    content beyond the frontmatter skeleton.
  - Do NOT hand-edit anything in output/.
```

---

## What changed since last time

After session 012 was processed, the prompt was strengthened with:

1. **Top-of-prompt STOP block** — the allowed/forbidden read lists are
   now the first thing in the prompt, before any "read" instruction.
   Previously they sat midway through and were ignored.

2. **Specific call-out of `discourses/002-shaar-hayichud/build.py`**
   as the most common context-poison trap, with explanation of *why*
   it's tempting and *why* it must be overwritten not read.

3. **"Critical double read-through" sub-step** inside Step 2,
   explicitly listing the failure modes from session 012 — homophone
   substitutions, foreign-language stutters, dittographies, dangling
   fragments, meaningless leftovers.

4. **Pre-flight checklist** — every Read/Glob/Grep call must be
   verified against the allowed list first.

5. **Expanded common-corrections list** to capture the new word-fixes
   discovered while cleaning session 012 (ממלא, עלמין, התהוות, אדנות,
   etc).

6. **Footnote-IDs spot-check** in Step 4 is now a concrete extraction
   procedure rather than a vague "spot-check".
