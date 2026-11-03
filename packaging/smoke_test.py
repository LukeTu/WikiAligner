"""Check that an installed or packaged WikiAligner really works. Standard library only.

    python packaging/smoke_test.py dist/WikiAligner.app/Contents/MacOS/WikiAligner
    python packaging/smoke_test.py "C:/.../WikiAligner.exe" --offline-model
    python packaging/smoke_test.py uv run --no-dev -m wikialigner

Starts the app's local server, aligns two short texts with the default model, aligns a real
Wikipedia revision and exports to Excel. ``--offline-model`` forbids Hugging Face access to
prove the bundled model is used. Exits non-zero and prints the app log on failure.
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


def call(base: str, path: str, body: dict | None = None, timeout: float = 30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, headers={"Content-Type": "application/json"} if data else {})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def wait_job(base: str, job: dict, limit: float) -> dict:
    end = time.time() + limit
    while time.time() < end:
        j = call(base, f"/api/jobs/{job['id']}")
        if j["status"] == "done":
            return j["result"]
        if j["status"] == "error":
            raise RuntimeError(j["error"])
        time.sleep(1)
    raise TimeoutError(f"job still '{j['status']}: {j['progress']}' after {limit:.0f}s")


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    offline = "--offline-model" in argv
    command = [a for a in argv if a != "--offline-model"]
    if not command:
        print(__doc__)
        return 2
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    data_dir = Path(tempfile.mkdtemp(prefix="wikialigner-smoke-"))
    env = {**os.environ, "WIKIALIGNER_DATA_DIR": str(data_dir), "WIKIALIGNER_CACHE_DIR": str(data_dir / "cache")}
    if offline:  # no network for models and an empty model cache: only the bundled model can work
        env.update(HF_HUB_OFFLINE="1", HF_HOME=str(data_dir / "hf"))
    proc = subprocess.Popen(command + ["--serve", "--port", str(port)], env=env)
    try:
        for _ in range(240):
            try:
                print("health:", call(base, "/api/health", timeout=2), flush=True)
                break
            except OSError:
                if proc.poll() is not None:
                    raise RuntimeError(f"app exited with code {proc.returncode}")
                time.sleep(1)
        else:
            raise TimeoutError("server did not start in 240s")

        models = call(base, "/api/models")
        default = next(m for m in models["models"] if m["key"] == models["default"])
        print("default model:", default["key"], "| available:", default["downloaded"], "| memory:", models["memory_gb"], flush=True)
        assert default["downloaded"] or not offline, "default model is not bundled"

        result = wait_job(base, call(base, "/api/align", {
            "left": {"type": "text", "lang": "en", "text": "The bridge is near the Kremlin.\n\nThousands marched in his memory."},
            "right": {"type": "text", "lang": "zh", "text": "数千人参加了悼念他的游行。这座桥靠近克里姆林宫。"},
            "options": {"min_margin": 0.9},
        }), 900)
        pairs = {(p["src"], p["tgt"]) for p in result["pairs"]}
        print("text alignment:", pairs, "| model:", result["model"]["id"], "| seconds:", result["stats"]["seconds"], flush=True)
        assert pairs == {(0, 1), (1, 0)}, "wrong pairs for the text alignment"

        wiki = wait_job(base, call(base, "/api/align", {
            "left": {"type": "wiki", "lang": "en", "title": "Assassination of Boris Nemtsov", "date": "2015-03-10"},
            "right": {"type": "wiki", "lang": "ru", "title": "Убийство Бориса Немцова", "date": "2015-03-10"},
        }), 900)
        print("wikipedia alignment:", wiki["stats"], flush=True)
        assert wiki["stats"]["pairs"] > 20, "too few pairs for the Wikipedia alignment"

        call(base, "/api/settings", {"export_dir": str(data_dir / "out")})
        path = call(base, "/api/export", {"run_id": wiki["id"], "format": "xlsx"})["path"]
        assert Path(path).stat().st_size > 1000, "empty export"
        print("export:", path, flush=True)
        print("SMOKE TEST PASSED", flush=True)
        return 0
    except Exception as e:
        print(f"SMOKE TEST FAILED: {e}", flush=True)
        log = data_dir / "wikialigner.log"
        if log.exists():
            print("--- app log ---\n" + log.read_text(encoding="utf-8", errors="replace")[-6000:], flush=True)
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(10)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
