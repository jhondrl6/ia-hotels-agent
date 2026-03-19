import json
from pathlib import Path

import os

from modules.generators.proposal_gen import ProposalGenerator


PLAN_JSON = Path("data/benchmarks/plan_maestro_data.json")
PLAN_MD = Path("data/benchmarks/Plan_maestro_v2_5.md")  # Legacy: suite v2.4 (decision_core)


def test_plan_md_contains_client_components():
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    md_text = PLAN_MD.read_text(encoding="utf-8").lower()

    paquetes = data.get("paquetes_servicios_v23", {})
    assert paquetes, "No packages found in plan JSON"

    for nombre, info in paquetes.items():
        assert nombre.lower() in md_text, f"Paquete {nombre} no encontrado en MD"
        componentes = info.get("componentes_cliente") or info.get("componentes") or []
        assert componentes, f"Paquete {nombre} no tiene componentes definidos"


def test_proposal_filename_casing(tmp_path: Path) -> None:
    gen = ProposalGenerator()
    hotel_data = {"nombre": "Hotel Test"}
    claude_analysis = {"paquete_recomendado": "Starter GEO", "gbp_data": {"score": 50, "gbp_activity_score": 100}}
    roi_data = {"totales_6_meses": {"roas": 1.0}}

    gen.create_pdf(hotel_data, claude_analysis, roi_data, tmp_path)

    upper = tmp_path / "02_PROPUESTA_COMERCIAL.md"
    lower = tmp_path / "02_propuesta_comercial.md"
    assert upper.exists(), "Archivo de propuesta no generado con el casing esperado"

    # En Windows el sistema es case-insensitive; solo validamos ausencia del alias en FS sensibles
    if os.name != "nt":
        assert not lower.exists(), "Se encontró variante en minúsculas; debe mantenerse casing canonico"


def test_owner_bundles_have_default_region():
    data = json.loads(PLAN_JSON.read_text(encoding="utf-8"))
    paquetes = data.get("paquetes_servicios_v23", {})
    assert paquetes, "No packages found in plan JSON"

    required_fields = [
        "plan_7_30_60_90_por_region",
        "kpis_cliente_por_region",
        "dependencias_cliente_por_region",
        "cadencia_mensual_por_region",
        "triggers_upgrade_por_region",
        "playbook_cierre_por_region",
    ]

    for nombre, info in paquetes.items():
        for field in required_fields:
            regional = info.get(field)
            assert isinstance(regional, dict), f"{field} ausente o no es dict en {nombre}"
            default_items = regional.get("default")
            assert isinstance(default_items, list), f"default debe ser lista en {field} de {nombre}"
            assert default_items, f"default vacío en {field} de {nombre}"
