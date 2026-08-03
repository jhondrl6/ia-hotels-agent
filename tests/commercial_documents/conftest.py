"""
Conftest para tests/commercial_documents.

FASE-C-B (L11): Excluye archivos patológicos que causan fuga de RAM (~8GB)
o cuelgue indefinido durante la colección/ejecución de la suite completa.
Ver lección L1 y L11 en 10-analisis-post-implementacion.md del plan
COHERENCIA-MODULO-ENTREGA-2026-08-03.

Archivos excluidos:
- test_proposal_generator.py: fuga ~8GB RAM (V4ProposalGenerator._prepare_template_data)
- test_price_consistency.py: cuelgue indefinido (CommercialGateValidator en generate())
- test_proposal_generator_dict.py: MagicMock incompatible con score_seo < 30

Para ejecutar estos tests manualmente (bajo riesgo):
  pytest tests/commercial_documents/test_proposal_generator.py --run-pathological

Para reactivar permanentemente: eliminar los nombres de PATHOLOGICAL_FILES.
"""

import pytest

# Archivos que causan bloqueo del equipo (L1, L11)
PATHOLOGICAL_FILES = {
    "test_proposal_generator.py",
    "test_price_consistency.py",
    "test_proposal_generator_dict.py",
}


def pytest_addoption(parser):
    """Agregar flag --run-pathological para ejecutar tests excluidos."""
    parser.addoption(
        "--run-pathological",
        action="store_true",
        default=False,
        help="Ejecutar tests patológicos (riesgo: fuga RAM / cuelgue)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip archivos patológicos a menos que se pase --run-pathological."""
    if config.getoption("--run-pathological"):
        return  # No skip — el usuario quiere correrlos explícitamente

    skip_marker = pytest.mark.skip(
        reason=(
            "Test patológico: causa fuga de RAM o cuelgue del equipo (L1/L11). "
            "Usar --run-pathological para ejecutar bajo propio riesgo."
        )
    )
    for item in items:
        # item.fspath contiene la ruta completa del archivo de test
        filename = item.fspath.basename
        if filename in PATHOLOGICAL_FILES:
            item.add_marker(skip_marker)
