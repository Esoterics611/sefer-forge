#!/usr/bin/env bash
# Render compiled/book.md to output/book.docx via pandoc.
# Uses templates/book-template.docx as the style source.
set -e

mkdir -p output

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
  -f markdown+yaml_metadata_block+bracketed_spans \
  --resource-path=.:discourses

echo "Built: output/book.docx"
