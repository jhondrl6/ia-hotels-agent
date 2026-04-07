"""
Permission Mode -- Control granular de aprobacion de operaciones con costo.

Patron inspirado en Goose (GooseMode: auto, approve, smart_approve, chat).
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable


class PermissionMode(str, Enum):
    AUTO = "auto"              # Ejecutar todo sin preguntar
    SMART_APPROVE = "smart_approve"  # Preguntar solo si costo > umbral
    APPROVE = "approve"        # Preguntar antes de cada operacion externa
    CHAT = "chat"              # Solo diagnostico, sin llamadas externas


DEFAULT_MODE = PermissionMode.AUTO
COST_THRESHOLD = 0.05  # USD -- arriba de este valor, preguntar en smart_approve


@dataclass
class OperationPermission:
    name: str
    estimated_cost: float
    is_external: bool  # llamada a API externa


def check_permission(
    op: OperationPermission,
    mode: PermissionMode = DEFAULT_MODE,
    on_ask: Optional[Callable] = None,
) -> bool:
    """
    Decide si una operacion debe ejecutarse segun el modo de permiso.

    Args:
        op: la operacion a evaluar
        mode: el modo activo
        on_ask: callback para pedir confirmacion (recibe nombre y costo, retorna bool)

    Returns:
        True si se debe ejecutar, False si se debe saltar
    """
    if mode == PermissionMode.AUTO:
        return True
    if mode == PermissionMode.CHAT:
        return False  # sin llamadas externas
    if mode == PermissionMode.APPROVE:
        if op.is_external and on_ask:
            return on_ask(op.name, op.estimated_cost)
        return True  # operaciones internas siempre pasan
    if mode == PermissionMode.SMART_APPROVE:
        if op.is_external and op.estimated_cost > COST_THRESHOLD:
            if on_ask:
                return on_ask(op.name, op.estimated_cost)
            return False  # sin callback, no ejecutar por seguridad
        return True  # bajo umbral o interno = ejecutar
    return True
