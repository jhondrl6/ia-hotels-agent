"""FASE-HOTFIX-PRE-RELEASE / H2 (AC7, S-I2): la severidad debe ser legible en
el artefacto `gate_report_*.json`, no solo en el codigo y los tests.

FASE-VERIFY certifico AC7 ⚠️ porque el `gate_report` de la unica corrida del plan
serializaba 7 claves por gate y **cero** de severidad (`severity`: 0 ocurrencias).
L-V1: un validador que no lee el artefacto que el sistema produce certifica un
mundo que produccion no habita — por eso estos tests **leen el JSON que quedo en
disco**, no el objeto en memoria.

Insumo real: una copia de `evidence/FASE-I/corrida/hotelsalentoreal/v4_audit/`
(los artefactos de la unica corrida E2E del plan). Sin red, sin LLM, sin
`v4complete`.
"""

import json
from pathlib import Path

import pytest

from main import _build_gate_report_payload, _make_evidence_path
from modules.quality_gates.publication_gates import (
    ADVISORY_GATE_NAMES,
    BLOCKING_GATE_NAMES,
    GateStatus,
    PublicationGateResult,
    gate_blocks_publication,
    gate_severity,
)

RUN_GATE_REPORT = (
    Path("evidence/FASE-I/corrida/hotelsalentoreal/v4_audit")
    / "gate_report_20260904_120413.json"
)


def _results_from_real_run() -> list:
    """Reconstruir los 13 gates de la corrida real como PublicationGateResult."""
    data = json.loads(RUN_GATE_REPORT.read_text(encoding="utf-8"))
    return [
        PublicationGateResult(
            gate_name=g["gate_name"],
            passed=g["passed"],
            status=GateStatus(g["status"]),
            message=g["message"],
            value=g["value"],
            suggestion=g.get("suggestion", ""),
            details=g.get("details", {}) or {},
        )
        for g in data["gate_results"]
    ]


def _write_and_read(tmp_path: Path, results: list) -> dict:
    """Escribir con el MISMO camino de produccion y leer lo que quedo en disco."""
    payload = _build_gate_report_payload(
        results,
        {
            "status": "READY_FOR_PUBLICATION",
            "ready": True,
            "blocking_issues": [],
            "summary": {"warnings": []},
        },
        hotel_url="https://hotelsalentoreal.com.co",
    )
    path = _make_evidence_path(tmp_path, "hotelsalentoreal", "gate_report", "20260904_120413")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    # Leer en disco (L-F3 / L-V1): el contrato es el archivo, no el objeto.
    return json.loads(path.read_text(encoding="utf-8"))


class TestGateReportSeveridadEnDisco:
    """AC7: las 11 blocking + 2 advisory deben poder reconstruirse del artefacto."""

    @pytest.fixture(scope="class")
    def artifact(self, tmp_path_factory):
        results = _results_from_real_run()
        out_dir = tmp_path_factory.mktemp("gate_report")
        return _write_and_read(out_dir, results), results

    def test_cada_gate_trae_severity_y_bloqueo(self, artifact):
        payload, _ = artifact
        for g in payload["gate_results"]:
            assert g["severity"] in ("blocking", "advisory"), g
            assert isinstance(g["blocks_publication"], bool), g

    def test_severidad_derivada_del_criterio_canonico(self, artifact):
        payload, _ = artifact
        por_severidad = {}
        for g in payload["gate_results"]:
            por_severidad.setdefault(g["severity"], []).append(g["gate_name"])
        # Comparado contra las listas canonicas, no contra un numero literal.
        assert set(por_severidad["advisory"]) == set(ADVISORY_GATE_NAMES)
        assert set(por_severidad["blocking"]) >= set(BLOCKING_GATE_NAMES) & {
            g["gate_name"] for g in payload["gate_results"]
        }

    def test_la_palabra_severity_existe_en_el_archivo(self, artifact):
        """El criterio de AC7 sobre artefacto: legible por un lector del ZIP."""
        payload, _ = artifact
        assert sum(1 for g in payload["gate_results"] if "severity" in g) == len(
            payload["gate_results"]
        )

    def test_blocks_publication_coincide_con_el_predicado(self, artifact):
        payload, results = artifact
        by_name = {g["gate_name"]: g for g in payload["gate_results"]}
        for r in results:
            assert by_name[r.gate_name]["blocks_publication"] is gate_blocks_publication(r)

    def test_en_la_corrida_real_ningun_gate_bloquea(self, artifact):
        """La corrida I dio ready=true: el artefacto debe decir lo mismo."""
        payload, _ = artifact
        assert [g["gate_name"] for g in payload["gate_results"] if g["blocks_publication"]] == []
        assert payload["readiness"]["ready"] is True


class TestGateReportSeveridadDiscrimina:
    """Un valor que siempre vale lo mismo no prueba nada: los casos adversos.

    FASE-H midio que «blocks_publication» no puede ser `not passed` — los tres
    estados (FAILED blocking / advisory sobre el piso / NOT_EVALUATED) dan
    respuestas distintas y solo el predicado canónico las conoce.
    """

    def test_blocking_fallido_bloquea_advisory_fallido_no(self, tmp_path):
        results = [
            PublicationGateResult(
                gate_name="evidence_coverage", passed=False, status=GateStatus.FAILED,
                message="coverage 0.5", value=0.5,
            ),
            PublicationGateResult(
                # advisory por debajo del piso: SI bloquea (degrada a blocking)
                gate_name="proposal_asset_alignment", passed=False, status=GateStatus.FAILED,
                message="coverage 0.5", value=0.5,
            ),
            PublicationGateResult(
                # advisory que falla sin degradar (content_quality sin blockers)
                gate_name="content_quality", passed=False, status=GateStatus.WARNING,
                message="advertencia de redaccion", value=0.9,
            ),
            PublicationGateResult(
                # gate no evaluado: visible, no bloquea, no pasa
                gate_name="doc_audit_consistency", passed=False,
                status=GateStatus.NOT_EVALUATED, message="insumo no disponible", value=None,
            ),
        ]
        payload = _write_and_read(tmp_path, results)
        by_name = {g["gate_name"]: g for g in payload["gate_results"]}
        assert by_name["evidence_coverage"]["blocks_publication"] is True
        assert by_name["proposal_asset_alignment"]["blocks_publication"] is True
        assert by_name["content_quality"]["blocks_publication"] is False
        assert by_name["doc_audit_consistency"]["blocks_publication"] is False
        # ...y los cuatro NO son «passed»: el artefacto distingue los tres ejes.
        assert all(g["passed"] is False for g in payload["gate_results"])

    def test_writer_no_copia_listas_de_severidad(self):
        """DA-V1 / L-F2: el writer deriva, no mantiene una tercera lista de nombres.

        Un literal con nombres de gate en el escritor seria la segunda
        representacion del mismo hecho que este plan persigue.
        """
        import inspect

        src = inspect.getsource(_build_gate_report_payload)
        assert "gate_severity(" in src
        assert "gate_blocks_publication(" in src
        for gate_name in set(BLOCKING_GATE_NAMES) | set(ADVISORY_GATE_NAMES):
            assert f'"{gate_name}"' not in src, f"el writer enumera {gate_name} a mano"
