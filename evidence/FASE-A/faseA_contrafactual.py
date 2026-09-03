"""FASE-A / A4 — contrafactual: ¿la derivación cambió la salida comercial?

Compara los registros derivados contra los literales que reemplazaron (copiados aquí
desde HEAD) y renderiza las tablas reales de la propuesta.
"""
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pathlib import Path

_root = Path(__file__).resolve()
while _root.parent != _root and not (_root / "VERSION.yaml").exists():
    _root = _root.parent
sys.path.insert(0, str(_root))

from modules.common.service_identity import SERVICE_IDENTITIES
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
from modules.quality.asset_semantics_validator import validar_semantica_comercial
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

# --- literales ANTES de FASE-A (copiados de HEAD) -------------------------
OLD_BRECHA_CANDIDATES = {
    "optimization_guide": ["low_seo_score", "low_content_length"],
    "whatsapp_button": ["whatsapp_conflict", "no_whatsapp_visible"],
    "hotel_schema": ["no_hotel_schema"],
    "org_schema": ["no_org_schema"],
    "faq_page": ["no_faq_schema"],
    "open_graph": ["no_og_tags"],
    "llms_txt": ["missing_llmstxt"],
}
OLD_ASSET_TO_PAIN_ID = {
    "monthly_report":          "no_faq_schema",
    "faq_page":                "no_faq_schema",
    "hotel_schema":            "no_hotel_schema",
    "llms_txt":                "missing_llmstxt",
    "whatsapp_button":         "no_whatsapp_visible",
    "whatsapp_conflict_guide": "no_whatsapp_visible",
}
OLD_SERVICE_CATALOG_KEYS = [
    "seo_local", "boton_whatsapp", "schema_hotel", "schema_organization",
    "pagina_faq", "meta_tags_sociales", "informe_mensual", "optimizacion_ia_generativa",
]
OLD_PROPOSAL_SERVICE_TO_ASSET = {
    "SEO Local": "optimization_guide",
    "Botón de WhatsApp": "whatsapp_button",
    "Schema Hotel": "hotel_schema",
    "Schema Organization": "org_schema",
    "Página de FAQ": "faq_page",
    "Meta Tags Sociales (Open Graph)": "open_graph",
    "Optimización para IA Generativa": "llms_txt",
}

nuevo_brecha = {
    i.asset_type: list(i.brecha_candidates) for i in SERVICE_IDENTITIES if i.brecha_candidates
}
nuevo_a2p = {i.asset_type: i.pain_id for i in SERVICE_IDENTITIES}

print("=" * 78)
print("1. service_brecha_candidates — derivado vs literal anterior")
print("=" * 78)
print("  IDENTICOS:", nuevo_brecha == OLD_BRECHA_CANDIDATES)
if nuevo_brecha != OLD_BRECHA_CANDIDATES:
    print("   nuevo:", nuevo_brecha)
    print("   viejo:", OLD_BRECHA_CANDIDATES)
print("  orden de claves preservado:", list(nuevo_brecha) == list(OLD_BRECHA_CANDIDATES))

print()
print("=" * 78)
print("2. PROPOSAL_SERVICE_TO_ASSET — derivado vs literal anterior (orden incluido)")
print("=" * 78)
print("  IDENTICOS:", dict(PROPOSAL_SERVICE_TO_ASSET) == OLD_PROPOSAL_SERVICE_TO_ASSET)
print("  orden:", list(PROPOSAL_SERVICE_TO_ASSET) == list(OLD_PROPOSAL_SERVICE_TO_ASSET))

print()
print("=" * 78)
print("3. SERVICE_CATALOG — claves y orden")
print("=" * 78)
from modules.commercial_documents.service_catalog import SERVICE_CATALOG
print("  IDENTICOS:", list(SERVICE_CATALOG) == OLD_SERVICE_CATALOG_KEYS)
print("  claves:", list(SERVICE_CATALOG))

print()
print("=" * 78)
print("4. ASSET_TO_PAIN_ID — efecto REAL sobre la validación semántica")
print("   (sólo los assets iterados desde PROPOSAL_SERVICE_TO_ASSET cuentan)")
print("=" * 78)
print(f"  {'asset':26s} {'ANTES(pain,resultado)':38s} {'AHORA(pain,resultado)':38s} iterado")
divergencias_efectivas = []
for asset in sorted(set(PROPOSAL_SERVICE_TO_ASSET.values()) | set(OLD_ASSET_TO_PAIN_ID) | set(nuevo_a2p)):
    iterado = asset in PROPOSAL_SERVICE_TO_ASSET.values()
    viejo_p = OLD_ASSET_TO_PAIN_ID.get(asset)
    nuevo_p = nuevo_a2p.get(asset)
    viejo_r = validar_semantica_comercial(viejo_p, asset, "IMPLEMENT")[1] if viejo_p else "SKIP(sin pain)"
    nuevo_r = validar_semantica_comercial(nuevo_p, asset, "IMPLEMENT")[1] if nuevo_p else "SKIP(sin pain)"
    marca = "  <<< CAMBIO" if (viejo_r != nuevo_r and iterado) else ""
    if viejo_r != nuevo_r and iterado:
        divergencias_efectivas.append(asset)
    print(f"  {asset:26s} {str(viejo_p) + ',' + viejo_r:38s} {str(nuevo_p) + ',' + nuevo_r:38s} {iterado}{marca}")
print()
print("  Cambios EFECTIVOS en assets iterados:", divergencias_efectivas or "NINGUNO")

print()
print("=" * 78)
print("5. Salida real — _generate_dynamic_services_table")
print("=" * 78)
gen = V4ProposalGenerator()
assets = [
    {"asset_type": t, "confidence_score": 0.9}
    for t in set(PROPOSAL_SERVICE_TO_ASSET.values())
]
tabla = gen._generate_dynamic_services_table(
    detected_pain_ids=["no_og_tags", "no_monthly_report"], assets_generated=assets
)
print(tabla)
print("  filas:", len([l for l in tabla.strip().split("\n") if l.startswith("| ")]) - 1)

print()
print("=" * 78)
print("6. Salida real — _generate_asset_quality_table (modo backwards-compat)")
print("=" * 78)
aq = gen._generate_asset_quality_table(assets_generated=[], detected_pain_ids=[])
print(aq)
