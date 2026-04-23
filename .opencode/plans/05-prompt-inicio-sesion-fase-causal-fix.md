# FASE-CAUSAL-FIX: Corregir Mapeo y Hacer Dinámica la Plantilla

**ID**: FASE-CAUSAL-FIX  
**Objetivo**: Actualizar proposal_asset_alignment.py y plantilla para incluir FAQ y Open Graph  
**Dependencias**: FASE-CAUSAL-DIAG (causa raíz confirmada)  
**Duración estimada**: 1-2 horas  
**Skill**: Ninguna específica (cambio directo)

---

## Contexto

### Causa Raíz Confirmada (de FASE-CAUSAL-DIAG)
La propuesta comercial tiene **DOS** tablas de servicios:
1. **Tabla principal** (`propuesta_v6_template.md` líneas 44-50): Hardcodeada en markdown — 5 filas fijas de texto plano.
2. **Tabla de calidad** (`${asset_quality_table}`): Generada dinámicamente desde `PROPOSAL_SERVICE_TO_ASSET` (5 entradas).

Ambas tablas son **estáticas**: no reaccionan a los pains detectados por `pain_solution_mapper`. Los mapeos para FAQ (`no_faq_schema` → `faq_page`) y Open Graph (`no_og_tags` → `open_graph`) existen en el código, pero nunca llegan a la propuesta.

Además, `ASSET_NAMES` en `pain_solution_mapper` no tiene entrada para `open_graph`.

### ⚠️ Alcance y Limitaciones
- **Este plan resuelve**: FAQ y Open Graph aparecerán en la propuesta (corrección sintomática).
- **Este plan NO resuelve**: Que la propuesta se genere dinámicamente desde los pains detectados (causa raíz sistémica). Eso requiere refactor posterior de `v4_proposal_generator` para usar `pain_solution_mapper` como fuente de servicios en vez de `PROPOSAL_SERVICE_TO_ASSET`.

### Servicios que FALTAN en la propuesta
1. **"Página de FAQ"** → pain `no_faq_schema` → asset `faq_page`
2. **"Meta Tags Sociales (Open Graph)"** → pain `no_og_tags` → asset `open_graph`

### Base Técnica Disponible
- `modules/asset_generation/proposal_asset_alignment.py` (modificar diccionario)
- `modules/commercial_documents/templates/propuesta_v6_template.md` (modificar tabla hardcodeada)
- `modules/commercial_documents/pain_solution_mapper.py` (modificar ASSET_NAMES)
- `modules/commercial_documents/v4_proposal_generator.py` (referencia — tabla dinámica)

---

## Tareas

### Tarea 1: Actualizar PROPOSAL_SERVICE_TO_ASSET
**Objetivo**: Agregar entradas para FAQ y Open Graph

**Archivo**: `modules/asset_generation/proposal_asset_alignment.py`

**Cambios**:
```python
# AGREGAR estas entradas al dict PROPOSAL_SERVICE_TO_ASSET:
"Meta Tags Sociales (Open Graph)": "open_graph",
"Página de FAQ": "faq_page",
```

**Criterios de aceptación**:
- [ ] `PROPOSAL_SERVICE_TO_ASSET` tiene 7 entradas (5 originales + 2 nuevas)
- [ ] `ALL_PROMISED_SERVICES` se actualiza automáticamente

---

### Tarea 2: Corregir ASSET_NAMES en pain_solution_mapper
**Objetivo**: Agregar nombres amigables faltantes para FAQ y OG

**Archivo**: `modules/commercial_documents/pain_solution_mapper.py` líneas 285-300

**Cambios**:
```python
ASSET_NAMES = {
    ...
    "faq_page": "Página de FAQ",           # ✓ Ya existe — verificar
    "open_graph": "Meta Tags Sociales (Open Graph)",  # ← AGREGAR si falta
    "og_tags_guide": "Guía de Open Graph",             # ← AGREGAR si falta
    ...
}
```

**Criterios de aceptación**:
- [ ] `faq_page` tiene nombre amigable
- [ ] `open_graph` tiene nombre amigable
- [ ] `og_tags_guide` tiene nombre amigable

---

### Tarea 3: Actualizar tabla principal del template markdown
**Objetivo**: Modificar la tabla hardcodeada en `propuesta_v6_template.md` para incluir FAQ y OG

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md` líneas 44-50

**Cambios**:
```markdown
|| Servicio | Qué obtiene |
||----------|-------------|
|| **✅ Google Maps Optimizado** (GEO) | ... |
|| **✅ SEO Local** (SEO) | ... |
|| **✅ Botón de WhatsApp** | ... |
|| **✅ Datos Estructurados** | ... |
|| **✅ Informe Mensual** | ... |
|| **✅ Página de FAQ** | ... |          ← AGREGAR
|| **✅ Meta Tags Sociales (Open Graph)** | ... |  ← AGREGAR
```

**Nota**: Esta tabla sigue siendo estática. La solución dinámica real requiere refactor futuro. Por ahora, agregamos las filas faltantes para que el documento sea consistente con `${asset_quality_table}`.

**Criterios de aceptación**:
- [ ] La tabla principal tiene 7 filas
- [ ] Las descripciones de FAQ y OG son coherentes con el resto del documento

---

### Tarea 4: Implementar corrección en tabla dinámica (si aplica)
**Objetivo**: Verificar que `${asset_quality_table}` refleje los 7 servicios

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` (líneas 654-700)

**Acciones**:
1. Verificar que `_generate_asset_quality_table` itera sobre `PROPOSAL_SERVICE_TO_ASSET.items()`
2. Confirmar que, tras Tarea 1, esta tabla mostrará 7 servicios automáticamente
3. Si el generador tiene otra lógica que filtra servicios, documentarla

**Criterios de aceptación**:
- [ ] `_generate_asset_quality_table` muestra 7 servicios tras el cambio
- [ ] No hay regresión en servicios existentes

---

### Tarea 5: Ejecutar tests de proposal_alignment
**Objetivo**: Verificar que no hay regresión

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
```

**Criterios de aceptación**:
- [ ] Tests pasan
- [ ] Si hay tests que verifican explícitasmente 5 servicios, actualizarlos a 7

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_proposal_service_to_asset_mapping` | `tests/asset_generation/test_proposal_alignment.py` | Pasa con 7 entradas |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -v
```

**Validación de regresión**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar:

1. **`dependencias-fases.md`**
   - Marcar FASE-CAUSAL-FIX como ✅ Completada
   - Agregar fecha de ejecución
   - Notas sobre qué se modificó

2. **`06-checklist-implementacion.md`**
   - Marcar Tareas 1-4 como completadas
   - Actualizar estado de FASE-CAUSAL-FIX

3. **`09-documentacion-post-proyecto.md`** (sección simple, no el flujo completo):
   - Sección A: Nota de módulos modificados
   - Sección E: Archivos modificados

4. **Ejecutar tests** para verificar que no hay regresión

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `PROPOSAL_SERVICE_TO_ASSET` tiene 7 entradas
- [ ] `ASSET_NAMES` incluye `open_graph` y `og_tags_guide` con nombres amigables
- [ ] Tabla principal del template (`propuesta_v6_template.md`) tiene 7 filas
- [ ] Tabla dinámica (`_generate_asset_quality_table`) refleja 7 servicios automáticamente
- [ ] `pytest tests/asset_generation/test_proposal_alignment.py -v` pasa
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] Documentación básica agregada
- [ ] **Disclaimer de alcance agregado**: se documenta que esta es corrección sintomática, no refactor arquitectónico

---

## Restricciones

- [ No modificar el orquestador principal ]
- [ No cambiar lógica de detección de pains ]
- [ Solo cambiar propuesta→asset y plantilla ]
- [ Mantener compatibilidad hacia atrás ]

---

## Prompt de Ejecución

```
Actúa como refactorizador de código.

CONTEXTO:
- Causa raíz superficial: PROPOSAL_SERVICE_TO_ASSET solo tiene 5 entradas (falta FAQ y OG).
- Causa raíz REAL: la propuesta se genera desde diccionario estático, no desde pains detectados.
- Este plan resuelve el síntoma inmediato; el refactor arquitectónico queda para FASE futura.
- Hay DOS tablas en la propuesta: tabla principal hardcodeada en template markdown + asset_quality_table dinámica.

TAREAS:
1. Agregar "Meta Tags Sociales (Open Graph)" → "open_graph" y "Página de FAQ" → "faq_page" a PROPOSAL_SERVICE_TO_ASSET
2. Verificar/agregar ASSET_NAMES para open_graph y og_tags_guide (faq_page ya existe)
3. Actualizar tabla principal en propuesta_v6_template.md (líneas 44-50) para incluir 7 filas
4. Verificar que _generate_asset_quality_table refleja 7 servicios automáticamente
5. Ejecutar tests de proposal_alignment y run_all_validations.py --quick

CRITERIOS:
- 7 entradas en PROPOSAL_SERVICE_TO_ASSET
- ASSET_NAMES completo para FAQ y OG
- Ambas tablas de la propuesta consistentes (7 servicios)
- Tests pasan sin regresión
- Se documenta que esto es corrección sintomática
```
