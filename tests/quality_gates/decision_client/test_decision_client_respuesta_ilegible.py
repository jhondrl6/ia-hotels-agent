"""AC7 / estado 2 de 3 - `ILEGIBLE`: el proveedor contesto mal y eso **no** es un favorable.

Cubre un solo estado: aqui el proveedor SI esta configurado y SI contesta; lo que falla es la forma.
Los casos `NO-CONFIGURADO` viven en `test_decision_client_provider_no_configurado.py` y el
`RESUELTO` en `test_decision_client_contract_forma.py`, y ningun caso de este archivo cubre dos
estados (R2.9: un test que cubre dos no prueba ninguno).
"""

import pytest


def test_choice_sin_confidence_es_ilegible_no_favorable(dc, preguntas, proveedores_falsos):
    """`falso-ilegible` manda una choice sin confidence: sin ella no hay «actue» ni «no estoy seguro».

    El fallo tiene que ser **ruidoso**: una decision sin confidence leida como decision segura es el
    colapso que L-PF6 y L-PF10 producen en el pipeline.
    """
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "falso-ilegible",
                                        "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)})
    assert any("confidence" in m for m in exc.value.motivos), exc.value.motivos
    guardas = {dc._nombre_de_la_verificacion(m) for m in exc.value.motivos}
    assert guardas <= {"campos-conocidos", "cobertura-de-preguntas", "forma-choice"}, exc.value.motivos
    assert "forma-choice" in guardas


def test_pregunta_sin_respuesta_es_ilegible(dc, preguntas, proveedores_falsos):
    """Ningun drop silencioso: una pregunta sin respuesta es un fallo, no un «no hay hallazgo»."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "falso-ilegible",
                                        "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)})
    motivos = " | ".join(exc.value.motivos)
    assert "cobertura-de-preguntas" in motivos
    assert preguntas[-1].id in motivos


def test_payload_vacio_no_es_decision_favorable(dc, preguntas, entorno_falso):
    """`respuestas: []` es ILEGIBLE con su causa (L-PF10: vacio != ausente != resuelto)."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, entorno_falso, _payload={"modelo": "x", "respuestas": []})
    assert exc.value.motivos == ["respuesta-vacia:list"]


def test_payload_no_dict_no_se_traga(dc, preguntas, entorno_falso):
    for basura, marca in ((None, "NoneType"), ([], "list"), ("texto", "str")):
        with pytest.raises(dc.RespuestaIlegible) as exc:
            dc.evaluar("estado", preguntas, entorno_falso, _payload=basura)
        assert marca in exc.value.motivos[0], (basura, exc.value.motivos)


def test_campo_nuevo_de_una_primitiva_es_ilegible(dc, preguntas, entorno_falso):
    """La primitiva «redefinio sus criterios» dos veces en nueve dias: un campo extra rompe aqui."""
    payload = {"modelo": "falso-forma-0.1",
               "respuestas": [{"pregunta_id": "c1", "tipo": "choice", "eleccion": "pertinente",
                               "probabilidades": {"pertinente": 1.0, "no-pertinente": 0.0,
                                                 "insuficiente": 0.0},
                               "confidence": 0.9,
                               "confianza_nueva": 0.9}],
               "usage": None, "request_id": None}
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, entorno_falso, _payload=payload)
    assert any("fuera de contrato" in m and "confianza_nueva" in m for m in exc.value.motivos)


def test_probabilidades_que_no_sumen_uno_es_ilegible(dc, preguntas, entorno_falso):
    payload = {"modelo": "falso-forma-0.1",
               "respuestas": [{"pregunta_id": "c1", "tipo": "choice", "eleccion": "pertinente",
                               "probabilidades": {"pertinente": 0.4, "no-pertinente": 0.2,
                                                 "insuficiente": 0.1},
                               "confidence": 0.9},
                              {"pregunta_id": "s1", "tipo": "score", "nivel": 1,
                               "leyenda": "medio", "confidence": 0.9},
                              {"pregunta_id": "n1", "tipo": "noul", "probabilidad_si": 0.5}],
               "usage": None, "request_id": None}
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, entorno_falso, _payload=payload)
    assert any("suman" in m for m in exc.value.motivos), exc.value.motivos


def test_el_nivel_y_su_leyenda_tienen_que_cuadrar(dc, preguntas, entorno_falso):
    """Un `score` cuyo nivel no corresponde a la leyenda declarada es una forma rota, no un dato."""
    payload = {"modelo": "falso-forma-0.1",
               "respuestas": [{"pregunta_id": "c1", "tipo": "choice", "eleccion": "pertinente",
                               "probabilidades": {"pertinente": 1.0, "no-pertinente": 0.0,
                                                 "insuficiente": 0.0},
                               "confidence": 0.9},
                              {"pregunta_id": "s1", "tipo": "score", "nivel": 2,
                               "leyenda": "bajo", "confidence": 0.9},
                              {"pregunta_id": "n1", "tipo": "noul", "probabilidad_si": 0.5}],
               "usage": None, "request_id": None}
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, entorno_falso, _payload=payload)
    assert any("no cuadran" in m for m in exc.value.motivos), exc.value.motivos


def test_noul_con_confidence_inventada_es_ilegible(dc, preguntas, entorno_falso):
    """La primitiva noul **no** expone confidence: rellenarla seria fabricar el eje de AC12."""
    payload = {"modelo": "falso-forma-0.1",
               "respuestas": [{"pregunta_id": "c1", "tipo": "choice", "eleccion": "pertinente",
                               "probabilidades": {"pertinente": 1.0, "no-pertinente": 0.0,
                                                 "insuficiente": 0.0},
                               "confidence": 0.9},
                              {"pregunta_id": "s1", "tipo": "score", "nivel": 1,
                               "leyenda": "medio", "confidence": 0.9},
                              {"pregunta_id": "n1", "tipo": "noul", "probabilidad_si": 0.5,
                               "confidence": 0.5}],
               "usage": None, "request_id": None}
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, entorno_falso, _payload=payload)
    assert any("noul no debe reportar confidence" in m for m in exc.value.motivos)


def test_la_costura_no_convierte_un_ilegible_en_heuristica(dc, preguntas, proveedores_falsos):
    """Ni una clave de decision por defecto: la excepcion no trae respuestas disfrazadas."""
    with pytest.raises(dc.RespuestaIlegible) as exc:
        dc.evaluar("estado", preguntas, {"IAH_DECISION_PROVIDER": "falso-ilegible",
                                        "IAH_DECISION_PROVIDERS_DIR": str(proveedores_falsos)})
    assert not hasattr(exc.value, "respuestas")
    assert not hasattr(exc.value, "elecciones")
    assert exc.value.proveedor == "falso-ilegible"
