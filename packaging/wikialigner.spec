# PyInstaller spec: builds WikiAligner.app on macOS and a WikiAligner folder with WikiAligner.exe on Windows.
# PyInstaller cannot cross-compile, so build each platform on that platform (see .github/workflows/build.yml).
#   uv run --group build pyinstaller packaging/wikialigner.spec --noconfirm
# Run packaging/fetch_model.py first to include the default model; other models download on first use.
import re
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules, copy_metadata

ROOT = Path(SPECPATH).parent
VERSION = re.search(r'"(.+)"', (ROOT / "wikialigner" / "__init__.py").read_text()).group(1)
datas = [(str(ROOT / "wikialigner" / "web"), "wikialigner/web"),
         (str(ROOT / "wikialigner" / "model_benchmark.json"), "wikialigner")]
if (ROOT / "wikialigner" / "bundled_models").is_dir():
    datas.append((str(ROOT / "wikialigner" / "bundled_models"), "wikialigner/bundled_models"))
binaries = []
hiddenimports = collect_submodules("wikialigner") + collect_submodules("uvicorn")

for pkg in ("sentence_transformers", "transformers", "tokenizers", "pysbd", "webview", "docx", "openpyxl"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

# Libraries that check their own installed version at import time.
for dist in ("torch", "transformers", "tokenizers", "huggingface_hub", "safetensors", "sentence_transformers",
             "tqdm", "regex", "requests", "packaging", "filelock", "numpy", "pyyaml", "scipy", "scikit-learn"):
    try:
        datas += copy_metadata(dist)
    except Exception:
        pass

if sys.platform == "win32":
    for pkg in ("clr_loader", "pythonnet"):
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h

a = Analysis(
    [str(ROOT / "packaging" / "launch.py")],
    pathex=[str(ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["tkinter", "matplotlib", "IPython", "jupyter", "notebook", "pytest", "torchvision", "torchaudio",
              "tensorflow", "jax", "flax", "keras"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name="WikiAligner",
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="WikiAligner")

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="WikiAligner.app",
        bundle_identifier="edu.hkbu.wikialigner",
        info_plist={
            "CFBundleShortVersionString": VERSION,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
        },
    )
