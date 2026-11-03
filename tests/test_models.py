from fastapi.testclient import TestClient

from wikialigner.models import REGISTRY, benchmark_summary, load_benchmark, spec_for
from wikialigner.server import create_app

BENCH = {"models": {"m": {
    "sentences_per_second": 100.0,
    "margin": {
        "best": {"threshold": 1.1, "precision": 0.95, "recall": 0.97, "f1": 0.96},
        "curve": [[1.0, 0.80, 0.99, 0.88], [1.1, 0.95, 0.97, 0.96], [1.15, 0.975, 0.93, 0.952], [1.2, 0.99, 0.85, 0.915]],
    },
    "per_language": {"zh": {"margin": {"f1": 0.95}}},
}}}


def test_recommended_threshold_is_lowest_with_high_precision():
    s = benchmark_summary("m", BENCH)
    assert s["best_threshold"] == 1.1
    assert s["recommended_threshold"] == 1.15 and s["precision"] == 0.975
    assert s["per_language"] == {"zh": 0.95}
    assert benchmark_summary("missing", BENCH) is None


def test_recommended_threshold_falls_back_to_best_f1():
    assert benchmark_summary("m", BENCH, min_precision=0.999)["recommended_threshold"] == 1.1


def test_registry_entries_are_complete():
    for key, spec in REGISTRY.items():
        assert spec.key == key
        assert spec.note_zh and spec.note_en and spec.license and spec.tier
        assert spec_for(spec.model_id) is spec
    # Instruction-tuned models must get their prompt; plain encoders must not.
    assert REGISTRY["e5-large-instruct"].prompt.startswith("Instruct:")
    assert REGISTRY["e5-small"].prompt == "query: "
    assert REGISTRY["labse"].prompt is None


def test_shipped_benchmark_covers_registry():
    bench = load_benchmark()
    tested = set(bench.get("models", {}))
    assert {k for k, s in REGISTRY.items() if s.tier != "large"} <= tested


def test_models_endpoint_reports_benchmark_and_memory(fake_embedder, tmp_path):
    client = TestClient(create_app())
    data = client.get("/api/models").json()
    labse = next(m for m in data["models"] if m["key"] == "labse")
    assert labse["benchmark"]["recommended_threshold"] > 1.0
    assert data["benchmark_setup"]["languages"]
    assert data["memory_gb"] is None or data["memory_gb"] > 0


def test_bundled_model_counts_as_downloaded(tmp_path, monkeypatch):
    import wikialigner.models as m
    monkeypatch.setattr(m, "BUNDLED_DIR", tmp_path)
    assert m.bundled_model_path("org/model") is None
    (tmp_path / "org--model").mkdir()
    (tmp_path / "org--model" / "config.json").write_text("{}")
    assert m.bundled_model_path("org/model") == tmp_path / "org--model"
    assert m.is_downloaded("org/model")


def test_mirror_is_used_only_when_hugging_face_is_unreachable(monkeypatch):
    import wikialigner.config as c
    for var in ("HF_ENDPOINT", "HF_HUB_OFFLINE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setattr(c, "_reachable", lambda url, timeout=2.5: True)
    c.apply_startup_environment(c.Settings())
    assert "HF_ENDPOINT" not in c.os.environ
    monkeypatch.setattr(c, "_reachable", lambda url, timeout=2.5: url == c.HF_MIRROR)
    c.apply_startup_environment(c.Settings())
    assert c.os.environ["HF_ENDPOINT"] == c.HF_MIRROR
    monkeypatch.delenv("HF_ENDPOINT")
