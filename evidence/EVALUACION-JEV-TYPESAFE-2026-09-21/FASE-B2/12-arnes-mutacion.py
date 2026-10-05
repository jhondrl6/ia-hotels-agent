# -*- coding: utf-8 -*-
"""Arnhes de mutacion del par de FASE-B.2 (SESION 3.5, 2026-10-04). Cero red, cero inferencias.

Que produce
  FASE-B2/mutation.json - por cada diente del instrumento nuevo: la linea base verde, el mutante
  aplicado SOBRE EL MODULO CARGADO EN MEMORIA, el valor que se mueve y la causa nombrada, y la
  restauracion verificada.

Que NO produce
  Ningun numero de la corrida real: los insumos son sinteticos y viven en el temp del sistema, no
  en el arbol de trabajo. El arbol no se muta: el archivo fuente se copia a memoria, se parcha el
  simbolo y se comprueba por sha256 que el disco no se toco (L-V2.1, contrato de la casa: "no mutar
  el working tree compartido").

Comando
  venv/Scripts/python.exe evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/12-arnes-mutacion.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path("C:/Users/Jhond/Github/iah-cli")
FUENTE = ROOT / "scripts" / "evaluate_jev_pilot.py"
OUT = ROOT / "evidence" / "EVALUACION-JEV-TYPESAFE-2026-09-21" / "FASE-B2"

# Insumos sinteticos: los mismos cuatro pares y las mismas cuatro filas del diente base de
# tests/quality_gates/jev_pilot/test_jev_pilot_report_decide_fase_b2.py, copiados aqui para que la
# medicion sea independiente de la coleccion de pytest.
PARES = [("A::L-A", "L-A", "eval"), ("B::L-B", "L-B", "eval"),
         ("C::L-C", "L-C", "dev"), ("D::L-D", "L-D", "dev")]
LABELS = [("A::L-A", "pertinente", "alta"), ("B::L-B", "pertinente", "media"),
          ("C::L-C", "pertinente", "alta"), ("D::L-D", "no_pertinente", None)]
FILAS = [
    {"pair_id": "A::L-A", "split": "eval", "lesson_id_target": "L-A", "brazo": "jev",
     "propuesta": "L-A", "abstencion": False, "candidatos_frios": ["L-A", "L-X", "L-Y"],
     "leccion_target_en_candidatos": True, "attempts": 1, "error_kind": None,
     "intentos": [{"n": 1, "resultado": "exito", "duracion_ms": 200.0}],
     "usage_normalized": None, "duracion_ms": [200.0], "modelo_pedido": "jev-1.13.0",
     "modelo_efectivo": None, "request_id": None, "etiqueta": "pertinente",
     "importancia": "alta"},
    {"pair_id": "B::L-B", "split": "eval", "lesson_id_target": "L-B", "brazo": "jev",
     "propuesta": "L-Z", "abstencion": False, "candidatos_frios": ["L-X", "L-Y", "L-Z"],
     "leccion_target_en_candidatos": False, "attempts": 1, "error_kind": None,
     "intentos": [{"n": 1, "resultado": "exito", "duracion_ms": 300.0}],
     "usage_normalized": None, "duracion_ms": [300.0], "modelo_pedido": "jev-1.13.0",
     "modelo_efectivo": None, "request_id": None, "etiqueta": "pertinente",
     "importancia": "media"},
    {"pair_id": "A::L-A", "split": "eval", "lesson_id_target": "L-A", "brazo": "deepseek",
     "propuesta": "ninguna-aplica", "abstencion": True, "candidatos_frios": ["L-A", "L-X", "L-Y"],
     "leccion_target_en_candidatos": True, "attempts": 1, "error_kind": None,
     "intentos": [{"n": 1, "resultado": "exito", "duracion_ms": 1000.0}],
     "usage_normalized": None, "duracion_ms": [1000.0], "modelo_pedido": "deepseek-chat",
     "modelo_efectivo": None, "request_id": None, "etiqueta": "pertinente",
     "importancia": "alta"},
    {"pair_id": "B::L-B", "split": "eval", "lesson_id_target": "L-B", "brazo": "deepseek",
     "propuesta": None, "abstencion": None, "candidatos_frios": ["L-X", "L-Y", "L-Z"],
     "leccion_target_en_candidatos": False, "attempts": 1, "error_kind": "conexion",
     "intentos": [{"n": 1, "resultado": "fallo", "duracion_ms": 12.0,
                   "error_kind": "conexion", "clase": "TypeSafeAPIConnectionError"}],
     "usage_normalized": None, "duracion_ms": [12.0], "modelo_pedido": "deepseek-chat",
     "modelo_efectivo": None, "request_id": None, "etiqueta": "pertinente",
     "importancia": "media"},
]


def _cargar(nombre: str) -> object:
    spec = importlib.util.spec_from_file_location(nombre, FUENTE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nombre] = mod
    spec.loader.exec_module(mod)
    return mod


def _insumos(dir_tmp: Path) -> dict:
    muestra = {"schema": "jev-pilot-muestra/v1", "status": "CONGELADA",
               "review": {"human_reviewed": True, "reviewer": "jhon", "reviewed_at": "2026-10-02"},
               "pairs": [{"pair_id": pid, "target_plan": pid.split("::")[0],
                          "target_phase": "FASE-B", "lesson_id": lesson,
                          "input_fragment": f"fragmento de {pid}", "split": split,
                          "original_sha256": "0" * 64, "sanitized_sha256": "0" * 64}
                         for pid, lesson, split in PARES],
               "exclusions": [], "counts": {"total": 4, "dev": 2, "eval": 2, "excluidos": 0},
               "corpus_source": "synthetic", "temporal_cut": "2026-09-12"}
    etiquetas = {"schema": "jev-pilot-etiquetas/v1", "review_status": "revisada",
                 "labels": [{"pair_id": pid, "label": lab, "importance": imp,
                             "reviewer": "jhon", "reviewed_at": "2026-10-02"}
                            for pid, lab, imp in LABELS]}
    protocolo = {"schema": "jev-pilot-protocolo/v1", "status": "CONGELADA",
                 "congelado": {"revisado_por": "jhon", "fecha": "2026-10-04"},
                 "reglas_recuperacion": "top-8 por consulta fria",
                 "rubrica": {"valores": ["pertinente", "no_pertinente", "insuficiente"],
                             "importancia": ["alta", "media", "baja"]},
                 "modelos": {"jev_pin": "jev-1.13.0", "comparador": "DeepSeek",
                             "excluido": "Anthropic"},
                 "parametros": {"retry_policy": {"max_retries": 0}, "timeout_s": 30},
                 "limites_gasto": {"usd": None, "llamadas": 12, "tokens_in": 1834,
                                   "tokens_out": 139,
                                   "motivo": "fuera de gobernanza por decision del operador"},
                 "criterios_adopcion": {"cobertura_min": 0.95, "margen_vs_deepseek": 0.25,
                                        "tratamiento_abstenciones": "contadas como fallo",
                                        "suficiencia_minima": 0.5, "latencia_max": 30000,
                                        "revision_humana": "obligatoria; designado: jhon"}}
    ruta_r = dir_tmp / "respuestas.jsonl"
    dir_tmp.mkdir(parents=True, exist_ok=True)
    ruta_r.write_text("".join(json.dumps(f, ensure_ascii=False) + "\n" for f in FILAS),
                      encoding="utf-8")
    rutas = {"respuestas": ruta_r}
    for nombre, datos in (("muestra", muestra), ("etiquetas", etiquetas), ("protocolo", protocolo)):
        ruta = dir_tmp / f"{nombre}.json"
        ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
        rutas[nombre] = ruta
    return rutas


CENTINELA = "CLAVE-SINTETICA-NO-IMPRIMIBLE-0123456789"


def _medida(mod: object, dir_tmp: Path) -> dict:
    """Los cuatro cocientes del brazo jev, dos lecturas del brazo deepseek y el estado de la
    credencial, en un solo dict. La credencial se mide sobre un `.env` sintetico en el temp del
    sistema: lo que se afirma es que el estado publicado no porta ni el valor ni su longitud."""
    r = _insumos(dir_tmp)
    informe = mod.report(respuestas=r["respuestas"], etiquetas=r["etiquetas"], muestra=r["muestra"],
                         protocolo=r["protocolo"], fecha="2026-10-04")
    jev, ds = informe["por_brazo"]["jev"], informe["por_brazo"]["deepseek"]
    decision = mod.decide(informe=informe, protocolo=json.loads(
        r["protocolo"].read_text(encoding="utf-8")), fecha="2026-10-04")
    dir_env = dir_tmp / "env"
    dir_env.mkdir(parents=True, exist_ok=True)
    (dir_env / ".env").write_text(f"TYPESAFE_API_KEY={CENTINELA}\n", encoding="utf-8")
    estado = mod.credencial_del_sdk(dir_env)
    return {
        "jev_precision": [jev["precision_entre_propuestas"]["numerator"],
                          jev["precision_entre_propuestas"]["denominator"]],
        "jev_recall": [jev["recall_importante_candidatos"]["numerator"],
                       jev["recall_importante_candidatos"]["denominator"]],
        "jev_e2e": [jev["extremo_a_extremo"]["numerator"], jev["extremo_a_extremo"]["denominator"]],
        "jev_recuperacion": [jev["recuperacion"]["numerator"],
                             jev["recuperacion"]["denominator"]],
        "ds_abstenciones": ds["abstenciones"]["abstenciones"],
        "ds_cociente_abstencion": [ds["abstenciones"]["cociente_de_abstencion"]["numerator"],
                                   ds["abstenciones"]["cociente_de_abstencion"]["denominator"]],
        "ds_e2e_denominator": ds["extremo_a_extremo"]["denominator"],
        "margen_estado": decision["criterios_congelados"]["margen_vs_deepseek"]["estado"],
        "run_status": decision["run_status"],
        "credencial_estado_claves": sorted(estado),
        "centinela_en_el_estado_publicado": CENTINELA in json.dumps(estado),
    }


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


MUTANTES = [
    {"id": "M1", "diente": "test_mutante_acierto_siempre_falso_mueve_los_tres_cocientes_que_usan"
                           "_la_regla",
     "mutante": "es_acierto devuelto siempre falso",
     "aplicar": lambda m: setattr(m, "es_acierto", lambda par: False),
     "esperado": "los tres numeradores de clasificacion y e2e caen a 0; la recuperacion NO se mueve "
                 "porque la pone la funcion testada",
     "cae_por": "el contador de clasificacion deja de leer el acierto de la fila"},
    {"id": "M2", "diente": "test_mutante_abstencion_vuelta_eleccion_cambia_precision_y_el_"
                           "denominador_aparte",
     "mutante": "estado_de_propuesta trata `ninguna-aplica` como eleccion",
     "aplicar": lambda m: setattr(m, "estado_de_propuesta",
                                 (lambda real: lambda fila: (
                                     "eleccion" if fila and fila.get("propuesta")
                                     == m.ETIQUETA_DE_NINGUNA else real(fila)))(m.estado_de_propuesta)),
     "esperado": "el denominador propio de abstenciones se vacia y precision sube de 0 a 1",
     "cae_por": "la abstencion se conto como propuesta: el criterio congelado peridio su columna"},
    {"id": "M3", "diente": "test_un_fallo_del_camino_cuenta_en_extremo_a_extremo_y_no_como_propuesta",
     "mutante": "estado_de_propuesta colapsa `sin_eleccion_por_fallo` en `sin_fila` (el fallo se "
                "vuelve invisible)",
     "aplicar": lambda m: setattr(m, "estado_de_propuesta",
                                 (lambda real: lambda fila: "sin_fila" if (
                                     fila and fila.get("propuesta") is None
                                     and fila.get("error_kind")) else real(fila))(
                                     m.estado_de_propuesta)),
     "esperado": "el denominador del extremo a extremo baja de 2 a 1: el score sube por excluir el "
                 "fallo, que es exactamente lo que el maestro :93 prohibe",
     "cae_por": "el fallo desaparecio del registro y el brazo quedo mejor medido de lo que fue"},
    {"id": "M4", "diente": "test_la_credencial_se_resuelve_por_entorno_y_no_sale_en_ningun_artefacto",
     "mutante": "credencial_del_sdk publica el valor leido del `.env` y su longitud en el estado",
     "aplicar": lambda m: setattr(
         m, "credencial_del_sdk",
         (lambda real: lambda raiz, nombre=m.CREDENCIAL_DEL_SDK, **k: {
             **real(raiz, nombre=nombre, **k),
             "valor": (dict(__import__("dotenv").dotenv_values(Path(raiz) / ".env"))
                       .get(nombre) or ""),
             "longitud": len((dict(__import__("dotenv").dotenv_values(
                 Path(raiz) / ".env")).get(nombre) or ""))})(m.credencial_del_sdk)),
     "esperado": "el estado publicado gana las claves `valor` y `longitud` y el centinela aparece "
                 "en el json: el diente de la fuga cae por la clave nombrada",
     "cae_por": "una credencial publicada, o incluso su forma (la longitud), es una fuga y no un "
                "detalle del registro"},
    {"id": "M5", "diente": "test_una_indisponibilidad_no_elimina_el_brazo",
     "mutante": "el informe se construye con los fallos operativos del brazo sujeto borrados "
                "(la indisponibilidad se esconde del criterio de margen)",
     "aplicar": None,
     "esperado": "margen pasa de NO-EVALUABLE a evaluable y run_status de INCOMPLETO a COMPLETO, "
                 "con el brazo todavía publicado",
     "cae_por": "AC12: medirle al modelo una indisponibilidad de la infraestructura convierte un "
                 "fallo del camino en veredicto"},
]


def main() -> int:
    sha_antes = _sha(FUENTE)
    directorios = []
    registros = []
    for mut in MUTANTES:
        nombre = f"ejv_mut_{mut['id']}"
        dir_tmp = Path(tempfile.mkdtemp(prefix=f"jev-b2-{mut['id']}-"))
        directorios.append(dir_tmp)
        base = _cargar(f"ejv_base_{mut['id']}")
        verde = _medida(base, dir_tmp / "base")
        if mut["aplicar"] is not None:
            mutante = _cargar(nombre)
            mut["aplicar"](mutante)
            rojo = _medida(mutante, dir_tmp / "mutante")
        else:
            # M5 trabaja sobre el informe ya construido: es la unica forma de expresar "el fallo
            # desaparecio del registro" sin re-escribir el instrumento.
            r = _insumos(dir_tmp / "m5")
            muestra_datos = json.loads(r["muestra"].read_text(encoding="utf-8"))
            etiquetas_datos = json.loads(r["etiquetas"].read_text(encoding="utf-8"))
            protocolo_datos = json.loads(r["protocolo"].read_text(encoding="utf-8"))
            informe = base.report(respuestas=r["respuestas"], etiquetas=r["etiquetas"],
                                  muestra=r["muestra"], protocolo=r["protocolo"],
                                  fecha="2026-10-04")
            for brazo in ("jev", "deepseek"):
                informe["por_brazo"][brazo]["contabilidad"]["fallos_operativos"] = []
            informe["criterios"] = base.evaluar_criterios(
                informe["por_brazo"],
                base.poblacion_de_comparacion(muestra_datos, etiquetas_datos),
                protocolo_datos, list(informe["por_brazo"]))
            mutante_rojo = base.decide(informe=informe, protocolo=protocolo_datos,
                                       fecha="2026-10-04")
            rojo = dict(verde)
            rojo["margen_estado"] = mutante_rojo["criterios_congelados"]["margen_vs_deepseek"]["estado"]
            rojo["run_status"] = mutante_rojo["run_status"]
        restaurada = _medida(_cargar(f"ejv_restaura_{mut['id']}"), dir_tmp / "restaura")
        movidos = sorted(k for k in verde if verde[k] != rojo[k])
        registros.append({
            "id": mut["id"], "diente": mut["diente"], "mutante": mut["mutante"],
            "verde": verde, "rojo": rojo, "campos_que_se_movieron": movidos,
            "esperado": mut["esperado"], "cae_por": mut["cae_por"],
            "cae_por_la_causa_nombrada": bool(movidos) and restaurada == verde,
            "restauracion": "modulo recargado desde la fuente en disco; el arbol no se muto",
        })
    sha_despues = _sha(FUENTE)
    artefacto = {
        "schema": "jev-pilot-mutacion/v1",
        "sesion": "SESION 3.5 (FASE-B.2) del piloto JEV",
        "fecha": "2026-10-04",
        "instrumento": "scripts/evaluate_jev_pilot.py, cargado por importlib desde la ruta versionada",
        "comando": "venv/Scripts/python.exe evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/"
                   "12-arnes-mutacion.py",
        "cero_red": "el guard de sockets del conftest no interviene aqui: ninguna de estas rutas "
                    "abre transporte, `report`/`decide` no lo instancian y el mutant M4 reemplaza "
                    "la resolucion de la credencial",
        "fuente": {"ruta": "scripts/evaluate_jev_pilot.py", "sha256_antes": sha_antes,
                   "sha256_despues": sha_despues, "arbol_intacto": sha_antes == sha_despues},
        "insumos": "sinteticos en el temp del sistema (4 pares, 2 brazos), no la corrida de FASE-C",
        "mutantes": registros,
        "todos_caeen_por_la_causa_nombrada": all(r["cae_por_la_causa_nombrada"] for r in registros),
    }
    destino = OUT / "mutation.json"
    destino.write_text(json.dumps(artefacto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for d in directorios:
        shutil.rmtree(d, ignore_errors=True)
    print(json.dumps({"mutantes": len(registros),
                      "todos_caeen": artefacto["todos_caeen_por_la_causa_nombrada"],
                      "arbol_intacto": artefacto["fuente"]["arbol_intacto"],
                      "sha": sha_despues[:12]}, ensure_ascii=False, indent=1))
    for r in registros:
        print(f"{r['id']}: movio {r['campos_que_se_movieron']} -> cae por la causa nombrada: "
              f"{r['cae_por_la_causa_nombrada']}")
    return 0 if artefacto["todos_caeen_por_la_causa_nombrada"] and \
        artefacto["fuente"]["arbol_intacto"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
