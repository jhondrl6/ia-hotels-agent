# Documentación Post-Proyecto: Refactorización Coherencia Termales

> Plan: `00-plan-refactor-coherencia-termales.md`  
> Versión objetivo: 4.44.0  
> Fecha inicio: 2026-05-09

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| *(ninguno — refactor, no nuevos módulos)* | — | — | — |

---

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Coherence post-generación | `v4_asset_orchestrator.py` | Re-valida coherencia con assets reales post-generación | FASE-1 |
| Propuesta 8 servicios | `v4_proposal_generator.py` | Muestra todos los servicios de PROPOSAL_SERVICE_TO_ASSET con estados | FASE-2 |
| Assets técnicos visibles | `v4_proposal_generator.py` + `service_catalog.py` | analytics_setup_guide e indirect_traffic_optimization en propuesta | FASE-2 |
| Gate 9 threshold 0.8 | `publication_gates.py` | Bloquea publicación si alignment < 80% | FASE-2 |
| Monthly report fail-safe | `conditional_generator.py` | Try/except + retry para monthly_report | FASE-3 |
| Monthly report bug fix | `monthly_report_generator.py` | Corrige `'list' object has no attribute 'items'` | FASE-3 |
| Disclaimer monthly report | `v4_proposal_generator.py` | Nota en propuesta cuando monthly_report falla | FASE-3 |
| Normalización brechas | `v4_proposal_generator.py` | Suma de brechas = financial_value_central exacto | FASE-4 |
| Separación pain/recovery | `v4_proposal_generator.py` + templates | Distingue pain_ratio vs recovery_factor | FASE-4 |

---

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Hallazgos corregidos | 8/8 | FASE-1 a FASE-4 |
| Tests nuevos | 19+ (3-7 por fase) | FASE-1 a FASE-4 |
| Regresiones | 0 | Todas |
| Coherence score post-gen | TBD | FASE-5 |
| Servicios en propuesta | 8 (vs 3 anterior) | FASE-2 |
| Gate 9 umbral | 0.8 (vs 0.5 anterior) | FASE-2 |
| Diferencia brechas | 0 COP (vs 373 COP anterior) | FASE-4 |
| v4complete ejecuciones | 1 | FASE-5 |

---

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/asset_generation/v4_asset_orchestrator.py` | `_validate_post_generation()` + reporte dual scores | FASE-1 |
| `main.py` | Consume coherence_score_post en DiagnosticSummary | FASE-1 |
| `modules/commercial_documents/coherence_validator.py` | Posible ajuste en cómo se consume generated_assets | FASE-1 |
| `modules/commercial_documents/v4_proposal_generator.py` | 8 servicios, assets técnicos, disclaimer monthly, brechas normalizadas, pain/recovery | FASE-2,3,4 |
| `modules/commercial_documents/service_catalog.py` | Entradas analytics_setup_guide e indirect_traffic_optimization | FASE-2 |
| `modules/quality_gates/publication_gates.py` | Umbral Gate 9: 0.5 → 0.8 | FASE-2 |
| `modules/asset_generation/conditional_generator.py` | Try/except + retry monthly_report | FASE-3 |
| `modules/asset_generation/monthly_report_generator.py` | Fix bug list→dict | FASE-3 |
| `tests/commercial_documents/test_proposal_fase4_h3_h4.py` | 7 tests: H3 normalización + H4 separación pain/recovery | FASE-4 |
| `VERSION.yaml` | 4.43.0 → 4.44.0 | FASE-RELEASE |
| `GUIA_TECNICA.md` | Notas técnicas FASE-1 a FASE-5 | FASE-RELEASE |
| `REGISTRY.md` | Registro de 5 fases | FASE-RELEASE |
| `dependencias-fases.md` | Estado ✅ FASE-1 a FASE-RELEASE | FASE-RELEASE |
