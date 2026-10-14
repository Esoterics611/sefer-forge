#!/usr/bin/env bash
# Add a new session to an existing discourse.
# Usage: ./scripts/new-session.sh <slug-or-path>
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <slug-or-path>"
  exit 1
fi

# Resolve discourse directory
if [ -d "$1" ]; then
  DDIR="$1"
elif [ -d "discourses/$1" ]; then
  DDIR="discourses/$1"
else
  DDIR=$(ls -d discourses/*"$1"* 2>/dev/null | head -1)
  if [ -z "$DDIR" ]; then
    echo "Discourse not found matching: $1"
    echo "Available:"
    ls -1 discourses/ 2>/dev/null | grep -E '^[0-9]+-' || echo "  (none yet)"
    exit 1
  fi
fi

N=$(ls -1 "$DDIR/sessions" 2>/dev/null | awk '/^[0-9]+$/ {print $0+0}' | sort -n | tail -1)
NEXT=$(printf "%03d" $((${N:-0} + 1)))
SDIR="$DDIR/sessions/$NEXT"

if grep -qE '^type:[[:space:]]*voice-only' "$DDIR/meta.yaml" 2>/dev/null; then
  mkdir -p "$SDIR/voicenotes"
  echo "Created $SDIR  (voice-only discourse)"
  echo "  - $SDIR/voicenotes/   drop the shiur recording (.m4a) here"
  echo ""
  echo "Then run: python scripts/transcribe.py $SDIR"
  echo "and tell Claude: ingest voice session $SDIR"
  exit 0
fi

mkdir -p "$SDIR/images" "$SDIR/voicenotes"

echo "Created $SDIR"
echo "  - $SDIR/images/       drop book-page photos here"
echo "  - $SDIR/voicenotes/   drop your Hebrew voicenote (.m4a) here"
echo ""
echo "Then run: python scripts/transcribe.py $SDIR"
