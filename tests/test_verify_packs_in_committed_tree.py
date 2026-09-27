"""Tests de `scripts/verify_packs_in_committed_tree.py` (cura (b) de S19).

Anclado a `c85dff9`, una **revisión publicada fija**, nunca HEAD: es el commit que publicó el cierre del
registro con sus packs re-sellados, así que su árbol sí tiene que reproducirse. Un control contra HEAD no
tendría con qué compararse en cuanto el árbol se moviera.

El control negativo no simula el defecto: lo ejerce. Copia el writer del clon, cambia el literal que el
propio writer imprime dentro de los packs, y exige dos cosas a la vez — que el verificador pierda y que
`build_phase_briefing.py --check` siga dando verde sobre ese mismo árbol. Eso es S19: el check compara
fuentes, y el escritor no está entre ellas.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
VERIFICADOR = SCRIPTS / "verify_packs_in_committed_tree.py"
sys.path.insert(0, str(SCRIPTS))
from verify_index_in_committed_tree import clon_fiel  # noqa: E402

REV = "c85dff9"
PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
PAQUETES = ("FASE-A.md", "FASE-B.md", "FASE-C.md", "FASE-D.md", "FASE-RELEASE.md")
LITERAL_DEL_ESCRITOR = "[8/11]"   # el puntero al denominador del runner, copiado por el writer al pack


def _rev_existe(rev: str) -> bool:
    return subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}"],
        cwd=str(ROOT), capture_output=True,
    ).returncode == 0


def _arbol(destino: Path) -> Path:
    clon, motivo = clon_fiel(destino, REV)
    assert clon is not None, f"el árbol de {REV} no fue evaluable: {motivo}"
    return clon


def _plan_path(clon: Path) -> Path:
    return clon / ".opencode" / "plans" / PLAN


def _correr(clon: Path | None = None, rev: str = REV) -> subprocess.CompletedProcess:
    args = [sys.executable, str(VERIFICADOR), "--rev", rev]
    if clon is not None:
        args += ["--clon", str(clon)]
    return subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _check_del_writer(clon: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/build_phase_briefing.py", "--plan", PLAN, "--check"],
        cwd=str(clon), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


@pytest.fixture(autouse=True)
def _anclaje_vivo():
    if not _rev_existe(REV):
        pytest.fail(
            f"el anclaje del control se perdió: {REV} no está en este repositorio. "
            "Re-anclar a otra revisión publicada, no cambiar a HEAD."
        )


@pytest.fixture(scope="module")
def _arbol_fiel(tmp_path_factory):
    """Un solo clon limpio para las pruebas que no lo mutan: materializar cuesta ~6 s."""
    return _arbol(tmp_path_factory.mktemp("packs-fiel"))


def test_pasa_sobre_un_commit_cuyos_packs_coinciden(_arbol_fiel):
    corrida = _correr(_arbol_fiel)
    assert corrida.returncode == 0, corrida.stdout + corrida.stderr
    assert "[OK] packs en el árbol" in corrida.stdout
    assert "5/5 reproducidos" in corrida.stdout


def test_la_normalizacion_es_la_que_hace_falta(_arbol_fiel):
    """Sin normalizar el sello, el diff pierde siempre: el writer estampa su reloj (S19, §2 del 19-).

    Dos corridas sucesivas sobre el mismo árbol tienen que dar el mismo veredicto. Si esta prueba cae, el
    verificador no compara el producto sino el minuto en que se corrió.
    """
    primero = _correr(_arbol_fiel)
    segundo = _correr(_arbol_fiel)
    assert primero.returncode == 0 and segundo.returncode == 0
    assert _reproducidos(primero.stdout) == _reproducidos(segundo.stdout)


def _reproducidos(salida: str) -> str:
    m = re.search(r"\((\d+/\d+) reproducidos", salida)
    assert m, salida
    return m.group(1)


def test_detecta_la_edicion_del_escritor_que_el_check_no_ve(tmp_path):
    """El caso S19 reproducido sobre una revisión fija, no simulado."""
    clon = _arbol(tmp_path)
    escritor = clon / "scripts" / "build_phase_briefing.py"
    texto = escritor.read_text(encoding="utf-8")
    assert LITERAL_DEL_ESCRITOR in texto, (
        f"el writer de {REV} ya no imprime {LITERAL_DEL_ESCRITOR}: re-anclar el literal, no la aserción"
    )
    os.unlink(escritor)          # `clone --local` enlaza objetos: se quita el enlace antes de escribir
    escritor.write_text(texto.replace(LITERAL_DEL_ESCRITOR, "[8/99]"),
                        encoding="utf-8", newline="\n")

    ceguera = _check_del_writer(clon)
    assert ceguera.returncode == 0, (
        "el control perdió su premisa: el --check ya no es ciego a la edición del escritor, "
        "y entonces este verificador sobra"
    )

    corrida = _correr(clon)
    assert corrida.returncode == 1, corrida.stdout + corrida.stderr
    assert "[DIVERGE]" in corrida.stdout and "8/99" in corrida.stdout


def test_una_fuente_fuera_del_arbol_no_se_disfraza_de_verde(tmp_path):
    """Sin `docs/`, el escritor no emite FASE-RELEASE: el verificador debe decir 2, no aprobar ni acusar."""
    clon = _arbol(tmp_path)
    shutil.rmtree(clon / "docs")

    corrida = _correr(clon)
    salida = corrida.stdout + corrida.stderr
    assert corrida.returncode == 2, salida
    assert "INCOMPLETO" in salida
    assert re.search(r"\[NO-EVALUABLE\] .*/FASE-RELEASE\.md", salida), salida
    assert "[DIVERGE]" not in salida, (
        "un pack que el árbol no puede producir es un límite del método, no una divergencia del commit"
    )


def test_un_destino_relativo_no_escribe_dentro_del_clon(tmp_path):
    """El bug que cierra esta prueba: con `--keep temp/x`, la ruta del scratch era relativa y el `cwd` del
    subprocess (el clon) la resolvía dentro del propio clon; el veredicto era NO-PRODUCIDO para los cinco
    packs, un rojo que no medía nada."""
    relativa = Path("temp") / f"verif-ruta-{tmp_path.name}"
    destino = Path.cwd() / relativa
    # `tmp_path.name` es estable entre corridas y el `rmtree(ignore_errors=True)` del finally puede dejar
    # el arbol por locking de Windows. Sobre ese residuo `git clone` muere con «already exists and is not
    # an empty directory» y el test falla **sin medir nada**: medido el 2026-09-27 en la segunda pasada
    # seguida de la bateria, con el arbol anterior todavia en `temp/`. Se limpia antes de clonar; el
    # `finally` sigue intentando la salida, pero ya no es lo único que sostiene la aislacion.
    if destino.exists():
        shutil.rmtree(destino, ignore_errors=True)
    if destino.exists():
        pytest.fail(
            f"no se pudo despejar el residuo de la corrida anterior: {destino} sigue en pie "
            "(bloqueo de Windows sobre los objetos del clon). El rojo es de aislamiento, no del "
            "verificador: reintentar la bateria o borrar el directorio a mano."
        )
    try:
        clon, motivo = clon_fiel(relativa, REV)      # destino RELATIVO a propósito
        assert clon is not None, motivo
        assert clon.is_absolute(), "clon_fiel devolvió una ruta relativa: el scratch se desvía"
        corrida = _correr(clon)
        assert "NO-PRODUCIDO" not in corrida.stdout, corrida.stdout
        assert corrida.returncode == 0, corrida.stdout + corrida.stderr
    finally:
        shutil.rmtree(destino, ignore_errors=True)
