#!/bin/bash
# Cloud sessions only: install transcription deps + git-lfs so
# `python scripts/transcribe.py <session>` works out of the box.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "$CLAUDE_PROJECT_DIR"

python3 -c "import faster_whisper" 2>/dev/null || pip install -q -r requirements.txt
command -v git-lfs >/dev/null || { apt-get install -y -q git-lfs >/dev/null 2>&1 || (apt-get update -q && apt-get install -y -q git-lfs); }
git lfs install --local >/dev/null
