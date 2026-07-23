---
description: Ejecutor de proyectos por fases. Una fase por sesión. Sin excepciones. Máximo 60 iteraciones por fase. Ejecutado por agentes AI.
version: v2.12.0
---

# Skill: Phased Project Executor

> [!NOTE]
> **Trigger**: "Ejecuta por fases", "Continúa en nueva sesión", "Divide en sprints", "Preserva contexto para siguiente fase", "Trabajo por fases".

## Regla de Sesión Única (OBLIGATORIO)

> [!CAUTION]
> **REGLAS MANDATORIAS - Sin excepciones**
>
> **R1: Una fase por sesión.** No se permite ejecutar múltiples fases en una misma sesión.
>
> **R2: Máximo 60 iteraciones del agente por fase.** Si se alcanza el límite, la fase se marca como incompleta y DEBE retomarse en una nueva sesión fresca. No se permite exceder este límite bajo ningún pretexto (ni "falta poco", ni "ya casi termino").

## Regla de Scope de Fase (OBLIGATORIO — Al Crear el Plan)

> [!CAUTION]
> **R3: Una fase no puede contener mas de UN comando de larga duracion (v4complete, v4audit, scraping, etc.) NI mas de 4 tareas de investigacion/fix counting.**
>
> Si una fase requiere investigar+implementar+ejecutar+verificar+documentar, se DIVIDE en sub-fases: `FASE-X-A`, `FASE-X-B`, etc.

#### Como evaluar si una fase es demasiado grande

Al crear un prompt de fase, el orquestador debe responder:

```
TAREAS DE LA FASE:
  [ ] Investigacion de codigo existente
  [ ] Implementar fix / desarrollo nuevo
  [ ] Ejecutar comando de larga duracion (v4complete, v4audit, etc.)
  [ ] Verificar output del comando contra criterios
  [ ] Documentacion (log_phase + docs cascade)

CONTADOR:
  - Cada [ ] = 1 tarea
  - v4complete = 1 tarea + 1 comando largo
  - Total permitido por fase: maximo 4 tareas + 0 comandos largos
           O: maximo 3 tareas + 1 comando largo
```

#### Ejemplos de Division

| FASE demasiado grande | FASE bien acotada |
|------------------------|------------------|
| Investigar 5 hallazgos + Fix 5 hallazgos + v4complete + Verificar + Docs | FASE-X-A: Investigar + Fix |
| Fix 5 hallazgos + v4complete + Verificar 5 fixes + Docs | FASE-X-B: v4complete + Verificar |
| Implementar modulo + Testear + Integrar + v4audit + Docs | FASE-X-A: Implementar + Testear |
| | FASE-X-B: Integrar + v4audit |
| | FASE-X-C: Docs cascade |

#### Regla de Decision para el Orquestador

```
SI la fase tiene:
  - Mas de 4 tareas de investigacion/fix
  - O 1+ comando(s) de larga duracion (v4complete, etc.)
  - O combinacion de ambos que sume > 4 items de la lista

ENTONCES:
  → Dividir en FASE-X-A (investigacion/fix),
             FASE-X-B (ejecucion/verificacion),
             FASE-X-C (docs) segun corresponda
  → Cada sub-fase recibe su propio 05-prompt-inicio-sesion-fase-X-Y.md
  → Las sub-fases se ejecutan en sesiones separadas
```

#### Señales de Alerta al Planificar

- "Esta fase toma 2-3 horas" → probablemente necesita division
- "5 hallazgos para corregir" → dividir: A=investigacion, B=fixes, C=verificacion
- "Ejecutar v4complete y verificar los 5 hallazgos" → v4complete solo en su propia sub-fase
- "Docs cascade al final" → docs son su propia sub-fase

> [!WARNING]
> **El orquestador que crea fases demasiado grandes es responsable del agotamiento de las sesiones siguientes.** La regla R2 (60 iteraciones max) protege contra ejecucion excesiva, pero la prevencion empieza en el diseño del plan.

> [!TIP]
> **Convenciones de Nomenclatura de Fases**
>
> | Tipo | Formato | Ejemplo | Significado |
> |------|---------|---------|-------------|
> | Iteracion | `FASE-N` | `FASE-12` | Iteration de desarrollo |
> | Feature | `FASE-{LETRA}` | `FASE-A`, `FASE-B` | Sub-fase de un feature (A..Z) |
> | Release | `FASE-RELEASE-X.Y.Z` | `FASE-RELEASE-4.10.0` | Fase ejecutable de cierre + documentación (sesión propia) |
>
> **Regla:** Si la fase cambia la versión (nueva release), usar `FASE-RELEASE-X.Y.Z`.
> Esto activa automaticamente el Version Sync Gate.

**Fases del workflow (3 etapas):**

| Etapa | Tipo de fase | Sesiones | Descripción |
|-------|-------------|----------|-------------|
| 1. Preparación | (orquestación) | 1 sesión | Crear todos los prompts, checklists, docs para todas las fases |
| 2. Implementación | `FASE-{N\|LETRA}` | N sesiones | Cada fase de código en su propia sesión nueva de agente |
| 3. Cierre / Release | `FASE-RELEASE-X.Y.Z` | 1 sesión | Documentación oficial, version bump, validaciones finales |

**Regla de dependencia:** `FASE-RELEASE-X.Y.Z` solo se ejecuta cuando TODAS las fases de implementación (etapa 2) están completadas (`✅`).

**Aplicación:**
- **Etapa 1 (Preparación):** En UNA sesión, Hermes (orquestador) genera todos los prompts de fase, incluyendo el de RELEASE
- **Etapa 2 (Implementación):** Cada fase requiere una sesión NUEVA del agente. El agente lee su `05-prompt-inicio-sesion-fase-{X}.md` y ejecuta las tareas de código
- **Etapa 3 (RELEASE):** Una sesión NUEVA del agente. El agente ejecuta `05-prompt-inicio-sesion-fase-RELEASE.md`. Tareas: version bump, sync, CHANGELOG, GUIA_TECNICA, validaciones, log. **NO modifica código fuente.**
- La sesión termina cuando el checklist de la fase muestra ✅ completo

## Modelo de Ejecución: Agentes AI

> [!IMPORTANT]
> **Este workflow es ejecutado por agentes AI** (Hermes, subagentes vía `delegate_task`), no por humanos.
>
> Cada prompt de fase (`05-prompt-inicio-sesion-fase-*.md`) es una **instrucción completa para un agente** en una sesión fresca. El agente:
> 1. Lee el prompt al inicio de la sesión
> 2. Planifica la ejecución de las tareas
> 3. Ejecuta — el modo de ejecución lo determinan las reglas de decisión más abajo:
>    - Código/tests puro → agente principal DIRECTO (§Regla código+tests)
>    - Comandos externos (v4complete, scraping) → §Regla v4complete
>    - Trabajo paralelo (2+ tracks) → subagentes vía `delegate_task`
>    - **NO usar subagente fuera de estos casos.**
> 4. Verifica criterios de completitud contra el checklist
> 5. Ejecuta `log_phase_completion.py` al finalizar, luego actualiza `09-documentacion-post-proyecto.md` con los datos de la fase
>
> **Implicaciones del modelo agente:**
> - Las "iteraciones" de R2 son **tool calls del agente** — no pasos humanos
> - El agente NO debe pedir confirmación para cada paso; el prompt es su mandato completo
> - Subagentes (`delegate_task`) pueden usarse para trabajo paralelo dentro de una fase, pero el total de iteraciones de la sesión no debe exceder 60
> - La fase termina cuando el checklist muestra ✅, no cuando "se acabó el tiempo"
> - **Orquestación**: La etapa de Preparación la ejecuta Hermes como orquestador. Las etapas de Implementación/RELEASE las ejecuta un agente nuevo en cada sesión.

### Regla de Iteraciones para Comandos de Larga Duración

> [!CAUTION]
> **GUIA CRITICA: 60 iteraciones vs. comandos que duran minutos**
>
> `v4complete` es un comando que tarda 5-10 minutos en ejecutarse (scraping + APIs + generación de documentos + assets). Aunque `terminal(..., timeout=600)` cuenta como **1 tool call**, el comando consume tiempo real de pared, no tiempo de iteraciones del agente.
>
> **El agente debe planificar su presupuesto de iteraciones ANTES de invocar comandos largos.**

#### Calculo del Presupuesto de Iteraciones

```
Presupuesto total: 60 iteraciones

Gastos fijos por fase:
  - Leer plan y verificar estado previo: ~3 iteraciones
  - Investigar codigo/archivos: ~5-15 iteraciones
  - Ejecutar log_phase_completion.py + docs cascade: ~10 iteraciones
  - Actualizar plan al finalizar: ~5 iteraciones
  - run_all_validations.py: ~3 iteraciones
  Total fijo: ~26-36 iteraciones

Margen para trabajo especifico de la fase: 24-34 iteraciones
```

#### Regla de Desicion: ejecutar v4complete directamente o via subagente?

```
SI (investigacion + verificacion + docs) < 30 iteraciones restantes:
    → Ejecutar v4complete DIRECTAMENTE con terminal(timeout=600)
    → Usar notify_on_complete=True para no bloquear
    → Después de verificar output y hacer docs cascade

SI no:
    → Spawn subagent via delegate_task(timeout=900, notify_on_complete=True)
    → El subagent ejecuta v4complete completo
    → El agente parent usa sus iteraciones solo en verificacion + docs
```

#### Regla de Decisión: ejecutar código+tests directamente o vía subagente?

> [!IMPORTANT]
> **Para fases de implementación pura (investigación/fix/código/tests), la ejecución directa del agente principal es más eficiente que delegar a subagente.** El overhead de spawn (contexto, toolsets limitados, timeout) degrada fases que no tienen comandos de larga duración. Esta regla surgió del aprendizaje de FIN-3 (sesión 20260504_123434_49e7de): subagente agotado a 600s/37 tool calls para tareas que el agente principal habría completado en menos iteraciones sin overhead.

```
SI la fase tiene SOLO tareas de investigacion/fix/implementacion de codigo:
    → Ejecutar DIRECTAMENTE con el agente principal
    → Herramientas principales: terminal, file, execute_code
    → Budget: ~30-40 iteraciones para trabajo + ~20 para verificacion/docs
    → Este budget reemplaza el calculo generico de "Calculo del Presupuesto"
      (seccion anterior) — la ejecucion directa elimina el overhead de spawn

SI la fase tiene 1+ comandos externos (v4complete, scraping, apis):
    → Regla de v4complete aplica (seccion anterior ↑)

SI la fase tiene trabajo paralelo independiente (2+ tracks separadas):
    → Subagente(s) para trabajo paralelo
    → Agente principal para coordinacion + docs

SI la fase requiere imports del proyecto (tests, integracion) Y el proyecto
   usa venv Windows accedido desde WSL:
    → Ejecutar DIRECTAMENTE con el agente principal
    → Invocar el Python del venv del proyecto via subprocess.run():
       ./venv/Scripts/python.exe -m pytest tests/...
    → NO delegar a subagentes: corren en WSL Linux sin acceso al venv
       Windows, imports como bs4/selenium fallan
    → Esta regla PREVALECE sobre la regla de trabajo paralelo (branch 3)
    → Causa raíz: subagente WSL no comparte el Python environment del
       venv Windows; los imports del proyecto fallan y el subagente
       consume iteraciones intentando resolver dependencias inexistentes
    → Lección: FASE-4 BUGS-ONBOARDING-ADR (2026-07-22) — subagente
       atascado en imports bs4/selenium, ~40 iteraciones perdidas
```

#### Protocolo de Subagente para v4complete

Cuando se usa `delegate_task` para ejecutar `v4complete`:

```
1. En el context del subagente, incluir:
   - URL del hotel
   - Comando exacto: ./venv/Scripts/python.exe main.py v4complete --url {url}
   - Expected output: diagnostico, propuesta, assets, coherence >= 0.80

2. En el parent agent, usar:
   delegate_task(
     goal="Ejecutar v4complete para {hotel}...",
     context="...",
     timeout=900,  # 15 minutos — v4complete necesita 5-10 min
     notify_on_complete=True,
     toolsets=["terminal"]
   )

3. Cuando el subagente completa:
   → Parent agent verifica que los archivos existen
   → Agent generation_report y coherence_validation
   → Continua con docs cascade si todo OK
```

> [!WARNING]
> **NUNCA ejecutar `v4complete` sin `notify_on_complete=True` o sin subagente.**
> Si el agente parent se agota antes de que `v4complete` termine, el output
> se genera pero la verificacion/docs no se ejecutan — la fase queda incompleta.

#### Protocolo de Evidencia Proactiva (OBLIGATORIO)

> [!CAUTION]
> **Inmediatamente despues de que `v4complete` genera output**, antes de
> cualquier verificacion o investigacion adicional:
>
> 1. Copiar los archivos criticos a `evidence/{fase-id}/`:
>    ```bash
>    mkdir -p evidence/{fase-id}
>    cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/{fase-id}/
>    cp output/v4_complete/02_PROPUESTA_*.md evidence/{fase-id}/
>    cp output/v4_complete/{hotel_id}/v4_audit/*.json evidence/{fase-id}/
>    ```
> 2. **Esto es OBLIGATORIO sin importar cuanto tiempo quede en el presupuesto de iteraciones.**
>    Si el agente se agota despues, la evidencia ya esta a salvo para la siguiente sesion.
> 3. Solo despues de guardar evidencia, continuar con verificacion/docs cascade.

### Cierre Obligatorio de Sesion (SIEMPRE — aunque la fase no haya completado)

> [!IMPORTANT]
> **Al terminar la sesion (completada o no), SIEMPRE ejecutar en orden:**
>
> 1. **Guardar evidencia** (si hay output de v4complete): ejecutar el bloque bash del **Protocolo de Evidencia Proactiva** (seccion anterior §Protocolo-Evidencia-Proactiva)
> 2. **Actualizar el plan de fase** con estado real:
>    - Si completo: marcar todos los items del checklist como ✅
>    - Si incompleto: marcar como `⏳ INCOMPLETA` con checkpoint y que falta
> 3. **Solo entonces** cerrar la sesion.

**Esta regla no tiene excepciones.** Aunque la sesion termine en iteracion 1 y no haya hecho nada, el plan debe reflejar ese estado.

### Recuperacion de Agotamiento (60 iteraciones o timeout de subagente)

Cuando la fase no completa por agotamiento:

```
1. Actualizar el plan de fase (.opencode/plans/05-prompt-inicio-sesion-fase-X.md):
   - Estado: "⏳ INCOMPLETA — agotamiento en iteracion Y"
   - Ultimo checkpoint: describir que se habia completado
   - Que falta: enumerar tareas pendientes
   - Timestamp de la sesion

2. Guardar evidencia en evidence/{fase-id}/:
   - Copiar cualquier output generado hasta el momento
   - Copiar diagnosticos/propuestas/JSONs aunque esten incompletos

3. Nueva sesion:
   - Leer estado desde el plan actualizado
   - Continuar desde el checkpoint
   - NO re-ejecutar lo que ya se ejecuto correctamente
```

#### Síntomas de Agotamiento de Subagente

| Sintoma | Causa | Accion |
|---------|-------|--------|
| Subagente retorna sin output | Timeout 600s insuficiente | Re-spawn con delegate_task y timeout=900 |
| v4complete nunca termina de generar | API rate limits / network | Verificar logs, retry con backoff |
| Agent parent agota 60 iteraciones antes de v4complete | Presupuesto mal calculado | Dividir: subagente para v4complete |
| Docs cascade no se ejecuta post-v4complete | Agent se agoto al final | Guardar evidencia ANTES, docs en sesion separada |

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

**Obligatorio en cada prompt (segun CONTRIBUTING §Flujo-Post-Fase):**
- Contexto de fases anteriores
- Tareas específicas de la fase
- Seccion de documentacion post-fase (editar CHANGELOG, GUIA_TECNICA, y acumular en 09-documentacion-post-proyecto.md)
- **Post-Ejecución** (marcar checklist, actualizar estados)
- **Criterios de Completitud**
- **Restricciones** (mínimo: máximo 60 iteraciones; según la fase: no modificar ROADMAP.md, no ejecutar v4complete, etc.)

**Verificación:**
- [ ] Nombre de archivo coincide con título interno
- [ ] Referencias a fases previas con números correctos
- [ ] Tests base acumulativos correctos

### 2.5. Verificación Pre-Creación de Prompts (OBLIGATORIO — Anti-Deuda Acumulativa)

> [!CAUTION]
> **REGLA CRÍTICA**: Antes de crear/codificar los prompts de fase, el orquestador DEBE verificar que cada fase incluye `log_phase_completion.py` al final de su ejecución. NO delegar esto a FASE-RELEASE.

**Checklist de verificación obligatoria:**

```
□ FASE-1 a FASE-N (impl): Cada prompt termina con:
    ./venv/Scripts/python.exe scripts/log_phase_completion.py \
        --fase FASE-X --desc "..." \
        --archivos-mod "..." --tests "N" --check-manual-docs

□ FASE-RELEASE: NO registra fases anteriores. Solo sincroniza y valida.

□ Si el plan muestra T1 de FASE-RELEASE = "registrar FASE-1 a FASE-5" → ERROR.
  Las fases 1-5 DEBEN registrarse a sí mismas al completar.

□ Si no existe prompt-fase-template.md → crear uno antes de planificar fases.
```

**Error típico que este paso previene:**

```
Planificador diseña:
  FASE-1: T1=investigar, T2=fix, T3=tests
  FASE-2: T1=investigar, T2=fix, T3=tests
  FASE-RELEASE: T1=registrar FASE-1, T2=registrar FASE-2, ..., T5=registrar FASE-5, T6=version bump

Resultado: Deuda de 5 registros acumulada en RELEASE.
          Si RELEASE falla, las fases quedan "completadas" sin registro.
```

**Acción correctiva si se detecta el error:**

```
Si el plan tiene "T1 de FASE-RELEASE = registrar FASE-1 a FASE-5":
  → Reestructurar: Cada fase de implementación ejecuta log_phase_completion.py al terminar.
  → FASE-RELEASE solo hace: sync_versions, CHANGELOG, GUIA_TECNICA, validaciones.
  → Regenerar los prompts de fase con la sección post-ejecución incluida.
```

### 3. Actualizar Checklist Maestro
Actualizar `.opencode/plans/06-checklist-implementacion.md`:
- Estado de cada fase (pendiente/en progreso/completada)
- Dependencias entre fases

### 4. Documentación Incremental
**Estrategia**: Documentar durante todo el proyecto, no solo al final.

**Al inicio del proyecto**: Crear `.opencode/plans/09-documentacion-post-proyecto.md` con estructura vacía.

**Después de cada fase completada**, editar directamente CHANGELOG.md y GUIA_TECNICA.md con los cambios de esa fase (segun template §6). La acumulacion en 09-documentacion-post-proyecto.md es un backup de datos para FASE-RELEASE:

- Sección A: Módulos nuevos
- Sección B: Funcionalidades nuevas
- Sección D: Métricas acumulativas
- Sección E: Archivos afiliados actualizados

**Estructura concreta de 09-documentacion-post-proyecto.md:**

```markdown
# Documentación Post-Proyecto

## Sección A: Módulos Nuevos
| Módulo | Archivos | Descripción | Fase |

## Sección B: Funcionalidades Nuevas
| Feature | Módulo | Descripción | Fase |

## Sección D: Métricas Acumulativas
| Métrica | Valor | Fase |

## Sección E: Archivos Afiliados Actualizados
| Archivo | Cambio | Fase |
```

Cada fase completa su columna "Fase". FASE-RELEASE usa los datos acumulados para generar CHANGELOG y GUIA_TECNICA oficiales.

---

### 4.5. Ejecución de Plan de Documentación (OBLIGATORIO)

> [!CAUTION]
> **REGLA MANDATORIA**: Cuando se ejecute un plan de documentación (como `09-documentacion-post-proyecto.md`), SE DEBE seguir este procedimiento. NO ejecutar el plan directamente sin estas validaciones.

#### Flujo de Ejecución

```
Plan de documentación (09-documentacion-post-proyecto.md)
    │
    ├── Paso 4.5.1: Ejecutar log_phase_completion.py por cada fase
    │   └── Registrar en REGISTRY.md (automático)
    │
    ├── Paso 4.5.2: Ejecutar sync_versions.py
    │   └── Sincronizar VERSION.yaml → 6 archivos
    │
    ├── Paso 4.5.3: Validar CHANGELOG.md formato
    │   └── Verificar secciones requeridas por CONTRIBUTING.md
    │
    ├── Paso 4.5.4: Validar GUIA_TECNICA.md
    │   └── Verificar notas técnicas por fase
    │
    └── Paso 4.5.5: Validación final
        └── run_all_validations.py --quick
```

#### Paso 4.5.1: Registrar Fases en REGISTRY.md

Para cada fase mencionada en el plan, ejecutar:

```bash
# Ejemplo: Registrar FASE-GEO-BRIDGE
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-GEO-BRIDGE \
    --desc "Bridge enrichment geo_enriched → delivery" \
    --archivos-nuevos "modules/asset_generation/geo_enriched_bridge.py,tests/asset_generation/test_geo_enriched_bridge.py" \
    --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py" \
    --tests "13" \
    --check-manual-docs
```

**Regla**: Ejecutar UNA vez por cada fase documentada en el plan.

#### Paso 4.5.2: Sincronizar Versiones

```bash
# Sincronizar VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md
./venv/Scripts/python.exe scripts/sync_versions.py

# Verificar sincronización
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

#### Paso 4.5.3: Validar CHANGELOG.md

Verificar que la entrada de CHANGELOG tenga el formato requerido por `docs/CONTRIBUTING.md §Verificar-CHANGELOG`:

```markdown
## [X.Y.Z] - Titulo descriptivo — YYYY-MM-DD

### Objetivo
{Descripcion breve del cambio}

### Cambios Implementados
- Descripción de cambios realizados

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|

### Tests
- N tests nuevos, 0 regresiones
```

**Checklist CHANGELOG:**
- [ ] Entrada `[X.Y.Z]` existe
- [ ] Tiene sección `### Objetivo`
- [ ] Tiene sección `### Cambios Implementados`
- [ ] Tiene sección `### Archivos Nuevos` (si aplica)
- [ ] Tiene sección `### Archivos Modificados` (si aplica)
- [ ] Tiene sección `### Tests`
- [ ] No hay entradas duplicadas

#### Paso 4.5.4: Validar GUIA_TECNICA.md

Verificar que `docs/GUIA_TECNICA.md` tenga nota técnica para cada fase:

**Checklist GUIA_TECNICA:**
- [ ] Cada fase tiene una sección "Notas de Cambios vX.Y.Z"
- [ ] Incluye módulos afectados
- [ ] Incluye problema/solución
- [ ] Incluye backwards compatibility
- [ ] Incluye tests (si aplica)

#### Paso 4.5.5: Validación Final

```bash
# Ejecutar todas las validaciones
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificar estado del sistema
./venv/Scripts/python.exe scripts/doctor.py --status

# Regenerar DOMAIN_PRIMER (al cerrar cada fase de implementacion)
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer

# Verificar DOMAIN_PRIMER (context check, solo en FASE-RELEASE)
./venv/Scripts/python.exe scripts/doctor.py --context
```

**Checklist Final:**
- [ ] `run_all_validations.py --quick` pasa (4/4)
- [ ] `doctor.py --status` ejecutado sin errores
- [ ] `version_consistency_checker.py` pasa
- [ ] `sync_versions.py` ejecutado
- [ ] Todos los archivos de documentación actualizados

#### Ejemplo Completo de Ejecución

```bash
# 1. Registrar cada fase del plan
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-GEO-BRIDGE --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-CONF-GATE --desc "..." --check-manual-docs
# ... repetir para cada fase

# 2. Sincronizar versiones
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. Verificar consistencia
./venv/Scripts/python.exe scripts/version_consistency_checker.py

# 4. Validar documentación manual
# Verificar CHANGELOG.md tiene formato correcto
# Verificar GUIA_TECNICA.md tiene notas técnicas

# 5. Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

#### Checklist de Completitud del Plan de Documentación

Después de ejecutar el plan, verificar:

| Verificación | Comando | Estado |
|--------------|---------|--------|
| Fases registradas en REGISTRY.md | `grep "## FASE-" docs/contributing/REGISTRY.md` | [ ] |
| Versiones sincronizadas | `scripts/sync_versions.py` | [ ] |
| CHANGELOG formato correcto | Manual: verificar secciones | [ ] |
| GUIA_TECNICA actualizada | Manual: verificar notas técnicas | [ ] |
| Validaciones pasan | `scripts/run_all_validations.py --quick` | [ ] |
| Doctor sin errores | `scripts/doctor.py --status` | [ ] |

---

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
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-12 --desc "Descripcion"
```

```bash
# Recomendado (con verificacion de docs manuales)
./venv/Scripts/python.exe scripts/log_phase_completion.py \
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

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.10.0 \
    --desc "Release 4.10.0" \
    --archivos-mod "modules/foo.py" \
    --check-manual-docs

# Verificar consistency antes de commit:
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

**Caso 3: Forzar skip (excepciones)**

```bash
# Solo si hay razon valida: no-aplica, en-release-posterior, etc.
./venv/Scripts/python.exe scripts/log_phase_completion.py \
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

## Estandares Compartidos (CONTRIBUTING §Contrato-con-Executor)

Los siguientes estandares aplican a TODOS los documentos del workflow. La fuente canonica es `docs/CONTRIBUTING.md`.

| Estandar | Valor | Referencia |
|----------|-------|------------|
| **Python path (WSL)** | `./venv/Scripts/python.exe` | CONTRIBUTING §Reglas-Contractuales |
| **CHANGELOG heading** | `## [X.Y.Z] - Titulo — YYYY-MM-DD` | CONTRIBUTING §Formato-CHANGELOG |
| **Version header** | `version: vX.Y.Z` (con prefijo `v`) | CONTRIBUTING §Reglas-Contractuales |
| **DOMAIN_PRIMER** | Regenerar al cerrar cada fase (`--regenerate-domain-primer`) | CONTRIBUTING §Paso-5b-DOMAIN-PRIMER |
| **Template** | Fuente de verdad para docs post-fase | Template §6 |
| **Referencias** | Siempre §Section-Name, nunca §NN-MM | CONTRIBUTING §Secciones-Nominativas |

---

### Paso 7: FASE-RELEASE — Cierre y Documentación Oficial del Repositorio

> [!NOTE]
> **Este paso ES la FASE-RELEASE-X.Y.Z.** Se ejecuta como una fase más, en su propia sesión de agente, usando su prompt `05-prompt-inicio-sesion-fase-RELEASE.md`.
> La diferencia con las fases de implementación: NO modifica código fuente, solo documentación y validaciones.

**Cuando**: Una vez completadas TODAS las fases de implementación (etapa 2). El agente ejecuta esta fase en una sesión nueva. **Es la última fase del proyecto.**

**Fuente de verdad**: `docs/CONTRIBUTING.md §Trigger-Documentacion-Oficial`. Los pasos E1-E8 abajo son la transcripción operativa de esa sección. Si CONTRIBUTING.md cambia, este paso se actualiza para reflejarlo.

**Que NO hace**: NO modifica ROADMAP.md, NO edita código fuente, NO ejecuta `v4complete`.

> [!TIP]
> **FASE-RELEASE es delegable a subagente.** A diferencia de las fases de implementación que pueden requerir imports del proyecto, FASE-RELEASE solo edita YAML/MD y ejecuta scripts (`sync_versions.py`, `run_all_validations.py`, `doctor.py`). Si el agente principal tiene presupuesto limitado de iteraciones, puede delegar FASE-RELEASE a un subagente con `delegate_task`. Confirmado en BUGS-ONBOARDING-ADR (2026-07-22): 18 tool calls, ~4 minutos, sin imports del proyecto.

---

#### E1. Diagnostico Inicial (CONTRIBUTING §Paso-1-Diagnostico)

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores criticos

#### E2. Sincronizacion Automatica (CONTRIBUTING §Paso-2-Sync-Automatico)

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

Sincroniza VERSION.yaml → 6 archivos: AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md

- [ ] sync_versions.py ejecutado sin errores

#### E3. CHANGELOG.md (CONTRIBUTING §Verificar-CHANGELOG, MANUAL)

Formato segun `docs/contributing/documentation_rules.md §Formato-CHANGELOG`:

```markdown
## [X.Y.Z] - Titulo descriptivo — YYYY-MM-DD

### Objetivo
{Descripcion breve}

### Cambios Implementados
- `ruta/archivo.py` - Descripcion del cambio

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|

### Tests
- N tests en `test_xxx.py`
```

**Regla de validacion-only**: Si la fase NO modifica codigo (solo validacion/documentacion), NO crear entrada `[X.Y.Z+1]`. Agregar como subsection dentro de la version existente.

- [ ] CHANGELOG.md tiene entrada para la version actual
- [ ] No hay entradas duplicadas
- [ ] CHANGELOG describe archivos nuevos y modificados de cada fase

#### E4. GUIA_TECNICA.md (CONTRIBUTING §Paso-4-Verificar-GUIA, MANUAL)

Agregar seccion "Notas de Cambios vX.Y.Z" con:

| Campo requerido | Contenido |
|----------------|-----------|
| Modulos afectados | Lista de modulos tocados por las fases |
| Problema | Que estaba roto o incorrecto |
| Solucion | Que se cambio y por que |
| Backwards compatibility | Si la API publica cambia o no |

- [ ] GUIA_TECNICA.md tiene nota tecnica para las fases del proyecto
- [ ] Nota incluye modulos afectados, problema/solucion, backwards compatibility

#### E5. Skills/Workflows (CONTRIBUTING §Paso-5-Skills-Workflows, MANUAL)

```bash
ls -la .agents/workflows/*.md
```

- [ ] Todos los .md en .agents/workflows/ listados en .agents/workflows/README.md
- [ ] No hay skills huerfanos

#### E6. Regenerar SYSTEM_STATUS.md (CONTRIBUTING §Paso-6-SYSTEM-STATUS)

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [ ] SYSTEM_STATUS.md regenerado con version actual

#### E7. Regenerar DOMAIN_PRIMER.md (CONTRIBUTING §Paso-5b-DOMAIN-PRIMER)

Al cerrar cada fase de implementacion, regenerar el Domain Primer:

```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

Solo en FASE-RELEASE (cierre final del proyecto):

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] DOMAIN_PRIMER.md regenerado con modulos actuales
- [ ] Todo modulo en `modules/` documentado
- [ ] Archivo regenerable automaticamente (no editar manualmente)

#### E8. Symlink + Validacion Final (CONTRIBUTING §Paso-7-8-Symlink-Validacion)

```bash
ls -la .agent/workflows    # Debe mostrar → .agents/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

- [ ] Symlink .agent/workflows → .agents/workflows intacto
- [ ] run_all_validations.py --quick pasa sin errores
- [ ] git diff --stat muestra todos los archivos modificados

---

## Criterios de Éxito
- [ ] Prompts creados para todas las fases de implementación (1 por fase)
- [ ] Prompt creado para FASE-RELEASE (si hay version bump)
- [ ] Checklist maestro con estados de todas las fases (incluyendo RELEASE)
- [ ] `dependencias-fases.md` con conflictos documentados y dependencia → RELEASE
- [ ] Documentación incremental preparada
- [ ] Estructura lista para que cada fase se ejecute en sesión propia de agente

## Plan de Recuperación
- Sin estructura de planes → crear `.opencode/plans/` automáticamente
- Sin división en fases → proponer estructura estándar (Fase 0-N) + FASE-RELEASE
- Prompts muy grandes → dividir en secciones dentro del mismo archivo
- **Límite de 60 iteraciones alcanzado** → marcar fase como `INCOMPLETA`, documentar progreso parcial en `dependencias-fases.md`, retomar en nueva sesión fresca
- Fase retomada (INCOMPLETA) → leer estado de `dependencias-fases.md`, continuar desde donde se dejó
- **FASE-RELEASE ejecutada sin implementaciones completadas** → abortar; verificar `dependencias-fases.md` que todas las fases previas estén en `✅`

## Versiones
- **v2.12.0** (2026-07-22): GAP 1 — Nueva branch 4 en Regla de Decisión código+tests: proyectos con venv Windows accedidos desde WSL no deben delegar tests a subagentes (causa raíz: subagente WSL no puede importar dependencias del venv Windows como bs4/selenium; lección de FASE-4 BUGS-ONBOARDING-ADR, ~40 iteraciones perdidas). GAP 2 — Nota [!TIP] en Paso 7: FASE-RELEASE es delegable a subagente (solo edita YAML/MD + scripts, sin imports del proyecto; confirmado 18 tool calls / ~4 min).
- **v2.11.0** (2026-05-11): Nueva sección §2.5 "Verificación Pre-Creación de Prompts". Regla anti-deuda acumulativa: cada fase de implementación ejecuta `log_phase_completion.py` al terminar — NO delegar a FASE-RELEASE. Checklist obligatorio para detectar planes mal diseñados antes de crear prompts. Si T1 de RELEASE = "registrar FASE-1 a FASE-5" → error. Agregada acción correctiva.
- **v2.8.0** (2026-04-28): Protocolo de Evidencia Proactiva (obligatorio inmediatamente despues de output v4complete, antes de cualquier verificacion). Nueva seccion "Cierre Obligatorio de Sesion" — siempre guardar evidencia + actualizar plan antes de cerrar, sin excepciones.
- **v2.6.0** (2026-04-26): Modelo de Ejecución por Agentes AI explícito. Flujo reestructurado a 3 etapas (Preparación → Implementación → RELEASE). FASE-RELEASE integrada como etapa del flujo principal. Paso 7 renombrado a "FASE-RELEASE — Cierre y Documentación Oficial". Eliminada contradicción "no se ejecuta por fase". Regla de dependencia explícita: RELEASE requiere todas las implementaciones completadas.
- **v2.5.0** (2026-04-26): Límite de 60 iteraciones como regla mandatoria (R2). Sección `## Restricciones` obligatoria en prompts de fase. FASE-RELEASE formalizado como fase ejecutable con sesión propia. Alineado con estructura real de `.opencode/plans/` del PATCH Forense AmaziliaHotel 4.36.0.
- **v2.4.0** (2026-04-13): Paso 4.5: Ejecución de Plan de Documentación. Prevención de desajustes documentales al ejecutar planes como 09-documentacion-post-proyecto.md. Incluye gates de validación: log_phase_completion.py por fase, sync_versions.py, validación CHANGELOG formato CONTRIBUTING.md, validación GUIA_TECNICA.md, run_all_validations.py --quick. Checklist de completitud integrado.
- **v2.3.0** (2026-03-26): Version Sync Gate + Documentation Audit + FASE-RELEASE auto-detect. Convencion FASE-RELEASE-X.Y.Z para releases. Pre-commit hook para consistencia de versiones.
- **v2.2.0** (2026-03-25): Enforcement de docs manuales --check-manual-docs. Si hay cambios arquitectonicos en archivos de REQUIRE_ArchitectURAL_CHANGE (conditional_generator.py, faq_gen.py, voice_guide.py, aeo_kpis.py, etc.) y GUIA_TECNICA.md no menciona la fase, el script FAIL. Uso --force-skip-docs --skip-reason para excepciones.
- **v2.0.0** (2026-03-23): Simplificado — preparación en una sesión, implementación en sesión propia por fase. Elimina TDD Gate, Capability Contract, lecciones extensas.
- **v1.5.0** (2026-03-18): Regla de Sesión Única, TDD Gate
- **v1.0.0** (2026-03-03): Versión inicial

## Ejemplo de Uso

Usuario: "Divide este proyecto de refactorización en fases y prepáralo para ejecutar por sesiones"

La skill debe:
1. Leer plan existente
2. Crear `05-prompt-inicio-sesion-fase-{X}.md` para cada fase de implementación
3. Crear `05-prompt-inicio-sesion-fase-RELEASE.md` (fase de cierre)
4. Actualizar checklist con estados de fases (incluyendo RELEASE)
5. Crear `09-documentacion-post-proyecto.md` con estructura base
6. Verificar numeración de todos los prompts

**Output de esta sesión:**
```
.opencode/plans/
├── 05-prompt-inicio-sesion-fase-{X}.md         (1 por fase de implementación)
├── 05-prompt-inicio-sesion-fase-RELEASE.md      (fase de cierre)
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
├── dependencias-fases.md
└── README.md
```

La implementación de cada fase se hace en UNA sesión nueva de agente por fase. FASE-RELEASE es la última sesión.
