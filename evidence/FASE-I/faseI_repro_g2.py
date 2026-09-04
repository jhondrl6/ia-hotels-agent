"""Repro minimo (medicion, NO fix) del camino G2/NR2 con la forma real de produccion.

Pregunta: despues de builder.with_audit_data(...) + with_geo_flow(banda critical),
el dict que reciben los gates contiene 'audit_data' y 'critical_issues'?
Si no, el detector _evident_critical_missed lee {} y el recall 1.0 vacuo sobrevive.
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# al correr como temp/*.py el sys.path[0] es temp/, no la raiz del repo
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.assessment_builder import AssessmentBuilder
from modules.quality_gates.publication_gates import PublicationGatesOrchestrator

audit_data = {
    "performance": {"status": "ERROR", "has_field_data": False, "mobile_score": None, "desktop_score": 11},
    "gbp": {"reviews": 118, "rating": 4.5, "photos": 10, "geo_score": 79},
    "schema": {"total_schemas": 8},
    "ia_readiness": {"overall_score": 73.78, "components": {"llms_txt": 0}},
}
geo_flow = {
    "case": "critical",
    "success": True,
    "errors": [],
    "geo_assessment": {"total_score": 29, "band": "critical"},
}

builder = AssessmentBuilder()
builder.with_core("https://www.hotelsalentoreal.com/", "Hotelsalentoreal")
builder.with_audit_data(audit_data)
builder.with_geo_flow(geo_flow)
assessment = builder.build()

print("type(assessment) =", type(assessment).__name__)
if not isinstance(assessment, dict):
    assessment = getattr(assessment, "__dict__", {})
print("audit_data presente?", "audit_data" in assessment)
print("geo_flow presente?", "geo_flow" in assessment)
print("critical_issues =", repr(assessment.get("critical_issues")))
print("audit_schema vacuo?", not assessment.get("audit_schema"))
print("critical_recall directo?", "critical_recall" in assessment)

orch = PublicationGatesOrchestrator()
missed = orch._evident_critical_missed(assessment, assessment.get("critical_issues") or [])
print("_evident_critical_missed ->", missed)
print("_extract_critical_recall ->", orch._extract_critical_recall(assessment))

result = orch._critical_recall_gate(assessment)
print(
    "gate:",
    result.status,
    "value=",
    result.value,
    "details=",
    result.details,
)
