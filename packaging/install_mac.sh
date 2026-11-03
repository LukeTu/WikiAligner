#!/bin/bash
# One-step install for macOS (Apple silicon):
#   curl -fsSL https://github.com/LukeTu/WikiAligner/releases/latest/download/install_mac.sh | bash
# Set WIKIALIGNER_DMG (a URL or file:// path) or WIKIALIGNER_INSTALL_DIR to override the defaults.
set -euo pipefail

url="${WIKIALIGNER_DMG:-https://github.com/LukeTu/WikiAligner/releases/latest/download/WikiAligner-macOS-arm64.dmg}"

if [ "$(uname -s)" != "Darwin" ] || [ "$(uname -m)" != "arm64" ]; then
  echo "This installer is for Macs with Apple silicon (M1 or later)." >&2
  echo "On an Intel Mac, ask an AI agent to follow HANDOFF.md, or use a Windows PC." >&2
  exit 1
fi

dest="${WIKIALIGNER_INSTALL_DIR:-/Applications}"
if [ ! -w "$dest" ] && [ -z "${WIKIALIGNER_INSTALL_DIR:-}" ]; then dest="$HOME/Applications"; fi
mkdir -p "$dest"

work="$(mktemp -d)"
mnt="$work/mnt"
cleanup() { hdiutil detach -quiet "$mnt" 2>/dev/null || true; rm -rf "$work"; }
trap cleanup EXIT

echo "Downloading WikiAligner (under 1 GB)…"
curl -fL --retry 3 --progress-bar -o "$work/WikiAligner.dmg" "$url"
mkdir -p "$mnt"
hdiutil attach -quiet -nobrowse -readonly -mountpoint "$mnt" "$work/WikiAligner.dmg"
echo "Installing to $dest…"
rm -rf "$dest/WikiAligner.app"
ditto "$mnt/WikiAligner.app" "$dest/WikiAligner.app"
xattr -dr com.apple.quarantine "$dest/WikiAligner.app" 2>/dev/null || true
echo "Installed $dest/WikiAligner.app"
if [ -z "${WIKIALIGNER_NO_OPEN:-}" ]; then open "$dest/WikiAligner.app"; fi
