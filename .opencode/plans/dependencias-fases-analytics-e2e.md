# Dependencias de Fases — ANALYTICS-E2E-BRIDGE

## Diagrama de dependencias

```
FASE-ANALYTICS-01 (persistir JSON)  ←── INDEPENDIENTE
FASE-ANALYTICS-03 (doc stubs)       ←── INDEPENDIENTE
        │                                    │
        └──────────┬─────────────────────────┘
                   ▼
        FASE-ANALYTICS-02 (proposal recibe analytics)
                   │
                   ▼
        FASE-ANALYTICS-04 (analytics → asset bridge)
```

## Conflictos de archivos

| Fase | Archivos que modifica | Riesgo de conflicto |
|------|----------------------|-------------------|
| ANALYTICS-01 | `main.py` (L2378, insercion en dict report) | BAJO — zona distinta |
| ANALYTICS-03 | `profound_client.py`, `semrush_client.py`, `README.md` | BAJO — archivos separados |
| ANALYTICS-02 | `main.py` (L2030-2039), `v4_proposal_generator.py` (L140-152) | MEDIO — toca firma generate() |
| ANALYTICS-04 | `pain_solution_mapper.py`, `asset_catalog.py`, templates nuevos | MEDIO — agrega pain types |

## Reglas de modificacion

| Archivo | Regla | Razon |
|---------|-------|-------|
| `main.py` | Solo agregar parametros, no cambiar orden existente | 2612 lineas, muchas dependencias |
| `v4_proposal_generator.py` | `analytics_data` es Optional[Dict] = None | Backwards compatible |
| `pain_solution_mapper.py` | Agregar pain types nuevos (no modificar existentes) | Preservar flujo actual |
| `asset_catalog.py` | Agregar assets con status IMPLEMENTED | Templates deben existir |
| `data_models/analytics_status.py` | NO MODIFICAR — ya esta completo desde v4.13.0 | Funciona correctamente |
