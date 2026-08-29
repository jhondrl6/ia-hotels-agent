# Documentación Post-Proyecto — DT-4 Residual Fixes

> **Versión target**: v4.66.0
> **Se completa incrementalmente al cerrar cada fase**

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| SitePresence canonical adapter | `modules/asset_generation/site_presence_adapter.py` | `normalize_site_presence()` — adapta SitePresenceReport, asdict() y None a dict canónico con top-level keys para CoherenceValidator | FASE-2 |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| pain_ledger_resolved en AssessmentPayload | assessment_builder | Campo nuevo en dataclass + builder method | FASE-1 |
| SitePresence canonical adapter | site_presence_adapter | Normalización dataclass↔dict↔enum con top-level keys para CoherenceValidator | FASE-2 |
| SitePresence single-computation | main.py | Una llamada a SitePresenceChecker antes de coherence gate, snapshot propagado | FASE-2 |
| SitePresence en 3 CoherenceValidator calls | main.py + v4_asset_orchestrator | Pre-assets, pre-gen, post-gen reciben site_presence_report | FASE-2 |
| Eliminación de reconstrucción fake + re-ejecución | publication_gates | ~55 líneas eliminadas de L861-919 | FASE-2 |
| final_coherence_report | v4_asset_orchestrator | Fuente única de score post-generación | FASE-3 |
| AlignmentResult DTO | publication_gates | Resultado canónico de alignment compartido entre publication_gates y modules/quality_gates/delivery_quality_report | FASE-4 |
| Gate single-execution path | main.py + publication_gates | Eliminación de doble ejecución y mutaciones | FASE-5 |
| E2E-Zione v4complete verification | FASE-6 | v4complete ejecutado vía delegate_task, 14 criterios verificados, análisis post-implementación | FASE-6 |

## Sección C: Bugs Corregidos

| Bug | Causa | Fix | Fase |
|-----|-------|-----|------|
| coverage_no_silent_drop FAILED para no_whatsapp_visible | pain_ledger_resolved no inyectado en assessment | Campo + builder + inyección | FASE-1 |
| whatsapp_verified.score = 0.30 pese a site_verified=true | site_presence_report no propagado a CoherenceValidator | Wire 3 call sites + adapter | FASE-2 |
| SitePresenceChecker ejecutado 2x en pipeline | Llamada en main.py L2670 + publication_gates L895 | Una llamada upfront, snapshot propagado | FASE-2 |
| Fake SitePresenceReport construido con SimpleNamespace | publication_gates L861-890 | Eliminado — usa snapshot canónico | FASE-2 |
| Coherence score usa pre-gen (0.84) cuando post-gen es 0.82 | AssessmentBuilder.with_coherence() usa reporte pre-gen | final_coherence_report como fuente | FASE-3 |
| gate_report dice 5/7, delivery dice 7/7 | Distinta semántica de denominador | AlignmentResult DTO compartido | FASE-4 |
| Gates se ejecutan 2 veces y mutan assessment | check_publication_readiness() re-ejecuta run_publication_gates() | Una ejecución, derivar readiness | FASE-5 |
| **BUG ENCONTRADO**: pain_ledger_resolved path sin hotel_id | main.py:2690 usa `output_dir / "v4_audit"` en vez de `output_dir / hotel_id / "v4_audit"` | Fix: agregar `hotel_id` al path | FASE-6 |
| **BUG ENCONTRADO**: Delivery report no usa AlignmentResult DTO | delivery_quality_report.py no consume el DTO canónico | Pendiente — muestra `present_in_production=0` vs `2` reales | FASE-6 |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos | 10 (6 funciones + 4 parametrized) | FASE-2 |
| Tests existentes sin regresión | 61/61 (50 pre-existing + 11 new adapter tests) | FASE-2 |
| Archivos nuevos | 2 (site_presence_adapter.py + test) | FASE-2 |
| Archivos modificados | 4 (main.py, v4_asset_orchestrator.py, coherence_validator.py, publication_gates.py) | FASE-2 |
| Líneas eliminadas | ~71 (55 publication_gates + 16 main.py) | FASE-2 |
| Solo 1 fallo pre-existente (test_generated_assets_4_of_8_score — no relacionado) | | FASE-2 |
| Tests nuevos | 3 (idempotency: doble ejecución, no mutación, no re-ejecución) | FASE-5 |
| Tests existentes sin regresión | 293/293 (quality_gates suite completa) | FASE-5 |
| Archivos modificados | 2 (publication_gates.py, main.py) | FASE-5 |
| Solo 1 fallo pre-existente (test_gate_presence_with_skipped_assets — FASE-2) | | FASE-5 |
| **FASE-6: Verificación E2E** | | |
| v4complete ejecutado (exit_code=0, ~80s) | Zi One Luxury | FASE-6 |
| Verificación 14 criterios | 7/13 PASSED, 5 FAILED (3 por bug de path), 1 WARNING | FASE-6 |
| delegate_task viability | ✅ v4complete subagente exitoso (~3min total) | FASE-6 |
| Archivos nuevos | 3 (/.opencode/plans/Archives/DT4-RESIDUAL-FIXES/08-analisis-post-implementacion.md, evidence/FASE-6/ con 16 archivos, BLOCKED_BY_GATES.md) | FASE-6 |
| **Fixes pendientes para RELEASE** | | |
| Bug path pain_ledger_resolved | main.py:2690 — 1 línea (agregar `hotel_id /`) | FASE-6 |
| Delivery report AlignmentResult | delivery_quality_report.py — consumir DTO canónico | FASE-6 |
| CG-ROI-NEGATIVE | Decisión comercial — no es bug técnico | FASE-6 |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `main.py` | +19 líneas (SitePresence snapshot before coherence gate); wire to CoherenceValidator; wire to orchestrator; remove duplicate | FASE-2 |
| `modules/commercial_documents/coherence_validator.py` | Docstring actualizado con site_presence_report | FASE-2 |
| `modules/asset_generation/v4_asset_orchestrator.py` | Parámetro site_presence_report en generate_assets(); wire a pre + post coherence | FASE-2 |
| `modules/quality_gates/publication_gates.py` | -63 líneas (fake reconstruction + re-execution eliminados) | FASE-2 |
| `modules/quality_gates/publication_gates.py` | Refactor: `check_publication_readiness()` acepta `gate_results` opcional; backward-compat conservada | FASE-5 |
| `main.py` | L2796: pasa `gate_results` a `check_publication_readiness()` — ejecución única | FASE-5 |
| `tests/quality_gates/test_coverage_gate.py` | +3 tests de idempotencia (TestGateIdempotency class) | FASE-5 |
| `/.opencode/plans/Archives/DT4-RESIDUAL-FIXES/08-analisis-post-implementacion.md` | Análisis completo post-implementación (11KB, 8 secciones) | FASE-6 |
| `/.opencode/plans/Archives/DT4-RESIDUAL-FIXES/evidence/FASE-6/` | 16 archivos JSON de evidencia + BLOCKED_BY_GATES.md | FASE-6 |
| `/.opencode/plans/Archives/DT4-RESIDUAL-FIXES/06-checklist-implementacion.md` | Actualizado con FASE-6 status y log de cierres | FASE-6 |
| `/.opencode/plans/Archives/DT4-RESIDUAL-FIXES/09-documentacion-post-proyecto.md` | Este archivo — actualizado con FASE-6 | FASE-6 |
