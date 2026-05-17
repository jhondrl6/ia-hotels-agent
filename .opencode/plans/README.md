# Plan: IA-Readiness Advisory Warnings

**Creado:** 2026-05-16
**Contexto:** `.opencode/context/ia-readiness-advisory-vs-blocking.md`
**Dictamen:** IA-Readiness Critical debe ser advisory no bloqueante, pero visible y persistente
**Versión objetivo:** 4.47.0
**Código:** `ADVISORY-WARNINGS`

---

## Arquitectura del Plan

```
FASE-A ──→ FASE-B ──→ FASE-RELEASE-4.47.0
 (impl)     (v4c+verify)   (docs)
```

| Fase | Propósito | Sesiones | Comando largo |
|------|-----------|----------|---------------|
| FASE-A | Implementar advisory warnings + tests | 1 | No |
| FASE-B | v4complete Hotel Castilla Real + verificación | 1 | Sí (v4complete) |
| FASE-RELEASE-4.47.0 | Documentación oficial + validaciones | 1 | No |

---

## Resumen de Cambios

1. **Cambio 1** — Alerta en DIAGNOSTICO.md cuando IA-Readiness < 50
   - Archivo: `modules/commercial_documents/v4_diagnostic_generator.py`
   - Template: `modules/commercial_documents/templates/diagnostico_v6_template.md`

2. **Cambio 2** — Advisory warning en `delivery_quality_report.json`
   - Archivo: `modules/quality_gates/delivery_quality_report.py`
   - Nuevo campo: `advisory_warnings: List[dict]`
   - Regla: `IA_READINESS_CRITICAL` cuando `status == "Critical"` o `overall_score < 50`

3. **Cambio 3 (opcional)** — Human checklist item (solo si cabe en ≤10 items)

---

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `dependencias-fases.md` | Dependencias y conflictos |
| `05-prompt-inicio-sesion-fase-A.md` | Prompt para FASE-A |
| `05-prompt-inicio-sesion-fase-B.md` | Prompt para FASE-B |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Prompt para FASE-RELEASE |
| `06-checklist-implementacion.md` | Checklist maestro |
| `09-documentacion-post-proyecto.md` | Acumulador de docs |
