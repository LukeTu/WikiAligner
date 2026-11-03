# Handoff: install and run WikiAligner on this computer

For an AI coding agent working for the person who received this package. Follow these steps in order. Work on their computer only; nothing here needs a server, an account or an API key.

## What this is

A desktop app that finds corresponding sentences across Wikipedia language editions and revisions: a local FastAPI server (`wikialigner/server.py`) plus a static web UI (`wikialigner/web/`) shown in a native window through pywebview. See `README.md` for features and for the benchmark behind the model list.

Supported: macOS on Apple silicon and 64-bit Windows 10/11. Linux should work from source but is untested. Intel Macs are not supported, because current PyTorch has no Intel Mac builds.

Needs: about 4 GB of free disk, 8 GB of RAM, and internet access. Mainland China needs a proxy for Wikipedia; see Troubleshooting.

## Step 1: Try the prebuilt installer

Skip to step 2 if the person asked for a source install or is on another platform.

- macOS: `curl -fsSL https://github.com/LukeTu/WikiAligner/releases/latest/download/install_mac.sh | bash`
- Windows (PowerShell): `irm https://github.com/LukeTu/WikiAligner/releases/latest/download/install_windows.ps1 | iex`

Read each script before running it. They only download the installer from this repository's Releases page, install for the current user where possible, and open the app. If this works, go to step 4.

## Step 2: Install from source

Run from the folder containing this file. `uv` manages Python 3.12 and all dependencies in a local `.venv`, using the versions pinned in `uv.lock`.

1. Install uv if `uv --version` fails. Tell the person first, since this adds a tool to their computer:
   - macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. `uv sync --no-dev --python 3.12` (downloads about 1 GB).

## Step 3: Verify

Run the smoke test. It starts the local server, aligns two short texts, aligns a real Wikipedia revision and exports to Excel. From source it downloads the default model (about 0.5 GB) on first use.

```bash
uv run --no-dev python packaging/smoke_test.py uv run --no-dev -m wikialigner
```

It must print `SMOKE TEST PASSED`. For an installed app, pass the executable instead of `uv run …`:

- macOS: `python3 packaging/smoke_test.py /Applications/WikiAligner.app/Contents/MacOS/WikiAligner`
- Windows: `python packaging/smoke_test.py "%LOCALAPPDATA%\Programs\WikiAligner\WikiAligner.exe"`

If you changed any code, also run `uv sync && uv run pytest` (no network needed).

## Step 4: Start it and hand back

- Installed app: open WikiAligner from Applications or the Start menu.
- From source: double-click `scripts/start_mac.command` or `scripts/start_windows.bat`, or run `uv run --no-dev -m wikialigner`. Add `--browser` to use the default browser if the native window fails.

Show the person how to run the built-in example: on the Align tab, click the first example button (Assassination of Boris Nemtsov, en/ru, 2015-03-10). Tell them what you installed and where, and report any step that failed or that you skipped.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| "Could not reach Wikipedia" | Wikipedia is blocked or offline. Set a proxy under Settings, or use a system proxy. Do not change code for this. |
| Model download fails or hangs | The app tries hf-mirror.com automatically when huggingface.co is unreachable. It can also be chosen under Settings (restart needed). The default model is included in the installers and needs no download. |
| macOS: "cannot be opened" or "could not verify" | The app has no Apple Developer ID signature. System Settings → Privacy & Security → Open Anyway. Tell the person what this does before they approve it. Installing with the curl command above avoids the prompt. |
| Windows: SmartScreen warning | The app has no paid signing certificate. More info → Run anyway, with the person's approval. |
| Windows: no window, or a browser opens instead | WebView2 Runtime is missing, so the app fell back to the browser. It still works. Install the WebView2 Runtime from Microsoft for a native window. |
| Page says it cannot reach the local server | The app was closed while the page stayed open. Restart the app. |
| Slow on a CPU-only computer | The default gives roughly 50 sentences per second on four CPU threads, so a 600-sentence article pair takes about 12 seconds. Multilingual E5 small is about four times faster but less accurate. Larger models are slower. |
| Anything else in the installed app | Read the log. macOS: `~/Library/Application Support/WikiAligner/wikialigner.log`. Windows: `%LOCALAPPDATA%\WikiAligner\wikialigner.log`. |

## Rules for this handoff

- Do not disable security features (Gatekeeper, SmartScreen, antivirus) system-wide. Approve only this app, and only with the person's agreement.
- Do not enter passwords or API keys. The app needs none.
- User data is kept outside this folder (see "Where data is stored" in `README.md`). Do not delete it when reinstalling.

## Building the installers

Only if asked. Pushing a tag such as `v0.2.0` to GitHub makes `.github/workflows/build.yml` build and test both installers and publish a Release. To build locally on that platform:

```bash
uv sync --no-dev --group build --python 3.12
uv run --no-dev --group build python packaging/fetch_model.py
uv run --no-dev --group build pyinstaller packaging/wikialigner.spec --noconfirm
```

Then run `bash packaging/make_dmg.sh` on macOS, or `iscc /DAppVersion=0.2.0 packaging\wikialigner.iss` on Windows.
