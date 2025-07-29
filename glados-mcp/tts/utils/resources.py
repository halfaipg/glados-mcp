from functools import lru_cache
import os
from pathlib import Path


@lru_cache(maxsize=1)
def get_models_root() -> Path:
    """Get the absolute path to the models directory (cached)."""
    # Get the directory where this module is located (tts/utils/)
    utils_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    # Go up to the glados-mcp directory and into models
    return utils_dir.parent.parent / "models"


def resource_path(relative_path: str) -> Path:
    """Return absolute path to a model file."""
    return get_models_root() / relative_path
