# Checklist Maestro de Implementación — DT-4 Residual Fixes

> **Última sesión cerrada**: 2026-07-28 FASE-6 post-audit fixes (DT4-N7 + DT4-N8)
> **Última fase cerrada**: FASE-6
> **Próxima tarea**: FASE-RELEASE v4.66.0 o decisión comercial CG-ROI-NEGATIVE

## Estado de Fases

| Fase | Título | Estado | Cerrada | Pendiente |
|------|--------|--------|---------|-----------|
| FASE-1 | DT4-R1-CONTRACT — pain_ledger_resolved injection | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-2 | DT4-R2-SITE-PRESENCE — Normalización + wiring ★ | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-3 | DT4-N4-COHERENCE — Unify coherence source | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-4 | DT4-N5-ALIGNMENT — Unify alignment | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-5 | DT4-N3-GATE-IDEMPOTENCY — Single execution | ✅ COMPLETADA | 2026-07-27 | — |
| FASE-6 | E2E-ZIONE — v4complete + verification | ✅ COMPLETADA | 2026-07-28 | Hallazgos resueltos en post-audit (ver abajo) |
| FASE-6-A | DT4-N7 — Fix path pain_ledger_resolved | ✅ COMPLETADA | 2026-07-28 | — |
| FASE-6-B | DT4-N8 — Fix delivery alignment C9 | ✅ COMPLETADA | 2026-07-28 | — |
| FASE-RELEASE | v4.66.0 — Docs + version bump | 🔓 PENDIENTE | — | CG-ROI-NEGATIVE + CG-TECH-JARGON (comercial, no técnico) |

## Log de Cierres de Sesión

| Fase | Fecha | Hallazgos |
|------|-------|-----------|
| FASE-1 | 2026-07-27 | Implementación correcta |
| FASE-2 | 2026-07-27 | Implementación correcta |
| FASE-3 | 2026-07-27 | Implementación correcta |
| FASE-4 | 2026-07-27 | Implementación correcta (parcial: delivery report no actualizado — corregido en FASE-6-B) |
| FASE-5 | 2026-07-27 | Implementación correcta |
| FASE-6 | 2026-07-28 | **BUG CRÍTICO**: main.py:2690 path sin hotel_id → C2-C4-C12-C14 FAIL. **BUG SECUNDARIO**: C9 delivery alignment divergente. Ver `08-analisis-post-implementacion.md`. |
| FASE-6-A | 2026-07-28 | **DT4-N7 corregido**: `output_dir / hotel_id / "v4_audit" / "pain_ledger_resolved.json"`. coverage_no_silent_drop: justified=0→9, uncovered=[]→[]. |
| FASE-6-B | 2026-07-28 | **DT4-N8 corregido**: `from_asset_alignment_matrix()` cross-referencea SitePresence. Delivery: status FAIL→PASS, 5/5 gates, present_in_production=0→2. Consistente con gate_report. |

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

- [x] `pain_ledger_resolved` existe en el contrato de assessment
- [x] El assessment usado por publication gates contiene el ledger reconciliado
- [x] `coverage_no_silent_drop` cuenta `no_whatsapp_visible` como justificado
- [x] Gate report muestra `justified >= 1` y `uncovered = []` para Zi One
- [x] Boost SitePresence se ejecuta en CoherenceValidator con reporte real
- [x] `whatsapp_verified.score` deja de ser 0.30 cuando SitePresence confirma `exists`
- [x] Dataclass, dict serializado y enum/string tienen única normalización
- [x] No hay reejecuciones redundantes de SitePresence
- [x] Publication y delivery alignment reportan mismo contrato y totales
- [x] Score final de coherencia es único y trazable
- [x] Tests de integración existen (no solo unitarios)
- [x] Zi One validado post-fixes
- [ ] Decisión explícita sobre CG-ROI-NEGATIVE documentada
- [x] Documentos existen y no fueron eliminados por otro gate
