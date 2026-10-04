"""Fixtures y **guard de cero red** de la seleccion del piloto JEV (FASE-B, 2026-10-03).

El guard es la mitad del contrato AC9: «SDK real con transporte falso y red bloqueada». Un
`MockTransport` que nunca llega al socket no prueba por si solo que la red esta cerrada, asi que
aqui cualquier intento de abrir un socket, resolver un nombre o negociar TLS revienta con
`RedProhibida` — el rojo de una fuga es ruidoso y no silencioso. Va por fixture autouse, como en la
seleccion de la costura, y no por una promesa en un documento.
"""
from __future__ import annotations

import importlib.util
import socket
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
PUERTA = ROOT / "scripts" / "decision_client.py"
RUNNER = ROOT / "scripts" / "evaluate_jev_pilot.py"


class RedProhibida(RuntimeError):
    """Alguien intento salir a la red dentro de la seleccion del piloto."""


def _bloquear(*nombres):
    def explotar(*a, **kw):
        raise RedProhibida(
            f"FASE-B del piloto prohibe llamadas de red; se intento {nombres[0]!r} con args={a[:2]!r}")
    return explotar


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    reales = {k: getattr(socket, k) for k in
              ("socket", "create_connection", "getaddrinfo", "gethostbyname")}
    for k in reales:
        monkeypatch.setattr(socket, k, _bloquear(k))
    yield
    for k, v in reales.items():
        setattr(socket, k, v)


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="session")
def puerta():
    """La costura real, cargada por ruta: es quien porta el import del SDK (AC6)."""
    return _cargar("decision_client_piloto", PUERTA)


@pytest.fixture
def dc():
    """La misma costura, recargada por test y con el nombre de la seleccion hermana.

    Ambito de funcion a proposito: los controles que apagan un simbolo con `monkeypatch` no pueden
    compartir instancia con los que leen el arbol (la leccion del conftest de `decision_client`).
    """
    return _cargar("decision_client_bajo_prueba_jev", PUERTA)


@pytest.fixture(scope="session")
def runner():
    return _cargar("evaluate_jev_pilot_piloto", RUNNER)


@pytest.fixture(scope="session")
def excpcion_de_red():
    """La clase que lanza el guard: por fixture y no por `from conftest import`, que bajo la
    coleccion resuelve al `tests/conftest.py` raiz y no al de esta seleccion."""
    return RedProhibida


@pytest.fixture(scope="session")
def raiz_repo() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def sdk(puerta):
    """El SDK REAL, por la ruta duradera de `FASE-B/entorno.json`.

    Devuelve el dict de `cargar_sdk` (modulo + resolucion efectiva), no solo el modulo: la resolucion
    es la que prueba que `pydantic` sigue siendo el del proyecto.

    Si el entorno aislado no esta en la maquina, se SALTA con su causa nombrada y el salto se cuenta
    en el artefacto: un skip silencioso convertiria la bateria en un verde por vacio, que es justo lo
    que la casa prohibe (L-R.3).
    """
    try:
        cargado = puerta.cargar_sdk()
    except puerta.BrazoNoInstalable as exc:
        pytest.skip(f"el SDK real no esta instalable en esta maquina: {exc}")
    return cargado


@pytest.fixture(scope="session")
def mod(sdk):
    """El modulo `typesafe_sdk` ya cargado: los tests lo usan para clases, RetryPolicy y clientes."""
    return sdk["modulo"]


@pytest.fixture(scope="session")
def httpx2(puerta):
    """El modulo de transporte, pedido a la puerta: un `import httpx2` fuera de ella es HALLAZGOS de AC6.

    Medido el 2026-10-03: la primera version de este fixture importaba httpx2 directamente y el
    escaneo de la casa paso de `SIN-HALLAZGOS` a `1 import prohibido fuera de la puerta`.
    """
    return puerta.cargar_transporte()
