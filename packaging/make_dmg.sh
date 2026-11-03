#!/bin/bash
# Wrap dist/WikiAligner.app in a drag-to-install disk image: dist/WikiAligner-macOS-arm64.dmg
set -euo pipefail
cd "$(dirname "$0")/.."

# Re-sign the whole bundle ad hoc so its signature stays valid after copying. This is not an Apple
# Developer ID signature, so Gatekeeper still asks once for apps opened from a downloaded disk image.
codesign --force --deep --sign - dist/WikiAligner.app
codesign --verify --deep --strict dist/WikiAligner.app

staging="$(mktemp -d)"
trap 'rm -rf "$staging"' EXIT
ditto dist/WikiAligner.app "$staging/WikiAligner.app"
ln -s /Applications "$staging/Applications"
rm -f dist/WikiAligner-macOS-arm64.dmg
hdiutil create -quiet -volname WikiAligner -srcfolder "$staging" -format ULFO -ov dist/WikiAligner-macOS-arm64.dmg
ls -lh dist/WikiAligner-macOS-arm64.dmg
