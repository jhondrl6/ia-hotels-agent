"""AC3 (estado 2 de 3) — `AUSENTE` imprime la **ruta buscada** (L-PF6, L-PF10).

Cubre **un solo** estado: aqui falta una ruta, no se cae el lector ni se mide un arbol limpio.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_documento_de_gobierno_ausente_dice_la_ruta(gobierno: dict):
    falta = gobierno["tmp"] / "no-existe" / "workflow.md"
    r = _correr("--governance-doc", str(falta),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]))
    assert r.returncode == 2, r.stdout + r.stderr
    assert "AUSENTE" in r.stdout
    assert "no-existe" in r.stdout and "workflow.md" in r.stdout, "AUSENTE sin ruta no informa"
    assert "SIN-HALLAZGOS" not in r.stdout


def test_fuente_de_checks_ausente_dice_la_ruta(gobierno: dict):
    r = _correr("--governance-doc", str(gobierno["doc"]),
                "--source", str(gobierno["tmp"] / "otro.py"), "--hook", str(gobierno["hook"]))
    assert r.returncode == 2
    assert "otro.py" in r.stdout
    assert "SIN-HALLAZGOS" not in r.stdout and "HALLAZGOS\n" not in r.stdout


def test_ausente_no_deja_informe_favorable(gobierno: dict):
    informe = gobierno["tmp"] / "informe-ausente.json"
    r = _correr("--governance-doc", str(gobierno["tmp"] / "falta.md"),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]),
                "--report", str(informe))
    assert r.returncode == 2
    assert not informe.exists(), "un estado AUSENTE no puede publicar un informe"
