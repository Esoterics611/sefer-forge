#!/usr/bin/env bash
# Render one session's section.md exactly as the book renders it, for a
# visual check of the נוסח and the ביאור boxes together.
# Usage: bash scripts/preview-session.sh <session-path>
#
# Writes output/preview/<discourse>-<session>.docx (same template, pandoc
# flags and polish pass as build-docx.sh). When Microsoft Word is reachable
# (WSL + Windows Office) it also writes the .pdf and one PNG per page,
# output/preview/<discourse>-<session>-<N>.png, for reading the pages.
set -e

SESSION="${1%/}"
if [ -z "$SESSION" ] || [ ! -f "$SESSION/section.md" ]; then
  echo "Usage: $0 <session-path>   (needs <session-path>/section.md)"
  exit 1
fi

PY=$(command -v python || command -v python3)
NAME="$(basename "$(dirname "$(dirname "$SESSION")")")-$(basename "$SESSION")"
OUTDIR=output/preview
mkdir -p "$OUTDIR"
rm -f "$OUTDIR/$NAME".* "$OUTDIR/$NAME"-*.png

# Same frontmatter strip as compile.py: left in, pandoc would treat the
# session's title as the document title.
MD="$OUTDIR/$NAME.md"
"$PY" - "$SESSION/section.md" "$MD" <<'EOF'
import re, sys
from pathlib import Path
text = Path(sys.argv[1]).read_text(encoding="utf-8")
Path(sys.argv[2]).write_text(re.sub(r"^---[\s\S]*?---\s*\n?", "", text, count=1), encoding="utf-8")
EOF

TEMPLATE=templates/book-template.docx
if [ ! -s "$TEMPLATE" ] || [ scripts/create-template.py -nt "$TEMPLATE" ]; then   # -s: an empty file (a crash mid-write) is rebuilt too
  "$PY" scripts/create-template.py
fi

DOCX="$OUTDIR/$NAME.docx"
pandoc "$MD" \
  -o "$DOCX" \
  --reference-doc="$TEMPLATE" \
  --metadata-file=templates/defaults.yaml \
  -f markdown+yaml_metadata_block+bracketed_spans+grid_tables \
  --resource-path=.:discourses
"$PY" scripts/polish-docx.py "$DOCX"
echo "Built: $DOCX"

# PDF + page images through Word, when this is WSL with Office installed.
if ! command -v powershell.exe &>/dev/null || ! command -v pdftoppm &>/dev/null; then
  echo "No Word/pdftoppm here: open $DOCX to review."
  exit 0
fi
bash "$(dirname "$0")/docx-to-pdf.sh" "$DOCX" "$OUTDIR/$NAME.pdf"
pdftoppm -png -r 70 "$OUTDIR/$NAME.pdf" "$OUTDIR/$NAME"
echo "Pages: $(ls "$OUTDIR/$NAME"-*.png | tr '\n' ' ')"
