"""FASE-B — mutaciones AC1/AC2/AC19 con restauracion verificada por sha256.

Cada mutación debilita UN guard del producto (no la asercion del test) y se ejecuta la
seleccion que debe ponerse roja. Se restaura el original en memoria y se comprueba el
sha256 en disco: un verde que sobrevive a la mutacion seria evidencia de que el test no
toca la rama que dice certificar (L-T4A.5, L-VUP-5).
"""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PY = str(ROOT / "venv" / "Scripts" / "python.exe")
EVID = ROOT / "evidence" / "REFACTOR-WHATSAPP-ENTREGA-2026-09-18" / "FASE-B"

ORQ = "modules/asset_generation/v4_asset_orchestrator.py"
MAPPER = "modules/commercial_documents/pain_solution_mapper.py"
SETUP = "modules/asset_generation/whatsapp_setup_guide.py"
WIRING = "scripts/validate_wiring.py"

TESTS_AC1 = ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py::test_ac1_el_orquestador_propaga_la_senal_a_los_tres_productores"]
TESTS_AC1_HTML = ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py"]
TESTS_AC2_CONFL = ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py::test_ac2_conflicto_ya_no_fuerza_el_boton"]
TESTS_AC2_AUSE = ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py::test_ac2_la_ausencia_promete_setup_y_no_boton"]
TESTS_AC2_GUIA = ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py::test_ac2_la_guia_no_contiene_numero_ni_enlace_y_se_genera"]

MUTACIONES = [
    {
        "id": "M1",
        "guard": "AC1 · senal propagate a detect_pains",
        "archivo": ORQ,
        "old": "            analytics_data,\n            whatsapp_html_detected=whatsapp_html_detected,\n        )",
        "new": "            analytics_data,\n        )",
        "tests": TESTS_AC1,
        "espera": "rojo por AST: la invocacion pierde el kwarg",
        "extra": "wiring",
    },
    {
        "id": "M2",
        "guard": "AC1 · las TRES invocaciones, no una",
        "archivo": ORQ,
        "old": "            whatsapp_html_detected=whatsapp_html_detected,  # FASE-B (AC1)\n            site_presence_report=site_presence_report,  # FASE-2 (DT4-R2)",
        "new": "            site_presence_report=site_presence_report,  # FASE-2 (DT4-R2)",
        "tests": TESTS_AC1_HTML,
        "espera": "rojo: pre-gen sin senal (y wiring lo reporta)",
        "extra": "wiring",
    },
    {
        "id": "M3",
        "guard": "AC2 · can_generate incondicional retirado",
        "archivo": MAPPER,
        "old": "            can_generate = avg_confidence >= min_confidence\n            reason = (\n                f\"Confidence {avg_confidence:.2f} vs required {min_confidence}\"",
        "new": "            can_generate = True if pain_id == \"whatsapp_conflict\" else avg_confidence >= min_confidence\n            reason = (\n                f\"Confidence {avg_confidence:.2f} vs required {min_confidence}\"",
        "tests": TESTS_AC2_CONFL,
        "espera": "rojo: el conflicto vuelve a prometer boton listo",
    },
    {
        "id": "M4",
        "guard": "AC2 · ausencia promete setup",
        "archivo": MAPPER,
        "old": "\"assets\": [\"whatsapp_setup_guide\"],",
        "new": "\"assets\": [\"whatsapp_button\"],",
        "tests": TESTS_AC2_AUSE,
        "espera": "rojo: la ausencia ofrece boton operativo otra vez",
    },
    {
        "id": "M5",
        "guard": "AC2 · la guia no lleva numero ni enlace",
        "archivo": SETUP,
        "old": '    _CAMPO_PENDIENTE = "<Numero WhatsApp a confirmar por el hotel>"',
        "new": '    _CAMPO_PENDIENTE = "+573001234567"',
        "tests": TESTS_AC2_GUIA,
        "espera": "rojo: la guia de preparacion publica un numero (y con el, un destino)",
    },
    {
        "id": "M6",
        "guard": "AC7/B · excepciones tipadas retiradas",
        "archivo": WIRING,
        "old": "EXCEPCIONES: list[dict] = [\n    # FASE-B",
        "new": "EXCEPCIONES: list[dict] = [\n    {\"tipo\": \"HALLAZGO_CONOCIDO\", \"archivo\": \"modules/asset_generation/v4_asset_orchestrator.py\",\n     \"simbolo\": \"PainSolutionMapper.detect_pains\", \"senal\": \"whatsapp_html_detected\",\n     \"motivo\": \"mutante\", \"dueno\": \"FASE-B\", \"ac\": \"AC1\", \"baja_cuando\": \"nunca\"},\n    # FASE-B",
        "tests": ["tests/test_validate_wiring.py::test_ignore_known_deja_ver_lo_que_tapan_las_excepciones"],
        "espera": "rojo: excepcion vigente sin hallazgo que amparar (EXCEPCION_VAGA)",
        "extra": "wiring",
    },
    {
        "id": "M7",
        "guard": "A1 · resolucion separada del universo contado",
        "archivo": "modules/asset_generation/proposal_asset_alignment.py",
        "old": "    for identidad in SERVICE_IDENTITIES\n    if identidad.counts_in_alignment\n}",
        "new": "    for identidad in SERVICE_IDENTITIES\n    if True\n}",
        "tests": ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py::test_ac2_tabla_de_resolucion_separada_del_universo_contado"],
        "espera": "rojo: el servicio condicional entra al universo contado del gate",
    },
    {
        "id": "M8",
        "guard": "A1 · la tabla de resolucion cubre el registro completo",
        "archivo": "modules/asset_generation/proposal_asset_alignment.py",
        "old": "RESOLUCION_SERVICIO_A_ASSET: Dict[str, str] = {\n    identidad.service_name: identidad.asset_type\n    for identidad in SERVICE_IDENTITIES\n}",
        "new": "RESOLUCION_SERVICIO_A_ASSET: Dict[str, str] = dict(PROPOSAL_SERVICE_TO_ASSET)",
        "tests": ["tests/commercial_documents/test_fase_b_promesa_whatsapp.py::test_ac2_tabla_de_resolucion_separada_del_universo_contado"],
        "espera": "rojo: resolver vuelve a ser igual a contar (el doble uso que A1 separo)",
    },
]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def correr(ruta_archivos: list[str]) -> tuple[int, str]:
    r = subprocess.run([PY, "-m", "pytest", *ruta_archivos, "-q", "--tb=no", "-p", "no:warnings"],
                       cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def correr_wiring() -> tuple[int, str]:
    r = subprocess.run([PY, WIRING], cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    informe = {"fase": "FASE-B", "generado": datetime.now(timezone.utc).isoformat(),
               "instrumento": "run_mutations.py (mutar el guard, no la asercion)",
               "mutaciones": []}
    for mut in MUTACIONES:
        archivo = ROOT / mut["archivo"]
        bytes_originales = archivo.read_bytes()
        original = bytes_originales.decode("utf-8")
        sha_original = sha(archivo)
        if original.count(mut["old"]) < 1:
            informe["mutaciones"].append(
                {"id": mut["id"], "aplicada": False, "motivo": "ancla no encontrada"})
            continue
        # newline="": `open()` en modo texto convertiria \n a CRLF en Windows y el
        # sha256 de restauracion daria falso negativo (medido en esta fase: 1101/1309/
        # 875 fines de linea CRLF en tres archivos goberados).
        archivo.write_text(
            original.replace(mut["old"], mut["new"], 1), encoding="utf-8", newline=""
        )
        exito_tests, salida = correr(mut["tests"])
        exito_wiring, salida_wiring = (None, "")
        if mut.get("extra") == "wiring":
            exito_wiring, salida_wiring = correr_wiring()
        archivo.write_bytes(bytes_originales)
        restaurado = sha(archivo) == sha_original
        resumen = [l for l in salida.splitlines() if " passed" in l or " failed" in l][-1:]
        informe["mutaciones"].append({
            "id": mut["id"],
            "guard": mut["guard"],
            "archivo": mut["archivo"],
            "espera": mut["espera"],
            "pytest_exit_code": exito_tests,
            "pytest_resumen": resumen,
            "wiring_exit_code": exito_wiring,
            "wiring_linea": [l for l in salida_wiring.splitlines() if l.strip()][:1],
            "rojo_como_se_esperaba": exito_tests != 0,
            "restaurado_sha256": restaurado,
        })
        print(f"{mut['id']}: pytest={exito_tests} wiring={exito_wiring} restaurado={restaurado}")
    (EVID / "mutation_report.json").write_text(
        json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8")
    rotas = [m["id"] for m in informe["mutaciones"] if not m.get("rojo_como_se_esperaba", True)]
    no_restauradas = [m["id"] for m in informe["mutaciones"] if not m.get("restaurado_sha256", True)]
    print("VERDE PERSISTENTE (guard no sensible):", rotas or "ninguna")
    print("NO RESTAURADAS:", no_restauradas or "ninguna")
    return 1 if (rotas or no_restauradas) else 0


if __name__ == "__main__":
    sys.exit(main())
