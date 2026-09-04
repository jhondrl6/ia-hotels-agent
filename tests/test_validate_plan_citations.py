"""Test propio de `scripts/validate_plan_citations.py` (FASE-HOTFIX H9).

Un validador que nunca se dispara es una instancia mas de la clase que este plan
certifico (L-V1: AC7 estuvo ✅ nueve fases sobre un `gate_report` que no tenia la
clave que el criterio miraba). Por eso este archivo no se limita a celebrar el
verde: **fuerza el rojo** sobre un fixture malo y comprueba que el disparo ocurre,
que la salida nombra el archivo culpable y que el verificador **no reescribe nada**.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_plan_citations.py"

# Cita mala: posicion numerica en un plan nuevo. Cita buena: simbolo.
MALA = "Ver `modules/asset_generation/proposal_asset_alignment.py:526` y `main.py:2985`.\n"
BUENA = "Ver `classify_promised_services()` y `gate_blocks_publication()`.\n"


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )


@pytest.fixture()
def arbol(tmp_path: Path):
    """Directorio de planes con un baseline fijado sobre un plan historico limpio."""
    plans = tmp_path / "plans"
    historico = plans / "PLAN-HISTORICO-2026-01-01"
    historico.mkdir(parents=True)
    (historico / "01-plan-maestro.md").write_text(
        "Registro: `publication_gates.py:130` decia 10+3.\n"
        "Y `coherence_validator.py:278-319` era el denominador.\n",
        encoding="utf-8",
    )
    baseline = tmp_path / "baseline.json"
    r = _correr("--plans-dir", str(plans), "--baseline", str(baseline), "--update-baseline")
    assert r.returncode == 0, r.stdout + r.stderr
    return plans, baseline


class TestDisparaConFixtureMalo:
    def test_plan_nuevo_con_cita_numerica_falla(self, arbol):
        plans, baseline = arbol
        nuevo = plans / "PLAN-NUEVO-2026-09-05"
        nuevo.mkdir()
        (nuevo / "05-prompt-inicio-sesion-fase-A.md").write_text(MALA, encoding="utf-8")

        r = _correr("--plans-dir", str(plans), "--baseline", str(baseline))
        assert r.returncode == 1, "el verificador NO se disparo ante una cita nueva"
        assert "NUEVO con citas numericas (2)" in r.stdout
        assert "PLAN-NUEVO-2026-09-05/05-prompt-inicio-sesion-fase-A.md" in r.stdout

    def test_inventario_que_crece_falla_como_delta(self, arbol):
        plans, baseline = arbol
        historico = plans / "PLAN-HISTORICO-2026-01-01" / "01-plan-maestro.md"
        historico.write_text(
            historico.read_text(encoding="utf-8") + "Ademas `main.py:4210`.\n",
            encoding="utf-8",
        )
        r = _correr("--plans-dir", str(plans), "--baseline", str(baseline))
        assert r.returncode == 1
        assert "CRECIO 2 -> 3" in r.stdout

    def test_simbolos_no_disparan(self, arbol):
        plans, baseline = arbol
        nuevo = plans / "PLAN-NUEVO-2026-09-05"
        nuevo.mkdir()
        (nuevo / "05-prompt-inicio-sesion-fase-A.md").write_text(BUENA, encoding="utf-8")
        r = _correr("--plans-dir", str(plans), "--baseline", str(baseline))
        assert r.returncode == 0, r.stdout + r.stderr


class TestNoAutoarregla:
    """Prohibido reescribir numeros: el verificador reporta, no repara (H9)."""

    def test_no_tiene_bandera_de_reparacion(self):
        src = SCRIPT.read_text(encoding="utf-8")
        assert "--fix" not in src
        # Unico escrito del script es el baseline explicito; verificar no escribe.
        assert src.count("write_text") == 1
        assert "def escribir_baseline" in src

    def test_deja_el_archivo_malo_intacto(self, arbol):
        plans, baseline = arbol
        nuevo = plans / "PLAN-NUEVO-2026-09-05"
        nuevo.mkdir()
        culpable = nuevo / "01-plan-maestro.md"
        culpable.write_text(MALA, encoding="utf-8")
        antes = culpable.read_text(encoding="utf-8")
        _correr("--plans-dir", str(plans), "--baseline", str(baseline))
        assert culpable.read_text(encoding="utf-8") == antes, "el verificador reescribio la historia"


class TestBaselinePortable:
    def test_claves_relativas_para_sobrevivir_el_clone(self, arbol):
        _, baseline = arbol
        datos = json.loads(baseline.read_text(encoding="utf-8"))
        for ruta in datos["files"]:
            assert not Path(ruta).is_absolute(), f"ruta absoluta en el baseline: {ruta}"

    def test_sin_baseline_exige_fijarlo_y_no_pasa_en_silencio(self, tmp_path):
        plans = tmp_path / "plans"
        plans.mkdir()
        (plans / "a.md").write_text(MALA, encoding="utf-8")
        r = _correr("--plans-dir", str(plans), "--baseline", str(tmp_path / "x.json"))
        assert r.returncode == 2
        assert "--update-baseline" in r.stdout


class TestIntegracionQuick:
    def test_el_check_corre_sobre_el_repo_real(self):
        """Contra el arbol real: 0 citas nuevas y 0 crecimientos (inventario historico)."""
        r = _correr()
        assert r.returncode == 0, r.stdout + r.stderr
        assert "[OK] Plan citations:" in r.stdout

    def test_registrado_como_check_en_run_all_validations(self):
        src = (ROOT / "scripts" / "run_all_validations.py").read_text(encoding="utf-8")
        assert "_check_plan_citations()" in src
        assert "validate_plan_citations.py" in src
