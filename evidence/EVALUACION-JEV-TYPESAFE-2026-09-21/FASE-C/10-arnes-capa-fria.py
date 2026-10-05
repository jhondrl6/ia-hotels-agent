"""Arnies de la capa fria (FASE-C, 2026-10-04).

NO implementa metrica nueva: importa `recuperacion_fria` de `scripts/evaluate_jev_pilot.py` (el
instrumento versionado y testado) y la llama sobre los pares `split == eval` de la muestra
CONGELADA, con k = 8 leido del protocolo. Cero red, cero logica de conteo propia.

Comando:
    venv/Scripts/python.exe temp/fasec-2026-10-04/capa_fria.py
Salida: stdout JSON (se transcribe a evidence/.../FASE-C/ como crudo).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


inst = _cargar("inst_jev_pilot", ROOT / "scripts" / "evaluate_jev_pilot.py")

muestra = json.loads((PLAN / "muestra.json").read_text(encoding="utf-8"))
etiquetas = json.loads((PLAN / "etiquetas.json").read_text(encoding="utf-8"))
protocolo = json.loads((PLAN / "protocolo.json").read_text(encoding="utf-8"))
lecciones = json.loads((ROOT / ".opencode" / "lecciones_index.json")
                       .read_text(encoding="utf-8")).get("lecciones") or []

validacion = inst.validar_protocolo(protocolo)
k = validacion["k"]

por_par_etiqueta = {l["pair_id"]: l for l in etiquetas.get("labels", [])}
salida = {
    "instrumento": "scripts/evaluate_jev_pilot.py::recuperacion_fria",
    "k": k,
    "k_desde": "validar_protocolo(protocolo.json)['k'] - no se fija a mano en este arnes",
    "protocolo_status": validacion["protocolo_status"],
    "protocolo_check": validacion["check_status"],
    "poblacion_lecciones": len(lecciones),
    "splits": {},
    "pares": [],
}

for par in muestra.get("pairs", []):
    fria = inst.recuperacion_fria(par["input_fragment"], lecciones, k)
    ids = [c["id"] for c in fria["candidatos"]]
    etiqueta = por_par_etiqueta.get(par["pair_id"], {})
    fila = {
        "pair_id": par["pair_id"],
        "split": par.get("split"),
        "lesson_id_target": par["lesson_id"],
        "input_fragment": par["input_fragment"],
        "candidatos_frios": ids,
        "n_candidatos": len(ids),
        "leccion_target_en_candidatos": par["lesson_id"] in ids,
        "puesto_del_target": (ids.index(par["lesson_id"]) + 1)
        if par["lesson_id"] in ids else None,
        "poblacion": fria["poblacion"],
        "desempate": fria["desempate"],
        "etiqueta_humana": etiqueta.get("label"),
        "importancia_humana": etiqueta.get("importance"),
    }
    salida["pares"].append(fila)
    salida["splits"].setdefault(par.get("split"), []).append(par["pair_id"])

# La metrica 1 del brazo 'capa fria' se calcula con el instrumento, no con este arnes:
# `recuperacion_medida` recibe el ledger en la forma que escribe el runner (una fila por par con
# `pair_id` y `leccion_target_en_candidatos`), asi que se le construye esa proyeccion y se le llama.
for split, pair_ids in salida["splits"].items():
    filas_ledger = [{"pair_id": pid,
                     "leccion_target_en_candidatos": next(
                         p["leccion_target_en_candidatos"] for p in salida["pares"]
                         if p["pair_id"] == pid)} for pid in pair_ids]
    salida.setdefault("recuperacion_por_split", {})[split] = inst.recuperacion_medida(
        muestra, etiquetas, filas_ledger)

print(json.dumps(salida, ensure_ascii=False, indent=2))
