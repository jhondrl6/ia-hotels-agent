"""FASE-HOTFIX-PRE-RELEASE — sonda de artefactos ANTES/DESPUES (H2, H3, H6).

Re-ejecutable:  python evidence/FASE-HOTFIX-PRE-RELEASE/faseHotfix_sonda_artefactos.py

Regla de la sesion (L-V1): la evidencia NO es un log de consola ni un string en
el codigo. Esta sonda produce **los JSON que el writer de produccion deja en
disco** y compara contra el JSON que efectivamente dejo la unica corrida E2E del
plan (`evidence/FASE-I/corrida/`, solo lectura).

Sin red, sin LLM, sin `v4complete`.
"""

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from modules.asset_generation.proposal_asset_alignment import (  # noqa: E402
    AssetAlignmentMatrix,
    PROPOSAL_SERVICE_TO_ASSET,
    ProposalAssetMatrixEntry,
)
from modules.asset_generation.site_presence_adapter import normalize_site_presence  # noqa: E402
from modules.commercial_documents.coherence_validator import CoherenceValidator  # noqa: E402
from modules.commercial_documents.data_structures import (  # noqa: E402
    AssetSpec,
    DiagnosticDocument,
    ProposalDocument,
    Scenario,
)
from modules.quality_gates.publication_gates import (  # noqa: E402
    GateStatus,
    PublicationGateResult,
)
from main import _build_gate_report_payload, _make_evidence_path  # noqa: E402

AUDIT = ROOT / "evidence/FASE-I/corrida/hotelsalentoreal/v4_audit"
REPORT = ROOT / "evidence/FASE-I/corrida/v4_complete_report.json"
ANTES = AUDIT / "gate_report_20260904_120413.json"


def _hr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# ---------------------------------------------------------------- H2: gate_report
def h2():
    _hr("H2 / AC7 / S-I2 — severidad en gate_report_*.json")
    real = json.loads(ANTES.read_text(encoding="utf-8"))
    severidades_antes = sum(1 for g in real["gate_results"] if "severity" in g)
    print(f"ANTES  (artefact de la corrida): gate_results = {len(real['gate_results'])}, "
          f"con 'severity' = {severidades_antes}, "
          f"ocurrencias de 'severity' en el archivo = "
          f"{ANTES.read_text(encoding='utf-8').count('severity')}")

    results = [
        PublicationGateResult(
            gate_name=g["gate_name"], passed=g["passed"], status=GateStatus(g["status"]),
            message=g["message"], value=g["value"], suggestion=g.get("suggestion", ""),
            details=g.get("details", {}) or {},
        )
        for g in real["gate_results"]
    ]
    payload = _build_gate_report_payload(
        results,
        {"status": real["readiness"]["status"], "ready": real["readiness"]["ready"],
         "blocking_issues": real["readiness"]["blocking_issues"],
         "summary": {"warnings": real["readiness"].get("warnings", [])}},
        hotel_url=real.get("hotel_url", ""),
        financial_sources=real.get("financial_sources", {}),
        generated_at=real.get("generated_at"),
    )
    with tempfile.TemporaryDirectory() as td:
        out = _make_evidence_path(Path(td), "hotelsalentoreal", "gate_report", "20260904_120413")
        out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        despues = json.loads(out.read_text(encoding="utf-8"))
        print(f"DESPUES (writer real, en disco): claves por gate = "
              f"{sorted(despues['gate_results'][0].keys())}")
        bloq = [g["gate_name"] for g in despues["gate_results"] if g["blocks_publication"]]
        adv = [g["gate_name"] for g in despues["gate_results"] if g["severity"] == "advisory"]
        print(f"  severity=advisory -> {adv}")
        print(f"  blocks_publication=True -> {bloq} (la corrida dio ready="
              f"{despues['readiness']['ready']}, coherente)")
        print(f"  ocurrencias de 'severity' en el archivo = "
              f"{out.read_text(encoding='utf-8').count('severity')}")
    return despues


# ---------------------------------------------------------------- H3: matriz
def h3():
    _hr("H3 / AC6 / S-V3 — coverage_ratio en proposal_asset_matrix.json")
    real = json.loads((AUDIT / "proposal_asset_matrix.json").read_text(encoding="utf-8"))
    print(f"ANTES  : claves = {sorted(real.keys())}")
    print(f"         coverage_ratio presente = {'coverage_ratio' in real}  "
          f"(VERIFY: la clave no existia en el artefacto)")
    gate = json.loads(ANTES.read_text(encoding="utf-8"))
    align = next(g["details"]["alignment"] for g in gate["gate_results"]
                 if g["gate_name"] == "proposal_asset_alignment")
    print(f"         el unico ratio visible era gate_report.details.alignment."
          f"coverage_ratio = {align['coverage_ratio']} "
          f"(actionable_total = {align['actionable_total']})")

    entries = [
        ProposalAssetMatrixEntry(
            service_name=e["service_name"], pain_ids=e["pain_ids"], asset_type=e["asset_type"],
            asset_path=e.get("asset_path"), confidence=e["confidence"], status=e["status"],
        )
        for e in real["entries"]
    ]
    presence = normalize_site_presence(
        json.loads((AUDIT / "site_presence_snapshot.json").read_text(encoding="utf-8"))["snapshot"]
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "proposal_asset_matrix.json"
        AssetAlignmentMatrix(
            entries=entries, site_presence_report=presence,
            not_promised=list(real.get("not_promised", [])),
            unknown_services=list(real.get("unknown_services", [])),
        ).save(p)
        d = json.loads(p.read_text(encoding="utf-8"))
        print(f"DESPUES: version = {d['proposal_asset_matrix_version']}, "
              f"coverage_ratio = {d['coverage_ratio']}, "
              f"actionable_total = {d['alignment']['actionable_total']}, "
              f"summary = {d['summary']}")
        print(f"  coincide con el gate (un solo oraculo) = "
              f"{d['coverage_ratio'] == align['coverage_ratio'] and d['alignment'] == align}")

        # caso negativo: el asset generado desaparece -> el ratio SE MUEVE
        sin_asset = [
            ProposalAssetMatrixEntry(
                service_name=e.service_name, pain_ids=list(e.pain_ids), asset_type=e.asset_type,
                asset_path=None, confidence=0.0,
                status="MISSING_ASSET" if e.status == "LINKED" else e.status,
            )
            for e in entries
        ]
        p2 = Path(td) / "matriz_negativa.json"
        AssetAlignmentMatrix(
            entries=sin_asset, site_presence_report=presence,
            not_promised=list(real.get("not_promised", [])),
            unknown_services=list(real.get("unknown_services", [])),
        ).save(p2)
        dn = json.loads(p2.read_text(encoding="utf-8"))
        print(f"  caso negativo (LINKED -> MISSING_ASSET): coverage_ratio = "
              f"{dn['coverage_ratio']} unresolved = {dn['alignment']['unresolved']} "
              f"delivery_ready = {dn['delivery_ready']}  <-- discrimina")
    return d


# ---------------------------------------------------------------- H6: mensaje
def h6():
    _hr("H6 / S-C3 mitad textual — que narran los artefactos del cliente")
    catalogo = len(PROPOSAL_SERVICE_TO_ASSET)
    for f in ("coherence_validation.json", "coherence_validation_post_gen.json",
              "asset_generation_report.json"):
        blob = (AUDIT / f).read_text(encoding="utf-8")
        hits = re.findall(r"\d+ servicios verificados", blob)
        print(f"ANTES  {f}: {len(hits)} hit de «N servicios verificados» -> {hits[:1]}")
    print(f"         el numero narrado ({catalogo}) es el tamano del catalogo "
          f"estatico; la matriz de esa corrida promete "
          f"{json.loads((AUDIT / 'proposal_asset_matrix.json').read_text(encoding='utf-8'))['summary']['promised']}")

    gen = json.loads((AUDIT / "asset_generation_report.json").read_text(encoding="utf-8"))
    generated = {
        a["asset_type"]: {"can_use": True, "confidence_score": a.get("confidence_score", 0.9),
                          "filename": a.get("filename", "")}
        for a in gen["generated_assets"]
    }
    specs = [AssetSpec(asset_type=t, pain_ids=["p"]) for t in generated]
    escenario = Scenario(monthly_loss_min=0, monthly_loss_max=0, probability=0.7,
                         description="sonda FASE-HOTFIX")
    validator = CoherenceValidator()
    report = validator.validate(
        diagnostic=DiagnosticDocument(path="", problems=[], financial_impact=escenario,
                                      generated_at="2026-09-04T12:04:13"),
        proposal=ProposalDocument(path="", price_monthly=0, assets_proposed=specs,
                                  roi_projected=0.0, generated_at="2026-09-04T12:04:13"),
        assets=specs, validation_summary=_Summary(), generated_assets=generated,
        site_presence_report=normalize_site_presence(
            json.loads((AUDIT / "site_presence_snapshot.json").read_text(encoding="utf-8"))["snapshot"]
        ),
    )
    with tempfile.TemporaryDirectory() as td:
        report.save(td)
        d = json.loads((Path(td) / "coherence_validation.json").read_text(encoding="utf-8"))
        msg = next(c["message"] for c in d["checks"] if c["name"] == "promised_assets_exist")
        print(f"DESPUES coherence_validation.json (writer real): {msg}")
        print(f"  ocurrencias de «servicios verificados» en el archivo = "
              f"{len(re.findall(r'servicios verificados', (Path(td) / 'coherence_validation.json').read_text(encoding='utf-8')))}, "
              f"PROPOSAL_SERVICE_TO_ASSET = "
              f"{(Path(td) / 'coherence_validation.json').read_text(encoding='utf-8').count('PROPOSAL_SERVICE_TO_ASSET')}")
    return msg


class _Summary:
    overall_confidence = "VERIFIED"

    def get_field(self, name):
        return None


if __name__ == "__main__":
    h2()
    h3()
    h6()
    print("\nSONDA COMPLETA")
