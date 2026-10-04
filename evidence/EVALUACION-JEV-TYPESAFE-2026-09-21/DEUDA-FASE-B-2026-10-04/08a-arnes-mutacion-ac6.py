"""ARNES de la mutacion AC6 (fila 1 de la deuda de FASE-B, 2026-10-04).

Un mutante -> un nodo de pytest -> restauracion en `finally` con sha256 antes y despues, que es la regla de
restauracion que ya publico `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/mutation.json`.

Escribe solo dos cosas: el crudo JSON del resultado (ruta explicita por argumento) y el arbol de trabajo
durante la ventana del mutante, que se devuelve byte a byte.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# El arnes vive en temp/deuda-<fecha>/, dos niveles bajo la raiz: parents[1] apuntaba a `temp/` y la primera
# corrida murio antes de tocar nada (`FileNotFoundError` sobre temp/scripts/...), que es el fallo inocuo
# pero hay que decirlo.
ROOT = Path(__file__).resolve().parents[2]
OBJETIVO = ROOT / "scripts" / "triage_lesson_relevance.py"
NODO = ("tests/quality_gates/lesson_relevance/test_triage_guard_real_aditividad.py"
        "::test_real_triage_guard_preserves_anchored_rows")
ANCLA = ("    if intentos:\n"
         "        return list(anteriores) + [f for f in propuesta if f not in anteriores], intentos")
MUTANTE = ("    if intentos:\n"
           "        return list(propuesta), intentos")


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def correr_nodo() -> dict:
    proc = subprocess.run([sys.executable, "-m", "pytest", NODO, "-q", "--no-header", "-x"],
                          capture_output=True, cwd=str(ROOT), timeout=600)
    texto = (proc.stdout or b"").decode("utf-8", "replace") + (proc.stderr or b"").decode("utf-8", "replace")
    lineas = [l for l in texto.splitlines() if l.strip()]
    # La marca solo se afirma en un rojo: en el verde el tail re-imprime la fuente del assert, y ahi el
    # literal «el triaje filtro filas ancladas» aparece sin que nadie haya fallado (medido en la primera
    # pasada). Y el mojibake del tail (`\ufffd` por donde va el §) es consola cp1252 decodeada como utf-8:
    # es forma de la impresion, no contenido del artefacto.
    return {"codigo_de_salida": proc.returncode, "tail_de_la_caida": "\n".join(lineas[-12:]),
            "cae_por_la_causa_nombrada": (proc.returncode != 0
                                          and any("el triaje filtro filas ancladas" in l
                                                  and l.startswith("E ") for l in lineas))}


def main(destino: str) -> int:
    originales = OBJETIVO.read_bytes()
    sha_antes = sha(originales)
    lf = originales.decode("utf-8").replace("\r\n", "\n")
    ocurrencias = lf.count(ANCLA)
    resultado = {"artefacto": "mutacion AC6 sobre el guard real",
                 "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "archivo_mutado": OBJETIVO.relative_to(ROOT).as_posix(),
                 "nodo_que_debe_caer": NODO,
                 "ocurrencias_del_literal": ocurrencias,
                 "sha_original_12": sha_antes[:12],
                 "simbolo_no_apagado": ("no se toca GUARD_ADITIVIDAD_ACTIVO: se corta el texto de la "
                                        "clausula de reinsercion, que es la otra mitad del guard")}
    if ocurrencias != 1:
        resultado["aplicado"] = False
        resultado["motivo_no_aplicado"] = (
            f"el ancla aparece {ocurrencias} veces: no se muta sin ancla unica")
        Path(destino).write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("[NO-APLICADO]", resultado["motivo_no_aplicado"])
        return 3

    mutado = lf.replace(ANCLA, MUTANTE, 1).encode("utf-8")
    try:
        OBJETIVO.write_bytes(mutado)
        sha_mutante = sha(OBJETIVO.read_bytes())
        resultado["aplicado"] = True
        resultado["sha_mutante_12"] = sha_mutante[:12]
        resultado["rojo_con_el_mutante"] = correr_nodo()
    finally:
        OBJETIVO.write_bytes(originales)
        sha_despues = sha(OBJETIVO.read_bytes())
        resultado["restaurado_12"] = sha_despues[:12]
        resultado["restauracion_coincide"] = sha_despues == sha_antes

    resultado["verde_tras_restaurar"] = correr_nodo()
    git = subprocess.run(["git", "status", "--porcelain", "--",
                          OBJETIVO.relative_to(ROOT).as_posix()], capture_output=True, cwd=str(ROOT),
                         text=True, encoding="utf-8", errors="replace")
    resultado["git_status_del_archivo_despues"] = git.stdout.strip() or "(limpio)"
    Path(destino).write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: resultado[k] for k in
                      ("aplicado", "sha_original_12", "sha_mutante_12", "restaurado_12",
                       "restauracion_coincide", "git_status_del_archivo_despues")}, ensure_ascii=False))
    print("ROJO :", resultado["rojo_con_el_mutante"])
    print("VERDE:", resultado["verde_tras_restaurar"])
    return 0 if (resultado["restauracion_coincide"]
                 and resultado["rojo_con_el_mutante"]["codigo_de_salida"] != 0
                 and resultado["verde_tras_restaurar"]["codigo_de_salida"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
