from pathlib import Path

import pytest

from modules.generators.report_builder_fixed import (
    ReportBuilder,
    ReportDataBundle,
    ReportIntegrationAdapter,
)


def _base_bundle() -> ReportDataBundle:
    return ReportDataBundle(
        hotel_data={
            "nombre": "Hotel Base",
            "ubicacion": "Ciudad Base",
            "habitaciones": None,
            "campos_estimados": ["habitaciones", "precio_promedio"],
            "precio_promedio": None,
            "servicios": ["WiFi"],
        },
        gbp_data={"score": 40, "reviews": 5, "issues": ["Sin GBP"]},
        schema_data={"score_schema": 20, "schemas_faltantes": ["Hotel"]},
        ia_test={"total_queries": 4, "perplexity": {"menciones": 0}, "chatgpt": {"menciones": 0}},
        llm_analysis={"perdida_mensual_total": 5_000_000, "quick_wins": ["Optimizar GBP"]},
        roi_data={"totales_6_meses": {"roas": 4}, "proyeccion_6_meses": []},
    )


def test_adapter_merges_and_cleans_estimated_fields():
    adapter = ReportIntegrationAdapter(prefer_external=True)
    base_bundle = _base_bundle()
    payload = {
        "hotel_data": {
            "habitaciones": 22,
            "precio_promedio": 320000,
            "campos_estimados": [],
            "servicios": ["WiFi", "Piscina"],
        },
        "gbp_data": {"score": 55, "reviews": 12},
        "schema_data": {"score_schema": 65, "schemas_faltantes": ["FAQPage"]},
        "ia_test": {"total_queries": 6, "perplexity": {"menciones": 2}},
        "llm_analysis": {
            "perdida_mensual_total": 4_200_000,
            "quick_wins": ["Optimizar schema"],
        },
        "roi_data": {"totales_6_meses": {"roas": 5}},
    }

    merged, audit = adapter.combine(base_bundle, payload)

    assert audit.is_compatible
    assert merged.hotel_data["habitaciones"] == 22
    assert "habitaciones" not in merged.hotel_data.get("campos_estimados", [])
    assert merged.hotel_data["servicios"] == ["WiFi", "Piscina"]
    assert merged.gbp_data["reviews"] == 12
    assert merged.schema_data["schemas_faltantes"] == ["Hotel", "FAQPage"]
    assert merged.llm_analysis["perdida_mensual_total"] == 4_200_000
    assert merged.roi_data["totales_6_meses"]["roas"] == 5


def test_adapter_flags_conflicts_when_no_estimation():
    adapter = ReportIntegrationAdapter(prefer_external=False)
    base_bundle = _base_bundle()
    base_bundle.hotel_data.pop("campos_estimados")
    payload = {
        "hotel_data": {
            "nombre": "Hotel Nuevo",
            "ubicacion": "Ciudad Base",
        },
        "gbp_data": {"score": 60},
        "schema_data": {"score_schema": 25},
        "ia_test": {"total_queries": 5},
        "llm_analysis": {"perdida_mensual_total": 4_800_000},
        "roi_data": {"totales_6_meses": {"roas": 4}},
    }

    _, audit = adapter.combine(base_bundle, payload)

    assert not audit.is_compatible
    assert "hotel_data" in audit.conflicts
    assert "nombre" in audit.conflicts["hotel_data"]


def test_report_builder_applies_integration_when_forced(tmp_path):
    builder = ReportBuilder()
    output_dir = Path(tmp_path)
    base_bundle = _base_bundle()
    payload = {
        "hotel_data": {
            "habitaciones": 30,
            "precio_promedio": 410000,
        },
        "gbp_data": {"score": 70},
        "schema_data": {"score_schema": 70},
        "ia_test": {"total_queries": 8},
        "llm_analysis": {"perdida_mensual_total": 3_900_000},
        "roi_data": {"totales_6_meses": {"roas": 6}},
    }

    builder.generate(
        base_bundle.hotel_data,
        base_bundle.gbp_data,
        base_bundle.schema_data,
        base_bundle.ia_test,
        base_bundle.llm_analysis,
        base_bundle.roi_data,
        output_dir,
        integration_payload=payload,
        force_integration=True,
    )

    audit = builder.get_last_integration_audit()
    assert audit is not None and audit.is_compatible
    resumen_path = output_dir / "00_RESUMEN_EJECUTIVO.md"
    assert resumen_path.exists()
    raw_path = output_dir / "evidencias" / "raw_data" / "analisis_completo.json"
    assert raw_path.exists()
    raw_data = raw_path.read_text(encoding="utf-8")
    assert "410000" in raw_data
