"""Tests de `scripts/verify_index_in_committed_tree.py`.

Los dos anclajes son **revisiones publicadas y fijas**, no HEAD: `911f8d7` es el commit cuyo árbol quedó
con el índice vencido mientras el hook `[6/7]` lo daba en verde, y `c85dff9` es el commit que publicó ese
cierre. Un control anclado a HEAD no tendría con qué compararse en cuanto el árbol se moviera.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VERIFICADOR = ROOT / "scripts" / "verify_index_in_committed_tree.py"

REV_VENCIDA = "911f8d7"
REV_FRESCA = "c85dff9"


def _rev_existe(rev: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(ROOT),
        capture_output=True,
    ).returncode == 0


def _correr(rev: str, destino: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VERIFICADOR), "--rev", rev, "--keep", str(destino)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


@pytest.fixture(autouse=True)
def _anclajes_vivos():
    faltan = [r for r in (REV_VENCIDA, REV_FRESCA) if not _rev_existe(r)]
    if faltan:
        pytest.fail(
            "el anclaje del control se perdió: "
            + ", ".join(faltan)
            + " no está en este repositorio. Re-anclar a otra revisión publicada, no cambiar a HEAD."
        )


def test_pierde_contra_el_commit_cuyo_arbol_nadie_verifico(tmp_path):
    """El rojo que `[6/7]` no vio: `911f8d7` publicó un índice vencido."""
    corrida = _correr(REV_VENCIDA, tmp_path)
    assert corrida.returncode == 1, corrida.stdout + corrida.stderr
    assert "[VENCIDO]" in corrida.stdout


def test_el_rojo_no_es_el_defecto_de_fecha_sino_frescura(tmp_path):
    """Distinguir los dos rojos: con la cura de S15 puesta, `sin_fuente` tiene que seguir en 0.

    Si esta aserción cae, el verificador está midiendo otra cosa (un árbol sin historial, p. ej.) y su
    veredicto sobre `911f8d7` dejaría de significar lo que significa aquí.
    """
    corrida = _correr(REV_VENCIDA, tmp_path)
    fechas = re.search(r"\[fechas\] nombre=(\d+) commit=(\d+) sin_fuente=(\d+)", corrida.stdout)
    assert fechas, f"el verificador no imprimió su línea [fechas]: {corrida.stdout!r}"
    nombre, commit, sin_fuente = fechas.groups()
    assert int(commit) == 11, "las once entradas fechadas por commit perdieron su fuente"
    assert int(sin_fuente) == 0, "el rojo viene de un árbol sin historial, no de un índice vencido"
    assert int(nombre) + int(commit) == 339


def test_pasa_contra_un_commit_cuyo_arbol_si_es_automateria(tmp_path):
    corrida = _correr(REV_FRESCA, tmp_path)
    assert corrida.returncode == 0, corrida.stdout + corrida.stderr
    assert "[OK] índice en el árbol" in corrida.stdout


def test_una_revision_que_no_existe_no_devuelve_veredicto_de_indice(tmp_path):
    """Exit 2, no 1: un método que no produjo árbol evaluable no puede reportar índice vencido."""
    corrida = _correr("no-existe-0000000", tmp_path)
    assert corrida.returncode == 2, corrida.stdout + corrida.stderr
    assert "revisión inexistente" in corrida.stdout
    assert "[VENCIDO]" not in corrida.stdout


def test_el_arbol_materializado_no_queda_parcial(tmp_path):
    """El fallo silencioso de esta herramienta sería un checkout truncado por rutas largas."""
    corrida = _correr(REV_FRESCA, tmp_path)
    materializadas = re.search(r"\((\d+) rutas materializadas\)", corrida.stdout)
    assert materializadas, corrida.stdout
    assert int(materializadas.group(1)) >= 550, "el checkout dejó un árbol parcial: el veredicto es ruido"
