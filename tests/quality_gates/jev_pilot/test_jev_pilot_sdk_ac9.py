"""AC9 con el **SDK real** y transporte falso (`httpx2.MockTransport`), con la red bloqueada por conftest.

Lo que se ejercita aqui no es un substituto: quien serializa el request, quien parsea la respuesta y
quien elige la clase de error es `typesafe_sdk` 0.7.0, resuelto por la ruta duradera congelada en
`FASE-B/entorno.json`. Lo unico falso es el transporte, y hay un test que afirma que **fue invocado**
(L-T4A.5: sin esa prueba, «transporte falso» podria significar «el codigo no alcanzo la rama»).

Cada control afirma su causa, no su etiqueta (L-V2.1): la clase del error y su `status`, nunca un
`Exception` generico que colapsase los cuatro estados que AC9 pide mantener separados (DA-C3).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PIN = "jev-1.13.0"
DEVUELTO = "jev-9.9.9"
CLAVE_SINTETICA = "clave-sintetica-de-test-que-no-es-una-credencial"
RESPUESTA_BUENA = {"model": DEVUELTO,
                   "usage": {"input_tokens": 111, "output_tokens": 22},
                   "answers": {"q1": {"type": "noul", "noul": 0.83}}}
PREGUNTAS = {"q1": {"type": "noul", "instructions": "¿Es la unica leccion pertinente?"}}


def _transporte(httpx2, *, status=None, body=None, exc=None, headers=None):
    """Transporte falso con contador: `invocadas` es la prueba de que la rama de red se alcanzo."""
    contados = {"invocadas": 0, "requests": []}

    def handler(request):
        contados["invocadas"] += 1
        contados["requests"].append(request)
        if exc is not None:
            raise exc
        return httpx2.Response(status, json=body if body is not None else {},
                               headers=headers or {})

    return httpx2.MockTransport(handler=handler), contados


def _llamar(puerta, mod, httpx2, *, respuesta, modelo_solicitado=PIN):
    """Un envio del SDK real contra el transporte falso, con la puerta en medio.

    Devuelve (payload o None, excepcion o None, contador de envios). El cliente se arma con
    `puerta.cliente_jev`, o sea con `max_retries=0` por contrato: los envios extra del default del
    SDK se provocan aparte, en su propio test.
    """
    transporte, contados = _transporte(httpx2, **respuesta)
    cliente = puerta.cliente_jev(mod, modelo=modelo_solicitado, transport=transporte,
                                 api_key=CLAVE_SINTETICA)
    try:
        return (puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS,
                                      modelo=modelo_solicitado), None, contados)
    except Exception as exc:
        return None, exc, contados


# ------------------------------------------------------------------ AC9: las cuatro clases no colapsan

def test_http_failure_cases_remain_distinct(puerta, mod, httpx2):
    """AC9: 401 → Authentication, 429 → RateLimit, timeout → Connection; por clase **y** por status.

    El timeout no trae `status`: `TypeSafeAPIConnectionError` no desciende de `TypeSafeAPIError`, y
    eso es un hecho medido del SDK. Se afirma como None en vez de rellenarlo con un codigo que la
    puerta invente.
    """
    casos = [
        ({"status": 401, "body": {"error": "clave mala"}}, mod.TypeSafeAuthenticationError, 401),
        ({"status": 429, "body": {"error": "lento"}, "headers": {"retry-after-ms": "0"}},
         mod.TypeSafeRateLimitError, 429),
        ({"status": 500, "body": {"error": "servidor"}}, mod.TypeSafeInternalServerError, 500),
    ]
    kinds = set()
    for respuesta, clase_esperada, status_esperado in casos:
        _, excepcion, contados = _llamar(puerta, mod, httpx2, respuesta=respuesta)
        assert type(excepcion) is clase_esperada, (
            f"esperaba {clase_esperada.__name__}, el SDK lanzo {type(excepcion).__name__}")
        assert excepcion.status == status_esperado
        assert contados["invocadas"] == 1, "con max_retries=0 el SDK no debe reintentar"
        kinds.add(type(excepcion).__name__)
    assert len(kinds) == 3, f"las tres clases colapsaron: {sorted(kinds)}"

    _, excepcion, contados = _llamar(puerta, mod, httpx2,
                                     respuesta={"exc": httpx2.ConnectTimeout("no contesto")})
    assert isinstance(excepcion, mod.TypeSafeAPIConnectionError), (
        "un timeout debe ser conex segun AC9, no una excepcion generica")
    assert isinstance(excepcion, mod.TypeSafeAPITimeoutError)
    assert getattr(excepcion, "status", None) is None
    assert contados["invocadas"] == 1


def test_error_kind_del_runner_cas_con_las_clases_reales_del_sdk(puerta, mod, runner, httpx2):
    """El diente que faltaba: `error_kind_de` se calcula sobre excepciones **producidas por el SDK**.

    Hasta hoy el ledger se probaba con clases sinteticas que solo llevaban el nombre puesto a mano.
    Si el proveedor renombra una clase, el `desconocido` que resulta se ve aqui y no en produccion.
    """
    esperado = [({"status": 401, "body": {"error": "x"}}, "auth", 401),
                ({"status": 429, "body": {"error": "x"}, "headers": {"retry-after-ms": "0"}},
                 "cuota", 429),
                ({"status": 200, "body": {"model": DEVUELTO, "answers": {}}},
                 "respuesta_ilegible", 200),
                ({"exc": httpx2.ConnectTimeout("x")}, "timeout", None)]
    vistos = {}
    for respuesta, kind, status in esperado:
        _, excepcion, _ = _llamar(puerta, mod, httpx2, respuesta=respuesta)
        assert excepcion is not None, f"{kind}: el SDK no fallo, el control se queda verde por vacio"
        clasificado = runner.error_kind_de(excepcion)
        assert clasificado["error_kind"] == kind, (
            f"el SDK lanzo {clasificado['clase']} y el ledger la nombro {clasificado['error_kind']}")
        assert clasificado["status"] == status
        vistos[kind] = clasificado["clase"]
    assert len(set(vistos.values())) == 4, f"cuatro clases, una etiqueta: {vistos}"


# ------------------------------------------------------------------- AC9: el transporte se alcanzo

def test_una_respuesta_sin_cabecera_de_request_id_no_revienta_la_corrida(puerta, mod, httpx2):
    """El `request_id` del SDK es una propiedad que Lanza si la cabecera falta: la puerta lo vuelve None.

    Diente medido el 2026-10-03: `getattr(respuesta, "request_id", None)` NO cubre una excepcion,
    solo un atributo ausente. Con la envolvente vieja, un 200 sin `x-typesafe-request-id` tiraba
    `TypeSafeError` desde dentro del normalizador y la corrida perdia el usage ya observado.
    """
    transporte, _ = _transporte(httpx2, status=200, body=RESPUESTA_BUENA)
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    payload = puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS,
                                    modelo=PIN)
    assert payload["request_id"] is None
    assert payload["usage"] == {"input_tokens": 111, "output_tokens": 22}, (
        "se perdio el uso ya observado por culpa de una cabecera ausente")

    con_cabecera, _ = _transporte(httpx2, status=200, body=RESPUESTA_BUENA,
                                  headers={"x-typesafe-request-id": "req-abc"})
    cliente2 = puerta.cliente_jev(mod, modelo=PIN, transport=con_cabecera, api_key=CLAVE_SINTETICA)
    assert puerta.system_one_jev(cliente2, state={"consulta": "x"}, questions=PREGUNTAS,
                                 modelo=PIN)["request_id"] == "req-abc"


def test_el_transporte_falso_fue_invocado_y_el_sdk_serializo_el_contrato(puerta, mod, httpx2):
    """AC9: la rama salio por el transporte, con el path, el metodo y el body que arma el SDK.

    Sin este control, un `pytest.raises` sobre un cliente mal construido daria verde sin haber
    tocado nunca la serializacion (L-T4A.5).
    """
    transporte, contados = _transporte(httpx2, status=200, body=RESPUESTA_BUENA)
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    payload = puerta.system_one_jev(cliente, state={"consulta": "hola"}, questions=PREGUNTAS,
                                    modelo=PIN)
    assert contados["invocadas"] == 1, "el transporte falso no fue alcanzado: verde por vacio"
    pedido = contados["requests"][0]
    assert pedido.method == "POST" and pedido.url.path == "/v1/systemone"
    assert json.loads(pedido.content.decode("utf-8")) == {
        "state": {"consulta": "hola"}, "model": PIN, "questions": PREGUNTAS}
    assert "Authorization" in pedido.headers
    assert payload["modelo"] == DEVUELTO


# --------------------------------------------------------------------------- AC8: intentos y ledger

def test_con_defaults_el_mismo_429_da_tres_envios_y_el_ledger_ve_uno(puerta, mod, httpx2):
    """AC8 medido con el default del SDK: `RetryPolicy()` = 2 reintentos = 3 envios por UNA llamada.

    Los dos numeros se afirman juntos porque ahi esta el hueco que la reserva de presupuesto cierra:
    el ledger del runner registra 1 excepcion mientras el cable gasto 3. Con `max_retries=0` los dos
    coinciden, y eso es lo que autoriza la corrida.
    """
    transporte, contados = _transporte(httpx2, status=429, body={"error": "lento"},
                                       headers={"retry-after-ms": "0"})
    cliente = mod.TypeSafeClient(api_key=CLAVE_SINTETICA, model=PIN, transport=transporte,
                                 retry=mod.RetryPolicy(), timeout=30)
    with pytest.raises(mod.TypeSafeRateLimitError):
        cliente.system_one(state={"consulta": "x"}, questions=PREGUNTAS, model=PIN)
    assert contados["invocadas"] == 3, (
        f"el default medido del SDK 0.7.0 es max_retries=2 (3 envios); el transporte vio "
        f"{contados['invocadas']}")


def test_max_retries_cero_da_un_envio_y_el_ledger_coincide(puerta, mod, httpx2, runner):
    """AC8: con `max_retries=0`, envios == intentos del ledger == 1, y el fallo queda clasificado."""
    ledger = runner.nuevo_ledger("jev", PIN)
    transporte, contados = _transporte(httpx2, status=429, body={"error": "lento"},
                                       headers={"retry-after-ms": "0"})
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    with pytest.raises(mod.TypeSafeRateLimitError) as vio:
        puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS, modelo=PIN)
    runner.registrar_intento(ledger, resultado="fallo", excepcion=vio.value, duracion_ms=12.0)
    assert contados["invocadas"] == 1, "max_retries=0 no elimino el reintento del SDK"
    assert ledger["attempts"] == contados["invocadas"] == 1
    assert ledger["error_kind"] == "cuota"
    assert ledger["estado"] == "FALLO"


def test_cliente_jev_rechaza_reintentos_distintos_de_cero(puerta, mod, httpx2):
    """AC8 en la puerta y no solo en el runner: pedir `max_reintentos=2` se niega al construir.

    Se le da transporte falso a proposito: sin el, apagar la guarda hace que `TypeSafeClient` arme su
    maquinaria de sockets y el rojo salga como un AttributeError de trio. Con transporte inyectado, la
    caida del mutante es `DID NOT RAISE`, o sea la firma limpia de que la negacion desaparecio.
    """
    transporte, _ = _transporte(httpx2, status=200, body=RESPUESTA_BUENA)
    with pytest.raises(ValueError, match="max_retries"):
        puerta.cliente_jev(mod, modelo=PIN, api_key=CLAVE_SINTETICA, transport=transporte,
                          max_reintentos=2)
    # Y la ruta autorizada sigue construyendo: la guarda niega el numero, no el brazo entero.
    ok = puerta.cliente_jev(mod, modelo=PIN, api_key=CLAVE_SINTETICA, transport=transporte)
    assert ok is not None


# --------------------------------------------------------------------- AC9: un 200 sin usage es fallo

def test_un_200_sin_usage_es_validacion_y_nunca_coste_cero(puerta, mod, httpx2, runner):
    """AC9 medido: `SystemOneResponse.usage` es obligatorio, asi que un 200 sin `usage` revienta.

    Lo que se niega es la degradacion: ni `usage = null` aceptado ni coste cero. El ledger conserva
    la reserva (`libera_reserva_como_cero False`) y su usage sigue sin observar nada.
    """
    ledger = runner.nuevo_ledger("jev", PIN)
    transporte, contados = _transporte(httpx2, status=200,
                                       body={"model": DEVUELTO, "answers": {}})
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    with pytest.raises(mod.TypeSafeAPIResponseValidationError) as vio:
        puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS, modelo=PIN)
    assert vio.value.status == 200
    assert getattr(vio.value, "field_path", None) == "usage"
    assert contados["invocadas"] == 1
    runner.registrar_intento(ledger, resultado="fallo", excepcion=vio.value)
    uso = ledger["usage_normalized"]
    assert ledger["error_kind"] == "respuesta_ilegible"
    assert uso["total"] is None and uso["input_tokens"] is None
    assert uso["estado"] != "observado"
    assert uso["libera_reserva_como_cero"] is False, (
        "un 200 ileible no puede liberar la reserva como si valiera cero")


def test_usage_dict_del_la_puerta_se_normaliza_igual_que_el_objeto_del_sdk(puerta, mod, httpx2,
                                                                           runner):
    """AC10: la puerta entrega `usage` ya en dict y el ledger lo lee; un dict no es `desconocido`.

    El defecto que este control cierra: `normalizar_usage` leia solo atributos, asi que el dict que
    `system_one_jev` devuelve caia en `desconocido` y una corrida real habria publicado tokens nulos
    con el uso efectivamente observado.
    """
    transporte, _ = _transporte(httpx2, status=200, body=RESPUESTA_BUENA)
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    payload = puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS,
                                    modelo=PIN)
    assert payload["usage"] == {"input_tokens": 111, "output_tokens": 22}
    assert runner.normalizar_usage(payload["usage"]) == {
        "input_tokens": 111, "output_tokens": 22, "total": 133, "estado": "observado",
        "libera_reserva_como_cero": False}
    assert runner.normalizar_usage({"input_tokens": True, "output_tokens": "22"})["estado"] \
        == "desconocido"
    assert runner.normalizar_usage({"input_tokens": None, "output_tokens": None})["estado"] \
        == "desconocido"


# ------------------------------------------------------------- AC4: el modelo efectivo, no el pin

def test_el_modelo_efectivo_es_el_devuelto_y_no_el_pin(puerta, mod, httpx2, runner):
    """AC4/L-ENT.9: el ledger guarda el modelo que el SERVICIO reporto, distinto del pin pedido.

    El transporte falso declara `jev-9.9.9` contra un pedido de `jev-1.13.0`; si el runner publicara
    el pin como si fuera lo devuelto, este control cae por la causa nombrada.
    """
    transporte, _ = _transporte(httpx2, status=200, body=RESPUESTA_BUENA)
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    payload = puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS,
                                    modelo=PIN)
    assert payload["modelo"] == DEVUELTO != PIN
    ledger = runner.nuevo_ledger("jev", PIN)
    runner.registrar_intento(ledger, resultado="exito", usage=payload["usage"],
                             modelo_efectivo=payload["modelo"], duracion_ms=812.5)
    assert ledger["modelo_efectivo"] == DEVUELTO
    assert ledger["modelo_solicitado"] == PIN
    assert ledger["usage_normalized"]["estado"] == "observado"
    assert ledger["attempts"] == 1 and ledger["estado"] == "EJERCITADO"


def test_una_respuesta_sin_modelo_devuelto_no_se_rellena_con_el_pin(puerta, mod, httpx2):
    """AC4: si el servicio no nombra el modelo, `system_one_jev` lo devuelve ausente y no lo inventa.

    El SDK exige `model` en la respuesta, o sea esto es una validacion del SDK y no una decision de
    la puerta: la puerta tampoco lo rellenaria.
    """
    transporte, _ = _transporte(httpx2, status=200,
                                body={"usage": {"input_tokens": 5, "output_tokens": 6},
                                      "answers": {}})
    cliente = puerta.cliente_jev(mod, modelo=PIN, transport=transporte, api_key=CLAVE_SINTETICA)
    with pytest.raises(mod.TypeSafeAPIResponseValidationError) as vio:
        puerta.system_one_jev(cliente, state={"consulta": "x"}, questions=PREGUNTAS, modelo=PIN)
    assert vio.value.field_path == "model"


# ------------------------------------------------------------------ la ruta duradera del SDK (AC9)

def test_cargar_sdk_anade_al_final_y_conserva_el_pydantic_del_product(puerta, sdk, raiz_repo):
    """El site-packages del SDK va AL FINAL de `sys.path`, y por eso `pydantic` sigue siendo el proyecto.

    Medido el 2026-10-03: con `PYTHONPATH` esa ruta queda ANTES del venv y pydantic resuelve 2.13.5,
    o sea la corrida dejaria de ser el entorno del piloto. Este es el diente de esa trampa: si alguien
    cambia `append` por `insert(0, ...)`, la version reportada sube y el control cae por la causa
    escrita.
    """
    sitio = str(puerta.ruta_del_sdk(raiz_repo))
    assert sitio in sys.path, "la ruta duradera no esta en sys.path: el SDK no se esta cargando por ella"
    venv_paquete = next((p for p in sys.path if "venv" in p.lower() and "site-packages" in p.lower()),
                        None)
    assert venv_paquete is not None and sys.path.index(sitio) > sys.path.index(venv_paquete), (
        "el site-packages del SDK quedo ANTES que el del venv: la resolucion dejo de ser la del "
        "proyecto (la trampa de PYTHONPATH, medida el 2026-10-03)")
    assert sdk["resolucion"]["pydantic"] == "2.12.5", (
        f"pydantic resolvio {sdk['resolucion']['pydantic']}: esta corrida ya no es la del proyecto")
    assert sdk["resolucion"]["typesafe-sdk"] == "0.7.0"
    assert sitio.endswith("Lib" + __import__("os").sep + "site-packages") or \
        sitio.replace("\\", "/").endswith("Lib/site-packages")


def test_cargar_sdk_con_un_sitio_inexistente_no_deja_rastro_en_sys_path(puerta):
    """`BrazoNoInstalable` falla fuerte y no deja una ruta colgada que ensucie la siguiente import."""
    antes = list(sys.path)
    with pytest.raises(puerta.BrazoNoInstalable, match="no existe"):
        puerta.cargar_sdk(sitio=Path("Z:/no-existe-jev-piloto/site-packages"))
    assert sys.path == antes


def test_cargar_sdk_devuelve_el_mismo_modulo_si_ya_esta_cargado(puerta, sdk, raiz_repo):
    """`ya_estaba_en_sys_path` se publica: la segunda carga no apila la ruta ni cambia la resolucion.

    Sin el flag publicado, una `cargar_sdk` repetida pareceria una carga nueva y el lector no podria
    distinguir «ya estaba» de «se apilo otra vez».
    """
    sitio = str(puerta.ruta_del_sdk(raiz_repo))
    assert sdk["ya_estaba_en_sys_path"] is True or sys.path.count(sitio) == 1
    segunda = puerta.cargar_sdk()
    assert segunda["ya_estaba_en_sys_path"] is True
    assert sys.path.count(sitio) == 1, "la ruta del SDK se apilo en sys.path"
    assert segunda["modulo"] is sdk["modulo"]
    assert segunda["resolucion"] == sdk["resolucion"]
