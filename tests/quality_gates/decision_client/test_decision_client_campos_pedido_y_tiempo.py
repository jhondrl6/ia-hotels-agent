"""Mitad (a) del gap de contrato del piloto JEV: los tres campos que la costura **si** puede observar.

El dossier (`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-09-30/
01-gap-de-contrato.md`) deja medido que de los once campos que exige `01-plan-maestro.md` §Interfaz, la
puerta publicaba siete. Esta bateria cubre los tres cuya dueña real es la propia costura -
`provider_requested`, `model_requested` y `elapsed_ms` - y **certifica por asercion que los otros tres
no se publican desde aqui**: `attempts`, `error_kind` y `usage_normalized` le corresponden a la mitad
(b), que vive en el runner del piloto, porque la costura no ve los reintentos que ocurren dentro del
cliente que arma el proveedor.

Que NO prueba esta seleccion: que exista un segundo proveedor con eleccion (deuda D7). Con uno solo,
pedido y efectivo coinciden por construccion, y el valor se publica igual - lo que se exige aqui es que
`provider_requested` salga del **entorno**, no de un literal, y que `model_requested` salga del **pin
declarado**, no de lo que el proveedor reporte.
"""

NOMBRE_FALSO = "falso-forma"
PIN_DECLARADO = "falso-forma-0.1"

FUENTE_LENTA = '''"""Proveedor falso de un directorio temporal: duerme 20 ms para que el tiempo sea medible."""

from __future__ import annotations

import time

PROVEEDOR = {"nombre": "falso-lento-pedido", "falso": True, "credencial_env": None,
             "modelo": "pin-declardo-jev-1.13.0"}


def evaluar(state, preguntas):
    time.sleep(0.02)
    respuestas = []
    for p in preguntas:
        if p.tipo == "choice":
            e = p.opciones[0]
            n = len(p.opciones)
            resto = round((1.0 - 0.7) / (n - 1), 6) if n > 1 else 0.0
            respuestas.append({"pregunta_id": p.id, "tipo": "choice", "eleccion": e,
                               "probabilidades": {o: (0.7 if o == e else resto) for o in p.opciones},
                               "confidence": 0.91})
        elif p.tipo == "score":
            nivel = 1 if len(p.leyenda) > 1 else 0
            respuestas.append({"pregunta_id": p.id, "tipo": "score", "nivel": nivel,
                               "leyenda": p.leyenda[nivel], "confidence": 0.83})
        else:
            respuestas.append({"pregunta_id": p.id, "tipo": "noul", "probabilidad_si": 0.68})
    return {"modelo": "modelo-que-reporta-el-proveedor", "respuestas": respuestas,
            "usage": {"input_tokens": 10, "output_tokens": 4}, "request_id": "lento-req-1"}
'''


def _payload_valido(dc, preguntas, modelo):
    return {"modelo": modelo, "respuestas": [
        {"pregunta_id": preguntas[0].id, "tipo": "choice", "eleccion": preguntas[0].opciones[0],
         "probabilidades": {o: (0.7 if i == 0 else round(0.3 / (len(preguntas[0].opciones) - 1), 6))
                            for i, o in enumerate(preguntas[0].opciones)},
         "confidence": 0.9},
        {"pregunta_id": preguntas[1].id, "tipo": "score", "nivel": 1,
         "leyenda": preguntas[1].leyenda[1], "confidence": 0.8},
        {"pregunta_id": preguntas[2].id, "tipo": "noul", "probabilidad_si": 0.5},
    ], "usage": {"input_tokens": 11, "output_tokens": 5}, "request_id": "inyectado-1"}


def test_los_tres_campos_nuevos_viajan_en_el_dict_publicado(dc, entorno_falso, preguntas):
    """El contrato del piloto se lee del `to_dict()`, no de los slots: si un campo se llena pero no se
    publica, el runner del piloto no lo ve y el gap sigue abierto con la suite verde."""
    r = dc.evaluar("estado", preguntas, entorno_falso,
                   _payload=_payload_valido(dc, preguntas, PIN_DECLARADO))
    d = r.to_dict()
    for clave in ("provider_requested", "model_requested", "elapsed_ms"):
        assert clave in d, f"falta {clave} en lo que publica la costura: {sorted(d)}"


def test_provider_requested_sale_del_entorno_que_nombro_el_llamador(dc, entorno_falso, preguntas):
    r = dc.evaluar("estado", preguntas, entorno_falso,
                   _payload=_payload_valido(dc, preguntas, PIN_DECLARADO))
    assert r.provider_requested == entorno_falso[dc.ENV_PROVIDER] == NOMBRE_FALSO, (
        f"pedido {r.provider_requested!r} no es el nombre que dicto el entorno "
        f"{entorno_falso[dc.ENV_PROVIDER]!r}: se esta leyendo de otro lado")


def test_model_requested_es_el_pin_declarado_no_lo_que_reporta_el_proveedor(dc, entorno_falso,
                                                                            preguntas):
    """El diente de la mitad (a). El payload reporta un modelo **distinto** del pin que el modulo
    declara; si alguien cablea `model_requested` desde el payload, las dos mitades del par salen iguales
    y el piloto pierde el unico dato que le sirve para separar pedido de efectivo."""
    reportado = "modelo-que-el-proveedor-dice-ser"
    r = dc.evaluar("estado", preguntas, entorno_falso,
                   _payload=_payload_valido(dc, preguntas, reportado))
    assert r.modelo == reportado, "el efectivo dejo de ser lo que reporta el proveedor"
    assert r.model_requested == PIN_DECLARADO, (
        f"pedido {r.model_requested!r} != pin declarado {PIN_DECLARADO!r}: se copio del payload")
    assert r.model_requested != r.modelo, "pedido y efectivo salieron del mismo lado"


def test_elapsed_ms_es_none_cuando_no_hubo_llamada(dc, entorno_falso, preguntas):
    """Un temporizador alrededor de una invocacion que no ocurrio publica una medicion fabricada. Con
    payload inyectado (el camino del contract test) no hay llamada que cronometrar y el valor es None,
    no 0.0."""
    r = dc.evaluar("estado", preguntas, entorno_falso,
                   _payload=_payload_valido(dc, preguntas, PIN_DECLARADO))
    assert r.elapsed_ms is None, f"elapsed_ms {r.elapsed_ms!r} afirma un tiempo sin llamada"


def test_elapsed_ms_cronometra_la_llamada_real(dc, tmp_path, preguntas):
    """Y su otra mitad: cuando la llamada existe, el numero tiene que ser el de esa llamada. El proveedor
    del directorio temporal duerme 20 ms, asi que un `elapsed_ms` duro (0, o un literal) no pasa."""
    ruta = tmp_path / "falso_lento.py"
    ruta.write_text(FUENTE_LENTA, encoding="utf-8")
    entorno = {dc.ENV_PROVIDER: "falso-lento-pedido", dc.ENV_PROVIDERS_DIR: str(tmp_path)}
    r = dc.evaluar("estado", preguntas, entorno)
    assert r.provider_status == "RESUELTO", r.to_dict()
    assert isinstance(r.elapsed_ms, (int, float)) and r.elapsed_ms >= 10.0, (
        f"elapsed_ms {r.elapsed_ms!r} no refleja los 20 ms que durmio el proveedor")
    assert r.provider_requested == "falso-lento-pedido"
    assert r.model_requested == "pin-declardo-jev-1.13.0"


def test_los_siete_campos_viejos_no_cambiaron_de_nombre_ni_de_valor(dc, entorno_falso, preguntas):
    """La mitad (a) es aditiva: lo que el hermano ya consume (`proveedor`, `modelo`, `usage`,
    `request_id`, `credencial`, `provider_status`, `respuestas`) sigue estando y siendo lo mismo."""
    payload = _payload_valido(dc, preguntas, PIN_DECLARADO)
    r = dc.evaluar("estado", preguntas, entorno_falso, _payload=payload)
    d = r.to_dict()
    assert d["provider_status"] == "RESUELTO"
    assert d["proveedor"] == NOMBRE_FALSO
    assert d["modelo"] == payload["modelo"]
    assert d["usage"] == payload["usage"]
    assert d["request_id"] == payload["request_id"]
    assert len(d["respuestas"]) == len(preguntas)


def test_la_costura_no_se_hace_duenade_attempts_error_kind_ni_usage_normalized(dc):
    """Clausula del dossier, vuelta asercion: publicar `attempts = 1` desde la costura es verdadero sobre
    la costura y falso sobre la llamada facturable, y choca con que el SDK no pueda reintentar por debajo
    de la contabilidad del runner. Si alguien los anade aqui, esta prueba cae y la discusion vuelve a
    abrirse con dueno."""
    slots = set(dc.ResultadoEvaluacion.__slots__)
    filtrados = {s for s in slots if s in ("attempts", "error_kind", "usage_normalized")}
    assert not filtrados, (f"la costura publicaria {sorted(filtrados)}: es la mitad (b) del gap y su "
                           "productor es el runner del piloto, que es quien invoca con "
                           "RetryPolicy(max_retries=0)")
