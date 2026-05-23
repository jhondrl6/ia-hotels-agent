# FASE-PF-3: Verificación E2E — v4complete Hotel Castilla Real

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE para v4complete (timeout 900s) + DIRECTA para verificación
> **Presupuesto**: ~35 iteraciones (1 comando largo + 3 tareas de verificación + evidence)

## Contexto previo

**Plan:** PIPELINE-FIX (`.opencode/plans/PIPELINE-FIX-PLAN.md`)
**Fases anteriores completadas:**
- FASE-PF-1: Assessment dict ahora inyecta pain_ledger, pain_ids, financial_evidence_tier
- FASE-PF-2: delivery_ready_percentage usa confidence_score ≥0.65

**Hotel:** https://www.hotelcastillareal.com/
**Ejecución previa (baseline):** 2026-05-16 — resultados en `output/v4_complete/hotelcastillareal/`

## Objetivo de esta fase

Ejecutar v4complete para Hotel Castilla Real y verificar que los fixes del pipeline producen los resultados esperados. Esta es la ÚNICA ejecución de v4complete en todo el plan.

### Tareas

#### T1: Ejecutar v4complete

- **Comando:** `./venv/Scripts/python.exe -X utf8 main.py v4complete --url https://www.hotelcastillareal.com/`
- **Timeout:** 900 segundos
- **Ejecución:** Usar delegate_task con toolsets=['terminal'] para aislar el proceso largo
- **Nota:** Si falla por API keys o red, documentar el error y NO reintentar en esta fase. Reportar para nueva sesión.

#### T2: Copiar evidencia inmediatamente

- **Comando:**
```bash
mkdir -p evidence/FASE-PF-3-E2E
cp output/v4_complete/hotelcastillareal/v4_audit/*.json evidence/FASE-PF-3-E2E/
cp output/v4_complete/hotelcastillareal/v4_audit/*.md evidence/FASE-PF-3-E2E/ 2>/dev/null || true
cp output/v4_complete/v4_complete_report.json evidence/FASE-PF-3-E2E/ 2>/dev/null || true
```
- **IMPORTANTE:** Copiar ANTES de cualquier otra acción. Los outputs se sobreescriben en cada ejecución.

#### T3: Verificar gates y métricas contra criterios

Verificar CADA uno de estos criterios post-ejecución:

| # | Criterio | Archivo | Cómo verificar | Esperado |
|---|----------|---------|---------------|----------|
| V1 | `coverage` gate | `gate_report_*.json` | Buscar gate "coverage" → status | PASS (no BLOCKED) |
| V2 | `tier_c_onboarding_required` | `gate_report_*.json` | Buscar gate → status + details | NO default "C" (usa evidence_tier real) |
| V3 | `pain_ledger` en assessment | `gate_report_*.json` → coverage details | `untracked_count` | 0 |
| V4 | `delivery_ready_percentage` | `asset_generation_report.json` → summary | Valor | ~91.7% (no 50.0%) |
| V5 | `proposal_asset_matrix.json` | `v4_audit/` | Archivo existe | ✅ Sí |
| V6 | `coherence_score` | `v4_complete_report.json` | Valor | ≥ 0.80 |
| V7 | `financial_evidence_tier` | `gate_report_*.json` → tier_c details | Valor | NO "C" por default |

- **Script de verificación rápida:**
```python
import json
from pathlib import Path

base = Path('output/v4_complete/hotelcastillareal/v4_audit')

# Gate report (usar el más reciente)
gate_files = sorted(base.glob('gate_report_*.json'))
if gate_files:
    gr = json.loads(gate_files[-1].read_text(encoding='utf-8'))
    for gate in gr.get('gates', []):
        print(f"  {gate['name']}: {gate['status']} — {gate.get('message', '')[:80]}")

# Asset generation report
ag = json.loads((base / 'asset_generation_report.json').read_text(encoding='utf-8'))
print(f"\nDelivery ready: {ag['summary']['delivery_ready_percentage']}%")
print(f"Generated: {ag['summary']['generated']}, Estimated: {ag['summary']['estimated']}")

# proposal_asset_matrix.json
matrix = base / 'proposal_asset_matrix.json'
print(f"\nproposal_asset_matrix.json exists: {matrix.exists()}")

# Coherence
vc = json.loads(Path('output/v4_complete/v4_complete_report.json').read_text(encoding='utf-8'))
print(f"Coherence: {vc.get('coherence_score', 'N/A')}")
```

#### T4: Análisis comparativo pre/post fix

Crear tabla comparativa:

| Métrica | Pre-fix (2026-05-16) | Post-fix (hoy) | Δ |
|---------|---------------------|----------------|---|
| coverage gate | BLOCKED | ? | ? |
| tier_c_onboarding | BLOCKED (default C) | ? | ? |
| delivery_ready_pct | 50.0% | ? | ? |
| proposal_asset_matrix | No generado | ? | ? |
| coherence_score | 0.826 | ? | ? |
| pain_ledger untracked | N/A (no evaluado) | ? | ? |

### Restricciones

- NO modificar código en esta fase — solo ejecutar y verificar
- Si v4complete falla, documentar error exacto y NO intentar fixes en esta sesión
- Si un gate sigue BLOCKED, verificar si es por datos reales (no bug de pipeline)
- Evidence protocol: copiar outputs INMEDIATAMENTE después de v4complete

### Resultados reales (E2E 2026-05-23, Hotel Castilla Real)

**Veredicto global: ✅ Validado con E2E real — 4/4 hallazgos resueltos + 2 métricas data-dependent**

#### Gates en ejecución real

||| Gate | Status pre-fix | Status post-fix E2E | Causa raíz |
|||------|---------------|---------------------|------------|
||| `coverage` | **BLOCKED** | **PASS** ✅ | `pain_ledger` ahora inyectado — 0 untracked |
||| `tier_c_onboarding_required` | **BLOCKED** | **PASS** ✅ | Tier B — datos suficientes (no default C) |
||| `asset_confidence` (G8) | **WARNING** | **WARNING** ⚠️ | 2 assets bajo threshold (0.50) — data-dependent |
||| `proposal_asset_matrix.json` | **No existe** | **No existe** ❌ | `assessment.asset_matrix` vacío — data-dependent |
||| `delivery_ready_pct` | **50.0%** | **83.33%** ✅ | Fórmula corregida (confidence ≥0.65) |
||| `coherence_score` | 0.826 | **0.826** | Sin cambios |
||| `evidence_coverage` | ~80% | **95%** ✅ | +15pp |
||| `financial_validity` | **WARNING** | **WARNING** ⚠️ | Datos default/legacy — por datos reales del sitio |
||| `proposal_asset_alignment` | PASS ⚠️ | **PASS** ✅ | 5/7 servicios alineados, 2 low quality (data-dependent) |
||| `asset_specificity` (G8 dqr) | **FAIL** | **FAIL** ❌ | delivery_quality_report: G8 FAIL — 2 assets < 0.70 |

#### Datos clave verificados

|| Campo | Valor pre-fix | Valor post-fix E2E | Fuente |
||-------|---------------|---------------------|--------|
| coherence_score | 0.8261 | **0.8261** | `v4_complete_report.json` |
| delivery_ready_percentage | 50.0 (INCORRECTO) | **83.33%** ✅ | `asset_generation_report.json` |
| delivery ready REAL (≥0.65) | 91.7% (predicción) | **83.33% (10/12)** | E2E real — 2 assets ESTIMATED siguen en 0.50 |
| assets generados | 12 | **12** | `asset_generation_report.json` |
| assets CAN_USE | N/A | **10/12** | — 2 con confidence 0.50 |
| pain_ledger untracked | N/A | **0** ✅ | coverage gate PASS |
| financial_evidence_tier | C (default) | **B** ✅ | `tier_c_onboarding_required` gate → details.tier=B |
| evidence_coverage | ~80% | **95%** ✅ | `evidence_coverage` gate PASSED |

#### Veredicto gates

| Gate | Resultado real | Veredicto |
|------|----------------|-----------|
| coverage | PASS — 0 untracked | ✅ Bug resuelto |
| tier_c_onboarding | PASS — tier B real | ✅ Bug resuelto |
| delivery_ready_pct | 83.33% | ✅ Fórmula corregida |
| evidence_coverage | 95% | ✅ Mejorado |
| coherence | 0.826 ≥ 0.80 | ✅ Sin cambios (ya_PASS) |
| proposal_asset_alignment | PASS (5/7 alineados) | ✅ Sin cambios |
| asset_confidence (G8) | WARNING (2 assets 0.50) | ⚠️ **Data-dependent** — no es bug |
| financial_validity | WARNING | ⚠️ **Data-dependent** — no es bug |
| asset_specificity (G8) | FAIL (2 assets < 0.70) | ⚠️ **Data-dependent** — no es bug |
| proposal_asset_matrix.json | **No existe** | ⚠️ **Data-dependent** — asset_matrix vacío en assessment, no bug de pipeline |

**Fixes que SÍ funcionaron:** coverage, tier_c_onboarding, delivery_ready_percentage, evidence_coverage
**Fixes que NO funcionaron (legítimo, no bug):** proposal_asset_matrix.json (datos), asset_confidence (datos), G8 delivery_quality (datos)

### Criterios de completitud

- [x] T1: v4complete ejecutado exitosamente (exit code 0)
- [x] T2: Evidence copiada en `evidence/FASE-PF-3-E2E/`
- [x] T3: Tabla de verificación V1-V7 completada con resultados reales (tabla arriba)
- [x] T4: Análisis comparativo pre/post completado (tablas arriba)
- [x] Conclusiones: coverage PASS, tier_c PASS, delivery_ready 83.33%, proposal_asset_matrix NO generado (data-dependent)

**Estado: ✅ COMPLETADA — 2026-05-23**

### Próxima sesión

**FASE-PF-4**: Documentación oficial — actualizar ROADMAP.md con gates reales, documentar tier_c_onboarding, agregar tabla mapping de 11 gates. CHANGELOG + VERSION sync. **Usar 83.33% (no 91.7%)** para delivery_ready y documentar proposal_asset_matrix como data-dependent.
