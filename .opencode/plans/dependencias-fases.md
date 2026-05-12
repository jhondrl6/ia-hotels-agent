# Dependencias de Fases — REFACTOR-COHERENCIA-CASTILLAREAL

## Diagrama de Dependencias

```
FASE-1-COH ──> FASE-2-DEFAULT ──> FASE-3-CONTENT ──> FASE-4-GATE ──> FASE-5-VERIFY
     │                                                                     │
     │                                                                     ▼
     │                                                            FASE-RELEASE-4.45.0
     │                                                                     ▲
     └─────────────────────────────────────────────────────────────────────┘
                    (RELEASE requiere TODAS las fases ✅)
```

## Tabla de Conflictos Potenciales

| Fase | Archivos modificados | Conflicto con |
|------|---------------------|---------------|
| FASE-1-COH | `modules/quality_gates/coherence_gate.py`, `main.py` | FASE-2-DEFAULT (main.py potencial) |
| FASE-2-DEFAULT | `modules/asset_generation/open_graph_generator.py`, `modules/asset_generation/conditional_generator.py` | Ninguno (generadores distintos) |
| FASE-3-CONTENT | `modules/asset_generation/local_content_generator.py`, `modules/financial_engine/*.py`, `modules/quality_gates/proposal_asset_alignment.py` | Ninguno (módulos independientes) |
| FASE-4-GATE | `modules/quality_gates/publication_gates.py` (o equivalente) | FASE-1-COH (ambos quality_gates/) |
| FASE-5-VERIFY | Solo lectura de `output/v4_complete/` | Ninguno |
| FASE-RELEASE | `docs/CHANGELOG.md`, `docs/GUIA_TECNICA.md`, `VERSION.yaml` | Ninguno (solo docs) |

**Nota de conflicto FASE-1-COH ↔ FASE-4-GATE**:
Ambas tocan `modules/quality_gates/`. FASE-1-COH modifica `coherence_gate.py`; FASE-4-GATE modifica el gate de `asset_confidence` (probablemente en `publication_gates.py` o archivo separado). Si `asset_confidence` vive en `coherence_gate.py`, el conflicto es real y FASE-4-GATE debe fusionarse con FASE-1-COH. El agente de FASE-1-COH debe verificar la ubicación de `asset_confidence` y reportar si hay overlap.

## Estado de Fases

| Fase | Estado | Fecha inicio | Fecha fin | Iteraciones | Notas |
|------|--------|--------------|-----------|-------------|-------|
| FASE-1-COH | ⏳ PENDIENTE | — | — | — | — |
| FASE-2-DEFAULT | ⏳ PENDIENTE | — | — | — | — |
| FASE-3-CONTENT | ⏳ PENDIENTE | — | — | — | — |
| FASE-4-GATE | ⏳ PENDIENTE | — | — | — | — |
| FASE-5-VERIFY | ⏳ PENDIENTE | — | — | — | — |
| FASE-RELEASE-4.45.0 | ⏳ PENDIENTE | — | — | — | — |

**Regla**: FASE-RELEASE solo se ejecuta cuando TODAS las fases de implementación están en estado ✅.
