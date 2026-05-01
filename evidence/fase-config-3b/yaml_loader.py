"""
Generic YAML config loader with file-level mtime caching.

Provides load_yaml_config() for any config/<domain>.yaml file.
Used by FEATURE-CONFIG-EXTRACTION phases CONFIG-2 through CONFIG-5.

Pattern:
    from modules.common.yaml_loader import load_yaml_config

    config = load_yaml_config('scenarios')
    recovery = config['recovery_factors']['conservative']
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Module-level cache: {path_str: (data_dict, mtime)}
_cache: Dict[str, Tuple[Dict, float]] = {}


class YAMLLoadError(Exception):
    """Raised when a YAML config file is missing or has invalid structure."""
    pass


def _resolve_path(name: str, config_dir: Optional[Path] = None) -> Path:
    """Resolve config/<name>.yaml path. Accepts name with or without .yaml."""
    if config_dir is None:
        config_dir = Path("config")

    filename = name if name.endswith(".yaml") else f"{name}.yaml"
    return config_dir / filename


def load_yaml_config(
    name: str,
    config_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Load a YAML config file with mtime-based caching.

    Args:
        name: Config name (e.g. 'scenarios', 'financial_defaults').
              '.yaml' suffix is optional.
        config_dir: Optional override for config directory.

    Returns:
        Parsed YAML dict.

    Raises:
        YAMLLoadError: If file doesn't exist, isn't a dict, or YAML is invalid.
    """
    import yaml

    path = _resolve_path(name, config_dir)
    cache_key = str(path.resolve())

    # Check cache
    if cache_key in _cache:
        cached_data, cached_mtime = _cache[cache_key]
        try:
            current_mtime = path.stat().st_mtime
        except OSError:
            del _cache[cache_key]
        else:
            if current_mtime == cached_mtime:
                return cached_data

    # Load file
    if not path.exists():
        raise YAMLLoadError(
            f"Config file not found: {path}. "
            f"Create config/{name}.yaml or check working directory."
        )

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise YAMLLoadError(
            f"config/{name}.yaml must be a dict, got {type(data).__name__}"
        )

    # Update cache
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    _cache[cache_key] = (data, mtime)

    return data


def clear_cache() -> None:
    """Clear the module-level cache. Useful for testing."""
    _cache.clear()
