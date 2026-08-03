# Documentación Post-Proyecto — COHERENCIA-MODULO-ENTREGA (v4.70.0)

> Acumulativo por fase. FASE-RELEASE usa estos datos para CHANGELOG y GUIA_TECNICA oficiales.
> Cada fase completa su columna "Fase" al cerrar (post-ejecución obligatoria).

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| gate `doc_audit_consistency` | `modules/quality_gates/publication_gates.py` | Validación WARNING de pares doc↔audit (OG, reviews, fotos, performance) — DEC-C1/C2 | C-A |
| helper compartido de recuperación 6m | `modules/financial_engine/pillar_maturity_curve.py` | Fórmula única de recuperación proyectada | B |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Brecha OG veraz (D1) | commercial_documents | `_pain_to_brecha` usa `pain.name`/`description` del mapper; ya no dice "Sin Meta Tags" con 8 tags detectados | A |
| Detección única de brechas | commercial_documents + main | `_identify_brechas` con inputs reales, una sola invocación | A |
| Costos de brecha de fuente única | financial_engine | `estimated_monthly_cop` == pesos normalizados del doc | B |
| Escenarios honestos en doc | commercial_documents | 3 escenarios reales con labels correctos + CG-SCENARIO-ORDER | B |
| Coverage gate honesto | quality_gates | covered cuenta antes de eximir; warning si covered=0 (D5) | C-A |
| Gate doc↔audit consistency | quality_gates | Detecta contradicciones OG, reviews, fotos, performance entre doc y audit (N2, WARNING mode DEC-C1) | C-A |
| Freshness v4_audit | delivery + proposal | commercial_gates_report fresco; históricos fuera del ZIP | D |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests iniciales | 3,185 funciones / 253 archivos | baseline |
| Tests nuevos acumulados | +6 (test_diagnostic_brechas.py → 40 passed) | A |
| Tests nuevos acumulados | +14 (8 nuevos FASE-B + 6 FASE-A) | B |
| Tests nuevos acumulados | +13 (9 nuevos doc_audit + 4 coverage honest) | C-A |
| Hallazgos cerrados | 2/21 (D1, D2) | A |
| Hallazgos cerrados | 5/21 (D1, D2, D3, D4, N1) | B |
| Hallazgos cerrados | 7/21 (+D5, +N2) | C-A |
| Coherence última verificación | 0.9168 (run 2026-08-01) | baseline |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | D1 (pain.name) + D2 (firma/caché/narrativas/contadores dinámicos) | A |
| `main.py` | `brechas_reales` y `channel_context` con inputs reales | A |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Conteo dinámico `${brechas_*_count}` | A |
| `config/regional_benchmarks.yaml` | Pesos `low_seo_score`/`low_organic_visibility` en 4 regiones | A |
| `tests/commercial_documents/test_diagnostic_brechas.py` | +6 tests (OG 8 tags, N unificado, pesos YAML, template, caché, low_seo) | A |
| `modules/financial_engine/pillar_maturity_curve.py` | `calcular_recuperacion_6m()` — fórmula ÚNICA de recuperación 6m (N1) | B |
| `modules/commercial_documents/v4_diagnostic_generator.py` | D3: `estimated_monthly_cop` alineado por pain_id con pesos normalizados · D4: tabla de escenarios reales, `financial_method` derivado, `financial_value_range_label`, urgencia N8 · N1: `recuperacion_proyectada_6m` con curva · persistencia `commercial_gates_report_diagnostic_<ts>.json` | B |
| `modules/commercial_documents/v4_proposal_generator.py` | N1: gate `net_benefit_6m`/`roi` y `recovered_6m`/`net_benefit_6m` con `calcular_recuperacion_6m` (curva única) | B |
| `modules/quality_gates/commercial_gate.py` | CG-SCENARIO-ORDER con semántica real (conservador = peor caso = mayor pérdida) | B |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Sección "Lo que está en juego" con curva de maduración; frontmatter `financial_value_range_label` | B |
| `tests/commercial_documents/test_fase_f_financial_placeholders.py` | +3 tests (curva N1, nota curva, range label) + method derivado | B |
| `tests/commercial_documents/test_diagnostic_brechas.py` | +2 tests D3 (costo == doc, impacto == peso) | B |
| `tests/commercial_documents/test_financial_coherence.py` | +2 tests N1 (wrapper curva, caso Zione $9.691.220) | B |
| `tests/quality_gates/test_commercial_gate.py` | 2 tests actualizados a semántica real del orden de escenarios | B |
| `modules/quality_gates/publication_gates.py` | D5: `_coverage_gate` reestructurado (covered cuenta antes de justified) + WARNING si covered=0 · N2: nuevo gate `_doc_audit_consistency_gate` (WARNING, DEC-C1) con 4 patrones (OG, reviews, fotos, performance) | C-A |
| `tests/quality_gates/test_doc_audit_consistency_gate.py` | +9 tests nuevos (OG, performance, reviews, fotos, consistente, sin doc, sin audit, no bloquea, múltiples) | C-A |
| `tests/quality_gates/test_coverage_gate.py` | +4 tests TestCoverageHonestCount (D5) + 2 tests actualizados (status→WARNING) | C-A |
| `tests/quality_gates/test_coverage_gate_integration.py` | 1 test actualizado (acepta WARNING) | C-A |
| `tests/quality_gates/test_publication_gates.py` | 3 aserciones actualizadas: gate count 11→12 | C-A |

## Notas para FASE-RELEASE

- **DEC-C1**: Gate `doc_audit_consistency` nace en modo WARNING (no bloquea publicación). Upgrade a BLOCKING documentado para release posterior. Riesgo: si naciera BLOCKING, fallarían runs existentes con contradicciones hoy invisibles.
- **DEC-C2**: Mecanismo de evidencia — Opción A (evidence_used.json / diagnostic_evidence) con fallback a B (parseo de patrones en markdown). El gate usa `_DOC_AUDIT_CONTRADICTION_PATTERNS` declarativo.
- CHANGELOG formato: `## [4.70.0] - Titulo — YYYY-MM-DD` con secciones Objetivo / Cambios / Archivos Nuevos / Archivos Modificados / Tests.
- GUIA_TECNICA: nota técnica por cada fase (módulos, problema/solución, backwards compatibility).
- Documentar explícitamente los cambios de comportamiento: pesos normalizan sobre N real (D2) y fórmula única de recuperación (N1) cambian cifras de TODOS los hoteles.
