# FASE-CAUSAL-DIAG: Diagnosticar Causa Raíz

**ID**: FASE-CAUSAL-DIAG  
**Objetivo**: Confirmar y documentar la causa raíz del desalineamiento entre diagnóstico y propuesta comercial  
**Dependencias**: Ninguna  
**Duración estimada**: 30-45 minutos  
**Skill**: `iah-cli-plan-vs-reality-check`

---

## Contexto

El diagnóstico de v4complete para Amaziliahotel identifica múltiples brechas a través de `pain_solution_mapper` (~20 pains posibles), pero la propuesta comercial solo lista 5 servicios fijos. Específicamente, **FAQ** (`no_faq_schema` → `faq_page`) y **Open Graph** (`no_og_tags` → `open_graph`) están detectados en el audit pero nunca aparecen en la propuesta.

### Doble Tabla en la Propuesta
La propuesta comercial tiene **DOS** tablas de servicios:
1. **Tabla principal** (`propuesta_v6_template.md` líneas 44-50): Hardcodeada en markdown — texto plano con 5 filas fijas.
2. **Tabla de calidad** (`${asset_quality_table}`): Generada dinámicamente por `v4_proposal_generator.py` desde `PROPOSAL_SERVICE_TO_ASSET`.

El plan original solo consideraba la segunda. Esta fase debe documentar ambas.

### Base Técnica Disponible
- Archivos existentes:
  - `modules/commercial_documents/templates/propuesta_v6_template.md` (plantilla con tabla hardcodeada)
  - `modules/asset_generation/proposal_asset_alignment.py` (diccionario estático PROPOSAL_SERVICE_TO_ASSET)
  - `modules/commercial_documents/pain_solution_mapper.py` (mapeo pains→assets, incluye ASSET_NAMES)
  - `modules/asset_generation/asset_catalog.py` (catálogo centralizado — confirma que `faq_page` y `open_graph` son IMPLEMENTED)
- Tests base: Tests existentes de proposal_alignment
- Módulos disponibles: asset_generation, commercial_documents

---

## Tareas

### Tarea 1: Analizar proposal_asset_alignment.py
**Objetivo**: Documentar el mapeo actual PROPOSAL_SERVICE_TO_ASSET

**Acciones**:
1. Leer `modules/asset_generation/proposal_asset_alignment.py`
2. Extraer las entradas de `PROPOSAL_SERVICE_TO_ASSET`
3. Documentar qué servicios están mapeados

**Entregable**: Lista de servicios hardcoded en el mapeo

---

### Tarea 2: Analizar pain_solution_mapper.py
**Objetivo**: Verificar que FAQ y Open Graph están mapeados desde pains

**Acciones**:
1. Leer `modules/commercial_documents/pain_solution_mapper.py`
2. Buscar entrada `no_faq_schema` y sus assets
3. Buscar entrada `no_og_tags` y sus assets
4. Buscar `ASSET_NAMES` para verificar que incluye "Página de FAQ" y "Meta Tags Sociales"

**Entregable**: Confirmación de que los mapeos existen

---

### Tarea 3: Analizar plantilla propuesta
**Objetivo**: Confirmar que la plantilla hardcodea los servicios

**Acciones**:
1. Leer `modules/commercial_documents/templates/propuesta_v6_template.md`
2. Identificar las líneas con la tabla de servicios (líneas 46-50)
3. Confirmar que son filas hardcoded, no iteración dinámica

**Entregable**: Citar las líneas exactas del hardcoding

---

### Tarea 4: Analizar asset_catalog.py
**Objetivo**: Confirmar que `faq_page` y `open_graph` son assets implementados

**Acciones**:
1. Leer `modules/asset_generation/asset_catalog.py`
2. Buscar entradas `faq_page` y `open_graph` en `ASSET_CATALOG`
3. Verificar que ambos tienen `status=AssetStatus.IMPLEMENTED`

**Entregable**: Confirmación de que los assets existen y están implementados

---

### Tarea 5: Analizar ASSET_NAMES en pain_solution_mapper
**Objetivo**: Verificar nombres amigables para FAQ y OG

**Acciones**:
1. Leer `modules/commercial_documents/pain_solution_mapper.py` líneas 285-300
2. Verificar si `faq_page` tiene entrada en `ASSET_NAMES`
3. Verificar si `open_graph` tiene entrada en `ASSET_NAMES`
4. Verificar si `og_tags_guide` tiene entrada en `ASSET_NAMES`

**Entregable**: Lista de gaps en ASSET_NAMES

---

### Tarea 6: Documentar la Doble Tabla
**Objetivo**: Confirmar que hay DOS tablas de servicios en la propuesta

**Acciones**:
1. Leer `modules/commercial_documents/templates/propuesta_v6_template.md` líneas 44-50 (tabla principal hardcodeada)
2. Leer `modules/commercial_documents/v4_proposal_generator.py` líneas 654-700 (`_generate_asset_quality_table` — tabla dinámica)
3. Documentar que la tabla principal es texto estático markdown; la secundaria se genera desde PROPOSAL_SERVICE_TO_ASSET

**Entregable**: Evidencia de la doble tabla con citas de líneas exactas

---

### Tarea 7: Comparar servicios diagnóstico vs propuesta
**Objetivo**: Documentar exactamente qué brechas no tienen servicio correspondiente en la propuesta

**Acciones**:
1. Listar todos los pains en `pain_solution_mapper.PAIN_SOLUTION_MAP` que tienen assets IMPLEMENTED
2. Comparar contra las 5 entradas de `PROPOSAL_SERVICE_TO_ASSET`
3. Documentar cuáles pains quedan fuera de la propuesta

**Entregable**: Tabla comparativa Pain ↔ Servicio en propuesta

---

## Tests Obligatorios

Esta fase es de solo lectura. No hay tests que ejecutar.

**Comando de validación** (al final de la fase):
```bash
echo "FASE-CAUSAL-DIAG: Solo lectura, no hay tests"
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar:

1. **`dependencias-fases.md`**
   - Marcar FASE-CAUSAL-DIAG como ✅ Completada
   - Agregar fecha de ejecución

2. **`06-checklist-implementacion.md`**
   - Marcar Tarea 1-4 como ✅ completadas
   - Agregar notas de causa raíz confirmada

3. **NO modificar código** (esta fase es solo diagnóstico)

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `PROPOSAL_SERVICE_TO_ASSET` documentado (5 servicios)
- [ ] `no_faq_schema` y `no_og_tags` verificados en pain_solution_mapper
- [ ] `faq_page` y `open_graph` verificados en asset_catalog como IMPLEMENTED
- [ ] Gaps en `ASSET_NAMES` documentados (falta `open_graph`?)
- [ ] Doble tabla documentada (template hardcodeado + asset_quality_table dinámica)
- [ ] Líneas de hardcoding citadas de plantilla
- [ ] Tabla comparativa Pain ↔ Servicio creada
- [ ] Causa raíz resumida en una frase (incluyendo disclaimer de solución sintomática)
- [ ] **NO se modificó ningún archivo de código**

---

## Restricciones

- [ Esta fase es SOLO LECTURA ]
- [ NO modificar ningún archivo ]
- [ NO ejecutar scripts de generación ]
- [ NO crear commits ]

---

## Prompt de Ejecución

```
Actúa como detective de código. Tu objetivo es confirmar la causa raíz del desalineamiento.

CONTEXTO:
- Diagnóstico: 4 brechas detectadas
- Propuesta: 5 servicios hardcoded
- Problema: FAQ y Open Graph no aparecen en propuesta

TAREAS:
1. Documenta PROPOSAL_SERVICE_TO_ASSET en proposal_asset_alignment.py
2. Verifica que pain_solution_mapper tiene mapeos para FAQ y OG
3. Confirma que plantilla propuesta_v6 es hardcoded
4. Crea tabla comparativa Brecha → Servicio

CRITERIOS:
- Causa raíz identificada con evidencia de código
- Ningún archivo modificado
- Solo lectura
```
