"""Tests de `scripts/validate_lesson_capitalization.py` (Paso 0 del executor, v2.22.0).

Mismo principio que las suites de `validate_plan_closure.py` y `validate_plan_citations.py`:
un validador que nunca se dispara es letra muerta, y uno que se dispara sobre un fixture
que nadie escribió tampoco vale. Por eso este archivo hace tres cosas:

- arranca de un artefacto **conforme** y degrada una sola dimensión por test (así cada rojo
  señala al check que existe para cazar esa forma de trampa, y no a un typo del fixture);
- fuerza los **tres estados** de R2.9 sobre el propio verificador: `AUSENTE`, `SIN-HALLAZGOS`
  y `LECTOR-FALLIDO`, y comprueba que del tercero **no** sale un verde (L-PF10);
- corre una vez contra el **árbol real del repo**, no solo contra fixtures (R2.6/L-B1).
"""

import hashlib
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

CONTEXTO = {
    "CONTEXT-FT-A.md": (
        "# Contexto del fixture A\n\n"
        "| ID | Enunciado | Sección |\n|----|-----------|---------|\n"
        "| L-FT-A1 | Primera leccion del fixture, con texto bastante largo | 1. x |\n"
    ),
    "CONTEXT-FT-B.md": (
        "# Contexto del fixture B\n\n"
        "| ID | Enunciado | Sección |\n|----|-----------|---------|\n"
        "| L-FT-B1 | Segunda leccion del fixture, con texto bastante largo | 1. y |\n"
    ),
}

MAESTRO = """# 01 — Plan maestro del fixture

## 6. Criterios de aceptación

| AC | Fase | Criterio | Artefacto y clave |
|----|------|----------|-------------------|
| AC-F1 | V2 | El check C4 existe | evidencia/FASE-V2 |
| AC-F2 | V2 | El check C7 existe | evidencia/FASE-V2 |
"""

CONFORME = """# Lecciones Capitalizadas — PLAN-FT-2026-09-12

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado |
|---|------|------------------|-----------|
| Q1 | Índice generado | `grep -in "leccion" .opencode/LECCIONES-INDEX.md` | 2 IDs |
| Q2 | Notebook QMind | `qmind retrieve --nb fixture -q "consulta" --format agent` | 1 fuente |

## 2. Lecciones capitalizadas

| ID | Enunciado | Definida en | Qué cambia en ESTE plan | Dónde se aplica |
|----|-----------|-------------|-------------------------|-----------------|
| L-FT-A1 | Primera | `context/CONTEXT-FT-A` | Fija el criterio AC-F1 | AC-F1 |
| L-FT-B1 | Segunda | `context/CONTEXT-FT-B` | Cambia AC-F2 | AC-F2 |

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-FT-A1 | motivo uno, medido |
| L-FT-B1 | motivo dos, medido |
| L-FT-A1 | motivo tres, medido |

## 4. Cobertura declarada de este documento

- Verificador mecánico sobre este archivo: `validate_lesson_capitalization.py`.
- No verifico la pertinencia de estas filas.
"""


def _corpus(
    tmp_path: Path,
    artefacto: str | None = CONFORME,
    maestro: str | None = MAESTRO,
    plan_nombre: str = PLAN,
    archives: bool = False,
) -> tuple[Path, Path]:
    """Árbol mínimo: corpus de definiciones en `context/` y un plan bajo `plans/`."""
    plans = tmp_path / "plans"
    context = tmp_path / "context"
    plans.mkdir(parents=True, exist_ok=True)
    context.mkdir(parents=True, exist_ok=True)
    for nombre, cuerpo in CONTEXTO.items():
        (context / nombre).write_text(cuerpo, encoding="utf-8")
    plan = plans / plan_nombre
    plan.mkdir(parents=True, exist_ok=True)
    if artefacto is not None:
        (plan / vlc.ARTIFACTO).write_text(artefacto, encoding="utf-8")
    if maestro is not None:
        (plan / vlc.MAESTRO).write_text(maestro, encoding="utf-8")
    if archives:
        viejo = plans / "Archives" / "PLAN-VIEJO-2026-01-01"
        viejo.mkdir(parents=True, exist_ok=True)
    return plans, context


def _violar(tmp_path: Path, **kwargs) -> list[vlc.Violacion]:
    plans, context = _corpus(tmp_path, **kwargs)
    violaciones, _ = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False)
    return violaciones


def _hay(vs: list[vlc.Violacion], check: str, estado: str | None = None) -> bool:
    return any(v.check == check and (estado is None or v.estado == estado) for v in vs)


# ------------------------------------------------------------------ control positivo


def test_artefacto_conforme_no_produce_ninguna_violacion(tmp_path: Path):
    """Sin este control, todos los rojos de abajo podrían ser culpa del fixture."""
    assert _violar(tmp_path) == []


# ------------------------------------------------------------------------------- C1


def test_c1_plan_en_alcance_sin_artefacto_declara_ausente_con_su_ruta(tmp_path: Path):
    vs = _violar(tmp_path, artefacto=None)
    assert _hay(vs, "C1", "AUSENTE"), vs
    assert any(vlc.ARTIFACTO in v.mensaje for v in vs)


def test_c1_artefacto_ilegible_es_lector_fallido_y_no_ausente(tmp_path: Path):
    plans, context = _corpus(tmp_path, artefacto=None)
    (plans / PLAN / vlc.ARTIFACTO).write_bytes(b"\xff\xfe\x00\x01 no es utf-8")
    vs, _ = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False)
    assert _hay(vs, "C1", "LECTOR-FALLIDO"), vs
    assert not _hay(vs, "C1", "AUSENTE")


# ------------------------------------------------------------------------------- C2


def test_c2_sin_seccion_tres_no_hay_descartes_que_contar(tmp_path: Path):
    roto = CONFORME.replace("## 3. Candidatos evaluados y descartados", "## 3x. Candidatos")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C2"), vs


# ------------------------------------------------------------------------------- C3


def test_c3_consultas_que_solo_miran_al_predecesor_no_cuentan(tmp_path: Path):
    """La señal que originó el encargo: un Paso 0 que solo leyó al plan de al lado."""
    roto = CONFORME.replace("| Q1 | Índice generado |", "| Q1 | Plan predecesor |")
    roto = roto.replace("| Q2 | Notebook QMind |", "| Q2 | Plan predecesor |")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C3", "SIN-HALLAZGOS"), vs


def test_c3_consulta_corpus_wide_sin_comando_no_es_reejecutable(tmp_path: Path):
    roto = CONFORME.replace(
        '`grep -in "leccion" .opencode/LECCIONES-INDEX.md`', "revisé el indice generado"
    )
    roto = roto.replace(
        '`qmind retrieve --nb fixture -q "consulta" --format agent`', "consulté el notebook"
    )
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C3", "SIN-HALLAZGOS"), vs


# ------------------------------------------------------------------------------- C4


def test_c4_un_ac_inventado_no_existe_en_el_maestro(tmp_path: Path):
    """Forma válida de AC, pero no declarado en el maestro: la ceremonia con aspecto de efecto."""
    roto = CONFORME.replace("AC-F1", "AC-F9").replace("AC-F2", "AC-F9")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C4", "SIN-HALLAZGOS"), vs
    assert any("no existen en la tabla de ACs" in v.mensaje for v in vs), vs


def test_c4_fila_de_leccion_sin_efecto_nombrado_es_citar_no_capitalizar(tmp_path: Path):
    roto = CONFORME.replace("Fija el criterio AC-F1", "se tuvo en cuenta").replace(
        "Cambia AC-F2", "contexto general"
    )
    roto = roto.replace("| AC-F1 |", "| — |").replace("| AC-F2 |", "| — |")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C4", "SIN-HALLAZGOS"), vs
    assert any("nombra un AC" in v.mensaje for v in vs), vs


def test_c4_maestro_sin_tabla_de_acs_no_puede_dar_verde(tmp_path: Path):
    """R2.9: el lector que no puede operar no se disfraza de artefacto correcto."""
    vs = _violar(tmp_path, maestro="# 01 — Plan maestro sin tablas\n\nSin ACs todavía.\n")
    assert _hay(vs, "C4", "LECTOR-FALLIDO"), vs


def test_c4_maestro_ausente_se_declara_ausente_con_nombre(tmp_path: Path):
    vs = _violar(tmp_path, maestro=None)
    assert _hay(vs, "C4", "LECTOR-FALLIDO"), vs
    assert any(vlc.MAESTRO in v.mensaje for v in vs)


# ------------------------------------------------------------------------------- C5


def test_c5_dos_descartes_no_prueban_que_se_miro_el_corpus(tmp_path: Path):
    cuerpo = re.sub(r"\| L-FT-A1 \| motivo tres, medido \|\n", "", CONFORME)
    assert cuerpo.count("motivo") == 2
    vs = _violar(tmp_path, artefacto=cuerpo)
    assert _hay(vs, "C5", "SIN-HALLAZGOS"), vs
    assert any("≥3" in v.mensaje for v in vs)


# ------------------------------------------------------------------------------- C6


def test_c6_declaracion_que_no_nombra_al_verificador_queda_fosil(tmp_path: Path):
    """El límite de L-NC10: decir «no tengo verificador» cuando ya existe."""
    roto = CONFORME.replace("`validate_lesson_capitalization.py`", "ninguno hasta la fecha")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C6", "SIN-HALLAZGOS"), vs


def test_c6_declaracion_sin_limite_es_un_ok_sin_denominador(tmp_path: Path):
    roto = CONFORME.replace("- No verifico la pertinencia de estas filas.\n", "")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C6", "SIN-HALLAZGOS"), vs


# --------------------------------------------------------------------------- C7 y C8


def test_c7_celda_de_identificacion_que_no_es_un_id_del_corpus(tmp_path: Path):
    """C7a: una fila que empieza con prosa en vez de con un ID no capitaliza nada."""
    roto = CONFORME.replace("| L-FT-A1 | Primera |", "| leido de memoria | Primera |")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C7", "SIN-HALLAZGOS"), vs
    assert any("debe ser un ID del corpus" in v.mensaje for v in vs), vs


def test_c7_id_inventado_no_esta_definido_en_el_corpus(tmp_path: Path):
    roto = CONFORME.replace("| L-FT-A1 | Primera |", "| L-FT-QUE-NO-EXISTE | Primera |")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C7", "SIN-HALLAZGOS"), vs
    assert any("no está definido en el corpus" in v.mensaje for v in vs), vs


def test_c7_dueno_real_distinto_al_publicado_es_una_fila_mal_atribuida(tmp_path: Path):
    """El defecto medido del predecesor: siete filas que citaban a un plan que no las definía."""
    roto = CONFORME.replace("`context/CONTEXT-FT-B`", "`context/CONTEXT-FT-A`")
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C7", "SIN-HALLAZGOS"), vs
    assert any("L-FT-B1" in v.mensaje for v in vs)


def test_c8_todo_de_un_mismo_dueno_no_mira_el_corpus_completo(tmp_path: Path):
    """Un solo dueño = capitalizó una fuente. C8 lo impide con ≥2."""
    roto = CONFORME.replace(
        "| L-FT-B1 | Segunda | `context/CONTEXT-FT-B`", "| L-FT-A1 | Otra | `context/CONTEXT-FT-A`"
    )
    vs = _violar(tmp_path, artefacto=roto)
    assert _hay(vs, "C8", "SIN-HALLAZGOS"), vs
    assert not _hay(vs, "C7"), vs


def test_corpus_sin_definiciones_no_produce_un_verde(tmp_path: Path):
    """Si el índice no encuentra ninguna lección, todo ID citado es un hallazgo, no un OK."""
    plans, context = _corpus(tmp_path)
    for nombre in CONTEXTO:
        (context / nombre).unlink()
    vs, pobo = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False)
    assert _hay(vs, "C7", "SIN-HALLAZGOS"), vs
    assert pobo["alcance"] == [PLAN]


# --------------------------------------------------------------------------- alcance


def test_plan_anterior_al_corte_queda_fuera_y_no_falla_por_faltar_el_artefacto(tmp_path: Path):
    plans, context = _corpus(
        tmp_path, artefacto=None, maestro=None, plan_nombre="PLAN-FT-2026-09-11"
    )
    vs, pobo = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False)
    assert vs == []
    assert pobo["exentos_fecha"] == ["PLAN-FT-2026-09-11"]


def test_archives_queda_fuera_del_alcance_aunque_no_tenga_artefacto(tmp_path: Path):
    plans, context = _corpus(tmp_path, archives=True)
    viejo = plans / "Archives" / "PLAN-VIEJO-2026-01-01"
    assert not (viejo / vlc.ARTIFACTO).exists()
    vs, pobo = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False)
    assert vs == []
    assert pobo["archivados"] == 1


def test_plan_sin_fecha_en_el_nombre_queda_exento_pero_declarado(tmp_path: Path):
    plans, context = _corpus(tmp_path, artefacto=None, maestro=None, plan_nombre="SIN-FECHA")
    vs, pobo = vlc.verificar(plans, context, vlc.date.fromisoformat(CUTOFF), verbose=False)
    assert vs == [], "la exención no puede convertirse en una falla silenciosa"
    assert pobo["exentos_sin_fecha"] == ["SIN-FECHA"]


def test_fecha_invalida_en_el_nombre_no_se_confunde_con_una_fecha(tmp_path: Path):
    assert vlc._fecha_del_plan("PLAN-FT-2026-13-45") is None
    assert vlc._fecha_del_plan("PLAN-FT-2026-09-12") == vlc.date(2026, 9, 12)


# -------------------------------------------------------------- CLI, AC-B1 y AC-B5


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_b1_sin_fix_y_sin_reescribir_los_artefactos(tmp_path: Path):
    plans, context = _corpus(tmp_path, artefacto="# Lecciones sin ninguna sección\n")
    antes = hashlib.sha256((plans / PLAN / vlc.ARTIFACTO).read_bytes()).hexdigest()
    r = _correr("--plans-dir", str(plans), "--context-dir", str(context))
    assert r.returncode == 1
    assert "--fix" not in _correr("--help").stdout
    despues = hashlib.sha256((plans / PLAN / vlc.ARTIFACTO).read_bytes()).hexdigest()
    assert antes == despues, "el verificador reporta, no reescribe"


def test_b5_la_salida_publica_la_poblacion_mirada(tmp_path: Path):
    plans, context = _corpus(tmp_path, archives=True)
    r = _correr("--plans-dir", str(plans), "--context-dir", str(context))
    linea = next(f for f in r.stdout.splitlines() if f.startswith("cobertura:"))
    for fragmento in ("1 plan(es) en alcance", "1 archivados excluidos", "0 exentos por fecha"):
        assert fragmento in linea, linea


def test_exit_code_cero_y_dos_segun_el_estado_del_directorio(tmp_path: Path):
    plans, context = _corpus(tmp_path)
    assert _correr("--plans-dir", str(plans), "--context-dir", str(context)).returncode == 0
    assert _correr("--plans-dir", str(tmp_path / "no-existe")).returncode == 2
    assert _correr("--plans-dir", str(plans), "--cutoff", "no-es-fecha").returncode == 2


# ------------------------------------------------------- R2.6: el artefacto real del repo


def test_los_artefactos_reales_del_repo_pasan_todos_los_checks_aunque_esten_archivados():
    """Contra el árbol versionado, no contra un fixture: es el plan que concibió este script.

    Medido al cerrar este plan: la versión anterior pedía además `pobo["alcance"]` no vacío, y el
    propio `git mv` de R2.5 sacó al plan de alcance. El test puso rojo sin que el artefacto
    hubiera cambiado — el mismo defecto de aserción-anclada-a-una-variable-que-muta que la
    lección L-V3.2. Lo que se quiere observar es la forma del `00-` real, y eso vale igual
    archivado; la no-vacuidad la asegura el conteo de testigos, no la clasificación de alcance.
    """
    owners, indice_motivo = vlc.duenos_del_corpus(vlc.DEFAULT_PLANS, vlc.DEFAULT_CONTEXT)
    planes = sorted({p.parent for p in vlc.DEFAULT_PLANS.rglob(vlc.ARTIFACTO)})
    assert planes, "el repo debe conservar al menos un 00- real que sirva de testigo"
    violaciones: list[vlc.Violacion] = []
    for plan in planes:
        vs, _ = vlc.analizar_plan(plan, vlc.DEFAULT_PLANS, owners, indice_motivo)
        violaciones += vs
    assert violaciones == [], [str(v) for v in violaciones]


@pytest.mark.parametrize(
    "cutoff,plan_esperado", [("2026-09-11", "TRIBUNAL-ENFORCEMENT-OBS-2026-09-11")]
)
def test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme(
    cutoff: str, plan_esperado: str
):
    """Cobertura real del gate sobre el segundo `00-` del repo (medición, no aspiración).

    Atrás del corte a 2026-09-11 para que el predecesor deje de estar exento por fecha: si el
    verde viniera de que nadie lo miró, este test sería decorativo, así que primero exige que
    esté en la población evaluada. **Historia medida**: desde que existió el verificador hasta el
    cierre de FASE-V3 (2026-09-13) este plan devolvía exactamente una violación, C6, porque su §4
    seguía declarando que el verificador no existía. Se corrigió esa declaración en la misma
    fecha en que se publicó el cierre, y ahora lo verificable es la conformidad de su forma — que
    su §2 sea pertinente sigue sin verificarlo ningún check (límite del propio §4).
    """
    vs, pobo = vlc.verificar(
        vlc.DEFAULT_PLANS, vlc.DEFAULT_CONTEXT, vlc.date.fromisoformat(cutoff), verbose=False
    )
    assert plan_esperado in pobo["alcance"], pobo["alcance"]
    del_plan = [v for v in vs if plan_esperado in v.mensaje]
    assert del_plan == [], [str(v) for v in del_plan]


# ---------------------------------------------------------------- cableado (AC-B4)
#
# Motivo medido en la fase: el hook cambio de denominador (5 a 6 a 7) y su contract test
# siguio pinando la etiqueta vieja, asi que el rojo vivio dos commits sin que nadie lo
# declarara. Que el bloqueo funcione «hoy» no prueba que siga funcionando tras renumerar.


def _etiquetas(texto: str) -> list[tuple[int, int]]:
    return [(int(i), int(n)) for i, n in re.findall(r"\[(\d+)/(\d+)\]", texto)]


def test_el_hook_versionado_invoca_el_script_y_su_numeracion_no_tiene_huecos():
    src = (ROOT / "scripts" / "git_hooks" / "pre-commit").read_text(encoding="utf-8")
    assert "validate_lesson_capitalization.py" in src
    etiquetas = _etiquetas(src)
    assert etiquetas, "el hook ya no numera sus checks"
    denominadores = {n for _, n in etiquetas}
    assert len(denominadores) == 1, f"denominadores mezclados en el hook: {denominadores}"
    n = denominadores.pop()
    assert sorted({i for i, _ in etiquetas}) == list(
        range(1, n + 1)
    ), f"ordinales rotos: {etiquetas}"


def test_run_all_validations_registra_el_check_dentro_del_modo_rapido():
    src = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
    assert src.index("self._check_lesson_capitalization()") < src.index("if not self.quick:")
    assert "[10/10] Checking lesson capitalization" in src
    rapidos = {n for i, n in _etiquetas(src) if i <= 10}
    assert rapidos == {10}, f"los checks del modo rapido comparten denominador: {rapidos}"
