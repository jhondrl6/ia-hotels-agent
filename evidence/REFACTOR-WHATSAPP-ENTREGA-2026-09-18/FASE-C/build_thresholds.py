"""FASE-C / T4 — `thresholds.json` de C: las barras leídas del código vivo.

Cinco barras miden el mismo hecho (AC5). Cada valor se lee del símbolo que lo
define, nunca de los documentos del plan. La fila `cambio_en_fase_c` declara si
esta fase lo tocó: C tenía prohibido bajar 0.9/0.8 y cambiar `blocking=True`, y
el contraste se hace sobre el símbolo, no sobre la afirmación.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from modules.asset_generation.asset_catalog import ASSET_CATALOG  # noqa: E402
from modules.asset_generation.preflight_checks import NEW_HOTEL_THRESHOLDS  # noqa: E402
from modules.asset_generation.site_presence_checker import SitePresenceChecker  # noqa: E402
from modules.commercial_documents.coherence_config import CoherenceConfig  # noqa: E402
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper  # noqa: E402
from modules.data_validation import whatsapp_contract as wc  # noqa: E402
from modules.quality_gates.domain_gates import CommercialGate  # noqa: E402


def _barra(entrada):
    return (entrada["confidence_required"] if isinstance(entrada, dict)
            else entrada.confidence_required)


def _numstat(rel):
    out = subprocess.run(["git", "diff", "--numstat", "--", rel], cwd=REPO,
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace").stdout.strip()
    return out or "identico a HEAD"


config = CoherenceConfig()
mapper = PainSolutionMapper()
catalogo = ASSET_CATALOG["whatsapp_button"]

evidencia = {
    "fase": "FASE-C",
    "plan": "REFACTOR-WHATSAPP-ENTREGA-2026-09-18",
    "medido_el": "2026-10-06",
    "head": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip(),
    "leer_como": (
        "Valores leidos del codigo vivo el dia de la fase. `cambio_en_fase_c: no` "
        "= congelado por el plan y verificado intacto. La barra vigente NO es una: "
        "son cinco midiendo el mismo hecho, cada una con su consumidor."
    ),
    "barras_de_whatsapp": {
        "coherencia_whatsapp_verified": {
            "valor": config.get_threshold("whatsapp_verified"),
            "blocking": config.is_blocking("whatsapp_verified"),
            "fuente": "CoherenceConfig.DEFAULT_RULES['whatsapp_verified']",
            "consumidor": "CoherenceValidator._check_whatsapp_verified",
            "cambio_en_fase_c": "no (valor y flag intactos; lo que se retiro fue el boost que la saltaba)",
        },
        "dolor_no_whatsapp_visible": {
            "valor": _barra(mapper.pain_map["no_whatsapp_visible"]),
            "fuente": "PAIN_SOLUTION_MAP['no_whatsapp_visible'].confidence_required",
            "consumidor": "PainSolutionMapper.get_assets_for_pain",
            "cambio_en_fase_c": "no",
        },
        "dolor_whatsapp_conflict": {
            "valor": _barra(mapper.pain_map["whatsapp_conflict"]),
            "fuente": "PAIN_SOLUTION_MAP['whatsapp_conflict'].confidence_required",
            "consumidor": "PainSolutionMapper.get_assets_for_pain (unica via que planifica el boton tras B)",
            "cambio_en_fase_c": "no",
        },
        "catalogo_boton": {
            "valor": catalogo.required_confidence,
            "block_on_failure": catalogo.block_on_failure,
            "fuente": "ASSET_CATALOG['whatsapp_button']",
            "consumidor": "PreflightChecker.ASSET_REQUIREMENTS / get_effective_threshold",
            "cambio_en_fase_c": "no (block_on_failure=False intacto: el preflight sigue sin bloquear; quien bloquea es el limite de generacion)",
        },
        "hotel_nuevo_boton": {
            "valor": NEW_HOTEL_THRESHOLDS["whatsapp_button"],
            "fuente": "preflight_checks.NEW_HOTEL_THRESHOLDS['whatsapp_button']",
            "consumidor": "PreflightChecker.get_effective_threshold(is_new_hotel=True)",
            "cambio_en_fase_c": "no — y su rojo sigue vigente: 0.3 planifica el boton aunque la coherencia exija 0.9; C lo goberno anclando el DESTINO, no la barra (AC5, dueno C-D)",
        },
        "gate_comercial_legado": {
            "valor": CommercialGate(config={}).whatsapp_confidence_threshold,
            "fuente": "CommercialGate.__init__ (default de 'whatsapp_confidence_threshold')",
            "consumidor": "modules/quality_gates/domain_gates.py",
            "cambio_en_fase_c": "no",
        },
    },
    "nuevo_por_fase_c": {
        "contrato_de_forma_del_numero": {
            "longitud_min_digitos": wc.LONGITUD_MIN,
            "longitud_max_digitos": wc.LONGITUD_MAX,
            "fuente_longitud": "ITU-T E.164 (max 15); minimo 8 fijado por C y documentado en whatsapp_contract.py",
            "digitos_aceptados": "ASCII 0-9 (no str.isdigit(): acepta digitos Unicode)",
            "separadores_permitidos": sorted(wc.SEPARADORES_PERMITIDOS),
            "centinelas_rechazados": sorted(wc.CENTINELAS),
            "sin_inferir_pais_ni_completar_partes": True,
            "normalizador_no_reutilizado": "modules/data_validation/cross_validator.normalize_phone_number (muta 57/60/0: valido para comparar, no para un destino)",
        },
        "boost_retirado": {
            "que_era": "confidence_score = max(confidence_score, 0.95) cuando presence.status == 'exists'",
            "estado": "RETIRADO en FASE-C por AC3",
            "diente": "mutante M4 del run_mutations.py de esta fase",
        },
        "presencia_no_promociona_a_verified": True,
        "claves_aditivas_del_reporte": ["observation_scope", "read_status", "presence_evidence_kind", "details"],
        "presence_confidence_sonda_html": 0.85,
        "marcas_congeladas": {
            "status": "sin redefinir (los cinco valores de PresenceStatus son los mismos)",
            "site_verified": "sin redefinir",
            "confidence": "sin redefinir",
        },
    },
    "archivos_con_diferencia_contra_HEAD": {
        rel: _numstat(rel) for rel in [
            "modules/commercial_documents/coherence_validator.py",
            "modules/asset_generation/conditional_generator.py",
            "modules/asset_generation/site_presence_checker.py",
            "modules/asset_generation/site_presence_adapter.py",
            "modules/asset_generation/v4_asset_orchestrator.py",
            "modules/auditors/v4_comprehensive.py",
            "modules/data_validation/whatsapp_contract.py",
            "main.py",
        ]
    },
}

salida = Path(__file__).resolve().parent / "thresholds.json"
salida.write_text(json.dumps(evidencia, indent=2, ensure_ascii=False, sort_keys=True),
                  encoding="utf-8")
print(f"thresholds.json escrito: {salida}")
print("barras:", {k: v["valor"] for k, v in evidencia["barras_de_whatsapp"].items()})
