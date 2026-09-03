"""
Contratos FASE-C — propuesta dinámica (Punto 8).

Codifica el contrato de `evidence/FASE-C/contrato-propuesta-dinamica.md`:

* AC5 — ``no_breach == 0`` **por construcción**: la matriz sólo promete
  servicios con brecha detectada (pain mapeado) O presencia verificada.
  Los servicios sin compromiso no desaparecen: quedan en ``not_promised``.
* AC6 — los complementos siempre-activos (``counts_in_alignment=False``)
  no entran al denominador de ``assets_are_justified``: no se prometen por
  pain, se entregan por modelo de servicio.
* vacío ≠ ausente — ``pain_ledger=[]`` (0 comprometidos) no se colapsa con
  ``pain_ledger=None`` (catálogo estático legacy).
* anti-A5 — los DOS builders particionan idéntico y el skip de servicio
  desconocido es visible (log + contador), no silencioso.

Los asserts fijan **relaciones**, no valores fijos (L-NC10).
"""

import logging

import pytest

from modules.asset_generation.pain_ledger import PainLedgerEntry
from modules.asset_generation.proposal_asset_alignment import (
    ALL_PROMISED_SERVICES,
    ALWAYS_ACTIVE_COMPLEMENT_ASSETS,
    AssetAlignmentMatrix,
    ProposalAssetMatrix,
)
from modules.asset_generation.v4_asset_orchestrator import GeneratedAsset
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.commercial_documents.data_structures import (
    AssetSpec,
    DiagnosticDocument,
)
from modules.common.service_identity import SERVICE_IDENTITIES
from modules.delivery.delivery_context import DeliveryContext
from modules.quality_gates.alignment_result import AlignmentResult


# ── Fixtures ──────────────────────────────────────────────────────────

def _entry(pain_id: str, severity: str = "HIGH") -> PainLedgerEntry:
    return PainLedgerEntry(
        pain_id=pain_id,
        source_module="pain_solution_mapper",
        source_file="schema_validator_v2.py",
        severity=severity,
        confidence=0.9,
        status="DETECTED",
        human_label=pain_id,
        evidence_refs=[f"{pain_id}=true"],
    )


@pytest.fixture
def ledger_dos_brechas():
    """Ledger resuelto con 2 brechas de los 7 servicios alineables."""
    return [_entry("no_whatsapp_visible"), _entry("no_hotel_schema")]


@pytest.fixture
def assets_whatsapp_schema():
    return [
        GeneratedAsset(
            asset_type="whatsapp_button",
            filename="whatsapp_button.html",
            path="/tmp/o/whatsapp_button.html",
            metadata_path="/tmp/o/wa.json",
            preflight_status="PASSED",
            confidence_score=0.95,
            pain_ids_resolved=["no_whatsapp_visible"],
            can_use=True,
            delivery_filename="boton_whatsapp.html",
        ),
        GeneratedAsset(
            asset_type="hotel_schema",
            filename="hotel_schema.json",
            path="/tmp/o/hotel_schema.json",
            metadata_path="/tmp/o/hs.json",
            preflight_status="PASSED",
            confidence_score=0.9,
            pain_ids_resolved=["no_hotel_schema"],
            can_use=True,
            delivery_filename="hotel_schema.jsonld",
        ),
    ]


def _diagnostic(problem_ids):
    class _P:
        def __init__(self, pid):
            self.id = pid

    return DiagnosticDocument(
        path="/tmp/d.md",
        problems=[_P(p) for p in problem_ids],
        financial_impact=None,
        generated_at="2026-09-03",
    )


# ═══════════════════════════════════════════════════════════════════════
# AC6 — complementos siempre-activos fuera del denominador
# ═══════════════════════════════════════════════════════════════════════

class TestComplementosFueraDeJustificacion:
    """El defecto estructural: un asset que NUNCA puede tener pain_id
    (porque no se promete por pain) arrastra ``assets_are_justified`` a
    < 0.8 en TODA corrida ⟹ ``is_coherent=False`` estructural."""

    def test_registry_declara_al_menos_un_complemento(self):
        """El conjunto de complementos se deriva del registro canónico."""
        esperados = {
            i.asset_type for i in SERVICE_IDENTITIES if not i.counts_in_alignment
        }
        assert ALWAYS_ACTIVE_COMPLEMENT_ASSETS == esperados
        assert esperados, "FASE-A congeló al menos un complemento siempre-activo"

    def test_complemento_no_cuenta_en_el_denominador(self):
        validator = CoherenceValidator()
        assets = [
            AssetSpec(asset_type="whatsapp_button", pain_ids=["no_whatsapp_visible"]),
            AssetSpec(asset_type="hotel_schema", pain_ids=["no_hotel_schema"]),
            AssetSpec(asset_type="faq_page", pain_ids=["no_faq_schema"]),
            AssetSpec(asset_type="monthly_report", pain_ids=[]),  # complemento
        ]
        check = validator._check_assets_are_justified(
            assets, _diagnostic(["no_whatsapp_visible", "no_hotel_schema", "no_faq_schema"])
        )
        # 3 prometidos por pain, 3 justificados ⟹ 1.0 (no 0.75)
        assert check.score == pytest.approx(1.0)
        assert check.passed is True
        assert check.severity != "error"

    def test_asset_sin_pain_que_no_es_complemento_sigue_restando(self):
        """Dientes intactos: sólo el complemento queda fuera. Un asset
        cualquiera sin pain_id sigue siendo un defecto de coherencia."""
        validator = CoherenceValidator()
        assets = [
            AssetSpec(asset_type="whatsapp_button", pain_ids=["no_whatsapp_visible"]),
            AssetSpec(asset_type="open_graph", pain_ids=[]),  # NO complemento
        ]
        check = validator._check_assets_are_justified(
            assets, _diagnostic(["no_whatsapp_visible"])
        )
        assert check.score == pytest.approx(0.5)
        assert check.passed is False

    def test_solo_complementos_no_divide_por_cero(self):
        validator = CoherenceValidator()
        assets = [AssetSpec(asset_type="monthly_report", pain_ids=[])]
        check = validator._check_assets_are_justified(assets, _diagnostic([]))
        assert check.score == pytest.approx(1.0)
        assert check.passed is True


# ═══════════════════════════════════════════════════════════════════════
# AC5 — no_breach == 0 por construcción
# ═══════════════════════════════════════════════════════════════════════

class TestMatrizSoloPrometeConBrecha:

    def _build(self, ledger, assets, presence=None):
        return AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=ledger,
            generated_assets=assets,
            site_presence_report=presence,
        )

    def test_servicios_sin_brecha_no_son_entradas(self, ledger_dos_brechas, assets_whatsapp_schema):
        matrix = self._build(ledger_dos_brechas, assets_whatsapp_schema)
        statuses = [e.status for e in matrix.entries]
        assert "NO_BREACH" not in statuses, (
            "Con propuesta dinámica ningún servicio sin brecha entra a la matriz"
        )
        # 2 brechas ⟹ 2 servicios comprometidos, no los 7 del catálogo
        assert len(matrix.entries) == 2
        assert len(matrix.entries) < len(ALL_PROMISED_SERVICES)

    def test_alignment_result_da_no_breach_cero(self, ledger_dos_brechas, assets_whatsapp_schema):
        matrix = self._build(ledger_dos_brechas, assets_whatsapp_schema)
        result = AlignmentResult.from_asset_alignment_matrix(matrix)
        assert result.no_breach == 0
        # AC5: los denominadores convergen ⟹ la tautología se disuelve
        assert result.actionable_total == result.promised_services_total
        assert result.unresolved == 0
        assert result.coverage_ratio == pytest.approx(1.0)

    def test_invariante_de_aritmetica_se_mantiene(self, ledger_dos_brechas, assets_whatsapp_schema):
        """Identidad, no valores: effective + unresolved + no_breach == total."""
        matrix = self._build(ledger_dos_brechas, assets_whatsapp_schema)
        r = AlignmentResult.from_asset_alignment_matrix(matrix)
        assert r.effective_total + r.unresolved + r.no_breach == r.promised_services_total

    def test_brecha_sin_asset_generado_es_deuda_visible(
        self, ledger_dos_brechas, assets_whatsapp_schema
    ):
        """Quitar un asset NO debe volverlo 'sin brecha': es MISSING_ASSET."""
        solo_whatsapp = assets_whatsapp_schema[:1]
        matrix = self._build(ledger_dos_brechas, solo_whatsapp)
        r = AlignmentResult.from_asset_alignment_matrix(matrix)
        assert r.unresolved == 1
        assert r.passed is False
        assert r.coverage_ratio == pytest.approx(0.5)

    def test_servicios_excluidos_quedan_visibles(self, ledger_dos_brechas, assets_whatsapp_schema):
        """Auditoría: lo no prometido se declara, no se descarta en silencio."""
        matrix = self._build(ledger_dos_brechas, assets_whatsapp_schema)
        prometidos = {e.service_name for e in matrix.entries}
        assert set(matrix.not_promised) == set(ALL_PROMISED_SERVICES) - prometidos
        assert matrix.not_promised, "Con 2 de 7 brechas debe haber excluidos"
        assert "not_promised" in matrix.to_dict()

    def test_presencia_compromete_servicio_sin_brecha(self, ledger_dos_brechas, assets_whatsapp_schema):
        """D-PF1: committed = pain mapeado OR presencia ``exists``."""
        presence = {"faq_page": {"status": "exists"}}
        matrix = self._build(ledger_dos_brechas, assets_whatsapp_schema, presence)
        nombres = {e.service_name for e in matrix.entries}
        faq = next(i.service_name for i in SERVICE_IDENTITIES if i.asset_type == "faq_page")
        assert faq in nombres
        assert len(matrix.entries) == 3
        assert faq not in matrix.not_promised


# ═══════════════════════════════════════════════════════════════════════
# vacío ≠ ausente
# ═══════════════════════════════════════════════════════════════════════

class TestVacioNoEsAusente:

    def test_ledger_vacio_cero_comprometidos(self, assets_whatsapp_schema):
        matrix = AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=[],
            generated_assets=assets_whatsapp_schema,
        )
        assert matrix.entries == []
        assert len(matrix.not_promised) == len(ALL_PROMISED_SERVICES)
        r = AlignmentResult.from_asset_alignment_matrix(matrix)
        assert r.promised_services_total == 0
        assert r.no_breach == 0
        assert r.actionable_total == 0

    def test_ledger_ausente_conserva_catalogo_estatico(self, assets_whatsapp_schema):
        """``None`` = sin ledger ⟹ modo legacy: los 7 con NO_BREACH donde no
        haya pain. No se puede colapsar con el caso anterior."""
        matrix = AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=None,
            generated_assets=assets_whatsapp_schema,
        )
        assert len(matrix.entries) == len(ALL_PROMISED_SERVICES)
        assert matrix.not_promised == []
        assert any(e.status == "NO_BREACH" for e in matrix.entries)


# ═══════════════════════════════════════════════════════════════════════
# anti-A5 — los DOS builders particionan igual; skip visible
# ═══════════════════════════════════════════════════════════════════════

class TestAmbosBuildersIdenticos:
    """A5: los dos builders tenían rutas de descarte silencioso idénticas en
    5/5 variantes medidas. Tocar uno solo re-introduce la deriva."""

    VARIANTES = [
        ("con brechas y assets", ["no_whatsapp_visible", "no_hotel_schema"], True),
        ("brecha sin asset", ["no_whatsapp_visible"], False),
        ("ledger vacio", [], True),
        ("sin presencia ni pain", ["no_og_tags"], False),
    ]

    @pytest.mark.parametrize("nombre,pains,con_assets", VARIANTES)
    def test_particion_identica(self, nombre, pains, con_assets, assets_whatsapp_schema):
        ledger = [_entry(p) for p in pains]
        assets = assets_whatsapp_schema if con_assets else []
        servicios = list(ALL_PROMISED_SERVICES)

        m1 = ProposalAssetMatrix()
        entries1 = m1.build(servicios, ledger, assets)
        m2 = AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=ledger,
            generated_assets=assets,
        )

        clave1 = sorted((e.service_name, e.status) for e in entries1)
        clave2 = sorted((e.service_name, e.status) for e in m2.entries)
        assert clave1 == clave2, f"Deriva A5 en variante '{nombre}'"
        assert sorted(m1.not_promised) == sorted(m2.not_promised)

    def test_skip_de_servicio_desconocido_es_visible(self, caplog):
        """El comentario literal 'Unknown service — skip silently' es el
        defecto: debe quedar rastro observable."""
        m = ProposalAssetMatrix()
        with caplog.at_level(logging.WARNING):
            entries = m.build(
                ["Servicio Inexistente", "Botón de WhatsApp"],
                [_entry("no_whatsapp_visible")],
                [],
            )
        assert all(e.service_name != "Servicio Inexistente" for e in entries)
        assert "Servicio Inexistente" in m.unknown_services
        assert any("Servicio Inexistente" in r.getMessage() for r in caplog.records)
