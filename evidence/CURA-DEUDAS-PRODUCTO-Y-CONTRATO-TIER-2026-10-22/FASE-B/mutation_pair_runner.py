# -*- coding: utf-8 -*-
"""FASE-B — par rojo/verde del mutation check (R2.8) sobre AC1.

Verde: render B+ con la condición del render ACTIVA → summary.over_presentations == 0.
Rojo:  condición del render desactivada (A-bloque siempre visible) → el revisor
       real vuelve a emitir los 2 claims (summary.over_presentations == 2).

Ademas imprime el par del contrato del diagnostico: strings forzados a la
variante A en tier B+ → la funcion real del revisor marca los 2 claims.
"""
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.quality_gates.tribunal.honesty_reviewer import (
    FINDING_OVER_PRESENTATION,
    coincidencias_lenguaje_de_verificacion,
)
from tests.commercial_documents.test_fase_b_claims_tier_render import (
    CLAIM_1_A,
    CLAIM_2_A,
    claims_del_diagnostico,
    diagnostico_render,
    montar_run,
    renderizar_propuesta,
    revisar,
)


def escaneo(reporte):
    emitidos = [f for f in reporte["findings"]
                if f.get("finding_type") == FINDING_OVER_PRESENTATION]
    return reporte["summary"]["over_presentations"], emitidos


print("PAR ROJO/VERDE — mutation check AC1 (FASE-B)")
print("Simbolo del guard: _preprocess_conditionals (propuesta) / "
      "_build_financial_placeholders (diagnostico)")
print("=" * 70)

# ── VERDE: condicion del render activa, tier B+ ──────────────────────────
propuesta = renderizar_propuesta("B+")
with tempfile.TemporaryDirectory() as t:
    v4_audit, deliveries = montar_run(Path(t), propuesta, diagnostico_render("B+"), "B+")
    reporte = revisar(v4_audit, deliveries)
n, emitidos = escaneo(reporte)
print(f"\n[VERDE] render B+ con condicion activa: summary.over_presentations = {n}")
for e in emitidos:
    print("   EMITIDO:", e["claim_text"], "|", e["matched_line"][:90])

# ── ROJO: condicion desactivada (A-bloque siempre visible), tier B+ ─────
original = V4ProposalGenerator._preprocess_conditionals


def mutante(self, template_content, data):
    datos = dict(data)
    datos["financial_evidence_tier"] = "A"  # condicion del render desactivada
    return original(self, template_content, datos)


V4ProposalGenerator._preprocess_conditionals = mutante
try:
    propuesta_mut = renderizar_propuesta("B+")
finally:
    V4ProposalGenerator._preprocess_conditionals = original

with tempfile.TemporaryDirectory() as t:
    v4_audit, deliveries = montar_run(Path(t), propuesta_mut, diagnostico_render("B+"), "B+")
    reporte_mut = revisar(v4_audit, deliveries)
n, emitidos = escaneo(reporte_mut)
print(f"\n[ROJO]  render B+ con condicion DESACTIVADA: summary.over_presentations = {n}")
for e in emitidos:
    print("   EMITIDO:", e["claim_text"], "|", e["matched_line"][:90])

# ── Par del contrato del diagnostico (strings precomputados) ────────────
titulo_v, cuerpo_v = claims_del_diagnostico("B+")
hallazgos_v = coincidencias_lenguaje_de_verificacion(f"{titulo_v}\n{cuerpo_v}\n")
print(f"\n[VERDE] strings diagnostico B+ (variante honesta): "
      f"{len(hallazgos_v)} hallazgos de la funcion real")

orig_ph = V4DiagnosticGenerator._build_financial_placeholders


def mutante_ph(self, *args, **kwargs):
    datos = orig_ph(self, *args, **kwargs)
    datos["garantias_titulo"] = f"🛡️ GARANTÍAS: {CLAIM_1_A}"
    datos["garantias_cuerpo"] = f"**{CLAIM_2_A}**: reporte mensual con métricas reales."
    return datos


V4DiagnosticGenerator._build_financial_placeholders = mutante_ph
try:
    titulo_r, cuerpo_r = claims_del_diagnostico("B+")
finally:
    V4DiagnosticGenerator._build_financial_placeholders = orig_ph
hallazgos_r = coincidencias_lenguaje_de_verificacion(f"{titulo_r}\n{cuerpo_r}\n")
print(f"[ROJO]  strings diagnostico B+ forzados a variante A: "
      f"{len(hallazgos_r)} hallazgos de la funcion real")
for h in hallazgos_r:
    print("   EMITIDO:", h["literal"], "|", h["linea"][:90])

print("\nResta publicada (antes -> despues): 2 emitidos -> 0 emitidos.")
print("Verificador mecanico de la resta: NO EXISTE — se declara (L-R.4 / R2.7).")
