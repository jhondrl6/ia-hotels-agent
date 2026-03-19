"""Centralized data normalization utilities for delivery workflows."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

NORMALIZATION_CACHE_PATH = Path("data/cache/hotel_normalization.json")

_CONFIDENCE_LABELS: Dict[str, float] = {
    "alta": 0.95,
    "media": 0.75,
    "media-alta": 0.8,
    "media_baja": 0.6,
    "media-baja": 0.6,
    "baja": 0.4,
    "desconocida": 0.4,
}

_HARDCODED_OVERRIDES: Tuple[Tuple[str, str, str], ...] = (
    ("visperas", "Santa Rosa de Cabal, Risaralda", "hardcoded_visperas"),
)


def _load_cache() -> Dict[str, Dict[str, Any]]:
    if not NORMALIZATION_CACHE_PATH.exists():
        return {}
    try:
        return json.loads(NORMALIZATION_CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


_NORMALIZATION_CACHE: Dict[str, Dict[str, Any]] = _load_cache()


def _build_cache_key(hotel_data: Dict[str, Any]) -> str:
    base = (
        hotel_data.get("url")
        or hotel_data.get("nombre")
        or hotel_data.get("hotel_name")
        or ""
    ).strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")
    if cleaned:
        return cleaned
    fallback = hotel_data.get("slug") or hotel_data.get("id") or "__unknown__"
    return re.sub(r"[^a-z0-9]+", "-", str(fallback).lower()).strip("-") or "__unknown__"


def _persist_cache() -> None:
    try:
        NORMALIZATION_CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        NORMALIZATION_CACHE_PATH.write_text(
            json.dumps(_NORMALIZATION_CACHE, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception:
        # Cache persistence issues should not break execution flow
        return


def _remember_location(hotel_data: Dict[str, Any], location: str, source: str) -> None:
    cache_key = _build_cache_key(hotel_data)
    if not cache_key or cache_key == "__unknown__":
        return
    _NORMALIZATION_CACHE[cache_key] = {
        "ubicacion": location,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": hotel_data.get("url"),
        "nombre": hotel_data.get("nombre") or hotel_data.get("hotel_name"),
    }
    _persist_cache()


def _clean_location(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None


def _confidence_score(hotel_data: Dict[str, Any]) -> float:
    for key in ("ubicacion_confianza", "location_confidence", "confidence_score"):
        raw = hotel_data.get(key)
        if isinstance(raw, (int, float)):
            return max(0.0, min(1.0, float(raw)))
    label = str(hotel_data.get("confidence") or "").lower().strip()
    if label in _CONFIDENCE_LABELS:
        return _CONFIDENCE_LABELS[label]
    return 0.5


def lookup_cached_location(hotel_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
    cache_key = _build_cache_key(hotel_data)
    cached = _NORMALIZATION_CACHE.get(cache_key)
    if cached and cached.get("ubicacion"):
        return {
            "ubicacion": cached["ubicacion"],
            "source": cached.get("source", "normalization_cache"),
        }
    return None


def _apply_hardcoded_overrides(hotel_data: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    reference = f"{hotel_data.get('nombre', '')} {hotel_data.get('hotel_name', '')} {hotel_data.get('url', '')}".lower()
    for token, location, source in _HARDCODED_OVERRIDES:
        if token in reference:
            return location, source
    return None


def _choose_location(hotel_data: Dict[str, Any]) -> Optional[Tuple[str, str]]:
    validated = _clean_location(hotel_data.get("ubicacion_validada"))
    if validated:
        source = hotel_data.get("ubicacion_fuente", "gbp_validation")
        return validated, source

    confident_raw = _clean_location(hotel_data.get("ubicacion"))
    if confident_raw and _confidence_score(hotel_data) >= 0.7:
        source = hotel_data.get("ubicacion_fuente", "scraper_high_confidence")
        return confident_raw, source

    cached = lookup_cached_location(hotel_data)
    if cached:
        return cached["ubicacion"], cached["source"]

    hardcoded = _apply_hardcoded_overrides(hotel_data)
    if hardcoded:
        return hardcoded

    if confident_raw:
        return confident_raw, hotel_data.get("ubicacion_fuente", "scraper_low_confidence")

    return None


def normalize_hotel_data(hotel_data: Dict[str, Any], *, persist: bool = True) -> Dict[str, Any]:
    """Return a normalized copy of hotel data with consistent critical fields."""

    if hotel_data is None:
        return {}

    normalized: Dict[str, Any] = deepcopy(hotel_data)
    location_choice = _choose_location(normalized)

    if location_choice:
        location_value, source = location_choice
        previous_location = normalized.get("ubicacion")
        if (
            previous_location
            and previous_location.strip()
            and previous_location.strip().lower() != location_value.strip().lower()
        ):
            normalized.setdefault("ubicacion_original", previous_location)
        normalized["ubicacion"] = location_value
        normalized["ubicacion_normalizada"] = location_value
        normalized["ubicacion_fuente"] = source
        trace = normalized.setdefault("normalization_trace", [])
        trace.append(f"ubicacion<-{source}")
        normalized.setdefault("normalization_meta", {})["ubicacion"] = {
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            _remember_location(normalized, location_value, source)

    return normalized


__all__ = ["normalize_hotel_data", "lookup_cached_location"]
