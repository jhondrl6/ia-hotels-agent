# Dependencias entre Fases — PROPUESTA-COMERCIAL

```
┌─────────────────────────────────────────────────────────────┐
│                  PROPUESTA-COMERCIAL                         │
│                  Dependency Diagram                          │
└─────────────────────────────────────────────────────────────┘

FASE-A (Unificación financiera)
  │  CODE-1/3/4: recovered_6m, net_benefit_6m → effective_monthly_gain
  │  CODE-2: Sincronizar gate CG-ROI-NEGATIVE
  │  Sin dependencias — fase inicial
  │
  ▼
FASE-B (Puente dual)
  │  CROSS-1: Dual bridge fuga bruta/recuperación en diagnóstico + propuesta
  │  Depende de: FASE-A (usa effective_monthly_gain unificado)
  │  ⚠️ FASE-B puede ejecutarse en paralelo con FASE-A si es urgente
  │     (trabajan en archivos distintos: templates vs .py)
  │
  ▼
FASE-C (Mapping + WhatsApp)
  │  CROSS-2: Brecha→servicio mapping en tabla de propuesta
  │  CROSS-4: WhatsApp conflict reflejado en propuesta
  │  Depende de: FASE-B (usa la estructura de puente dual en template)
  │
  ▼
FASE-D (Credibilidad)
  │  V-2: Unificar labels "⚠️ En preparación"
  │  V-3: Expandir CG-TECH-JARGON + mover tabla IAO
  │  A-1: Eliminar fallback string has_onboarding
  │  CROSS-5: Vincular confidence score a servicios
  │  Depende de: FASE-C (trabaja sobre la tabla de servicios ya mapeada)
  │
  ▼
FASE-E (Paquete + Pulido + Gate)
  │  A-2: Unificar umbral AEO (20→30)
  │  V-4/5/6: Cupo, garantía, prueba social
  │  A-3: Typo PASSO→PASO
  │  CROSS-6: Gates NOT_READY bloquean generación
  │  Depende de: FASE-D (limpia el pipeline para que CROSS-6 sea efectivo)
  │
  ▼
FASE-F (v4complete + Análisis)
  │  v4complete Hotel Castilla Real
  │  Análisis post-implementación por niveles
  │  Depende de: TODAS las fases anteriores (FASE-A a FASE-E)
  │
  ▼
FASE-RELEASE
     log_phase, sync_versions, CHANGELOG, GUIA_TECNICA
     Depende de: FASE-F (resultados de v4complete incluidos en docs)
```

---

## Tabla de Conflictos

| Par de Fases | ¿Conflicto? | Razón |
|-------------|-------------|-------|
| A ↔ B | ⚠️ Bajo | Archivos distintos (`.py` vs `.md`) pero B usa variables de A |
| A ↔ C | ✅ Ninguno | Archivos y módulos distintos |
| B ↔ C | ❌ Secuencial | C modifica el mismo template que B ya extendió |
| C ↔ D | ❌ Secuencial | D agrega columnas a la tabla de servicios que C creó |
| D ↔ E | ⚠️ Bajo | Distintas secciones del código/template |
| E ↔ F | ❌ Secuencial | F requiere todos los fixes aplicados |

---

## Orden de Ejecución Recomendado

```
Sesión 1 → FASE-A (Código — unificación financiera)
Sesión 2 → FASE-B (Templates — puente dual)
Sesión 3 → FASE-C (Templates — mapping + WhatsApp)
Sesión 4 → FASE-D (Código+Templates — credibilidad)
Sesión 5 → FASE-E (Código+Templates — paquete + pulido)
Sesión 6 → FASE-F (Ejecución — v4complete + análisis)
Sesión 7 → FASE-RELEASE (Documentación)
```

---

## Estado de Fases

| Fase | Estado | Fecha | Evidencia |
|------|--------|-------|-----------|
| FASE-A | ✅ COMPLETADA | 2026-05-26 | `v4_proposal_generator.py` L796, L797 + CODE-2 gate sync |
| FASE-B | ✅ COMPLETADA | 2026-05-26 | `v4_diagnostic_generator.py` L1080-1126 + `v4_proposal_generator.py` L894-900 + templates |
| FASE-C | ✅ COMPLETADA | 2026-05-26 | `v4_proposal_generator.py` L986-1110: BREACH_BY_ASSET dict + columna "Problema que resuelve" + CROSS-4 whatsapp_conflict → "⚠️ Requiere corrección" |
| FASE-D | ⏳ PENDIENTE | — | — |
| FASE-E | ⏳ PENDIENTE | — | — |
| FASE-F | ⏳ PENDIENTE | — | — |
| FASE-RELEASE | ⏳ PENDIENTE | — | — |
