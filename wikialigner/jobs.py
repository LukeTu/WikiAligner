"""Background jobs with status the UI can poll, and a folder of saved alignment runs."""
from __future__ import annotations

import json
import logging
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .wiki import WikiError

log = logging.getLogger(__name__)


@dataclass
class Job:
    id: str
    kind: str
    status: str = "queued"          # queued | running | done | error
    progress: str = ""
    result: Any = None
    error: str = ""
    created: float = field(default_factory=time.time)

    def to_dict(self, with_result: bool = True) -> dict:
        d = {"id": self.id, "kind": self.kind, "status": self.status, "progress": self.progress,
             "error": self.error, "created": self.created}
        if with_result and self.status == "done":
            d["result"] = self.result
        return d


class JobManager:
    def __init__(self, workers: int = 2, keep: int = 50):
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="job")
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._keep = keep

    def submit(self, kind: str, fn: Callable[[Callable[[str], None]], Any],
               on_done: Callable[[Any], None] | None = None) -> Job:
        job = Job(uuid.uuid4().hex[:12], kind)
        with self._lock:
            self._jobs[job.id] = job
            for old in sorted(self._jobs.values(), key=lambda j: j.created)[:-self._keep]:
                if old.status in ("done", "error"):
                    del self._jobs[old.id]

        def progress(msg: str) -> None:
            job.progress = msg

        def run() -> None:
            job.status = "running"
            try:
                job.result = fn(progress)
                if on_done:
                    on_done(job.result)
                job.status = "done"
            except (WikiError, ValueError) as e:
                job.error, job.status = str(e), "error"
            except Exception as e:  # report unexpected failures instead of hanging the UI
                log.error("job %s failed\n%s", job.id, traceback.format_exc())
                job.error, job.status = f"{e.__class__.__name__}: {e}", "error"

        self._pool.submit(run)
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)


class RunStore:
    """Completed alignments saved as JSON so they can be reopened without recomputing."""

    def __init__(self, directory: Path):
        self.dir = directory

    def save(self, result: dict) -> None:
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / f"{result['id']}.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
        summary = {
            "id": result["id"], "created": result["created"], "mode": result["mode"],
            "left": _brief(result["left"]), "right": _brief(result["right"]),
            "model": result["model"]["id"], "stats": result["stats"],
        }
        (self.dir / f"{result['id']}.meta.json").write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")

    def list(self, limit: int = 200) -> list[dict]:
        if not self.dir.exists():
            return []
        metas = sorted(self.dir.glob("*.meta.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
        out = []
        for p in metas:
            try:
                out.append(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return out

    def load(self, run_id: str) -> dict | None:
        if not run_id.isalnum():
            return None
        p = self.dir / f"{run_id}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def delete(self, run_id: str) -> None:
        if run_id.isalnum():
            for p in (self.dir / f"{run_id}.json", self.dir / f"{run_id}.meta.json"):
                p.unlink(missing_ok=True)


def _brief(doc: dict) -> dict:
    rev = doc.get("revision") or {}
    return {"title": doc["title"], "lang": doc["lang"], "revid": rev.get("revid"),
            "timestamp": rev.get("timestamp"), "source": doc["source"]}
