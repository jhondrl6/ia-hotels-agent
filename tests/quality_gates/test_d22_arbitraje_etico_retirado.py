"""FASE-H2 (`D22`, AC8): el dead code de `validar_arbitraje_etico` queda retirado.

`D22` midio una funcion con su bateria de 12 tests y **cero** consumidores de produccion:
el gate etico que si corre en `v4complete` es `EthicsGate`, instanciado en
`PublicationGateRunner` y ejecutado por `run_publication_gates`. Un nombre con "gate" en su
docstring que nadie invoca es un gate aparente, y eso es lo que este archivo impide que vuelva.

Los dientes se anclan al AST del arbol (definiciones), no a un grep de menciones: una funcion
que se re-introduce sin llamador vuelve a caer aqui.
"""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULOS = ROOT / "modules"
TESTS = ROOT / "tests"
SIMBOLO = "validar_arbitraje_etico"
MODULO_RETIRADO = "modules.quality.financial_coherence_validator"


def _definiciones_de_funcion(arbol: Path) -> dict:
    """nombre de funcion -> ruta, para todo .py bajo `arbol` (sin __pycache__)."""
    halladas = {}
    for archivo in arbol.rglob("*.py"):
        if "__pycache__" in archivo.parts:
            continue
        for nodo in ast.walk(ast.parse(archivo.read_text(encoding="utf-8"), filename=str(archivo))):
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                halladas.setdefault(nodo.name, archivo)
    return halladas


def test_la_funcion_no_se_define_en_modulos():
    """Retirar el dead code es que no exista, no que este comentado."""
    definiciones = _definiciones_de_funcion(MODULOS)
    assert SIMBOLO not in definiciones, (
        f"{SIMBOLO} volvio a definirse en {definiciones.get(SIMBOLO)} sin consumidor de produccion"
    )


def test_el_modulo_no_importa():
    """El modulo entero se retiro: quien lo pida recibe ModuleNotFoundError, no un stub."""
    with pytest.raises(ModuleNotFoundError):
        __import__(MODULO_RETIRADO)


def test_no_queda_su_bateria_de_tests():
    """El test que certificaba la configuracion muerta se retiro con ella."""
    propio = Path(__file__).resolve()
    assert not (TESTS / "quality_gates" / "test_financial_coherence_validator.py").exists()
    # Este archivo nombra el simbolo para cortarlo: se excluye a si mismo del barrido.
    citantes = [
        archivo
        for archivo in TESTS.rglob("*.py")
        if "__pycache__" not in archivo.parts
        and archivo.resolve() != propio
        and SIMBOLO in archivo.read_text(encoding="utf-8")
    ]
    assert citantes == [], f"aun hay tests que ejercitan {SIMBOLO}: {citantes}"


def test_el_gate_etico_real_no_se_muevo():
    """`EthicsGate` sigue siendo el gate etico de verdad: importado, instanciado y cableado."""
    fuente = (MODULOS / "quality_gates" / "publication_gates.py").read_text(encoding="utf-8")
    assert "from modules.quality_gates.ethics_gate import EthicsGate" in fuente
    assert "self.ethics_gate = EthicsGate()" in fuente
    assert "self.ethics_gate.validate_from_assessment(assessment)" in fuente
    assert (MODULOS / "quality_gates" / "ethics_gate.py").exists()


def test_no_queda_como_gate_aparente_en_la_prosa_del_codigo():
    """Ningun codigo vivo vuelve a anunciar un 'arbitraje etico' que nadie ejecuta."""
    vivas = [MODULOS] + [ROOT / "scripts"] + [ROOT / "main.py"]
    menciones = []
    for raiz in vivas:
        archivos = [raiz] if raiz.is_file() else list(raiz.rglob("*.py"))
        for archivo in archivos:
            if "__pycache__" in archivo.parts:
                continue
            if "arbitraje" in archivo.read_text(encoding="utf-8").lower():
                menciones.append(archivo)
    assert menciones == [], f"el nombre del gate retirado revive en la prosa: {menciones}"

