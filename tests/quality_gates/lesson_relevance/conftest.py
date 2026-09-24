"""Fixtures y **guard de cero red** de la seleccion FASE-C / `triage_lesson_relevance.py`.

El contrato de ejecucion de este plan prohibe una sola llamada de red (§Regla de cero red), y aqui el
riesgo es mayor que en FASE-B porque C es el primer consumidor que *pide juicios*. El guard hace que
cualquier intento de abrir un socket, resolver un nombre o negociar TLS reviente con
`RedProhibida`, asi que una fuga es un rojo ruidoso y no un verde silencioso.

El proveedor falso se monta **en `tmp_path`** con las dos variables de entorno que resuelve la puerta
(`IAH_DECISION_PROVIDER` + `IAH_DECISION_PROVIDERS_DIR`): C no tiene ninguna ruta de proveedor por
defecto, igual que B. Si el entorno externo ya trae las dos, el fixture no las toca — es el camino por
el que la corrida de evidencia pasa las variables a mano y publica el comando completo.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import socket
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "triage_lesson_relevance.py"
DOOR = ROOT / "scripts" / "decision_client.py"
FALOS = Path(__file__).resolve().parent / "falsos_proveedores_triage"
PLAN = ROOT / ".opencode" / "plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
ARCHIVES = ROOT / ".opencode" / "plans" / "Archives"
NOMBRE_PLAN = PLAN.name


class RedProhibida(RuntimeError):
    """Alguien intento salir a la red dentro de la seleccion de FASE-C."""


def _bloquear(*nombres):
    def explotar(*a, **kw):
        raise RedProhibida(f"FASE-C prohibe llamadas de red; se intento {nombres[0]!r} con args={a[:2]!r}")
    return explotar


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    """Autouse: arma el guard antes de cada caso y lo deja despues."""
    parches = {"socket": _bloquear("socket.socket"),
               "create_connection": _bloquear("socket.create_connection"),
               "getaddrinfo": _bloquear("socket.getaddrinfo"),
               "gethostbyname": _bloquear("socket.gethostbyname")}
    reales = {k: getattr(socket, k) for k in parches}
    for k, v in parches.items():
        monkeypatch.setattr(socket, k, v)
    yield
    for k, v in reales.items():
        setattr(socket, k, v)


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def trl():
    """El modulo bajo prueba, cargado por ruta: los mutantes de AC14 le apagan simbolos."""
    return _cargar(f"trl_bajo_prueba_{os.getpid()}", SCRIPT)


@pytest.fixture
def puerta():
    """La unica puerta al proveedor (AC6): se carga para afirmar forma, nunca para saltarla."""
    return _cargar("decision_client_para_triage", DOOR)


@pytest.fixture
def proveedores_falsos(tmp_path: Path) -> Path:
    """El proveedor falso, **montado en tmp_path** como en FASE-B: nada del arbol de produccion."""
    destino = tmp_path / "proveedores_triage"
    destino.mkdir(parents=True, exist_ok=True)
    for src in sorted(FALOS.glob("*.py")):
        shutil.copy2(src, destino / src.name)
    return destino


@pytest.fixture
def entorno_falso(monkeypatch, proveedores_falsos) -> dict:
    """Entorno resuelto por variable, como lo resuelve la puerta. Sin default de proveedor."""
    monkeypatch.setenv("IAH_DECISION_PROVIDER", "falso-pertinencia")
    monkeypatch.setenv("IAH_DECISION_PROVIDERS_DIR", str(proveedores_falsos))
    return dict(os.environ)


@pytest.fixture
def indice_real() -> Path:
    return ROOT / ".opencode" / "lecciones_index.json"


@pytest.fixture
def ancladas_reales(trl) -> list[dict]:
    """Las filas de §2 del plan triado, leidas por el mismo camino que usa el triaje."""
    return trl.filas_ancladas(PLAN / "00-lecciones-capitalizadas.md")


@pytest.fixture
def corpus_archivado() -> list[Path]:
    """Planes **reales** de `.opencode/plans/Archives/` que tienen su `00-` (desviacion declarada AC13)."""
    if not ARCHIVES.is_dir():
        return []
    return sorted(p.parent for p in ARCHIVES.glob("*/00-lecciones-capitalizadas.md"))


@pytest.fixture
def informe_real(trl, entorno_falso) -> dict:
    """Una corrida completa del triaje sobre ESTE plan, con el proveedor falso determinista."""
    indice, estado = trl.leer_suelo()
    ancladas = trl.filas_ancladas(PLAN / "00-lecciones-capitalizadas.md")
    pendientes = trl.candidatos_de_pertinencia(indice, NOMBRE_PLAN, ancladas)
    return trl.construir_informe(NOMBRE_PLAN, pendientes, ancladas, indice, estado,
                                 entorno=entorno_falso)
