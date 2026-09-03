"""FASE-D (H10 / T0.1) — candado de regresion sobre la severidad de gates.

Antes de esta fase habia **0 tests** que fijaran la pertenencia de un gate a
blocking o advisory, y cuatro regimenes contradictorios describian la misma
severidad (docstrings 10+3, codigo bloqueando con los 13, AGENTS.md repitiendo
el docstring, y `delivery_quality_report.py` con un regimen propio de ZIP).

Sin este candado el cuarto regimen reaparece. Lo que se fija es lo que la
decision medida establece: la pertenencia de `asset_confidence` a blocking y la
cardinalidad 11 + 2 — no un literal inmutable con los 13 nombres.
"""

import ast
from pathlib import Path

import pytest

from modules.quality_gates.publication_gates import (
    ADVISORY_GATE_NAMES,
    BLOCKING_GATE_NAMES,
    PublicationGatesOrchestrator,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_GATES = REPO_ROOT / "modules" / "quality_gates" / "publication_gates.py"
QUALITY_GATES_DIR = REPO_ROOT / "modules" / "quality_gates"

# `delivery_quality_report.py` rige el ZIP (main.py "⛔ ZIP ABORTED"): es un
# regimen de DELIVERY, deliberadamente separado del de publicacion (dossier §8.4
# tarea 3). `commercial_gate.py` es la familia CG-* — el patron que se copio.
DELIVERY_REGIME_EXEMPT = {"delivery_quality_report.py", "commercial_gate.py"}


def _source() -> str:
    return PUBLICATION_GATES.read_text(encoding="utf-8")


def _function(name: str) -> ast.FunctionDef:
    tree = ast.parse(_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"funcion {name} no existe en publication_gates.py")


class TestSeveridadListas:
    def test_asset_confidence_no_es_advisory(self):
        """Dossier §8.2: es el unico mecanismo que vuelve no-entregable un Tier C."""
        assert "asset_confidence" in BLOCKING_GATE_NAMES
        assert "asset_confidence" not in ADVISORY_GATE_NAMES

    def test_advisory_son_exactamente_dos(self):
        assert set(ADVISORY_GATE_NAMES) == {"content_quality", "proposal_asset_alignment"}

    def test_listas_suman_13_y_son_disjuntas(self):
        assert len(BLOCKING_GATE_NAMES) == 11
        assert len(ADVISORY_GATE_NAMES) == 2
        assert len(set(BLOCKING_GATE_NAMES) | set(ADVISORY_GATE_NAMES)) == 13
        assert not set(BLOCKING_GATE_NAMES) & set(ADVISORY_GATE_NAMES)

    def test_registro_de_gates_coincide_con_la_severidad(self):
        """Un gate nuevo sin clasificar rompe tambien en __init__ (falla fuerte)."""
        gates = set(PublicationGatesOrchestrator().gates)
        assert gates == set(BLOCKING_GATE_NAMES) | set(ADVISORY_GATE_NAMES)


class TestNoRegresionEstructural:
    def test_check_publication_readiness_no_decide_con_not_passed_plano(self):
        """Guardián AST: `blocking_gates = [r for r in results if not r.passed]`
        es exactamente el bug que esta fase cierra; no puede volver por
        compresion, ni por una refactorizacion que 'simplifica' el filtro."""
        body = ast.dump(_function("check_publication_readiness"))
        assert "blocking_gates" in body

        offenders = []
        for node in ast.walk(_function("check_publication_readiness")):
            if not isinstance(node, (ast.ListComp, ast.GeneratorExp)):
                continue
            for gen in node.generators:
                for condition in gen.ifs:
                    if _is_bare_not_passed(condition):
                        offenders.append(ast.unparse(condition))
        assert not offenders, (
            "el filtro de bloqueantes decide con `not r.passed` plano; debe usar "
            f"gate_blocks_publication (severidad). Offenders: {offenders}"
        )

    def test_no_apesta_una_segunda_copia_del_criterio(self):
        source = _source()
        assert source.count("def gate_blocks_publication") == 1

    def test_no_hay_tercera_lista_de_severidad_en_el_regimen_de_publicacion(self):
        """Anti-cuarto-regimen: ninguna otra lectura de severidad vive suelta en
        `modules/quality_gates/` fuera de la unica fuente."""
        for path in sorted(QUALITY_GATES_DIR.glob("*.py")):
            if path.name == "publication_gates.py" or path.name in DELIVERY_REGIME_EXEMPT:
                continue
            for node in ast.parse(path.read_text(encoding="utf-8")).body:
                if not isinstance(node, (ast.AnnAssign, ast.Assign)):
                    continue
                for target in _targets(node):
                    if _is_severity_name(target):
                        pytest.fail(
                            f"{path.name} define una lista de severidad de publicacion "
                            f"propia ({target}): use BLOCKING_GATE_NAMES / "
                            "ADVISORY_GATE_NAMES de publication_gates.py"
                        )

    def test_docstrings_no_prometen_el_regimen_antiguo(self):
        """AC8 montado en AC7: si la estructura cambia y el docstring no, este
        test rompe — es lo que impidio durante 30+ versiones que ocurriera."""
        source = _source()
        assert "10 blocking" not in source
        assert "3 advisory" not in source
        assert "11 blocking" in source
        assert "2 advisory" in source


def _targets(node):
    if isinstance(node, ast.AnnAssign):
        return [node.target.id] if isinstance(node.target, ast.Name) else []
    names = []
    for t in node.targets:
        if isinstance(t, ast.Name):
            names.append(t.id)
    return names


def _is_severity_name(name: str) -> bool:
    upper = name.upper()
    return "GATE" in upper and any(
        word in upper for word in ("BLOCKING", "ADVISORY", "WARNING")
    )


def _is_bare_not_passed(condition: ast.expr) -> bool:
    """`not r.passed` sin guarda adicional de severidad."""
    if not isinstance(condition, ast.UnaryOp) or not isinstance(condition.op, ast.Not):
        return False
    inner = condition.operand
    if isinstance(inner, ast.Attribute) and inner.attr == "passed":
        return True
    return _is_bare_not_passed(inner)
