# -*- coding: utf-8 -*-
"""Corrida de eval del brazo DeepSeek (FASE-C, 2026-10-04), por la costura.

El runner la niega expresamente (`run --proveedor deepseek` -> NEGADO) y el mandato manda NO migrar
ese brazo al runner, asi que se despacha por la puerta: `scripts/decision_client.py:evaluar` con
`IAH_DECISION_PROVIDER=deepseek-comparador`, que carga `scripts/proveedores/deepseek.py`.

Nada de conteo nace aqui. Lo que este arnes si hace, y solo por eso existe:
  * proyectar la entrada con los instrumentos congelados: `recuperacion_fria` + `preguntas_para_par`
    del propio `evaluate_jev_pilot.py`, o sea los MISMOS candidatos y la MISMA pregunta que vio Jev;
  * gobernar AC8 con `reservar_presupuesto` del instrumento antes de cada envio, contra la cuenta de
    la etapa que escribio el runner (`consumo.json` de FASE-C);
  * llenar el ledger por llamada con `nuevo_ledger` / `registrar_intento` / `normalizar_usage` /
    `error_kind_de`, que son las funciones testadas del contrato;
  * sumar la cuenta de etapa con la misma aritmetica que suma `run` (libro de campo, no metrica).

Primer ejercicio REAL del camino emparejado (`_emparejar_respuestas`) sobre ids de par: la cura del
id recortado del 2026-10-04 no se habia vuelto a probar con trafico.

Cero reintentos. Credencial leida de `.env` por nombre y jamas impresa.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import dotenv_values

ROOT = Path("C:/Users/Jhond/Github/iah-cli")
EVID = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
OUT = EVID / "FASE-C"

CLAVE_DS = "DEEPSEEK_API_KEY"

_entorno = dotenv_values(ROOT / ".env")
os.environ[CLAVE_DS] = os.environ.get(CLAVE_DS) or (_entorno.get(CLAVE_DS) or "")
os.environ["IAH_DECISION_PROVIDER"] = "deepseek-comparador"
os.environ["IAH_DECISION_PROVIDERS_DIR"] = str(ROOT / "scripts" / "proveedores")


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


ejv = _cargar("ejv_fasec", ROOT / "scripts" / "evaluate_jev_pilot.py")
dc = _cargar("dc_fasec", ROOT / "scripts" / "decision_client.py")

muestra = json.loads((EVID / "muestra.json").read_text(encoding="utf-8"))
protocolo = json.loads((EVID / "protocolo.json").read_text(encoding="utf-8"))
lecciones = json.loads((ROOT / ".opencode" / "lecciones_index.json")
                       .read_text(encoding="utf-8")).get("lecciones") or []

validacion = ejv.validar_protocolo(protocolo)
k = validacion["k"]
limites = ejv.limites_desde_protocolo(protocolo)
cuenta = ejv._estado_cuenta(OUT)
rubrica = protocolo.get("rubrica")

pares_eval = [p for p in muestra.get("pairs", []) if p.get("split") == "eval"]
modelo_pedido = "deepseek-chat"

salida = {"brazo": "deepseek", "k": k, "modelo_pedido": modelo_pedido,
          "timeout_s": limites["timeout_s"], "max_reintentos": limites["max_reintentos"],
          "cuenta_al_entrar": dict(cuenta),
          "resoluciones": [{"clave": CLAVE_DS, "presente": bool(os.environ.get(CLAVE_DS))}],
          "filas": [], "cuenta_al_salir": None}

for par in pares_eval:
    fria = ejv.recuperacion_fria(par["input_fragment"], lecciones, k)
    questions = ejv.preguntas_para_par(par["pair_id"], fria["candidatos"], rubrica)
    q = questions[par["pair_id"]]
    state = {"consulta": par["input_fragment"], "candidatos": fria["candidatos"]}

    reserva = ejv.reservar_presupuesto(cuenta, limites)
    fila = ejv.nuevo_ledger("deepseek", modelo_pedido)
    fila["pair_id"] = par["pair_id"]
    fila["split"] = par.get("split")
    fila["candidatos_frios"] = [c["id"] for c in fria["candidatos"]]
    fila["leccion_target_en_candidatos"] = par["lesson_id"] in fila["candidatos_frios"]
    fila["n_preguntas"] = 1
    fila["tipo_pregunta"] = q["type"]
    fila["opciones"] = list(q["criteria"].keys())
    if not reserva["reservado"]:
        fila["estado"] = "NO-EJERCITADO"
        fila["motivos"] = reserva["motivos"]
        salida["filas"].append(fila)
        continue
    fila["reserva_previa"] = {"reservado": True, "llamadas_restantes": reserva["llamadas_restantes"]}

    inicio = time.monotonic()
    try:
        resultado = dc.evaluar(str(state), [dc.Pregunta(par["pair_id"], "choice",
                                                        q["instructions"],
                                                        opciones=list(q["criteria"].keys()))])
    except Exception as exc:
        duracion_ms = round((time.monotonic() - inicio) * 1000.0, 3)
        ejv.registrar_intento(fila, resultado="fallo", excepcion=exc, duracion_ms=duracion_ms)
        # `error_kind_de` clasifica por nombres del SDK de TypeSafe: para una excepcion del brazo
        # DeepSeek da `desconocido`, que es la lectura honesta del instrumento ajeno. Se publica
        # tambien el codigo HTTP que el brazo conserva en su mensaje, sin re-etiquetarlo.
        fila["error_kind_del_instrumento"] = ejv.error_kind_de(exc)
        fila["lectura_local"] = {"clase": type(exc).__name__, "mensaje": str(exc)[:400],
                                 "credencial_en_el_mensaje": False}
    else:
        duracion_ms = resultado.elapsed_ms
        crudo_usage = {"input_tokens": (resultado.usage or {}).get("input_tokens"),
                       "output_tokens": (resultado.usage or {}).get("output_tokens")}
        ejv.registrar_intento(fila, resultado="exito", usage=crudo_usage,
                              modelo_efectivo=resultado.modelo, duracion_ms=duracion_ms)
        fila["answers"] = {r.pregunta_id: r.to_dict() for r in resultado.respuestas}
        fila["request_id"] = resultado.request_id
        fila["proveedor_resuelto"] = resultado.proveedor
        fila["provider_status"] = resultado.provider_status
        fila["modelo_pedido_por_la_costura"] = resultado.model_requested
        fila["alias_movil"] = True
    cuenta["llamadas_usadas"] += 1
    cuenta["intentos"] += fila["attempts"]
    uso = fila["usage_normalized"]
    if uso.get("input_tokens") is not None:
        cuenta["tokens_in_max"] = max(cuenta.get("tokens_in_max") or 0, uso["input_tokens"])
    if uso.get("output_tokens") is not None:
        cuenta["tokens_out_max"] = max(cuenta.get("tokens_out_max") or 0, uso["output_tokens"])
    if uso.get("estado") != "observado":
        cuenta.setdefault("usage_estados", []).append(uso.get("estado"))
    salida["filas"].append(fila)

salida["cuenta_al_salir"] = dict(cuenta)
salida["hora_cierre_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

(OUT / "ledger-deepseek.jsonl").write_text(
    "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in salida["filas"]), encoding="utf-8")
(OUT / "registro_deepseek.json").write_text(
    json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(salida, ensure_ascii=False, indent=1))
