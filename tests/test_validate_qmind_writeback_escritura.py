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
    """

    def __init__(self, fuentes: list, contenidos: dict, motivo: str | None = None,
                 excepcion: type | None = None):
        self.fuentes = fuentes
        self.contenidos = contenidos
        self.motivo = motivo
        self.excepcion = excepcion
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
            return 0, json.dumps({"id": ident})
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
    """Deja en el registro una publicacion vigente de `titulo`, con su instantanea copiada al montaje."""
    datos = vw.cargar_registro(m["registro"])
    return vw.registrar_publicacion(datos, m["registro"], PLAN, titulo,
                                    archivo or m["cuerpo"], "", "2026-10-07")


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
    vw.registrar_publicacion(datos, m["registro"], PLAN, TITULO_CIERRE, m["cuerpo"], "", "2026-10-07")
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
                             "10-analisis: PLAN-B (cierre)", m["cuerpo"], "", "2026-10-07")
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
