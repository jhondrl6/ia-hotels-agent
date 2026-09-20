"""FASE-0 / T3 — mutaciones del guard real (AC15 / AC20).

Instrumento: cada mutacion se aplica sobre el ARCHIVO VIVO, se corre `pytest`
sobre los tests que la gobiernan, y se restaura de una copia byte-a-byte y el
sha256 resultante se verifica despues de escribir. PRE no esta en juego: la corrida ya esta
capturada en `tests_baseline_pre.txt`.

Por que no una copia temporal del repo: los tests de esta fase importan `main` y
paquetes completos de `modules/`; un sandbox con los 9 archivos sueltos produce
rojos por `ImportError`, y AC15 los declara evidencia inutil ("no aceptar rojos
por syntax/import en vez del guard").

Incluye dos mutaciones PROHIBIDAS por el plan (M5, M6) con un fin distinto: no
compran el verde de la fase, demuestran que los tests que vigilan ese limite estan
vivos. Si alguien relaja el detector o barre la anotacion SR-H2, algo rompe.
"""

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent
TEST_FILES = [
    "tests/test_fase_0_ac20_evidencia_veredicto.py",
    "tests/quality_gates/test_publication_gates.py",
    "tests/quality_gates/tribunal/test_diagnosis_reviewer.py",
    "tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py",
    "tests/test_ac_g3_package_evidence.py",
]

MUTATIONS = [
    SimpleNamespace(
        mid="M1",
        ac="AC20-i",
        prohibida=False,
        que="apagar la anotacion del camino FUNDADO (dejar solo el derivado SR-H2)",
        objetivo="TestAnotacionDelCaminoFundado + TestCaminoFundadoSobreBaselineReal",
        edit=(Path("modules/quality_gates/publication_gates.py"),
              "        if critical_issues:\n"
              "            missed = self._evident_critical_missed(assessment, list(critical_issues))",
              "        if False:  # MUTA-M1: el fundado vuelve a viajar mudo\n"
              "            missed = self._evident_critical_missed(assessment, list(critical_issues))"),
        tests=["tests/test_fase_0_ac20_evidencia_veredicto.py",
               "tests/quality_gates/test_publication_gates.py",
               "tests/quality_gates/tribunal/test_diagnosis_reviewer.py"],
    ),
    SimpleNamespace(
        mid="M2",
        ac="AC20-ii",
        prohibida=False,
        que="quitar la proyeccion `findings` de `ReviewerReport.to_dict`",
        objetivo="TestToDictPublicaHallazgos + TestActaPublicaLaCausa + AC-E1 (forma del acta)",
        edit=(Path("modules/quality_gates/tribunal/outcome.py"),
              '            "findings": [\n'
              '                projected\n'
              '                for projected in (\n'
              '                    _acta_finding_projection(f) for f in self.findings[:ACTA_FINDING_CAP]\n'
              '                )\n'
              '                if projected is not None\n'
              '            ],',
              '            # MUTA-M2: sin proyeccion de hallazgos (forma legacy)'),
        tests=["tests/test_fase_0_ac20_evidencia_veredicto.py",
               "tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py"],
    ),
    SimpleNamespace(
        mid="M3",
        ac="AC20-iii",
        prohibida=False,
        que="quitar la llamada de evidencia en la rama publish de `run_v4_complete_mode`",
        objetivo="TestCableadoPublishPublicaEvidencia (regla AST propia, L-V2.2)",
        edit=(Path("main.py"),
              '                delivery_zip_path = packager.publish(quarantine_tmp_path)\n'
              '                print(f"   [OK] Delivery package created: {delivery_zip_path}")\n'
              '                _record_published_package_evidence(\n'
              '                    tribunal_acta, delivery_zip_path, v4_audit_dir\n'
              '                )',
              '                delivery_zip_path = packager.publish(quarantine_tmp_path)\n'
              '                print(f"   [OK] Delivery package created: {delivery_zip_path}")\n'
              '                # MUTA-M3: se publica sin registrar evidencia'),
        tests=["tests/test_fase_0_ac20_evidencia_veredicto.py"],
    ),
    SimpleNamespace(
        mid="M4",
        ac="AC20-iii",
        prohibida=False,
        que="el helper sigue siendo llamado pero ya no anota `package_evidence` en el acta",
        objetivo="TestPackageEvidenceEnRamaPublish::test_del_paquete_entregado",
        edit=(Path("main.py"),
              '        tribunal_acta["package_evidence"] = {\n'
              '            "suppressed": False,',
              '        tribunal_acta["MUTA_M4"] = {\n'
              '            "suppressed": False,'),
        tests=["tests/test_fase_0_ac20_evidencia_veredicto.py"],
    ),
    SimpleNamespace(
        mid="M5",
        ac="AC20-i (limite prohibido por el plan)",
        prohibida=True,
        que="relajar `DiagnosisReviewer._check_vacuous_recall` para que deje de denunciar",
        objetivo="test_recall_declarado_sin_lista_sin_audit_sigue_vacio + suite del revisor",
        edit=(Path("modules/quality_gates/tribunal/diagnosis_reviewer.py"),
              "        if recall_value == 1.0 and not has_critical_count:",
              "        if False and recall_value == 1.0 and not has_critical_count:  # MUTA-M5"),
        tests=["tests/test_fase_0_ac20_evidencia_veredicto.py",
               "tests/quality_gates/tribunal/test_diagnosis_reviewer.py"],
    ),
    SimpleNamespace(
        mid="M6",
        ac="AC20-i (limite prohibido por el plan)",
        prohibida=True,
        que="sustituir (en vez de sumar) la anotacion SR-H2: `details` vacios con cero criticos",
        objetivo="TestCriticalRecallGate::test_empty_critical_issues_with_audit_passes",
        edit=(Path("modules/quality_gates/publication_gates.py"),
              '        if (\n'
              '            "critical_recall" not in assessment\n'
              '            and not critical_issues\n'
              '            and assessment.get("audit_schema")\n'
              '        ):',
              '        if False:  # MUTA-M6: se barre la serie heredada de SR-H2'),
        tests=["tests/quality_gates/test_publication_gates.py",
               "tests/test_fase_0_ac20_evidencia_veredicto.py"],
    ),
]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _run(tests) -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *tests, "-q", "--no-header",
         "-p", "no:cacheprovider", "--tb=no"],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
    summary = next((ln for ln in reversed(lines) if " passed" in ln or " failed" in ln
                    or " error" in ln.lower()), lines[-1] if lines else "(sin salida)")
    rojos = [ln for ln in lines if ln.startswith("FAILED") or ln.startswith("ERROR")]
    return {
        "exit_code": proc.returncode,
        "resumen": summary,
        "causa_rojo": sorted({ln.split("::")[0] for ln in rojos})[:6],
        "rojos": rojos[:12],
    }


def main():
    archivos = sorted({str(m.edit[0]) for m in MUTATIONS})
    respaldos = {}
    informe = {"seleccion_de_tests": TEST_FILES, "archivos_mutables": archivos, "mutaciones": []}

    for rel in archivos:
        path = REPO / rel
        backup = EVIDENCE / "_respaldo" / Path(rel).name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, backup)
        respaldos[rel] = {"sha_antes": _sha(path), "backup": str(backup.relative_to(EVIDENCE))}

    try:
        sombra = _run(TEST_FILES)
        informe["sombra_sin_mutar"] = sombra
        for mut in MUTATIONS:
            rel, old, new = mut.edit
            path = REPO / rel
            text = path.read_text(encoding="utf-8")
            if old not in text:
                informe["mutaciones"].append({
                    "mutacion": mut.mid, "ac": mut.ac, "aplicada": False,
                    "motivo": "el ancla no existe: el guard ya no es el simbolo que se muto",
                })
                continue
            path.write_text(text.replace(old, new, 1), encoding="utf-8")
            despues = _run(mut.tests)
            path.write_text(text, encoding="utf-8")
            restaurado = _sha(path) == respaldos[str(rel)]["sha_antes"]
            informe["mutaciones"].append({
                "mutacion": mut.mid,
                "ac": mut.ac,
                "prohibida_por_el_plan": mut.prohibida,
                "que_se_rompe": mut.que,
                "guard_objetivo": mut.objetivo,
                "tests": mut.tests,
                "aplicada": True,
                "antes": {"exit_code": 0 if not sombra else sombra["exit_code"]},
                "despues": despues,
                "rompio": despues["exit_code"] != 0,
                "causa_del_rojo": (
                    "guard" if despues["exit_code"] != 0
                    else "NO ROMPIO: el test no alcanza la rama (L-T4A.5)"
                ),
                "restaurado_sha256_ok": restaurado,
            })
    finally:
        for rel, meta in respaldos.items():
            path = REPO / rel
            if _sha(path) != meta["sha_antes"]:
                shutil.copyfile(EVIDENCE / meta["backup"], path)
            informe.setdefault("restauracion", {})[rel] = {
                "sha_esperado": meta["sha_antes"],
                "sha_final": _sha(path),
                "identico": _sha(path) == meta["sha_antes"],
            }

    informe["total_rompio"] = sum(1 for m in informe["mutaciones"] if m.get("rompio"))
    informe["total_aplicadas"] = sum(1 for m in informe["mutaciones"] if m.get("aplicada"))
    informe["todo_restaurado"] = all(
        v["identico"] for v in informe.get("restauracion", {}).values()
    )
    shutil.rmtree(EVIDENCE / "_respaldo", ignore_errors=True)
    (EVIDENCE / "mutation_report.json").write_text(
        json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({
        "sombra_sin_mutar": informe["sombra_sin_mutar"]["resumen"],
        "mutaciones": [
            {m["mutacion"]: [m.get("rompio"), m.get("causa_del_rojo"),
                             m.get("despues", {}).get("resumen")]}
            for m in informe["mutaciones"]
        ],
        "rompieron": f"{informe['total_rompio']}/{informe['total_aplicadas']}",
        "todo_restaurado": informe["todo_restaurado"],
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
