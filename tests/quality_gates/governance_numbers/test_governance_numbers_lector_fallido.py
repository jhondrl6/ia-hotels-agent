"""AC3 (estado 3 de 3) — `LECTOR-FALLIDO` dice el motivo y **nunca** un favorable ni un 0.

Es el estado que L-PF6 convirtio en prohibicion: un lector roto leido como «no habia nada».
Cubre **un solo** estado; los otros dos tienen su propio archivo.
"""

import json
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


def test_documento_vacio_tambien_cae(gobierno: dict):
    """Poblacion AUSENTE en su forma mas literal: un documento de gobierno de 0 bytes pasaba sin
    instancias y sin hallazgos, y salia `SIN-HALLAZGOS` con exit 0 — un favorable sobre un documento
    que no audito nada (orden 2026-09-22 §4.A-a: poblacion ausente/vacia no produce favorable ni 0)."""
    doc_en_blanco = gobierno["tmp"] / "gobierno-en-blanco.md"
    doc_en_blanco.write_text("", encoding="utf-8")
    r = _correr("--governance-doc", str(doc_en_blanco),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]))
    assert r.returncode == 3, r.stdout + r.stderr
    assert "LECTOR-FALLIDO" in r.stdout
    assert "vacio" in r.stdout
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


def test_hallazgos_de_un_documento_se_conservan_cuando_otro_falla(gobierno: dict):
    """Sesion 3, §4.A-a: con dos documentos y uno ilegible para el patron, el exit sigue siendo 3
    (nunca favorable), pero los hallazgos del documento sano se conservan en el informe parcial y
    el stdout de `--json` sigue siendo JSON parseable con la causa del fallo."""
    doc_vencido = gobierno["tmp"] / "gobierno-vencido-parcial.md"
    doc_vencido.write_text(
        "# Gobierno vencido de prueba\n\n"
        "**Verificador**: `scripts/validate_alpha.py` es check 7 de `run_all_validations.py"
        " --quick`.\n"
        "Beta corre como `[9/9]` de `run_all_validations.py --quick` "
        "(`scripts/validate_beta.py`).\n",
        encoding="utf-8")
    doc_vacio = gobierno["tmp"] / "gobierno-en-blanco-2.md"
    doc_vacio.write_text("", encoding="utf-8")
    r = _correr("--governance-doc", str(doc_vencido), "--governance-doc", str(doc_vacio),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]), "--json")
    assert r.returncode == 3, r.stdout + r.stderr
    informe = json.loads(r.stdout)
    assert informe["status"] == "LECTOR-FALLIDO"
    assert len(informe["findings"]) >= 1, (
        "el fallo del segundo documento borro los hallazgos del primero")
    assert any("vacio" in f["motivo"] for f in informe["fallos_de_lectura"]), informe["fallos_de_lectura"]


def test_documento_que_falla_no_deja_informe_en_el_destino(gobierno: dict):
    """El contrato FASE-A de «LECTOR-FALLIDO no publica informe» aplica tambien cuando la
    incompletitud nace de un documento: el destino nombrado no se escribe, ni siquiera parcial."""
    doc_vacio = gobierno["tmp"] / "gobierno-en-blanco-3.md"
    doc_vacio.write_text("", encoding="utf-8")
    destino = gobierno["tmp"] / "no-debe-existir.json"
    r = _correr("--governance-doc", str(gobierno["doc"]), "--governance-doc", str(doc_vacio),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]),
                "--report", str(destino))
    assert r.returncode == 3, r.stdout + r.stderr
    assert not destino.exists(), "un verificador con lectura incompleta no debe publicar informe"


def test_documento_ausente_no_descarta_los_hallazgos_del_legible(gobierno: dict):
    """Sesion 4: la AUSENCIA de un documento en poblacion mixta era una puerta previa al analisis
    que devolvia exit 2 con stdout en prosa y DESCARTABA los hallazgos del documento legible
    (medido: doc legible + ruta ausente -> exit 2, json_parseable=false, hallazgos_perdidos).
    Ahora es la misma incompletitud de §4.A-a que un documento ilegible: se analizan los
    legibles, la ruta ausente se publica con su causa y el estado es LECTOR-FALLIDO (exit 3)."""
    doc_vencido = gobierno["tmp"] / "gobierno-vencido-ausente.md"
    doc_vencido.write_text(
        "# Gobierno vencido de prueba\n\n"
        "**Verificador**: `scripts/validate_alpha.py` es check 7 de `run_all_validations.py"
        " --quick`.\n"
        "Beta corre como `[9/9]` de `run_all_validations.py --quick` "
        "(`scripts/validate_beta.py`).\n",
        encoding="utf-8")
    ausente = gobierno["tmp"] / "no-existe.md"
    r = _correr("--governance-doc", str(doc_vencido), "--governance-doc", str(ausente),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]), "--json")
    assert r.returncode == 3, r.stdout + r.stderr
    informe = json.loads(r.stdout)  # el exit 2 en prosa rompia el JSON por stdout
    assert informe["status"] == "LECTOR-FALLIDO"
    assert len(informe["findings"]) >= 1, (
        "la ruta ausente borro los hallazgos del documento legible")
    fallo = next(f for f in informe["fallos_de_lectura"] if "no-existe.md" in f["document"])
    assert "no existe" in fallo["motivo"] and "AUSENTE" in fallo["motivo"], fallo
    _assert_nada_favorable(json.dumps(
        [f["motivo"] for f in informe["fallos_de_lectura"]], ensure_ascii=False))


def test_poblacion_sin_nada_analizable_sigue_siendo_ausente_exit_2(gobierno: dict):
    """Frontera de la semantica mixta: el exit 2 (AUSENTE) responde solo cuando no queda ningun
    documento analizable. (La ausencia de la fuente/hook tiene su propio test en
    `test_governance_numbers_ausente.py`.)"""
    r = _correr("--governance-doc", str(gobierno["tmp"] / "tampoco-existe.md"),
                "--governance-doc", str(gobierno["tmp"] / "y-este-tampoco.md"),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]))
    assert r.returncode == 2, r.stdout + r.stderr
    assert "AUSENTE" in r.stdout
    _assert_nada_favorable(r.stdout)


def test_documento_ausente_no_deja_informe_en_el_destino(gobierno: dict):
    """La incompletitud por AUSENCIA hereda el contrato de LECTOR-FALLIDO: el destino nombrado no
    se escribe ni parcialmente."""
    destino = gobierno["tmp"] / "no-debe-existir-ausente.json"
    r = _correr("--governance-doc", str(gobierno["doc"]),
                "--governance-doc", str(gobierno["tmp"] / "tampoco-existe-2.md"),
                "--source", str(gobierno["source"]), "--hook", str(gobierno["hook"]),
                "--report", str(destino))
    assert r.returncode == 3, r.stdout + r.stderr
    assert not destino.exists(), "un verificador con lectura incompleta no debe publicar informe"
