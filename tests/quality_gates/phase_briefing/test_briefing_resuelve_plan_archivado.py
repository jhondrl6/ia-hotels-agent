"""AC19 (clausula de traslado) — el generador resuelve un plan **tambien bajo `Archives/`**.

El orden del cierre del contrato llama a `build_phase_briefing.py --plan <ruta-vigente>`
**despues** del `git mv` del RELEASE. Si el generador solo conociera `.opencode/plans/<PLAN>`,
ese llamado daria un rojo que no es un rojo: el plan existe, cambio de sitio. Se prueba sobre
los archivados **reales** del repo, no sobre un directorio plantado, porque la forma del
archivado (un nivel mas debajo de `plans/`) es justo lo que hay que acertar.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PLANS = ROOT / ".opencode" / "plans"
ARCHIVES = PLANS / "Archives"


def _archivados_con_prompts() -> list[Path]:
    if not ARCHIVES.is_dir():
        return []
    return sorted(d for d in ARCHIVES.iterdir()
                  if d.is_dir() and list(d.glob("05-prompt-inicio-sesion-fase-*.md")))


CORPUS = _archivados_con_prompts()

skip_sin_archivados = pytest.mark.skipif(
    not CORPUS,
    reason=(f"no hay planes archivados con prompts bajo {ARCHIVES.as_posix()} "
            f"(medido: {len(CORPUS)})"))


@skip_sin_archivados
def test_resuelve_el_plan_por_nombre_aunque_viva_bajo_archives(bpb):
    plan = CORPUS[0]
    resuelto = bpb.resolver_plan(plan.name, PLANS)
    assert resuelto is not None, (
        f"{plan.name} esta en Archives/ y el generador no lo resolvio: el llamado del RELEASE "
        "despues del git mv daria un rojo falso")
    assert resuelto.resolve() == plan.resolve()


@skip_sin_archivados
def test_resuelve_tambien_la_ruta_vigente_completa(bpb):
    """El cierre llama `--plan <ruta-vigente-del-plan>`: con la ruta absoluta tambien."""
    plan = CORPUS[0]
    assert bpb.resolver_plan(str(plan), PLANS) is not None
    assert bpb.resolver_plan(plan.as_posix(), PLANS) is not None


@skip_sin_archivados
def test_generar_y_verificar_sobre_un_archivado_no_toca_nada(bpb, tmp_path):
    plan = CORPUS[0]
    destinos = tmp_path / "briefing"

    def huellas() -> dict:
        return {p.relative_to(ROOT).as_posix():
                (hashlib.sha256(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns)
                for p in sorted(plan.rglob("*")) if p.is_file()}

    antes = huellas()
    paquetes, rc = bpb.generar(plan, destinos, ROOT)
    assert rc == 0, "un plan archivado no puede dar rojo por estar archivado"
    assert paquetes, "el plan archivado no tiene prompts: el verde seria vacio"
    assert (destinos / f"FASE-{paquetes[0]['fase']}.md").is_file()
    res, rc_check = bpb.verificar(plan, destinos, ROOT)
    assert rc_check == 0
    assert sum(r["fuentes"] for r in res) > 0 or all(r["sin_fuentes"] for r in res), (
        "el check no informo ni de fuentes ni de su ausencia")
    assert huellas() == antes, (
        "generar el pack de un plan archivado toco el plan archivado: prohibido")


def test_un_plan_inexistente_no_se_confunde_con_un_plan_vacio(bpb, tmp_path):
    """Ruta que no existe: rc 2 con las rutas intentadas, no un pack vacio (R2.9)."""
    rc = bpb.main(["--plan", "NO-EXISTE-ESTE-PLAN", "--briefing-dir", str(tmp_path / "x")])
    assert rc == 2
    resuelto = bpb.resolver_plan("NO-EXISTE-ESTE-PLAN", PLANS)
    assert resuelto is None
    intentadas = bpb.rutas_intentadas("NO-EXISTE-ESTE-PLAN", PLANS)
    assert len(intentadas) >= 2, intentadas
    assert any("Archives" in r for r in intentadas), (
        f"la ausencia hay que nombrarla con las rutas que se probaron, incluida Archives/: "
        f"{intentadas}")
