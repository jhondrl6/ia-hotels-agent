"""Guardrails for Phase 4 asset-generation strategy."""

from modules.asset_generation.asset_catalog import ASSET_CATALOG
from modules.asset_generation.v4_asset_orchestrator import (
    AssetGenerationResult,
    GeneratedAsset,
)


class StubCoherenceReport:
    """Minimal coherence report for report serialization tests."""

    def to_dict(self):
        return {"is_coherent": True, "overall_score": 0.91}


class TestAssetConfidenceGuardrails:
    """Protect confidence thresholds for critical assets."""

    def test_confidence_threshold_snapshot(self):
        expected_thresholds = {
            "whatsapp_button": 0.7,
            "faq_page": 0.5,
            "hotel_schema": 0.6,
            "geo_playbook": 0.5,
            "review_plan": 0.4,
            "review_widget": 0.5,
            "org_schema": 0.5,
            "barra_reserva_movil": 0.6,
            "financial_projection": 0.5,
            "performance_audit": 0.5,
            "optimization_guide": 0.5,
            "llms_txt": 0.5,
        }

        for asset_type, expected in expected_thresholds.items():
            assert ASSET_CATALOG[asset_type].required_confidence == expected

    def test_all_implemented_assets_keep_minimum_floor(self):
        for asset_type, entry in ASSET_CATALOG.items():
            if entry.status.value == "implemented":
                assert entry.required_confidence >= 0.4, (
                    f"{asset_type} below confidence floor: {entry.required_confidence}"
                )


class TestDeliveryFilenamePresentation:
    """Keep reporting friendly names while preserving traceability."""

    def test_report_exposes_delivery_filename_without_estimated_prefix(self):
        result = AssetGenerationResult(
            hotel_id="hotel_visperas",
            hotel_name="Hotel Visperas",
            generated_assets=[
                GeneratedAsset(
                    asset_type="faq_page",
                    filename="ESTIMATED_faqs_20260313_120000.csv",
                    path="output/hotel_visperas/faq_page/ESTIMATED_faqs_20260313_120000.csv",
                    metadata_path="output/hotel_visperas/faq_page/ESTIMATED_faqs_20260313_120000_metadata.json",
                    preflight_status="WARNING",
                    confidence_score=0.62,
                    pain_ids_resolved=["no_faq_schema"],
                    can_use=True,
                    delivery_filename="faqs_20260313_120000.csv",
                )
            ],
            failed_assets=[],
            coherence_report=StubCoherenceReport(),
            output_dir="output/hotel_visperas",
            timestamp="2026-03-13T12:00:00",
        )

        report = result.to_dict()
        assert report["generated_assets"][0]["filename"].startswith("ESTIMATED_")
        assert report["generated_assets"][0]["delivery_filename"] == "faqs_20260313_120000.csv"
        assert report["summary"]["estimated"] == 1
        assert report["summary"]["delivery_ready_percentage"] == 0.0
