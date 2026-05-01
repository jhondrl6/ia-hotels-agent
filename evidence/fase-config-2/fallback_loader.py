"""
Fallback value loader with schema validation.

Loads fallback values from config/fallbacks.yaml and provides:
- Schema validation (types, ranges)
- File-level caching
- Flag injection (is_estimated) for template transparency

FEATURE-CONFIG-EXTRACTION (FASE-CONFIG-2)
Resolves: CR-3 (silent fallbacks), H-11, H-12, H-13, H-27
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# --- Schema definition ---
_SCORE_SCHEMA = {
    "benchmark_score": {"type": int, "min": 0, "max": 100},
    "score_tecnico": {"type": int, "min": 0, "max": 100},
    "coherence_score": {"type": int, "min": 0, "max": 100},
    "voice_readiness": {"type": int, "min": 0, "max": 100},
    "voice_status": {"type": str},
}

_DEFAULT_CONFIG_PATH = Path("config/fallbacks.yaml")

# Module-level cache: {path_str: (data_dict, mtime)}
_cache: Dict[str, Tuple[Dict, float]] = {}


class FallbackLoadError(Exception):
    """Raised when fallbacks.yaml has invalid schema or cannot be loaded."""
    pass


def _validate_schema(data: Dict[str, Any]) -> None:
    """Validate fallbacks.yaml against expected schema."""
    if "scores" not in data:
        raise FallbackLoadError("Missing 'scores' section in fallbacks.yaml")

    scores = data["scores"]
    for key, spec in _SCORE_SCHEMA.items():
        if key not in scores:
            raise FallbackLoadError(f"Missing score key '{key}' in fallbacks.yaml")

        entry = scores[key]
        if not isinstance(entry, dict) or "value" not in entry:
            raise FallbackLoadError(
                f"Score '{key}' must be a dict with 'value' field, got: {type(entry)}"
            )

        expected_type = spec["type"]
        actual_val = entry["value"]

        if not isinstance(actual_val, expected_type):
            # Try coercion for int/str boundary
            try:
                if expected_type is int:
                    entry["value"] = int(actual_val)
                elif expected_type is str:
                    entry["value"] = str(actual_val)
                else:
                    raise ValueError()
            except (ValueError, TypeError):
                raise FallbackLoadError(
                    f"Score '{key}' expected type {expected_type.__name__}, "
                    f"got {type(actual_val).__name__}: {actual_val!r}"
                )

        # Range checks
        val = entry["value"]
        if "min" in spec and val < spec["min"]:
            raise FallbackLoadError(
                f"Score '{key}' value {val} below minimum {spec['min']}"
            )
        if "max" in spec and val > spec["max"]:
            raise FallbackLoadError(
                f"Score '{key}' value {val} above maximum {spec['max']}"
            )


def load_fallbacks(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load and validate fallbacks.yaml. Returns parsed dict.
    Uses file-level cache invalidated by mtime.

    Raises FallbackLoadError on schema errors.
    """
    import yaml

    path = config_path or _DEFAULT_CONFIG_PATH
    path = Path(path)
    cache_key = str(path.resolve())

    # Check cache
    if cache_key in _cache:
        cached_data, cached_mtime = _cache[cache_key]
        try:
            current_mtime = path.stat().st_mtime
        except OSError:
            # File disappeared — invalidate cache
            del _cache[cache_key]
        else:
            if current_mtime == cached_mtime:
                return cached_data

    # Load file
    if not path.exists():
        raise FallbackLoadError(
            f"Fallback config not found: {path}. "
            f"Create config/fallbacks.yaml or check working directory."
        )

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise FallbackLoadError(
            f"fallbacks.yaml must be a dict, got {type(data).__name__}"
        )

    # Validate schema
    _validate_schema(data)

    # Update cache
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    _cache[cache_key] = (data, mtime)

    return data


def get_fallback_value(
    key: str,
    config_path: Optional[Path] = None,
) -> Any:
    """
    Get a single fallback score value by key.

    Args:
        key: Score key (e.g. 'benchmark_score', 'score_tecnico')
        config_path: Optional override for config file path

    Returns:
        The fallback value (int or str)

    Raises:
        FallbackLoadError if YAML is missing or invalid
        KeyError if key doesn't exist
    """
    data = load_fallbacks(config_path)
    scores = data.get("scores", {})
    if key not in scores:
        raise KeyError(
            f"Fallback key '{key}' not found in fallbacks.yaml. "
            f"Available: {list(scores.keys())}"
        )
    return scores[key]["value"]


def get_estimated_text(config_path: Optional[Path] = None) -> str:
    """Get the estimated disclaimer text from fallbacks.yaml."""
    data = load_fallbacks(config_path)
    flags = data.get("flags", {})
    return flags.get("estimated_text", "Valor estimado")


def clear_cache() -> None:
    """Clear the module-level cache. Useful for testing."""
    _cache.clear()
