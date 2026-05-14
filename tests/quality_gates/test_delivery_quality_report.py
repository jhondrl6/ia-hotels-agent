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
            human_review_items=["Review low confidence assets"],
            summary={"total_gates": 4, "passed": 1, "failed": 3},
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
            human_review_items=["3 assets below confidence threshold"],
            summary={"total_gates": 4, "passed": 3, "failed": 1},
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
            human_review_items=[],
            summary={"total_gates": 4, "passed": 4, "failed": 0},
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
        assert len(report.human_review_items) == 0

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
