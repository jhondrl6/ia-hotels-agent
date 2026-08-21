"""FASE-P2-A (F14): Tests de contrato promised_assets_exist + site_presence_report.

Verifica que el coherence validator acepta assets "verificados en producción"
(status exists/redundant + site_verified=True en site_presence_report)
aunque no tengan archivo físico generado, alineándose con el gate
proposal_asset_alignment que los marca como "present_in_production".

Contratos:
  C1: asset verificado en producción → coherence PASSED (coincidente con gate)
  C2: asset prometido sin archivo ni verificación → coherence FAILED (gate no debilitado)
  C3: mix de assets generados + verificados en producción → PASSED
  C4: site_presence_report=None → comportamiento legacy preservado
"""

import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET


class TestPromisedAssetsProductionVerification:
    """F14: promised_assets_exist acepta 'verificado en producción'."""

    @pytest.fixture
    def validator(self):
        return CoherenceValidator()

    @pytest.fixture
    def mock_diagnostic(self):
        return MagicMock()

    def _make_asset_specs(self, asset_types):
        """Helper: create mock AssetSpec list from asset_type names."""
        specs = []
        for at in asset_types:
            mock = MagicMock()
            mock.asset_type = at
            specs.append(mock)
        return specs

    def _make_site_presence_report(self, verified_types: dict) -> dict:
        """Helper: build canonical site_presence_report dict.

        Args:
            verified_types: {asset_type: status} where status is
                "exists", "redundant", "not_exists", etc.

        Returns:
            Dict canónico con structure compatible con normalize_site_presence.
        """
        results = {}
        for asset_type, status in verified_types.items():
            results[asset_type] = {
                "status": status,
                "site_verified": status in ("exists", "redundant"),
                "confidence": 0.95 if status == "exists" else 0.85,
            }
        return {
            "site_url": "https://test-hotel.com",
            "checked_at": "2026-08-21T00:00:00",
            "results": results,
            **results,  # top-level keys for direct access
        }

    # =====================================================================
    # C1: asset verificado en producción → coherence PASSED
    # =====================================================================

    def test_c1_whatsapp_verified_in_production_passes(self, validator, mock_diagnostic):
        """C1: whatsapp_button verified in production → PASSED even without generated file.

        This is the exact F14 scenario: whatsapp_button exists on the live site,
        the orchestrator skipped generation (SkippedAsset), and the coherence
        validator should agree with the gate that it's "present".
        """
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        # whatsapp_button NOT generated (skipped), all others generated
        generated_assets = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
            if at != "whatsapp_button"
        }

        site_report = self._make_site_presence_report({
            "whatsapp_button": "exists",
        })

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=site_report,
        )

        assert result.passed is True, (
            f"F14 FAILED: asset verified in production should pass. "
            f"Message: {result.message}"
        )
        assert result.score == 1.0
        assert "producción" in result.message or "verificado" in result.message

    def test_c1_multiple_assets_verified_in_production(self, validator, mock_diagnostic):
        """C1: multiple assets verified in production → all PASSED."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        # Only 4 generated, 3 verified in production
        generated_assets = {
            "optimization_guide": {"can_use": True, "confidence_score": 0.9},
            "hotel_schema": {"can_use": True, "confidence_score": 0.8},
            "org_schema": {"can_use": True, "confidence_score": 0.7},
            "open_graph": {"can_use": True, "confidence_score": 0.6},
        }

        site_report = self._make_site_presence_report({
            "whatsapp_button": "exists",
            "faq_page": "exists",
            "llms_txt": "redundant",
        })

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=site_report,
        )

        assert result.passed is True
        assert result.score == 1.0

    # =====================================================================
    # C2: asset sin archivo ni verificación → FAILED (gate no debilitado)
    # =====================================================================

    def test_c2_missing_without_verification_still_fails(self, validator, mock_diagnostic):
        """C2: asset missing from generated AND not in production → FAILED.

        The fix must NOT weaken the gate: assets that are truly missing
        (no file, no production verification) still cause failure.
        """
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        # Only 3 generated, 0 verified in production
        generated_assets = {
            "optimization_guide": {"can_use": True, "confidence_score": 0.9},
            "hotel_schema": {"can_use": True, "confidence_score": 0.8},
            "org_schema": {"can_use": True, "confidence_score": 0.7},
        }

        # No site presence report at all
        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=None,
        )

        assert result.passed is False, (
            "C2: missing assets without production verification should FAIL"
        )

    def test_c2_not_exists_in_production_still_fails(self, validator, mock_diagnostic):
        """C2: asset with status 'not_exists' in site report → still FAILED."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        generated_assets = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
            if at != "whatsapp_button"
        }

        # whatsapp_button NOT exists in production
        site_report = self._make_site_presence_report({
            "whatsapp_button": "not_exists",
        })

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=site_report,
        )

        assert result.passed is False, (
            "C2: asset not in production and not generated should FAIL"
        )
        assert "whatsapp_button" in result.message

    def test_c2_site_verified_false_still_fails(self, validator, mock_diagnostic):
        """C2: status 'exists' but site_verified=False → still FAILED.

        Prevents false positives from unverified reports.
        """
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        generated_assets = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
            if at != "whatsapp_button"
        }

        # whatsapp_button has status=exists but site_verified=False
        site_report = {
            "site_url": "https://test-hotel.com",
            "checked_at": "2026-08-21T00:00:00",
            "results": {
                "whatsapp_button": {
                    "status": "exists",
                    "site_verified": False,  # NOT verified
                    "confidence": 0.4,
                }
            },
        }

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=site_report,
        )

        assert result.passed is False, (
            "C2: unverified presence should not count as production-verified"
        )

    # =====================================================================
    # C3: mix de generados + verificados en producción → PASSED
    # =====================================================================

    def test_c3_generated_plus_production_mix(self, validator, mock_diagnostic):
        """C3: some generated, some in production, all covered → PASSED."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        # 5 generated
        generated_assets = {
            "optimization_guide": {"can_use": True, "confidence_score": 0.9},
            "whatsapp_button": {"can_use": True, "confidence_score": 0.8},
            "hotel_schema": {"can_use": True, "confidence_score": 0.7},
            "org_schema": {"can_use": True, "confidence_score": 0.6},
            "open_graph": {"can_use": True, "confidence_score": 0.5},
        }

        # 2 verified in production
        site_report = self._make_site_presence_report({
            "faq_page": "exists",
            "llms_txt": "exists",
        })

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=site_report,
        )

        assert result.passed is True
        assert result.score == 1.0

    # =====================================================================
    # C4: site_presence_report=None → legacy behavior preserved
    # =====================================================================

    def test_c4_no_site_report_legacy_behavior(self, validator, mock_diagnostic):
        """C4: site_presence_report=None → same behavior as before F14 fix."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        # All generated
        generated_assets = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
        }

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=None,
        )

        assert result.passed is True
        assert result.score == 1.0

    def test_c4_no_site_report_missing_still_fails(self, validator, mock_diagnostic):
        """C4: no site report + missing assets → still fails (legacy)."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        # Only 2 generated
        generated_assets = {
            "optimization_guide": {"can_use": True, "confidence_score": 0.9},
            "whatsapp_button": {"can_use": True, "confidence_score": 0.8},
        }

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=None,
        )

        assert result.passed is False

    # =====================================================================
    # C5: Coherence ↔ Gate alignment (end-to-end contract)
    # =====================================================================

    def test_c5_coherence_and_gate_agree_on_production_asset(
        self, validator, mock_diagnostic
    ):
        """C5: coherence and proposal_asset_alignment agree on 'present_in_production'.

        This is the core F14 contract: both validators must produce the SAME
        signal for an asset that exists in production but has no generated file.
        """
        from modules.asset_generation.proposal_asset_alignment import (
            verify_proposal_asset_alignment,
        )

        # Simulate: whatsapp_button skipped (not generated), exists in production
        generated_list = [
            {"asset_type": at, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
            if at != "whatsapp_button"
        ]

        # Gate: verify_proposal_asset_alignment
        site_report_obj = MagicMock()
        site_report_obj.results = {
            "whatsapp_button": MagicMock(
                status=MagicMock(value="exists"),
                site_verified=True,
            )
        }

        gate_report = verify_proposal_asset_alignment(
            proposal_services=list(PROPOSAL_SERVICE_TO_ASSET.keys()),
            generated_assets=generated_list,
            site_presence_report=site_report_obj,
        )

        # Gate: whatsapp_button should be present_in_production
        production_types = [s.asset_type for s in gate_report.present_in_production]
        assert "whatsapp_button" in production_types, (
            "Gate should mark whatsapp_button as present_in_production"
        )

        # Coherence: build canonical dict for coherence validator
        site_presence_dict = {
            "results": {
                "whatsapp_button": {
                    "status": "exists",
                    "site_verified": True,
                    "confidence": 0.95,
                }
            },
            "whatsapp_button": {
                "status": "exists",
                "site_verified": True,
                "confidence": 0.95,
            },
        }

        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())
        generated_assets_dict = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
            if at != "whatsapp_button"
        }

        coherence_check = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets_dict,
            site_presence_report=site_presence_dict,
        )

        # Both MUST agree: whatsapp_button is NOT missing
        assert coherence_check.passed is True, (
            f"C5 FAILED: gate says present_in_production but coherence says: "
            f"{coherence_check.message}"
        )

    # =====================================================================
    # Edge cases
    # =====================================================================

    def test_empty_site_presence_report(self, validator, mock_diagnostic):
        """Empty site_presence_report → no production verification."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        generated_assets = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
        }

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report={"results": {}},
        )

        assert result.passed is True  # all generated → passes regardless

    def test_verification_failed_status_not_accepted(self, validator, mock_diagnostic):
        """status='verification_failed' should NOT be treated as production-verified."""
        all_planned = self._make_asset_specs(PROPOSAL_SERVICE_TO_ASSET.values())

        generated_assets = {
            at: {"can_use": True, "confidence_score": 0.9}
            for at in PROPOSAL_SERVICE_TO_ASSET.values()
            if at != "whatsapp_button"
        }

        site_report = self._make_site_presence_report({
            "whatsapp_button": "verification_failed",
        })

        result = validator._check_promised_assets_exist(
            all_planned, mock_diagnostic,
            generated_assets=generated_assets,
            site_presence_report=site_report,
        )

        assert result.passed is False, (
            "verification_failed should not count as production-verified"
        )
