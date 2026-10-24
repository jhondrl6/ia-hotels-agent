"""FASE-H2 (`D23`, AC8): el docstring de `_check_claim_vs_evidence` dice lo que hace la rama.

La deuda eran **dos** divergencias en la misma prosa (`L-CST-7`): una disyuncion donde el
codigo tiene conjuncion, y una frontera exclusiva (`>`) donde el codigo es inclusivo (`>=`).
Aqui se curan las dos por separado: el docstring se coteja contra la condicion que el AST
desenrolla del metodo, y la frontera `rating == 4.0` se juzga contra el comportamiento real.

No se toca la logica del gate: los tres casos de la frontera son el behavior actual, fijado.
"""

import ast
from pathlib import Path

from modules.quality_gates.commercial_gate import CommercialGateValidator

RAIZ = Path(__file__).resolve().parents[2]
FUENTE = RAIZ / "modules" / "quality_gates" / "commercial_gate.py"
METODO = "_check_claim_vs_evidence"
CLAIM_FACTUAL = "El hotel no aparece en Google."


def _metodo() -> ast.FunctionDef:
    arbol = ast.parse(FUENTE.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.FunctionDef) and nodo.name == METODO:
            return nodo
    raise AssertionError(f"{METODO} desaparecio de {FUENTE}")


def _condicion_de_disparo() -> str:
    """La conjuncion del `if` que falla el gate, reproducida por el propio AST.

    Se ancla por identidad (la rama que menciona `place_found`), no por posicion: asi
    cualquier otro `and` que se sume al metodo no le roba el sitio al disparo.
    """
    candidatas = [
        ast.unparse(nodo.test)
        for nodo in ast.walk(_metodo())
        if isinstance(nodo, ast.If)
        and isinstance(nodo.test, ast.BoolOp)
        and "place_found" in ast.unparse(nodo.test)
    ]
    assert len(candidatas) == 1, f"la rama de disparo no es unica: {candidatas}"
    return candidatas[0]


def test_la_condicion_real_es_conjuncion_inclusiva():
    """El diente del diente: si alguien cambia la rama, este control lo nombra."""
    assert _condicion_de_disparo() == "place_found and gbp_rating >= 4.0"


def test_el_docstring_cita_la_condicion_del_codigo():
    """`D23`: el docstring lleva la condicion literal que imprime `ast.unparse`."""
    doc = ast.get_docstring(_metodo())
    assert doc is not None, "el metodo se quedo sin docstring"
    assert _condicion_de_disparo() in doc


def test_el_docstring_no_promete_disyuncion_ni_frontera_exclusiva():
    """Las dos divergencias retiradas: ni `or` como operador, ni `> 4.0` como umbral."""
    import re

    doc = ast.get_docstring(_metodo())
    assert "4.0" in doc
    assert "> 4.0" not in doc
    assert re.search(r"\bor\b", doc, flags=re.IGNORECASE) is None


def test_frontera_rating_igual_4_dispara():
    """`rating == 4.0` con place_found=True: la frontera inclusiva es FAIL del gate."""
    resultado = CommercialGateValidator()._check_claim_vs_evidence(
        CLAIM_FACTUAL, place_found=True, gbp_rating=4.0
    )
    assert resultado.passed is False
    assert resultado.severity == "BLOCKING"
    assert "rating=4.0/5.0" in resultado.message


def test_justo_debajo_de_la_frontera_no_dispara():
    """3.99 sigue el mismo criterio: el umbral es 4.0, no 3.x."""
    resultado = CommercialGateValidator()._check_claim_vs_evidence(
        CLAIM_FACTUAL, place_found=True, gbp_rating=3.99
    )
    assert resultado.passed is True


def test_place_found_falso_no_dispara_aunque_el_rating_suba():
    """La segunda divergencia (`or` → `and`): sin prueba de ficha, el claim es admisible."""
    resultado = CommercialGateValidator()._check_claim_vs_evidence(
        CLAIM_FACTUAL, place_found=False, gbp_rating=4.9
    )
    assert resultado.passed is True
