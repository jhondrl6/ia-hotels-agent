from __future__ import annotations

from typing import Dict, List


def _prioritized_issues(issues: List[dict]) -> List[dict]:
    if not issues:
        return []
    priority_order = {"CRÍTICO": 0, "CRITICO": 0, "ALTO": 1, "MEDIO": 2, "BAJO": 3}
    sorted_issues = sorted(
        issues,
        key=lambda item: (
            priority_order.get(item.get("priority", "MEDIO"), 4),
            -(item.get("estimated_monthly_loss") or 0),
        ),
    )
    critical_high = [issue for issue in sorted_issues if issue.get("priority") in {"CRÍTICO", "CRITICO", "ALTO"}]
    if critical_high:
        return critical_high
    return sorted_issues[:5]


def align_seo_summary(summary: Dict[str, object], full_analysis: Dict[str, object]) -> Dict[str, object]:
    issues = full_analysis.get("issues") or []
    financial = full_analysis.get("financial_impact", {})
    score_data = full_analysis.get("score", {})
    
    # v2.5.2: Extraer penalty_metadata para trazabilidad
    penalty_metadata = score_data.get("penalty_metadata") if isinstance(score_data, dict) else None
    
    result = {
        "score": summary.get("score") or score_data.get("total", 0) if isinstance(score_data, dict) else 0,
        "estimated_revenue_loss": financial.get("estimated_monthly_loss", 0),
        "issues": _prioritized_issues(list(issues)),
    }
    
    # Incluir penalty_metadata si existe
    if penalty_metadata:
        result["penalty_metadata"] = penalty_metadata
    
    return result
