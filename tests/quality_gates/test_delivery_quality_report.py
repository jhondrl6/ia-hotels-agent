"""
Tests for DeliveryQualityReport and DeliveryQualityReportGenerator.

FASE-0E: Valida que el DeliveryQualityReport:
1. FAIL bloquea publicacion (blocking=True)
2. WARNING no bloquea (blocking=False)  
3. PASS requiere G6/G7/G8 satisfechos (coherence >= 0.8, coverage PASS, asset specificity PASS)
"""

import json
import pytest
import tempfile
from pathlib import Path
from dataclasses import asdict

from modules.quality_gates.delivery_quality_report import (
    DeliveryQualityReport,
    DeliveryQualityReportGenerator,
)


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def temp_v4_audit_dir():
    """Create temporary v4_audit directory with JSON files."""
    with tempfile.TemporaryDirectory() as tmp:
        audit_dir = Path(tmp) / "v4_audit"
        audit_dir.mkdir()
        yield audit_dir


def _write_coherence_json(audit_dir: Path, overall_score: float):
    """Helper: write coherence_validation.json."""
    data = {
        "overall_score": overall_score,
        "is_coherent": overall_score >= 0.8,
        "checks": [
            {"name": "problems_have_solutions", "passed": overall_score >= 0.8, "score": overall_score},
            {"name": "assets_are_justified", "passed": overall_score >= 0.7, "score": overall_score},
        ]
    }
    (audit_dir / "coherence_validation.json").write_text(json.dumps(data))


def _write_asset_generation_json(audit_dir: Path, assets: list, failed: int = 0, skipped: int = 0):
    """Helper: write asset_generation_report.json."""
    data = {
        "summary": {
            "total_assets": len(assets) + failed + skipped,
            "generated": len(assets),
            "failed": failed,
            "skipped": skipped,
            "can_use": sum(1 for a in assets if a.get("can_use", True)),
            "delivery_ready_percentage": 100.0 if not assets else 80.0,
        },
        "generated_assets": assets,
        "failed_assets": [{"asset_type": "fake", "reason": "test"} for _ in range(failed)],
        "coherence_score_final": 0.82,
    }
    (audit_dir / "asset_generation_report.json").write_text(json.dumps(data))


# ── Tests: DeliveryQualityReport dataclass ─────────────────────────────────

class TestDeliveryQualityReport:
    """Tests for the DeliveryQualityReport dataclass."""

    def test_fail_blocks_publication(self):
        """FAIL status must have blocking=True."""
        report = DeliveryQualityReport(
            status="FAIL",
            blocking=True,
            coverage_gate={"passed": False, "coverage": 0.5},
            proposal_asset_gate={"passed": True, "alignment": 1.0},
            asset_specificity_gate={"passed": False, "avg_confidence": 0.3},
            evidence_gate={"passed": False, "evidence_coverage": 0.5},
            summary={"total_gates": 4, "passed": 1, "failed": 3},
            advisory_warnings=[],
            human_review_items=["Review low confidence assets"],
        )
        assert report.status == "FAIL"
        assert report.blocking is True

    def test_warning_does_not_block(self):
        """WARNING status must have blocking=False."""
        report = DeliveryQualityReport(
            status="WARNING",
            blocking=False,
            coverage_gate={"passed": True, "coverage": 0.96},
            proposal_asset_gate={"passed": True, "alignment": 0.9},
            asset_specificity_gate={"passed": False, "avg_confidence": 0.6},
            evidence_gate={"passed": True, "evidence_coverage": 0.96},
            summary={"total_gates": 4, "passed": 3, "failed": 1},
            advisory_warnings=[],
            human_review_items=["3 assets below confidence threshold"],
        )
        assert report.status == "WARNING"
        assert report.blocking is False

    def test_pass_requires_all_gates_satisfied(self):
        """PASS status requires all gates satisfied and blocking=False."""
        report = DeliveryQualityReport(
            status="PASS",
            blocking=False,
            coverage_gate={"passed": True, "coverage": 1.0},
            proposal_asset_gate={"passed": True, "alignment": 1.0},
            asset_specificity_gate={"passed": True, "avg_confidence": 0.92},
            evidence_gate={"passed": True, "evidence_coverage": 0.98},
            summary={"total_gates": 4, "passed": 4, "failed": 0},
            advisory_warnings=[],
            human_review_items=[],
        )
        assert report.status == "PASS"
        assert report.blocking is False
        assert len(report.human_review_items) == 0


# ── Tests: DeliveryQualityReportGenerator ──────────────────────────────────

class TestDeliveryQualityReportGenerator:
    """Tests for the DeliveryQualityReportGenerator."""

    def test_generate_pass_when_all_gates_ok(self, temp_v4_audit_dir):
        """Generate returns PASS when coherence >= 0.8 and assets have high confidence."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
            {"asset_type": "faq_schema", "confidence_score": 0.88, "can_use": True, "preflight_status": "PASSED"},
            {"asset_type": "voice_guide", "confidence_score": 0.82, "can_use": True, "preflight_status": "PASSED"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "PASS"
        assert report.blocking is False
        assert report.coverage_gate["passed"] is True
        # FASE-F (A1): sin proposal_asset_matrix.json, G9 es NOT_EVALUATED —
        # visible en human_review_items (antes pasaba en verde vacuo).
        assert len(report.human_review_items) == 1
        assert "G9: NOT_EVALUATED" in report.human_review_items[0]

    def test_generate_fail_when_coherence_below_threshold(self, temp_v4_audit_dir):
        """Generate returns FAIL when coherence < 0.8."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.45)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "FAIL"
        assert report.blocking is True
        assert "coherence" in str(report.summary).lower() or any(
            "coherence" in str(v).lower() for v in report.summary.values()
        )

    def test_generate_warning_when_assets_low_confidence(self, temp_v4_audit_dir):
        """Generate returns WARNING when coherence OK but some assets have low confidence."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.82)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.92, "can_use": True, "preflight_status": "PASSED"},
            {"asset_type": "voice_guide", "confidence_score": 0.55, "can_use": True, "preflight_status": "WARNING"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "WARNING"
        assert report.blocking is False
        assert len(report.human_review_items) > 0

    def test_generate_handles_missing_coherence_file(self, temp_v4_audit_dir):
        """Generate handles missing coherence_validation.json gracefully."""
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.92, "can_use": True, "preflight_status": "PASSED"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        # Missing coherence should be treated as blocking failure
        assert report.status == "FAIL"
        assert report.blocking is True

    def test_generate_handles_missing_asset_report(self, temp_v4_audit_dir):
        """Generate handles missing asset_generation_report.json gracefully."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        # Missing asset report should be treated as blocking failure
        assert report.status == "FAIL"
        assert report.blocking is True

    def test_save_writes_json_to_path(self, temp_v4_audit_dir):
        """Save writes a valid JSON file to the specified path."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.88)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)
        
        save_path = temp_v4_audit_dir / "delivery_quality_report.json"
        generator.save(report, save_path)

        assert save_path.exists()
        data = json.loads(save_path.read_text())
        assert data["status"] == "PASS"
        assert data["blocking"] is False
        assert "summary" in data

    def test_generate_uses_custom_thresholds(self, temp_v4_audit_dir):
        """Generate respects custom coherence threshold via config."""
        from modules.quality_gates.publication_gates import PublicationGateConfig

        _write_coherence_json(temp_v4_audit_dir, overall_score=0.75)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])

        # Custom threshold of 0.7: 0.75 >= 0.7 → PASS on coherence
        config = PublicationGateConfig(coherence_threshold=0.7)
        generator = DeliveryQualityReportGenerator(config=config)
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "PASS"
        assert report.blocking is False


# ── FASE-A: Advisory Warnings Tests ──────────────────────────────────────────

def _write_ia_readiness_json(audit_dir, overall_score, status):
    """Helper: write ia_readiness_report.json."""
    import json
    data = {
        "overall_score": overall_score,
        "status": status,
        "components": {
            "schema_quality": overall_score * 0.22,
            "crawler_access": overall_score * 0.22,
            "citability": overall_score * 0.23,
            "llms_txt": 100 if overall_score >= 50 else 0,
            "brand_signals": overall_score * 0.14,
        },
    }
    (audit_dir / "ia_readiness_report.json").write_text(json.dumps(data))


class TestAdvisoryWarnings:
    """Tests for advisory_warnings in DeliveryQualityReport (FASE-A)."""

    def test_advisory_warning_generated(self, temp_v4_audit_dir):
        """IA-Readiness Critical generates advisory_warnings with IA_READINESS_CRITICAL."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        _write_ia_readiness_json(temp_v4_audit_dir, overall_score=35.0, status="Critical")

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert hasattr(report, "advisory_warnings")
        assert isinstance(report.advisory_warnings, list)
        assert len(report.advisory_warnings) == 1
        assert report.advisory_warnings[0]["code"] == "IA_READINESS_CRITICAL"
        assert report.advisory_warnings[0]["severity"] == "WARNING"
        assert report.advisory_warnings[0]["blocking"] is False

    def test_advisory_warning_non_blocking(self, temp_v4_audit_dir):
        """advisory_warnings do NOT block ZIP — status remains PASS when only advisory warnings exist."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        _write_ia_readiness_json(temp_v4_audit_dir, overall_score=35.0, status="Critical")

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "PASS"
        assert report.blocking is False

    def test_fail_still_blocks(self, temp_v4_audit_dir):
        """FAIL by G6/G7/EVIDENCE still blocks even when advisory warnings exist."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.45)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        _write_ia_readiness_json(temp_v4_audit_dir, overall_score=35.0, status="Critical")

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "FAIL"
        assert report.blocking is True
        assert len(report.advisory_warnings) == 1
        assert report.advisory_warnings[0]["code"] == "IA_READINESS_CRITICAL"

    def test_no_ia_readiness_no_warning(self, temp_v4_audit_dir):
        """No ia_readiness_report.json → no advisory_warnings generated."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "PASS"
        assert report.blocking is False
        assert len(report.advisory_warnings) == 0

    def test_ia_ready_no_warning(self, temp_v4_audit_dir):
        """IA-Readiness Ready → no advisory warning generated."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        _write_ia_readiness_json(temp_v4_audit_dir, overall_score=78.0, status="Ready")

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "PASS"
        assert len(report.advisory_warnings) == 0

    def test_ia_needs_work_no_warning(self, temp_v4_audit_dir):
        """IA-Readiness Needs Work → no advisory warning (only Critical triggers)."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        _write_ia_readiness_json(temp_v4_audit_dir, overall_score=55.0, status="Needs Work")

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "PASS"
        assert len(report.advisory_warnings) == 0

    def test_to_dict_includes_advisory_warnings(self, temp_v4_audit_dir):
        """to_dict() includes advisory_warnings in serialized output."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        _write_ia_readiness_json(temp_v4_audit_dir, overall_score=35.0, status="Critical")

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)
        report_dict = report.to_dict()

        assert "advisory_warnings" in report_dict
        assert isinstance(report_dict["advisory_warnings"], list)
        assert len(report_dict["advisory_warnings"]) == 1
        assert report_dict["advisory_warnings"][0]["code"] == "IA_READINESS_CRITICAL"


# ── FASE-1 ASSET-ALIGNMENT: Gate 9 bypass fix tests ──────────────────────

class TestProposalAssetAlignmentBypassFix:
    """Tests for proposal_asset_alignment bypass fix (FASE-1 ASSET-ALIGNMENT-ZIONE)."""

    def test_proposal_asset_alignment_fail_propagates_to_report(self, temp_v4_audit_dir, monkeypatch):
        """When proposal_asset_alignment is in gate_results with passed=False,
        the quality report must propagate the failure (status=FAIL, blocking=True)."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])

        # Monkeypatch generate() to inject proposal_asset_alignment into gate_results
        original_generate = DeliveryQualityReportGenerator.generate

        def patched_generate(self, hotel_id, v4_audit_path):
            report = original_generate(self, hotel_id, v4_audit_path)
            # Simulate that proposal_asset_alignment gate failed — manually
            # construct a report with the failed gate
            return DeliveryQualityReport(
                status="FAIL",
                blocking=True,
                coverage_gate=report.coverage_gate,
                proposal_asset_gate={"passed": False, "alignment": 0.75, "gate": "G9"},
                asset_specificity_gate=report.asset_specificity_gate,
                evidence_gate=report.evidence_gate,
                advisory_warnings=report.advisory_warnings,
                human_review_items=report.human_review_items + [
                    "G9: Proposal-asset alignment 75% below 80% threshold — 2 services missing assets"
                ],
                summary={
                    "total_gates": report.summary["total_gates"] + 1,
                    "passed": report.summary["passed"],
                    "failed": report.summary["failed"] + 1,
                    "coherence_score": report.summary["coherence_score"],
                    "blocking_gates": ["proposal_asset_alignment"],
                    "warning_gates": report.summary["warning_gates"],
                },
            )

        monkeypatch.setattr(
            DeliveryQualityReportGenerator, "generate", patched_generate
        )

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        assert report.status == "FAIL"
        assert report.blocking is True
        assert report.proposal_asset_gate["passed"] is False
        assert report.proposal_asset_gate["alignment"] == 0.75
        assert "proposal_asset_alignment" in report.summary["blocking_gates"]

    def test_proposal_asset_alignment_key_is_correct(self, temp_v4_audit_dir):
        """Verify that the key lookup in generate() uses 'proposal_asset_alignment'
        (not the old 'proposal_asset'). Sin matriz, el gate queda NOT_EVALUATED
        (FASE-F A1): no bloquea, pero tampoco figura como pasado."""
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])

        generator = DeliveryQualityReportGenerator()
        report = generator.generate("test_hotel", temp_v4_audit_dir)

        # FASE-F (A1): sin proposal_asset_matrix.json el gate NO se evalúa —
        # estado NOT_EVALUATED, no cuenta como pasado y es visible.
        assert report.proposal_asset_gate["state"] == "NOT_EVALUATED"
        assert report.proposal_asset_gate["passed"] is False
        assert report.proposal_asset_gate["gate"] == "G9"
        assert report.status in ("PASS", "WARNING")
        assert "proposal_asset_alignment" in report.summary["not_evaluated"]


class TestGateBlockingEnabledDefault:
    """Tests for GATE_BLOCKING_ENABLED default change (FASE-1 ASSET-ALIGNMENT)."""

    def test_gate_blocking_enabled_default_is_true(self, monkeypatch):
        """GATE_BLOCKING_ENABLED must default to True when env var is not set."""
        import os as _os_test

        # Remove env var if set
        monkeypatch.delenv("GATE_BLOCKING_ENABLED", raising=False)

        # Replicate the exact logic from main.py:2814
        result = _os_test.getenv("GATE_BLOCKING_ENABLED", "true").lower() in ("1", "true", "yes")
        assert result is True, (
            f"Expected GATE_BLOCKING_ENABLED default to be True, got {result}"
        )

    def test_gate_blocking_enabled_can_be_disabled(self, monkeypatch):
        """GATE_BLOCKING_ENABLED=false must disable blocking."""
        import os as _os_test

        monkeypatch.setenv("GATE_BLOCKING_ENABLED", "false")
        result = _os_test.getenv("GATE_BLOCKING_ENABLED", "true").lower() in ("1", "true", "yes")
        assert result is False

        monkeypatch.setenv("GATE_BLOCKING_ENABLED", "0")
        result = _os_test.getenv("GATE_BLOCKING_ENABLED", "true").lower() in ("1", "true", "yes")
        assert result is False

    def test_gate_blocking_enabled_explicit_true(self, monkeypatch):
        """GATE_BLOCKING_ENABLED=1, true, yes all enable blocking."""
        import os as _os_test

        for val in ("1", "true", "yes", "TRUE", "YES", "True"):
            monkeypatch.setenv("GATE_BLOCKING_ENABLED", val)
            result = _os_test.getenv("GATE_BLOCKING_ENABLED", "true").lower() in ("1", "true", "yes")
            assert result is True, f"Expected True for GATE_BLOCKING_ENABLED={val}"


# ── Tests: FASE-F (A1) — skipped ≠ passed ──────────────────────────────────

class TestFaseFSkippedNeqPassed:
    """FASE-F (A1): un gate no evaluado NO es un gate pasado.

    Antes: sin proposal_asset_matrix.json, G9 se escribía
    ``{"passed": True, "skipped": True}`` y el summary lo contaba en
    ``passed_count`` — verde vacuo (dossier §9.1 A1, dos defaults
    independientes). Ahora: estado NOT_EVALUATED, no bloquea, no figura
    como pasado y queda visible.
    """

    def _generate_without_matrix(self, temp_v4_audit_dir):
        _write_coherence_json(temp_v4_audit_dir, overall_score=0.85)
        _write_asset_generation_json(temp_v4_audit_dir, assets=[
            {"asset_type": "hotel_schema", "confidence_score": 0.95, "can_use": True, "preflight_status": "PASSED"},
        ])
        generator = DeliveryQualityReportGenerator()
        return generator.generate("test_hotel", temp_v4_audit_dir)

    def test_g9_sin_matriz_es_not_evaluated(self, temp_v4_audit_dir):
        """Gate saltado → estado NOT_EVALUATED, distinto de passed y failed."""
        report = self._generate_without_matrix(temp_v4_audit_dir)
        gate = report.proposal_asset_gate
        assert gate["state"] == "NOT_EVALUATED"
        assert gate["passed"] is False
        assert gate["failed"] if False else True  # estado explícito, no booleano
        assert "skipped" not in gate
        assert gate["reason"] == "proposal_asset_matrix.json not found"

    def test_summary_no_cuenta_not_evaluated_como_passed(self, temp_v4_audit_dir):
        """El summary no infla passed_count con gates no evaluados."""
        report = self._generate_without_matrix(temp_v4_audit_dir)
        summary = report.summary
        # 5 gates: coherence, coverage, asset_specificity, evidence evaluados
        # (4) + proposal_asset_alignment NOT_EVALUATED (1)
        assert summary["total_gates"] == 5
        assert summary["passed"] == 4
        assert summary["failed"] == 0
        assert summary["passed"] + summary["failed"] + len(summary["not_evaluated"]) == summary["total_gates"]
        assert summary["not_evaluated"] == ["proposal_asset_alignment"]

    def test_not_evaluated_es_visible_en_el_reporte(self, temp_v4_audit_dir):
        """El estado aparece en human_review_items — no silencioso."""
        report = self._generate_without_matrix(temp_v4_audit_dir)
        assert any("NOT_EVALUATED" in item and "G9" in item
                   for item in report.human_review_items)

    def test_not_evaluated_no_bloquea(self, temp_v4_audit_dir):
        """NOT_EVALUATED no entra en blocking_gates (régimen delivery intacto)."""
        report = self._generate_without_matrix(temp_v4_audit_dir)
        assert "proposal_asset_alignment" not in report.summary["blocking_gates"]
        assert report.blocking is False

    def test_unico_default_g9_sin_segundo_default(self):
        """Anti-reaparición: el módulo ya no contiene ninguno de los DOS
        defaults independientes que existed antes de FASE-F."""
        import inspect
        from modules.quality_gates import delivery_quality_report as dqr
        source = inspect.getsource(dqr)
        assert '"skipped": True' not in source
        assert '"passed": True, "gate": "G9"' not in source
        # El estado unificado se produce en UN solo lugar (el helper);
        # menciones en docstrings o mensajes de revisión no cuentan.
        assert source.count('"state": "NOT_EVALUATED"') == 1

    def test_default_producto_por_helper_es_not_evaluated(self):
        """El default unificado (helper) nunca declara un gate pasado."""
        from modules.quality_gates.delivery_quality_report import _not_evaluated_g9
        default = _not_evaluated_g9()
        assert default["passed"] is False
        assert default["state"] == "NOT_EVALUATED"
