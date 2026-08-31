"""Guardián AST (lección L7/SR-A) — cableado del guard de URL propia.

Los tests unitarios del guard no detectan si alguien elimina la llamada desde
ensure_url(); este guardián congela el cableado en el choke point único
(D-VUP-A1): ensure_url DEBE invocar assert_own_site y capturar
UrlNoPropiaError con sys.exit(2). FASE-B lo extenderá a las demás superficies.
"""

import ast
from pathlib import Path

MAIN_PATH = Path(__file__).resolve().parent.parent / "main.py"


def _function_def(tree: ast.Module, nombre: str) -> ast.FunctionDef:
    defs = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == nombre
    ]
    assert defs, f"No existe la función {nombre}() en main.py"
    return defs[0]


def _llamadas(func: ast.FunctionDef, nombre: str):
    return [
        n for n in ast.walk(func)
        if isinstance(n, ast.Call) and (
            (isinstance(n.func, ast.Name) and n.func.id == nombre)
            or (isinstance(n.func, ast.Attribute) and n.func.attr == nombre)
        )
    ]


def test_ensure_url_invoca_assert_own_site():
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8"))
    ensure_url = _function_def(tree, "ensure_url")
    assert _llamadas(ensure_url, "assert_own_site"), (
        "ensure_url() debe llamar a own_site_guard.assert_own_site() "
        "(VALIDADOR-URL-PROPIA FASE-A: choke point único del guard)"
    )


def test_ensure_url_captura_url_no_propia_y_sale_con_2():
    tree = ast.parse(MAIN_PATH.read_text(encoding="utf-8"))
    ensure_url = _function_def(tree, "ensure_url")

    handlers = [
        h for h in ast.walk(ensure_url)
        if isinstance(h, ast.ExceptHandler) and h.type is not None
        and any(
            (isinstance(h.type, ast.Name) and h.type.id == "UrlNoPropiaError")
            or (isinstance(n, ast.Name) and n.id == "UrlNoPropiaError")
            for n in ast.walk(h.type)
        )
    ]
    assert handlers, "ensure_url() debe capturar UrlNoPropiaError"

    exit_2 = [
        n for n in ast.walk(ensure_url)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute) and n.func.attr == "exit"
        and any(isinstance(a, ast.Constant) and a.value == 2 for a in n.args)
    ]
    assert exit_2, "ensure_url() debe terminar con sys.exit(2) ante URL no propia"
