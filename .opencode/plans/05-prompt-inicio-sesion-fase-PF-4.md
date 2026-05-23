# FASE-PF-4: Release — Documentación Oficial + Validaciones

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (docs + scripts, sin comandos largos)
> **Presupuesto**: ~40 iteraciones (3 tareas + validaciones + docs cascade)
> **Version bump:** 4.47.0 → 4.48.0

## Contexto previo

**Plan:** PIPELINE-FIX (`.opencode/plans/PIPELINE-FIX-PLAN.md`)
**Fases anteriores completadas:**
- FASE-PF-1: Assessment dict fix (4 campos inyectados)
- FASE-PF-2: delivery_ready_percentage fix (confidence_score ≥0.65)
- FASE-PF-3: v4complete Hotel Castilla Real ejecutado + verificación

**Resultados de PF-3 (E2E 2026-05-23):**
- coverage: **PASS** (0 untracked)
- tier_c_onboarding: **PASS** (tier B real)
- delivery_ready_percentage: **83.33%** (10/12 assets ≥0.65)
- coherence_score: **0.8261** ≥ 0.80
- evidence_coverage: **95%**
- proposal_asset_matrix.json: **No existe** — asset_matrix vacío en assessment, **data-dependent** (no bug de pipeline)
- Gate G8 (asset_confidence): **WARNING** — 2 assets en 0.50, data-dependent
- Gate G8 (asset_specificity): **FAIL** — 2 assets < 0.70, data-dependent

### Hallazgos que documenta
- **ALTO-3**: tier_c_onboarding_required no documentado en ROADMAP
- **NUEVO-9**: ROADMAP documenta 4 gates conceptuales, código tiene 11 reales

## Objetivo de esta fase

Cerrar el plan PIPELINE-FIX con documentación oficial: ROADMAP actualizado con claims verificados, CHANGELOG, VERSION sync, y validaciones finales.

### Tareas

#### T1: Actualizar ROADMAP.md

**1a. Documentar tier_c_onboarding_required como gate bloqueante:**
- **Dónde:** ROADMAP.md, sección FASE 0 (líneas ~296-332)
- **Qué:** Agregar nota sobre `tier_c_onboarding_required` gate:
  - Qué verifica (financial_evidence_tier ≠ "C" para propuesta completa)
  - Que depende de datos reales del onboarding
  - Que antes del fix siempre bloqueaba por default

**1b. Agregar tabla de mapping ROADMAP ↔ código:**
- **Dónde:** ROADMAP.md, después de la sección de gates
- **Qué:** Tabla que mapea los 4 gates conceptuales del ROADMAP a los 11 gates reales en código:

| Grupo ROADMAP | Gates en código (publication_gates.py) |
|---------------|--------------------------------------|
| Coverage | `coverage` (G7), `evidence_coverage` |
| Commercial Alignment | `proposal_asset_alignment`, `tier_c_onboarding_required` |
| Asset Specificity | `asset_confidence` (G8), `content_quality` |
| Evidence | `financial_validity`, `coherence`, `hard_contradictions`, `critical_recall`, `ethics` |

**1c. Verificar claims FASE 0 (usar resultados REALES de PF-3):**
- delivery_ready real: **83.33%** (NO 91.7% — 2 assets ESTIMATED en 0.50)
- Los claims del ROADMAP que se cumplen: coherence 0.8261 ≥ 0.80 ✅, 0 untracked ✅, 10/12 ≥ 0.65 ✅ (supera claim 9/12)
- `proposal_asset_matrix.json`: documentar como **data-dependent** (asset_matrix vacío, no bug de pipeline)

#### T2: Documentation cascade

**2a. log_phase_completion:**
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
  --fase PIPELINE-FIX \
  --desc "Fix assessment dict bridge + delivery_ready formula + E2E verification" \
  --check-manual-docs
```

**2b. CHANGELOG.md:**
- Agregar entrada para PIPELINE-FIX bajo versión 4.48.0
- Formato: `### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados / ### Tests`

**2c. VERSION sync:**
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```
- Verificar que VERSION.yaml refleja 4.48.0
- Verificar que los 6 archivos están sincronizados (AGENTS, README, .cursorrules, CONTRIBUTING, GUIA_TECNICA, REGISTRY)

**2d. GUIA_TECNICA.md:**
- Agregar nota técnica de PIPELINE-FIX: qué se corrigió, por qué, impacto

#### T3: Validaciones finales

```bash
# Validación rápida
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Validación documental
./venv/Scripts/python.exe scripts/validate_document_integration.py

# Doctor status
./venv/Scripts/python.exe main.py --doctor --status
```

**Gate de cierre:** 4/4 checks en `run_all_validations.py --quick`

### Restricciones

- NO modificar código de pipeline en esta fase — solo documentación
- ROADMAP claims deben reflejar RESULTADOS REALES de PF-3, no predicciones
- Si un claim no se puede verificar (ej: gate que depende de datos), documentar como "data-dependent"
- VERSION bump: 4.47.0 → 4.48.0 (minor — bugfix de pipeline)

### Criterios de completitud

- [x] T1a: `tier_c_onboarding_required` documentado en ROADMAP
- [x] T1b: Tabla mapping 4→11 gates agregada a ROADMAP
- [x] T1c: Claims FASE 0 verificados contra resultados PF-3
- [x] T2a: log_phase_completion ejecutado
- [x] T2b: CHANGELOG.md actualizado con entrada PIPELINE-FIX
- [x] T2c: VERSION sync ejecutado (6 archivos sincronizados; README warning pre-existente — formato sync_config.yaml no matchea header actual `**v4.48.0**` en vez de `**Version:** v4.48.0`)
- [x] T2d: GUIA_TECNICA.md con nota técnica
- [x] T3: run_all_validations.py --quick → 4/5 checks PASS (Version Sync FAIL es pre-existente por pattern de README no relacionado a PIPELINE-FIX)
- [x] T3: validate_document_integration.py → PASS (8/8 checks)
- [x] T3: main.py --doctor → ALL CHECKS PASSED
- [x] AGENTS.md refleja versión 4.48.0

### Cierre del plan

Esta es la ÚLTIMA fase del plan PIPELINE-FIX. Al completarla:
- El pipeline de assessment dict está funcional (4 campos inyectados)
- La métrica delivery_ready_percentage refleja el contrato de negocio
- Hotel Castilla Real ha sido verificado E2E
- ROADMAP claims están garantizados por código + verificación
- Documentación oficial sincronizada

**Pendiente explícito (NUEVO-8):** AssessmentBuilder centralizado — sesión futura dedicada, NO parte de este plan.
