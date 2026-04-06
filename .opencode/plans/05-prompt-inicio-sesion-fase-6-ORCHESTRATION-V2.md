# FASE 6: Orchestration v2 - Intelligent Branching

**ID**: FASE-6-ORCHESTRATION-V2
**Objetivo**: Implementar validación temprana y branching inteligente basado en calidad de datos
**Dependencias**: FASE 5 completada
**Duración estimada**: 2-3 horas
**Skill**: code-architecture, systematic-debugging

---

## Problema Actual

```
Flujo actual (lineal):
Audit → Validation → Asset Generation → Report

Problema:
- Validation ocurre DESPUÉS de generación
- No hay branching
- Assets se escriben antes de validar
```

---

## Solución: Data Assessment + Branching

```
                    ┌──────────────┐
                    │   AUDIT      │
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │  ASSESSMENT  │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ LOW DATA │ │ MED DATA  │ │HIGH DATA │
        │ (< 30%)  │ │ (30-70%) │ │ (> 70%)  │
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Fast Gen │ │ Standard │ │ Full Gen │
        │ 3-4 ass. │ │ 6-7 ass. │ │ 9+ ass.  │
        └──────────┘ └──────────┘ └──────────┘
```

---

## Tareas

### T6A: Implementar Data Assessment
**Archivos**: `modules/asset_generation/data_assessment.py` (NUEVO)

**Clasificaciones**:
- `LOW`: < 30% data available → Fast Path
- `MED`: 30-70% data available → Standard Path
- `HIGH`: > 70% data available → Full Path

**Métricas a evaluar**:
- GBP completeness (reviews, photos, score)
- Web scraping success
- SEO data availability
- Schema markup presence

### T6B: Validation Before Generation
**Archivos**: `modules/asset_generation/conditional_generator.py`

**Flujo corregido**:
1. Collect data
2. Validate data quality → SI FAIL → error inmediato
3. Assess data classification
4. Branch to appropriate path
5. Generate (validación ya pasó)

### T6C: Refactorizar conditional_generator
**Cambios**:
- Agregar método `assess_data_quality(data) → Classification`
- Modificar `generate()` para usar branching
- Crear `generate_fast()`, `generate_standard()`, `generate_full()`

---

## Tests Obligatorios

| Test | Criterio |
|------|----------|
| `test_data_assessment_low` | Clasifica hotels <30% datos como LOW |
| `test_data_assessment_high` | Clasifica hotels >70% datos como HIGH |
| `test_validation_before_generation` | No genera si datos inválidos |
| `test_branching_paths` | 3 paths ejecutan correctamente |

---

## Criterios de Completitud

- [ ] Data Assessment implementado y funcionando
- [ ] Validación ocurre ANTES de generación
- [ ] 3 paths de branching implementados
- [ ] Tests pasan
- [ ] Integration test pasa

---

## Post-Ejecución

1. Actualizar `dependencias-fases.md`
2. Documentar en `09-documentacion-post-proyecto.md`
3. CHANGELOG.md actualizado
