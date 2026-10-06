"""Tests de `scripts/verify_qmind_context_freshness.py` (S34, fila 11 del registro del 2026-09-29).

El criterio que se prueba es **descarga + sha256 contra el archivo gobernado, nunca por titulo**;
`metadata.fileSha256` es corroboracion. La fila nace de que el verificador hermano
(`validate_qmind_writeback.py`) audita los `10-analisis` y decide por titulo, asi que su `13/13` convivio
nueve dias con un `CONTEXT` vencido sin decir nada (RI §6).

No hay red: se sustituye la unica frontera de E/S del CLI (`_run_qmind`) por un doble que responde los
mismos comandos y escribe los mismos archivos. Todo lo demas —parseo del JSON, resolucion del notebook,
el `-o` de la descarga, la poblacion, el barrido completo y los codigos de salida— es codigo real. El doble
reproduce el limite medido del listado: las fuentes vienen bajo la clave `sources` y con `--all` el
`totalSize` vuelve 0.

El anclaje del control negativo es una **revision publicada fija** (`7737347`), nunca HEAD.

Un detalle de aislamiento que hace que los rojos signifiquen lo que dicen: cada prueba de criterio usa un
contexto con **un solo** archivo gobernado. Con dos, el que no tiene fuente publicada pone rojo el resultado
entero y un verde de mas o de menos no se atribuiria al miembro que se estaba midiendo (la familia de «el
primer rojo oculta el resto del test»).
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_qmind_context_freshness.py"
REV_HERMANO_VERSIONADO = "7737347"
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"

# Revision publicada y fija del cierre documental de FASE-B: su `verify_qmind_context_freshness.py` ya tenia
# el criterio de bytes, pero su poblacion era solo `CONTEXT-*`. El control negativo se ancla aqui, nunca a
# HEAD (HEAD es el arbol que esta prueba ayuda a cambiar).
REV_SIN_POBLACION_DECLARADA = "6cdb430"
DEFAULT_PLANS = ROOT / ".opencode" / "plans"
# El literal del fixture esta aqui a proposito y se contrasta contra el modulo en cada corrida: si la
# declaracion del guion se mueve, el fixture dejo de montar lo que el guion goberna y el verde diria otra
# cosa (las cotas que crea una prueba se declaran).
REL_DECLORADO = "Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/10-analisis-post-implementacion.md"
PLAN_10_ANALISIS = DEFAULT_PLANS / REL_DECLORADO

UNO = "CONTEXT-UNO-2026-09-21.md"
DOS = "CONTEXT-DOS-2026-09-20.md"
SIN_DECLARAR = "CONTEXT-SIN-DECLARAR-2026-09-19.md"
CONGELADO = "CONTEXT-CONGELADO-2026-08-01.md"


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    antes = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


@pytest.fixture
def vq():
    mod = _cargar("vq_fresco", SCRIPT)
    # El literal con el que los fixtures montan la poblacion declarada tiene que ser el que el guion
    # goberna; se comprueba en TODA corrida de esta familia, no solo en la prueba de la declaracion.
    _afirmar_rel_comun(mod)
    return mod


class QmindFalso:
    """Responde `notebook list`, `source list` y `source download` sobre datos en memoria.

    `descargas` cuenta las bajadas: es como se prueba el barrido completo antes de decir `VENCIDO` y como
    se corta un verde que pasaria sin haber bajado nada.
    """

    def __init__(self, fuentes: list[dict], contenidos: dict[str, bytes], motivo: str | None = None,
                 excepcion: type | None = None):
        self.fuentes = fuentes
        self.contenidos = contenidos
        self.descargas = 0
        self.motivo = motivo
        # `_run_qmind` real convierte el shim no resuelto en `QmindNoDisponible`; el doble tiene que
        # propagar lo mismo, o la prueba mediria al doble y no al camino de degradacion del guion.
        self.excepcion = excepcion

    def __call__(self, args: list[str]) -> tuple[int, str]:
        if self.motivo:
            raise self.excepcion(self.motivo)
        if args[:2] == ["notebook", "list"]:
            return 0, json.dumps({"notebooks": [{"id": NB, "title": "iah-cli-lecciones"}]})
        if args[:2] == ["source", "list"]:
            return 0, json.dumps({"sources": self.fuentes, "totalSize": 0, "currentPage": 0})
        if args[:2] == ["source", "download"]:
            source_id = args[args.index("--nb") + 2]   # despues del id del notebook
            destino = Path(args[args.index("-o") + 1])
            self.descargas += 1
            if source_id not in self.contenidos:
                return 1, "fuente sin archivo original"
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(self.contenidos[source_id])
            return 0, f"Downloaded {destino} ({len(self.contenidos[source_id])} bytes)"
        return 1, "comando no esperado"


def _fuente(source_id: str, titulo: str, contenido: bytes, metadata: bool = True) -> dict:
    return {"id": source_id, "title": titulo, "status": "ready",
            "metadata": ({"fileSha256": hashlib.sha256(contenido).hexdigest()}
                         if metadata else {})}


def _contexto(tmp_path: Path, dos: bool = False) -> tuple[Path, Path]:
    """(context_dir, plans_dir). Con `dos=False` hay UN solo gobernado, para poder atribuir el rojo."""
    contexto = tmp_path / "context"
    (contexto / "Historico").mkdir(parents=True)
    (contexto / UNO).write_text(
        "# Contexto uno\n\n## Leccion durable: un archivado vence tambien los CONTEXT\n",
        encoding="utf-8", newline="\n")
    (contexto / SIN_DECLARAR).write_text("# Contexto\n\nnada que declarar aqui\n",
                                         encoding="utf-8", newline="\n")
    (contexto / "Historico" / CONGELADO).write_text(
        "# Contexto\n\n## Leccion durable: congelado por R2.5\n", encoding="utf-8", newline="\n")
    if dos:
        (contexto / DOS).write_text(
            "# Contexto dos\n\nLeccion de forma: la pertinencia no se infiere\n",
            encoding="utf-8", newline="\n")
    plans = tmp_path / "plans"
    (plans / "Archives").mkdir(parents=True)
    return contexto, plans


def _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes, contenidos, *extra) -> tuple:
    falso = QmindFalso(fuentes, contenidos)
    monkeypatch.setattr(vq, "_run_qmind", falso)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vq.main(["--context-dir", str(contexto), "--plans-dir", str(plans), *extra])
    return salio, falso, buffer.getvalue()


# --------------------------------------------------------------------------------- la poblacion

def test_la_poblacion_es_declarados_mas_citados_y_sus_exclusiones_se_publican(vq, tmp_path):
    contexto, plans = _contexto(tmp_path, dos=True)
    gobernados, excluidos = vq.poblacion_del_context(contexto, plans)
    assert sorted(g.name for g in gobernados) == sorted([UNO, DOS]), [g.name for g in gobernados]
    assert {r.name for r, _ in excluidos} == {SIN_DECLARAR, CONGELADO}
    razones = {r.name: razon for r, razon in excluidos}
    assert "Historico" in razones[CONGELADO]
    assert "no autodeclara" in razones[SIN_DECLARAR]


def test_las_dos_grafias_de_autodeclaracion_se_ven(vq, tmp_path):
    """Encabezado (`## Leccion durable:`) y linea suelta (`Leccion de forma:`).

    La copia del hermano ancla solo la segunda, y asi perdio al CONTEXT de JEV (medido 2026-09-27).
    """
    contexto, _ = _contexto(tmp_path, dos=True)
    assert vq.declara_durable(contexto / UNO) is True
    assert vq.declara_durable(contexto / DOS) is True
    assert vq.declara_durable(contexto / SIN_DECLARAR) is False


def test_control_negativo_el_hermano_versionado_no_ve_el_contexto_de_encabezado(tmp_path):
    """El write-back commiteado en `7737347` devuelve 0 declaraciones sobre el MISMO arbol.

    Se lee y se ejecuta el hermano versionado (`git show`, solo lectura): no es una parodia dentro del
    test. Su marcador ancla a inicio de linea y el artefacto lo escribe como encabezado, que es el hueco
    medido el 2026-09-27 y la razon por la que este verificador es un guion propio y no una extension.
    """
    proc = subprocess.run(["git", "show", f"{REV_HERMANO_VERSIONADO}:scripts/validate_qmind_writeback.py"],
                          capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:200]
    assert '"^Leccion de forma:"' in proc.stdout.replace("'", '"') or "^Lecci" in proc.stdout, (
        "el hermano ya no ancla a inicio de linea: re-leer el control antes de afirmar que era ciego")
    destino = tmp_path / "hermano_versionado.py"
    destino.write_text(proc.stdout, encoding="utf-8", newline="\n")
    hermano = _cargar("hermano_wb", destino)

    contexto, _ = _contexto(tmp_path / "h", dos=True)
    hermano.ROOT_DIR = ROOT          # el guion versionado resuelve sus rutas por su propio __file__
    declarado_por_el_hermano = {ruta.name for ruta, _ in hermano.scan_context_declarations()}
    assert declarado_por_el_hermano == set(), (
        f"el hermano ya ve los CONTEXT declarados ({declarado_por_el_hermano}): el control perdio su "
        "premissa y hay que re-redactarlo")

    nuevo = _cargar("vq_contra_hermano", SCRIPT)
    planes = tmp_path / "plans" / "Archives"
    vistos = {g.name for g in nuevo.poblacion_del_context(contexto, tmp_path / "h" / "plans")[0]}
    assert UNO in vistos, (
        "el verificador nuevo tampoco lo ve: ya no hay differential y el control no afirma nada")


def test_los_context_que_cita_un_plan_archivado_entran_en_poblacion(vq, tmp_path):
    contexto, plans = _contexto(tmp_path)
    plan = plans / "Archives" / "PLAN-FT-2026-09-10"
    plan.mkdir(parents=True)
    (plan / "10-analisis-post-implementacion.md").write_text(
        f"Se capitalizo de `{SIN_DECLARAR[:-3]}`, que no declara pero el plan cita.\n", encoding="utf-8")
    gobernados, _ = vq.poblacion_del_context(contexto, plans)
    assert SIN_DECLARAR in [g.name for g in gobernados], [g.name for g in gobernados]


def test_una_cita_no_arrastra_al_historico(vq, tmp_path):
    """La cita de un plan resuelve solo dentro de `context_dir`: `Historico/` sigue congelado."""
    contexto, plans = _contexto(tmp_path)
    plan = plans / "Archives" / "PLAN-FT-2-2026-09-10"
    plan.mkdir(parents=True)
    (plan / "10-analisis-post-implementacion.md").write_text(f"cita a {CONGELADO[:-3]}\n",
                                                              encoding="utf-8")
    gobernados, excluidos = vq.poblacion_del_context(contexto, plans)
    assert CONGELADO not in [g.name for g in gobernados]
    assert CONGELADO in {r.name for r, _ in excluidos}


# --------------------------------------------------------------------- el criterio: bytes, no titulo

def test_fresco_cuando_una_bajada_casa_aunque_el_titulo_no_lo_nomvre(vq, monkeypatch, tmp_path):
    """Fuente publicada con titulo que NO nombra el archivo, pero bytes identicos: FRESCO.

    Si el criterio fuera el titulo, este caso daria VENCIDO. Es la mitad dura de la decision.
    """
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000001"
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                    [_fuente(sid, "Apunte suelto del cierre", disco)],
                                    {sid: disco})
    assert salio == 0, salida
    assert "[FRESCO]" in salida, salida
    assert falso.descargas >= 1, "el verde salio sin descargar nada: el criterio no se ejercito"


def test_vencido_cuando_ninguna_bajada_casa_y_el_barrido_es_completo(vq, monkeypatch, tmp_path):
    """Titulo que lo nombra + bytes que no casan = VENCIDO, habiendo examinado TODAS las fuentes."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    viejo = disco + b"\n(version anterior al git mv, sin el segmento Archives/)\n"
    a = "01a0ffff-0000-7000-8000-000000000002"
    b = "01a0ffff-0000-7000-8000-000000000003"
    fuentes = [_fuente(a, f"CONTEXT: {UNO[:-3]}", viejo), _fuente(b, "otra fuente", b"nada que ver")]
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes,
                                    {a: viejo, b: b"nada que ver"})
    assert salio == 1, salida
    assert "[VENCIDO]" in salida, salida
    assert "barrido completo" in salida, salida
    assert falso.descargas == len(fuentes), (
        f"el VENCIDO se dijo con {falso.descargas} bajadas sobre {len(fuentes)} fuentes: goberno el "
        "titulo, no los bytes")


def test_la_forma_original_mas_cierre_es_legal(vq, monkeypatch, tmp_path):
    """Dos fuentes que nombran al mismo CONTEXT, una vencida y otra fresca: FRESCO, no gemelo.

    Es la decision del operador del 2026-09-29: la re-ingesta con titulo nuevo no borra la anterior. El
    verificador no puede exigir «una sola fuente por stem».
    """
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    vencido = disco + b"\n(segmento Archives/ movido)\n"
    viejo_id, nuevo_id = ("01a0ffff-0000-7000-8000-000000000010",
                          "01a0ffff-0000-7000-8000-000000000011")
    fuentes = [_fuente(viejo_id, f"CONTEXT: {UNO[:-3]}", vencido),
               _fuente(nuevo_id, f"CONTEXT: {UNO[:-3]} (cierre 2026-09-29)", disco)]
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes,
                                    {viejo_id: vencido, nuevo_id: disco})
    assert salio == 0, salida
    assert "[FRESCO]" in salida and "1 fuente(s) que casan" in salida, salida
    assert "barrido completo" not in salida, (
        "corrio barrido completo teniendo dos fuentes que nombran al stem: " + salida)
    assert falso.descargas == 1, (
        f"bajo {falso.descargas} fuentes: D2 (2026-10-05) concentra la bajada en la fuente cuya promesa "
        "hay que verificar. La vencida queda descartada por SU PROPIO metadata, que es un sha de bytes y "
        "no un titulo; la mitad que se conserva del contrato viejo es que sigue habiendo UNA bajada real "
        "(la de arriba: '1 fuente(s) que casan' sale de la verificacion, no del indice). Que se siga "
        "examinando el barrido cuando ninguna metadata casa lo goberna "
        "test_sin_metadata_publicada_el_camino_de_descarga_sigue_vivo y "
        "test_vencido_cuando_ninguna_bajada_casa_y_el_barrido_es_completo")


def test_metadata_no_es_el_criterio(vq, monkeypatch, tmp_path):
    """`metadata.fileSha256` que casa con el disco pero cuya descarga NO: sigue cortando.

    Si el verificador admitiera el metadata como prueba, el `--upload` que responde `[SKIP]` por titulo
    volveria a dejar la version vieja como verdad publicada sin decir nada (RI §13).

    Desde D2 (2026-10-05) la etiqueta de este rojo es `[PROMESA-ROTA]` y no `[VENCIDO]`, y la asercion
    sigue siendo la misma: `salio == 1` con al menos una descarga real. Lo que se prueba aqui no es el
    nombre del rojo sino que **la metadata sola nunca aprueba**.
    """
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000020"
    fuentes = [{"id": sid, "title": f"CONTEXT: {UNO[:-3]}", "status": "ready",
                "metadata": {"fileSha256": hashlib.sha256(disco).hexdigest()}}]
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes,
                                    {sid: b"el notebook guarda otra cosa"})
    assert salio == 1, salida
    assert falso.descargas >= 1, "sin descarga no hay decision que valga"


def test_el_desacuerdo_del_metadata_se_declara_no_se_calla(vq, monkeypatch, tmp_path):
    """Descarga que casa y metadata que no: FRESCO, con el desacuerdo escrito en la salida."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000030"
    fuentes = [{"id": sid, "title": f"CONTEXT: {UNO[:-3]}", "status": "ready",
                "metadata": {"fileSha256": "0" * 64}}]
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes, {sid: disco})
    assert salio == 0, salida
    assert "DESACUERDO" in salida, salida


# --------------------------------------------------------------------------------- los tri-estados

def test_gobernado_que_desaparece_del_disco_es_no_evaluable(vq, monkeypatch, tmp_path):
    """Salida 2 si el gobernado ya no existe: no es rojo del notebook ni verde propio."""
    contexto, plans = _contexto(tmp_path)
    objetivo = contexto / UNO
    fuentes = [_fuente("01a0ffff-0000-7000-8000-000000000040", "nada", b"nada")]

    def censo_que_ya_no_ve_disco(context_dir, plans_dir):
        """El censo nombra al gobernado y el disco ya no lo tiene: la carrera que la fila describe.

        No invoca a `poblacion_del_context` del modulo: ese atributo esta parcheado y llamarlo
        recursionaria sobre si mismo (medido: RecursionError en la primera version del control).
        """
        assert objetivo.is_file(), "premissa: el gobernado tiene que existir antes de borrarse"
        objetivo.unlink()
        return [objetivo], []

    monkeypatch.setattr(vq, "_run_qmind",
                        QmindFalso(fuentes, {"01a0ffff-0000-7000-8000-000000000040": b"nada"}))
    monkeypatch.setattr(vq, "poblacion_del_context", censo_que_ya_no_ve_disco)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vq.main(["--context-dir", str(contexto), "--plans-dir", str(plans), "--quiet"])
    assert salio == 2, buffer.getvalue()
    assert "NO-EVALUABLE" in buffer.getvalue(), buffer.getvalue()


def test_poblacion_vacia_con_ficheros_presentes_no_es_verde(vq, monkeypatch, tmp_path):
    """Si desaparecen las declaraciones, el check se declara NO-EVALUABLE: no aprueba en silencio."""
    contexto = tmp_path / "context"
    contexto.mkdir(parents=True)
    (contexto / "CONTEXT-SIN-NADA-2026-09-01.md").write_text("# nada\n", encoding="utf-8")
    plans = tmp_path / "plans"
    (plans / "Archives").mkdir(parents=True)
    monkeypatch.setattr(vq, "_run_qmind", QmindFalso([], {}))
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        salio = vq.main(["--context-dir", str(contexto), "--plans-dir", str(plans), "--quiet"])
    assert salio == 2, buffer.getvalue()


def test_sin_qmind_degrada_a_warn_y_strict_corta(vq, monkeypatch, tmp_path):
    """El mismo fallback (:468) del hermano: sin CLI no hay rojo; con `--strict` si lo hay."""
    contexto, plans = _contexto(tmp_path)
    falso = QmindFalso([], {}, motivo="shim .CMD no resuelto", excepcion=vq.QmindNoDisponible)
    monkeypatch.setattr(vq, "_run_qmind", falso)
    assert vq.main(["--context-dir", str(contexto), "--plans-dir", str(plans), "--quiet"]) == 0
    assert vq.main(["--context-dir", str(contexto), "--plans-dir", str(plans), "--quiet",
                    "--strict"]) == 1


def test_un_id_que_no_es_uuid_no_llega_al_cli(vq, monkeypatch, tmp_path):
    """Los ids que entran al comando salen del listado y se validan: nada se interpola crudo."""
    llamado: list[list[str]] = []

    def espia(args):
        llamado.append(list(args))
        if args[:2] == ["notebook", "list"]:
            return 0, json.dumps({"notebooks": [{"id": NB, "title": "iah-cli-lecciones"}]})
        return 0, json.dumps({"sources": []})

    monkeypatch.setattr(vq, "_run_qmind", espia)
    with pytest.raises(vq.QmindNoDisponible):
        vq.listar_fuentes("01a04d98 - o algo; rm -rf /")
    assert [a for a in llamado if a[:2] == ["source", "list"]] == [], (
        "se llamo al CLI con un id no validado")
    assert vq.resolver_notebook(NB) == NB


# ------------------------------------------------------------------ la interfaz y el cableado real

def test_la_interfaz_publica_poblacion_exclusiones_y_estado(vq, monkeypatch, tmp_path):
    contexto, plans = _contexto(tmp_path, dos=True)
    uno = (contexto / UNO).read_bytes()
    dos = (contexto / DOS).read_bytes()
    a, b = "01a0ffff-0000-7000-8000-000000000060", "01a0ffff-0000-7000-8000-000000000061"
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                [_fuente(a, f"CONTEXT: {UNO[:-3]}", uno),
                                 _fuente(b, f"CONTEXT: {DOS[:-3]}", dos)], {a: uno, b: dos})
    assert salio == 0, salida
    assert "poblacion: 2 CONTEXT gobernado(s)" in salida, salida
    assert "2 excluido(s)" in salida, salida
    assert "notebook iah-cli-lecciones: 2 fuente(s) publicada(s)" in salida, salida
    assert salida.count("[FRESCO]") == 2, salida
    assert "[OK] frescura de CONTEXT" in salida, salida


def test_el_check_queda_cableado_al_modo_completo_y_no_al_rapido():
    """Decision de la orden: necesita red, y el rapido tiene que seguir corriendo offline.

    Leido de la estructura del runner, no de una cota magicada: los invocadoes antes de
    `if not self.quick:` son el rapido y los del bloque son las exclusivas del completo.
    """
    src = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
    cuerpo = src.split("    def run_all(self) -> bool:", 1)[1]
    rapido, _, completo = cuerpo.partition("        if not self.quick:")
    assert "self._check_context_freshness()" in completo, (
        "el check nuevo no esta en las exclusivas del modo completo: o se cableo al rapido (prohibido "
        "por decision) o no corre")
    assert "self._check_context_freshness()" not in rapido
    assert "verify_qmind_context_freshness.py" in src


def test_la_guarde_del_denominador_sigue_cerrando_la_renumeracion():
    """17→18: los literales de etiqueta del completo tienen que casar con el TOTAL dinamico.

    Es la guarda de §S21/D-a, no un pin suelto: se leen las etiquetas del archivo y se compara contra el
    numero de checks que el runner ejecuta en cada modo.
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    mod = _cargar("rav_denominador", ROOT / "scripts" / "run_all_validations.py")
    runner = mod.ValidationRunner()
    rapido, completo = runner._orden_del_modo()
    assert len(rapido) == 13, f"el rapido dejo de tener 13: {len(rapido)}"
    assert len(completo) == 18, f"el completo no llego a 18: {len(completo)}"
    assert completo[-1] == "self._check_context_freshness", (
        f"el check nuevo no es el ultimo del completo: {completo[-3:]}")


# =============================================================== la poblacion declarada (FILA 4, 2026-10-04)
#
# El gobernado nuevo NO es un `CONTEXT-*` autodeclarado: entra por `POBLACION_DECLARADA`, con su ruta bajo
# `--plans-dir` y el prefijo de titulo con el que se buscan sus candidatas. El criterio sigue siendo
# descarga + sha256 por bytes. Lo que se prueba aqui es la poblacion nueva y el recorte de la bajada, y que
# el viejo `10-analisis` del hermano (que decide por titulo) pueda seguir conviviendo con un cuerpo vencido.

DECLORADO_NOMBRE = "10-analisis-post-implementacion.md"


def _afirmar_rel_comun(vq) -> str:
    """La declaracion del guion y la del fixture tienen que ser la misma ruta, o nada prueba nada."""
    assert len(vq.POBLACION_DECLARADA) == 1, (
        f"la poblacion declarada dejo de ser una entrada ({len(vq.POBLACION_DECLARADA)}): los fixtures de "
        "esta familia montan una sola, re-leerlos antes de tocar esta cota")
    assert vq.POBLACION_DECLARADA[0]["rel"] == REL_DECLORADO, (
        f"el guion declara {vq.POBLACION_DECLARADA[0]['rel']!r} y el fixture monta {REL_DECLORADO!r}")
    return REL_DECLORADO


def _contexto_vacio(tmp_path: Path) -> Path:
    """Raiz de CONTEXT sin autodeclaraciones: el unico gobernado que queda es el declarado."""
    contexto = tmp_path / "context"
    contexto.mkdir(parents=True, exist_ok=True)
    return contexto


def _plans_con_declorado(tmp_path: Path, contenido: bytes, *, con_plan: bool = True) -> Path:
    """`plans/Archives/<PLAN>/10-analisis-post-implementacion.md` montado en tmp con el cuerpo que se diga."""
    plans = tmp_path / "plans"
    destino = plans / REL_DECLORADO
    if not con_plan:
        (plans / "Archives").mkdir(parents=True, exist_ok=True)
        return plans
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(contenido)
    return plans


def _rev_existe(rev: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(ROOT), capture_output=True,
    ).returncode == 0


def _correr(mod, contexto: Path, plans: Path, fuentes: list, contenidos: dict) -> tuple[int, str]:
    """`main()` del modulo dado con el doble de E/S montado: sirve para el actual y para el versionado.

    El doble se instala sobre el modulo que se va a correr, asi el diferencial no compara dos
    implementaciones del arnes sino la MISMA frontera sustituida en dos copias del mismo guion.
    """
    falso = QmindFalso(fuentes, contenidos)
    anterior = mod._run_qmind
    mod._run_qmind = falso
    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            salio = mod.main(["--context-dir", str(contexto), "--plans-dir", str(plans)])
    finally:
        mod._run_qmind = anterior
    return salio, buffer.getvalue()


CUERPO_DECLORADO = b"# 10-analisis del piloto JEV\n\n## 3. Lecciones\n\ncuerpo vigente 2026-10-04\n"
CUERPO_PUBLICADO_VIEJO = CUERPO_DECLORADO + b"\n(snapshot ingested 2026-09-27, sin el cierre de FASE-B)\n"


def test_la_poblacion_declorada_resuelve_bajo_plans_dir_y_declara_su_identificacion(vq, tmp_path):
    plans = _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    resueltos, fuera = vq.poblacion_declorada(plans)
    assert fuera == [], fuera
    assert [r["ruta"].name for r in resueltos] == [DECLORADO_NOMBRE], resueltos
    assert resueltos[0]["criterio"] == "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21", (
        "el prefigo con el que se recorta la bajada cambio de forma: la seleccion de candidatas deja de "
        "ser la que se pruebo")
    assert resueltos[0]["ruta"] == plans / _afirmar_rel_comun(vq), (
        "la ruta gobernada no es la declarada bajo --plans-dir: el diente gobernaria otra raiz")
    assert "01a04d98" in resueltos[0]["identificacion"], (
        "la declaracion dice como identificar la fuente, pero ya no nombra el notebook")


def test_un_plan_que_no_esta_en_esta_raiz_se_publica_fuera_de_alcance_no_se_calla(vq, tmp_path):
    plans = _plans_con_declorado(tmp_path, CUERPO_DECLORADO, con_plan=False)
    resueltos, fuera = vq.poblacion_declorada(plans)
    assert resueltos == []
    assert [rel for rel, _ in fuera] == [_afirmar_rel_comun(vq)], fuera
    assert "--plans-dir" in fuera[0][1], fuera[0][1]


def test_el_arbol_real_goberna_el_10_analisis_del_plan_jev(vq):
    """El residuo anclado al arbol: sin red, el declarado resuelve y su archivo existe.

    Un `git mv` del plan, un renombre del `10-analisis` o una segunda entrada declarada mueven esta linea;
    por eso se mide aqui y no dentro de un fixture.
    """
    resueltos, fuera = vq.poblacion_declorada(DEFAULT_PLANS)
    assert fuera == [], fuera
    assert [r["ruta"] for r in resueltos] == [PLAN_10_ANALISIS], (
        f"la poblacion declarada del arbol ya no es el 10-analisis del JEV: {resueltos}")
    assert PLAN_10_ANALISIS.is_file(), (
        f"el archivo declarado no esta en el arbol: {PLAN_10_ANALISIS}")


def test_vencido_por_bytes_aunque_la_fuente_lo_nombre_por_prefijo(vq, monkeypatch, tmp_path):
    """El caso de la fila 4: publicacion del 2026-09-27 con cuerpo anterior y disco del 2026-10-04."""
    contexto, plans = _contexto_vacio(tmp_path), _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    sid = "01a0ffff-0000-7000-8000-000000000100"
    titulo = (f"{vq.POBLACION_DECLARADA[0]['criterio_titulo']} (cierre offline, lecciones finales "
              "2026-09-27)")
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                   [_fuente(sid, titulo, CUERPO_PUBLICADO_VIEJO)],
                                   {sid: CUERPO_PUBLICADO_VIEJO})
    assert salio == 1, salida
    assert f"[VENCIDO] {DECLORADO_NOMBRE} ({_afirmar_rel_comun(vq)})" in salida, salida
    assert "barrido completo" in salida, salida
    assert "ninguna de 1 fuente(s) examinada(s) casa" in salida, (
        "el VENCIDO no publica cuantas fuentes se examinaron: " + salida)
    assert "sha_disco=" in salida, salida
    assert falso.descargas == 1, (
        f"se bajaron {falso.descargas} fuentes habiendo solo una en el notebook: el recorte no goberno")


def test_fresco_cuando_la_fuente_declorada_casa_y_no_hace_falta_barrer(vq, monkeypatch, tmp_path):
    """La mitad que falta: con el prefijo que casa por bytes se baja UNA fuente y no las 56.

    Sin este control, un `criterio` que recortara mal (por ejemplo el stem del archivo, que no aparece en
    el titulo publicado) daria igualmente VERDE tras un barrido completo: el verde seria caro, no falso.
    Este control es el que distingue las dos cosas.
    """
    contexto, plans = _contexto_vacio(tmp_path), _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    bueno = "01a0ffff-0000-7000-8000-000000000101"
    decoy = "01a0ffff-0000-7000-8000-000000000102"
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                   [_fuente(bueno, "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 "
                                                   "(cierre 2026-10-04)", CUERPO_DECLORADO),
                                    _fuente(decoy, "Otra fuente del mismo plan", b"cuerpo ajeno")],
                                   {bueno: CUERPO_DECLORADO, decoy: b"cuerpo ajeno"})
    assert salio == 0, salida
    assert "[FRESCO]" in salida and "barrido completo" not in salida, salida
    assert falso.descargas == 1, (
        f"bajo {falso.descargas}: el recorte por prefijo no goberno la bajada del declarado")


def test_un_titulo_sin_prefijo_tambien_se_examina_por_bytes(vq, monkeypatch, tmp_path):
    """El prefijo recorta, nunca decide: titulo irreconocible + bytes que casan = FRESCO.

    Re-anclado por D2 (2026-10-05): la ruta cambio (la declaracion del servidor concentra la bajada), el
    veredicto no. La ruta de barrido sigue gobernada por
    `test_sin_metadata_publicada_el_camino_de_descarga_sigue_vivo`.
    """
    contexto, plans = _contexto_vacio(tmp_path), _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    sid = "01a0ffff-0000-7000-8000-000000000103"
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                [_fuente(sid, "Snapshot del cierre sin prefijo alguno",
                                         CUERPO_DECLORADO)],
                                {sid: CUERPO_DECLORADO})
    assert salio == 0, salida
    assert "[FRESCO]" in salida, salida
    assert "metadata del servidor" in salida, (
        "el titulo irreconocible dejo de resolverse por bytes: " + salida)


def test_el_declorado_vencido_corta_rojo_aunque_el_context_este_fresco(vq, monkeypatch, tmp_path):
    """Las dos poblaciones alimentan el MISMO exit code: una no puede tapar a la otra."""
    contexto, _ = _contexto(tmp_path)
    plans = _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    ctx_bytes = (contexto / UNO).read_bytes()
    viejo = "01a0ffff-0000-7000-8000-000000000104"
    ctx_fresco = "01a0ffff-0000-7000-8000-000000000105"
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                [_fuente(ctx_fresco, f"CONTEXT: {UNO[:-3]}", ctx_bytes),
                                 _fuente(viejo, "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (v0)",
                                         CUERPO_PUBLICADO_VIEJO)],
                                {ctx_fresco: ctx_bytes, viejo: CUERPO_PUBLICADO_VIEJO})
    assert salio == 1, salida
    assert "[FRESCO] CONTEXT-UNO" in salida, salida
    assert f"[VENCIDO] {DECLORADO_NOMBRE}" in salida, salida
    assert "[FAIL] frescura de CONTEXT" in salida, salida


def test_el_declorado_que_desaparece_del_disco_es_no_evaluable_no_es_silencio(vq, monkeypatch, tmp_path):
    """Directorio del plan presente, archivo borrado o movido: salida 2 con el nombre de la ruta declarada.

    Si la resolucion pidiera `is_file()` la entrada se cairia sola y el check quedaria verde sin
    candidatos, que es exactamente el hueco que la deuda de la fila 4 registro.
    """
    contexto, plans = _contexto_vacio(tmp_path), _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    (plans / _afirmar_rel_comun(vq)).unlink()
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, [], {})
    assert salio == 2, salida
    assert "[NO-EVALUABLE]" in salida and DECLORADO_NOMBRE in salida, salida


def test_la_interfaz_publica_la_poblacion_declorada_con_su_linea(vq, monkeypatch, tmp_path):
    contexto, plans = _contexto_vacio(tmp_path), _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    sid = "01a0ffff-0000-7000-8000-000000000106"
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                [_fuente(sid, "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre)",
                                         CUERPO_DECLORADO)],
                                {sid: CUERPO_DECLORADO})
    assert salio == 0, salida
    assert "poblacion declarada: 1 gobernado(s) (" in salida, salida
    linea_declorada = next(l for l in salida.splitlines() if l.startswith("poblacion declarada:"))
    assert DECLORADO_NOMBRE in linea_declorada, linea_declorada
    assert "poblacion: 0 CONTEXT gobernado(s)" in salida, (
        "la linea de CONTEXT perdio su forma: las aserciones existentes de la poblacion se aflojarian")
    assert "[OK] frescura de CONTEXT" in salida, salida


def test_el_resumen_sigue_llevando_el_token_que_filtra_el_runner(vq, monkeypatch, tmp_path):
    """La etiqueta del estado puede anunciar mas alcance, pero no puede perder el token del cableado.

    `run_all_validations.py` escoge su resumen con un filtro por cadena: si la linea final lo pierde, el
    runner publica la ultima linea cualquiera (el detalle de la poblacion) como si fuera el estado.
    """
    src = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
    filtro = re.search(r'if "(frescura de [^"]+)" in l', src)
    assert filtro, "el runner ya no filtra el resumen por la cadena conocida: re-leer el cableado"
    contexto, plans = _contexto_vacio(tmp_path), _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    sid = "01a0ffff-0000-7000-8000-000000000107"
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                [_fuente(sid, "sin prefijo", CUERPO_DECLORADO)], {sid: CUERPO_DECLORADO})
    assert salio == 0, salida
    assert filtro.group(1) in salida.splitlines()[-1], (
        f"la linea de estado no lleva `{filtro.group(1)}`: {salida.splitlines()[-1]!r}")


def test_control_negativo_el_diente_versionado_era_verde_con_el_cuerpo_vencido(tmp_path):
    """El `6cdb430` goberno solo CONTEXT: sobre el MISMO arbol dice [OK] mientras el 10-analisis esta vencido.

    Se lee y se ejecuta la copia versionada (`git show`), no una parodia escrita aqui. El arbol sintetico
    tiene un CONTEXT fresco y un `10-analisis` cuyo cuerpo publicado no casa: la version vieja devuelve 0,
    la nueva 1. Eso es lo que prueba que la cura cierra el hueco de la fila 4 y no otro.
    """
    assert _rev_existe(REV_SIN_POBLACION_DECLARADA), (
        f"la revision {REV_SIN_POBLACION_DECLARADA} no esta en el repo: re-anclar el control")
    proc = subprocess.run(
        ["git", "show", f"{REV_SIN_POBLACION_DECLARADA}:scripts/verify_qmind_context_freshness.py"],
        capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, proc.stderr[:200]
    ruta_vieja = tmp_path / "diente_versionado.py"
    ruta_vieja.write_text(proc.stdout, encoding="utf-8", newline="\n")
    viejo = _cargar("vq_versionado", ruta_vieja)

    assert not hasattr(viejo, "POBLACION_DECLARADA"), (
        "la revision anclada ya declara la poblacion nueva: el control dejo de ser anterior a la cura "
        "y hay que re-ancalarlo a una revision previa")

    contexto = _contexto_vacio(tmp_path)
    (contexto / UNO).write_text("# Contexto uno\n\n## Leccion durable: un archivado vence tambien "
                                "los CONTEXT\n", encoding="utf-8", newline="\n")
    ctx_bytes = (contexto / UNO).read_bytes()
    plans = _plans_con_declorado(tmp_path, CUERPO_DECLORADO)
    sid_ctx = "01a0ffff-0000-7000-8000-000000000108"
    sid_ana = "01a0ffff-0000-7000-8000-000000000109"
    fuentes = [_fuente(sid_ctx, f"CONTEXT: {UNO[:-3]}", ctx_bytes),
               _fuente(sid_ana, "10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre offline)",
                       CUERPO_PUBLICADO_VIEJO)]
    contenidos = {sid_ctx: ctx_bytes, sid_ana: CUERPO_PUBLICADO_VIEJO}

    salio_viejo, salida_vieja = _correr(viejo, contexto, plans, fuentes, contenidos)
    assert salio_viejo == 0, (
        "el diente versionado ya no da verde con el cuerpo del 10-analisis vencido: el control perdio su "
        "premissa y hay que re-leer la cura antes de afirmar que era ciega")
    assert "poblacion: 1 CONTEXT gobernado(s)" in salida_vieja and "10-analisis" not in salida_vieja, (
        "la salida del versionado ya menciona al 10-analisis: la copia anclada no es anterior a la cura")

    nuevo = _cargar("vq_contra_diente", SCRIPT)
    salio_nuevo, salida_nueva = _correr(nuevo, contexto, plans, fuentes, contenidos)
    assert salio_nuevo == 1, (
        "el instrumento actual tampoco ve el 10-analisis vencido sobre el mismo arbol: no hay "
        "differential y la prueba no afirma la cura")
    assert f"[VENCIDO] {DECLORADO_NOMBRE} ({REL_DECLORADO})" in salida_nueva, salida_nueva
    assert "[FRESCO] CONTEXT-UNO" in salida_nueva, (
        "el CONTEXT del diferencial dejo de estar fresco: el rojo vendria de otra causa")



# =================================================== el contrato re-escrito por D2 (2026-10-05, REL-6)

#   La fila anterior del contrato decia "metadata es corroboracion, ninguna decision sale de el". D2
#   invierte el ORDEN de la prueba sin tocar el criterio: la primera via es lo que el servidor declara de
#   sus propios bytes y la descarga queda como verificacion de esa promesa. Los dientes de abajo van por
#   las dos mitades: que la metadata decida, y que **siga haciendo falta la descarga** para decir FRESCO.

def test_fuente_que_casa_por_metadata_y_no_baja_es_no_evaluable_no_vencido(vq, monkeypatch, tmp_path):
    """H15 / B2-4 con la causa nombrada: la promesa que no se pudo verificar no pinta VENCIDO.

    Es exactamente la corrida `FASE-RELEASE/12-` y su apendice `40-`: la unica fuente cuyo
    `fileSha256` iguala el disco (`01a0efcc-3297…`) no bajo por un `QMind network request failed` y el
    verificador dijo `[VENCIDO]` sobre un fresco.
    """
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000200"
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                    [_fuente(sid, f"CONTEXT: {UNO[:-3]}", disco)], {})
    assert salio == 2, salida
    assert "[NO-EVALUABLE]" in salida and sid in salida, salida
    assert "[VENCIDO]" not in salida, "la abstencion volvio a pintarse de vencido: " + salida
    assert "[OK]" not in salida, salida
    assert falso.descargas == 1, "se conto una bajada que no produjo archivo: " + salida


def test_el_verde_nuevo_sigue_exigiendo_la_descarga_que_verifica_la_promesa(vq, monkeypatch, tmp_path):
    """AC-3 del lado viejo: metadata que casa NO aprueba por si sola, aprueba la promesa verificada."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000201"
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                    [_fuente(sid, f"CONTEXT: {UNO[:-3]}", disco)], {sid: disco})
    assert salio == 0, salida
    assert "[FRESCO]" in salida and "metadata del servidor" in salida, salida
    assert "descarga+sha256" in salida, (
        "el FRESCO salio de la metadata sin verificar la promesa: " + salida)
    assert falso.descargas == 1, (
        f"la promesa se verifico con {falso.descargas} bajadas: o no se bajo nada o se bajo de mas")


def test_descarga_que_desmiente_al_indice_del_servidor_es_promesa_rota(vq, monkeypatch, tmp_path):
    """El servidor declara el sha del disco y entrega otros bytes: rojo, pero rojo de la promesa."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000202"
    fuentes = [{"id": sid, "title": f"CONTEXT: {UNO[:-3]}", "status": "ready",
                "metadata": {"fileSha256": hashlib.sha256(disco).hexdigest(),
                             "fileSize": len(disco)}}]
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes,
                                    {sid: b"el notebook guarda otros bytes"})
    assert salio == 1, salida
    assert "[PROMESA-ROTA]" in salida and "[FRESCO]" not in salida, salida
    assert falso.descargas >= 1, salida


def test_barrido_del_que_no_baja_nada_sale_no_evaluable_y_declara_su_causa(vq, monkeypatch, tmp_path):
    """La misma regla generalizada al camino viejo: cero observaciones no es un VENCIDO."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    a = "01a0ffff-0000-7000-8000-000000000203"
    b = "01a0ffff-0000-7000-8000-000000000204"
    fuentes = [_fuente(a, f"CONTEXT: {UNO[:-3]}", disco, metadata=False),
               _fuente(b, "otra fuente", b"nada que ver", metadata=False)]
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes, {})
    assert salio == 2, salida
    assert "[VENCIDO]" not in salida, salida
    assert "[SIN-DESCARGA]" in salida, "la bajada que fallo se callo: " + salida
    assert "no bajo ninguna" in salida, salida


def test_la_primera_via_no_mira_el_titulo_basta_la_metadata_que_casa(vq, monkeypatch, tmp_path):
    """El nuevo camino recorta el costo: titulo irreconocible + metadata que casa = FRESCO con UNA bajada.

    Antes este caso pagaba el barrido completo de las 57 fuentes; ahora la declaracion del servidor
    concentra la bajada en la fuente que promete, y el titulo sigue sin decidir nada.
    """
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000205"
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                    [_fuente(sid, "Apunte suelto sin el stem", disco)], {sid: disco})
    assert salio == 0 and "[FRESCO]" in salida, salida
    assert "barrido completo" not in salida, salida
    assert falso.descargas == 1, f"se bajo {falso.descargas} veces donde la promesa concentraba en 1"


def test_sin_metadata_publicada_el_camino_de_descarga_sigue_vivo(vq, monkeypatch, tmp_path):
    """El diente viejo no se jubila: fuente SIN `fileSha256` se decide bajando y barrviendo."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000206"
    salio, falso, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans,
                                    [_fuente(sid, "Apunte suelto sin el stem", disco,
                                             metadata=False)], {sid: disco})
    assert salio == 0 and "[FRESCO]" in salida, salida
    assert "barrido completo" in salida, "el camino de bytes sin metadata perdio su ruta: " + salida
    assert "por descarga+sha256" in salida, salida
    assert falso.descargas == 1, salida


def test_el_fileSize_del_servidor_tambien_se_corrobora_y_se_declara(vq, monkeypatch, tmp_path):
    """`fileSize` que no casa con el disco se escribe en la linea: corroboracion, no veredicto."""
    contexto, plans = _contexto(tmp_path)
    disco = (contexto / UNO).read_bytes()
    sid = "01a0ffff-0000-7000-8000-000000000207"
    fuentes = [{"id": sid, "title": f"CONTEXT: {UNO[:-3]}", "status": "ready",
                "metadata": {"fileSha256": hashlib.sha256(disco).hexdigest(),
                             "fileSize": len(disco) + 7}}]
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes, {sid: disco})
    assert salio == 0, salida
    assert "DESACUERDO tam=" in salida, (
        "el tamano declarado se callo en vez de declararse: " + salida)


def test_el_rojo_de_un_gobernado_manda_sobre_la_abstencion_de_otro(vq, monkeypatch, tmp_path):
    """La abstencion no puede tapar un vencido: si algo se observo y no casa, la corrida corta."""
    contexto, plans = _contexto(tmp_path, dos=True)
    disco_uno = (contexto / UNO).read_bytes()
    disco_dos = (contexto / DOS).read_bytes()
    vencido = "01a0ffff-0000-7000-8000-000000000208"
    no_bajable = "01a0ffff-0000-7000-8000-000000000209"
    fuentes = [_fuente(vencido, f"CONTEXT: {UNO[:-3]}", disco_uno + b"\notra version\n"),
               _fuente(no_bajable, f"CONTEXT: {DOS[:-3]}", disco_dos)]
    salio, _, salida = _corrida(vq, monkeypatch, tmp_path, contexto, plans, fuentes,
                                {vencido: disco_uno + b"\notra version\n"})
    assert "[NO-EVALUABLE]" in salida, salida
    assert "[VENCIDO]" in salida, salida
    assert salio == 1, f"la abstencion tapo al vencido (salio {salio}): " + salida
