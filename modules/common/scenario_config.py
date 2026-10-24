"""Respaldo de `config/scenarios.yaml` con un solo sitio para sus valores.

El maestro es `config/scenarios.yaml`. Este dict existe solo para el caso en que el YAML no se
pueda leer; `tests/config/test_coherencia_escenarios_d25bis.py` lo contra contra el maestro y
pone en rojo cualquier divergencia (`D25-bis`: el respaldo decía `realistic: 0.20` mientras el
YAML publicaba `0.35` y el ROI se calculaba con un factor que nadie recuerda).
"""

from copy import deepcopy
from typing import Any, Dict

RESPALDO_ESCENARIOS: Dict[str, Any] = {
    "recovery_factors": {"conservative": 0.15, "realistic": 0.35, "optimistic": 0.25},
    "scenario_weights": {"conservative": 0.70, "realistic": 0.20, "optimistic": 0.10},
    "pain_ratio_default": 0.20,
}


def respaldo_escenarios() -> Dict[str, Any]:
    """Copia del respaldo, para que nadie mutée la única fuente Python de estos valores."""
    return deepcopy(RESPALDO_ESCENARIOS)
