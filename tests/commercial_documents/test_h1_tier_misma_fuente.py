"""`H1` — propuesta y diagnóstico resuelven el tier con la MISMA fuente (FASE-F).

Dueño declarado: FASE-F (fila H1 de `10-analisis` §Seguimientos, abierta en FASE-B). Sin
`financial_breakdown`, los dos documentos degradan a `'C'`; el tier no lo decide `use_ga4`.
"""

import ast
from pathlib import Path

from modules.commercial_documents.evidence_tier import (
    TIER_SIN_EVIDENCIA,
    resolver_tier_evidencia,
)

RAIZ = Path(__file__).resolve().parents[2]
GENERADORES = (
    "modules/commercial_documents/v4_proposal_generator.py",
    "modules/commercial_documents/v4_diagnostic_generator.py",
)


class _Breakdown:
    def __init__(self, tier=None):
        if tier is not None:
            self.evidence_tier = tier


def test_sin_breakdown_el_tier_degrade_a_c():
    """El caso que fabricaba la asimetría: sin breakdown no hay evidencia que nombre."""
    assert resolver_tier_evidencia(None) == "C" == TIER_SIN_EVIDENCIA
    assert resolver_tier_evidencia(_Breakdown()) == "C", "breakdown sin el atributo no promueve"
    assert resolver_tier_evidencia(_Breakdown("")) == "C", "tier vacío no es un tier"


def test_el_breakdown_es_el_que_publica_el_tier():
    """Con breakdown manda lo que declaró su productor, en los tres formatos del plan."""
    for tier in ("A", "B", "B+", "C"):
        assert resolver_tier_evidencia(_Breakdown(tier)) == tier


def test_ambos_generadores_delegan_en_el_productor_unico():
    """Ningún generador vuelve a resolver el tier por su cuenta."""
    for rel_ruta in GENERADORES:
        arbol = ast.parse((RAIZ / rel_ruta).read_text(encoding="utf-8"))
        importados = {
            alias.name
            for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.ImportFrom) and (nodo.module or "").endswith("evidence_tier")
            for alias in nodo.names
        }
        assert "resolver_tier_evidencia" in importados, f"{rel_ruta} no delega el tier"
        llamados = [
            ast.unparse(nodo)
            for nodo in ast.walk(arbol)
            if isinstance(nodo, ast.Call) and getattr(nodo.func, "id", "") == "resolver_tier_evidencia"
        ]
        assert llamados, f"{rel_ruta} importa el productor único pero nunca lo invoca"


def test_el_fallback_del_tier_es_el_mismo_en_las_dos_poblaciones():
    """Dos resolutores, una letra: el DTO comercial y los artefactos del tribunal no derivan.

    Son poblaciones distintas (el DTO `FinancialBreakdown` aquí; `financial_scenarios_*.json`
    + `MANIFEST.json` en el tribunal), así que no se importan entre sí. Pero el fallback es el
    mismo hecho del producto: un tier que nadie declaró no certifica. Este diente impide que
    una cura mueva una letra y deje la otra atrás.
    """
    from modules.quality_gates.tribunal.evidence_tier import TIER_FALLBACK

    assert TIER_SIN_EVIDENCIA == TIER_FALLBACK == "C"


def test_el_diagnostico_no_promueve_el_tier_por_ga4():
    """El `tier = "A"` de la rama sin breakdown desapareció: ese era el defecto."""
    arbol = ast.parse(
        (RAIZ / "modules/commercial_documents/v4_diagnostic_generator.py").read_text(encoding="utf-8")
    )
    funcion = next(
        n
        for n in ast.walk(arbol)
        if isinstance(n, ast.FunctionDef) and n.name == "_build_financial_placeholders"
    )
    rama_sin_breakdown = next(
        h
        for h in funcion.body
        if isinstance(h, ast.If) and ast.unparse(h.test).startswith("financial_breakdown")
    )
    promovidos = [
        ast.unparse(nodo)
        for nodo in ast.walk(rama_sin_breakdown.orelse[-1] if isinstance(rama_sin_breakdown.orelse[-1], ast.If) else rama_sin_breakdown.orelse[-1])
        if isinstance(nodo, ast.Assign)
        and any(isinstance(o, ast.Name) and o.id == "tier" for o in nodo.targets)
        and getattr(nodo.value, "value", None) == "A"
    ]
    assert not promovidos, f"la rama sin breakdown sigue promoviendo el tier: {promovidos}"
