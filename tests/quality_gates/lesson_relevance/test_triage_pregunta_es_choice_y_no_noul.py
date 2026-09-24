"""AC12 (parte E1) — la pregunta es `choice` de dos opciones y el umbral gobierna `confidence`.

Lo que se prueba aqui no es que el numero este publicado: es que **el campo que corta el umbral es
`confidence` y no la probabilidad de la opcion afirmativa**. `decision_client.RespuestaNoul` fija
`confidence = None` con su motivo (la primitiva no la expone y la puerta la rechaza ahi), asi que una
pregunta `noul` no podria gobernar este umbral ni por error.

El proveedor falso de esta seleccion deliberadamente **desacopla** los dos ejes (`por_si` por
`len(id) % 4`, `confidence` por `len(id) % 3`), de modo que existe en el arbol real un candidato con
`por_si` alto y `confidence` baja: si el codigo gobernara por `por_si`, ese candidato saldria
`propuesto`. Sale `a-revisar-humano`.
"""

from __future__ import annotations

import pytest


def test_todas_las_preguntas_son_choice_de_dos_opciones(trl, puerta, informe_real):
    fuentes = informe_real["candidatos"]
    assert fuentes, "sin candidatos no hay forma de pregunta que probar"
    preguntas, state = trl.construir_preguntas(puerta, fuentes)
    assert len(preguntas) == len(fuentes)
    for p in preguntas:
        assert p.tipo == "choice", f"{p.id}: contrato E1 exige choice, no {p.tipo}"
        assert p.validar() == []
        assert len(p.opciones) == 2, f"E1 fija dos opciones, llegaron {p.opciones}"
        assert tuple(p.opciones) == trl.OPCIONES_PERTINENCIA
    assert "noul" not in {p.tipo for p in preguntas}


def test_la_primitiva_noul_no_puede_gobernar_el_umbral(puerta):
    """La razon estructural de E1, leida de la puerta y no de su documentacion."""
    assert puerta.RespuestaNoul.confidence is None
    noul = puerta.RespuestaNoul("x", 0.9)
    dic = noul.to_dict()
    assert dic["confidence"] is None and "confidence_motivo" in dic
    elec = puerta.RespuestaEleccion("y", "pertinente", {"pertinente": 0.9, "no-pertinente": 0.1}, 0.42)
    assert elec.to_dict()["confidence"] == 0.42, "en `choice` confidence es un campo propio"


def test_probabilidad_si_no_es_el_campo_gobernado(trl, informe_real):
    assert trl.UMBRAL["campo"] == "confidence"
    assert "probabilidad_si" in trl.UMBRAL["basis"] or "por_si" in trl.UMBRAL["basis"]
    umbral = trl.UMBRAL["value"]
    invertidos = [j for j in informe_real["candidatos"]
                  if j.get("por_si") is not None and j["por_si"] >= umbral
                  and j.get("confidence") is not None and j["confidence"] < umbral]
    assert invertidos, (
        "la seleccion no produce ningun caso con por_si sobre el umbral y confidence debajo: no se "
        "puede distinguir que campo gobierna (L-HF1)")
    for j in invertidos:
        assert j["bucket"] == "a-revisar-humano", (
            f"{j['id']}: por_si={j['por_si']} >= {umbral} y confio={j['confidence']} < {umbral} salio "
            f"{j['bucket']}: el umbral goberno la probabilidad, no la confianza")


def test_misma_probabilidad_distinta_confidencia_cambia_el_bucket(trl, informe_real):
    """Dos candidatos con el mismo `por_si` y distinta `confidence` caen en buckets distintos."""
    por_si = [j["por_si"] for j in informe_real["candidatos"] if j.get("por_si") is not None]
    alto = [j for j in informe_real["candidatos"] if j.get("por_si") == max(por_si)]
    buckets = {j["bucket"] for j in alto}
    assert len(buckets) == 2, (
        f"con la misma probabilidad afirmativa todos cayeron en {buckets}: el bucket no depende de "
        "`confidence`, que es lo que afirma AC12")


def test_el_umbral_no_acepta_una_confidence_ausente(trl, informe_real):
    """`confidence = None` no se lee como 0.0 ni como «pasa»: se revisa (L-PF10)."""
    for j in informe_real["candidatos"]:
        if j.get("confidence") is None:
            assert j["bucket"] == "a-revisar-humano"


@pytest.mark.parametrize("clave", ["campo", "value", "basis", "action_below"])
def test_forma_pregunta_publicada(trl, informe_real, clave):
    assert clave in informe_real["umbral"]
    assert informe_real["forma_pregunta"]["campo_gobernado"] == "confidence"
    assert informe_real["forma_pregunta"]["opciones"] == list(trl.OPCIONES_PERTINENCIA)
