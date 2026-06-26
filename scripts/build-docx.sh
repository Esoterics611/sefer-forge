#!/usr/bin/env bash
# Render compiled/book.md to output/book.docx via pandoc.
# Uses templates/book-template.docx as the style source.
set -e

mkdir -p output

# On Windows, pandoc is often in AppData and not on the bash PATH.
# Prefer a PATH-discovered pandoc; fall back to the known Windows location.
if ! command -v pandoc &>/dev/null; then
  WINPANDOC="$LOCALAPPDATA/Pandoc/pandoc.exe"
  if [ -f "$WINPANDOC" ]; then
    alias pandoc="$WINPANDOC"
    shopt -s expand_aliases
  else
    echo "pandoc not found. Install from https://pandoc.org/installing.html"
    exit 1
  fi
fi

if [ ! -f compiled/book.md ]; then
  echo "Missing compiled/book.md — run scripts/compile.py first."
  exit 1
fi

REF=""
if [ -f templates/book-template.docx ]; then
  REF="--reference-doc=templates/book-template.docx"
else
  echo "WARN: templates/book-template.docx not found — using pandoc defaults."
  echo "      See templates/README.md to create one."
fi

META=""
if [ -f templates/metadata.yaml ]; then
  META="--metadata-file=templates/metadata.yaml"
fi

pandoc compiled/book.md \
  -o output/book.docx \
  $REF \
  $META \
  --toc --toc-depth=2 \
  -f markdown+yaml_metadata_block+bracketed_spans+grid_tables \
  --resource-path=.:discourses

echo "Built: output/book.docx"

# Polish pass: fix paragraph spacing, line-height, callout-box margins.
# Non-fatal if it fails — the raw docx is still usable.
if command -v python &>/dev/null; then
  python scripts/polish-docx.py output/book.docx || \
    echo "WARN: polish pass failed; docx is raw."
else
  echo "WARN: python not on PATH; skipping polish pass."
fi
