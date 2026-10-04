"""Paso 1c (2026-10-03): el brazo DeepSeek EXPLICITO, por la costura y sin fallback a Anthropic.

Tres cosas se prueban aqui y cada una con su contrafactual:

* **falta la credencial -> falla antes de enviar**, aunque el entorno traiga una clave Anthropic
  sintetica. Que el fallo sea `CredencialAusente` y no `RedProhibida` es la prueba de que no se
  toco el transporte: el guard de red del conftest esta armado, y un envio lo habria gritado;
* **usage y modelo se preservan antes de descartarlos** (AC4 / L-ENT.9): el payload del servicio
  llega intacto a `ResultadoEvaluacion`, y `model_requested` sigue siendo distinto de `modelo`;
* **no se inventa `confidence`**: si el servicio no la trajo, la puerta responde `ILEGIBLE`.

`modules/providers/llm_provider.py` no se toca ni se importa desde el piloto, y el ultimo control
lo afirma por AST sobre los tres archivos del piloto.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

NOMBRE = "deepseek-comparador"
PINEADO = "deepseek-chat"
DEVUELTO_POR_EL_SERVICIO = "deepseek-chat-2026-09-30-fix"
CLAVE_SINTETICA = "sk-sintetica-de-test-que-no-es-una-credencial"


@pytest.fixture(scope="session")
def ruta_proveedor(raiz_repo) -> Path:
    return raiz_repo / "scripts" / "proveedores" / "deepseek.py"


@pytest.fixture
def proveedor(dc, ruta_proveedor):
    """El modulo del brazo, cargado por el lector REAL de la puerta (`cargar_modulo_proveedor`)."""
    return dc.cargar_modulo_proveedor(ruta_proveedor)


@pytest.fixture
def entorno_brazo(raiz_repo):
    return {"IAH_DECISION_PROVIDER": NOMBRE,
            "IAH_DECISION_PROVIDERS_DIR": str(raiz_repo / "scripts" / "proveedores")}


RESPUESTAS_INNER = [{"pregunta_id": "n1", "probabilidad_si": 0.11},
                    {"pregunta_id": "c1", "eleccion": "pertinente",
                     "probabilidades": {"pertinente": 0.7, "no_pertinente": 0.2,
                                        "insuficiente": 0.1},
                     "confidence": 0.7}]


def _crudo_ok(respuestas=None):
    """El envelope real de un chat-completion: el JSON va DENTRO de choices[0].message.content."""
    return {"id": "cmpl-1", "model": DEVUELTO_POR_EL_SERVICIO,
            "usage": {"prompt_tokens": 1234, "completion_tokens": 56},
            "choices": [{"message": {"content": json.dumps(
                {"respuestas": respuestas if respuestas is not None else RESPUESTAS_INNER})}}]}


def _transporte_que_cuenta():
    vistos = {"llamadas": []}

    def transporte(request):
        vistos["llamadas"].append(request)
        return _crudo_ok()
    return transporte, vistos


# ------------------------------------------------------------------ AC2/AC12: sin clave, cero envio

def test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic(
        dc, proveedor, entorno_brazo, excpcion_de_red):
    """AC2/AC12: el brazo se detiene por su propia credencial y no se deriva a Anthropic.

    Que la excepcion sea `CredencialAusente` y no `RedProhibida` es la mitad del control: el guard
    de red esta armado, asi que cualquier intento de envio habria saltado antes. La clave Anthropic
    sintetica esta puesta a proposito: si alguien programara un fallback, aqui se veria.
    """
    entorno = {**entorno_brazo, "ANTHROPIC_API_KEY": CLAVE_SINTETICA}
    with pytest.raises(Exception) as vio:
        dc.evaluar("estado del plan", [dc.Pregunta("n1", "noul", "¿Sigues vigente?")],
                   entorno=entorno)
    assert type(vio.value).__name__ == "CredencialAusente", (
        f"esperaba CredencialAusente y hubo {type(vio.value).__name__}: hubo un intento de envio")
    assert not isinstance(vio.value, excpcion_de_red)
    assert "DEEPSEEK_API_KEY" in str(vio.value)
    assert vio.value.env_buscado == "DEEPSEEK_API_KEY"
    # La clave ajena aparece en el mensaje SOLO en la lista de las que no se leyeron: nombrarlas es
    # como el informe prueba la ausencia de fallback, contarlas como uso seria el rojo falso.
    assert "no se leyeron" in str(vio.value) and vio.value.env_buscado == "DEEPSEEK_API_KEY"


def test_el_brazo_no_lee_otras_credenciales_aunque_esten(proveedor, dc, entorno_brazo):
    """AC12: la unica credencial que este brazo mira es la que declara; las demas no se leen.

    `no_lecturas` registra cuales habia en el entorno, por nombre y sin valor: es lo que permite
    afirmar que Anthropic estaba presente y aun asi no se uso.
    """
    entorno = {**entorno_brazo, "ANTHROPIC_API_KEY": CLAVE_SINTETICA,
               "OPENROUTER_API_KEY": CLAVE_SINTETICA}
    with pytest.raises(Exception) as vio:
        proveedor.evaluar("estado", [dc.Pregunta("n1", "noul", "¿Sigues vigente?")],
                          entorno=entorno)
    assert set(vio.value.no_lecturas) == {"ANTHROPIC_API_KEY", "OPENROUTER_API_KEY"}
    assert "TYPESAFE_API_KEY" not in vio.value.no_lecturas


def test_con_clave_presente_el_brazo_si_intenta_enviar(proveedor, dc, entorno_brazo):
    """La otra mitad del criterio: con la clave puesta el camino LLEGA al transporte real.

    Sin este control, «falla antes de enviar» podria significar simplemente «nunca envia». El guard
    de red del conftest es el que da la señal: si el brazo no intentara, esto no levantaria.
    """
    with pytest.raises(Exception) as vio:
        proveedor.evaluar("estado", [dc.Pregunta("n1", "noul", "¿Sigues vigente?")],
                          transporte=None,
                          entorno={**entorno_brazo, "DEEPSEEK_API_KEY": CLAVE_SINTETICA})
    assert type(vio.value).__name__ == "RedProhibida", (
        f"el brazo no salio al transporte sino a {type(vio.value).__name__}: el criterio de arriba "
        "seria «nunca envia» y no «falla antes de enviar»")


# ------------------------------------------------------------------ AC4: crudo preservado, no rellenado

def test_usage_y_modelo_crudos_sobreviven_el_adapter(proveedor, dc, entorno_brazo):
    """AC4: el modelo que devolvio el servicio y sus tokens llegan intactos a la puerta.

    `modelo_solicitado` (el alias pineado) y `modelo` (lo devuelto) son cuerdas distintas y deben
    seguir siendolo en el resultado: el piloto reporta el efectivo, nunca el pin.
    """
    transporte, vistos = _transporte_que_cuenta()
    payload = proveedor.evaluar(
        "estado del plan",
        [dc.Pregunta("n1", "noul", "¿Sigues vigente?"),
         dc.Pregunta("c1", "choice", "¿Cual?", opciones=("pertinente", "no_pertinente",
                                                          "insuficiente"))],
        transporte=transporte, entorno={"DEEPSEEK_API_KEY": CLAVE_SINTETICA})
    assert vistos["llamadas"][0]["body"]["model"] == PINEADO
    assert payload["modelo"] == DEVUELTO_POR_EL_SERVICIO != PINEADO
    assert payload["usage"] == {"input_tokens": 1234, "output_tokens": 56}
    assert payload["request_id"] == "cmpl-1"
    validado = dc.validar_payload(payload, [dc.Pregunta("n1", "noul", "¿Sigues vigente?"),
                                            dc.Pregunta("c1", "choice", "¿Cual?",
                                                        opciones=("pertinente", "no_pertinente",
                                                                  "insuficiente"))],
                                  NOMBRE)
    assert validado is payload


def test_el_estado_de_la_cuenta_de_deepseek_no_se_confunde_con_una_respuesta_negativa(
        proveedor, dc):
    """DA-C3: `p_yes` bajo NO se reclasifica como abstencion ni como error (AC2)."""
    transporte, _ = _transporte_que_cuenta()
    payload = proveedor.evaluar("estado", [dc.Pregunta("n1", "noul", "¿Sigues vigente?")],
                               transporte=transporte,
                               entorno={"DEEPSEEK_API_KEY": CLAVE_SINTETICA})
    noul = [r for r in payload["respuestas"] if r["tipo"] == "noul"][0]
    assert noul["probabilidad_si"] == 0.11
    tipadas = dc.a_respuestas_tipadas(payload)
    assert type(tipadas[0]).__name__ == "RespuestaNoul"
    assert tipadas[0].to_dict()["probabilidad_si"] == 0.11, (
        "la puerta convirtio un 0.11 en otra cosa: un no claro no es una abstencion")


def test_deepseek_no_inventa_confidence_y_la_puerta_responde_ilegible(proveedor, dc):
    """Tarea 4 del prompt: un self-report del modelo no es una probabilidad calibrada.

    Si el servicio no trae `confidence`, el mapping la deja ausente a proposito y `validar_payload`
    responde `ILEGIBLE` con el guard que la produjo nombrado. Rellenarla daria un favorable inventado.
    """
    sin_conf = [dict(r) for r in RESPUESTAS_INNER]
    for r in sin_conf:
        r.pop("confidence", None)

    def transporte(request):
        return _crudo_ok(sin_conf)

    payload = proveedor.evaluar(
        "estado", [dc.Pregunta("c1", "choice", "¿Cual?",
                              opciones=("pertinente", "no_pertinente", "insuficiente"))],
        transporte=transporte, entorno={"DEEPSEEK_API_KEY": CLAVE_SINTETICA})
    assert "confidence" not in payload["respuestas"][0]
    with pytest.raises(dc.RespuestaIlegible) as vio:
        dc.validar_payload(payload, [dc.Pregunta("c1", "choice", "¿Cual?",
                                                opciones=("pertinente", "no_pertinente",
                                                          "insuficiente"))], NOMBRE)
    assert any("campos-conocidos" in m and "confidence" in m for m in vio.value.motivos), \
        vio.value.motivos


def test_un_deepseek_sin_modelo_devuelto_no_se_rellena_con_el_pineado(proveedor, dc):
    """AC4: si el servicio no nombra el modelo, `modelo` es None y la puerta lo falla por metadata."""
    def transporte(request):
        crudo = _crudo_ok()
        crudo.pop("model")
        return crudo

    payload = proveedor.evaluar("estado", [dc.Pregunta("n1", "noul", "¿Sigues vigente?")],
                               transporte=transporte,
                               entorno={"DEEPSEEK_API_KEY": CLAVE_SINTETICA})
    assert payload["modelo"] is None
    with pytest.raises(dc.RespuestaIlegible) as vio:
        dc.validar_payload(payload, [dc.Pregunta("n1", "noul", "¿Sigues vigente?")], NOMBRE)
    assert any("metadata-modelo-usage" in m for m in vio.value.motivos)


# ------------------------------------------------------------------------ la declaracion del brazo

def test_el_proveedor_declara_alias_movil_y_exclusion_de_anthropic(proveedor):
    """Tarea 1 del prompt: declarar cualquier alias que impida reproducibilidad estricta.

    `deepseek-chat` es alias movil del proveedor: se publica como tal para que la tabla comparativa
    no lo presente como version fijada, y Anthropic queda excluido por declaracion, no por olvido.
    """
    decl = proveedor.PROVEEDOR
    assert decl["nombre"] == NOMBRE and decl["credencial_env"] == "DEEPSEEK_API_KEY"
    assert decl["alias_movil"] is True and decl["sin_fallback"] is True
    assert decl["brazo_excluido"] == "anthropic"
    assert decl["falso"] is False, "un brazo del piloto no puede declararse de prueba"


def test_la_puerta_resuelve_el_brazo_por_entorno_sin_default(dc, entorno_brazo):
    """AC12: el brazo existe solo si la costura lo nombra; sin `IAH_DECISION_PROVIDER` no hay candidato."""
    estado = dc.estado_proveedor(entorno_brazo)
    assert estado["provider_status"] == "RESUELTO" and estado["proveedor"] == NOMBRE
    assert estado["credencial"]["presente"] is False, "la puerta reportaria presence, jamas el valor"
    assert "env_var" in estado["credencial"]

    with pytest.raises(dc.ProveedorNoConfigurado):
        dc.resolver_proveedor({})


# ------------------------------------------------------- llm_provider.py intacto, por AST (AC6/AC7)

def test_los_tres_archivos_del_piloto_no_importan_llm_provider(dc, raiz_repo):
    """El comparador no pasa por `modules/providers/llm_provider.py`: ni lo importa ni lo carga.

    El control es por AST sobre la poblacion nombrada, no por `git diff`: un import nuevo cae aqui
    con el archivo y la linea. La AC de intactibilidad del archivo la goberna el diff del rango.
    """
    archivos = [raiz_repo / "scripts" / "evaluate_jev_pilot.py",
                raiz_repo / "scripts" / "decision_client.py",
                raiz_repo / "scripts" / "proveedores" / "deepseek.py"]
    for ruta in archivos:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        importados = []
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom) and nodo.module:
                importados.append(nodo.module)
            elif isinstance(nodo, ast.Import):
                importados += [a.name for a in nodo.names]
        prohibidos = [m for m in importados if "providers" in m or "llm_provider" in m]
        assert not prohibidos, f"{ruta.name} importa {prohibidos}: el brazo toca el proveedor legacy"
    # Y tampoco lo carga en runtime con nombre literal: el escaneo de cargas es el otro lado del AST.
    for ruta in archivos:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call) and (getattr(nodo.func, "attr", "") or
                                               getattr(nodo.func, "id", "")) in (
                    "import_module", "__import__"):
                literales = [a.value for a in nodo.args
                             if isinstance(a, ast.Constant) and isinstance(a.value, str)]
                assert not [lit for lit in literales if "llm_provider" in lit or "providers" in lit], (
                    f"{ruta.name} carga el proveedor legacy en runtime: {literales}")
