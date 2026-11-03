"""Start the local server and show it in a native window (or the default browser)."""
from __future__ import annotations

import argparse
import logging
import socket
import sys
import threading
import time
import urllib.request
import webbrowser

from .config import APP_NAME, LOG_FILE, apply_startup_environment, load_settings


def _log_to_file_when_packaged() -> None:
    """An installed app has no console (on Windows sys.stdout is None, which crashes
    libraries that write to it), so send all output to a log file users can share."""
    if not getattr(sys, "frozen", False):
        return
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    mode = "w" if LOG_FILE.exists() and LOG_FILE.stat().st_size > 2_000_000 else "a"
    sys.stdout = sys.stderr = open(LOG_FILE, mode, encoding="utf-8", buffering=1)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_until_up(url: str, timeout: float = 30.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url + "/api/health", timeout=1):
                return
        except OSError:
            time.sleep(0.15)
    raise RuntimeError("The local server did not start")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="wikialigner", description=f"{APP_NAME} desktop app")
    parser.add_argument("--browser", action="store_true", help="open in the default browser instead of a window")
    parser.add_argument("--serve", action="store_true", help="only run the local server (for development)")
    parser.add_argument("--port", type=int, default=0, help="port for the local server (default: any free port)")
    args = parser.parse_args(argv)

    _log_to_file_when_packaged()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    apply_startup_environment(load_settings())

    import uvicorn

    from .server import create_app

    port = args.port or _free_port()
    url = f"http://127.0.0.1:{port}"
    if args.serve:
        print(f"{APP_NAME} serving at {url}", flush=True)
        uvicorn.run(create_app(), host="127.0.0.1", port=port, log_level="warning")
        return
    server = uvicorn.Server(uvicorn.Config(create_app(), host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    _wait_until_up(url)

    window_shown = False
    if not args.browser:
        try:
            import webview

            webview.create_window(APP_NAME, url, width=1440, height=900, min_size=(960, 640))
            webview.start()
            window_shown = True
        except Exception as e:  # no GUI backend available: fall back to the browser
            logging.warning("Native window unavailable (%s); opening the browser instead", e)

    if not window_shown:
        webbrowser.open(url)
        print(f"{APP_NAME} is running at {url} — press Ctrl+C to quit.")
        try:
            while thread.is_alive():
                thread.join(0.5)
        except KeyboardInterrupt:
            pass
    server.should_exit = True
    thread.join(5)


if __name__ == "__main__":
    main()
