"""Static AST guardian for main.py — FASE-SR-A (L-SR1 / D-PF5).

Guardián de la clase de bug H1 (CONTEXT Salento Real §2): "símbolo no definido
en una rama condicional no ejercitada por la corrida estándar".

Historia: el fallback FASE-D S7 de main.py invocaba ``logger.info()`` sin que
``logger`` estuviera definido en el archivo. La corrida estándar (output
default) nunca evalúa esa condición, así que el defecto latente sobrevivió a
los 3,379 tests unitarios hasta que una corrida E2E con ``--output`` alternativo
murió con NameError (corregido y comiteado en d8e509d, 2026-08-27).

Prevención permanente (decisión D-PF5 del plan SR-PIPELINE-FIXES-2026-08-27):
1. ``py_compile`` de main.py debe pasar.
2. El AST de main.py no debe referenciar símbolos prohibidos (lista extensible
   ``FORBIDDEN_SYMBOLS``; inicia con ``logger``). Se usa AST —no regex— según
   L7 (contratos transversales): el parser distingue código de comentarios y
   strings, evitando falsos positivos como los comentarios del fix H1.
"""

import ast
import py_compile
from pathlib import Path

# FASE-SR-A (D-PF5): extensible. Añadir aquí símbolos que NUNCA deben
# referenciarse en main.py sin estar definidos (clase H1 / L-NC8 / L-NC9).
FORBIDDEN_SYMBOLS = ["logger"]

MAIN_PY = Path(__file__).resolve().parent.parent / "main.py"


def test_main_py_exists():
    """main.py must exist for the guardian to be meaningful."""
    assert MAIN_PY.exists(), f"main.py no encontrado en {MAIN_PY}"


def test_main_py_compiles(tmp_path):
    """Criterio L-SR1 (1/2): py_compile de main.py OK.

    Compila a un .pyc efímero (tmp_path) para no contaminar __pycache__.
    """
    py_compile.compile(str(MAIN_PY), cfile=str(tmp_path / "main.pyc"), doraise=True)


def test_main_py_has_no_forbidden_symbols():
    """Criterio L-SR1 (2/2) / D-PF5: el AST no referencia símbolos prohibidos.

    Cubre ``Name('logger')`` (uso directo del símbolo) y ``Attribute('.logger')``
    (acceso como atributo de otro objeto) — ambas manifestaciones de la clase
    de bug "símbolo no definido en rama no ejercitada" (H1 / L-NC8 / L-NC9).
    """
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"), filename=str(MAIN_PY))
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in FORBIDDEN_SYMBOLS:
            violations.append(
                f"{MAIN_PY.name}:{node.lineno}: Name '{node.id}' (símbolo prohibido)"
            )
        if isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_SYMBOLS:
            violations.append(
                f"{MAIN_PY.name}:{node.lineno}: Attribute '.{node.attr}' "
                "(símbolo prohibido)"
            )
    assert not violations, (
        "Guardián L-SR1 (clase de bug H1): main.py referencia símbolos "
        "prohibidos — probablemente en una rama no ejercitada por la corrida "
        "estándar:\n" + "\n".join(violations)
    )
