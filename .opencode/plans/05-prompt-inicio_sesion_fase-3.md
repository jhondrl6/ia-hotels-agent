# Prompt de Inicio - Fase 3: Validaciones Finales

**ID**: FASE-3  
**Objetivo**: Ejecutar validaciones completas y actualizar documentación  
**Proyecto**: Evolución Agent Harness - Patrones Superpowers-Inspired

---

## Contexto de Fases Anteriores

**Fase 1**: ✅ COMPLETADA (2026-03-17)
- TDD Gate implementado en `phased_project_executor.md`

**Fase 2**: ✅ COMPLETADA (2026-03-17)
- Parallel Execution implementado en `audit_guardian.md`
- Matriz de capacidades actualizada

**Pre-requisitos validados**:
- [ ] Fases 1 y 2 completadas
- [ ] `python scripts/run_all_validations.py --quick` debe pasar

---

## Tareas Específicas de Fase 3

### 3.1 Ejecutar Validaciones Completas

```bash
# Validación rápida
python scripts/run_all_validations.py --quick

# Validación completa
python scripts/run_all_validations.py

# Sincronización de versiones
python scripts/sync_versions.py --check
```

**Checklist**:
- [ ] domain_primer_methods: PASS
- [ ] version_sync: PASS
- [ ] context_file_paths: PASS
- [ ] Sin hardcoded secrets detectados

### 3.2 Ejecutar Regression Test

```bash
# Tests completos
python -m pytest tests/ -v --tb=short
```

**Criterio**: 1434+ tests passing

### 3.3 Actualizar Documentación Obligatoria (CONTRIBUTING.md §5)

#### 3.3.1 CHANGELOG.md

Agregar entrada:

```markdown
## v4.5.4 - Process Refinement (2026-03-17)

### Objetivo
Implementar mejoras incrementales al agent_harness inspiradas en Superpowers sin adopción de framework externo.

### Cambios Implementados
- `.agents/workflows/phased_project_executor.md` - Agregado Step 0.5 TDD Gate
- `.agents/workflows/audit_guardian.md` - Modificado Steps 2-4 para ejecución paralela

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `.agents/workflows/phased_project_executor.md` | Agregado TDD Gate |
| `.agents/workflows/audit_guardian.md` | Ejecución paralela |

### Tests
- 1434+ tests passing (sin cambios)
```

#### 3.3.2 GUIA_TECNICA.md

Agregar en "Notas de Cambios":

```markdown
### v4.5.4 - Process Refinement (2026-03-17)

**Mejoras de Proceso**:
- TDD Gate: Require test fallido antes de implementación (phased_project_executor.md Step 0.5)
- Parallel Execution: Stages geo/seo/ia ejecutados en paralelo (audit_guardian.md Steps 2-4)
```

#### 3.3.3 VERSION.yaml (Opcional)

Según alcance del cambio, considerar incremento de versión:
- Si es release completo: actualizar a v4.5.4
- Si es patch: puede mantenerse en v4.5.3

**Recomendación**: Mantener v4.5.3 hasta próxima release completa

### 3.4 Actualizar AGENTS.md

En "Estado Actual":

| Aspecto | Estado |
|---------|--------|
| **Version** | v4.5.3 → v4.5.3+ (process) |
| **Mejoras** | TDD Gate, Parallel Execution |

Opcional: Agregar nota en CHANGELOG de features en lugar de versión.

### 3.5 Verificar Capability Contract

```bash
# Verificar TDD Gate conectado
grep -n "0.5. TDD Gate" .agents/workflows/phased_project_executor.md

# Verificar Parallel Execution conectado  
grep -n "parallel" .agents/workflows/audit_guardian.md
```

**Checklist**:
- [ ] 0 capacidades sin invocación en runtime
- [ ] 0 capacidades sin output observable
- [ ] TDD Gate: "conectada"
- [ ] Parallel Execution: "conectada"

---

## Base Técnica Disponible

- **Validaciones**: scripts/run_all_validations.py
- **Documentación**: CHANGELOG.md, GUIA_TECNICA.md, AGENTS.md
- **Capability Contract**: matriz-capacidades.md

---

## Post-Ejecución (Obligatorio)

1. **Actualizar checklist** en `06-checklist-implementacion.md`:
   - [ ] Todas las tareas 3.1-3.5 completadas ✅
   - [ ] Registrar fecha de completion

2. **Ejecutar validación final**:
   ```bash
   python scripts/run_all_validations.py
   python -m pytest tests/ -v --tb=short
   ```

3. **Documentar resultado**:
   - Tests passing: ____
   - Validaciones: PASS/FAIL
   - Issues: (si hay)

4. **Preparar commit**:
   - Mensaje sugerido: `[RELEASE] v4.5.4 - Process refinement: TDD Gate + Parallel Execution`

---

## Criterios de Completitud Fase 3

| Criterio | Validación |
|----------|------------|
| Validaciones passent | `python scripts/run_all_validations.py` |
| Tests passing | `python -m pytest tests/` → 1434+ |
| CHANGELOG.md actualizado | Verificar entrada v4.5.4 |
| Capability contract verificado | 0 capacidades huérfanas |
| Documentación actualizada | GUIA_TECNICA.md, AGENTS.md |

**Veredicto Final**: ⏳ Pendiente de validación

---

## Cierre del Proyecto

Una vez completada Fase 3:

1. ✅ Ejecutar validaciones finales
2. ✅ Actualizar documentación
3. ✅ Verificar capability contract
4. ✅ Hacer commit con mensaje apropiado
5. ✅ Reportar al usuario

**El proyecto v4.5.4 está completo cuando todos los criterios de Fase 3 pasen.**

---

##召唤

Actúa como especialista en evolución de agent harness para el sistema IA Hoteles.

**Tu tarea**:
1. Implementar las tareas 3.1-3.5 descritas arriba
2. Ejecutar todas las validaciones
3. Documentar el resultado final en Post-Ejecución
4. Preparar para commit

**Recursos**:
- `scripts/run_all_validations.py` - Validaciones
- `CHANGELOG.md` - Actualizar
- `GUIA_TECNICA.md` - Actualizar
- `AGENTS.md` - Actualizar
- `.opencode/plans/matriz-capacidades.md` - Verificar

**Validación final**:
```bash
python scripts/run_all_validations.py
python -m pytest tests/ -v --tb=short
```

Si todas las validaciones pasan, el proyecto está completo. Cerrar sesión y reportar al usuario.
