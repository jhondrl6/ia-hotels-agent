"""Arnès de mutantes del guard de preflight (REL-1, dictado D4) - sesion CIERRE-DE-ABANICO 2026-10-05.

Que un test nuevo pierda NO se afirma leyendo el test: se mide. Cada mutante desarma una clausula del
contrato nuevo sobre el arbol de trabajo, corre la seleccion del piloto y exige (a) que caiga el diente
nombrado y (b) que el arbol vuelva byte por byte, verificado por sha256 y no por promesa.

Corre en la sesion principal. No sale a la red ni escribe nada fuera del propio script mutado y de su
salida estandar.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
SCRIPT = RAIZ / "scripts" / "evaluate_jev_pilot.py"
SELECCION = "tests/quality_gates/jev_pilot"

MUTANTES = [
    {
        "id": "M1",
        "clausula": "la excusa NO-APLICA existe",
        "ancla": ('        motivo = _no_aplica_con_motivo(valor)\n'
                  '        if motivo:\n'
                  '            no_aplica[clave] = motivo\n'
                  '            continue\n'),
        "mutacion": "",
        "cae_porque": "sin la excusa el brazo comparador vuelve a cortarse: los dos VERDE de D4 y el "
                      "diente sobre FASE-C/preflight.json pierden",
        "esperados": ["test_no_aplica_con_motivo_escusa_el_estado_y_la_excusa_queda_publicada",
                      "test_el_guard_no_corta_el_run_cuando_el_brazo_declara_no_aplica_con_motivo",
                      "test_el_preflight_versionado_de_fase_c_ya_no_corta_el_comparador"],
    },
    {
        "id": "M2",
        "clausula": "la comparacion es de tipo y valor",
        "ancla": "    return type(valor) is type(esperado) and valor == esperado\n",
        "mutacion": "    return valor == esperado\n",
        "cae_porque": "`1 == True` en Python: con la comparacion ciega de tipo un entero vuelve a pasar "
                      "por declaracion de SDK instalado",
        "esperados": ["test_cada_forma_que_no_es_declaracion_valida_sigue_cortando[1-un entero que se "
                      "parece a True]"],
    },
    {
        "id": "M3",
        "clausula": "el motivo tiene que estar escrito",
        "ancla": "    return resto.strip(_SEPARADORES_NO_APLICA).strip()\n",
        "mutacion": '    return "excusa"\n',
        "cae_porque": "un NO-APLICA pelado excusa igual que uno con motivo, que es justo lo que D4 "
                      "niega",
        "esperados": ["test_cada_forma_que_no_es_declaracion_valida_sigue_cortando[NO-APLICA-el literal "
                      "sin motivo]",
                      "test_cada_forma_que_no_es_declaracion_valida_sigue_cortando[NO-APLICA:-el "
                      "separador sin motivo]",
                      "test_no_aplica_sin_motivo_corta_el_run_y_no_envia_nada"],
    },
    {
        "id": "M4",
        "clausula": "NO-APLICA es un literal, no un prefijo de cualquiera",
        "ancla": ('    if resto and resto[0] not in _SEPARADORES_NO_APLICA:\n'
                  '        return ""\n'),
        "mutacion": '    if False:\n        return ""\n',
        "cae_porque": "`NO-APLICABLE: ...` pasa por declaracion valida cuando el brazo no escribio el "
                      "literal que se le pide",
        "esperados": ["test_cada_forma_que_no_es_declaracion_valida_sigue_cortando[NO-APLICABLE: el "
                      "brazo no usa SDK-otra palabra que empieza igual]"],
    },
]


def sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def correr_seleccion() -> tuple[int, list[str], str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", SELECCION, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(RAIZ), capture_output=True, text=True)
    fracasos = [l.split("::", 1)[1].strip()
                for l in proc.stdout.splitlines() if l.startswith("FAILED ")]
    return proc.returncode, fracasos, proc.stdout[-400:]


def main() -> int:
    original = SCRIPT.read_bytes()
    sha_original = sha256(SCRIPT)
    baseline_rc, baseline_fallos, baseline_cola = correr_seleccion()
    print(f"== BASELINE (arbol curado) rc={baseline_rc} fracasos={len(baseline_fallos)}")
    print(f"   cola: {baseline_cola.strip().splitlines()[-1] if baseline_cola else ''}")
    if baseline_fallos:
        print("ABORTO: la seleccion no estaba verde antes de mutar")
        return 2

    resultados = []
    try:
        for m in MUTANTES:
            texto = original.decode("utf-8")
            n = texto.count(m["ancla"])
            if n != 1:
                resultados.append({"id": m["id"], "ancla_unica": False, "ocurrencias": n})
                print(f"== {m['id']}: ANCLA NO UNICA ({n}) - no se muta, el diseno cambio")
                continue
            SCRIPT.write_bytes(texto.replace(m["ancla"], m["mutacion"], 1).encode("utf-8"))
            rc, fallos, cola = correr_seleccion()
            restaurado = sha256(SCRIPT)
            SCRIPT.write_bytes(original)
            cayeron = [e for e in m["esperados"] if any(e in f for f in fallos)]
            resultados.append({
                "id": m["id"], "clausula": m["clausula"], "ancla_unica": True,
                "rc": rc, "n_fracasos": len(fallos), "fracasos": fallos,
                "esperados_que_cayeron": cayeron,
                "todos_los_esperados_cayeron": len(cayeron) == len(m["esperados"]),
                "arbol_restaurado_por_sha": sha_original == sha256(SCRIPT),
            })
            print(f"== {m['id']} ({m['clausula']}): rc={rc} fracasos={len(fallos)} "
                  f"cayeron {len(cayeron)}/{len(m['esperados'])} esperados")
            for f in fallos:
                print(f"     - {f}")
    finally:
        SCRIPT.write_bytes(original)

    sha_final = sha256(SCRIPT)
    print("== SHA256 del script")
    print(f"   previo     = {sha_original}")
    print(f"   posterior  = {sha_final}")
    print(f"   IDENTICO   = {sha_original == sha_final}")
    salida = {"baseline_fracasos": baseline_rc, "mutantes": resultados,
              "sha_previo": sha_original, "sha_posterior": sha_final,
              "arbol_intacto": sha_original == sha_final}
    print(json.dumps(salida, ensure_ascii=False, indent=1))
    return 0 if sha_original == sha_final else 1


if __name__ == "__main__":
    raise SystemExit(main())
