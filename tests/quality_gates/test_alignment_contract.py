"""FASE-SR-B (D-PF1): Test de contrato de las 3 capas de la promesa.

Para un pain_ledger dado, las tres capas del pipeline deben reportar el MISMO
conjunto de servicios comprometidos (fuente única — L-SR3/L-NC10):

  Capa 1 (RC1):    v4_proposal_generator — _derive_committed_services +
                   _generate_dynamic_services_table (la promesa textual)
  Capa 2 (Matriz): AssetAlignmentMatrix.committed_services
                   (proposal_asset_matrix.json)
  Capa 3 (Gate):   publication_gates._proposal_asset_alignment_gate
                   (coverage_ratio sobre el conjunto actionable)

Escenario corrida C (Hotel Salento Real, 2026-08-27 18:30): 7 servicios,
2 LINKED, 1 present_in_production (llms_txt vía presencia), 1 MISSING-con-pain
(hotel_schema), 3 NO_BREACH. Coverage esperado sobre actionable = 3/4 = 0.75
(estado intermedio documentado hasta SR-E; tras SR-E → 3/3 = 1.0).

Anti-B7 (D-NC7): un servicio sin pain ni presencia NUNCA se promete — no
aparece como fila comprometida ni en el footnote "Servicios adicionales".
"""

import pytest
from types import SimpleNamespace

from modules.asset_generation.proposal_asset_alignment import (
    AssetAlignmentMatrix,
    PROPOSAL_SERVICE_TO_ASSET,
    derive_committed_services,
)
from modules.delivery.delivery_context import DeliveryContext
from modules.quality_gates.alignment_result import AlignmentResult
from modules.quality_gates.publication_gates import (
    GateStatus,
    PublicationGatesOrchestrator,
)


# ── Escenario corrida C (L3: tests contra fuente dinámica — pain_ids REALES
# de PainSolutionMapper.PAIN_SOLUTION_MAP, no valores inventados):
#   no_hotel_schema → hotel_schema · no_org_schema → org_schema ·
#   no_faq_schema → faq_page
PAIN_LEDGER = [
    {"pain_id": "no_hotel_schema"},
    {"pain_id": "no_org_schema"},
    {"pain_id": "no_faq_schema"},
]
GENERATED_ASSETS = [
    {"asset_type": "org_schema", "confidence_score": 0.9},
    {"asset_type": "faq_page", "confidence_score": 0.85},
]
# Snapshot canónico dict (misma forma que site_presence_adapter
# .normalize_site_presence) — consumido por matriz/DTO/gate.
SITE_PRESENCE_DICT = {
    "results": {"llms_txt": {"status": "exists"}},
    "llms_txt": {"status": "exists"},
}
# Objeto SitePresenceReport-like (.results con enums .value) — forma que
# consume la tabla RC1 (presence_lookup).
SITE_PRESENCE_OBJ = SimpleNamespace(
    results={
        "llms_txt": SimpleNamespace(status=SimpleNamespace(value="exists")),
    },
)

# Fuente única D-PF1: comprometido = pain mapeado OR presencia exists.
COMMITTED_C = {
    "Schema Organization",               # pain no_org_schema → LINKED
    "Página de FAQ",                     # pain no_faq_schema → LINKED
    "Optimización para IA Generativa",   # presencia llms_txt exists
    "Schema Hotel",                      # pain no_hotel_schema → MISSING (pendiente)
}


class TestContractProposalLayer:
    """Capa 1 (RC1): la propuesta deriva su promesa de la fuente única."""

    def _generator(self):
        from modules.commercial_documents.v4_proposal_generator import (
            V4ProposalGenerator,
        )
        # __new__: la tabla dinámica no requiere el template en disco
        return V4ProposalGenerator.__new__(V4ProposalGenerator)

    def test_committed_derived_from_unique_source(self):
        committed = self._generator()._derive_committed_services(
            PAIN_LEDGER, SITE_PRESENCE_DICT, GENERATED_ASSETS
        )
        assert set(committed) == COMMITTED_C

    def test_committed_none_without_pain_ledger(self):
        """Sin pain_ledger → None (modo legacy: catálogo estático)."""
        gen = self._generator()
        assert gen._derive_committed_services(
            None, SITE_PRESENCE_DICT, GENERATED_ASSETS
        ) is None
        assert gen._derive_committed_services(
            [], SITE_PRESENCE_DICT, GENERATED_ASSETS
        ) is None

    def test_table_renders_exactly_committed_rows(self):
        gen = self._generator()
        committed = gen._derive_committed_services(
            PAIN_LEDGER, SITE_PRESENCE_DICT, GENERATED_ASSETS
        )
        table = gen._generate_dynamic_services_table(
            assets_generated=GENERATED_ASSETS,
            site_presence_report=SITE_PRESENCE_OBJ,
            committed_services=committed,
        )
        body, _, footnote = table.partition(
            "> **Servicios adicionales disponibles:**"
        )
        # Cada compromiso aparece como fila de servicio
        for name in COMMITTED_C:
            assert f"**{name}**" in body
        # EXACTAMENTE 4 filas comprometidas (los otros 3 → footnote)
        rows = [ln for ln in body.splitlines() if ln.startswith("| **")]
        assert len(rows) == 4
        # No comprometidos → footnote "disponibles SIN compromiso" (D-PF1)
        assert "sin compromiso" in footnote
        assert "SEO Local" in footnote
        assert "Meta Tags Sociales (Open Graph)" in footnote
        # B7 (D-NC7): WhatsApp sin brecha ni presencia NO aparece NUNCA
        # (ni como fila, ni en el footnote)
        assert "Botón de WhatsApp" not in table
        # AEO: no duplica la fila del mismo asset (llms_txt ya está como fila)
        aeo_rows = [
            ln for ln in body.splitlines()
            if "**Optimización para IA Generativa**" in ln
        ]
        assert len(aeo_rows) == 1

    def test_states_identical_per_service_across_layers(self):
        """Estados por servicio idénticos entre la matriz (capa 2) y la fila
        textual de la propuesta (capa 1)."""
        matrix = AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=PAIN_LEDGER,
            generated_assets=GENERATED_ASSETS,
        )
        status_of = {e.service_name: e.status for e in matrix.entries}
        gen = self._generator()
        committed = gen._derive_committed_services(
            PAIN_LEDGER, SITE_PRESENCE_DICT, GENERATED_ASSETS
        )
        table = gen._generate_dynamic_services_table(
            assets_generated=GENERATED_ASSETS,
            site_presence_report=SITE_PRESENCE_OBJ,
            committed_services=committed,
        )
        body, _, _footnote = table.partition(
            "> **Servicios adicionales disponibles:**"
        )
        row_of = {
            svc: next(ln for ln in body.splitlines() if f"**{svc}**" in ln)
            for svc in COMMITTED_C
        }
        # Taxonomía de la matriz (capa 2)
        assert status_of["Schema Organization"] == "LINKED"
        assert status_of["Página de FAQ"] == "LINKED"
        # NO_BREACH estático en matriz — la presencia lo re-clasifica a
        # covered en el DTO canónico (_from_entries) y se muestra como
        # "Presente en sitio" en la propuesta (capa 1).
        assert status_of["Optimización para IA Generativa"] == "NO_BREACH"
        assert status_of["Schema Hotel"] == "MISSING_ASSET"
        # Estados textuales de la propuesta (capa 1) — equivalentes
        assert "✅ Alineado" in row_of["Schema Organization"]
        assert "✅ Alineado" in row_of["Página de FAQ"]
        assert "ℹ️ Presente en sitio" in row_of["Optimización para IA Generativa"]
        assert "⏳ Pendiente" in row_of["Schema Hotel"]


class TestAntiB7:
    """FASE-SR-B + D-NC7: servicio sin pain ni presencia nunca se promete."""

    def test_whatsapp_not_committed_without_pain_or_presence(self):
        committed = derive_committed_services(
            [{"pain_id": "no_org_schema"}], None, []
        )
        assert "Botón de WhatsApp" not in committed

    def test_whatsapp_never_rendered_without_pain_or_presence(self):
        """Ni fila comprometida ni footnote (B7): sin brecha no se lista."""
        from modules.commercial_documents.v4_proposal_generator import (
            V4ProposalGenerator,
        )
        gen = V4ProposalGenerator.__new__(V4ProposalGenerator)
        committed = derive_committed_services(
            [{"pain_id": "no_org_schema"}], None, []
        )
        table = gen._generate_dynamic_services_table(
            assets_generated=[],
            site_presence_report=None,
            committed_services=committed,
        )
        assert "Botón de WhatsApp" not in table
        # El compromiso declarado sí está (Schema Organization, pendiente)
        assert "**Schema Organization**" in table


class TestContractGateLayer:
    """Capa 3 (Gate): verifica EXACTAMENTE el committed set (override D-PF1)."""

    def _orchestrator(self):
        return PublicationGatesOrchestrator()

    def _assessment(self):
        return {
            "pain_ledger": PAIN_LEDGER,
            "generated_assets": GENERATED_ASSETS,
            "site_presence_report": SITE_PRESENCE_DICT,
            "hotel_url": "",
        }

    def test_gate_verifies_exactly_committed_scope(self):
        result = self._orchestrator()._proposal_asset_alignment_gate(
            self._assessment()
        )
        # coverage sobre actionable = 3/4 (AC1) — NO_BREACH fuera del
        # denominador. Estado intermedio: 0.75 < 0.80 → BLOCKED hasta SR-E.
        assert result.value == pytest.approx(3 / 4)
        assert result.status == GateStatus.BLOCKED
        assert result.details["alignment"]["unresolved"] == 1  # hotel_schema
        assert result.details["alignment"]["actionable_total"] == 4

    def test_gate_matches_delivery_report_same_run(self):
        """AC3: gate_report ≡ delivery_quality_report para el MISMO run."""
        result = self._orchestrator()._proposal_asset_alignment_gate(
            self._assessment()
        )
        matrix = AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=PAIN_LEDGER,
            generated_assets=GENERATED_ASSETS,
        )
        delivery = AlignmentResult.from_asset_alignment_matrix(
            matrix, SITE_PRESENCE_DICT
        )
        assert result.details["alignment"] == delivery.to_dict()

    def test_gate_trivial_pass_zero_committed(self):
        """Pain sin mapeo a servicios → 0 comprometidos → PASS trivial
        (never-block): nada prometido, nada puede estar 'missing'."""
        result = self._orchestrator()._proposal_asset_alignment_gate({
            "pain_ledger": [{"pain_id": "pain_no_mapeado_a_servicios"}],
            "generated_assets": [],
            "site_presence_report": None,
            "hotel_url": "",
        })
        assert result.passed is True
        assert result.value == 1.0
        assert "0 servicios comprometidos" in result.message

    def test_gate_legacy_without_pain_ledger_uses_static_catalog(self):
        """Sin pain_ledger → comportamiento legacy pre-SR-B (catálogo
        estático): 7 servicios, coverage 3/7 (verificación de entrega)."""
        result = self._orchestrator()._proposal_asset_alignment_gate({
            "pain_ledger": [],
            "generated_assets": GENERATED_ASSETS,
            "site_presence_report": SITE_PRESENCE_DICT,
            "hotel_url": "",
        })
        assert result.details["alignment"]["promised_services_total"] == 7
        assert result.details["alignment"]["no_breach"] == 0  # no knowable aquí
