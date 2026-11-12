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
5. **Pronunciation** (critical): the English has no Hebrew terms, only names.
   `--names` lists every capitalised word as the voice says it; a name it says
   badly gets a respelling in `booklets/narration/say-en.yaml`, written as one
   word with one stress (a hyphen makes the voice stress every syllable, slow
   and foreign); `--say` checks it. Then make a sample of the episode's opening
   and send it to Ronnie to hear. Speed: 1.1 (Ronnie's choice, 2026-11-03).
6. **Approval**: Ronnie reads the English and hears the samples. Only then
   `approved: <date>` in the plan; the full build refuses a plan of `parts:`
   without it.
7. **Build and publish**: `python scripts/build-narration.py
   booklets/narration/<name>.yaml` (about 40 minutes of audio takes a while:
   run it in the background), look at `frame.png`, then
   `python scripts/youtube-publish.py publish --extra <name>` (beyond the
   day's two story videos; the quota still holds), and review it on
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
- **Plain English, no transliteration** (Ronnie's decision, 2026-11-03: Hebrew
  words in an English voice sound foreign however they are spelled). Every
  term is translated, always the same way:

  | Hebrew | English |
  |---|---|
  | חכמה, בינה, דעת | Wisdom, Understanding, Knowledge |
  | כתר, מלכות | the Crown, Kingship |
  | עתיק | the Ancient One |
  | אבא ואמא | the Father and the Mother |
  | ישראל סבא ותבונה | Israel the Elder and lower Understanding |
  | זעיר אנפין, לאה | the Small Countenance, Leah |
  | אצילות, בריאה, יצירה, עשייה | the worlds of Emanation, Creation, Formation and Action |
  | עשר ספירות | the ten divine attributes |
  | מוחין | the powers of the mind |
  | נרנח"י | the five levels of the soul (from the soul that gives life to the body up to the single, innermost essence) |
  | התבוננות, עיון | contemplation, study |
  | התפעלות | arousal |
  | קונטרס; שער הייחוד; קונטרס ההתפעלות | treatise; the Gate of Unity; the Treatise on Arousal |
  | חסידות, חסידים | Hasidic teaching, the Hasidim |
  | גמרא; שולחן ערוך; ספר יצירה; מסכת ברכות | the Talmud; the Code of Jewish Law; the Book of Formation; the Talmud |
  | משיח; ההשכלה | the Messiah; the Enlightenment movement |
  | שמע ישראל | Hear, O Israel |
  | סידור | prayer book |
  | אבא ואמא עילאין / תתאין; פרצוף | the upper / lower Father and Mother; configuration |
  | חסד, גבורה, תפארת, נצח, הוד, יסוד, מלכות | Kindness, Might, Beauty, Victory, Splendor, Foundation, Kingship |
  | ג' ראשונות, ז' תחתונות; מידות שבשכל | the first three, the seven lower attributes; the emotions within the mind |
  | ב"כן, נפקא מינא; היולי | the outcome, the practical result; formless matter |
  | ממלא כל עלמין; יש מאין; כוח הפועל בנפעל | the One who fills all worlds; something from nothing; the power of the Maker within the made |
  | שם אדנות, שם אלוקים | the divine Name that means Lord, the Name of God that is a word of power |
  | עין רבתי, דלת רבתי (בשמע ישראל) | the enlarged last letter of "Hear", of "One" |
  | נו"ן כפופה, נו"ן פשוטה | the letter of fifty bent, and straight |
  | איש תבונה | a man of understanding (Proverbs 20:5) |
  | וד"ל | and the understanding will understand |

  Add each new term here as it is first translated.
- **Wordplay** the teaching rests on is explained in English without saying the
  Hebrew word: "In Hebrew, the word for study comes from the word for the
  eye"; "the word for contemplation is written with the letter whose number
  is fifty, twice". Nothing else is added.
- **Names stay** (people, books, movements): Chabad, the Baal Shem Tov, the
  Alter Rebbe, the Mitteler Rebbe, the Maggid, Rashi, the Tanya, the Zohar,
  Kabbalah, the Torah. Verses in English, as said.
- **Titles**: each "## " section is a chapter of the video, a short English
  title of what it says. No footnotes (they are not read).
- **No brackets** in what is read: the build stops on one.
- Hebrew stays Hebrew everywhere else in the repo; this English is made only
  because Ronnie asked for English episodes.
