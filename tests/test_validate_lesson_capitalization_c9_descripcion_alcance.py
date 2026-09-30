"""C9 — la DESCRIPCION del alcance contrastada con lo que el codigo ejerce (sub-punto de §S29).

Fila 10 del registro unificado del 2026-09-29. Lo medido el 2026-09-27: revertir el parrafo vencido del
§2.5 del workflow **NO producia rojo** (`SIN-HALLAZGOS`, 79 passed, quick 13/13). Gobernar el
comportamiento no goberna la descripcion del comportamiento, y nadie avisaba cuando la descripcion se
desfasaba.

Los dos anclajes de este archivo son revisiones publicadas **fijas**, nunca HEAD:
- `84282c1^` — el clasificador anterior a la cura a-prima, que todavia saltaba `Archives/` por estructura.
- `7737347`  — el instrumento versionado sin C9 (la revision de anclaje del Paso 0 de la orden del 2026-09-30).

No se re-numera ni el quick ni el hook: el check nuevo vive dentro de `validate_lesson_capitalization.py`,
que ya esta cableado, y su codigo no pertenece a la familia `C1..C8` de los artefactos (esos describen el
`00-`; este describe el workflow).

Se re-declara el arbol minimo en vez de importar los helpers de
`tests/test_validate_lesson_capitalization.py`: ese archivo es una bateria, no un soporte compartido, y
importarlo arrastraria sus fixtures a esta coleccion.
"""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_lesson_capitalization.py"
sys.path.insert(0, str(ROOT / "scripts"))

import validate_lesson_capitalization as vlc  # noqa: E402

PLAN = "PLAN-FT-2026-09-12"
CUTOFF = "2026-09-12"
REV_CLASIFICADOR_SIN_CURA = "84282c1^"
REV_INSTRUMENTO_SIN_C9 = "7737347"

CONTEXTO = {
    "CONTEXT-FT-A.md": (
        "# Contexto del fixture A\n\n"
        "| ID | Enunciado | Seccion |\n|----|-----------|---------|\n"
        "| L-FT-A1 | Primera leccion del fixture, con texto bastante largo | 1. x |\n"
    ),
    "CONTEXT-FT-B.md": (
        "# Contexto del fixture B\n\n"
        "| ID | Enunciado | Seccion |\n|----|-----------|---------|\n"
        "| L-FT-B1 | Segunda leccion del fixture, con texto bastante largo | 1. y |\n"
    ),
}

MAESTRO = """# 01 — Plan maestro del fixture

## 6. Criterios de aceptacion

| AC | Fase | Criterio | Artefacto y clave |
|----|------|----------|-------------------|
| AC-F1 | V2 | El check C4 existe | evidencia/FASE-V2 |
| AC-F2 | V2 | El check C7 existe | evidencia/FASE-V2 |
"""

# El artefacto conforme no le importa a C9 (el corpus de plans se construye conforme para que NINGUN
# hallazgo de esta seccion pueda atribuirse a un fixture roto).
ARTIFACTO_CONFORME = """# Lecciones Capitalizadas — PLAN-FT-2026-09-12

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado |
|---|------|------------------|-----------|
| Q1 | Indice generado | `python scripts/build_lesson_index.py` | 3 candidatos |

## 2. Lecciones capitalizadas

| ID | Definida en | Enunciado | Que cambia en este plan |
|----|-------------|-----------|-------------------------|
| L-FT-A1 | `context/CONTEXT-FT-A` | Primera | Fija el criterio AC-F1 |
| L-FT-B1 | `context/CONTEXT-FT-B` | Segunda | Fija el criterio AC-F2 |

## 3. Candidatos evaluados y descartados

| ID | Motivo del descarte |
|----|---------------------|
| L-FT-A1 | motivo uno, medido |
| L-FT-B1 | motivo dos, medido |
| OTRO | motivo tres, medido |

## 4. Limite del verificador

Se uso `validate_lesson_capitalization.py`. No verifico la pertinencia de estas filas.
"""

# Las dos polaridades que el parrafo gobernado puede afirmar, en la forma exacta en que viven en el
# workflow: la cura a-prima de §S29 y el texto que la precedio.
ENCABEZADO = ("# Workflow de prueba (texto gobernado por C9)\n\n"
              "- **Alcance hacia delante** (misma politica que `validate_plan_citations.py`, "
              "decision DA-HF3): ")
CIERRE = "\n- **Lo que NO verifica**: la pertinencia.\n"

AFIRMA_CUTOFF = ("manda el **cutoff de fecha, no la carpeta**. Estan en alcance los planes cuyo nombre "
                 "lleva fecha `>= 2026-09-12`, **esten o no bajo `Archives/`**; los anteriores al corte "
                 "quedan exentos por su fecha, no por su ubicacion. Desde el commit `84282c1` la carpeta "
                 "`Archives/` es un marcador de corpus y **no** una exclusion.")

AFIRMA_CARPETA = ("manda el cutoff de fecha. Estan en alcance los planes cuyo nombre lleva fecha "
                  "``>= 2026-09-12`` y que no esten en `Archives/`; los archivados excluidos se cuentan "
                  "aparte y la linea de cobertura imprime `archivados excluidos`.")


def _corpus(tmp_path: Path) -> tuple[Path, Path]:
    plans = tmp_path / "plans"
    context = tmp_path / "context"
    plans.mkdir(parents=True, exist_ok=True)
    context.mkdir(parents=True, exist_ok=True)
    for nombre, cuerpo in CONTEXTO.items():
        (context / nombre).write_text(cuerpo, encoding="utf-8")
    plan = plans / PLAN
    plan.mkdir(parents=True, exist_ok=True)
    (plan / vlc.ARTIFACTO).write_text(ARTIFACTO_CONFORME, encoding="utf-8", newline="\n")
    (plan / vlc.MAESTRO).write_text(MAESTRO, encoding="utf-8", newline="\n")
    return plans, context


def _hay(violaciones: list[vlc.Violacion], check: str, estado: str | None = None) -> bool:
    return any(v.check == check and (estado is None or v.estado == estado) for v in violaciones)


def _texto_gobernado(tmp_path: Path, afirmacion: str, nombre: str = "workflow.md") -> Path:
    doc = tmp_path / nombre
    doc.write_text(ENCABEZADO + afirmacion + CIERRE, encoding="utf-8", newline="\n")
    return doc


def _fuente_versionada(destino: Path, rev: str) -> Path:
    proc = subprocess.run(["git", "show", f"{rev}:scripts/validate_lesson_capitalization.py"],
                          capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
    assert proc.returncode == 0, f"no se pudo leer el versionado en {rev}: {proc.stderr[:200]}"
    destino.write_text(proc.stdout, encoding="utf-8", newline="\n")
    return proc.stdout, destino


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


def _violar_con_texto(tmp_path: Path, afirmacion: str):
    plans, context = _corpus(tmp_path)
    texto = _texto_gobernado(tmp_path, afirmacion)
    violaciones, poblacion = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF),
                                          verbose=False, gobernados=[texto])
    return violaciones, poblacion


# ------------------------------------------------------------------ los dos lados del contraste

def test_el_corpus_base_sin_parrafo_gobernado_esta_conforme(tmp_path):
    """Premisa de toda la seccion: el corpus scratch pasa C1..C8, asi que ningun rojo es del fixture."""
    plans, context = _corpus(tmp_path)
    violaciones, _ = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False,
                                  gobernados=[])
    sin_c9 = [v for v in violaciones if v.check != "C9"]
    assert sin_c9 == [], [str(v) for v in sin_c9]


def test_c9_el_parrafo_que_describe_la_exclusion_por_carpeta_pierde(tmp_path):
    """El texto historico del §2.5 (pre-cura) contra el codigo curado: DESCRIPCION-VENCIDA."""
    violaciones, _ = _violar_con_texto(tmp_path, AFIRMA_CARPETA)
    assert _hay(violaciones, "C9", "DESCRIPCION-VENCIDA"), [str(v) for v in violaciones]


def test_c9_el_parrafo_conforme_gana(tmp_path):
    """El texto curado, reproducido en scratch: sin hallazgos de C9."""
    violaciones, _ = _violar_con_texto(tmp_path, AFIRMA_CUTOFF)
    assert not _hay(violaciones, "C9"), [str(v) for v in violaciones]


# --------------------------------------------------------------------- el criterio sale del codigo

def test_la_sonda_de_regla_vigente_lee_el_comportamiento(tmp_path):
    """`regla_vigente_del_alcance` mide ejecutando `clasificar_planes`, no leyendo su prosa."""
    assert vlc.regla_vigente_del_alcance(vlc.date.fromisoformat(CUTOFF)) == "cutoff", (
        "la sonda ya no ve la cura a-prima: o se revirtio `clasificar_planes` sin tocar esta prueba, "
        "o la sonda dejo de ejecutar el clasificador")


def test_c9_se_cae_cuando_el_codigo_revierte_la_cura(tmp_path, monkeypatch):
    """El MISMO parrafo conforme pasa a ser la descripcion vencida si el clasificador vuelve atras.

    El clasificador viejo se lee de `84282c1^` con `git show` (instrumento versionado, no una parodia
    escrita aqui) y se monta en el modulo. Si el check dependiera de una cadena fija del workflow, aqui
    daria verde y la gobernanza seria de adorno.
    """
    fuente, viejo = _fuente_versionada(tmp_path / "vlc_pre_cura.py", REV_CLASIFICADOR_SIN_CURA)
    assert 'if hijo.name == "Archives":' in fuente and "_encasillar(plan, cutoff, grupos)" not in fuente, (
        f"{REV_CLASIFICADOR_SIN_CURA} ya no salta `Archives/` por estructura: el anclaje perdio su "
        "premissa y el control no ejercita la reversion")
    modulo = _cargar("vlc_pre_cura", viejo)

    monkeypatch.setattr(vlc, "clasificar_planes", modulo.clasificar_planes)
    assert vlc.regla_vigente_del_alcance(vlc.date.fromisoformat(CUTOFF)) == "carpeta", (
        "la sonda no detecto la reversion del clasificador: el check no esta midiendo el codigo")

    violaciones, _ = _violar_con_texto(tmp_path, AFIRMA_CUTOFF)
    assert _hay(violaciones, "C9", "DESCRIPCION-VENCIDA"), (
        "con la cura revertida el parrafo que afirma cutoff sigue verde: el check goberna literales, "
        "no el reparto real del corpus")


# ------------------------------------------------------------------------- los tres estados (R2.9)

def test_c9_sin_parrafo_que_leer_declara_ausente_y_no_un_verde(tmp_path):
    """Un texto sin el rotulo de alcance no puede aprobarse a si mismo (verde vacio)."""
    plans, context = _corpus(tmp_path)
    doc = tmp_path / "workflow-sin-parrafo.md"
    doc.write_text("# Workflow sin el rotulo de alcance\n\nnada\n", encoding="utf-8", newline="\n")
    violaciones, _ = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF),
                                   verbose=False, gobernados=[doc])
    assert _hay(violaciones, "C9", "AUSENTE"), [str(v) for v in violaciones]


def test_c9_lectores_fallidos_se_nombran_como_tales(tmp_path):
    """Un texto que no existe es `LECTOR-FALLIDO` con la ruta, no `AUSENTE` disfrazado."""
    plans, context = _corpus(tmp_path)
    violaciones, _ = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False,
                                   gobernados=[tmp_path / "no-existe.md"])
    assert _hay(violaciones, "C9", "LECTOR-FALLIDO"), [str(v) for v in violaciones]


def test_c9_poblacion_vacia_no_es_verde():
    """Cero textos gobernados es un limite del metodo y se declara."""
    assert _hay(vlc.c9_descripcion_del_alcance([], vlc.date.fromisoformat(CUTOFF)), "C9", "AUSENTE")


def test_c9_la_salida_publica_su_poblacion(tmp_path):
    """Cuantos textos se gobernarón y con que regla vigente, en la linea de cobertura (L-HF1)."""
    _, poblacion = _violar_con_texto(tmp_path, AFIRMA_CUTOFF)
    assert poblacion["regla_del_alcance"] == "cutoff"
    assert len(poblacion["gobernados"]) == 1
    linea = vlc._linea_de_cobertura(poblacion, vlc.date.fromisoformat(CUTOFF))
    assert "descripcion del alcance: regla=cutoff en 1 texto(s) gobernado(s)" in linea, linea


# -------------------------------------------------------------------------------- el arbol real

def test_c9_sobre_los_dos_textos_reales_del_repo_no_da_hallazgos():
    """El workflow y su copia congelada, leidos como estan en disco: conformes y gobernados.

    Esta es la prueba de que la regla no se monto sobre el corpus viejo tirando el arbol (la familia de
    «regla nueva se choca contra el corpus viejo»): los dos textos gobernados hoy afirman cutoff y el
    codigo ejerce cutoff.
    """
    r = subprocess.run([sys.executable, str(SCRIPT), "--quiet"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "descripcion del alcance: regla=cutoff en 2 texto(s) gobernado(s)" in r.stdout, r.stdout


def test_control_negativo_el_instrumento_versionado_es_ciego_al_parrafo(tmp_path):
    """El mismo parrafo vencido, con el verificador commiteado en `7737347`: verde.

    Se lee y se ejecuta el archivo versionado (`git show`, solo lectura). Su verde sobre el corpus de
    scratch demuestra que la ceguera era del instrumento y no del fixture, y que el rojo de
    `test_c9_el_parrafo_que_describe_la_exclusion_por_carpeta_pierde` lo produce exactamente el check
    nuevo. La comparacion es entre los DOS sobre el mismo corpus, nunca contra HEAD.
    """
    fuente, viejo = _fuente_versionada(tmp_path / "vlc_versionado.py", REV_INSTRUMENTO_SIN_C9)
    assert "--goberna" not in fuente and "c9_descripcion_del_alcance" not in fuente, (
        "el instrumento versionado ya goberna la descripcion: el control no ejercita la ceguera")

    plans, context = _corpus(tmp_path)
    texto = _texto_gobernado(tmp_path, AFIRMA_CARPETA)

    curado = subprocess.run([sys.executable, str(SCRIPT), "--plans-dir", str(plans),
                             "--context-dir", str(context), "--quiet", "--goberna", str(texto)],
                            capture_output=True, text=True)
    assert curado.returncode == 1, curado.stdout + curado.stderr
    assert "C9=1" in curado.stdout, curado.stdout   # el resumen cuenta el check; con --quiet
    #   las violaciones individuales no se listan, asi que el rojo se afirma por su codigo y su cuenta

    # `PYTHONPATH=scripts` porque la copia versionada vive en un temporal y `duenos_del_corpus` importa
    # `build_lesson_index` desde el directorio de su propio `__file__`: sin esta ruta el instrumento
    # copia no ve su insumo y devuelve dos `C7` que no son del corpus, sino de donde esta parado el guion
    # («rojo de herramienta que no ve su insumo», leccion de la casa).
    env = dict(os.environ, PYTHONPATH=str(ROOT / "scripts"))
    ciego = subprocess.run([sys.executable, str(viejo), "--plans-dir", str(plans),
                            "--context-dir", str(context), "--quiet"],
                           capture_output=True, text=True, env=env)
    assert ciego.returncode == 0, (
        f"el versionado tambien corto rojo, asi que el rojo del curado no atribuye al check nuevo:\n"
        f"{ciego.stdout[-600:]}")
    assert "C9" not in ciego.stdout, ciego.stdout[-600:]


# ---------------------------------------------------------------------- sin re-numerar quick ni hook

def test_c9_no_renumera_el_quick_ni_el_hook(tmp_path):
    """El check nuevo vive DENTRO del check ya cableado: los denominadores no se mueven.

    Leido de la estructura del runner y del hook, no de una cota magicada (misma tecnica que
    `test_run_all_validations_registra_el_check_dentro_del_modo_rapido`).
    """
    runner = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
    cuerpo_rapido = runner.split("if not self.quick:", 1)[0]
    invocados = re.findall(r"self\.(_check_\w+)\(\)", cuerpo_rapido)
    assert "self._check_lesson_capitalization()" in invocados or \
        "_check_lesson_capitalization" in runner.split("if not self.quick:", 1)[0], (
        "el check del Paso 0 salio del rapido: su verde ya no diria nada de C9")
    assert len(invocados) == 13, f"el rapido dejo de tener 13 checks: {len(invocados)}"

    hook = (ROOT / "scripts" / "git_hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "validate_lesson_capitalization.py" in hook
    etiquetas = [(int(i), int(n)) for i, n in re.findall(r"\[(\d+)/(\d+)\]", hook)]
    denominadores = {n for _, n in etiquetas}
    assert len(denominadores) == 1, f"denominadores mezclados en el hook: {denominadores}"
