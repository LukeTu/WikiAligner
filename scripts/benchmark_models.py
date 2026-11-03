"""Benchmark embedding models inside WikiAligner's own alignment pipeline.

Simulates the real task: an English text and a partial translation of it that also
contains unrelated sentences. Built from NTREX-128 (news, 1997 sentences in 128 languages,
CC BY-SA 4.0). For each episode:

  source  = 300 consecutive English sentences
  target  = translations of a random half of them + 150 unrelated target-language sentences
            taken from the text that follows

Each model embeds both sides, ``align_documents`` pairs them (greedy one-to-one, k=4,
minimum margin 1.0), and precision/recall/F1 are computed against the known pairs while
sweeping the display threshold on cosine and on margin. Results are written to
``wikialigner/model_benchmark.json`` and shown in the app's model chooser.

    uv run python scripts/benchmark_models.py                 # all registry models except "large"
    uv run python scripts/benchmark_models.py labse bge-m3    # selected models
"""
from __future__ import annotations

import json
import platform
import random
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from wikialigner.align import AlignParams, align_documents  # noqa: E402
from wikialigner.models import BENCHMARK_FILE, REGISTRY, SentenceTransformerEmbedder  # noqa: E402

DATA_DIR = ROOT / "benchmarks" / "ntrex"
LANGS = {"zh": "zho_Hans", "ru": "rus_Cyrl", "de": "deu_Latn", "ja": "jpn_Jpan", "ar": "arb_Arab",
         "ko": "kor_Hang", "th": "tha_Thai", "sw": "swa_Latn", "ta": "tam_Taml", "am": "amh_Ethi"}
EPISODES = 3
SRC_LEN, KEEP, DISTRACTORS = 300, 0.5, 150


def fetch_ntrex(config: str) -> list[str]:
    path = DATA_DIR / f"{config}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    listing = f"https://huggingface.co/api/datasets/davidstap/NTREX/tree/main/data/{config}"
    with urllib.request.urlopen(listing, timeout=60) as r:
        name = json.load(r)[0]["path"]
    with urllib.request.urlopen(f"https://huggingface.co/datasets/davidstap/NTREX/resolve/main/{name}", timeout=120) as r:
        rows = r.read().decode("utf-8").rstrip("\n").split("\n")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def episodes(en: list[str], tgt: list[str], seed: int = 13):
    rng = random.Random(seed)
    stride = (len(en) - SRC_LEN - DISTRACTORS) // EPISODES
    for e in range(EPISODES):
        start = e * stride
        src_idx = list(range(start, start + SRC_LEN))
        kept = sorted(rng.sample(src_idx, int(SRC_LEN * KEEP)))
        distract = list(range(start + SRC_LEN, start + SRC_LEN + DISTRACTORS))
        tgt_idx = kept + distract
        rng.shuffle(tgt_idx)
        gold = {(src_idx.index(i), tgt_idx.index(i)) for i in kept}
        yield [en[i] for i in src_idx], [tgt[i] for i in tgt_idx], gold


def prf(pred: set, gold: set) -> tuple[float, float, float]:
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 1.0
    r = tp / len(gold) if gold else 1.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def sweep(runs: list[tuple[list[dict], set]], key: str, grid: np.ndarray) -> dict:
    best = {"f1": -1}
    curve = []
    for th in grid:
        scores = []
        for pairs, gold in runs:
            pred = {(p["src"], p["tgt"]) for p in pairs if (p[key] or 0) >= th}
            scores.append(prf(pred, gold))
        p, r, f = (float(np.mean([s[i] for s in scores])) for i in range(3))
        curve.append((round(float(th), 3), round(p, 4), round(r, 4), round(f, 4)))
        if f > best["f1"]:
            best = {"threshold": round(float(th), 3), "precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)}
    return {"best": best, "curve": curve}


def benchmark(key: str, data: dict[str, tuple[list[str], list[str]]]) -> dict:
    spec = REGISTRY[key]
    t0 = time.time()
    emb = SentenceTransformerEmbedder(spec.model_id, prompt=spec.prompt)
    load_s = time.time() - t0
    emb.encode(["warm up"])
    runs_all, per_lang, n_sent, enc_s = [], {}, 0, 0.0
    for lang, (en, tgt) in data.items():
        runs = []
        for src, trg, gold in episodes(en, tgt):
            t = time.time()
            e1, e2 = emb.encode(src), emb.encode(trg)
            enc_s += time.time() - t
            n_sent += len(src) + len(trg)
            res = align_documents(src, trg, e1, e2, [True] * len(src), [True] * len(trg),
                                  AlignParams(k=4, min_margin=1.0, strategy="greedy"))
            runs.append((res["pairs"], gold))
        per_lang[lang] = {"cos": sweep(runs, "cos", np.arange(0.3, 0.96, 0.01))["best"],
                          "margin": sweep(runs, "margin", np.arange(1.0, 1.6, 0.005))["best"]}
        runs_all += runs
    out = {
        "model_id": spec.model_id,
        "dim": emb.dim,
        "device": emb.device,
        "load_seconds": round(load_s, 1),
        "sentences_per_second": round(n_sent / enc_s, 1) if enc_s else None,
        "cos": sweep(runs_all, "cos", np.arange(0.3, 0.96, 0.01)),
        "margin": sweep(runs_all, "margin", np.arange(1.0, 1.6, 0.005)),
        "per_language": per_lang,
    }
    del emb
    return out


def main(keys: list[str]) -> None:
    keys = keys or [k for k, s in REGISTRY.items() if s.tier != "large"]
    en = fetch_ntrex("eng_Latn")
    data = {lang: (en, fetch_ntrex(cfg)) for lang, cfg in LANGS.items()}
    results = json.loads(BENCHMARK_FILE.read_text(encoding="utf-8")) if BENCHMARK_FILE.exists() else {}
    results.setdefault("models", {})
    results["setup"] = {
        "dataset": "NTREX-128 (davidstap/NTREX on Hugging Face), CC BY-SA 4.0",
        "languages": list(LANGS), "episodes_per_language": EPISODES,
        "source_sentences": SRC_LEN, "translated_share": KEEP, "unrelated_target_sentences": DISTRACTORS,
        "alignment": "greedy one-to-one, k=4, min margin 1.0", "machine": f"{platform.system()} {platform.machine()}",
    }
    for key in keys:
        print(f"== {key}", flush=True)
        try:
            r = benchmark(key, data)
        except Exception as e:  # keep going so one broken model does not stop the run
            print(f"   failed: {e}", flush=True)
            continue
        r["date"] = time.strftime("%Y-%m-%d")
        results["models"][key] = r
        b = r["margin"]["best"]
        print(f"   margin≥{b['threshold']}: P {b['precision']:.3f} R {b['recall']:.3f} F1 {b['f1']:.3f} · "
              f"cos best F1 {r['cos']['best']['f1']:.3f} @ {r['cos']['best']['threshold']} · "
              f"{r['sentences_per_second']} sent/s", flush=True)
        BENCHMARK_FILE.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
