# Prompt de Inicio - Fase 1: TDD Gate

**ID**: FASE-1  
**Objetivo**: Implementar TDD Gate en `phased_project_executor.md`  
**Proyecto**: Evolución Agent Harness - Patrones Superpowers-Inspired

---

## Contexto de Fases Anteriores

**Estado del proyecto**: 
- No hay fases anteriores completadas
- Este es el inicio del plan v4.5.4
- Contexto base: AGENTS.md v4.5.3

**Pre-requisitos validados**:
- [ ] `python scripts/run_all_validations.py --quick` pasa
- [ ] `python scripts/run_all_validations.py` pasa
- [ ] `python scripts/sync_versions.py --check` pasa

---

## Tareas Específicas de Fase 1

### 1.1 Agregar Step 0.5 TDD Gate

Editar `.agents/workflows/phased_project_executor.md`:

**Ubicación**: Después de "Pre-requisitos (Contexto)" y antes de "1. Análisis del Plan"

**Contenido a agregar**:

```markdown
### 0.5. TDD Gate (Nuevo)
Antes de implementar cualquier cambio en esta fase:

- [ ] Test escrito que FALLA (describe el comportamiento esperado)
- [ ] Test commitado en tests/ (evidencia de intento TDD)
- [ ] Solo entonces: proceder a implementar código

**Output obligatorio**: Archivo `tests/test_[caracteristica].py` con:
  - Test fallando claramente documentado
  - Comentario explicando el comportamiento esperado
  - Commit en historial con mensaje "[TDD] Test inicial para [caracteristica]"

**Validación**: 
  - `pytest tests/test_[caracteristica].py -v` debe fallar inicialmente
  - Después de implementación, mismo test debe pasar

*Validación*: Test fallando documentado, listo para implementación.
```

### 1.2 Actualizar Criterios de Éxito

Agregar en la sección "Criterios de Éxito":
- [ ] "Paso 0.5 TDD Gate: PASS (test fallando antes de implementación)"

### 1.3 Actualizar Validación de Cumplimiento (Paso 9)

En la tabla de Paso 9, agregar verificación para TDD Gate.

---

## Base Técnica Disponible

- **Archivo objetivo**: `.agents/workflows/phased_project_executor.md`
- **Workflow de referencia**: Mismo archivo (auto-referencia)
- **Línea de inserción sugerida**: Después de línea 25 (Pre-requisitos de Validación)

---

## Tests Obligatorios

**Tests base**: 1434+ tests passing (no se esperan tests nuevos para esta fase)

**Nota**: Esta fase modifica un workflow, no código Python. Los tests de regresión existentes validan el comportamiento general.

---

## Post-Ejecución (Obligatorio)

Después de completar las tareas:

1. **Actualizar checklist** en `06-checklist-implementacion.md`:
   - [ ] Marcar tareas 1.1, 1.2, 1.3 como completadas ✅
   - [ ] Registrar fecha de completion

2. **Ejecutar validación**:
   ```bash
   grep -n "0.5. TDD Gate" .agents/workflows/phased_project_executor.md
   ```

3. **Documentar issues** (si hay):
   - Registrar en este archivo cualquier problema encontrado

4. **Preparar para Fase 2**:
   - Confirmar que TDD Gate está implementado
   - Verificar que las tareas de validación pasaron

---

## Criterios de Completitud Fase 1

| Criterio | Validación |
|----------|------------|
| Step 0.5 existe | `grep "0.5. TDD Gate" .agents/workflows/phased_project_executor.md` |
| Criterios de éxito actualizados | Verificar presencia en sección correspondiente |
| Validación de cumplimiento actualizada | Verificar en Paso 9 |

**Veredicto**: ⏳ Pendiente de validación

---

## Restricciones

- ❌ **NO continuar a Fase 2** en la misma sesión
- ❌ **NO hacer commit** hasta completar validación de completitud
- ✅ **CERRAR sesión** después de completar Fase 1
- ✅ **Abrir nueva sesión** para Fase 2

---

##召唤

Actúa como especialista en evolución de agent harness para el sistema IA Hoteles.

**Tu tarea**:
1. Implementar las tareas 1.1, 1.2, 1.3 descritas arriba
2. Ejecutar validaciones de post-ejecución
3. Documentar el resultado en Post-Ejección
4. Cerrar la sesión (NO continuar a Fase 2)

**Recursos**:
- `.agents/workflows/phased_project_executor.md` - Archivo a modificar
- `docs/CONTRIBUTING.md` - Guía de referencia
- `.opencode/plans/06-checklist-implementacion.md` - Checklist a actualizar

**Validación final**:
```bash
grep -n "0.5. TDD Gate" .agents/workflows/phased_project_executor.md
```

Si la validación pasa, la Fase 1 está completa. Cerrar sesión y reportar al usuario.
