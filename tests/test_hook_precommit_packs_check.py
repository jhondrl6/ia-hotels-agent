"""Letra C de la tanda 2026-10-01: el verificador de packs del arbol commiteado entra al pre-commit.

Origem medido (2026-10-01): `verify_packs_in_committed_tree.py` corria en `--quick` pero no en el hook,
asi que un commit que movia una fuente proyectada pasaba 7/7 y dejaba el tip con DIVERGE publicado; el
rojo solo lo veia el siguiente `--quick`. La cura lo cablea como `[8/8]`. Coste medido de la corrida:
~3,3 s por commit (clon temporal del arbol de HEAD con `clon_fiel`).

Los dientes de este archivo leen la **estructura** del hook versionado, no una cota magicada: si la
numeracion se re-numera sin mover el script, caen; si el script sale del hook, caen; y un mutante que
borra la invocacion en una copia de scratch prueba que la asercion tiene sensibilidad (misma tecnica
que `test_validate_plan_closure.py::test_registrado_como_check_5_en_el_hook`).
"""

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOOK = ROOT / "scripts" / "git_hooks" / "pre-commit"

ETIQUETA_RE = re.compile(r"\[(\d+)/(\d+)\]")


def _texto_hook() -> str:
    return HOOK.read_text(encoding="utf-8")


def test_el_hook_versionado_invoca_el_verificador_de_packs():
    src = _texto_hook()
    assert "verify_packs_in_committed_tree.py" in src, (
        "el verificador de packs del arbol commiteado salio del hook: el hueco medido "
        "el 2026-10-01 (commit que mueve una fuente proyectada y pasa con el tip rojo) "
        "vuelve a estar abierto")


def test_el_check_de_packs_es_el_ultimo_y_con_denominador_coherente():
    src = _texto_hook()
    etiquetas = [(int(i), int(n)) for i, n in ETIQUETA_RE.findall(src)]
    assert etiquetas, "el hook ya no numera sus checks"
    denominadores = {n for _, n in etiquetas}
    assert len(denominadores) == 1, f"denominadores mezclados en el hook: {denominadores}"
    n = denominadores.pop()
    assert sorted({i for i, _ in etiquetas}) == list(range(1, n + 1)), f"ordinales rotos: {etiquetas}"
    # En el cuerpo ejecutable (no en la cabecera de comentarios), la invocacion cuelga del ultimo
    # ordinal: despues del OK del bloque anterior y antes del suyo.
    cuerpo = src.split("set -e", 1)[1]
    assert cuerpo.index("scripts/verify_packs_in_committed_tree.py") > cuerpo.index(f"[{n - 1}/{n}] OK"), (
        "el verificador de packs no se invoca en el ultimo bloque del hook")
    assert f"[{n}/{n}] OK" in cuerpo.split("scripts/verify_packs_in_committed_tree.py", 1)[1], (
        "el ordinal final del hook no estampa el OK de los packs")


def test_el_bloque_de_packs_corta_por_exit_distinto_de_cero():
    """EXIT 1 (DIVERGE) y EXIT 2 (NO-EVALUABLE) deben bloquear: el 2 no se disfraza de verde."""
    src = _texto_hook()
    bloque = src.split("verify_packs_in_committed_tree.py", 1)[1]
    bloque = bloque.split("All checks PASSED", 1)[0]
    assert re.search(r"PACKS_EXIT", bloque), "el bloque de packs no captura el exit del verificador"
    assert re.search(r'-ne 0', bloque), "el bloque de packs no corta por exit distinto de cero"
    assert re.search(r"\bexit 1\b", bloque), "el bloque de packs no bloquea el commit"
    assert "NO-EVALUABLE" in bloque, "la salida 2 (verde no probado) no esta declarada en el mensaje"


def test_el_comentario_de_cabecera_enumera_tantos_checks_como_el_denominador():
    src = _texto_hook()
    cabecera = src.split("set -e", 1)[0]
    lineas = ETIQUETA_RE.findall(cabecera)
    denominadores = {int(n) for _, n in lineas}
    assert len(denominadores) == 1, f"cabecera con denominadores mezclados: {denominadores}"
    n = denominadores.pop()
    assert sorted(int(i) for i, _ in lineas) == list(range(1, n + 1)), (
        "la cabecera del hook no enumera sus checks completa")
    # Y coincide con el denominador que publican los bloques ejecutados.
    cuerpo = src.split("set -e", 1)[1]
    assert {int(nn) for _, nn in ETIQUETA_RE.findall(cuerpo)} == {n}


def test_el_hook_instalado_es_identico_al_versionado_en_esta_maquina():
    """Solo si el hook existe instalado: en un clon sin instalar, el verde del quick lo cubre igual."""
    instalado = ROOT / ".git" / "hooks" / "pre-commit"
    if not instalado.exists():
        import pytest
        pytest.skip("hook no instalado en este clon: la capa rapida sigue cubriendo el check")
    assert instalado.read_text(encoding="utf-8") == _texto_hook(), (
        "el hook instalado diverge del versionado: python scripts/install_git_hooks.py")


def test_mutante_sin_invocacion_hace_cair_la_primera_diente():
    """Los dientes tienen sensibilidad: una copia sin el nombre del verificador pierde diente [1]."""
    scratch = Path(tempfile.mkdtemp(prefix="hook-mutante-"))
    try:
        src = _texto_hook()
        mutado = src.replace("verify_packs_in_committed_tree.py", "_sin_invocar.py")
        assert mutado != src, "el hook ya no invoca el verificador: no hay nada que mutar"
        (scratch / "pre-commit").write_text(mutado, encoding="utf-8")
        copia = (scratch / "pre-commit").read_text(encoding="utf-8")
        assert "verify_packs_in_committed_tree.py" not in copia, (
            "la mutacion no borro el nombre: la diente [1] no estaria midiendo nada")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
