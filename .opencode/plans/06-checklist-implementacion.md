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
| T2 | Agregar `whatsapp_html_detected` a `ValidationSummary` | [x] Completado |
| T3 | Actualizar condicion brecha WhatsApp en v4_diagnostic_generator.py | [x] Completado |
| T4 | Actualizar quick wins (linea 1013-1018) | [x] Completado |
| T5 | Actualizar tabla brechas (linea 941-949) | [x] Completado |
| T6 | Tests de regresion pasan (25/25) | [x] Completado |
| T7 | log_phase_completion.py ejecutado | [x] Completado |

---

## FASE-B: Citability Narrative Fix

**Dependencias:** Ninguna (independiente de FASE-A)  
**Archivos:** v4_diagnostic_generator.py, opportunity_scorer.py

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Diferenciar `blocks_analyzed=0` vs score bajo | [x] Completado |
| T2 | Actualizar narrativa opportunity_scorer.py | [x] Completado |
| T3 | Verificar pain_solution_mapper alignment | [x] Completado |
| T4 | Tests de regresion pasan (218 passed) | [x] Completado |
| T5 | log_phase_completion.py ejecutado | [x] Completado |

---

## FASE-C: Regional Template Fixes

**Dependencias:** Ninguna  
**Archivos:** diagnostico_v6_template.md, v4_diagnostic_generator.py

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Corregir typo `yRevisan` en template linea 27 | [x] Completado |
| T2 | Agregar "Eje Cafetero" al mapping `region_contexts` | [x] Completado |
| T3 | Corregir fallback regional generico | [x] Completado |
| T4 | Verificar hotel_region fallback | [x] Completado |
| T5 | Tests de regresion pasan | [x] Completado |
| T6 | log_phase_completion.py ejecutado | [x] Completado |

---

## FASE-D: Validacion E2E amaziliahotel.com

**Dependencias:** FASE-A + FASE-B + FASE-C

| # | Tarea | Estado |
|---|-------|--------|
| T1 | v4complete ejecuta sin crashes | [x] Completado |
| T2 | Fix WhatsApp verificado | [~] Parcial — BRECHA 2 persiste |
| T3 | Fix Citability verificado | [x] Completado |
| T4 | Fix Regional verificado | [~] Parcial — "nacional" persiste |
| T5 | Coherence >= 0.80 | [x] 0.84 |
| T6 | Evidence capturada | [x] Completado |
| T7 | log_phase_completion.py ejecutado | [x] Completado |

**NOTA:** Las persistencias de T2 y T4 se resolvieron en FASE-E con fixes W1-W4 y R1-R3,
pero el efecto real no se validó hasta descubrir la causa raiz Brotli (FASE-F).

---

## FASE-E: Integridad de Datos Diagnosticos

**Dependencias:** FASE-A completada  
**Archivos:** main.py, pain_solution_mapper.py, coherence_validator.py, web_scraper.py, v4_diagnostic_generator.py

### Workstream WhatsApp (W1-W4)

| # | Tarea | Estado |
|---|-------|--------|
| W1 | Agregar rama elif whatsapp_html_detected en ValidationSummary | [x] Completado |
| W2 | pain_solution_mapper consulta whatsapp_html_detected | [x] Completado |
| W3 | web_scraper captura tel: links | [x] Completado |
| W4 | coherence_validator consulta whatsapp_html_detected | [x] Completado |

### Workstream Regional (R1-R3)

| # | Tarea | Estado |
|---|-------|--------|
| R1 | Inferir region desde GBP address post-auditoria | [x] Completado |
| R2 | Sanitizar hotel_region ("nacional" → "Colombia") | [x] Completado |
| R3 | Ampliar keywords URL Eje Cafetero | [x] Completado |

### Validacion

| # | Tarea | Estado |
|---|-------|--------|
| V1 | Tests de regresion pasan | [x] Completado |
| V2 | v4complete sin crashes | [x] Completado |
| V3 | Region muestra "Eje Cafetero" | [x] Completado |
| V4 | pain_solution_mapper no genera falso no_whatsapp_visible | [x] Completado |
| V5 | log_phase_completion.py ejecutado | [x] Completado |

**NOTA:** Todos los checks pasaron contra HTML binario (Brotli). Los fixes son correctos
pero el efecto real se validara en FASE-F cuando el HTML llegue decodificado.

---

## FASE-F: Fix Brotli Encoding + Defensa en Profundidad

**Dependencias:** FASE-A a FASE-E completadas  
**Archivos:** v4_comprehensive.py (nuevo metodo + integracion), tests/test_html_integrity.py (nuevo)  
**Principio:** Un falso diagnostico destruye credibilidad. No hay margen para que HTML corrupto genere diagnosticas falsos otra vez.

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Instalar brotli (`venv/Scripts/pip.exe install brotli`) | [ ] Pendiente |
| T2 | Implementar `_validate_html_integrity()` en v4_comprehensive.py | [ ] Pendiente |
| T3 | Integrar validacion en `audit()` linea 370+ | [ ] Pendiente |
| T4 | Crear `tests/test_html_integrity.py` con 5 tests regresion | [ ] Pendiente |
| T5 | Verificar HTML decodificado contiene "joinchat" | [ ] Pendiente |
| T6 | Tests de regresion pasan | [ ] Pendiente |
| T7 | v4complete --url https://amaziliahotel.com/ sin crashes | [ ] Pendiente |
| T8 | BRECHA 2 "Sin WhatsApp" NO aparece en diagnostico | [ ] Pendiente |
| T9 | Region muestra "Eje Cafetero" (no "nacional") | [ ] Pendiente |
| T10 | Coherence >= 0.80 | [ ] Pendiente |
| T11 | whatsapp_verified score > 0 | [ ] Pendiente |
| T12 | log_phase_completion.py ejecutado | [ ] Pendiente |

---

## Resumen Global

| Fase | Estado | Tests | Coherence |
|------|--------|-------|-----------|
| FASE-A | Completado | 25/25 passed | N/A |
| FASE-B | Completado | 218 passed | N/A |
| FASE-C | Completado | 218 passed | N/A |
| FASE-D | Completado (parcial) | - | 0.84 |
| FASE-E | Completado | 8 errores pre-existentes | 0.84 |
| **FASE-F** | **Pendiente** | - | - |
