"""Cero red de FASE-D, con instrumento y no con la palabra (L-VCF-10).

El `conftest.py` de esta seleccion monta un guard `autouse` que bloquea `socket`. Un guard que
nadie dispara es la variante de L-VCF-13: «cero llamadas» es cierto sobre un insumo que nunca
intento llamar. Se prueban las dos cosas que hacen falta:

1. que el guard **dispara** dentro de la seleccion (con su excepcion accesible por fixture, no
   por `from conftest import ...`, que en colecciones anidadas resuelve al conftest raiz —
   L-VCF-10 medido en FASE-B), y
2. que el generador **no necesita** dispararlo: su superficie de imports esta auditada por AST
   sobre el archivo real, y cargarlo no arrastra ningun cliente a `sys.modules`.

El punto 2 sostiene la afirmacion; el punto 1 sostiene el instrumento. Sin el 1, el 2 se podria
leer sobre un guard roto.
"""

from __future__ import annotations

import ast
import importlib.util
import socket
import sys

import pytest

# Modulos capaces de establecer un canal, de resolver un nombre para abrirlo, o de abrirlo por
# rebote (invocar un binario que llame). Es la misma familia que exercito FASE-B en su
# `cero-red.txt`; se re-declara aqui para que este archivo se lea sin ir a buscar la lista a otra
# seleccion.
MODULOS_CAPACES_DE_RED = {
    "socket", "ssl", "http", "urllib", "urllib3", "ftplib", "smtplib", "poplib", "imaplib",
    "telnetlib", "requests", "httpx", "aiohttp", "websocket", "wsgiref", "xmlrpc", "asyncio",
    "subprocess", "os", "pathlib", "shutil",
}

# `subprocess`, `os`, `pathlib` y `shutil` estan en el generador y no son red: se auditan abajo
# con su uso, en lugar de declarar un cero comodo que los negara.
PERMITIDOS_POR_ESCRITURA = {"subprocess", "os", "pathlib", "shutil"}

VETADOS_EN_SYS_MODULES = {"requests", "httpx", "urllib3", "http", "ssl", "websocket", "aiohttp",
                          "decision_client"}


def _modulos_importados(ruta) -> set:
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
            modulos.add(nodo.module.split(".")[0])
    return modulos


def test_el_guard_de_red_dispara_dentro_de_la_seleccion(red_prohibida):
    """Si esta prueba pasara sin el guard montado, el guard no existe."""
    with pytest.raises(red_prohibida):
        socket.socket()


def test_el_guard_tambien_corta_la_resolucion_de_nombres(red_prohibida):
    with pytest.raises(red_prohibida):
        socket.getaddrinfo("example.invalid", 443)


def test_la_superficie_de_imports_del_generador_esta_auditada(ruta_script):
    importados = _modulos_importados(ruta_script)
    capaces = importados & MODULOS_CAPACES_DE_RED
    assert capaces <= PERMITIDOS_POR_ESCRITURA, (
        f"modulos de red sin auditar en el generador: "
        f"{sorted(capaces - PERMITIDOS_POR_ESCRITURA)}")


def test_los_permisos_por_escritura_no_se_usan_para_llamar(ruta_script):
    """`subprocess` si esta: se audita que su unico destino sea `git`, no un cliente HTTP."""
    arbol = ast.parse(ruta_script.read_text(encoding="utf-8"))
    argumentos = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute) \
                and nodo.func.attr in {"run", "check_output", "Popen", "call"}:
            for arg in nodo.args:
                if isinstance(arg, (ast.List, ast.Tuple)):
                    argumentos.append([e.value for e in arg.elts if isinstance(e, ast.Constant)])
    assert argumentos, "el generador invoca subprocess: la auditoria necesita el caso"
    for comando in argumentos:
        assert comando and comando[0] in {"git"}, f"invocacion no auditada: {comando}"


def test_cargar_el_generador_no_arrasta_clientes_a_sys_modules(ruta_script):
    nombre = "bpb_cero_red"
    sys.modules.pop(nombre, None)
    antes = set(sys.modules)
    spec = importlib.util.spec_from_file_location(nombre, ruta_script)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    nuevos = {m.split(".")[0] for m in set(sys.modules) - antes}
    assert not (nuevos & VETADOS_EN_SYS_MODULES), (
        f"cargar el generador arrastro: {sorted(nuevos & VETADOS_EN_SYS_MODULES)}")
