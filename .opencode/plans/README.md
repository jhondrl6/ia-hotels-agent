# Plan: Corrección Falsos Positivos y Errores de Contexto

> **Proyecto:** iah-cli v4.25.x  
> **Fecha creación:** 2026-04-09  
> **Contexto fuente:** `.opencode/plans/context/whatsapp_false_positive.md`  
> **Hotel de validación:** amaziliahotel.com

---

## Resumen

El documento de contexto documenta 3 problemas confirmados (auditados 2026-04-09, 10/10 afirmaciones CONFIRMADAS contra el codigo actual):

1. **Falso Positivo WhatsApp** — Boton existe visualmente pero el sistema reporta "Sin WhatsApp"
2. **Narrativa Imprecisa Citabilidad** — Dice "contenido poco estructurado" cuando el score es 0 por ausencia de datos (no por mala calidad)
3. **Errores Regionales Template** — "nacional" en lugar de region real + typo "yRevisan"

---

## Estructura de Fases

| Fase | Nombre | Tipo | Archivos principales |
|------|--------|------|---------------------|
| FASE-A | WhatsApp Detection Fix | Codigo | v4_comprehensive.py, v4_diagnostic_generator.py, data_structures.py |
| FASE-B | Citability Narrative Fix | Codigo | v4_diagnostic_generator.py |
| FASE-C | Regional Template Fixes | Codigo + Template | diagnostico_v6_template.md, v4_diagnostic_generator.py |
| FASE-D | Validacion E2E | Validacion | Ninguno (prueba v4complete amaziliahotel.com) |

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
| FASE-B | Pendiente | - |
| FASE-C | Pendiente | - |
| FASE-D | Pendiente | - |
