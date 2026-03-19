# Prompt de Inicio - Fase 2: Parallel Execution

**ID**: FASE-2  
**Objetivo**: Implementar Parallel Execution en `audit_guardian.md`  
**Proyecto**: Evolución Agent Harness - Patrones Superpowers-Inspired

---

## Contexto de Fases Anteriores

**Fase 1**: ✅ COMPLETADA
- TDD Gate implementado en `phased_project_executor.md`
- Step 0.5 agregado y validado

**Pre-requisitos validados**:
- [ ] Fase 1 completada (TDD Gate implementado)
- [ ] `python scripts/run_all_validations.py --quick` pasa
- [ ] Validación de Fase 1: `grep "0.5. TDD Gate" .agents/workflows/phased_project_executor.md`

---

## Tareas Específicas de Fase 2

### 2.1 Modificar Steps 2-4 para Ejecución Paralela

Editar `.agents/workflows/audit_guardian.md`:

**Ubicación**: Líneas 20-42 (Steps 1-5)

**Contenido actual** (líneas 20-42):
```markdown
### 1. Validación de Identidad y Verdad
// turbo
truth_protocol --url {{url}}

### 2. Extracción Geográfica y GBP
// turbo
geo_stage --url {{url}}

### 3. Auditoría de Credibilidad Web (SEO)
// turbo
seo_stage --url {{url}}

### 4. Análisis Inteligente e IA
// turbo
ia_stage --url {{url}}

### 5. Generación de Entregables
// turbo
outputs_stage --url {{url}}
```

**Contenido a reemplazar**:
```markdown
### 1. Validación de Identidad y Verdad
// turbo
truth_protocol --url {{url}}

*Validación*: El hotel ha sido validado contra Benchmarks 2026.

### 2-4. Ejecución Paralela de Etapas Independientes
// turbo parallel
geo_stage --url {{url}}

// turbo parallel  
seo_stage --url {{url}}

// turbo parallel
ia_stage --url {{url}}

*Validación*: Se han obtenido datos de GBP, web_score y análisis IA en paralelo.

### 5. Generación de Entregables
// turbo
outputs_stage --url {{url}}
```

**Nota**: El comentario `// turbo parallel` es una convención propuesta. Si el skill_executor.py actual no lo soporta, documentar como mejora futura.

### 2.2 Verificar Compatibilidad con skill_executor.py

Revisar `agent_harness/skill_executor.py` para determinar:
- [ ] ¿Soporta el token `// turbo parallel`?
- [ ] ¿Cómo maneja ejecución paralela de stages?
- [ ] Documentar hallazgos

**Si no soporta**:
- Agregar nota en el workflow sobre fallback
- Mantener estructura actual como comentario
- Crear issue para mejora futura

### 2.3 Actualizar Matriz de Capacidades

Editar `.opencode/plans/matriz-capacidades.md`:
- [ ] Cambiar estado de "Parallel Execution" de "por conectar" a "conectada"
- [ ] Agregar fecha de conexión

---

## Base Técnica Disponible

- **Archivo objetivo**: `.agents/workflows/audit_guardian.md`
- **Archivo de referencia**: `agent_harness/skill_executor.py` (para compatibilidad)
- **Dependencia**: Fase 1 debe estar completada

---

## Tests Obligatorios

**Tests base**: 1434+ tests passing (no se esperan tests nuevos para esta fase)

**Validación de regresión**:
```bash
python -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (Obligatorio)

Después de completar las tareas:

1. **Actualizar checklist** en `06-checklist-implementacion.md`:
   - [ ] Marcar tareas 2.1, 2.2, 2.3 como completadas ✅
   - [ ] Registrar fecha de completion

2. **Ejecutar validación**:
   ```bash
   grep -n "parallel" .agents/workflows/audit_guardian.md
   ```

3. **Verificar skill_executor.py**:
   - Documentar si soporta o no ejecución paralela
   - Si no soporta, documentar fallback

4. **Documentar issues** (si hay):
   - Registrar en este archivo cualquier problema encontrado

5. **Preparar para Fase 3**:
   - Confirmar que Parallel Execution está implementado
   - Verificar que las tareas de validación pasaron

---

## Criterios de Completitud Fase 2

| Criterio | Validación |
|----------|------------|
| Steps 2-4 modificados | `grep "parallel" .agents/workflows/audit_guardian.md` |
| Matriz actualizada | Verificar estado "conectada" en matriz-capacidades.md |
| Compatibilidad verificada | Revisión de skill_executor.py documentada |

**Veredicto**: ⏳ Pendiente de validación

---

## Restricciones

- ❌ **NO continuar a Fase 3** en la misma sesión
- ❌ **NO hacer commit** hasta completar validación de completitud
- ✅ **CERRAR sesión** después de completar Fase 2
- ✅ **Abrir nueva sesión** para Fase 3 (Validaciones Finales)

---

##召唤

Actúa como especialista en evolución de agent harness para el sistema IA Hoteles.

**Tu tarea**:
1. Implementar las tareas 2.1, 2.2, 2.3 descritas arriba
2. Ejecutar validaciones de post-ejecución
3. Documentar el resultado en Post-Ejecución
4. Cerrar la sesión (NO continuar a Fase 3)

**Recursos**:
- `.agents/workflows/audit_guardian.md` - Archivo a modificar
- `agent_harness/skill_executor.py` - Referencia para compatibilidad
- `.opencode/plans/matriz-capacidades.md` - Actualizar
- `.opencode/plans/06-checklist-implementacion.md` - Checklist a actualizar

**Validación final**:
```bash
grep -n "parallel" .agents/workflows/audit_guardian.md
```

Si la validación pasa, la Fase 2 está completa. Cerrar sesión y reportar al usuario.
