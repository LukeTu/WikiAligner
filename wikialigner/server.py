"""Local HTTP API and static UI. Binds to 127.0.0.1 only; the desktop shell opens it in a window."""
from __future__ import annotations

import base64
import io
import platform
import shutil
import subprocess
import sys
import webbrowser
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import __version__
from .config import HTML_CACHE_DIR, RUNS_DIR, Settings, load_settings, save_settings
from .export import FORMATS, export
from .history import compare_traces, is_content_translation, trace_first_appearance
from .jobs import JobManager, RunStore
from .models import REGISTRY, ModelManager, benchmark_summary, is_downloaded, load_benchmark, resolve_model_id
from .pipeline import AlignOptions, SourceSpec, run_alignment
from .wiki import VARIANTS, WikiClient, WikiError, cache_size_bytes, check_lang, diff_url

WEB_DIR = Path(__file__).parent / "web"


class AlignRequest(BaseModel):
    left: dict
    right: dict
    options: dict = {}


class TraceRequest(BaseModel):
    lang: str
    title: str
    revid: int
    text: str
    variant: str | None = None
    fuzzy: float | None = None


class TracePairRequest(BaseModel):
    left: TraceRequest
    right: TraceRequest


class ExportRequest(BaseModel):
    run_id: str
    format: str = "xlsx"


class FileRequest(BaseModel):
    name: str
    data: str  # base64


class PathRequest(BaseModel):
    path: str


class UrlRequest(BaseModel):
    url: str


def _memory_gb() -> float | None:
    """Physical memory, used to warn before choosing a model that will not fit."""
    try:
        if sys.platform == "darwin":
            out = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True, timeout=2).stdout
            return round(int(out.strip()) / 2**30, 1)
        if sys.platform.startswith("win"):
            import ctypes

            class MemStatus(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MemStatus()
            m.dwLength = ctypes.sizeof(MemStatus)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return round(m.ullTotalPhys / 2**30, 1)
        import os
        return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2**30, 1)
    except Exception:
        return None


def create_app(models: ModelManager | None = None, client: WikiClient | None = None,
               runs: RunStore | None = None) -> FastAPI:
    app = FastAPI(title="WikiAligner", version=__version__)
    # Refuse requests addressed to any other host name, so a web page cannot reach this
    # local API through DNS rebinding. Browsers already block cross-origin JSON posts.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "testserver"])
    state = {"settings": load_settings()}
    models = models or ModelManager()
    runs = runs or RunStore(RUNS_DIR)
    jobs = JobManager()
    state["client"] = client or WikiClient(proxy=state["settings"].proxy)

    def wiki() -> WikiClient:
        return state["client"]

    def guard(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except WikiError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # ------------------------------------------------------------------ app
    @app.get("/api/health")
    def health():
        return {"ok": True, "version": __version__, "platform": platform.system()}

    @app.get("/api/settings")
    def get_settings():
        s = state["settings"]
        return {**asdict(s), "export_dir_resolved": str(s.resolved_export_dir()),
                "cache_bytes": cache_size_bytes(), "runs_dir": str(runs.dir)}

    @app.post("/api/settings")
    def set_settings(body: dict):
        current = asdict(state["settings"])
        current.update({k: v for k, v in body.items() if k in current})
        s = Settings(**current)
        save_settings(s)
        if s.proxy != state["settings"].proxy:
            state["client"] = WikiClient(proxy=s.proxy)
        state["settings"] = s
        return get_settings()

    @app.post("/api/cache/clear")
    def clear_cache():
        shutil.rmtree(HTML_CACHE_DIR, ignore_errors=True)
        return {"cache_bytes": 0}

    @app.get("/api/models")
    def list_models():
        s = state["settings"]
        bench = load_benchmark()
        entries = [{**spec.to_dict(), "downloaded": is_downloaded(spec.model_id),
                    "benchmark": benchmark_summary(spec.key, bench)} for spec in REGISTRY.values()]
        for line in s.custom_models.splitlines():
            mid = line.strip()
            if mid and mid not in {e["model_id"] for e in entries}:
                entries.append({"key": mid, "model_id": mid, "label": mid.split("/")[-1], "tier": "custom",
                                "params": "", "download": "", "languages": "", "license": "", "note_zh": "",
                                "note_en": "", "sources": [], "min_ram_gb": 0, "benchmark": None,
                                "downloaded": is_downloaded(mid)})
        loaded = set(models.loaded())
        for e in entries:
            e["loaded"] = e["model_id"] in loaded
        return {"models": entries, "default": s.default_model, "benchmark_setup": bench.get("setup"),
                "memory_gb": _memory_gb()}

    @app.post("/api/models/{key:path}/load")
    def load_model(key: str):
        job = jobs.submit("load_model", lambda progress: {"model": resolve_model_id(key),
                                                          "dim": models.get(key, progress).dim})
        return job.to_dict()

    # ------------------------------------------------------------------ wikipedia
    @app.get("/api/search")
    def search(lang: str, q: str):
        return {"titles": guard(wiki().search, lang, q)}

    @app.get("/api/page")
    def page(lang: str, title: str):
        info = guard(wiki().page_info, lang, title)
        return {**asdict(info), "variants": VARIANTS.get(info.lang, [])}

    @app.get("/api/revisions")
    def revisions(lang: str, title: str, limit: int = 50, start: str | None = None, cont: str | None = None):
        def fetch():
            from .wiki import normalize_timestamp
            revs, nxt = wiki().revisions(lang, title, limit=limit,
                                         start=normalize_timestamp(start) if start else None, cont=cont)
            return revs, nxt
        revs, nxt = guard(fetch)
        return {"revisions": [{**r.to_dict(), "content_translation": is_content_translation(r),
                               "diff_url": diff_url(lang, r.revid)} for r in revs],
                "continue": nxt}

    @app.get("/api/variants")
    def variants(lang: str):
        return {"variants": VARIANTS.get(check_lang(lang), [])}

    # ------------------------------------------------------------------ jobs
    @app.post("/api/align")
    def align(req: AlignRequest):
        try:
            left, right = SourceSpec.from_dict(req.left), SourceSpec.from_dict(req.right)
            opts = AlignOptions.from_dict(req.options)
        except (TypeError, ValueError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        job = jobs.submit("align", lambda progress: run_alignment(left, right, opts, wiki(), models, progress),
                          on_done=runs.save)
        return job.to_dict()

    @app.post("/api/trace")
    def trace(req: TraceRequest):
        job = jobs.submit("trace", lambda progress: trace_first_appearance(
            wiki(), req.lang, req.title, req.text, req.revid, req.variant, req.fuzzy, progress))
        return job.to_dict()

    @app.post("/api/trace_pair")
    def trace_pair(req: TracePairRequest):
        def run(progress):
            a = trace_first_appearance(wiki(), req.left.lang, req.left.title, req.left.text, req.left.revid,
                                       req.left.variant, req.left.fuzzy, lambda s: progress(f"left {s}"))
            b = trace_first_appearance(wiki(), req.right.lang, req.right.title, req.right.text, req.right.revid,
                                       req.right.variant, req.right.fuzzy, lambda s: progress(f"right {s}"))
            return {"left": a, "right": b, "comparison": compare_traces(a, b)}
        return jobs.submit("trace_pair", run).to_dict()

    @app.get("/api/jobs/{job_id}")
    def job_status(job_id: str):
        job = jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Unknown job")
        return job.to_dict()

    # ------------------------------------------------------------------ runs and files
    @app.get("/api/runs")
    def list_runs():
        return {"runs": runs.list()}

    @app.get("/api/runs/{run_id}")
    def get_run(run_id: str):
        result = runs.load(run_id)
        if not result:
            raise HTTPException(status_code=404, detail="Unknown run")
        return result

    @app.delete("/api/runs/{run_id}")
    def delete_run(run_id: str):
        runs.delete(run_id)
        return {"ok": True}

    @app.post("/api/export")
    def export_run(req: ExportRequest):
        if req.format not in FORMATS:
            raise HTTPException(status_code=400, detail=f"format must be one of {FORMATS}")
        result = runs.load(req.run_id)
        if not result:
            raise HTTPException(status_code=404, detail="Unknown run")
        path = export(result, req.format, state["settings"].resolved_export_dir())
        return {"path": str(path)}

    @app.post("/api/read_file")
    def read_file(req: FileRequest):
        raw = base64.b64decode(req.data)
        name = req.name.lower()
        if name.endswith(".docx"):
            import docx
            d = docx.Document(io.BytesIO(raw))
            text = "\n\n".join(p.text for p in d.paragraphs if p.text.strip())
        else:
            for enc in ("utf-8-sig", "utf-16", "gb18030", "latin-1"):
                try:
                    text = raw.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
        return {"text": text}

    @app.post("/api/reveal")
    def reveal(req: PathRequest):
        p = Path(req.path)
        if not p.exists():
            raise HTTPException(status_code=404, detail="File not found")
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(p)])
        elif sys.platform.startswith("win"):
            subprocess.Popen(["explorer", "/select,", str(p)])
        else:
            subprocess.Popen(["xdg-open", str(p.parent)])
        return {"ok": True}

    @app.post("/api/open_url")
    def open_url(req: UrlRequest):
        if not req.url.startswith(("https://", "http://")):
            raise HTTPException(status_code=400, detail="Only web links can be opened")
        webbrowser.open(req.url)
        return {"ok": True}

    # ------------------------------------------------------------------ UI
    @app.get("/")
    def index():
        return FileResponse(WEB_DIR / "index.html", headers={"Cache-Control": "no-store"})

    app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
    return app
