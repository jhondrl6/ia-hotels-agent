# Contexto: Auditoría Forense y Plan de Integración Documental

> **Fecha**: 2026-05-07
> **Sesión origen**: Auditoría exhaustiva de phased_project_executor.md
> **Plan asociado**: `.opencode/plans/INTEGRACION-DOCUMENTAL-PLAN.md`
> **Estado**: Plan creado, NO ejecutado. Listo para FASE-A en nueva sesión.
> **Verificación post-auditoría**: 2026-05-07 — 11 hallazgos adicionales documentados en §9

---

## 1. Qué motivó esta investigación

El usuario solicitó una revisión exhaustiva de:
- `.agents/workflows/phased_project_executor.md` (workflow de ejecución por fases)

contra:
- `docs/CONTRIBUTING.md` (reglas documentales del repositorio)

Observación inicial del usuario: DOMAIN_PRIMER.md tenía fecha de última
modificación del 20 de abril, lo cual indicaba desactualización. Esto
disparó la sospecha de que los documentos no estaban trabajando en equipo.

---

## 2. Qué se encontró (15 anomalías en 10 fallos agrupados)

> **NOTA**: El conteo original decía "18 anomalías". Verificación post-auditoría
> confirmó que Fallo #5 y Fallo #9 describen el mismo problema (formato
> CHANGELOG inconsistente) en dos secciones distintas. Conteo real: ~15 issues
> en 10 fallos (6 typos en #3 contados individualmente + 9 fallos restantes).

### FALLO #1 — CRÍTICO: DOMAIN_PRIMER.md desactualizado 11 versiones

DOMAIN_PRIMER.md decía: v4.31.1 AMAZILIA-BUGFIX (2026-04-20)
El sistema real estaba en: v4.42.0 SOL-2-ASSET-ALIGNMENT-REFACTOR (2026-05-07)

Causa: no hay ningún flujo que regenere DOMAIN_PRIMER automáticamente
post-proyecto. Se queda congelado en la versión que tenía cuando se creó.

**Acción tomada**: Se ejecutó `doctor.py --regenerate-domain-primer` y
se actualizó a v4.42.0. Pero esto es un parche — el flujo del executor
no lo mandaba hacer.

**⚠️ Hallazgo post-auditoría**: DOMAIN_PRIMER.md quedó con release_date
`2026-05-08` (fecha futura) mientras VERSION.yaml dice `2026-05-07`.
Posible bug en `doctor.py` o desplazamiento de timezone. Ver §9-F.

### FALLO #2 — ALTO: Caracteres chinos en texto español

Línea 48 del executor: "FASE太大了 (una sesion)" y "bien scopes"
**Acción tomada**: Corregido a "FASE demasiado grande" / "bien acotada"

### FALLO #3 — ALTO: 6 typos/errores ortográficos

- "Des pues" → "Después de"
- "si tudo OK" → "si todo OK" (portugués)
- "insu clergal" → "insuficiente"
- "termina de generations" → "termina de generar"
- "Senales" → "Señales"
- "Sintomas" → "Síntomas"

**Acción tomada**: Todos corregidos.

### FALLO #4 — ALTO: Python path inconsistente

El mismo archivo usaba `python` (4 veces) y `./venv/Scripts/python.exe`
(19 veces) para el mismo tipo de comandos. CONTRIBUTING.md usa `python`
genérico (16 veces).

**Acción tomada**: Estandarizado a `./venv/Scripts/python.exe` en el
executor. CONTRIBUTING.md no se tocó (pendiente de decisión en FASE-A).

### FALLO #5 — MEDIO: Formato CHANGELOG inconsistente (3 referencias, mismo problema que #9)

| Documento | Formato |
|-----------|---------|
| CHANGELOG.md real | `## [4.42.1] - 2026-05-07` |
| documentation_rules.md §37 | `## [X.Y.Z] - YYYY-MM-DD` |
| executor E3 | `## [X.Y.Z] - Titulo (Fecha)` |

CHANGELOG real usa `[X.Y.Z]` sin prefijo `v` y sin título en el heading
(solo fecha). documentation_rules.md ya lo declaraba correctamente en §37.
El executor E3 agregaba título, que no corresponde.

**Acción tomada**: Corregido template E3 para alinear con el formato real.
Pero la fuente de verdad no está declarada formalmente en un solo sitio.

**⚠️ Hallazgo post-auditoría**: CHANGELOG.md está en `[4.42.1]` mientras
VERSION.yaml está en `4.42.0`. Hay un drift de versión patch-level entre
CHANGELOG y la fuente de verdad. Ver §9-A.

### FALLO #6 — MEDIO: 10 referencias a CONTRIBUTING.md con líneas incorrectas

Todas las referencias §NN-MM en el executor estaban desfasadas 1-2
líneas respecto al CONTRIBUTING real. Ejemplo: §78-85 → real §79-85.

Causa: las referencias usan números de línea absolutos que se desfasan
cuando cualquiera de los dos documentos se edita.

**Acción tomada**: Corregidas 7 referencias. **3 referencias quedaron sin
corregir y no fueron documentadas cuáles son**. El problema persiste:
las referencias a líneas absolutas seguirán rompiéndose con cada edición.

### FALLO #7 — MEDIO: Redundancia Evidencia + Cierre

"Protocolo de Evidencia Proactiva" (§223-238) y "Cierre Obligatorio de
Sesión" (§240-257) repetían el mismo bloque bash de copia de evidencia.

**Acción tomada**: El bloque duplicado del Cierre se reemplazó con una
referencia al Protocolo. Línea 245 ahora dice: "ejecutar el bloque bash
del Protocolo de Evidencia Proactiva (sección anterior §L223-238)".

### FALLO #8 — BAJO: Version header sin prefijo "v"

Executor: `version: 2.10.0`
**Acción tomada**: Corregido a `version: v2.10.0`

**⚠️ Hallazgo post-auditoría**: El mismo problema existe en
`.agents/workflows/templates/prompt-fase-template.md` línea 3:
`version: 1.3.0` (sin "v"). No fue corregido en esta sesión. Ver §9-D.

### FALLO #9 — BAJO: Template CHANGELOG en §4.5.3 no coincide con el real

Mismo problema que #5 pero en sección diferente del executor.
**Acción tomada**: Corregido. Fusionado conceptualmente con Fallo #5.

### FALLO #10 — BAJO: "Entrega" como directorio de planes

El árbol de output del executor (ahora líneas 800-808) mostraba
"Entrega/" sin que sea un archivo estándar de `.opencode/plans/`.
**Acción tomada**: Eliminado del tree. El archivo tiene 810 líneas
totales (la referencia original a "línea 812" era incorrecta).

---

## 3. Análisis de flujo: ¿Los documentos trabajan en equipo?

### Pregunta central
¿Desde la planificación del executor, la actualización documental es una
parte específica que cumple lo dispuesto en CONTRIBUTING?

### Respuesta: NO completamente

Se descubrió una desconexión estructural entre los flujos documentales:

#### Flujo actual (3 etapas)

**ETAPA 1 — PREPARACIÓN** (executor §Step 4):
- Crea `09-documentacion-post-proyecto.md` con "estructura vacía"
- Solo menciona Secciones A, D, E (genéricas)
- NO define formato concreto
- NO referencia CONTRIBUTING.md para el contenido

**ETAPA 2 — IMPLEMENTACIÓN** (executor §Step 6):
- Ejecuta `log_phase_completion.py` → registra en REGISTRY.md
- Detecta gaps de GUIA_TECNICA
- PERO NO instruye al agente a EDITAR CHANGELOG
- PERO NO instruye al agente a EDITAR GUIA_TECNICA
- El agente ejecuta el script y "confía" en que eso es suficiente

**ETAPA 3 — RELEASE** (executor §Paso 7 E3-E4):
- Aquí SÍ se exigen CHANGELOG y GUIA_TECNICA completos
- PERO es una sesión diferente, posiblemente días después
- El agente RELEASE tiene que reconstruir contexto perdido

#### El template es más estricto que el executor

`.agents/workflows/templates/prompt-fase-template.md` línea 128 dice:
  "Documentación afiliada: CHANGELOG.md, GUIA_TECNICA.md, etc. actualizados"

Pero el executor §Step 4 (línea 323-331) solo dice:
  "Sección A: Módulos nuevos / Sección D: Métricas / Sección E: Archivos afiliados"

"Archivos afiliados" es VAGO. No dice cuáles ni cómo.

Resultado: el template exige CHANGELOG/GUIA_TECNICA en el checklist de
completitud (§6), pero el executor nunca instruye al agente a hacerlo.
El agente que sigue el executor al pie de la letra FALLA el checklist
del template.

#### Los dos flujos documentales de CONTRIBUTING

CONTRIBUTING.md tiene DOS flujos que no se comunican:

1. **Post-fase** (§39-52): solo ejecuta `log_phase_completion.py` → REGISTRY
2. **Post-proyecto/RELEASE** (§56-165): documentación completa (CHANGELOG,
   GUIA_TECNICA, sync, DOMAIN_PRIMER, etc.)

El executor refleja esta estructura fielmente. PERO el template (línea 128)
exige CHANGELOG/GUIA_TECNICA por fase, lo cual NO está respaldado por
CONTRIBUTING.md.

---

## 4. La causa raíz (5 factores — revisados post-auditoría)

### Factor 1: Sin contrato formal
CONTRIBUTING define reglas. El executor las "referencia". Pero no hay
mecanismo que garantice cumplimiento. Si CONTRIBUTING cambia, el executor
no se entera. Las referencias a líneas absolutas (§78-85) se rompen con
cualquier edición.

### Factor 2: Formatos propietarios
Cada documento define su propio formato de CHANGELOG, version header, y
comandos python. No hay un estándar único declarado en un solo sitio.

### Factor 3: DOMAIN_PRIMER huérfano
No hay ningún flujo que lo regenere automáticamente post-proyecto. Se
queda en la versión que tenía cuando se creó. El executor dice "verificar"
(E7) pero no "regenerar".

### Factor 4: AGENTS.md con vínculos existentes pero insuficientes
**CORREGIDO POST-AUDITORÍA**: A diferencia de lo indicado inicialmente,
AGENTS.md SÍ tiene vínculos activos:
- Referencia directa al executor por sección: `.agents/workflows/phased_project_executor.md §4.5` (línea 95)
- Sección "Vinculo con la Documentacion del Repositorio" que lista CONTRIBUTING.md, documentation_rules.md, validation.md
- Flujo documental resumido con 5 pasos numerados

Sin embargo, estos vínculos son de navegación general, no contractuales.
AGENTS.md referencia documentos pero no verifica su coherencia cruzada.
El problema no es que AGENTS.md sea "pasivo" (no lo es), sino que sus
vínculos son informativos, no validadores.

### Factor 5: Template desalineado
`.agents/workflows/templates/prompt-fase-template.md` §6 exige CHANGELOG/
GUIA_TECNICA por fase, pero el executor no lo instruye. El template es
más estricto que el workflow que lo invoca. Nadie verifica esta coherencia.

---

## 5. Patches sintomáticos aplicados (esta sesión)

Se corrigieron los 15 fallos directamente en los archivos. Estos patches
son válidos pero NO resuelven la causa raíz. Sin la intervención
estructural (plan INTEGRACION-DOCUMENTAL), los mismos tipos de errores
reaparecerán cuando:

- Se edite CONTRIBUTING sin actualizar el executor
- Se edite el executor sin verificar CONTRIBUTING
- Se complete un proyecto sin regenerar DOMAIN_PRIMER
- Se cree un prompt de fase sin alinearlo con el executor

### Archivos modificados en esta sesión

| Archivo | Cambios |
|---------|---------|
| `.agents/workflows/phased_project_executor.md` | Typos, python path, formato CHANGELOG, redundancia, version header, referencias CONTRIBUTING (7/10 corregidas) |
| `docs/contributing/documentation_rules.md` | Formato CHANGELOG alineado con realidad |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Regenerado v4.31.1 → v4.42.0 |

### Archivos con problemas remanentes no corregidos

| Archivo | Problema |
|---------|----------|
| `.agents/workflows/phased_project_executor.md` | 3 referencias a CONTRIBUTING sin corregir (no identificadas) |
| `.agents/workflows/templates/prompt-fase-template.md` | Version header sin prefijo "v" (`1.3.0` en vez de `v1.3.0`) |
| `.agent/knowledge/DOMAIN_PRIMER.md` | release_date `2026-05-08` no coincide con VERSION.yaml `2026-05-07` |
| `CHANGELOG.md` | Versión `[4.42.1]` vs VERSION.yaml `4.42.0` (drift no resuelto) |
| Todo el repo | `run_all_validations.py --quick` NO ejecutado post-patches |

---

## 6. Plan de intervención estructural

**Archivo**: `.opencode/plans/INTEGRACION-DOCUMENTAL-PLAN.md`

**Tres fases**:
- **FASE-A** (1 sesión): Diseño de la arquitectura de integración.
  Definir contratos, estándares compartidos, flujos de DOMAIN_PRIMER,
  vínculos AGENTS.md, y resolver template ↔ executor.
- **FASE-B** (1-2 sesiones): Implementación. Modificar los 5 archivos
  (CONTRIBUTING, executor, AGENTS, DOMAIN_PRIMER, template) según el
  diseño de FASE-A.
- **FASE-C** (opcional, 1 sesión): Gate de no-regresión. Script de
  validación cross-documental integrado en pre-commit.

**Para ejecutar**: "Continúa con FASE-A del plan INTEGRACION-DOCUMENTAL-PLAN.md"

---

## 7. Preguntas abiertas para FASE-A

1. **Python path**: ¿Estandarizar a `./venv/Scripts/python.exe` (WSL) o
   `python` genérico (portable)? Afecta executor Y CONTRIBUTING.

2. **CHANGELOG por fase**: ¿Cada fase crea entrada CHANGELOG (Opción A),
   solo RELEASE crea CHANGELOG (Opción B), o cada fase acumula datos en
   09 y RELEASE genera CHANGELOG con esos datos (Opción C — recomendada)?

3. **DOMAIN_PRIMER frequency**: ¿Regenerar siempre en RELEASE o solo
   cuando hubo cambios arquitectónicos?

4. **Referencias a CONTRIBUTING**: ¿Mantener §líneas absolutas (frágil) o
   cambiar a §Section-Name (estable)?

5. **Template vs executor**: ¿Cuál es la fuente de verdad cuando difieren?

6. **Pre-commit hooks existentes**: ¿Cómo se integra el gate de FASE-C con
   los hooks `agent-ecosystem` y `version-sync` que ya están activos?
   AGENTS.md línea 108 documenta "Pre-commit ecosystem validation" como
   mejora implementada. Verificar `validate_agent_ecosystem.py` antes de
   diseñar FASE-C para no duplicar funcionalidad.

7. **3 referencias pendientes**: Identificar y documentar las 3 referencias
   a CONTRIBUTING que quedaron sin corregir en el executor (Fallo #6).

---

## 8. Estado del sistema al momento de la auditoría

| Aspecto | Valor |
|---------|-------|
| Versión del sistema (VERSION.yaml) | v4.42.0 |
| CHANGELOG.md última entrada | [4.42.1] (⚠️ drift: 1 patch por delante de VERSION.yaml) |
| Codename | SOL-2-ASSET-ALIGNMENT-REFACTOR |
| DOMAIN_PRIMER (post-regen) | v4.42.0 (⚠️ release_date: 2026-05-08 vs VERSION.yaml: 2026-05-07) |
| Executor version | v2.10.0 |
| Template version | 1.3.0 (⚠️ sin prefijo "v" — mismo bug que FALLO #8) |
| CONTRIBUTING version header | v4.42.0 |
| Tests | 2491 funciones, 192 archivos |
| doctor.py --context | PASS |
| run_all_validations.py --quick | ⚠️ NO EJECUTADO post-patches |
| Pre-commit hooks | `agent-ecosystem` + `version-sync` activos (no analizados en esta auditoría) |

---

## 9. Hallazgos de verificación post-auditoría (2026-05-07)

Esta sección documenta discrepancias encontradas al cotejar el context
original contra el código real del repositorio.

### 9-A. CHANGELOG.md desincronizado de VERSION.yaml

- VERSION.yaml: `version: "4.42.0"`
- CHANGELOG.md: `## [4.42.1] - 2026-05-07`

CHANGELOG está 1 patch-level por delante de la fuente de verdad.
El context original no detectó este drift. Impacto: cualquier
script de sync que lea VERSION.yaml versus CHANGELOG encontrará
inconsistencia.

### 9-B. Factor 4 corregido: AGENTS.md no es "pasivo"

AGENTS.md línea 95 referencia directamente al executor por sección
(`phased_project_executor.md §4.5`). La sección "Vinculo con la
Documentacion del Repositorio" (líneas ~82-98) lista CONTRIBUTING.md,
documentation_rules.md, y validation.md con flujo numerado.

El diagnóstico original subestimó los vínculos existentes. El problema
real es que son vínculos *informativos*, no *contractuales*: AGENTS.md
apunta a los documentos pero no garantiza que estén sincronizados.

### 9-C. Las 3 referencias a CONTRIBUTING no corregidas

El Fallo #6 documenta 10 referencias desfasadas. Se corrigieron 7.
Las 3 restantes no fueron identificadas ni documentadas. FASE-A
necesita localizarlas antes de diseñar soluciones.

### 9-D. Template version header sin "v" (mismo bug que Fallo #8)

`.agents/workflows/templates/prompt-fase-template.md` línea 3:
`version: 1.3.0` — sin prefijo "v". El context original documentó
este archivo como "Template version: v1.3.0" (línea 268), agregando
una "v" que el archivo real no tiene.

### 9-E. Path real del template

El context original usa el nombre corto `prompt-fase-template.md`.
El path real es `.agents/workflows/templates/prompt-fase-template.md`.
Búsquedas por nombre corto fallan (0 resultados en search_files).

### 9-F. DOMAIN_PRIMER.md release_date futuro

DOMAIN_PRIMER.md línea 7: `Release date: 2026-05-08`
VERSION.yaml línea 5: `release_date: "2026-05-07"`

La regeneración con `doctor.py --regenerate-domain-primer` produjo una
fecha 1 día en el futuro. Posibles causas: timezone del script, fecha
del sistema al momento de regeneración, o bug en doctor.py.

### 9-G. Inconsistencia de line endings

| Archivo | Line ending |
|---------|-------------|
| `DOMAIN_PRIMER.md` | CRLF (Windows) |
| `CONTRIBUTING.md` | CRLF (Windows) |
| `phased_project_executor.md` | LF (Unix) |
| `AGENTS.md` | CRLF (Windows) |

Esta mezcla de CRLF/LF puede causar que las referencias a números de
línea varíen según el sistema que las lee (Git, grep, editors).

### 9-H. Pre-commit hooks no analizados

AGENTS.md línea 108 documenta "Pre-commit ecosystem validation" como
mejora activa. Los hooks `agent-ecosystem` y `version-sync` ya existen.
La FASE-C del plan propone crear un "gate de no-regresión" — pero no
se analizó si los hooks existentes ya cubren parte de esa funcionalidad.
Verificar `scripts/validate_agent_ecosystem.py` antes de diseñar FASE-C.

### 9-I. Plan INTEGRACION-DOCUMENTAL-PLAN.md no validado

El plan asociado (213 líneas) existe pero no fue auditado contra el
código real. No se verificó si sus referencias a archivos son correctas,
si sus fases son realistas, o si refleja fielmente los 5 factores.

### 9-J. `run_all_validations.py --quick` pendiente

La tabla de estado (línea 272 original) admitía: "pendiente de verificar
post-patches". Esto sigue sin ejecutarse. Sin esta validación, no hay
garantía de que los patches no introdujeran errores de sintaxis o formato.

### 9-K. Conteo de anomalías corregido: 15, no 18

El título original "18 anomalías" contaba el Fallo #5 (formato CHANGELOG)
y el Fallo #9 (mismo problema en otra sección) como anomalías separadas,
inflando artificialmente el número. Conteo real:
- 10 fallos agrupados
- 6 sub-items en Fallo #3
- Fallo #5 y #9 fusionados → 9 fallos reales
- Total: ~15 issues

---

## 10. Acciones recomendadas ANTES de FASE-A

1. Ejecutar `python scripts/run_all_validations.py --quick` y documentar resultado
2. Identificar las 3 referencias a CONTRIBUTING que siguen rotas en el executor
3. Resolver drift VERSION.yaml (4.42.0) vs CHANGELOG.md (4.42.1)
4. Corregir release_date en DOMAIN_PRIMER.md (2026-05-08 → 2026-05-07)
5. Auditar `scripts/validate_agent_ecosystem.py` para no duplicar en FASE-C
6. Validar INTEGRACION-DOCUMENTAL-PLAN.md contra código real antes de ejecutarlo
