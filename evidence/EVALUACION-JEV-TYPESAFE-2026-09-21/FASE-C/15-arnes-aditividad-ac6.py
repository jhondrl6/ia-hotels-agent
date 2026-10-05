# -*- coding: utf-8 -*-
"""AC6 (FASE-C, 2026-10-04): aditividad del guard REAL con las respuestas persistidas de esta corrida.

Cero inferencias nuevas: no se llama a `triar()` ni a `construir_informe()`, porque esos si enviarían
algo a un proveedor. Se usan las respuestas que ya estan en `respuestas.jsonl` y el guard versionado
`scripts/triage_lesson_relevance.py:guardar_filas_ancladas`, con la misma semantica de filtro que usa
el propio script en su linea 570 (`lo_que_el_filtro_daria = [f for f in ancladas if f["id"] not in
cuestionadas]`).

Lectura honesta que se publica junto al numero: los ids que esta corrida eligio (D-AJUST.4 y
`ninguna-aplica`) NO nombran ninguna de las 25 filas ancladas del plan hermano, asi que la interseccion
`afirmadas ∩ ancladas` es vacia por construccion. Eso hace que el filtro intentara sacar las 25 y que el
guard tenga su trabajo maximo; NO significa que esta corrida haya validado esas 25 filas.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("C:/Users/Jhond/Github/iah-cli")
sys.path.insert(0, str(ROOT))
EVID = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
OUT = EVID / "FASE-C"

from tests.support_resolucion_plan import ruta_plan  # noqa: E402

NOMBRE_PLAN_HERMANO = "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"
LECCIONES = ruta_plan(NOMBRE_PLAN_HERMANO) / "00-lecciones-capitalizadas.md"


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    antes = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(mod)
    finally:
        sys.dont_write_bytecode = antes
    return mod


trl = _cargar("trl_fasec", ROOT / "scripts" / "triage_lesson_relevance.py")

assert trl.GUARD_ADITIVIDAD_ACTIVO is True, "el guard llega apagado: se mediria un mutante"

ancladas = trl.filas_ancladas(LECCIONES)
ids_ancladas = [f["id"] for f in ancladas]

respuestas = [json.loads(l) for l in (OUT / "respuestas.jsonl")
              .read_text(encoding="utf-8").splitlines() if l.strip()]
elecciones_de_la_corrida = sorted({f["propuesta"] for f in respuestas
                                   if isinstance(f.get("propuesta"), str)})
candidatos_de_la_corrida = sorted({i for f in respuestas
                                   for i in (f.get("candidatos_frios") or [])})

afirmadas = [i for i in ids_ancladas if i in set(elecciones_de_la_corrida)]
cuestionadas = [i for i in ids_ancladas if i not in set(afirmadas)]
lo_que_el_filtro_daria = [f for f in ancladas if f["id"] not in cuestionadas]

despues, intentos_filtrados = trl.guardar_filas_ancladas(ancladas, lo_que_el_filtro_daria)
ids_despues = [f["id"] for f in despues]
removidas = [i for i in ids_ancladas if i not in ids_despues]

resultado = {
    "schema": "jev-pilot-aditividad/v1",
    "fase": "FASE-C",
    "guard_real": "scripts/triage_lesson_relevance.py:guardar_filas_ancladas",
    "GUARD_ADITIVIDAD_ACTIVO": trl.GUARD_ADITIVIDAD_ACTIVO,
    "ancladas_desde": str(LECCIONES.relative_to(ROOT)).replace("\\", "/"),
    "sin_nuevas_inferencias": True,
    "respuestas_usadas": "FASE-C/respuestas.jsonl (persistidas en esta corrida)",
    "elecciones_de_la_corrida": elecciones_de_la_corrida,
    "candidatos_de_la_corrida": candidatos_de_la_corrida,
    "anchored_before": len(ancladas),
    "anchored_after": len(despues),
    "removed": removidas,
    "intentos_filtrados": intentos_filtrados,
    "filas_cuestionadas_sin_borrar": cuestionadas,
    "orden_preservado": ids_despues[:len(ids_ancladas)] == ids_ancladas,
    "duplicadas_en_el_regreso": sorted({i for i in ids_despues if ids_despues.count(i) > 1}),
    "criterio_del_informe_del_script": "la misma clausula que ejercita "
                                       "tests/quality_gates/lesson_relevance/test_triage_guard_real_"
                                       "aditividad.py; aqui se llama al guard con las respuestas de "
                                       "esta corrida, no con un emisor falso",
    "lectura_honesta": {
        "interseccion_afirmadas_ancladas": afirmadas,
        "declaracion": "ninguna fila anclada del plan hermano fue elegida por los brazos de esta "
                       "corrida, asi que el filtro habria vaciado §2 y el guard la devolvio intacta. "
                       "`removed` vacio afirma la aditividad del guard; NO afirma que las 25 filas "
                       "sean pertinentes para los pares de eval de este plan",
        "el_removed_vacio_no_seria_verde_por_vacio_porque": "intentos_filtrados trae las 25 filas: el "
                                                            "guard tuvo trabajo maximo sobre la "
                                                            "poblacion"},
}

(OUT / "aditividad.json").write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n",
                                     encoding="utf-8")
print(json.dumps({k2: resultado[k2] for k2 in
                  ("anchored_before", "anchored_after", "removed", "intentos_filtrados",
                   "orden_preservado", "duplicadas_en_el_regreso", "elecciones_de_la_corrida")},
                 ensure_ascii=False, indent=1))
