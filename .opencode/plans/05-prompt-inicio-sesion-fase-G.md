# FASE-G: Fix DESCONEXION-04 - WhatsApp CONFLICT No Detectado

**ID**: FASE-G  
**Objetivo**: Corregir causa raíz de whatsapp_button que no se planifica cuando WhatsApp tiene conflicto
**Dependencias**: FASE-D' (desconexiones identificadas)  
**Duración estimada**: 20-30 minutos
**Skill**: systematic-debugging

---

## Contexto

### Problema Identificado en FASE-D'
DESCONEXION-04: `whatsapp_button` no se detecta como pain aunque `whatsapp_validation.confidence == CONFLICT`

### Causa Raíz
**Ubicación**: `main.py` líneas 1696-1713

```python
if whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.VERIFIED:
    # Add as VERIFIED
elif whatsapp_web:
    # Add as ESTIMATED - PROBLEMA: CONFLICT cae aquí
```

Cuando `whatsapp_validation.confidence == CONFLICT`, el código cae al `elif whatsapp_web` y añade el campo como `ESTIMATED` en lugar de `CONFLICT`. Esto causa que `detect_pains` nunca vea `whatsapp_number` como CONFLICT y por tanto `whatsapp_conflict` pain nunca se detecta.

### Bug Adicional
**BUG-02**: `optimization_guide` falla por placeholder `...` (ellipsis)
- El template usa `...` que el content validator detecta como placeholder genérico
- Error: "Content validation failed: placeholder: Placeholder detected: \.\.\."

---

## Criterios de Éxito

| # | Criterio | Verificación |
|---|----------|--------------|
| G1 | `whatsapp_number` aparece como CONFLICT en validation_summary | Buscar en logs |
| G2 | `whatsapp_conflict` pain se detecta | Buscar en "Problemas detectados" |
| G3 | `whatsapp_button` aparece en assets planificados | Buscar en logs |
| G4 | `whatsapp_button` se genera exitosamente | Verificar archivo en output |
| G5 | `optimization_guide` pasa content validation | Sin errores de placeholder |
| G6 | Coherence score >= 0.8 | Verificar en salida |
| G7 | Publication Readiness = READY | Verificar en salida |
| G8 | NO hay nuevas desconexiones | Revisar TODOS los errores/warnings |
| G9 | 0 desconexiones no resueltas | Todos los pains tienen asset |

---

## Ejecución

### Tarea 1: Fix DESCONEXION-04 (main.py)

**Archivo**: `main.py`
**Ubicación**: Líneas ~1696-1713

**Cambio requerido**:
```python
# ANTES (INCORRECTO):
if whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.VERIFIED:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        value=whatsapp_web,
        confidence=ConfidenceLevel.VERIFIED,
        ...
    ))
elif whatsapp_web:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        value=whatsapp_web,
        confidence=ConfidenceLevel.ESTIMATED,
        ...
    ))

# DESPUÉS (CORRECTO):
if whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.VERIFIED:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        value=whatsapp_web,
        confidence=ConfidenceLevel.VERIFIED,
        ...
    ))
elif whatsapp_validation and whatsapp_validation.confidence == ConfidenceLevel.CONFLICT:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        value=whatsapp_web,
        confidence=ConfidenceLevel.CONFLICT,
        ...
    ))
elif whatsapp_web:
    validated_fields.append(ValidatedField(
        field_name="whatsapp_number",
        value=whatsapp_web,
        confidence=ConfidenceLevel.ESTIMATED,
        ...
    ))
```

### Tarea 2: Fix BUG-02 (conditional_generator.py)

**Problema**: El template de `optimization_guide` usa `...` (ellipsis) que el content validator rechaza.

**Buscar en**: `modules/asset_generation/conditional_generator.py`
**Método**: `_generate_optimization_guide`

Reemplazar `...` con texto válido como:
- `"continuar con la siguiente sección"` o similar
- O eliminar del todo si no es necesario

### Tarea 3: Verificación con Tests

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_pain_solution_mapper.py tests/asset_generation/test_conditional_generator.py -v --tb=short
```

**Criterio**: 28/28 tests pasan

### Tarea 4: Ejecución E2E

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
mkdir -p evidence/fase-G
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/ --debug 2>&1 | tee evidence/fase-G/ejecucion.log
```

### Verificación de Resultados
Buscar en la salida:
```
whatsapp_button
optimization_guide
CONFLICT
Problemas detectados
Assets planificados
```

---

## Post-Ejecución (OBLIGATORIO - Línea 97 phased_project_executor.md)

### 1. `dependencias-fases.md`
- Marcar FASE-G como ✅ Completada o ❌ Fallida
- Fecha de finalización
- Resultados G1-G9

### 2. `06-checklist-implementacion.md`
- Marcar FASE-G según corresponda
- Actualizar estado general del proyecto

### 3. `09-documentacion-post-proyecto.md`
- Sección D: Actualizar métricas
- Sección G: Agregar FASE-G y DESCONEXION-04

### 4. `evidence/fase-G/`
- Guardar logs de ejecución

### 5. Si TODAS las fases completadas y 0 desconexiones:
- El proyecto REFACTOR-COHESION-01 está COMPLETO
- Actualizar línea 97 del phased_project_executor.md si hay cambios

---

## Criterios de Completitud (CHECKLIST FINAL)

- [ ] **G1**: `whatsapp_number` como CONFLICT en validation_summary
- [ ] **G2**: `whatsapp_conflict` pain detectado
- [ ] **G3**: `whatsapp_button` planificado
- [ ] **G4**: `whatsapp_button` generado
- [ ] **G5**: `optimization_guide` pasa content validation
- [ ] **G6**: Coherence >= 0.8
- [ ] **G7**: Publication Readiness = READY
- [ ] **G8**: NO nuevas desconexiones
- [ ] **G9**: 0 desconexiones no resueltas
- [ ] **Tests**: 28/28 regresión pasan
- [ ] **`dependencias-fases.md` actualizado**
- [ ] **Documentación post-proyecto actualizada**

---

## Resultado Esperado

Después de FASE-G:
- ✅ `whatsapp_number` aparece como CONFLICT en validation_summary
- ✅ `whatsapp_conflict` pain se detecta
- ✅ `whatsapp_button` planificado y generado
- ✅ `optimization_guide` pasa content validation
- ✅ 0 desconexiones
- ✅ Proyecto REFACTOR-COHESION-01 COMPLETO
