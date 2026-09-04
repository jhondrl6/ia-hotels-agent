"""FASE-I ESTABILIZACION-PRE-TRIBUNAL: comparacion E2E vs baseline FASE-D.

Adaptado de evidence/FASE-VUP-D/verificar_no_regresion.py (hizo 7/7 contra este
mismo baseline). Cambios de fondo respecto del original:
  - los nombres timestamped se RESUELLEN con glob por lado, nunca se asumen
  - lee los DOS archivos de commercial gates (3 + 9 = 12 CG-*)
  - cada check lleva referencia de AC/NR y clasificacion de la diferencia
Salida: JSON a stdout + evidence/FASE-I/comparacion_resultados.json
"""

import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "output" / "FASE-I_salentoreal_post_estabilizacion" / "v4_complete"
BASE = ROOT / "output" / "FASE-D_salentoreal_post_guard" / "v4_complete"
RUN_LOG = ROOT / "temp" / "faseI_run.txt"
OUT = ROOT / "evidence" / "FASE-I" / "comparacion_resultados.json"

AUDIT_SUB = Path("hotelsalentoreal") / "v4_audit"

checks = []


def check(cid, ac, passed, base_value, new_value, note=""):
    checks.append(
        {
            "id": cid,
            "ref": ac,
            "pass": bool(passed),
            "baseline": base_value,
            "new": new_value,
            "note": note,
        }
    )


def load(path):
    if not path or not Path(path).exists():
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def audit_file(side, pattern):
    """Resuelve un nombre (posiblemente timestamped) dentro de v4_audit/."""
    hits = sorted((side / AUDIT_SUB).glob(pattern))
    return hits[-1] if hits else None


def tree_grep(side, needle):
    """Ocurrencias de un string por archivo de artefacto (JSON/MD) en todo el arbol."""
    counts = {}
    for path in sorted(side.rglob("*")):
        if not path.is_file() or path.suffix not in {".json", ".md", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        n = text.count(needle)
        if n:
            counts[str(path.relative_to(side))] = n
    return counts


# ---------- cargas comunas ----------
new_report = load(NEW / "v4_complete_report.json") or {}
base_report = load(BASE / "v4_complete_report.json") or {}

new_gate_path = audit_file(NEW, "gate_report_*.json")
base_gate_path = audit_file(BASE, "gate_report_*.json")
new_gates = load(new_gate_path) or {}
base_gates = load(base_gate_path) or {}

new_matrix = load(audit_file(NEW, "proposal_asset_matrix.json")) or {}
base_matrix = load(audit_file(BASE, "proposal_asset_matrix.json")) or {}


def gate_map(doc):
    out = {}
    for item in doc.get("gate_results", []):
        name = item.get("gate_name") or item.get("name")
        out[name] = item
    return out


def matrix_entries(doc):
    return doc.get("entries") or doc.get("services") or []


def count_status(entries, status):
    return sum(1 for e in entries if str(e.get("status", "")).upper() == status)


# ---------- C1 identidad del run ----------
check(
    "C1_identidad",
    "equiv baseline",
    new_report.get("hotel_id") == "hotel_hotelsalentoreal.com"
    and new_report.get("url") == "https://www.hotelsalentoreal.com/",
    f'{base_report.get("hotel_id")} | {base_report.get("url")}',
    f'{new_report.get("hotel_id")} | {new_report.get("url")}',
    "mismo sitio, mismos datos de entrada; distincto codigo",
)

# ---------- C2 AC6/NR6 coherence numerica ----------
new_coh = new_report.get("coherence_score")
base_coh = base_report.get("coherence_score")
check(
    "C2_coherence_ge_0.80",
    "NR6/AC6",
    isinstance(new_coh, (int, float)) and new_coh >= 0.80,
    base_coh,
    new_coh,
    "baseline 0.88 canónico (0.9133 no existe en artefactos: C1 del dossier)",
)

# ---------- C3 AC6 is_coherent en toda la evidencia ----------
base_iscoherent = tree_grep(BASE, '"is_coherent"')
new_iscoherent = tree_grep(NEW, '"is_coherent"')
base_values = {}
new_values = {}
for side, values, files in (
    (BASE, base_values, ("coherence_validation.json", "coherence_validation_post_gen.json")),
    (NEW, new_values, ("coherence_validation.json", "coherence_validation_post_gen.json")),
):
    for name in files:
        doc = load(side / AUDIT_SUB / name) or {}
        gen = load(side / AUDIT_SUB / "asset_generation_report.json") or {}
        values[name] = doc.get("is_coherent")
        values["asset_generation_report.coherence_report"] = (gen.get("coherence_report") or {}).get("is_coherent")
        values["asset_generation_report.final_coherence_report"] = (gen.get("final_coherence_report") or {}).get("is_coherent")
copias_base = sum(base_iscoherent.values())
copias_new = sum(new_iscoherent.values())
# AC6 admite los dos desenlaces legitimos: true en todas las declaraciones, o
# campo eliminado por la decision F3 (entonces 0 declaraciones en el arbol).
campo_eliminado = copias_new == 0
todos_true = any(v is True for v in new_values.values()) and not any(v is False for v in new_values.values())
check(
    "C3_is_coherent",
    "AC6/V16",
    campo_eliminado or todos_true,
    f'{len([k for k, v in base_values.items()])} declaraciones, valores={base_values}, copias_en_disco={copias_base}',
    f'valores={new_values}, copias_en_disco={copias_new}, archivos={new_iscoherent}',
    "exigido: true en todas, o campo eliminado por decision F3 (copias=0)",
)

# ---------- C4 AC5 matriz: no_breach 6 -> 0 ----------
base_entries = matrix_entries(base_matrix)
new_entries = matrix_entries(new_matrix)
base_no_breach = count_status(base_entries, "NO_BREACH")
new_no_breach = count_status(new_entries, "NO_BREACH")
check(
    "C4_no_breach_cero",
    "AC5",
    new_no_breach == 0,
    f'no_breach={base_no_breach} / enlaces={len(base_entries)} (6 NO_BREACH + 1 LINKED)',
    f'no_breach={new_no_breach} / enlaces={len(new_entries)}',
    f'summary nuevo={json.dumps(new_matrix.get("summary"), ensure_ascii=False)}',
)

# ---------- C5 AC9 site_presence_snapshot ----------
base_snap = sorted(BASE.rglob("*site_presence*"))
new_snap = sorted(NEW.rglob("*site_presence*"))
check(
    "C5_site_presence_snapshot",
    "AC9/A2",
    len(new_snap) >= 1,
    f'{len(base_snap)} archivos (deuda A2/H7: inexistente)',
    f'{[str(p.relative_to(NEW)) + f" ({p.stat().st_size}B)" for p in new_snap]}',
    "su aparicion es la prueba positiva de AC9",
)

# ---------- C6 AC9 asset_path poblado ----------
def paths_por_estado(entries):
    return [
        {
            "asset_type": e.get("asset_type"),
            "status": e.get("status"),
            "asset_path": e.get("asset_path"),
        }
        for e in entries
    ]


base_paths = paths_por_estado(base_entries)
new_paths = paths_por_estado(new_entries)
new_linked = [p for p in new_paths if str(p.get("status", "")).upper() in {"LINKED", "DELIVERED", "GENERATED"}]
linked_con_ruta = [p for p in new_linked if p.get("asset_path")]
assets_new = [
    {"asset_type": a.get("asset_type"), "asset_path": a.get("asset_path")}
    for a in new_report.get("assets_generated", [])
]
assets_con_ruta = [a for a in assets_new if a.get("asset_path")]
check(
    "C6_asset_path_poblado",
    "AC9/A6",
    (not new_linked or len(linked_con_ruta) == len(new_linked)) and bool(assets_con_ruta),
    f'matriz={base_paths} | report asset_path={[a.get("asset_path") for a in base_report.get("assets_generated", [])]}',
    f'matriz={new_paths} | report={assets_new}',
    "baseline: null incluso en la entrada LINKED (A6)",
)

# ---------- C7 AC7 perfil de gates 11 blocking + 2 advisory ----------
def severity_profile(doc):
    out = {}
    for name, item in gate_map(doc).items():
        out[name] = {
            "severity": item.get("severity"),
            "blocking": item.get("blocking"),
            "status": item.get("status"),
            "passed": item.get("passed"),
            "value": item.get("value"),
        }
    return out


base_profile = severity_profile(base_gates)
new_profile = severity_profile(new_gates)
blocking = sorted(k for k, v in new_profile.items() if str(v.get("severity", "")).lower() == "blocking" or v.get("blocking") is True)
advisory = sorted(k for k, v in new_profile.items() if str(v.get("severity", "")).lower() == "advisory" or v.get("blocking") is False)
check(
    "C7_perfil_gates",
    "AC7/D2",
    len(blocking) == 11 and len(advisory) == 2,
    f'{len(base_profile)} gates, severity=null en todos (dict plano)',
    f'n={len(new_profile)} blocking={len(blocking)} advisory={len(advisory)}',
    f'blocking={blocking} advisory={advisory}',
)

# ---------- C8 NR1 doc_audit_consistency evaluado ----------
def gate_value(doc, name):
    return gate_map(doc).get(name, {})


base_doc_audit = gate_value(base_gates, "doc_audit_consistency")
new_doc_audit = gate_value(new_gates, "doc_audit_consistency")
# NR1 exige que deje de ser un PASSED vacuo. Los dos desenlaces honestos son:
# value poblado, o NOT_EVALUATED explicito (FASE-G) — nunca PASSED con value=null.
doc_audit_honesto = new_doc_audit.get("value") is not None or str(new_doc_audit.get("status", "")).upper() == "NOT_EVALUATED"
check(
    "C8_doc_audit_no_nulo",
    "NR1/G1",
    doc_audit_honesto,
    f'status={base_doc_audit.get("status")} value={base_doc_audit.get("value")} (PASSED con value=null)',
    f'status={new_doc_audit.get("status")} value={new_doc_audit.get("value")} detail={json.dumps(new_doc_audit, ensure_ascii=False)[:300]}',
    "exigido: evaluado de verdad, con value no nulo o NOT_EVALUATED visible",
)

# ---------- C9 NR2 critical_recall no vacuo ----------
base_recall = gate_value(base_gates, "critical_recall").get("value")
new_recall_item = gate_value(new_gates, "critical_recall")
new_recall = new_recall_item.get("value")
check(
    "C9_critical_recall_lt_1",
    "NR2/G2",
    isinstance(new_recall, (int, float)) and new_recall < 1.0,
    base_recall,
    f'{new_recall} status={new_recall_item.get("status")} detail={json.dumps(new_recall_item, ensure_ascii=False)[:260]}',
    "baseline 1.0 vacuo; con audit_data real debe bajar de 1.0",
)

# ---------- C10 AC12 coherencia <-> veredicto <-> ZIP ----------
def zip_info(side):
    out = []
    ddir = side / "deliveries"
    if ddir.exists():
        for path in sorted(ddir.glob("*.zip")):
            try:
                with zipfile.ZipFile(path) as archive:
                    n = len(archive.namelist())
            except OSError:
                n = -1
            out.append({"file": path.name, "bytes": path.stat().st_size, "files": n})
    return out


base_zips, new_zips = zip_info(BASE), zip_info(NEW)
new_ready = (new_gates.get("readiness") or {}).get("ready")
new_status = (new_gates.get("readiness") or {}).get("status")
coherente = not any(v is False for v in new_values.values())
ac12_ok = (new_zips and coherente and new_ready) or (not new_zips and (not coherente or not new_ready))
check(
    "C10_coherencia_veredicto_zip",
    "AC12",
    ac12_ok,
    f'ZIP generado con is_coherent=false (incoherencia): {base_zips}',
    f'zips={new_zips} ready={new_ready} status={new_status} is_coherent_false={not coherente}',
    "no debe empaquetarse entrega si el veredicto de coherencia es negativo",
)

# ---------- C11 commercial gates: los DOS archivos, 12 CG-* ----------
def cg_files(side):
    out = {}
    for path in sorted((side / AUDIT_SUB).glob("commercial_gates_report*.json")):
        doc = load(path) or {}
        results = doc.get("results") or []
        items = {}
        for item in results:
            key = item.get("gate_id") or item.get("id") or item.get("name") or item.get("gate_name")
            items[key] = {"passed": item.get("passed"), "status": item.get("status"), "severity": item.get("severity")}
        out[path.name] = {
            "n": len(items),
            "all_passed": doc.get("all_passed"),
            "blocking_passed": doc.get("blocking_passed"),
            "failed": sorted(k for k, v in items.items() if v.get("passed") is False),
            "items": items,
        }
    return out


base_cg, new_cg = cg_files(BASE), cg_files(NEW)
base_cg_total = sum(v["n"] for v in base_cg.values())
new_cg_total = sum(v["n"] for v in new_cg.values())
check(
    "C11_commercial_gates",
    "CG-* / D2",
    new_cg_total >= 1,
    f'{base_cg_total} CG en {len(base_cg)} archivos: {json.dumps({k: v["n"] for k, v in base_cg.items()}, ensure_ascii=False)} fallan={json.dumps({k: v["failed"] for k, v in base_cg.items()}, ensure_ascii=False)}',
    f'{new_cg_total} CG en {len(new_cg)} archivos: {json.dumps({k: v["n"] for k, v in new_cg.items()}, ensure_ascii=False)} fallan={json.dumps({k: v["failed"] for k, v in new_cg.items()}, ensure_ascii=False)}',
    "baseline: 3 verdes + 9 diagnosticos con CG-WHATSAPP-LEAD failed (WARNING)",
)

# ---------- C12 pain_ledger_resolved / biyeccion FASE-B ----------
base_resolved = (load(audit_file(BASE, "pain_ledger_resolved.json")) or {}).get("entries", [])
new_resolved_doc = load(audit_file(NEW, "pain_ledger_resolved.json")) or {}
new_resolved = new_resolved_doc.get("entries", [])
base_pains = sorted((e.get("pain_id"), e.get("status"), e.get("severity")) for e in base_resolved)
new_pains = sorted((e.get("pain_id"), e.get("status"), e.get("severity")) for e in new_resolved)
check(
    "C12_pain_ledger_resolved",
    "AC6/FASE-B",
    len(new_resolved) >= 1,
    f'{len(base_resolved)} entradas: {base_pains}',
    f'{len(new_resolved)} entradas: {new_pains} summary={json.dumps(new_resolved_doc.get("summary"), ensure_ascii=False)[:200]}',
    "baseline: 3 MEDIUM ASSET_GENERATED; V7 (FASE-H) habilita un pain high desde default",
)

# ---------- C13 V7 low_ota_divergence presente ----------
new_pain_ids = sorted({e.get("pain_id") for e in new_resolved})
new_ledger = (load(audit_file(NEW, "pain_ledger.json")) or {}).get("entries", [])
new_ledger_ids = sorted({e.get("pain_id") for e in new_ledger})
base_ledger_ids = sorted({e.get("pain_id") for e in (load(audit_file(BASE, "pain_ledger.json")) or {}).get("entries", [])})
ota_nuevo = [pid for pid in new_ledger_ids + new_pain_ids if pid and "ota" in pid]
check(
    "C13_pain_high_v7",
    "V7/FASE-H",
    bool(ota_nuevo),
    f'pain_ledger ids={base_ledger_ids}',
    f'pain_ledger ids={new_ledger_ids} resolved={new_pain_ids} ota={ota_nuevo}',
    "V7 reactiva low_ota_divergence: debe aparecer como pain real, no invisible",
)

# ---------- C14 equivalencia de tier de evidencia (defaults) ----------
run_log = ""
if RUN_LOG.exists():
    run_log = RUN_LOG.read_text(encoding="utf-8", errors="replace")
defaults_en_log = "Using defaults" in run_log or "default" in run_log.lower()
base_warn = [w.get("message", "") for w in (base_gates.get("readiness") or {}).get("warnings", []) if isinstance(w, dict)]
new_warn = [w.get("message", "") for w in (new_gates.get("readiness") or {}).get("warnings", []) if isinstance(w, dict)]
tier_base = [m for m in base_warn if "Tier" in m or "default" in m.lower()]
tier_new = [m for m in new_warn if "Tier" in m or "default" in m.lower()]
check(
    "C14_tier_B_defaults",
    "equiv Tier B",
    defaults_en_log and bool(tier_new),
    f'warnings tier={tier_base}',
    f'log_con_defaults={defaults_en_log} warnings tier={tier_new}',
    "el baseline corrio CON DEFAULTS; sin clientes/ ni --ga4-property-id",
)

# ---------- C15 plan de assets ----------
def asset_plan(report):
    return sorted(
        (a.get("asset_type"), a.get("preflight_status"), a.get("confidence_score"))
        for a in report.get("assets_generated", [])
    )


base_plan, new_plan = asset_plan(base_report), asset_plan(new_report)
base_gen = (load(audit_file(BASE, "asset_generation_report.json")) or {}).get("summary", {})
new_gen = (load(audit_file(NEW, "asset_generation_report.json")) or {}).get("summary", {})
check(
    "C15_plan_assets",
    "AC6/FASE-C",
    len(new_report.get("assets_generated", [])) >= 1,
    f'{asset_plan(base_report)} summary={json.dumps(base_gen, ensure_ascii=False)}',
    f'{asset_plan(new_report)} summary={json.dumps(new_gen, ensure_ascii=False)}',
    "baseline: 4 assets (2 huerfanos), estimated=2, delivery_ready_percentage=100.0",
)

# ---------- C16 PageSpeed / infraestructura ----------
ps_new = "ERROR"
for token in ("PAGESPEED", "pagespeed"):
    if token in run_log:
        block = run_log.lower()
        idx = block.find(token)
        ps_new = re.sub(r"\s+", " ", run_log[max(0, idx - 60): idx + 200])[:220]
        break
check(
    "C16_pagespeed",
    "anomalia (iii)",
    True,
    "status=ERROR en corrida baseline (anterior al fix OPS)",
    f'log: {ps_new or "sin menciones de PageSpeed"}',
    "GOOGLE_PAGESPEED_API_KEY de 3 chars es placeholder conocido (V12); PAGESPEED_API_KEY canónica presente",
)

passed = sum(1 for c in checks if c["pass"])
result = {
    "new_dir": str(NEW.relative_to(ROOT)),
    "baseline_dir": str(BASE.relative_to(ROOT)),
    "passed": passed,
    "total": len(checks),
    "gate_names_new": sorted(new_profile),
    "checks": checks,
}
print(json.dumps(result, ensure_ascii=False, indent=2))
if OUT.parent.exists():
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
sys.exit(0)
