"""Arnès de mutantes del contrato de frescura re-escrito por D2 (REL-6) - 2026-10-05.

Mismo pacto que `44-arnes-mutantes-guard-preflight.py`: cada mutante desarma UNA clausula del contrato
nuevo, corre la seleccion de `tests/test_verify_qmind_context_freshness.py`, exige que caiga el diente
nombrado y restaura el arbol, verificado por sha256 y no por promesa. Corre en la sesion principal.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
SCRIPT = RAIZ / "scripts" / "verify_qmind_context_freshness.py"
SELECCION = "tests/test_verify_qmind_context_freshness.py"

MUTANTES = [
    {"id": "F1",
     "clausula": "la descarga verifica la promesa del servidor",
     "ancla": ('                descargado = _hash_bajado(nb, fuente["id"], scratch, ruta.stem)\n'
               '                if descargado is None:\n'),
     "mutacion": ('                descargado = fuente["sha_metadata"]\n'
                  '                if descargado is None:\n'),
     "esperados": ["test_el_verde_nuevo_sigue_exigiendo_la_descarga_que_verifica_la_promesa",
                   "test_fuente_que_casa_por_metadata_y_no_baja_es_no_evaluable_no_vencido"],
     "cae_porque": "con el indice como prueba nadie baja: el verde vuelve a ser una promesa sin verificar"},
    {"id": "F2",
     "clausula": "la fuente que casa por metadata y no baja es NO-EVALUABLE",
     "ancla": ('            abstenido = 2\n'
               '            lineas.append(f"  [NO-EVALUABLE] {etiqueta}: {len(sin_bajar)} fuente(s) cuyo "\n'),
     "mutacion": ('            salio = 1\n'
                  '            lineas.append(f"  [VENCIDO] {etiqueta}: {len(sin_bajar)} fuente(s) cuyo "\n'),
     "esperados": ["test_fuente_que_casa_por_metadata_y_no_baja_es_no_evaluable_no_vencido"],
     "cae_porque": "es H15 con su forma vieja: un fallo de red pinta VENCIDO un fresco"},
    {"id": "F3",
     "clausula": "la primera via es la metadata",
     "ancla": "        if prometidas:\n",
     "mutacion": "        if False:\n",
     "esperados": ["test_la_primera_via_no_mira_el_titulo_basta_la_metadata_que_casa",
                   "test_el_verde_nuevo_sigue_exigiendo_la_descarga_que_verifica_la_promesa"],
     "cae_porque": "se vuelve al camino de costo viejo: barrer las 58 fuentes aunque el servidor ya "
                   "diga cual casa"},
    {"id": "F4",
     "clausula": "cero observaciones en el barrido no es VENCIDO",
     "ancla": "        if sin_descarga == len(bajadas) and bajadas:\n",
     "mutacion": "        if False:\n",
     "esperados": ["test_barrido_del_que_no_baja_nada_sale_no_evaluable_y_declara_su_causa"],
     "cae_porque": "un barrido del que no bajo nada afirmaria vencido sin haber visto un byte"},
    {"id": "F5",
     "clausula": "fileSize se lee del listado y se corrobora",
     "ancla": '             "tam_metadata": (f.get("metadata") or {}).get("fileSize", "")}\n',
     "mutacion": '             "tam_metadata": ""}\n',
     "esperados": ["test_el_fileSize_del_servidor_tambien_se_corrobora_y_se_declara"],
     "cae_porque": "el tamano declarado deja de leerse, o sea la primera via pierde la mitad de su "
                   "insumo y el desacuerdo se calla"},
    {"id": "F6",
     "clausula": "el rojo manda sobre la abstencion",
     "ancla": "    return (salio or abstenido), lineas\n",
     "mutacion": "    return (abstenido or salio), lineas\n",
     "esperados": ["test_el_rojo_de_un_gobernado_manda_sobre_la_abstencion_de_otro"],
     "cae_porque": "la abstencion de un gobernado taparia el vencido de otro: el check se volveria "
                   "verdero por la via de la prudencia"},
]


def sha256_de(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def correr_seleccion() -> tuple[int, list[str], str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SELECCION, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(RAIZ), capture_output=True, text=True)
    fracasos = [l.split("::", 1)[1].strip()
                for l in proc.stdout.splitlines() if l.startswith("FAILED ")]
    return proc.returncode, fracasos, proc.stdout


def main() -> int:
    original = SCRIPT.read_bytes()
    sha_previo = sha256_de(SCRIPT)
    rc0, fallos0, cola0 = correr_seleccion()
    ultima = [l for l in cola0.splitlines() if "passed" in l or "failed" in l]
    print(f"== BASELINE (arbol curado) rc={rc0} fracasos={len(fallos0)} :: {ultima[-1:]}")
    if fallos0:
        print("ABORTO: la seleccion no estaba verde antes de mutar")
        return 2

    resultados = []
    try:
        for m in MUTANTES:
            texto = original.decode("utf-8")
            ocurrencias = texto.count(m["ancla"])
            if ocurrencias != 1:
                resultados.append({"id": m["id"], "ancla_unica": False, "ocurrencias": ocurrencias})
                print(f"== {m['id']}: ANCLA NO UNICA ({ocurrencias}) - no se muta")
                continue
            SCRIPT.write_bytes(texto.replace(m["ancla"], m["mutacion"], 1).encode("utf-8"))
            rc, fallos, _ = correr_seleccion()
            SCRIPT.write_bytes(original)
            restaurado = sha256_de(SCRIPT) == sha_previo
            cayeron = [e for e in m["esperados"] if any(e in f for f in fallos)]
            resultados.append({"id": m["id"], "clausula": m["clausula"], "rc": rc,
                               "n_fracasos": len(fallos), "fracasos": fallos,
                               "esperados": m["esperados"], "cayeron": cayeron,
                               "todos_los_esperados_cayeron": len(cayeron) == len(m["esperados"]),
                               "arbol_restaurado_por_sha": restaurado})
            print(f"== {m['id']} ({m['clausula']}): rc={rc} fracasos={len(fallos)} "
                  f"cayeron {len(cayeron)}/{len(m['esperados'])} restaurado={restaurado}")
            for f in fallos:
                print(f"     - {f}")
            if not restaurado:
                print("     !! el arbol NO volvio, abortando sin seguir mutando")
                return 3
    finally:
        SCRIPT.write_bytes(original)

    sha_final = sha256_de(SCRIPT)
    print(f"== SHA256 previo={sha_previo}")
    print(f"== SHA256 posterior={sha_final}  IDENTICO={sha_previo == sha_final}")
    print(json.dumps({"baseline_rc": rc0, "mutantes": resultados,
                      "arbol_intacto": sha_previo == sha_final}, ensure_ascii=False, indent=1))
    return 0 if sha_previo == sha_final else 1


if __name__ == "__main__":
    raise SystemExit(main())
