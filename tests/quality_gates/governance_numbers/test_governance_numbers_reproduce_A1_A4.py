"""AC1 + AC2 — el verificador reproduce A1-A4 del maestro §1 sobre un contraejemplo congelado.

Desde el bloque B de la orden `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` (D1), el árbol real de
`.agents/` **ya no** contiene esas cifras vencidas: las aserciones se retiraron de su fuente para que
no vuelvan a desfasar (la opción que el propio plan de CONTEXTO recomienda). Por eso la detección de
A1-A4 se prueba ahora contra `fixtures/`, una copia congelada de los documentos **antes** de D1, que
reproduce exactamente las cuatro aserciones, las dos occurrences de A1, las 24 instancias y las 8
menciones históricas congeladas. Con el mismo `run_all_validations.py` y hook reales, los `observed`
son idénticos a los del maestro §1. Y `test_arbol_real_honesto_tras_d1` fija el otro lado: el árbol
vigente sale `SIN-HALLAZGOS`.

El verde no puede venir de recortar la población a mano: por eso se afirman también
`historical_excluded[]` (A8) y la suma interna de las tres clases.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"
FIXTURES = ROOT / "tests" / "quality_gates" / "governance_numbers" / "fixtures"
DOC_EJECUTOR = FIXTURES / "phased_project_executor.md"
DOC_TEMPLATE = FIXTURES / "lecciones-capitalizadas-template.md"
DOC_ARGS = ["--governance-doc", str(DOC_EJECUTOR), "--governance-doc", str(DOC_TEMPLATE)]


def _informe(destino: Path) -> dict:
    r = subprocess.run([sys.executable, str(SCRIPT), "--report", str(destino), *DOC_ARGS],
                       capture_output=True, text=True)
    assert r.returncode == 1, f"se esperaban hallazgos, salio {r.returncode}: {r.stdout}{r.stderr}"
    return json.loads(destino.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def informe_real(tmp_path_factory) -> dict:
    destino = tmp_path_factory.mktemp("gn") / "informe.json"
    return _informe(destino)


def test_arbol_real_honesto_tras_d1():
    """D1 cerró las cuatro aserciones vencidas: el árbol de `.agents/` vigente ya no da hallazgos."""
    r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.splitlines()[0].startswith("[SIN-HALLAZGOS]"), r.stdout


def test_findings_son_exactamente_A1_A4(informe_real: dict):
    assert [f["assertion_id"] for f in informe_real["findings"]] == ["A1", "A2", "A3", "A4"]


def test_cada_hallazgo_trae_su_clave_legible(informe_real: dict):
    for f in informe_real["findings"]:
        for clave in ("assertion_id", "document", "claimed", "observed", "occurrences"):
            assert clave in f, f"{f.get('assertion_id')} no publica {clave} (R2.4)"
        assert f["occurrences"], "un hallazgo sin occurrences no es auditable"


def test_claimed_y_observed_cuadran_con_el_maestro(informe_real: dict):
    """Re-anclado el 2026-09-26 por D2: el quick pasó de 11 a 12 checks y el completo de 15 a 16.

    `observed` se lee del `scripts/run_all_validations.py` vigente, así que estos cuatro valores son
    consecuencia de la renumeración, no del fixture (de ahí el dueño D1/D2 declarado en S8/L-VCF-5: al
    renumerar el quick, el test se re-ancla con su nota datada). `claimed` sigue siendo lo que afirma el
    documento del maestro, y por eso los cuatro hallazgos A1–A4 no desaparecen: el desvío se mantiene,
    solo que contra otro denominador. Nota de la promotora: A1 y A4 reclaman `[9/12]` y `[10/12]` porque
    los ordinales 9 y 10 no se movieron, y A3 pasa a `[16/16]` porque los cuatro checks exclusivos del
    modo completo se desplazaron a 13..16.
    """
    por_id = {f["assertion_id"]: f for f in informe_real["findings"]}
    assert por_id["A1"]["claimed"] == "check 8" and por_id["A1"]["observed"] == "[9/12]"
    assert por_id["A2"]["claimed"] == "[9/9]" and por_id["A2"]["observed"] == "[10/12]"
    assert por_id["A3"]["claimed"] == "[12/12]" and por_id["A3"]["observed"] == "[16/16]"
    # A4 es PARCIAL: su [7/7] del hook si cuadra, y solo el [10/10] del quick no.
    assert por_id["A4"]["claimed"] == "[10/10]" and por_id["A4"]["observed"] == "[10/12]"


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
    r = subprocess.run([sys.executable, str(SCRIPT), "--quiet", *DOC_ARGS],
                       capture_output=True, text=True)
    assert r.stdout == ""
    r2 = subprocess.run([sys.executable, str(SCRIPT), *DOC_ARGS], capture_output=True, text=True)
    linea0 = r2.stdout.splitlines()[0]
    assert linea0.isascii(), f"la marca de estado no es ASCII: {linea0!r}"
    assert linea0.startswith("[HALLAZGOS]"), linea0


def test_coverage_basis_legible_sin_abrir_el_codigo(informe_real: dict):
    cb = informe_real["coverage_basis"]
    assert cb["documents_scanned"] and cb["fuentes"]["quick"]["total"] == 12
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
