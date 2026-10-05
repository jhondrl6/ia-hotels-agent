# -*- coding: utf-8 -*-
"""Corrida de eval del brazo Jev (FASE-C, 2026-10-04).

Espejo exacto del corredor antecedente `temp/ola2-2026-10-03/correr_k8.py` (el que midio los techos
1834/139 que hoy estan congelados): misma carga de `TYPESAFE_API_KEY` desde `.env` por nombre, misma
llamada in-process a `evaluate_jev_pilot.run()`, mismos gobernanza de AC12/AC8 dentro del runner.

Lo unico que cambia es lo que la fase cambia: `splits="eval"` (el protocolo ya esta CONGELADA, que es
la condicion dura del maestro 3.4) y `out_dir` dentro de FASE-C. No hay logica nueva aqui: el runner
hace el preflight, la reserva, el ledger y la contabilidad, y la metrica la calcula
`recuperacion_medida` del propio instrumento porque `etiquetas` si se pasa (el CLI no lo expone).

Cero reintentos, timeout 30, techo de 12 llamadas del protocolo congelado, k=8.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import dotenv_values

ROOT = Path("C:/Users/Jhond/Github/iah-cli")
EVID = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
OUT = EVID / "FASE-C"

for clave, valor in dotenv_values(ROOT / ".env").items():
    if clave == "TYPESAFE_API_KEY" and valor and clave not in os.environ:
        os.environ[clave] = valor

spec = importlib.util.spec_from_file_location("ejv_run", ROOT / "scripts" / "evaluate_jev_pilot.py")
ejv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ejv)

resultado = ejv.run(
    muestra=EVID / "muestra.json",
    etiquetas=EVID / "etiquetas.json",
    protocolo=EVID / "protocolo.json",
    indice=ROOT / ".opencode" / "lecciones_index.json",
    preflight=EVID / "FASE-C" / "preflight.json",
    out_dir=OUT,
    proveedor="jev",
    k=8,
    splits="eval",
)
print(json.dumps(resultado, ensure_ascii=False, indent=1))
print("--- LEDGER (una linea por llamada) ---")
ledger = OUT / "ledger.jsonl"
if ledger.exists():
    for linea in ledger.read_text(encoding="utf-8").splitlines():
        fila = json.loads(linea)
        print(json.dumps({k: fila.get(k) for k in
                          ("pair_id", "split", "attempts", "estado", "error_kind",
                           "modelo_solicitado", "modelo_efectivo", "usage_normalized",
                           "candidatos_frios", "leccion_target_en_candidatos", "answers",
                           "request_id", "intentos")},
                         ensure_ascii=False))
print("--- CONSUMO ---")
consumo = OUT / "consumo.json"
if consumo.exists():
    print(consumo.read_text(encoding="utf-8"))
