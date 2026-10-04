"""ARNES de los mutantes del Cierre A (SESION 2.5, 2026-10-04).

Un mutante -> la bateria entera del archivo -> restauracion en `finally` con sha256 antes y despues (la
regla que ya publican `FASE-B/mutation.json` y `DEUDA-FASE-B-2026-10-04/08a-arnes-mutacion-ac6.py`).

Cada ancla se verifica por numero de ocurrencias antes de mutar (por clave, no por posicion): un ancla
ambigua mutaria la rama equivocada y daria un rojo que no es el del diente. Se corre el archivo completo
por mutante y se publica el kill-set, no solo el nodo previsto: asi un rojo inesperado se ve en vez de
contarse como exito.

Nota de instrumento: la primera ronda tuvo dos mutantes EQUIVALENTES (verde). `split(SEP, 1)[1]` y
`split(SEP)[1]` coinciden con `rsplit(SEP, 1)[1]` porque los ids del corpus (`sonda:1`, `pert:L-R.1`)
llevan UN solo `:`; cortar por el separador no distingue. Se declaran aqui en vez de esconderlos y se
sustituyen por `split(SEP)[0]`, que toma el prefijo y si muerde.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OBJETIVO = ROOT / "scripts" / "proveedores" / "deepseek.py"
ARCHIVO_TEST = "tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py"

FILA_NOUL = '            fila = {"pregunta_id": p.id, "tipo": "noul"}\n'
FILA_CHOICE = '            fila = {"pregunta_id": p.id, "tipo": "choice"}\n'
FILA_SCORE = '            fila = {"pregunta_id": p.id, "tipo": "score"}\n'
CONSTRUC = FILA_NOUL + FILA_CHOICE + FILA_SCORE

DIENTES = [
    {
        "id": "M1-el-recorte-vuelve-a-descartarse",
        "predicho": ["test_un_id_recortado_devuelve_la_respuesta_mapeada_en_vez_de_descartarla"],
        "causa_predicha": ("desaparece la segunda vuelta del emparejamiento: la respuesta recortada vuelve "
                           "al basurero y el payload sale `respuestas: []` con el envio cobrado, o sea el "
                           "defecto de la deuda (fila 2) reapareciendo tal cual"),
        "ancla": ("    for p in preguntas:\n"
                  "        if p.id in emparejadas:\n"
                  "            continue\n"
                  "        recorte = _recorte_de(p.id)\n"),
        "mutante": ("    for p in []:\n"
                    "        if p.id in emparejadas:\n"
                    "            continue\n"
                    "        recorte = _recorte_de(p.id)\n"),
    },
    {
        "id": "M2-toma-el-prefijo-en-vez-de-la-cola",
        "predicho": ["test_el_prefijo_del_triaje_recortado_conserva_la_respuesta_completa"],
        "causa_predicha": ("el recorte se toma del lado equivocado del delimitador: `pert:L-R.1` busca "
                           "`pert` en vez de `L-R.1` y la respuesta del triaje se pierde otra vez"),
        "ancla": '    return pid.rsplit(DELIMITADOR_DE_PREFIJO, 1)[1] if DELIMITADOR_DE_PREFIJO in pid else ""',
        "mutante": '    return pid.split(DELIMITADOR_DE_PREFIJO)[0] if DELIMITADOR_DE_PREFIJO in pid else ""',
    },
    {
        "id": "M3-adivina-el-recorte-ambiguo",
        "predicho": ["test_un_recorte_ambiguo_no_se_adivina"],
        "causa_predicha": ("se quita el control de unicidad entre preguntas: con `a:1` y `b:1` la `1` suelta "
                           "se asigna a la primera y la filiacion sale inventada"),
        "ancla": "        if len(candidatas) == 1 and len(libres) == 1:\n",
        "mutante": "        if len(libres) == 1:\n",
    },
    {
        "id": "M4-el-recorte-roba-la-respuesta-exacta",
        "predicho": ["test_la_coincidencia_exacta_no_le_cede_su_respuesta_al_recorte"],
        "causa_predicha": ("el recorte ya no respeta las respuestas consumidas: la misma cruda se publica "
                           "dos veces, una con el id exacto y otra con el preguntado"),
        "ancla": ("        libres = [i for i, r in enumerate(trayidas)\n"
                  "                  if i not in tomadas and r[\"pregunta_id\"] == recorte]\n"),
        "mutante": ("        libres = [i for i, r in enumerate(trayidas)\n"
                    "                  if r[\"pregunta_id\"] == recorte]\n"),
    },
    {
        "id": "M5-rellena-lo-que-no-vino",
        "predicho": ["test_el_recorte_no_rellena_lo_que_el_servicio_no_trajo"],
        "causa_predicha": ("la rama choice planta un `confidence` que el servicio no trajo: sale un numero "
                           "inventado y la puerta deja de poder marcarlo como ILEGIBLE"),
        "ancla": FILA_CHOICE,
        "mutante": '            fila = {"pregunta_id": p.id, "tipo": "choice", "confidence": 0.5}\n',
    },
    {
        "id": "M6-publica-el-id-del-servicio",
        "predicho": ["test_un_id_recortado_devuelve_la_respuesta_mapeada_en_vez_de_descartarla",
                     "test_el_prefijo_del_triaje_recortado_conserva_la_respuesta_completa",
                     "test_el_recorte_no_rellena_lo_que_el_servicio_no_trajo"],
        "causa_predicha": ("la fila se arma con el `pregunta_id` que trajo el servicio y no con el "
                           "preguntado: la puerta cuenta la fila como pregunta no pedida y ademas deja "
                           "sin respuesta la que si se pidio"),
        "ancla": '"pregunta_id": p.id',
        "ocurrencias_esperadas": 3,
        "mutante": '"pregunta_id": bruto["pregunta_id"]',
    },
]

EQUIVALENTES_MEDIDOS = [
    {"id": "M2a-split-con-maxsplit-1", "mutante": 'pid.split(DELIMITADOR_DE_PREFIJO, 1)[1]',
     "resultado": "VERDE (rc=0)", "lectura": "equivalente: con un solo `:` coincide con `rsplit(.., 1)[1]`"},
    {"id": "M2b-split-sin-maxsplit", "mutante": 'pid.split(DELIMITADOR_DE_PREFIJO)[1]',
     "resultado": "VERDE (rc=0)",
     "lectura": "equivalente por el mismo motivo: `pert:L-R.1` parte en ['pert', 'L-R.1'] porque el resto "
                "usa guiones y punto, no `:`"},
]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def correr_bateria() -> dict:
    proc = subprocess.run([sys.executable, "-m", "pytest", ARCHIVO_TEST, "-q", "--no-header",
                           "-p", "no:cacheprovider"], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    salida = (proc.stdout or "") + (proc.stderr or "")
    fallidos = sorted(l.split("::")[-1].strip() for l in salida.splitlines() if l.startswith("FAILED"))
    return {"rc": proc.returncode, "fallidos": fallidos,
            "linea_final": next((l.strip() for l in reversed(salida.splitlines())
                                 if " passed" in l or " failed" in l or "error" in l), ""),
            "crudo_rojo": "\n".join(l for l in salida.splitlines()
                                    if l.startswith(("FAILED", "E  ", "assert", "_____")))[:1800]}


def main() -> int:
    original = OBJETIVO.read_bytes()
    baseline = sha(original)

    def status_objetivo() -> str:
        return subprocess.run(["git", "status", "--porcelain", "--",
                               "scripts/proveedores/deepseek.py"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip()

    git_antes = status_objetivo()
    resultados = []
    try:
        for d in DIENTES:
            texto = original.decode("utf-8")
            ocurrencias = texto.count(d["ancla"])
            esperado = d.get("ocurrencias_esperadas", 1)
            if ocurrencias != esperado:
                resultados.append({"id": d["id"], "error_de_arnes": f"ancla con {ocurrencias} ocurrencias "
                                   f"(se esperaban {esperado})"})
                continue
            OBJETIVO.write_bytes(texto.replace(d["ancla"], d["mutante"], ocurrencias).encode("utf-8"))
            rojo = correr_bateria()
            sha_mutante = sha(OBJETIVO.read_bytes())
            OBJETIVO.write_bytes(original)
            verde = correr_bateria()
            sha_restaurado = sha(OBJETIVO.read_bytes())
            caen = set(rojo["fallidos"])
            predichos = set(d["predicho"])
            resultados.append({
                "id": d["id"], "predichos": sorted(predichos), "causa_predicha": d["causa_predicha"],
                "rojo": {"rc": rojo["rc"], "linea_final": rojo["linea_final"], "kill_set": rojo["fallidos"]},
                "cayeron_todos_los_predichos": predichos <= caen,
                "cayo_algo_no_predicho": sorted(caen - predichos),
                "rojo_ruidoso": rojo["rc"] != 0 and bool(rojo["fallidos"]),
                "crudo_rojo": rojo["crudo_rojo"],
                "verde_tras_restaurar": {"rc": verde["rc"], "linea_final": verde["linea_final"],
                                         "fallidos": verde["fallidos"]},
                "sha_mutante": sha_mutante[:12], "sha_restaurado": sha_restaurado[:12],
                "restauracion_coincide": sha_restaurado == baseline,
            })
    finally:
        OBJETIVO.write_bytes(original)
    git_despues = status_objetivo()
    informe = {
        "arnes": "p2_mutantes_cierre_a.py",
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "revision_arranque": subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                            capture_output=True, text=True).stdout.strip(),
        "objetivo": "scripts/proveedores/deepseek.py",
        "bateria": ARCHIVO_TEST,
        "sha_baseline_antes_de_la_ronda": baseline,
        "sha_baseline_antes_de_la_ronda_trunco": baseline[:12],
        "resultado_por_mutante": resultados,
        "mutantes_equivalentes_declarados": EQUIVALENTES_MEDIDOS,
        "todos_restaurados": all(r.get("restauracion_coincide") for r in resultados
                                 if "error_de_arnes" not in r),
        "todos_cortaron_por_su_causa": all(r.get("cayeron_todos_los_predichos") and r.get("rojo_ruidoso")
                                           for r in resultados if "error_de_arnes" not in r),
        "git_status_objetivo_antes": git_antes,
        "git_status_objetivo_despues": git_despues,
        "git_status_identico": git_antes == git_despues,
        "lectura_del_status": ("el archivo figura M en git por la cura de esta sesion (A1), no por los "
                               "mutantes: la restauracion la goberna el sha y el status es el mismo antes "
                               "y despues de la ronda"),
        "cantidad_de_mutantes": len(resultados),
    }
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else (
        ROOT / "temp" / "sesion25-2026-10-04" / "04-mutantes-cierre-a.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(informe, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in informe.items() if k != "resultado_por_mutante"},
                     ensure_ascii=False, indent=1))
    for r in resultados:
        print("-", r["id"], "| predichos", len(r.get("predichos", [])),
              "| cortaron", r.get("cayeron_todos_los_predichos"),
              "| kill_set", len(r.get("rojo", {}).get("kill_set", [])),
              "| inesperados", r.get("cayo_algo_no_predicho"),
              "| verde", r.get("verde_tras_restaurar", {}).get("linea_final"),
              "| restaurado", r.get("restauracion_coincide"),
              r.get("error_de_arnes", ""))
    return 0 if (informe["todos_restaurados"] and informe["todos_cortaron_por_su_causa"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
