"""C1 / D-A — el estado de cada familia no delega en la fila D1, que esta cerrada.

D1 quedo CERRADA por §13 de `BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md` en un alcance
que no cubre estas familias (lint de prosa, conteos fuera de los dos documentos de gobierno, pins en
`tests/`). Un verificador no puede cobrarle una deuda a una fila cerrada: cada estado declara su
limite con la autoridad vigente. Deuda D-A en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md` §5.

Se afirma por **contenido** y con la familia como clave, no por posicion: reordenar
`FAMILIES_NOT_COVERED` no toca este verde, y reintroducir un puntero vencido si lo corta.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "validate_governance_numbers.py"

# El patron del barrido de la orden: la forma ampliada, que caza las tres variantes y no dos.
PUNTERO_D1_RE = re.compile(r"D1 (decide|es)|es D1|trabajo D1")
AUTORIDAD = "BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md"
FAMILIAS = (
    "prosa-de-conteo-sin-patron",
    "conteos-fuera-de-los-documentos-de-gobierno",
    "pins-de-conteo-en-tests",
    "fuentes-dinamicas-que-no-sean-etiqueta-impresa",
)


@pytest.fixture(scope="module")
def estados(tmp_path_factory) -> dict:
    """Las cuatro cadenas `estado` del informe real, claveadas por familia."""
    destino = tmp_path_factory.mktemp("c1") / "informe.json"
    r = subprocess.run([sys.executable, str(SCRIPT), "--report", str(destino)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    familias = json.loads(destino.read_text(encoding="utf-8"))[
        "coverage_basis"]["families_not_covered"]
    assert [f["familia"] for f in familias] == list(FAMILIAS), "cambio de poblacion, no de estado"
    return {f["familia"]: f["estado"] for f in familias}


def test_ningun_estado_delega_en_la_fila_d1(estados):
    """El mutante de C1 cae aqui: «D1 decide» vuelve a ser un puntero vencido, no un dueno."""
    for familia, estado in estados.items():
        assert not PUNTERO_D1_RE.search(estado), f"{familia} delega su estado en D1: {estado}"


@pytest.mark.parametrize("familia,declaracion", [
    ("prosa-de-conteo-sin-patron",
     ("limite permanente de este verificador", "no hay lint de prosa",
      "no incluye el lint de prosa")),
    ("conteos-fuera-de-los-documentos-de-gobierno",
     ("fuera del alcance de este plan (maestro §3)", "cerro la fila D1",
      "no cubre los conteos fuera de los dos documentos de gobierno")),
    ("pins-de-conteo-en-tests",
     ("barrido por AC5/AC16 de esta fase", "cerro la fila D1",
      "no cubre los pins de conteo en tests/")),
])
def test_el_estado_declara_su_limite_y_su_autoridad(estados, familia, declaracion):
    estado = estados[familia]
    for fragmento in declaracion:
        assert fragmento in estado, f"{familia} no declara {fragmento!r}: {estado}"
    assert AUTORIDAD in estado and "§13" in estado, f"{familia} no cita la matriz que cerro D1"


def test_la_familia_que_no_es_deuda_d1_no_se_toco(estados):
    """C1 cura tres punteros, no reescribe las cuatro: la cuarta sigue en su limite permanente."""
    estado = estados["fuentes-dinamicas-que-no-sean-etiqueta-impresa"]
    assert estado.startswith("limite permanente de este verificador")
    assert AUTORIDAD not in estado, "una familia sin puntero D1 no debe ganar la cita de §13"
