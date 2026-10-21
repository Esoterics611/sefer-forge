#!/usr/bin/env bash
# Export a .docx to PDF through Microsoft Word (WSL + Windows Office), so the
# book can be proofed like the pamphlets: python scripts/proof-pdf.py <pdf>.
# Usage: bash scripts/docx-to-pdf.sh <file.docx> [out.pdf]   (default: next to the .docx)
set -e

DOCX="$1"
PDF="${2:-${DOCX%.docx}.pdf}"
if [ -z "$DOCX" ] || [ ! -f "$DOCX" ]; then
  echo "Usage: $0 <file.docx> [out.pdf]"
  exit 1
fi
if ! command -v powershell.exe &>/dev/null; then
  echo "No Word here (needs WSL with Windows Office): open $DOCX and save it as PDF."
  exit 2
fi

# Word cannot open files on the WSL side reliably: work in the Windows temp folder.
NAME="docx2pdf-$$"
WINTMP=$(wslpath "$(powershell.exe -NoProfile -Command '[IO.Path]::GetTempPath()' | tr -d '\r')")
cp "$DOCX" "$WINTMP/$NAME.docx"
WDOCX=$(wslpath -w "$WINTMP/$NAME.docx")
WPDF=$(wslpath -w "$WINTMP/$NAME.pdf")
powershell.exe -NoProfile -Command "
  \$w = New-Object -ComObject Word.Application
  \$w.Visible = \$false
  try {
    \$d = \$w.Documents.Open('$WDOCX', \$false, \$true)
    \$d.ExportAsFixedFormat('$WPDF', 17)
    \$d.Close(\$false)
  } finally { \$w.Quit() }
" >/dev/null
mv "$WINTMP/$NAME.pdf" "$PDF"
rm -f "$WINTMP/$NAME.docx"
echo "PDF: $PDF"
