# Dependencias y Conflictos — ADVISORY-WARNINGS

**Plan:** IA-Readiness Advisory Warnings
**Fecha:** 2026-05-16
**Versión objetivo:** 4.47.0

---

## Diagrama de Dependencias

```
┌─────────────────────────────────────────────────────────────┐
│                      FASE-A                                 │
│  Investigar + Implementar advisory warnings + Tests         │
│  Archivos:                                                  │
│    - v4_diagnostic_generator.py                             │
│    - delivery_quality_report.py                             │
│    - tests nuevos                                            │
│  Depende de: NADA (primera fase)                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      FASE-B                                 │
│  v4complete Hotel Castilla Real + Verificación              │
│  Archivos:                                                  │
│    - Ejecuta v4complete (comando largo)                     │
│    - Verifica output contiene advisory warnings             │
│  Depende de: FASE-A (código debe estar implementado)        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                FASE-RELEASE-4.47.0                          │
│  Documentación oficial + Version bump + Validaciones        │
│  Depende de: FASE-A ✅, FASE-B ✅                           │
│  NO modifica código fuente                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Tabla de Conflictos Potenciales

| Archivo | FASE-A | FASE-B | RELEASE | Riesgo |
|---------|--------|--------|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICA | LEE | — | Ninguno (secuencial) |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | MODIFICA | LEE | — | Ninguno (secuencial) |
| `modules/quality_gates/delivery_quality_report.py` | MODIFICA | LEE | — | Ninguno (secuencial) |
| `main.py` | POSIBLE MOD | LEE | — | Bajo (coordinado) |
| `tests/quality_gates/test_delivery_quality_report.py` | MODIFICA | — | — | Ninguno |
| `tests/commercial_documents/test_v4_diagnostic_generator.py` | CREA/MOD | — | — | Ninguno |
| `CHANGELOG.md` | — | — | MODIFICA | Ninguno |
| `GUIA_TECNICA.md` | — | — | MODIFICA | Ninguno |
| `VERSION.yaml` | — | — | MODIFICA | Ninguno |

---

## Regla de Dependencia

> FASE-RELEASE-4.47.0 solo se ejecuta cuando FASE-A y FASE-B están ✅ completadas.

---

## Estados de Fase

| Fase | Estado | Fecha inicio | Fecha fin | Iteraciones |
|------|--------|-------------|-----------|-------------|
| FASE-A | ✅ Completada | 2026-05-16 | 2026-05-16 | — |
| FASE-B | ✅ Completada | 2026-05-16 | 2026-05-16 | — |
| FASE-RELEASE-4.47.0 | ⬜ Pendiente | — | — | — |
