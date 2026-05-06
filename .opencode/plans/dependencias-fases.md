# Dependencias de Fases — REFACTOR-ONBOARDING-CTA

## Diagrama ASCII

```
┌────────────────────────────────────────────────────┐
│  FASE-REFACTOR-CTA-A                        │
│  (fix generator + tests)                    │
└────────────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────┐
│  FASE-REFACTOR-CTA-B                        │
│  (v4complete Hotel Castilla Real + verificar)│
└────────────────────────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────┐
│  FASE-REFACTOR-CTA-C                        │
│  (docs cascade: REGISTRY, CHANGELOG, GUIA)   │
└────────────────────────────────────────────────────┘
```

## Tabla de Conflictos Potenciales

| Fase | Archivos Modificados | Conflictos |
|------|---------------------|------------|
| FASE-A | `modules/commercial_documents/v4_diagnostic_generator.py` | Ninguno — solo cambio de string |
| FASE-A | `tests/commercial_documents/test_precision_rendering.py` | Ninguno — solo actualizacion de assertions |
| FASE-B | Output en `output/v4_complete/` + `evidence/FASE-REFACTOR-CTA-B/` | Ninguno — solo lectura/escritura de evidencia |
| FASE-C | Documentacion (`CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md`) | Ninguno — solo escritura de docs |

## Evaluacion R3 por Fase

| Fase | Tareas | Comandos Largos | Dentro de R3? |
|------|--------|-----------------|---------------|
| FASE-A | 4 | 0 | ✅ Si (4 tareas + 0 comandos) |
| FASE-B | 3 | 1 (v4complete) | ✅ Si (3 tareas + 1 comando largo) |
| FASE-C | 4 | 0 | ✅ Si (4 tareas + 0 comandos) |

## Presupuesto de Iteraciones

| Fase | Fijas | Especificas | Total Est. |
|------|-------|-------------|------------|
| FASE-A | ~26 | ~10 | ~36 |
| FASE-B | ~26 | ~8 | ~34 |
| FASE-C | ~26 | ~10 | ~36 |

## Orden de Ejecucion Recomendado

1. FASE-REFACTOR-CTA-A → fix codigo + tests
2. FASE-REFACTOR-CTA-B → v4complete Hotel Castilla Real + verificacion
3. FASE-REFACTOR-CTA-C → docs cascade

No requiere FASE-RELEASE separada: cambio PATCH-level (bugfix de texto, sin cambios arquitectonicos).
