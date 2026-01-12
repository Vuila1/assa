"""Helper utilities."""
import json
from typing import Any


def clamp(value: float, minv: float, maxv: float) -> float:
    return max(minv, min(value, maxv))


def load_config(path: str) -> dict[str, Any]:
    """Load configuration from a JSON file. Returns empty dict on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
