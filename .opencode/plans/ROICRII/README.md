# ROICRII — Fix QA Report v3 (Post-ROICR Structural Fixes)

**Versión**: v1.0.0 (plan)
**Target Release**: v4.55.0 → v4.56.0 — ROICRII
**Creado**: 2026-05-27
**Origen**: `ROICRII.md` (reporte de QA v3 — auditoría de tercer orden vs código vivo)
**Objetivo**: Corregir los 4 hallazgos CRÍTICOS + 3 IMPORTANTES que hacen que la propuesta de Hotel Castilla Real sea **NO APTA PARA ENVÍO AL CLIENTE** (score actual: 72%, 18/25 checkpoints).

---

## Resumen del Problema

El plan ROICR (FASE-1 a FASE-7, v4.55.0) implementó correctamente la **capa cosmética** del refactor (separación CAPEX/OPEX, curva de maduración, garantía Día 55). Pero la auditoría ROICRII v3 reveló que la **capa estructural** falló:

| # | Hallazgo | Severidad | Verificado |
|---|----------|-----------|------------|
| CRIT-01 | 3 sistemas ROI paralelos — solo uno debe quedar | 🔴 CRÍTICO | ✅ L1492, L1534, roi_formatter L25 (0 calls) |
| NEW-03 | ROI inconsistente entre commercial gate y documento | 🔴 CRÍTICO | ✅ L377 vs L1550 |
| CRIT-02 | Ethical cap pipeline existe pero wrapper no lo activa | 🔴 CRÍTICO | ✅ L143 wrapper vs L264 pipeline |
| IMP-01 | pain_ratio ≠ fee/loss — confusión semántica | 🟡 IMPORTANTE | ✅ L793-801 |
| IMP-02 | Formato `:.1f` produce display incorrecto (absorbido CRIT-01) | 🟡 IMPORTANTE | ✅ L1515, L1554, roi_formatter:81 |
| NEW-05 | operational_floor con dos fallbacks distintos | 🟡 IMPORTANTE | ✅ L245 vs L329 |
| NEW-02 | Commercial gate no previene publicación para audiencia externa | 🟡 IMPORTANTE | ✅ L394-412 |
| IMP-03 | SETUP_FEE sin desglose de componentes | 🟡 IMPORTANTE | ✅ L126 |
| NEW-04 | pain_ratio concepto sobrecargado (3 significados) | 🟡 IMPORTANTE | ✅ L707, L795, pricing.yaml |

**Solución**: 5 fases — 3 de código, 1 de tests, 1 v4complete con análisis post-implementación.

---

## Fases del Plan

| Fase | Descripción | Tipo | Hallazgos | Prerrequisito |
|------|-------------|------|-----------|---------------|
| **FASE-1** | Unificar ROI: eliminar motores inline, usar roi_formatter como motor único, formato `:.2f` | Código+Tests | CRIT-01, IMP-02 | Ninguno |
| **FASE-2** | Corregir coherencia financiera: gate ROI opex-only + wrapper activa pipeline 3 pasos | Código+Tests | NEW-03, CRIT-02 | FASE-1 |
| **FASE-3** | Semántica + Floor + Gate estricto: pain_ratio clarificado, floor unificado, strict_mode externo | Código+Tests | IMP-01, NEW-05, NEW-02 | FASE-2 |
| **FASE-4** | CAPEX desglose + renombrar variables sobrecargadas | Código+Tests | IMP-03, NEW-04 | FASE-3 |
| **FASE-5** | v4complete Hotel Castilla Real + análisis post-implementación 5 niveles | Ejecución+Análisis | Todos | FASE-4 |

| **FASE-6** | RELEASE v4.56.0: version bump, CHANGELOG, REGISTRY, domain primer, pre-commit | Docs+Sync | — | FASE-5 |

**Total**: 6 sesiones. 1 fase por sesión. 1 v4complete en FASE-5. FASE-6 = RELEASE.

---

## Métricas Base (pre-ROICRII, post-ROICR)

| Métrica | Valor Actual |
|---------|-------------|
| Versión | v4.55.0 |
| Coherence Score | 0.826 |
| Publication Gates | 10/11 |
| ROI Castilla Real | 1.1X (saas) / 0.4X (legacy) — inconsistente |
| Formato ROI | `:.1f` (3 decimales perdidos) |
| Pipeline 3 pasos | Implementado pero NUNCA activado desde wrapper |
| Commercial gate | Calcula ROI con CAPEX, documento sin CAPEX |
| pain_ratio | 3 significados distintos |
| operational_floor | 2 fallbacks (400K vs 800K) |
| Gate externo | Solo logging, no bloquea |

---

## Métricas Objetivo (post-ROICRII)

| Métrica | Objetivo |
|---------|----------|
| ROI display | `:.2f` (precisión 2 decimales) |
| ROI motor | Solo `roi_formatter.py` (0 métodos inline) |
| Gate ROI formula | `total_recovery / (price_monthly * 6)` — SIN CAPEX |
| Pipeline 3 pasos | Activa desde wrapper vía `expected_recovery_cop` |
| pain_ratio | 2 semánticas separadas: `addressable_pain_ratio` + `fee_to_loss_ratio` |
| operational_floor | Fallback único 400K |
| Gate externo | `CommercialGateBlockedError` para audiencia ≠ internal |
| CAPEX | Desglose en componentes (no monto monolítico) |
| QA Score | ≥ 90% (23/25 checkpoints) |

---

## Criterio de Éxito Final (FASE-5)

Al completar FASE-5, el output de v4complete para Hotel Castilla Real debe satisfacer:

- [ ] **Nivel 1 — ROI Unificado**: `_calculate_roi()` y `_calculate_roi_saas()` eliminados. `roi_formatter.py` es el motor único. Formato `:.2f` en todas las salidas.
- [ ] **Nivel 2 — Coherencia Financiera**: Commercial gate calcula ROI con `price_monthly * 6` (sin CAPEX). Wrapper pasa `expected_recovery_cop` → pipeline 3 pasos activo.
- [ ] **Nivel 3 — Gobernanza Semántica**: `pain_ratio_note` diferencia addressable vs fee/loss. `operational_floor` fallback único 400K.
- [ ] **Nivel 4 — Gate Estricto**: Audiencia externa lanza `CommercialGateBlockedError` si gates fallan. CAPEX desglosado en componentes.
- [ ] **Nivel 5 — CI/CD**: pytest completo sin regresiones. Coherence ≥ 0.80.

---

## Archivos del Plan
| `05-prompt-inicio-sesion-fase-6.md` | Prompt para FASE-6 (RELEASE) |

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Este archivo — índice del plan |
| `dependencias-fases.md` | Diagrama de dependencias entre fases |
| `05-prompt-inicio-sesion-fase-1.md` | Prompt para FASE-1 (Unificar ROI) |
| `05-prompt-inicio-sesion-fase-2.md` | Prompt para FASE-2 (Coherencia Financiera) |
| `05-prompt-inicio-sesion-fase-3.md` | Prompt para FASE-3 (Semántica + Floor + Gate) |
| `05-prompt-inicio-sesion-fase-4.md` | Prompt para FASE-4 (CAPEX + Renombrar) |
| `05-prompt-inicio-sesion-fase-5.md` | Prompt para FASE-5 (v4complete + Análisis) |
| `06-checklist-implementacion.md` | Checklist maestro de implementación |
| `09-documentacion-post-proyecto.md` | Acumulador de documentación post-fase |

---

## Lo que este plan NO hace

- ❌ NO repite los fixes del plan ROICR (ya completados: semántica, gates, pipeline, curva, garantía)
- ❌ NO toca el plan ROI-REFACTOR ni el plan ROICR
- ❌ NO modifica la fórmula base del ROI — solo la unifica y presenta correctamente
- ❌ NO crea archivos que no existen (lección ROICRII v2→v3: solo archivos verificados)

---

## Lo que SÍ se preserva

- ✅ Todas las implementaciones previas de ROICR (FASE-1 a FASE-7)
- ✅ roi_formatter.py (ya implementado — solo falta usarlo)
- ✅ Pipeline 3 pasos de pricing_calculator.py (ya implementado — solo falta activarlo)
- ✅ Asset semantics validator, gates P1, garantía Día 55 (todo de ROICR)
