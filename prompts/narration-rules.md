# Narration rules: the Shivchei HaBesht videos

Applies when Claude makes a narrated video from the booklet stories: a plan
in `booklets/narration/<name>.yaml`, built by `scripts/build-narration.py`
into `output/narration/<name>/` (procedure: skill `narrate-video`). Settled
with the user on 2026-10-29 and 30; a change the user asks for is written here.

**The goal (2026-10-30): every story narrated**, in English, then French.
The first five English episodes were chosen by hand. From there on the
episodes follow the themed booklets (`booklets/booklets.yaml`), in order:
- **One episode per booklet**, with its stories that are not MATURE and
  not yet narrated, in the booklet's order.
- **Title:** the booklet's English title, shortened where it would not
  fit on one line.
- **Length:** a booklet over about 3,100 words splits into parts ("…, Part
  One"); one under about 1,000 words joins a neighbouring booklet of a like
  theme, or stands alone when neither neighbour shares its theme (Fit and
  Unfit, 5 minutes).
- **Coverage:** the table at the end shows which booklets are done.

## An episode

- Two to four stories that belong together: a stretch of his life (birth and
  youth, the hidden years, his passing) or a theme (the Days of Awe,
  journeys). 7–15 minutes: 1,300–2,600 words read, at about 175 a minute.
- Read in English or French by the free Kokoro voice. Kokoro has no Hebrew.
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
  ("The Locked Gate"), or for a booklet episode the booklet's title.
- Words that open a story by pointing back to the one before it are made to
  stand alone (Edits, below): "Another time", "I also heard", "that preacher".

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

## Brackets (`drop:` and `edits:`)

- **A bracket that explains** a word, a name, a phrase or a reference (the
  booklet's glossing) **is dropped**, with the space before it. Examples:
  "(the king's chief adviser)", "(Elisha ben Abuyah)", "(for his sermons)",
  "(that he was ready to die in his place)", "(what is called in Yiddish
  *hinerplet*)", "(Morocco)". List it under the story's `drop:` by its
  opening words, bracket included (`"(a punishment in which the soul"`): the
  build removes it to its closing bracket.
- **A narrator's note inside someone else's quoted words is dropped too**:
  which festival it was, which wording was said. Read aloud, it would sound
  like the speaker's own words ("(Rabbi Falk was not sure whether…)" inside
  the Baal Shem Tov's speech in 20; "(I do not know whether it was the first
  day of Passover…)" inside the Maggid's in 15).
- **A bracket that names who or where** is folded into the sentence:
  "the rabbi (of Nemirov)" → "the rabbi of Nemirov"; "I heard from him (from
  Rabbi Pinchas)" → "I heard from Rabbi Pinchas".
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

- `booklets/narration/say-en.yaml` (and `say-fr.yaml`) is shared by every
  plan in that language. Before recording, run `<plan> --names`: it prints
  every capitalised word as the voice will say it. Respell what comes out
  wrong, checking the respelling with
  `python scripts/build-narration.py --say Gershon Ghershon` (French:
  `--say --lang fr …`), and add it the first time a story uses the word. A
  lowercase entry (tzaddik) also covers the capitalised word (Tzaddik), but
  not the other way round. A plan's own `say:` is for a one-off.
- Check the glossary too (`booklets/glossary-en.yaml`, and the italic words
  in the stories): `--names` only lists capitalised words.
- English traps found so far:
  - "ch" reads as in "church": Chana, Nachman and Pinchas are respelled with h.
  - G before e or i reads as j: Gershon, Gedaliah and Gemara are respelled with "Gh".
  - "Tzvi" is spelled out letter by letter.
  - "Mishnah" loses its "sh".
  - "kh" comes out as plain k.
  - Many names starting with two consonants are spelled out letter by letter:
    Chmielnik, Shmeril, Sde, Tluste, Shmuel, Shneur.
  - Listen for English words a name sounds like (Bitchov → Bee-chov).
- French: the build reads `'h` (Na'hman, Pessa'h, 'hazan, the Hebrew ח) as the
  French r, the nearest sound, but leaves the elisions l'h d'h t'h m'h n'h
  j'h s'h c'h (l'homme, d'habitude, aujourd'hui) alone. `--names` marks a word
  that espeak reads as English (Falk, Kolomea); respell it the French way
  (Falque). Silent final letters need respelling too: Chabbat → Chabbate,
  Kamenets → Kaménètse.
- The English voice says "Tov" as "tahv". The user does not like it, but
  accepted it until there is a better voice (`docs/backlog.md`). The French
  voice says it right.

## Voice

English: `am_michael` (an American man), speed 1.0, in every episode so
far. To change it, give the user samples first:
`--sample am_michael,am_fenrir,bm_george,bm_fable,af_heart`.
French: `ff_siwis` (a woman), Kokoro's only French voice. The French episodes
reuse the English episode's drawing, with the French titles (series and
subtitle from `booklets.yaml`).

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

English, `lang: en`, in the order they were made: the first five chosen by hand, then the
booklets in order (192 stories, every one not flagged MATURE). Length: of the video, filled in
once it is built.

| Plan | Stories | Length | Picture |
|---|---|---|---|
| `the-boy-who-was-not-afraid` | 1, 12, 70, 33 | — | a moonlit forest, the boy with his stick on the path |
| `the-locked-gate` | 17, 161, 179 | — | the gate in the heavens, locked, with the prayers rising |
| `the-frog-in-the-wilderness` | 10, 11, 3 | — | the great frog in the wilderness at dusk, before the lone figure |
| `the-speech-of-the-birds` | 101, 26, 197 | — | a wagon on a road at dawn, birds rising over the fields |
| `the-passing-of-the-baal-shem-tov` | 207, 210 | — | a candle burning down at dawn, its flame rising blue toward an open window |
| `the-authors-introduction` | 0 | — | an open book on a lectern by lamplight, a quill in the inkwell |
| `the-hidden-years-and-the-revelation` | 4, 5, 9 | — | the rock like a small house on the mountain across the river Prut, at dawn, a lone figure on the way |
| `rabbi-gershon-of-kitov` | 7, 20, 66, 79, 111 | — | a wooden synagogue at dusk, the souls coming to it like a great flock of lights |
| `the-land-of-israel-and-the-way-there` | 28, 29, 30, 92, 93, 155, 191, 202 | — | a sailing ship at dusk off the coast of the Land of Israel, a walled city on the hills |
| `in-prayer` | 15, 16, 76, 95, 147 | — | a man wrapped in his prayer shawl, seen from behind, before the holy ark, its lamps and the light |
| `his-ways-and-customs` | 53, 63, 68, 134, 149, 156, 164, 169 | — | a pipe and a cup of wine on a table by the window, the Sabbath candles lit |
| `the-rabbi-of-polonne` | 21, 22, 23, 65, 103, 104, 150, 162, 166, 167 | — | the Rabbi of Polonne's study by night, a letter with its seal on the table, rain at the window |
| `the-mokhiach-of-polonne-part-one` | 84, 85, 96 | — | the great synagogue of Lvov, the preacher in borrowed silk at its door |
| `the-mokhiach-of-polonne-part-two` | 123, 125, 160 | — | the house in Kitov at night, the jester's dark shape at the window, one candle |
| `the-maggid-of-mezritch` | 34, 45, 47, 130, 200 | — | a night of thunder and lightning over a small house, one window lit |
| `the-maggids-household-and-disciples` | 40, 41, 42, 43, 46, 109 | — | a sukkah at night, its lamp lit, the stars through its roof of branches |
| `rabbi-nachman-of-horodenka` | 73, 74, 75, 91, 94, 102, 131, 186 | — | a study house on the water at dawn, the mikveh beside it, one window lit |
| `rabbi-yitzchak-of-drohobych` | 36, 37, 57, 58, 59 | — | a pair of tefillin and their open box on a table, a thaler beside them, lamplight |
| `tzaddikim-of-his-generation-part-one` | 24, 25, 35 | — | the schoolchildren's psalms rising over Nemirov by night, the Tatars' fires far off on the plain |
| `tzaddikim-of-his-generation-part-two` | 61, 78, 116, 135, 144, 145 | — | a wagon stopped on a dark road on Friday night, the stars, the first Sabbath candles in a far window |
| `opponents-and-testers` | 48, 87, 99, 188, 189, 190 | — | two wagons facing each other in a forest clearing, the robbers' shadows fleeing among the trees |
| `opponents-who-drew-close-part-one` | 13, 14, 112 | — | a splendid palace in a dream, its windows lit, a man looking in from the dark |
| `opponents-who-drew-close-part-two` | 113, 114, 115, 185, 203 | — | an open Gemara in the moonlight at a window, the night outside |
| `seeing-from-afar` | 18, 19, 38, 89, 118, 128, 129, 141, 143 | — | a man on a hilltop at dusk looking out over a wide plain, a covered wagon on the road far below, a town on the horizon |
| `wonders-on-the-road` | 8, 142, 148, 177, 178, 180 | — | a wagon on a snowy road under the moon, a long pipe stem trailing smoke from it |
| `leaseholders-and-noblemen-part-one` | 67, 110, 159 | — | a nobleman's castle on a hill above a village, its tower lit, a river below |
| `leaseholders-and-noblemen-part-two` | 172, 173 | — | a covered wagon under a low gateway, the lintel lifted above its hood, a lamp in the yard |
| `charity-and-money` | 86, 120, 121, 122, 138 | — | an empty purse and a last gold coin on a table by a candle, the door open to the night |
| `simple-jews-and-hidden-tzaddikim` | 51, 52, 126, 163, 194, 196 | — | a craftsman's small house at dawn, wool stockings drying on a line, the synagogue beyond |
| `fit-and-unfit` | 39, 100, 108, 139, 140, 151 | — | a shochet's long knife on its cloth by a whetstone, a turnip set aside at the end of the table, lamplight |
| `healings-part-one` | 31, 56, 69 | — | a sickroom at night, a bed by the window, a small bottle of medicine and a candle on the sill |
| `healings-part-two` | 80, 82, 83, 117, 192, 205 | — | a tavern in a snowstorm at night, its door shut fast, a rider coming through the snow |
| `sons-for-the-childless-part-one` | 71, 165, 182, 183 | — | a cradle by the window at dawn, a pair of small shoes beside it |
| `sons-for-the-childless-part-two` | 184, 204 | — | a small house alone in a dark forest, candles burning in its window, a loaded wagon on the road |
| `demons-sorcerers-and-harmful-spirits` | 6, 62, 88, 119, 124, 157, 158 | — | a dark spirit rolling like a whirlwind out of a tollkeeper's house at night, amulets on the table inside |
| `false-accusations-and-dangers` | 32, 97, 133, 136, 154, 171 | — | a ford across a wide river at sunset, people crossing with their bundles before the Sabbath |
| `the-garden-of-eden-and-gehinnom` | 54, 55, 64, 127, 152, 153, 168, 176 | — | a pillar of fire standing over a grave in a cemetery at night, the road passing by |
| `sin-repentance-and-reincarnation` | 193, 49, 72, 175, 201, 209 | — | a dog swimming in a dark river at dusk, a fisherman's boat with its net, the far bank |
| `his-last-days` | 77, 90, 105, 106, 107 | — | a bell on a string in a quiet house at dusk, the string running out through the door to a small house |

French, `lang: fr` (the English episode's stories and drawing):

| Plan | Stories | Length | As |
|---|---|---|---|
| `le-garcon-qui-n-avait-pas-peur` | 1, 12, 70, 33 | — | the-boy-who-was-not-afraid |
| `la-porte-verrouillee` | 17, 161, 179 | — | the-locked-gate |

Ideas for the next episodes are in `docs/backlog.md`.
