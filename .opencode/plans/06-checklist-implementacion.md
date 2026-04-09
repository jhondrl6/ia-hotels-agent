# Checklist de Implementacion — Correccion Falsos Positivos

> **Proyecto:** iah-cli v4.25.x  
> **Hotel validacion:** amaziliahotel.com  
> **Fecha:** 2026-04-09

---

## FASE-A: WhatsApp Detection Fix

**Dependencias:** Ninguna  
**Archivos:** v4_comprehensive.py, data_structures.py, v4_diagnostic_generator.py

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Conectar scraper `_detectar_whatsapp()` al pipeline de validacion | [x] Completado |
| T2 | Agregar `whatsapp_html_detected` a `ValidationSummary` en data_structures.py | [x] Completado |
| T3 | Actualizar condicion brecha WhatsApp en v4_diagnostic_generator.py:1799-1810 | [x] Completado |
| T4 | Actualizar quick wins (linea 1013-1018) | [x] Completado |
| T5 | Actualizar tabla brechas (linea 941-949) | [x] Completado |
| T6 | Tests de regresion pasan (25/25) | [x] Completado |
| T7 | log_phase_completion.py ejecutado | [x] Completado |

---

## FASE-B: Citability Narrative Fix

**Dependencias:** Ninguna (independiente de FASE-A)  
**Archivos:** v4_diagnostic_generator.py, opportunity_scorer.py, test_diagnostic_brechas.py

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Diferenciar `blocks_analyzed=0` vs score real bajo en `_detect_brechas` (lineas 1868-1890) | [x] Completado |
| T2 | Actualizar narrativa opportunity_scorer.py justificacion low_citability | [x] Completado |
| T3 | Verificar pain_solution_mapper alignment (sin cambios, optimization_guide) | [x] Completado |
| T4 | Tests de regresion pasan (218 passed, 7 pre-existentes) | [x] Completado |
| T5 | log_phase_completion.py ejecutado | [x] Completado |

---

## FASE-C: Regional Template Fixes

**Dependencias:** Ninguna (independiente de FASE-A/B)  
**Archivos:** diagnostico_v6_template.md, v4_diagnostic_generator.py

| # | Tarea | Estado |
|---|-------|--------|
|| T1 | Corregir typo `yRevisan` en template linea 27 | [x] Completado |
|| T2 | Agregar "Eje Cafetero" al mapping `region_contexts` (lineas 1613-1620) | [x] Completado |
|| T3 | Corregir fallback regional generico (linea 1627) | [x] Completado |
|| T4 | Verificar hotel_region fallback (linea 413) | [x] Completado |
|| T5 | Tests de regresion pasan (218 passed, 7 pre-existentes) | [x] Completado |
|| T6 | log_phase_completion.py ejecutado | [x] Completado |

---

## FASE-D: Validacion E2E amaziliahotel.com

**Dependencias:** FASE-A + FASE-B + FASE-C completadas  
**Archivos:** Ninguno (solo validacion)

| # | Tarea | Estado |
|---|-------|--------|
| T1 | v4complete ejecuta sin crashes | [x] Completado |
| T2 | Fix WhatsApp verificado | [x] Completado - Fix funcional. Sitio NO tiene WhatsApp (brecha correcta). phone_web=null es hallazgo nuevo. |
| T3 | Fix Citability verificado (narrativa correcta segun blocks_analyzed) | [x] Completado - blocks=0 genera "No Discoverable" (no "poco estructurado") |
| T4 | Fix Regional verificado | [~] Parcial - yRevisan corregido. Region sigue "nacional" (fallback). |
| T5 | Coherence >= 0.80 | [x] Completado - 0.84 |
| T6 | Evidence capturada en evidence/fase-d/ | [x] Completado |
| T7 | log_phase_completion.py ejecutado | [x] Completado |

**Hallazgos E2E:**
- phone_web=null cuando tel: link existe en HTML (nuevo issue, no bloqueante)
- Region detectada como "nacional" (FASE-C fix parcial)
- 9/11 assets WARNING por confidence insuficiente

---

## Resumen Global

| Fase | Estado | Tests | Coherence |
|------|--------|-------|-----------|
| FASE-A | Completado | 25/25 passed | N/A |
|| FASE-B | Completado | 218 passed (+3 nuevos) | N/A |
|| FASE-C | Completado | 218 passed | N/A |
|| FASE-D | Parcial | - | 0.84 |
