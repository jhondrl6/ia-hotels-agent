"""Post-orchestration reconciliation: unifies 3 sources of truth about pain resolution.

FASE-0 (DT-4): Reconciliation module. After asset generation, this module
reads the asset_generation_report and pain_ledger to produce a single
canonical pain_ledger_resolved.json — resolving conflicts between the
3 independent sources of truth that previously caused false positives
in coverage gates (BUG-6, BUG-9).

Sources:
  1. pain_ledger.json — DETECTED/DIAGNOSED/MAPPED_TO_SERVICE/ASSET_GENERATED/...
  2. generated_assets[].pain_ids_resolved — assets generated that resolve pains
  3. skipped_assets[].pain_ids_affected — assets skipped because site already has them
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PainResolutionStatus:
    """Status values emitted by the reconciler."""
    ASSET_GENERATED = "ASSET_GENERATED"
    MAPPED_TO_SERVICE = "MAPPED_TO_SERVICE"
    JUSTIFIED_SKIP = "JUSTIFIED_SKIP"


class PostOrchestratorReconciler:
    """Reconciles pain_ledger with asset_generation_report after orchestration.

    Three sources of truth exist for "is this pain resolved?":
    1. pain_ledger.json — DETECTED/DIAGNOSED/MAPPED_TO_SERVICE/ASSET_GENERATED/...
    2. generated_assets[].pain_ids_resolved — assets generated that resolve pains
    3. skipped_assets[].pain_ids_affected — assets skipped because site already has them

    This reconciler reads all three, resolves conflicts, and emits a single
    pain_ledger_resolved.json as the canonical post-orchestration state.
    """

    def reconcile(
        self,
        asset_generation_report_path: Path,
        pain_ledger_path: Path,
        output_path: Path,
    ) -> Dict:
        """Reconcile and emit pain_ledger_resolved.json.

        Returns the reconciled pain ledger as a dict.
        """
        # Load inputs
        asset_report = self._load_json(asset_generation_report_path)
        pain_ledger = self._load_json(pain_ledger_path)

        # Build resolution maps
        generated_pain_ids = self._extract_generated_pain_ids(asset_report)
        skipped_pain_map = self._extract_skipped_pain_map(asset_report)

        # Normalize pain_ledger to list of entries
        raw_entries = pain_ledger.get("entries", pain_ledger if isinstance(pain_ledger, list) else [])

        # Reconcile each pain
        resolved_entries = []
        for entry in raw_entries:
            pain_id = entry.get("pain_id", entry.get("id", ""))
            new_status = self._resolve_status(
                pain_id=pain_id,
                current_status=entry.get("status", "DETECTED"),
                in_generated=pain_id in generated_pain_ids,
                skipped_info=skipped_pain_map.get(pain_id),
            )
            resolved_entry = {**entry, "status": new_status}
            resolved_entries.append(resolved_entry)

        # Build output
        result = {
            "version": "1.0",
            "source": "post_orchestrator_reconciler",
            "entries": resolved_entries,
            "summary": {
                "total": len(resolved_entries),
                "asset_generated": sum(
                    1 for e in resolved_entries if e["status"] == PainResolutionStatus.ASSET_GENERATED
                ),
                "mapped_to_service": sum(
                    1 for e in resolved_entries if e["status"] == PainResolutionStatus.MAPPED_TO_SERVICE
                ),
                "justified_skip": sum(
                    1 for e in resolved_entries if e["status"] == PainResolutionStatus.JUSTIFIED_SKIP
                ),
            },
        }

        # Emit
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(
            "Reconciled pain ledger → %s (%d entries)",
            output_path,
            len(resolved_entries),
        )

        return result

    def _resolve_status(
        self,
        pain_id: str,
        current_status: str,
        in_generated: bool,
        skipped_info: Optional[Dict],
    ) -> str:
        """Determine final status for a single pain."""
        if in_generated:
            return PainResolutionStatus.ASSET_GENERATED
        # FASE-P1-D (F13): VERIFIED_IN_SITE es estado de primera clase — el
        # reconciler lo preserva (el asset ya está confirmado en producción;
        # el skip del asset layer no debe degradarlo a MAPPED_TO_SERVICE).
        if current_status == "VERIFIED_IN_SITE":
            return current_status
        if skipped_info:
            presence = skipped_info.get("presence_status", "")
            if presence == "exists":
                return PainResolutionStatus.MAPPED_TO_SERVICE
            if presence == "redundant":
                return PainResolutionStatus.JUSTIFIED_SKIP
            # exists_with_issues or unknown — keep current
        return current_status

    def _extract_generated_pain_ids(self, asset_report: Dict) -> set:
        """Extract pain IDs resolved by generated assets."""
        pain_ids = set()
        for asset in asset_report.get("generated_assets", []):
            for pid in asset.get("pain_ids_resolved", []):
                pain_ids.add(pid)
        return pain_ids

    def _extract_skipped_pain_map(self, asset_report: Dict) -> Dict[str, Dict]:
        """Build map of pain_id → skip_info for skipped assets."""
        skipped_map = {}
        for asset in asset_report.get("skipped_assets", []):
            presence = asset.get("presence_status", "")
            for pid in asset.get("pain_ids_affected", []):
                skipped_map[pid] = {
                    "presence_status": presence,
                    "asset_name": asset.get("asset_name", ""),
                    "site_verified": asset.get("site_verified", False),
                }
        return skipped_map

    def _load_json(self, path: Path) -> Dict:
        """Load a JSON file, returning empty dict on failure."""
        if not path.exists():
            logger.warning("File not found: %s", path)
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
