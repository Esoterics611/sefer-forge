---
name: narrate-video
description: Make a narrated YouTube video (an episode) from the Shivchei HaBesht booklet stories in English or French. It chooses the stories, writes the plan, fixes how names are said, draws an original picture, records, builds video.mp4 with subtitles and chapters, checks and hands over. Use when the user says "narration", "make a video", "YouTube", "read the stories aloud", "another episode", "more videos". Argument - optional story numbers, a theme, or an existing plan name.
---

Rules (what is read, cut, dropped, respelled, drawn): `prompts/narration-rules.md`;
read it whole first. One episode is one plan, `booklets/narration/<name>.yaml`.
A session makes four or five episodes. Prepare them all (steps 1–4), then
record them in one background batch (step 5): each takes about 5 minutes of
recording and 3–4 of video on four CPUs.

1. **Choose the stories** by the rules: the next booklet in `booklets.yaml`
   (its stories not yet narrated and not MATURE; the rules' tables say which
   booklets are done), split or joined by length. Read each story whole in
   `shivchei-habesht-simple-en.md` (or `-fr.md`) before choosing. Tell the user
   the choice in a line per episode.
2. **Write the plan**: copy the layout of an existing plan (English
   `in-prayer.yaml`, French `la-porte-verrouillee.yaml`), with `title`, `lang`,
   `voice`, `speed`, `image`, `intro`, `outro`, and `stories` with their
   `cut:`, `drop:` and `edits:`. List every bracket in the chosen
   stories, and decide each one by the rules (dropped if it explains, made a
   sentence if it tells). Then run
   `python scripts/build-narration.py booklets/narration/<name>.yaml --script`
   and read `output/narration/<name>/script.txt` whole.
   **A French episode of an English one** starts from the English plan:
   `python scripts/narration-french-plan.py booklets/narration/<english>.yaml <french-name> "<French title>"`
   carries its cuts, dropped brackets and unbracketed asides over by position,
   and writes a `# TODO` for whatever it cannot (a reworded opening such as
   "I also heard" → "I heard", or a story whose French brackets differ from
   the English). Write each TODO in French by hand, delete it, and build
   `--script`, which stops on any bracket left.
3. **Names**: `python scripts/build-narration.py <plan> --names` prints every
   capitalised word as the voice will say it, after the shared respellings
   (`booklets/narration/say-en.yaml` / `say-fr.yaml`). Add a respelling where
   the phonemes are wrong, checked first with `--say` (French: `--say --lang fr`).
4. **Picture**: add a drawing function to `booklets/narration/images/draw.py`
   (its own seed, a `DRAWINGS` entry named after the plan) and run
   `python booklets/narration/images/draw.py <name>`. Check that `git diff`
   leaves the other drawings unchanged. Then run `--frame`, which builds only
   `frame.png` (the picture with the titles on it) and `thumbnail.jpg`. Look
   at it, and redraw until nothing that matters sits under the titles.
   A picture the user supplies goes in `image:` instead, and that file is
   committed from their computer (Git LFS).
5. **Build**: `python scripts/build-narration.py booklets/narration/<name>.yaml`
   for each plan, one after another, in the background. A changed picture
   needs only `--video`, without recording again.
6. **Check** each episode by the rules' list: the subtitles end with the audio
   (`ffprobe` the MP3 against the last `.srt` cue), the chapters start at 0:00,
   the volume is levelled, and the frame has been seen.
7. **Hand over**: send `video.mp4`, `thumbnail.jpg`, `narration.srt` and
   `chapters.txt`, with the episode's length and a line on what was cut. In a
   cloud session these files exist only in that session.
8. **Publish** (`docs/youtube-publishing.md`):
   `python scripts/youtube-publish.py publish <name>` adds the episode to the
   end of the YouTube queue and uploads it, private, if the day still has
   room (six a day). Sign in first with `auth` (a code for the user to enter
   at google.com/device), once per session. Without `YOUTUBE_CLIENT_ID` and
   `YOUTUBE_CLIENT_SECRET` in the environment, add the episode to `queue:`
   in `booklets/narration/youtube.yaml` by hand, and tell the user it is
   queued.
9. **Record**: add the episode to the rules' table (stories, length, picture).
   Commit the plan, `say-<lang>.yaml`, `draw.py`, the SVG and
   `booklets/narration/youtube.yaml`, and get them into `main`: the next
   session starts from it. Never commit `output/`.
   An idea left for later goes in `docs/backlog.md`.
