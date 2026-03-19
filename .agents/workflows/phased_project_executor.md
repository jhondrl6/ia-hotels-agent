---
description: Ejecutor de proyectos por fases con verificación de capability contracts, runtime evidence y prevención de capacidades desconectadas.
version: 1.5.0
---

# Skill: Phased Project Executor

> [!NOTE]
> **Trigger**: "Ejecuta por fases", "Continúa en nueva sesión", "Divide en sprints", "Preserva contexto para siguiente fase", "Trabajo por fases".

## Pre-requisitos (Contexto)
- [ ] Proyecto con división clara en fases/sprints/etapas
- [ ] Estructura de directorio `.opencode/plans/` o similar para planes
- [ ] Definición de criterios de aceptación por fase

### Pre-requisitos de Validación
- [ ] Scripts de validación funcionan: `python scripts/validate_context_integrity.py`
- [ ] Validaciones del proyecto pasan: `python scripts/run_all_validations.py --quick`
- [ ] Sincronización de versiones: `python scripts/sync_versions.py --check`

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

> [!NOTE]
> **Relación con TDD Gate**: La Regla de Sesión Única complementa el TDD Gate - 
> una fase por sesión garantiza que el test TDD tenga atención dedicada sin interrupciones.

---

### 0.6. Regla de Sesión Única (OBLIGATORIO)

> [!CAUTION]
> **REGLA MANDATORIA - Sin excepciones**
> 
> Una fase por sesión. No se permite ejecutar múltiples fases en una misma sesión.

**Aplicación**:
- Cada sesión del agente debe completar exactamente UNA fase (Fase 0, Fase 1, Fase 2, etc.)
- No existe "media fase" - se termina una fase completamente antes de pasar a la siguiente
- La sesión termina cuando el checklist de la fase muestra todos los items marcados como ✅

**Excepciones**: NINGUNA. Esta regla es absoluta.

**Validación**: 
- Al iniciar sesión, verificar que solo hay UNA fase pendiente
- Al cerrar sesión, confirmar que la fase actual está 100% completada

*Validación*: Sesión respeta regla de una fase por sesión.

### Capability Contract (CONTRATO DE CAPACIDADES)
- [ ] **Definición opcional**: capability contract definido (aunque sea mínimo)
- [ ] Mapping capability → invocation point → output artifact
- [ ] Failure policy especificada (block/warn/trace)

**Propósito**: Evitar "capabilidades huérfanas" - módulos que existen pero no se invocan en runtime ni producen output observable.

> [!TIP]
> El capability contract es un mecanismo preventivo. Si el proyecto NO tiene un listado formal de capacidades críticas, este paso puede omitirse o reducirse a una verificación básica de "módulos nuevos vs. flujos principales".

## Fronteras (Scope)
- **Hará**: 
  - Crear prompts de inicio por fase en archivos separados
  - Generar checklist de implementación por fase
  - Preparar documentación post-proyecto
  - Gestionar dependencias entre fases (0→1→2→...)
- **NO Hará**: 
  - No implementa código del proyecto (eso se hace en cada sesión con el prompt)
  - No modifica AGENTS.md ni documentación oficial (solo prepara el checklist)

## Pasos de Ejecución

### 1. Análisis del Plan del Proyecto
Leer el plan maestro y identificar:
- Número de fases/sprints
- Dependencias entre fases
- Entregables por fase
- Criterios de aceptación
- **Conflictos de archivos potenciales** (mapear qué archivos toca cada fase)
- **Overlaps de líneas** (detectar si múltiples fases modifican mismo archivo)

**Output obligatorio**: Crear `dependencias-fases.md` con:
- Diagrama ASCII de dependencias entre fases
- Tabla de conflictos potenciales (archivos, líneas, fases involucradas)
- Orden de ejecución recomendado con justificación

*Validación*: Estructura de fases identificada, conflictos documentados, orden de ejecución aprobado.

### 1.5 Verificación de Capacidades Desconectadas (CAPABILITY CONTRACT)
**Propósito**: Detectar y documentar capacidades que existen en código pero no están conectadas al flujo principal.

**Paso opcional** - Ejecutar si el proyecto tiene un "contrato de capacidades" definido o si se sospecha de módulos huérfanos.

**Output obligatorio**: Crear `matriz-capacidades.md` con:

| Capability | Estado | Punto de Invocación | Evidencia en Output | Severidad |
|------------|--------|---------------------|---------------------|-----------|
| metadata_validator | conectada/desconectada | v4_comprehensive.py:_audit_metadata() | audit_result.metadata | HIGH |
| publication_gates | conectada/desconectada | main.py:FASE 4.5 | gate_results en report | CRITICAL |
| consistency_checker | conectada/desconectada | main.py:FASE 4.6 | consistency_report | HIGH |
| financial_calculator_v2 | conectada/desconectada | main.py:FASE 3 | scenarios en report | CRITICAL |

**Criterios de evaluación**:
- **Conectada**: Existe en código Y se invoca en runtime
- **Desconectada**: Existe en código PERO no se invoca en el flujo principal
- **Huérfana**: Existe en código PERO no produce output observable

**Patrón de verificación genérico**:
```bash
# 1. Listar capacidades del contrato
grep -rn "class.*Validator\|class.*Checker\|class.*Calculator" modules/ data_validation/

# 2. Verificar invocación en flujo principal
grep -rn "Validator()\|Checker()\|Calculator()" main.py modules/

# 3. Verificar output en serialización
grep -rn "to_dict()\|export\|report" main.py | grep -i "validator\|checker\|calculator"
```

*Validación*: Matriz de capacidades completada, estados asignados, gaps identificados.

> [!NOTE]
> Este paso es especialmente útil cuando:
> - Se heredan módulos de versiones anteriores
> - Se integran capacidades de otros proyectos
> - Se sospecha de "código muerto" o funcionalidades no utilizadas

### 2. Creación de Prompts por Fase
Para cada fase, crear archivo: `.opencode/plans/05-prompt-inicio-sesion-fase-{N}.md`

**Usar como base el template**: `.agents/workflows/templates/prompt-fase-template.md`

El template incluye secciones obligatorias:
- Encabezado con ID y objetivo
- Contexto de fases anteriores
- Tareas específicas
- Tests obligatorios
- **Post-Ejecución** (obligatorio - ver template)
- **Criterios de Completitud** (obligatorio - ver template)
- Restricciones

Adaptar el contenido del template según las necesidades específicas de cada fase, manteniendo las secciones marcadas como obligatorias.

**Checklist de Verificación por Prompt:**
- [ ] Número de fase en nombre de archivo coincide con título interno
- [ ] Referencias a "fases anteriores" usan números correctos
- [ ] Tests base reflejan acumulado correcto (ej: 88, 108, 123, 135...)
- [ ] No hay conflictos de numeración con otros prompts

**Validación de Prompts Creados:**
- [ ] Cada prompt incluye referencias a fases previas con números correctos
- [ ] Tests base son acumulativos (suma de tests de fases previas + nuevos)
- [ ] Identificadores con números verificados (ej: `orchestration_v4`, `calculator_v2`)
- [ ] Métodos de 3 partes verificados (ej: `modulo.clase.metodo()`)

*Validación*: Prompts creados con especificaciones suficientes para implementación autónoma.

### 3. Generación de Checklist Maestro
Actualizar `.opencode/plans/06-checklist-implementacion.md` con:
- Estado de cada fase (pendiente/en progreso/completada)
- Tareas desglosadas por fase
- Dependencias entre fases

*Validación*: Checklist refleja el estado real del proyecto.

### 3.5. Actualización de Sprints
Para cada fase completada, actualizar el archivo correspondiente en `sprints/`:

- Marcar sprint como completado con fecha
- Actualizar estado de entregables  
- Verificar que criterios de aceptación estén marcados

Archivos afectados:
- `sprints/sprint-1-fundaciones.md` (Fases 0-1)
- `sprints/sprint-2-contradicciones.md` (Fase 2)
- `sprints/sprint-3-guardrails.md` (Fase 3)
- `sprints/sprint-4-composicion.md` (Fases 4-6)

*Validación*: Sprint correspondiente refleja el estado de la fase completada.

### 4. Preparación de Documentación Post-Proyecto (INCREMENTAL)

**Estrategia**: Documentar durante todo el proyecto, no solo al final.

**Al INICIO del proyecto**:
- Crear `.opencode/plans/09-documentacion-post-proyecto.md` con estructura base (Secciones A-E vacías)

**DESPUÉS de CADA fase completada**:
- Actualizar Sección A: Agregar módulos nuevos de esta fase
- Actualizar Sección D: Actualizar métricas acumulativas (tests, coverage, etc.)
- Actualizar Sección E: Marcar archivos afiliados actualizados
- **No esperar a la fase final para documentar**

Estructura completa del documento:

#### Sección A: Módulos Nuevos (Automático)
- [ ] Listar todos los archivos nuevos en `data_models/`
- [ ] Listar todos los archivos nuevos en `modules/*/` 
- [ ] Listar todos los tests nuevos en `tests/`
- [ ] Conteo total de tests (debe ser acumulativo)

#### Sección B: Cambios de Arquitectura (Manual)
- [ ] Diagramas actualizados (si aplica)
- [ ] Flujos de datos modificados
- [ ] Breaking changes documentados con ejemplos

#### Sección C: Validación Cruzada (Obligatorio)
Ejecutar y documentar resultados:
```bash
python scripts/validate_context_integrity.py
python scripts/run_all_validations.py --quick
python scripts/sync_versions.py --check
```

**Checklist de validación:**
- [ ] `domain_primer_methods`: PASS (sin métodos faltantes)
- [ ] `version_sync`: PASS (todas las versiones sincronizadas)
- [ ] `context_file_paths`: PASS (sin referencias rotas)
- [ ] Sin hardcoded secrets detectados

#### Sección D: Métricas Finales (Documentar)
```markdown
| Métrica | Valor | Target | Estado |
|---------|-------|--------|--------|
| Total tests | ___ | > previo | ⬜ |
| Evidence Coverage | ___% | >= 95% | ⬜ |
| Hard contradictions | ___ | = 0 | ⬜ |
| Validaciones passed | ___/___ | 100% | ⬜ |
```

#### Sección E: Archivos Afiliados por Tipo de Cambio

**Cuando se agregan nuevos módulos:**
- [ ] `CHANGELOG.md` - Entrada de release
- [ ] `docs/GUIA_TECNICA.md` - Notas de cambios técnicos
- [ ] `docs/INDICE_DOCUMENTACION.md` - Tabla de módulos
- [ ] `AGENTS.md` - Tabla de módulos activos
- [ ] `ROADMAP.md` - Logros de la sub-fase

**Cuando se modifican scripts de validación:**
- [ ] Probar regex con identificadores con números (`v4`, `v2`)
- [ ] Probar captura de métodos de 3 partes (`mod.clase.metodo`)
- [ ] Verificar con `--verbose` que no hay falsos negativos
- [ ] Documentar casos edge en comentarios del código

**Cuando se agregan modelos de datos:**
- [ ] `DOMAIN_PRIMER.md` - Glosario de conceptos
- [ ] `docs/GUIA_TECNICA.md` - Ejemplos de uso
- [ ] Tests de modelo en `tests/`

**Cuando se modifican feature flags:**
- [ ] `.conductor/guidelines.yaml` - Configuración
- [ ] `ROADMAP.md` - Estrategia de monetización
- [ ] `docs/GUIA_TECNICA.md` - Documentación técnica

*Validación*: Checklist completo de documentación listo para usar post-fase-final.

### 5. Actualización de README del Plan
Actualizar `.opencode/plans/README.md` con:
- Tabla de estados por fase
- Instrucciones de uso de los prompts
- Enfoque por sesiones/fases

**Incluir referencia a:**
- `GUIA-INICIO-RAPIDO.md` - Guía paso a paso para continuar trabajo en nuevas sesiones

*Validación*: README actualizado con información de navegación entre fases.

### 6. Validación de Numeración y Contenido
Verificar que cada prompt tenga el número de fase correcto en:
- Nombre del archivo
- Título interno (ej: "FASE 4: ...")
- Referencias cruzadas en el contexto

*Validación*: Ejecutar verificación manual o automática:
```bash
# Verificación rápida con grep
grep -n "FASE [0-9]" .opencode/plans/05-prompt-inicio-sesion-fase-*.md
```

Debe confirmar:
- [ ] fase-2.md contiene "FASE 2" en título
- [ ] fase-3.md contiene "FASE 3" en título
- [ ] fase-4.md contiene "FASE 4" en título
- [ ] fase-5.md contiene "FASE 5" en título
- [ ] fase-6.md contiene "FASE 6" en título
- [ ] No hay fases duplicadas o faltantes

### 6.5. Verificación de Guía de Inicio Rápido
Si existe `GUIA-INICIO-RAPIDO.md`, verificar que:
- [ ] Referencia al sprint/fase actual
- [ ] Enlaces a archivos correctos
- [ ] Checklist de verificación actualizado

*Validación*: Guía de inicio rápido refleja el estado actual del proyecto.

### 7. Validación Técnica Pre-Entrega (NUEVO)

Antes de marcar la fase como completada en el checklist:

#### 7.1 Validación de Scripts Críticos
Si la fase modificó scripts en `scripts/`:
```bash
# Verificar que los scripts de validación funcionan
python scripts/validate_context_integrity.py --verbose
python scripts/run_all_validations.py --quick
```

**Checklist:**
- [ ] Scripts ejecutan sin errores de importación
- [ ] Regex capturan patrones esperados (probar con identificadores reales)
- [ ] No hay falsos positivos/negativos en validaciones
- [ ] Métodos de 3 partes (`modulo.clase.metodo`) detectados correctamente
- [ ] Identificadores con números (`orchestration_v4`) detectados correctamente

#### 7.2 Validación de Sincronización
```bash
python scripts/sync_versions.py --check
```

**Checklist:**
- [ ] Todas las versiones sincronizadas
- [ ] No hay discrepancias entre encabezados y contenido
- [ ] Fechas de actualización consistentes

#### 7.3 Validación de Métricas
Verificar que las métricas están actualizadas en TODOS los documentos:

**Tests:**
- [ ] `AGENTS.md` - Tests count actualizado
- [ ] `docs/GUIA_TECNICA.md` - Tests count actualizado  
- [ ] `docs/INDICE_DOCUMENTACION.md` - Tests count actualizado
- [ ] README.md - Tests count actualizado

**Versión y Fecha:**
- [ ] `AGENTS.md` - Versión y fecha actualizadas
- [ ] `.cursorrules` - Versión sincronizada
- [ ] `README.md` - Versión y fecha actualizadas
- [ ] `docs/INDICE_DOCUMENTACION.md` - Versión y fecha actualizadas

**Validación Automática de Consistencia:**
```bash
# Verificar que todos los conteos de tests sean iguales
grep -rn "[0-9]\+ tests passing" AGENTS.md CHANGELOG.md ROADMAP.md docs/*.md 2>/dev/null | head -20
# Todos los números deben coincidir

# Verificar consistencia de versión
grep -rn "v[0-9]\+\.[0-9]\+\.[0-9]\+" AGENTS.md .cursorrules README.md VERSION.yaml 2>/dev/null | head -20
# Todas las versiones deben coincidir con VERSION.yaml
```

**Acción si hay inconsistencias**:
- Corregir inmediatamente antes de marcar fase como completada
- Usar `grep` para encontrar todos los archivos con el valor incorrecto
- Actualizar todos los documentos simultáneamente

*Validación*: Todas las validaciones pasan antes de marcar fase como completada.

#### 7.4 Runtime Invocation & Output Evidence (CONTRACTUAL)
**Propósito**: Verificar que las capacidades contractuales tienen invocación real en runtime Y producen output observable.

**Este paso es obligatorio si existe capability contract definido.**

**Verificación de Invocación en Runtime**:
```bash
# Para cada capability del contrato, verificar:
# 1. Existe en código (archivo con clase/función)
grep -rn "class.*Capability\|def.*capability" modules/ data_validation/

# 2. Se invoca en flujo principal (no solo se importa)
grep -rn "Capability()\|capability\." main.py modules/orchestration_v4/

# 3. NO está comentada o en bloque unreachable
grep -B5 -A5 "capability" main.py | grep -v "^[[:space:]]*#"
```

**Verificación de Output Observable**:
```bash
# Para cada capability, verificar que serializa en output
grep -rn "to_dict\|export\|report\|json" main.py | grep -i "capability"

# Verificar presencia en artefactos de salida
ls -la output/*.json 2>/dev/null
grep -l "metadata\|gate_results\|consistency" output/*.json 2>/dev/null
```

**Checklist de Approval**:
- [ ] 0 capacidades contractuales sin invocación en runtime
- [ ] 0 capacidades invocadas sin output observable
- [ ] Si existe `matriz-capacidades.md`, todos los estados son "conectada"

**Patrón Genérico de Validación** (reemplaza nombres específicos):
```python
# Pseudocódigo para validación automática
def validate_capability_contract(contract_file="matriz-capacidades.md"):
    capabilities = parse_capability_matrix(contract_file)
    for cap in capabilities:
        has_code = file_exists(cap.module_path)
        has_invocation = grep_in_files(cap.invocation_pattern, ["main.py", "orchestration_v4/"])
        has_output = grep_in_files(cap.output_pattern, ["output/"])
        
        if not (has_code and has_invocation and has_output):
            report_capability_gap(cap.name, has_code, has_invocation, has_output)
```

*Validación*: 0 gaps en capability contract. Todas las capacidades están conectadas y producen evidencia.

### 8. Gate de Calidad Pre-Cierre (NUEVO)

Última verificación antes de finalizar la fase:

#### Checklist de Calidad
- [ ] Paso 7 (Validación Técnica) completado con éxito
- [ ] Todos los archivos de "Archivos Afiliados" verificados
- [ ] No hay referencias rotas (links, imports, métodos)
- [ ] Métricas consistentes en todos los documentos
- [ ] **Disconnected Capability Gate: PASS** (0 capacidades huérfanas)
- [ ] **Execution Trace Gate: PASS** (evidencia de validadores ejecutados)
- [ ] Commit listo con mensaje descriptivo

#### Comando de Validación Final
```bash
# Ejecutar antes de marcar como completada
python scripts/run_all_validations.py
python scripts/validate_context_integrity.py
python scripts/sync_versions.py --check

# Si existe capability contract, verificar también:
python -m pytest tests/ -v --tb=short  # Validar que capacidades se ejecutan
```

**Resultado esperado:** 
```
STATUS: ALL VALIDATIONS PASSED
RESULT: All validations passed
All files in sync
```

Si alguna validación falla, corregir antes de continuar.

*Validación*: Fase lista para ser marcada como completada.

### 9. Validación de Cumplimiento de Skill (NUEVO)

Verificar que todos los pasos de esta skill se ejecutaron correctamente:

#### Checklist de Cumplimiento
- [ ] Paso 1: Plan analizado con conflictos documentados en `dependencias-fases.md`
- [ ] Paso 1.5: Matriz de capacidades completada (si aplica capability contract)
- [ ] Paso 2: Prompts creados (1 por fase) usando el template
- [ ] Paso 3: Checklist maestro actualizado
- [ ] Paso 4: `09-documentacion-post-proyecto.md` creado e incrementado
- [ ] Paso 5: README del plan actualizado
- [ ] Paso 6: Numeración verificada
- [ ] Paso 7: Validaciones técnicas PASSED (5/5: 7.1-7.4)
- [ ] Paso 7.4: Runtime invocation & output evidence PASS
- [ ] Paso 8: Gate de calidad aprobado (incl. Disconnected Capability Gate)
- [ ] **Paso 0.5 TDD Gate: Verificado (test fallando antes de implementación)**
- [ ] Post-ejecución: Estados de salud actualizados después de cada fase

#### Output de Cumplimiento
Agregar al final de `09-documentacion-post-proyecto.md`:

```markdown
## Cumplimiento de Skill phased_project_executor

| Paso | Descripción | Estado |
|------|-------------|--------|
| 1 | Análisis del Plan | ✅/❌ |
| 1.5 | Matriz de Capacidades | ✅/❌ |
| 2 | Prompts por Fase | ✅/❌ |
| 3 | Checklist Maestro | ✅/❌ |
| 4 | Documentación Post-Proyecto | ✅/❌ |
| 5 | README del Plan | ✅/❌ |
| 6 | Validación Numeración | ✅/❌ |
| 7 | Validación Técnica (5/5) | ✅/❌ |
| 7.4 | Runtime Invocation & Output | ✅/❌ |
| 8 | Gate de Calidad | ✅/❌ |
| 0.5 | **TDD Gate (Test Fallando)** | ✅/❌ |
| 9 | Cumplimiento Skill | ✅/❌ |

**Versión Skill**: v1.5.0
**Fecha Verificación**: YYYY-MM-DD
```

*Validación*: Skill ejecutada correctamente. Evidencia documentada.

## Criterios de Éxito
- [ ] Prompts de inicio por fase creados (1 por fase) **(con secciones Post-Ejecución y Criterios Completitud)**
- [ ] Checklist maestro con estados actualizados
- [ ] Sprints sincronizados con estados de fases
- [ ] Documentación post-proyecto preparada (Secciones A-E completas) **(actualizada incrementally)**
- [ ] README del plan actualizado (con referencia a guía rápida)
- [ ] Guía de inicio rápido verificada (si existe)
- [ ] **Validación técnica pasada (Paso 7) - 5/5 verificaciones**
- [ ] **Paso 7.4 Runtime Invocation & Output Evidence: PASS**
- [ ] **Gate de calidad pre-cierre aprobado (Paso 8)**
- [ ] **Disconnected Capability Gate: PASS** (0 capacidades huérfanas)
- [ ] **Execution Trace Gate: PASS** (validadores ejecutados documentados)
- [ ] **Matriz de capacidades completada** (si aplica capability contract)
- [ ] **Todas las métricas consistentes entre documentos**
- [ ] **Archivos afiliados actualizados según tipo de cambio**
- [ ] **"Paso 0.5 TDD Gate: PASS (test fallando antes de implementación)"**
- [ ] **Conflictos de archivos documentados en `dependencias-fases.md`**
- [ ] **Validación de cumplimiento de skill verificada (Paso 9)**
- [ ] Estructura lista para ejecutar fase siguiente en nueva sesión

## Plan de Recuperación (Fallback)
- Si el proyecto no tiene estructura de planes, crear `.opencode/plans/` automáticamente.
- Si no hay división en fases, proponer una estructura estándar (Fase 0-6).
- Si los prompts quedan muy grandes, dividir en secciones dentro del mismo archivo.

## Nota sobre Documentación Oficial

Esta skill prepara la estructura para actualizar AGENTS.md **al finalizar todas las fases** del proyecto.

El archivo `09-documentacion-post-proyecto.md` generado por esta skill contiene el checklist completo de elementos a documentar en la actualización oficial del repositorio.

## Versiones

- **v1.5.0** (2026-03-18): Regla de Sesión Única - Una fase por sesión (obligatorio, sin excepciones), TDD Gate agregado a tabla de validación (Paso 9).
- **v1.4.0** (2026-03-09): Capabilidad de contratos de capacidades - Paso 1.5 (matriz-capacidades.md), Paso 7.4 (Runtime Invocation & Output Evidence), Disconnected Capability Gate, Execution Trace Gate. Enfoque genérico reusable para evitar módulos huérfanos.
- **v1.3.0** (2026-03-04): Mejoras post-implementación v4.4.0 - Detección temprana de conflictos (Paso 1), documentación incremental (Paso 4), estado de salud visible y checklist "Done" en template de prompts, validación automática de métricas (Paso 7.3), validación de cumplimiento de skill (Paso 9).
- **v1.2.0** (2026-03-03): Agregado Paso 7 (Validación Técnica), Paso 8 (Gate de Calidad), checklist de Archivos Afiliados, y lecciones aprendidas de v4.3.0.
- **v1.1.0** (2026-03-03): Agregado soporte para sincronización de sprints, referencia a guía rápida, y verificación de documentación auxiliar.
- **v1.0.0** (2026-03-03): Versión inicial. Soporte para proyectos de 2-6 fases con preservación de contexto entre sesiones.

## Ejemplo de Uso

Usuario dice: "Divide este proyecto de refactorización en fases y prepáralo para ejecutar por sesiones"

La skill debe:
1. Leer plan existente
2. Crear `05-prompt-inicio-sesion-fase-2.md` con especificaciones técnicas completas
3. Crear `05-prompt-inicio-sesion-fase-3.md` (borrador)
4. Actualizar checklist con fases 0-1 completadas, fase 2 siguiente
5. Actualizar sprint correspondiente (`sprints/sprint-2-*.md`)
6. Crear `09-documentacion-post-fase-6.md` con checklist AGENTS.md
7. Actualizar README con referencia a GUIA-INICIO-RAPIDO.md
8. Verificar numeración y guía rápida

## Lecciones Aprendidas de Implementaciones Previas

### Numeración de Fases
**Problema común**: Al crear múltiples prompts en paralelo, la numeración puede intercambiarse (ej: fase-4.md conteniendo "FASE 6").

**Prevención**:
- Siempre usar paso de validación final (Paso 6)
- Verificar que el título interno coincida con el nombre de archivo
- Revisar secuencia lógica: Fase N debe tener fases 0 a N-1 como completadas

### Dependencias Acumulativas
**Problema común**: Los prompts de fases avanzadas deben reflejar correctamente el estado acumulado.

**Verificación**:
- Tests base debe ser acumulativo (tests_fase_1 + tests_fase_2 + ...)
- Contexto debe listar correctamente fases previas como ✅ COMPLETADAS
- Base técnica disponible debe incluir módulos de TODAS las fases previas

### Validación de Scripts (v4.3.0)
**Problema**: Regex `[a-zA-Z_]+` no captura identificadores con números (`orchestration_v4`).

**Impacto**: Falsos negativos en validación de métodos, fallo en `domain_primer_methods`.

**Solución aplicada**: Usar `[a-zA-Z_][a-zA-Z0-9_]*` para identificadores válidos en Python.

**Prevención**:
- Probar regex con casos reales antes de commit
- Incluir identificadores con números en tests unitarios
- Documentar casos edge en comentarios

### Sincronización de Versiones (v4.3.0)
**Problema**: `AGENTS.md` tenía versión 4.2.0 en encabezado pero contenido de 4.3.0.

**Impacto**: Inconsistencia percibida, validaciones fallidas.

**Solución aplicada**: 
1. Ejecutar `python scripts/sync_versions.py` después de cambiar `VERSION.yaml`
2. Verificar con `python scripts/sync_versions.py --check`

**Prevención**:
- Incluir validación de versiones en Paso 7
- No modificar versiones manualmente en archivos individuales

### Métricas Desactualizadas (v4.3.0)
**Problema**: Diferentes archivos reportaban diferentes cantidades de tests (704 vs 908 vs 1257).

**Impacto**: Desconfianza en la documentación.

**Solución aplicada**:
- Crear checklist de métricas en Paso 4 (Sección D)
- Validar consistencia en Paso 7.3

**Prevención**:
- Actualizar métricas en TODOS los documentos simultáneamente
- Usar búsqueda global (`grep -r "704 tests"`) para encontrar inconsistencias

### Documentación Faltante (v4.3.0)
**Problema**: `CHANGELOG.md`, `GUIA_TECNICA.md`, `ROADMAP.md` no tenían entradas para v4.3.0.

**Impacto**: Contexto incompleto para futuros desarrolladores.

**Solución aplicada**:
- Crear checklist de "Archivos Afiliados" en Paso 4 (Sección E)
- Definir qué archivos actualizar según tipo de cambio

**Prevención**:
- Consultar `docs/CONTRIBUTING.md` §5 para checklist de documentación
- No considerar fase completada hasta que documentación esté lista

### Cumplimiento de Skill No Verificado (v4.4.0)
**Problema**: Se ejecutaron 7 sesiones sin verificar que todos los pasos de la skill se cumplieran. El archivo `09-documentacion-post-proyecto.md` no existió hasta el final, y las métricas de tests eran inconsistentes entre documentos (1257 vs 1261).

**Impacto**: Pérdida de contexto intermedio, estado desactualizado, inconsistencias de métricas, documentación faltante.

**Solución aplicada**:
- Crear Paso 9 (Validación de Cumplimiento de Skill)
- Agregar documentación incremental al Paso 4 (actualizar después de cada fase)
- Agregar post-ejecución obligatoria y checklist "Done" a cada prompt de fase
- Agregar validación automática de métricas en Paso 7.3
- Agregar detección temprana de conflictos en Paso 1

**Prevención**:
- Verificar cumplimiento de skill antes de cerrar proyecto (Paso 9)
- No esperar a la fase final para documentar
- Actualizar estado de salud después de cada sesión
- Validar consistencia de métricas entre documentos antes de marcar completado

### Capacidades Desconectadas (PATRÓN REUSABLE - v1.4.0)
**Problema**: Módulos como MetadataValidator, PublicationGates, ConsistencyChecker y FinancialCalculatorV2 existían en código pero no estaban conectados al flujo principal (main.py).

**Impacto**: Funcionalidades "huérfanas" que no se ejecutan, no producen output, y no son visibles para el usuario.

**Solución aplicada (genérica)**:
- Crear Paso 1.5 (Verificación de Capacidades Desconectadas) con `matriz-capacidades.md`
- Agregar Paso 7.4 (Runtime Invocation & Output Evidence) para verificar invocación real
- Agregar "Disconnected Capability Gate" en Paso 8
- Documentar capability contract: capability → invocation point → output artifact
- Usar validación por patrón (no por nombre fijo) para reutilización futura

**Patrón de Prevención**:
```bash
# Verificación genérica de capabilities
1. Listar clases que terminan en Validator/Checker/Calculator
2. Verificar que se invocan en main.py u orchestrator
3. Verificar que producen output serializable (to_dict, export, report)
4. Documentar gaps en matriz-capacidades.md
```

**Este patrón aplica a cualquier proyecto** con múltiples módulos que requieren integración.

## Patrones de Validación Probados

Basado en implementaciones previas, estos son patrones validados:

### Regex para Identificadores Python
```python
# ✅ CORRECTO: Captura identificadores con números
r'\b([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+)\(\)'

# ❌ INCORRECTO: No captura números (ej: orchestration_v4)
r'\b([a-zA-Z_]+(?:\.[a-zA-Z_]+)+)\(\)'
```

### Mapeo de Módulos a Archivos
```python
module_files = {
    'orchestration_v4': project_root / "modules" / "orchestration_v4" / "onboarding_controller.py",
    'financial_engine': project_root / "modules" / "financial_engine" / "scenario_calculator.py",
    # Agregar nuevos módulos aquí
}
```

### Validación de Métodos en Clases
```python
# Para métodos de 3 partes: modulo.clase.metodo()
def _check_method_exists(module_path, method_name, class_name=None):
    if class_name:
        # Buscar dentro de clase específica
        class_pattern = rf'class {class_name}[^:]*:'
        # ... extraer contenido de clase
        method_pattern = rf'def {method_name}\s*\('
    else:
        # Buscar método global
        method_pattern = rf'def {method_name}\s*\('
```

### Checklist de Métricas Consistentes
```bash
# Buscar conteos de tests inconsistentes
grep -r "tests passing" docs/ *.md

# Buscar versiones inconsistentes  
grep -r "version.*4\." docs/ *.md | grep -v "4\.3\.0"
```

## Formato de Salida

La skill debe guardar archivos en:
```
.opencode/plans/
├── 05-prompt-inicio-sesion-fase-{N}.md    (1 por fase)
├── 06-checklist-implementacion.md         (actualizado)
├── 09-documentacion-post-proyecto.md      (nuevo)
├── matriz-capacidades.md                 (opcional: capability contract)
├── dependencias-fases.md                  (analisis de conflictos)
├── README.md                              (actualizado)
└── sprints/sprint-{N}-*.md               (sincronizado con fases)
```

**Opcional (si existen):**
- `GUIA-INICIO-RAPIDO.md` - Guía de navegación
- `modules/*.md` - Documentación de módulos específicos
- `tests/*.md` - Casos de prueba
