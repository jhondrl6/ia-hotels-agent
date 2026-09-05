"""Test propio de `scripts/validate_plan_closure.py` (regla R2.5).

Mismo principio que el test del verificador de citas: un validador que nunca
se dispara es letra muerta. Este archivo **fuerza el rojo** sobre un fixture
que declara «Cierre del plan COMPLETADO» y aun asi publica «⬜ Pendiente»,
comprueba que `Archives/` esta fuera de alcance y que el verificador no
reescribe nada (la correccion es decision de redaccion, no de script).
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_plan_closure.py"

CIERRE = "## 10. Cierre del plan\n\nEl plan esta **COMPLETADO** (v4.75.0, 2026-09-04).\n"
FILA_PENDIENTE = "| FASE-RELEASE | 2026-09-04 | ⬜ Pendiente | — | — |\n"
FILA_OK = "| FASE-RELEASE | 2026-09-04 | ✅ Completado | nota datada | — |\n"


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )


def _crear_plan(plans: Path, nombre: str, cuerpo: str) -> Path:
    plan = plans / nombre
    plan.mkdir(parents=True)
    (plan / "10-analisis-post-implementacion.md").write_text(cuerpo, encoding="utf-8")
    return plan


class TestDisparaConFixtureMalo:
    def test_plan_cerrado_con_fila_pendiente_falla(self, tmp_path: Path):
        plans = tmp_path / "plans"
        _crear_plan(
            plans,
            "PLAN-CERRADO-2026-09-04",
            CIERRE + "\n## Resumen de Ejecución\n\n" + FILA_PENDIENTE,
        )
        r = _correr("--plans-dir", str(plans))
        assert r.returncode == 1, "el verificador NO se disparo ante «⬜ Pendiente» en un plan cerrado"
        assert "1 violacion" in r.stdout
        assert "PLAN-CERRADO-2026-09-04/10-analisis-post-implementacion.md" in r.stdout

    def test_sin_declaracion_de_cierre_las_pendientes_son_legitimas(self, tmp_path: Path):
        plans = tmp_path / "plans"
        _crear_plan(
            plans,
            "PLAN-VIVO-2026-09-04",
            "## Resumen de Ejecución\n\n" + FILA_PENDIENTE,
        )
        r = _correr("--plans-dir", str(plans))
        assert r.returncode == 0, r.stdout + r.stderr


class TestVerdes:
    def test_plan_cerrado_limpio_pasa(self, tmp_path: Path):
        plans = tmp_path / "plans"
        _crear_plan(
            plans,
            "PLAN-CERRADO-LIMPIO-2026-09-04",
            CIERRE + "\n## Resumen de Ejecución\n\n" + FILA_OK,
        )
        r = _correr("--plans-dir", str(plans))
        assert r.returncode == 0, r.stdout + r.stderr

    def test_plan_sin_analisis_pasa(self, tmp_path: Path):
        plans = tmp_path / "plans"
        minimo = plans / "PLAN-MINIMO"
        minimo.mkdir(parents=True)
        (minimo / "01-plan-maestro.md").write_text("x", encoding="utf-8")
        r = _correr("--plans-dir", str(plans))
        assert r.returncode == 0, r.stdout + r.stderr

    def test_archives_fuera_de_alcance(self, tmp_path: Path):
        """Histórico congelado: un plan archivado con ⬜ no bloquea (como en el de citas)."""
        plans = tmp_path / "plans"
        _crear_plan(
            plans / "Archives",
            "PLAN-ANTIGUO-2025-01-01",
            CIERRE + "\n## Resumen de Ejecución\n\n" + FILA_PENDIENTE,
        )
        r = _correr("--plans-dir", str(plans))
        assert r.returncode == 0, r.stdout + r.stderr


class TestNoAutoarregla:
    def test_no_tiene_bandera_de_reparacion(self):
        src = SCRIPT.read_text(encoding="utf-8")
        assert "--fix" not in src
        assert "write_text" not in src

    def test_deja_el_archivo_malo_intacto(self, tmp_path: Path):
        plans = tmp_path / "plans"
        culpable = _crear_plan(
            plans,
            "PLAN-CERRADO-2026-09-04",
            CIERRE + "\n## Resumen de Ejecución\n\n" + FILA_PENDIENTE,
        ) / "10-analisis-post-implementacion.md"
        antes = culpable.read_text(encoding="utf-8")
        _correr("--plans-dir", str(plans))
        assert culpable.read_text(encoding="utf-8") == antes, "el verificador reescribio la historia"


class TestIntegracionRepoReal:
    def test_el_check_corre_sobre_el_repo_real(self):
        """El repo real queda verde (ESTABILIZACION vive hoy en Archives/)."""
        r = _correr()
        assert r.returncode == 0, r.stdout + r.stderr
        assert "[OK] Cierre de planes" in r.stdout

    def test_registrado_como_check_5_en_el_hook(self):
        src = (ROOT / "scripts" / "git_hooks" / "pre-commit").read_text(encoding="utf-8")
        assert "validate_plan_closure.py" in src
        assert "[5/5]" in src
