# -*- coding: utf-8 -*-
"""Ensayo SIN RED de la proyeccion DeepSeek (FASE-C, 2026-10-04).

Gastar un envio de eval en un defecto de marshaling seria peor que un FALLIDO: consumiria presupuesto
de la etapa y dejaria un par sin respuesta. Este arnes no abre sockets:
  * `estado_proveedor()` resuelve el brazo sin llamarlo;
  * `dc.evaluar(..., _payload=falso)` es el parametro que la puerta documenta para el contract test
    de forma, o sea ejercita `validar_payload` + `a_respuestas_tipadas` sobre la MISMA pregunta que
    se construira en la corrida, con un payload fabricado aqui.
Credenciales: ni se leen ni se imprimen. Red: cero.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("C:/Users/Jhond/Github/iah-cli")
EVID = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
os.environ["IAH_DECISION_PROVIDER"] = "deepseek-comparador"
os.environ["IAH_DECISION_PROVIDERS_DIR"] = str(ROOT / "scripts" / "proveedores")
os.environ["DEEPSEEK_API_KEY"] = "SENTINELA-NO-REAL-para-el-ensayo"


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


ejv = _cargar("ejv_ensayo", ROOT / "scripts" / "evaluate_jev_pilot.py")
dc = _cargar("dc_ensayo", ROOT / "scripts" / "decision_client.py")

sintaxis = {}
for f in ["correr_deepseek_eval.py", "correr_jev_eval.py", "capa_fria.py"]:
    ruta = ROOT / "temp" / "fasec-2026-10-04" / f
    ast.parse(ruta.read_text(encoding="utf-8"))
    sintaxis[f] = "AST-OK"

muestra = json.loads((EVID / "muestra.json").read_text(encoding="utf-8"))
protocolo = json.loads((EVID / "protocolo.json").read_text(encoding="utf-8"))
lecciones = json.loads((ROOT / ".opencode" / "lecciones_index.json")
                       .read_text(encoding="utf-8")).get("lecciones") or []
k = ejv.validar_protocolo(protocolo)["k"]
rubrica = protocolo.get("rubrica")

estado = dc.estado_proveedor()
salida = {"sintaxis_de_los_arneses": sintaxis,
          "estado_proveedor_sin_llamar": {k2: estado.get(k2) for k2 in
                                          ("provider_status", "proveedor", "archivo", "credencial",
                                           "declara", "motivo_clase")},
          "enviado": False, "pares": []}

for par in [p for p in muestra["pairs"] if p["split"] == "eval"]:
    fria = ejv.recuperacion_fria(par["input_fragment"], lecciones, k)
    q = ejv.preguntas_para_par(par["pair_id"], fria["candidatos"], rubrica)[par["pair_id"]]
    ids = list(q["criteria"].keys())
    pregunta = dc.Pregunta(par["pair_id"], "choice", q["instructions"], opciones=ids)
    fila = {"pair_id": par["pair_id"], "n_opciones": len(ids),
            "opciones": ids, "validar_pregunta": pregunta.validar(),
            "instrucciones_len": len(q["instructions"])}
    falso = {"modelo": "deepseek-flash",
             "respuestas": [{"pregunta_id": par["pair_id"], "tipo": "choice",
                             "eleccion": par["lesson_id"],
                             "probabilidades": {o: (1.0 - 0.08 * (len(ids) - 1)) if o == par["lesson_id"]
                                                else 0.08 for o in ids},
                             "confidence": 0.9}],
             "usage": {"input_tokens": 1700, "output_tokens": 120},
             "request_id": "ensayo-sin-red"}
    fila["suma_probabilidades_del_falso"] = round(sum(
        falso["respuestas"][0]["probabilidades"].values()), 6)
    try:
        res = dc.evaluar(str({"consulta": par["input_fragment"],
                              "candidatos": fria["candidatos"]}), [pregunta], _payload=falso)
    except Exception as exc:
        fila["forma_aceptada"] = False
        fila["excepcion"] = f"{type(exc).__name__}: {str(exc)[:300]}"
        fila["motivos"] = list(getattr(exc, "motivos", []))
    else:
        fila["forma_aceptada"] = True
        fila["answers_proyectadas"] = {r.pregunta_id: r.to_dict() for r in res.respuestas}
        fila["usage_proyectado"] = res.usage
        fila["modelo_efectivo_proyectado"] = res.modelo
        fila["request_id_proyectado"] = res.request_id
        n = ejv.normalizar_usage(res.usage)
        fila["usage_normalized_del_instrumento"] = n
    salida["pares"].append(fila)

print(json.dumps(salida, ensure_ascii=False, indent=1))
