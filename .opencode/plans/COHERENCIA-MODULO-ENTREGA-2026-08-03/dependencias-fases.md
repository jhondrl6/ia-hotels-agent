# Dependencias entre Fases — COHERENCIA-MODULO-ENTREGA-2026-08-03

> **Regla R1**: una fase por sesión. **Regla R3**: cada fase ≤ 4 tareas + ≤ 1 comando largo.
> RELEASE solo se ejecuta cuando TODAS las fases de implementación están ✅.

## Diagrama de dependencias

```
FASE-A (D1+D2, detección única)
   │   establece brechas_reales como fuente única
   ▼
FASE-B (D3+D4+N1, dinero único) ── depende de A: los costos se calculan
   │                                  sobre el N real de brechas de A
   ▼
FASE-C-A (D5+N2, gates reales) ── depende de A: coverage gate lee brechas_reales
   │                                y pain_ids del doc
   ▼
FASE-C-B (D6+D7+D8, textos dinámicos) ── depende de A (estructura del doc
   │                                       estable); paralelizable con C-A (archivos distintos)
   ▼
FASE-D (D9-D12+N4+N3+N5-N8, pulido+freshness) ── depende de B (N8 label de
   │                                              probabilidad exige D4 resuelto)
   ▼
FASE-E (E2E v4complete Zi One Luxury, ÚNICA ejecución) ── depende de A+B+C-A+C-B+D
   │
   ▼
FASE-RELEASE-4.70.0 (docs oficiales + flujo documental) ── depende de E ✅
```

**Nota de orden**: C-A y C-B no se tocan entre sí (archivos distintos) pero se
ejecutan en sesiones separadas por R1. Si alguna fase queda ⏳ INCOMPLETA, NO
avanzar a la siguiente sin resolver el checkpoint.

## Tabla de conflictos de archivos

| Archivo | Fase(s) | Secciones/líneas | Riesgo de conflicto |
|---------|---------|------------------|---------------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | A → B → C-B → D | A: L2823-3028 (`_identify_brechas`, `_pain_to_brecha`, `_normalize_weights`) · B: L1063-1240 (escenarios), L3217-3230 (`_compute_opportunity_scores`) · C-B: L316 (reviews), L1741 (performance) · D: L1854-1862 (social dedupe), L2458 (ortografía), L2471 (truncamiento) | MEDIO — orden estricto A→B→C-B→D; cada fase toca rangos disjuntos |
| `main.py` | A, D | A: L2638 (brechas_reales con inputs reales), L3290 (channel_context — actualizar inputs, NO eliminar) · D: L1878, L1937 (label occupancy) | BAJO — rangos disjuntos |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | A, C-B | A: L66-67 (conteo dinámico `${brechas_total_count}`) · C-B: L57 (N5), L112 y L228 (atribución GEO D8 — las L140/L299 del contexto son del DOC generado, no del template) | BAJO — rangos disjuntos |
| `modules/quality_gates/publication_gates.py` | C-A | L240-270 (`_hard_contradictions_gate`), L1263-1276 (`_coverage_gate`) | NINGUNO — fase única |
| `modules/financial_engine/opportunity_scorer.py` | B | L566 (`estimated_monthly_cop`) | NINGUNO — fase única |
| `modules/financial_engine/scenario_calculator.py` | B | L245/L300/L358 (probs), semántica labels | NINGUNO — fase única; NO tocar fórmulas de pérdida |
| `modules/financial_engine/pillar_maturity_curve.py` | B | L22 (CURVA_4_PILARES) | NINGUNO — fase única |
| `modules/commercial_documents/v4_proposal_generator.py` | B, D | B: reconciliación `recuperacion_proyectada_6m` · D: L629 (escribir commercial_gates_report SIEMPRE — hoy está en el branch de ERROR/raise, mover fuera) | BAJO |
| `modules/delivery/delivery_packager.py` | D | Solo criterio de selección de v4_audit (run_id/historico/) | NINGUNO — NO tocar arquitectura single-write |
| `output/clientes/zi-one-luxury_onboarding.yaml` | E (T0) | Agregar `url: https://zione.co` en sección `hotel` | NINGUNO |

## Matriz hallazgo → fase → verificación

| Hallazgo | Fase | Check de cierre (contexto §6) |
|----------|------|-------------------------------|
| D1 | A | Doc dice "Open Graph Tags Incompletos (8 tags)", no "Sin Meta Tags" |
| D2 | A | pain_ledger.json == brechas del doc (mismo N); template con conteo dinámico |
| D3 | B | `estimated_monthly_cop` del report == costos del doc |
| D4 | B | Doc muestra escenarios reales o rango renombrado; CG-SCENARIO-ORDER en gate_report |
| N1 | B | Diagnóstico y propuesta con MISMA recuperación 6m |
| D5 | C-A | gate_report: covered>0 o mensaje honesto |
| N2 | C-A | Gate detecta contradicción OG doc↔audit |
| D6 | C-B | Doc refleja "API key inválida" / estado real de performance |
| D7 | C-B | Sin "203 reseñas" |
| D8 | C-B | Atribución GEO correcta ("algoritmo propio de iah-cli sobre datos de Google Places") |
| D9 | D | Target fotos 40 ("subir al menos N fotos adicionales") |
| D10 | D | Redes sin duplicados, TikTok/YouTube si aplican |
| D11 | D | commercial_gates_report.json fresco (timestamp == run) |
| D12 | D | occupancy label "onboarding" cuando viene de onboarding |
| N4 | D | ZIP con SOLO artefactos del run actual |
| N3 | D (verif. E) | diff entre runs > 3 líneas |
| N5-N8 | D | Greps estáticos en 0 hits |
| E2E | E | Checklist completo 21/21 + coherence ≥ 0.8 + gates PASSED honestos |

## Presupuesto de iteraciones por fase (R2: máx 60)

| Fase | Trabajo | Verif+docs | Comandos largos | Total est. |
|------|---------|-----------|-----------------|-----------|
| A | ~25 | ~20 | 0 | ~45 |
| B | ~30 (decisión + 3 subsistemas) | ~25 | 0 | ~55 ⚠️ (la más ajustada) |
| C-A | ~25 | ~20 | 0 | ~45 |
| C-B | ~15 (delegado parcial) | ~20 | 0 | ~35 |
| D | ~20 + subagente N5-N8 | ~20 | 0 | ~40 |
| E | T0 + verificación ~25 | ~15 | 1 (v4complete, subagente) | ~42 |
| RELEASE | docs E1-E8b | — | 0 | ~30 |

## Estado de fases

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | ⏳ PENDIENTE | — | |
| FASE-B | ⏳ PENDIENTE | — | Mayor complejidad técnica |
| FASE-C-A | ⏳ PENDIENTE | — | |
| FASE-C-B | ⏳ PENDIENTE | — | |
| FASE-D | ⏳ PENDIENTE | — | |
| FASE-E | ⏳ PENDIENTE | — | Única ejecución v4complete |
| FASE-RELEASE-4.70.0 | ⏳ PENDIENTE | — | Requiere todas las anteriores ✅ |
