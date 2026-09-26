"""Fixtures y guard de cero red de la seleccion FASE-D / `build_phase_briefing.py`.

El contrato de ejecucion de este plan prohibe las llamadas de red en las cuatro fases de
implementacion (§Regla de cero red). FASE-D es determinista y no llama a ningun proveedor, pero
la regla se sostiene con instrumento y no con la palabra: cualquier intento de abrir un socket
dentro de la seleccion reviente con `RedProhibida`.

El modulo bajo prueba se carga **por ruta** (como en B y C) para que el arnes de mutacion de AC23
pueda apagarle simbolos concretos sin reimplementar nada.
"""

from __future__ import annotations

import importlib.util
import os
import re
import socket
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "build_phase_briefing.py"
PLAN = ROOT / ".opencode" / "plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
ARCHIVES = ROOT / ".opencode" / "plans" / "Archives"
WORKFLOW = ROOT / ".agents" / "workflows"
NOMBRE_PLAN = PLAN.name


class RedProhibida(RuntimeError):
    """Alguien intento salir a la red dentro de la seleccion de FASE-D."""


def _bloquear(*nombres):
    def explotar(*a, **kw):
        raise RedProhibida(
            f"FASE-D prohibe llamadas de red; se intento {nombres[0]!r} con args={a[:2]!r}")
    return explotar


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
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


@pytest.fixture
def red_prohibida():
    """La excepcion del guard, expuesta **por fixture**: `from conftest import RedProhibida`
    en una coleccion anidada resuelve al `tests/conftest.py` raiz (L-VCF-10, medido en FASE-B)."""
    return RedProhibida


@pytest.fixture
def ruta_script() -> Path:
    return SCRIPT


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def bpb():
    """El generador bajo prueba, cargado por ruta (AC23 le apaga un simbolo)."""
    return _cargar(f"bpb_bajo_prueba_{os.getpid()}", SCRIPT)


@pytest.fixture
def raiz_arbol():
    return ROOT


# ---------------------------------------------------------------------------
# planes plantados: un prompt que DECLARA lectura y sus documentos, en tmp_path
# ---------------------------------------------------------------------------

PROMPT_QUE_DECLARE = """# FASE-X — plantado para la seleccion

## Prompt de ejecución

```text
Ejecuta unicamente FASE-X del plan
Lee {lectura}
Escribe algo.
```
"""


def _escribir(p: Path, texto: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8", newline="\n")
    return p


@pytest.fixture
def plantear(tmp_path: Path):
    """Planta un plan minimo bajo `tmp_path` y devuelve una fabrica.

    `raiz` es el propio `tmp_path`: el generador resuelve ahi el workflow canonico y las
    rutas de `sources[]`, asi que nada de esto toca el arbol del repo.
    """
    def _plantar(nombre: str = "PLAN-PLANTADO", lectura: str = "01-doc.md §1 y el workflow canónico",
                 secciones_doc1: tuple[str, ...] = ("1", "2"),
                 fases: tuple[str, ...] = ("X",),
                 prompt_texto: str | None = None) -> dict:
        raiz = tmp_path
        plan_dir = raiz / ".opencode" / "plans" / nombre
        cuerpo = ["# Doc 1\n"]
        for s in secciones_doc1:
            cuerpo.append(f"## {s}. Seccion {s}\n\ncontenido {s}\n")
        _escribir(plan_dir / "01-doc.md", "\n".join(cuerpo))
        _escribir(raiz / ".agents/workflows/phased_project_executor.md",
                  "# Workflow\n\nreglas\n")
        texto = (prompt_texto if prompt_texto is not None
                 else PROMPT_QUE_DECLARE.format(lectura=lectura))
        for f in fases:
            _escribir(plan_dir / f"05-prompt-inicio-sesion-fase-{f}.md", texto)
        return {"raiz": raiz, "plan_dir": plan_dir, "nombre": nombre,
                "doc1": plan_dir / "01-doc.md", "fases": list(fases)}
    return _plantar


@pytest.fixture
def workflow_observado() -> dict:
    """sha256 de cada archivo bajo `.agents/`: la linea base de AC17 (cero bytes de la fase)."""
    return {p.relative_to(ROOT).as_posix(): p.stat().st_size
            for p in sorted(WORKFLOW.rglob("*")) if p.is_file()}


def _ids_archivados() -> list[Path]:
    if not ARCHIVES.is_dir():
        return []
    return sorted(d for d in ARCHIVES.iterdir()
                  if d.is_dir() and list(d.glob("05-prompt-inicio-sesion-fase-*.md")))


CORPUS_ARCHIVADO = _ids_archivados()


skip_sin_corpus = pytest.mark.skipif(
    not ARCHIVES.is_dir() or len(CORPUS_ARCHIVADO) < 1,
    reason=(f"R2.6 exige corpus real: no hay planes con 05-prompt-inicio-sesion-fase-*.md bajo "
            f"{ARCHIVES.as_posix()} (medido: {len(CORPUS_ARCHIVADO)})"))
