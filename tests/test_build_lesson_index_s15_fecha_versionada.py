"""S15: la fecha del indice de lecciones sale de una fuente versionada, no del `mtime`.

Deuda registrada en `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-
implementacion.md` fila **S15** (su texto vigente es ese; este archivo es la cura, no el registro).

Que se prueba, y por que no basta con mirar los bytes:

* Dos **checkouts reales** del mismo commit (clones locales, `--local`, sin red) con `mtime`
  **distinto** en los dos documentos que no tienen fecha en el nombre. Con el generador viejo eso
  publicaba dos `lecciones_index.json` distintos; con la cura publican **bytes identicos**.
* El control negativo se lee en la **revision publicada** (`git show REV_CONTROL_DEFECTUOSO:...`),
  no re-implementando el defecto dentro del test: asi lo que se ejercita es el instrumento que
  estuvo en `origin/master`, y el control conserva su rojo despues de comitear la cura. **No puede
  ser `HEAD`**: al comitear esta cura HEAD pasa a contener el generador corregido y el control se
  queda sin defecto con el que compararse (`tests/test_sync_writers_lf_y_fecha_readme.py:56` ya lo
  pago tres pruebas).
* El tercer corte, `SIN-FUENTE`, se ejercita sobre una **copia fuera del repositorio**: ahi no hay
  commit posible, y lo que se exige es un estado publicado, no una fecha aproximada. Un test que
  solo viera el camino feliz diraria `0 sin_fuente` sin haber observado nunca ese estado.
* No se pinea el numero de entradas con fuente `commit` (ese conjunto crece cuando alguien añade un
  CONTEXT sin fecha en el nombre): la asercion derive la fecha esperada de `git log`, que es la
  misma fuente que consumio el generador.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_REL = "scripts/build_lesson_index.py"
SOURCE_CURADO = ROOT / SCRIPT_REL

# Ancla del control negativo: la ultima revision publicada en la que `_plan_date` caia a `st_mtime`.
# Medido con `git show 6b02532:scripts/build_lesson_index.py` (linea 112: `f.stat().st_mtime`).
REV_CONTROL_DEFECTUOSO = "6b02532"

# Los dos unicos duenios del corpus real que llegan al tier 2: su nombre no trae fecha (viven bajo
# `.opencode/context/Historico/` y el dueno se etiqueta por stem).
DOC_SIN_FECHA = [
    ".opencode/context/Historico/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL.md",
    ".opencode/context/Historico/CONTEXT-DT-3-TECH-DEBT-POST-DT2.md",
]

MTO_A = "2020-01-02 03:04:05"
MTO_B = "2031-06-06 06:06:06"

SIN_GIT = pytest.mark.skipif(
    shutil.which("git") is None or not (ROOT / ".git").exists(),
    reason="hace falta un repositorio git real (y el binario) para montar dos checkouts",
)


def _correr(script: Path, out_dir: Path) -> subprocess.CompletedProcess:
    """Corre el generador **de ese checkout**, con sus directorios por defecto."""
    return subprocess.run(
        [sys.executable, str(script), "--out-dir", str(out_dir)],
        cwd=str(script.parents[1]),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _escribir(destino: Path, texto: str) -> None:
    """`unlink` antes de escribir: `git clone --local` enlaza objetos, y un `write_text` sobre un
    enlace duro re-escribiria el archivo del repositorio de origen. El `mkdir` es porque el checkout
    es parcial: el clon no trae `scripts/` hasta que esta prueba lo pone."""
    destino.unlink(missing_ok=True)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto, encoding="utf-8", newline="\n")


def _fuente_commiteada(rev: str, rel: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{rev}:{rel}"], cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 0, f"git show {rev}:{rel} fallo: {proc.stderr[:200]}"
    return proc.stdout


def _pareja_de_checkouts(base: Path) -> tuple[Path, Path]:
    """Dos clones locales del mismo commit, con mtimos distintos en los documentos del tier 2.

    Se clona `--no-checkout` y se materializan solo `.opencode/plans` y `.opencode/context`, que es
    TODO lo que el generador recorre: un checkout completo del repo no cabe en la ruta corta de
    Windows (medido: `Filename too long` en `.opencode/.qoder/repowiki/.../Pending Functionality
    Refactoring (v4.58.0).md`, y `Clone succeeded, but checkout failed`). El historial de git si esta
    entero, que es lo que hace falta para que el tier 2 resuelva en el clon.
    """
    for nombre in ("A", "B"):
        if (base / nombre).exists():
            shutil.rmtree(base / nombre)
    for nombre, mtime in (("A", MTO_A), ("B", MTO_B)):
        destino = base / nombre
        proc = subprocess.run(
            ["git", "-c", "core.autocrlf=input", "-c", "core.longpaths=true", "clone", "--local",
             "--no-checkout", "--quiet", str(ROOT), str(destino)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0, f"el clon {nombre} no se creo: {proc.stderr[:300]}"
        resta = subprocess.run(
            ["git", "checkout", "HEAD", "--", ".opencode/plans", ".opencode/context"],
            cwd=str(destino), capture_output=True, text=True, encoding="utf-8",
        )
        assert resta.returncode == 0, (
            f"el corpus no se materializo en {nombre}: {resta.stderr[:300]}")
    for rel in DOC_SIN_FECHA:
        for nombre, fecha in (("A", MTO_A), ("B", MTO_B)):
            ruta = base / nombre / rel
            assert ruta.is_file(), f"{rel} no existe en el checkout {nombre}: el control no tendria que medir"
            stamp = time.mktime(time.strptime(fecha, "%Y-%m-%d %H:%M:%S"))
            os.utime(ruta, (stamp, stamp))
    return base / "A", base / "B"


def _mtimos_divergen(a: Path, b: Path) -> None:
    """Precondition sin la cual los dos `run` serian la misma maquina y el verde no observaria nada."""
    for rel in DOC_SIN_FECHA:
        ma = (a / rel).stat().st_mtime
        mb = (b / rel).stat().st_mtime
        assert ma != mb, f"{rel}: los dos checkouts quedaron con el mismo mtime ({ma}); nada que medir"


def _leer_json(ruta: Path) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


@SIN_GIT
def test_dos_checkouts_con_mtimos_distintos_publican_bytes_identicos(tmp_path_factory):
    """Lo que S15 pide: el mismo commit en dos arboles, un solo resultado."""
    base = tmp_path_factory.mktemp("s15")
    a, b = _pareja_de_checkouts(base)
    _mtimos_divergen(a, b)

    texto_curado = SOURCE_CURADO.read_text(encoding="utf-8")
    assert "st_mtime" not in texto_curado, "el generador vuelve a consultar el sistema de archivos"
    _escribir(a / SCRIPT_REL, texto_curado)
    _escribir(b / SCRIPT_REL, texto_curado)

    ra, rb = _correr(a / SCRIPT_REL, base / "out_A"), _correr(b / SCRIPT_REL, base / "out_B")
    assert ra.returncode == 0 and rb.returncode == 0, [ra.stdout, ra.stderr, rb.stdout, rb.stderr]

    json_a, json_b = (base / "out_A" / "lecciones_index.json").read_bytes(), \
                     (base / "out_B" / "lecciones_index.json").read_bytes()
    assert json_a == json_b, (
        "dos checkouts del mismo commit publicaron JSONes distintos: la fecha todavia depende del "
        "entorno (S15 sin cerrar)")
    md_a, md_b = (base / "out_A" / "LECCIONES-INDEX.md").read_bytes(), \
                 (base / "out_B" / "LECCIONES-INDEX.md").read_bytes()
    assert md_a == md_b, "el indice legible por humanos tampoco es estable entre checkouts"

    lecciones = _leer_json(base / "out_A" / "lecciones_index.json")["lecciones"]
    commit = [e for e in lecciones if e["fuente_fecha"] == "commit"]
    assert commit, (
        "ninguna leccion salio del tier 2: el par de checkouts no ejercito la rama curada "
        "(verde vacio, L-VCF-13)")
    assert not [e for e in lecciones if e["fuente_fecha"] == "mtime"], (
        "quedan entradas fechadas por mtime")
    for e in commit:
        rel = next((d for d in DOC_SIN_FECHA
                    if Path(d).stem == e["plan"].split("/", 1)[-1]), None)
        assert rel, f"{e['id']}: fuente commit para un dueno ({e['plan']}) fuera de la poblacion anclada"
        esperada = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", rel],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
        ).stdout.strip()[:10]
        assert e["fecha_plan"] == esperada, (
            f"{e['id']}: la fecha publicada ({e['fecha_plan']}) no es la del commit que toco su "
            f"documento ({esperada})")


@SIN_GIT
def test_el_control_defectuoso_de_la_revision_publicada_si_diverge(tmp_path_factory):
    """El rojo que la cura quito: con `6b02532` los dos checkouts publicaban dos fechas."""
    base = tmp_path_factory.mktemp("s15_defecto")
    a, b = _pareja_de_checkouts(base)
    _mtimos_divergen(a, b)

    defectuoso = _fuente_commiteada(REV_CONTROL_DEFECTUOSO, SCRIPT_REL)
    assert "st_mtime" in defectuoso, (
        f"la revision anclada {REV_CONTROL_DEFECTUOSO} ya no contiene el defecto: el control "
        "perdio su rojo y hay que re-anclarlo")
    assert defectuoso != SOURCE_CURADO.read_text(encoding="utf-8"), (
        "el control y la cura son el mismo archivo: no hay comparacion posible")

    _escribir(a / SCRIPT_REL, defectuoso)
    _escribir(b / SCRIPT_REL, defectuoso)
    ra, rb = _correr(a / SCRIPT_REL, base / "out_A"), _correr(b / SCRIPT_REL, base / "out_B")
    assert ra.returncode == 0 and rb.returncode == 0, [ra.stdout, ra.stderr, rb.stdout, rb.stderr]

    la = {e["id"]: e for e in _leer_json(base / "out_A" / "lecciones_index.json")["lecciones"]}
    lb = {e["id"]: e for e in _leer_json(base / "out_B" / "lecciones_index.json")["lecciones"]}
    assert la.keys() == lb.keys(), "las dos revisiones del control poblaron el indice distinto"
    distintos = {i for i in la if la[i] != lb[i]}
    assert distintos, (
        "el control negativo no ejercito el defecto: hasta la version commiteada dio bytes "
        "identicos, asi que la prueba de arriba pasa sobre cualquier cosa")
    # Y nombra lo que desaparece, para que el rojo sea atribuible (L-V2.1): la diferencia son las
    # dos fechas del reloj del sistema de cada arbol, no el conjunto de lecciones.
    for i in distintos:
        assert la[i]["fuente_fecha"] == "mtime" and lb[i]["fuente_fecha"] == "mtime"
        assert la[i]["fecha_plan"] == MTO_A[:10] and lb[i]["fecha_plan"] == MTO_B[:10], (
            f"{i}: el control difiere por otra cosa que la fecha de mtime, y la asercion de arriba "
            "no estaria midiendo S15")
    assert {la[i]["id"] for i in distintos} >= {"S-1", "S-11"}, (
        "el rojo del control no cae sobre la familia que S15 nombra (S-1..S-11)")


def test_un_copiar_fuera_del_repo_publica_sin_fuente_y_no_una_aproximacion(tmp_path):
    """Tercer corte: sin commit posible se declara el estado, no se rellena con el reloj."""
    plans = tmp_path / "plans"
    plans.mkdir()
    # Nombre sin fecha: tier 1 no aplica. Y la ruta esta fuera de ROOT: tier 2 tampoco puede aplicar.
    plan = plans / "PLAN-SIN-VERSION"
    plan.mkdir()
    (plan / "10-analisis-post-implementacion.md").write_text(
        "## Lecciones Aprendidas\n\n"
        "| L-S15X | Copiar el corpus fuera del repo no da fecha, da un estado | x |\n",
        encoding="utf-8",
    )
    contexto = tmp_path / "context-vacio"
    contexto.mkdir()

    from scripts import build_lesson_index as bli

    index, coverage = bli.build(plans, contexto)
    entry = index["lessons"]["L-S15X"]
    assert entry["fuente_fecha"] == bli.FUENTE_SIN_FUENTE, (
        f"sin fuente versionada la salida fue {entry['fuente_fecha']!r}: se volvio a una fecha "
        "aproximada")
    assert entry["fecha_plan"] == bli.FECHA_SIN_FUENTE
    assert coverage["fechas_por_fuente"][bli.FUENTE_SIN_FUENTE] == 1

    out = tmp_path / "out"
    proc = subprocess.run(
        [sys.executable, str(SOURCE_CURADO), "--plans-dir", str(plans),
         "--context-dir", str(contexto), "--out-dir", str(out)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 0, proc.stderr[:400]
    assert "sin_fuente=1" in proc.stdout, (
        f"la generacion no declaro el estado: {proc.stdout!r}")


def test_el_check_declara_de_que_fuente_salen_las_fechas(tmp_path):
    """Un verde de `[6/7]` que no dice de donde salio la fecha no es auditable (S15)."""
    plans = tmp_path / "plans"
    plans.mkdir()
    plan = plans / "PLAN-2026-01-01"
    plan.mkdir()
    (plan / "10-analisis-post-implementacion.md").write_text(
        "## Lecciones Aprendidas\n\n"
        "| L-S15Y | El check publica sus fuentes | x |\n",
        encoding="utf-8",
    )
    contexto = tmp_path / "context-vacio"
    contexto.mkdir()
    out = tmp_path / "out"

    args = ["--plans-dir", str(plans), "--context-dir", str(contexto), "--out-dir", str(out)]
    assert subprocess.run([sys.executable, str(SOURCE_CURADO), *args],
                          capture_output=True, text=True, encoding="utf-8").returncode == 0

    verificado = subprocess.run([sys.executable, str(SOURCE_CURADO), *args, "--check"],
                                 capture_output=True, text=True, encoding="utf-8")
    assert verificado.returncode == 0, verificado.stdout + verificado.stderr
    assert "[fechas] nombre=1 commit=0 sin_fuente=0" in verificado.stdout, verificado.stdout
    payload = _leer_json(out / "lecciones_index.json")
    assert payload["cobertura"]["fechas_por_fuente"] == {
        "nombre": 1, "commit": 0, "SIN-FUENTE": 0}

    # Y la declaracion sigue en la via roja: un [6/7] que corta sin decir de donde salian
    # las fechas deja a quien lee sin el dato que gobernaría su decision.
    (out / "LECCIONES-INDEX.md").write_text("contenido vencido\n", encoding="utf-8")
    vencido = subprocess.run([sys.executable, str(SOURCE_CURADO), *args, "--check"],
                             capture_output=True, text=True, encoding="utf-8")
    assert vencido.returncode == 1 and "vencido" in vencido.stdout, vencido.stdout
    assert "[fechas] nombre=1 commit=0 sin_fuente=0" in vencido.stdout, (
        f"el check cortó sin declarar sus fuentes: {vencido.stdout!r}")
