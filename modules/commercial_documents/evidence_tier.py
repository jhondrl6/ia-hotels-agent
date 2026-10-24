"""Resolución del tier de evidencia financiera con un solo productor (`H1`, FASE-F).

Antes de esta fase los dos documentos comerciales resolvían el tier cada uno a su manera:
la propuesta degradaba a `'C'` cuando no había `financial_breakdown`, mientras el diagnóstico
promovía a `'A'` solo porque `analytics_data.use_ga4` estaba encendido. Mismo run, dos
contratos: el diagnóstico emitía los claims de totalidad que la propuesta negaba.

Regla: el tier lo dicta el `FinancialBreakdown` (productor `scenario_calculator._determine_evidence_tier`).
Sin breakdown —o sin el atributo— no hay evidencia que nombre, así que ambos documentos degradan
a `'C'`. El `use_ga4` sigue decidiendo el texto del disclaimer, no el tier.
"""

from typing import Any, Optional

TIER_SIN_EVIDENCIA = "C"


def resolver_tier_evidencia(financial_breakdown: Optional[Any]) -> str:
    """Tier declarado por el breakdown; `'C'` cuando no existe o no lo publica."""
    if financial_breakdown is None:
        return TIER_SIN_EVIDENCIA
    return getattr(financial_breakdown, "evidence_tier", None) or TIER_SIN_EVIDENCIA
