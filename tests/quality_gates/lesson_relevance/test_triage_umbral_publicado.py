"""AC12 — el umbral se publica **con valor, base y accion por debajo** (L-R.4).

Una regla sin verificador es publicable solo si lo declara: por eso `basis` tiene que nombrar el campo
gobernado y `action_below` tiene que decir que debajo del umbral **se revisa, no se descarta**.
"""

from __future__ import annotations

import pytest

CLAVES = ("campo", "value", "basis", "action_below")


def test_las_tres_partes_del_ac12_estan_en_el_artefacto(trl, informe_real):
    u = informe_real["umbral"]
    assert set(CLAVES) <= set(u), f"falta {set(CLAVES) - set(u)}: AC12 no es legible en el artefacto (R2.4)"
    assert u["campo"] == "confidence"
    assert isinstance(u["value"], float) and 0.0 < u["value"] < 1.0
    assert "confidence" in u["basis"], "`basis` debe nombrar el campo que gobierna"
    assert u["action_below"]


def test_la_accion_por_debajo_no_es_descartar(trl, informe_real):
    accion = informe_real["umbral"]["action_below"].lower()
    for prohibido in ("descartar", "borrar", "eliminar", "ignorar"):
        assert prohibido not in accion.replace("no se " + prohibido, ""), (
            f"`action_below` menciona {prohibido!r} sin negarlo: AC12 separa, no filtra")
    assert "revisar" in accion


def test_todos_los_candidatos_tienen_bucket_y_ninguno_se_pierde(trl, informe_real):
    juicios = informe_real["candidatos"]
    assert juicios
    assert all(j.get("bucket") in ("propuesto", "a-revisar-humano") for j in juicios)
    repartidos = informe_real["buckets"]["propuesto"] + informe_real["buckets"]["a_revisar_humano"]
    triados_no_anclados = [j["id"] for j in juicios if j.get("tipo_fila") != "anclada"]
    assert sorted(repartidos) == sorted(set(triados_no_anclados)), (
        "un candidato sin bucket es un descarte silencioso (AC10/AC12)")
    assert len(repartidos) == len(set(repartidos))


@pytest.mark.parametrize("clave", CLAVES)
def test_el_valor_publicado_es_el_del_codigo_no_el_del_test(trl, informe_real, clave):
    assert informe_real["umbral"][clave] == trl.UMBRAL[clave]


def test_el_coste_del_reporte_lleva_tope_publicado(trl, informe_real):
    c = informe_real["coste"]
    assert c["tope"] == trl.TECHO_LLAMADAS
    assert c["llamadas_al_proveedor"] >= 1
    assert c["emisor"]["falso"] is True, (
        "el informe debe decir que quien contesto era falso: sin eso se leeria como juicio real (E4)")
