"""AC1 + AC2 — `validate_governance_numbers.py` reproduce A1-A4 del maestro §1 y ninguna otra.

El verde de este archivo no puede venir de haber recortado la poblacion a mano: por eso afirma
tambien el conteo de `historical_excluded[]` (A8) y la suma interna de las tres clases.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"


def _informe(destino: Path) -> dict:
    r = subprocess.run([sys.executable, str(SCRIPT), "--report", str(destino)],
                       capture_output=True, text=True)
    assert r.returncode == 1, f"se esperaban hallazgos, salio {r.returncode}: {r.stdout}{r.stderr}"
    return json.loads(destino.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def informe_real(tmp_path_factory) -> dict:
    destino = tmp_path_factory.mktemp("gn") / "informe.json"
    return _informe(destino)


def test_findings_son_exactamente_A1_A4(informe_real: dict):
    assert [f["assertion_id"] for f in informe_real["findings"]] == ["A1", "A2", "A3", "A4"]


def test_cada_hallazgo_trae_su_clave_legible(informe_real: dict):
    for f in informe_real["findings"]:
        for clave in ("assertion_id", "document", "claimed", "observed", "occurrences"):
            assert clave in f, f"{f.get('assertion_id')} no publica {clave} (R2.4)"
        assert f["occurrences"], "un hallazgo sin occurrences no es auditable"


def test_claimed_y_observed_cuadran_con_el_maestro(informe_real: dict):
    por_id = {f["assertion_id"]: f for f in informe_real["findings"]}
    assert por_id["A1"]["claimed"] == "check 8" and por_id["A1"]["observed"] == "[9/11]"
    assert por_id["A2"]["claimed"] == "[9/9]" and por_id["A2"]["observed"] == "[10/11]"
    assert por_id["A3"]["claimed"] == "[12/12]" and por_id["A3"]["observed"] == "[15/15]"
    # A4 es PARCIAL: su [7/7] del hook si cuadra, y solo el [10/10] del quick no.
    assert por_id["A4"]["claimed"] == "[10/10]" and por_id["A4"]["observed"] == "[10/11]"


def test_poblacion_de_A8_publicada_y_suma(informe_real: dict):
    p = informe_real["coverage_basis"]["poblacion"]
    assert p["instancias_totales"] == 24, (
        "A8 midio 22 instancias `[N/M]` + 2 formas «check N»; si esto cambia, la regla de "
        "poblacion se re-mide, no se ajusta el test"
    )
    suma = (p["clase_viva_con_hallazgo"] + p["clase_viva_correcta"]
            + p["clase_historica_congelada"] + p["clase_no_resuelta"])
    assert suma == p["instancias_totales"], "ninguna instancia puede quedar sin clase"


def test_historicas_congeladas_publicadas_con_su_conteo(informe_real: dict):
    hist = informe_real["historical_excluded"]
    assert len(hist) == informe_real["coverage_basis"]["poblacion"]["clase_historica_congelada"]
    assert hist, "la poblacion congelada debe publicarse, no silenciarse (L-HF1)"
    for h in hist:
        assert h["regla"].startswith(("H1", "H2"))
        assert h["authorized_by"], "toda exclusion historica cita la frase que la ampara"
    amparo = informe_real["coverage_basis"]["regla_de_poblacion"]["historical_authorizing_phrase"]
    assert "menciones" in amparo and "literales" in amparo


def test_marca_de_estado_en_ascii(informe_real: dict):
    """La primera linea de la consola lleva el estado en ASCII, sin depender del resto.

    Es el contrato que fija `_estado_a_imprimir`: la salida de este script va a logs y a
    consolas que no son UTF-8 (lección «evidencia de consola no es UTF-8» del indice).
    """
    r = subprocess.run([sys.executable, str(SCRIPT), "--quiet"] , capture_output=True, text=True)
    assert r.stdout == ""
    r2 = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    linea0 = r2.stdout.splitlines()[0]
    assert linea0.isascii(), f"la marca de estado no es ASCII: {linea0!r}"
    assert linea0.startswith("[HALLAZGOS]"), linea0


def test_coverage_basis_legible_sin_abrir_el_codigo(informe_real: dict):
    cb = informe_real["coverage_basis"]
    assert cb["documents_scanned"] and cb["fuentes"]["quick"]["total"] == 11
    assert cb["fuentes"]["hook"]["total"] == 7
    assert [f["familia"] for f in cb["families_not_covered"]] == [
        "prosa-de-conteo-sin-patron",
        "conteos-fuera-de-los-documentos-de-gobierno",
        "pins-de-conteo-en-tests",
        "fuentes-dinamicas-que-no-sean-etiqueta-impresa",
    ]
    for familia in cb["families_not_covered"]:
        assert familia["medicion"], f"{familia['familia']} se declara sin medicion"
        assert familia["comando"], f"{familia['familia']} no es re-ejecutable"
    assert cb["excluded"], "las exenciones de poblacion se publican (AC2)"
    assert cb["comando"] and cb["medido_el"], "toda cifra va con su comando y su fecha"
