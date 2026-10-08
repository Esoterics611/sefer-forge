#!/usr/bin/env bash
# Scaffold a new discourse folder.
# Usage: ./scripts/new-discourse.sh <slug> [--voice-only]
#   --voice-only: sessions are recorded shiurim (transcript.md), no photos
set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <slug>   (e.g. 'teshuvah-intro')"
  exit 1
fi

SLUG="$1"
TYPE="images+voice"
[ "$2" = "--voice-only" ] && TYPE="voice-only"
N=$(ls -1 discourses/ 2>/dev/null | awk -F- '/^[0-9]+-/ {print $1+0}' | sort -n | tail -1)
NEXT=$(printf "%03d" $((${N:-0} + 1)))
DIR="discourses/$NEXT-$SLUG"

if [ -d "$DIR" ]; then
  echo "Already exists: $DIR"
  exit 1
fi

mkdir -p "$DIR/sessions"

cat > "$DIR/meta.yaml" <<EOF
discourse: $NEXT
slug: $SLUG
title: ""
status: draft
type: $TYPE
chapter: null
EOF

cat > "$DIR/notes.md" <<EOF
# Notes — $SLUG

Personal notes, source references, ideas for this discourse.
EOF

cat > "$DIR/discourse.md" <<EOF
---
discourse: $NEXT
slug: $SLUG
title: ""
status: draft
---

EOF

echo "Created $DIR"
echo "Next: ./scripts/new-session.sh $SLUG"
