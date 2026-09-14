"""Sonda read-only de FASE-P3-A (AC-F1 / AC-F2 / AC-F4).

Re-ejecutable: `python evidence/FASE-P3-A/verify_probe_ac_f1_f2_f4.py`

No modifica nada: instancia AssetReviewer y TribunalJudge contra los artefactos
reales disponibles y publica por stdout las claves que los AC declaran:

- AC-F1: revision_assets → findings[].finding_type == EMPTY_DELIVERY_TEMPLATE
         + implementation_order_check.{status,source} (régimen ZIP-only real).
- AC-F2: acta → evidence_tier vs financial_scenarios_*.json → breakdown.evidence_tier.
- AC-F4: acta → first_floor_rule.{applied,reason} con tier B+ (B_PLUS serializado).

Baselines (fuera del repo, regla output/* de .gitignore — límite declarado R2.6):
- deliveries ZIP-only real: output/FASE-D_salentoreal_post_guard/v4_complete/deliveries/
- audit real con financial_scenarios: evidence/FASE-I/corrida/hotelsalentoreal/v4_audit/
"""

import json
import sys
import tempfile
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from modules.quality_gates.tribunal.asset_reviewer import AssetReviewer  # noqa: E402
from modules.quality_gates.tribunal.judge import TribunalJudge  # noqa: E402

FASE_D_DELIVERIES = (
    PROJECT_ROOT / "output" / "FASE-D_salentoreal_post_guard" / "v4_complete" / "deliveries"
)
FASE_I_AUDIT = PROJECT_ROOT / "evidence" / "FASE-I" / "corrida" / "hotelsalentoreal" / "v4_audit"


def probe_ac_f1() -> None:
    print("=" * 70)
    print("AC-F1 · AssetReviewer sobre deliveries/ real (FASE-D baseline)")
    print("=" * 70)
    if not FASE_D_DELIVERIES.exists():
        print(f"[AUSENTE] baseline no disponible: {FASE_D_DELIVERIES}")
        return

    zips = sorted(FASE_D_DELIVERIES.glob("*.zip"))
    print(f"ZIPs encontrados: {[z.name for z in zips]}")
    for z in zips:
        with zipfile.ZipFile(z) as zf:
            names = zf.namelist()
            print(f"  {z.name}: IMPLEMENTATION_ORDER.md en ZIP = {'IMPLEMENTATION_ORDER.md' in names}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_audit = Path(tmp) / "v4_audit"
        tmp_audit.mkdir()
        reviewer = AssetReviewer(v4_audit_dir=tmp_audit, deliveries_dir=FASE_D_DELIVERIES)
        report = reviewer.review()

    empty = [f for f in report["findings"] if f["finding_type"] == "EMPTY_DELIVERY_TEMPLATE"]
    print(f"findings EMPTY_DELIVERY_TEMPLATE: {len(empty)}")
    for f in empty:
        print(f"  severity={f['severity']} desc={f['description']!r}")
    print(f"implementation_order_check: {json.dumps(report.get('implementation_order_check'), ensure_ascii=False)}")
    print(f"verdict_recommendation: {report['verdict_recommendation']}")


def probe_ac_f2_f4() -> None:
    print("=" * 70)
    print("AC-F2/AC-F4 · TribunalJudge sobre audit real (FASE-I) sin MANIFEST en disco")
    print("=" * 70)
    if not FASE_I_AUDIT.exists():
        print(f"[AUSENTE] baseline no disponible: {FASE_I_AUDIT}")
        return

    fs_files = sorted(FASE_I_AUDIT.glob("financial_scenarios_*.json"))
    if not fs_files:
        print("[AUSENTE] financial_scenarios_*.json no encontrado en FASE-I")
        return
    with open(fs_files[-1], encoding="utf-8") as fh:
        pipeline_tier = json.load(fh).get("breakdown", {}).get("evidence_tier")
    print(f"fuente pre-packaging: {fs_files[-1].name} → breakdown.evidence_tier = {pipeline_tier!r}")

    with tempfile.TemporaryDirectory() as tmp:
        empty_deliveries = Path(tmp) / "deliveries"
        empty_deliveries.mkdir()
        judge = TribunalJudge(
            v4_audit_dir=FASE_I_AUDIT, deliveries_dir=empty_deliveries, hotel_id="hotelsalentoreal"
        )
        acta = judge.evaluate()

    print(f"acta → evidence_tier = {acta['evidence_tier']!r}  (¿== pipeline? {acta['evidence_tier'] == pipeline_tier})")
    print(f"acta → first_floor_rule = {json.dumps(acta['first_floor_rule'], ensure_ascii=False)}")
    print(f"acta → verdict = {acta['verdict']}")

    # AC-F4 sintético: tier B+ (EvidenceTier.B_PLUS.value) vía financial_scenarios
    with tempfile.TemporaryDirectory() as tmp:
        audit = Path(tmp) / "v4_audit"
        audit.mkdir()
        deliveries = Path(tmp) / "deliveries"
        deliveries.mkdir()
        (audit / "financial_scenarios_20260101_000000.json").write_text(
            json.dumps({"breakdown": {"evidence_tier": "B+"}}), encoding="utf-8"
        )
        judge = TribunalJudge(v4_audit_dir=audit, deliveries_dir=deliveries, hotel_id="synthetic")
        acta = judge.evaluate()
    print("-" * 70)
    print("AC-F4 sintético · tier B+ sin MANIFEST:")
    print(f"acta → evidence_tier = {acta['evidence_tier']!r}")
    print(f"acta → first_floor_rule = {json.dumps(acta['first_floor_rule'], ensure_ascii=False)}")
    print(f"acta → verdict = {acta['verdict']}")


if __name__ == "__main__":
    probe_ac_f1()
    probe_ac_f2_f4()
