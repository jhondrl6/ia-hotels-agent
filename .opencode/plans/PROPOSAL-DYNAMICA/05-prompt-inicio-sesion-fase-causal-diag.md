# FASE-CAUSAL-DIAG: Diagnosticar Mapeo Pain→Servicio

**ID**: FASE-CAUSAL-DIAG  
**Objetivo**: Mapear exactamente qué pain genera qué servicio y documentar el flujo actual  
**Dependencias**: Ninguna  
**Duración estimada**: 1-2 horas  
**Skill**: Código (lectura y análisis)

---

## Contexto

### Estado de Fases Anteriores
N/A — esta es la primera fase.

### Base Técnica Disponible
- Archivos existentes:
  - `modules/commercial_documents/v4_proposal_generator.py` — generador de propuesta
  - `modules/commercial_documents/pain_solution_mapper.py` — detector de pains
  - `modules/asset_generation/proposal_asset_alignment.py` — mapping servicio→asset con `PROPOSAL_SERVICE_TO_ASSET`
  - `modules/commercial_documents/templates/propuesta_v6_template.md` — template de propuesta
- Tests base: 13/13 en `test_proposal_alignment.py`
- Módulos disponibles:pain_solution_mapper, v4_proposal_generator, proposal_asset_alignment

### Problema Conocido
La propuesta genera servicios desde un diccionario estático (`PROPOSAL_SERVICE_TO_ASSET` de 7 entradas), no desde los pains detectados dinámicamente. Esto causa desalineamiento entre el diagnóstico y la propuesta.

---

## Tareas

### Tarea 1: Leer y Documentar pain_solution_mapper.py

**Objetivo**: Entender todos los pains que se detectan y cómo se mapean a soluciones.

**Acciones**:
- Leer `modules/commercial_documents/pain_solution_mapper.py` completo
- Documentar cada pain detectado en `detect_pains()`:
  - `id` del pain
  - `name` y `description`
  - `solution_asset_type` o asset asociado
  - `severity`
- Identificar cuáles de estos pains tienen映射 a servicios en `PROPOSAL_SERVICE_TO_ASSET`

### Tarea 2: Leer y Documentar PROPOSAL_SERVICE_TO_ASSET

**Objetivo**: Entender los 7 servicios estáticos actuales.

**Acciones**:
- Leer `modules/asset_generation/proposal_asset_alignment.py`
- Documentar cada entrada de `PROPOSAL_SERVICE_TO_ASSET`:
  - Nombre del servicio (como aparece en la propuesta)
  - `asset_type` correspondiente
- Identificar cuál de los 7 servicios NO corresponde a un pain detectado

### Tarea 3: Leer y Documentar v4_proposal_generator.py

**Objetivo**: Entender cómo se genera la propuesta y dónde está la doble tabla.

**Acciones**:
- Leer `modules/commercial_documents/v4_proposal_generator.py`
- Documentar `_generate_asset_quality_table()`: cómo itera sobre `PROPOSAL_SERVICE_TO_ASSET`
- Identificar la tabla principal hardcodeada en `propuesta_v6_template.md`

### Tarea 4: Gap Analysis

**Objetivo**: Documentar el desalineamiento completo.

**Acciones**:
- Crear tabla de mapping: pain → servicio(s) correspondiente(s)
- Identificar:
  - Pains detectados que NO tienen servicio en `PROPOSAL_SERVICE_TO_ASSET`
  - Servicios en `PROPOSAL_SERVICE_TO_ASSET` que NO tienen pain correspondiente
- Documentar la causa del desalineamiento

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| N/A | - | Esta fase es solo lectura, sin tests |

**Comando de validación**:
```bash
# Sin tests en esta fase - solo lectura
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**
   - Marcar FASE-CAUSAL-DIAG como ✅ Completada
   - Actualizar fecha de finalización

2. **`README.md` del plan**
   - Actualizar tabla de progreso

3. **En `.opencode/plans/PROPOSAL-DYNAMICA/context/`** (nuevo o existente)
   - Crear archivo `mapeo-pain-servicio.md` con el gap analysis completo

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `pain_solution_mapper.py` leído y documentado (todos los pains)
- [ ] `PROPOSAL_SERVICE_TO_ASSET` documentado (7 entradas)
- [ ] `v4_proposal_generator.py` leído (especialmente `_generate_asset_quality_table`)
- [ ] Gap analysis completo: pains sin servicio + servicios sin pain
- [ ] Mapeo pain→servicio documentado
- [ ] **No se modificó ningún archivo de código**
- [ ] Post-ejecución completada

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Solo lectura**: No modificar ningún archivo de código.
- **Alcance**: Documentar el mapeo existente, no diseñar la solución.
- **Evidencia**: Guardar el mapeo en `.opencode/plans/PROPOSAL-DYNAMICA/context/mapeo-pain-servicio.md`

---

## Prompt de Ejecución

```
Actúa como arquitecto de software. Tu objetivo es diagnosticar el mapeo pain→servicio actual.

CONTEXTO:
- Proyecto: iah-cli v4.34.0
- Problema: La propuesta usa diccionario estático, no pains dinámicos
- Necesitas mapear exactamente qué pain genera qué servicio

TAREAS:
1. Leer pain_solution_mapper.py — documentar todos los pains y sus soluciones
2. Leer proposal_asset_alignment.py — documentar PROPOSAL_SERVICE_TO_ASSET (7 entradas)
3. Leer v4_proposal_generator.py — entender cómo se genera la propuesta
4. Hacer gap analysis: pains sin servicio, servicios sin pain
5. Documentar mapeo pain→servicio completo

CRITERIOS:
- Mapeo completo de todos los pains a servicios
- Gap analysis claro
- Cero modificaciones de código

ENTREGABLE:
- Archivo: .opencode/plans/PROPOSAL-DYNAMICA/context/mapeo-pain-servicio.md
```
