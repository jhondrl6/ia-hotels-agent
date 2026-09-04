"""FASE-HOTFIX-PRE-RELEASE / H6 (S-C3, mitad textual): la prosa que lee el
cliente debe narrar el conteo verificado en runtime, no el tamano del catalogo.

Medido por FASE-VERIFY y reproducedo aqui: `promised_assets_exist` publicaba
«7 servicios verificados via PROPOSAL_SERVICE_TO_ASSET» en los tres artefactos de
la corrida (`asset_generation_report.json`, `coherence_validation.json`,
`coherence_validation_post_gen.json`) mientras la matriz de esa misma corrida
declaraba `summary.promised = 4`. Es el defecto B2 (registro estatico vs runtime)
reaparecido en la tercera superficie: el mensaje.

La barra de esta sesion (L-V1): el numero se verifica **en el JSON que el writer
de produccion deja en disco**, con insumos de la unica corrida E2E del plan.

Fuera de alcance a proposito (P12, dueno tribunal): `score=1.0` fijo, que el
check solo corra pre-gen y la union del denominador. Aqui cambia solo el string.
"""

import json
import re
from pathlib import Path
from typing import List

from modules.asset_generation.site_presence_adapter import normalize_site_presence
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.commercial_documents.data_structures import (
    AssetSpec,
    DiagnosticDocument,
    ProposalDocument,
    Scenario,
)

AUDIT_DIR = Path("evidence/FASE-I/corrida/hotelsalentoreal/v4_audit")

# Escenario sin dolor financiero: `price_matches_pain` corta en su rama
# «no hay dolor» y no interfiere con el check que aqui se certifica.
_ESCENARIO = Scenario(
    monthly_loss_min=0, monthly_loss_max=0, probability=0.7, description="fixture FASE-HOTFIX"
)


class _Summary:
    """ValidationSummary minima: los checks bajo prueba no consultan confianza."""

    overall_confidence = "VERIFIED"

    def get_field(self, name):
        return None


def _spec(asset_type: str) -> AssetSpec:
    return AssetSpec(asset_type=asset_type, pain_ids=["p"])


def _diagnostic() -> DiagnosticDocument:
    return DiagnosticDocument(
        path="", problems=[], financial_impact=_ESCENARIO, generated_at="2026-09-04T12:04:13"
    )


def _proposal(assets: List[AssetSpec]) -> ProposalDocument:
    return ProposalDocument(
        path="",
        price_monthly=0,
        assets_proposed=assets,
        roi_projected=0.0,
        generated_at="2026-09-04T12:04:13",
    )


def _real_generated_assets() -> dict:
    """Los 4 assets que la corrida real genero, en la forma del orquestador."""
    data = json.loads(
        (AUDIT_DIR / "asset_generation_report.json").read_text(encoding="utf-8")
    )
    return {
        a["asset_type"]: {
            "can_use": True,
            "confidence_score": a.get("confidence_score", 0.9),
            "filename": a.get("filename", ""),
        }
        for a in data["generated_assets"]
    }


def _real_presence():
    raw = json.loads((AUDIT_DIR / "site_presence_snapshot.json").read_text(encoding="utf-8"))
    return normalize_site_presence(raw["snapshot"])


def _write_report_and_read(tmp_path: Path, specs: List[AssetSpec], generated: dict) -> dict:
    """Correr el `validate` real y leer `coherence_validation.json` del disco."""
    validator = CoherenceValidator()
    report = validator.validate(
        diagnostic=_diagnostic(),
        proposal=_proposal(specs),
        assets=specs,
        validation_summary=_Summary(),
        generated_assets=generated,
        site_presence_report=_real_presence(),
    )
    # CoherenceReport.save: el mismo writer que v4_asset_orchestrator usa en produccion
    report.save(str(tmp_path))
    return json.loads((tmp_path / "coherence_validation.json").read_text(encoding="utf-8"))


def _message_of(report: dict) -> str:
    check = next(c for c in report["checks"] if c["name"] == "promised_assets_exist")
    return check["message"]


class TestMensajeNarrativaRuntime:
    def test_el_numero_narrado_es_el_de_los_assets_verificados(self, tmp_path):
        generated = _real_generated_assets()
        specs = [_spec(t) for t in generated]
        report = _write_report_and_read(tmp_path, specs, generated)
        message = _message_of(report)
        narrado = int(re.search(r"\((\d+) assets verificados", message).group(1))
        assert narrado == len(generated) == 4, message

    def test_el_artifact_ya_no_narra_el_tamano_del_catalogo(self, tmp_path):
        """`len(PROPOSAL_SERVICE_TO_ASSET)` == 7: ese numero no puede aparecer."""
        from modules.asset_generation.proposal_asset_alignment import (
            PROPOSAL_SERVICE_TO_ASSET,
        )

        generated = _real_generated_assets()
        specs = [_spec(t) for t in generated]
        report = _write_report_and_read(tmp_path, specs, generated)
        blob = json.dumps(report, ensure_ascii=False)
        assert "PROPOSAL_SERVICE_TO_ASSET" not in blob
        assert f"{len(PROPOSAL_SERVICE_TO_ASSET)} servicios verificados" not in blob

    def test_el_check_no_cambia_de_veredicto_por_cambiar_el_mensaje(self, tmp_path):
        """H6 es serializacion: passed/score/severity quedan intactos (P12)."""
        generated = _real_generated_assets()
        specs = [_spec(t) for t in generated]
        report = _write_report_and_read(tmp_path, specs, generated)
        check = next(c for c in report["checks"] if c["name"] == "promised_assets_exist")
        assert check["passed"] is True
        assert check["score"] == 1.0
        assert check["severity"] == "info"


class TestMensajeDiscriminaConElInsumo:
    """Un numero que no se mueve con la entrada no demuestra que derive de ella."""

    def test_plan_de_dos_assets_narra_dos(self, tmp_path):
        generated = _real_generated_assets()
        dos = {k: generated[k] for k in list(generated)[:2]}
        specs = [_spec(t) for t in dos]
        report = _write_report_and_read(tmp_path, specs, dos)
        assert "(2 assets verificados" in _message_of(report)

    def test_pre_gen_declara_la_fuente_estatica(self, tmp_path):
        """Rama pre-gen: el texto dice a quien consulto, no inventa runtime."""
        specs = [_spec("llms_txt"), _spec("faq_page")]
        validator = CoherenceValidator()
        coherence_report = validator.validate(
            diagnostic=_diagnostic(),
            proposal=_proposal(specs),
            assets=specs,
            validation_summary=_Summary(),
            generated_assets=None,
            site_presence_report=_real_presence(),
        )
        coherence_report.save(str(tmp_path))
        report = json.loads(
            (tmp_path / "coherence_validation.json").read_text(encoding="utf-8")
        )
        message = _message_of(report)
        assert "via catalogo_estatico" in message, message
        assert "(2 assets verificados" in message, message
