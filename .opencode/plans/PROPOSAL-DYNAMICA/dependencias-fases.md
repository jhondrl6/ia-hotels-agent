# Dependencias de Fases - Propuesta Dinámica desde Pain Detection

> **Plan**: Resolver causa raíz arquitectónica — propuesta desde diccionario estático → pains dinámicos  
> **Fecha**: 2026-04-23

---

## Diagrama de Dependencias

```
[FASE-CAUSAL-DIAG] ──→ [FASE-CAUSAL-REFACTOR] ──→ [FASE-CAUSAL-VALIDATE] ──→ [FASE-RELEASE-X.Y.Z]
      │                     │                     │                      │
  Sin dependencias       Requiere DIAG         Requiere REFACTOR       Requiere VALIDATE
  (Inicio)              + código actual        + tests                 + docs completos
```

---

## Tabla de Conflictos Potenciales

| Fase | Archivos Modificados | Riesgo de Conflicto |
|------|---------------------|---------------------|
| FASE-CAUSAL-DIAG | Ninguno (solo lectura) | Ninguno |
| FASE-CAUSAL-REFACTOR | `v4_proposal_generator.py`, `proposal_asset_alignment.py` | Medio - comparte con gate de publicación |
| FASE-CAUSAL-VALIDATE | Tests nuevos | Bajo |
| FASE-RELEASE-X.Y.Z | VERSION.yaml, CHANGELOG.md, GUIA_TECNICA.md | Medio - sincronización manual |

---

## Detalle de Fases

### FASE-CAUSAL-DIAG
- **Objetivo**: Mapear exactamente qué pain genera qué servicio y documentar el flujo actual
- **Archivos leídos**:
  - `modules/commercial_documents/v4_proposal_generator.py`
  - `modules/commercial_documents/pain_solution_mapper.py`
  - `modules/asset_generation/proposal_asset_alignment.py`
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
- **Dependencias**: Ninguna
- **Conflictos**: Ninguno

### FASE-CAUSAL-REFACTOR
- **Objetivo**: Crear SERVICE_CATALOG y refactorizar generador para usar pain detection
- **Archivos a modificar**:
  - `modules/commercial_documents/v4_proposal_generator.py`
  - Posible nuevo archivo: `modules/commercial_documents/service_catalog.py`
- **Dependencias**: FASE-CAUSAL-DIAG (mapeo completo)
- **Conflictos**: Ninguno con otras fases activas
- **Nota**: Mantener backwards compatibility con `PROPOSAL_SERVICE_TO_ASSET` para gates de publicación

### FASE-CAUSAL-VALIDATE
- **Objetivo**: Verificar refactor mediante tests unitarios, inspección de código y test dinámico nuevo
- **Archivos leídos**: Código refactorizado (v4_proposal_generator.py, service_catalog.py)
- **Tests a ejecutar**: Tests existentes de proposal_alignment (13/13) + test dinámico nuevo
- **Dependencias**: FASE-CAUSAL-REFACTOR
- **Conflictos**: Ninguno

### FASE-RELEASE-X.Y.Z
- **Objetivo**: Documentar, sincronizar versiones y hacer release
- **Archivos a modificar**:
  - `VERSION.yaml`
  - `CHANGELOG.md`
  - `GUIA_TECNICA.md`
  - `docs/contributing/REGISTRY.md`
  - `AGENTS.md`
- **Dependencias**: FASE-CAUSAL-VALIDATE (tests pasan)
- **Conflictos**: Verificar sincronización con sync_versions.py

---

## Estado de Fases

| Fase | Estado | Fecha Inicio | Fecha Fin | Notas |
|------|--------|--------------|-----------|-------|
| FASE-CAUSAL-DIAG | ✅ Completada | 2026-04-23 | 2026-04-23 | Mapeo: 25 pains, 7 servicios, 13 gaps |
| FASE-CAUSAL-REFACTOR | ✅ Completada | 2026-04-23 | 2026-04-23 | SERVICE_CATALOG (7 entries), _generate_asset_quality_table refactorizado |
| FASE-CAUSAL-VALIDATE | ✅ Completada | 2026-04-23 | 2026-04-23 | Tests: 14/14 PASS (test_proposal_dynamic.py), 13/13 alignment, 4/4 validations |
| FASE-RELEASE-X.Y.Z | ⏳ Pendiente | - | - | Depende de VALIDATE |
