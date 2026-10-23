"""Retiro de la ruta ``spark`` — FASE-A (N1/D19, L-SR1/L-T4A.5).

La ruta spark estaba deprecada y rota: ``_map_audit_to_spark_data`` referenciaba
``FinancialFactors.SUPERPOSITION_FACTOR``, atributo inexistente desde el refactor
``1501dd8``. Decisión del Operador (DA-PLAN-4): se retira, no se repara. El
comando informa el retiro y sale 0; ningún lector ejecutable del atributo muerto
queda en main.py.

Los tests cierran el retiro con diente (L-T4A.5): afirman exit 0 Y mensaje de
retiro Y ausencia de ``AttributeError``, no solo "no lanzó". El mutante de
reintroducción del lector roto es rojo por AST.
"""

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = ROOT / "main.py"

RETIRED_SYMBOLS = (
    "_map_audit_to_spark_data",
    "_spark_handler",
    "_run_spark_legacy",
)


def test_spark_informa_retiro_y_sale_0_sin_attribute_error():
    """`main.py spark --url <fixture>` sale 0 y declara el retiro (AC5)."""
    proc = subprocess.run(
        [sys.executable, str(MAIN_PY), "spark", "--url", "https://example.com/hotel-fixture"],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=180,
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, (
        f"spark debe salir con código 0 tras el retiro; salió {proc.returncode}:\n{out}"
    )
    assert "retirad" in out.lower(), (
        f"el comando debe declarar su retiro en el mensaje; stdout:\n{out}"
    )
    assert "AttributeError" not in out, (
        f"el retiro no puede romperse con AttributeError; stdout:\n{out}"
    )
    assert "v4complete" in out, (
        f"el mensaje de retiro debe orientar al producto vivo (v4complete); stdout:\n{out}"
    )


def test_simbolos_spark_retirados_de_main():
    """Los símbolos de la ruta rota ya no están definidos en main.py."""
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"), filename=str(MAIN_PY))
    defs = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    faltantes = [s for s in RETIRED_SYMBOLS if s in defs]
    assert not faltantes, f"la ruta spark fue reintroducida en main.py: {faltantes}"
    assert "run_spark_mode" in defs, (
        "el centinela de retiro `run_spark_mode` debe conservarse para informar el retiro"
    )


def test_main_sin_lector_ejecutable_de_superposition_factor():
    """Mutante de reintroducción del lector roto → rojo (AST, no grep).

    Si alguien vuelve a escribir `FinancialFactors.SUPERPOSITION_FACTOR` en
    main.py (lectura ejecutable del atributo muerto), este test falla aunque la
    rama no se ejercite (L-SR1).
    """
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"), filename=str(MAIN_PY))
    lectores = [
        f"línea {node.lineno}"
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr == "SUPERPOSITION_FACTOR"
    ]
    assert not lectores, (
        f"lector roto reintroducido en main.py ({', '.join(lectores)}): "
        "FinancialFactors.SUPERPOSITION_FACTOR ya no existe"
    )
