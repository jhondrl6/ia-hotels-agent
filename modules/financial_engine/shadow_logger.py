"""Shadow Mode Logger for Financial Calculations."""

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, List


@dataclass
class ShadowComparison:
    comparison_id: str
    timestamp: str
    hotel_id: Optional[str] = None
    hotel_name: Optional[str] = None
    legacy_scenarios: Optional[Dict[str, Any]] = None
    legacy_pricing: Optional[Dict[str, Any]] = None
    new_scenarios: Optional[Dict[str, Any]] = None
    new_pricing: Optional[Dict[str, Any]] = None
    monthly_loss_delta: Optional[float] = None
    monthly_loss_delta_pct: Optional[float] = None
    pricing_delta: Optional[float] = None
    pricing_delta_pct: Optional[float] = None
    would_use_new: bool = False
    rejection_reason: Optional[str] = None
    flags_used: Optional[Dict[str, Any]] = None
    validation_errors: Optional[List[Dict]] = None


class ShadowLogger:
    DEFAULT_LOG_PATH = ".agent/shadow_logs"

    def __init__(self, log_path: Optional[str] = None):
        self.log_path = Path(log_path or self.DEFAULT_LOG_PATH)
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        self.log_path.mkdir(parents=True, exist_ok=True)

    def _generate_id(self) -> str:
        return f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    def log_comparison(
        self,
        legacy_result: Dict[str, Any],
        new_result: Dict[str, Any],
        hotel_id: Optional[str] = None,
        hotel_name: Optional[str] = None,
        flags: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[List[Dict]] = None,
    ) -> ShadowComparison:
        comparison = ShadowComparison(
            comparison_id=self._generate_id(),
            timestamp=datetime.utcnow().isoformat(),
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            legacy_scenarios=legacy_result.get("scenarios"),
            legacy_pricing=legacy_result.get("pricing"),
            new_scenarios=new_result.get("scenarios"),
            new_pricing=new_result.get("pricing"),
            flags_used=flags or {},
            validation_errors=validation_errors or [],
        )
        comparison = self._calculate_deltas(comparison)
        comparison = self._decide_usage(comparison)
        self._save_comparison(comparison)
        return comparison

    def _calculate_deltas(self, comparison: ShadowComparison) -> ShadowComparison:
        if comparison.legacy_scenarios and comparison.new_scenarios:
            legacy_val = self._get_expected_value(comparison.legacy_scenarios)
            new_val = self._get_expected_value(comparison.new_scenarios)
            if legacy_val is not None and new_val is not None:
                comparison.monthly_loss_delta = round(new_val - legacy_val, 2)
                if legacy_val != 0:
                    comparison.monthly_loss_delta_pct = round((comparison.monthly_loss_delta / legacy_val) * 100, 2)

        if comparison.legacy_pricing and comparison.new_pricing:
            legacy_price = comparison.legacy_pricing.get("monthly_price_cop")
            new_price = comparison.new_pricing.get("monthly_price_cop")
            if legacy_price is not None and new_price is not None:
                comparison.pricing_delta = round(new_price - legacy_price, 2)
                if legacy_price != 0:
                    comparison.pricing_delta_pct = round((comparison.pricing_delta / legacy_price) * 100, 2)

        return comparison

    def _get_expected_value(self, scenarios: Dict[str, Any]) -> Optional[float]:
        if not scenarios:
            return None
        for key in ["expected_value", "expected", "realistic"]:
            if key in scenarios:
                val = scenarios[key]
                if isinstance(val, dict):
                    return val.get("monthly_cop") or val.get("monthly_loss_cop")
                return val
        return None

    def _decide_usage(self, comparison: ShadowComparison) -> ShadowComparison:
        reasons = []

        if comparison.validation_errors:
            critical = [e for e in comparison.validation_errors if e.get("severity") in ("error", "critical")]
            if critical:
                reasons.append(f"Validation errors: {len(critical)} critical")

        if comparison.monthly_loss_delta_pct and abs(comparison.monthly_loss_delta_pct) > 50:
            reasons.append(f"Monthly loss delta too large: {comparison.monthly_loss_delta_pct}%")

        if comparison.new_pricing:
            pain_ratio = comparison.new_pricing.get("pain_ratio")
            if pain_ratio is not None and (pain_ratio < 0.03 or pain_ratio > 0.06):
                reasons.append(f"Pain ratio outside GATE: {pain_ratio:.2%}")

        comparison.would_use_new = len(reasons) == 0
        comparison.rejection_reason = "; ".join(reasons) if reasons else None
        return comparison

    def _save_comparison(self, comparison: ShadowComparison) -> Path:
        filename = f"{comparison.comparison_id}.json"
        filepath = self.log_path / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(comparison), f, indent=2, ensure_ascii=False)
        return filepath

    def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        stats = {"total": 0, "would_use_new": 0, "would_reject": 0, "avg_monthly_loss_delta_pct": 0.0, "rejection_reasons": {}}

        files = list(self.log_path.glob("*.json"))
        valid_comparisons = []

        for filepath in files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                timestamp = datetime.fromisoformat(data.get("timestamp", ""))
                if timestamp < cutoff:
                    continue
                stats["total"] += 1
                if data.get("would_use_new"):
                    stats["would_use_new"] += 1
                else:
                    stats["would_reject"] += 1
                    reason = data.get("rejection_reason", "unknown")
                    stats["rejection_reasons"][reason] = stats["rejection_reasons"].get(reason, 0) + 1
                valid_comparisons.append(data)
            except Exception:
                continue

        if valid_comparisons:
            loss_deltas = [d.get("monthly_loss_delta_pct", 0) for d in valid_comparisons if d.get("monthly_loss_delta_pct") is not None]
            if loss_deltas:
                stats["avg_monthly_loss_delta_pct"] = round(sum(loss_deltas) / len(loss_deltas), 2)

        return stats


def get_logger(log_path: Optional[str] = None) -> ShadowLogger:
    return ShadowLogger(log_path)