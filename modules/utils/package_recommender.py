"""Package Recommender v2.3 (legacy wrapper).

Delegates deterministic package selection to `DecisionEngine` (reglas puras, sin LLM).
"""
from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

try:
    from modules.decision_engine import DecisionEngine, Diagnostico
    DECISION_ENGINE_AVAILABLE = True
except ImportError:
    DECISION_ENGINE_AVAILABLE = False
    DecisionEngine = None
    Diagnostico = None

try:
    from modules.utils.benchmarks import BenchmarkLoader
    loader = BenchmarkLoader()
except ImportError:
    loader = None

if DECISION_ENGINE_AVAILABLE and loader:
    engine = DecisionEngine(loader)
else:
    engine = None


def determine_package(
    region: str,
    reviews: int,
    gbp_score: int,
    schema_score: int,
    tiene_schema: bool,
    total_mentions: int,
    precio_promedio: int = 0,
    hotel_data: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    """Legacy entry point kept for compatibility.

    All logic is delegated to the deterministic decision engine. Input fields are
    mapped to the v2.3 Diagnostico schema.
    """
    if not DECISION_ENGINE_AVAILABLE or engine is None or loader is None:
        return "starter_geo", "Módulo deprecado - use comando v4complete"

    hotel_data = hotel_data or {}
    thresholds = loader.get_thresholds()
    region_data = loader.get_regional_data(region)

    # Estimar pérdidas si no vienen en hotel_data
    factor_gbp = thresholds.get("factor_gbp_punto", 50_000)
    gbp_gap = max(thresholds.get("gbp_score_bajo", 60) - gbp_score, 0)
    estimado_brecha_gbp = gbp_gap * factor_gbp

    sin_motor_reservas = int(hotel_data.get("perdida_conversion", estimado_brecha_gbp))
    schema_ausente = int(hotel_data.get("perdida_ia", 0 if tiene_schema else estimado_brecha_gbp))
    web_score = int(hotel_data.get("web_score", 70))

    revpar_estimado = hotel_data.get("revpar_estimado")
    if revpar_estimado is None:
        ocupacion = hotel_data.get("ocupacion_actual", 0.6)
        precio = precio_promedio or region_data.get("revpar_cop", 150_000)
        revpar_estimado = int(precio * ocupacion) if ocupacion and precio else region_data.get("revpar_cop", 150_000)

    gbp_activity_score = int(hotel_data.get("gbp_activity_score", 100) or 100)
    gbp_motor_existe = bool(hotel_data.get("gbp_motor_existe", hotel_data.get("motor_reservas_gbp", True)))
    gbp_motor_prominente = bool(hotel_data.get("gbp_motor_prominente", hotel_data.get("motor_reservas_prominente", False)))

    diag = Diagnostico(
        sin_motor_reservas=sin_motor_reservas,
        schema_ausente=schema_ausente,
        gbp_score=gbp_score,
        web_score=web_score,
        revpar=revpar_estimado,
        region=region,
        menciones_ia=total_mentions,
        gbp_activity_score=gbp_activity_score,
        gbp_motor_existe=gbp_motor_existe,
        gbp_motor_prominente=gbp_motor_prominente,
    )

    result = engine.recomendar(diag)
    razon_extendida = (
        f"Región: {region}. Reviews: {reviews}. GBP: {gbp_score}/100. "
        f"Schema: {schema_score}/100 ({'ok' if tiene_schema else 'faltante'}). "
        f"Menciones IA: {total_mentions}. Activity: {gbp_activity_score}/100. "
        f"Motor GBP: {'sí' if gbp_motor_existe else 'no'}; prominente: {'sí' if gbp_motor_prominente else 'no'}. "
        f"Decisión: {result['razon']}"
    )
    return result["paquete"], razon_extendida


def get_package_info(paquete: str) -> Dict[str, Any]:
    if loader is None:
        return {"name": paquete, "description": "Módulo deprecado - use comando v4complete"}
    packages = loader.get_packages()
    return packages.get(paquete, packages.get("Pro AEO", {}))
