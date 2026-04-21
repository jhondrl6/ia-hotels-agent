# Dependencias entre Fases — AMH_REFACTOR_V3_ALT

```
FASE-1: DATASOURCE-GAP ————————————————————————┐
  Diagnosticar por que datos GBP no llegan       |
  a validated_data["hotel_data"]                 |
  (sin costo API, solo codigo y tests)           |
                                                 ↓
FASE-2: BRIDGE-QUALITY-GUARD ———————————————————┐
  GEO-BRIDGE solo reemplaza si el reemplazo      |
  es objetivamente mejor (verifica campos)       |
                                                 ↓
FASE-3: MINIMUM-DATA-GUARANTEE ————————————————┐
  Garantizar datos minimos en                    |
  conditional_generator sin importar fuentes     |
                                                 ↓
FASE-RELEASE: E2E + Release 4.33.0 —————————————┘
  Ejecucion E2E unica, validacion de gates, release
```

## Tabla de Fases

| # | ID | Estado | Fecha | Archivos | Tests nuevos |
|---|----|--------|-------|----------|-------------|
| 1 | FASE-1 DATASOURCE-GAP | Completada | 2026-04-21 | v4_asset_orchestrator.py | 13 |
| 2 | FASE-2 BRIDGE-QUALITY-GUARD | Completada | 2026-04-21 | geo_enriched_bridge.py | 5 |
| 3 | FASE-3 MINIMUM-DATA-GUARANTEE | Completada | 2026-04-21 | conditional_generator.py, v4_asset_orchestrator.py | 5 |
| R | FASE-RELEASE 4.33.0 | Pendiente | — | Todos (version bump) | 0 (E2E) |
| C | FASE-4 INYECCION-MANUAL (contingencia) | Pendiente | — | v4_asset_orchestrator.py | 0 |

## Dependencias Detalladas

### FASE-1 → FASE-2
- FASE-2 necesita saber exactamente QUE datos faltan (FASE-1 lo diagnostica)
- FASE-2 define "que es mejor" basado en el diagnostico de FASE-1

### FASE-2 → FASE-3
- FASE-3 garantiza datos minimos, pero necesita saber que campos son criticos
- La lista de campos criticos viene del diagnostico de FASE-1 + la definicion de calidad de FASE-2

### FASE-3 → FASE-RELEASE
- FASE-3 es el ultimo fix antes del release
- FASE-RELEASE valida todo con v4complete E2E

### FASE-RELEASE → FASE-4 (contingencia)
- FASE-4 solo se ejecuta si FASE-RELEASE T3 detecta schema vacio o confidence 0.3
- FASE-4 inyecta datos conocidos del schema 15-abr y re-ejecuta v4complete
- NO hay release hasta que FASE-4 valide exito

## Regla de Ejecucion

- **1 fase por sesion** — nunca ejecutar 2 fases en la misma sesion
- **v4complete SOLO en FASE-RELEASE** — verificar con tests unitarios en fases intermedias
