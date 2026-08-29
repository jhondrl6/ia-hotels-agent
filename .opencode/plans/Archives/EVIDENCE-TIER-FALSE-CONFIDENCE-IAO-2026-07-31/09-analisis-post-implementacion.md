# Analisis Post-Implementacion: EVIDENCE-TIER-FALSE-CONFIDENCE-IAO

> **Estado**: COMPLETADO (2026-07-31)
> **Plan**: EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31 (CORREGIDO tras auditoria 2026-07-31)
> **Version final**: v4.68.0 (pendiente RELEASE)
> **Hallazgos totales**: 20/20 verificados (12 originales + 8 nuevos NP1-NP8)

---

## Resumen de Ejecucion

| Fase | Sesion | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-1 | 2026-07-31 | ✅ COMPLETADO | 1 | ❌ DIRECTA | T0/T0b (NP1-NP4) + T1-T4. 7 archivos. Tests: 10/10 financial_breakdown + 17/17 financial_evidence. B_PLUS introducido. |
| FASE-2 | 2026-07-31 | ✅ COMPLETADO | 1 | ❌ DIRECTA | T0 NP5 + T1-T4. 4 archivos. 549/550 tests pasan. has_onboarding sin fallback. precision_tier visible. |
| FASE-3 | 2026-07-31 | ✅ COMPLETADO | 1 | ❌ DIRECTA | T1 NP7 (gate per-hotel, sin os.getenv) + T2 (caller en v4_diagnostic_generator) + T3 NP6 (MANIFEST en delivery_packager.py). 3 archivos + main.py caller. 549/550 tests pasan. |
| FASE-4 | 2026-07-31 | ✅ COMPLETADO | 1 | ❌ DIRECTA | T0 NP3 (5 suites validadas, 0 fixes) + T1 (9 unit tests) + T2 (5 integration tests) + T3 (8 gate tests). Archivo nuevo: test_evidence_tier.py (22 tests, 365 lineas). Tests: 549+22 passed, 1 pre-existente OpenRouter. |
| FASE-5 | 2026-07-31 | ✅ COMPLETADO | 1 | ✅ MIXTO | T0 NP8 (control hotel_test_001, delegate_task) + T1 (Zi One, delegate_task) + T2 (evidencia) + T3 (verificacion 20/20) + T4 (analisis). v4complete Zi One: Tier B+, honesto. v4complete control: Tier B, sin regresion. |

### Evidencia v4complete FASE-5

| Hotel | evidence_tier | precision_tier | Disclaimer | Gate CG-EVIDENCE-TIER | has_onboarding |
|-------|---------------|----------------|------------|----------------------|----------------|
| **Zi One Luxury** | **B+** ✅ | C | "Datos operativos verificados de su hotel... Conecte GA4 y Search Console" | INFO (passed, tier != A) | True (4 campos) ✅ |
| **Hotel Visperas (control)** | **B** ✅ | C | "Estimación basada en benchmarks regionales y datos de su web. Para mayor precision, conecte GA4." | INFO (passed, tier != A) | False (defaults usados) ✅ |

---

## Matriz de Verificacion de Hallazgos (20/20 ✅)

### 12 hallazgos originales del plan

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| 1 | Tier A falso sin GA4 | B+ | **B+** en financial_evidence_tier | ✅ |
| 2 | Disclaimer "GA4 verificado" | NO dice GA4 verificado | 0 matches en diagnostico | ✅ |
| 3 | Contradiccion 84 vs 215 vs 276 | Consistente | CTA: "conecte GA4", fuentes: "GA4: No configurado", disclaimer: "Conecte GA4..." — consistente | ✅ |
| 4 | _determine_evidence_tier sin check | B+ | evidence_tier = "B+" en financial_scenarios.json | ✅ |
| 5 | EvidenceTier.A.disclaimer falso | N/A (tier != A) | No aplica (tier=B+) | ✅ |
| 6 | has_onboarding hardcodeado False | "datos operativos verificados" | Log: "Onboarding data loaded: 4 campos confirmados" | ✅ |
| 7 | Propuesta 3 tiers diferentes | Un solo tier | Solo Tier B+ en disclaimer, 0 "benchmarks regionales" | ✅ |
| 8 | relationship text hardcodeado | Dinamico | "evidence_tier B+ limita precision_tier a C" — usa tier real | ✅ |
| 9 | precision_tier no visible | Visible | Linea 217: "Precision: **Tier C**" | ✅ |
| 10 | Template legend sin B+ | Incluye B+ | Linea 219: "Tier B+: Datos operativos verificados" | ✅ |
| 11 | Sin gate GA4/GSC | CG-EVIDENCE-TIER-CONSISTENCY | Gate ejecutado (severity=INFO para B+, passed). Codigo en commercial_gate.py:662 | ✅ |
| 12 | MANIFEST sin metadata | quality_metadata presente | zione_20260731_MANIFEST.json: quality_metadata.evidence_tier = "B+" | ✅ |

### 8 hallazgos nuevos NP1-NP8 (auditoria 2026-07-31)

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| 13 | **NP1** hook_pdf_generator rechaza B+ | PDF sin WARN | valid_tiers = {"A", "B+", "B", "C"} en codigo | ✅ |
| 14 | **NP2** publication_gates:399 logica rota | tier_message coherente | Log: "tier_c_onboarding_required: Tier B+: Datos suficientes" | ✅ |
| 15 | **NP3** tests pre-existentes rompen con B_PLUS | Tests pasan | FASE-4 T0: 5 suites validadas, 0 fixes necesarios | ✅ |
| 16 | **NP4** default "A" en diagnostic generator | Default "C" | evidence_tier: str = "C" en v4_diagnostic_generator.py:1059 | ✅ |
| 17 | **NP5** fallback silencioso has_onboarding | Param pasado correctamente | 0 matches de getattr(pricing_result, 'is_onboarding') | ✅ |
| 18 | **NP6** MANIFEST ubicacion incorrecta | delivery_packager.py | 3 matches de quality_metadata en delivery_packager.py, 0 en main.py | ✅ |
| 19 | **NP7** gate usa env vars globales | Gate con params per-hotel | Recibe ga4_available/gsc_available como params, NO os.getenv | ✅ |
| 20 | **NP8** control sin onboarding | Tier C/B, sin regresion | hotel_test_001: evidence_tier = "B" (default, NO B+ ni A) | ✅ |

---

## Tabla de Riesgos (Post-Implementacion)

| Riesgo | Probabilidad | Impacto | Ocurrio? | Notas |
|--------|-------------|---------|----------|-------|
| Fix rompe tiering hoteles con GA4 | BAJA | ALTO | **NO** | T1 test case cubierto en FASE-4 |
| B_PLUS no propagado a consumers downstream | ALTA | CRITICO | **NO** | T0/T0b de FASE-1 + FASE-5 verificacion confirman |
| CG-EVIDENCE-TIER-CONSISTENCY usa env vars globales | MEDIA | ALTO | **NO** | NP7 corregido: params per-hotel |
| MANIFEST no se enriquece | BAJA | MEDIO | **NO** | NP6 corregido: quality_metadata en delivery_packager.py |
| Test pre-existentes rompen con B_PLUS | ALTA | ALTO | **NO** | FASE-4 T0 confirmo: 5 suites pasan con 0 fixes |
| Default "A" en diagnostic generator | MEDIA | ALTO | **NO** | NP4 corregido: default "C" |
| has_onboarding fallback silencioso | ALTA | ALTO | **NO** | NP5 corregido: getattr eliminado |
| Regresion en hoteles sin onboarding | ALTA | MEDIO | **NO** | hotel_test_001: Tier B (sin B+, sin A) |
| Service account GCP no existe | ALTA | MEDIO | PENDIENTE | OUT OF PLAN — user action |
| v4complete Zi One timeout | MEDIA | BAJO | **NO** | Completo en ~120s |
| v4complete control timeout | MEDIA | MEDIO | **NO** | Completo en ~137s |

---

## Lecciones Aprendidas

### 1. Efectividad del plan corregido

La auditoria pre-ejecucion que detecto NP1-NP8 fue CRITICA. Sin ella, el plan original de 12 hallazgos habria introducido regressions silenciosas. Los 8 hallazgos nuevos fueron todos reales y bloqueadores:
- **NP1/NP2** (consumers downstream): sin fix previo, B_PLUS habria causado WARN en PDFs y mensajes incoherentes en gates
- **NP3** (tests pre-existentes): 5 suites necesitaban validacion; afortunadamente ninguna requirio fixes
- **NP4** (default "A"): bug latente que solo se manifiesta cuando financial_breakdown es None
- **NP5** (fallback silencioso): el getattr con default=False ocultaba el bug
- **NP6** (MANIFEST ubicacion): error de documentacion que habria causado enrichment en archivo equivocado
- **NP7** (env vars): diseno incorrecto que no respetaba arquitectura per-hotel
- **NP8** (control): omitido en plan original, critico para verificar no-regresion

### 2. Fase mas dificil

**FASE-1** fue la mas compleja (7 archivos, cross-module signature change). La complejidad vino de:
- Introducir B_PLUS requirio limpiar consumers downstream PRIMERO (T0/T0b)
- Cambiar firma de `_determine_evidence_tier()` impacto a callers en scenario_calculator y main.py
- Default "C" vs "A" (NP4) requirio decision arquitectonica: conservador > liberal

### 3. Mayor sorpresa

**CG-EVIDENCE-TIER-CONSISTENCY no aparece en el reporte de gates comerciales** porque para tiers != A devuelve severity=INFO. El sistema filtra INFO del reporte (solo BLOCKING/WARNING visibles). Esto es comportamiento correcto pero no documentado — en FASE-5 esperabamos ver el gate en el reporte.

### 4. Mejora para proximo plan

- **Documentar filtros de severidad en gates**: INFO-level results no son visibles en reportes. Si un gate solo debe ser visible cuando BLOCKING, documentarlo explicitamente.
- **Control test con URL real**: La URL placeholder del plan ("example-hotel-sin-onboarding.com") obligo a improvisar. Incluir URL real en el plan.
- **Verificar integracion completa**: El gate existe en codigo pero no era visible en reporte → verificar que cada cambio de codigo sea verificable en el output final.

### 5. Patron reutilizable

- **Auditoria pre-ejecucion con grep exhaustivo**: el patron de buscar TODOS los consumers de un enum/campo antes de modificarlo evito regressions. Aplicable a cualquier cambio cross-module.
- **T0/T0b como pre-requisito**: limpiar consumers downstream ANTES de introducir el nuevo valor (B_PLUS) evito el tipico "agregar enum → arreglar consumers despues".
- **Control de caso default (NP8)**: siempre incluir un test del caso sin datos cuando se introduce una nueva rama logica.

---

### Lecciones de la auditoria (especificas de este plan)

- **Auditoria pre-ejecucion detecto 8 bloqueadores**: NP1-NP8 no estaban en el plan original. Sin esta auditoria, FASE-1 habria introducido regressions silenciosas en PDFs (NP1), publication gates (NP2), y tests pre-existentes (NP3). Patron a aplicar: SIEMPRE grep exhaustivo de todos los consumers del enum/campo a modificar antes de cambiar firma.
- **NP5 (fallback silencioso `getattr`)** es un patron critico: el codigo parecia funcionar pero el `getattr` con default False ocultaba el bug. Patron a aplicar: preferir firmas explicitas con parametros obligatorios sobre `getattr` defensivos.
- **NP7 (env vars globales vs per-hotel)** es un anti-patron de diseno: el sistema ya usa `ga4_property_id` per-hotel via CLI flag, pero el plan asumia env vars globales. Patron a aplicar: leer el codigo de integracion (main.py) ANTES de disenar gates que consultan estado externo.
- **NP8 (control de regresion sin onboarding)** fue omitido en el plan original. La leccion previa §6 "Regresion en hoteles sin onboarding" del plan ONBOARDING-INJECTION-GAP no verificada se manifesto como riesgo real. Patron a aplicar: SIEMPRE incluir control del caso default (sin datos) cuando se introduce un nuevo enum value o rama logica.

---

## Artefactos Entregables

| Artefacto | Path | Estado |
|-----------|------|--------|
| Plan maestro | `/.opencode/plans/Archives/EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31/01-plan-maestro.md` | ✅ CORREGIDO |
| Prompts de fase | `02-07-prompt-fase-*.md` | ✅ CORREGIDOS |
| Checklist | `08-checklist-implementacion.md` | ✅ ACTUALIZADO (FASE-5 completada) |
| Analisis | `09-analisis-post-implementacion.md` | ✅ COMPLETADO |
| Evidencia v4complete Zi One | `evidence/FASE-5/zione/` | ✅ 6 archivos |
| Evidencia v4complete control | `evidence/FASE-5/control-sin-onboarding/` | ✅ 4 archivos |
| Codigo FASE-1 | `data_structures.py`, `hook_pdf_generator.py`, `publication_gates.py`, `v4_diagnostic_generator.py`, `scenario_calculator.py`, `test_financial_breakdown.py`, `main.py` | ✅ Committed (5def28a) |
| Codigo FASE-2 | `v4_proposal_generator.py`, `v4_diagnostic_generator.py`, `diagnostico_v6_template.md`, `propuesta_v6_template.md`, `main.py` | ✅ Committed (259e0ed) |
| Codigo FASE-3 | `commercial_gate.py`, `v4_diagnostic_generator.py`, `delivery_packager.py`, `main.py` | ✅ Committed (cd17fb9) |
| Tests FASE-4 | `tests/test_evidence_tier.py` (22 tests, 365 lineas) | ✅ Committed (24fd6fe) |
| CHANGELOG [4.68.0] | `CHANGELOG.md` | ⬜ PENDIENTE (FASE-RELEASE) |
| Tag v4.68.0 | git | ⬜ PENDIENTE (FASE-RELEASE) |
