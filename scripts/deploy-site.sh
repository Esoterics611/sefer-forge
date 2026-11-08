#!/usr/bin/env bash
# Publish site/ (the app's home page, privacy policy and terms, and the sample
# project's pages from scripts/site-samples.py) to the
# Esoterics611/Esoterics611.github.io repo, which GitHub Pages serves at
# https://esoterics611.github.io/ (the domain Google's consent screen verifies).
# A cloud session needs that repo attached first (add_repo, push access).
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
DEST="${1:-$(dirname "$PWD")/esoterics611.github.io}"
[ -d "$DEST/.git" ] || git clone --depth 1 https://github.com/Esoterics611/esoterics611.github.io "$DEST"
git -C "$DEST" pull -q --ff-only
cp -r site/. "$DEST"/
git -C "$DEST" add -A
if git -C "$DEST" diff --cached --quiet; then echo "site: nothing changed"; exit 0; fi
git -C "$DEST" -c user.email=192616319+Esoterics611@users.noreply.github.com -c user.name="Ronnie Rendel" \
    commit -qm "Site from sefer-forge $(git rev-parse --short HEAD)"
git -C "$DEST" push -q origin HEAD
echo "site: published to https://esoterics611.github.io/"
