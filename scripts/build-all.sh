#!/usr/bin/env bash
# Compile + render. The full pipeline from sources to docx.
# Usage: bash scripts/build-all.sh [book ...]   (no args = every book in books/)
set -e

PY=$(command -v python || command -v python3)

if [ $# -eq 0 ]; then
  set -- $(ls books)
fi

for BOOK in "$@"; do
  echo "==> [$BOOK] Compiling compiled/$BOOK.md"
  "$PY" scripts/compile.py "$BOOK"
  echo ""
  echo "==> [$BOOK] Rendering DOCX"
  bash scripts/build-docx.sh "$BOOK"
  echo ""
done

echo "Done. See output/"
