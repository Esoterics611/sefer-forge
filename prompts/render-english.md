# Rendering shiurim in English, for narrated episodes

Ronnie's shiurim (a voice-only discourse such as `discourses/002-shaar-hayichud`)
become English episodes on the YouTube channel: an English rendering beside
each part's Hebrew, a narration plan that reads a few parts as one episode
(about 40 minutes), Ronnie's approval, then the usual build and publishing.
It continues as sessions are added: `python scripts/narration-status.py`
says how far each discourse has got and the next step.

## The pipeline, per discourse

1. **A new shiur** is ingested as always (`prompts/02v-ingest-voice-session.md`):
   `sessions/<MMM>/transcript.md`, cleaned and checked.
2. **Status**: `python scripts/narration-status.py [discourse]` lists each part
   (the introduction when `meta.yaml` has `intro:`, standing for its
   `skip_sessions:`; then each other session) with its English (missing,
   current, STALE) and its episode, and says what to do next.
3. **Render** each missing part (rules below) into `transcript-en.md` beside
   `transcript.md` (`introduction-en.md` beside `introduction.md`), with:
   ```yaml
   ---
   title: "The Gate of Unity: Chapter 2"
   language: en
   rendered_from: sessions/011/transcript.md     # relative to the discourse
   source_sha256: <first 16 hex of sha256 of that file>
   rules: prompts/render-english.md
   ---
   ```
   The fingerprint marks the English STALE when the Hebrew changes later
   (a correction): bring the English up to date, then set the new one.
4. **Episode**: add the part to the discourse's next plan
   (`booklets/narration/<name>.yaml`, copy `the-gate-of-unity-part-one.yaml`):
   `parts:` in reading order, until about 7,000 words (40 minutes); then
   start the next plan ("…, Part Two"). Its `series:`, `subtitle:`, `about:`,
   `tags:` and `hashtags:` carry the series; its playlist is the series'.
5. **Pronunciation** (critical): `--names` lists every capitalised word as the
   voice says it; check the lowercase Hebrew terms too (hitbonenut, iyun,
   mochin…). Every Hebrew term goes in `booklets/narration/say-en.yaml`
   ("Chassidus and Kabbalah"), shared by every episode, checked with `--say`.
   Write each respelling as one word, without hyphens (`Hasiddus`, not
   `Hah-see-dus`): a hyphen makes the voice stress every syllable, which
   sounds slow and foreign; `--say` should show one stress mark (ˈ) per word.
   Then make a sample of the new terms and the episode's opening and send
   them to Ronnie to hear. Speed: 1.1 (Ronnie's choice, 2026-11-03).
6. **Approval**: Ronnie reads the English and hears the samples. Only then
   `approved: <date>` in the plan; the full build refuses a plan of `parts:`
   without it.
7. **Build and publish**: `python scripts/build-narration.py
   booklets/narration/<name>.yaml` (about 40 minutes of audio takes a while:
   run it in the background), look at `frame.png`, then
   `python scripts/youtube-publish.py publish <name>`, and review it on
   YouTube as every video is (`docs/youtube-publishing.md`).

## Rendering rules

- **Faithful**: what Ronnie said, in order, in clear written English. No
  additions, no new explanations, no sources he did not give. Spoken
  repetitions and false starts may be smoothed; ideas are never dropped.
  Where the Hebrew is unclear, follow the corrected text (`discourse.md`
  applies the transcript's `edits:`); never guess past an `UNCLEAR`.
- **The text being taught** (the `>` lines: Shaar HaYichud and its
  commentary) is rendered as quotation, also `>`, introduced as the shiur
  introduces it ("The text reads:", "The Rebbe continues:").
- **Hebrew terms**: the term in transliteration, glossed once at first use
  ("contemplation, hitbonenut"; "Chochmah, Binah and Da'at, wisdom,
  understanding and knowledge"), then either. Chabad spellings: Chochmah,
  Binah, Da'at, Chassidus, Atzilut, Beriah, Yetzirah, Asiyah, Malchut,
  Keter, Atik, mochin, sefirot, kuntres. Verses in English, as said.
- **Titles**: each "## " section is a chapter of the video, a short English
  title of what it says. No footnotes (they are not read).
- **No brackets** in what is read: the build stops on one.
- Hebrew stays Hebrew everywhere else in the repo; this English is made only
  because Ronnie asked for English episodes.
