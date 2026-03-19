---
description: Template para prompts de inicio de fase en proyectos phased_project_executor
version: 1.3.0
---

# Template: Prompt de Inicio de Fase

Este template define la estructura obligatoria para los archivos de prompt de fase (`sesion-N-*.md`, `05-prompt-inicio-sesion-fase-N.md`, etc.).

Basado en la skill `phased_project_executor` v1.3.0.

---

## Estructura Obligatoria

### 1. Encabezado

```markdown
# [TÍTULO DE LA FASE]

**ID**: [ID-ÚNICO]  
**Objetivo**: [Descripción clara y concisa del objetivo]  
**Dependencias**: [Lista de fases previas requeridas]  
**Duración estimada**: [Tiempo estimado, ej: 2-3 horas]  
**Skill**: [Skill recomendada de .agents/workflows/]
```

### 2. Contexto

```markdown
## Contexto

[Breve descripción del contexto del proyecto y por qué esta fase es necesaria]

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| Fase 1 | ✅ Completada |
| Fase 2 | ✅ Completada |
| ... | ... |

### Base Técnica Disponible
- Archivos existentes: [lista]
- Tests base: [número aproximado]
- Módulos disponibles: [lista]
```

### 3. Tareas Específicas

```markdown
## Tareas

### [Tarea 1: Nombre descriptivo]
**Objetivo**: [Qué se debe lograr]

**Archivos afectados**:
- `ruta/archivo.py`
- `ruta/otro.py`

**Criterios de aceptación**:
- [ ] Criterio 1 medible
- [ ] Criterio 2 medible
- [ ] Tests pasan

### [Tarea 2: Nombre descriptivo]
...
```

### 4. Tests Obligatorios

```markdown
## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_nombre.py` | `tests/test_nombre.py` | Debe pasar con X/X tests |
| ... | ... | ... |

**Comando de validación**:
```bash
pytest tests/test_nombre.py -v
python scripts/run_all_validations.py --quick
```
```

### 5. Post-Ejecución (OBLIGATORIO)

```markdown
## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesión):

1. **`dependencias-fases.md`** (o `dependencias-sesiones.md`)
   - Marcar esta fase como ✅ Completada
   - Actualizar fecha de finalización
   - Agregar notas de ejecución si aplica

2. **`README.md` del plan** (o archivo de índice principal)
   - Actualizar tabla de progreso
   - Marcar fase como completada
   - Actualizar métricas (tests, validaciones)

3. **`09-documentacion-post-proyecto.md`**
   - **Sección A**: Agregar módulos nuevos de esta fase
   - **Sección D**: Actualizar métricas acumulativas
   - **Sección E**: Marcar archivos afiliados actualizados

4. **`evidence/fase-{N}/`** (si aplica)
   - Crear directorio si hay evidencia que preservar
   - Guardar logs, screenshots, reportes, etc.

**NO esperar a la siguiente sesión para documentar.** La documentación incremental evita pérdida de contexto.
```

### 6. Criterios de Completitud (CHECKLIST)

```markdown
## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: Todos los tests de esta fase ejecutan exitosamente
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: Estado de esta fase marcado
- [ ] **Métricas consistentes**: Conteo de tests, versión, fechas coinciden con fases anteriores
- [ ] **Documentación afiliada**: CHANGELOG.md, GUIA_TECNICA.md, etc. actualizados (ver Paso 4 Sección E de la skill)
- [ ] **Evidencia preservada**: Archivos en `evidence/fase-{N}/` si aplica
- [ ] **Post-ejecución completada**: Todos los puntos de la sección anterior realizados

**NO marcar la fase como completada si algún criterio falla.**
```

### 7. Restricciones (Si aplica)

```markdown
## Restricciones

- [Lista de restricciones técnicas o de negocio]
- [Límites de alcance: qué NO está incluido en esta fase]
- [Dependencias que no se pueden modificar]
```

### 8. Prompt de Ejecución (Opcional)

```markdown
## Prompt de Ejecución

```
Actúa como [rol].

OBJETIVO: [Objetivo de la fase]

CONTEXTO:
- Fases previas completadas: [lista]
- Base técnica: [archivos disponibles]
- Tests actuales: [número]

TAREAS:
1. [Tarea 1]
2. [Tarea 2]
...

CRITERIOS:
- [Criterio 1]
- [Criterio 2]

VALIDACIONES:
- [Validación 1]
- [Validación 2]
```
```

---

## Checklist de Calidad del Prompt

Antes de usar este prompt, verificar:

- [ ] **Numeración correcta**: ID de fase coincide con nombre de archivo
- [ ] **Referencias consistentes**: Fases previas referenciadas correctamente
- [ ] **Tests acumulativos**: Conteo de tests incluye fases previas + nuevos
- [ ] **Dependencias claras**: Qué se necesita de fases anteriores
- [ ] **Criterios medibles**: Cada criterio es verificable (sí/no)
- [ ] **Post-ejecución incluida**: Sección 5 no fue omitida
- [ ] **Checklist completitud presente**: Sección 6 no fue omitida

---

## Notas de Uso

### Cuándo Modificar este Template

**NO modificar** este template para casos específicos. El template es la base estándar.

**SÍ modificar** el prompt generado a partir de este template para:
- Agregar contexto específico del proyecto
- Adaptar tareas a necesidades particulares
- Incluir referencias a archivos reales del proyecto

### Ejemplo de Adaptación

**Template (genérico)**:
```markdown
### Tareas
- Modificar archivo afectado
```

**Prompt adaptado**:
```markdown
### Tareas
- Modificar `modules/financial_engine/scenario_calculator.py` líneas 45-67
- Agregar método `calculate_monthly_opportunity()`
```

---

## Versión

- **v1.3.0** (2026-03-04): Template inicial para skill phased_project_executor v1.3.0
  - Incluye secciones Post-Ejecución y Criterios de Completitud obligatorios
  - Basado en lecciones aprendidas de implementación v4.4.0

