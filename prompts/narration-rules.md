# Narration rules: the Shivchei HaBesht videos

Applies when Claude makes a narrated video from the booklet stories: a plan
in `booklets/narration/<name>.yaml`, built by `scripts/build-narration.py`
into `output/narration/<name>/` (procedure: skill `narrate-video`). Settled
with the user on 2026-10-29 and 30; a change the user asks for is written here.

## An episode

- Two to four stories that belong together: a stretch of his life (birth and
  youth, the hidden years, his passing) or a theme (the Days of Awe,
  journeys). 7–15 minutes: 1,300–2,600 words read, at about 175 a minute.
- Read in English (or French) by the free Kokoro voice. Kokoro has no Hebrew.
- The video is one picture for the whole reading, with the series line, the
  episode's title and "Retold in Modern English" over its lower part. The
  subtitles go up beside it as `narration.srt`, not burned in. No music.

## Choosing the stories

- A story that holds a listener: one clear event, a few people, a turn at
  the end. Long teachings and lists of names are for the booklets.
- Never a story flagged MATURE in the booklet text (`<!-- MATURE: ... -->`).
- A story goes in one episode only. The table at the end lists every story
  narrated; check it first, and add each new episode to it.
- Order: the strongest story first or last. The book's order can change when
  one story refers back to another (161 recalls the ark in 17, so 17 first);
  say why in the plan.
- The episode's title is its central story's title, shortened if needed
  ("The Locked Gate").

## What is read

- The `intro:`, which is the series line only: "In Praise of the Baal Shem
  Tov, retold in modern English." **No list of the stories (no contents), no
  glossary.**
- Each story's title, then its paragraphs. Not the `**Summary:**` paragraph,
  not the book's closing line.
- The `outro:`: "Here end these stories from In Praise of the Baal Shem Tov."

## Cuts (`cut:`)

Leave out a whole paragraph only when it stops the story for a listener:
- a printer's note,
- a second version ("in the manuscripts it is written like this", "some tell
  it like this"),
- a long explanation of a verse or a saying,
- an afterword once the story has ended (the anger with the guests after the
  gate opened, in 17).

Never cut to shorten or to soften. Comment each cut in the plan, and tell the
user what was cut.

## Edits (`edits:`)

- **A bracket that explains** a word, a name, a phrase or a reference (the
  booklet's glossing) **is dropped**, with the space before it. Examples:
  "(the king's chief adviser)", "(Elisha ben Abuyah)", "(for his sermons)",
  "(that he was ready to die in his place)", "(what is called in Yiddish
  *hinerplet*)".
- **Any other bracket is part of the telling** (the narrator's aside, a
  detail, someone else's report). It loses its brackets and becomes a
  sentence or a clause:
  - "(I heard that he slept only two hours)" → "; I heard that he slept only two hours."
  - "(whose name I have forgotten)" → ", whose name I have forgotten,"
- **Words that point into the book** are made to stand alone:
  - "I also heard from him (from Rabbi Falk)" → "I heard from Rabbi Falk"
  - "as is explained above in the story of Yom Kippur" → "as is told in the story of Yom Kippur"
  - "Rabbi Pesach also told me" → "Rabbi Pesach told me"
- **Nothing is added.** No explanation of Claude's own: an early "many
  kilometers off" after "parsahs" was taken out at the user's word.
- The build stops on any bracket left in what is read, and on a `cut` or an
  `edit` that no longer matches the story exactly once.

## How names are said (`say:`)

- `booklets/narration/say.yaml` is shared by every plan. Add a name or term
  the first time a story uses it, after hearing it in phonemes:
  `python scripts/build-narration.py --say Gershon Ghershon`. A plan's own
  `say:` is for a one-off.
- Traps found so far:
  - "ch" reads as in "church": Chana, Nachman and Pinchas are respelled with h.
  - G before e or i reads as j: Gershon, Gedaliah and Gemara are respelled with "Gh".
  - "Tzvi" is spelled out letter by letter.
  - "Mishnah" loses its "sh".
  - "kh" comes out as plain k.
- The voice says "Tov" as "tahv". The user does not like it, but accepted
  it until there is a better voice (`docs/backlog.md`).

## Voice

`am_michael` (an American man), speed 1.0, in every episode so far. To
change it, give the user samples first:
`--sample am_michael,am_fenrir,bm_george,bm_fable,af_heart`.

## The picture

- **An original drawing for each episode**: a function in
  `booklets/narration/images/draw.py`, written to `<name>.svg`. The style is
  flat vector art, silhouettes against a lit sky or room, with one detail
  from the stories: the boy's stick, the lock on the heavenly gate, the
  frog's eye, the stopped clock and the blue flame.
- People appear as small silhouettes, never faces, as in every drawing so far.
- **What matters stays above y ≈ 620** (of 1080). The build darkens the lower
  part and lays the series line, title and subtitle there. View `frame.png`
  before building the video.
- **A picture the user brings** (ChatGPT, Nano Banana) works too, as
  `image:`. Such a JPG or PNG goes into Git LFS (`.gitattributes`), which a
  cloud session cannot push: commit it from the user's computer.

## Before handing over

- `--script`, then read `script.txt` whole: each story starts and ends where
  it should, and no aside or gloss is left.
- After the build:
  - The last subtitle cue ends with the audio.
  - `chapters.txt` starts at 0:00, with every chapter at least 10 seconds.
  - The audio is levelled (mean volume about −18 dB, peak below −1 dB, by ffmpeg's volumedetect).
  - `frame.png` has been looked at.
- Hand over `video.mp4`, `thumbnail.jpg`, `narration.srt` and `chapters.txt`.
  In a cloud session, send them as files: `output/` is not in git, so they
  are gone when the session ends. Each one rebuilds with one command.

## Episodes made

| Plan | Stories | Length | Picture |
|---|---|---|---|
| `the-boy-who-was-not-afraid` | 1, 12, 70, 33 | 14:31 | moonlit forest, the boy with his stick on the path |
| `the-locked-gate` | 17, 161, 179 | 10:38 | the gate in the heavens, locked, the prayers rising |
| `the-frog-in-the-wilderness` | 10, 11, 3 | — | the great frog at dusk, the Baal Shem Tov before it |
| `the-speech-of-the-birds` | 101, 26, 197 | — | a wagon on the road at dawn, birds rising |
| `the-passing-of-the-baal-shem-tov` | 207, 210 | — | a candle with a blue flame, the stopped clock, dawn in the window |

Ideas for the next episodes are in `docs/backlog.md`.
