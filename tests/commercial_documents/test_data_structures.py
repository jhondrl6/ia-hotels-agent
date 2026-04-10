"""
Tests de regresión FASE-I: verificación de deduplicación en data_structures.py.
"""
import ast
import inspect
from modules.commercial_documents.data_structures import (
    Scenario,
    DiagnosticSummary,
    calculate_quick_wins,
    extract_top_problems,
)


class TestDeduplication:
    """Verifica que FASE-I eliminó correctamente las definiciones duplicadas."""

    def test_scenario_no_duplicate_fields(self):
        """Scenario no debe tener campos ni métodos duplicados."""
        with open("modules/commercial_documents/data_structures.py") as f:
            source = f.read()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Scenario":
                field_names = [
                    item.target.id
                    for item in node.body
                    if isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                ]
                method_names = [
                    item.name
                    for item in node.body
                    if isinstance(item, ast.FunctionDef)
                ]

                # No field should appear more than once
                for name in field_names:
                    assert field_names.count(name) == 1, (
                        f"Campo duplicado en Scenario: '{name}' "
                        f"aparece {field_names.count(name)} veces"
                    )

                # No method should appear more than once
                for name in method_names:
                    assert method_names.count(name) == 1, (
                        f"Método duplicado en Scenario: '{name}' "
                        f"aparece {method_names.count(name)} veces"
                    )
                return

        pytest.fail("Clase Scenario no encontrada en data_structures.py")

    def test_calculate_quick_wins_single_definition(self):
        """calculate_quick_wins debe tener exactamente 1 definición."""
        with open("modules/commercial_documents/data_structures.py") as f:
            source = f.read()
        tree = ast.parse(source)

        count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "calculate_quick_wins"
        )
        assert count == 1, (
            f"calculate_quick_wins tiene {count} definiciones, esperaba 1"
        )

    def test_extract_top_problems_single_definition(self):
        """extract_top_problems debe tener exactamente 1 definición."""
        with open("modules/commercial_documents/data_structures.py") as f:
            source = f.read()
        tree = ast.parse(source)

        count = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "extract_top_problems"
        )
        assert count == 1, (
            f"extract_top_problems tiene {count} definiciones, esperaba 1"
        )

    def test_diagnostic_summary_has_brechas_reales(self):
        """DiagnosticSummary debe tener brechas_reales con tipado correcto."""
        with open("modules/commercial_documents/data_structures.py") as f:
            source = f.read()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DiagnosticSummary":
                field_names = [
                    item.target.id
                    for item in node.body
                    if isinstance(item, ast.AnnAssign)
                    and isinstance(item.target, ast.Name)
                ]
                assert "brechas_reales" in field_names, (
                    "Campo 'brechas_reales' no encontrado en DiagnosticSummary"
                )
                return

        pytest.fail("Clase DiagnosticSummary no encontrada en data_structures.py")
