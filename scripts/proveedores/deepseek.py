"""Brazo DeepSeek EXPLICITO del piloto JEV, en la forma que la costura ya admite.

La puerta (`scripts/decision_client.py`) resuelve proveedores por entorno y los carga por ruta: este
archivo es un modulo de proveedor, no un framework nuevo ni un buscador. Vive bajo un directorio
`*proveedores*` a proposito: AC6 declara esa familia como superficie de contrabando, y este modulo
no hace ninguna carga dinamica, asi que estar dentro es lo que hace el escaneo mas honesto, no mas
permisivo.

Que NO hace, y por eso existe la prueba que lo afirma:

* no mira `ANTHROPIC_API_KEY` ni ninguna otra credencial: Anthropic esta excluido por el protocolo y
  la ausencia del propio `DEEPSEEK_API_KEY` detiene la llamada en vez de derivar a otro brazo;
* no inventa `confidence` ni `probabilidades`: un self-report del modelo no es una probabilidad
  calibrada (prompt de FASE-B, tarea 4), asi que si el servicio no los trae, el payload se va por
  `ILEGIBLE` con su motivo en vez de rellenarse;
* no toca `modules/providers/llm_provider.py`: el comparador se construye por la costura.

Reproducibilidad declarada: `deepseek-chat` es un **alias movil** del proveedor. Se publica como
`alias_movil` en el payload para que la tabla comparativa no lo presente como version fijada.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

PROVEEDOR = {
    "nombre": "deepseek-comparador",
    "falso": False,
    "credencial_env": "DEEPSEEK_API_KEY",
    "modelo": "deepseek-chat",
    "alias_movil": True,
    "sin_fallback": True,
    "brazo_excluido": "anthropic",
    "endpoint": "https://api.deepseek.com/v1/chat/completions",
    "nota": ("comparador del piloto EVALUACION-JEV-TYPESAFE-2026-09-21; solo responde si la costura "
             "lo nombra por entorno"),
}

CREDENCIALES_NO_MIRADAS = ("ANTHROPIC_API_KEY", "OPENROUTER_API_KEY", "TYPESAFE_API_KEY")


class CredencialAusente(RuntimeError):
    """Falta la credencial que ESTE brazo declara. Se lanza antes de tocar el transporte (AC2/AC12).

    Lleva el nombre de la variable buscada y la lista de las que no se miraron, para que el informe
    pueda afirmar que no hubo fallback sin tener que leer ninguna credencial.
    """

    def __init__(self, env_buscado: str, entorno: dict):
        super().__init__(f"{env_buscado} no esta en el entorno: el brazo DeepSeek se detiene, "
                         f"no se deriva a otro proveedor (no se leyeron {list(CREDENCIALES_NO_MIRADAS)})")
        self.env_buscado = env_buscado
        self.no_lecturas = [nombre for nombre in CREDENCIALES_NO_MIRADAS if nombre in entorno]


class RespuestaServicioFalla(RuntimeError):
    """El servicio contesto mal o no contesto: se conserva el codigo y el texto, no se re-escribe."""


def _instrucciones(preguntas) -> str:
    partes = []
    for p in preguntas:
        if p.tipo == "choice":
            partes.append(f"{p.id}: choice entre {list(p.opciones)} — {p.enunciado}")
        elif p.tipo == "score":
            partes.append(f"{p.id}: score 0..{len(p.leyenda) - 1} ({list(p.leyenda)}) — {p.enunciado}")
        else:
            partes.append(f"{p.id}: noul (probabilidad de si entre 0 y 1) — {p.enunciado}")
    return ("Responde SOLO con JSON: {\"respuestas\": [{\"pregunta_id\", \"tipo\", y segun el tipo "
            "\"eleccion\"+\"probabilidades\"+\"confidence\", \"nivel\"+\"leyenda\"+\"confidence\", o "
            "\"probabilidad_si\"}]}.\n" + "\n".join(partes))


def post_default(request: dict) -> dict:
    """El unico camino de red del brazo. `evaluar` lo sustituye con un transporte falso en las pruebas.

    No hay reintento aqui: el contrato del piloto goberna los intentos en el ledger, y un reintento
    silencioso en el transporte sería un intento que nadie conto (AC8).
    """
    cuerpo = json.dumps(request["body"]).encode("utf-8")
    req = urllib.request.Request(request["url"], data=cuerpo, method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + request["api_key"]})
    try:
        with urllib.request.urlopen(req, timeout=request["timeout_s"]) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RespuestaServicioFalla(f"HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RespuestaServicioFalla(f"conexion: {exc}") from exc


def _contenido_a_respuestas(crudo) -> dict:
    """Del envelope del servicio al cuerpo de respuestas.

    Un chat-completion trae el JSON adentro de `choices[0].message.content`, no en la raiz: leerlo
    directo del payload seria un contrato que solo funciona con el falso del test. Un content que no
    es JSON es un fallo DEL SERVICIO y se nombra como tal, no se convierte en lista vacia (DA-C3).
    """
    opciones = crudo.get("choices") or []
    if not opciones:
        raise RespuestaServicioFalla("el servicio devolvio `choices` vacio: no hay respuestas")
    texto = ((opciones[0] or {}).get("message") or {}).get("content")
    if not isinstance(texto, str) or not texto.strip():
        raise RespuestaServicioFalla("el mensaje del servicio vino sin contenido")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        raise RespuestaServicioFalla(f"el content no es JSON: {exc}") from exc
    return datos if isinstance(datos, dict) else {"respuestas": datos}


def _mapear_respuestas(crudo, preguntas) -> list:
    """Conserva lo que el servicio trajo y no rellena lo que no trajo.

    Un campo de probabilidad ausente se deja ausente a proposito: la puerta lo convierte en
    `ILEGIBLE`, que es el estado honesto, y no en un numero inventado que despues se lee como
    probabilidad calibrada.
    """
    por_id = {}
    for r in (crudo.get("respuestas") or []):
        if isinstance(r, dict) and r.get("pregunta_id"):
            por_id[r["pregunta_id"]] = r
    salida = []
    for p in preguntas:
        bruto = por_id.get(p.id)
        if bruto is None:
            continue
        if p.tipo == "noul":
            fila = {"pregunta_id": p.id, "tipo": "noul"}
            if "probabilidad_si" in bruto:
                fila["probabilidad_si"] = bruto["probabilidad_si"]
        elif p.tipo == "choice":
            fila = {"pregunta_id": p.id, "tipo": "choice"}
            for k in ("eleccion", "probabilidades", "confidence"):
                if k in bruto:
                    fila[k] = bruto[k]
        else:
            fila = {"pregunta_id": p.id, "tipo": "score"}
            for k in ("nivel", "leyenda", "confidence"):
                if k in bruto:
                    fila[k] = bruto[k]
        salida.append(fila)
    return salida


def evaluar(state, preguntas, transporte=None, entorno=None, timeout_s: float = 30.0) -> dict:
    """Devuelve el payload del contrato. `transporte` existe para ejercitar la rama sin red (AC9)."""
    entorno = os.environ if entorno is None else entorno
    clave = entorno.get(PROVEEDOR["credencial_env"])
    if not clave:
        raise CredencialAusente(PROVEEDOR["credencial_env"], entorno)
    body = {"model": PROVEEDOR["modelo"],
            "messages": [{"role": "user",
                          "content": _instrucciones(preguntas) + "\n\nCONTEXTO:\n" + str(state)}],
            "temperature": 0}
    llamar = transporte or post_default
    crudo = llamar({"url": PROVEEDOR["endpoint"], "body": body, "api_key": clave,
                    "timeout_s": timeout_s, "nombre": PROVEEDOR["nombre"]})
    uso = crudo.get("usage") or {}
    return {
        # El modelo que el SERVICIO reporto, nunca el pedido re-etiquetado: si el servicio no lo
        # nombra, esto es None y la puerta lo falla por `metadata-modelo-usage`, que es el estado
        # honesto. Rellenarlo con el pedido fingiria reproducibilidad (AC4 / L-ENT.9).
        "modelo": crudo.get("model"),
        "respuestas": _mapear_respuestas(_contenido_a_respuestas(crudo), preguntas),
        # Solo las cuatro claves que `check_campos_conocidos` admite: una quinta vuelta ILEGIBLE
        # cualquier respuesta correcta, o sea el metadato extra tenia que irse del payload.
        "usage": {"input_tokens": uso.get("prompt_tokens"),
                  "output_tokens": uso.get("completion_tokens")},
        "request_id": crudo.get("id"),
    }
