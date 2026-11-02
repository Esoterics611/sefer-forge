#!/usr/bin/env python3
"""Sign in to YouTube once, on your own computer, for a sign-in that lasts.

Usage (on your computer, not in a cloud session):
    python youtube-signin-local.py client_secret_XXXX.json
    python youtube-signin-local.py client_secret_XXXX.json --youtube-only   # no subtitles or Drive permission

It needs only Python 3.8 or newer: nothing to install. Download it from the
repo (scripts/youtube-signin-local.py) if you do not have a clone.

Why: the sign-in by code (youtube-publish.py auth) keeps its token inside the
cloud session's machine, which is recycled after a quiet spell, and Google
refuses that kind of sign-in any permission beyond YouTube itself. A sign-in
in your browser here gives a refresh token that the daily run reads from the
environment (YOUTUBE_REFRESH_TOKEN), so nobody has to enter a code again, and
it can include the subtitles (youtube.force-ssl) and Drive (drive.file).

Before running it (docs/youtube-publishing.md, setup step 8):
  - Google Cloud → Credentials → Create credentials → OAuth client ID →
    application type "Desktop app" → Create → Download JSON. That file is
    the argument.
  - Google Auth Platform → Audience → Publish app (In production): an app
    left in Testing has its sign-ins expire after 7 days.

What it does: opens Google's sign-in page in your browser (or prints the
address to open), waits on this computer (127.0.0.1) for Google to send you
back, trades the answer for a refresh token, checks which channel it reaches,
and prints the three lines to put in the Claude environment's settings.
Nothing is sent anywhere but Google. Never paste the printed lines into a chat.
"""
from __future__ import annotations

import base64
import hashlib
import http.server
import json
import secrets
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
CHANNELS = "https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true"
SCOPES = {
    "youtube": "https://www.googleapis.com/auth/youtube",
    "subtitles": "https://www.googleapis.com/auth/youtube.force-ssl",
    "drive": "https://www.googleapis.com/auth/drive.file",
}
PAGE = """<!doctype html><meta charset="utf-8"><title>YouTube sign-in</title>
<body style="font-family:sans-serif;max-width:36em;margin:4em auto;line-height:1.5">
<h2>{head}</h2><p>{text}</p><p>You can close this tab and go back to the terminal.</p></body>"""


def client_from(path: str) -> tuple[str, str]:
    data = json.load(open(path, encoding="utf-8"))
    c = data.get("installed")
    if not c:
        sys.exit("This JSON is not a Desktop app client. In Google Cloud: Credentials → Create credentials → "
                 "OAuth client ID → Desktop app, then Download JSON.")
    return c["client_id"], c["client_secret"]


class Catch(http.server.BaseHTTPRequestHandler):
    """Takes the one request Google sends back to http://127.0.0.1:<port>/."""
    answer: dict = {}

    def do_GET(self):
        query = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(self.path).query))
        if "code" not in query and "error" not in query:
            self.send_response(404)
            self.end_headers()
            return
        Catch.answer = query
        ok = "code" in query
        body = PAGE.format(head="Back from Google" if ok else "Sign-in refused",
                           text="The terminal now finishes the sign-in and prints the result." if ok
                           else f"Google said: {query.get('error')}").encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, *args):
        pass                                                    # keep the terminal clean


def post(url: str, fields: dict) -> dict:
    req = urllib.request.Request(url, data=urllib.parse.urlencode(fields).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Google refused the token request: {e.code} {e.read().decode()[:400]}")


def main(argv: list[str]) -> None:
    files = [a for a in argv if not a.startswith("--")]
    if len(files) != 1:
        sys.exit(__doc__)
    cid, secret = client_from(files[0])
    scopes = [SCOPES["youtube"]] if "--youtube-only" in argv else list(SCOPES.values())

    server = http.server.HTTPServer(("127.0.0.1", 0), Catch)
    redirect = f"http://127.0.0.1:{server.server_port}/"
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(16)
    url = AUTH_URL + "?" + urllib.parse.urlencode({
        "client_id": cid, "redirect_uri": redirect, "response_type": "code", "scope": " ".join(scopes),
        "access_type": "offline", "prompt": "consent", "state": state,
        "code_challenge": challenge, "code_challenge_method": "S256",
    })
    print("\nOpening Google's sign-in page. If no browser opens, copy this address into one:\n")
    print(url + "\n")
    print("Choose the YouTube channel's Google account. Google warns that the app is not verified:")
    print("it is your own, so Advanced → Go to (the app) → allow each permission.\n")
    webbrowser.open(url)
    server.serve_forever()                                      # until Google sends the browser back

    answer = Catch.answer
    if answer.get("state") != state:
        sys.exit("The answer did not match this sign-in (state). Run the script again.")
    if "error" in answer:
        sys.exit(f"Sign-in refused: {answer['error']}")
    granted = set(answer.get("scope", "").split())
    tokens = post(TOKEN_URL, {"code": answer["code"], "client_id": cid, "client_secret": secret,
                              "redirect_uri": redirect, "grant_type": "authorization_code",
                              "code_verifier": verifier})
    refresh = tokens.get("refresh_token")
    if not refresh:
        sys.exit("Google gave no refresh token. Remove the app's access at myaccount.google.com/permissions "
                 "and run the script again.")

    req = urllib.request.Request(CHANNELS, headers={"Authorization": f"Bearer {tokens['access_token']}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            channels = [c["snippet"]["title"] for c in json.load(r).get("items", [])]
    except urllib.error.HTTPError as e:
        channels = []
        print(f"(Could not read the channel: {e.code}. Is the YouTube Data API enabled in this project?)")
    print("Signed in." + (f" Channel: {', '.join(channels)}" if channels else " No YouTube channel on this account!"))
    for name, scope in SCOPES.items():
        if scope in scopes:
            print(f"  {name:10} {'granted' if scope in granted or not granted else 'NOT granted (untick?)'}")

    print("\nPut these three lines in the Claude cloud environment's settings, under Environment variables")
    print("(the environment menu in a session's title bar → Edit), replacing the YOUTUBE_CLIENT_ID and")
    print("YOUTUBE_CLIENT_SECRET there. Never paste them into a chat. A new session picks them up.\n")
    print(f"YOUTUBE_CLIENT_ID={cid}")
    print(f"YOUTUBE_CLIENT_SECRET={secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={refresh}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
