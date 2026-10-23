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
import importlib
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


# ---------------------------------------------------------------------------
# FASE-A (N7 / D-PF5 / L-CIM.12): guardián por EXISTENCIA de atributo.
#
# El guardián de arriba solo caza nombres prohibidos; pasaba en verde sobre un
# `AttributeError` latente (FinancialFactors.SUPERPOSITION_FACTOR, inexistente
# desde el refactor 1501dd8). Este bloque lo extiende a existencia: todo
# `Clase.atributo` sobre una clase vigilada debe existir realmente sobre la
# clase IMPORTADA. La comprobación es AST + import — no un grep de menciones.
# ---------------------------------------------------------------------------

GUARDED_CLASSES = {
    "FinancialFactors": ("modules.utils.financial_factors", "FinancialFactors"),
}

GUARDED_SITES = [
    MAIN_PY,
    MAIN_PY.parent / "modules" / "analyzers" / "gap_analyzer.py",
]


def check_attribute_existence(source: str, filename: str = "main.py"):
    """Devuelve violaciones de existencia de `Clase.atributo` (AST + import).

    Cubre `Clase.atributo` cuando `Clase` está en GUARDED_CLASSES. Accesos sobre
    instancias (objeto.atributo) quedan fuera: no son resolubles por AST sin
    inferencia de tipos.
    """
    tree = ast.parse(source, filename=filename)
    classes = {
        name: getattr(importlib.import_module(mod), cls)
        for name, (mod, cls) in GUARDED_CLASSES.items()
    }
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            cls = classes.get(node.value.id)
            if cls is None:
                continue
            if not hasattr(cls, node.attr):
                violations.append(
                    f"{filename}:{node.lineno}: {node.value.id}.{node.attr} no existe "
                    f"sobre {cls.__module__}.{cls.__name__}"
                )
    return violations


def test_guarded_sites_sin_atributos_inexistentes():
    """Árbol actual → verde: ningún `Clase.atributo` inexistente en los sitios vigilados.

    Sitios vigilados: main.py y gap_analyzer.py — las dos superficies del
    contrato `FinancialFactors` tocadas por el refactor 1501dd8 (AC5).
    """
    violations = []
    for site in GUARDED_SITES:
        violations += check_attribute_existence(
            site.read_text(encoding="utf-8"), filename=site.name
        )
    assert not violations, (
        "Guardián de existencia (N7): atributo inexistente sobre la clase "
        "importada — rama latente lista para AttributeError:\n" + "\n".join(violations)
    )


def test_mutante_con_atributo_inventado_es_rojo():
    """Mutation check (R2.8) sobre el símbolo real del guard → rojo.

    Inyecta un atributo inventado sobre la clase vigilada en la fuente real de
    gap_analyzer.py (el sitio donde vivió el defecto `factor_superposicion`) y
    exige que el guardián lo detecte. Sin este rojo, el verde de arriba no
    certifica la propiedad que nombra (L-CIM.12).
    """
    real_src = GUARDED_SITES[1].read_text(encoding="utf-8")
    mutante_src = (
        real_src
        + "\n# mutante FASE-A (R2.8): atributo inventado sobre la clase importada\n"
        + "_MUTANTE_FASE_A = FinancialFactors.ATTR_INVENTADA_FASE_A\n"
    )
    violations = check_attribute_existence(mutante_src, filename="gap_analyzer.py")
    assert violations, (
        "El guardián de existencia NO detectó un atributo inventado: "
        "el control verde no mediría la propiedad que nombra (L-CIM.12)"
    )
