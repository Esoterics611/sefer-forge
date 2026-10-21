#!/usr/bin/env python3
"""PostToolUse hook: after an edit to a session's text files, run
scripts/check-session.py on that session and hand its errors back to Claude.

Reads the hook's JSON on stdin. Silent (exit 0, no output) for files outside
discourses/*/sessions/*/ and when the session has no errors; warnings are
left to the explicit check. Errors come back as additionalContext.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

WATCHED = re.compile(r"(discourses/[^/]+/sessions/\d+)/"
                     r"(section\.md|commentary\.md|transcript\.md|ocr\.md|section-plan\.yaml)$")


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    path = (event.get("tool_input") or {}).get("file_path") or \
        (event.get("tool_response") or {}).get("filePath") or ""
    m = WATCHED.search(path.replace("\\", "/"))
    if not m:
        return 0
    root = Path(__file__).resolve().parents[2]
    r = subprocess.run([sys.executable, "scripts/check-session.py", m.group(1), "--quiet"],
                       cwd=root, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 1:
        return 0
    errors = "\n".join(ln for ln in r.stdout.splitlines() if "✗" in ln or not ln.startswith("  "))
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": f"scripts/check-session.py found errors after this edit:\n{errors}",
    }}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
