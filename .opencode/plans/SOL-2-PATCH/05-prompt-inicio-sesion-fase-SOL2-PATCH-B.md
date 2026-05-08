---
description: Prompt de inicio de fase SOL2-PATCH-B — Parcheo de prompts historicos con POST-EJECUCION
version: 1.0.0
---

# FASE-SOL2-PATCH-B: Parcheo de prompts historicos

**ID**: SOL2-PATCH-B
**Objetivo**: Agregar notas POST-EJECUCION a los prompts SOL2-A y SOL2-B para evitar trampas temporales
**Dependencias**: Ninguna (puede ejecutarse en paralelo con PATCH-A)
**Duracion estimada**: 20-30 minutos
**Skill**: `phased_project_executor.md` v2.10.0
**Modo Ejecucion**: DIRECTO (edicion de archivos de plan)

## Contexto

El contexto 07 identifico que los prompts de fase SOL-2-A y SOL-2-B asumen que GAP-A y GAP-B son problemas reales de severidad ALTA. Si un agente futuro re-ejecuta estos prompts sin contexto post-SOL-2:
- SOL-2-A: Perderia iteraciones intentando crear SitePresenceChecker (ya existe) y deployment_assistant.md (ya existe)
- SOL-2-B: Ejecutaria la unificacion de PROPOSAL_SERVICE_TO_ASSET (ya hecha)

**Solucion**: Agregar bloque NOTA POST-EJECUCION al inicio de cada archivo.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| SOL-2-REFACTOR (A-D + RELEASE) | ✅ Completada |
| SOL2-PATCH-B | ⏳ En progreso |

### Base Tecnica Disponible
- `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md`
- `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-B.md`
- Contexto 07: `.opencode/context/07_SOL-2_UNIFIED_VALIDATED_20260507.md`

## Tareas

### T1: Parchear prompt SOL2-A
**Objetivo**: Agregar nota POST-EJECUCION al inicio del prompt.

**Archivo**: `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md`

**Contenido de la nota** (insertar despues del frontmatter YAML, antes del titulo #):
```markdown
> [!IMPORTANT]
> **NOTA POST-EJECUCION (2026-05-07)**
> Esta fase fue completada exitosamente. Los siguientes componentes YA EXISTEN:
> - `SitePresenceChecker` en `modules/asset_generation/site_presence_checker.py` (601 lineas)
> - `deployment_assistant.md` en `.agents/workflows/deployment_assistant.md` (43 lineas)
> Si estas leyendo este prompt en una sesion futura, NO re-crear estos componentes.
> Saltar directamente a la seccion de verificacion o al siguiente paso del plan.
```

**Criterios de aceptacion**:
- [ ] Nota presente al inicio del archivo
- [ ] Fecha correcta (2026-05-07)
- [ ] Referencias de archivo correctas

### T2: Parchear prompt SOL2-B
**Objetivo**: Agregar nota POST-EJECUCION al inicio del prompt.

**Archivo**: `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-B.md`

**Contenido de la nota**:
```markdown
> [!IMPORTANT]
> **NOTA POST-EJECUCION (2026-05-07)**
> Esta fase fue completada exitosamente. `PROPOSAL_SERVICE_TO_ASSET` ya tiene 7 entradas
> incluyendo `"Optimizacion para IA Generativa": "llms_txt"`. La unificacion de baseline
> entre coherence_validator y proposal_asset_alignment_gate ya fue implementada.
> Si estas leyendo este prompt en una sesion futura, NO re-ejecutar la unificacion.
> Verificar directamente que PROPOSAL_SERVICE_TO_ASSET tenga 7 entradas y continuar.
```

**Criterios de aceptacion**:
- [ ] Nota presente al inicio del archivo
- [ ] Fecha correcta
- [ ] Mencion de 7 entradas presente

### T3: Verificar consistencia del plan SOL-2-REFACTOR
**Objetivo**: Revisar los 9 archivos del plan SOL-2-REFACTOR para asegurar que no hay otras trampas temporales.

**Archivos a revisar**:
- `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-*.md` (5 archivos)
- `.opencode/plans/SOL-2-REFACTOR/06-checklist-implementacion.md`
- `.opencode/plans/SOL-2-REFACTOR/09-documentacion-post-proyecto.md`
- `.opencode/plans/SOL-2-REFACTOR/README.md`
- `.opencode/plans/SOL-2-REFACTOR/dependencias-fases.md`

**Criterios de aceptacion**:
- [ ] Ningun prompt sin nota POST-EJECUCION afirma que SitePresenceChecker no existe
- [ ] Ningun prompt sin nota POST-EJECUCION afirma que deployment_assistant.md no existe
- [ ] Ningun prompt recomienda crear PROPOSAL_SERVICE_TO_ASSET desde cero

## Tests Obligatorios

Esta fase no modifica codigo ejecutable — no requiere tests de pytest.

| Verificacion | Metodo | Criterio de Exito |
|--------------|--------|-------------------|
| Nota SOL2-A presente | `grep "NOTA POST-EJECUCION" .opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-A.md` | Match encontrado |
| Nota SOL2-B presente | `grep "NOTA POST-EJECUCION" .opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-B.md` | Match encontrado |
| Consistencia | Revision manual de 9 archivos | Sin trampas temporales |

## Post-Ejecucion (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**:
   - Marcar PATCH-B como ✅ Completada

2. **Actualizar `06-checklist-implementacion.md`**:
   - Marcar tareas de PATCH-B como completadas

3. **Actualizar `09-documentacion-post-proyecto.md`**:
   - Seccion E: marcar archivos de plan historicos como actualizados

## Criterios de Completitud (CHECKLIST)

- [ ] T1: Prompt SOL2-A parcheado con NOTA POST-EJECUCION
- [ ] T2: Prompt SOL2-B parcheado con NOTA POST-EJECUCION
- [ ] T3: Verificacion de consistencia completada
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado

## Restricciones

- **NO modificar codigo fuente** — solo archivos de plan
- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md**
- Maximo 60 iteraciones

## Prompt de Ejecucion

```
Actua como agente de mantenimiento de documentacion de planes.

OBJETIVO: Parchear prompts historicos SOL2-A y SOL2-B con notas POST-EJECUCION.

CONTEXTO:
- Los prompts SOL2-A y SOL2-B asumen problemas que ya fueron resueltos
- Un agente futuro podria perder iteraciones re-ejecutando soluciones ya implementadas
- Contexto 07 documenta que SitePresenceChecker y deployment_assistant.md YA EXISTEN

TAREAS:
1. Insertar NOTA POST-EJECUCION en SOL2-A (SitePresenceChecker + deployment_assistant ya existen)
2. Insertar NOTA POST-EJECUCION en SOL2-B (PROPOSAL_SERVICE_TO_ASSET ya tiene 7 entradas)
3. Verificar consistencia de los 9 archivos del plan SOL-2-REFACTOR

CRITERIOS:
- Ambos prompts tienen nota visible al inicio
- Ningun prompt afirma falsamente que componentes no existen
```
