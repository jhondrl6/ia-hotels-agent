"""AC1 — un hallazgo es **una asercion**, no una linea.

A1 esta escrita en dos sitios del workflow canonico (`scripts/validate_plan_citations.py`, check 8
de `--quick` — el parrafo «Verificador mecanico» de R2.2 y la entrada v2.19.0 de `## Versiones`).
Cuenta como **un** hallazgo con dos `occurrences[]`: si no, el conteo de hallazgos dependeria de
cuantas veces se repita la frase y dejaria de medir contratos.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"
WORKFLOW = ROOT / ".agents" / "workflows" / "phased_project_executor.md"


@pytest.fixture(scope="module")
def informe(tmp_path_factory) -> dict:
    destino = tmp_path_factory.mktemp("gn_occ") / "informe.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "--report", str(destino)],
                       capture_output=True, text=True)
    assert r.returncode == 1
    return json.loads(destino.read_text(encoding="utf-8"))


def _contar_afirmaciones_en_el_documento() -> int:
    """Medicion independiente del patron interno: cuantos sitios escriben «check 8» hoy."""
    texto = WORKFLOW.read_text(encoding="utf-8")
    return texto.count("check 8")


def test_A1_es_un_hallazgo_con_dos_occurrences(informe: dict):
    a1 = next(f for f in informe["findings"] if f["assertion_id"] == "A1")
    assert len(a1["occurrences"]) == _contar_afirmaciones_en_el_documento() == 2
    assert len(informe["findings"]) == 4, (
        "repetir la frase no puede anadir hallazgos: se cuentan aserciones, no ocurrencias"
    )


def test_las_occurrences_apuntan_a_sitios_distintos(informe: dict):
    a1 = next(f for f in informe["findings"] if f["assertion_id"] == "A1")
    lineas = {o["linea"] for o in a1["occurrences"]}
    assert len(lineas) == 2, "dos occurrences en la misma linea no serian dos sitios"
    assert all(o["document"].endswith("phased_project_executor.md") for o in a1["occurrences"])


def test_duplicar_la_frase_no_duplica_el_hallazgo(modulo_gn, tmp_path: Path):
    """El mismo documento con la asercion escrita tres veces sigue dando UN hallazgo."""
    source = tmp_path / "run_all_validations.py"
    source.write_text(
        "class Runner:\n"
        "    def run_all(self) -> None:\n"
        "        self._check_alpha()\n\n"
        "    def _check_alpha(self) -> None:\n"
        '        print("[1/1] Checking alpha...")\n'
        '        script_path = ROOT_DIR / "scripts" / "validate_alpha.py"\n',
        encoding="utf-8",
    )
    hook = tmp_path / "pre-commit"
    hook.write_text("#   [1/1] Alpha check (validate_alpha.py)\n", encoding="utf-8")
    doc = tmp_path / "gobierno.md"
    doc.write_text(
        "`scripts/validate_alpha.py` es check 4 de `run_all_validations.py --quick`.\n"
        "`scripts/validate_alpha.py` es check 4 de `run_all_validations.py --quick`.\n"
        "`scripts/validate_alpha.py` es check 4 de `run_all_validations.py --quick`.\n",
        encoding="utf-8",
    )
    informe_local = modulo_gn.analizar(
        [{"path": doc, "name": "gobierno"}], source, hook
    )
    assert len(informe_local["findings"]) == 1
    assert len(informe_local["findings"][0]["occurrences"]) == 3
    assert informe_local["coverage_basis"]["poblacion"]["clase_viva_con_hallazgo"] == 3
