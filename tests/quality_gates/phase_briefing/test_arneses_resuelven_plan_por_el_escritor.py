"""S31 (fragilidad estructural) — el arnés resuelve el plan **por el escritor**, en las dos formas de la ruta.

Los seis `PLAN` de las selecciones FASE-C y FASE-D estaban pineados a `plans/Archives/<PLAN>` a pelo.
La cura es `tests/support_resolucion_plan.py`: delegar en `resolver_plan()` de
`scripts/build_phase_briefing.py`, que es quien sabe que un plan vive en `plans/`, en
`plans/Archives/` o en la ruta que se le dé.

Dientes anclados a una **revisión fija**, con el precedente de la cura de D-c para el verificador de
packs (`test_el_plan_archivado_posterior_al_corte_entra_en_alcance_sobre_revision_fija` en
`tests/test_validate_lesson_capitalization.py`): un árbol plantado por esta sesión no ejercita ninguna
rama de `git`, y `HEAD` no vale como ancla porque el próximo commit cambia lo que contiene. Se mide
contra `44f53c2`, el padre del `git mv` de D-c (`3c2e6a3`), verificado con
`git ls-tree --name-only 44f53c2:.opencode/plans | grep -c VERIFICADOR-CONTEXTO` = **1** (en raíz) y
`.../Archives` = **0**. Las dos aserciones van en **un solo test**: la cura tiene que valer para las
dos formas de la ruta, y separarlas permitiría que una de las dos se apagara sin que el verde se note.
"""

from __future__ import annotations

import io
import subprocess
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
NOMBRE_PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
REV_PLAN_EN_RAIZ = "44f53c2"


def _arbol_de_la_revision(rev: str, rutas: list[str], tmp_path: Path) -> Path:
    """Materializa `rev` en un temporal con `git archive` (solo lectura, sin tocar el árbol de trabajo)."""
    destino = tmp_path / f"arbol-{rev}"
    destino.mkdir(parents=True, exist_ok=True)
    corrida = subprocess.run(
        ["git", "archive", "--format=tar", rev, *rutas],
        cwd=str(ROOT), capture_output=True, check=True)
    with tarfile.open(fileobj=io.BytesIO(corrida.stdout)) as tar:
        tar.extractall(path=destino, filter="data")
    return destino


def test_el_escritor_resuelve_el_plan_en_raiz_y_bajo_archives_en_la_misma_prueba(tmp_path: Path):
    """Raíz en `44f53c2`, `Archives/` en el árbol de trabajo: la misma llamada, dos árboles."""
    from tests.support_resolucion_plan import ruta_plan

    # --- el arbol versionado es el testigo: sin el layout esperado, el verde no diria nada
    en_raiz = _arbol_de_la_revision(
        REV_PLAN_EN_RAIZ, [f".opencode/plans/{NOMBRE_PLAN}"], tmp_path)
    plans_raiz = en_raiz / ".opencode" / "plans"
    prompt_de_la_raiz = plans_raiz / NOMBRE_PLAN / "05-prompt-inicio-sesion-fase-A.md"
    assert prompt_de_la_raiz.is_file(), (
        f"la revision {REV_PLAN_EN_RAIZ} ya no trae el plan en raiz con sus prompts: el arbol testigo "
        "dejo de servir y esta prueba perderia su oportunidad de fallar")
    assert not (plans_raiz / "Archives" / NOMBRE_PLAN).exists(), (
        f"{REV_PLAN_EN_RAIZ} dejo de ser el padre del traslado: si el plan tambien vive bajo "
        "Archives/ en esa revision, la asercion de raiz no distingue las dos formas de la ruta")

    # --- asercion 1: sobre ese arbol, el escritor resuelve el plan EN RAIZ
    resuelto_en_raiz = ruta_plan(NOMBRE_PLAN, plans_dir=plans_raiz)
    assert resuelto_en_raiz == plans_raiz / NOMBRE_PLAN, (
        f"el escritor no resolvio el plan en raiz sino {resuelto_en_raiz.as_posix()}: un proximo "
        "`git mv` volveria a dejar ciegos a los arneses, que es la fragilidad que S31 declara")

    # --- asercion 2: sobre el arbol de trabajo, el mismo nombre resuelve BAJO Archives/
    resuelto_archives = ruta_plan(NOMBRE_PLAN)
    assert resuelto_archives.parent.name == "Archives", (
        f"en el arbol de trabajo el plan se resolvio en {resuelto_archives.as_posix()}, no bajo "
        "Archives/: el escritor perdio la mitad del traslado")
    assert resuelto_archives.name == NOMBRE_PLAN

    # --- y el arbol versionado de trabajo sigue siendo el que la cura goberna
    assert (ROOT / ".opencode" / "plans" / "Archives" / NOMBRE_PLAN).is_dir()
    assert not (ROOT / ".opencode" / "plans" / NOMBRE_PLAN).exists(), (
        "el plan volvio a raiz: los arneses siguen resolviendo (esa es la cura), pero el motivo del "
        "control cambia y hay que re-anclar la revision testigo")


def test_los_arneses_no_vuelven_a_pinear_la_ruta():
    """Los seis arneses resuelven por el puente: ni literal completo ni arithmetic sobre `ARCHIVES`.

    Sin este control, un `PLAN = ...` pineado pasa las 109 pruebas de hoy (la ruta actual si esta
    bajo `Archives/`) y la fragilidad reaparece sin senal — que es exactamente como nacio S31.
    Medido con el mutante T3-b: la primera version de este predicado buscaba solo la cadena
    `"Archives" / "<PLAN>"` y dejo pasar `PLAN = ARCHIVES / NOMBRE_PLAN`, o sea un verde vacio
    frente a la forma mas probable de reintroducirse. Por eso el predicado es ahora de dos cortes:
    **exigir** el paso por el puente y **prohibir** la aritmetica de rutas.
    """
    archivos = [ROOT / "tests" / "quality_gates" / "lesson_relevance" / n for n in
                ("conftest.py", "test_triage_mutation_aditividad.py",
                 "test_triage_propuesta_no_escribe_seccion_dos.py")] + [
        ROOT / "tests" / "quality_gates" / "phase_briefing" / n for n in
        ("conftest.py", "test_briefing_carga_total_tres_sumandos.py",
         "test_briefing_se_genera_por_fase.py")]
    assert len(archivos) == 6, "S31 se abrio sobre seis constantes, no sobre otra cantidad"

    sin_puente, pineados = [], []
    for py in archivos:
        lineas_plan = [l.strip() for l in py.read_text(encoding="utf-8").splitlines()
                       if l.strip().startswith("PLAN = ")
                       or l.strip().startswith("PLAN: ")]
        assert lineas_plan, f"{py.name} ya no define `PLAN`: el control perdio su sujeto"
        if not any("ruta_plan(" in l for l in lineas_plan):
            sin_puente.append(f"{py.as_posix()} -> {lineas_plan}")
        for l in lineas_plan:
            if any(marca in l for marca in ("ROOT /", "ARCHIVES /", "PLANS /", '"/"')):
                pineados.append(f"{py.as_posix()} -> {l}")
    assert sin_puente == [], (
        f"estos arneses no preguntan al escritor: {sin_puente} — un proximo traslado los vuelve a "
        "cegar (S31)")
    assert pineados == [], f"la ruta del plan vuelve a armarse a pelo en {pineados}"
