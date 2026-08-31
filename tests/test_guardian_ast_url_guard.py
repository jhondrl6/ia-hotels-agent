"""Guardián AST (lección L7/SR-A) — cableado del guard de URL propia.

Los tests unitarios del guard no detectan si alguien elimina la llamada desde
su superficie. Este guardián congela el cableado en las 4 superficies reales
del plan VALIDADOR-URL-PROPIA-2026-08-30:

  1. main.ensure_url()                 (choke point único, D-VUP-A1, exit 2)
  2. WebScraper.extract_hotel_data()   (capa de datos, T2)
  3. V4ComprehensiveAuditor.audit()    (capa de datos, T2)
  4. HookPDFGenerator.extract_data()   (AC7, sobre report_json["url"])

Y la contra-condición de la auditoría F2: en main.py debe haber UNA sola
llamada al guard (en ensure_url) y ninguna al arranque de run_execution_mode /
run_onboard_mode / run_deploy_mode, porque main() ya llama ensure_url() para
todos los comandos — duplicarlo fosilizaría la redundancia.
"""

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MAIN_PATH = REPO_ROOT / "main.py"
SCRAPER_PATH = REPO_ROOT / "modules" / "scrapers" / "web_scraper.py"
AUDITOR_PATH = REPO_ROOT / "modules" / "auditors" / "v4_comprehensive.py"
HOOK_PDF_PATH = REPO_ROOT / "modules" / "commercial_documents" / "hook_pdf_generator.py"


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


# ---------------------------------------------------------------------------
# FASE-B — las otras 3 superficies + anti-duplicación (auditoría F2)
# ---------------------------------------------------------------------------

def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _min_lineno_llamada(func, nombre: str):
    líneas = [n.lineno for n in _llamadas(func, nombre)]
    assert líneas, f"No hay llamadas a {nombre}() en {func.name}()"
    return min(líneas)


@pytest.mark.parametrize(
    "path,superficie",
    [
        (SCRAPER_PATH, "extract_hotel_data"),
        (AUDITOR_PATH, "audit"),
        (HOOK_PDF_PATH, "extract_data"),
    ],
)
def test_superficie_de_capa_datos_llama_al_guard(path, superficie):
    """Sin esta llamada, un llamador de librería (sondas, handlers del harness)
    llega a red/API con una URL de OTA sin pasar por ensure_url()."""
    tree = _tree(path)
    func = _function_def(tree, superficie)
    assert _llamadas(func, "assert_own_site"), (
        f"{path.name}::{superficie}() debe llamar a assert_own_site() "
        "(VALIDADOR-URL-PROPIA FASE-B T2/AC7)"
    )


def test_scraper_guard_antes_de_cualquier_http():
    """El guard debe ir antes del try que hace la petición: dentro del try, el
    except propio se tragaría UrlNoPropiaError."""
    func = _function_def(_tree(SCRAPER_PATH), "extract_hotel_data")
    guard = _min_lineno_llamada(func, "assert_own_site")
    peticiones = [
        n.lineno for n in _llamadas(func, "get")
    ] + [n.lineno for n in ast.walk(func) if isinstance(n, ast.Try)]
    assert peticiones, "extract_hotel_data() dejó de hacer peticiones HTTP: revisar"
    assert guard < min(peticiones), (
        "assert_own_site() debe preceder a cualquier acceso de red en el scraper"
    )


def test_auditor_guard_antes_de_salida_y_red():
    func = _function_def(_tree(AUDITOR_PATH), "audit")
    guard = _min_lineno_llamada(func, "assert_own_site")
    prints = [n.lineno for n in _llamadas(func, "print")]
    assert guard < min(prints), (
        "audit() debe validar la URL antes de imprimir cabecera (señal de que "
        "el pipeline ya arrancó)"
    )


def test_hook_pdf_extrae_force_y_lo_pasa_al_guard():
    """AC7 con bypass: extract_data debe recibir force y pasarlo al guard."""
    func = _function_def(_tree(HOOK_PDF_PATH), "extract_data")
    args = [a.arg for a in func.args.args]
    assert "force" in args, "extract_data() debe exponer force (bypass del operador)"
    llamada = _llamadas(func, "assert_own_site")[0]
    keywords = {k.arg for k in llamada.keywords}
    assert "force" in keywords, "extract_data() debe pasar force a assert_own_site()"


def test_generate_pasa_force_a_extract_data():
    """El --force del CLI llega al guard: generate() debe reenviarlo."""
    func = _function_def(_tree(HOOK_PDF_PATH), "generate")
    llamadas = [
        n for n in _llamadas(func, "extract_data")
        if any(k.arg == "force" for k in n.keywords)
    ]
    assert llamadas, "generate() debe llamar a extract_data(force=force)"


def test_run_hook_pdf_mode_capture_exit_code():
    """Sin este catch, UrlNoPropiaError caería en el except Exception → exit 1,
    divergiendo del exit 2 congelado en FASE-A."""
    func = _function_def(_tree(MAIN_PATH), "run_hook_pdf_mode")
    handlers = [
        h for h in ast.walk(func)
        if isinstance(h, ast.ExceptHandler) and h.type is not None
        and any(
            isinstance(n, ast.Name) and n.id == "UrlNoPropiaError"
            for n in ast.walk(h.type)
        )
    ]
    assert handlers, "run_hook_pdf_mode() debe capturar UrlNoPropiaError"

    salidas = [
        n for n in ast.walk(func)
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute) and n.func.attr == "exit"
        and any(
            (isinstance(a, ast.Constant) and a.value == 2)
            or (isinstance(a, ast.Name) and a.id == "EXIT_CODE_URL_NO_PROPIA")
            for a in n.args
        )
    ]
    assert salidas, "run_hook_pdf_mode() debe salir con el exit code del contrato (2)"


def test_main_tiene_una_sola_llamada_al_guard():
    tree = _tree(MAIN_PATH)
    llamadas = _llamadas(tree, "assert_own_site")
    assert len(llamadas) == 1, (
        f"main.py debe tener UN solo call site del guard (en ensure_url); "
        f"hay {len(llamadas)}. Duplicarlo fosiliza la redundancia (F2)."
    )


@pytest.mark.parametrize(
    "modo", ["run_execution_mode", "run_onboard_mode", "run_deploy_mode"]
)
def test_modos_sin_guard_propio(modo):
    """main() llama ensure_url() para TODOS los comandos: un guard por modo
    sería rechazo duplicado y dos fuentes de verdad del mismo invariante."""
    func = _function_def(_tree(MAIN_PATH), modo)
    assert not _llamadas(func, "assert_own_site"), (
        f"{modo}() NO debe invocar assert_own_site(): el enforcement vive en "
        "ensure_url() (auditoría F2 del plan)"
    )
