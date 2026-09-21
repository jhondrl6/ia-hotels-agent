"""AC3 (estado 3 de 3) — `LECTOR-FALLIDO` dice el motivo y **nunca** un favorable ni un 0.

Es el estado que L-PF6 convirtio en prohibicion: un lector roto leido como «no habia nada».
Cubre **un solo** estado; los otros dos tienen su propio archivo.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"


def _correr(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def _assert_nada_favorable(salida: str):
    for prohibido in ("SIN-HALLAZGOS", "0 hallazgos", "[OK]", "sin violaciones"):
        assert prohibido not in salida, f"LECTOR-FALLIDO publico «{prohibido}» (R2.9)"


def test_fuente_sin_etiquetas_no_es_ausencia_sino_lector_fallido(gobierno: dict):
    """El archivo existe y se lee, pero no imprime ninguna etiqueta `[N/M]`."""
    fuente_rota = gobierno["tmp"] / "run_all_sin_labels.py"
    fuente_rota.write_text("class Runner:\n    def run_all(self) -> None:\n        pass\n",
                           encoding="utf-8")
    r = _correr("--governance-doc", str(gobierno["doc"]),
                "--source", str(fuente_rota), "--hook", str(gobierno["hook"]))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "LECTOR-FALLIDO" in r.stdout
    assert "motivo:" in r.stdout and "def _check_" in r.stdout
    _assert_nada_favorable(r.stdout)


def test_hook_sin_pasos_tambien_cae(gobierno: dict):
    hook_roto = gobierno["tmp"] / "pre-commit-sin-pasos"
    hook_roto.write_text("#!/bin/sh\necho hola\n", encoding="utf-8")
    r = _correr("--governance-doc", str(gobierno["doc"]),
                "--source", str(gobierno["source"]), "--hook", str(hook_roto))
    assert r.returncode == 3
    assert "LECTOR-FALLIDO" in r.stdout and "hook" in r.stdout
    _assert_nada_favorable(r.stdout)


def test_documento_no_vacio_sin_poblacion_cae(gobierno: dict):
    """Cero instancias en un documento no vacio es «no lei», no «esta limpio» (L-PF10)."""
    doc_vacio = gobierno["tmp"] / "gobierno-sin-conteos.md"
    doc_vacio.write_text("# Gobierno\n\nNada de numeros por aqui.\n", encoding="utf-8")
    r = _correr("--governance-doc", str(doc_vacio),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]))
    assert r.returncode == 3, r.stdout
    assert "LECTOR-FALLIDO" in r.stdout
    _assert_nada_favorable(r.stdout)


def test_dos_sujetos_por_alias_no_se_deciden_a_capon(gobierno: dict):
    """Si dos verificadores reivindican la misma asercion por alias, el lector lo declara.

    Adivinar cual es el sujeto produciria un hallazgo falso contra la fuente del equivocado —
    y ese fue exactamente el defecto de medicion de A3 en la concepcion del plan.
    """
    fuente = gobierno["tmp"] / "run_all_ambigua.py"
    fuente.write_text(
        "class Runner:\n"
        "    def run_all(self) -> None:\n"
        "        self._check_alpha()\n"
        "        self._check_beta()\n\n"
        "    def _check_alpha(self) -> None:\n"
        '        print("[1/2] Checking omega sync...")\n'
        '        script_path = ROOT_DIR / "scripts" / "validate_alpha.py"\n\n'
        "    def _check_beta(self) -> None:\n"
        '        print("[2/2] Checking omega report...")\n'
        '        script_path = ROOT_DIR / "scripts" / "validate_beta.py"\n',
        encoding="utf-8",
    )
    doc = gobierno["tmp"] / "gobierno-ambiguo.md"
    doc.write_text(
        "Omega corre como `[1/2]` de `run_all_validations.py --quick`.\n", encoding="utf-8"
    )
    r = _correr("--governance-doc", str(doc), "--source", str(fuente),
                "--hook", str(gobierno["hook"]))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "LECTOR-FALLIDO" in r.stdout and "alias" in r.stdout
    _assert_nada_favorable(r.stdout)


def test_lector_fallido_no_publica_informe(gobierno: dict):
    informe = gobierno["tmp"] / "informe-caido.json"
    fuente_rota = gobierno["tmp"] / "sin-labels.py"
    fuente_rota.write_text("x = 1\n", encoding="utf-8")
    r = _correr("--governance-doc", str(gobierno["doc"]), "--source", str(fuente_rota),
                "--hook", str(gobierno["hook"]), "--report", str(informe))
    assert r.returncode == 3
    assert not informe.exists()
