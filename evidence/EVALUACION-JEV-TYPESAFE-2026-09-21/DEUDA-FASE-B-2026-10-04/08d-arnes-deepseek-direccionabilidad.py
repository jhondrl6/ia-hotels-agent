"""Sonda de direccionabilidad (ampliacion de la opcion (b), 2026-10-04): ¿es `deepseek-flash` un nombre
que el servicio atienda, o solo una etiqueta de routing que echo en `model`?

Lo que midio la tanda anterior (`09-deepseek-estabilidad-crudo.json`): pidiendo `deepseek-chat` el servicio
echo `deepseek-flash` en 3 de 3 envios, y pidiendo `deepseek-flash` explicitamente con `max_tokens=64` el
servicio contesto 200 pero con `choices[0].message.content` vacio y `finish_reason=length`. Con ese par de
datos no se puede afirmar que el nombre sea direccionable: un 200 con contenido vacio y recortado por el
tope es compatible con dos cosas distintas (el modelo existe y el tope no le alcanzo, o el alias cae en una
ruta que no produce). Esta sonda levanta el tope a 254 tokens y captura el envelope crudo (`model`, `usage`,
`finish_reason`, `content`), que la firma de `evaluar` no devuelve cuando el content viene vacio.

Un envio. Cero reintentos. No se imprime la clave ni el header Authorization ni `.env`.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
MAX_TOKENS = 254
ESTADO = "FASE-B del piloto JEV cerrada el 2026-10-04."
ENUNCIADO = ("¿La siguiente frase afirma algo verificable? «El piloto JEV cerro FASE-B documentalmente "
             "el 2026-10-04.»")


def _cargar(nombre: str, ruta: Path):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def clave_desde_env(nombre: str):
    for linea in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
        s = linea.strip()
        if s.startswith(f"{nombre}="):
            return s.split("=", 1)[1].strip().strip('"').strip("'") or None
    return None


def pedir(url: str, cuerpo: dict, clave: str, timeout: float = 45.0) -> dict:
    req = urllib.request.Request(url, data=json.dumps(cuerpo).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + clave})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"http": resp.status, "crudo": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as exc:
        return {"http": exc.code, "error": exc.read().decode("utf-8", "replace")[:400]}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"http": None, "error": f"conexion: {exc}"}


def resumir(resp: dict) -> dict:
    crudo = resp.get("crudo") or {}
    opciones = crudo.get("choices") or []
    primera = opciones[0] if opciones else {}
    content = ((primera.get("message") or {}).get("content"))
    salida = {"http": resp.get("http"), "model_devuelto_por_el_servicio": crudo.get("model"),
              "usage": crudo.get("usage"), "finish_reason": primera.get("finish_reason"),
              "content_len": len(content) if isinstance(content, str) else None,
              "content_head": (content[:200] if isinstance(content, str) else None),
              "razon_de_la_forma": None}
    if isinstance(content, str) and content.strip():
        try:
            datos = json.loads(content)
            respuestas = datos.get("respuestas") if isinstance(datos, dict) else None
            salida["json_claves"] = sorted(datos) if isinstance(datos, dict) else None
            salida["pregunta_ids_devueltos"] = [r.get("pregunta_id") for r in (respuestas or [])
                                                if isinstance(r, dict)]
        except json.JSONDecodeError as exc:
            salida["razon_de_la_forma"] = f"content no es JSON: {exc}"
    if "error" in resp:
        salida["error"] = resp["error"]
    return salida


def main() -> int:
    dsp = _cargar("dsp_dir", ROOT / "scripts" / "proveedores" / "deepseek.py")
    dc = _cargar("dc_dir", ROOT / "scripts" / "decision_client.py")
    clave = clave_desde_env("DEEPSEEK_API_KEY")
    registro = {"sonda": "deepseek-flash-direccionable-2026-10-04",
                "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "instrumento": "python temp/deuda-2026-10-04/p4c_deepseek_flash_direccionable.py",
                "motivo": "la tanda anterior dio 200 con content vacio y finish_reason=length pidiendo "
                          "`deepseek-flash`: con ese dato no se decide si el nombre es direccionable",
                "endpoint": dsp.PROVEEDOR["endpoint"], "preguntas": 1, "tipo": "noul",
                "temperature": 0, "max_tokens": MAX_TOKENS,
                "credencial": {"variable": "DEEPSEEK_API_KEY", "presente_en_env": bool(clave)},
                "envios": []}
    if not clave:
        registro["resultado"] = "NO-INTENTADA"
        print(json.dumps(registro, ensure_ascii=False, indent=2))
        return 2

    preguntas = [dc.Pregunta("sonda:1", "noul", ENUNCIADO)]
    instrucciones = dsp._instrucciones(preguntas) + "\n\nCONTEXTO:\n" + ESTADO

    for nombre in ("deepseek-flash", "deepseek-chat"):     # el par control/efecto en la MISMA corrida
        cuerpo = {"model": nombre, "messages": [{"role": "user", "content": instrucciones}],
                  "temperature": 0, "max_tokens": MAX_TOKENS}
        fila = {"modelo_pedido": nombre, "motivo_de_pedirlo": (
            "decidir si el echo del servicio es un nombre que el servicio atiende"
            if nombre == "deepseek-flash" else
            "control en el MISMO cuerpo y con el MISMO tope: si aqui el content sale y alla no, la "
            "diferencia es del modelo pedido y no del presupuesto")}
        fila.update(resumir(pedir(dsp.PROVEEDOR["endpoint"], cuerpo, clave)))
        registro["envios"].append(fila)

    flash, chat = registro["envios"][0], registro["envios"][1]
    registro["lectura"] = {
        "eco_estable_de_deepseek_chat": flash.get("model_devuelto_por_el_servicio") == chat.get(
            "model_devuelto_por_el_servicio"),
        "model_devuelto_al_pedir_flash": flash.get("model_devuelto_por_el_servicio"),
        "model_devuelto_al_pedir_chat": chat.get("model_devuelto_por_el_servicio"),
        "content_flash_len": flash.get("content_len"), "content_chat_len": chat.get("content_len"),
        "finish_flash": flash.get("finish_reason"), "finish_chat": chat.get("finish_reason"),
    }
    print(json.dumps(registro, ensure_ascii=False, indent=2))
    destino = Path(__file__).with_name("10-deepseek-flash-direccionable-crudo.json")
    destino.write_text(json.dumps(registro, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
