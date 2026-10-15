#!/usr/bin/env bash
# Scaffold a new book under books/<slug>/.
# Usage: ./scripts/new-book.sh <slug> "<Hebrew title>"
set -e

if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <slug> \"<Hebrew title>\""
  exit 1
fi

DIR="books/$1"
if [ -d "$DIR" ]; then
  echo "Already exists: $DIR"
  exit 1
fi

# Title-page date: today's Hebrew year (e.g. תשפ״ז) and Gregorian year.
PY=$(command -v python || command -v python3)
HEB_YEAR=$("$PY" -c 'from pyluach import dates; print(dates.HebrewDate.today().hebrew_year(thousands=False))')

mkdir -p "$DIR/front-matter" "$DIR/back-matter" "$DIR/chapters"

cat > "$DIR/metadata.yaml" <<YAML
title: "$2"
subtitle: ""
author: "רני רנדל"
date: "$HEB_YEAR · $(date +%Y)"
YAML

cat > "$DIR/structure.yaml" <<'YAML'
# Book structure. Discourse slugs = the <slug> in discourses/NNN-<slug>/.
# A chapter's `title` is optional (omit it when the discourse supplies its
# own '#' headings, as voice-only discourses do).

front_matter: []     # files in front-matter/

chapters: []
  # - title: "שער א"
  #   intro: 01-intro.md   # optional, file in chapters/
  #   discourses:
  #     - some-slug

back_matter: []      # files in back-matter/
YAML

echo "Created $DIR"
echo "Next: add discourses to $DIR/structure.yaml, then: bash scripts/build-all.sh $1"
