"""FASE-D VALIDADOR-URL-PROPIA: verificación de no-regresión vs baseline H2.

Compara output/FASE-D_salentoreal_post_guard contra output/salentoreal_final_v4c_h2
(FASE-SR-H2: smoke 7/7, coherence 0.88, READY_FOR_PUBLICATION).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NEW = ROOT / "output" / "FASE-D_salentoreal_post_guard" / "v4_complete"
BASE = ROOT / "output" / "salentoreal_final_v4c_h2" / "v4_complete"
OUT = ROOT / "evidence" / "FASE-VUP-D" / "verificacion_resultados.json"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def find(pattern):
    hits = sorted(NEW.glob(pattern))
    return hits[0] if hits else None


checks = {}


def check(name, passed, detail):
    checks[name] = {"pass": bool(passed), "detail": detail}


# --- 1. Cargas ---
new_report = load_json(NEW / "v4_complete_report.json")
base_report = load_json(BASE / "v4_complete_report.json")
new_gate_files = sorted(NEW.glob("hotelsalentoreal/v4_audit/gate_report_*.json"))
base_gate_files = sorted(BASE.glob("hotelsalentoreal/v4_audit/gate_report_*.json"))
new_gates = load_json(new_gate_files[-1]) if new_gate_files else None
base_gates = load_json(base_gate_files[-1]) if base_gate_files else None

# --- 2. Identidad (target_id) ---
hotel_id = new_report.get("hotel_id")
url = new_report.get("url")
check(
    "1_target_id_hotelsalentoreal",
    hotel_id == "hotel_hotelsalentoreal.com" and url == "https://www.hotelsalentoreal.com/",
    f"hotel_id={hotel_id!r} url={url!r}",
)

# --- 3. Coherence + publicación ---
coh = new_report.get("coherence_score")
base_coh = base_report.get("coherence_score")
ready = (new_gates or {}).get("readiness", {})
check(
    "2_coherence_ge_0.8",
    isinstance(coh, (int, float)) and coh >= 0.8,
    f"coherence={coh} (baseline H2={base_coh}); readiness={ready.get('status')}",
)
check(
    "3_ready_for_publication",
    ready.get("status") == "READY_FOR_PUBLICATION",
    f"status={ready.get('status')} blocking_issues={ready.get('blocking_issues')}",
)

# --- 4. Gates: mismo perfil que baseline ---
def gate_profile(gates_doc):
    results = (gates_doc or {}).get("gate_results", [])
    return {g["gate_name"]: bool(g.get("passed", g.get("status") == "PASSED")) for g in results}

new_profile = gate_profile(new_gates)
base_profile = gate_profile(base_gates)
regresiones = {
    name: (base_profile.get(name), new_profile.get(name))
    for name in base_profile
    if base_profile.get(name) and new_profile.get(name, True) is False
}
missing = sorted(set(base_profile) - set(new_profile))
extra = sorted(set(new_profile) - set(base_profile))
check(
    "4_gates_sin_regresion_blocking",
    not regresiones and not missing,
    f"n_gates new={len(new_profile)} base={len(base_profile)}; regresiones={regresiones or 'ninguna'}; "
    f"faltantes={missing or 'ninguno'}; extra={extra or 'ninguno'}; perfil_nuevo={new_profile}",
)

# --- 5. Plan de assets (determinismo L-PF12) ---
def asset_plan(report):
    return sorted(
        (a.get("asset_type"), a.get("preflight_status"), a.get("confidence_score"))
        for a in report.get("assets_generated", [])
    )

new_plan, base_plan = asset_plan(new_report), asset_plan(base_report)
check(
    "5_plan_assets_equivalente",
    new_plan == base_plan,
    f"new={new_plan} base={base_plan}",
)

# --- 6. Pains→assets (pain_ledger_resolved + proposal_asset_matrix) ---
def load_entries(v4_audit_dir, filename):
    hits = sorted(v4_audit_dir.glob(filename))
    if not hits:
        return None
    return load_json(hits[-1]).get("entries", [])

def pain_status_map(entries):
    return {e["pain_id"]: (e.get("status"), e.get("severity")) for e in entries or []}

def matrix_map(entries):
    return {
        e.get("asset_type"): (e.get("alignment"), e.get("status"), tuple(e.get("pain_ids", [])))
        for e in entries or []
    }

new_resolved = load_entries(NEW / "hotelsalentoreal" / "v4_audit", "pain_ledger_resolved.json")
base_resolved = load_entries(BASE / "hotelsalentoreal" / "v4_audit", "pain_ledger_resolved.json")
new_matrix = load_entries(NEW / "hotelsalentoreal" / "v4_audit", "proposal_asset_matrix.json")
base_matrix = load_entries(BASE / "hotelsalentoreal" / "v4_audit", "proposal_asset_matrix.json")

new_pm, base_pm = pain_status_map(new_resolved), pain_status_map(base_resolved)
new_mm, base_mm = matrix_map(new_matrix), matrix_map(base_matrix)
check(
    "6_pains_to_assets_equivalente",
    new_pm == base_pm and new_mm == base_mm,
    f"pains new={new_pm} base={base_pm} | matrix diff_keys="
    f"{sorted(k for k in set(new_mm) | set(base_mm) if new_mm.get(k) != base_mm.get(k)) or 'ninguna'}",
)

# --- 7. Escenarios financieros idénticos (smoke check 7 de H2) ---
fin_new = new_report.get("financial_data") or {}
fin_base = base_report.get("financial_data") or {}

def escenarios(fd):
    for key in ("scenarios", "financial_scenarios"):
        if isinstance(fd.get(key), dict):
            return fd[key]
    return fd

check(
    "7_financiera_identica_baseline",
    fin_new == fin_base,
    f"new={json.dumps(fin_new, ensure_ascii=False)[:400]} base={json.dumps(fin_base, ensure_ascii=False)[:400]}",
)

# --- Resumen ---
passed = sum(1 for c in checks.values() if c["pass"])
result = {"passed": passed, "total": len(checks), "checks": checks}
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
sys.exit(0 if passed == len(checks) else 1)
