"""FASE-I: re-evaluacion de las 8 caidas silenciosas del dossier §4 sobre artefactos reales.

Uso: python temp/faseI_ocho_caidas.py <dir_v4_complete>
No interpreta: localiza evidencia por item (pain_id, valor de audit, mencion en el MD)
y la imprime. La clasificacion (i)-(iv) la hace el parent en comparacion-vs-baseline.md.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
AUDIT = ROOT / "hotelsalentoreal" / "v4_audit"


def load(pattern):
    hits = sorted(AUDIT.glob(pattern))
    if not hits:
        return None
    with open(hits[-1], encoding="utf-8") as handle:
        return json.load(handle)


def brief(value, limit=200):
    return json.dumps(value, ensure_ascii=False, default=str)[:limit]


audit = load("audit_report_*.json") or {}
ledger = (load("pain_ledger.json") or {}).get("entries", [])
resolved = (load("pain_ledger_resolved.json") or {}).get("entries", [])
ia = load("ia_readiness_report.json") or {}
geo = load("geo_flow_result.json") or {}
matrix = load("proposal_asset_matrix.json") or {}
md_paths = sorted(ROOT.glob("01_DIAGNOSTICO_*.md"))
md = md_paths[0].read_text(encoding="utf-8", errors="replace") if md_paths else ""
snapshot = load("site_presence_snapshot.json")


def deep_find(obj, needles, path="$", hits=None, limit=14):
    """Busra claves o valores que contengan alguna needle; devuelve caminos JSON truncados."""
    if hits is None:
        hits = []
    if len(hits) >= limit:
        return hits
    if isinstance(obj, dict):
        for key, value in obj.items():
            if any(n in str(key).lower() for n in needles) and not isinstance(value, (dict, list)):
                hits.append(f"{path}.{key} = {brief(value, 90)}")
            deep_find(value, needles, f"{path}.{key}", hits, limit)
    elif isinstance(obj, list):
        for index, value in enumerate(obj[:60]):
            deep_find(value, needles, f"{path}[{index}]", hits, limit)
    return hits


def md_grep(needles, limit=4):
    out = []
    for needle in needles:
        for match in re.finditer(re.escape(needle), md, re.I):
            line_start = md.rfind("\n", 0, match.start()) + 1
            line_end = md.find("\n", match.start())
            out.append(f"[{needle}] {md[line_start:line_end].strip()[:150]}")
            break
    return out


pain_ids = sorted({e.get("pain_id") for e in ledger if e.get("pain_id")})
resolved_ids = sorted({e.get("pain_id") for e in resolved if e.get("pain_id")})
print(f"# OCHO CAIDAS — dir={ROOT}")
print(f"n_pain_ledger={len(ledger)} ids={pain_ids}")
print(f"n_resolved={len(resolved)} ids={resolved_ids}")
print(f"n_matrix={len(matrix.get('entries') or [])} summary={brief(matrix.get('summary'), 240)}")

ITEMS = [
    ("1 PageSpeed ERROR", ["pagespeed", "page_speed", "lighthouse", "performance"], ["PageSpeed", "page speed", "Lighthouse"]),
    ("2 GEO critico 29/100", ["geo_score", "band", "score", "crisis"], ["GEO", "29/100", "critical"]),
    ("3 Visibilidad LLM = 0", ["mention_rate", "sov", "share_of_voice", "llm", "snippet"], ["Visibilidad", "menci", "LLM", "IA"]),
    ("4 missing_llmstxt", ["llms_txt", "llms", "missing_llmstxt"], ["llms.txt", "llms_txt"]),
    ("5 schema warnings image/priceRange", ["price_range", "pricerange", "image", "schema_warning", "warnings"], ["priceRange", "imagen", "schema"]),
    ("6 Fotos GBP 10/40", ["photos", "fotos", "gbp_photos", "photo_count"], ["Fotos", "fotos GBP", "fotograf"]),
    ("7 metadata vacios/None", ["metadata", "title", "description", "metadata_defaults"], ["titulo", "descripci"]),
    ("8 low_ota_divergence", ["ota", "divergence", "direct_channel"], ["OTA", "divergencia", "canal directo"]),
]

for title, needles, md_needles in ITEMS:
    print(f"\n## {title}")
    print(f"  audit: {deep_find(audit, needles) or 'SIN HIT'}")
    hits_ledger = [pid for pid in pain_ids if any(n in pid.lower() for n in needles)]
    print(f"  pain_ledger ids que calzan: {hits_ledger or 'NINGUNO'}")
    print(f"  md: {md_grep(md_needles) or 'SIN MENCION'}")

print("\n## geo_flow_result.json")
print(f"  keys={sorted(geo.keys())}")
print(f"  case={brief(geo.get('case'), 120)} success={geo.get('success')} errors={brief(geo.get('errors'), 160)}")
print(f"  geo_assessment={brief(geo.get('geo_assessment'), 400)}")
print(f"  assets_generated={brief(geo.get('assets_generated'), 200)}")
print(f"  sync_result={brief(geo.get('sync_result'), 200)}")

print("\n## ia_readiness_report.json")
print(f"  overall={ia.get('overall_score')} status={ia.get('status')}")
print(f"  components={brief(ia.get('components'), 400)}")
print(f"  actionable={brief(ia.get('actionable_items'), 300)}")

print("\n## site_presence_snapshot.json")
print(f"  {'AUSENTE' if snapshot is None else brief(snapshot, 500)}")

print("\n## performance / presencia en ledger y matriz")
perf_pains = [e for e in ledger if any(k in str(e.get("pain_id", "")) for k in ("perf", "page_speed", "pagespeed", "core_web"))]
print(f"  pains de performance en ledger: {brief(perf_pains, 300)}")
entries = matrix.get("entries") or []
print(f"  estados matriz: {sorted({str(e.get('status')) for e in entries})}")
for entry in entries:
    print(f"    - {brief({k: entry.get(k) for k in ('service_name', 'status', 'alignment', 'asset_type', 'asset_path', 'pain_ids')}, 240)}")
