"""Arnés de mutación de FASE-G (AC15 · R2.8): cada verde tiene que deberse al guard.

Corre sobre el archivo VIVO pero restaura byte a byte al terminar (y lo verifica con sha256
antes y después). Ninguna mutación es de sintaxis ni de import: si un rojo llegara por
`SyntaxError` o `ModuleNotFoundError`, este arnés lo reporta como mutación INVALIDA, no
como guard funcionando.

Uso:  ./venv/Scripts/python.exe temp/mutaciones_fase_g.py
Salida: JSON por mutación a stdout (se archiva en evidence/FASE-G/mutation_report.json).
"""
from __future__ import annotations

import hashlib
import os
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIVOS = {
    "verificador": ROOT / "scripts" / "validate_wiring.py",
    "quick": ROOT / "scripts" / "run_all_validations.py",
    "builder": ROOT / "modules" / "assessment_builder.py",
}
FIRMAS = {k: hashlib.sha256(v.read_bytes()).hexdigest() for k, v in VIVOS.items()}

# (nombre, archivo, viejo, nuevo, test o comando, asercion que debe aparecer en el rojo)
MUTACIONES = [
    {
        "id": "M1",
        "ac": "AC7",
        "guard": "politica GOBERNADOS (la tabla de senales exigidas)",
        "que_se_debilta": "vacia la politica: el verificador deja de exigir senales",
        "archivo": "verificador",
        # Vaciar la politica DESPUES de su literal: una sustitucion dentro del
        # `= {` daría SyntaxError, y un rojo por sintaxis no prueba el guard (AC15).
        "viejo": 'NOMBRES_GOBERNADOS = {metodo for (_cls, metodo) in GOBERNADOS}',
        "nuevo": 'GOBERNADOS.clear()' + chr(10) + 'NOMBRES_GOBERNADOS = set()',
        "objetivo": ["-q", "tests/test_validate_wiring.py::"
                     "test_caller_nuevo_en_archivo_nuevo_que_omite_la_senal_rompe"],
        "debe_decir": "assert 0 == 1",
    },
    {
        "id": "M2",
        "ac": "AC7",
        "guard": "clasificacion KWARGS_OPACOS",
        "que_se_debilta": "permite esconder la senal detras de **kwargs",
        "archivo": "verificador",
        "viejo": "elif hay_kwargs_opacos and ausentes:",
        "nuevo": "elif False and hay_kwargs_opacos and ausentes:",
        "objetivo": ["-q", "tests/test_validate_wiring.py::"
                     "test_ocultar_la_senal_tras_kwargs_opacos_rompe"],
        "debe_decir": "KWARGS_OPACOS",
    },
    {
        "id": "M3",
        "ac": "AC7",
        "guard": "gobernar por clase resuelta (exclusion de homonimos)",
        "que_se_debilta": "gobierna por NOMBRE de metodo: `validate` de cualquier clase "
                          "entra en la poblacion",
        "archivo": "verificador",
        "viejo": "            politica = GOBERNADOS.get((clase, metodo)) if clase else None",
        "nuevo": ("            politica = next((p for (c, m), p in GOBERNADOS.items()"
                  " if m == metodo), None)"),
        "objetivo": ["-q", "tests/test_validate_wiring.py::"
                     "test_clases_validate_no_relacionadas_quedan_excluidas"],
        "debe_decir": "modules/ajeno.py",
    },
    {
        "id": "M4",
        "ac": "AC7",
        "guard": "baja automatica de una excepcion que ya no ampara nada",
        "que_se_debilta": "las excepciones tipadas se vuelven allowlist permanente "
                          "(una excepcion vaga ya no rompe)",
        "archivo": "verificador",
        "viejo": '            "tipo": "EXCEPCION_VAGA",',
        "nuevo": '            "tipo": "EXCEPCION_VAGA_MUTADA",',
        "objetivo": ["-q", "tests/test_validate_wiring.py::"
                     "test_excepcion_que_ya_no_ampa_nada_es_en_si_una_violacion"],
        "debe_decir": "EXCEPCION_VAGA",
    },
    {
        "id": "M5",
        "ac": "AC16",
        "guard": "retiro del contrato muerto `whatsapp_validation`",
        "que_se_debilta": "re-introduce el parametro descartado en la firma",
        "archivo": "builder",
        "viejo": "    def with_validation(\n        self,\n"
                 "        validation_summary: Dict[str, Any],\n    ) -> \"AssessmentBuilder\":",
        "nuevo": "    def with_validation(\n        self,\n"
                 "        validation_summary: Dict[str, Any],\n"
                 "        whatsapp_validation: Any = None,\n    ) -> \"AssessmentBuilder\":",
        "objetivo": ["-q", "tests/test_validate_wiring.py::"
                     "test_retiro_real_en_el_repo_deja_el_contrato_cerrado"],
        "debe_decir": "assert 'whatsapp_validation' not in",
    },
    {
        "id": "M6",
        "ac": "AC16",
        "guard": "deteccion del argumento prohibido en el caller",
        "que_se_debilta": "deja de mirar los argumentos prohibidos: un caller con la "
                          "firma vieja pasaria",
        "archivo": "verificador",
        "viejo": '            if vistos:',
        "nuevo": '            if False and vistos:',
        "objetivo": ["-q", "tests/test_validate_wiring.py::"
                     "test_caller_con_la_firma_vieja_rompe_el_contrato"],
        "debe_decir": "AssertionError: []",
    },
    {
        "id": "M7",
        "ac": "AC7",
        "guard": "registro del check dentro del modo rapido",
        "que_se_debilta": "des-registra el check del quick: el verde del rapido dejaria "
                          "de decir nada del cableado",
        "archivo": "quick",
        "viejo": "        self._check_wiring()\r\n",
        "nuevo": "",
        "objetivo": ["-q", "tests/test_validate_lesson_capitalization.py::"
                     "test_run_all_validations_registra_el_check_dentro_del_modo_rapido"],
        "debe_decir": "no son exactamente 1..11",
    },
]


def _leer(clave: str) -> str:
    return VIVOS[clave].read_text(encoding="utf-8", newline="")


def _escribir(clave: str, texto: str) -> None:
    VIVOS[clave].write_text(texto, encoding="utf-8", newline="")


def _restaurar_todo() -> list[str]:
    problemas = []
    for clave, ruta in VIVOS.items():
        if hashlib.sha256(ruta.read_bytes()).hexdigest() != FIRMAS[clave]:
            problemas.append(f"{ruta} no coincide con la firma guardada")
    return problemas


def main() -> int:
    resultados = []
    for mut in MUTACIONES:
        clave = mut["archivo"]
        original = _leer(clave)
        if original.count(mut["viejo"]) != 1:
            resultados.append({
                "id": mut["id"], "ac": mut["ac"], "aplicable": False,
                "motivo": f"ancla de mutacion encontrada "
                          f"{original.count(mut['viejo'])} veces",
            })
            continue
        _escribir(clave, original.replace(mut["viejo"], mut["nuevo"], 1))
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", *mut["objetivo"]],
                cwd=ROOT, capture_output=True, text=True, timeout=900,
                encoding="utf-8", errors="replace",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            salida = proc.stdout + proc.stderr
            invalida = ("SyntaxError" in salida or "ModuleNotFoundError" in salida
                        or "ImportError" in salida or "error: no tests ran" in salida)
            resultados.append({
                "id": mut["id"], "ac": mut["ac"], "aplicable": True,
                "guard": mut["guard"], "que_se_debilta": mut["que_se_debilta"],
                "test_objetivo": " ".join(mut["objetivo"]),
                "exit_code": proc.returncode,
                "rompio": proc.returncode != 0,
                "rojo_por_el_guard": (proc.returncode != 0 and not invalida),
                "vio_la_asercion_esperada": mut["debe_decir"] in salida,
                "invalida_por_syntax_o_import": invalida,
                "extracto_ultima_linea": [
                    l for l in salida.splitlines() if l.startswith("FAILED")
                    or "Error" in l][:3],
            })
        finally:
            _escribir(clave, original)

    restauracion = _restaurar_todo()
    informe = {
        "plan": "REFACTOR-WHATSAPP-ENTREGA-2026-09-18",
        "fase": "FASE-G",
        "instrumento": "temp/mutaciones_fase_g.py (R2.8: sin el rojo no hay verde)",
        "reglas": [
            "cada mutacion debilita el GUARD real, no la asercion del test",
            "un rojo por SyntaxError/ImportError no cuenta como guard funcionando",
            "el worktree se restaura byte a byte y se verifica por sha256",
            "los tres anclajes de M3/M6/M7 se corrigieron tras la primera corrida: el rojo era el correcto pero el texto esperado no coincidia con lo que imprime pytest (pytest trunca el dict de la violacion en M3; M6 falla con lista vacia; M7 falla por coherencia de ordinales, no por la cadena `_check_wiring`)",
        ],
        "mutaciones": resultados,
        "aplicadas": sum(1 for r in resultados if r.get("aplicable")),
        "con_rojo_del_guard": sum(1 for r in resultados if r.get("rojo_por_el_guard")),
        "asercion_esperada_en_el_rojo": sum(
            1 for r in resultados if r.get("vio_la_asercion_esperada")),
        "worktree_restaurado_sin_pendencias": not restauracion,
        "problemas_de_restauracion": restauracion,
    }
    print(json.dumps(informe, indent=2, ensure_ascii=False))
    return 0 if not restauracion else 1


if __name__ == "__main__":
    sys.exit(main())
