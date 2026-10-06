"""FASE-D (REFACTOR-WHATSAPP-ENTREGA-2026-09-18): veredicto canónico y causa legible.

Gobierna AC4, AC8 y AC9 en la ruta del pre-gate de coherencia:

* AC8 — el pre-gate decide con `coherence_verdict_passes`, no con el score solo, y
  un check de severidad error sin resolver NO entra a la generación de assets.
* AC4 — los checks culpables viajan del reporte real al assessment y de alli al
  `gate_report_*.json` escrito por el writer, sin whitelist de nombres.
* AC9 — el lector nuevo del reporte persistido publica `read_status` (READ_OK
  incluido el vacio valido, ABSENT, READ_ERROR) y su causa.

Los arneses llaman a la funcion de produccion que gobierna la rama (no a una
re-implementacion del criterio dentro del test): L-T4A.5.
"""

import ast
import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from main import (
    _build_gate_report_payload,
    _coherence_pre_gate_decision,
    _persist_coherence_pre_gate,
    _run_asset_generation,
)
from modules.asset_generation.v4_asset_orchestrator import (
    CoherenceError,
    assert_pre_generation_coherence,
)
from modules.assessment_builder import AssessmentBuilder
from modules.commercial_documents.coherence_config import CoherenceConfig
from modules.commercial_documents.coherence_validator import (
    CoherenceCheck,
    CoherenceReport,
    failed_error_checks,
    mask_telephone_digits,
    read_coherence_report,
)
from modules.data_validation.whatsapp_contract import (
    READ_ABSENT,
    READ_ERROR,
    READ_OK,
)
from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    check_publication_readiness,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE_PRE_GATE = (
    PROJECT_ROOT
    / "output"
    / "TAREA7-2026-09-19"
    / "v4_complete"
    / "hotel_don_alfonso"
    / "v4_audit"
    / "coherence_validation.json"
)


def _check(name, *, passed=True, score=1.0, severity="info", message="ok"):
    return CoherenceCheck(
        name=name,
        passed=passed,
        score=score,
        message=message,
        severity=severity,
    )


def _report(*, score, is_coherent, checks):
    return CoherenceReport(
        is_coherent=is_coherent,
        overall_score=score,
        checks=list(checks),
    )


def _report_con_culpables(*, score=0.88, culpables=("whatsapp_verified", "assets_are_justified")):
    """Score por encima del umbral con veredicto False: el caso SalentoReal."""
    checks = [_check("problems_have_solutions", severity="warning", score=0.75)]
    checks += [
        _check(name, passed=False, score=0.0, severity="error",
               message=f"{name} sin resolver (confidence 0.30)")
        for name in culpables
    ]
    return _report(score=score, is_coherent=False, checks=checks)


class TestVeredictoCanonicoDelPreGate:
    """AC8: la decision del pre-gate sale del veredicto, no del score solo."""

    def test_veredicto_falso_con_score_alto_bloca_antes_de_generar(self):
        decision = _coherence_pre_gate_decision(
            report=_report_con_culpables(), threshold=0.8, is_blocking=False
        )
        assert decision["passed"] is False
        assert decision["status"] == "FAILED"
        assert decision["blocks_asset_generation"] is True
        assert decision["generate_proposal"] is False

    def test_score_alto_con_veredicto_falso_no_invoca_al_generador(self):
        """Spy sobre la entrada real a FASE 4: no se llama `generate_assets`."""
        orchestrator = MagicMock()
        result = _run_asset_generation(
            orchestrator=orchestrator,
            pre_gate_blocked=True,
            audit_result=MagicMock(),
            validation_summary={},
            diagnostic_doc=MagicMock(),
            proposal_doc=MagicMock(),
            hotel_name="Hotel",
            hotel_url="https://ejemplo.com",
        )
        assert result is None
        orchestrator.generate_assets.assert_not_called()

    def test_verde_complementario_si_entra_a_generacion(self):
        """Sin el verde de esta prueba, el guard de arriba podia saltar siempre."""
        orchestrator = MagicMock()
        orchestrator.generate_assets.return_value = MagicMock(
            generated_assets=[], failed_assets=[], coherence_report=MagicMock(overall_score=0.91)
        )
        report = _report(
            score=0.91,
            is_coherent=True,
            checks=[_check("whatsapp_verified", severity="info")],
        )
        decision = _coherence_pre_gate_decision(
            report=report, threshold=0.8, is_blocking=False
        )
        assert decision["blocks_asset_generation"] is False

        result = _run_asset_generation(
            orchestrator=orchestrator,
            pre_gate_blocked=decision["blocks_asset_generation"],
            audit_result=MagicMock(),
            validation_summary={},
            hotel_name="Hotel",
        )
        orchestrator.generate_assets.assert_called_once()
        assert result is orchestrator.generate_assets.return_value

    def test_culpable_fuera_del_vocabulario_whatsapp_tambien_bloquea(self):
        """No hay whitelist: un check nuevo con severidad error corta igual."""
        report = _report_con_culpables(culpables=("banda_de_un_check_que_no_exista_hoy",))
        decision = _coherence_pre_gate_decision(
            report=report, threshold=0.8, is_blocking=False
        )
        assert decision["guilty_check_names"] == ["banda_de_un_check_que_no_exista_hoy"]
        assert decision["blocks_asset_generation"] is True

    def test_veredicto_ausente_conserva_comportamiento_por_score(self):
        """None no es False: artefacto legacy con score bueno pasa (L-SR5)."""
        report = _report(
            score=0.9, is_coherent=None, checks=[_check("whatsapp_verified")]
        )
        decision = _coherence_pre_gate_decision(
            report=report, threshold=0.8, is_blocking=True
        )
        assert decision["passed"] is True
        assert decision["status"] == "PASSED"
        assert decision["blocks_asset_generation"] is False
        assert decision["generate_proposal"] is True

    def test_score_insuficiente_sin_errores_respeta_el_flag_documentado(self):
        """AC5: `overall_coherence` sigue con blocking=False; D no la sube."""
        report = _report(
            score=0.62,
            is_coherent=False,
            checks=[_check("price_matches_pain", passed=False, severity="warning", score=0.4)],
        )
        decision = _coherence_pre_gate_decision(
            report=report, threshold=0.8, is_blocking=CoherenceConfig().is_blocking(
                "overall_coherence"
            )
        )
        assert decision["passed"] is False
        assert decision["guilty_checks"] == []
        assert decision["blocks_asset_generation"] is False
        assert decision["generate_proposal"] is True

    def test_score_insuficiente_con_blocking_declara_solo_diagnostico(self):
        report = _report(score=0.42, is_coherent=False, checks=[])
        decision = _coherence_pre_gate_decision(
            report=report, threshold=0.8, is_blocking=True
        )
        assert decision["passed"] is False
        assert decision["generate_proposal"] is False

    def test_umbral_de_coherencia_intacto(self):
        """AC5: la barra 0.8 sigue siendo la del config; el decision la recibe."""
        assert CoherenceConfig().get_threshold("overall_coherence") == 0.8
        verde = _report(score=0.80, is_coherent=None, checks=[])
        rojo = _report(score=0.79, is_coherent=None, checks=[])
        assert _coherence_pre_gate_decision(
            report=verde, threshold=0.8, is_blocking=False
        )["passed"] is True
        assert _coherence_pre_gate_decision(
            report=rojo, threshold=0.8, is_blocking=False
        )["passed"] is False


class TestPersistenciaDelPreGate:
    """AC8: el reporte y sus culpables quedan en disco antes de decidir el resto."""

    def _escribir(self, tmp_path, report):
        decision = _coherence_pre_gate_decision(
            report=report, threshold=0.8, is_blocking=False
        )
        path = _persist_coherence_pre_gate(
            output_dir=tmp_path,
            hotel_id="hotelx",
            report=report,
            decision=decision,
            hotel_url="https://ejemplo.com",
        )
        return Path(path), json.loads(Path(path).read_text(encoding="utf-8"))

    def test_artefacto_conserva_los_dos_culpables_y_la_causa(self, tmp_path):
        path, payload = self._escribir(tmp_path, _report_con_culpables())
        assert path.parent.name == "v4_audit"
        assert payload["gate"]["status"] == "FAILED"
        assert payload["gate"]["blocks_asset_generation"] is True
        assert sorted(payload["failed_error_check_names"]) == [
            "assets_are_justified",
            "whatsapp_verified",
        ]
        culpables = {c["name"]: c["message"] for c in payload["failed_error_checks"]}
        assert "confidence 0.30" in culpables["whatsapp_verified"]

    def test_mensaje_con_numero_de_telefono_se_persiste_enmascarado(self, tmp_path):
        report = _report_con_culpables(culpables=("whatsapp_verified",))
        report.checks[1].message = "WhatsApp con confidence insuficiente (0.30) - destino +573001234567"
        _, payload = self._escribir(tmp_path, report)
        persistido = payload["failed_error_checks"][0]["message"]
        assert "+573001234567" not in persistido
        assert "573****" in persistido

    def test_veredicto_verde_persiste_lista_vacia_no_un_hueco(self, tmp_path):
        """Vacio valido ≠ fuente ausente (L-PF10): la clave existe y esta vacia."""
        report = _report(
            score=0.9, is_coherent=True, checks=[_check("whatsapp_verified")]
        )
        _, payload = self._escribir(tmp_path, report)
        assert payload["failed_error_check_names"] == []
        assert payload["failed_error_checks"] == []
        assert payload["gate"]["blocks_asset_generation"] is False


class TestTransporteDeCulpablesAlAssessment:
    """AC4: score, veredicto y causas salen del MISMO reporte correspondiente."""

    def test_post_gen_usa_su_reporte_no_un_pre_gate_obsoleto(self):
        pre = _report_con_culpables(culpables=("whatsapp_verified",))
        post = _report(
            score=0.93,
            is_coherent=True,
            checks=[_check("whatsapp_verified", severity="info")],
        )
        asset_result = MagicMock()
        asset_result.final_coherence_report = post
        asset_result.coherence_report = post

        payload = AssessmentBuilder().with_core("https://ejemplo.com", "Hotel X").with_coherence(pre, asset_result).build()
        assert payload["coherence_score"] == 0.93
        assert payload["is_coherent"] is True
        assert payload["coherence_failed_checks"] == []

    def test_fallback_sin_reporte_del_orquestador_usa_el_del_pre_gate(self):
        pre = _report_con_culpables()
        payload = AssessmentBuilder().with_core("https://ejemplo.com", "Hotel X").with_coherence(pre, None).build()
        assert payload["coherence_score"] == 0.88
        assert payload["is_coherent"] is False
        assert sorted(c["name"] for c in payload["coherence_failed_checks"]) == [
            "assets_are_justified",
            "whatsapp_verified",
        ]

    def test_sin_ningun_reporte_no_inventa_culpables_ni_veredicto(self):
        payload = AssessmentBuilder().with_core("https://ejemplo.com", "Hotel X").with_coherence(None, None).build()
        assert payload["coherence_score"] == 0.0
        assert payload["is_coherent"] is None
        assert payload["coherence_failed_checks"] is None

    def test_un_reporte_no_puede_dejar_verdict_y_causas_divorciadas(self):
        report = _report(
            score=0.88,
            is_coherent=False,
            checks=[_check("promised_assets_exist", passed=False, severity="error",
                           message="Assets no implementados: llms_txt")],
        )
        payload = AssessmentBuilder().with_core("https://ejemplo.com", "Hotel X").with_coherence(report, None).build()
        assert payload["is_coherent"] is False
        assert [c["name"] for c in payload["coherence_failed_checks"]] == [
            "promised_assets_exist"
        ]


class TestCulpablesEnElGateReport:
    """AC4: `gate_results[coherence].details.failed_check_names` y sus mensajes."""

    def _payload_del_writer(self, assessment):
        gate = PublicationGatesOrchestrator().gates["coherence"](assessment)
        readiness = check_publication_readiness(assessment, [gate])
        return json.loads(
            json.dumps(
                _build_gate_report_payload([gate], readiness, hotel_url="https://ejemplo.com"),
                ensure_ascii=False,
            )
        )

    def _assessment(self, report):
        return (
            AssessmentBuilder()
            .with_core("https://ejemplo.com", "Hotel X")
            .with_coherence(report, None)
            .build()
        )

    def test_dos_errores_conservan_ambos_nombres_en_el_json_real(self):
        assessment = self._assessment(_report_con_culpables())
        documento = self._payload_del_writer(assessment)
        coherence = [
            g for g in documento["gate_results"] if g["gate_name"] == "coherence"
        ][0]
        assert coherence["passed"] is False
        assert sorted(coherence["details"]["failed_check_names"]) == [
            "assets_are_justified",
            "whatsapp_verified",
        ]
        assert len(coherence["details"]["failed_check_messages"]) == 2

    def test_ninguna_whitelist_de_whatsapp_filtra_los_nombres(self):
        assessment = self._assessment(
            _report_con_culpables(culpables=("cobertura_de_geo", "whatsapp_verified"))
        )
        documento = self._payload_del_writer(assessment)
        names = [
            g["details"]["failed_check_names"]
            for g in documento["gate_results"]
            if g["gate_name"] == "coherence"
        ][0]
        assert "cobertura_de_geo" in names

    def test_el_mensaje_que_baja_al_gate_report_sale_saneado_desde_el_reporte(self):
        """AC8 con AC4: el numero no escapa por la serializacion nueva.

        El telefono se escribe crudo en el check del validador (que es como
        llega en produccion) y se sostiene que la unica boca de las causas,
        `failed_error_checks`, lo enmascara antes del assessment.
        """
        report = _report_con_culpables(culpables=("whatsapp_verified",))
        report.checks[1].message = "WhatsApp insuficiente (0.30) - destino +573001234567"
        documento = self._payload_del_writer(self._assessment(report))
        messages = [
            g["details"]["failed_check_messages"]
            for g in documento["gate_results"]
            if g["gate_name"] == "coherence"
        ][0]
        assert "+573001234567" not in messages[0]
        assert "573****" in messages[0]

    def test_gate_pasado_con_reporte_sano_publica_lista_vacia(self):
        assessment = self._assessment(
            _report(score=0.95, is_coherent=True, checks=[_check("whatsapp_verified")])
        )
        documento = self._payload_del_writer(assessment)
        details = [
            g["details"] for g in documento["gate_results"] if g["gate_name"] == "coherence"
        ][0]
        assert details["failed_check_names"] == []

    def test_assessment_legacy_sin_reporte_no_fabrica_lista_vacia(self):
        assessment = {"url": "u", "coherence_score": 0.9, "is_coherent": None}
        documento = self._payload_del_writer(assessment)
        details = [
            g["details"] for g in documento["gate_results"] if g["gate_name"] == "coherence"
        ][0]
        assert "failed_check_names" not in details


class TestEntradaDirectaDelOrquestador:
    """AC8: quien llame a `generate_assets` sin pre-gate obtiene el mismo corte."""

    def test_error_de_severidad_corta_aunque_el_score_compile(self):
        with pytest.raises(CoherenceError) as exc:
            assert_pre_generation_coherence(_report_con_culpables())
        assert "whatsapp_verified" in str(exc.value)

    def test_suelo_de_score_bajo_sigue_vigente(self):
        with pytest.raises(CoherenceError):
            assert_pre_generation_coherence(
                _report(score=0.4, is_coherent=False, checks=[])
            )

    def test_reporte_sano_no_corta(self):
        assert_pre_generation_coherence(
            _report(score=0.9, is_coherent=True, checks=[_check("whatsapp_verified")])
        )

    def test_generate_assets_llama_al_guard_antes_de_generar(self):
        """El cable, no la intencion: el guard domina a la primera generacion."""
        import modules.asset_generation.v4_asset_orchestrator as orq

        tree = ast.parse(Path(orq.__file__).read_text(encoding="utf-8"))
        cls = next(
            n for n in tree.body
            if isinstance(n, ast.ClassDef) and n.name == "V4AssetOrchestrator"
        )
        fn = next(
            n for n in cls.body
            if isinstance(n, ast.FunctionDef) and n.name == "generate_assets"
        )
        guard = None
        generacion = None
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                nombre = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if nombre == "assert_pre_generation_coherence" and guard is None:
                    guard = node.lineno
                if nombre == "_generate_with_coherence_check" and generacion is None:
                    generacion = node.lineno
        assert guard is not None, "generate_assets no llama al guard de coherencia"
        assert generacion is None or guard < generacion


class TestLectorDelReporteAC9:
    """AC9: READ_OK (incluido vacio), ABSENT y READ_ERROR con causa."""

    def test_lectura_ok_sobre_el_artefacto_de_baseline_real(self):
        if not BASELINE_PRE_GATE.exists():
            pytest.skip(
                f"baseline real ausente en {BASELINE_PRE_GATE} — AC9 sin certificar "
                "sobre esta ruta"
            )
        leido = read_coherence_report(BASELINE_PRE_GATE)
        assert leido["read_status"] == READ_OK
        assert leido["cause"] == ""
        assert isinstance(leido["report"].get("checks"), list)
        assert len(leido["report"]["checks"]) > 0

    def test_artefacto_inexistente_es_absent_con_causa(self, tmp_path):
        leido = read_coherence_report(tmp_path / "no-esta.json")
        assert leido["read_status"] == READ_ABSENT
        assert leido["report"] is None
        assert "no-esta.json" in leido["cause"]

    def test_json_roto_es_read_error_y_no_un_fallback_favorable(self, tmp_path):
        roto = tmp_path / "coherence_validation.json"
        roto.write_text("{ no es json", encoding="utf-8")
        leido = read_coherence_report(roto)
        assert leido["read_status"] == READ_ERROR
        assert leido["report"] is None
        assert leido["cause"]

    def test_lista_de_checks_vacia_sigue_siendo_lectura_ok(self, tmp_path):
        vacio = tmp_path / "vacio.json"
        vacio.write_text(
            json.dumps({"is_coherent": True, "overall_score": 0.9, "checks": []}),
            encoding="utf-8",
        )
        leido = read_coherence_report(vacio)
        assert leido["read_status"] == READ_OK
        assert leido["report"]["checks"] == []

    def test_raiz_que_no_es_objeto_es_read_error(self, tmp_path):
        raro = tmp_path / "lista.json"
        raro.write_text("[1, 2, 3]", encoding="utf-8")
        assert read_coherence_report(raro)["read_status"] == READ_ERROR


class TestCableDeLaRutaDeProduccion:
    """El pre-gate no puede volver a comparar el score a mano (mutante M1)."""

    def _fuente_del_modo(self):
        import inspect

        import main

        tree = ast.parse(inspect.getsource(main))
        fn = next(
            n for n in tree.body
            if isinstance(n, ast.FunctionDef) and n.name == "run_v4_complete_mode"
        )
        return fn

    def test_run_v4_complete_mode_decide_por_veredicto_canonico(self):
        fn = self._fuente_del_modo()
        llamadas = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Call):
                nombre = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                llamadas.add(nombre)
        assert "_coherence_pre_gate_decision" in llamadas
        assert "_persist_coherence_pre_gate" in llamadas
        assert "_run_asset_generation" in llamadas

    def test_el_pre_gate_ya_no_compara_el_score_contra_el_umbral(self):
        """La comparacion suelta era el defecto: restaurarla debe romper aqui.

        Se compara por AST, no por literal: el texto de la comparacion se forma
        con los mismos nombres que usan las banderas de la decision, y esa
        coincidencia no es el criterio.
        """
        fn = self._fuente_del_modo()
        variables_de_score = {"pre_coherence_score", "threshold"}
        for node in ast.walk(fn):
            if isinstance(node, ast.Compare) and len(node.ops) == 1:
                lados = {getattr(n, "id", None) for n in [node.left, *node.comparators]}
                if variables_de_score.issubset(lados):
                    pytest.fail(
                        f"run_v4_complete_mode vuelve a comparar el score contra el "
                        f"umbral en la linea {node.lineno}; la decision es de "
                        f"_coherence_pre_gate_decision"
                    )


class TestSaneadoDeCausas:
    def test_mask_telephone_digits_deja_los_numeros_legibles(self):
        assert "573****" in mask_telephone_digits("destino +573001234567 listo")
        assert mask_telephone_digits("confidence 0.30 - requiere >= 0.9") == (
            "confidence 0.30 - requiere >= 0.9"
        )

    def test_failed_error_checks_lee_el_reporte_sin_reconstruir_nombres(self):
        report = _report(
            score=0.88,
            is_coherent=False,
            checks=[
                _check("a_error", passed=False, severity="error", message="uno"),
                _check("warning_abierto", passed=False, severity="warning", message="dos"),
                _check("error_resuelto", passed=True, severity="error", message="tres"),
            ],
        )
        assert [c["name"] for c in failed_error_checks(report)] == ["a_error"]
