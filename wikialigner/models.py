"""Sentence-embedding models: a curated registry, lazy loading and an in-memory vector cache.

The registry notes come from published benchmarks (cited in ``sources``) and from
``scripts/benchmark_models.py``, which runs each model through WikiAligner's own
alignment on NTREX-128 and stores the results in ``model_benchmark.json``.
"""
from __future__ import annotations

import hashlib
import json
import threading
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Protocol

import numpy as np

BENCHMARK_FILE = Path(__file__).with_name("model_benchmark.json")
# Models shipped inside the installers (see packaging/fetch_model.py), so the app works right after
# installing, with no download and no access to Hugging Face.
BUNDLED_DIR = Path(__file__).with_name("bundled_models")
DEFAULT_MODEL = "harrier-270m"

# Instruction used by instruction-tuned models for parallel-sentence search. Bitext mining is
# symmetric, so the same prompt is applied to both sides.
BITEXT_INSTRUCTION = "Instruct: Retrieve parallel sentences\nQuery: "


@dataclass(frozen=True)
class ModelSpec:
    key: str
    model_id: str
    label: str
    params: str
    download: str
    languages: str
    license: str
    tier: str                    # recommended | alternative | light | general | large
    note_zh: str
    note_en: str
    prompt: str | None = None    # prepended to every sentence on both sides
    sources: tuple[str, ...] = ()
    min_ram_gb: int = 8

    def to_dict(self) -> dict:
        return asdict(self)


REGISTRY: dict[str, ModelSpec] = {
    s.key: s for s in [
        ModelSpec(
            "labse", "sentence-transformers/LaBSE", "LaBSE", "471M", "1.9 GB", "109", "Apache-2.0", "recommended",
            "专为双语句对挖掘训练，也是论文和第一版使用的模型，结果可与旧版比较。本机评测与 Harrier 270M 并列最好，"
            "在 Apple 芯片上速度最快。泰语略弱；输入超过 256 token 会被截断，按段落对齐时建议换用 BGE-M3 或 Harrier。",
            "Trained for bitext mining and used by the paper and the first version, so results stay comparable. "
            "Ties with Harrier 270M for the best local score and is the fastest on Apple silicon. Slightly weaker on Thai; input "
            "beyond 256 tokens is cut, so prefer BGE-M3 or Harrier for paragraph-level alignment.",
            sources=("https://arxiv.org/abs/2007.01852",),
        ),
        ModelSpec(
            "harrier-270m", "microsoft/harrier-oss-v1-270m", "Harrier OSS v1 270M", "270M", "0.5 GB", "94", "MIT",
            "recommended",
            "默认模型，随安装包附带，无需下载。微软 2026 年 4 月发布，MMTEB v2 平均 66.5。本机评测与 LaBSE 并列最好，"
            "十种语言都很稳定（包括 LaBSE 稍弱的泰语）。在 Apple 芯片上速度约为 LaBSE 的三分之一，在纯 CPU 上略快于 LaBSE。"
            "自带平行句检索指令，已自动使用。",
            "Default, included in the installers with nothing to download. Released by Microsoft in April 2026; "
            "MMTEB v2 average 66.5. Ties with LaBSE for the best local score and is steady across all ten languages, "
            "including Thai where LaBSE dips. About a third of LaBSE's speed on Apple silicon and slightly faster than "
            "LaBSE on a plain CPU. Its parallel-sentence instruction is applied automatically.",
            prompt=BITEXT_INSTRUCTION, min_ram_gb=4,
            sources=("https://huggingface.co/microsoft/harrier-oss-v1-270m",
                     "https://blogs.bing.com/search/April-2026/Microsoft-Open-Sources-Industry-Leading-Embedding-Model"),
        ),
        ModelSpec(
            "e5-large-instruct", "intfloat/multilingual-e5-large-instruct", "Multilingual E5 large instruct",
            "560M", "2.2 GB", "100+", "MIT", "alternative",
            "MTEB 多语言 bitext 80.1，公开评测第一梯队。本机评测召回率最高，适合尽量不漏掉译文的场景。"
            "它的余弦分数整体偏高，请按 margin 筛选（已自动设置）。",
            "MTEB multilingual bitext 80.1, in the top published cluster. Highest recall in the local test, useful "
            "when missing a translation costs more than checking extra pairs. Its cosines run high, so filter by "
            "margin (set automatically).",
            prompt=BITEXT_INSTRUCTION,
            sources=("https://arxiv.org/abs/2402.05672", "https://arxiv.org/abs/2605.31142"),
        ),
        ModelSpec(
            "bge-m3", "BAAI/bge-m3", "BGE-M3", "568M", "2.3 GB", "100+", "MIT", "alternative",
            "2026 年 MMTEB 稳健性研究中 bitext mining 五种语言都排第一梯队；MTEB 多语言 bitext 79.1。"
            "本机评测略低于前几名，阿姆哈拉语稍弱。能处理较长输入，适合按段落对齐。",
            "Top bitext-mining cluster in all five languages of a 2026 MMTEB robustness study; MTEB multilingual "
            "bitext 79.1. Slightly behind the leaders locally, weaker on Amharic. Handles longer input, so it suits "
            "paragraph-level alignment.",
            sources=("https://arxiv.org/abs/2605.31142", "https://github.com/QwenLM/Qwen3-Embedding"),
        ),
        ModelSpec(
            "harrier-0.6b", "microsoft/harrier-oss-v1-0.6b", "Harrier OSS v1 0.6B", "0.6B", "1.2 GB", "94",
            "MIT", "alternative",
            "Harrier 的中型版，MMTEB v2 平均 69.0。本机评测与 270M 版相当，但在笔记本上慢得多，一般不必选它。",
            "Mid-size Harrier, MMTEB v2 average 69.0. Scores like the 270M version locally but runs far slower on a "
            "laptop, so the 270M version is usually the better pick.",
            prompt=BITEXT_INSTRUCTION,
            sources=("https://huggingface.co/microsoft/harrier-oss-v1-0.6b",),
        ),
        ModelSpec(
            "e5-small", "intfloat/multilingual-e5-small", "Multilingual E5 small", "118M", "0.5 GB", "100", "MIT",
            "light",
            "体积小、速度很快，准确率比推荐模型低几个百分点。适合内存小的电脑或快速预览。",
            "Small and very fast, a few points below the recommended models. Good for low-memory computers or a "
            "quick first look.",
            prompt="query: ", min_ram_gb=4,
            sources=("https://arxiv.org/abs/2402.05672",),
        ),
        ModelSpec(
            "minilm", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "Multilingual MiniLM",
            "118M", "0.5 GB", "50+", "Apache-2.0", "light",
            "最快，但为释义而非翻译训练；在斯瓦希里语、泰米尔语、阿姆哈拉语等它不支持的语言上几乎失效。"
            "只建议用于主要语言的快速预览。",
            "Fastest, but trained for paraphrase rather than translation, and close to useless for languages it "
            "does not cover, such as Swahili, Tamil and Amharic. Use only for a quick look at major languages.",
            min_ram_gb=4,
        ),
        ModelSpec(
            "qwen3-0.6b", "Qwen/Qwen3-Embedding-0.6B", "Qwen3-Embedding 0.6B", "0.6B", "1.2 GB", "100+",
            "Apache-2.0", "general",
            "通用检索模型，找译文较弱：MTEB 多语言 bitext 72.2，本机评测在阿姆哈拉语、斯瓦希里语上明显下降，"
            "而且较慢。不建议用于本工具。",
            "A general retrieval model that is weak at finding translations: MTEB multilingual bitext 72.2, and in "
            "the local test it drops sharply on Amharic and Swahili. It is also slow. Not advised for this tool.",
            prompt=BITEXT_INSTRUCTION,
            sources=("https://github.com/QwenLM/Qwen3-Embedding",),
        ),
        ModelSpec(
            "qwen3-4b", "Qwen/Qwen3-Embedding-4B", "Qwen3-Embedding 4B", "4B", "8 GB", "100+", "Apache-2.0",
            "large",
            "MTEB 多语言 bitext 79.4，明显强于 0.6B 版；需要 16 GB 以上内存，笔记本上很慢。未做本机评测。",
            "MTEB multilingual bitext 79.4, much stronger than the 0.6B version; needs 16 GB+ of memory and is "
            "slow on a laptop. Not benchmarked locally.",
            prompt=BITEXT_INSTRUCTION, min_ram_gb=16,
            sources=("https://github.com/QwenLM/Qwen3-Embedding",),
        ),
    ]
}


def load_benchmark() -> dict:
    try:
        return json.loads(BENCHMARK_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def benchmark_summary(key: str, bench: dict | None = None, min_precision: float = 0.97) -> dict | None:
    """Local benchmark results for one model, with a recommended display threshold.

    The recommended margin threshold is the lowest one whose precision reaches
    ``min_precision``: researchers check candidates by hand, so a short list of mostly
    correct pairs is worth more than a few extra pairs.
    """
    b = (bench if bench is not None else load_benchmark()).get("models", {}).get(key)
    if not b:
        return None
    curve = b["margin"]["curve"]  # (threshold, precision, recall, f1), ascending threshold
    rec = next((c for c in curve if c[1] >= min_precision), None)
    best = b["margin"]["best"]
    if rec is None:
        rec = (best["threshold"], best["precision"], best["recall"], best["f1"])
    return {
        "f1": best["f1"],
        "best_threshold": best["threshold"],
        "recommended_threshold": rec[0],
        "precision": rec[1],
        "recall": rec[2],
        "f1_at_recommended": rec[3],
        "sentences_per_second": b.get("sentences_per_second"),
        "device": b.get("device"),
        "per_language": {lang: v["margin"]["f1"] for lang, v in b.get("per_language", {}).items()},
        "date": b.get("date"),
    }


def resolve_model_id(key_or_id: str) -> str:
    spec = REGISTRY.get(key_or_id)
    return spec.model_id if spec else key_or_id


def spec_for(key_or_id: str) -> ModelSpec | None:
    if key_or_id in REGISTRY:
        return REGISTRY[key_or_id]
    return next((s for s in REGISTRY.values() if s.model_id == key_or_id), None)


def bundled_model_path(model_id: str) -> Path | None:
    path = BUNDLED_DIR / model_id.replace("/", "--")
    return path if (path / "config.json").exists() else None


def is_downloaded(model_id: str) -> bool:
    if bundled_model_path(model_id):
        return True
    try:
        from huggingface_hub import try_to_load_from_cache
    except ImportError:
        return False
    hit = try_to_load_from_cache(model_id, "config.json")
    return isinstance(hit, str)


class Embedder(Protocol):
    name: str
    dim: int

    def encode(self, texts: list[str], progress: Callable[[str], None] | None = None) -> np.ndarray: ...


def _load_sentence_transformer(model_id: str):
    """Load from the app bundle or the local cache without touching the network when possible."""
    import torch
    from sentence_transformers import SentenceTransformer

    kwargs = {}
    if not (torch.cuda.is_available() or torch.backends.mps.is_available()):
        # Some checkpoints are stored as bfloat16, which is about 7x slower on most CPUs.
        kwargs["model_kwargs"] = {"dtype": torch.float32}
    bundled = bundled_model_path(model_id)
    if bundled:
        return SentenceTransformer(str(bundled), **kwargs)
    if is_downloaded(model_id):
        try:
            return SentenceTransformer(model_id, local_files_only=True, **kwargs)
        except Exception:  # an interrupted download left only part of the files: fetch the rest
            pass
    return SentenceTransformer(model_id, **kwargs)


class SentenceTransformerEmbedder:
    """Wraps a sentence-transformers model; returns L2-normalised float32 vectors."""

    def __init__(self, model_id: str, prompt: str | None = None, max_seq_length: int = 512,
                 cache_size: int = 50_000):
        self.name = model_id
        self.prompt = prompt
        self._model = _load_sentence_transformer(model_id)
        if self._model.max_seq_length is None or self._model.max_seq_length > max_seq_length:
            self._model.max_seq_length = max_seq_length  # sentences rarely need more; bounds memory
        self.dim = int(self._model.get_sentence_embedding_dimension())
        self.device = str(self._model.device)
        self._lock = threading.Lock()
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self._cache_size = cache_size

    def encode(self, texts: list[str], progress: Callable[[str], None] | None = None) -> np.ndarray:
        keys = [hashlib.sha1(t.encode("utf-8")).hexdigest() for t in texts]
        with self._lock:
            missing = {}
            for key, text in zip(keys, texts):
                if key not in self._cache and key not in missing:
                    missing[key] = text
            if missing:
                if progress:
                    progress(f"encode {len(missing)}")
                vecs = self._encode_safely(list(missing.values()))
                for key, vec in zip(missing.keys(), vecs):
                    self._cache[key] = vec
                while len(self._cache) > self._cache_size:
                    self._cache.popitem(last=False)
            out = np.stack([self._cache[k] for k in keys]) if keys else np.zeros((0, self.dim), np.float32)
        return out.astype(np.float32)

    def _encode_once(self, texts: list[str]) -> np.ndarray:
        return self._model.encode(texts, prompt=self.prompt, batch_size=32, normalize_embeddings=True,
                                  convert_to_numpy=True, show_progress_bar=False)

    def _encode_safely(self, texts: list[str]) -> np.ndarray:
        try:
            return self._encode_once(texts)
        except RuntimeError:
            # Some operators are missing on Apple's MPS backend; fall back to the CPU once.
            if self.device.startswith("mps"):
                self._model.to("cpu").float()
                self.device = "cpu"
                return self._encode_once(texts)
            raise


class ModelManager:
    """Loads each model once per process and shares it between jobs."""

    def __init__(self):
        self._models: dict[str, Embedder] = {}
        self._lock = threading.Lock()

    def get(self, key_or_id: str, progress: Callable[[str], None] | None = None) -> Embedder:
        model_id = resolve_model_id(key_or_id)
        spec = spec_for(model_id)
        with self._lock:
            if model_id not in self._models:
                if progress:
                    progress("download_model" if not is_downloaded(model_id) else "load_model")
                self._models[model_id] = SentenceTransformerEmbedder(model_id, prompt=spec.prompt if spec else None)
            return self._models[model_id]

    def loaded(self) -> list[str]:
        return list(self._models)

    def register(self, embedder: Embedder) -> None:
        """Install a ready embedder (used by tests)."""
        self._models[embedder.name] = embedder
