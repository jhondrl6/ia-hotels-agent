"""S21 (cura C3): cada modo publica un solo denominador y la guarda corta también fuera del rápido.

La fila §S21 de
`.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` prescribe la
salida **(b)**: publicar en la cabecera a qué modo pertenece el denominador impreso, sin tocar los
literales de las etiquetas — de ellos vive el registro de emisores que lee
`validate_governance_numbers.py`, y la salida (a) lo cegaba.

Dos cosas gobiernan este archivo:

* Los denominadores **no se pinean**: se leen del propio runner con `_orden_del_modo()`, que es la
  misma lectura que goberna la guarda. Re-numerar el runner mueve las pruebas con él.
* Los mutantes corren sobre **copias** del guion (`_runner_copia`), nunca sobre el árbol: el módulo
  copia leído resuelve su propia `__file__`, así que la guarda ejercita el texto mutado sin tocar
  `scripts/`.

Los literales de etiqueta se arman por partes: si quedaran contiguos, la lectura de
`validate_governance_numbers.py` tomaría esta línea como un emisor más del runner.
"""

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_all_validations.py"
GOBERNANZA = ROOT / "scripts" / "validate_governance_numbers.py"

APERTURA = "print(" + '"' + "["
D9 = "[" + "9/13]"
D9_MUTADO = "[" + "9/12]"


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    anterior = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = anterior
    return mod


def _runner_copia(tmp_path: Path, nombre: str, *, mutar=None):
    """Copia del guion, con un literal de etiqueta cambiado si `mutar` lo pide.

    El `assert` de la mutación es parte del control: un mutante que no toca nada da un verde vacío.
    """
    fuente = RUNNER.read_text(encoding="utf-8")
    if mutar is not None:
        viejo, nuevo = mutar
        assert fuente.count(viejo) == 1, (
            f"el mutante no es localizable ({viejo!r} aparece {fuente.count(viejo)} veces): "
            "la prueba no estaría ejercitando nada")
        fuente = fuente.replace(viejo, nuevo, 1)
    ruta = tmp_path / nombre / "run_all_validations.py"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(fuente, encoding="utf-8", newline="\n")
    return _cargar(f"rav_{nombre}", ruta)


def _summary(mod, quick: bool, n: int, capsys) -> tuple:
    """`_print_summary` sobre un runner con `n` resultados puestos, sin correr un solo check."""
    runner = mod.ValidationRunner(quick=quick, verbose=False)
    runner.results = [mod.ValidationResult(f"c{i}", True) for i in range(1, n + 1)]
    capsys.readouterr()
    ok = runner._print_summary()
    return ok, capsys.readouterr().out


@pytest.fixture(scope="module")
def ordenes():
    mod = _cargar("rav_ordenes", RUNNER)
    runner = mod.ValidationRunner()
    rapido, completo = runner._orden_del_modo()
    assert rapido and len(completo) > len(rapido), (
        "el runner dejó de tener exclusivas del modo completo: el mutante de la guarda no tendría "
        "segundo denominador que aprobar")
    return len(rapido), len(completo)


def test_la_cabecera_publica_el_denominador_de_cada_modo(tmp_path, capsys, ordenes):
    n_rapido, n_completo = ordenes
    mod = _runner_copia(tmp_path, "cabecera")
    for quick, n, etiqueta in ((True, n_rapido, "rapido"), (False, n_completo, "completo")):
        ok, salida = _summary(mod, quick, n, capsys)
        linea = [l for l in salida.splitlines() if "MODO:" in l]
        assert len(linea) == 1, f"el modo {etiqueta} no publica su cabecera: {salida!r}"
        assert f"es el del modo rapido ({n_rapido})" in linea[0], (
            f"la cabecera del modo {etiqueta} no publica el denominador del rapido: {linea[0]!r}")
        assert f"el modo completo llega a {n_completo}" in linea[0], (
            f"la cabecera no nombra el denominador del completo: {linea[0]!r}")
        assert "el denominador de las etiquetas impresas es el del modo rapido" in linea[0], (
            f"la cabecera no dice a que modo pertenece el denominador impreso: {linea[0]!r}")
        assert APERTURA not in linea[0], (
            "la cabecera se escribió como etiqueta [N/M]: el lector de gobernanza la tomaría por "
            "un emisor más")
        assert ok is True, f"un modo coherente debería dar verde: {salida[-400:]}"


def test_la_guarda_aprueba_los_dos_denominadores_legitimos_del_completo(tmp_path, capsys, ordenes):
    """Control anti-rojo-falso: 13 y 17 conviviendo es el diseño de §S21, no un desalineado."""
    _, n_completo = ordenes
    mod = _runner_copia(tmp_path, "legal")
    ok, salida = _summary(mod, False, n_completo, capsys)
    assert ok is True, f"la guarda cortó los dos denominadores legítimos: {salida[-500:]}"
    assert "NO CASAN" not in salida


def test_la_guarda_corta_un_denominador_ajeno_en_el_modo_completo(tmp_path, capsys, ordenes):
    """El mutante de C3: un denominador 9 sobre 12 suelto era verde fuera del rápido antes de la cura."""
    _, n_completo = ordenes
    mod = _runner_copia(tmp_path, "ajeno-completo", mutar=(D9, D9_MUTADO))
    ok, salida = _summary(mod, False, n_completo, capsys)
    assert ok is False, (
        "la guarda dejó pasar un denominador foráneo en el modo completo: §S21 sigue sin gobernar")
    assert "NO CASAN" in salida, f"el rojo no se nombra a si mismo: {salida[-500:]!r}"
    publicado = re.search(r"denominadores \[([0-9, ]+)\]", salida)
    assert publicado, f"el rojo no publica los denominadores que cortaron: {salida[-500:]!r}"
    assert "12" in publicado.group(1).replace(" ", "").split(","), (
        f"el rojo no nombra el denominador que sobra: {publicado.group(1)!r}")


def test_la_guarda_sigue_cortando_ese_mismo_denominador_en_el_rapido(tmp_path, capsys, ordenes):
    """La misma mutación, modo rápido: el corte que ya existía no se aflojó con la cura."""
    n_rapido, _ = ordenes
    mod = _runner_copia(tmp_path, "ajeno-rapido", mutar=(D9, D9_MUTADO))
    ok, salida = _summary(mod, True, n_rapido, capsys)
    assert ok is False, f"el modo rápido aflojó su corte: {salida[-500:]!r}"
    assert "NO CASAN" in salida


def test_el_lector_de_gobernanza_sigue_resolviendo_las_etiquetas(tmp_path, ordenes):
    """«Prohibido romper al lector»: la etiqueta impresa sigue siendo su fuente de verdad."""
    n_rapido, n_completo = ordenes
    destino = tmp_path / "informe.json"
    r = subprocess.run([sys.executable, str(GOBERNANZA), "--report", str(destino)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    cb = json.loads(destino.read_text(encoding="utf-8"))["coverage_basis"]
    assert cb["fuentes"]["quick"]["total"] == n_rapido, (
        f"el lector ya no resuelve el denominador del rápido ({cb['fuentes']['quick']['total']} "
        f"contra {n_rapido} del runner)")
    assert cb["fuentes"]["solo_completo"]["total"] == n_completo, (
        "el lector ya no resuelve el denominador del completo")
    fuente = RUNNER.read_text(encoding="utf-8")
    etiquetas = re.findall("print" + r"""\(f?["']\[(\d+)/(\d+)\]""", fuente)
    assert len(etiquetas) == n_completo, (
        f"el runner imprime {len(etiquetas)} etiquetas para {n_completo} checks: hay un emisor "
        "de más (la cabecera nueva) o uno perdido")
