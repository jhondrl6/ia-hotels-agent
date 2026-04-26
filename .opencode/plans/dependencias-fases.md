# Dependencias entre Fases - PATCH Forense AmaziliaHotel

## Diagrama de Dependencias

```
FASE-A (hotel_schema dual)  ──┐
FASE-B (Comision OTA label)  ─┤
FASE-C (open_graph asset)    ──┼──→ FASE-RELEASE-4.36.0 (cierre + docs)
FASE-D (gate_report presence) ─┘
```

## Tabla de Conflictos Potenciales

| Archivo | FASE-A | FASE-B | FASE-C | FASE-D | Conflicto? |
|---------|--------|--------|--------|--------|------------|
| `conditional_generator.py` | SI (schema) | NO | SI (open_graph) | NO | A vs C |
| `v4_asset_orchestrator.py` | SI (bridge) | NO | NO | NO | No |
| `v4_diagnostic_generator.py` | NO | SI (labels) | NO | NO | No |
| `diagnostico_v6_template.md` | NO | SI (vars) | NO | NO | No |
| `asset_catalog.py` | SI (conf) | NO | SI (OG entry) | NO | A vs C |
| `pain_solution_mapper.py` | NO | NO | SI (no_og_tags) | NO | No |
| `open_graph_template.html` | NO | NO | SI (NUEVO) | NO | No |
| `gate_report generator` | NO | NO | NO | SI | No |
| `scenario_calculator.py` | NO | SI (lectura) | NO | NO | No |

**Conflictos identificados**:
- **FASE-A vs FASE-C** en `conditional_generator.py` y `asset_catalog.py`:
  - FASE-A modifica rama hotel_schema
  - FASE-C agrega/modifica rama open_graph
  - Son ramas DISTINTAS del mismo archivo → conflicto BAJO si se ejecutan en paralelo
  - **Mitigacion**: Ejecutar secuencialmente (A antes que C, o viceversa)

**Recomendacion de orden**: A → B → C → D → RELEASE (secuencial por seguridad)

## Orden de Ejecucion

Las 4 fases de implementacion son funcionalmente independientes pero comparten algunos archivos (conflicto bajo):
- Sesion 1: FASE-A (hotel_schema)
- Sesion 2: FASE-B (Comision OTA)
- Sesion 3: FASE-C (open_graph)
- Sesion 4: FASE-D (gate_report)
- Sesion 5: FASE-RELEASE-4.36.0 (cierre)

## Estado de Fases

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | Completada | 2026-04-26 | hotel_schema dual (schema rico como default) |
|| FASE-B | Completada | 2026-04-26 | Comision OTA label → Perdida Mensual Estimada + ota_commission_real_formatted |
|| FASE-C | Completada | 2026-04-26 | open_graph template + pain_id no_og_tags |
|| FASE-D | Completada | 2026-04-26 | gate_report presence check con SitePresenceChecker |
| FASE-RELEASE-4.36.0 | Completada | 2026-04-26 | Cierre + documentacion - version bump 4.36.0 |
