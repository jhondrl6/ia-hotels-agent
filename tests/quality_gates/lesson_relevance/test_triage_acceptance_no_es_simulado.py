"""AC15 (contrato E4) — `acceptance` es `NO-EJERCITADO` con su motivo, y **no se simulo**.

El tramo semantico de AC15 pide candidatos que resultaron pertinentes sobre el total propuesto **con
un proveedor real**. Aqui contesta un falso determinista: publicar un numero sería fabricar el
disparador de la deuda D6 y abrir un lint semantico sobre una base que nunca juzgo nada. Lo que C si
cierra con el falso es la parte **no semantica** del denominador: poblacion, terminos con sus ceros y
familias no juzgadas (L-R.3, L-HF1).
"""

from __future__ import annotations

import json
import re

import pytest


def test_acceptacion_no_ejercitado_con_motivo_literal(trl, informe_real):
    a = trl.coverage_json(informe_real)["aceptacion"]
    assert a["estado"] == "NO-EJERCITADO"
    assert a["motivo"] and "falso" in a["motivo"].lower() and "D7" in a["motivo"]
    assert a["valor"] is None and a["muestra"] is None and a["metodo"] is None
    assert "D6" in a["deuda_afectada"] and "dormida" in a["deuda_afectada"]["D6"]


def test_no_se_simulo_ninguna_aceptabilidad(trl, informe_real):
    """Ningun numero de la corrida puede leerse como aceptabilidad: se busca y se niega."""
    a = trl.coverage_json(informe_real)["aceptacion"]
    assert not re.search(r"\b0?\.\d+\b", json.dumps(a)), (
        f"hay un numero en el bloque `aceptacion`: {a} — E4 lo prohibe")
    propuestos = len(informe_real["buckets"]["propuesto"])
    total = len(informe_real["candidatos"])
    ratio = round(propuestos / total, 2) if total else None
    texto = json.dumps(trl.coverage_json(informe_real), ensure_ascii=False)
    assert str(ratio) not in texto, (
        f"la ratio mecanica {ratio} aparece publicada: eso es aceptabilidad simulada con el falso")
    assert propuestos and total, "sin muestra no hay ratio que tentar, pero el test seria vacio"


def test_el_informe_declara_quien_contesto(trl, informe_real):
    emisor = informe_real["coste"]["emisor"]
    assert emisor["falso"] is True
    assert emisor["nombre"] == "falso-pertinencia"
    assert emisor["credencial_env"] is None, (
        "un emisor con credencial no es un falso: la corrida de evidencia debe ser offline")


def test_denominador_con_poblacion_terminos_ceros_y_familias(trl, informe_real):
    cb = trl.coverage_json(informe_real)["coverage_basis"]
    assert cb["poblacion_leida_del_indice"]["ids_con_definicion"], "poblacion vacia: no se midio"
    assert cb["denominador_juicio"]
    terminos = cb["terminos_capa_fria"]
    assert terminos["conteos"] and len(terminos["conteos"]) >= 5
    ceros = [t for t in terminos["conteos"] if t["coincidencias"] == 0]
    assert ceros, (
        "AC15 exige publicar los ceros (A5 midio `verificador mec` = 0 sobre un corpus que si contiene "
        "verificadores): ningun termino dio cero, revise la lista")
    assert {"verificador mec"} <= {t["termino"] for t in terminos["conteos"]}
    assert terminos["metodo"], "un conteo sin su metodo no es re-ejecutable"
    assert cb["familias_no_juzgadas"] is not None
    assert cb["ids_numericos"]["metodo"]
    assert cb["pool_no_sometido_a_juicio"]["nota"]


@pytest.mark.parametrize("clave", ["familias_no_juzgadas", "familias_excluidas_por_el_generador"])
def test_lo_que_no_se_juzga_queda_declarado(trl, informe_real, clave):
    cb = trl.coverage_json(informe_real)["coverage_basis"]
    assert clave in cb
    assert isinstance(cb[clave], list)


def test_la_cifra_no_esta_pineada_en_el_codigo(trl):
    """L-V2.3 / A6: el denominador se lee de la corrida; los literales de concepcion no estan en C."""
    fuente = (trl.__file__ if isinstance(trl.__file__, str) else str(trl.__file__)).strip()
    import io
    texto = io.open(fuente, encoding="utf-8").read()
    for pin in ("320", "332", "402", " == 50", '"ids_con_definicion": 3'):
        assert pin not in texto, f"el script pinea la cifra {pin!r} en lugar de leerla de la corrida"
