# FASE-D': Certificación E2E - Confirmación de Desconexiones Resueltas

**ID**: FASE-D'  
**Estado**: ❌ FALLIDA (2026-03-25 16:05) - REQUIERE FASE-G
**Objetivo**: Certificar que TODAS las desconexiones están resueltas y NO hay nuevas desconexiones sin detectar
**Dependencias**: FASE-F (fix DESCONEXION-03 completada)  
**Duración estimada**: 30-45 minutos
**Skill**: dogfood

---

## Contexto

### Problemas a Resolver
| Bug ID | Descripción | Estado Pre-FASE-D' |
|--------|-------------|-------------------|
| FASE-B-01 | optimization_guide: "pendiente" rechazado por content validator | ✅ Corregido en FASE-E |
| DESCONEXION-03 | whatsapp_button no se planifica con whatsapp_conflict | ✅ Corregido en FASE-F |
| DESCONEXION-04 | whatsapp_conflict no se detecta como pain (validation_summary incorrecto) | ❌ NUEVA |
| BUG-02 | optimization_guide falla por placeholder `...` | ❌ NUEVO |

### Estado de Fases Anteriores
| Fase | Estado | Notas |
|------|--------|-------|
| FASE-A | ✅ Completada | PainSolutionMapper detecta CONFLICT |
| FASE-B | ✅ Completada | optimization_guide corregido |
| FASE-C | ✅ Completada | Tests 28/28 pasan |
| FASE-D | ❌ Fallida | Bugs identificados |
| FASE-E | ✅ Completada | E1✅ (pendiente→"Sin title tag") |
| FASE-F | ✅ Completada | Fix confirmado en get_assets_for_pain |
| FASE-D' | ❌ Fallida | Bugs adicionales identificados |
| FASE-G | ⏳ Pendiente | Fix DESCONEXION-04 + BUG-02 |

### Cambios desde FASE-D Original
1. **FASE-E E1**: `conditional_generator.py` - "pendiente" → "Sin title tag"/"Sin meta description"
2. **FASE-F**: `pain_solution_mapper.py` - `whatsapp_conflict` ahora genera `whatsapp_button` sin verificar threshold
3. **FASE-D'**: Se descubrieron bugs adicionales que requieren FASE-G

### Resultados FASE-D' (FALLIDA)
| Criterio | Estado | Detalle |
|----------|--------|---------|
| D1: whatsapp_button planificado | ❌ FALSO | No aparece en asset_plan |
| D2: whatsapp_button generado | ❌ FALSO | No aparece en generated_assets |
| D3: optimization_guide pasa | ❌ FALSO | Content validation failed: placeholder `...` |
| D4: Coherence >= 0.8 | ✅ PASÓ | Score 0.87 |
| D5: Publication Readiness | ✅ PASÓ | READY_FOR_PUBLICATION |
| D6: NO nuevas desconexiones | ❌ FALSO | Nueva: DESCONEXION-04 |
| D7: 0 desconexiones no resueltas | ❌ FALSO | 2 desconexiones activas |
| Tests regresión | ✅ PASÓ | 28/28 PASSED |

### Bugs Identificados en FASE-D'

1. **DESCONEXION-04**: `whatsapp_button` NO se detecta como pain
   - Causa: `main.py` líneas 1696-1713 - cuando `whatsapp_validation.confidence == CONFLICT`, el código cae al `elif whatsapp_web` y añade el campo como `ESTIMATED`
   - El pain `whatsapp_conflict` nunca se detecta porque `validation_summary` tiene `whatsapp_number` como `ESTIMATED`

2. **BUG-02**: `optimization_guide` falla por placeholder `...`
   - Causa: El template usa `...` (ellipsis) que el content validator detecta como placeholder
   - Error: "Content validation failed: placeholder: Placeholder detected: \.\.\."

---

## Nueva Fase Requerida: FASE-G

**Siguiente paso**: Ejecutar FASE-G para corregir DESCONEXION-04 y BUG-02

Prompt: `.opencode/plans/05-prompt-inicio-sesion-fase-G.md`

---

## Criterios de Certificación E2E (para cuando FASE-G se complete)

### Criterios de Éxito (CHECKLIST OBLIGATORIO)

| # | Criterio | Verificación |
|---|----------|--------------|
| G1 | `whatsapp_number` aparece como CONFLICT en validation_summary | Buscar en logs |
| G2 | `whatsapp_conflict` pain se detecta | Buscar en "Problemas detectados" |
| G3 | `whatsapp_button` aparece en assets planificados | Buscar en logs |
| G4 | `whatsapp_button` se genera exitosamente | Verificar archivo en output |
| G5 | `optimization_guide` pasa content validation | Sin errores de placeholder |
| G6 | Coherence score >= 0.8 | Verificar en salida |
| G7 | Publication Readiness = READY | Verificar en salida |
| G8 | **NO hay nuevas desconexiones** | Revisar TODOS los errores/warnings |
| G9 | 0 desconexiones no resueltas | Todos los pains tienen asset |

---

## Ejecución (para FASE-G)

### Comando de Verificación (post-fix)
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/ --debug 2>&1 | tee evidence/fase-G/ejecucion.log
```

### Verificación de Assets Planificados
Buscar en la salida:
```
whatsapp_button
optimization_guide
```

### Verificación de Content Validation
Buscar errores:
```
generic_phrase
pendiente
placeholder
```

---

## Tests de Regresión Obligatorios

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/asset_generation/test_conditional_generator.py -v --tb=short
```

**Criterio**: 28/28 tests pasan

---

## Post-Ejecución (OBLIGATORIO - Línea 97 phased_project_executor.md)

⚠️ **NO OMITIR** ⚠️

### 1. `dependencias-fases.md`
- Marcar FASE-G como ✅ Completada o ❌ Fallida
- Fecha de finalización
- Resultados G1-G9
- Coherence score final
- Lista de assets generados

### 2. `06-checklist-implementacion.md`
- Marcar FASE-G según corresponda
- Actualizar estado general del proyecto

### 3. `09-documentacion-post-proyecto.md`
- Sección D: Actualizar métricas
- Sección G: Agregar DESCONEXION-04 y BUG-02 como identificados/corregidos
- Sección H: Notas de cierre si aplica

### 4. `evidence/fase-G/`
- Crear directorio si no existe
- Guardar logs de ejecución
- Capturar output de assets generados

### 5. Actualizar Workflow (si aplica)
Si TODAS las fases están completas y 0 desconexiones:
- Actualizar línea 97 del phased_project_executor.md si hay cambios necesarios
- El proyecto REFACTOR-COHESION-01 está COMPLETO

---

## Criterios de Completitud (CHECKLIST FINAL) - FASE-G

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **G1**: `whatsapp_number` como CONFLICT en validation_summary
- [ ] **G2**: `whatsapp_conflict` pain detectado
- [ ] **G3**: `whatsapp_button` planificado
- [ ] **G4**: `whatsapp_button` generado exitosamente
- [ ] **G5**: `optimization_guide` pasa content validation
- [ ] **G6**: Coherence >= 0.8
- [ ] **G7**: Publication Readiness = READY
- [ ] **G8**: NO hay nuevas desconexiones detectadas
- [ ] **G9**: 0 desconexiones no resueltas
- [ ] **Tests**: 28/28 regresión pasan
- [ ] **`dependencias-fases.md` actualizado**: FASE-G marcada como completada
- [ ] **Documentación post-proyecto actualizada**

---

## Resultado Esperado (post FASE-G)

Después de FASE-G:
- ✅ `whatsapp_number` aparece como CONFLICT en validation_summary
- ✅ `whatsapp_conflict` pain se detecta
- ✅ `whatsapp_button` planificado y generado
- ✅ `optimization_guide` pasa content validation
- ✅ NO hay nuevas desconexiones
- ✅ Todas las desconexiones RESUELTAS
- ✅ El sistema v4complete funciona correctamente para hotelvisperas.com
- ✅ Proyecto REFACTOR-COHESION-01 COMPLETADO
