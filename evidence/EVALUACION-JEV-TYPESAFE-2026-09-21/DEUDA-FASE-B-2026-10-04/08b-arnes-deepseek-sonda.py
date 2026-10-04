"""Sonda DeepSeek real (fila 2 de la deuda de FASE-B, AC12 + AC4), por el brazo de la costura.

Autorizacion literal de la sesion: UNA llamada `chat/completions`, maximo 2 intentos, payload minimo, con
`DEEPSEEK_API_KEY` leida de `.env`. Prohibido imprimir la clave, el header Authorization o el contenido de
`.env`: este arnes solo publica booleans de presencia, codigos, tokens de usage y duracion.

El brazo es invocable aislado (`scripts/proveedores/deepseek.py:evaluar`), asi que se usa la via
preferida y no la HTTP directa. El unico detalle del cuerpo que el arnes anade es `max_tokens`, y lo anade
por la costura documentada de `transporte` (esa es su razon de existir en el contrato del brazo): el resto
del payload es el que construye `evaluar`, y el parsing de la respuesta tambien.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

MAX_TOKENS = 64
TOPE_INTENTOS = 2


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clave_desde_env(nombre: str) -> str | None:
    """Lee UNA variable de `.env` sin imprimir el archivo ni su contenido."""
    env = ROOT / ".env"
    if not env.is_file():
        return None
    for linea in env.read_text(encoding="utf-8", errors="replace").splitlines():
        s = linea.strip()
        if s.startswith(f"{nombre}="):
            return s.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def kind_por_codigo(texto: str) -> dict:
    """`error_kind` medido del codigo HTTP que conserva el brazo en su mensaje.

    `evaluate_jev_pilot.CLASES_DE_ERROR` classify por nombres del SDK de TypeSafe: la excepcion del brazo
    DeepSeek no esta ahi, asi que reutilizarla daria `desconocido` para un 401 perfectamente nombrado. Se
    declara el mapeo propio en vez de prestar el ajeno.
    """
    codigo = re.search(r"HTTP (\d{3})", texto or "")
    n = int(codigo.group(1)) if codigo else None
    if n in (401, 403):
        return {"error_kind": "auth", "http_status": n}
    if n == 402:
        return {"error_kind": "cuota", "http_status": n}
    if n == 429:
        return {"error_kind": "cuota", "http_status": n}
    if n and n >= 500:
        return {"error_kind": "servidor", "http_status": n}
    if n:
        return {"error_kind": "peticion", "http_status": n}
    if "conexion" in (texto or "").lower() or "timed out" in (texto or "").lower():
        return {"error_kind": "conexion", "http_status": None}
    return {"error_kind": "desconocido", "http_status": n}


def main() -> int:
    dsp = _cargar("dsp_brazo", ROOT / "scripts" / "proveedores" / "deepseek.py")
    dc = _cargar("dc_sonda", ROOT / "scripts" / "decision_client.py")

    clave = clave_desde_env("DEEPSEEK_API_KEY")
    registro = {"sonda": "deepseek-preflight-deuda-2026-10-04",
                "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "instrumento": "python temp/deuda-2026-10-04/p4_deepseek.py",
                "via": "brazo de la costura: scripts/proveedores/deepseek.py:evaluar con transporte que "
                       "anade max_tokens y despues llama a post_default (el unico camino de red del brazo)",
                "endpoint": dsp.PROVEEDOR["endpoint"],
                "modelo_pedido": dsp.PROVEEDOR["modelo"],
                "alias_movil_declarado": dsp.PROVEEDOR["alias_movil"],
                "credencial": {"variable": "DEEPSEEK_API_KEY", "presente_en_env": bool(clave),
                               "leida_de": ".env (una linea, por nombre; el archivo no se imprime)",
                              },
                "payload": {"state": "una linea", "preguntas": 1, "tipo_pregunta": "noul",
                            "max_tokens": MAX_TOKENS, "temperature": 0},
                "intentos": []}
    if not clave:
        registro["autenticacion_real"] = "NO-INTENTADA"
        registro["motivo"] = "DEEPSEEK_API_KEY no esta en .env: el brazo se detiene sin fallback (AC12)"
        print(json.dumps(registro, ensure_ascii=False, indent=2))
        return 2

    entorno = {"DEEPSEEK_API_KEY": clave}
    preguntas = [dc.Pregunta("sonda:1", "noul",
                             "¿La siguiente frase afirma algo verificable? «El piloto JEV cerro FASE-B "
                             "documentalmente el 2026-10-04.»")]

    def transporte_con_tope(request: dict) -> dict:
        body = dict(request["body"])
        body["max_tokens"] = MAX_TOKENS
        return dsp.post_default({**request, "body": body})

    for intento in range(1, TOPE_INTENTOS + 1):
        inicio = time.time()
        fila = {"intento": intento, "reintentos_del_brazo": 0}
        try:
            salida = dsp.evaluar("FASE-B del piloto JEV cerrada el 2026-10-04.", preguntas,
                                 transporte=transporte_con_tope, entorno=entorno, timeout_s=30.0)
            fila.update({"ok": True, "modelo_efectivo_devuelto": salida.get("modelo"),
                         "usage": salida.get("usage"), "request_id": salida.get("request_id"),
                         "respuestas": salida.get("respuestas"),
                         "duracion_s": round(time.time() - inicio, 2)})
            registro["intentos"].append(fila)
            registro["autenticacion_real"] = "AUTENTICADA"
            registro["modelo_efectivo_devuelto"] = salida.get("modelo")
            registro["usage_tokens"] = salida.get("usage")
            registro["request_id"] = salida.get("request_id")
            registro["contraste_del_pedido"] = {
                "pedido": dsp.PROVEEDOR["modelo"],
                "devuelto": salida.get("modelo"),
                "casa": salida.get("modelo") == dsp.PROVEEDOR["modelo"],
                "lectura": ("el brazo publica lo que DEVOLVO el servicio, nunca el pedido re-etiquetado "
                            "(AC4); si el servicio no nombra el modelo, esto es None y se declara")
            }
            break
        except Exception as exc:      # noqa: BLE001 — el brazo traduce a sus dos excepciones y el arnes
                                      # tiene que publicar cualquiera, incluida la que nadie previera
            fila.update({"ok": False, "clase": type(exc).__name__, "mensaje": str(exc)[:300],
                         **kind_por_codigo(str(exc)),
                         "duracion_s": round(time.time() - inicio, 2)})
            registro["intentos"].append(fila)
            registro["autenticacion_real"] = "FALLO"
            registro["error_kind"] = fila["error_kind"]
            registro["clase_excepcion"] = fila["clase"]
            if fila["error_kind"] == "auth":
                break                  # un 401 no se persigue con un segundo envio
    print(json.dumps(registro, ensure_ascii=False, indent=2))
    destino = Path(__file__).with_name("04-deepseek-crudo.json")
    destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if registro.get("autenticacion_real") == "AUTENTICADA" else 1


if __name__ == "__main__":
    sys.exit(main())
