"""FASE-F (AC13) — sumidero unico de redaccion y sus consumidores reales.

NR7/L-VUP-5: cada deteccion tiene su rojo. Los sanitizadores preexistentes
(`LLMMentionChecker`, `HttpClient`, `SSLLogger`) se **califican** aqui: se les
exige el mismo marcador en el mismo canal, y los mutantes de F caen estas
aserciones. No se reemplazan.

L-T4A.5: las pruebas recorren consola, archivo y excepciones reales, no solo
helpers aislados. El marcador tiene que desaparecer de lo que escribe el writer.

Los marcadores son sinteticos y no satisfacen ninguna credencial real. Tienen
forma valida a la vez para el sumidero (producto) y para los patrones de
`ValidationRunner._check_no_secrets` (verificador), que son instrumentos
independientes por disenio: la bateria comprueba que los dos cazan el mismo
marcador.
"""

import importlib.util
import json
import logging
import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests as real_requests

from main import _persist_coherence_pre_gate
from modules.auditors.llm_mention_checker import LLMMentionChecker
from modules.data_validation.external_apis.pagespeed_client import PageSpeedClient
from modules.scrapers.google_places_client import GooglePlacesClient
from modules.utils import redaction as sink
from modules.utils.http_client import HttpClient
from modules.utils.ssl_logger import SSLLogger

ROOT = Path(__file__).resolve().parents[2]

_spec = importlib.util.spec_from_file_location(
    "run_all_validations", ROOT / "scripts" / "run_all_validations.py"
)
rav = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rav)

# Los marcadores se construyen por concatenacion: ningun literal del archivo casa
# con los patrones del verificador (que escanea archivos versionados y contenido
# staged), pero el valor EN MEMORIA si tiene la forma, y ahi es donde se prueba la
# redaccion. Es el mismo recurso de tests/test_p5_ac_s2_remediacion.py:33.
_CUERPO_GOOGLE = "SINTETICO-FASE-F-marca-no-es-credencial-000000"
_CUERPO_OPENROUTER = "v1-sinteticofasefmarcanoesunaclave00000000"
_CUERPO_ANTHROPIC = "sinteticofasefmarcanoesunaclave000000"
_CUERPO_PERPLEXITY = "sinteticofasefmarcanoesunaclave0000"
_CUERPO_GITHUB = "sinteticofasefmarcanoesunaclave0000"

SYNTH_GOOGLE = "AIzaSy" + _CUERPO_GOOGLE
SYNTH_OPENROUTER = "sk-or-" + _CUERPO_OPENROUTER
SYNTH_ANTHROPIC = "sk-ant-" + _CUERPO_ANTHROPIC
SYNTH_PERPLEXITY = "pplx-" + _CUERPO_PERPLEXITY
SYNTH_GITHUB = "ghp_" + _CUERPO_GITHUB

TODAS = (
    SYNTH_GOOGLE,
    SYNTH_OPENROUTER,
    SYNTH_ANTHROPIC,
    SYNTH_PERPLEXITY,
    SYNTH_GITHUB,
)

_GIT_ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "fase-f",
    "GIT_AUTHOR_EMAIL": "fase-f@local",
    "GIT_COMMITTER_NAME": "fase-f",
    "GIT_COMMITTER_EMAIL": "fase-f@local",
    "GPGPROGRAM": "",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args], cwd=repo, env=_GIT_ENV, check=True,
        capture_output=True, text=True,
    )


def _last_result(runner) -> object:
    result = runner.results[-1]
    assert result.name == "Secrets Check", f"el check no corrrio: {result.name}"
    return result


# --------------------------------------------------------------------------
# TAREA 2 — el sumidero: lo que redacta y lo que NO debe tocar
# --------------------------------------------------------------------------


class TestSumideroUnico:
    """`redact_secrets` es la unica definicion de forma de credencial."""

    def test_texto_inocuo_se_preserva_identico(self):
        texto = "PageSpeed quota exceeded for https://hotel.example/faq?format=json"
        assert sink.redact_secrets(texto) == texto

    @pytest.mark.parametrize(
        "marcador",
        TODAS,
        ids=["forma-google", "forma-openrouter", "forma-anthropic", "forma-perplexity", "forma-github"],
    )
    def test_cada_forma_de_credencial_se_redacta(self, marcador):
        resultado = sink.redact_secrets(f"fallo al llamar al proveedor: {marcador}")
        assert marcador not in resultado
        assert sink.MASK in resultado

    def test_param_key_con_interrogacion_se_redacta(self):
        url = f"https://api.example/v1?key={SYNTH_GOOGLE}&format=json"
        resultado = sink.redact_secrets(url)
        assert SYNTH_GOOGLE not in resultado
        assert "key=***" in resultado
        assert "format=json" in resultado

    def test_param_key_sin_prefijo_de_url_se_redacta(self):
        # El regex original pedia [?&]: "key=<valor>" suelto en un mensaje de error
        # de un SDK sobrevivia intacto.
        resultado = sink.redact_secrets(f"credencial enviada key=abcdef0123456789 fin")
        assert "abcdef0123456789" not in resultado
        assert "key=***" in resultado

    def test_cabecera_x_goog_api_key_se_redacta(self):
        resultado = sink.redact_secrets(
            f"x-goog-api-key: {SYNTH_GOOGLE}",
        )
        assert SYNTH_GOOGLE not in resultado

    def test_cabecera_authorization_bearer_se_redacta(self):
        resultado = sink.redact_secrets(f"Authorization: Bearer {SYNTH_OPENROUTER}")
        assert SYNTH_OPENROUTER not in resultado

    def test_bearer_separado_de_la_forma_sk_tambien_se_redacta(self):
        resultado = sink.redact_secrets("Authorization: Bearer tokensinteticofasef1234567")
        assert "tokensinteticofasef1234567" not in resultado

    def test_sufijo_de_palabra_no_se_toca(self):
        # La word boundary es un diente, no decoracion: sin ella "monkey=" hacia
        # rojo un log inocuo y el sanitizador se desactivaba por ruido.
        for inocuo in ("monkey=3", "donkey=4", "turkey=5"):
            assert sink.redact_secrets(inocuo) == inocuo

    def test_cadena_vacia_es_noop(self):
        assert sink.redact_secrets("") == ""

    def test_contains_secret_shape_distingue_los_dos_estados(self):
        assert sink.contains_secret_shape(f"key={SYNTH_GOOGLE}")
        assert not sink.contains_secret_shape("Connection refused")
        assert not sink.contains_secret_shape("")

    def test_guard_de_informe_pasa_con_texto_redactado(self):
        sink.assert_redacted(sink.redact_secrets(f"error {SYNTH_GOOGLE}"), channel="test")

    def test_guard_de_informe_falla_y_no_repite_el_valor(self):
        with pytest.raises(sink.RedactionLeakError) as excinfo:
            sink.assert_redacted(f"valor crudo {SYNTH_GOOGLE}", channel="sanitization_report")
        assert SYNTH_GOOGLE not in str(excinfo.value)
        assert "sanitization_report" in str(excinfo.value)

    def test_el_guard_no_marca_un_texto_ya_redactado(self):
        # `key=***` es justo lo que produce redact_secrets. Si el guard lo lee como
        # leak, quien redacta y despues verifica no puede verificar: el seam de H
        # (captura del runner) se cierra sobre si mismo.
        redactado = sink.redact_secrets(f"en la URL ?key={SYNTH_GOOGLE} y ademas {SYNTH_PERPLEXITY}")
        assert "key=***" in redactado
        assert not sink.contains_secret_shape(redactado)
        sink.assert_redacted(redactado, channel="sanitization_report")

    def test_el_guard_sigue_marcando_el_valor_crudo_tras_ese_arreglo(self):
        assert sink.contains_secret_shape(f"en la URL ?key={SYNTH_GITHUB}")

    def test_redact_and_clip_redacta_antes_de_recortar(self):
        # El orden inverso corta el marcador y deja el prefijo por delante: esta
        # es exactamente la ruta de HttpClient, que recortaba a 100 caracteres.
        largo = "x" * 60 + f" key={SYNTH_GOOGLE}" + "y" * 40
        assert "AIzaSy" in largo[:97], (
            "el recorte a ciegas tenia que estar dejando el prefijo de la key"
        )
        resultado = sink.redact_and_clip(largo, 100)
        assert "AIzaSy" not in resultado
        assert len(resultado) <= 100

    def test_redact_and_clip_deja_los_mensajes_cortos_igual(self):
        assert sink.redact_and_clip("SSL handshake failed", 100) == "SSL handshake failed"

    def test_redact_payload_es_recurisivo_y_conserva_la_forma(self):
        payload = {
            "checks": [
                {"name": "whatsapp_consistency", "message": f"ver {SYNTH_GOOGLE}", "score": 0.4},
            ],
            "errors": [f"otro {SYNTH_PERPLEXITY}"],
            "ok": True,
            "umbral": 0.8,
            "ausente": None,
            "par": ("clave", f"valor {SYNTH_ANTHROPIC}"),
        }
        resultado = sink.redact_payload(payload)
        serializado = json.dumps(resultado, ensure_ascii=False)
        assert SYNTH_GOOGLE not in serializado
        assert SYNTH_PERPLEXITY not in serializado
        assert SYNTH_ANTHROPIC not in serializado
        assert resultado["checks"][0]["name"] == "whatsapp_consistency"
        assert resultado["checks"][0]["score"] == 0.4
        assert resultado["ok"] is True
        assert resultado["umbral"] == 0.8
        assert resultado["ausente"] is None
        assert isinstance(resultado["par"], tuple)


# --------------------------------------------------------------------------
# TAREA 2 — calificacion de los sanitizadores que ya existian (L-VUP-5)
# --------------------------------------------------------------------------


class TestCalificacionSanitizadoresExistentes:
    """Se reutiliza lo de FASE-P5 AC-S1; solo se cierra lo que dejaba pasar."""

    def test_sanitize_text_sigue_redactando_su_propia_key(self):
        checker = LLMMentionChecker(gemini_key=SYNTH_GOOGLE)
        assert SYNTH_GOOGLE not in checker._sanitize_text(f"msg {SYNTH_GOOGLE} fin")

    def test_sanitize_text_redacta_una_forma_ajena_sin_keys_cargadas(self):
        # Antes: con ninguna key cargada, _sanitize_text era noop y una key de OTRO
        # provider (registry, config, otro auditor) salia cruda al log.
        checker = LLMMentionChecker()
        resultado = checker._sanitize_text(f"filtrada {SYNTH_OPENROUTER}")
        assert SYNTH_OPENROUTER not in resultado

    def test_sanitize_error_redacta_formas_y_params(self):
        error = Exception(
            f"403 Forbidden: https://generativelanguage.googleapis.com/v1beta/"
            f"models/x:generateContent?key={SYNTH_GOOGLE} raw={SYNTH_ANTHROPIC}"
        )
        resultado = LLMMentionChecker._sanitize_error(error)
        assert SYNTH_GOOGLE not in resultado
        assert SYNTH_ANTHROPIC not in resultado

    def test_query_gemini_no_filtra_una_key_que_no_es_suya(self, caplog):
        # La defensa anterior solo conocia las 3 keys de la instancia. Aqui el
        # texto del proveedor trae la key de OTRO proyecto.
        http_error = real_requests.HTTPError(
            f"403 Forbidden: Key {SYNTH_GITHUB} esta dada de alta en otro proyecto"
        )
        response = MagicMock()
        response.status_code = 403
        response.raise_for_status.side_effect = http_error
        http_error.response = response

        checker = LLMMentionChecker(gemini_key=SYNTH_GOOGLE)
        with caplog.at_level(logging.WARNING, logger="modules.auditors.llm_mention_checker"):
            with patch("requests.post", return_value=response):
                assert checker._query_gemini("proba") is None

        assert caplog.records, "el 403 no registro nada: el rojo no ejercito la rama"
        for record in caplog.records:
            assert SYNTH_GITHUB not in record.getMessage()
            assert SYNTH_GOOGLE not in record.getMessage()

    def test_ruta_todos_los_modelos_fallaron_tambien_sanea(self, caplog):
        # El rojo tiene que morder la rama final (:448), no solo los except cortos.
        http_error = real_requests.HTTPError(
            f"404 Not Found: https://generativelanguage.googleapis.com/x?key={SYNTH_GOOGLE}"
        )
        response = MagicMock()
        response.status_code = 404
        response.raise_for_status.side_effect = http_error
        http_error.response = response

        checker = LLMMentionChecker(gemini_key=SYNTH_GOOGLE)
        with caplog.at_level(logging.WARNING, logger="modules.auditors.llm_mention_checker"):
            with patch("requests.post", return_value=response):
                assert checker._query_gemini("proba") is None

        assert caplog.records, "la rama de agotamiento no registro nada"
        for record in caplog.records:
            assert SYNTH_GOOGLE not in record.getMessage()


# --------------------------------------------------------------------------
# TAREA 3 — consola
# --------------------------------------------------------------------------


class TestConsolaSinMarcadores:
    """La redaccion ocurre antes de `print`, no despues."""

    def test_log_ssl_bypass_imprime_redactado(self, capsys):
        client = HttpClient()
        client._logger = MagicMock()  # sin handler de disco: esta prueba mide consola
        client._log_ssl_bypass(
            "https://hotel.example", f"SSL error en https://api.example?key={SYNTH_GOOGLE}"
        )
        salida = capsys.readouterr().out
        assert SYNTH_GOOGLE not in salida
        assert "SSL bypass activado" in salida

    def test_log_ssl_bypass_entrega_al_logger_el_texto_redactado(self):
        client = HttpClient()
        spy = MagicMock()
        client._logger = spy
        client._log_ssl_bypass("https://hotel.example", f"boom key={SYNTH_PERPLEXITY}")
        url, entregado = spy.log_ssl_bypass.call_args[0]
        assert SYNTH_PERPLEXITY not in entregado
        assert url == "https://hotel.example"

    def test_sanitize_error_de_http_client_redacta_y_mantiene_el_limite(self):
        client = HttpClient()
        error = Exception("x" * 60 + f" key={SYNTH_GOOGLE}")
        resultado = client._sanitize_error(error)
        assert "AIzaSy" not in resultado
        assert len(resultado) <= 100

    def test_el_error_del_fallback_sale_redactado(self):
        client = HttpClient()
        client.ssl_fallback_enabled = False
        client.allow_http_downgrade = False
        with patch.object(
            client, "_try_request",
            return_value=(None, Exception(f"connection refused key={SYNTH_GOOGLE}")),
        ):
            response, info = client.get("https://hotel.example")
        assert response is None
        assert SYNTH_GOOGLE not in json.dumps(info, default=str)


# --------------------------------------------------------------------------
# TAREA 3 — archivo bajo logs/: la ruta que el verificador no veia
# --------------------------------------------------------------------------


class TestEscrituraBajoLogs:
    """`logs/` esta en .gitignore: lo que ahi se escribe nunca paso por un check."""

    def test_ssl_logger_escribe_el_archivo_sin_el_marcador(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        logger = SSLLogger()
        try:
            logger.log_ssl_bypass(
                "https://hotel.example",
                f"certificate verify failed para https://api.example?key={SYNTH_GOOGLE}",
            )
        finally:
            logging.getLogger("ssl_fallback").handlers.clear()

        escrito = (tmp_path / "logs" / "ssl_fallback.log").read_bytes().decode("utf-8")
        assert "SSL_BYPASS" in escrito
        assert SYNTH_GOOGLE not in escrito
        assert "hotel.example" in escrito  # el detalle diagnostico se conserva

    def test_ssl_logger_con_texto_inocuo_conserva_el_detalle(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        logger = SSLLogger()
        try:
            logger.log_ssl_bypass("https://hotel.example", "certificate has expired")
        finally:
            logging.getLogger("ssl_fallback").handlers.clear()

        escrito = (tmp_path / "logs" / "ssl_fallback.log").read_text(encoding="utf-8")
        assert "certificate has expired" in escrito


# --------------------------------------------------------------------------
# TAREA 3 — el artefacto nuevo de D bajo output/
# --------------------------------------------------------------------------


class _ReporteFalso:
    """Sustituye CoherenceReport: el writer solo usa to_dict()."""

    def __init__(self, message: str):
        self._message = message

    def to_dict(self) -> dict:
        return {
            "is_valid": False,
            "coherence_score": 0.4,
            "checks": [{"name": "whatsapp_consistency", "message": self._message, "severity": "error"}],
            "errors": [self._message],
            "warnings": [],
        }


def _decision() -> dict:
    return {
        "threshold": 0.8,
        "passed": False,
        "status": "BLOQUEADO",
        "blocks_asset_generation": True,
        "guilty_checks": [
            {"name": "whatsapp_consistency", "message": "crudo", "score": 0.4},
        ],
    }


class TestEscrituraBajoOutput:
    """AC13 exige el rojo tambien en un archivo escrito bajo output/."""

    def test_pre_gate_persiste_el_mensaje_redactado(self, tmp_path):
        message = f"WhatsApp no verificado, token {SYNTH_GOOGLE} en la URL"
        path = _persist_coherence_pre_gate(
            output_dir=tmp_path,
            hotel_id="hotel-sintetico",
            report=_ReporteFalso(message),
            decision=_decision(),
            hotel_url="https://hotel.example",
        )
        crudo = Path(path).read_bytes().decode("utf-8")
        assert SYNTH_GOOGLE not in crudo
        assert "whatsapp_consistency" in crudo

    def test_pre_gate_conserva_los_campos_del_contrato_de_d(self, tmp_path):
        path = _persist_coherence_pre_gate(
            output_dir=tmp_path,
            hotel_id="hotel-sintetico",
            report=_ReporteFalso("mensaje inocuo"),
            decision=_decision(),
            hotel_url="https://hotel.example",
        )
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        assert payload["gate"]["blocks_asset_generation"] is True
        assert payload["failed_error_check_names"] == ["whatsapp_consistency"]
        assert payload["failed_error_checks"][0]["score"] == 0.4
        assert payload["failed_error_checks"][0]["message"] == "crudo"

    def test_pre_gate_redacta_tambien_la_lista_de_culpables(self, tmp_path):
        decision = _decision()
        decision["guilty_checks"][0]["message"] = f"culpable con {SYNTH_PERPLEXITY}"
        path = _persist_coherence_pre_gate(
            output_dir=tmp_path,
            hotel_id="hotel-sintetico",
            report=_ReporteFalso("sin marcadores"),
            decision=decision,
            hotel_url="https://hotel.example",
        )
        crudo = Path(path).read_bytes().decode("utf-8")
        assert SYNTH_PERPLEXITY not in crudo


# --------------------------------------------------------------------------
# TAREA 3 — escritores de texto de proveedor todavia crudos
# --------------------------------------------------------------------------


class TestWritersDeProveedor:
    """PageSpeed y Places: la key viaja en la peticion, el fallo no puede traerla."""

    def _response(self, status: int, text: str = ""):
        response = MagicMock()
        response.status_code = status
        response.text = text
        return response

    def test_pagespeed_cuerpo_500_sale_redactado(self):
        client = PageSpeedClient(api_key=SYNTH_GOOGLE)
        cuerpo = f"Error: {SYNTH_OPENROUTER} no tiene permiso"
        with patch("requests.get", return_value=self._response(500, cuerpo)):
            with pytest.raises(Exception) as excinfo:
                client._make_request("https://hotel.example", "mobile")
        assert SYNTH_OPENROUTER not in str(excinfo.value)

    def test_pagespeed_mensaje_400_del_servidor_sale_redactado(self):
        client = PageSpeedClient(api_key=SYNTH_GOOGLE)
        response = MagicMock()
        response.status_code = 400
        response.json.return_value = {"error": {"message": f"bad key {SYNTH_GOOGLE}"}}
        with patch("requests.get", return_value=response):
            with pytest.raises(ValueError) as excinfo:
                client._make_request("https://hotel.example", "mobile")
        assert SYNTH_GOOGLE not in str(excinfo.value)

    def test_pagespeed_request_exception_sale_redactado(self):
        client = PageSpeedClient(api_key=SYNTH_GOOGLE)
        with patch(
            "requests.get",
            side_effect=real_requests.exceptions.RequestException(
                f"Max retries: https://www.googleapis.com/x?key={SYNTH_GOOGLE}"
            ),
        ):
            with pytest.raises(Exception) as excinfo:
                client._make_request("https://hotel.example", "mobile")
        assert SYNTH_GOOGLE not in str(excinfo.value)
        assert "Request failed" in str(excinfo.value)

    def test_places_error_message_sale_redactado(self, tmp_path):
        client = GooglePlacesClient(api_key=SYNTH_GOOGLE, cache_path=str(tmp_path / "c.json"))
        with patch(
            "modules.scrapers.google_places_client.requests.post",
            side_effect=real_requests.exceptions.RequestException(
                f"400 Bad Request: https://places.googleapis.com/v1/x?key={SYNTH_ANTHROPIC}"
            ),
        ):
            lugar = client.search_by_name("Hotel Sintetico", "Ciudad Sintetica")
        assert lugar is not None
        assert SYNTH_ANTHROPIC not in json.dumps(lugar.__dict__, default=str)


# --------------------------------------------------------------------------
# TAREA 3 — el verificador: cubre las salidas y caza las formas nuevas
# --------------------------------------------------------------------------


@pytest.fixture
def tmp_repo(tmp_path):
    _git(tmp_path, "init", "-q", "--initial-branch=main", ".")
    (tmp_path / "notas.md").write_text("documento limpio\n", encoding="utf-8")
    _git(tmp_path, "add", "notas.md")
    _git(tmp_path, "commit", "-q", "-m", "base")
    (tmp_path / ".gitignore").write_text("logs/*\noutput/*\n", encoding="utf-8")
    _git(tmp_path, "add", ".gitignore")
    _git(tmp_path, "commit", "-q", "-m", "base con salidas ignoradas")
    return tmp_path


class TestVerificadorCubreSalidas:
    """`output/` y `logs/` no estan en `git ls-files`: el check los lee ahora."""

    @pytest.mark.parametrize(
        "marcador",
        [SYNTH_OPENROUTER, SYNTH_ANTHROPIC],
        ids=["caza-sk-or", "caza-sk-ant"],
    )
    def test_patron_nuevo_caza_las_formas_que_el_viejo_perdia(self, tmp_repo, marcador):
        (tmp_repo / "notas.md").write_text(f"clave: {marcador}\n", encoding="utf-8")
        _git(tmp_repo, "add", "notas.md")
        _git(tmp_repo, "commit", "-q", "-m", "con marcador")

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert not result.passed, f"el patron no caz6 {marcador[:6]}..."
        assert "sk-or-" in result.message or "BLOCKING" in result.message

    @pytest.mark.parametrize("carpeta", ["logs", "output"])
    def test_un_marcador_en_la_salida_sin_versionar_es_blocking(self, tmp_repo, carpeta):
        destino = tmp_repo / carpeta
        destino.mkdir()
        (destino / "corrida.log").write_text(
            f"SSL bypass con key={SYNTH_GOOGLE}\n", encoding="utf-8"
        )
        # Gitignored: el arbol versionado sigue limpio y aun asi debe rodar rojo.
        assert _git_files(tmp_repo) == {"notas.md", ".gitignore"}

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert not result.passed
        assert "salida sin versionar" in result.details[0]
        assert str(destino.name) in result.details[0]

    def test_salidas_limpias_pasay_declaran_lo_que_se_leyo(self, tmp_repo):
        (tmp_repo / "logs").mkdir()
        (tmp_repo / "logs" / "corrida.log").write_text("SSL bypass para x\n", encoding="utf-8")

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert result.passed
        assert "1 salidas en output/ y logs/" in result.message, (
            "el verde tiene que decir que efectivamente leyó la salida"
        )

    def test_directorios_de_salida_ausentes_no_inventan_hallazgo(self, tmp_repo):
        # ABSENT != READ_ERROR != cubierto: cero leidos, cero alegaciones.
        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert result.passed
        assert "0 salidas en output/ y logs/" in result.message

    def test_una_salida_que_no_se_pudo_leer_es_no_legible(self, tmp_repo, monkeypatch):
        # READ_ERROR: la ruta existe al enumerarla y desaparece antes de leerse.
        (tmp_repo / "output").mkdir()
        (tmp_repo / "output" / "corrida.json").write_text("limpio\n", encoding="utf-8")
        original = rav.ValidationRunner._untracked_output_files

        def _fantasma(self):
            listed = original(self)
            return listed + [self.repo_root / "output" / "ya-no-esta.json"]

        monkeypatch.setattr(rav.ValidationRunner, "_untracked_output_files", _fantasma)

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert not result.passed
        assert result.message.startswith("NO_LEGIBLE")

    def test_archivo_grande_de_una_salida_es_no_cubierto_sin_name_error(self, tmp_repo):
        # La rama citaba un global inexistente: con un archivo >5MB el check
        # reventaba en NameError en lugar de declarar NO_CUBIERTO.
        (tmp_repo / "output").mkdir()
        (tmp_repo / "output" / "grande.log").write_text(
            "a" * (rav.ValidationRunner._MAX_SCAN_BYTES + 10), encoding="utf-8"
        )

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert not result.passed
        assert result.message.startswith("NO_CUBIERTO"), result.message

    def test_archivo_grande_versionado_es_no_cubierto_sin_name_error(self, tmp_repo):
        (tmp_repo / "grande.txt").write_text(
            "b" * (rav.ValidationRunner._MAX_SCAN_BYTES + 10), encoding="utf-8"
        )
        _git(tmp_repo, "add", "grande.txt")

        runner = rav.ValidationRunner(quick=True, repo_root=tmp_repo)
        runner._check_no_secrets()
        result = _last_result(runner)
        assert not result.passed
        assert result.message.startswith("NO_CUBIERTO"), result.message


def _git_files(repo: Path) -> set:
    salida = subprocess.run(
        ["git", "ls-files"], cwd=repo, env=_GIT_ENV, check=True, capture_output=True, text=True
    )
    return {line for line in salida.stdout.splitlines() if line}
