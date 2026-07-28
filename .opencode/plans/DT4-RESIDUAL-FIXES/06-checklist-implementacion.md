# Checklist Maestro de Implementación — DT-4 Residual Fixes

> **Última sesión cerrada**: 2026-07-27 FASE-2
> **Última fase cerrada**: FASE-2
> **Próxima tarea**: FASE-3 (requiere FASE-2 completada)

## Estado de Fases

| Fase | Título | Estado | Cerrada | Pendiente |
|------|--------|--------|---------|-----------|
| FASE-1 | DT4-R1-CONTRACT — pain_ledger_resolved injection | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-2 | DT4-R2-SITE-PRESENCE — Normalización + wiring ★ | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-3 | DT4-N4-COHERENCE — Unify coherence source | ⬜ PENDIENTE | — | Requiere FASE-2 ✅ |
| FASE-4 | DT4-N5-ALIGNMENT — Unify alignment | ⬜ PENDIENTE | — | 4 tareas |
| FASE-5 | DT4-N3-GATE-IDEMPOTENCY — Single execution | ⬜ PENDIENTE | — | 4 tareas (requiere FASE-2 ✅) |
| FASE-6 | E2E-ZIONE — v4complete + verification | 🔒 BLOQUEADA | — | Requiere FASE-1,2,3,4,5 |
| FASE-RELEASE | v4.66.0 — Docs + version bump | 🔒 BLOQUEADA | — | Requiere FASE-6 |

## Log de Cierres de Sesión

*(Se completa al cerrar cada fase)*

## Decisiones Arquitectónicas

| # | Decisión | Respuesta |
|---|---------|-----------|
| 1 | ¿Agregar pain_ledger_resolved a AssessmentPayload o como dict suelto? | **Dataclass field** — tipado fuerte, consumidores existentes usan `.get()` |
| 2 | ¿Canonical SitePresence: dataclass o dict? | **Dict canónico** — `asdict()` produce dict, consumidores usan `.get()`, adapter en el borde |
| 3 | ¿final_coherence_report como campo nuevo en AssetGenerationResult? | **Sí** — pre/post se conservan como trazabilidad, final es fuente única |
| 4 | ¿Alignment DTO: nuevo dataclass o extender existente? | **Nuevo `AlignmentResult` dataclass** — consumido por pub gate + delivery report |
| 5 | ¿Eliminar `check_publication_readiness()` o refactorizar? | **Refactorizar** — derivar de `gate_results` ya calculados, no re-ejecutar |
| 6 | ¿CG-ROI-NEGATIVE: relajar, ocultar, o mantener? | **Mantener sin cambios** — es decisión comercial, no bug técnico |

## Criterios de Éxito Globales (del contexto §14)

- [ ] `pain_ledger_resolved` existe en el contrato de assessment
- [ ] El assessment usado por publication gates contiene el ledger reconciliado
- [ ] `coverage_no_silent_drop` cuenta `no_whatsapp_visible` como justificado
- [ ] Gate report muestra `justified >= 1` y `uncovered = []` para Zi One
- [ ] Boost SitePresence se ejecuta en CoherenceValidator con reporte real
- [ ] `whatsapp_verified.score` deja de ser 0.30 cuando SitePresence confirma `exists`
- [ ] Dataclass, dict serializado y enum/string tienen única normalización
- [ ] No hay reejecuciones redundantes de SitePresence
- [ ] Publication y delivery alignment reportan mismo contrato y totales
- [ ] Score final de coherencia es único y trazable
- [ ] Tests de integración existen (no solo unitarios)
- [ ] Zi One validado post-fixes
- [ ] Decisión explícita sobre CG-ROI-NEGATIVE documentada
- [ ] Documentos existen y no fueron eliminados por otro gate
