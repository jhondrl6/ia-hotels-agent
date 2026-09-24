"""AC11, segunda causa — `VENCIDO` lo produce **el check de frescura propio de C** (contrato E2).

No lo produce un `--check` ajeno ni el `[6/7]` del hook: el script calcula el indice en memoria con el
generador de la casa y compara contra lo que hay en disco. Para provocar el estado se deja el
**artefacto en desfase con el corpus** (aqui, un JSON al que se le quita un ID), que es exactamente lo
que es un indice vencido: el arbol se movio despues de la ultima regeneracion.

Que el archivo exista no es que este fresco: si este test pasara con el JSON intacto, el check no
estaria mirando nada.
"""

from __future__ import annotations

import json

import pytest

PLAN = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"


@pytest.fixture
def indice_vencido(trl, indice_real, tmp_path):
    """Copia del indice real con una leccion menos: el disco queda por detras del corpus."""
    payload = json.loads(indice_real.read_text(encoding="utf-8"))
    robada = payload["lecciones"].pop(len(payload["lecciones"]) // 2)
    vencido = tmp_path / "lecciones_index.json"
    vencido.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return vencido, robada["id"]


def test_vencido_lo_detecta_el_check_propio(trl, indice_vencido):
    vencido, id_fuera = indice_vencido
    estado = trl.comprobar_frescura(vencido)
    assert estado["index_status"] == "VENCIDO"
    assert estado["index_status"] not in ("AUSENTE", "LECTOR-FALLIDO", "FRESCO")
    assert estado["ejecutado_por"] == "triage_lesson_relevance"
    assert id_fuera in estado["diff"]["solo_en_el_calculo"], (
        "el check dice VENCIDO pero no nombra que diff lo vencio: sin eso no informa (L-R.3)")


def test_vencido_dice_que_lo_vencio_y_quien_lo_corta_en_el_hook(trl, indice_vencido, capsys):
    vencido, id_fuera = indice_vencido
    rc = trl.main(["--plan", PLAN, "--index-json", str(vencido)])
    salida = capsys.readouterr().out
    assert rc == 4, f"VENCIDO debe salir con exit 4, salio {rc}"
    assert "[VENCIDO]" in salida
    assert "6/7" in salida and "pre-commit" in salida, (
        "AC11 pide que VENCIDO diga que check del hook lo detecta")
    assert id_fuera in str(trl.comprobar_frescura(vencido)["diff"]["solo_en_el_calculo"])


def test_vencido_no_devuelve_candidatos_ni_denominador_favorable(trl, indice_vencido):
    with pytest.raises(trl.SueloNoLeible) as exc:
        trl.leer_suelo(indice_vencido[0])
    informe = trl.informe_suelo_no_leible(PLAN, exc.value.estado, exc.value.payload)
    assert informe["candidatos"] is None
    assert "coverage_basis" not in informe, "no hay denominador que publicar sobre un suelo vencido"
    assert informe["status"] == "SUELO-VENCIDO"


def test_la_tercera_via_esta_prohibida(trl, indice_real):
    """Existir y leerse no es estar fresco: contra el indice vigente el check dice FRESCO, y eso es
    lo unico que habilita el consumo."""
    estado = trl.comprobar_frescura(indice_real)
    assert estado["index_status"] == "FRESCO"
    indice, estado2 = trl.leer_suelo(indice_real)
    assert estado2["index_status"] == "FRESCO"
    assert len(indice["lecciones"]) == trl.denominador(indice, [], [])["poblacion_leida_del_indice"][
        "ids_con_definicion"]
