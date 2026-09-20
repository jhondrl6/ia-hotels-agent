"""FASE-0 (AC20) — la evidencia del veredicto se serializa en las dos ramas.

Cubre los tres cambios aditivos de la fase y nada más:

(i)  `PublicationGatesOrchestrator._critical_recall_gate` anota el recall
     FUNDADO, no solo el derivado SR-H2. Causa medida: la corrida
     `output/TAREA7-2026-09-19/` viajó con `value: 1.0, details: {}` y eso es
     exactamente lo que `DiagnosisReviewer._check_vacuous_recall` denuncia como
     `VACUOUS_RECALL` CRITICAL → `BLOQUEADO` → ZIP suprimido.
(ii) `ReviewerReport.to_dict()` proyecta los hallazgos: un acta con
     `critical_count >= 1` ya no puede quedarse sin causa (AC12).
(iii) La rama publish de `run_v4_complete_mode` registra `package_evidence` con
     el mismo contrato que la de supresión (AC-G3), sobre el ZIP entregado.

Límites: no toca `_compute_verdict`, la tabla de cláusulas, `BLOCKING_VERDICTS`,
`GATE_BLOCKING_ENABLED`, los umbrales ni `write/publish/suppress`. La defensa del
caso genuinamente vacuo (SR-H2 / L-SR5) se conserva explícitamente abajo.
"""

import ast
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from main import _build_gate_report_payload
from modules.quality_gates.publication_gates import (
    PublicationGateConfig,
    PublicationGatesOrchestrator,
)
from modules.quality_gates.tribunal.diagnosis_reviewer import (
    FINDING_VACUOUS_RECALL,
    DiagnosisReviewer,
)
from modules.quality_gates.tribunal.outcome import ReviewerReport, ReviewerStatus

# ACTA_FINDING_CAP y ACTA_FINDING_TEXT_LIMIT son símbolos NUEVOS de esta fase: se
# importan dentro de los tests que los usan, para que sobre un árbol sin el fix el
# suite rompa por asercion (guard) y no por ImportError (AC15 lo descarta).

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_RUN = REPO_ROOT / "output" / "TAREA7-2026-09-19" / "v4_complete"
BASELINE_AUDIT = BASELINE_RUN / "hotel_don_alfonso" / "v4_audit" / "audit_report_20260919_150111.json"
MAIN_PY = REPO_ROOT / "main.py"

SCHEMA_KEYS = (
    "hotel_schema_detected",
    "hotel_schema_valid",
    "hotel_confidence",
    "faq_schema_detected",
    "faq_schema_valid",
    "faq_confidence",
)


def _gate_details(assessment):
    orch = PublicationGatesOrchestrator(PublicationGateConfig())
    result = orch._critical_recall_gate(assessment)
    return result, orch._critical_recall_details(assessment)


def _assessment(critical_issues, *, audit_schema=None, audit_data=None, declared_recall=None):
    assessment = {
        "audit_schema": audit_schema if audit_schema is not None else {"hotel_schema_detected": False},
        "critical_issues": list(critical_issues),
    }
    if audit_data is not None:
        assessment["audit_data"] = audit_data
    if declared_recall is not None:
        assessment["critical_recall"] = declared_recall
    return assessment


# --------------------------------------------------------------------------- #
# (i) el camino fundado deja de viajar mudo
# --------------------------------------------------------------------------- #

class TestAnotacionDelCaminoFundado:
    def test_recall_fundado_declara_conteo_y_base(self):
        """critical_issues no vacío + recall 1.0 → `details` fundado (no `{}`)."""
        result = _gate_details(_assessment(["schema ausente", "meta description vacía"]))[0]

        assert result.passed is True
        assert result.value == 1.0
        assert result.details["critical_issues_count"] == 2
        assert result.details["recall_basis"] == "all_critical_issues_detected"

    def test_el_acta_del_revisor_ya_no_denuncia_vacuidad(self, tmp_path):
        """Con la anotación, `_check_vacuous_recall` no emite el CRITICAL que suprimió el ZIP."""
        gate_result, details = _gate_details(_assessment(["schema ausente"]))
        gate_report = _build_gate_report_payload(
            [gate_result],
            {"status": "READY", "ready": True, "blocking_issues": {}, "summary": {}},
        )
        reviewer = DiagnosisReviewer(v4_audit_dir=tmp_path)

        assert gate_report["gate_results"][0]["details"] == details
        assert reviewer._check_vacuous_recall(gate_report) == []

    def test_camino_derivado_sr_h2_conserva_su_serializacion(self):
        """Cero críticos con audit presente sigue con `audit_present_no_critical_issues`."""
        _, details = _gate_details(_assessment([], audit_schema={"hotel_schema_detected": True}))

        assert details == {
            "critical_issues_count": 0,
            "recall_basis": "audit_present_no_critical_issues",
        }

    def test_recall_declarado_sin_lista_sin_audit_sigue_vacio(self, tmp_path):
        """L-SR5: aquí la ausencia SÍ es la señal — el detector sigue denunciando."""
        result, details = _gate_details({"critical_issues": [], "audit_schema": {},
                                         "critical_recall": 1.0})

        assert details == {}
        assert result.details == {}
        findings = DiagnosisReviewer(v4_audit_dir=tmp_path)._check_vacuous_recall(
            {"gate_results": [{"gate_name": "critical_recall", "value": 1.0, "details": {}}]},
        )
        assert [f["finding_type"] for f in findings] == [FINDING_VACUOUS_RECALL]
        assert findings[0]["severity"] == "CRITICAL"

    def test_base_distinta_cuando_el_audit_evidencia_criticos_no_cubiertos(self):
        """Recall fraccional que pasa el umbral declara el conteo y los no cubiertos."""
        issues = [f"critico {i}" for i in range(10)]
        assessment = _assessment(
            issues,
            audit_schema={"hotel_schema_detected": True},
            audit_data={"performance": {"status": "ERROR"}},
        )
        result, details = _gate_details(assessment)

        assert result.passed is True, "10/(10+1) = 0.909 debe seguir pasando el umbral de 0.9"
        assert details["critical_issues_count"] == 10
        assert details["recall_basis"] == "evident_critical_issues_missed"
        assert details["evident_critical_missed"] == 1

    def test_umbral_y_veredicto_del_gate_intactos(self):
        """Cambio de serialización: el gate no cambió de decisión ni de mensaje."""
        assessment = _assessment(["schema ausente"])
        orch = PublicationGatesOrchestrator(PublicationGateConfig())
        result = orch._critical_recall_gate(assessment)

        assert result.status.value == "PASSED"
        assert result.message == "Critical recall at 100.0% (threshold: 90%)"
        assert result.value == orch._extract_critical_recall(assessment)
        assert result.details["critical_issues_count"] == 1


# --------------------------------------------------------------------------- #
# (i) sobre el baseline real de la corrida del 2026-09-19 (L-T2A.2)
# --------------------------------------------------------------------------- #

class TestCaminoFundadoSobreBaselineReal:
    """Reconstruye el assessment con el audit archivado; lectura, nunca escritura."""

    @staticmethod
    def _audit_shim(raw):
        from types import SimpleNamespace

        class Shim:
            def __init__(self):
                self.critical_issues = list(raw.get("overall", {}).get("critical_issues") or [])
                self.schema = SimpleNamespace(**{k: raw["schema"].get(k) for k in SCHEMA_KEYS})

            def to_dict(self):
                return raw

        return Shim()

    def test_sobre_el_audit_real_el_fundado_viaja_anotado(self):
        if not BASELINE_AUDIT.exists():
            pytest.skip(
                f"baseline ausente ({BASELINE_AUDIT}): el AC no se certifica en silencio"
            )
        raw = json.loads(BASELINE_AUDIT.read_text(encoding="utf-8"))
        audit = self._audit_shim(raw)
        result = _gate_details({
            "critical_issues": list(audit.critical_issues),
            "audit_schema": {k: getattr(audit.schema, k) for k in SCHEMA_KEYS},
            "audit_data": raw,
        })[0]

        assert result.value == 1.0
        assert result.details["critical_issues_count"] == len(audit.critical_issues) > 0
        assert result.details["recall_basis"] == "all_critical_issues_detected"

    def test_la_corrida_archivada_confirma_el_hueco_medido(self):
        """El `gate_report` archivado traía 1.0 con `details` vacío: el hecho que AC20 cierra."""
        archived = BASELINE_AUDIT.parent / "gate_report_20260919_150131.json"
        if not archived.exists():
            pytest.skip(f"baseline ausente ({archived}): el AC no se certifica en silencio")
        data = json.loads(archived.read_text(encoding="utf-8"))
        gate = next(g for g in data["gate_results"] if g["gate_name"] == "critical_recall")

        assert gate["value"] == 1.0
        assert gate["details"] == {}


# --------------------------------------------------------------------------- #
# (ii) `ReviewerReport.to_dict` publica las causas
# --------------------------------------------------------------------------- #

def _finding(index):
    return {
        "severity": "CRITICAL" if index == 0 else "WARNING",
        "clause": "P6.1",
        "finding_type": "VACUOUS_RECALL" if index == 0 else "OTRO",
        "source_artifact": "gate_report_*.json",
        "description": "critical_recall=1.0 pero details no declara critical_issues_count.",
        "pain_id": "critical_recall",
    }


def _report(findings, *, critical=1, status=ReviewerStatus.OK_WITH_FINDINGS):
    return ReviewerReport(
        reviewer="diagnosis_reviewer",
        status=status,
        findings_count=len(findings),
        critical_count=critical,
        recommendation="BLOQUEAR" if critical else "APROBADO",
        report_path="revision_diagnostico.json",
        findings=findings,
    )


class TestToDictPublicaHallazgos:
    def test_los_cuatro_campos_de_la_causa_estan(self):
        payload = _report([_finding(0)]).to_dict()

        assert payload["critical_count"] == 1
        assert payload["findings"] == [{
            "finding_type": "VACUOUS_RECALL",
            "severity": "CRITICAL",
            "clause": "P6.1",
            "description": "critical_recall=1.0 pero details no declara critical_issues_count.",
        }]

    def test_no_duplica_lo_que_ya_escriben_los_revision(self):
        """La proyección lista blanca: `source_artifact`/`pain_id` viven en el informe del Bot."""
        projected = _report([_finding(0)]).to_dict()["findings"][0]

        assert set(projected) == {"finding_type", "severity", "clause", "description"}

    def test_descripcion_larga_se_acota(self):
        from modules.quality_gates.tribunal.outcome import ACTA_FINDING_TEXT_LIMIT

        finding = dict(_finding(0), description="x" * (ACTA_FINDING_TEXT_LIMIT + 500))
        projected = _report([finding]).to_dict()["findings"][0]

        assert len(projected["description"]) == ACTA_FINDING_TEXT_LIMIT + 1

    def test_tope_declarado_con_su_contador(self):
        from modules.quality_gates.tribunal.outcome import ACTA_FINDING_CAP

        findings = [_finding(i) for i in range(ACTA_FINDING_CAP + 3)]
        payload = _report(findings, critical=0).to_dict()

        assert len(payload["findings"]) == ACTA_FINDING_CAP
        assert payload["findings_omitted"] == 3

    def test_sin_tope_no_aparece_la_clave(self):
        assert "findings_omitted" not in _report([_finding(0)]).to_dict()

    def test_es_serializacion_no_decision(self):
        """Dos informes con los mismos campos decisorios deciden igual con o sin hallazgos.

        `to_dict` alimenta el acta, no al Juez: `verified_critical`/`verified_block`
        siguen leyendo `status`, `critical_count` y `recommendation`.
        """
        con_hallazgos = _report([_finding(0)])
        vacio = _report([], critical=1)

        for key in ("status", "critical_count", "recommendation"):
            assert con_hallazgos.to_dict()[key] == vacio.to_dict()[key]
        assert con_hallazgos.verified_critical is vacio.verified_critical is True
        assert con_hallazgos.verified_block is vacio.verified_block is True

    def test_hallazgo_no_mapeable_no_rompe_y_se_omite(self):
        payload = _report(["texto-suelto"], critical=0).to_dict()

        assert payload["findings"] == []
        assert payload["findings_count"] == 1


class TestActaPublicaLaCausa:
    """AC12 exigía el rojo: acta con `critical_count >= 1` y `findings` vacío."""

    def test_el_acta_serializada_conserva_el_hallazgo(self, tmp_path):
        from modules.quality_gates.tribunal.acta_writer import ActaWriter

        acta = {
            "verdict": "BLOQUEADO",
            "evidence_tier": "B",
            "hotel_id": "hotel-test",
            "timestamp": "2026-09-20T00:00:00Z",
            "clauses_evaluated": 6,
            "clauses": {},
            "reviewer_reports": [_report([_finding(0)]).to_dict()],
            "corrective_actions": [],
            "enforcement": {},
        }
        json_path, _md_path = ActaWriter(tmp_path).write(acta)
        written = json.loads(json_path.read_text(encoding="utf-8"))
        report = written["reviewer_reports"][0]

        assert report["critical_count"] == 1
        assert report["findings"][0]["finding_type"] == "VACUOUS_RECALL"


# --------------------------------------------------------------------------- #
# (iii) `package_evidence` en la rama publish
# --------------------------------------------------------------------------- #

def _make_zip(path: Path, members=3) -> str:
    with zipfile.ZipFile(path, "w") as zf:
        for i in range(members):
            zf.writestr(f"file{i}.txt", f"content{i}")
    return str(path)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


class TestPackageEvidenceEnRamaPublish:
    def test_del_paquete_entregado(self, tmp_path):
        from main import _record_published_package_evidence

        audit_dir = tmp_path / "v4_audit"
        audit_dir.mkdir()
        published = tmp_path / "hotel_20260920.zip"
        _make_zip(published, members=4)
        acta = {"verdict": "APROBADO-CONDICIONAL-PENDING-ONBOARDING"}

        _record_published_package_evidence(acta, published, audit_dir)

        evidence = acta["package_evidence"]
        assert evidence["suppressed"] is False, "la supresión conserva su propia marca"
        assert evidence["sha256"] == _sha256(published)
        assert evidence["member_count"] == 4
        assert Path(evidence["path"]) == published
        written = json.loads((audit_dir / "acta_revision.json").read_text(encoding="utf-8"))
        assert written["package_evidence"]["sha256"] == evidence["sha256"]
        assert written["package_evidence"]["suppressed"] is False

    def test_never_block_no_propaga_ni_con_acta_incompleta(self, tmp_path):
        from main import _record_published_package_evidence

        published = tmp_path / "hotel.zip"
        _make_zip(published)

        _record_published_package_evidence(None, published, tmp_path)
        _record_published_package_evidence({}, published, tmp_path / "no-existe")

    def test_paquete_inexistente_viaja_con_error_declarado(self, tmp_path):
        from main import _record_published_package_evidence

        acta = {}

        _record_published_package_evidence(acta, tmp_path / "no.zip", tmp_path)

        assert acta["package_evidence"]["sha256"] is None
        assert acta["package_evidence"]["error"]


class TestCableadoPublishPublicaEvidencia:
    """`run_v4_complete_mode` no es invocable sin corrida: se goberna por AST.

    Regla propia (L-V2.2), no prestada de otro gate: cada `packager.publish(`
    del flujo va seguida, en el MISMO bloque de sentencias, por la llamada que
    registra la evidencia. Un `publish` nuevo sin su evidencia —o borrar una de
    las dos llamadas— rompe aquí, no por re-numeración.
    """

    @staticmethod
    def _publish_sites(func):
        return [
            node for node in ast.walk(func)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "publish"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "packager"
        ]

    @pytest.fixture(scope="class")
    def flujo(self):
        tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
        func = next(
            (n for n in ast.walk(tree)
             if isinstance(n, ast.FunctionDef) and n.name == "run_v4_complete_mode"),
            None,
        )
        assert func is not None, "main.py ya no define run_v4_complete_mode()"
        parents = {}
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        return func, parents

    def test_son_dos_las_ramas_de_publicacion(self, flujo):
        func, _parents = flujo

        assert len(self._publish_sites(func)) == 2, (
            "el flujo v4complete cambió de ramas de publicación: AC20(iii) exige "
            "evidencia en TODAS, hay que extender la regla explícitamente"
        )

    def test_cada_publish_va_seguido_de_su_evidencia(self, flujo):
        func, parents = flujo
        sites = self._publish_sites(func)
        annotated = 0
        for site in sites:
            stmt = site
            while parents.get(stmt) is not func and not isinstance(
                stmt, (ast.Assign, ast.Expr)
            ):
                stmt = parents[stmt]
            block = parents.get(stmt)
            siblings = []
            for _field, value in ast.iter_fields(block):
                if isinstance(value, list) and any(node is stmt for node in value):
                    siblings = value
                    break
            after = siblings[siblings.index(stmt) + 1:]
            if any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "_record_published_package_evidence"
                for sibling in after
                for node in ast.walk(sibling)
            ):
                annotated += 1

        assert annotated == len(sites), (
            "hay un packager.publish() sin su _record_published_package_evidence: "
            "el ZIP entregado quedaría sin hash ni conteo (AC12/AC20-iii)"
        )
