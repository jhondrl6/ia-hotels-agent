# Plan: Correccion Falsos Positivos y Errores de Contexto

> **Proyecto:** iah-cli v4.25.x  
> **Fecha creacion:** 2026-04-09  
> **Contexto fuente:** `.opencode/plans/context/whatsapp_false_positive.md`  
> **Hotel de validacion:** amaziliahotel.com

---

## Resumen

### Ronda 1 (FASE-A a FASE-D): COMPLETADA

1. **Falso Positivo WhatsApp** — Patrones ampliados, propagacion conectada
2. **Narrativa Imprecisa Citabilidad** — blocks=0 vs score bajo diferenciados
3. **Errores Regionales Template** — typo corregido, sanitizacion "nacional"

### Ronda 2 (FASE-E): COMPLETADA

4. **WhatsApp: propagacion completa** — whatsapp_html_detected llega a todos los consumers
5. **Regional: deteccion desde GBP** — _infer_region_from_address + sanitizacion

### Ronda 3 (FASE-F): PENDIENTE

6. **Causa raiz real: Brotli encoding** — HttpClient entrega HTML binario porque pide br sin tener la libreria. TODOS los fixes previos son correctos pero no tenian efecto.

---

## Estructura de Fases

| Fase | Nombre | Tipo | Archivos principales |
|------|--------|------|---------------------|
| FASE-A | WhatsApp Detection Fix | Codigo | v4_comprehensive.py, v4_diagnostic_generator.py, data_structures.py |
| FASE-B | Citability Narrative Fix | Codigo | v4_diagnostic_generator.py |
| FASE-C | Regional Template Fixes | Codigo + Template | diagnostico_v6_template.md, v4_diagnostic_generator.py |
| FASE-D | Validacion E2E | Validacion | Ninguno (prueba v4complete) |
| FASE-E | Integridad de Datos Diagnosticos | Codigo | main.py, pain_solution_mapper.py, coherence_validator.py, web_scraper.py |
| **FASE-F** | **Fix Brotli Encoding** | **1 linea + validacion** | **http_client.py** |

---

## Ejecucion

- **1 fase por sesion** (regla mandatoria del workflow)
- Cada fase tiene su prompt en `05-prompt-inicio-sesion-fase-{LETRA}.md`
- Al completar: ejecutar `log_phase_completion.py`
- Al final: prueba E2E con `v4complete --url https://amaziliahotel.com/`

---

## Estado

| Fase | Estado | Sesion |
|------|--------|--------|
| FASE-A | Completado | 2026-04-09 |
| FASE-B | Completado | 2026-04-09 |
| FASE-C | Completado | 2026-04-09 |
| FASE-D | Completado (parcial) | 2026-04-09 |
| FASE-E | Completado | 2026-04-09 |
| **FASE-F** | **Pendiente** | - |
