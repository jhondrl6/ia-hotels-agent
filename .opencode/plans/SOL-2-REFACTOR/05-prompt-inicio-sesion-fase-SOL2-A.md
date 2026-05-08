---
description: FASE-SOL2-A Ghost Ref & SitePresence Cleanup
version: 1.0.0
skill: phased_project_executor
---

> [!IMPORTANT]
> **NOTA POST-EJECUCION (2026-05-07)**
> Esta fase fue completada exitosamente. Los siguientes componentes YA EXISTEN:
> - `SitePresenceChecker` en `modules/asset_generation/site_presence_checker.py` (601 lineas)
> - `deployment_assistant.md` en `.agents/workflows/deployment_assistant.md` (43 lineas)
> Si estas leyendo este prompt en una sesion futura, NO re-crear estos componentes.
> Saltar directamente a la seccion de verificacion o al siguiente paso del plan.

# FASE-SOL2-A: Ghost Ref & SitePresence Cleanup

**ID**: FASE-SOL2-A  
**Objetivo**: Eliminar o crear componentes fantasma (SitePresenceChecker, deployment_assistant.md) para eliminar bloqueantes de integridad del sistema.  
**Dependencias**: Ninguna (primera fase del proyecto SOL-2).  
**Duración estimada**: 1.5-2 horas  
**Skill**: phased_project_executor, systematic-debugging  

## Contexto

Durante la validación E2E de FASE-PATCH-C (Termales, 2026-05-07) se descubrieron dos componentes fantasma:

1. **GAP-A [ALTA]**: `modules/asset_generation/site_presence_checker.py` NO EXISTE pero es importado en `publication_gates.py:798`. El `try/except` silencia el error, dejando el feature "check site presence" completamente deshabilitado.
2. **GAP-B [ALTA]**: `.agents/workflows/deployment_assistant.md` es referenciado en `AGENTS.md:52` e `INDICE_DOCUMENTACION.md:210` pero el archivo NO EXISTE.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| PROP-PATCH FASE-PATCH-C | ✅ Completada |
| Contexto SOL-2 | ✅ Validado |

### Base Técnica Disponible
- `modules/quality_gates/publication_gates.py` (líneas 793-813 ya tienen infraestructura para SitePresenceChecker)
- `AGENTS.md` (línea 52 referencia deployment_assistant.md)
- `INDICE_DOCUMENTACION.md` (línea 210 referencia deployment_assistant.md)
- Tests base: ~2491 funciones en 192 archivos

## Tareas

### Tarea 1: Decisión SitePresenceChecker
**Objetivo**: Decidir si crear el módulo faltante o eliminar la referencia.

**Criterios de aceptación**:
- [ ] Leer `publication_gates.py` líneas 793-813 para entender cómo se usa
- [ ] Evaluar si el feature "detectar assets ya existentes en sitio del cliente" tiene valor comercial
- [ ] Decisión documentada en un comentario/docstring en publication_gates.py

**Si se decide CREAR**:
- [ ] Crear `modules/asset_generation/site_presence_checker.py` con clase `SitePresenceChecker`
- [ ] Método mínimo: `check_site(url: str, asset_types: list) -> dict`
- [ ] Debe ser importable sin errores desde publication_gates.py
- [ ] Test básico en `tests/asset_generation/test_site_presence_checker.py`

**Si se decide ELIMINAR**:
- [ ] Remover bloque try/except de importación en publication_gates.py
- [ ] Simplificar lógica del gate para no depender de site presence
- [ ] Actualizar docstring del gate eliminando referencias a SitePresenceChecker

### Tarea 2: Limpiar deployment_assistant.md refs
**Objetivo**: Eliminar referencias fantasma a un workflow que nunca existió.

**Archivos afectados**:
- `AGENTS.md` (línea ~52, tabla workflows disponibles)
- `INDICE_DOCUMENTACION.md` (línea ~210)

**Criterios de aceptación**:
- [ ] AGENTS.md ya no lista `deployment_assistant.md` en workflows disponibles
- [ ] INDICE_DOCUMENTACION.md ya no referencia `deployment_assistant.md`
- [ ] Buscar con `search_files` cualquier otra referencia fantasma a deployment_assistant
- [ ] Si `deploy` CLI command existe y es funcional, documentarlo como tal (no como workflow)

### Tarea 3: Validación
**Objetivo**: Asegurar que las eliminaciones no rompen validaciones.

**Comando de validación**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

**Criterios de aceptación**:
- [ ] 4/4 checks pasan
- [ ] Doctor no reporta errores críticos
- [ ] No hay import errors al cargar publication_gates.py

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_site_presence_checker.py (si aplica) | tests/asset_generation/test_site_presence_checker.py | Pasa 3/3 tests mínimos |
| test_publication_gates_import.py | tests/quality_gates/test_publication_gates.py | Import limpio, sin errores |

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**
   - Marcar FASE-SOL2-A como ✅ Completada
   - Fecha: {timestamp}

2. **`06-checklist-implementacion.md`**
   - Estado ✅ en FASE-SOL2-A
   - Iteraciones usadas: {N}

3. **`09-documentacion-post-proyecto.md`**
   - Sección A: `site_presence_checker.py` (si fue creado)
   - Sección E: AGENTS.md, INDICE_DOCUMENTACION.md actualizados

4. **Evidencia**:
   - Guardar diff de cambios: `git diff > evidence/SOL2-A/diff.patch`

## Criterios de Completitud (CHECKLIST)

- [ ] SitePresenceChecker: creado O referencia eliminada limpiamente
- [ ] deployment_assistant.md: ninguna referencia fantasma en codebase
- [ ] Tests pasan (nuevos + existentes sin regresión)
- [ ] run_all_validations.py --quick 4/4
- [ ] dependencias-fases.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
- [ ] Evidencia preservada en evidence/SOL2-A/

## Restricciones

- **NO ejecutar v4complete** en esta fase (es trabajo de código puro)
- **NO modificar ROADMAP.md** (eso es trabajo de RELEASE)
- **NO cambiar lógica de coherence_validator** (eso es FASE-SOL2-B)
- Si se crea SitePresenceChecker, mantenerlo MÍNIMO (MVP), no over-engineering
- Máximo 60 iteraciones del agente

## Prompt de Ejecución

```
Actúa como ingeniero de software enfocado en integridad de sistema.

OBJETIVO: Resolver GAP-A y GAP-B del contexto SOL-2.

CONTEXTO:
- Fase previa: Contexto SOL-2 validado
- publication_gates.py tiene try/except para importar SitePresenceChecker (línea 798) pero el módulo NO EXISTE
- AGENTS.md e INDICE_DOCUMENTACION.md referencian deployment_assistant.md que NO EXISTE

TAREAS:
1. Leer publication_gates.py:793-813 y decidir: ¿Crear SitePresenceChecker o eliminar refs?
2. Ejecutar decisión (código + test mínimo si aplica)
3. Buscar y eliminar todas las referencias a deployment_assistant.md
4. Validar con run_all_validations.py --quick

CRITERIOS:
- No quedan import errors silenciados
- No quedan referencias fantasma
- Tests existentes no regresan

VALIDACIONES:
- run_all_validations.py --quick pasa 4/4
- doctor.py --status sin errores críticos
```
