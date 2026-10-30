#!/usr/bin/env python3
"""Publish the narration videos to YouTube, a few a day, and record what is up.

Usage:
    python scripts/youtube-publish.py queue                 # what is up, and what goes up on which day
    python scripts/youtube-publish.py auth                  # sign in once per session (a code for google.com/device)
    python scripts/youtube-publish.py publish               # the next videos in the queue, up to the day's limit
    python scripts/youtube-publish.py publish --build       # ... building first any video not in output/
    python scripts/youtube-publish.py publish <name> ...    # these plans (added to the end of the queue if new)
    python scripts/youtube-publish.py publish --dry-run     # print the titles and descriptions, upload nothing
    python scripts/youtube-publish.py sync                  # rebuild the record from the channel itself
    python scripts/youtube-publish.py drive [--build] <name> ...   # copy episodes to Google Drive

Workflow, setup and limits: docs/youtube-publishing.md.

The record is booklets/narration/youtube.yaml: the settings (privacy, made for
kids, videos a day), the queue (the order of publishing), and each video put up
(its YouTube id, the day, its playlist). It is rewritten after every video;
commit it and get it into main, because the next session starts from it.

Each video goes up with its plan's title and the series, a description holding
the chapters (output/narration/<name>/chapters.txt), the story numbers and the
credits, its language, and a tag `sefer-forge-<name>` that `sync` finds it by.
It joins a playlist per language, made on the first upload. Not uploaded: the
thumbnail (the video is one picture, so YouTube's own is the same) and the
subtitles (captions.insert needs the youtube.force-ssl scope, which the
sign-in by code does not grant): add narration.srt in YouTube Studio.

`drive` copies an episode's video.mp4, thumbnail.jpg, narration.srt and
chapters.txt to Google Drive, in a folder per episode under "Shivchei HaBesht
narration" in My Drive (the sign-in's drive.file scope: it sees only the files
it made). The Google Drive API must be enabled in the same Cloud project.

Quota: YouTube gives a project 10,000 units a day, reset at midnight Pacific
time; an upload costs 1,600, a playlist entry 50. The script counts what it
spends per Pacific day in the record and stops before the budget or the day's
count runs out, and when YouTube says the quota is spent.

Sign-in: an OAuth client of the type "TVs and Limited Input devices" in the
user's Google Cloud project, given as YOUTUBE_CLIENT_ID and
YOUTUBE_CLIENT_SECRET (environment secrets of the cloud environment, never
pasted into a chat). `auth` prints a code; the user enters it at
google.com/device with the channel's Google account. The refresh token is kept
in ~/.config/sefer-forge/youtube-token.json (outside the repo), or read from
YOUTUBE_REFRESH_TOKEN.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "booklets/narration/youtube.yaml"
PLANS = ROOT / "booklets/narration"
OUT = ROOT / "output/narration"
SERIES = ROOT / "booklets/booklets.yaml"
TOKEN = Path.home() / ".config/sefer-forge/youtube-token.json"

SCOPE = "https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/drive.file"
DEVICE_URL = "https://oauth2.googleapis.com/device/code"
TOKEN_URL = "https://oauth2.googleapis.com/token"
API = "https://www.googleapis.com/youtube/v3"
UPLOAD = "https://www.googleapis.com/upload/youtube/v3/videos"
DRIVE = "https://www.googleapis.com/drive/v3/files"
DRIVE_UPLOAD = "https://www.googleapis.com/upload/drive/v3/files"
DRIVE_FOLDER = "Shivchei HaBesht narration"     # in the user's My Drive
DRIVE_FILES = {"video.mp4": "video/mp4", "thumbnail.jpg": "image/jpeg",
               "narration.srt": "application/x-subrip", "chapters.txt": "text/plain"}
COST = {"upload": 1600, "playlist": 50, "entry": 50, "list": 1}
PACIFIC = ZoneInfo("America/Los_Angeles")
CHUNK = 16 * 1024 * 1024            # a multiple of 256 KiB, as resumable uploads require
RECORD_SETTINGS: dict = {}          # the record's settings, read by main()

TEXT = {
    "en": {
        "about": "Stories of the Baal Shem Tov from Shivchei HaBesht, retold in modern English and read aloud.",
        "stories": "Stories {} of the book.",
        "credits": "Narration: a synthetic voice (Kokoro). Picture: an original drawing.",
        "playlist": "{} (English)",
        "tags": ["Baal Shem Tov", "Shivchei HaBesht", "In Praise of the Baal Shem Tov", "Hasidic stories",
                 "Chassidus", "Jewish stories", "Besht"],
    },
    "fr": {
        "about": "Des récits du Baal Chem Tov tirés du Chivhei HaBecht, racontés en français d’aujourd’hui et lus à voix haute.",
        "stories": "Récits {} du livre.",
        "credits": "Narration : une voix de synthèse (Kokoro). Image : un dessin original.",
        "playlist": "{} (en français)",
        "tags": ["Baal Chem Tov", "Chivhei HaBecht", "Les louanges du Baal Chem Tov", "histoires hassidiques",
                 "hassidisme", "récits juifs", "Besht"],
    },
}

HEAD = """\
# What is on YouTube: written by scripts/youtube-publish.py after every video.
# Commit it and get it into main after each publishing session: the next
# session starts from it. Workflow: docs/youtube-publishing.md.
#
# settings: privacy is private, unlisted or public (an unverified Google API
#   project's uploads stay private whatever it says); made_for_kids is
#   YouTube's question, asked of every video; per_day the videos a day;
#   daily_units the project's quota; category 27 is Education.
# queue: the order of publishing, one English episode then one French (each
#   in the rules' table order), with the day each is planned for; a run that
#   misses a day moves the plan on. A new episode is added at the end.
# uploaded: plan -> YouTube id, the day it went up, whether it is in its
#   language's playlist.
# days: units spent and videos put up, per Pacific day (the quota's day).
"""


# ---------- the record

def load() -> dict:
    rec = yaml.safe_load(RECORD.read_text(encoding="utf-8")) if RECORD.exists() else {}
    rec.setdefault("settings", {"privacy": "private", "made_for_kids": False, "per_day": 6,
                                "daily_units": 10000, "category": "27"})
    for key in ("queue", "playlists", "uploaded", "days"):
        rec.setdefault(key, [] if key == "queue" else {})
    return rec


def save(rec: dict) -> None:
    body = {k: rec[k] for k in ("settings", "playlists", "uploaded", "days", "drive") if k in rec}
    text = yaml.safe_dump(body, allow_unicode=True, sort_keys=False, width=100)
    # The queue, with the day each video not yet up is planned for: what the next sessions upload.
    lines, (_, n_left) = ["queue:"], left(rec)
    day, slot, last = dt.date.fromisoformat(today()), rec["settings"]["per_day"] - max(0, n_left), None
    for name in rec["queue"]:
        if name in rec["uploaded"]:
            lines.append(f"- {name}    # up {rec['uploaded'][name]['date']}")
            continue
        if slot >= rec["settings"]["per_day"]:
            day, slot = day + dt.timedelta(days=1), 0
        slot += 1
        if day != last:
            lines.append(f"  # planned for {day}")
            last = day
        lines.append(f"- {name}")
    head, _, rest = text.partition("playlists:")
    RECORD.write_text(HEAD + "\n" + head + "\n".join(lines) + "\nplaylists:" + rest, encoding="utf-8")


def today() -> str:
    return dt.datetime.now(PACIFIC).date().isoformat()


def spend(rec: dict, units: int, upload: bool = False) -> None:
    day = rec["days"].setdefault(today(), {"units": 0, "uploads": 0})
    day["units"] += units
    day["uploads"] += int(upload)
    save(rec)


def left(rec: dict) -> tuple[int, int]:
    """Units and uploads left today."""
    day = rec["days"].get(today(), {"units": 0, "uploads": 0})
    return rec["settings"]["daily_units"] - day["units"], rec["settings"]["per_day"] - day["uploads"]


# ---------- what goes up

def plan_of(name: str) -> dict:
    return yaml.safe_load((PLANS / f"{name}.yaml").read_text(encoding="utf-8"))


def metadata(name: str) -> dict:
    plan = plan_of(name)
    lang = plan["lang"]
    t = TEXT[lang]
    series = yaml.safe_load(SERIES.read_text(encoding="utf-8"))["languages"][lang]["series"]
    title = re.sub(r"(?<=\w)'", "’", plan["title"])
    if len(f"{title} | {series}") <= 100:
        title = f"{title} | {series}"
    chapters = (OUT / name / "chapters.txt").read_text(encoding="utf-8").strip()
    numbers = ", ".join(str(s["n"]) for s in plan["stories"])
    description = "\n\n".join([t["about"], chapters, t["stories"].format(numbers), t["credits"]])
    description = description.replace("<", "‹").replace(">", "›")      # YouTube refuses angle brackets
    return {
        "snippet": {"title": title, "description": description, "tags": t["tags"] + [f"sefer-forge-{name}"],
                    "categoryId": str(RECORD_SETTINGS["category"]), "defaultLanguage": lang,
                    "defaultAudioLanguage": lang},
        "status": {"privacyStatus": RECORD_SETTINGS["privacy"],
                   "selfDeclaredMadeForKids": bool(RECORD_SETTINGS["made_for_kids"]), "embeddable": True},
        "lang": lang, "series": series,
    }


def built(name: str) -> bool:
    video = OUT / name / "video.mp4"
    if not video.exists() or not (OUT / name / "chapters.txt").exists():
        return False
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                            str(video)], capture_output=True, text=True)
    return probe.returncode == 0                                    # not a video still being written


# ---------- sign-in

def client() -> tuple[str, str]:
    cid, secret = os.environ.get("YOUTUBE_CLIENT_ID"), os.environ.get("YOUTUBE_CLIENT_SECRET")
    if not cid or not secret:
        sys.exit("YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET are not set: add them to the environment's "
                 "secrets (docs/youtube-publishing.md, setup) and start a new session.")
    return cid, secret


def auth() -> None:
    cid, secret = client()
    r = requests.post(DEVICE_URL, data={"client_id": cid, "scope": SCOPE}, timeout=30)
    r.raise_for_status()
    d = r.json()
    print(f"\n  On your phone or computer, open {d['verification_url']}\n  and enter the code:  {d['user_code']}\n"
          f"  Sign in with the YouTube channel's Google account and allow access.\n", flush=True)
    deadline = time.time() + d["expires_in"]
    while time.time() < deadline:
        time.sleep(d.get("interval", 5))
        t = requests.post(TOKEN_URL, data={"client_id": cid, "client_secret": secret, "device_code": d["device_code"],
                                           "grant_type": "urn:ietf:params:oauth:grant-type:device_code"}, timeout=30)
        j = t.json()
        if t.ok:
            TOKEN.parent.mkdir(parents=True, exist_ok=True)
            TOKEN.write_text(json.dumps({"refresh_token": j["refresh_token"]}), encoding="utf-8")
            TOKEN.chmod(0o600)
            print(f"  Signed in. Token kept in {TOKEN} (not in the repo).")
            channel = api("GET", "channels", params={"part": "snippet", "mine": "true"})
            for c in channel.get("items", []):
                print(f"  Channel: {c['snippet']['title']} ({c['id']})")
            return
        if j.get("error") == "slow_down":
            d["interval"] = d.get("interval", 5) + 5
        elif j.get("error") != "authorization_pending":
            sys.exit(f"  Sign-in failed: {j.get('error')}: {j.get('error_description', '')}")
    sys.exit("  The code expired before it was entered. Run auth again.")


_access: dict = {}


def access_token(renew: bool = False) -> str:
    if _access.get("token") and not renew and time.time() < _access["until"]:
        return _access["token"]
    cid, secret = client()
    refresh = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    if not refresh and TOKEN.exists():
        refresh = json.loads(TOKEN.read_text(encoding="utf-8"))["refresh_token"]
    if not refresh:
        sys.exit("Not signed in: run  python scripts/youtube-publish.py auth")
    r = requests.post(TOKEN_URL, data={"client_id": cid, "client_secret": secret, "refresh_token": refresh,
                                       "grant_type": "refresh_token"}, timeout=30)
    if not r.ok:
        sys.exit(f"The sign-in has expired or was revoked ({r.json().get('error')}): run auth again.")
    _access.update(token=r.json()["access_token"], until=time.time() + r.json()["expires_in"] - 60)
    return _access["token"]


class QuotaSpent(Exception):
    pass


def api(method: str, path: str, **kw) -> dict:
    for attempt in (0, 1):
        r = requests.request(method, f"{API}/{path}", headers={"Authorization": f"Bearer {access_token(attempt > 0)}"},
                             timeout=60, **kw)
        if r.status_code != 401:
            break
    if r.status_code == 403 and any(e.get("reason") in ("quotaExceeded", "uploadLimitExceeded", "dailyLimitExceeded")
                                    for e in r.json().get("error", {}).get("errors", [])):
        raise QuotaSpent(r.json()["error"]["message"])
    if not r.ok:
        raise RuntimeError(f"{method} {path}: {r.status_code} {r.text[:500]}")
    return r.json() if r.text else {}


# ---------- YouTube calls

def resumable(url: str, params: dict, body: dict, path: Path, mime: str) -> dict:
    """A resumable upload (YouTube and Drive take the same protocol); the finished upload's JSON."""
    size = path.stat().st_size
    r = requests.post(url, params={"uploadType": "resumable", **params}, json=body, timeout=60,
                      headers={"Authorization": f"Bearer {access_token()}", "X-Upload-Content-Type": mime,
                               "X-Upload-Content-Length": str(size)})
    if r.status_code == 403 and "quota" in r.text.lower():
        raise QuotaSpent(r.json()["error"]["message"])
    if r.status_code == 403 and "insufficient" in r.text.lower():
        sys.exit("The sign-in does not allow this (Drive was added to it later): run auth again.")
    if not r.ok:
        raise RuntimeError(f"upload start: {r.status_code} {r.text[:500]}")
    session, start = r.headers["Location"], 0
    with path.open("rb") as f:
        while True:
            f.seek(start)
            chunk = f.read(CHUNK)
            end = start + len(chunk) - 1
            try:
                p = requests.put(session, data=chunk, timeout=300,
                                 headers={"Authorization": f"Bearer {access_token()}",
                                          "Content-Range": f"bytes {start}-{end}/{size}"})
            except requests.RequestException:
                time.sleep(5)                                       # ask where it got to, and go on from there
                p = requests.put(session, headers={"Authorization": f"Bearer {access_token()}",
                                                   "Content-Range": f"bytes */{size}"}, timeout=60)
            if p.status_code in (200, 201):
                return p.json()
            if p.status_code == 308:
                got = p.headers.get("Range")
                start = int(got.split("-")[1]) + 1 if got else 0
                if size > CHUNK:
                    print(f"    {start * 100 // size}%", flush=True)
                continue
            raise RuntimeError(f"upload: {p.status_code} {p.text[:500]}")


def upload(name: str, meta: dict) -> str:
    body = {"snippet": meta["snippet"], "status": meta["status"]}
    return resumable(UPLOAD, {"part": "snippet,status"}, body, OUT / name / "video.mp4", "video/mp4")["id"]


def playlist(rec: dict, lang: str, series: str) -> str:
    if lang in rec["playlists"]:
        return rec["playlists"][lang]
    title = TEXT[lang]["playlist"].format(series)
    found = api("GET", "playlists", params={"part": "snippet", "mine": "true", "maxResults": 50})
    spend(rec, COST["list"])
    pid = next((p["id"] for p in found.get("items", []) if p["snippet"]["title"] == title), None)
    if not pid:
        made = api("POST", "playlists", params={"part": "snippet,status"},
                   json={"snippet": {"title": title, "defaultLanguage": lang},
                         "status": {"privacyStatus": rec["settings"]["privacy"]}})
        spend(rec, COST["playlist"])
        pid = made["id"]
        print(f"  playlist made: {title} ({pid})")
    rec["playlists"][lang] = pid
    save(rec)
    return pid


def add_to_playlist(rec: dict, name: str) -> bool:
    meta = metadata(name)
    units, _ = left(rec)
    need = COST["entry"] + (0 if meta["lang"] in rec["playlists"] else COST["list"] + COST["playlist"])
    if units < need:
        return False
    pid = playlist(rec, meta["lang"], meta["series"])
    api("POST", "playlistItems", params={"part": "snippet"},
        json={"snippet": {"playlistId": pid, "resourceId": {"kind": "youtube#video",
                                                           "videoId": rec["uploaded"][name]["id"]}}})
    spend(rec, COST["entry"])
    rec["uploaded"][name]["playlist"] = True
    save(rec)
    return True


def drive_api(method: str, url: str, **kw) -> dict:
    r = requests.request(method, url, headers={"Authorization": f"Bearer {access_token()}"}, timeout=60, **kw)
    if r.status_code == 403 and "insufficient" in r.text.lower():
        sys.exit("The sign-in does not allow Drive (it was made before Drive was added): run auth again.")
    if not r.ok:
        raise RuntimeError(f"{method} {url}: {r.status_code} {r.text[:500]}")
    return r.json()


def drive_folder(rec: dict, name: str, parent: str | None) -> str:
    """The id of the folder `name` (in `parent`, or My Drive), made if it is not there."""
    q = f"name = '{name.replace(chr(39), chr(92) + chr(39))}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    q += f" and '{parent}' in parents" if parent else " and 'root' in parents"
    found = drive_api("GET", DRIVE, params={"q": q, "fields": "files(id)"}).get("files", [])
    if found:
        return found[0]["id"]
    made = drive_api("POST", DRIVE, json={"name": name, "mimeType": "application/vnd.google-apps.folder",
                                          **({"parents": [parent]} if parent else {})})
    return made["id"]


def drive(rec: dict, names: list[str], build: bool) -> None:
    """Copy each episode's video, thumbnail, subtitles and chapters to Drive, a folder per episode."""
    access_token()
    root = rec.setdefault("drive", {}).get("folder") or drive_folder(rec, DRIVE_FOLDER, None)
    rec["drive"]["folder"] = root
    copied = rec["drive"].setdefault("copied", [])
    save(rec)
    for name in names or [n for n in rec["queue"] if built(n)]:
        if name in copied:
            print(f"  {name}: already in Drive")
            continue
        if not built(name):
            if not build:
                print(f"  {name}: not built; --build builds it first")
                continue
            subprocess.run([sys.executable, str(ROOT / "scripts/build-narration.py"), str(PLANS / f"{name}.yaml")],
                           check=True)
        folder = drive_folder(rec, name, root)
        for file, mime in DRIVE_FILES.items():
            path = OUT / name / file
            if path.exists():
                resumable(DRIVE_UPLOAD, {"fields": "id"}, {"name": file, "parents": [folder]}, path, mime)
        copied.append(name)
        save(rec)
        print(f"  {name}: in Drive, {DRIVE_FOLDER}/{name}/")


# ---------- commands

def show_queue(rec: dict) -> None:
    per_day = rec["settings"]["per_day"]
    _, n_left = left(rec)
    day, slot = dt.date.fromisoformat(today()), per_day - max(0, n_left)
    print(f"Privacy {rec['settings']['privacy']}, made for kids {rec['settings']['made_for_kids']}, {per_day} a day.")
    for name in rec["queue"]:
        up = rec["uploaded"].get(name)
        if up:
            print(f"  up  {up['date']}  {name}  https://youtu.be/{up['id']}" + ("" if up.get("playlist") else "  (not in playlist yet)"))
            continue
        if slot >= per_day:
            day, slot = day + dt.timedelta(days=1), 0
        slot += 1
        print(f"      {day}  {name}" + ("" if built(name) else "  (to build)"))


def publish(rec: dict, names: list[str], build: bool, dry: bool) -> None:
    for name in names:
        if name not in rec["queue"]:
            rec["queue"].append(name)
    if not dry:
        access_token()                                  # signed in, before an hour of building
        save(rec)
    todo = [n for n in (names or rec["queue"]) if n not in rec["uploaded"]]
    if not dry:                                         # first, playlist entries a spent quota left undone
        for name, up in rec["uploaded"].items():
            if not up.get("playlist") and not add_to_playlist(rec, name):
                break
    done = 0
    for name in todo:
        units, count = left(rec)
        if dry and done >= rec["settings"]["per_day"]:
            break
        if not dry and (count <= 0 or units < COST["upload"]):
            print(f"  The day's limit is reached ({rec['settings']['per_day']} videos, {units} units left): "
                  f"the rest go up on the next days (queue).")
            break
        if not built(name):
            if not build:
                print(f"  {name}: not built (output/narration/{name}/video.mp4); --build builds it first")
                continue
            print(f"  {name}: building ...", flush=True)
            subprocess.run([sys.executable, str(ROOT / "scripts/build-narration.py"), str(PLANS / f"{name}.yaml")],
                           check=True)
        meta = metadata(name)
        if dry:
            print(f"\n=== {name}\n{meta['snippet']['title']}\n{meta['status']}\n\n{meta['snippet']['description']}\n")
            done += 1
            continue
        print(f"  {name}: uploading {meta['snippet']['title']}", flush=True)
        try:
            vid = upload(name, meta)
        except QuotaSpent as e:
            print(f"  YouTube says the quota is spent ({e}): the rest go up tomorrow.")
            rec["days"].setdefault(today(), {"units": 0, "uploads": 0})["units"] = rec["settings"]["daily_units"]
            save(rec)
            break
        rec["uploaded"][name] = {"id": vid, "date": today(), "playlist": False}
        spend(rec, COST["upload"], upload=True)
        print(f"    up: https://youtu.be/{vid}")
        try:
            add_to_playlist(rec, name)
        except QuotaSpent:
            pass                                        # its playlist entry waits for the next run
        done += 1
    if not dry:
        print(f"  {done} uploaded. Record: {RECORD.relative_to(ROOT)}; commit it and get it into main.")


def sync(rec: dict) -> None:
    ch = api("GET", "channels", params={"part": "contentDetails,snippet", "mine": "true"})
    spend(rec, COST["list"])
    item = ch["items"][0]
    print(f"Channel: {item['snippet']['title']}")
    uploads, token, ids = item["contentDetails"]["relatedPlaylists"]["uploads"], None, []
    while True:
        page = api("GET", "playlistItems", params={"part": "contentDetails", "playlistId": uploads,
                                                   "maxResults": 50, **({"pageToken": token} if token else {})})
        spend(rec, COST["list"])
        ids += [i["contentDetails"]["videoId"] for i in page.get("items", [])]
        token = page.get("nextPageToken")
        if not token:
            break
    found = 0
    for k in range(0, len(ids), 50):
        vids = api("GET", "videos", params={"part": "snippet", "id": ",".join(ids[k:k + 50])})
        spend(rec, COST["list"])
        for v in vids.get("items", []):
            for tag in v["snippet"].get("tags", []):
                if tag.startswith("sefer-forge-") and tag[12:] not in rec["uploaded"]:
                    day = v["snippet"]["publishedAt"][:10]
                    rec["uploaded"][tag[12:]] = {"id": v["id"], "date": day, "playlist": False}
                    found += 1
    save(rec)
    print(f"  {found} videos found that the record lacked (their playlist entries are made on the next publish).")


def main(argv: list[str]) -> None:
    if not argv or argv[0] not in ("queue", "auth", "publish", "sync", "drive"):
        sys.exit(__doc__)
    rec = load()
    RECORD_SETTINGS.update(rec["settings"])
    cmd, rest = argv[0], argv[1:]
    if cmd == "queue":
        show_queue(rec)
    elif cmd == "auth":
        auth()
    elif cmd == "sync":
        sync(rec)
    elif cmd == "drive":
        names = [a for a in rest if not a.startswith("--")]
        for n in names:
            if not (PLANS / f"{n}.yaml").exists():
                sys.exit(f"No plan booklets/narration/{n}.yaml")
        drive(rec, names, "--build" in rest)
    else:
        flags = {a for a in rest if a.startswith("--")}
        names = [a for a in rest if not a.startswith("--")]
        for n in names:
            if not (PLANS / f"{n}.yaml").exists():
                sys.exit(f"No plan booklets/narration/{n}.yaml")
        publish(rec, names, "--build" in flags, "--dry-run" in flags)


if __name__ == "__main__":
    main(sys.argv[1:])
