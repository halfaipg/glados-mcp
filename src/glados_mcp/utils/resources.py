"""Locations of bundled data files and of the downloaded voice models.

Small lookup tables and sounds ship inside the package. The ONNX models are too
large for that (~300 MB), so they are downloaded once into a per-user cache
directory and verified against a SHA-256 checksum.
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
import urllib.request
from collections.abc import Callable
from pathlib import Path

logger = logging.getLogger(__name__)

PACKAGE_ROOT = Path(__file__).resolve().parent.parent

_RELEASE_URL = "https://github.com/dnhkng/GLaDOS/releases/download/0.1/"

# filename -> (sha256, size in bytes)
MODELS: dict[str, tuple[str, int]] = {
    "glados.onnx": (
        "17ea16dd18e1bac343090b8589042b4052f1e5456d42cad8842a4f110de25095",
        63_511_038,
    ),
    "kokoro-v1.0.fp16.onnx": (
        "c1610a859f3bdea01107e73e50100685af38fff88f5cd8e5c56df109ec880204",
        177_464_787,
    ),
    "kokoro-voices-v1.0.bin": (
        "c5adf5cc911e03b76fa5025c1c225b141310d0c4a721d6ed6e96e73309d0fd88",
        13_584_708,
    ),
    "phomenizer_en.onnx": (
        "b64dbbeca8b350927a0b6ca5c4642e0230173034abd0b5bb72c07680d700c5a0",
        61_141_157,
    ),
}


def data_path(name: str) -> Path:
    """Path to a data file bundled with the package."""
    return PACKAGE_ROOT / "data" / name


def sound_path(name: str) -> Path:
    """Path to a sound effect bundled with the package."""
    return PACKAGE_ROOT / "sounds" / name


def models_dir() -> Path:
    """Directory holding the downloaded models.

    Set GLADOS_MCP_MODELS_DIR to override the per-user cache location.
    """
    override = os.environ.get("GLADOS_MCP_MODELS_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Caches"
    else:
        base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    return base / "glados-mcp" / "models"


def model_path(name: str) -> Path:
    """Path to a downloaded model file (which may not exist yet)."""
    return models_dir() / name


def missing_models() -> list[str]:
    return [name for name in MODELS if not model_path(name).exists()]


def _download(name: str, on_bytes: Callable[[int], None]) -> None:
    expected_sha, _ = MODELS[name]
    target = model_path(name)
    partial = target.with_name(target.name + ".part")
    digest = hashlib.sha256()
    try:
        with urllib.request.urlopen(_RELEASE_URL + name, timeout=60) as response:
            with partial.open("wb") as out:
                while chunk := response.read(1 << 20):
                    out.write(chunk)
                    digest.update(chunk)
                    on_bytes(len(chunk))
        if digest.hexdigest() != expected_sha:
            raise RuntimeError(f"Checksum mismatch for {name}; the download is corrupt.")
        # Only a fully verified file ever gets the final name.
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)


def ensure_models(progress: Callable[[int, int], None] | None = None) -> None:
    """Download any models that are not in the cache yet.

    Args:
        progress: called with (bytes downloaded so far, total bytes).
    """
    missing = missing_models()
    if not missing:
        return
    models_dir().mkdir(parents=True, exist_ok=True)
    total = sum(MODELS[name][1] for name in missing)
    done = 0

    def on_bytes(count: int) -> None:
        nonlocal done
        done += count
        if progress:
            progress(done, total)

    for name in missing:
        logger.info("Downloading %s to %s", name, models_dir())
        _download(name, on_bytes)
