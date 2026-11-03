#!/bin/bash
# Double-click to start WikiAligner on macOS.
# The first start installs Python and the dependencies (about 1 GB, needs internet);
# later starts take a few seconds.
cd "$(dirname "$0")/.." || exit 1
export PATH="$HOME/.local/bin:$PATH"
if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv (Python package manager)…"
  curl -LsSf https://astral.sh/uv/install.sh | sh || { echo "Could not install uv."; read -r -p "Press Enter to close"; exit 1; }
  export PATH="$HOME/.local/bin:$PATH"
fi
uv run --no-dev --python 3.12 -m wikialigner "$@"
status=$?
if [ $status -ne 0 ]; then read -r -p "WikiAligner stopped with an error. Press Enter to close"; fi
exit $status
