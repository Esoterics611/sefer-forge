#!/usr/bin/env bash
# Render compiled/<book>.md to output/<book>.docx via pandoc.
# Usage: bash scripts/build-docx.sh <book>
#
# Styles:   books/<book>/reference.docx if present, else templates/book-template.docx
# Metadata: templates/defaults.yaml, then books/<book>/metadata.yaml (book wins)
set -e

BOOK="$1"
if [ -z "$BOOK" ]; then
  echo "Usage: $0 <book>   (books: $(ls books))"
  exit 1
fi

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

SRC="compiled/$BOOK.md"
OUT="output/$BOOK.docx"

if [ ! -f "$SRC" ]; then
  echo "Missing $SRC — run: python scripts/compile.py $BOOK"
  exit 1
fi

PY=$(command -v python || command -v python3 || true)

# The shared template is generated (not committed): (re)build it when missing
# or when scripts/create-template.py has changed since.
TEMPLATE=templates/book-template.docx
if [ -n "$PY" ] && { [ ! -f "$TEMPLATE" ] || [ scripts/create-template.py -nt "$TEMPLATE" ]; }; then
  "$PY" scripts/create-template.py
fi

REF=""
if [ -f "books/$BOOK/reference.docx" ]; then
  REF="--reference-doc=books/$BOOK/reference.docx"
elif [ -f "$TEMPLATE" ]; then
  REF="--reference-doc=$TEMPLATE"
else
  echo "WARN: no reference docx — using pandoc defaults."
  echo "      Run: python scripts/create-template.py"
fi

META=()
[ -f templates/defaults.yaml ] && META+=(--metadata-file=templates/defaults.yaml)
[ -f "books/$BOOK/metadata.yaml" ] && META+=(--metadata-file="books/$BOOK/metadata.yaml")

pandoc "$SRC" \
  -o "$OUT" \
  $REF \
  "${META[@]}" \
  --toc --toc-depth=2 \
  -f markdown+yaml_metadata_block+bracketed_spans+grid_tables \
  --resource-path=.:discourses

echo "Built: $OUT"

# Polish pass: fix paragraph spacing, line-height, callout-box margins.
# Non-fatal if it fails — the raw docx is still usable.
if [ -n "$PY" ]; then
  "$PY" scripts/polish-docx.py "$OUT" || echo "WARN: polish pass failed; docx is raw."
else
  echo "WARN: python not on PATH; skipping polish pass."
fi
