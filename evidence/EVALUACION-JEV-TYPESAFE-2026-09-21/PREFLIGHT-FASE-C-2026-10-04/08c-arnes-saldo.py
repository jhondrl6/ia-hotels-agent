"""ARNES del Cierre B (SESION 2.5, 2026-10-04): UNA llamada autenticada de lectura de saldo.

Autorizacion literal A2: una (1) llamada de lectura contra la via que la API publica para
`cuota_o_saldo`, con CERO reintentos. La via se nombro por documentacion (see `via.fuente` en el
crudo), no por adivinanza: `GET https://api.deepseek.com/user/balance` con `Accept: application/json`.

El brazo `scripts/proveedores/deepseek.py` no sirve para esto: su unico camino de red es el POST de
`chat/completions`, y en esa ruta el request no trae pregunta alguna que ejercite el mapper. Pedir
saldo por el brazo habria sido un segundo envio de chat (V5) o una modificacion del brazo fuera de
la cura (D3). Por eso el arnes habla con `urllib` a una sola mano.

Regla de la casa (`preflight.json:29` / V6): se registra presencia por nombre y el resultado de
autenticar, jamas la clave, su longitud o un prefijo. Antes de escribir cualquier crudo se pasa la
clave por un barrido de subcadena y se afirma que no esta.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = "https://api.deepseek.com/user/balance"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def cargar_env() -> None:
    """`.env` al entorno del proceso sin imprimir valores."""
    ruta = ROOT / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8", errors="replace").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        os.environ.setdefault(clave.strip(), valor.strip())


def sin_clave(texto: str, clave: str) -> str:
    """Barrido defensivo: si la clave apareciera en una respuesta, no sale hacia el crudo."""
    return texto.replace(clave, "***REDACTADO-VALOR-DE-CLAVE***") if clave else texto


def main() -> int:
    cargar_env()
    clave = os.environ.get("DEEPSEEK_API_KEY", "")
    informe: dict = {
        "arnes": "p3_saldo_deepseek.py",
        "autorizacion": "A2: una (1) llamada autenticada de lectura, cero reintentos",
        "via": {"metodo": "GET", "url": URL, "acepta": "application/json",
                "fuente_de_la_via": "documentacion publica del endpoint de saldo de DeepSeek "
                                    "(la pagina `api/get-user-balance`); el sitio de docs no resolvio "
                                    "desde esta maquina (curl HTTP=000) y la via se copio de un espejo "
                                    "de terceros (CodexBar/docs/deepseek.md): por eso el crudo registra "
                                    "el riesgo de un 404 como medida, no como sorpresa"},
        "credencial": {"env_var": "DEEPSEEK_API_KEY", "presente": bool(clave),
                       "motivo": "presencia por nombre y bool: el valor, su longitud y cualquier "
                                 "prefijo quedan fuera (V6)"},
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    if not clave:
        informe["resultado"] = "CREDENCIAL_AUSENTE"
        informe["envios"] = 0
        print(json.dumps(informe, ensure_ascii=False, indent=1))
        return 2

    datos = None
    req = urllib.request.Request(URL, method="GET", headers={
        "Authorization": "Bearer " + clave, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            cuerpo = resp.read().decode("utf-8", errors="replace")
            informe["http_status"] = resp.status
            informe["envios"] = 1
            informe["reintentos"] = 0
            try:
                datos = json.loads(cuerpo)
            except json.JSONDecodeError as exc:
                informe["respuesta_parseada"] = "NO-ES-JSON"
                informe["motivo_parseo"] = str(exc)[:200]
                informe["crudo_recortado"] = sin_clave(cuerpo, clave)[:600]
    except urllib.error.HTTPError as exc:
        informe["envios"] = 1
        informe["reintentos"] = 0
        informe["http_status"] = exc.code
        informe["respuesta_parseada"] = "HTTP-ERROR"
        try:
            informe["crudo_recortado"] = sin_clave(exc.read().decode("utf-8", "replace"), clave)[:600]
        except Exception:
            informe["crudo_recortado"] = "(cuerpo no legible)"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        informe["envios"] = 1
        informe["reintentos"] = 0
        informe["respuesta_parseada"] = "FALLO_DE_TRANSPORTE"
        informe["motivo_transporte"] = sin_clave(str(exc), clave)[:300]
    else:
        if isinstance(datos, dict):
            informe["respuestas_claves"] = sorted(datos)
            informe["is_available"] = datos.get("is_available")
            infos = datos.get("balance_infos") or []
            informe["balance_infos"] = [
                {"currency": i.get("currency"), "total_balance": i.get("total_balance"),
                 "granted_balance": i.get("granted_balance"),
                 "topped_up_balance": i.get("topped_up_balance")}
                for i in infos if isinstance(i, dict)]
            extras = {k: v for k, v in datos.items()
                      if k not in ("is_available", "balance_infos")}
            if extras:
                informe["otros_campos_del_servicio"] = sin_clave(
                    json.dumps(extras, ensure_ascii=False, default=str), clave)[:400]
    texto = json.dumps(informe, ensure_ascii=False, indent=1)
    assert clave not in texto, "la clave aparecio en el crudo: no se escribe"
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        ROOT / "temp" / "sesion25-2026-10-04" / "05-saldo-crudo.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(texto + "\n", encoding="utf-8")
    print(texto)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
