"""
Site Presence Adapter — Canonical representation for cross-module consumption.

FASE-2 (DT4-R2): Unifies the dataclass SitePresenceReport, dataclasses.asdict()
output, and None into a single canonical dict that CoherenceValidator,
publication_gates, and the assessment builder all consume identically.

Problem solved:
  - SitePresenceChecker produces dataclass SitePresenceReport with enum .status
  - CoherenceValidator expects dict with .get("whatsapp_button", {})
  - asdict() preserves enum values (not strings)
  - publication_gates rebuilds a fake report from skipped_assets

This adapter is the SINGLE entry point — compute once, propagate everywhere.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import Any, Dict, Optional, Union


def normalize_site_presence(
    report: Any,
) -> Dict[str, Any]:
    """Normalize SitePresence input into a canonical dict.

    Accepts:
      - SitePresenceReport dataclass (with .results[asset_type] = PresenceCheckResult)
      - dataclasses.asdict(SitePresenceReport) → dict with enum values
      - dict already in canonical shape (pass-through with validation)
      - None → {"results": {}}

    Returns a dict with:
      - "site_url": str
      - "checked_at": str (ISO 8601)
      - "results": {asset_type: {status, site_verified, confidence}}
      - Asset-type keys at top level for CoherenceValidator direct access
        (e.g. {"whatsapp_button": {status, site_verified, confidence}})
    """
    if report is None:
        return {"results": {}}

    if isinstance(report, dict):
        return _from_dict(report)

    if hasattr(report, "results"):
        return _from_dataclass(report)

    raise TypeError(
        f"normalize_site_presence: unsupported type {type(report).__name__}. "
        f"Expected SitePresenceReport, dict, or None."
    )


def _from_dataclass(report: Any) -> Dict[str, Any]:
    """Convert SitePresenceReport dataclass to canonical dict."""
    result: Dict[str, Any] = {
        "site_url": getattr(report, "site_url", ""),
        "checked_at": _isoformat(getattr(report, "checked_at", None)),
        "results": {},
    }

    for asset_type, presence_result in getattr(report, "results", {}).items():
        asset_dict = _presence_result_to_canonical(presence_result)
        result["results"][asset_type] = asset_dict
        # Top-level key for CoherenceValidator direct access
        result[asset_type] = asset_dict

    return result


def _from_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """Convert or validate a dict input into canonical shape.

    Cases:
      - Already canonical (has "results" key): ensure top-level keys present
      - asdict() output: has "results" but enum values need conversion
      - Raw results dict (no top-level "results"): wrap it
    """
    already_canonical = "results" in d

    if already_canonical:
        result = {"site_url": d.get("site_url", ""),
                   "checked_at": d.get("checked_at", ""),
                   "results": {}}
        for asset_type, asset_data in d.get("results", {}).items():
            asset_dict = _asset_data_to_canonical(asset_data)
            result["results"][asset_type] = asset_dict
            result[asset_type] = asset_dict
        return result

    # Raw dict: assume it's a flat dict of {asset_type: PresenceCheckResult-like}
    # with no top-level "results" wrapper
    result: Dict[str, Any] = {"results": {}}
    for key, value in d.items():
        if isinstance(value, dict):
            asset_dict = _asset_data_to_canonical(value)
            result["results"][key] = asset_dict
            result[key] = asset_dict
    return result


def _presence_result_to_canonical(presence_result: Any) -> Dict[str, Any]:
    """Convert a PresenceCheckResult (dataclass or dict) to canonical asset dict.

    Handles:
      - PresenceCheckResult dataclass (has .status as PresenceStatus enum, .confidence, etc.)
      - dict from asdict(PresenceCheckResult) (has "status" as enum or string)
    """
    if hasattr(presence_result, "status"):
        # Dataclass instance
        status = getattr(presence_result, "status", None)
        status_str = _status_to_string(status)
        confidence = float(getattr(presence_result, "confidence", 1.0))
        return {
            "status": status_str,
            "site_verified": status_str in ("exists", "exists_with_issues", "redundant"),
            "confidence": confidence,
        }
    elif isinstance(presence_result, dict):
        return _asset_data_to_canonical(presence_result)
    else:
        return {"status": "not_checked", "site_verified": False, "confidence": 0.0}


def _asset_data_to_canonical(asset_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a dict-representation of an asset's presence to canonical form.

    Handles enum values from asdict() and ensures string status.
    """
    status = asset_data.get("status", "")
    status_str = _status_to_string(status)
    confidence = float(asset_data.get("confidence", 1.0))
    return {
        "status": status_str,
        "site_verified": status_str in ("exists", "exists_with_issues", "redundant"),
        "confidence": confidence,
    }


def _status_to_string(status: Any) -> str:
    """Convert PresenceStatus enum or string to lowercase string."""
    if status is None:
        return "not_checked"
    if hasattr(status, "value"):
        # Enum — get the string value (e.g., "exists")
        return str(status.value).lower()
    if isinstance(status, str):
        return status.lower()
    return str(status).lower()


def _isoformat(dt: Optional[datetime]) -> str:
    """Safely convert datetime to ISO 8601 string."""
    if dt is None:
        return ""
    try:
        return dt.isoformat()
    except Exception:
        return str(dt)
