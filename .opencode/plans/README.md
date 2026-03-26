# Planes - GAPS V4COMPLETE Hotel Vísperas

## Índice

| Archivo | Descripción |
|---------|-------------|
| `README.md` | Este archivo |
| `dependencias-fases-GAPS-V4COMPLETE.md` | Diagrama de dependencias y análisis causa raíz |
| `06-checklist-GAPS-V4COMPLETE.md` | Checklist de implementación con estados |
| `05-prompt-inicio-sesion-FASE-H-01.md` | Prompt para FASE-H-01 (Diagnóstico WhatsApp) |
| `05-prompt-inicio-sesion-FASE-H-02.md` | Prompt para FASE-H-02 (Fix WhatsApp) |
| `05-prompt-inicio-sesion-FASE-H-03.md` | Prompt para FASE-H-03 (Verificación Optimization Guide) |
| `05-prompt-inicio-sesion-FASE-H-04.md` | Prompt para FASE-H-04 (Fix Optimization Guide + ROI) |
| `05-prompt-inicio-sesion-FASE-H-05.md` | Prompt para FASE-H-05 (E2E Certification) |
| `09-documentacion-post-proyecto-GAPS-V4COMPLETE.md` | Documentación incremental del proyecto |

---

## Resumen de Fases

```
FASE-H-01: Diagnóstico Causa Raíz WhatsApp
    ↓
FASE-H-02: Fix Causa Raíz WhatsApp
    │
FASE-H-03: Verificación Optimization Guide ← (paralelo con H-01)
    ↓
FASE-H-04: Fix Optimization Guide + ROI
    │
    └──────────────┐
                   ▼
             FASE-H-05: E2E Certification
```

---

## Ejecución Sugerida

1. **Sesión 1**: FASE-H-01 + FASE-H-03 (pueden ejecutarse en paralelo)
2. **Sesión 2**: FASE-H-02 (depende de H-01)
3. **Sesión 3**: FASE-H-04 (depende de H-03)
4. **Sesión 4**: FASE-H-05 (E2E Certification)

---

## Verificación de Numeración

```bash
grep -n "FASE-H-" .opencode/plans/05-prompt-inicio-sesion-FASE-H-*.md
```

---

*Creado: 2026-03-26*
