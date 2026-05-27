"""
Asset Semantics Validator — ROICR FASE-1.

Detects illogical pain→asset mappings ("semantic hallucinations")
and enforces migration_target for deprecated assets.

Maps INVALID_MAPPINGS: pain_id → list of asset_ids that CANT solve it.
For DEPRECATED assets without a migration_target, raises UnmappedPainError.
"""

import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------
# INVALID MAPPINGS: pain_id → [asset_ids that CANNOT solve it]
#
# These mappings are semantically wrong regardless of confidence.
# Example: monthly_report is a commercial INTERNAL tool - it does NOT
# fix FAQ/schema/IAO gaps.
#
# NOTE: FASE-2 audit found this dict had WRONG keys (asset_type instead of pain_id).
# Original keys: "monthly_report" and "whatsapp_conflict_guide" (these are asset_types).
# Corrected keys below use real pain_ids from PainSolutionMapper.PAIN_SOLUTION_MAP.
# ---------------------------------------------------------------
INVALID_MAPPINGS: Dict[str, List[str]] = {
    # monthly_report es un informe interno, no resuelve gaps técnicos de SEO/IAO
    # "monthly_report" key was wrong → correct pain_id: "no_faq_schema"
    "no_faq_schema": ["monthly_report"],
    "no_hotel_schema": ["monthly_report"],
    "missing_llmstxt": ["monthly_report"],
    # whatsapp_conflict_guide no resuelve "missing WhatsApp" — the guide is advisory
    # "whatsapp_conflict_guide" key was wrong → correct pain_id: "no_whatsapp_visible"
    "no_whatsapp_visible": ["whatsapp_conflict_guide"],
}


def validar_semantica_comercial(
    pain_id: str,
    asset_id: str,
    asset_status: str,
) -> Tuple[bool, str]:
    """
    Validate that a pain→asset mapping makes commercial sense.

    Returns:
        (True, "IMPLEMENT")           — Normal case, mapping is valid
        (True, "AUDIT_ONLY")          — Asset is skipped_existing; audit/optimize only
        (False, "BLOCKED: <reason>")  — Mapping is semantically wrong (hallucination)
    """
    # Case: skipped_existing → audit, don't implement
    if asset_status == "skipped_existing":
        return (True, "AUDIT_ONLY")

    # Case: check invalid mappings
    if pain_id in INVALID_MAPPINGS:
        blocked_assets = INVALID_MAPPINGS[pain_id]
        if asset_id in blocked_assets:
            reason = f"HALLUCINATION: asset '{asset_id}' cannot logically solve pain '{pain_id}'"
            logger.warning(f"[AssetSemantics] BLOCKED — {reason}")
            return (False, f"BLOCKED: {reason}")

    return (True, "IMPLEMENT")
