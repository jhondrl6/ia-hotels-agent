"""Sonda de estabilidad del alias DeepSeek (ampliacion autorizada de la fila 2, 2026-10-04).

Que se mide
    1. Si el `model` que devuelve el servicio es estable al repetir el MISMO pedido `deepseek-chat`
       (dos envios, cuerpo construido por el brazo).
    2. Si `deepseek-flash` —el nombre que el servicio echo— es **direccionable**: se pide explicitamente y
       se observa si el servicio lo acepta o lo rechaza con su codigo. Este es el dato que decide si la
       opcion «cambiar el pedido» existe siquiera.
    3. Por via lateral, la causa del `respuestas` vacio de la primera sonda: el transporte guarda el
       `finish_reason`, la longitud del `content` y las claves del JSON que el brazo recibi6, sin tocar el
       contrato de `evaluar`.

Coste y limites
    Cuatro envios como maximo (3 sondas + 1 repeticion de la tercera si el primer par diverge). Cero
    reintentos del brazo: un fallo se registra y se pasa a la siguiente sonda, no se persigue. No se
    imprime la clave, ni el header Authorization, ni el contenido de `.env`. El `content` del modelo se
    publica recortado a 160 caracteres y solo para nombrar la forma, nunca como dato de producto.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
MAX_TOKENS = 64
STATE = "FASE-B del piloto JEV cerrada el 2026-10-04."
ENUNCIADO = ("¿La siguiente frase afirma algo verificable? «El piloto JEV cerro FASE-B documentalmente "
             "el 2026-10-04.»")
CONTENIDO_MAX = 160


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clave_desde_env(nombre: str):
    env = ROOT / ".env"
    if not env.is_file():
        return None
    for linea in env.read_text(encoding="utf-8", errors="replace").splitlines():
        s = linea.strip()
        if s.startswith(f"{nombre}="):
            return s.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def _forma(respuesta):
    """La forma de la respuesta del servicio, no su mensaje: longitudes, claves y un recorte."""
    opciones = (respuesta or {}).get("choices") or []
    if not opciones:
        return {"choices": 0, "finish_reason": None, "content_len": None, "content_head": None,
                "json_claves": None, "json_respuestas": None, "json_pregunta_ids": None}
    c = ((opciones[0] or {}).get("message") or {}).get("content")
    fila = {"choices": len(opciones), "finish_reason": (opciones[0] or {}).get("finish_reason"),
            "content_len": len(c) if isinstance(c, str) else None,
            "content_head": (c[:CONTENIDO_MAX] if isinstance(c, str) else None),
            "json_claves": None, "json_respuestas": None, "json_pregunta_ids": None}
    try:
        datos = json.loads(c) if isinstance(c, str) else None
    except json.JSONDecodeError:
        fila["json_claves"] = "NO_ES_JSON"
        return fila
    if isinstance(datos, dict):
        fila["json_claves"] = sorted(datos.keys())
        respuestas = datos.get("respuestas")
        if isinstance(respuestas, list):
            fila["json_respuestas"] = len(respuestas)
            fila["json_pregunta_ids"] = [r.get("pregunta_id") for r in respuestas if isinstance(r, dict)]
    return fila


def sonda(dsp, dc, modelo_a_pedir: str, entorno: dict, registro_grueso: list):
    """Una llamada por el brazo, con el modelo pedido sustituido EN MEMORIA (el archivo no se toca)."""
    def transporte(request: dict) -> dict:
        body = dict(request["body"])
        body["max_tokens"] = MAX_TOKENS
        body["model"] = modelo_a_pedir          # lo que el brazo pone en el cuerpo, declarado aqui
        req = urllib.request.Request(
            request["url"], data=json.dumps(body).encode("utf-8"), method="POST",
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + request["api_key"]})
        try:
            with urllib.request.urlopen(req, timeout=request["timeout_s"]) as resp:
                crudo = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detalle = exc.read().decode("utf-8", "replace")[:220] if hasattr(exc, "read") else ""
            raise dsp.RespuestaServicioFalla(f"HTTP {exc.code}: {detalle}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise dsp.RespuestaServicioFalla(f"conexion: {exc}") from exc
        registro_grueso.append(_forma(crudo))
        return crudo

    preguntas = [dc.Pregunta("sonda:1", "noul", ENUNCIADO)]
    inicio = time.time()
    fila = {"modelo_pedido_en_el_cuerpo": modelo_a_pedir}
    try:
        salida = dsp.evaluar(STATE, preguntas, transporte=transporte, entorno=entorno, timeout_s=30.0)
        fila.update({"ok": True, "modelo_efectivo_devuelto": salida.get("modelo"),
                     "usage": salida.get("usage"), "request_id": salida.get("request_id"),
                     "respuestas": salida.get("respuestas"),
                     "n_respuestas": len(salida.get("respuestas") or [])})
    except Exception as exc:  # noqa: BLE001
        fila.update({"ok": False, "clase": type(exc).__name__, "mensaje": str(exc)[:260]})
    fila["duracion_s"] = round(time.time() - inicio, 2)
    return fila


def main() -> int:
    dsp = _cargar("dsp_est", ROOT / "scripts" / "proveedores" / "deepseek.py")
    dc = _cargar("dc_est", ROOT / "scripts" / "decision_client.py")
    modelo_de_casa = dsp.PROVEEDOR["modelo"]

    clave = clave_desde_env("DEEPSEEK_API_KEY")
    registro = {"sonda": "deepseek-estabilidad-del-alias-2026-10-04",
                "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "instrumento": "python temp/deuda-2026-10-04/p4b_deepseek_estabilidad.py",
                "autorizacion": "el operador autorizo la opcion (b) de la sesion: sondas minimas para medir "
                                "la estabilidad del eco del modelo",
                "endpoint": dsp.PROVEEDOR["endpoint"],
                "modelo_declarado_por_el_brazo": modelo_de_casa,
                "alias_movil_declarado": dsp.PROVEEDOR["alias_movil"],
                "credencial": {"variable": "DEEPSEEK_API_KEY", "presente_en_env": bool(clave)},
                "payload_fijo": {"state": "una linea", "preguntas": 1, "tipo": "noul",
                                 "temperature": 0, "max_tokens": MAX_TOKENS},
                "sondas": []}
    if not clave:
        registro["resultado"] = "NO-INTENTADA"
        registro["motivo"] = "DEEPSEEK_API_KEY no esta en .env"
        print(json.dumps(registro, ensure_ascii=False, indent=2))
        return 2

    entorno = {"DEEPSEEK_API_KEY": clave}
    plan = [("deepseek-chat", "repeticion 1 del pedido de casa"),
            ("deepseek-chat", "repeticion 2 del pedido de casa"),
            ("deepseek-flash", "el nombre que el servicio echo, pedido explicitamente")]

    for i, (modelo, motivo) in enumerate(plan, 1):
        grueso: list = []
        fila = {"sonda": i, "motivo": motivo}
        fila.update(sonda(dsp, dc, modelo, entorno, grueso))
        if grueso:
            fila["forma_de_la_respuesta"] = grueso[0]
        registro["sondas"].append(fila)
        if fila.get("ok") is False and "HTTP 401" in str(fila.get("mensaje", "")):
            registro["corte"] = f"sonda {i}: autenticacion rechazada, no se hacen los envios restantes"
            break
        time.sleep(1.0)

    ecos = [s.get("modelo_efectivo_devuelto") for s in registro["sondas"] if s.get("ok")]
    registro["resumen"] = {
        "envios_ejecutados": len(registro["sondas"]),
        "envios_exitosos": len(ecos),
        "eco_de_deepseek_chat": sorted({s.get("modelo_efectivo_devuelto") for s in registro["sondas"]
                                        if s.get("ok") and s["modelo_pedido_en_el_cuerpo"] == "deepseek-chat"}),
        "respuesta_a_pedir_deepseek_flash": next(
            ({"ok": s["ok"], "modelo_devuelto": s.get("modelo_efectivo_devuelto"),
              "mensaje": s.get("mensaje")} for s in reversed(registro["sondas"])
            if s.get("ok") is not None and s["modelo_pedido_en_el_cuerpo"] == "deepseek-flash"), None),
        "respuestas_no_vacias": [s.get("n_respuestas") for s in registro["sondas"] if s.get("ok")],
    }
    print(json.dumps(registro, ensure_ascii=False, indent=2))
    destino = Path(__file__).with_name("09-deepseek-estabilidad-crudo.json")
    destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if registro["resumen"]["envios_exitosos"] else 1


if __name__ == "__main__":
    sys.exit(main())
