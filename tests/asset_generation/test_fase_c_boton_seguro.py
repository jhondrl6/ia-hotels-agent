"""FASE-C (REFACTOR-WHATSAPP-ENTREGA-2026-09-18) — número utilizable y botón seguro.

Dientes de AC3, AC5, AC6 y AC19a. Cada caso sigue la regla del plan: lo que se
certifica es la rama que el producto realmente recorre (L-T4A.5), y cada guarda
se demuestra con su oportunidad de perder.
"""

import dataclasses
import json
from datetime import datetime

import pytest

from modules.asset_generation.asset_catalog import ASSET_CATALOG
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.preflight_checks import NEW_HOTEL_THRESHOLDS
from modules.asset_generation.site_presence_adapter import (
    normalize_site_presence,
    save_site_presence_snapshot,
)
from modules.asset_generation.site_presence_checker import (
    PresenceCheckResult,
    PresenceStatus,
    SitePresenceChecker,
    SitePresenceReport,
)
from modules.commercial_documents.coherence_config import CoherenceConfig
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from modules.data_validation.whatsapp_contract import (
    EVIDENCE_NONE,
    EVIDENCE_PLUGIN_FINGERPRINT,
    EVIDENCE_WA_ME_HREF,
    WHATSAPP_HTML_PATTERNS,
    detect_whatsapp_in_html,
    rechazo_numero_whatsapp,
)
from modules.quality_gates.domain_gates import CommercialGate

URL = "https://hotel-ejemplo.test/"


def _campo(valor, confidence, can_use=True):
    """ValidatedField con la misma forma que construye `run_v4_complete_mode`."""
    from modules.commercial_documents.data_structures import ValidatedField

    return ValidatedField(
        field_name="whatsapp_number",
        value=valor,
        confidence=confidence,
        sources=["Web"],
        match_percentage=0.9,
        can_use_in_assets=can_use,
    )


def _confianza(nombre):
    from modules.data_validation.confidence_taxonomy import ConfidenceLevel

    return getattr(ConfidenceLevel, nombre)


class FakeResponse:
    def __init__(self, text):
        self.text = text


# ── AC6: forma del número en el límite de generación ─────────────────────────

class TestAC6FormaEnElLimite:

    @pytest.mark.parametrize("entrada,causa", [
        ("", "VACIO"),
        ("   ", "VACIO"),
        (None, "VACIO"),
        ("detected_via_html", "CENTINELA"),
        ("+573104019O49", "CARACTERES_NO_PERMITIDOS"),
        ("300１234567", "DIGITOS_NO_ASCII"),
        ("573104", "LONGITUD_INVALIDA"),
        ("5731040190491234567", "LONGITUD_INVALIDA"),
        (12345, "TIPO_NO_TEXTO"),
    ])
    def test_entradas_no_utilizables_con_causa_nombrada(self, entrada, causa):
        digitos, motivo = rechazo_numero_whatsapp(entrada)
        assert digitos is None
        assert motivo == causa

    @pytest.mark.parametrize("entrada,esperado", [
        ("+57 310 401 9049", "573104019049"),
        ("+57-310-401-9049", "573104019049"),
        ("(57) 310.401.9049", "573104019049"),
        ("573104019049", "573104019049"),
        ("  +49 30 1234567890  ", "49301234567890"),
    ])
    def test_formas_validas_se_igualan_sin_completar_partes(self, entrada, esperado):
        digitos, causa = rechazo_numero_whatsapp(entrada)
        assert causa is None
        # Ni se añade país, ni se quita el 57, ni se reordena: solo separadores fuera.
        assert digitos == esperado

    def test_el_recorte_a_siete_digitos_del_fixture_viejo_ya_no_es_posible(self):
        """El '+573****4567' histórico producía `wa.me/5734567` (7 dígitos fabricados)."""
        digitos, causa = rechazo_numero_whatsapp("+573****4567")
        assert digitos is None
        assert causa == "CARACTERES_NO_PERMITIDOS"

    def test_boton_forzado_con_centinela_no_produce_href(self, tmp_path):
        """Caso REAL del centinela: se construye con la misma forma que escribe main.py."""
        campo = _campo("detected_via_html", _confianza("ESTIMATED"), can_use=False)
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={"whatsapp_number": campo},
            hotel_name="Hotel Ejemplo",
            hotel_id="hotel_ejemplo",
        )
        assert result["success"] is False
        assert result["status"] == "blocked"
        assert result["reason_code"] == "whatsapp_number_no_utilizable"
        assert result["rejection"]["causa"] == "CAMPO_NO_UTILIZABLE"
        assert not list(tmp_path.rglob("*.html"))

    def test_marca_no_utilizable_bloquea_aunque_la_forma_sea_valida(self, tmp_path):
        """El flag `can_use_in_assets` tiene lector: no es decorativo.

        Un número de forma válida pero marcado no-utilizable (el camino del
        centinela con valor, o cualquier campo que el validador retire) no puede
        convertirse en href. Sin este test la marca de main.py caducaría en
        silencio: el guard de forma por sí solo no la mira.
        """
        campo = _campo("+57 310 401 9049", _confianza("ESTIMATED"), can_use=False)
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={"whatsapp_number": campo},
            hotel_name="Hotel Ejemplo",
            hotel_id="hotel_ejemplo",
        )
        assert result["status"] == "blocked"
        assert result["rejection"]["causa"] == "CAMPO_NO_UTILIZABLE"
        assert not list(tmp_path.rglob("*.html"))

    def test_el_orquestador_deja_de_escribir_phone_web_en_la_clave_del_boton(self):
        """Escritor real (AC6): `validated_data["whatsapp"]` es el campo validado.

        FIX-A2 escribía `phone_web` en esa clave y por eso ganaba por precedencia.
        Tras C la clave es un ALIAS del campo validado (no un número paralelo,
        L-NC6), así que el preflight sigue encontrando su `required_field`.
        """
        from unittest.mock import MagicMock

        from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator

        campo = _campo("+57 310 401 9049", _confianza("VERIFIED"))
        resumen = MagicMock()
        resumen.fields = [campo]
        audit = MagicMock()
        audit.validation.phone_web = "+57 601 555 0100"
        audit.validation.phone_gbp = "+57 601 555 0999"
        audit.schema = None
        audit.gbp = None
        audit.metadata = None
        audit.hotel_name = "Hotel Ejemplo"
        audit.url = URL

        orchestrador = V4AssetOrchestrator.__new__(V4AssetOrchestrator)
        datos = orchestrador._extract_validated_fields(resumen, audit_result=audit)

        assert datos["whatsapp"] is campo
        assert datos["whatsapp"] is datos["whatsapp_number"]
        assert datos["whatsapp"] != datos["phone_web"]

    def test_boton_con_numero_validado_escribe_el_destino_normalizado(self, tmp_path):
        """Lectura del HTML del writer real: el href es el número validado, no un derivado."""
        campo = _campo("+57 310 401 9049", _confianza("VERIFIED"))
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={"whatsapp_number": campo},
            hotel_name="Hotel Ejemplo",
            hotel_id="hotel_ejemplo",
        )
        assert result["success"] is True
        from pathlib import Path
        archivos = list(Path(str(tmp_path)).rglob("*.html"))
        assert archivos, "el writer debió dejar el HTML"
        texto = archivos[0].read_text(encoding="utf-8")
        assert "https://wa.me/573104019049?" in texto
        assert "wa.me/?text=" not in texto

    def test_phone_web_no_gana_por_precedencia(self, tmp_path):
        """AC6: `phone_web` (teléfono alternativo distinto) no puede ser el destino."""
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={
                "whatsapp": "+57 601 555 0100",       # clave legada: teléfono web suelto
                "phone_web": "+57 601 555 0100",
                "whatsapp_number": _campo("+57 310 401 9049", _confianza("VERIFIED")),
            },
            hotel_name="Hotel Ejemplo",
            hotel_id="hotel_ejemplo",
        )
        assert result["success"] is True
        from pathlib import Path
        texto = list(Path(str(tmp_path)).rglob("*.html"))[0].read_text(encoding="utf-8")
        assert "https://wa.me/573104019049?" in texto
        assert "576015550100" not in texto


# ── AC3: la presencia no neutraliza el bloqueo ───────────────────────────────

class TestAC3PresenciaNoPromociona:

    def _validator(self):
        return CoherenceValidator(config=CoherenceConfig())

    def _assets(self):
        return [dataclasses.make_dataclass("A", [("asset_type", str)])(asset_type="whatsapp_button")]

    def _presence_canonica(self, confidence=0.85):
        resultado = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=PresenceStatus.EXISTS,
            verified_at=datetime(2026, 10, 6),
            site_url=URL,
            confidence=confidence,
            details={"matched_texts": ["css_class:joinchat joinchat--btn"],
                     "presence_evidence_kind": EVIDENCE_PLUGIN_FINGERPRINT},
            read_status="OK",
            presence_evidence_kind=EVIDENCE_PLUGIN_FINGERPRINT,
            observation_scope={"routes_inspected": [URL], "crawl": False, "nivel": "raiz"},
        )
        reporte = SitePresenceReport(
            site_url=URL,
            checked_at=datetime(2026, 10, 6),
            results={"whatsapp_button": resultado},
        )
        return normalize_site_presence(reporte)

    @pytest.mark.parametrize("nombre_confianza", ["CONFLICT", "UNKNOWN", "ESTIMATED"])
    def test_boton_forzado_bloquea_con_y_sin_presencia(self, nombre_confianza):
        for con_presencia in (False, True):
            informe = self._presence_canonica() if con_presencia else None
            check = self._validator()._check_whatsapp_verified(
                assets=self._assets(),
                validation_summary=_Summary(_campo("+57 310 401 9049", _confianza(nombre_confianza))),
                whatsapp_html_detected=False,
                site_presence_report=informe,
            )
            assert check.passed is False, (
                f"{nombre_confianza} con presencia={con_presencia} no debe pasar"
            )
            assert check.score < 0.9

    def test_numero_verified_si_pasa(self):
        check = self._validator()._check_whatsapp_verified(
            assets=self._assets(),
            validation_summary=_Summary(_campo("+57 310 401 9049", _confianza("VERIFIED"))),
            whatsapp_html_detected=False,
            site_presence_report=None,
        )
        assert check.passed is True
        assert check.score >= 0.9

    def test_umbral_y_blocking_intactos(self):
        """No se bajó 0.9/0.8 ni se cambió blocking=True (restricción de C)."""
        config = CoherenceConfig()
        assert config.get_threshold("whatsapp_verified") == 0.9
        assert config.is_blocking("whatsapp_verified") is True

    def test_rojo_invertido_don_alfonso_huella_no_es_numero(self):
        """El caso medido: huella de plugin con `exists` 0.85 no llega a la barra.

        Si alguien restaura el boost indiscriminado, o promociona la huella a
        confianza ≥0.9 con un botón, ESTE test se rompe.
        """
        informe = self._presence_canonica(confidence=0.85)
        assert informe["whatsapp_button"]["presence_evidence_kind"] == EVIDENCE_PLUGIN_FINGERPRINT
        assert informe["whatsapp_button"]["confidence"] == 0.85
        assert informe["whatsapp_button"]["confidence"] < 0.9
        check = self._validator()._check_whatsapp_verified(
            assets=self._assets(),
            validation_summary=_Summary(_campo("detected_via_html", _confianza("ESTIMATED"), can_use=False)),
            whatsapp_html_detected=True,
            site_presence_report=informe,
        )
        assert check.passed is False


class _Summary:
    """ValidationSummary mínimo: solo lee get_field."""

    def __init__(self, campo):
        self._campo = campo

    def get_field(self, nombre):
        return self._campo if nombre == "whatsapp_number" else None


# ── AC6 producibilidad: el caso entra por la ruta que sí planifica ───────────

class TestAC6ProducibilidadDesdeLaRutaViva:

    def test_el_boton_se_planifica_por_whatsapp_conflict(self):
        """Tras B la única vía que planifica el botón es `whatsapp_conflict`."""
        mapper = PainSolutionMapper()
        assets = mapper.get_assets_for_pain(
            "whatsapp_conflict",
            {"whatsapp_number": 0.9, "phone_web": 0.9, "whatsapp": 0.9},
        )
        assert "whatsapp_button" in [a.asset_type for a in assets]

    def test_ese_boton_planificado_con_centinela_resulta_bloqueado(self, tmp_path):
        """Misma entrada producible + campo centinela → error, no un archivo vacío.

        Si el caso dejara de ser producible por esta ruta, el test fallaría aquí
        y no en el aserción del guard (L-T4A.5).
        """
        mapper = PainSolutionMapper()
        planificados = mapper.get_assets_for_pain(
            "whatsapp_conflict", {"whatsapp_number": 0.9, "phone_web": 0.9}
        )
        assert "whatsapp_button" in [a.asset_type for a in planificados]
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={"whatsapp_number": _campo("detected_via_html", _confianza("CONFLICT"), can_use=False)},
            hotel_name="Hotel Ejemplo",
            hotel_id="hotel_ejemplo",
        )
        assert result["status"] == "blocked"
        assert result["rejection"]["causa"] == "CAMPO_NO_UTILIZABLE"


# ── AC5: cinco barras midiendo el mismo hecho ────────────────────────────────

def _barra(entrada):
    return entrada["confidence_required"] if isinstance(entrada, dict) else entrada.confidence_required


class TestAC5BarrasInvariantes:

    def test_cada_barra_con_su_valor_y_su_dueno(self):
        mapper = PainSolutionMapper()
        assert _barra(mapper.pain_map["no_whatsapp_visible"]) == 0.9
        assert _barra(mapper.pain_map["whatsapp_conflict"]) == 0.5
        catalogo = ASSET_CATALOG["whatsapp_button"]
        assert catalogo.required_confidence == 0.7
        assert catalogo.block_on_failure is False
        assert NEW_HOTEL_THRESHOLDS["whatsapp_button"] == 0.3
        assert CommercialGate(config={}).whatsapp_confidence_threshold == 0.9
        assert CoherenceConfig().get_threshold("whatsapp_verified") == 0.9

    def test_la_barra_baja_de_un_hotel_nuevo_no_autoriza_un_destino_inventado(self, tmp_path):
        """El rojo medido de AC5: 0.3 planifica el botón, y aun así el destino se exige.

        Preflight no bloquea (block_on_failure=False, intacto); el límite de
        generación sí impide el href. Bajar la barra del catálogo no convertiría
        un número inutilizable en número.
        """
        checker = ConditionalGenerator(output_dir=str(tmp_path))
        result = checker.generate(
            asset_type="whatsapp_button",
            validated_data={"whatsapp_number": _campo("", _confianza("ESTIMATED"))},
            hotel_name="Hotel Nuevo",
            hotel_id="hotel_nuevo",
        )
        assert result["status"] == "blocked"
        assert result["rejection"]["causa"] == "VACIO"


# ── AC19a: observación aditiva, sin redefinir estados ────────────────────────

class TestAC19aObservacionAditiva:

    def _con_html(self, monkeypatch, html=None, excepcion=None):
        import requests

        def fake_get(*args, **kwargs):
            if excepcion is not None:
                raise excepcion
            return FakeResponse(html)

        monkeypatch.setattr(requests, "get", fake_get)
        checker = SitePresenceChecker()
        return checker, checker._check_asset_presence(
            "whatsapp_button", URL, {"schemas_encontrados": [{"type": "Hotel", "data": {}}]}
        )

    def test_huella_de_plugin_declara_presencia_sin_numero(self, monkeypatch):
        html = '<div class="joinchat joinchat--left joinchat--btn">...</div>'
        checker, resultado = self._con_html(monkeypatch, html=html)
        assert resultado.status == PresenceStatus.EXISTS
        assert resultado.confidence == 0.85
        assert resultado.presence_evidence_kind == EVIDENCE_PLUGIN_FINGERPRINT
        assert resultado.read_status == "OK"
        assert "whatsapp_href_number" not in resultado.details
        assert resultado.observation_scope["nivel"] == "raiz"

    def test_href_de_wa_me_declara_el_tipo_de_evidencia(self, monkeypatch):
        html = '<a href="https://wa.me/573104019049?text=hola">WhatsApp</a>'
        checker, resultado = self._con_html(monkeypatch, html=html)
        assert resultado.presence_evidence_kind == EVIDENCE_WA_ME_HREF
        assert resultado.details["whatsapp_href_number"] == "573104019049"

    def test_canal_en_pagina_interna_se_declara_como_no_inspeccionada(self, monkeypatch):
        """Solo se lee la raíz: la ausencia observada NUNCA es 'no tiene WhatsApp'."""
        checker, resultado = self._con_html(monkeypatch, html="<p>Contacto</p>")
        assert resultado.status == PresenceStatus.NOT_EXISTS
        assert resultado.presence_evidence_kind == EVIDENCE_NONE
        assert resultado.read_status == "OK"
        assert resultado.observation_scope == {
            "routes_inspected": [URL], "crawl": False, "nivel": "raiz",
        }
        assert resultado.observation_scope["crawl"] is False

    def test_excepcion_de_transporte_es_read_error_no_ausencia(self, monkeypatch):
        checker, resultado = self._con_html(
            monkeypatch, excepcion=ConnectionError("sitio no accesible")
        )
        assert resultado.read_status == "READ_ERROR"
        assert resultado.status == PresenceStatus.VERIFICATION_FAILED
        assert resultado.status != PresenceStatus.NOT_EXISTS

    def test_claves_nuevas_sin_redefinir_las_viejas(self, monkeypatch):
        html = '<a href="https://wa.me/573104019049">WhatsApp</a>'
        checker, resultado = self._con_html(monkeypatch, html=html)
        reporte = SitePresenceReport(
            site_url=URL, checked_at=datetime(2026, 10, 6),
            results={"whatsapp_button": resultado},
        )
        canonico = normalize_site_presence(reporte)
        entrada = canonico["results"]["whatsapp_button"]
        assert entrada["status"] == "exists"
        assert entrada["site_verified"] is True
        assert entrada["confidence"] == 0.85
        for clave in ("observation_scope", "read_status", "presence_evidence_kind", "details"):
            assert clave in entrada, f"{clave} debía publicarse sin tocar las claves viejas"

    def test_reporte_sin_observacion_conserva_la_forma_exacta(self):
        """Aditivo por construcción: sin observación no hay claves nuevas.

        Es el control que mantiene verdes los cuatro asserts de igualdad exacta
        del plan: la forma canónica de un resultado sin observación sigue siendo
        exactamente `status/site_verified/confidence`.
        """
        resultado = PresenceCheckResult(
            asset_type="whatsapp_button", status=PresenceStatus.NOT_EXISTS,
            verified_at=datetime(2026, 10, 6), site_url=URL, confidence=0.7,
        )
        reporte = SitePresenceReport(
            site_url=URL, checked_at=datetime(2026, 10, 6),
            results={"whatsapp_button": resultado},
        )
        canonico = normalize_site_presence(reporte)["results"]["whatsapp_button"]
        assert canonico["status"] == "not_exists"
        assert set(canonico.keys()) == {"status", "site_verified", "confidence"}

    def test_las_claves_sobreviven_al_writer_del_snapshot(self, tmp_path, monkeypatch):
        html = '<div class="joinchat"></div>'
        checker, resultado = self._con_html(monkeypatch, html=html)
        reporte = SitePresenceReport(
            site_url=URL, checked_at=datetime(2026, 10, 6),
            results={"whatsapp_button": resultado},
        )
        ruta = tmp_path / "site_presence_snapshot.json"
        save_site_presence_snapshot(normalize_site_presence(reporte), ruta)
        leido = json.loads(ruta.read_text(encoding="utf-8"))["snapshot"]
        assert leido["whatsapp_button"]["presence_evidence_kind"] == EVIDENCE_PLUGIN_FINGERPRINT
        assert leido["whatsapp_button"]["observation_scope"]["crawl"] is False
        assert "whatsapp_href_number" not in leido["whatsapp_button"]["details"]


# ── Prerrequisito de AC19a: los dos lectores, designados y con un vocabulario ─

class TestDosLectoresDesignados:

    def test_el_lector_de_dolor_conserva_el_vocabulario_al_delegarlo(self):
        """Caracterización de la unificación: los patrones NO cambiaron.

        La lista histórica del auditor se copia-identica en el módulo compartido;
        si la delegación perdiera un patrón, el auditor dejaría de ver ese
        canal y ESTE test se rompe.
        """
        historicos = (
            r"wa\.me/", r"api\.whatsapp\.com", r"web\.whatsapp\.com",
            r"whatsapp://", r"whatsapp\.com/send",
            r'class="[^"]*whatsapp[^"]*"', r'id="[^"]*whatsapp[^"]*"',
            r"joinchat", r"creame-whatsapp-me", r"ht-ctc", r"click-to-chat",
            r"wa-chat", r"data-settings.*telephone",
        )
        assert tuple(WHATSAPP_HTML_PATTERNS) == historicos

        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor

        auditor = V4ComprehensiveAuditor.__new__(V4ComprehensiveAuditor)
        muestras = [
            '<a href="https://wa.me/573104019049">x</a>',
            '<a href="https://api.whatsapp.com/send?phone=573104019049">x</a>',
            '<script src="wp-content/plugins/joinchat/js/main.js"></script>',
            '<span class="wa-chat-btn">hola</span>',
        ]
        for muestra in muestras:
            assert auditor._detect_whatsapp_from_html(muestra) is True, muestra
        assert auditor._detect_whatsapp_from_html("<p>reservas por teléfono</p>") is False
        assert auditor._detect_whatsapp_from_html("") is False

    def test_ambos_lectores_dependen_del_mismo_modulo(self):
        import inspect

        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor
        from modules.asset_generation import site_presence_checker as spc

        dolor = inspect.getsource(V4ComprehensiveAuditor._detect_whatsapp_from_html)
        presencia = inspect.getsource(spc.SitePresenceChecker._check_html_element)
        assert "whatsapp_contract" in dolor, "el lector de dolor debe delegar el vocabulario"
        assert "whatsapp_contract" in presencia or "WA_HREF_TOKENS" in presencia
