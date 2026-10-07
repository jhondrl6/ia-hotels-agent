"""Harness de mutantes de la recuperacion AC6/AC10 (2026-10-07).

Cada entrada tumba UN guard nuevo, corre el test que debe sufrir y exige:
  (a) EXIT distinto de cero,
  (b) el nodo que falla es el nombrado (rojo POR SU CAUSA, no un collection error),
  (c) el archivo vuelve a su sha256 previo con `git status` sin residuo.

Escritura en binario: bajo Git Bash en Windows `open(..., 'w')` re-codifica a CRLF y
el blob del commit posterior ya no casa con el disco. Aqui se copian bytes.

Uso:
    python evidence/AC6-AC10-RECUPERACION-2026-10-07/run_mutations.py            # aplicar y restaurar
    python evidence/AC6-AC10-RECUPERACION-2026-10-07/run_mutations.py --keep M3   # dejar un mutante puesto
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

EVIDENCIA = Path(__file__).resolve().parent

CONTRATO = ROOT / "modules/data_validation/whatsapp_contract.py"
LOCAL = ROOT / "modules/asset_generation/local_content_generator.py"
PLANTILLA = ROOT / "modules/commercial_documents/templates/propuesta_v6_template.md"
CONTRATO_ASSETS = ROOT / "modules/geo_enrichment/asset_responsibility_contract.py"
REVISOR = ROOT / "modules/quality_gates/tribunal/asset_reviewer.py"

TESTS = {
    "real_plugin": "tests/asset_generation/test_reserva_whatsapp_desde_canal_ac6.py::test_caso_real_plugin_fingerprint_no_emite_wa_me",
    "otro_canal": "tests/asset_generation/test_reserva_whatsapp_desde_canal_ac6.py::test_telefono_de_otro_canal_no_suplanta_al_canal",
    "estado": "tests/asset_generation/test_reserva_whatsapp_desde_canal_ac6.py::test_estado_estimated_con_numero_casado_rechaza_por_estado",
    "evidencia": "tests/asset_generation/test_reserva_whatsapp_desde_canal_ac6.py::test_plugin_fingerprint_con_numero_casado_rechaza_por_clase_de_evidencia",
    "texto": "tests/asset_generation/test_reserva_whatsapp_desde_canal_ac6.py::test_caso_real_conserva_texto_sin_fabricar_destino",
    "handler": "tests/asset_generation/test_reserva_whatsapp_desde_canal_ac6.py::test_handler_pasa_el_canal_y_sin_href_no_hay_wa_me",
    "contacto": "tests/commercial_documents/test_contacto_propuesta_sin_whatsapp_hotel.py::test_bloque_contacto_no_emite_whatsapp_del_hotel",
    "despojo": "tests/geo_enrichment/test_orden_implementacion_nombres_reales_ac10.py::test_orden_no_vacio_con_nombres_reales",
    "fabrica": "tests/geo_enrichment/test_orden_implementacion_nombres_reales_ac10.py::test_los_nombres_reales_que_casan",
    "seccion": "tests/quality_gates/tribunal/test_impl_order_check_contenido_ac10.py::test_la_tarea_de_la_guia_no_cuenta_como_orden",
    "check": "tests/quality_gates/tribunal/test_impl_order_check_contenido_ac10.py::test_orden_vacio_del_paquete_certificado_reporta_rojo",
}

MUTANTES = [
    {
        "id": "M1",
        "guard": "destino_whatsapp_verificado: filtro de presencia `wa.me_href`",
        "archivo": CONTRATO,
        "original": b'    if canal.get("presence_evidence_kind") != EVIDENCE_WA_ME_HREF:\n        return None',
        "mutado": b'    if False:\n        return None',
        "test": "evidencia",
        "causa": "test_plugin_fingerprint_con_numero_casado_rechaza_por_clase_de_evidencia",
    },
    {
        "id": "M2",
        "guard": "destino_whatsapp_verificado: exige estado VERIFIED del canal",
        "archivo": CONTRATO,
        "original": b'    if canal.get("whatsapp_status") != ConfidenceLevel.VERIFIED.value:\n        return None',
        "mutado": b'    if False:\n        return None',
        "test": "estado",
        "causa": "test_estado_estimated_con_numero_casado_rechaza_por_estado",
    },
    {
        "id": "M3",
        "guard": "destino_whatsapp_verificado: el numero en uso casa con el del canal",
        "archivo": CONTRATO,
        "original": b'    if numero_en_uso not in (None, ""):\n        if normalizar_numero_whatsapp(numero_en_uso) != destino:\n            return None',
        "mutado": b'    if False:\n        pass',
        "test": "otro_canal",
        "causa": "test_telefono_de_otro_canal_no_suplanta_al_canal",
    },
    {
        "id": "M4",
        "guard": "_conclusion: el destino llega del canal, no de `hotel_data['phone']`",
        "archivo": LOCAL,
        "original": b'        region = location_context.get("region", state)\n        destino_whatsapp = self._destino_whatsapp(hotel_data)',
        "mutado": b'        region = location_context.get("region", state)\n        destino_whatsapp = re.sub(r"[^\\d+]", "", str(hotel_data.get("phone", ""))).lstrip("+") or None',
        "test": "texto",
        "causa": "test_caso_real_conserva_texto_sin_fabricar_destino",
    },
    {
        "id": "M5",
        "guard": "_build_internal_links: enlace solo con destino verificado",
        "archivo": LOCAL,
        "original": b'        hotel_name = hotel_data.get("name", "Hotel")\n        destino_whatsapp = self._destino_whatsapp(hotel_data)',
        "mutado": b'        hotel_name = hotel_data.get("name", "Hotel")\n        destino_whatsapp = re.sub(r"[^\\d+]", "", str(hotel_data.get("phone", ""))).lstrip("+") or None',
        "test": "real_plugin",
        "causa": "test_caso_real_plugin_fingerprint_no_emite_wa_me",
    },
    {
        "id": "M6",
        "guard": "bloque CONTACTO de la plantilla sin el telefono del hotel",
        "archivo": PLANTILLA,
        "original": b"Email: contacto@iahoteles.co",
        "mutado": b"WhatsApp: ${hotel_phone}  \nEmail: contacto@iahoteles.co",
        "test": "contacto",
        "causa": "test_bloque_contacto_no_emite_whatsapp_del_hotel",
    },
    {
        "id": "M7",
        "guard": "despojer_nombre_real: quita ESTIMATED_ y la marca de tiempo",
        "archivo": CONTRATO_ASSETS,
        "original": b'    cabeza = _SUFIJO_MARCA_TIEMPO.sub("", cabeza)',
        "mutado": b'    pass  # mutante: no despoja la marca',
        "test": "despojo",
        "causa": "test_orden_no_vacio_con_nombres_reales",
    },
    {
        "id": "M8",
        "guard": "resolver_nombre_real: coincidencia exacta, sin pares inventados",
        "archivo": CONTRATO_ASSETS,
        "original": b'        candidato = despojer_nombre_real(nombre)\n        if candidato is None:\n            return None',
        "mutado": b'        candidato = despojer_nombre_real(nombre)\n        if candidato is None:\n            return None\n        for _c in self.CORE_TO_GEO_MAP:\n            if _c.split("_")[0] in candidato:\n                return _c, AssetType.CORE',
        "test": "fabrica",
        "causa": "test_los_nombres_reales_que_casan",
    },
    {
        "id": "M9",
        "guard": "_medir_orden_implementacion: corta por seccion, no por documento",
        "archivo": REVISOR,
        "original": b'        bloque = resto[:siguiente.start()] if siguiente else resto',
        "mutado": b'        bloque = content  # mutante: cuenta tareas en todo el documento',
        "test": "seccion",
        "causa": "test_la_tarea_de_la_guia_no_cuenta_como_orden",
    },
    {
        "id": "M10",
        "guard": "_check_implementation_order: cero tareas es rojo",
        "archivo": REVISOR,
        "original": b'        if medida["tareas"] == 0:\n            findings.append(self._make_finding(\n                severity=SEVERITY_WARNING,',
        "mutado": b'        if False:\n            findings.append(self._make_finding(\n                severity=SEVERITY_WARNING,',
        "test": "check",
        "causa": "test_orden_vacio_del_paquete_certificado_reporta_rojo",
    },
]

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _adaptar_eol(crudo: bytes, fragmento: bytes) -> bytes:
    """Los archivos del disco pueden venir con CRLF; el ancla se escribe con LF."""
    if b"\r\n" in crudo:
        return fragmento.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    return fragmento


def correr_test(nodo: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", nodo, "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", help="id del mutante a dejar aplicado (diagnostico)")
    args = ap.parse_args()

    linea_base = {str(m["archivo"]): sha(m["archivo"]) for m in MUTANTES}
    resultados = []
    for m in MUTANTES:
        archivo = m["archivo"]
        crudo = archivo.read_bytes()
        original = _adaptar_eol(crudo, m["original"])
        mutado = _adaptar_eol(crudo, m["mutado"])
        if crudo.count(original) != 1:
            resultados.append({**_meta(m), "aplicado": False,
                               "motivo": f"ancla no unica ({crudo.count(original)} ocurrencias)"})
            continue
        nuevo = crudo.replace(original, mutado, 1)
        archivo.write_bytes(nuevo)
        exit_code, salida = correr_test(TESTS[m["test"]])
        falla_por_causa = m["causa"] in salida and exit_code != 0
        archivo.write_bytes(crudo)
        restaurado = sha(archivo) == linea_base[str(archivo)]
        resultados.append({
            **_meta(m),
            "aplicado": True,
            "exit": exit_code,
            "rojo_por_su_causa": falla_por_causa,
            "coleccion_error": "error" in salida.lower() and "1 failed" not in salida,
            "restaurado_por_sha256": restaurado,
            "sha256_restaurado": sha(archivo),
            "crudo": salida[-400:],
        })
        print(f"[{m['id']}] exit={exit_code} causa={falla_por_causa} restaurado={restaurado}")

    arbol_intacto = all(sha(Path(r)) == b for r, b in linea_base.items())
    informe = {
        "schema": "iah-cli/mutation-report/1",
        "fecha": datetime.now(timezone.utc).isoformat(),
        "harness": str(EVIDENCIA / "run_mutations.py"),
        "instrumento": "python -m pytest <nodo> -q --no-header -p no:cacheprovider",
        "mutantes": resultados,
        "total": len(resultados),
        "rojos_por_causa": sum(1 for r in resultados if r.get("rojo_por_su_causa")),
        "arbol_intacto_por_sha256": arbol_intacto,
        "linea_base_sha256": linea_base,
    }
    (EVIDENCIA / "mutation_report.json").write_text(
        json.dumps(informe, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"TOTAL={len(resultados)} rojos_por_causa={informe['rojos_por_causa']} arbol_intacto={arbol_intacto}")
    return 0 if (informe["rojos_por_causa"] == len(resultados) and arbol_intacto) else 1


def _meta(m):
    return {
        "id": m["id"],
        "guard": m["guard"],
        "archivo": str(m["archivo"].relative_to(ROOT)),
        "test": TESTS[m["test"]],
        "causa_esperada": m["causa"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
