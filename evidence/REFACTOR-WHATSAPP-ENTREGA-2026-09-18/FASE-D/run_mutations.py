"""FASE-D: mutantes del veredicto canonico y de las causas serializadas.

Cada mutante se aplica sobre el archivo vivo con ancla unica (si el literal
aparece mas de una vez, el mutante se declara NO-APLICABLE en vez de morder la
rama equivocada), corre la bateria de D y se restaura el archivo. La restauracion
se verifica por sha256 contra el capturado al inicio: un mutante que no vuelve a
su estado original invalida todo el informe.

Uso:
  ./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-D/run_mutations.py
"""

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
SELECCION = ["tests/quality_gates/test_fase_d_veredicto_canonico.py"]

MUTANTES = [
    {
        "id": "M1",
        "que": "restaurar la decision por score solo en el pre-gate",
        "archivo": "main.py",
        "viejo": "    passed = coherence_verdict_passes(report.overall_score, threshold, report.is_coherent)",
        "nuevo": "    passed = report.overall_score >= threshold",
        "cae_por": ["test_veredicto_falso_con_score_alto_bloca_antes_de_generar"],
    },
    {
        "id": "M2",
        "que": "omitir la propagacion de los checks culpables al assessment",
        "archivo": "modules/assessment_builder.py",
        "viejo": '            failed_error_checks(source) if hasattr(source, "checks") else None',
        "nuevo": "            [] if hasattr(source, \"checks\") else None",
        "cae_por": ["test_fallback_sin_reporte_del_orquestador_usa_el_del_pre_gate"],
    },
    {
        "id": "M3",
        "que": "no publicar los culpables en details del gate de coherencia",
        "archivo": "modules/quality_gates/publication_gates.py",
        "viejo": '        failed = assessment.get("coherence_failed_checks")\n        if not isinstance(failed, list):\n            return {}',
        "nuevo": '        return {}  # MUTANTE\n        failed = assessment.get("coherence_failed_checks")\n        if not isinstance(failed, list):\n            return {}',
        "cae_por": ["test_dos_errores_conservan_ambos_nombres_en_el_json_real"],
    },
    {
        "id": "M4",
        "que": "quitar el guard de entrada a FASE 4 (generar aunque el veredicto corte)",
        "archivo": "main.py",
        "viejo": "    if pre_gate_blocked:\n        print(\"   [SKIP] FASE 4 omitida",
        "nuevo": "    if False:  # MUTANTE\n        print(\"   [SKIP] FASE 4 omitida",
        "cae_por": ["test_score_alto_con_veredicto_falso_no_invoca_al_generador"],
    },
    {
        "id": "M5",
        "que": "dejar neutro el guard de la entrada directa del orquestador",
        "archivo": "modules/asset_generation/v4_asset_orchestrator.py",
        "viejo": "    if (not coherence.is_coherent and coherence.overall_score < 0.5) or guilty:",
        "nuevo": "    if False and (not coherence.is_coherent and coherence.overall_score < 0.5) or guilty:",
        "cae_por": ["test_suelo_de_score_bajo_sigue_vigente"],
    },
    {
        "id": "M6",
        "que": "no escribir la firma de culpables en el artefacto del pre-gate",
        "archivo": "main.py",
        "viejo": '    payload["failed_error_check_names"] = [c["name"] for c in guilty]',
        "nuevo": "    pass  # MUTANTE: no se publica la firma",
        "cae_por": ["test_artefacto_conserva_los_dos_culpables_y_la_causa"],
    },
]

PY = sys.executable


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def correr_pytest() -> dict:
    proc = subprocess.run(
        [PY, "-m", "pytest", *SELECCION, "-q", "--no-header", "-p", "no:warnings", "--tb=no"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    salida = (proc.stdout or "") + (proc.stderr or "")
    caidos = sorted(set(re.findall(r"^FAILED [^:]+::(?:\w+::)*(\w+)", salida, flags=re.M)))
    resumen = ""
    for linea in reversed(salida.splitlines()):
        if "passed" in linea or "failed" in linea or "error" in linea:
            resumen = linea.strip()
            break
    return {
        "exit": proc.returncode,
        "resumen": resumen,
        "pruebas_caidas": caidos,
        "coleccion_vacia": "1 passed" not in salida and not caidos,
    }


def main() -> int:
    archivos = sorted({m["archivo"] for m in MUTANTES})
    originales = {a: (ROOT / a).read_bytes() for a in archivos}
    shas_antes = {a: sha256(ROOT / a) for a in archivos}

    informe = []
    for mutante in MUTANTES:
        ruta = ROOT / mutante["archivo"]
        texto = originales[mutante["archivo"]].decode("utf-8")
        ocurrencias = texto.count(mutante["viejo"])
        registro = {
            "id": mutante["id"],
            "que": mutante["que"],
            "archivo": mutante["archivo"],
            "ancla_unica": ocurrencias == 1,
            "ocurrencias": ocurrencias,
        }
        if ocurrencias != 1:
            registro["estado"] = "NO-APLICABLE (ancla no unica)"
            informe.append(registro)
            continue

        ruta.write_bytes(texto.replace(mutante["viejo"], mutante["nuevo"], 1).encode("utf-8"))
        try:
            resultado = correr_pytest()
        finally:
            ruta.write_bytes(originales[mutante["archivo"]])

        registro.update(resultado)
        registro["restaurado"] = sha256(ruta) == shas_antes[mutante["archivo"]]
        registro["esperada_cayo"] = all(
            t in resultado["pruebas_caidas"] for t in mutante["cae_por"]
        )
        registro["rojo_por_causa_correcta"] = (
            registro["esperada_cayo"]
            and resultado["exit"] != 0
            and not resultado["coleccion_vacia"]
        )
        informe.append(registro)

    shas_despues = {a: sha256(ROOT / a) for a in archivos}
    arbol_intacto = shas_despues == shas_antes
    resumen = {
        "generado": datetime.now().isoformat(),
        "seleccion": SELECCION,
        "mutantes": informe,
        "aplicados": sum(1 for r in informe if "exit" in r),
        "rojos_por_causa_correcta": sum(1 for r in informe if r.get("rojo_por_causa_correcta")),
        "arbol_intacto_por_sha": arbol_intacto,
        "shas": shas_despues,
    }
    (EV / "mutation_report.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps(
        {
            "aplicados": resumen["aplicados"],
            "rojos_por_causa_correcta": resumen["rojos_por_causa_correcta"],
            "arbol_intacto_por_sha": arbol_intacto,
            "detalle": [
                {
                    "id": r["id"],
                    "exit": r.get("exit"),
                    "caidas": len(r.get("pruebas_caidas", [])),
                    "causa_correcta": r.get("rojo_por_causa_correcta"),
                    "restaurado": r.get("restaurado"),
                }
                for r in informe
            ],
        },
        indent=2,
        ensure_ascii=False,
    ))
    return 0 if (arbol_intacto and resumen["rojos_por_causa_correcta"] == resumen["aplicados"]) else 1


if __name__ == "__main__":
    sys.exit(main())
