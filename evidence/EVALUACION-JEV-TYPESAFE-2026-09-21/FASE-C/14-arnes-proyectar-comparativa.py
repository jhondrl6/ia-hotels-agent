# -*- coding: utf-8 -*-
"""Proyeccion mecanica de los tres brazos (FASE-C, 2026-10-04), sin red y sin logica de conteo nueva.

Salidas:
  * FASE-C/respuestas.jsonl  - una fila por (par, brazo) leida de los registros persistidos de la
    etapa: `ledger.jsonl` (lo escribe el runner) y `ledger-deepseek.jsonl` (lo escribe el arnes de la
    costura con las funciones del instrumento). Capa fria: la proyeccion de `recuperacion_fria`.
  * FASE-C/informe_comparativa.json - los cuatro cocientes por brazo.

Regla que gobierna este archivo: NINGUN numero publicado nace aqui. La unica metrica que se calcula
es `recuperacion_medida`, funcion testada del instrumento versionado, a la que se le pasan los
registros tal como quedaron en disco. Los otros tres cocientes se publican en null con su motivo de
no-estimacion y su cambio requerido: `metrics()` existe pero nadie construye sus conteos desde
respuestas reales (medido: el unico productor de `prec_num`/`rec_num` es un fixture de test).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("C:/Users/Jhond/Github/iah-cli")
EVID = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21"
OUT = EVID / "FASE-C"


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


ejv = _cargar("ejv_proyecta", ROOT / "scripts" / "evaluate_jev_pilot.py")

muestra = json.loads((EVID / "muestra.json").read_text(encoding="utf-8"))
etiquetas = json.loads((EVID / "etiquetas.json").read_text(encoding="utf-8"))
protocolo = json.loads((EVID / "protocolo.json").read_text(encoding="utf-8"))
lecciones = json.loads((ROOT / ".opencode" / "lecciones_index.json")
                       .read_text(encoding="utf-8")).get("lecciones") or []
k = ejv.validar_protocolo(protocolo)["k"]


def _ledger(nombre):
    ruta = OUT / nombre
    if not ruta.exists():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


jev_filas = _ledger("ledger.jsonl")
ds_filas = _ledger("ledger-deepseek.jsonl")
registro_ds = json.loads((OUT / "registro_deepseek.json").read_text(encoding="utf-8"))
consumo_jev = json.loads((OUT / "consumo.json").read_text(encoding="utf-8"))
run_resumen = json.loads((OUT / "run_resumen.json").read_text(encoding="utf-8"))

pares_eval = [p for p in muestra["pairs"] if p.get("split") == "eval"]
por_par = {p["pair_id"]: p for p in pares_eval}
etiq = {l["pair_id"]: l for l in etiquetas["labels"]}


def _respuesta(fila):
    """Lectura, no conteo: la eleccion que el brazo publico para ese par, o null si no hubo."""
    ans = (fila or {}).get("answers") or {}
    d = ans.get(fila.get("pair_id")) or {}
    return d.get("eleccion") or d.get("choice") or None


filas_respuestas = []
for par in pares_eval:
    pid = par["pair_id"]
    fria = ejv.recuperacion_fria(par["input_fragment"], lecciones, k)
    frio_ids = [c["id"] for c in fria["candidatos"]]
    comun = {"pair_id": pid, "split": "eval", "lesson_id_target": par["lesson_id"],
             "etiqueta": etiq[pid]["label"], "importancia": etiq[pid]["importance"],
             "candidatos_frios": frio_ids,
             "leccion_target_en_candidatos": par["lesson_id"] in frio_ids}
    capa = dict(comun)
    capa.update({"brazo": "capa_fria", "modelo_pedido": None, "modelo_efectivo": None,
                 "propuesta": frio_ids, "abstencion": None, "attempts": 0,
                 "error_kind": None, "duracion_ms": None, "usage_normalized": None,
                 "request_id": None,
                 "nota": "la capa fria no propone una eleccion: entrega el ranking k=8; es la misma "
                         "para los tres brazos por construccion (mismo conjunto elegible)"})
    filas_respuestas.append(capa)

    for brazo, filas in (("jev", jev_filas), ("deepseek", ds_filas)):
        f = next((x for x in filas if x.get("pair_id") == pid), None)
        g = dict(comun)
        if f is None:
            g.update({"brazo": brazo, "modelo_pedido": None, "modelo_efectivo": None,
                      "propuesta": None, "abstencion": None, "attempts": None,
                      "error_kind": "sin_fila_en_el_ledger", "duracion_ms": None,
                      "usage_normalized": None, "request_id": None})
        else:
            eleccion = _respuesta(f)
            g.update({"brazo": brazo,
                      "modelo_pedido": f.get("modelo_solicitado"),
                      "modelo_efectivo": f.get("modelo_efectivo"),
                      "propuesta": eleccion,
                      # `abstencion` es null cuando la fila no trajo ninguna eleccion: una llamada
                      # que fallo por conexion no es una eleccion no-abstencion, es no-evaluable.
                      "abstencion": (None if eleccion is None
                                     else eleccion == ejv.ETIQUETA_DE_NINGUNA),
                      "attempts": f.get("attempts"),
                      "estado_fila": f.get("estado"),
                      "error_kind": f.get("error_kind"),
                      "duracion_ms": [i.get("duracion_ms") for i in f.get("intentos") or []],
                      "usage_normalized": f.get("usage_normalized"),
                      "request_id": f.get("request_id"),
                      "intentos": f.get("intentos")})
        filas_respuestas.append(g)

(OUT / "respuestas.jsonl").write_text(
    "".join(json.dumps(f, ensure_ascii=False) + "\n" for f in filas_respuestas),
    encoding="utf-8")

BRAZOS = ("capa_fria", "deepseek", "jev")
ledgers = {"capa_fria": [{"pair_id": p["pair_id"],
                          "leccion_target_en_candidatos": p["lesson_id"] in
                          [c["id"] for c in ejv.recuperacion_fria(
                              p["input_fragment"], lecciones, k)["candidatos"]]}
                         for p in pares_eval],
           "deepseek": ds_filas, "jev": jev_filas}

rec = {b: ejv.recuperacion_medida(muestra, etiquetas, ledgers[b]) for b in BRAZOS}

no_estimado = {
    "value": None, "numerator": None, "denominator": None,
    "motivo": "instrumento_no_implementado",
    "por_que_no_se_rellena": "publisharlo a mano seria un numero nacido de logica nueva sin test "
                             "(AC10). `metrics()` envuelve conteos que nadie construye desde "
                             "respuestas reales.",
    "prueba_de_la_ausencia": "grep -rn 'prec_num' scripts/ -> solo evaluate_jev_pilot.py:191-192 "
                             "(los LEE); el unico que los alimenta es un fixture: "
                             "tests/quality_gates/jev_pilot/test_jev_pilot_offline.py:113-115",
}

informe = {
    "schema": "jev-pilot-informe-comparativa/v1",
    "fase": "FASE-C",
    "plan": "EVALUACION-JEV-TYPESAFE-2026-09-21",
    "generado_sin_red": True,
    "regenerable_desde": ["FASE-C/ledger.jsonl", "FASE-C/ledger-deepseek.jsonl",
                          "FASE-C/registro_deepseek.json", "FASE-C/respuestas.jsonl",
                          ".opencode/lecciones_index.json",
                          "evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/{muestra,etiquetas,"
                          "protocolo}.json"],
    "comando": "venv/Scripts/python.exe temp/fasec-2026-10-04/proyectar_comparativa.py",
    "protocolo": {"status": protocolo.get("status"), "congelado": protocolo.get("congelado"),
                  "k": k, "sufficiency": protocolo["criterios_adopcion"]["suficiencia_minima"],
                  "cobertura_min": protocolo["criterios_adopcion"]["cobertura_min"],
                  "margen_vs_deepseek": protocolo["criterios_adopcion"]["margen_vs_deepseek"],
                  "latencia_max_ms": protocolo["criterios_adopcion"]["latencia_max"],
                  "tratamiento_abstenciones":
                      protocolo["criterios_adopcion"]["tratamiento_abstenciones"]},
    "conjunto_elegible": {"denominador_pares_total": muestra["counts"]["total"],
                          "pares_en_eval": [p["pair_id"] for p in pares_eval],
                          "pertinentes_importantes_en_eval": rec["jev"]["elegibles"],
                          "muestra_chica_declarada": True,
                          "nota": "los 4 pares estan congelados y el plan prohibe re-etiquetarlos; "
                                  "2 pertinentes-importantes caen en eval, y ese es el denominador "
                                  "de la metrica 1"},
    "por_brazo": {b: {"recuperacion": rec[b],
                      "precision_entre_propuestas": dict(no_estimado),
                      "recall_importante_candidatos": dict(no_estimado),
                      "extremo_a_extremo": dict(no_estimado)} for b in BRAZOS},
    "abstenciones_denominador_aparte": {
        "criterio_congelado": "contadas como fallo de recuperacion, no como insuficiente; "
                              "publicadas en denominador aparte",
        "recuento_publicado_como_hecho_del_registro_no_como_cociente": {
            b: [{"pair_id": f["pair_id"], "propuesta": f.get("propuesta"),
                 "abstencion": f.get("abstencion")}
                for f in filas_respuestas if f["brazo"] == b and f["brazo"] != "capa_fria"]
            for b in ("jev", "deepseek")},
        "cociente_de_abstencion": dict(no_estimado),
    },
    "costo_y_cuentas_tres_monedas": {
        "usage_observed": {b: [f.get("usage_normalized") for f in filas_respuestas
                               if f["brazo"] == b and f["brazo"] != "capa_fria"] for b in BRAZOS},
        "cost_calculated": None,
        "cost_billed": None,
        "motivo_coste": "usd sigue null en el protocolo congelado, fuera de gobernanza por decision "
                        "del operador del 2026-10-03: no hay decision de coste sin coste en "
                        "gobernanza (COSTE-NO-PAGADO queda bloqueado)",
        "cuenta_de_etapa": {
            "jev_desde_consumo_json_del_runner": consumo_jev,
            "etapa_completa_desde_registro_deepseek": registro_ds["cuenta_al_salir"],
            "techo_llamadas": protocolo["limites_gasto"]["llamadas"],
            "techo_tokens_in_congelado": protocolo["limites_gasto"]["tokens_in"],
            "techo_tokens_out_congelado": protocolo["limites_gasto"]["tokens_out"],
            "token_out_max_observado_en_la_etapa": max(
                consumo_jev["tokens_out_max"], registro_ds["cuenta_al_salir"]["tokens_out_max"]),
            "token_in_max_observado_en_la_etapa": max(
                consumo_jev["tokens_in_max"], registro_ds["cuenta_al_salir"]["tokens_in_max"]),
            "regla_del_max": "max() sobre las dos cuentas de la etapa, que es la misma regla que "
                             "aplica `run` en scripts/evaluate_jev_pilot.py:676-678; no es un "
                             "conteo nuevo ni un promedio",
            "envios_de_inferencia_de_la_sesion": 4,
            "envios_de_conectividad_de_la_sesion": 0},
        "latencia_ms_por_intento": {
            b: [x for f in filas_respuestas if f["brazo"] == b
                for x in (f.get("duracion_ms") or [])] for b in ("jev", "deepseek")},
        "attempts_por_fila": {
            b: [{"pair_id": f["pair_id"], "attempts": f.get("attempts")}
                for f in filas_respuestas if f["brazo"] == b and f["brazo"] != "capa_fria"]
            for b in ("jev", "deepseek")}},
    "hallazgos": [
        {"id": "H1",
         "hallazgo": "la recuperacion es identica en los tres brazos por construccion "
                     f"({rec['jev']['numerator']}/{rec['jev']['denominator']} = "
                     f"{rec['jev']['value']}): la capa fria es comun, asi que la metrica 1 NO "
                     "diferencia brazos y no puede sostener la decision",
         "consecuencia": "la comparacion decidible depende de los cocientes que requieren el "
                         "contador no implementado"},
        {"id": "H2",
         "hallazgo": "el par pertinente-importante de importancia ALTA "
                     "(REFACTOR-WHATSAPP-ENTREGA-2026-09-18::D-AJUST.1) no tiene su leccion D-AJUST.1 "
                     "entre los 8 candidatos frios",
         "consecuencia": "cobertura_min 0.95 no se alcanza con 0.5; la colision entre el umbral "
                         "congelado y el denominador real se publica, no se resuelve re-leyendo el "
                         "criterio"},
        {"id": "H3",
         "hallazgo": f"el techo congelado de tokens_out ({protocolo['limites_gasto']['tokens_out']}) "
                     "fue vencido por la observacion en la misma etapa del congelado: "
                     f"{consumo_jev['tokens_out_max']} (jev) y "
                     f"{registro_ds['cuenta_al_salir']['tokens_out_max']} (deepseek)",
         "consecuencia": "se publica como hallazgo y NO se sube: subirlo despues de abrir eval "
                         "seria protocolo nuevo"},
        {"id": "H4",
         "hallazgo": "el brazo Jev fallo por conexion en 1 de sus 2 envios "
                     "(TypeSafeAPIConnectionError, 48 ms, request_id null, usage no_intentada) y NO "
                     "se reintento: max_retries=0 y el mandato autoriza 4 envios de inferencia",
         "consecuencia": "AC12: la indisponibilidad detiene o aplaza, no elimina el brazo; la "
                         "comparacion queda incompleta y declarada"},
        {"id": "H5",
         "hallazgo": "el CLI `run` no propaga `etiquetas` y `main()` no carga `.env`: por la via de "
                     "CLI el brazo Jev muere en TypeSafeError('No API key was provided') y "
                     "run_resumen.json saldria con recuperacion null",
         "consecuencia": "cambio requerido CR-3; la corrida de esta fase uso el mismo arnes "
                         "in-process que el corredor antecedente de FASE-B"},
        {"id": "H6",
         "hallazgo": "colision entre un umbral congelado y el denominador real: "
                     f"margen_vs_deepseek = {protocolo['criterios_adopcion']['margen_vs_deepseek']} "
                     f"sobre un denominador de eval de {len(pares_eval)} pares. La resolucion del "
                     "cociente extremo_a_extremo es 1/2 = 0.5 por par, o sea CUALQUIER diferencia no "
                     "nula supera el margen y la unica alternativa es 0.0: el umbral no discrimina en "
                     "este denominador. La `nota` congelada del protocolo lo calculaba contra el "
                     "denominador 4 de la muestra completa, no contra el 2 de eval",
         "consecuencia": "se publica como hallazgo y NO se re-lee el criterio, que es lo que el "
                         "mandato 3.5 prohibe. Sumado al fallo de Jev, el numero de pares donde los "
                         "dos brazos tienen una eleccion utilizable es 1"}],
    "cambios_requeridos": [
        {"id": "CR-1", "cambio": "implementar el contador de clasificacion (prec_num, rec_num) y el "
                                 "cociente extremo a extremo desde las respuestas persistidas, como "
                                 "instrumento testado, offline y regenerable desde registros",
         "diente": "test que lo ejercite sobre ledger.jsonl + ledger-deepseek.jsonl de esta fase"},
        {"id": "CR-2", "cambio": "implementar `report` (hoy fuera del parser: EXIT 2) y `decide` "
                                 "(hoy _refuse con EXIT 2) para emision mecanica de decision.json",
         "diente": "contract test sin red"},
        {"id": "CR-3", "cambio": "propagar `--etiquetas` en el parser de `run` y resolver la "
                                 "credencial del SDK sin exigir que el llamador cargue .env",
         "diente": "correr el CLI de punta a punta sobre un ledger persistido"},
        {"id": "CR-4", "cambio": "re-anclar la asercion de "
                                 "tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py:43 "
                                 "al estado CONGELADA, que es el aviso que la propia asercion "
                                 "anunciaba para FASE-C",
         "diente": "la bateria del protocolo debe volver a 24 verdes sin re-bajar ninguna asercion"}],
}

(OUT / "informe_comparativa.json").write_text(
    json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"filas_respuestas": len(filas_respuestas),
                  "recuperacion_por_brazo": {b: rec[b] for b in BRAZOS},
                  "hallazgos": [h["id"] for h in informe["hallazgos"]]},
                 ensure_ascii=False, indent=1))
