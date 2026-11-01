#!/usr/bin/env bash
# Publish site/ (the app's home page, privacy policy and terms) to the gh-pages
# branch, which GitHub Pages serves at https://esoterics611.github.io/sefer-forge/
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
git push origin "$(git subtree split --prefix site HEAD)":refs/heads/gh-pages
