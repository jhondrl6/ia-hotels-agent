# Dependencias de Fases

| Fase | Estado | Fecha | Dependencias | Detalles |
|------|--------|-------|--------------|----------|
| **FASE-1-COH** | ✅ Completada | 2026-05-11 | Ninguna | Unificar CoherenceValidator ↔ CoherenceGate: execute() integra validator, main.py unifica fuente de coherence_score, 7 tests nuevos de integración |
| FASE-1A | ✅ Completada | 2026-04-28 | Ninguna | Fix Estado Entregables: site_presence_report call chain en v4_proposal_generator.py + SitePresenceChecker en main.py |
| FASE-1B | ✅ Completada | 2026-04-28 | FASE-1A | v4complete x2 -- RESUELTO: (1) COP COP fix en template L125; (2) confidence_score default en Scenario constructors (0.85/0.70/0.50); (3) urgencia_content guard para 0% -> texto escalonado. Gate NOT_READY por bug estructural: ContentScrubber valida diagnostico STALE (pre-T4FIX). Fix pendiente: mover ContentScrubber post-T4FIX en main.py. Evidencia: evidence/fase-1b-amazilia-verificacion/ |
| FASE-1C | ✅ Completada | 2026-04-28 | FASE-1B-PATCH | Documentacion cascade (CHANGELOG, GUIA_TECNICA) |
| **FASE-1** | ✅ Completada | 2026-05-11 | Ninguna | Coherence post-generacion: _validate_post_generation() en v4_asset_orchestrator.py + main.py consume post_coherence_score |
| **FASE-2** | ✅ Completada | 2026-05-11 | FASE-1 | Propuesta completa + Gate robusto: 8 servicios con estados, assets tecnicos visibles, threshold Gate 0.8 |
| **FASE-2-DEFAULT** | ✅ Completada | 2026-05-11 | FASE-1-COH | Eliminar defaults hardcodeados cross-hotel en open_graph_generator.py + fix conditional_generator.py para usar API pública generate_content(). 11 tests nuevos. |
| **FASE-3-CONTENT** | ✅ Completada | 2026-05-12 | FASE-2-DEFAULT | Fix local_content location validation (fallback Colombia), unificar evidence_tier via FinancialBreakdown, renombrar all_aligned a all_covered con alias deprecado. 8 tests nuevos. |
| **FASE-4-GATE** | ✅ Completada | 2026-05-12 | FASE-3-CONTENT | Hardening de gate asset_confidence: BLOCKED cuando 100% assets son ESTIMATED (confidence < 0.7). 3 tests nuevos. |
| **FASE-3** | ✅ Completada | 2026-05-11 | FASE-2 | Monthly report fail-safe: try/except+retry, disclaimer en propuesta, fix bug runtime 'list' object has no attribute 'items' |
| **FASE-4** | ✅ Completada | 2026-05-11 | FASE-3 | Correccion financiera: normalizacion brechas al valor central, separacion pain_ratio vs recovery_factor |
| **FASE-5** | ✅ Completada | 2026-05-11 | FASE-4 | Verificacion E2E: v4complete para Termales Santa Rosa de Cabal + analisis de ejecucion |
| **FASE-5-VERIFY** | ✅ Completada | 2026-05-12 | FASE-4-GATE | v4complete Hotel Castilla Real post-refactor: 7/10 garantías PASS, G1 cv/gate diverge (+0.016), G7 WhatsApp confidence=0.5 (< 0.7). Gate coherence=0.826 >= 0.8. |
| **FASE-RELEASE** | ✅ Completada | 2026-05-11 | FASE-1..5 | Documentacion oficial: version bump 4.44.0, CHANGELOG, GUIA_TECNICA, REGISTRY, sync_versions |
| **FASE-A** | ✅ Completada | 2026-05-14 | Ninguna | Parche inmediato validate_document_integration.py con TextIOWrapper UTF-8. Plan: FIX-ENCODING-SISTEMICO-2026-05 |
| **FASE-B** | ✅ Completada | 2026-05-14 | FASE-A | Parche 3 scripts (verify_ga4, validate_structure, update_benchmarks) + verificar 4 ya parcheados (main.py, derive_version_from_changelog, version_consistency_checker, log_phase_completion) + validación (run_all_validations --quick 5/5). Plan: FIX-ENCODING-SISTEMICO-2026-05 |
| **FASE-C** | ✅ Completada | 2026-05-14 | FASE-B | Configuración anti-reintentos Hermes: tool_loop_guardrails.hard_stop_enabled + hard_stop_after.exact_failure=3. Investigación cleanup procesos (SIGTERM → SIGKILL). Plan: FIX-ENCODING-SISTEMICO-2026-05 |
| **FASE-D** | ✅ Completada | 2026-05-14 | FASE-C | Documentación y reglas: sección "Encoding en scripts Python" en CONTRIBUTING.md + gate en documentation_rules.md. Plan: FIX-ENCODING-SISTEMICO-2026-05 |
| **FASE-RELEASE-ENC** | ✅ Completada | 2026-05-14 | FASE-D | Docs cascade: CHANGELOG v4.46.1, version bump, sync_versions, GUIA_TECNICA, DOMAIN_PRIMER, validaciones 5/5. Plan: FIX-ENCODING-SISTEMICO-2026-05 |

---

## Notas

- FASE-1-COH pertenece al plan `05-prompt-inicio-sesion-fase-1-COH.md` (nuevo plan de unificación CoherenceValidator ↔ CoherenceGate).
- FASE-1A/B/C pertenecen a plan anterior (AmaziliaHotel). No deben bloquear el nuevo plan.
- FASE-1..5 y RELEASE pertenecen a plan `00-plan-refactor-coherencia-termales.md`.
- Regla: FASE-RELEASE solo ejecuta cuando TODAS las fases 1-5 tienen ✅.
- Contexto completo: `.opencode/context/AUDITORIA_DIAG_PROP_COHERENCIA_TERMALES_20260509.md`
- **Cierre del proyecto**: Refactorizacion de coherencia Termales COMPLETADA. v4.44.0 -- TERMALES-COHERENCE-FIX
