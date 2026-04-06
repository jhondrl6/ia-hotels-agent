# FASE 1: Corrección Bug COP COP + Test de Regresión

**ID**: FASE-1-COP-COP-REGRESSION
**Objetivo**: Eliminar la regresión "COP COP" y crear test de detección automática
**Dependencias**: Ninguna (fase standalone)
**Duración estimada**: 30-45 minutos
**Skill**: test-driven-development, systematic-debugging

---

## Contexto

### Problema Detectado
El documento `evidence/fase-2/validacion_fase2.md` línea 60 indica:
> "CORREGIDO: Duplicación 'COP COP' en línea del resumen"

**Pero el error sigue presente** en el archivo actual:
- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260323_073213.md`
- Línea 43: `$3.132.000 COP COP/mes`
- Línea 67: `$18.792.000 COP COP`

Esta es una **REGRESIÓN**: el bug fue "corregido" antes pero volvió a aparecer.

### Hallazgo Adicional
15+ archivos en archives/ y output/ contienen "COP COP":
```
/mnt/c/Users/Jhond/Github/iah-cli/archives/outputs/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260315_220603.md
/mnt/c/Users/Jhond/Github/iah-cli/archives/outputs/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260318_190641.md
/mnt/c/Users/Jhond/Github/iah-cli/archives/outputs/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260321_201334.md
/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260323_073213.md
... (15 archivos totales)
```

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| Ninguna | - |

### Base Técnica Disponible
- Archivos existentes: `modules/providers/benchmark_resolver.py`, `modules/delivery/generators/`
- Tests base: ~1434 tests
- Módulos disponibles: financial_engine, delivery/generators/

---

## Tareas

### Tarea 1: Identificar fuente del bug COP COP
**Objetivo**: Encontrar el template o generador que produce "COP COP"

**Archivos a investigar**:
- `modules/delivery/generators/report_gen.py`
- `modules/generators/report_builder*.py`
- `templates/*.md` en asset_generation

**Criterios de aceptación**:
- [ ] Fuente del "COP COP" identificada
- [ ] Ruta del generador al output documentada

### Tarea 2: Corregir la fuente del bug
**Objetivo**: Reemplazar "COP COP" por "COP" en el template/generador

**Archivos afectados**:
- `[archivo_identificado_en_tarea_1]`

**Criterios de aceptación**:
- [ ] " COP COP" reemplazado por " COP" en el generador/template
- [ ] Búsqueda `grep -rn "COP COP" modules/` retorna 0 resultados

### Tarea 3: Crear test de regresión
**Objetivo**: Asegurar que el bug no reaparezca

**Archivo a crear**:
- `tests/test_cop_cop_regression.py`

**Criterios de aceptación**:
- [ ] Test que verifica output de diagnosis sin "COP COP"
- [ ] Test que verifica templates de financial_scenarios sin "COP COP"
- [ ] Test pasa con `pytest tests/test_cop_cop_regression.py -v`

### Tarea 4: Validar corrección en archivos existentes
**Objetivo**: Limpiar outputs históricos contaminados

**Archivos a limpiar**:
- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260323_073213.md`
- `test_output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260316_124153.md`

**Criterios de aceptación**:
- [ ] `grep -rn "COP COP" output/` retorna 0 resultados
- [ ] `grep -rn "COP COP" test_output/` retorna 0 resultados

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_no_cop_cop_in_diagnosis` | `tests/test_cop_cop_regression.py` | Verifica ausencia de "COP COP" en outputs |
| `test_no_cop_cop_in_financial` | `tests/test_cop_cop_regression.py` | Verifica ausencia en financial scenarios |

**Comando de validación**:
```bash
pytest tests/test_cop_cop_regression.py -v
grep -rn "COP COP" modules/ output/ test_output/
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`** (o crear si no existe en `.opencode/plans/`)
   - Marcar FASE 1 como ✅ Completada
   - Fecha de finalización: 2026-03-23
   - Notas: "COP COP corregido, test de regresión creado"

2. **`08-plan-correccion-v4-issues.md`**
   - Marcar C1 y C2 como completadas
   - Actualizar tabla de métricas

3. **`09-documentacion-post-proyecto.md`** (crear si no existe)
   - Sección A: Agregar `tests/test_cop_cop_regression.py`
   - Sección D: Actualizar count de tests (+2)

4. **`evidence/fase-1-cop-cop/`**
   - Crear directorio
   - Guardar evidencia de grep antes/después

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Test nuevo pasa**: `pytest tests/test_cop_cop_regression.py -v` PASS
- [ ] **COP COP eliminado**: `grep -rn "COP COP" modules/` = 0 resultados
- [ ] **COP COP eliminado en output**: `grep -rn "COP COP" output/` = 0 resultados  
- [ ] **Test de regresión commitado**: Mensaje "[TDD] Test regresión COP COP"
- [ ] **Post-ejecución completada**: Todos los puntos anteriores realizados
- [ ] **Documentación afiliada**: CHANGELOG.md actualizado si corresponde

---

## Restricciones

- [ ] NO modificar otros archivos fuera de los específicamente listados
- [ ] NO cambiar lógica de negocio, solo corregir el string "COP COP"
- [ ] NO eliminar archivos de output/archive (solo limpiar contenido)

---

## Prompt de Ejecución

```
Actúa como developer con experiencia en Python y TDD.

OBJETIVO: Corregir bug de regresón "COP COP" y crear test de detección automática.

CONTEXTO:
- Bug: "COP COP" aparece duplicado en lugar de "COP"
- Fue "corregido" antes pero volvió como regresión
- 15+ archivos afectados en archives/ y output/
- Source: probablemente en templates de diagnosis o financial scenarios

TAREAS:
1. Buscar en modules/ y templates/ la fuente del "COP COP"
2. Corregir en el generador/template (no en outputs)
3. Crear test de regresión en tests/test_cop_cop_regression.py
4. Validar con grep que modules/ está limpio

CRITERIOS:
- modules/ no contiene "COP COP"
- Test de regresión pasa
- Fuente del bug identificada y documentada

VALIDACIONES:
- pytest tests/test_cop_cop_regression.py -v
- grep -rn "COP COP" modules/
```
