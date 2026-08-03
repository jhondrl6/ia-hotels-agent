# Documentación Post-Proyecto — COHERENCIA-MODULO-ENTREGA (v4.70.0)

> Acumulativo por fase. FASE-RELEASE usa estos datos para CHANGELOG y GUIA_TECNICA oficiales.
> Cada fase completa su columna "Fase" al cerrar (post-ejecución obligatoria).

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (posible) gate `doc_audit_consistency` | `modules/quality_gates/publication_gates.py` | Validación de pares doc↔audit (OG, reviews, fotos, performance) | C-A |
| (posible) helper compartido de recuperación 6m | `modules/financial_engine/pillar_maturity_curve.py` | Fórmula única de recuperación proyectada | B |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Brecha OG veraz (D1) | commercial_documents | `_pain_to_brecha` usa `pain.name`/`description` del mapper; ya no dice "Sin Meta Tags" con 8 tags detectados | A |
| Detección única de brechas | commercial_documents + main | `_identify_brechas` con inputs reales, una sola invocación | A |
| Costos de brecha de fuente única | financial_engine | `estimated_monthly_cop` == pesos normalizados del doc | B |
| Escenarios honestos en doc | commercial_documents | 3 escenarios reales con labels correctos + CG-SCENARIO-ORDER | B |
| Coverage gate honesto | quality_gates | covered cuenta antes de eximir; warning si covered=0 | C-A |
| Freshness v4_audit | delivery + proposal | commercial_gates_report fresco; históricos fuera del ZIP | D |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests iniciales | 3,185 funciones / 253 archivos | baseline |
| Tests nuevos acumulados | +6 (test_diagnostic_brechas.py → 40 passed) | A |
| Hallazgos cerrados | 2/21 (D1, D2) | A |
| Coherence última verificación | 0.9168 (run 2026-08-01) | baseline |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | D1 (pain.name) + D2 (firma/caché/narrativas/contadores dinámicos) | A |
| `main.py` | `brechas_reales` y `channel_context` con inputs reales | A |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Conteo dinámico `${brechas_*_count}` | A |
| `config/regional_benchmarks.yaml` | Pesos `low_seo_score`/`low_organic_visibility` en 4 regiones | A |
| `tests/commercial_documents/test_diagnostic_brechas.py` | +6 tests (OG 8 tags, N unificado, pesos YAML, template, caché, low_seo) | A |

## Notas para FASE-RELEASE

- CHANGELOG formato: `## [4.70.0] - Titulo — YYYY-MM-DD` con secciones Objetivo / Cambios / Archivos Nuevos / Archivos Modificados / Tests.
- GUIA_TECNICA: nota técnica por cada fase (módulos, problema/solución, backwards compatibility).
- Documentar explícitamente los cambios de comportamiento: pesos normalizan sobre N real (D2) y fórmula única de recuperación (N1) cambian cifras de TODOS los hoteles.
