# FASE 2: Corrección Bugs Asset Generation

**ID**: FASE-2-ASSET-GENERATION-BUGS
**Objetivo**: Corregir inconsistencias entre estadoReported y estadoReal en asset generation
**Dependencias**: FASE 1 completada
**Duración estimada**: 45-60 minutos
**Skill**: systematic-debugging, test-driven-development

---

## Contexto

### Problemas Identificados

**Problema A: optimization_guide se escribe aunque falla validación**
```
asset_generation_report.json dice:
  failed_assets → optimization_guide → "Content validation failed"
  
metadata.json del mismo asset dice:
  status: "generated"
  fallback_used: true
```

El archivo `ESTIMATED_guia_optimizacion_20260323_073214.md` existe (2702 bytes) pero el reporte lo marca como "failed". Esto indica que el fallback se ejecutó y escribió el archivo, pero después la validación falló, creando estado inconsistente.

**Problema B: confidence_score siempre 0.5 en asset_generation_report**
```
asset_generation_report.json muestra confidence_score = 0.5 para TODOS los assets:
  - geo_playbook: 0.5
  - review_plan: 0.5
  - hotel_schema: 0.5
  - llms_txt: 0.5
  - review_widget: 0.5
  - org_schema: 0.5

Pero los metadata.json tienen valores diferentes:
  - geo_playbook: 0.7
  - hotel_schema: 0.3
  - org_schema: 1.0
```

Los confidence scores NO se están leyendo correctamente de los metadata generados.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE 1: COP COP | 🚧 Pendiente |

### Base Técnica Disponible
- Archivos existentes: 
  - `modules/asset_generation/conditional_generator.py`
  - `modules/asset_generation/asset_content_validator.py`
  - `modules/asset_generation/asset_metadata.py`
- Tests base: ~1436 (después de FASE 1)
- Módulos: AssetGeneration, ConditionalGenerator, AssetContentValidator

---

## Tareas

### Tarea 1: Investigar orden de ejecución - Asset Write vs Validation
**Objetivo**: Determinar por qué el archivo se escribe antes de la validación final

**Archivos a investigar**:
- `modules/asset_generation/conditional_generator.py` - método generate()
- `modules/asset_generation/asset_content_validator.py` - lógica de validación

**Criterios de aceptación**:
- [ ] Flujo de ejecución documentado (¿write ocurre antes de validation?)
- [ ] Punto exacto de inconsistencia identificado

### Tarea 2: Corregir Bug - Archivo no debe escribirse si validation falla
**Objetivo**: El archivo SÓLO debe escribirse si pasa la validación de contenido

**Archivos a modificar**:
- `modules/asset_generation/conditional_generator.py`

**Lógica correcta**:
```
1. Generar contenido
2. Validar contenido
3. SI validación falla → NO escribir archivo, retornar con status "failed"
4. SI validación pasa → Escribir archivo con metadata
```

**Criterios de aceptación**:
- [ ] optimization_guide NO se escribe cuando validation falla
- [ ] El reporte muestra correctamente el estado "failed" (sin archivo escrito)
- [ ] Test: generar asset que fallaría y verificar que no existe archivo

### Tarea 3: Corregir Bug - confidence_score en asset_generation_report
**Objetivo**: Que el confidence_score del reporte lea el valor correcto de metadata

**Archivos a modificar**:
- `modules/asset_generation/asset_metadata.py` - cómo se calcula confidence_score
- `modules/asset_generation/v4_asset_orchestrator.py` - cómo se serializa el reporte

**Criterios de aceptación**:
- [ ] asset_generation_report.json muestra confidence_score = metadata.confidence_level
- [ ] Todos los 6 assets tienen valores coherentes (0.3, 0.7, 1.0)
- [ ] Test: generar assets y verificar que scores coinciden

### Tarea 4: Crear tests de regresión para ambos bugs
**Objetivo**: Asegurar que los bugs no reaparezcan

**Archivos a crear**:
- `tests/test_asset_write_validation_order.py`
- `tests/test_confidence_score_consistency.py`

**Criterios de aceptación**:
- [ ] Test de orden validate-then-write pasa
- [ ] Test de consistencia de scores pasa
- [ ] `pytest tests/test_asset_write_validation_order.py tests/test_confidence_score_consistency.py -v`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_asset_not_written_on_validation_failure` | `tests/test_asset_write_validation_order.py` | Archivo no existe si validation falla |
| `test_confidence_scores_match_metadata` | `tests/test_confidence_score_consistency.py` | Scores en report = scores en metadata |

**Comando de validación**:
```bash
pytest tests/test_asset_write_validation_order.py tests/test_confidence_score_consistency.py -v
python -m pytest tests/test_never_block_integration.py -v
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** (en `.opencode/plans/`)
   - Marcar FASE 2 como ✅ Completada
   - Dependencia: FASE 1 debe estar completada

2. **`08-plan-correccion-v4-issues.md`**
   - Marcar A1 y A2 como completadas
   - Actualizar estado de bugs

3. **`09-documentacion-post-proyecto.md`**
   - Sección A: Agregar tests nuevos
   - Sección D: Actualizar count de tests

4. **`evidence/fase-2-asset-bugs/`**
   - Crear directorio
   - Guardar evidencia: antes/después de corrección

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Bug A corregido**: optimization_guide NO se escribe cuando validation falla
- [ ] **Bug B corregido**: confidence_score en report = confidence en metadata
- [ ] **Tests nuevos pasan**: `pytest tests/test_asset_*.py -v` PASS
- [ ] **Tests de regresión commitados**: Mensaje "[TDD] Tests asset bugs"
- [ ] **Validación E2E**: `pytest tests/test_never_block_integration.py -v` PASS
- [ ] **Post-ejecución completada**: Todos los puntos anteriores realizados

---

## Restricciones

- [ ] NO cambiar la lógica de validation de frases genéricas (eso es FASE 3)
- [ ] NO modificar benchmark_resolver.py a menos que sea necesario para los bugs
- [ ] Mantener backwards compatibility con assets existentes

---

## Prompt de Ejecución

```
Actúa como developer con experiencia en debugging de sistemas de generación de assets.

OBJETIVO: Corregir 2 bugs en asset generation:

BUG A: optimization_guide se escribe aunque validation falla
- El archivo existe pero asset_generation_report.json dice "failed"
- El fallback se ejecutó y escribió, pero después validation falló

BUG B: confidence_score siempre 0.5 en asset_generation_report
- geo_playbook metadata dice 0.7 pero report dice 0.5
- Los scores no se están leyendo correctamente

CONTEXTO:
- Archivos principales: conditional_generator.py, asset_content_validator.py, asset_metadata.py
- asset_generation_report.json está en: output/v4_complete/hotel_vísperas/v4_audit/
- Los metadata.json están en cada carpeta de asset

TAREAS:
1. Investigar orden de ejecución: generate() → validate() → write()
2. Corregir para que validation failure prevenga el write
3. Corregir para que confidence_score se lea correctamente de metadata
4. Crear tests de regresión

CRITERIOS:
- optimization_guide NO existe cuando validation falla
- confidence_score en report = confidence en metadata para todos los assets

VALIDACIONES:
- pytest tests/test_asset_write_validation_order.py tests/test_confidence_score_consistency.py -v
- Verificar output real regenerando para hotelvisperas
```
