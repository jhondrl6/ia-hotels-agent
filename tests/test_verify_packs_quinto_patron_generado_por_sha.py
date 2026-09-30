"""S19(d), salida (c): quinto patron de `NORMALIZAR` + emision de `generado_por_sha`.

La fila (DF §S19, sello 2026-09-28 del C6) midio que el verificador del arbol commiteado normaliza
cuatro tokens y ninguno cubre la identidad del generador, mientras que el sha del propio escritor **si**
se mueve entre commits (cuatro revisiones + el arbol de trabajo: 4 valores sobre 5 mediciones). Publicar
el campo sin anadir el patron produce `DIVERGE` entre revisiones correctas — el mismo defecto de
instrumento que §S20 documento para el clon.

Anclajes, los dos de revision **publicada y fija** (nunca HEAD):
- `7737347` es la revision cuyo verificador todavia tiene CUATRO patrones: el control negativo lo lee con
  `git show` y lo ejecuta, asi que el rojo sale del instrumento versionado y no de una parodia escrita aqui.
- `3c2e6a3` es la revision que tiene el plan bajo `Archives/` (la forma de ruta que `resolver_plan()` ya
  gobierna); su arbol se materializa y se le superpone el escritor curado.

Lo que este archivo NO afirma: que la identidad publicada gobierne frescura. `generado_por_sha` es
procedencia no gobernante (AC21 hace lo mismo con `head`), y
`test_la_emision_no_entra_en_la_llave_de_frescura` lo cortaria si se colara en `sources[]`.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VERIFICADOR = SCRIPTS / "verify_packs_in_committed_tree.py"
ESCRITOR = SCRIPTS / "build_phase_briefing.py"
sys.path.insert(0, str(SCRIPTS))
from verify_index_in_committed_tree import clon_fiel  # noqa: E402

REV_SIN_QUINTO_PATRON = "7737347"    # el verificador versionado, con cuatro patrones
REV_ARBOLE = "3c2e6a3"               # el plan bajo Archives/
PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
CLAVE = "generado_por_sha"
EMISION = '"generado_por_sha": _sha_del_escritor(),'
META_RE = re.compile(r"<!-- BEGIN BRIEFING-META\n(.*?)\nEND BRIEFING-META -->", re.S)
SHA_FALSA = "d" * 64
# El literal del quinto patron, armado por partes: si quedara contiguo en esta prueba, el lector de
# gobernanza podria tomarlo por un emisor (misma convencion que `test_run_all_validations_..._por_modo`).
PATRON_QUINTO = CLAVE + '": "[0-9a-f]{7,}"'


def _rev_existe(rev: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(ROOT), capture_output=True,
    ).returncode == 0


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    anterior = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = anterior
    return mod


def _sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _meta_de(texto: str) -> dict:
    m = META_RE.search(texto)
    assert m, "el pack no trae bloque BRIEFING-META: no hay de donde leer la identidad"
    return json.loads(m.group(1))


def _linea_meta(valor_sha: str) -> str:
    """Una linea de meta como la imprime el escritor: `"generado_por_sha": "<sha>"`.

    Las comillas de la clave se arman por partes, igual que `PATRON_QUINTO`: un literal contiguo de
    clave-valor puede leerse como si este archivo emitiera la etiqueta que goberna gobernanza.
    """
    return ('  "generado_por": "scripts/build_phase_briefing.py",\n  "' + CLAVE + '": "'
            + valor_sha + '"\n')


def _quitar_enlace(ruta: Path) -> None:
    """`git clone --local` enlaza objetos: hay que desvincular antes de escribir, o se muta el repo."""
    if ruta.exists():
        ruta.unlink()


def _generar_en(cwd: Path, plan: str, destino: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ESCRITOR if cwd == ROOT else cwd / "scripts" / "build_phase_briefing.py"),
         "--plan", plan, "--briefing-dir", str(destino)],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8", errors="replace")


# ------------------------------------------------------- (1) emision del escritor, sobre el arbol real

def test_el_escritor_emite_su_identidad_en_los_cinco_packs(tmp_path):
    """Cada pack que emite el escritor lleva `generado_por_sha` = sha256 de su propio archivo."""
    corrida = _generar_en(ROOT, PLAN, tmp_path / "briefing")
    assert corrida.returncode in (0, 1), corrida.stdout[-500:] + corrida.stderr[-300:]
    packs = sorted((tmp_path / "briefing").glob("FASE-*.md"))
    assert len(packs) == 5, f"se esperaban cinco packs y salieron {len(packs)}: {corrida.stdout[-500:]}"
    esperado = _sha(ESCRITOR)
    for pack in packs:
        meta = _meta_de(pack.read_text(encoding="utf-8", errors="replace"))
        assert meta.get(CLAVE) == esperado, (
            f"{pack.name}: la identidad publicada es {meta.get(CLAVE)!r}, no el sha del escritor "
            f"{esperado!r} — el campo no se esta calculando sobre el archivo que corri")
        # `generado_por` sigue siendo la ruta declarada: la cura no sustituye al miembro viejo.
        assert meta["generado_por"] == "scripts/build_phase_briefing.py"


def test_la_emision_no_entra_en_la_llave_de_frescura(tmp_path):
    """`--check` tiene que seguir dando verde: el campo es procedencia, no fuente gobernada.

    Si alguien lo metiera en `sources[]`, cada edicion del escritor re-venceria los cinco packs de golpe
    — el coste que el §5 del parte 19- midio para descartar la salida (a).
    """
    _generar_en(ROOT, PLAN, tmp_path / "briefing")
    for pack in sorted((tmp_path / "briefing").glob("FASE-*.md")):
        meta = _meta_de(pack.read_text(encoding="utf-8", errors="replace"))
        rutas = [s["ruta"] for s in meta["sources"]]
        assert not any("build_phase_briefing" in r for r in rutas), (
            f"{pack.name}: el escritor se auto-declaro fuente gobernada ({rutas})")
        assert CLAVE in meta, f"{pack.name}: sin la clave no hay nada que sacar de la llave"

    check = subprocess.run(
        [sys.executable, str(ESCRITOR), "--plan", PLAN, "--check"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert check.returncode == 0, (
        "el --check del arbol de trabajo corto rojo: "
        + check.stdout[-600:] + check.stderr[-300:])


# ---------------------------------------------------------------- (2) el patron, a nivel de unidad

def test_el_quinto_patron_estabiliza_la_identidad_del_generador():
    """Dos textos que difieren SOLO en `generado_por_sha` casan; sin el patron, no.

    La segunda mitad es el control anti-verde-vacio: si los digirios fueran iguales incluso con cuatro
    patrones, la prueba superior no estaria afirmando nada del quinto.
    """
    ver = _cargar("verif_packs_unidad", VERIFICADOR)
    a = _linea_meta("a" * 64)
    b = _linea_meta("b" * 64)
    assert ver._digest(a) == ver._digest(b), (
        "el verificador ya no normaliza la identidad del generador: dos revisiones correctas del mismo "
        "plan divergirian por el sha del escritor, que es el defecto de instrumento de §S20")

    sin_quinto = [(p, r) for (p, r) in ver.NORMALIZAR if PATRON_QUINTO not in p.pattern]
    assert len(sin_quinto) == len(ver.NORMALIZAR) - 1, (
        "el filtro del control no quito exactamente un patron: la comparacion de abajo no significa nada")

    def digest_sin(texto: str) -> str:
        for patron, reemplazo in sin_quinto:
            texto = patron.sub(reemplazo, texto)
        return hashlib.sha256(texto.encode("utf-8")).hexdigest()

    assert digest_sin(a) != digest_sin(b), (
        "sin el quinto patron los dos textos IGUAL casan: el patron no hacia nada y la prueba superior "
        "es un verde vacio")


# ----------------------------------------- (3) el arbol con la identidad movida, y sus dos lecturas

def _fuente_versionada(destino: Path, rev: str, rel: str) -> Path:
    proc = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True, text=True,
                          encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, f"no se pudo leer {rel} en {rev}: {proc.stderr[:200]}"
    ruta = destino / Path(rel).name
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(proc.stdout, encoding="utf-8", newline="\n")
    return ruta


@pytest.fixture(scope="module")
def arbol_con_identidad_movida(tmp_path_factory):
    """Arbol evaluable donde el pack publicado y el regenerado difieren SOLO en `generado_por_sha`.

    Secuencia: materializar `3c2e6a3` con `clon_fiel` (S20), superponerle el escritor curado del arbol de
    trabajo, generar los packs ahi (identidad = sha real del archivo), y despues parchar el escritor para
    que emita otra identidad. El verificador regenera con el parchado: la unica diferencia entre los dos
    lados es el campo de la cura.
    """
    assert _rev_existe(REV_ARBOLE), f"la revision {REV_ARBOLE} no esta en el repositorio"
    base = tmp_path_factory.mktemp("s19d") / "clon"
    clon, motivo = clon_fiel(base, REV_ARBOLE)
    assert clon is not None, f"el arbol de {REV_ARBOLE} no fue evaluable: {motivo}"
    raiz_plan = clon / ".opencode" / "plans" / "Archives" / PLAN
    assert raiz_plan.is_dir(), f"premissa del control: {PLAN} debe estar bajo Archives/"

    escritor_clon = clon / "scripts" / "build_phase_briefing.py"
    fuente_curada = ESCRITOR.read_text(encoding="utf-8")
    assert fuente_curada.count(EMISION) == 1, (
        "el escritor del arbol de trabajo no emite la identidad con el literal esperado: el control "
        "no tendria nada que parchar")
    _quitar_enlace(escritor_clon)
    escritor_clon.write_text(fuente_curada, encoding="utf-8", newline="\n")

    corrida = _generar_en(clon, PLAN, raiz_plan / "briefing")
    assert corrida.returncode in (0, 1), corrida.stdout[-600:] + corrida.stderr[-300:]
    packs = sorted((raiz_plan / "briefing").glob("FASE-*.md"))
    assert len(packs) == 5, f"el escritor no produjo los cinco packs en el clon: {corrida.stdout[-600:]}"
    publicados = set()
    for pack in packs:
        meta = _meta_de(pack.read_text(encoding="utf-8", errors="replace"))
        assert re.fullmatch(r"[0-9a-f]{64}", str(meta.get(CLAVE))), (
            f"{pack.name}: el escritor superpuesto no emite la identidad ({meta.get(CLAVE)!r})")
        publicados.add(meta[CLAVE])
    assert len(publicados) == 1, "los cinco packs deberian declarar la misma identidad de generador"
    assert SHA_FALSA not in publicados, "la identidad falsa ya estaba publicada antes del parche"

    parchado = fuente_curada.replace(EMISION, f'"{CLAVE}": "{SHA_FALSA}",', 1)
    assert parchado != fuente_curada, "el parche no movio la identidad: el control no ejercita nada"
    # El mutante se verifica sintacticamente antes de fiarse de su rojo: la primera version de este
    # parche inyectaba una constante al principio del archivo y `from __future__` dejo de ser la primera
    # sentencia. El escritor moria con rc=1, que el verificador admite, y el veredicto salia
    # `NO-PRODUCIDO` en vez del `DIVERGE` que se queria medir.
    ast.parse(parchado)
    _quitar_enlace(escritor_clon)
    escritor_clon.write_text(parchado, encoding="utf-8", newline="\n")
    return clon


def _correr_verificador(script: Path, clon: Path, rev: str) -> subprocess.CompletedProcess:
    """`PYTHONPATH=scripts` porque la copia del instrumento versionado vive en un temporal: su propio
    `sys.path.insert` apunta a ese temporal y de ahi no importa a sus hermanos.

    Sin esto el rojo del control seria `ModuleNotFoundError` — un fallo del arnes, no del instrumento
    (la familia de «rojo de herramienta que no ve su insumo»).
    """
    env = dict(os.environ, PYTHONPATH=str(SCRIPTS))
    return subprocess.run(
        [sys.executable, str(script), "--rev", rev, "--clon", str(clon)],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)


def test_un_arbol_cuya_identidad_del_generador_se_mueve_reproduce(arbol_con_identidad_movida):
    """Con el quinto patron, el verificador APRUEBA el arbol: los packs se reproducen."""
    corrida = _correr_verificador(VERIFICADOR, arbol_con_identidad_movida, REV_ARBOLE)
    salida = corrida.stdout + corrida.stderr
    assert corrida.returncode == 0, (
        "el verificador curado corto rojo sobre un arbol cuya unica diferencia es la identidad del "
        f"generador — el defecto de §S20 reaparecio:\n{salida[-800:]}")
    assert "5/5 reproducidos" in salida, salida[-800:]


def test_control_negativo_el_instrumento_versionado_sin_quinto_patron_diverge(
        arbol_con_identidad_movida, tmp_path):
    """El mismo arbol, con el verificador leido de `7737347` (cuatro patrones): `DIVERGE`.

    El rojo del instrumento viejo no acusa al commit: nombra la clave que no sabe estabilizar. Eso es lo
    que hay que leer para no confundir la prueba superior con un verde que pasa por accidente.
    """
    viejo = _fuente_versionada(tmp_path / "instrumento-viejo", REV_SIN_QUINTO_PATRON,
                               "scripts/verify_packs_in_committed_tree.py")
    fuente = viejo.read_text(encoding="utf-8")
    assert CLAVE not in fuente, (
        f"{REV_SIN_QUINTO_PATRON} ya normaliza la identidad del generador: el control dejo de ser "
        "anterior a la cura")
    assert fuente.count("re.compile(") >= 4, "el instrumento versionado perdio sus cuatro patrones"

    corrida = _correr_verificador(viejo, arbol_con_identidad_movida, REV_ARBOLE)
    salida = corrida.stdout + corrida.stderr
    assert corrida.returncode == 1, (
        "el instrumento versionado APROBO el mismo arbol que el curado aprueba: o el quinto patron no "
        f"hace falta, o el control no esta ejercitando nada:\n{salida[-800:]}")
    assert "DIVERGE" in salida, salida[-800:]
    assert CLAVE in salida, (
        f"el divergido no nombra la identidad del generador: no es el campo que se esperaba "
        f"que el patron viejo no supiera estabilizar:\n{salida[-800:]}")
