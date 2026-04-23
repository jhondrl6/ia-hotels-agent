# FASE-CAUSAL-REFACTOR: Refactorizar Generador para Propuesta Dinámica

**ID**: FASE-CAUSAL-REFACTOR  
**Objetivo**: Crear SERVICE_CATALOG y refactorizar generador para usar pain detection como fuente  
**Dependencias**: FASE-CAUSAL-DIAG (mapeo completo)  
**Duración estimada**: 2-3 horas  
**Skill**: Código — Refactorización

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-CAUSAL-DIAG | ✅ Completada |

### Base Técnica Disponible
- Mapeo pain→servicio documentado en `context/mapeo-pain-servicio.md`
- Archivos a modificar:
  - `modules/commercial_documents/v4_proposal_generator.py`
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
- Tests base: 13/13 en `test_proposal_alignment.py`

### Decisión de Diseño: Opción C — SERVICE_CATALOG

En vez de iterar directamente sobre `detect_pains()`, crear un catálogo intermedio:

1. **`SERVICE_CATALOG`**: Dict[name → ServiceEntry] con:
   - `service_name`: nombre para la propuesta
   - `asset_type`: asset relacionado
   - `pain_id`: pain que lo activa
   - `description`: descripción corta

2. **Flujo refactorizado**:
   ```
   pain_solution_mapper.detect_pains()
         ↓
   [p.name for p in pains if p.solution_asset_type]
         ↓
   SERVICE_CATALOG[service_name]
         ↓
   Tabla de servicios (dinámica)
   ```

3. **`PROPOSAL_SERVICE_TO_ASSET` se mantiene** para backwards compatibility con gates de publicación.

---

## Tareas

### Tarea 1: Crear SERVICE_CATALOG

**Objetivo**: Crear catálogo de servicios vendibles con mapeo a pain.

**Archivos afectados**: `modules/commercial_documents/service_catalog.py` (nuevo)

**Acciones**:
- Crear dataclass `ServiceEntry` con: `service_name`, `asset_type`, `pain_id`, `description`
- Crear `SERVICE_CATALOG` como dict que incluya los 7 servicios actuales + mapeo a pain_id
- El `pain_id` debe coincidir con los ids de `Pain` en `pain_solution_mapper.py`

### Tarea 2: Refactorizar _generate_asset_quality_table

**Objetivo**: Que la tabla se genere dinámicamente desde los pains detectados.

**Archivos afectados**: `modules/commercial_documents/v4_proposal_generator.py`

**Acciones**:
- **IMPORTANTE**: Existe DUPLICACIÓN — `_generate_asset_quality_table` está definida DOS VECES (líneas ~654 y ~1084). Python usa la segunda, anulando la primera silenciosamente.
- Eliminar la definición duplicada (mantener solo una)
- Modificar `_generate_asset_quality_table()` para recibir también `detected_pains` (lista de Pain)
- En vez de iterar sobre `PROPOSAL_SERVICE_TO_ASSET`, iterar sobre `detected_pains`:
  - Para cada pain, buscar en `SERVICE_CATALOG` el servicio correspondiente
  - Solo incluir servicios cuyo pain fue detectado
- Mantener fallback: si no hay `detected_pains`, usar `PROPOSAL_SERVICE_TO_ASSET` (backwards)

### Tarea 3: Actualizar Template de Propuesta

**Objetivo**: Quitar hardcoding de la tabla principal.

**Archivos afectados**: `modules/commercial_documents/templates/propuesta_v6_template.md`

**Acciones**:
- Reemplazar la tabla principal hardcodeada (líneas ~44-52) con un placeholder `${dynamic_services_table}`
- El generador proveerá esta tabla dinámicamente basada en pains detectados
- O: si el template usa placeholder `${asset_quality_table}` para la tabla secundaria, verificar que ambxs sirven

### Tarea 4: Backwards Compatibility con Gates

**Objetivo**: Mantener `PROPOSAL_SERVICE_TO_ASSET` para verificación.

**Archivos afectados**: `modules/asset_generation/proposal_asset_alignment.py`

**Acciones**:
- NO eliminar `PROPOSAL_SERVICE_TO_ASSET`
- El gate de alineación (`verify_proposal_asset_alignment`) sigue usando `PROPOSAL_SERVICE_TO_ASSET`
- El cambio es en la generación, no en la verificación

### Tarea 5: Tests y Validaciones

**Acciones**:
- Ejecutar `pytest tests/asset_generation/test_proposal_alignment.py -v` — deben seguir pasando
- Ejecutar `run_all_validations.py --quick` — 4/4

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Existing alignment | `test_proposal_alignment.py` | 13/13 PASS (backwards compat) |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**
   - Marcar FASE-CAUSAL-REFACTOR como ✅ Completada
   - Actualizar fecha de finalización

2. **`README.md` del plan**
   - Actualizar tabla de progreso

3. **`09-documentacion-post-proyecto.md`**
   - Sección A: Agregar `service_catalog.py` si fue creado
   - Sección B: Agregar módulos modificados

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `SERVICE_CATALOG` creado con mapeo pain→servicio
- [ ] `_generate_asset_quality_table` duplicada eliminada (solo 1 definición)
- [ ] `_generate_asset_quality_table` refactorizado para usar pains detectados
- [ ] Tabla principal del template ya no es hardcodeada
- [ ] `PROPOSAL_SERVICE_TO_ASSET` se mantiene para backwards compatibility
- [ ] `test_proposal_alignment.py` pasa 13/13
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] Post-ejecución completada

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Backwards compatibility**: `PROPOSAL_SERVICE_TO_ASSET` NO se elimina — se mantiene para gates.
- **Sin romper gates**: Los gates de publicación deben seguir funcionando igual.
- **Template dinámico**: La tabla principal se genera dinámicamente desde los pains, no desde el diccionario fijo.
- **Tests**: Los 13 tests existentes deben seguir pasando sin modificación.

---

## Prompt de Ejecución

```
Actúa como ingeniero de software. Tu objetivo es refactorizar el generador de propuestas para usar pain detection.

CONTEXTO:
- FASE-CAUSAL-DIAG completada: mapeo pain→servicio documentado
- Solución: Crear SERVICE_CATALOG y usarlo en _generate_asset_quality_table
- Restricción: Mantener PROPOSAL_SERVICE_TO_ASSET para backwards compatibility de gates

TAREAS:
1. Crear SERVICE_CATALOG en modules/commercial_documents/service_catalog.py
   - ServiceEntry dataclass: service_name, asset_type, pain_id, description
   - 7+ entradas con pain_id que coincida con Pain.id en pain_solution_mapper

2. Refactorizar _generate_asset_quality_table() en v4_proposal_generator.py
   - IMPORTANTE: Eliminar duplicación (definida 2 veces, líneas ~654 y ~1084)
   - Recibir detected_pains como parámetro adicional
   - Iterar sobre detected_pains, no sobre PROPOSAL_SERVICE_TO_ASSET
   - Mantener fallback a PROPOSAL_SERVICE_TO_ASSET si no hay detected_pains

3. Actualizar propuesta_v6_template.md
   - Reemplazar tabla hardcodeada con placeholder dinámico

4. NO eliminar PROPOSAL_SERVICE_TO_ASSET — se mantiene para gates

5. Verificar backwards: pytest tests/asset_generation/test_proposal_alignment.py -v

CRITERIOS:
- Propuesta se genera dinámicamente desde pains detectados
- Tabla principal ya no es hardcodeada
- Backwards compatible con gates
- Tests pasan 13/13
```
