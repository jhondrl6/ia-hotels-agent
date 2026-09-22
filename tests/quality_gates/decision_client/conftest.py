"""Fixtures y **guard de cero red** de la seleccion FASE-B / `decision_client.py`.

El guard no es decoracion: el contrato de ejecucion de este plan prohibe una sola llamada de red, y
un «no la hice» afirmado no es verificable. Aqui cualquier intento de abrir un socket, resolver un
nombre o negociar TLS durante esta seleccion revienta con `RedProhibida`, asi que el rojo de una
fuga es ruidoso y no silencioso.

Las rutas del proveedor falso se resuelven **por entorno** y con una regla: si el entorno ya trae
`IAH_DECISION_PROVIDER` y `IAH_DECISION_PROVIDERS_DIR` (lo hace cuando lanza el harness de mutacion
de AC8, que corre el mismo test contra una copia alterada del proveedor), el fixture **no** los
toca. Si no, apunta al directorio del repo. Sin esa regla, el harness tendria que reescribir el test
para provocar el rojo, y el rojo dejaria de probar el contrato.
"""

import importlib.util
import os
import socket
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "decision_client.py"
FALOS = Path(__file__).resolve().parent / "falsos_proveedores"


class RedProhibida(RuntimeError):
    """Alguien intento salir a la red dentro de la seleccion de FASE-B."""


def _bloquear(*nombres):
    def explotar(*a, **kw):
        raise RedProhibida(
            f"FASE-B prohibe llamadas de red; se intento {nombres[0]!r} con args={a[:2]!r}")
    return explotar


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Autouse: arma el guard antes de cada caso y lo quita pytest despues."""
    parches = {
        "socket": _bloquear("socket.socket"),
        "create_connection": _bloquear("socket.create_connection"),
        "getaddrinfo": _bloquear("socket.getaddrinfo"),
        "gethostbyname": _bloquear("socket.gethostbyname"),
    }
    reales = {k: getattr(socket, k) for k in parches}
    for k, v in parches.items():
        monkeypatch.setattr(socket, k, v)
    yield
    for k, v in reales.items():
        setattr(socket, k, v)


@pytest.fixture(scope="session")
def excpcion_de_red():
    """La clase que lanza el guard: por fixture, no por `from conftest import ...`, que bajo la
    coleccion resuelve al `tests/conftest.py` raiz y no al de esta seleccion."""
    return RedProhibida


@pytest.fixture(scope="session")
def raiz_repo() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def script_ruta() -> Path:
    return SCRIPT


@pytest.fixture(scope="session")
def proveedores_falsos() -> Path:
    return FALOS


@pytest.fixture
def dc():
    """El modulo real de la puerta, cargado por ruta (los mutantes de R2.8 lo patchean a el)."""
    spec = importlib.util.spec_from_file_location("decision_client_bajo_prueba", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def preguntas(dc):
    """Una pregunta de cada forma del contrato: choice, score ordenado y noul."""
    return [
        dc.Pregunta("c1", "choice", "¿Cual de estas lecciones debia capitalizarse?",
                    opciones=("pertinente", "no-pertinente", "insuficiente")),
        dc.Pregunta("s1", "score", "¿Que riesgo tiene esta decision?",
                    leyenda=("bajo", "medio", "alto", "critico")),
        dc.Pregunta("n1", "noul", "¿Esta asercion sigue vigente en el arbol?"),
    ]


@pytest.fixture
def entorno_falso(monkeypatch, proveedores_falsos, request):
    """Entorno resuelto **por variable**, como lo resuelve la puerta.

    `request.param` permite elegir proveedor desde `@pytest.mark.parametrize` (los tres estados de
    AC7 se provocan asi, sin markers propios). Si el entorno externo ya trae las dos variables, el
    fixture no las toca: es el camino por el que el harness de mutacion de AC8 corre **el mismo**
    contract test contra una copia alterada del proveedor falso.
    """
    elegido = getattr(request, "param", None) or "falso-forma"
    externo = (os.environ.get("IAH_DECISION_PROVIDER")
               and os.environ.get("IAH_DECISION_PROVIDERS_DIR"))
    if externo:
        return dict(os.environ)
    monkeypatch.setenv("IAH_DECISION_PROVIDER", elegido)
    monkeypatch.setenv("IAH_DECISION_PROVIDERS_DIR", str(proveedores_falsos))
    return dict(os.environ)
