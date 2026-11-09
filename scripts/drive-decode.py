#!/usr/bin/env python3
"""Write a file the Google Drive connector downloaded (download_file_content) to disk.

Usage:
    python scripts/drive-decode.py <saved-result.json> <output-file>

The connector returns the file as JSON with its bytes in base64 (`content`),
too large to pass through the conversation: a subagent saves the tool result to
a JSON file and runs this on it (skill new-session, step 2). For recordings up
to about 3 MB; a larger one goes by a share link and curl (same step).
"""
import base64
import json
import sys

if len(sys.argv) != 3:
    sys.exit(__doc__)
src, dst = sys.argv[1], sys.argv[2]
with open(src, encoding="utf-8") as f:
    obj = json.load(f)
data = base64.b64decode(obj["content"], validate=True)
with open(dst, "wb") as f:
    f.write(data)
print(f"{obj.get('title') or obj.get('id')} ({obj.get('mimeType')}): wrote {len(data)} bytes to {dst}")
