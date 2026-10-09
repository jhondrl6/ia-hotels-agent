"""Tests de `scripts/validate_qmind_writeback.py` (FASE-UNICA de VERIFICADOR-ESCRITURA-QMIND-2026-09-20).

Lo que se prueba es el **cambio de criterio**: la ingesta ya no decide por la existencia del titulo, sino
por contenido contra la instantanea versionada en el repo (AC2) y por vigencia de una sola fuente por plan
(AC4); y la ausencia del CLI `qmind` deja de publicarse como PASS (AC3).

No hay red: se sustituye la unica frontera de E/S del CLI (`_run_qmind`) por un doble que responde
`notebook list`, `source list`, `source download` y `source upload` sobre datos en memoria, y escribe en el
destino lo que el servidor habria bajado. Todo lo demas —parseo del JSON, resolucion del notebook, el `-o`
de la bajada, el registro, la marca de reemplazo y los codigos de salida— es codigo real.

La poblacion se monta bajo `--plans-dir` y `--registro` temporales: el arbol real no se usa como fixture y
el mismo codigo goberna ambos montajes (la decision del hermano `verify_qmind_context_freshness.py`).

El control negativo esta anclado a una **revision publicada fija** (`21ade6c`, el tip anterior a esta fase),
nunca a HEAD: HEAD es el arbol que estas pruebas ayudan a cambiar.

Cada prueba de criterio usa **un solo** gobernado cuando el rojo tiene que atribuirse: con dos, el miembro
sin fuente publicada pone rojo el resultado entero y un verde de mas no se podria imputar a quien se media.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_qmind_writeback.py"
REV_SIN_ACTUALIZACION = "21ade6c"
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"
PLAN = "PLAN-A-2026-09-01"
TITULO_HISTORICO = "10-analisis: PLAN-A-2026-09-01 (lecciones aprendidas y decisiones)"
TITULO_CIERRE = "10-analisis: PLAN-A (cierre v2)"
CUERPO = "# 10-analisis del plan A\n\nLeccion durable: una fuente vieja no es un cierre.\n".encode("utf-8")


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def vw():
    return _cargar("validate_qmind_writeback_bajo_prueba", SCRIPT)


@pytest.fixture(autouse=True)
def _sin_cache_entre_pruebas(vw):
    """La cache de descargas es por corrida: sin este corte, el verde de una prueba heredaria la bajada de otra."""
    vw._CACHE_BAJADAS.clear()
    yield
    vw._CACHE_BAJADAS.clear()


class QmindFalso:
    """Responde los cuatro comandos que usa el writer y cuenta lo que se bajo y lo que se subio.

    `subidas` guarda (titulo, bytes) de cada `source upload`: asi se prueba que el writer publico con el
    titulo explicito y no con el historico. `descargas` cuenta las bajadas, para que ningun verde de
    contenido salga de una fuente que nunca bajo. `motivo` propaga la excepcion REAL del modulo
    (`QmindUnavailable`): si el doble lanzara cualquier otra, la prueba mediria al doble y no al guard.

    `respuesta_upload` sustituye la tabla que el doble imprime al confirmar la subida. El doble **respondio
    JSON desde el principio**, que no es la forma real de `qmind source upload` (es una tabla `Key: value`),
    y por eso nadie vio que la respuesta jamas se parseaba: el fixture certifica una interfaz que el servicio
    no tiene (L-T4A.5). Ahora responde la tabla y el JSON queda como opcion explicita para probar al parser.
    """

    def __init__(self, fuentes: list, contenidos: dict, motivo: str | None = None,
                 excepcion: type | None = None, respuesta_upload: str | None = None):
        self.fuentes = fuentes
        self.contenidos = contenidos
        self.motivo = motivo
        self.excepcion = excepcion
        self.respuesta_upload = respuesta_upload
        self.subidas: list[tuple[str, bytes]] = []
        self.descargas = 0

    def __call__(self, args: list) -> tuple[int, str]:
        if self.motivo:
            raise self.excepcion(self.motivo)
        if args[:2] == ["notebook", "list"]:
            return 0, json.dumps({"notebooks": [{"id": NB, "title": "iah-cli-lecciones"}]})
        if args[:2] == ["source", "list"]:
            return 0, json.dumps({"sources": self.fuentes, "totalSize": 0, "currentPage": 0})
        if args[:2] == ["source", "upload"]:
            ruta = Path(args[args.index("--file") + 1])
            titulo = args[args.index("--title") + 1]
            self.subidas.append((titulo, ruta.read_bytes()))
            ident = f"01a0bfc9-5f5a-783e-9492-{len(self.fuentes) + 1:012d}"
            self.fuentes.append(_fuente(ident, titulo, ruta.read_bytes()))
            if self.respuesta_upload is not None:
                return 0, self.respuesta_upload
            return 0, _tabla_de_subida(ident, titulo, ruta.name)
        if args[:2] == ["source", "download"]:
            source_id = args[args.index("--nb") + 2]
            destino = Path(args[args.index("-o") + 1])
            self.descargas += 1
            if source_id not in self.contenidos:
                return 1, "fuente sin archivo original"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(self.contenidos[source_id])
            return 0, f"Downloaded {destino}"
        return 1, "comando no esperado"


def _tabla_de_subida(source_id: str, titulo: str, archivo: str) -> str:
    """La forma con la que `qmind source upload` responde de verdad: siete lineas `Key: value`.

    Copiada de la subida archivada por el hermano en
    `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/39-de-subida-leccion-11.txt`
    (se conserva la clave `URI:` con una ruta sintetizada: la linea existe en la forma real y aqui no va ningun
    enlace firmado). Alineacion incluida: el valor viene despues de varios espacios, no de un solo `:`.
    """
    return (f"ID:          {source_id}\n"
            f"NotebookID:  {NB}\n"
            f"Title:       {titulo}\n"
            f"Type:        markdown\n"
            f"Status:      pending\n"
            f"URI:         notebook/sources/{NB}/00000000-0000-0000-0000-000000000000/{archivo}\n"
            f"UpdatedAt:   2026-10-08T00:00:00Z\n")


def _fuente(source_id: str, titulo: str, contenido: bytes, metadata: bool = True) -> dict:
    return {"id": source_id, "title": titulo, "status": "ready",
            "metadata": ({"fileSha256": hashlib.sha256(contenido).hexdigest(),
                          "fileSize": len(contenido)} if metadata else {})}


def _fuente_sin_promesa(source_id: str, titulo: str) -> dict:
    return {"id": source_id, "title": titulo, "status": "ready", "metadata": {}}


def _id(n: int) -> str:
    return f"01a0bfc9-5f5a-783e-9492-{n:012d}"


@pytest.fixture
def montaje(tmp_path):
    """(plans, registro, cuerpo) en tmp, con un plan archivado y su 10-analisis en disco."""
    plans = tmp_path / "plans"
    cuerpo = plans / "Archives" / PLAN / "10-analisis-post-implementacion.md"
    cuerpo.parent.mkdir(parents=True)
    cuerpo.write_bytes(CUERPO)
    registro = tmp_path / "qmind" / "registro.json"
    registro.parent.mkdir(parents=True)
    registro.write_text(json.dumps({"schema_version": "1.0", "entradas": []}), encoding="utf-8")
    return {"plans": plans, "registro": registro, "cuerpo": cuerpo, "tmp": tmp_path}


def _publicar(vw, m, titulo: str, archivo: Path = None) -> dict:
    """Deja en el registro una publicacion vigente de `titulo`, con su instantanea copiada al montaje.

    `cuerpo` es el cuerpo del plan en disco (`m["cuerpo"]`) y `archivo` la copia que se publica: desde AC1
    el writer graba las dos identidades, y las pruebas de la familia vieja publican el cuerpo sin sanear,
    donde son el mismo byte-exacto.
    """
    datos = vw.cargar_registro(m["registro"])
    return vw.registrar_publicacion(datos, m["registro"], PLAN, titulo,
                                    archivo or m["cuerpo"], "", "2026-10-07", m["cuerpo"])


def _corrida(vw, monkeypatch, m, fuentes, contenidos, *extra) -> tuple:
    falso = QmindFalso(fuentes, contenidos)
    monkeypatch.setattr(vw, "_run_qmind", falso)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro",
                         str(m["registro"]), *extra])
    return salio, falso, buffer.getvalue()


# ------------------------------------------------------------------ AC1: el writer admite actualizacion

def test_title_y_file_solo_tienen_sentido_con_upload(vw):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--title", "cierre v2"])
    assert salio == 1
    assert "--title y --file solo tienen sentido con --upload" in buffer.getvalue()


def test_control_negativo_el_writer_versionado_antes_no_aceptaba_title(tmp_path):
    """`21ade6c` es el tip anterior a la fase: su parser moria con `--title` (SystemExit 2 de argparse)."""
    proc = subprocess.run(["git", "show", f"{REV_SIN_ACTUALIZACION}:scripts/validate_qmind_writeback.py"],
                          cwd=str(ROOT), capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", errors="replace")
    viejo = proc.stdout.decode("utf-8")
    # El literal `--title` ya existia, pero solo como argumento del CLI `qmind` dentro de `upload_source()`:
    # la prueba de que no era bandera del writer es el parser, no la cadena suelta.
    assert viejo.count('"--title"') == 1, "el blob de referencia cambio de forma: re-anclar el control"
    assert 'add_argument' in viejo and 'add_argument(\n        "--title"' not in viejo
    ruta = tmp_path / "writer_viejo.py"
    ruta.write_text(viejo, encoding="utf-8", newline="\n")
    # Se ejercita como CLI, que es como lo invoca el runner: el parser del writer viejo moria con
    # `--title` antes de tocar el notebook, asi que el exit 2 de argparse es el control limpio.
    proc = subprocess.run([sys.executable, str(ruta), "--title", "cierre v2"],
                          capture_output=True, cwd=str(ROOT))
    assert proc.returncode == 2
    assert b"unrecognized arguments" in proc.stderr


def test_file_fuera_del_repo_corta_antes_de_subir_nada(vw, montaje, monkeypatch):
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    suelto = m["tmp"].parent / "fuera-del-montaje.md"
    suelto.write_bytes(CUERPO)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE,
                             archivo=suelto, registro_path=m["registro"], repo_root=m["tmp"])
    assert salio == 1
    assert "--file tiene que estar bajo el repo" in buffer.getvalue()
    assert falso.subidas == []
    assert len(vw.cargar_registro(m["registro"])["entradas"]) == 0, "un rechazo no registra nada"
    suelto.unlink()


def test_upload_explicito_registra_instanea_y_marca_la_anterior(vw, montaje, monkeypatch):
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    copia = m["tmp"] / "copia-saneada.md"
    copia.write_bytes(b"# 10-analisis saneado del cierre\n")
    plan_dir = m["plans"] / "Archives" / PLAN
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        primero = vw.do_upload(plan_dir, NB, registro_path=m["registro"], fecha="2026-10-01",
                               repo_root=m["tmp"])
        segundo = vw.do_upload(plan_dir, NB, titulo=TITULO_CIERRE, archivo=copia,
                               registro_path=m["registro"], fecha="2026-10-07", repo_root=m["tmp"])
    assert (primero, segundo) == (0, 0)
    datos = vw.cargar_registro(m["registro"])
    assert len(datos["entradas"]) == 2
    assert datos["entradas"][0]["estado"] == vw.ESTADO_REEMPLAZADA
    assert datos["entradas"][0]["reemplazada_por"] == TITULO_CIERRE
    assert datos["entradas"][1]["estado"] == vw.ESTADO_VIGENTE
    assert datos["entradas"][1]["sha256"] == hashlib.sha256(b"# 10-analisis saneado del cierre\n").hexdigest()
    instanea = vw.directorio_de_instantaneas(m["registro"]) / datos["entradas"][1]["instanea"]
    assert instanea.read_bytes() == b"# 10-analisis saneado del cierre\n"
    assert [t for t, _ in falso.subidas] == [TITULO_HISTORICO, TITULO_CIERRE]
    assert "sha256=" in buffer.getvalue()


def test_titulo_ya_vigente_con_contenido_distinto_no_colisiona_en_silencio(vw, montaje, monkeypatch):
    m = montaje
    viejo = b"# cuerpo publicado a mitad de plan\n"
    fuente = _fuente(_id(7), TITULO_CIERRE, viejo)
    falso = QmindFalso([fuente], {fuente["id"]: viejo})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    copia = m["tmp"] / "copia-saneada.md"
    copia.write_bytes(CUERPO)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE, archivo=copia,
                             registro_path=m["registro"], repo_root=m["tmp"])
    assert salio == 1
    assert "ya esta vigente" in buffer.getvalue().replace("á", "a")
    assert falso.subidas == [], "re-usar un titulo vigente publicaria un duplicado sin marca"
    assert len(vw.cargar_registro(m["registro"])["entradas"]) == 0


def test_titulo_ya_vigente_con_el_mismo_contenido_es_skip_declarado(vw, montaje, monkeypatch):
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    fuente = _fuente(_id(8), TITULO_CIERRE, CUERPO)
    falso = QmindFalso([fuente], {fuente["id"]: CUERPO})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE,
                             archivo=m["cuerpo"], registro_path=m["registro"], repo_root=m["tmp"])
    assert salio == 0
    assert "[SKIP]" in buffer.getvalue()
    assert falso.subidas == []
    assert len(vw.cargar_registro(m["registro"])["entradas"]) == 1


def test_el_default_de_upload_sigue_publicando_con_el_titulo_historico(vw, montaje, monkeypatch):
    """AC1: sin --title/--file, `--upload <PLAN>` hace exactamente lo de siempre."""
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, registro_path=m["registro"],
                             fecha="2026-10-07", repo_root=m["tmp"])
    assert salio == 0
    assert [t for t, _ in falso.subidas] == [TITULO_HISTORICO]
    assert TITULO_HISTORICO in buffer.getvalue()


# ----------------------------------------------------- AC2 y AC4: contenido y vigencia, no existencia


def test_instanea_editada_sin_re_subir_es_vencido(vw, montaje, monkeypatch):
    """M1: mover la instantanea versionada sin volver a publicar corta rojo por el guard de contenido.

    La razon se nombra y se exige: sin ella, una segunda guarda de contenido (registro vs instantanea)
    daria tambien `[VENCIDO]` y el mutante M1 passaria desapercibido. Se pide ademas que el rojo corte
    ANTES de bajar nada: la comprobacion local no depende del servicio.
    """
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    datos = vw.cargar_registro(m["registro"])
    instanea = vw.directorio_de_instantaneas(m["registro"]) / datos["entradas"][0]["instanea"]
    instanea.write_bytes(CUERPO + b"\nreedactada en el disco\n")
    fuente = _fuente(_id(9), TITULO_CIERRE, CUERPO)
    salio, falso, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 1
    assert "la instantanea publicada" in salida
    assert falso.descargas == 0, "la guarda local corta antes de preguntar al servicio"
    assert "[PASS]" not in salida


def test_cuerpo_que_cambio_despues_de_publicar_es_vencido(vw, montaje, monkeypatch):
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    m["cuerpo"].write_bytes(CUERPO + b"\nY hoy escribi el cierre\n")
    fuente = _fuente(_id(10), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 1
    assert "[VENCIDO]" in salida and "la instantanea publicada" in salida


def test_titulo_coincidente_con_contenido_distinto_es_rojo(vw, montaje, monkeypatch):
    """El defecto de P3 en su forma literal: hay fuente con el titulo, pero su cuerpo es otro."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    ingerido = b"# lo que el notebook guardo en realidad\n"
    fuente = _fuente_sin_promesa(_id(11), TITULO_CIERRE)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: ingerido})
    assert salio == 1
    assert "titulo coincidente con contenido distinto" in salida


def test_metadata_del_servidor_es_primera_via_y_la_descarga_la_verifica(vw, montaje, monkeypatch):
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    fuente = _fuente(_id(12), TITULO_CIERRE, CUERPO)
    salio, falso, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 0
    assert "[FRESCO]" in salida and "metadata del" in salida
    assert falso.descargas == 1, "ningun verde sale de la metadata sin haber bajado la fuente"


def test_fuente_que_promete_y_no_baja_es_no_evaluable_nunca_vencido(vw, montaje, monkeypatch):
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    fuente = _fuente(_id(13), TITULO_CIERRE, CUERPO)
    salio, falso, salida = _corrida(vw, monkeypatch, m, [fuente], {})
    assert salio == 2
    assert "[NO-EVALUABLE]" in salida and "[VENCIDO]" not in salida
    assert falso.descargas == 1


def test_descarga_que_desmiente_la_promesa_es_promesa_rota(vw, montaje, monkeypatch):
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    fuente = _fuente(_id(14), TITULO_CIERRE, CUERPO)
    contradictorio = b"# el servidor guarda otros bytes\n"
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: contradictorio})
    assert salio == 1
    assert "[PROMESA-ROTA]" in salida


def test_dos_fuentes_vigentes_sin_marca_de_reemplazo_cortan(vw, montaje, monkeypatch):
    """M3: la fuente que nombra al plan y no esta contable en el registro es el duplicado de P5."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    vigente = _fuente(_id(15), TITULO_CIERRE, CUERPO)
    huesped = _fuente(_id(16), TITULO_HISTORICO, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [vigente, huesped],
                                {vigente["id"]: CUERPO, huesped["id"]: CUERPO})
    assert salio == 1
    assert "[DUPLICADO-VIGENTE]" in salida


def test_la_fuente_marcada_como_reemplazada_no_duplica(vw, montaje, monkeypatch):
    m = montaje
    _publicar(vw, m, TITULO_HISTORICO)
    datos = vw.cargar_registro(m["registro"])
    vw.registrar_publicacion(datos, m["registro"], PLAN, TITULO_CIERRE, m["cuerpo"], "", "2026-10-07",
                             m["cuerpo"])
    vieja = _fuente(_id(17), TITULO_HISTORICO, CUERPO)
    nueva = _fuente(_id(18), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [vieja, nueva],
                                {vieja["id"]: CUERPO, nueva["id"]: CUERPO})
    assert salio == 0, salida
    assert "[DUPLICADO-VIGENTE]" not in salida


def test_registro_vacio_no_es_verde_sino_no_evaluable(vw, montaje, monkeypatch):
    """Sin publicaciones registradas la capa de contenido no goberna nada: no puede decir PASS."""
    m = montaje
    fuente = _fuente(_id(19), TITULO_HISTORICO, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 2
    assert "0 instantaneas vigentes" in salida
    assert "[PASS]" not in salida


def test_cuerpo_inaccesible_es_no_evaluable_no_vencido(vw, montaje, monkeypatch):
    m = montaje
    entrada = _publicar(vw, m, TITULO_CIERRE)
    m["cuerpo"].unlink()
    fuente = _fuente(_id(20), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 2
    assert "no resuelve bajo" in salida and "[VENCIDO]" not in salida
    assert entrada["estado"] == vw.ESTADO_VIGENTE


def test_el_rojo_manda_sobre_la_abstencion(vw, montaje, monkeypatch):
    """Un gobernado VENCIDO y otro NO-EVALUABLE en la misma corrida: sale 1 y se imprimen los dos."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    m["cuerpo"].write_bytes(CUERPO + b"\ncambiado tras publicar\n")
    (m["plans"] / "Archives" / "PLAN-B-2026-09-02").mkdir(parents=True)
    datos = vw.cargar_registro(m["registro"])
    vw.registrar_publicacion(datos, m["registro"], "PLAN-B-2026-09-02",
                             "10-analisis: PLAN-B (cierre)", m["cuerpo"], "", "2026-10-07", m["cuerpo"])
    fuente = _fuente(_id(21), TITULO_CIERRE, CUERPO + b"\ncambiado tras publicar\n")
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 1
    assert "[VENCIDO]" in salida and "[NO-EVALUABLE]" in salida


# ------------------------------------------------------------------ AC3: fin del verde por ausencia


def test_sin_qmind_sin_strict_es_no_evaluable_y_nunca_pass(vw, montaje, monkeypatch):
    """M2: la ausencia del instrumento era exit 0 y el runner la pintaba de PASS. Ahora es estado propio."""
    m = montaje
    falso = QmindFalso([], {}, motivo="CLI 'qmind' no esta instalado ni en PATH",
                       excepcion=vw.QmindUnavailable)
    monkeypatch.setattr(vw, "_run_qmind", falso)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(m["registro"])])
    assert salio == 2
    salida = buffer.getvalue()
    assert "[NO-EVALUABLE]" in salida and "[PASS]" not in salida


def test_con_strict_el_cli_ausente_corta_fail(vw, montaje, monkeypatch):
    m = montaje
    falso = QmindFalso([], {}, motivo="CLI 'qmind' no esta instalado ni en PATH",
                       excepcion=vw.QmindUnavailable)
    monkeypatch.setattr(vw, "_run_qmind", falso)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--nb", NB, "--strict", "--plans-dir", str(m["plans"]),
                         "--registro", str(m["registro"])])
    assert salio == 1
    assert "[FAIL]" in buffer.getvalue()


def test_el_check_del_runner_invoca_con_strict_y_trata_el_dos_como_estado_propio():
    """El guard de AC3 vive en `_check_qmind_writeback()`: se prueba sobre la fuente del runner."""
    fuente = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
    cuerpo = fuente.split("    def _check_qmind_writeback(self)", 1)[1].split("\n    def ", 1)[0]
    assert '"--strict"' in cuerpo, "el check volveria a publicar la ausencia del CLI como PASS"
    assert "exit_code == 2" in cuerpo and "NO-EVALUABLE" in cuerpo
    assert cuerpo.index("exit_code == 0") < cuerpo.index("exit_code == 2"), \
        "el PASS tiene que estar cortado por codigo 0: un 2 que cayera al final seria verde hueco"
    assert cuerpo.count("passed=True") == 1, "solo el codigo 0 puede dar verde"


def test_el_check_queda_cableado_al_modo_completo_y_no_al_rapido():
    """L-V3.1: el verificador vive solo en el modo completo; el rapido sigue corriendo sin red."""
    fuente = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
    cuerpo = fuente.split("    def run_all(self) -> bool:", 1)[1]
    antes, sep, despues = cuerpo.partition("        if not self.quick:")
    assert sep
    assert "self._check_qmind_writeback()" in despues
    assert "self._check_qmind_writeback()" not in antes
    assert "self._check_context_freshness()" in despues


def test_collect_archived_analisis_resuelve_bajo_la_raiz_de_planes(vw, montaje):
    """La poblacion se resuelve bajo `--plans-dir`: si no, el verde saldria del arbol real y no del montaje."""
    m = montaje
    assert vw.collect_archived_analisis(m["plans"]) == [(PLAN, m["cuerpo"])]
    assert vw.collect_archived_analisis(m["tmp"] / "no-existe") == []


# ------------------------------------------- FASE-A1 de CURA-INSTRUMENTOS-QMIND-S15: AC1 y AC2


def _entrada_1_0(vw, m, titulo: str, contenido: bytes) -> str:
    """Una entrada en la forma del registro real del padre: con `sha256` de la instantanea y **sin** `sha_cuerpo`.

    Se escribe como dato de montaje, no como imitacion del defecto: lo que se prueba es al lector curado
    sobre la poblacion `1.0` que ya existe en `.opencode/qmind-writeback/registro.json`.
    """
    nombre = "instanea-anterior-a-la-cura.md"
    destino = vw.directorio_de_instantaneas(m["registro"]) / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    m["registro"].write_text(json.dumps(
        {"schema_version": "1.0",
         "entradas": [{"plan": PLAN, "titulo": titulo, "estado": "vigente", "fuente_id": "",
                       "sha256": hashlib.sha256(contenido).hexdigest(), "instanea": nombre,
                       "publicado": "2026-10-07"}]}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return nombre


def _modulo_versionado(rev: str, destino_dir: Path, nombre: str):
    """Carga el writer commiteado en `rev`, no un defecto reimplementado dentro del test."""
    proc = subprocess.run(["git", "show", f"{rev}:scripts/validate_qmind_writeback.py"],
                          cwd=str(ROOT), capture_output=True)
    assert proc.returncode == 0, proc.stderr.decode("utf-8", errors="replace")
    destino_dir.mkdir(parents=True, exist_ok=True)
    ruta = destino_dir / nombre
    ruta.write_bytes(proc.stdout)
    return _cargar(f"writer_versionado_{rev}", ruta)


def test_el_registro_graba_sha_cuerpo_del_cuerpo_y_no_de_la_copia_saneada(vw, montaje, monkeypatch):
    """AC1 en el artefacto: las dos identidades conviven y se distinguen leyendo solo el JSON."""
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    copia = m["tmp"] / "copia-saneada.md"
    copia.write_bytes(b"# 10-analisis con las identidades sustituidas\n")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE, archivo=copia,
                             registro_path=m["registro"], fecha="2026-10-07", repo_root=m["tmp"])
    assert salio == 0
    en_disco = json.loads(m["registro"].read_text(encoding="utf-8"))
    assert en_disco["schema_version"] == "1.1"
    entrada = en_disco["entradas"][0]
    assert entrada["sha_cuerpo"] == hashlib.sha256(CUERPO).hexdigest()
    assert entrada["sha256"] == hashlib.sha256(copia.read_bytes()).hexdigest()
    assert entrada["sha_cuerpo"] != entrada["sha256"], "una copia saneada no es el cuerpo: dos shas distintos"
    assert falso.subidas and falso.subidas[0][1] == copia.read_bytes()


def test_la_migracion_no_rellena_hacia_atras_la_entrada_vieja(vw, montaje, monkeypatch):
    """Prohibido back-fill: correr el verificador no escribe el registro, y menos sobre una entrada `1.0`."""
    m = montaje
    _entrada_1_0(vw, m, TITULO_CIERRE, CUERPO)
    antes = m["registro"].read_bytes()
    fuente = _fuente(_id(30), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 2
    assert m["registro"].read_bytes() == antes, "el lector de vigencia no es escritor del pasado"
    assert "sha_cuerpo" not in json.loads(antes.decode("utf-8"))["entradas"][0]


def test_entrada_sin_sha_cuerpo_es_no_evaluable_por_migracion(vw, montaje, monkeypatch):
    """L-QW.3: la ausencia del dato no se pinta ni de VENCIDO ni de verde, aunque lo remoto case todo."""
    m = montaje
    _entrada_1_0(vw, m, TITULO_CIERRE, CUERPO)
    fuente = _fuente(_id(31), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 2
    assert "no grabo sha_cuerpo" in salida and "schema 1.0" in salida
    assert "[VENCIDO]" not in salida and "[FRESCO]" not in salida and "[PASS]" not in salida
    assert "ver el [CONTADOR]" in salida, "hubo poblacion gobernada: el resumen no puede decir «ninguna»"
    assert "no goberna ninguna publicacion todavia" not in salida


def test_cuerpo_editado_despues_de_publicar_es_vencido_por_cuerpo(vw, montaje, monkeypatch):
    """Diente de vigencia real: la linea nombra el cuerpo y el rojo corta antes de preguntar al servicio.

    Se exige ademas que NO sea el gate de registro el que habla: con dos guards locales sobre el mismo
    `[VENCIDO]`, afirmar solo la etiqueta dejaria el diente verde por la rama equivocada (L-V2.1).
    """
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    copia = m["tmp"] / "copia-saneada.md"
    copia.write_bytes(b"# 10-analisis con las identidades sustituidas\n")
    with redirect_stdout(io.StringIO()):
        assert vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE, archivo=copia,
                            registro_path=m["registro"], fecha="2026-10-07", repo_root=m["tmp"]) == 0
    m["cuerpo"].write_bytes(CUERPO + b"\nescrito despues de publicar\n")
    fuente = _fuente(_id(32), TITULO_CIERRE, copia.read_bytes())
    salio, falso2, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: copia.read_bytes()})
    assert salio == 1
    assert "sha_cuerpo=" in salida and "el cuerpo del repo" in salida and str(m["cuerpo"]) in salida
    assert "que declara el registro" not in salida, "el rojo es de cuerpo, no del gate de registro"
    assert falso2.descargas == 0


def test_copia_saneada_con_cuerpo_intacto_es_vigente_y_el_guard_versionado_cortaba_vencido(vw, montaje,
                                                                                            monkeypatch, tmp_path):
    """El diente contrario (L-QW.1): la misma poblacion sobre los dos instrumentos, en las dos direcciones.

    `d8a7d80` es el tip con el que abrio FASE-A1: su puerta comparaba sha(instantanea) contra sha(cuerpo
    crudo), asi que publicar una copia saneada era estructuralmente vencible. El control se ejecuta sobre el
    blob commiteado, no sobre un defecto reimplementado aqui dentro.
    """
    viejo = _modulo_versionado("d8a7d80", tmp_path / "control", "writer_viejo.py")
    for mod, registro in ((viejo, tmp_path / "control" / "qmind" / "registro.json"),
                          (vw, montaje["registro"])):
        m = montaje
        copia = m["tmp"] / "copia-saneada-para-el-control.md"
        copia.write_bytes(b"# 10-analisis con las identidades sustituidas\n")
        falso = QmindFalso([], {})
        monkeypatch.setattr(mod, "_run_qmind", falso)
        monkeypatch.setattr(mod, "scan_context_declarations", lambda: [])
        registro.parent.mkdir(parents=True, exist_ok=True)
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            assert mod.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE, archivo=copia,
                                 registro_path=registro, fecha="2026-10-07", repo_root=m["tmp"]) == 0
            doble = QmindFalso(falso.fuentes, {f["id"]: copia.read_bytes() for f in falso.fuentes})
            monkeypatch.setattr(mod, "_run_qmind", doble)
            salio = mod.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(registro)])
        salida = buffer.getvalue()
        assert salio == (1 if mod is viejo else 0), salida
        if mod is viejo:
            assert "[VENCIDO]" in salida and "ya no casa con el cuerpo del repo" in salida
            assert doble.descargas == 0, "el guard viejo cortaba antes de medir lo remoto"
        else:
            assert "[VENCIDO]" not in salida and "[FRESCO]" in salida
            assert "1 dictaminada(s) por cuerpo" in salida, "el verde tiene que nombrar la pregunta que Respondio"
            assert doble.descargas == 1


def test_los_tres_estados_del_contador_no_se_colapsan(vw, montaje, monkeypatch):
    """R2.9: sin hallazgos, ausente y lector fallido salen por textos distintos y con su denominador."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    fuente = _fuente(_id(33), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    contador = next(l for l in salida.splitlines() if "[CONTADOR]" in l)
    assert salio == 0
    assert "1 vigente(s)" in contador and "0 NO-EVALUABLE por migracion" in contador
    assert "1+0+0==1" in contador, "el contador publica su suma, no solo sus sumandos"

    ruta_ausente = m["tmp"] / "sin-registro" / "registro.json"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio2 = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(ruta_ausente)])
    salida2 = buffer.getvalue()
    assert salio2 == 2
    assert "0 instantaneas vigentes" in salida2 and str(ruta_ausente) in salida2
    assert "[CONTADOR]" not in salida2, "un censo vacio no publica un denominador falso"

    roto = m["tmp"] / "registro-roto.json"
    roto.write_text("{ no es json", encoding="utf-8")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio3 = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(roto)])
    salida3 = buffer.getvalue()
    assert salio3 == 1
    assert "registro de write-back ilegible" in salida3 and str(roto) in salida3
    assert len({salida, salida2, salida3}) == 3


def test_el_rojo_manda_sobre_la_abstencion_de_migracion(vw, montaje, monkeypatch):
    """Un dictamen VENCIDO por cuerpo y una abstencion por migracion en la misma corrida: EXIT 1, las dos lineas."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    viejo_plan = "PLAN-VIEJO-2026-09-02"
    viejo_dir = m["plans"] / "Archives" / viejo_plan
    viejo_dir.mkdir(parents=True)
    contenido_viejo = CUERPO + b"\nla entrada antigua\n"
    (viejo_dir / "10-analisis-post-implementacion.md").write_bytes(contenido_viejo)
    destino = vw.directorio_de_instantaneas(m["registro"]) / "instanea-1-0.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido_viejo)
    datos = vw.cargar_registro(m["registro"])
    datos["entradas"].append({"plan": viejo_plan, "titulo": "10-analisis: PLAN-VIEJO (cierre)",
                              "estado": "vigente", "fuente_id": "",
                              "sha256": hashlib.sha256(contenido_viejo).hexdigest(),
                              "instanea": "instanea-1-0.md", "publicado": "2026-09-30"})
    vw.guardar_registro(m["registro"], datos)
    m["cuerpo"].write_bytes(CUERPO + b"\nescrito despues de publicar\n")
    fuente = _fuente(_id(34), TITULO_CIERRE, CUERPO)
    huesped = _fuente(_id(35), "10-analisis: PLAN-VIEJO (cierre)", contenido_viejo)
    salio, _, salida = _corrida(vw, monkeypatch, m, [fuente, huesped],
                                {fuente["id"]: CUERPO, huesped["id"]: contenido_viejo})
    assert salio == 1
    assert "sha_cuerpo=" in salida and "no grabo sha_cuerpo" in salida
    assert "1+1+0==2" in next(l for l in salida.splitlines() if "[CONTADOR]" in l)


def test_sin_cuerpo_resoluble_el_writer_no_publica_ni_graba(vw, montaje, monkeypatch):
    """El guard nuevo del escritor: sin cuerpo no hay sha_cuerpo, y el registro no se inventa uno."""
    m = montaje
    vacio = m["plans"] / "Archives" / "PLAN-SIN-CUERPO-2026-09-03"
    vacio.mkdir(parents=True)
    copia = m["tmp"] / "copia-saneada.md"
    copia.write_bytes(b"# copia con cuerpo inalcanzable\n")
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(vacio, NB, titulo="10-analisis: PLAN-SIN-CUERPO (cierre)", archivo=copia,
                             registro_path=m["registro"], fecha="2026-10-07", repo_root=m["tmp"])
    assert salio == 1
    assert "no resuelve bajo" in buffer.getvalue() and "PLAN-SIN-CUERPO-2026-09-03" in buffer.getvalue()
    assert falso.subidas == [], "rechazar antes de tocar el notebook: una publicacion a medias es peor"
    assert vw.cargar_registro(m["registro"])["entradas"] == []


# ---------------------------------- FASE-A2 de CURA-INSTRUMENTOS-QMIND-S15: AC3 y AC4

TITULO_LARGO_1 = "10-analisis: " + PLAN + " (cierre " + "x" * 140 + ", primera)"
TITULO_LARGO_2 = "10-analisis: " + PLAN + " (cierre " + "x" * 140 + ", segunda)"
TITULO_LARGO_3 = "10-analisis: " + PLAN + " (cierre " + "x" * 140 + ", tercera)"
TABLA_DEGENERADA = (f"NotebookID:  {NB}\n"
                    f"Title:       {TITULO_CIERRE}\n"
                    f"Type:        markdown\n"
                    f"Status:      pending\n")


def _subir_explicito(vw, m, falso, titulo: str, copia: Path, monkeypatch, fecha: str = "2026-10-08") -> str:
    """Publica una copia explicita por el camino real (`do_upload`) y devuelve lo que imprimio."""
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=titulo, archivo=copia,
                             registro_path=m["registro"], fecha=fecha, repo_root=m["tmp"])
    assert salio == 0, buffer.getvalue()
    return buffer.getvalue()


def _copia(vw, m, n: int, texto: str) -> Path:
    copia = m["tmp"] / f"copia-{n}.md"
    copia.write_bytes(texto.encode("utf-8"))
    return copia


class _CensoSeparado:
    """Deja fija la respuesta de `source list` mientras el upload sigue registrandose en el doble.

    Hace falta porque el doble anade la fuente subida a su propio censo: sin este corte la rama de ausencia
    y la de lector fallido serian inalcanzables y su verde no tendria oportunidad de perder. La excepcion
    que lanza es la REAL del modulo, para que la prueba mida al guard y no al doble.
    """

    def __init__(self, vw, base, fuentes=None, falla=False):
        self.base = base
        self.fuentes = fuentes
        self.falla = falla
        self.QmindUnavailable = vw.QmindUnavailable

    def __call__(self, args: list) -> tuple[int, str]:
        if args[:2] == ["source", "list"]:
            # El censo que se corta es el POSTERIOR a la publicacion: `do_upload` lista los titulos antes de
            # subir nada, y fallar ahi seria probar otro guard (el de ingesta previa), no este.
            if self.falla and self.base.subidas:
                raise self.QmindUnavailable("qmind source list falló: el servicio no respondio")
            if self.fuentes is not None:
                return 0, json.dumps({"sources": self.fuentes, "totalSize": 0, "currentPage": 0})
        return self.base(args)

    @property
    def subidas(self):
        return self.base.subidas


def test_dos_publicaciones_del_mismo_plan_dejan_dos_byte_exactos_distintos(vw, montaje, monkeypatch):
    """AC3 con la forma que perdio los bytes del padre: dos titulos de prefijo comun y cuerpo distinto.

    La asercion que pierde con el slug viejo es la de los **bytes propios** de cada entrada, no la
    existencia del archivo: con el prefijo trancado a 120 caracteres las dos publicaciones compartian
    nombre y la segunda copia pisaba a la primera.
    """
    m = montaje
    una, dos = _copia(vw, m, 1, "# cuerpo de la primera publicacion\n"), _copia(vw, m, 2, "# cuerpo de la segunda\n")
    _subir_explicito(vw, m, QmindFalso([], {}), TITULO_LARGO_1, una, monkeypatch)
    _subir_explicito(vw, m, QmindFalso([], {}), TITULO_LARGO_2, dos, monkeypatch)
    datos = vw.cargar_registro(m["registro"])
    nombres = [e["instanea"] for e in datos["entradas"]]
    assert len(nombres) == len(set(nombres)) == 2
    for entrada, copia in zip(datos["entradas"], (una, dos)):
        ruta = vw.directorio_de_instantaneas(m["registro"]) / entrada["instanea"]
        assert ruta.read_bytes() == copia.read_bytes(), \
            f"{entrada['instanea']} no casa con su propio byte-exacto"
        assert entrada["sha256"] == hashlib.sha256(copia.read_bytes()).hexdigest()


def test_un_tercer_titulo_de_prefijo_comun_tampoco_pisa_los_anteriores(vw, montaje, monkeypatch):
    """AC3: tres publicaciones seguidas del mismo plan dejan tres archivos, no tres punteros a uno."""
    m = montaje
    copias = tuple(_copia(vw, m, i, f"# cuerpo {i}\n") for i in (1, 2, 3))
    for titulo, copia in zip((TITULO_LARGO_1, TITULO_LARGO_2, TITULO_LARGO_3), copias):
        _subir_explicito(vw, m, QmindFalso([], {}), titulo, copia, monkeypatch)
    datos = vw.cargar_registro(m["registro"])
    assert len({e["instanea"] for e in datos["entradas"]}) == 3
    for entrada, copia in zip(datos["entradas"], copias):
        assert (vw.directorio_de_instantaneas(m["registro"]) / entrada["instanea"]).read_bytes() == copia.read_bytes()


def test_la_huella_del_nombre_es_el_sha256_de_su_propia_entrada(vw, montaje):
    """AC3 por el nombre: `instanea` termina en la huella del `sha256` que la entrada declara."""
    m = montaje
    entrada = _publicar(vw, m, TITULO_CIERRE)
    assert entrada["instanea"].endswith("--" + entrada["sha256"][:vw.HUELLA_INSTANEA] + ".md")


def test_el_nombre_conserva_el_prefijo_legible_y_llena_el_presupuesto_sin_cortar_la_huella(vw):
    """Lo que un humano ve en `instantaneas/`: prefijo del plan, recorte en el titulo, huella intacta."""
    sha = hashlib.sha256(b"cuerpo").hexdigest()
    slug = vw.slug_de_instantanea(PLAN, TITULO_LARGO_1, sha)
    assert slug.startswith(f"{PLAN}--10-analisis_{PLAN}_cierre_")
    assert slug.endswith(f"--{sha[:16]}.md")
    assert len(slug) == vw.NOMBRE_INSTANEA_MAXIMO, "el recorte cede sitio a la huella, no al reves"


def test_el_nombre_generado_nunca_es_el_README_del_directorio_y_ese_archivo_sigue_intacto(vw, montaje, monkeypatch):
    """El slug no puede producir `README.md` (todo nombre termina en `--<hex>.md`) ni tocar al que ya vive ahi."""
    m = montaje
    for plan, titulo in (("README", "md"), ("readme", "MD"), ("README-", "md")):
        assert vw.slug_de_instantanea(plan, titulo, "a" * 64) != "README.md"
    destino = vw.directorio_de_instantaneas(m["registro"])
    destino.mkdir(parents=True, exist_ok=True)
    readme = destino / "README.md"
    readme.write_bytes(b"prosa humana del directorio\n")
    _subir_explicito(vw, m, QmindFalso([], {}), TITULO_CIERRE, _copia(vw, m, 9, "# cuerpo\n"), monkeypatch)
    assert readme.read_bytes() == b"prosa humana del directorio\n"


def test_la_tabla_puebla_fuente_id_en_la_rama_explicita_y_casa_con_el_censo(vw, montaje, monkeypatch):
    """AC4 (rama `--file`/`--title`): el id sale de la tabla y el censo lo nombra con titulo y sha_metadata."""
    m = montaje
    copia = _copia(vw, m, 4, "# cuerpo con id que capturar\n")
    _subir_explicito(vw, m, QmindFalso([], {}), TITULO_CIERRE, copia, monkeypatch)
    entrada = vw.cargar_registro(m["registro"])["entradas"][-1]
    assert entrada["fuente_id"] and vw.ID_RE.match(entrada["fuente_id"]), "la entrada nace con su id"
    censo = vw.fetch_sources(NB)
    coincidencias = [f for f in censo if f["id"] == entrada["fuente_id"]]
    assert len(coincidencias) == 1
    assert coincidencias[0]["title"] == vw.norm(TITULO_CIERRE)
    assert coincidencias[0]["sha_metadata"] == entrada["sha256"]


def test_la_tabla_puebla_fuente_id_tambien_en_la_rama_por_defecto(vw, montaje, monkeypatch):
    """AC4 (rama historica): la segunda llamada a `publicar_en_registro`, sin titulo ni archivo explicitos."""
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, registro_path=m["registro"],
                             fecha="2026-10-08", repo_root=m["tmp"])
    assert salio == 0, buffer.getvalue()
    entrada = vw.cargar_registro(m["registro"])["entradas"][-1]
    assert entrada["fuente_id"] and vw.ID_RE.match(entrada["fuente_id"]), \
        "la otra rama no puede seguir entregando la cadena vacia"
    assert entrada["titulo"] == TITULO_HISTORICO


def test_tabla_degenerada_declara_id_no_capturado_y_no_invoca_una_segunda_subida(vw, montaje, monkeypatch):
    """AC4 de contencion: sin linea `ID:` el estado publicado es «id no capturado» y el contador es 1.

    La re-subida estaba prohibida y era el camino natural de un parser que aborta: la idempotencia del
    backend es por titulo, asi que re-corregir el parseo creando otra fuente es L-QW.2 consumado. Aqui el
    diente es el conteo de `subidas`, y el censo responde por la fuente ya publicada.
    """
    m = montaje
    copia = _copia(vw, m, 5, "# cuerpo con tabla sin id\n")
    falso = QmindFalso([], {}, respuesta_upload=TABLA_DEGENERADA)
    salida = _subir_explicito(vw, m, falso, TITULO_CIERRE, copia, monkeypatch)
    assert len(falso.subidas) == 1, "una segunda subida ante parseo fallido es el duplicado que DA-CIM.3 prohibe"
    assert "id no capturado" in salida
    assert "[CENSO] la fuente publicada es" in salida, "el censo es la verificacion que sustituye a la tabla"
    assert vw.cargar_registro(m["registro"])["entradas"][-1]["fuente_id"] == ""


def test_una_respuesta_json_no_se_confunde_con_la_tabla(vw, montaje, monkeypatch):
    """El diente contrario del parser: si alguien parseara JSON, aqui habria un id y el estado callaria.

    La respuesta real de `qmind source upload` es la tabla; el doble la imito mal durante toda la vida del
    writer (respondio JSON) y por eso el verde nunca alcanzo la rama (L-T4A.5). Un parser de JSON pasaria
    esta prueba dando por bueno un formato que el servicio no emite.
    """
    m = montaje
    copia = _copia(vw, m, 6, "# cuerpo con respuesta json\n")
    falso = QmindFalso([], {}, respuesta_upload='{"id": "01a0bfc9-5f5a-783e-9492-000000000042"}')
    salida = _subir_explicito(vw, m, falso, TITULO_CIERRE, copia, monkeypatch)
    assert "id no capturado" in salida
    assert "01a0bfc9-5f5a-783e-9492-000000000042" not in str(vw.cargar_registro(m["registro"]))


def test_censo_que_no_responde_es_estado_propio_y_no_re_subida(vw, montaje, monkeypatch):
    """R2.9 en la via nueva: «el censo no respondio» se nombra como lector fallido, no como ausencia (L-PF6)."""
    m = montaje
    copia = _copia(vw, m, 7, "# cuerpo con censo roto\n")
    base = QmindFalso([], {}, respuesta_upload=TABLA_DEGENERADA)
    falso = _CensoSeparado(vw, base, falla=True)
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE, archivo=copia,
                             registro_path=m["registro"], fecha="2026-10-08", repo_root=m["tmp"])
    assert salio == 0, buffer.getvalue()
    salida = buffer.getvalue()
    assert "id no capturado" in salida and "[NO-EVALUABLE] censo" in salida
    assert len(falso.subidas) == 1


def test_censo_que_no_la_ve_nombra_lo_buscado_sin_re_subir(vw, montaje, monkeypatch):
    """Ausencia observada: el censo responde y la fuente no esta; se publica lo buscado, no se sube otra vez."""
    m = montaje
    copia = _copia(vw, m, 8, "# cuerpo ausente del censo\n")
    base = QmindFalso([], {}, respuesta_upload=TABLA_DEGENERADA)
    falso = _CensoSeparado(vw, base, fuentes=[])
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.do_upload(m["plans"] / "Archives" / PLAN, NB, titulo=TITULO_CIERRE, archivo=copia,
                             registro_path=m["registro"], fecha="2026-10-08", repo_root=m["tmp"])
    assert salio == 0, buffer.getvalue()
    assert "[AUSENTE] censo: 0 fuentes" in buffer.getvalue() and TITULO_CIERRE in buffer.getvalue()
    assert len(falso.subidas) == 1


def test_el_parseo_de_tabla_no_confunde_NotebookID_ni_un_valor_que_no_es_uuid(vw):
    """Unidad del parser sobre la forma archivada, con sus trampas: `NotebookID:`, dos puntos del titulo, hueco."""
    tabla = _tabla_de_subida(_id(9), TITULO_HISTORICO, "copia.md")
    assert vw.fuente_id_de_tabla(tabla) == _id(9)
    assert vw.fuente_id_de_tabla(TABLA_DEGENERADA) == ""
    assert vw.fuente_id_de_tabla(f"NotebookID:  {NB}\n") == ""
    assert vw.fuente_id_de_tabla("ID:          no-es-un-uuid\n") == ""
    assert vw.fuente_id_de_tabla("ID:\n") == ""
    assert vw.fuente_id_de_tabla("") == ""
    assert vw.fuente_id_de_tabla(json.dumps({"id": _id(9)})) == ""


# ------------------- FASE-A3 de CURA-INSTRUMENTOS-QMIND-S15: AC5, AC6 y la errata DA-CIM.9

REV_SIN_GUARDA_DE_RUTA = "b32a5ad"
PLAN_RAIZ = "PLAN-EN-RAIZ-2026-10-09"
PLAN_VIEJO = "PLAN-VIEJO-2026-09-02"
PLAN_LOCAL = "PLAN-SIN-INSTANEA-2026-09-03"
TITULO_VIEJO = "10-analisis: PLAN-VIEJO-2026-09-02 (lecciones aprendidas y decisiones)"
TITULO_LOCAL = "10-analisis: PLAN-SIN-INSTANEA-2026-09-03 (lecciones aprendidas y decisiones)"


def _verificar(vw, monkeypatch, m, doble, *extra) -> tuple:
    """Corre `main()` en modo verificacion sobre un doble ya montado: el censo posterior a una publicacion."""
    monkeypatch.setattr(vw, "_run_qmind", doble)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(m["registro"]),
                         *extra])
    return salio, doble, buffer.getvalue()


def _entrada_de_migracion(vw, m, plan: str, titulo: str, contenido: bytes, nombre: str) -> None:
    """Anade al registro una entrada en la forma `1.0` (sin `sha_cuerpo`), con su cuerpo y su instantanea.

    Es montaje, no imitacion del defecto: esa forma existe en `.opencode/qmind-writeback/registro.json` (las
    dos entradas del padre) y asi queda poblada la rama que DA-CIM.9 governaba por separado, sin borrar las
    entradas `1.1` que ya estan en el documento.
    """
    cuerpo = m["plans"] / "Archives" / plan / vw.ANALISIS_FILENAME
    cuerpo.parent.mkdir(parents=True, exist_ok=True)
    cuerpo.write_bytes(contenido)
    destino = vw.directorio_de_instantaneas(m["registro"]) / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    datos = vw.cargar_registro(m["registro"])
    datos["entradas"].append({"plan": plan, "titulo": titulo, "estado": "vigente", "fuente_id": "",
                              "sha256": hashlib.sha256(contenido).hexdigest(), "instanea": nombre,
                              "publicado": "2026-10-07"})
    vw.guardar_registro(m["registro"], datos)


# ------------------------------------------------------------------ AC5: resolucion de rutas fijada por diente


def test_upload_con_prefijo_y_desde_la_raiz_dejan_la_clave_del_directorio_sin_prefijo(vw, montaje, monkeypatch):
    """AC5 en verde: la composicion `plans_dir / argv` ya admite `Archives/` y la clave sigue siendo el nombre.

    La capacidad no la construye esta fase: la fija. Por eso se prueba por `main()`, que es donde vive la
    composicion, y no llamando a `do_upload()` con la ruta ya armada.
    """
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    cuerpo_raiz = m["plans"] / PLAN_RAIZ / "10-analisis-post-implementacion.md"
    cuerpo_raiz.parent.mkdir(parents=True)
    cuerpo_raiz.write_bytes(CUERPO)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        uno = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(m["registro"]),
                       "--upload", f"Archives/{PLAN}"])
        dos = vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(m["registro"]),
                       "--upload", PLAN_RAIZ])
    assert (uno, dos) == (0, 0), buffer.getvalue()
    claves = [e["plan"] for e in vw.cargar_registro(m["registro"])["entradas"]]
    assert claves == [PLAN, PLAN_RAIZ], "la clave es el nombre del directorio, nunca el prefijo"
    assert not any("Archives" in c for c in claves)
    assert [t for t, _ in falso.subidas] == [TITULO_HISTORICO,
                                             f"10-analisis: {PLAN_RAIZ} (lecciones aprendidas y decisiones)"]


def test_upload_sin_prefijo_con_el_plan_archivado_corta_por_la_ruta_y_no_por_la_red(vw, montaje, monkeypatch,
                                                                                   tmp_path):
    """AC5 en rojo y por su causa: la ruta equivocada se dicta antes de preguntar al notebook.

    El control se ejecuta sobre el writer commiteado en `b32a5ad` (tip al abrir esta sesion): alli `main()`
    resolvía el notebook ANTES de componer la ruta, así que un `--upload <PLAN>` con el plan archivado
    respondía el motivo del lector remoto y no la ruta buscada. La guarda nueva se prueba en las dos
    direcciones: el curado nombra la ruta y no llama al servicio, el versionado nombra el servicio.
    """
    m = montaje
    llamadas_nuevas = []

    def sin_servicio_para(mod, llamadas):
        """La excepcion REAL del modulo gobernado: si el doble lanzara otra, el control mediria al doble."""
        def doble(args):
            llamadas.append(args[:2])
            raise mod.QmindUnavailable("el servicio no respondio: esta prueba no puede dictar la ruta por red")
        return doble

    monkeypatch.setattr(vw, "_run_qmind", sin_servicio_para(vw, llamadas_nuevas))
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--plans-dir", str(m["plans"]), "--registro", str(m["registro"]),
                         "--upload", PLAN])
    salida = buffer.getvalue()
    assert salio == 1
    assert "el directorio no existe" in salida and str(m["plans"] / PLAN) in salida
    assert "no respondio" not in salida, "el rojo de la ruta no puede venir disfrazado de fallo de red"
    assert llamadas_nuevas == [], "la guarda local corta antes de la primera llamada remota"
    assert vw.cargar_registro(m["registro"])["entradas"] == []

    viejo = _modulo_versionado(REV_SIN_GUARDA_DE_RUTA, tmp_path / "control", "writer_sin_guarda_de_ruta.py")
    llamadas_viejas = []
    monkeypatch.setattr(viejo, "_run_qmind", sin_servicio_para(viejo, llamadas_viejas))
    buffer_viejo = io.StringIO()
    with redirect_stdout(buffer_viejo):
        salio_viejo = viejo.main(["--plans-dir", str(m["plans"]), "--registro", str(m["registro"]),
                                  "--upload", PLAN])
    salida_viejo = buffer_viejo.getvalue()
    assert salio_viejo == 1
    assert llamadas_viejas == [["notebook", "list"]], \
        "el control perdio su forma: el viejo preguntaba al notebook antes que a la ruta"
    assert "no respondio" in salida_viejo and "el directorio no existe" not in salida_viejo, salida_viejo


def test_cuerpo_del_plan_resuelve_las_dos_raices_y_su_ausencia_no_es_ninguna(vw, montaje):
    """AC5 por el lector: la raiz de planes, la raiz `Archives/` y la ausencia bajo las dos son tres estados."""
    m = montaje
    assert vw.cuerpo_del_plan(PLAN, m["plans"]) == m["cuerpo"], "el plan archivado resuelve bajo Archives/"
    movido = m["plans"] / PLAN_RAIZ / "10-analisis-post-implementacion.md"
    movido.parent.mkdir(parents=True)
    movido.write_bytes(m["cuerpo"].read_bytes())
    m["cuerpo"].unlink()
    assert vw.cuerpo_del_plan(PLAN_RAIZ, m["plans"]) == movido, "el plan en raiz resuelve sin prefijo"
    assert vw.cuerpo_del_plan("PLAN-QUE-NO-EXISTE-2026-09-09", m["plans"]) is None
    m["cuerpo"].write_bytes(movido.read_bytes())
    movido.unlink()
    assert vw.cuerpo_del_plan(PLAN, m["plans"]) == m["cuerpo"]


def test_el_plan_archivado_publicado_por_prefijo_no_abstiene_al_verificador_por_no_resolver(vw, montaje,
                                                                                            monkeypatch):
    """AC5 con los dos modos seguidos: publica por `Archives/<PLAN>` y el dictamen sobre ese plan es medible.

    El rojo que prohibe el mandamiento es el `[NO-EVALUABLE] ... no resuelve bajo` sobre un cuerpo que si
    está: la abstencion tiene que reservarse para la ausencia real (L-PF6, R2.9).
    """
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        assert vw.main(["--nb", NB, "--plans-dir", str(m["plans"]), "--registro", str(m["registro"]),
                        "--upload", f"Archives/{PLAN}"]) == 0
    entrada = vw.cargar_registro(m["registro"])["entradas"][0]
    assert entrada["plan"] == PLAN and entrada["sha_cuerpo"] == hashlib.sha256(CUERPO).hexdigest()
    doble = QmindFalso(list(falso.fuentes), {f["id"]: CUERPO for f in falso.fuentes})
    salio, doble, salida = _verificar(vw, monkeypatch, m, doble)
    assert salio == 0, salida
    assert "no resuelve bajo" not in salida
    assert "[FRESCO]" in salida and "1 dictaminada(s) por cuerpo" in salida
    assert doble.descargas == 1, "ningun verde sale de la metadata sin haber bajado la fuente"


def test_upload_con_ruta_absoluta_bajo_archives_tampoco_escribe_el_prefijo_en_la_clave(vw, montaje, monkeypatch):
    """La otra rama de la composicion: una ruta absoluta no pasa por `--plans-dir` y la clave no se contamina."""
    m = montaje
    falso = QmindFalso([], {})
    monkeypatch.setattr(vw, "_run_qmind", falso)
    monkeypatch.setattr(vw, "scan_context_declarations", lambda: [])
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vw.main(["--nb", NB, "--plans-dir", str(m["plans"] / "esa-raiz-no-existe"),
                         "--registro", str(m["registro"]), "--upload",
                         str(m["plans"] / "Archives" / PLAN)])
    assert salio == 0, buffer.getvalue()
    assert vw.cargar_registro(m["registro"])["entradas"][0]["plan"] == PLAN


# ---------------------------------------------------------- AC6 y DA-CIM.9: la fila huesped en los dos caminos


def test_huespedes_sin_contabilidad_selecciona_por_plan_y_por_titulo_contable(vw, montaje):
    """Unidad del bloque extraido: nombra al plan, es un `10-analisis` y su titulo no esta en el registro."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    datos = vw.cargar_registro(m["registro"])
    huesped = _fuente(_id(50), TITULO_HISTORICO, CUERPO)
    de_otro_plan = _fuente(_id(51), "10-analisis: PLAN-OTRO-2026-09-09 (lecciones)", CUERPO)
    no_es_analisis = _fuente(_id(52), "contexto suelto que nombra al plan sin ser un 10-analisis", CUERPO)
    contable = _fuente(_id(53), TITULO_CIERRE, CUERPO)
    elegidas = vw._huespedes_sin_contabilidad(datos, [huesped, de_otro_plan, no_es_analisis, contable], PLAN)
    assert [f["id"] for f in elegidas] == [huesped["id"]]
    assert vw._huespedes_sin_contabilidad(datos, [], PLAN) == [], "censo vacio: ausencia, no hallazgo"


def test_la_huesped_sin_contabilidad_corta_rojo_sobre_una_entrada_1_0_sin_descargar_nada(vw, montaje,
                                                                                         monkeypatch):
    """Diente (i) de DA-CIM.9: el rojo de contabilidad es alcanzable con un registro que solo tiene `1.0`.

    Antes de la subtarea 3b la guarda de migracion terminaba en `continue` y el bloque huesped no se evaluaba:
    con las dos entradas `1.0` del padre, `[17/18]` quedaba en NO-EVALUABLE sin fecha. Aqui la corrida no
    descarga nada (la vigencia de esa entrada sigue en abstencion) y aun asi imprime el rojo con los tres
    datos que lo dictaminan: id, titulo truncado legible y sha del censo.
    """
    m = montaje
    _entrada_1_0(vw, m, TITULO_CIERRE, CUERPO)
    antes = m["registro"].read_bytes()
    contable = _fuente(_id(40), TITULO_CIERRE, CUERPO)
    huesped = _fuente(_id(41), TITULO_HISTORICO, CUERPO)
    salio, falso, salida = _corrida(vw, monkeypatch, m, [contable, huesped],
                                    {contable["id"]: CUERPO, huesped["id"]: CUERPO})
    assert salio == 1, "el rojo manda sobre la abstencion (contrato D2, R2.9)"
    assert "no grabo sha_cuerpo" in salida and "schema 1.0" in salida, "la abstencion sigue imprimiéndose"
    assert "[DUPLICADO-VIGENTE]" in salida
    assert huesped["id"][:13] in salida and TITULO_HISTORICO[:60] in salida
    assert hashlib.sha256(CUERPO).hexdigest()[:12] in salida, \
        "el sha que se publica es el del censo, no el del registro"
    assert falso.descargas == 0, "la capa D2 no se levanta para una entrada 1.0"
    assert "[VENCIDO]" not in salida and "[FRESCO]" not in salida
    assert m["registro"].read_bytes() == antes, "declarar la huesped no es escribir su contabilidad"


def test_el_rojo_huesped_de_una_entrada_1_1_convive_con_la_abstencion_de_migracion(vw, montaje, monkeypatch):
    """Diente (ii): las dos lineas coexisten y el EXIT es el del rojo, sin pintar de VENCIDO la abstencion.

    El rojo sale de una entrada `1.1`, la abstencion de una `1.0`: asi el diente sobrevive al mutante que
    apaga SOLO la llamada de la rama de migracion (M3), que es lo que exige el prompt.
    """
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    contenido_viejo = CUERPO + b"\nla entrada antigua\n"
    _entrada_de_migracion(vw, m, PLAN_VIEJO, TITULO_VIEJO, contenido_viejo, "instanea-vieja.md")
    vigente = _fuente(_id(42), TITULO_CIERRE, CUERPO)
    huesped = _fuente(_id(43), TITULO_HISTORICO, CUERPO)
    contable_vieja = _fuente(_id(44), TITULO_VIEJO, contenido_viejo)
    salio, _, salida = _corrida(vw, monkeypatch, m, [vigente, huesped, contable_vieja],
                                {vigente["id"]: CUERPO, huesped["id"]: CUERPO,
                                 contable_vieja["id"]: contenido_viejo})
    assert salio == 1
    assert "[DUPLICADO-VIGENTE]" in salida and "no grabo sha_cuerpo" in salida
    assert "[VENCIDO]" not in salida, "el hallazgo no pinta de VENCIDO a la abstencion"
    contador = next(l for l in salida.splitlines() if "[CONTADOR]" in l)
    assert "1+1+0==2" in contador, salida
    assert "1 fuente(s) huesped(s)" in contador


def test_el_contador_sigue_cuadrando_con_la_huesped_fuera_de_la_suma(vw, montaje, monkeypatch):
    """Diente (iii): `cuerpo + migracion + local == N` sigue cerrando aunque haya dos huespedes rojas.

    Si la huesped entrara en la particcion, el literal de la suma dejaria de casar: por eso el diente afirma
    la suma y el recuento de huespedes en la misma linea, con sus dos denominadores separados.
    """
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    viejo = CUERPO + b"\nentrada sin sha_cuerpo\n"
    _entrada_de_migracion(vw, m, PLAN_VIEJO, TITULO_VIEJO, viejo, "instanea-migrada.md")
    local = vw.registrar_publicacion(vw.cargar_registro(m["registro"]), m["registro"], PLAN_LOCAL, TITULO_LOCAL,
                                     m["cuerpo"], "", "2026-10-09", m["cuerpo"])
    (vw.directorio_de_instantaneas(m["registro"]) / local["instanea"]).unlink()
    contable = _fuente(_id(45), TITULO_CIERRE, CUERPO)
    h1 = _fuente(_id(46), f"10-analisis: {PLAN} (otra fuente suelta)", b"# otra\n")
    h2 = _fuente(_id(47), f"10-analisis: {PLAN} (y una tercera)", b"# y otra\n")
    contable_vieja = _fuente(_id(48), TITULO_VIEJO, viejo)
    salio, _, salida = _corrida(vw, monkeypatch, m, [contable, h1, h2, contable_vieja],
                                {contable["id"]: CUERPO, h1["id"]: b"# otra\n", h2["id"]: b"# y otra\n",
                                 contable_vieja["id"]: viejo})
    assert salio == 1
    contador = next(l for l in salida.splitlines() if "[CONTADOR]" in l)
    assert "3 vigente(s)" in contador and "1+1+1==3" in contador, contador
    assert "2 fuente(s) huesped(s)" in contador, contador
    assert "==3; 2" in contador, "la huesped se reporta aparte: nunca entra en la suma de la particion"


def test_la_fuente_del_titulo_reemplazado_no_es_huesped_en_el_camino_de_migracion(vw, montaje, monkeypatch):
    """La contabilidad que ya gobierna AC3 no se re-baja al extraer el bloque: `reemplazada` tambien cuenta.

    Con las dos entradas `1.0` del padre (una vigente y una reemplazada) la corrida tiene que quedar en
    NO-EVALUABLE por migracion, sin rojo: si `registrados` solo mirara las vigentes, la fuente vieja del
    padre se dictaminaria huesped y el rojo de AC6 se mentiria por partida doble.
    """
    m = montaje
    instanea = "instanea-dos-entradas-1-0.md"
    destino = vw.directorio_de_instantaneas(m["registro"]) / instanea
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(CUERPO)
    sha = hashlib.sha256(CUERPO).hexdigest()
    m["registro"].write_text(json.dumps({"schema_version": "1.0", "entradas": [
        {"plan": PLAN, "titulo": TITULO_HISTORICO, "estado": "reemplazada", "reemplazada_por": TITULO_CIERRE,
         "fuente_id": "", "sha256": sha, "instanea": instanea, "publicado": "2026-10-01"},
        {"plan": PLAN, "titulo": TITULO_CIERRE, "estado": "vigente", "fuente_id": "", "sha256": sha,
         "instanea": instanea, "publicado": "2026-10-07"}]}, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8")
    vieja = _fuente(_id(49), TITULO_HISTORICO, CUERPO)
    nueva = _fuente(_id(54), TITULO_CIERRE, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [vieja, nueva],
                               {vieja["id"]: CUERPO, nueva["id"]: CUERPO})
    assert salio == 2, salida
    assert "[DUPLICADO-VIGENTE]" not in salida
    assert "no grabo sha_cuerpo" in salida and "0 fuente(s) huesped(s)" in salida


def test_un_vencido_por_cuerpo_y_una_abstencion_local_dan_exit_1_con_las_dos_lineas(vw, montaje, monkeypatch):
    """R2.9 con la particcion nueva: el rojo manda, la abstencion se nombra y cada una conserva su etiqueta."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    datos = vw.cargar_registro(m["registro"])
    nueva = vw.registrar_publicacion(datos, m["registro"], PLAN_LOCAL, TITULO_VIEJO.replace(PLAN_VIEJO, PLAN_LOCAL),
                                     m["cuerpo"], "", "2026-10-09", m["cuerpo"])
    (vw.directorio_de_instantaneas(m["registro"]) / nueva["instanea"]).unlink()
    m["cuerpo"].write_bytes(CUERPO + b"\neditado tras publicar\n")
    fuente = _fuente(_id(55), TITULO_CIERRE, CUERPO)
    salio, falso, salida = _corrida(vw, monkeypatch, m, [fuente], {fuente["id"]: CUERPO})
    assert salio == 1
    assert "[VENCIDO]" in salida and "sha_cuerpo=" in salida
    assert "[NO-EVALUABLE]" in salida and "la instantanea registrada no esta en" in salida
    assert salida.count("[VENCIDO]") == 1, "la abstencion no se pinta de VENCIDO"
    assert falso.descargas == 0
    assert "1+0+1==2" in next(l for l in salida.splitlines() if "[CONTADOR]" in l)


def test_la_huesped_sin_promesa_de_sha_nombra_su_abstencion_del_dato(vw, montaje, monkeypatch):
    """L-PF6 sobre la linea nueva: sin `metadata.fileSha256` el rojo no miente con un sha vacio."""
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    contable = _fuente(_id(56), TITULO_CIERRE, CUERPO)
    huesped = _fuente_sin_promesa(_id(57), TITULO_HISTORICO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [contable, huesped], {contable["id"]: CUERPO})
    assert salio == 1
    assert "sin-sha-en-el-censo" in salida and huesped["id"][:13] in salida
    assert "con sha_metadata ... nombra" not in salida


def test_el_resumen_lista_la_causa_del_rojo_y_no_inventa_un_vencido(vw, montaje, monkeypatch):
    """AC6 sobre la salida agregada: con DA-CIM.9 landed el unico rojo puede ser de contabilidad.

    La etiqueta vieja del resumen era `"VENCIDO" if codigo == 1`, o sea un nombre fijo para cualquier rojo.
    Desde que la huésped es evaluable sobre una entrada `1.0`, esa salida dictamina un VENCIDO que ninguna
    linea imprimio — y es lo unico que ve quien corre `[17/18]` sin leer el cuerpo del crudo. Dos poblaciones:
    la roja-solo-de-huesped y la de dos causas concurrentes.
    """
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    contable = _fuente(_id(58), TITULO_CIERRE, CUERPO)
    huesped = _fuente(_id(59), TITULO_HISTORICO, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [contable, huesped],
                                {contable["id"]: CUERPO, huesped["id"]: CUERPO})
    assert salio == 1
    assert "contenido: DUPLICADO-VIGENTE" in salida, salida
    assert "contenido: VENCIDO" not in salida, "el resumen no dictamina una causa que la corrida no imprimio"
    assert "[VENCIDO]" not in salida

    contenido_viejo = CUERPO + b"\nel cuerpo del plan viejo\n"
    viejo = m["plans"] / "Archives" / PLAN_VIEJO / vw.ANALISIS_FILENAME
    viejo.parent.mkdir(parents=True, exist_ok=True)
    viejo.write_bytes(contenido_viejo)
    vw.registrar_publicacion(vw.cargar_registro(m["registro"]), m["registro"], PLAN_VIEJO, TITULO_VIEJO,
                             viejo, "", "2026-10-09", viejo)
    m["cuerpo"].write_bytes(CUERPO + b"\nescrito despues de las dos publicaciones\n")
    fuente_a = _fuente(_id(62), TITULO_CIERRE, CUERPO)
    fuente_vieja = _fuente(_id(64), TITULO_VIEJO, contenido_viejo)
    huesped_vieja = _fuente(_id(63), f"10-analisis: {PLAN_VIEJO} (otra fuente suelta)", contenido_viejo)
    salio2, _, salida2 = _corrida(vw, monkeypatch, m, [fuente_a, fuente_vieja, huesped_vieja],
                                  {fuente_a["id"]: CUERPO, fuente_vieja["id"]: contenido_viejo,
                                   huesped_vieja["id"]: contenido_viejo})
    assert salio2 == 1
    assert "contenido: VENCIDO+DUPLICADO-VIGENTE" in salida2, salida2
    assert "[VENCIDO]" in salida2 and "[DUPLICADO-VIGENTE]" in salida2
    contador2 = next(l for l in salida2.splitlines() if "[CONTADOR]" in l)
    assert "2+0+0==2" in contador2 and "1 fuente(s) huesped(s)" in contador2, contador2


def test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado(vw, montaje,
                                                                                          monkeypatch):
    """Caracterizacion del limite que deja DA-CIM.9, con su dueno: la concurrence no se gobierna aqui.

    El bloque huesped vive al final del bucle y la puerta de vigencia termina en `continue`, asi que una
    entrada `1.0` y una `1.1` VENCIDA son dos casos distintos: la primera ya evalua a su huesped (subtarea 3b)
    y la segunda no. La especificacion del operador del 2026-10-08 recorto la cura a la rama de migracion y no
    abrio los demas `continue`, asi que este diente **aserta el comportamiento vigente** y se pone rojo el dia
    que un AC gobierne la concurrence (deuda S-CIM-9 del maestro §5, dueño operador).
    """
    m = montaje
    _publicar(vw, m, TITULO_CIERRE)
    m["cuerpo"].write_bytes(CUERPO + b"\neditado despues de publicar\n")
    contable = _fuente(_id(60), TITULO_CIERRE, CUERPO)
    huesped = _fuente(_id(61), TITULO_HISTORICO, CUERPO)
    salio, _, salida = _corrida(vw, monkeypatch, m, [contable, huesped],
                                {contable["id"]: CUERPO, huesped["id"]: CUERPO})
    assert salio == 1
    assert "[VENCIDO]" in salida and "sha_cuerpo=" in salida
    assert "[DUPLICADO-VIGENTE]" not in salida, "limite vigente: el continue de vigencia no llega a la huesped"
    assert "0 fuente(s) huesped(s)" in salida
    assert "contenido: VENCIDO" in salida, "la etiqueta lista solo las causas que se imprimieron"
