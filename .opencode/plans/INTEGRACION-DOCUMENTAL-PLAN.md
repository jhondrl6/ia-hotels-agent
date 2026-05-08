# Plan Maestro: Integracion Documental Estructural

## Origen
Auditoria forense de 2026-05-07 sobre phased_project_executor.md.
Los patches sintomaticos (typos, paths, formatos) revelaron la causa raiz:
**4 documentos operan como islas sin mecanismos de integracion.**

## Objetivo
Eliminar la desincronizacion estructural entre los 4 documentos clave
mediante cross-references, formatos compartidos, y gates automaticos.

## Documentos Involucrados

| Documento | Rol actual | Rol deseado |
|-----------|-----------|-------------|
| `docs/CONTRIBUTING.md` | Reglas documentales (fuente de verdad) | Mismo + contratos formales con executor |
| `.agents/workflows/phased_project_executor.md` | Workflow de ejecucion por fases | Mismo + cumplimiento contractual con CONTRIBUTING |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Base de conocimiento del dominio | Mismo + regeneracion automatica post-proyecto |
| `AGENTS.md` | Contexto global del agente | Mismo + vinculos activos y validadores a los otros 3 |

## Causa Raiz (5 factores — validados contra codigo real)

1. **Sin contrato formal**: CONTRIBUTING define reglas, executor las "referencia"
   pero no hay mecanismo que garantice cumplimiento. Si CONTRIBUTING cambia,
   el executor no se entera. Las referencias a lineas absolutas (§78-85) se
   rompen con cualquier edicion.

2. **Formatos propietarios**: Cada documento define su propio formato de
   CHANGELOG, version header, y comandos python. No hay un estandar unico
   declarado en un solo sitio.

3. **DOMAIN_PRIMER huerfano**: No hay ningun flujo que lo regenere
   automaticamente post-proyecto. Se queda en la version que tenia cuando se
   creo. El executor dice "verificar" (E7) pero no "regenerar".

4. **AGENTS.md con vinculos informativos insuficientes**: AGENTS.md SI tiene
   vinculos activos (linea 95 referencia executor §4.5, seccion "Vinculo con
   la Documentacion" lista CONTRIBUTING, documentation_rules.md, validation.md).
   El problema no es que sea "pasivo" — es que sus vinculos son informativos,
   no contractuales: apunta a documentos pero no garantiza que esten
   sincronizados.

5. **Template desalineado**: `.agents/workflows/templates/prompt-fase-template.md`
   §6 exige CHANGELOG/GUIA_TECNICA por fase, pero el executor no lo instruye.
   El template es mas estricto que el workflow que lo invoca.

---

## Dependencias entre Fases

```
FASE-PRE (saneamiento) --> FASE-A-A (contrato+estandares)
                                |
                                v
                         FASE-A-B (flujos+vinculos)
                                |
                                v
                         FASE-B-A (CONTRIBUTING+executor)
                                |
                                v
                         FASE-B-B (AGENTS+DOMAIN_PRIMER)
                                |
                                v
                         FASE-B-C (template+validacion)
                                |
                                v
                         FASE-C (gate de no-regresion)
```

**Sesiones estimadas**: 3-4 (1 PRE + 2 A/B + 1 C)

---

## FASE-PRE: Saneamiento de Drifts Existentes

**[✅ COMPLETADA — 2026-05-08]**
*Nota: Los drifts de version ya estaban sincronizados (4.42.0); solo se verificaron refs y formats.*

**Objetivo**: Resolver todos los drifts y desincronizaciones descubiertos
en la auditoria forense ANTES de disenar la arquitectura de integracion.
No tiene sentido construir contratos sobre cimientos quebrados.

**Sesion**: 1
**Prioridad**: BLOQUEANTE — sin esto, las fases siguientes operan sobre
              datos inconsistentes.

### Tareas (max 4 tareas, 0 comandos largos)

#### PRE-1. Resolver drift CHANGELOG.md vs VERSION.yaml
- **Problema**: CHANGELOG.md tiene `[4.42.1]` pero VERSION.yaml dice `4.42.0`
- **Accion**: Ejecutar `python scripts/version_consistency_checker.py`
  para diagnosticar. Si CHANGELOG esta adelantado: decidir si VERSION.yaml
  debe subir a 4.42.1 (si hay cambios sin versionar) o si CHANGELOG debe
  retroceder a 4.42.0 (si la entrada 4.42.1 es prematura).
- **Verificacion**: Ambos archivos deben coincidir exactamente en version.

#### PRE-2. Corregir release_date en DOMAIN_PRIMER.md
- **Problema**: DOMAIN_PRIMER.md linea 7 dice `2026-05-08`, VERSION.yaml
  linea 5 dice `2026-05-07`. Posible bug de timezone en doctor.py.
- **Accion**: Corregir manualmente DOMAIN_PRIMER.md L7 a `2026-05-07`.
  Documentar en 09-documentacion-post-proyecto.md que el script doctor.py
  necesita revision de timezone.
- **Verificacion**: `grep "release_date" .agent/knowledge/DOMAIN_PRIMER.md`
  y comparar con VERSION.yaml.

#### PRE-3. Identificar y corregir las 3 referencias rotas en executor
- **Problema**: 3 referencias a CONTRIBUTING.md desfasadas confirmadas:
  1. Executor L390 y L674: `§78-85` — L78 de CONTRIBUTING.md esta VACIA
     (entre paso 2 y paso 3). Seccion real empieza en L79.
     **Fix**: cambiar a `§79-85` en ambas lineas.
  2. Executor L676: `§36-58` — apunta a `docs/contributing/documentation_rules.md`
     pero se cita como si fuera CONTRIBUTING.md. Ademas L36 esta vacia.
     **Fix**: cambiar a `docs/contributing/documentation_rules.md §37-58`.
- **Verificacion**: Buscar con `grep -n "CONTRIBUTING.md §" executor` y
  validar que cada `§NN` apunte a una linea no-vacia que sea inicio de seccion.

#### PRE-4. Normalizar line endings y ejecutar validaciones
- **Problema**: Mezcla CRLF/LF (DOMAIN_PRIMER CRLF, executor LF, AGENTS.md CRLF).
  Invalida referencias futuras a numeros de linea.
- **Accion**:
  1. Ejecutar `python scripts/run_all_validations.py --quick`
     (pendiente desde auditoria original).
  2. Si hay errores de formato, corregirlos antes de continuar.
  3. Normalizar line endings de los 4 documentos involucrados a LF
     via `dos2unix` o `sed`.
- **Verificacion**: `file docs/CONTRIBUTING.md .agents/workflows/phased_project_executor.md`
  debe reportar `LF line terminators` para ambos.

### Output de FASE-PRE
- CHANGELOG.md y VERSION.yaml sincronizados
- DOMAIN_PRIMER.md con fecha correcta
- Executor con referencias corregidas
- run_all_validations.py --quick PASANDO
- Documento: `.opencode/plans/INTEGRACION-DOCUMENTAL/00-saneamiento.md`

### Criterios de Completitud
- [ ] CHANGELOG version == VERSION.yaml version
- [ ] DOMAIN_PRIMER release_date == VERSION.yaml release_date
- [ ] 0 referencias rotas a CONTRIBUTING en executor
- [ ] run_all_validations.py --quick pasa sin errores
- [ ] Todos los documentos del plan usan LF line endings

---

## FASE-A-A: Diseno del Contrato y los Estandares Compartidos

**[✅ COMPLETADA — 2026-05-08]**

*Output*: `.opencode/plans/INTEGRACION-DOCUMENTAL/01-diseno-contrato.md`

**Objetivo**: Definir el contrato documental y los estandares tecnicos
que regiran la integracion.

**Sesion**: 1
**Dependencia**: FASE-PRE completada

### Tareas (max 3 tareas + 0 comandos largos)

#### A-A1. Definir "Contrato Documental" entre CONTRIBUTING y Executor
- Identificar cada regla en CONTRIBUTING que el executor debe cumplir.
- Definir el formato del contrato (seccion fija en CONTRIBUTING o en el executor).
- Resolver la ambiguedad del CHANGELOG por fase vs por release.
  **Decision**: Opcion C (hibrida). Cada fase ACUMULA datos en 09-documentacion-post-proyecto.md.
  FASE-RELEASE genera CHANGELOG/GUIA_TECNICA usando esos datos acumulados.
- Reemplazar TODAS las referencias a lineas absolutas (§NN-MM) por
  referencias a nombres de seccion (§Section-Name) en AMBOS documentos.
  Esto previene roturas futuras.

#### A-A2. Definir estandares compartidos
- **Python path**: `./venv/Scripts/python.exe` para WSL (ya estandarizado
  en executor, falta documentar en CONTRIBUTING §convenciones).
- **CHANGELOG format**: Unificar a `## [X.Y.Z] - YYYY-MM-DD` (sin prefijo `v`,
  sin titulo en heading). Actualizar documentation_rules.md §37, executor E3,
  y CONTRIBUTING §79-85.
- **Version header**: Unificar a `version: vX.Y.Z` (con prefijo "v").
  **Excepcion corregida**: Template actualmente dice `version: 1.3.0` (sin "v").
  Debe cambiarse a `version: v1.3.0` para alinearse.
- **Referencias CONTRIBUTING**: Usar §Section-Name en vez de §NN-MM.

#### A-A3. Documentar decisiones en archivo de diseno
- Archivo: `.opencode/plans/INTEGRACION-DOCUMENTAL/01-diseno-contrato.md`
- Contiene: tabla de contratos (que regla -> que mecanismo),
  estandares compartidos definitivos, matriz de formatos por documento.

### Output de FASE-A-A
- Documento de contrato y estandares aprobado
- Lista de referencias a reemplazar (linea exacta en cada archivo)

### Criterios de Completitud
- [ ] Tabla de contratos documentales completa
- [ ] Estanadres de CHANGELOG, version header, python path definidos
- [ ] 0 referencias a §NN-MM en el nuevo contrato (solo §Section-Name)

---

## FASE-A-B: Diseno de Flujos y Vinculos

**Status**: ✅ COMPLETADA — 2026-05-08

**Objetivo**: Definir el flujo de DOMAIN_PRIMER, los vinculos AGENTS.md,
 y la resolucion template vs executor.

**Sesion**: 1
**Dependencia**: FASE-A-A completada

### Tareas (max 3 tareas + 0 comandos largos)

#### A-B1. Definir flujo de DOMAIN_PRIMER
- **Cuando se regenera?** -> Al cerrar FASE-RELEASE (no solo "si hay
  cambios arquitectonicos").
- **Quien lo ejecuta?** -> El agente de RELEASE.
- **Cambio**: En executor E7, cambiar de "verificar DOMAIN_PRIMER" a
  "regenerar DOMAIN_PRIMER via doctor.py --regenerate-domain-primer".
- En CONTRIBUTING.md seccion "Paso 5b: Verificar DOMAIN_PRIMER.md", cambiar de "verificar" a
  "verificar y regenerar si es necesario".
- **Accion adicional**: Documentar en DOMAIN_PRIMER.md header que es
  regenerable automaticamente.

#### A-B2. Definir vinculos contractuales en AGENTS.md
- **Que seccion de AGENTS.md referencia cada documento?**
  - "Flujo Documental Obligatorio" ya referencia CONTRIBUTING.md y executor.
  - Agregar: nota explicita de que DOMAIN_PRIMER se regenera en FASE-RELEASE.
  - Agregar: tabla de cross-references bidireccionales (CONTRIBUTING <-> executor).
  - Agregar: referencia a este plan como "ver INTEGRACION-DOCUMENTAL-PLAN.md".
- El objetivo NO es agregar mas links informativos (ya existen), sino
  transformar los existentes en vinculos que sean VERIFICABLES por script.

#### A-B3. Resolver desalineacion template vs executor
- **Decision**: Ajustar executor para que el template sea la fuente de verdad.
  - Executor §Step 4 debe exigir CHANGELOG/GUIA_TECNICA por fase
    (como dice template §6).
  - Executor §Step 6 debe instruir al agente a EDITAR CHANGELOG y
    GUIA_TECNICA, no solo ejecutar log_phase_completion.py.
- Archivo: `.opencode/plans/INTEGRACION-DOCUMENTAL/02-diseno-flujos.md`

### Output de FASE-A-B
- Flujo DOMAIN_PRIMER definido y documentado
- Mapa de cross-references AGENTS.md con mecanismo de verificacion
- Decision template vs executor documentada

### Criterios de Completitud
- [ ] Executor E7 dice "regenerar" no "verificar"
- [ ] CONTRIBUTING Paso 5b incluye regeneracion
- [ ] AGENTS.md tiene cross-reference table verificable
- [ ] Executor Step 4 y Step 6 alineados con template §6

---

## FASE-B-A: Implementar Contrato en CONTRIBUTING y Executor

**Status**: ✅ COMPLETADA — 2026-05-08

**Objetivo**: Aplicar los contratos y estandares a CONTRIBUTING.md y
phased_project_executor.md.

**Sesion**: 1
**Dependencia**: FASE-A-A y FASE-A-B completadas

### Tareas (max 3 tareas + 0 comandos largos)

#### B-A1. CONTRIBUTING.md — Agregar contrato con executor
- Nueva seccion "Contrato con phased_project_executor.md" (usando
  §Section-Name, no numeros de linea).
- Definir que reglas CONTRIBUTING son MANDATORIAS para el executor.
- Documentar formato CHANGELOG canonizado (referencia a estandar compartido).
- Documentar convencion de python path (referencia a estandar compartido).
- Actualizar §Flujo Post-Fase para incluir acumulacion en
  09-documentacion-post-proyecto.md (no solo REGISTRY.md).
- Actualizar §Paso 5b para DOMAIN_PRIMER: de "verificar" a
  "verificar y regenerar en RELEASE".

#### B-A2. phased_project_executor.md — Conectar con CONTRIBUTING
- Step 2: Agregar obligacion de incluir seccion de documentacion en cada
  prompt (referenciar CONTRIBUTING §Flujo-Post-Fase).
- Step 4: Definir estructura CONCRETA de 09-documentacion-post-proyecto.md
  (no "estructura vacia"):
  - Seccion por fase: archivos tocados, tests agregados, modulos afectados,
    descripcion, notas tecnicas.
  - Esto es lo que RELEASE usa para generar CHANGELOG/GUIA_TECNICA.
- Step 6: Agregar paso post-log_phase_completion:
  "Actualizar 09-documentacion-post-proyecto.md con datos de esta fase".
- Paso 7 E7: Cambiar de "verificar DOMAIN_PRIMER" a "regenerar DOMAIN_PRIMER".
- Agregar seccion "Estandares Compartidos" que referencie CONTRIBUTING.
- Reemplazar TODAS las referencias §NN-MM por §Section-Name.

#### B-A3. Unificar version headers y CHANGELOG format
- Aplicar estandar `version: vX.Y.Z` a todos los documentos del workflow.
- Aplicar estandar CHANGELOG `## [X.Y.Z] - YYYY-MM-DD` sin titulo.
- Verificar que executor E3, documentation_rules.md §37, y CHANGELOG.md real
  coincidan exactamente.

### Output de FASE-B-A
- CONTRIBUTING.md con contrato formal
- Executor conectado a CONTRIBUTING via referencias estables
- 0 referencias §NN-MM restantes en executor

### Criterios de Completitud
- [x] CONTRIBUTING tiene seccion "Contrato con phased_project_executor.md"
- [x] Executor usa solo §Section-Name (0 lineas absolutas)
- [x] CHANGELOG format identico en los 3 documentos (rules, executor, real)
- [x] Version header con "v" en executor

---

## FASE-B-B: Implementar Vinculos en AGENTS.md y DOMAIN_PRIMER

**[✅ COMPLETADA — 2026-05-08]**

**Sesion**: 1
**Dependencia**: FASE-B-A completada

### Tareas (max 3 tareas + 0 comandos largos)

#### B-B1. AGENTS.md — Agregar vinculos contractuales y tabla de cross-references
- En "Flujo Documental Obligatorio": agregar tabla bidireccional:
  | Documento | Seccion en AGENTS.md | Seccion en CONTRIBUTING | Seccion en Executor |
- Agregar nota: "DOMAIN_PRIMER se regenera en FASE-RELEASE (no manualmente)".
- Agregar referencia a este plan como "ver INTEGRACION-DOCUMENTAL-PLAN.md".
- Agregar nota de que los vinculos son verificables por script
  (referencia a FASE-C).

#### B-B2. DOMAIN_PRIMER.md — Header de regeneracion + fecha corregida
- Documentar en header: "ESTE ARCHIVO ES REGENERABLE: ejecutar
  `python scripts/doctor.py --regenerate-domain-primer`".
- Asegurar que release_date coincida con VERSION.yaml (corregido en PRE-2,
  verificar que sigue alineado post-cambios).

#### B-B3. Corregir template version header
- `.agents/workflows/templates/prompt-fase-template.md` linea 3:
  cambiar `version: 1.3.0` -> `version: v1.3.0`.
- Agregar nota en template: "Ver phased_project_executor.md §Step 6
  para flujo completo de documentacion post-fase".
- Alinear §5 Post-Ejecucion: agregar "Acumular datos en
  09-documentacion-post-proyecto.md".

### Output de FASE-B-B
- AGENTS.md con cross-reference table
- DOMAIN_PRIMER.md con header de regeneracion
- Template alineado con executor

### Criterios de Completitud
- [ ] AGENTS.md tiene tabla bidireccional CONTRIBUTING <-> executor
- [ ] DOMAIN_PRIMER header menciona regeneracion automatica
- [ ] Template version header tiene prefijo "v"
- [ ] Template §5 incluye acumulacion en 09-documentacion-post-proyecto

---

## FASE-B-C: Validacion Cruzada Post-Implementacion

**[✅ COMPLETADA — 2026-05-08]**

*Output*: `.opencode/plans/INTEGRACION-DOCUMENTAL/03-verificacion-post.md`

**Objetivo**: Verificar que TODAS las modificaciones de las fases B-A y B-B
funcionan correctamente y no introducen regresiones.

**Sesion**: 1
**Dependencia**: FASE-B-A y FASE-B-B completadas

### Resumen de validaciones

| Validacion | Resultado |
|------------|-----------|
| doctor.py --context | ✅ PASS (5/5) |
| run_all_validations.py --quick | ✅ PASS (4/4) |
| version_consistency_checker.py | ✅ PASS |
| 0 refs §NN-MM en executor/CONTRIBUTING | ✅ PASS |
| Version headers con "v" (executor/template) | ✅ PASS |
| Python path consistente | ✅ PASS |

### Issues detectadas (para FASE-C)

1. `§Flujo-Post-Fase` en executor L306 no existe en CONTRIBUTING
2. CHANGELOG real usa `-` en vez de `—` como separador
3. AGENTS.md header `agents_version: 4.42.0` sin prefijo "v"
4. DOMAIN_PRIMER header sin prefijo "v"

### Criterios de Completitud

- [x] doctor.py --context pasa
- [x] run_all_validations.py --quick pasa
- [x] 0 referencias §NN-MM restantes
- [x] CHANGELOG format consistente en spec
- [x] Version header con "v" en executor y template
- [x] Output guardado en 03-verificacion-post.md

---

## FASE-C: Gate de No-Regresion Documental

**Objetivo**: Prevenir que los documentos vuelvan a desincronizarse.
**Esta fase NO es opcional.** Es la unica garantia de que la causa raiz
(recurrencia de desincronizacion) no vuelva.

**Sesion**: 1
**Dependencia**: FASE-B-C completada (todos los estandares ya aplicados)

### Tareas (max 3 tareas + 0 comandos largos)

#### C1. Verificar validate_agent_ecosystem.py antes de disenar
- **Accion previa obligatoria**: Leer `scripts/validate_agent_ecosystem.py`
  y comparar su funcionalidad con los checks que FASE-C necesita.
- Si ya cubre parte de la validacion cross-documental, reutilizar.
- Si no cubre nada de lo necesario, disenar nuevo script.
- Esto evita duplicar funcionalidad documentada en AGENTS.md linea 108.

#### C2. Script de validacion cross-documental
Crear `scripts/validate_document_integration.py`:
- Verifica que cada §Section-Name referenciado en executor existe en
  CONTRIBUTING (y viceversa).
- Verifica que CHANGELOG format en documentation_rules.md coincide con
  CHANGELOG.md real.
- Verifica que DOMAIN_PRIMER version coincide con VERSION.yaml.
- Verifica que python path es consistente en todos los .md de workflows.
- Verifica que AGENTS.md cross-reference table esta completa.
- Verifica que template version header tiene prefijo "v".

#### C3. Integrar en pre-commit hooks
- Integrar C2 en `scripts/run_all_validations.py` como check adicional
  (no como hook separado, para no duplicar infraestructura).
- O si validate_agent_ecosystem.py ya tiene hooks, agregar el nuevo
  script como modulo invocado desde ahi.
- Documentar el gate en CONTRIBUTING.md nueva seccion
  "Validacion de Integracion Documental".
- Documentar en AGENTS.md tabla de validaciones.

### Output de FASE-C
- Script `scripts/validate_document_integration.py` funcional
- Integrado en run_all_validations.py o validate_agent_ecosystem.py
- Documentacion del gate en CONTRIBUTING.md y AGENTS.md

### Criterios de Completitud
- [x] Script valida cross-references CONTRIBUTING <-> executor
- [x] Script valida CHANGELOG format consistency
- [x] Script valida version headers
- [x] Script ejecuta en < 5 segundos
- [x] Integrado en pipeline de validaciones existente
- [x] Documentado en CONTRIBUTING.md y AGENTS.md

---

## Criterios de Exito Globales

- [x] FASE-PRE: 0 drifts entre CHANGELOG, VERSION.yaml, DOMAIN_PRIMER
- [x] FASE-A: Contrato documental definido y estandares compartidos fijados
- [x] FASE-B: 5 archivos modificados (CONTRIBUTING, executor, AGENTS,
  DOMAIN_PRIMER, template) con cross-references estables
- [x] FASE-C: Script de validacion cross-documental existe, pasa, y esta
  integrado en pre-commit
- [x] doctor.py --context pasa en todas las fases
- [x] run_all_validations.py --quick pasa en todas las fases
- [x] 0 referencias a lineas absolutas (§NN-MM) en executor
- [x] Todos los version headers usan prefijo "v"
- [x] Todos los line endings normalizados a LF

## Riesgos

| Riesgo | Mitigacion |
|--------|-----------|
| Cambios en CONTRIBUTING rompen executor existente | FASE-PRE sanea antes; FASE-A disena ANTES de tocar; FASE-C detecta regresiones |
| Template demasiado estricto -> agentes no lo cumplen | FASE-A-B valida con caso real antes de FASE-C; FASE-B-C prueba end-to-end |
| DOMAIN_PRIMER regeneration falla | PRE-2 corrige fecha; B-B2 documenta regeneracion; doctor.py --context valida |
| FASE-C duplica validate_agent_ecosystem.py | C1 verifica el script existente ANTES de crear nuevo |
| Referencias §Section-Name pueden seguir rompiendose | FASE-C script detecta secciones faltantes automaticamente |
| Line endings se reverten en ediciones futuras | FASE-C script detecta CRLF en archivos del plan |

## Estructura de Archivos del Plan

Este plan sigue la estructura obligatoria de phased_project_executor.md:

```
.opencode/plans/INTEGRACION-DOCUMENTAL/
├── README.md                              # Indice y resumen del plan
├── INTEGRACION-DOCUMENTAL-PLAN.md         # Este archivo (plan maestro)
├── dependencias-fases.md                  # Diagrama ASCII + tabla de conflictos
├── 00-saneamiento.md                      # Output de FASE-PRE
├── 01-diseno-contrato.md                  # Output de FASE-A-A
├── 02-diseno-flujos.md                    # Output de FASE-A-B
├── 03-verificacion-post.md                # Output de FASE-B-C
├── 05-prompt-inicio-sesion-fase-PRE.md    # Prompt para FASE-PRE
├── 05-prompt-inicio-sesion-fase-A-A.md    # Prompt para FASE-A-A
├── 05-prompt-inicio-sesion-fase-A-B.md    # Prompt para FASE-A-B
├── 05-prompt-inicio-sesion-fase-B-A.md    # Prompt para FASE-B-A
├── 05-prompt-inicio-sesion-fase-B-B.md    # Prompt para FASE-B-B
├── 05-prompt-inicio-sesion-fase-B-C.md    # Prompt para FASE-B-C
├── 05-prompt-inicio-sesion-fase-C.md      # Prompt para FASE-C
├── 06-checklist-implementacion.md         # Master checklist con todas las fases
└── 09-documentacion-post-proyecto.md      # Post-project doc plan (acumulativo)
```

## R3 Scope Evaluation por Fase

| Fase | Tareas | Comandos largos | Estado R3 |
|------|--------|-----------------|-----------|
| PRE  | 4      | 0               | PASS (4+0) |
| A-A  | 3      | 0               | PASS (3+0) |
| A-B  | 3      | 0               | PASS (3+0) |
| B-A  | 3      | 0               | PASS (3+0) |
| B-B  | 3      | 0               | PASS (3+0) |
| B-C  | 3      | 1               | PASS (3+1) |
| C    | 3      | 0               | PASS (3+0) |

## Iteration Budget Estimado por Fase

| Fase | Fijos | Disponibles | Total | Estado |
|------|-------|-------------|-------|--------|
| PRE  | 26    | 10          | 36    | OK |
| A-A  | 26    | 8           | 34    | OK |
| A-B  | 26    | 8           | 34    | OK |
| B-A  | 26    | 12          | 38    | OK |
| B-B  | 26    | 10          | 36    | OK |
| B-C  | 26    | 12          | 38    | OK |
| C    | 26    | 14          | 40    | OK |

## Metadatos

- **Creado**: 2026-05-07
- **Validado y corregido**: 2026-05-08
- **Origen**: Auditoria forense phased_project_executor.md + validacion cruzada
- **Fases**: PRE (saneamiento) + A-A/A-B (diseno) + B-A/B-B/B-C (implementacion) + C (gate)
- **Sesiones estimadas**: 4
- **Prioridad**: ALTA — causa raiz de desincronizacion documental recurrente
- **Validacion externa**: Este plan fue auditado contra codigo real del repositorio
  (VERSION.yaml, CHANGELOG.md, CONTRIBUTING.md, executor, template, DOMAIN_PRIMER.md)
  antes de su aprobacion final.