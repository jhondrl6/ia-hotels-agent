"""Sonda de estructura del baseline (solo lectura) para construir la comparacion FASE-I.

Uso: python temp/faseI_probe.py <dir_v4_complete>
Imprime claves y valores escogidos, compactos, sin volcar archivos enteros.
"""

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(sys.argv[1])
AUDIT = ROOT / "hotelsalentoreal" / "v4_audit"


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def resolve(pattern):
    hits = sorted(AUDIT.glob(pattern))
    return hits[-1] if hits else None


def brief(value, limit=160):
    return json.dumps(value, ensure_ascii=False, default=str)[:limit]


print(f"# PROBE {ROOT}")
print(f"EXISTS={ROOT.exists()}")

report = load(ROOT / "v4_complete_report.json")
print("\n## v4_complete_report.json top keys")
print(sorted(report.keys()))
for key in ("hotel_id", "url", "coherence_score", "is_coherent", "evidence_tier", "target_id"):
    if key in report:
        print(f"  {key} = {brief(report[key], 80)}")
print(f"  publication_state keys = {brief(report.get('publication_state'), 200)}")
print(f"  assets_generated = {len(report.get('assets_generated', []))}")
for asset in report.get("assets_generated", []):
    print(f"    - {brief({k: asset.get(k) for k in ('asset_type', 'preflight_status', 'confidence_score', 'asset_path', 'is_orphan')}, 220)}")

matrix_path = resolve("proposal_asset_matrix.json")
if matrix_path:
    matrix = load(matrix_path)
    print("\n## proposal_asset_matrix.json")
    print(f"  keys = {sorted(matrix.keys())}")
    entries = matrix.get("entries") or matrix.get("services") or []
    print(f"  n_entries = {len(entries)}")
    if entries:
        print(f"  entry keys = {sorted(entries[0].keys())}")
    for entry in entries:
        print(f"    - {brief({k: entry.get(k) for k in ('service_id', 'service', 'name', 'alignment', 'status', 'classification', 'asset_type', 'asset_path', 'pain_ids', 'no_breach')}, 240)}")
    print(f"  summary = {brief(matrix.get('summary'), 300)}")
    print(f"  delivery_ready = {brief(matrix.get('delivery_ready'), 80)}")

for name in ("coherence_validation.json", "coherence_validation_post_gen.json"):
    path = AUDIT / name
    if path.exists():
        doc = load(path)
        print(f"\n## {name}")
        print(f"  keys = {sorted(doc.keys())}")
        for key in ("is_coherent", "coherence_score", "score", "verdict", "final_score", "checks", "failures"):
            if key in doc:
                print(f"  {key} = {brief(doc[key], 300)}")

for pattern in ("gate_report_*.json", "commercial_gates_report.json", "commercial_gates_report_diagnostic_*.json"):
    path = resolve(pattern)
    if not path:
        print(f"\n## {pattern} -> AUSENTE")
        continue
    doc = load(path)
    print(f"\n## {path.name}")
    print(f"  keys = {sorted(doc.keys())}")
    results = doc.get("gate_results") or doc.get("checks") or doc.get("gates") or []
    print(f"  n_results = {len(results)}")
    for item in results:
        if isinstance(item, dict):
            print(f"    - {brief({k: item.get(k) for k in ('gate_name', 'name', 'id', 'passed', 'status', 'severity', 'value', 'blocking')}, 240)}")
        else:
            print(f"    - {brief(item, 160)}")
    print(f"  readiness = {brief(doc.get('readiness'), 240)}")

for name in ("pain_ledger_resolved.json", "pain_ledger.json"):
    path = resolve(name)
    if not path:
        print(f"\n## {name} -> AUSENTE")
        continue
    doc = load(path)
    entries = doc.get("entries", [])
    print(f"\n## {path.name} keys={sorted(doc.keys())} n_entries={len(entries)}")
    for entry in entries:
        print(f"    - {brief({k: entry.get(k) for k in ('pain_id', 'status', 'severity', 'asset_type', 'source', 'asset_path')}, 220)}")

for name in ("asset_generation_report.json", "delivery_quality_report.json", "site_presence_snapshot.json", "human_checklist.md", "ia_readiness_report.json", "geo_flow_result.json"):
    path = resolve(name)
    if path is None and not (AUDIT / name).exists():
        print(f"\n## {name} -> AUSENTE")
        continue
    if (AUDIT / name).exists() and path is None:
        path = AUDIT / name
    if path.suffix == ".md":
        text = path.read_text(encoding="utf-8", errors="replace")
        print(f"\n## {name} bytes={path.stat().st_size} lines={text.count(chr(10))}")
        print("   " + text[:400].replace(chr(10), " | "))
        continue
    doc = load(path)
    print(f"\n## {path.name}")
    print(f"  keys = {sorted(doc.keys())[:40]}")
    for key in ("snapshot", "assets", "summary", "is_coherent", "coherence_score", "critical_recall", "status", "checks"):
        if key in doc:
            print(f"  {key} = {brief(doc[key], 260)}")

print("\n## site_presence matches en todo el arbol")
for hit in sorted(ROOT.rglob("*site_presence*")):
    print(f"  {hit.relative_to(ROOT)} {hit.stat().st_size}B")

print("\n## deliveries")
for hit in sorted((ROOT / "deliveries").glob("*")) if (ROOT / "deliveries").exists() else []:
    if hit.is_file() and hit.suffix == ".zip":
        with zipfile.ZipFile(hit) as archive:
            print(f"  ZIP {hit.name} {hit.stat().st_size}B files={len(archive.namelist())}")
    else:
        print(f"  DIR/FILE {hit.name} dir={hit.is_dir()}")

print("\n## diagnosticos MD")
for hit in sorted(ROOT.glob("0[12]_*.md")):
    text = hit.read_text(encoding="utf-8", errors="replace")
    print(f"  {hit.name} bytes={hit.stat().st_size} lines={text.count(chr(10))}")
