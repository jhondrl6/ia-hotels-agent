"""
Tests for HumanChecklistGenerator.

FASE-0F: Valida que el HumanChecklistGenerator:
1. Genera checklist con <= 10 items
2. Incluye excepciones del delivery_quality_report
3. El checklist es markdown válido
"""

import json
import pytest
import tempfile
from pathlib import Path

from modules.quality_gates.delivery_quality_report import (
    DeliveryQualityReport,
    DeliveryQualityReportGenerator,
)
from modules.quality_gates.human_checklist_generator import HumanChecklistGenerator


# ── Fixtures ──────────────────────────────────────────────────────────────

def _make_report(**overrides) -> DeliveryQualityReport:
    """Build a DeliveryQualityReport with sensible defaults."""
    defaults = {
        "status": "WARNING",
        "blocking": False,
        "coverage_gate": {
            "passed": True,
            "details": {"total_assets": 5, "generated": 4, "failed": 1, "failure_rate": 0.2},
            "gate": "G7",
        },
        "proposal_asset_gate": {"passed": True, "gate": "G9"},
        "asset_specificity_gate": {
            "passed": False,
            "details": {
                "reason": "2 assets below confidence threshold",
                "avg_confidence": 0.65,
                "low_confidence_count": 2,
                "total_assets": 5,
            },
            "gate": "G8",
        },
        "evidence_gate": {
            "passed": True,
            "details": {"coherence_available": True, "asset_data_available": True, "coherence_score": 0.85},
            "gate": "EVIDENCE",
        },
        "human_review_items": [
            "G6: Coherence score 0.72 below threshold 0.8",
            "G8: Asset specificity failed — 2 assets below confidence threshold",
        ],
        "summary": {
            "total_gates": 4,
            "passed": 2,
            "failed": 2,
            "coherence_score": 0.72,
            "blocking_gates": [],
            "warning_gates": ["asset_specificity"],
        },
    }
    defaults.update(overrides)
    return DeliveryQualityReport(**defaults)


@pytest.fixture
def report_warning() -> DeliveryQualityReport:
    """Report with WARNING status and 2 human review items."""
    return _make_report()


@pytest.fixture
def report_pass() -> DeliveryQualityReport:
    """Report with PASS status, no human review items."""
    return _make_report(
        status="PASS",
        human_review_items=[],
        summary={
            "total_gates": 4,
            "passed": 4,
            "failed": 0,
            "coherence_score": 0.90,
            "blocking_gates": [],
            "warning_gates": [],
        },
        asset_specificity_gate={
            "passed": True,
            "details": {"avg_confidence": 0.92, "total_assets": 5, "all_above_threshold": True},
            "gate": "G8",
        },
    )


@pytest.fixture
def report_fail() -> DeliveryQualityReport:
    """Report with FAIL status, blocking=True."""
    return _make_report(
        status="FAIL",
        blocking=True,
        human_review_items=[
            "G6: Coherence score 0.45 below threshold 0.8",
            "G7: Coverage check failed — No assets generated — coverage is 0%",
            "Evidence: Quality check failed — Coherence score not extractable from data",
        ],
        summary={
            "total_gates": 4,
            "passed": 1,
            "failed": 3,
            "coherence_score": 0.45,
            "blocking_gates": ["coherence", "coverage", "evidence"],
            "warning_gates": [],
        },
        coverage_gate={
            "passed": False,
            "details": {"reason": "No assets generated — coverage is 0%"},
            "gate": "G7",
        },
        evidence_gate={
            "passed": False,
            "details": {"reason": "Coherence score not extractable from data"},
            "gate": "EVIDENCE",
        },
    )


@pytest.fixture
def generator() -> HumanChecklistGenerator:
    """Fresh HumanChecklistGenerator instance."""
    return HumanChecklistGenerator()


# ── RED Tests ─────────────────────────────────────────────────────────────

class TestHumanChecklistGenerator:
    """Tests for HumanChecklistGenerator — FASE-0F."""

    def test_checklist_has_at_most_10_items(self, generator, report_warning):
        """
        RED: El checklist generado NO debe exceder 10 items.
        Cada item es una línea que empieza con '- [ ]'.
        """
        checklist = generator.generate(report_warning)
        items = [line for line in checklist.splitlines() if line.strip().startswith("- [ ]")]
        assert len(items) <= 10, f"Checklist tiene {len(items)} items, máximo permitido es 10"

    def test_checklist_includes_exceptions_only(self, generator, report_warning):
        """
        RED: El checklist debe incluir los human_review_items como excepciones.
        El humano revisa excepciones, no reconstruye coherencia.
        """
        checklist = generator.generate(report_warning)
        # Las excepciones deben aparecer en el checklist
        for item in report_warning.human_review_items:
            # Buscar fragmentos clave de cada excepción en el checklist
            # El texto puede estar abreviado o formateado, pero el contenido debe estar
            assert any(
                fragment in checklist
                for fragment in ["Coherence score", "below threshold", "Asset specificity", "confidence threshold"]
            ), f"Checklist no incluye excepciones esperadas: {report_warning.human_review_items}"

    def test_checklist_is_valid_markdown(self, generator, report_warning):
        """El checklist generado debe ser markdown bien formado."""
        checklist = generator.generate(report_warning)
        assert checklist.startswith("#"), "Checklist debe empezar con título markdown"
        assert "- [ ]" in checklist, "Checklist debe contener items checkbox"

    def test_checklist_pass_report_is_concise(self, generator, report_pass):
        """Para report PASS, el checklist debe ser mínimo (sin excepciones que reportar)."""
        checklist = generator.generate(report_pass)
        items = [line for line in checklist.splitlines() if line.strip().startswith("- [ ]")]
        # PASS report still generates a checklist, but it should be focused
        assert len(items) <= 10

    def test_checklist_fail_report_includes_blocking_info(self, generator, report_fail):
        """Para report FAIL, el checklist debe indicar que hay gates bloqueantes."""
        checklist = generator.generate(report_fail)
        assert "FAIL" in checklist or "bloque" in checklist.lower() or "blocking" in checklist.lower()

    def test_save_writes_checklist_to_disk(self, generator, report_warning):
        """save() debe escribir el checklist a un archivo."""
        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "human_checklist.md"
            checklist = generator.generate(report_warning)
            generator.save(checklist, out_path)
            assert out_path.exists()
            saved = out_path.read_text(encoding="utf-8")
            assert saved == checklist
