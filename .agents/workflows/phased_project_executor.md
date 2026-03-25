---
description: Ejecutor de proyectos por fases. Una fase por sesión. Sin excepciones.
version: 2.1.0
---

# Skill: Phased Project Executor

> [!NOTE]
> **Trigger**: "Ejecuta por fases", "Continúa en nueva sesión", "Divide en sprints", "Preserva contexto para siguiente fase", "Trabajo por fases".

## Regla de Sesión Única (OBLIGATORIO)

> [!CAUTION]
> **REGLA MANDATORIA - Sin excepciones**
> Una fase por sesión. No se permite ejecutar múltiples fases en una misma sesión.

**Fases del workflow:**
1. **Preparación** (esta sesión): Crear prompts, checklists, docs para todas las fases
2. **Implementación** (sesión por fase): Cada fase se ejecuta en su propia sesión nueva

**Aplicación:**
- Preparación upfront: En UNA sesión se generan todos los prompts de fase
- Implementación: Cada fase requiere una sesión NUEVA del agente
- Sesión N → prepara fases N+1, N+2, ... (no las ejecuta)
- La sesión de implementación termina cuando el checklist muestra ✅ completo

**Excepciones**: NINGUNA. Esta regla es absoluta.

## Pre-requisitos
- [ ] Proyecto con división clara en fases/sprints/etapas
- [ ] Estructura de directorio `.opencode/plans/` o similar
- [ ] Criterios de aceptación definidos por fase

## Pasos de Ejecución

### 1. Analizar Plan y Detectar Conflictos
Leer el plan maestro:
- Número de fases/sprints
- Dependencias entre fases
- Entregables por fase
- **Conflictos de archivos** (qué archivo modifica cada fase)

**Output**: `dependencias-fases.md`
- Diagrama ASCII de dependencias
- Tabla de conflictos potenciales

### 2. Crear Prompts por Fase
Para cada fase, crear `.opencode/plans/05-prompt-inicio-sesion-fase-{N}.md`

Usar template `.agents/workflows/templates/prompt-fase-template.md`

**Obligatorio en cada prompt:**
- Contexto de fases anteriores
- Tareas específicas de la fase
- **Post-Ejecución** (marcar checklist, actualizar estados)
- **Criterios de Completitud**

**Verificación:**
- [ ] Nombre de archivo coincide con título interno
- [ ] Referencias a fases previas con números correctos
- [ ] Tests base acumulativos correctos

### 3. Actualizar Checklist Maestro
Actualizar `.opencode/plans/06-checklist-implementacion.md`:
- Estado de cada fase (pendiente/en progreso/completada)
- Dependencias entre fases

### 4. Documentación Incremental
**Estrategia**: Documentar durante todo el proyecto, no solo al final.

**Al inicio del proyecto**: Crear `.opencode/plans/09-documentacion-post-proyecto.md` con estructura vacía

**Después de cada fase completada:**
- Sección A: Módulos nuevos
- Sección D: Métricas acumulativas
- Sección E: Archivos afiliados actualizados

### 5. Validación Final de Preparación
Antes de cerrar la sesión de preparación:

```bash
# Verificar numeración de prompts
grep -n "FASE [0-9]" .opencode/plans/05-prompt-inicio-sesion-fase-*.md

# Verificar que todos los archivos de plan existen
ls -la .opencode/plans/
```

**Checklist:**
- [ ] Prompts creados para TODAS las fases
- [ ] Numeración correcta verificada
- [ ] `dependencias-fases.md` generado
- [ ] Checklist maestro actualizado
- [ ] Documentación base creada
- [ ] Sprints sincronizados (si existen)

### 6. Documentación Post-Fase (OBLIGATORIO - Según CONTRIBUTING.md)

Después de completar cada fase, ejecutar el registro de documentación:

**Fuentes:**
- Checklist de documentación: `docs/contributing/documentation_rules.md` §5
- Archivos manuales: `docs/contributing/documentation_rules.md` §8
- Capability contracts: `docs/contributing/capabilities.md` §13

**Comando:**
```bash
python scripts/log_phase_completion.py \
    --fase {FASE-N} \
    --desc "{descripcion de lo implementado}" \
    --archivos-nuevos "{ruta/archivo.py,ruta/test.py}" \
    --archivos-mod "{ruta/existente.py}" \
    --tests "{numero}" \
    --coherence {score}
```

**Ejemplo:**
```bash
python scripts/log_phase_completion.py \
    --fase FASE-12 \
    --desc "Google Travel Scraper integration" \
    --archivos-nuevos "modules/scrapers/google_travel.py,tests/scrapers/test_google_travel.py" \
    --archivos-mod "modules/providers/benchmark_resolver.py" \
    --tests "15" \
    --coherence 0.91
```

**Lo que hace el script:**
1. Registra en `docs/contributing/REGISTRY.md` (automático)
2. Muestra POR_HACER para documentación manual
3. Genera checklist de verificación

**Documentación que se actualiza MANUALMENTE (no con el script):**
| Archivo | Cuando |
|---------|--------|
| `CHANGELOG.md` | Al final del release |
| `GUIA_TECNICA.md` | Si hay cambios arquitectónicos |
| `ROADMAP.md` | Si hay hitos de monetización |
| `.agents/workflows/README.md` | Si se agrega/elimina skill |

**Verificación de Capability Contracts (capabilities.md §13):**
- [ ] Nueva capability tiene punto de invocación
- [ ] Output serializable en to_dict/export/report
- [ ] Matriz de capacidades actualizada

---

## Criterios de Éxito
- [ ] Prompts creados para todas las fases (1 por fase)
- [ ] Checklist maestro con estados
- [ ] `dependencias-fases.md` con conflictos documentados
- [ ] Documentación incremental preparada
- [ ] Estructura lista para que cada fase se ejecute en sesión propia

## Plan de Recuperación
- Sin estructura de planes → crear `.opencode/plans/` automáticamente
- Sin división en fases → proponer estructura estándar (Fase 0-N)
- Prompts muy grandes → dividir en secciones dentro del mismo archivo

## Versiones
- **v2.1.0** (2026-03-23): Agregado Paso 6 - Documentación Post-Fase según CONTRIBUTING.md. Ejecuta log_phase_completion.py y verifica capability contracts.
- **v2.0.0** (2026-03-23): Simplificado — preparación en una sesión, implementación en sesión propia por fase. Elimina TDD Gate, Capability Contract, lecciones extensas.
- **v1.5.0** (2026-03-18): Regla de Sesión Única, TDD Gate
- **v1.0.0** (2026-03-03): Versión inicial

## Ejemplo de Uso

Usuario: "Divide este proyecto de refactorización en fases y prepáralo para ejecutar por sesiones"

La skill debe:
1. Leer plan existente
2. Crear `05-prompt-inicio-sesion-fase-2.md` con especificaciones técnicas completas
3. Crear `05-prompt-inicio-sesion-fase-3.md` (y restantes)
4. Actualizar checklist con estados de fases
5. Crear `09-documentacion-post-proyecto.md` con estructura base
6. Verificar numeración de todos los prompts

**Output de esta sesión:**
```
.opencode/plans/
├── 05-prompt-inicio-sesion-fase-{N}.md    (1 por fase)
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
├── dependencias-fases.md
└── README.md
```

La implementación de cada fase se hace en UNA sesión nueva por fase.
