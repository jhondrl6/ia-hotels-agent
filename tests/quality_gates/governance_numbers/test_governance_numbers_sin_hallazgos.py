"""AC3 (estado 1 de 3) — `SIN-HALLAZGOS` imprime sobre QUE midio (L-R.3, L-PF10).

Cubre **un solo** estado: el fixture no puede dar `AUSENTE` ni `LECTOR-FALLIDO` porque todas las
rutas existen y todas las aserciones cuadran con la etiqueta que imprime el codigo.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_sin_hallazgos_sale_cuando_todo_cuadra(gobierno: dict):
    r = _correr("--governance-doc", str(gobierno["doc"]),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.splitlines()[0].startswith("[SIN-HALLAZGOS]"), r.stdout
    assert r.stdout.splitlines()[0].isascii()
    assert "HALLAZGOS]" not in r.stdout.replace("[SIN-HALLAZGOS]", "")
    assert "AUSENTE" not in r.stdout and "LECTOR-FALLIDO" not in r.stdout


def test_sin_hallazgos_publica_su_denominador(gobierno: dict):
    informe = gobierno["tmp"] / "informe.json"
    r = _correr("--governance-doc", str(gobierno["doc"]),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]),
                "--report", str(informe))
    assert r.returncode == 0, r.stdout
    datos = json.loads(informe.read_text(encoding="utf-8"))
    assert datos["status"] == "SIN-HALLAZGOS"
    assert datos["findings"] == []
    cb = datos["coverage_basis"]
    assert cb["poblacion"]["instancias_totales"] == 3
    assert cb["poblacion"]["clase_viva_correcta"] == 3
    assert cb["fuentes"]["quick"]["total"] == 2
    assert cb["fuentes"]["hook"]["total"] == 2
    assert cb["comando"] and cb["medido_el"]


def test_la_salida_favorable_no_existe_sin_denominador(gobierno: dict, monkeypatch):
    """`SIN-HALLAZGOS` sin `coverage_basis` completa esta prohibido: cae a LECTOR-FALLIDO."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("vgn_sin_denom", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "denominador_completo", lambda basis: False)
    try:
        mod.analizar([{"path": gobierno["doc"], "name": "workflow"}],
                     gobierno["source"], gobierno["hook"])
    except mod.LectorFallido as exc:
        assert "coverage_basis" in str(exc)
    else:
        raise AssertionError("SIN-HALLAZGOS se emito sin denominador (L-R.3)")
