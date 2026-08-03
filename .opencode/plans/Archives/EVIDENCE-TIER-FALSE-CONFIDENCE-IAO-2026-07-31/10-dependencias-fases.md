# Dependencias entre Fases: EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31

> **Regla**: Una fase = una sesion. No ejecutar multiples fases en la misma sesion.
> **Orden**: Estrictamente secuencial. Cada fase depende de la anterior.
> **Auditoria 2026-07-31**: Dependencias actualizadas con T0/T0b de NP1-NP8.

---

## Grafo de Dependencias

```
FASE-1 (Root Cause + Downstream Consumers — 7 archivos)
  │  T0/T0b: Limpiar NP1-NP4 ANTES de introducir B_PLUS
  │  T1-T4: B_PLUS enum + HotelFinancialData + tier check + main.py wire
  │  Impacto: TODOS los hoteles. Tier A requiere GA4+GSC real per-hotel.
  │
  └─► FASE-2 (Proposal + Template Honesty + PricingResolution.is_onboarding)
       │  T0 NP5: Eliminar fallback silencioso de has_onboarding
       │  Depende de: B_PLUS enum + downstream limpio (FASE-1)
       │  Cambia: v4_proposal_generator.py, v4_diagnostic_generator.py, template, main.py
       │
       └─► FASE-3 (Quality Gate per-hotel + Delivery Enrichment)
            │  T1 NP7: Gate con params per-hotel (NO env vars globales)
            │  T3 NP6: MANIFEST en delivery_packager.py (NO main.py)
            │  Depende de: Tier corregido (FASE-1) + has_onboarding wiring (FASE-2)
            │  Cambia: commercial_gate.py, delivery_quality.py, delivery_packager.py, main.py
            │
            └─► FASE-4 (Tests + Update Existing Tests)
                 │  T0 NP3: Validar tests pre-existentes compatibles con B_PLUS
                 │  Depende de: Codigo estable de FASE-1, FASE-2, FASE-3
                 │  Cambia: tests/
                 │
                 └─► FASE-5 (v4complete + Control + Analisis)
                      │  T0 NP8: v4complete control sin onboarding (hotel_test_001)
                      │  T1: v4complete Zi One Luxury (Tier B+ esperado)
                      │  Depende de: Todos los fixes + tests verdes (FASE-1 a FASE-4)
                      │  Ejecuta: 2 v4complete (Zi One + control)
                      │
                      └─► FASE-RELEASE (v4.68.0)
                           │  Depende de: FASE-5 verificada (Zi One + control)
                           │  Cambia: VERSION.yaml, CHANGELOG, docs
```

---

## Tabla de Dependencias

| Fase | Depende de | Bloquea a | Razon |
|------|-----------|-----------|-------|
| FASE-1 | — (inicio) | FASE-2, FASE-3, FASE-4, FASE-5, RELEASE | Cambia la logica CORE de tiering + limpia consumers downstream |
| FASE-2 | FASE-1 | FASE-3, FASE-4, FASE-5, RELEASE | Necesita B_PLUS enum + downstream limpio + elimina fallback silencioso (NP5) |
| FASE-3 | FASE-1, FASE-2 | FASE-4, FASE-5, RELEASE | Gate valida tier corregido + MANIFEST en delivery_packager.py (NP6) |
| FASE-4 | FASE-1, FASE-2, FASE-3 | FASE-5, RELEASE | Tests sobre codigo estable + valida tests pre-existentes (NP3) |
| FASE-5 | FASE-1, FASE-2, FASE-3, FASE-4 | RELEASE | v4complete Zi One (B+) + control hotel_test_001 (C) verifica todo |
| RELEASE | FASE-5 | — (fin) | Docs + version bump (CHANGELOG incluye NP1-NP8) |

---

## Que pasa si una fase falla?

| Escenario | Accion |
|-----------|--------|
| FASE-1 T0 falla (NP1-NP4 no corregidos) | NO continuar a T1-T4. El fix introducira regressions silenciosas. |
| FASE-1 T1-T4 falla (tests rompen) | Rollback del patch. Investigar causa. Reintentar en nueva sesion. |
| FASE-2 T0 NP5 falla (fallback no se puede eliminar) | Rollback al estado pre-T0. Investigar por que pricing_result.is_onboarding existe. |
| FASE-2 T1-T4 falla (template inconsistency) | Rollback del template. No afecta FASE-1. |
| FASE-3 T1 NP7 falla (gate no recibe params per-hotel) | Investigar caller en main.py. Sin params per-hotel, gate usa env vars globales (incorrecto). |
| FASE-3 T3 NP6 falla (MANIFEST no se enriquece) | Verificar ubicacion en delivery_packager.py, NO main.py. |
| FASE-4 T0 NP3 falla (tests pre-existentes no compatibles) | Aplicar T0.2 fixes. Si no se puede, escalar a user. |
| FASE-4 T1-T4 falla (test no pasa) | Fix el test o el codigo. No continuar a FASE-5 sin tests verdes. |
| FASE-5 T0 NP8 falla (control sin onboarding → tier != C) | **CRITICO**: hay regresion. Rollback FASE-1/FASE-2. Investigar causa. |
| FASE-5 T1 falla (v4complete Zi One timeout o tier != B+) | Recovery pattern: verificar output parcial. Re-ejecutar si es necesario. |
| RELEASE falla (sync_versions crash) | Fix version/codename. Re-ejecutar. Problema conocido con unicode. |

---

## Artefactos por Fase

| Fase | Archivos modificados | Tests creados/modificados | Output generado |
|------|---------------------|---------------------------|-----------------|
| FASE-1 | 7 (.py: 4 originales + 3 consumers downstream por NP1-NP4) | 1 modificado (test_financial_breakdown.py por NP3) | — |
| FASE-2 | 5 (.py: 4 originales + 1 fix NP5) | 0 | — |
| FASE-3 | 4 (.py: 3 originales + 1 caller en main.py por NP7) | 0 | — |
| FASE-4 | 1+ (tests/) | 1+ nuevo + multiples modificados (T0 NP3) | — |
| FASE-5 | 0 | 0 | v4complete output Zi One + control + analisis |
| RELEASE | 5+ (YAML/MD) | 0 | CHANGELOG, tag |

---

## Pre-requisitos Operacionales (OUT OF PLAN pero importantes)

- **H12 Service account GCP**: Sin esto, el CTA "conecte GA4" en el documento no es accionable. El hotel no podra conectar GA4 aunque quiera. Documentado en `01-plan-maestro.md` como accion manual del usuario. Si el usuario NO crea la service account antes de FASE-5, los diagnosticos se entregaran con CTA no accionable (riesgo reputacional).
