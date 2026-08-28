"""FASE-SR-E (H7/L-SR3): contabilización única de ``exists_with_issues``.

Doble contabilidad corregida: ``EXISTS_WITH_ISSUES`` bloquea la generación
("existe en producción") pero NO contaba como ``present_in_production`` en
alignment/matrix/ledger/coherencia ("no existe"). El mismo hecho tratado
como "existe" y "no existe" según el consumidor.

Contrato post-fix (un solo criterio, L-SR3/L-NC10):
- ``is_present_in_production`` (site_presence_checker) es el criterio canónico:
  ``exists`` y ``exists_with_issues`` cuentan como presente en producción.
- Los campos faltantes del asset existente van como mejora sugerida
  (recommendations), NO como brecha unresolved.
- D-PF3 (hardening residual): ausencia genuina con fuentes disponibles →
  fallback del catálogo genera versión básica; sin fuentes → bloqueo con
  ``justified_skip``.
"""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.asset_generation.site_presence_checker import (
    PRODUCTION_PRESENT_STATUSES,
    PresenceCheckResult,
    PresenceStatus,
    SitePresenceReport,
    is_present_in_production,
)
from modules.asset_generation.proposal_asset_alignment import (
    ProposalAssetMatrixEntry,
    _presence_exists,
    committed_services_from_entries,
)
from modules.quality_gates.alignment_result import (
    AlignmentResult,
    _presence_resolved,
)
from modules.asset_generation.pain_ledger import PainLedger, PainLedgerEntry
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.asset_generation.preflight_checks import PreflightChecker

from datetime import datetime


def _presence_entry(asset_type: str, status: PresenceStatus) -> PresenceCheckResult:
    return PresenceCheckResult(
        asset_type=asset_type,
        status=status,
        verified_at=datetime.now(),
        site_url="https://www.hotelsalentoreal.com/",
        details={},
    )


class TestCanonicalCriterion:
    """El criterio canónico vive en site_presence_checker (dueño del enum)."""

    def test_exists_with_issues_counts_as_present(self):
        assert is_present_in_production(PresenceStatus.EXISTS_WITH_ISSUES) is True
        assert is_present_in_production("exists_with_issues") is True

    def test_exists_counts_as_present(self):
        assert is_present_in_production(PresenceStatus.EXISTS) is True
        assert is_present_in_production("exists") is True

    def test_non_present_statuses(self):
        assert is_present_in_production(PresenceStatus.NOT_EXISTS) is False
        assert is_present_in_production(PresenceStatus.VERIFICATION_FAILED) is False
        assert is_present_in_production("not_exists") is False
        assert is_present_in_production(None) is False

    def test_statuses_constant_is_shared(self):
        assert PRODUCTION_PRESENT_STATUSES == ("exists", "exists_with_issues")


class TestAlignmentResultAccounting:
    """alignment_result: presence-resolved incluye exists_with_issues."""

    def test_presence_resolved_accepts_with_issues(self):
        snapshot = {"hotel_schema": {"status": "exists_with_issues"}}
        assert _presence_resolved(snapshot, "hotel_schema") is True

    def test_presence_resolved_rejects_not_exists(self):
        snapshot = {"hotel_schema": {"status": "not_exists"}}
        assert _presence_resolved(snapshot, "hotel_schema") is False

    def test_compute_unresolved_resolves_with_issues(self):
        """MISSING_ASSET con asset existente con issues NO es unresolved."""
        entries = [
            ProposalAssetMatrixEntry(
                service_name="Schema Hotel",
                pain_ids=["no_hotel_schema"],
                asset_type="hotel_schema",
                status="MISSING_ASSET",
            )
        ]
        snapshot = {"hotel_schema": {"status": "exists_with_issues"}}

        assert AlignmentResult.compute_unresolved(entries, snapshot) == 0

    def test_from_entries_counts_with_issues_as_present(self):
        """exists_with_issues → present_in_production (cubierta, no deuda)."""
        entries = [
            ProposalAssetMatrixEntry(
                service_name="Schema Hotel",
                pain_ids=["no_hotel_schema"],
                asset_type="hotel_schema",
                status="MISSING_ASSET",
            )
        ]
        snapshot = {"hotel_schema": {"status": "exists_with_issues"}}

        result = AlignmentResult._from_entries(entries, snapshot)

        assert result.present_in_production == 1
        assert result.unresolved == 0
        assert result.coverage_ratio == pytest.approx(1.0)


class TestCommittedServicesAccounting:
    """proposal_asset_alignment: presencia exists_with_issues compromete."""

    def test_presence_exists_accepts_with_issues(self):
        report = {"results": {"hotel_schema": {"status": "exists_with_issues"}}}
        assert _presence_exists(report, "hotel_schema") is True

    def test_committed_services_include_with_issues(self):
        entries = [
            ProposalAssetMatrixEntry(
                service_name="Schema Hotel",
                pain_ids=[],
                asset_type="hotel_schema",
                status="NO_BREACH",
            )
        ]
        report = {"results": {"hotel_schema": {"status": "exists_with_issues"}}}

        committed = committed_services_from_entries(entries, report)

        assert committed == ["Schema Hotel"]


class TestProposalGeneratorAccounting:
    """v4_proposal_generator: exists_with_issues muestra 'Presente en sitio'."""

    def test_services_table_counts_with_issues_as_present(self):
        from modules.asset_generation.proposal_asset_alignment import (
            PROPOSAL_SERVICE_TO_ASSET,
        )
        from modules.commercial_documents.v4_proposal_generator import (
            V4ProposalGenerator,
        )

        schema_service = next(
            name
            for name, asset in PROPOSAL_SERVICE_TO_ASSET.items()
            if asset == "hotel_schema"
        )
        report = SitePresenceReport(
            site_url="https://www.hotelsalentoreal.com/",
            checked_at=datetime.now(),
            results={
                "hotel_schema": _presence_entry(
                    "hotel_schema", PresenceStatus.EXISTS_WITH_ISSUES
                )
            },
        )

        generator = V4ProposalGenerator()
        table = generator._generate_dynamic_services_table(
            assets_generated=[],
            site_presence_report=report,
            opportunity_scores=[],
            committed_services=[schema_service],
        )

        assert "Presente en sitio" in table
        assert "⏳ Pendiente" not in table


class TestPainLedgerPropagation:
    """pain_ledger: exists_with_issues + site_verified → VERIFIED_IN_SITE."""

    def test_apply_site_verification_with_issues(self):
        entry = PainLedgerEntry(
            pain_id="no_hotel_schema",
            source_module="pain_solution_mapper",
            source_file="pain_solution_mapper.py",
            severity="HIGH",
            confidence=1.0,
            status="DETECTED",
            human_label="Sin Schema Hotel",
        )
        report = {
            "results": {
                "hotel_schema": {
                    "status": "exists_with_issues",
                    "site_verified": True,
                }
            }
        }

        updated = PainLedger().apply_site_verification([entry], report)

        assert updated[0].status == PainLedger.STATUS_VERIFIED_IN_SITE
        assert updated[0].severity == "LOW"

    def test_apply_site_verification_not_exists_stays_detected(self):
        entry = PainLedgerEntry(
            pain_id="no_hotel_schema",
            source_module="pain_solution_mapper",
            source_file="pain_solution_mapper.py",
            severity="HIGH",
            confidence=1.0,
            status="DETECTED",
            human_label="Sin Schema Hotel",
        )
        report = {
            "results": {"hotel_schema": {"status": "not_exists", "site_verified": True}}
        }

        updated = PainLedger().apply_site_verification([entry], report)

        assert updated[0].status == "DETECTED"


class TestCoherenceAccounting:
    """coherence_validator: exists_with_issues cuenta como verificado en producción."""

    def test_verified_in_production_includes_with_issues(self):
        validator = CoherenceValidator()
        report = {
            "results": {
                "hotel_schema": {
                    "status": "exists_with_issues",
                    "site_verified": True,
                }
            },
            "hotel_schema": {
                "status": "exists_with_issues",
                "site_verified": True,
            },
        }

        verified = validator._extract_verified_in_production_types(report)

        assert "hotel_schema" in verified

    def test_verified_in_production_excludes_not_exists(self):
        validator = CoherenceValidator()
        report = {
            "results": {"hotel_schema": {"status": "not_exists", "site_verified": True}}
        }

        verified = validator._extract_verified_in_production_types(report)

        assert "hotel_schema" not in verified


class TestDPF3CatalogFallback:
    """D-PF3 (hardening residual): contrato del catálogo para ausencia genuina."""

    def _audit_result(self, hotel_schema_detected: bool) -> MagicMock:
        audit = MagicMock()
        audit.url = "https://www.hotelsalentoreal.com/"
        audit.schema.hotel_schema_detected = hotel_schema_detected
        audit.schema.faq_schema_detected = True
        audit.schema.org_schema_detected = True
        audit.gbp.geo_score = 85
        audit.gbp.reviews = 200
        audit.performance.mobile_score = 90
        audit.performance.has_field_data = True
        # Checks numéricos FASE-2 de detect_pains (L494-528): valores sanos
        # para que ningún pain GEO se dispare por atributos Mock sin valor.
        audit.ai_crawlers.overall_score = 0.9
        audit.citability.overall_score = 80.0
        audit.ia_readiness.overall_score = 70.0
        audit.seo_elements = None
        audit.metadata.has_issues = False
        return audit

    def _validation_summary(self, fields: dict) -> SimpleNamespace:
        field_objs = [
            SimpleNamespace(field_name=name, confidence=conf)
            for name, conf in fields.items()
        ]
        return SimpleNamespace(
            fields=field_objs,
            get_field=lambda name: next(
                (f for f in field_objs if f.field_name == name), None
            ),
        )

    def test_no_hotel_schema_pain_not_generated_when_detected(self):
        """AC6: con schema detectado por el audit el pain NO se genera."""
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(
            self._audit_result(hotel_schema_detected=True),
            self._validation_summary({}),
        )
        assert "no_hotel_schema" not in [p.id for p in pains]

    def test_no_hotel_schema_pain_fires_on_genuine_absence(self):
        """Ausencia GENUINA (audit sin error, 0 schemas) sí detecta el pain."""
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(
            self._audit_result(hotel_schema_detected=False),
            self._validation_summary({}),
        )
        assert "no_hotel_schema" in [p.id for p in pains]

    def test_dp_f3_fallback_generates_with_available_sources(self):
        """Ausencia genuina + fuentes disponibles → can_generate vía catálogo."""
        mapper = PainSolutionMapper()
        confidence = {
            "schema_hotel_detected": 0.0,
            "hotel_name": 0.95,
            "gbp_rating": 0.9,
        }

        specs = mapper.get_assets_for_pain("no_hotel_schema", confidence)

        assert len(specs) == 1
        spec = specs[0]
        assert spec.asset_type == "hotel_schema"
        assert spec.can_generate is True
        assert "D-PF3" in spec.reason or "fallback" in spec.reason

    def test_dp_f3_no_sources_blocks_with_justified_skip(self):
        """Sin fuentes (confianza 0.00 en todo) → bloqueo con justified_skip."""
        mapper = PainSolutionMapper()
        confidence = {"schema_hotel_detected": 0.0}

        specs = mapper.get_assets_for_pain("no_hotel_schema", confidence)

        assert len(specs) == 1
        spec = specs[0]
        assert spec.can_generate is False
        assert "justified_skip" in spec.reason

    def test_preflight_respects_catalog_fallback_contract(self):
        """El preflight deriva del catálogo: block_on_failure=False → WARNING
        con fallback_action=generate_basic_schema y can_proceed=True."""
        checker = PreflightChecker()

        report = checker.check_asset("hotel_schema", {})

        assert report.can_proceed is True
        assert report.overall_status.value == "warning"
        assert report.checks[0].fallback_action == "generate_basic_schema"
