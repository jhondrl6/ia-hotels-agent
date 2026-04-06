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

> [!TIP]
> **Convenciones de Nomenclatura de Fases**
>
> | Tipo | Formato | Ejemplo | Significado |
> |------|---------|---------|-------------|
> | Iteracion | `FASE-N` | `FASE-12` | Iteration de desarrollo |
> | Feature | `FASE-{LETRA}` | `FASE-A`, `FASE-B` | Sub-fase de un feature (A..Z) |
> | Release | `FASE-RELEASE-X.Y.Z` | `FASE-RELEASE-4.10.0` | **Markers explícito de release** |
>
> **Regla:** Si la fase cambia la versión (nueva release), usar `FASE-RELEASE-X.Y.Z`.
> Esto activa automaticamente el Version Sync Gate.

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

---

#### DONDE: Ubicación en el Workflow

```
FASE completada (checklist muestra ✅)
    │
    └── Paso 6: Documentación Post-Fase ← AQUÍ
               │
               └─→ Ejecutar log_phase_completion.py
```

---

#### CUANDO: Cuándo se Activa

**INMEDIATAMENTE** después de que la fase se considera completa:
- Checklist de la fase muestra ✅ en todos los items
- Tests pasan (si aplica)
- No hay errores pendientes

**NO esperar** a la siguiente sesión. Ejecutar en la misma sesión donde se completó la fase.

---

#### COMO: Comandos Exactos

**Caso 1: Fase de iteración (FASE-N, FASE-A, etc.)**

```bash
# Minimo (registra en REGISTRY nomas)
python scripts/log_phase_completion.py --fase FASE-12 --desc "Descripcion"
```

```bash
# Recomendado (con verificacion de docs manuales)
python scripts/log_phase_completion.py \
    --fase FASE-12 \
    --desc "Google Travel Scraper integration" \
    --archivos-nuevos "modules/scrapers/google_travel.py,tests/scrapers/test_google_travel.py" \
    --archivos-mod "modules/providers/benchmark_resolver.py" \
    --tests "15" \
    --coherence 0.91 \
    --check-manual-docs
```

**Caso 2: Fase de RELEASE (FASE-RELEASE-X.Y.Z)**

```bash
# Convencion: FASE-RELEASE-4.10.0 = release marker
# El script detecta automaticamente que es un release

python scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.10.0 \
    --desc "Release 4.10.0" \
    --archivos-mod "modules/foo.py" \
    --check-manual-docs

# Verificar consistency antes de commit:
python scripts/version_consistency_checker.py
```

**Caso 3: Forzar skip (excepciones)**

```bash
# Solo si hay razon valida: no-aplica, en-release-posterior, etc.
python scripts/log_phase_completion.py \
    --fase FASE-X --desc "..." \
    --check-manual-docs --force-skip-docs --skip-reason "no-aplica"
```

---

#### QUE HACE: Salida del Script

```
1. Registra en REGISTRY.md (automatico)
2. Muestra POR_HACER para documentacion manual
3. DOCUMENTATION AUDIT (automatico si hay --archivos-mod)
4. Version Sync Gate (automatico si fase es FASE-RELEASE-X.Y.Z)
5. Checklist final en pantalla
```

---

#### VERSION SYNC GATE: Como Saber si Fallo

```
[VERSION GATE] Release: 4.10.0

  (!) CHANGELOG no tiene entrada [4.10.0]
      CHANGELOG dice: 4.9.0

  ACCION: Crear entrada en CHANGELOG.md antes de continuar
```

Si ves esto → El commit sera bloqueado por el pre-commit hook.

---

#### DOCUMENTATION AUDIT: Como Saber si Hay Gaps

```
DOCUMENTATION AUDIT - Documentacion Huérfana

  [GAP] GUIA_TECNICA.md
        Archivos de codigo que REQUIEREN actualizacion:
          - modules/asset_generation/conditional_generator.py

  Para resolver: Editar manualmente y agregar referencia a la fase
```

Si ves [GAP] → Editar GUIA_TECNICA.md y agregar la fase.

---

#### Checklist Post-Ejecucion

Después de ejecutar `log_phase_completion.py`, verificar:

- [ ] REGISTRY.md actualizado (nueva entrada visible)
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
- [ ] Si fue RELEASE: VERSION SYNC GATE pasó (no hubo `(!)`)
- [ ] CHANGELOG.md actualizado (si fue release)
- [ ] `git add -A && git commit`

---

### Paso 7: Actualizacion de Documentacion Oficial del Repositorio

**Cuándo**: Una vez completadas TODAS las fases de implementación del proyecto. No se ejecuta por fase individual — es el cierre del ciclo.

**Qué hace**: Ejecuta el procedimiento definido en docs/CONTRIBUTING.md §55-163 (sección "Trigger del Usuario: Actualizar documentacion oficial del repositorio").

**Ejecutar en orden**:
```bash
# Contributing §61-67: Diagnóstico
python scripts/version_consistency_checker.py
python main.py --doctor

# Contributing §70-76: Sync automático VERSION.yaml → 6 headers
python scripts/sync_versions.py

# Contributing §78-85: Verificar CHANGELOG.md (manual)
# Contributing §86-93: Verificar GUIA_TECNICA.md (manual)
# Contributing §94-106: Verificar skills/workflows (manual)
# Contributing §107-111: Regenerar SYSTEM_STATUS.md
# Contributing §113-128: Verificar symlink + validación pre-commit
```

**Qué NO hace**: NO modifica ROADMAP.md, NO edita código fuente, NO ejecuta `v4complete`.

**Dónde está el detalle completo**: docs/CONTRIBUTING.md §55-163 — el procedimiento está documentado ahí. Este paso solo orquesta su ejecución.

**Checklist:**
- [ ] docs/CONTRIBUTING.md §55-163 ejecutado completo
- [ ] version_consistency_checker.py pasó sin discrepancias
- [ ] CHANGELOG.md y GUIA_TECNICA.md verificados/actualizados
- [ ] SYSTEM_STATUS.md regenerado
- [ ] Symlink .agent/workflows → .agents/workflows verificado
- [ ] git diff --stat muestra todos los archivos modificados

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
- **v2.3.0** (2026-03-26): Version Sync Gate + Documentation Audit + FASE-RELEASE auto-detect. Convencion FASE-RELEASE-X.Y.Z para releases. Pre-commit hook para consistencia de versiones.
- **v2.2.0** (2026-03-25): Enforcement de docs manuales --check-manual-docs. Si hay cambios arquitectonicos en archivos de REQUIRE_ArchitectURAL_CHANGE (conditional_generator.py, faq_gen.py, voice_guide.py, aeo_kpis.py, etc.) y GUIA_TECNICA.md no menciona la fase, el script FAIL. Uso --force-skip-docs --skip-reason para excepciones.
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
