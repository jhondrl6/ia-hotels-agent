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

Como se gobierna el reloj del fixture (cura de FASE-B, medida en
`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-B/01-diagnostico-crudo.txt`): el desempate de
dueno del generador defectuoso ordena por **fecha ascendente**, asi que un `mtime` declarado por
encima del **piso del corpus** (la fecha mas antigua que aparece en el nombre de un dueno) pierde el
dueno frente a un plan fechado y el indice sale con fuente `nombre`, no `mtime`. Con el par fijado
**bajo** ese piso, derivado de la poblacion que el propio generador recorre, la unica divergencia
posible entre los dos arboles es la fecha de `mtime`, que es lo que la asercion de abajo afirma. La
horqueta (un `mtime` bajo el piso y otro sobre el techo) queda ejercitada por su propio test: es el
rojo que se gobierna, y se conserva visible en vez de desaparecer del archivo.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import date, timedelta
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

MTO_HORA = " 03:04:05"
# Estado de abstencion (R2.9): un fixture que no puede fijar su reloj sobre la poblacion que el
# generador recorre no tiene nada que certificar. Decirlo con la ruta o el criterio buscado vale
# mas que un verde, y mas que un «divergencia hallada» producida por un arbol que no materializo.
NO_EVALUABLE = "NO-EVALUABLE"

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


def _duenos_con_fecha(raiz_corpus: Path) -> list[str]:
    """Fechas que trae el nombre de un dueno, con el etiquetado del propio generador.

    No se reimplementa el barrido: el piso tiene que salir de la misma poblacion que el indice
    recorre (`_sources` + `DATE_RE`), si no el fixture gobernaría su reloj contra un corpus
    distinto del que se esta clasificando.
    """
    from scripts import build_lesson_index as bli

    sources, _ = bli._sources(raiz_corpus / ".opencode" / "plans",
                              raiz_corpus / ".opencode" / "context")
    return sorted({m.group(1) for m in (bli.DATE_RE.search(o)
                                        for o in {s["owner"] for s in sources}) if m})


def _piso_y_techo(raiz_corpus: Path) -> tuple[str, str]:
    """Rango de fechas-en-nombre del corpus: (la mas antigua, la mas reciente).

    Sin poblacion fechada no hay piso que gobernar y el estado es NO-EVALUABLE con el criterio
    buscado, nunca un par de mtimes inventados (R2.9, L-QW.3).
    """
    fechas = _duenos_con_fecha(raiz_corpus)
    if not fechas:
        pytest.fail(f"{NO_EVALUABLE}: ningun dueno del corpus bajo {raiz_corpus} trae fecha en el "
                    "nombre; el fixture no tiene piso contra el que fijar sus mtimes")
    return fechas[0], fechas[-1]


def _par_de_mtimes(piso: str, techo: str, modo: str) -> tuple[str, str]:
    """Los dos relojes del fixture, derivados del corpus y no pineados.

    `bajo_el_piso`: ambos estrictamente antes de la fecha-en-nombre mas antigua. Con `mtime` por
    debajo de todo dueno fechado, el desempate ascendente del generador defectuoso siempre deja el
    dueno en el documento fechado por `mtime`, asi que lo unico que puede divergir entre los dos
    arboles es la fecha. `horqueta`: A bajo el piso y B sobre el techo; ahi el `mtime` de B queda
    despues de todo dueno fechado y el dueno se invierte — es el rojo que FASE-B goberno, y sigue
    ejercitandose en su propio test en vez de desaparecer del archivo.
    """
    if modo == "bajo_el_piso":
        base = date.fromisoformat(piso)
        return ((base - timedelta(days=2)).isoformat() + MTO_HORA,
                (base - timedelta(days=1)).isoformat() + MTO_HORA)
    if modo == "horqueta":
        return ((date.fromisoformat(piso) - timedelta(days=2)).isoformat() + MTO_HORA,
                (date.fromisoformat(techo) + timedelta(days=2)).isoformat() + MTO_HORA)
    raise ValueError(f"modo de reloj no conocido: {modo!r}")


def _revisar_materializacion(raices: list[Path], docs: list[str]) -> None:
    """Antes de medir: si la ruta del fixture no esta, se nombra la ruta, no se afirma divergencia."""
    for raiz in raices:
        for rel in docs:
            if not (raiz / rel).is_file():
                pytest.fail(f"{NO_EVALUABLE}: la ruta del fixture no materializa en {raiz}: {rel}")


def _revisar_clon_fiel(clon: Path, docs: list[str]) -> None:
    """El arbol del clon tiene que ser byte a byte el del commit (patrón S20).

    Medido en FASE-B (`…/FASE-B/02-h2-crlf-del-clon.txt`): pasar `-c core.autocrlf=input` solo a
    `git clone` no persiste nada — el `checkout` corre dentro del clon y lee la config **del clon**,
    que hereda el `true` del ambito *system* de Windows. Con la config fijada dentro, el documento
    del fixture casa con su blob de HEAD; con las flags sueltas no (24.149 B en disco contra 23.622
    B commiteados).
    """
    autocrlf = subprocess.run(["git", "config", "--get", "core.autocrlf"], cwd=str(clon),
                              capture_output=True, text=True, encoding="utf-8").stdout.strip()
    if autocrlf != "input":
        pytest.fail(f"{NO_EVALUABLE}: `core.autocrlf` dentro del clon {clon} es {autocrlf!r}, no "
                    "'input': el arbol materializado no es el del commit")
    for rel in docs:
        esperado = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                                  capture_output=True)
        if esperado.returncode != 0:
            pytest.fail(f"{NO_EVALUABLE}: `git show HEAD:{rel}` no resuelve en {ROOT}: "
                        f"{esperado.stderr.decode('utf-8', 'replace')[:200]}")
        disco = (clon / rel).read_bytes()
        if disco != esperado.stdout:
            pytest.fail(f"{NO_EVALUABLE}: {rel} en {clon} no casa con su blob de HEAD "
                        f"({len(disco)} B en disco contra {len(esperado.stdout)} B commiteados)")


def _pareja_de_checkouts(base: Path, modo: str = "bajo_el_piso") -> tuple[Path, Path, str, str]:
    """Dos clones locales del mismo commit, con el reloj del fixture derivado del corpus.

    Se clona `--no-checkout` y se materializan solo `.opencode/plans` y `.opencode/context`, que es
    TODO lo que el generador recorre: un checkout completo del repo no cabe en la ruta corta de
    Windows (medido: `Filename too long` en `.opencode/.qoder/repowiki/.../Pending Functionality
    Refactoring (v4.58.0).md`, y `Clone succeeded, but checkout failed`). El historial de git si esta
    entero, que es lo que hace falta para que el tier 2 resuelva en el clon.

    Devuelve los dos arboles y los dos `mtime` que se estamparon: la asercion del control compara
    contra el reloj que el fixture aplico, no contra un literal que el corpus puede dejar atras.
    """
    for nombre in ("A", "B"):
        if (base / nombre).exists():
            shutil.rmtree(base / nombre)
    for nombre in ("A", "B"):
        destino = base / nombre
        proc = subprocess.run(
            ["git", "clone", "--local", "--no-checkout", "--quiet", str(ROOT), str(destino)],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert proc.returncode == 0, f"el clon {nombre} no se creo: {proc.stderr[:300]}"
        # S20: la config se fija DENTRO del clon, antes del checkout, y no como flag del `git clone`.
        for clave, valor in (("core.autocrlf", "input"), ("core.longpaths", "true")):
            fijada = subprocess.run(["git", "config", clave, valor], cwd=str(destino),
                                    capture_output=True, text=True, encoding="utf-8")
            assert fijada.returncode == 0, (
                f"no se pudo fijar {clave} dentro del clon {nombre}: {fijada.stderr[:200]}")
        resta = subprocess.run(
            ["git", "checkout", "HEAD", "--", ".opencode/plans", ".opencode/context"],
            cwd=str(destino), capture_output=True, text=True, encoding="utf-8",
        )
        assert resta.returncode == 0, (
            f"el corpus no se materializo en {nombre}: {resta.stderr[:300]}")
    a, b = base / "A", base / "B"
    _revisar_materializacion([a, b], DOC_SIN_FECHA)
    _revisar_clon_fiel(a, DOC_SIN_FECHA)
    _revisar_clon_fiel(b, DOC_SIN_FECHA)
    piso, techo = _piso_y_techo(a)
    mto_a, mto_b = _par_de_mtimes(piso, techo, modo)
    for rel in DOC_SIN_FECHA:
        for ruta, fecha in ((a / rel, mto_a), (b / rel, mto_b)):
            stamp = time.mktime(time.strptime(fecha, "%Y-%m-%d %H:%M:%S"))
            os.utime(ruta, (stamp, stamp))
    return a, b, mto_a, mto_b


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
    a, b, _mto_a, _mto_b = _pareja_de_checkouts(base)
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
    a, b, mto_a, mto_b = _pareja_de_checkouts(base)
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
        assert la[i]["fecha_plan"] == mto_a[:10] and lb[i]["fecha_plan"] == mto_b[:10], (
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


@SIN_GIT
def test_la_revision_fija_del_control_no_se_re_ancra_a_head():
    """AC8: re-ancorar el control negativo a HEAD se detecta, no se consiente.

    El defecto vive solo en `6b02532`; HEAD lleva la cura. Si alguien punta la constante a HEAD (o
    a cualquier revision sin `st_mtime`) el control se queda sin rojo con el que compararse y pasa
    a ser un verde vacio.
    """
    assert REV_CONTROL_DEFECTUOSO == "6b02532", (
        f"la revision del control negativo cambio a {REV_CONTROL_DEFECTUOSO!r}: AC8 prohibe "
        "re-ancorarla, y la ancla literal es lo que la audita")
    defectuoso = _fuente_commiteada(REV_CONTROL_DEFECTUOSO, SCRIPT_REL)
    assert "st_mtime" in defectuoso, (
        f"{REV_CONTROL_DEFECTUOSO} ya no cae a `st_mtime`: el control perdio su defecto")
    head = _fuente_commiteada("HEAD", SCRIPT_REL)
    assert "st_mtime" not in head, (
        "HEAD vuelve a consultar el sistema de archivos: la cura de S15 se revirtio")
    assert defectuoso != head, "el control y la cura son el mismo archivo: no hay comparacion"


@SIN_GIT
def test_el_par_de_mtimes_se_deriva_bajo_el_piso_del_corpus_y_el_clon_es_fiel(tmp_path_factory):
    """La gobernanza del reloj (AC8) y del arbol (S20), con su piso medido.

    Sin esta prueba el par derivado seria una cifra que nadie mira: lo que sostiene el rojo del
    control es que **ambos** mtimes queden antes de la fecha-en-nombre mas antigua del corpus. Y
    lo que sostiene el corte positivo es que el clon materializa el arbol del commit, no uno
    re-escrito por el `core.autocrlf` del ambito system.
    """
    base = tmp_path_factory.mktemp("s15_piso")
    a, b, mto_a, mto_b = _pareja_de_checkouts(base)
    piso, techo = _piso_y_techo(a)
    fechas = _duenos_con_fecha(a)
    assert fechas, "piso sin poblacion: el helper tenia que abstenerse, no llegar aqui"
    assert date.fromisoformat(mto_a[:10]) < date.fromisoformat(piso) and \
        date.fromisoformat(mto_b[:10]) < date.fromisoformat(piso), (
        f"el reloj del fixture no queda bajo el piso del corpus ({piso}): mtime podria perder el "
        f"dueno contra un plan cerrado y la divergencia dejaria de ser solo la fecha ({mto_a}, "
        f"{mto_b})")
    assert mto_a != mto_b, "los dos relojes coinciden: no hay nada que medir entre los arboles"
    assert techo >= piso, f"el techo del corpus ({techo}) precede a su piso ({piso})"
    # Y el arbol: la config fijada DENTRO del clon y el documento del fixture casando con su blob.
    assert subprocess.run(["git", "config", "--get", "core.autocrlf"], cwd=str(a),
                          capture_output=True, text=True, encoding="utf-8").stdout.strip() == "input"
    for clon in (a, b):
        for rel in DOC_SIN_FECHA:
            esperado = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=str(ROOT),
                                      capture_output=True)
            assert esperado.returncode == 0, f"HEAD:{rel} no resuelve en {ROOT}"
            assert (clon / rel).read_bytes() == esperado.stdout, (
                f"{rel} en {clon} no es el arbol del commit: el autocrlf heredado lo re-escribio")


@SIN_GIT
def test_un_par_en_horqueta_invierte_el_dueno_y_es_el_rojo_que_se_gobierna(tmp_path_factory):
    """El contrafactual de AC8: con un `mtime` sobre el techo del corpus el dueno se invierte.

    Es la firma exacta del rojo que traia el mandato (fuente `nombre` en el arbol B, no `mtime`).
    Se conserva ejercitada en el archivo para que la gobernanza del reloj no sea un verde por
    ausencia: si alguien quita el clamp, esta prueba sigue verde y la del control pierde, y ambas
    nombran el mismo mecanismo.
    """
    base = tmp_path_factory.mktemp("s15_horqueta")
    a, b, mto_a, mto_b = _pareja_de_checkouts(base, modo="horqueta")
    piso, techo = _piso_y_techo(a)
    assert date.fromisoformat(mto_a[:10]) < date.fromisoformat(piso) and \
        date.fromisoformat(mto_b[:10]) > date.fromisoformat(techo), (
        f"la horqueta no cruza el corpus: {mto_a} vs piso {piso}, {mto_b} vs techo {techo}")

    defectuoso = _fuente_commiteada(REV_CONTROL_DEFECTUOSO, SCRIPT_REL)
    _escribir(a / SCRIPT_REL, defectuoso)
    _escribir(b / SCRIPT_REL, defectuoso)
    ra, rb = _correr(a / SCRIPT_REL, base / "out_A"), _correr(b / SCRIPT_REL, base / "out_B")
    assert ra.returncode == 0 and rb.returncode == 0, [ra.stdout, ra.stderr, rb.stdout, rb.stderr]

    la = {e["id"]: e for e in _leer_json(base / "out_A" / "lecciones_index.json")["lecciones"]}
    lb = {e["id"]: e for e in _leer_json(base / "out_B" / "lecciones_index.json")["lecciones"]}
    distintos = {i for i in la if la[i] != lb[i]}
    assert distintos, "la horqueta no divergio: el reloj gobernado no tendria contra que compararse"
    invertidos = [i for i in distintos
                  if la[i]["plan"] != lb[i]["plan"]
                  or la[i]["fuente_fecha"] != "mtime" or lb[i]["fuente_fecha"] != "mtime"]
    assert invertidos, (
        "con un mtime sobre el techo del corpus el dueno NO se invierte: el mecanismo que produce "
        "el rojo del mandato ya no existe y hay que re-escribir la gobernanza, no asumirla")
    for i in invertidos:
        ganador = la[i] if la[i]["fuente_fecha"] != "mtime" else lb[i]
        assert ganador["fuente_fecha"] == "nombre", (
            f"{i}: el dueno que desplaza al mtime no viene del nombre ({ganador['fuente_fecha']})")
        assert ganador["fecha_plan"] in ganador["plan"], (
            f"{i}: la fecha {ganador['fecha_plan']} no aparece en el dueno {ganador['plan']}, que "
            "es lo que la hace ganar el desempate por ser mas antigua que el mtime")


def test_el_clon_que_no_materializa_declara_no_evaluable_con_la_ruta(tmp_path):
    """L-QW.3 / R2.9: la abstencion nombra la ruta buscada y no afirma divergencia."""
    raiz_vacia = tmp_path / "sin-corpus"
    raiz_vacia.mkdir()
    ruta = DOC_SIN_FECHA[0]
    with pytest.raises(pytest.fail.Exception) as exc:
        _revisar_materializacion([raiz_vacia], DOC_SIN_FECHA)
    mensaje = str(exc.value)
    assert NO_EVALUABLE in mensaje, mensaje
    assert ruta in mensaje, f"la abstencion no nombra la ruta buscada: {mensaje}"
    assert "divergencia" not in mensaje.lower(), (
        f"la abstencion esta afirmando una divergencia: {mensaje}")
    # Corte positivo: sobre el arbol real la misma revision no falla (sin el, el diente seria verde
    # por ausencia de poblacion).
    _revisar_materializacion([ROOT], DOC_SIN_FECHA)
