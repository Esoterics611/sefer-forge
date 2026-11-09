#!/usr/bin/env bash
# Set up a fresh cloud container (Claude Code on the web) for this repository:
# what such a container lacks and the pipeline needs. The cloud environment
# "sefer-forge" runs it at the start of every new container; it is safe to run
# again by hand (bash scripts/setup-cloud.sh) and changes nothing that is
# already in place. The home machine (WSL, Windows fonts) does not need it.
#
#   1. Python packages: requirements.txt (PyAV first, as a prebuilt wheel:
#      building it from source fails in the container).
#   2. Preview fonts: the house fonts (David, Guttman Frank) are Windows fonts;
#      free stand-ins under their names (David Libre, Frank Ruhl Libre) let the
#      pamphlets and proofs render here. proof-pdf.py reports them as outside
#      the house fonts; the real print is made at home.
#   3. The repository's git identity (CLAUDE.md, "GitHub account"): a fresh
#      clone does not carry it.
#
# Each step reports a failure and goes on: a setup that stops would keep the
# session from starting. Chrome is found on the PATH (forgelib.chrome_path);
# the Whisper model downloads on the first transcription (huggingface.co).
set -u
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
warn() { echo "setup-cloud: $*" >&2; }

# 1. Python packages
pip install -q --only-binary=:all: "av==14.2.0" 2>&1 | grep -v "Running pip as" || true
pip install -q -r "$REPO/requirements.txt" 2>&1 | grep -v "Running pip as" || true
python3 -c "import faster_whisper, av, yaml, fitz" 2>/dev/null || warn "python packages incomplete"

# 2. Preview fonts
F="$HOME/.local/share/fonts/sefer-preview"
mkdir -p "$F" "$HOME/.config/fontconfig"
for f in DavidLibre-Regular.ttf DavidLibre-Bold.ttf; do
  [ -s "$F/$f" ] || curl -fsS -m 60 -o "$F/$f" "https://raw.githubusercontent.com/google/fonts/main/ofl/davidlibre/$f" \
    || { rm -f "$F/$f"; warn "could not download $f"; }
done
cp "$REPO/templates/fonts/FrankRuhlLibre-Regular.ttf" "$REPO/templates/fonts/FrankRuhlLibre-Bold.ttf" "$F/" \
  || warn "Frank Ruhl Libre not copied"
cat > "$HOME/.config/fontconfig/fonts.conf" <<'EOF'
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<!-- Container-only preview (scripts/setup-cloud.sh): the house fonts (Windows) are not
     installed here; their free revivals stand in for them. Not used at home. -->
<fontconfig>
  <alias binding="same"><family>David</family><prefer><family>David Libre</family></prefer></alias>
  <alias binding="same"><family>Guttman Frank</family><prefer><family>Frank Ruhl Libre</family></prefer></alias>
</fontconfig>
EOF
fc-cache -f >/dev/null 2>&1 || warn "fc-cache failed"

# 3. Git identity for this repository
git -C "$REPO" config user.email "192616319+Esoterics611@users.noreply.github.com" || warn "git user.email not set"
git -C "$REPO" config user.name "Ronnie Rendel" || warn "git user.name not set"

echo "setup-cloud: done ($(fc-match -f '%{family}' David 2>/dev/null) for David; git $(git -C "$REPO" config user.email))"
