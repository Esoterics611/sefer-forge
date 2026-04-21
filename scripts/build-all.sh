#!/usr/bin/env bash
# Compile + render. The full pipeline from sources to docx.
set -e

echo "==> Compiling book.md"
python scripts/compile.py

echo ""
echo "==> Rendering DOCX"
bash scripts/build-docx.sh

echo ""
echo "Done. See output/book.docx"
