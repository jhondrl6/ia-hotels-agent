# FASE-6-HOTFIX — G6 WON'T FIX

**Fecha**: 2026-05-12
**Audit reference**: `AUDITORIA_FASE5_G1_G6_G7_20260512.md`
**Gate**: G6 — hotel_schema poblado
**Veredicto**: WON'T FIX

---

## Decisión

G6 se marca como **WON'T FIX** — no es un bug de código.

## Causa Raíz

`hotel_schema.json` se genera con datos disponibles (web scraping + GBP + benchmark).
Sin onboarding real, faltan:

| Campo | Fuente posible | Disponible sin onboarding |
|-------|---------------|--------------------------|
| amenities detallados | Onboarding | ❌ |
| checkInTime/checkOutTime reales | Onboarding | ❌ |
| starRating verificado | Onboarding | ❌ |
| roomTypes específicos | Onboarding | ❌ |
| ADR real | Onboarding | ❌ |
| ocupación real | Onboarding | ❌ |

El sistema **funciona correctamente**: genera el schema con los datos disponibles.
El gate FASE-4 ya bloquea correctamente cuando el 100% de assets son `ESTIMATED`.

## Acción Documentada

- Docstring agregado en `v4_asset_orchestrator.py` `_extract_validated_fields`:
  > G6 WON'T FIX: Los siguientes campos del hotel_schema requieren datos de onboarding real y no pueden poblarse solo con web scraping + GBP + benchmark.

- No se modificó la lógica de generación del schema.

## Solución Real

La solución real es **onboard al hotel** para obtener:
- Amenities detallados (checkInTime, checkOutTime, roomTypes, starRating)
- Datos financieros reales (ADR, ocupación)

Esto está fuera del scope de FASE-6-HOTFIX.
