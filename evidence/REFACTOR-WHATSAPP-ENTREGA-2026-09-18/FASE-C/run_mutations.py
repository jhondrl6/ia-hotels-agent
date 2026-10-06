"""FASE-C / T3 — mutantes de los guards (AC3, AC6, AC19a) y su restauración por sha.

Cada mutación se aplica sobre el archivo vivo, se corre la selección que debe
romperse, y se restaura el bytes-exact original verificado por sha256. Un mutante
que no rompe NADA significa un guard sin dientes (L-VUP-5); un mutante que rompe
la expectativa equivocada significa anclaje flojo.

Salida: `mutation_report.json` en este directorio.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EV = Path(__file__).resolve().parent
PY = str(REPO / "venv" / "Scripts" / "python.exe")

BATERIA = "tests/asset_generation/test_fase_c_boton_seguro.py"

MUTANTES = [
    {
        "id": "M1",
        "nombre": "guard DIGITOS_NO_ASCII apagado",
        "archivo": "modules/data_validation/whatsapp_contract.py",
        "old": '    if any(c.isdigit() and c not in ASCII_DIGITS for c in sin_separadores):\n        return None, "DIGITOS_NO_ASCII"',
        "new": '    if False:  # MUTANTE M1\n        return None, "DIGITOS_NO_ASCII"',
        "objetivo": [BATERIA],
        "causa_esperada": "DIGITOS_NO_ASCII",
    },
    {
        "id": "M2",
        "nombre": "banda de longitud internacional apagada",
        "archivo": "modules/data_validation/whatsapp_contract.py",
        "old": '    if not (LONGITUD_MIN <= len(sin_separadores) <= LONGITUD_MAX):\n        return None, "LONGITUD_INVALIDA"',
        "new": '    if False:  # MUTANTE M2\n        return None, "LONGITUD_INVALIDA"',
        "objetivo": [BATERIA],
        "causa_esperada": "LONGITUD_INVALIDA",
    },
    {
        "id": "M3",
        "nombre": "retorno al recorte silencioso del renderer (''.join isdigit)",
        "archivo": "modules/asset_generation/conditional_generator.py",
        "old": '        digitos, causa = rechazo_numero_whatsapp(phone_number)\n        if causa:\n            raise NumeroWhatsAppNoUtilizable(causa, phone_number, origen=origen)\n        clean_phone = digitos',
        "new": '        clean_phone = \'\'.join(c for c in str(phone_number) if c.isdigit())  # MUTANTE M3',
        "objetivo": [BATERIA, "tests/asset_generation/test_whatsapp_button.py"],
        "causa_esperada": "VACIO",
    },
    {
        "id": "M4",
        "nombre": "boost a 0.95 por mere `exists` restaurado",
        "archivo": "modules/commercial_documents/coherence_validator.py",
        "old": '        # o UNKNOWN pasaba la barra de 0.9 sin que nadie la bajara.\n        if confidence_score >= threshold:',
        "new": '        # o UNKNOWN pasaba la barra de 0.9 sin que nadie la bajara.\n        if site_presence_report and site_presence_report.get("whatsapp_button", {}).get("status") == "exists":  # MUTANTE M4\n            confidence_score = max(confidence_score, 0.95)\n        if confidence_score >= threshold:',
        "objetivo": [BATERIA, "tests/asset_generation/test_site_presence_adapter.py"],
        "causa_esperada": "score >= 0.9 con CONFLICT/UNKNOWN/ESTIMATED",
    },
    {
        "id": "M5",
        "nombre": "FIX-A2 restaurado: phone_web vuelve a escribir la clave del botón",
        "archivo": "modules/asset_generation/v4_asset_orchestrator.py",
        "old": '            validated_data["whatsapp"] = validated_data.get("whatsapp_number", "")',
        "new": '            validated_data["whatsapp"] = validated_data.get("phone_web", "")  # MUTANTE M5',
        "objetivo": [BATERIA],
        "causa_esperada": "destino = phone_web",
    },
    {
        "id": "M6",
        "nombre": "fallo de transporte vuelve a declararse lectura OK",
        "archivo": "modules/asset_generation/site_presence_checker.py",
        "old": '                "read_status": READ_ERROR,\n                "presence_evidence_kind": EVIDENCE_NONE,\n                "error_tipo": type(exc).__name__,',
        "new": '                "read_status": READ_OK,  # MUTANTE M6\n                "presence_evidence_kind": EVIDENCE_NONE,\n                "error_tipo": type(exc).__name__,',
        "objetivo": [BATERIA],
        "causa_esperada": "READ_ERROR → not_exists",
    },
    {
        "id": "M7",
        "nombre": "huella de plugin clasificada como href con número",
        "archivo": "modules/asset_generation/site_presence_checker.py",
        "old": '                    presence_evidence_kind=html_result.get(\n                        "presence_evidence_kind", EVIDENCE_NONE\n                    ),',
        "new": '                    presence_evidence_kind=EVIDENCE_WA_ME_HREF,  # MUTANTE M7',
        "objetivo": [BATERIA],
        "causa_esperada": "plugin_fingerprint → wa.me_href",
    },
    {
        "id": "M8",
        "nombre": "observation_scope eliminado (alcance vuelve a ser invisible)",
        "archivo": "modules/asset_generation/site_presence_checker.py",
        "old": '    return {\n        "routes_inspected": [site_url],\n        "crawl": False,\n        "nivel": "raiz",\n    }',
        "new": '    return None  # MUTANTE M8',
        "objetivo": [BATERIA],
        "causa_esperada": "observation_scope ausente",
    },
    {
        "id": "M9",
        "nombre": "confianza de la sonda HTML promocionada de 0.85 a 0.95",
        "archivo": "modules/asset_generation/site_presence_checker.py",
        "old": '                    confidence=0.85,\n                    read_status=html_result.get("read_status", READ_OK),',
        "new": '                    confidence=0.95,  # MUTANTE M9\n                    read_status=html_result.get("read_status", READ_OK),',
        "objetivo": [BATERIA],
        "causa_esperada": "huella por encima de la barra 0.9",
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def correr(test_ids):
    proc = subprocess.run(
        [PY, "-m", "pytest", *test_ids, "-q", "--tb=no", "-p", "no:randomly"],
        cwd=str(REPO), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    rojos = [l.split(" ")[1] for l in proc.stdout.splitlines() if l.startswith("FAILED ")]
    resumen = [l for l in proc.stdout.splitlines() if " passed" in l or " failed" in l]
    return proc.returncode, rojos, resumen[-1] if resumen else "(sin resumen)"


reporte = {"fase": "FASE-C", "plan": "REFACTOR-WHATSAPP-ENTREGA-2026-09-18",
           "instrumento": "run_mutations.py", "mutantes": []}

for mut in MUTANTES:
    ruta = REPO / mut["archivo"]
    original = ruta.read_bytes()
    sha_antes = hashlib.sha256(original).hexdigest()
    texto = original.decode("utf-8")
    ocurrencias = texto.count(mut["old"])
    entrada = {"id": mut["id"], "nombre": mut["nombre"], "archivo": mut["archivo"],
               "ancla_unica": ocurrencias == 1, "causa_esperada": mut["causa_esperada"]}
    if ocurrencias != 1:
        entrada["estado"] = f"ANCLA-AMBIGUA ({ocurrencias} ocurrencias)"
        reporte["mutantes"].append(entrada)
        continue
    try:
        ruta.write_bytes(texto.replace(mut["old"], mut["new"], 1).encode("utf-8"))
        exit_code, rojos, resumen = correr(mut["objetivo"])
        entrada.update({
            "estado": "ROJO" if exit_code != 0 else "VERDE-PERSISTENTE",
            "exit": exit_code,
            "resumen": resumen,
            "pruebas_rotas": rojos,
            "rompio_alguna_distinta": bool(rojos),
        })
    finally:
        ruta.write_bytes(original)
        entrada["sha_antes"] = sha_antes
        entrada["sha_despues"] = sha(ruta)
        entrada["restaurado_por_sha"] = entrada["sha_antes"] == entrada["sha_despues"]
    reporte["mutantes"].append(entrada)

rotos = sum(1 for m in reporte["mutantes"] if m.get("estado") == "ROJO")
restaurados = sum(1 for m in reporte["mutantes"] if m.get("restaurado_por_sha"))
reporte["total"] = len(MUTANTES)
reporte["rojos_causados_por_el_guard"] = rotos
reporte["restaurados_verificados_por_sha256"] = restaurados

(EV / "mutation_report.json").write_text(
    json.dumps(reporte, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
)
print(f"mutantes={len(MUTANTES)} rojos={rotos} restaurados_sha={restaurados}")
for m in reporte["mutantes"]:
    print(f"{m['id']}: {m['estado']} | {len(m.get('pruebas_rotas', []))} rotas | sha_ok={m.get('restaurado_por_sha')}")
sys.exit(0 if rotos == len(MUTANTES) and restaurados == len(MUTANTES) else 1)
