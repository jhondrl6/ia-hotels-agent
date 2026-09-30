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
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_qmind_context_freshness.py"
REV_HERMANO_VERSIONADO = "7737347"
NB = "01a04d98-b7bd-778c-8441-26fdc7e35f45"

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
    return _cargar("vq_fresco", SCRIPT)


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
    assert falso.descargas == 2, (
        f"bajo {falso.descargas} fuentes: se esperaban las dos que nombran al CONTEXT (la vencida y la "
        "de cierre), ni una mas (barrido) ni una menos (decision por titulo)")


def test_metadata_no_es_el_criterio(vq, monkeypatch, tmp_path):
    """`metadata.fileSha256` que casa con el disco pero cuya descarga NO: sigue VENCIDO.

    Si el verificador admitiera el metadata como prueba, el `--upload` que responde `[SKIP]` por titulo
    volveria a dejar la version vieja como verdad publicada sin decir nada (RI §13).
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
