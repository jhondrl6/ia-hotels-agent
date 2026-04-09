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
| T1 | Conectar scraper `_detectar_whatsapp()` al pipeline de validacion | [ ] Pendiente |
| T2 | Agregar `whatsapp_html_detected` a `ValidationSummary` en data_structures.py | [ ] Pendiente |
| T3 | Actualizar condicion brecha WhatsApp en v4_diagnostic_generator.py:1788 | [ ] Pendiente |
| T4 | Actualizar quick wins (linea 1005-1009) | [ ] Pendiente |
| T5 | Actualizar tabla brechas (linea 941-944) | [ ] Pendiente |
| T6 | Tests de regresion pasan | [ ] Pendiente |
| T7 | log_phase_completion.py ejecutado | [ ] Pendiente |

---

## FASE-B: Citability Narrative Fix

**Dependencias:** Ninguna (independiente de FASE-A)  
**Archivos:** v4_diagnostic_generator.py

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Diferenciar `blocks_analyzed=0` vs score real bajo en `_detect_brechas` (lineas 1850-1860) | [ ] Pendiente |
| T2 | Actualizar narrativa IA readiness para citability (~1044-1061) | [ ] Pendiente |
| T3 | Verificar pain_solution_mapper alignment | [ ] Pendiente |
| T4 | Tests de regresion pasan | [ ] Pendiente |
| T5 | log_phase_completion.py ejecutado | [ ] Pendiente |

---

## FASE-C: Regional Template Fixes

**Dependencias:** Ninguna (independiente de FASE-A/B)  
**Archivos:** diagnostico_v6_template.md, v4_diagnostic_generator.py

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Corregir typo `yRevisan` en template linea 27 | [ ] Pendiente |
| T2 | Agregar "Eje Cafetero" al mapping `region_contexts` (lineas 1613-1620) | [ ] Pendiente |
| T3 | Corregir fallback regional generico (linea 1627) | [ ] Pendiente |
| T4 | Verificar hotel_region fallback (linea 413) | [ ] Pendiente |
| T5 | Tests de regresion pasan | [ ] Pendiente |
| T6 | log_phase_completion.py ejecutado | [ ] Pendiente |

---

## FASE-D: Validacion E2E amaziliahotel.com

**Dependencias:** FASE-A + FASE-B + FASE-C completadas  
**Archivos:** Ninguno (solo validacion)

| # | Tarea | Estado |
|---|-------|--------|
| T1 | v4complete ejecuta sin crashes | [ ] Pendiente |
| T2 | Fix WhatsApp verificado (no aparece "Sin WhatsApp") | [ ] Pendiente |
| T3 | Fix Citability verificado (narrativa correcta segun blocks_analyzed) | [ ] Pendiente |
| T4 | Fix Regional verificado (no "yRevisan", no "Nacional") | [ ] Pendiente |
| T5 | Coherence >= 0.80 | [ ] Pendiente |
| T6 | Evidence capturada en evidence/fase-d/ | [ ] Pendiente |
| T7 | log_phase_completion.py ejecutado | [ ] Pendiente |

---

## Resumen Global

| Fase | Estado | Tests | Coherence |
|------|--------|-------|-----------|
| FASE-A | Pendiente | - | - |
| FASE-B | Pendiente | - | - |
| FASE-C | Pendiente | - | - |
| FASE-D | Pendiente | - | - |
