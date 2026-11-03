"""Download the default model into wikialigner/bundled_models so the installers can include it."""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from huggingface_hub import snapshot_download  # noqa: E402

from wikialigner.models import BUNDLED_DIR, DEFAULT_MODEL, resolve_model_id  # noqa: E402

model_id = resolve_model_id(DEFAULT_MODEL)
target = BUNDLED_DIR / model_id.replace("/", "--")
snapshot_download(model_id, local_dir=target, ignore_patterns=[".gitattributes", "mteb_*", "onnx/*", "openvino/*"])
shutil.rmtree(target / ".cache", ignore_errors=True)  # download bookkeeping, not needed at run time
print(f"{model_id} -> {target}")
