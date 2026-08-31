"""FASE-A (VALIDADOR-URL-PROPIA) — Contratos del guard de URL propia.

TDD: estos tests se escribieron ANTES del fix (evidencia roja: temp/fase_a_red.txt).
Congelan los contratos C1-C7 del plan VALIDADOR-URL-PROPIA-2026-08-30:

  C1  URLs de OTA / red social / buscador → UrlNoPropiaError con categoría correcta.
  C2  URLs de sitio propio (hotelsalentoreal.com y variantes) → pasan.
  C3  Subdominios (www.*, secure.*) y regionales (booking.com.co, google.com.co) → bloqueados.
  C4  --force → no lanza; retorna clasificación marcada y persiste el evento en
      .agent/memory/url_guard_force_events.json (JSON Lines append-only).
  C5  El guard reusa main._normalize_url() para el netloc (no parser propio).
  C7  Anti-falsos-positivos: matching por SUFIJO DE ETIQUETAS, nunca substring
      (bookingbogota.com, hotelairbnb.co, mytripadvisorhotel.com pasan).

Además: semántica AC6 (origen="estado_persistente" se menciona en el rechazo),
exit code 2 en el cableado CLI de ensure_url(), y nota de consistencia del
bypass: con --force la URL bloqueada SÍ se persiste como last_url (main.py
L1411, bypass explícito del operador) y la reinyección posterior será rechazada
con mención del estado persistente — ciclo auto-consistente documentado en
TestCicloForceReinyeccion.
"""

import argparse
import ast
import json
from datetime import datetime
from pathlib import Path

import pytest

from modules.data_validation.own_site_guard import (
    FORCE_EVENTS_PATH,
    ORIGEN_CLI,
    ORIGEN_ESTADO_PERSISTENTE,
    UrlClassification,
    UrlNoPropiaError,
    assert_own_site,
    classify_url,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

URL_BOOKING = "https://www.booking.com/hotel/co/finca-don-julio.es.html"
URL_INSTAGRAM = "https://www.instagram.com/fincahoteldonjulio"
URL_FACEBOOK = "https://www.facebook.com/fincahoteldonjulio"
URL_GOOGLE = "https://www.google.com/search?q=finca+hotel+don+julio"
URL_PROPIA = "https://www.hotelsalentoreal.com/"
URL_PROPIA_PATH_QUERY = "https://hotelsalentoreal.com/habitaciones?utm_source=google"


@pytest.fixture
def eventos_force(restaura_eventos_force):
    """Path real de eventos --force con snapshot/restore (el archivo es
    append-only en producción; los tests no deben dejar ruido en el repo)."""
    return restaura_eventos_force


@pytest.fixture
def restaura_eventos_force():
    path = Path(FORCE_EVENTS_PATH)
    previo = path.read_text(encoding="utf-8") if path.exists() else None
    yield path
    if previo is None:
        if path.exists():
            path.unlink()
    else:
        path.write_text(previo, encoding="utf-8")


def _lineas_eventos(path: Path):
    if not path.exists():
        return []
    return [json.loads(linea) for linea in path.read_text(encoding="utf-8").splitlines() if linea.strip()]


# ---------------------------------------------------------------------------
# C1 — OTA / red social / buscador → UrlNoPropiaError con categoría correcta
# ---------------------------------------------------------------------------

class TestC1RechazoPorCategoria:

    @pytest.mark.parametrize("url,categoria", [
        (URL_BOOKING, "ota"),
        ("https://booking.com/hotel/co/x", "ota"),
        (URL_INSTAGRAM, "red_social"),
        (URL_FACEBOOK, "red_social"),
        (URL_GOOGLE, "buscador"),
    ])
    def test_url_no_propia_lanza_con_categoria(self, url, categoria):
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(url)
        assert excinfo.value.categoria == categoria
        assert excinfo.value.clasificacion.bloqueada is True

    @pytest.mark.parametrize("url", [URL_BOOKING, URL_INSTAGRAM, URL_GOOGLE])
    def test_mensaje_nombra_plataforma_y_pide_sitio_propio(self, url):
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(url)
        mensaje = str(excinfo.value)
        assert "sitio web propio" in mensaje
        # La plataforma queda nombrada en el mensaje.
        assert any(p in mensaje for p in ("booking", "instagram", "google"))

    def test_default_origen_es_cli(self):
        """Sin origen explícito se asume --url (no menciona estado persistente)."""
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(URL_BOOKING)
        assert "persistente" not in str(excinfo.value)


# ---------------------------------------------------------------------------
# C2 — URLs de sitio propio pasan el guard
# ---------------------------------------------------------------------------

class TestC2UrlPropiaPasa:

    @pytest.mark.parametrize("url", [
        URL_PROPIA,
        URL_PROPIA_PATH_QUERY,
        "https://zione.co",
        "hotelsalentoreal.com/reservas",
    ])
    def test_sitio_propio_no_lanza(self, url):
        clasif = assert_own_site(url)
        assert isinstance(clasif, UrlClassification)
        assert clasif.bloqueada is False
        assert clasif.categoria is None

    def test_classify_marca_no_bloqueada(self):
        clasif = classify_url(URL_PROPIA)
        assert clasif.bloqueada is False
        assert clasif.netloc == "hotelsalentoreal.com"


# ---------------------------------------------------------------------------
# C3 — Subdominios y dominios regionales bloqueados
# ---------------------------------------------------------------------------

class TestC3SubdominiosYRegionales:

    @pytest.mark.parametrize("url,categoria", [
        ("https://secure.instagram.com/fincahoteldonjulio", "red_social"),
        ("https://m.facebook.com/x", "red_social"),
        ("https://booking.com.co/hotel/co/x", "ota"),
        ("https://www.booking.com.co/hotel/co/x", "ota"),
        ("https://www.airbnb.com.co/rooms/123", "ota"),
        ("https://www.google.com.co/search?q=hotel", "buscador"),
        ("https://maps.google.com/place/x", "buscador"),
    ])
    def test_subdominios_y_regionales_bloqueados(self, url, categoria):
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(url)
        assert excinfo.value.categoria == categoria


# ---------------------------------------------------------------------------
# C4 — --force: no lanza, clasificación marcada, evento persistido
# ---------------------------------------------------------------------------

class TestC4ForceBypass:

    def test_force_no_lanza_y_marca_clasificacion(self, eventos_force):
        clasif = assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        assert clasif.bloqueada is True
        assert clasif.categoria == "ota"

    def test_evento_persistido_en_ruta_por_defecto(self, eventos_force):
        assert eventos_force == REPO_ROOT / ".agent" / "memory" / "url_guard_force_events.json"
        assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        eventos = _lineas_eventos(eventos_force)
        assert any(e["url"] == URL_BOOKING and e["comando"] == "v4complete" for e in eventos)

    def test_evento_tiene_timestamp_url_comando(self, eventos_force):
        assert_own_site(URL_INSTAGRAM, force=True, comando="onboard")
        evento = next(e for e in _lineas_eventos(eventos_force) if e["url"] == URL_INSTAGRAM)
        assert set(evento) >= {"timestamp", "url", "comando"}
        datetime.fromisoformat(evento["timestamp"])  # parseable

    def test_append_only_acumula_eventos(self, tmp_path):
        path = tmp_path / "eventos.json"
        assert_own_site(URL_BOOKING, force=True, comando="v4complete", events_path=path)
        assert_own_site(URL_INSTAGRAM, force=True, comando="execute", events_path=path)
        eventos = _lineas_eventos(path)
        assert len(eventos) == 2
        assert eventos[0]["url"] == URL_BOOKING
        assert eventos[1]["url"] == URL_INSTAGRAM


# ---------------------------------------------------------------------------
# C5 — El guard reusa main._normalize_url() (no parser propio)
# ---------------------------------------------------------------------------

class TestC5ReusaNormalizeUrl:

    def test_ast_referencia_normalize_url(self):
        fuente = (REPO_ROOT / "modules" / "data_validation" / "own_site_guard.py").read_text(encoding="utf-8")
        tree = ast.parse(fuente)
        nombres = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
        atributos = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        assert "_normalize_url" in nombres or "_normalize_url" in atributos, (
            "classify_url debe extraer el netloc con main._normalize_url(), no con parser propio"
        )

    def test_soporta_url_sin_protocolo_como_normalize_url(self):
        # Comportamiento heredado de _normalize_url: URLs sin protocolo.
        assert classify_url("booking.com/hotel/co/x").bloqueada is True
        assert classify_url("hotelsalentoreal.com/habitaciones").bloqueada is False


# ---------------------------------------------------------------------------
# C7 — Anti-falsos-positivos: sufijo de etiquetas, NUNCA substring
# ---------------------------------------------------------------------------

class TestC7AntiFalsosPositivos:

    @pytest.mark.parametrize("url", [
        "https://bookingbogota.com/habitaciones",
        "https://hotelairbnb.co/",
        "https://mytripadvisorhotel.com/",
        "https://expediahotel.com.co/",
        "https://googlehotel.com/",
    ])
    def test_dominios_parecidos_no_bloqueados(self, url):
        clasif = assert_own_site(url)
        assert clasif.bloqueada is False, f"Falso positivo: {url} no es una plataforma"


# ---------------------------------------------------------------------------
# AC6 — Origen estado persistente
# ---------------------------------------------------------------------------

class TestAC6OrigenEstadoPersistente:

    def test_rechazo_menciona_estado_persistente(self):
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(URL_BOOKING, origen=ORIGEN_ESTADO_PERSISTENTE)
        assert "persistente" in str(excinfo.value)

    def test_origen_cli_sin_mencion(self):
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(URL_BOOKING, origen=ORIGEN_CLI)
        assert "persistente" not in str(excinfo.value)

    def test_ciclo_force_reinyeccion_auto_consistente(self, eventos_force):
        """Nota semántica AC6: con --force la URL bloqueada SÍ se persiste como
        last_url (bypass explícito del operador); la reinyección posterior desde
        el estado persistente es rechazada mencionando ese origen."""
        clasif = assert_own_site(URL_BOOKING, force=True, comando="v4complete")
        assert clasif.bloqueada is True
        with pytest.raises(UrlNoPropiaError) as excinfo:
            assert_own_site(URL_BOOKING, origen=ORIGEN_ESTADO_PERSISTENTE)
        assert "persistente" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Cableado CLI: ensure_url → exit code 2 (rechazo) / sin salida (OK, force)
# ---------------------------------------------------------------------------

def _args(command="v4complete", url=None, force=False):
    return argparse.Namespace(command=command, url=url, force=force)


class TestEnsureUrlExitCode2:

    def test_url_bloqueada_sale_con_codigo_2(self, capsys):
        from main import ensure_url
        with pytest.raises(SystemExit) as excinfo:
            ensure_url(argparse.ArgumentParser(), _args(url=URL_BOOKING))
        assert excinfo.value.code == 2
        stderr = capsys.readouterr().err
        assert "booking" in stderr
        assert "sitio web propio" in stderr

    @pytest.mark.parametrize("command", ["execute", "onboard", "deploy", "v4audit"])
    def test_cubre_todos_los_comandos(self, command):
        from main import ensure_url
        with pytest.raises(SystemExit) as excinfo:
            ensure_url(argparse.ArgumentParser(), _args(command=command, url=URL_BOOKING))
        assert excinfo.value.code == 2

    def test_url_propia_no_altera_el_flujo(self):
        from main import ensure_url
        assert ensure_url(argparse.ArgumentParser(), _args(url=URL_PROPIA)) is None

    def test_force_no_sale_y_mantiene_url(self, eventos_force, capsys):
        from main import ensure_url
        args = _args(url=URL_BOOKING, force=True)
        assert ensure_url(argparse.ArgumentParser(), args) is None
        assert args.url == URL_BOOKING
        assert any(e["url"] == URL_BOOKING for e in _lineas_eventos(eventos_force))

    def test_reinyeccion_envenenada_rechazada_con_mencion(self, capsys, monkeypatch, restaura_eventos_force):
        """AC6: una last_url bloqueada reinyectada desde el estado persistente
        se rechaza con mención explícita del estado persistente."""
        from main import ensure_url
        monkeypatch.setattr(
            "agent_harness.memory.MemoryManager.load_state",
            lambda self: {"last_url": URL_BOOKING},
        )
        with pytest.raises(SystemExit) as excinfo:
            ensure_url(argparse.ArgumentParser(), _args(command="v4complete", url=None))
        assert excinfo.value.code == 2
        stderr = capsys.readouterr().err
        assert "persistente" in stderr


# ===========================================================================
# FASE-B Track 1 — Superficies secundarias (last_url / comandos no-v4)
# ===========================================================================
# Congelan las tres garantias del Track 1 del plan VALIDADOR-URL-PROPIA
# (FASE-B). Auditoria F2: main() llama ensure_url() para TODOS los comandos
# (main.py L1428) ANTES de MemoryManager().save_state() (L1433), por lo que NO
# se agregan guards por modo (run_execution_mode / run_onboard_mode /
# run_deploy_mode) — seria redundancia fosilizada. Las garantias quedan
# fijadas a nivel de main():
#
#   T1-1  execute / onboard / deploy con URL bloqueada → rechazo IDENTICO que
#         v4complete (mismo mensaje, mismo exit code 2, misma API).
#   T1-2  Garantia de orden: con URL bloqueada save_state() NUNCA se llama,
#         ni siquiera a traves de main() (el rechazo precede a la persistencia).
#   T1-3  AC6 end-to-end: estado legacy envenenado (last_url bloqueada) sin
#         --url → SystemExit 2 con mencion de "persistente" y la URL NO se
#         re-persiste (ni en memoria ni en disco).
#


class _CentinelaModo(Exception):
    """Senal de que main() avanzo mas alla del guard (no debe ocurrir)."""


def _stub_modos(monkeypatch) -> None:
    """Neutraliza los runners de modo y el config-check de main().

    Motivo: estos tests suben hasta main() para congelar el ORDEN
    ensure_url → save_state. Si el guard dejara de bloquear, el test debe
    fallar rapido y en local (centinela), no lanzar pipelines reales con
    llamadas de red.
    """
    def _prohibido(*args, **kwargs):
        raise _CentinelaModo(
            "main() avanzo mas alla del guard de URL propia: el rechazo deberia "
            "haber ocurrido en ensure_url() antes de persistir/ejecutar"
        )

    for nombre in (
        "run_execution_mode",
        "run_onboard_mode",
        "run_deploy_mode",
        "run_v4_complete_mode",
        "run_v4_audit_mode",
        "maybe_run_config_check",
    ):
        monkeypatch.setattr(f"main.{nombre}", _prohibido)


@pytest.fixture
def spy_save_state(monkeypatch):
    """Registra las llamadas a MemoryManager.save_state SIN escribir en disco.

    Devuelve la lista de dicts recibidos. Main() persiste la URL justo despues
    de ensure_url(), asi que cualquier entrada con una URL bloqueada prueba que
    se rompio la garantia de orden.
    """
    llamadas: list = []

    def _spy(self, state):
        llamadas.append(dict(state))
        return True

    monkeypatch.setattr("agent_harness.memory.MemoryManager.save_state", _spy)
    return llamadas


@pytest.fixture
def snapshot_current_state():
    """Snapshot/restore del estado persistente REAL.

    Necesario solo para el test que usa save_state() real (el mas fuerte:
    demuestra que el archivo en disco no cambia). El restore deja el repo limpio
    haya o no regresion.
    """
    path = REPO_ROOT / ".agent" / "memory" / "current_state.json"
    previo = path.read_bytes() if path.exists() else None
    yield path
    if previo is None:
        if path.exists():
            path.unlink()
    else:
        path.write_bytes(previo)


def _contenido(path: Path):
    return path.read_bytes() if path.exists() else None


# ---------------------------------------------------------------------------
# T1-1 — execute / onboard / deploy rechazan exactamente igual que v4complete
# ---------------------------------------------------------------------------

class TestT11RechazoIdenticoEnComandosSecundarios:

    @pytest.mark.parametrize("command", ["execute", "onboard", "deploy"])
    def test_rechazo_contains_plataforma_y_sitio_propio(self, command, capsys):
        from main import ensure_url
        with pytest.raises(SystemExit) as excinfo:
            ensure_url(argparse.ArgumentParser(), _args(command=command, url=URL_BOOKING))
        assert excinfo.value.code == 2
        stderr = capsys.readouterr().err
        assert "URL rechazada" in stderr
        assert "booking" in stderr
        assert "sitio web propio" in stderr
        # El origen es --url, no el estado persistente.
        assert "persistente" not in stderr

    def test_mensaje_byte_a_byte_igual_que_v4complete(self, capsys):
        """Un solo guard, un solo mensaje: prohibido divergir por comando
        (mitigacion del riesgo 'divergencia de mensajes/exit code respecto a
        FASE-A' listado en el plan maestro)."""
        from main import ensure_url
        textos = {}
        for command in ("v4complete", "execute", "onboard", "deploy", "v4audit", "stage"):
            capsys.readouterr()
            args = _args(command=command, url=URL_BOOKING)
            with pytest.raises(SystemExit) as excinfo:
                ensure_url(argparse.ArgumentParser(), args)
            assert excinfo.value.code == 2, f"exit code divergente en {command}"
            textos[command] = capsys.readouterr().err
        referencia = textos["v4complete"]
        assert referencia, "el rechazo debe imprimir en stderr"
        for command, stderr in textos.items():
            assert stderr == referencia, f"mensaje divergente para el comando {command}"

    @pytest.mark.parametrize("command", ["execute", "onboard", "deploy"])
    def test_url_propia_no_altera_el_flujo_del_comando(self, command):
        from main import ensure_url
        assert ensure_url(argparse.ArgumentParser(), _args(command=command, url=URL_PROPIA)) is None


# ---------------------------------------------------------------------------
# T1-2 — Garantia de orden: ensure_url() (L1428) precede a save_state() (L1433)
# ---------------------------------------------------------------------------

class TestT12GarantiaDeOrdenEnMain:

    @pytest.mark.parametrize("command", ["v4complete", "execute", "onboard", "deploy"])
    def test_url_bloqueada_nunca_llega_a_save_state(
        self, command, monkeypatch, spy_save_state, capsys
    ):
        import main
        _stub_modos(monkeypatch)
        monkeypatch.setattr("sys.argv", ["main.py", command, "--url", URL_BOOKING])
        with pytest.raises(SystemExit) as excinfo:
            main.main()
        assert excinfo.value.code == 2
        # Contracto duro: ninguna URL bloqueada se persiste...
        assert not any(URL_BOOKING in str(call) for call in spy_save_state), (
            f"main() persistio una URL bloqueada en {command}: se rompio el orden "
            "ensure_url -> save_state"
        )
        # ... y en este camino save_state() no deberia invocarse nunca.
        assert spy_save_state == [], f"save_state() llamado con {spy_save_state}"
        assert "sitio web propio" in capsys.readouterr().err

    def test_url_propia_si_persiste_en_main(self, monkeypatch, spy_save_state, capsys):
        """Contrapositivo: el spy no es un falso verde — con URL propia main()
        SI llega a save_state(), luego el filtro del test anterior es real."""
        import main
        _stub_modos(monkeypatch)
        monkeypatch.setattr("sys.argv", ["main.py", "v4complete", "--url", URL_PROPIA])
        with pytest.raises(_CentinelaModo):
            main.main()
        assert any(URL_PROPIA in str(call) for call in spy_save_state), (
            "main() deberia persistir last_url con una URL propia"
        )


# ---------------------------------------------------------------------------
# T1-3 — AC6 end-to-end: estado legacy envenenado se rechaza y NO se re-persiste
# ---------------------------------------------------------------------------

class TestT13Ac6SinRepersistenciaEnMain:

    @pytest.mark.parametrize("command", ["v4complete", "v4audit"])
    def test_estado_envenenado_rechazado_y_no_repersistido(
        self, command, monkeypatch, spy_save_state, capsys
    ):
        """AC6 subiendo hasta main(): un last_url bloqueado (huérfano de una
        corrida anterior al guard) se rechaza con mencion explicita del estado
        persistente y no vuelve a escribirse en el estado."""
        import main
        monkeypatch.setattr(
            "agent_harness.memory.MemoryManager.load_state",
            lambda self: {"last_url": URL_BOOKING},
        )
        _stub_modos(monkeypatch)
        monkeypatch.setattr("sys.argv", ["main.py", command])
        with pytest.raises(SystemExit) as excinfo:
            main.main()
        assert excinfo.value.code == 2
        stderr = capsys.readouterr().err
        assert "persistente" in stderr
        assert "booking" in stderr
        assert "sitio web propio" in stderr
        assert spy_save_state == [], "la URL bloqueada no debe re-persistirse"

    def test_disco_no_cambia_con_estado_envenenado(
        self, monkeypatch, snapshot_current_state, capsys
    ):
        """Version mas fuerte de AC6 sin spy: con save_state() REAL el archivo
        .agent/memory/current_state.json queda intacto tras el rechazo."""
        import main
        monkeypatch.setattr(
            "agent_harness.memory.MemoryManager.load_state",
            lambda self: {"last_url": URL_BOOKING},
        )
        _stub_modos(monkeypatch)
        monkeypatch.setattr("sys.argv", ["main.py", "v4complete"])
        previo = _contenido(snapshot_current_state)
        with pytest.raises(SystemExit) as excinfo:
            main.main()
        assert excinfo.value.code == 2
        assert "persistente" in capsys.readouterr().err
        assert _contenido(snapshot_current_state) == previo, (
            "current_state.json fue modificado tras rechazar una URL bloqueada"
        )

    def test_ensure_url_no_reinyecta_en_comandos_del_tuple_de_exclusion(self):
        """Documento de comportamiento actual (no contracto deseado): el tuple
        main.py L222 ("execute","deploy","setup","onboard") EXCLUYE esos
        comandos de la reinyeccion de last_url, por lo que un estado legacy
        envenenado nunca se inyecta alli. Se verifica que ensure_url() con
        url=None no lanza: si algun dia se cambia la politica de --url
        obligatorio para esos comandos, este test debe actualizarse a conciencia
        (reportado al parent como ambiguedad D-T1-1)."""
        from main import ensure_url
        import agent_harness.memory as memory_mod
        original = memory_mod.MemoryManager.load_state
        memory_mod.MemoryManager.load_state = lambda self: {"last_url": URL_BOOKING}
        try:
            for command in ("execute", "onboard", "deploy"):
                args = _args(command=command, url=None)
                assert ensure_url(argparse.ArgumentParser(), args) is None
                assert args.url is None, (
                    f"{command} no deberia reinyectar last_url (tuple de exclusion)"
                )
        finally:
            memory_mod.MemoryManager.load_state = original
