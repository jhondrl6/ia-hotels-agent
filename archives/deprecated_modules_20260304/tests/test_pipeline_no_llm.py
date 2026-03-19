"""Integration-style test to ensure pipeline uses deterministic engine for package selection."""

import modules.orchestrator.pipeline as pipeline
from modules.orchestrator.pipeline import AnalysisPipeline, PipelineOptions, GeoStageResult


class _DummyIATester:
    def test_hotel(self, hotel_data):
        return {"perplexity": {"menciones": 0}, "chatgpt": {"menciones": 0}}


class _DummyLLMAdapter:
    def get_current_provider(self):
        return "dummy"


class _DummyGapAnalyzer:
    def __init__(self, provider_type=None):
        self.llm_adapter = _DummyLLMAdapter()

    def analyze_with_llm(self, hotel_data, gbp_data, schema_data, ia_test):
        return {"perdida_mensual_total": 1_230_000}


class _ExplodingGapAnalyzer:
    def __init__(self, provider_type=None):
        raise AssertionError("GapAnalyzer should not be used in deterministic mode")


def test_run_ia_stage_uses_decision_engine(monkeypatch, tmp_path):
    # Patch external dependencies to avoid network/LLM
    monkeypatch.setattr(pipeline, "IATester", _DummyIATester)
    monkeypatch.setattr(pipeline, "GapAnalyzer", _DummyGapAnalyzer)

    options = PipelineOptions(url="https://example.com", output_dir=tmp_path)
    pipe = AnalysisPipeline(options)

    geo_result = GeoStageResult(
        hotel_data={"ubicacion": "Manizales", "precio_promedio": 300_000},
        gbp_data={"score": 50, "reviews": 5},
        schema_data={"score_schema": 20, "tiene_hotel_schema": False},
    )

    ia_result = pipe.run_ia_stage(geo_result)

    decision = ia_result.decision_result
    assert decision["paquete"] in {"Starter GEO", "Pro AEO", "Pro AEO Plus", "Elite", "Elite PLUS"}
    assert "justificacion" in decision
    assert ia_result.llm_analysis.get("paquete_recomendado") == decision["paquete"]


def test_deterministic_mode_skips_llm(monkeypatch, tmp_path):
    monkeypatch.setattr(pipeline, "IATester", _DummyIATester)
    monkeypatch.setattr(pipeline, "GapAnalyzer", _ExplodingGapAnalyzer)

    options = PipelineOptions(url="https://example.com", output_dir=tmp_path, mode="deterministico")
    pipe = AnalysisPipeline(options)

    geo_result = GeoStageResult(
        hotel_data={"ubicacion": "Manizales", "precio_promedio": 300_000},
        gbp_data={"score": 50, "reviews": 5},
        schema_data={"score_schema": 20, "tiene_hotel_schema": False},
    )

    ia_result = pipe.run_ia_stage(geo_result)

    assert ia_result.current_provider == "deterministic"
    assert ia_result.llm_analysis.get("modo_narrativa") == "deterministico"
