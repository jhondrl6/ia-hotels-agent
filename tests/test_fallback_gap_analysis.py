"""Ensure fallback gap analysis uses deterministic package selection (no LLM)."""

import pytest

try:
    import modules.orchestrator.pipeline as pipeline
except ImportError:
    pytest.skip("modules.orchestrator no está disponible (archivado)", allow_module_level=True)


def test_fallback_calls_determine_package(monkeypatch):
    calls = {"count": 0}

    def _fake_determine_package(**kwargs):
        calls["count"] += 1
        return "Pro AEO", "justificacion"

    monkeypatch.setattr(pipeline, "determine_package", _fake_determine_package)

    hotel_data = {"ubicacion": "Manizales", "precio_promedio": 300000, "ocupacion_actual": 0.55}
    gbp_data = {"score": 40, "reviews": 5}
    schema_data = {"score_schema": 10, "tiene_hotel_schema": False}
    ia_test = {"perplexity": {"menciones": 0}, "chatgpt": {"menciones": 0}}

    result = pipeline._fallback_gap_analysis(hotel_data, gbp_data, schema_data, ia_test)

    assert calls["count"] == 1  # determinista, no LLM
    assert result["paquete_recomendado"] == "Pro AEO"
    assert "paquete" not in result  # no campo LLM
    assert result.get("proveedor_llm") == "fallback"
