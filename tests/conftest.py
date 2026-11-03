import hashlib
import os
import tempfile

import numpy as np
import pytest

# Keep tests away from the user's real settings, cache and saved runs.
_tmp = tempfile.mkdtemp(prefix="wikialigner-test-")
os.environ.setdefault("WIKIALIGNER_CACHE_DIR", os.path.join(_tmp, "cache"))
os.environ.setdefault("WIKIALIGNER_DATA_DIR", os.path.join(_tmp, "data"))


class FakeEmbedder:
    """Deterministic embeddings: texts that share a "concept" token map to nearby vectors.

    A text like "c3 the cat sat" is embedded near concept 3, so tests can say which
    sentences are translations of each other without a real model.
    """

    name = "fake"
    dim = 32

    def encode(self, texts, progress=None):
        out = []
        for t in texts:
            concept = next((w for w in t.split() if w.startswith("c") and w[1:].isdigit()), None)
            seed = int(hashlib.md5((concept or t).encode()).hexdigest()[:8], 16)
            base = np.random.default_rng(seed).normal(size=self.dim)
            noise = np.random.default_rng(int(hashlib.md5(t.encode()).hexdigest()[:8], 16)).normal(size=self.dim)
            v = base + (0.15 if concept else 1.0) * noise
            out.append(v / np.linalg.norm(v))
        return np.array(out, dtype=np.float32).reshape(len(texts), self.dim)


@pytest.fixture
def fake_embedder():
    return FakeEmbedder()
