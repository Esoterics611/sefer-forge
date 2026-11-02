# Publishing the narration videos to YouTube

The narrated episodes (skill `narrate-video`, `prompts/narration-rules.md`) go
up on the user's YouTube channel through `scripts/youtube-publish.py`: six a
day, private, one English episode then one French, each language in the
order of the rules' tables. The record lists every video not yet up under
the day it is planned for (`# planned for <date>`), so a session knows what
to upload; a missed day moves the plan on. The record of what is up, and of what goes up next, is
`booklets/narration/youtube.yaml`. A session picks up from it, so it is
committed and merged into `main` after every publishing session.

Settled with the user on 2026-10-30: English and French alternating; private for now (they make videos public
by hand in YouTube Studio), six a day, every new episode published as part of
making it. The workflow grows in small steps; upgrades are at the end.

## One-time setup (the user, about 15 minutes)

The channel's Google account is the one the user signs in to Claude with.

1. **Google Cloud project.** At console.cloud.google.com, signed in with that
   account, make a new project, e.g. `sefer-forge`.
2. **The APIs.** APIs & Services → Library → "YouTube Data API v3" → Enable,
   (and "Google Drive API", for the Drive copies once they have a sign-in of
   their own).
3. **Consent screen.** Google Auth Platform (OAuth consent screen):
   - user type External, an app name, your email;
   - Audience → Test users: add the channel's Gmail address;
   - leave it in Testing.
4. **The client.** Credentials → Create credentials → OAuth client ID.
   Choose the application type **TVs and Limited Input devices**: it signs in
   with a code typed on a phone, so it works from a cloud session. Keep the
   Client ID and Client secret it shows.
5. **Give them to Claude.** In the Claude cloud environment's settings (the
   environment menu in the session's title bar → Edit), add them under
   Network secrets (or as environment variables) as `YOUTUBE_CLIENT_ID` and
   `YOUTUBE_CLIENT_SECRET`. Never paste them into a chat. A new session
   picks them up.
6. **Home page and privacy policy** (asked for by the consent screen's
   Branding page, and needed to publish the app out of Testing):
   `site/` holds them, served by GitHub Pages from the repo
   Esoterics611/Esoterics611.github.io at https://esoterics611.github.io/
   (`privacy.html`, `terms.html`). After a change to `site/`, run
   `bash scripts/deploy-site.sh`. Authorized domain: `esoterics611.github.io`,
   verified in Search Console as the URL prefix `https://esoterics611.github.io/`
   by the tag in `site/index.html`. The old `/sefer-forge/` addresses (the
   `gh-pages` branch here) redirect to it.
7. **The Hebrew voice** (Google Cloud Text-to-Speech, free within its monthly
   allowance; `prompts/narration-rules.md`, Voice):
   - in the sefer-forge project, APIs & Services → Library → "Cloud
     Text-to-Speech API" → Enable;
   - Billing: Google asks for a billing account (a card) even for the free
     allowance. Set a budget alert at $1 (Billing → Budgets & alerts). The
     build stops at 900,000 characters a month, below the 1,000,000 free;
   - Credentials → Create credentials → API key → Edit API key → API
     restrictions: "Cloud Text-to-Speech API" only;
   - add it to the environment's secrets as `GOOGLE_TTS_API_KEY` (never in
     a chat). A new session picks it up.
   Until then the Hebrew episodes stay in the queue and each day's run skips
   them for the next videos.

## A publishing session (each day)

Say "publish to YouTube" or "next uploads". Then:

1. `python scripts/youtube-publish.py queue`: what is up, and which episodes
   go up on which day.
2. `python scripts/youtube-publish.py auth`: Claude shows a code. Open
   google.com/device on your phone, enter it, choose the channel's account,
   and allow access. The app is your own and unverified, so Google warns
   first: Continue. Once per session.
3. `python scripts/youtube-publish.py publish --build`, in the background:
   - builds the day's videos first, because a new session's `output/` is
     empty (about 10 minutes each, from the plans in git);
   - uploads up to six;
   - adds each to its language's playlist, made on the first upload.

   The record is rewritten after every video. A quota or day's limit
   reached stops it cleanly; the rest go up on the next run.
4. Commit `booklets/narration/youtube.yaml` and get it into `main` (a pull
   request, merged): the next session starts from `main`.
5. In YouTube Studio, the user:
   - looks over the videos;
   - adds the subtitles: Subtitles → Add language → Upload file → "With
     timing" → that episode's `narration.srt`, from the files Claude sends;
   - changes the visibility when ready.

**Copies in Google Drive: off for now.** `python scripts/youtube-publish.py drive
<name> ...` copies each episode's video, thumbnail, subtitles and chapters to
My Drive → "Shivchei HaBesht narration" → a folder per episode. But Google
refuses the sign-in by code (400 invalid_request, "Access blocked") when it
asks for Drive and YouTube together, so since 2026-11-01 the sign-in asks for
YouTube only and `drive` has no permission. To bring it back, give Drive a
sign-in of its own (a second token with `drive.file` alone), not a wider
YouTube one.

If the record is lost, or a session ended before it was merged,
`python scripts/youtube-publish.py sync` rebuilds it from the channel: every
video carries the tag `sefer-forge-<plan name>`.

`publish --dry-run` prints the next videos' titles, descriptions and settings
without signing in or uploading anything.

## What each video gets

- **Title:** the plan's title and the series, e.g. "The Boy Who Was Not
  Afraid | In Praise of the Baal Shem Tov".
- **Description:**
  - a line on the series;
  - the chapters (`chapters.txt`), which YouTube turns into chapters when
    there are three or more;
  - the story numbers, and what the book is;
  - the credits (a synthetic voice, an original drawing);
  - the link to the Sefer Forge site, https://esoterics611.github.io/ (how
    the videos are made);
  - three hashtags (YouTube shows them above the title).
- **Thumbnail:** the episode's `thumbnail.jpg`, the plain title card with
  בס"ד (dark ink on warm off-white), the same for every video and the same
  as the picture in the video (`prompts/narration-rules.md`, The
  thumbnail). `publish` sets it after the upload; `update [<name> ...]`
  puts the current description and thumbnail on videos already up.
- **Tags, language and playlist:** the series' tags, the episode's language,
  category Education, and the playlist "In Praise of the Baal Shem Tov
  (English)" or "Les louanges du Baal Chem Tov (en français)".
- **Settings:** private, and not made for kids. The stories include death,
  demons and Gehinnom, and the MATURE ones are not narrated at all. Change
  `made_for_kids` in the record if the user decides otherwise: YouTube asks
  it of every video.

## Limits, and the upgrades for later

- **Private, maybe locked.** Google restricts videos uploaded through an
  unverified API project (one made after 28 July 2020) to private. YouTube
  Studio may show them as "Locked (private)", which the user cannot change
  by hand. Check this on the first day's videos.
  - **Lifting it:** Google's YouTube API Services audit (the "Audit and
    Quota Extension Form", free, days to weeks). After it, set `privacy:`
    in the record to `public` or `unlisted`.
  - **Videos already locked** may have to be uploaded again: delete them in
    Studio, remove them from `uploaded:`, and run `publish`.
- **Five a day.** A project has 10,000 quota units a day, reset at midnight
  Pacific time. An upload costs 1,600, the thumbnail 50 and the playlist
  entry 50: 1,700 a video, so five a day (8,500); a sixth does not fit. The audit form also asks for more quota; raise `per_day` and
  `daily_units` in the record when it is granted.
- **Subtitles by hand.** Uploading captions needs the `youtube.force-ssl`
  scope, which the sign-in by code does not grant. Later: a "Desktop app"
  OAuth client, signed in once in a browser on the user's computer, and a
  `captions.insert` step in the script.
- **YouTube only, no Drive.** Google refuses the sign-in by code ("Access
  blocked: Authorization Error", Error 400 invalid_request) when it asks for
  `drive.file` together with `youtube`, so it asks for YouTube alone and
  `drive` is out of use.
- **Sign-in each session.** The token stays in the container
  (`~/.config/sefer-forge/youtube-token.json`), so each new session signs in
  again with a new code. Later: keep the refresh token as the environment
  secret `YOUTUBE_REFRESH_TOKEN`, which the script reads first. The
  consent screen must then be "In production", because tokens of an app
  in Testing expire after 7 days.
- **Scheduled publishing.** Once uploads may be public, YouTube's
  `publishAt` can space them out, e.g. one a day at a set hour, uploaded in
  advance.
- **The synthetic-content label** (`containsSyntheticMedia`) is not set.
  YouTube asks for it on realistic altered content, such as a real person
  seeming to say something; a narrator's voice reading a book is not that.
  Set it in `metadata()` if the user wants it shown.

## Going forward

Every new episode is published as a step of making it (skill
`narrate-video`, step 8): `python scripts/youtube-publish.py publish <name>`
adds it to the end of the queue, and uploads it at once if the day has room.
