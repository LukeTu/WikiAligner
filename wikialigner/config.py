"""Paths, network identity and user settings shared across the app."""
from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass, fields
from pathlib import Path

from platformdirs import user_cache_dir, user_data_dir, user_downloads_dir

from . import __version__

APP_NAME = "WikiAligner"
USER_AGENT = (
    f"WikiAligner/{__version__} "
    "(https://github.com/LukeTu/WikiAligner; desktop research tool)"
)

CACHE_DIR = Path(os.environ.get("WIKIALIGNER_CACHE_DIR") or user_cache_dir(APP_NAME, appauthor=False))
DATA_DIR = Path(os.environ.get("WIKIALIGNER_DATA_DIR") or user_data_dir(APP_NAME, appauthor=False))
HTML_CACHE_DIR = CACHE_DIR / "html"
RUNS_DIR = DATA_DIR / "runs"
SETTINGS_FILE = DATA_DIR / "settings.json"
LOG_FILE = DATA_DIR / "wikialigner.log"
HF_MIRROR = "https://hf-mirror.com"


@dataclass
class Settings:
    ui_language: str = "bi"  # zh | en | bi (Chinese and English together)
    # Hugging Face endpoint used for the first model download, e.g. https://hf-mirror.com.
    # Read once at start-up, so a change takes effect after a restart.
    hf_endpoint: str = ""
    # Explicit proxy for Wikipedia requests. Empty means use the system proxy settings.
    proxy: str = ""
    export_dir: str = ""
    default_model: str = "harrier-270m"  # the model shipped with the installers
    custom_models: str = ""  # one Hugging Face model id per line

    def resolved_export_dir(self) -> Path:
        if self.export_dir:
            return Path(self.export_dir).expanduser()
        return Path(user_downloads_dir()) / APP_NAME


_lock = threading.Lock()


def load_settings() -> Settings:
    with _lock:
        try:
            raw = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return Settings()
    known = {f.name for f in fields(Settings)}
    return Settings(**{k: v for k, v in raw.items() if k in known})


def save_settings(settings: Settings) -> None:
    with _lock:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        tmp = SETTINGS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(settings), ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(SETTINGS_FILE)


def _reachable(url: str, timeout: float = 2.5) -> bool:
    import requests

    try:
        requests.head(url, timeout=timeout)
        return True  # the server answered, whatever the status
    except requests.RequestException:
        return False


def apply_startup_environment(settings: Settings) -> None:
    """Set environment variables that libraries read at import time."""
    if settings.hf_endpoint:
        os.environ.setdefault("HF_ENDPOINT", settings.hf_endpoint.rstrip("/"))
    elif not (os.environ.get("HF_ENDPOINT") or os.environ.get("HF_HUB_OFFLINE")):
        # huggingface.co cannot be reached from mainland China; downloads work through the mirror.
        if not _reachable("https://huggingface.co") and _reachable(HF_MIRROR):
            os.environ["HF_ENDPOINT"] = HF_MIRROR
    # Tokenizers spawn worker threads that do not play well with our job threads.
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
