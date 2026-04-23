# Dependencias de Fases - FASE-CAUSAL Alignment Fix

> **Plan**: Corregir desalineamiento diagnóstico-propuesta en iah-cli v4.33.0  
> **Fecha**: 2026-04-22

---

## Diagrama de Dependencias

```
[FASE-CAUSAL-DIAG] ──→ [FASE-CAUSAL-FIX] ──→ [FASE-CAUSAL-TEST] ──→ [FASE-RELEASE-4.34.0]
      │                     │                     │                      │
  Sin dependencias       Requiere DIAG         Requiere FIX          Requiere TEST
  (Inicio)               + código actual        + Amaziliahotel       + docs completos
```

---

## Tabla de Conflictos Potenciales

| Fase | Archivos Modificados | Riesgo de Conflicto |
|------|---------------------|---------------------|
| FASE-CAUSAL-DIAG | Ninguno (solo lectura) | Ninguno |
| FASE-CAUSAL-FIX | `proposal_asset_alignment.py` | Medio - podría compartir con FASE-RELEASE |
| FASE-CAUSAL-FIX | `propuesta_v6_template.md` | Medio - podría compartir con FASE-RELEASE |
| FASE-CAUSAL-TEST | Tests nuevos | Bajo |
| FASE-RELEASE-4.34.0 | VERSION.yaml, CHANGELOG.md, GUIA_TECNICA.md | Medio - sincronización manual |

---

## Detalle de Fases

### FASE-CAUSAL-DIAG
- **Objetivo**: Confirmar causa raíz del desalineamiento y documentar doble tabla
- **Archivos leídos**: 
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
  - `modules/asset_generation/proposal_asset_alignment.py`
  - `modules/commercial_documents/pain_solution_mapper.py`
  - `modules/asset_generation/asset_catalog.py`
  - `modules/commercial_documents/v4_proposal_generator.py`
- **Dependencias**: Ninguna
- **Conflictos**: Ninguno

### FASE-CAUSAL-FIX
- **Objetivo**: Corregir mapeo propuesta→asset, ASSET_NAMES y ambas tablas de la propuesta
- **Archivos a modificar**:
  - `modules/asset_generation/proposal_asset_alignment.py`
  - `modules/commercial_documents/pain_solution_mapper.py`
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
- **Dependencias**: FASE-CAUSAL-DIAG (confirmar causa raíz y doble tabla)
- **Conflictos**: Ninguno con otras fases activas
- **Nota**: Corrección sintomática. La causa raíz sistémica (propuesta estática vs pains dinámicos) queda para FASE futura.

### FASE-CAUSAL-TEST
- **Objetivo**: Verificar que la corrección funciona end-to-end
- **Archivos leídos**: Output de v4complete para Amaziliahotel
- **Tests a ejecutar**: Tests existentes de proposal_alignment
- **Dependencias**: FASE-CAUSAL-FIX
- **Conflictos**: Ninguno

### FASE-RELEASE-4.34.0
- **Objetivo**: Documentar, sincronizar versiones y hacer release
- **Archivos a modificar**:
  - `VERSION.yaml`
  - `CHANGELOG.md`
  - `GUIA_TECNICA.md`
  - `docs/contributing/REGISTRY.md`
  - `AGENTS.md`
- **Dependencias**: FASE-CAUSAL-TEST (tests pasan)
- **Conflictos**: Verificar sincronización con sync_versions.py

---

## Estado de Fases

|| Fase | Estado | Fecha Inicio | Fecha Fin | Notas |
|------|--------|--------------|-----------|-------|
| FASE-CAUSAL-DIAG | ✅ Completada | 2026-04-23 | 2026-04-23 | Diagnóstico causa raíz confirmado |
| FASE-CAUSAL-FIX | ✅ Completada | 2026-04-23 | 2026-04-23 | 7 servicios, 13 tests pass |
| FASE-CAUSAL-TEST | ⏳ Pendiente | - | - | Depende de FIX |
| FASE-RELEASE-4.34.0 | ⏳ Pendiente | - | - | Depende de TEST |
