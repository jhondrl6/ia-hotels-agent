# Plan: Correccion Falsos Positivos y Errores de Contexto

> **Proyecto:** iah-cli v4.25.x  
> **Fecha creacion:** 2026-04-09  
> **Contexto fuente:** `.opencode/plans/context/whatsapp_false_positive.md`  
> **Hotel de validacion:** amaziliahotel.com

---

## Resumen

El documento de contexto documenta problemas confirmados (auditados contra codigo actual):

### Ronda 1 (FASE-A a FASE-D): COMPLETADA

1. **Falso Positivo WhatsApp** — Boton existe visualmente pero el sistema reporta "Sin WhatsApp"
2. **Narrativa Imprecisa Citabilidad** — Dice "contenido poco estructurado" cuando el score es 0 por ausencia de datos
3. **Errores Regionales Template** — "nacional" en lugar de region real + typo "yRevisan"

### Ronda 2 (FASE-E): Integridad de Datos Diagnosticos

4. **WhatsApp: propagacion incompleta** — `whatsapp_html_detected` no llega a `pain_solution_mapper`, `ValidationSummary`, `coherence_validator`
5. **Regional: deteccion solo por URL** — `_detect_region_from_url()` ignora GBP address, "nacional" persiste en template

---

## Estructura de Fases

| Fase | Nombre | Tipo | Archivos principales |
|------|--------|------|---------------------|
| FASE-A | WhatsApp Detection Fix | Codigo | v4_comprehensive.py, v4_diagnostic_generator.py, data_structures.py |
| FASE-B | Citability Narrative Fix | Codigo | v4_diagnostic_generator.py |
| FASE-C | Regional Template Fixes | Codigo + Template | diagnostico_v6_template.md, v4_diagnostic_generator.py |
| FASE-D | Validacion E2E | Validacion | Ninguno (prueba v4complete amaziliahotel.com) |
| FASE-E | Integridad de Datos Diagnosticos | Codigo | main.py, pain_solution_mapper.py, coherence_validator.py, web_scraper.py, v4_diagnostic_generator.py |

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
| FASE-E | Pendiente | - |
