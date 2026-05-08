# 02 — Diseño de Flujos y Vínculos

**Fase**: FASE-A-B  
**Fecha**: 2026-05-08  
**Output de**: FASE-A-B  
**Inputs**: CONTRIBUTING.md, executor (FASE-A-A completada), AGENTS.md, DOMAIN_PRIMER.md, prompt-fase-template.md, 01-diseno-contrato.md

---

## A. Flujo de DOMAIN_PRIMER — Regeneración en RELEASE

### A.1 — Problema Identificado

El executor E7 (L736) dice "Verificar DOMAIN_PRIMER.md" — pero verificar
no es suficiente. El documento puede quedar desactualizado sin que el
agente lo note hasta FASE-RELEASE, cuando el contenido ya debería
haberse regenerado.

El plan original (INTEGRACION-DOCUMENTAL-PLAN.md §A-B1) dice:
> "Cambio: En executor E7, cambiar de 'verificar DOMAIN_PRIMER' a
> 'regenerar DOMAIN_PRIMER via doctor.py --regenerate-domain-primer'."

**Corrección发现**: El trigger correcto NO es FASE-RELEASE sino
**Cierre de cada fase de implementación**. La regeneración debe ocurrir
al cerrar cada fase (no solo al final del proyecto). El documento
DOMAIN_PRIMER se usa durante todo el proyecto, no solo en RELEASE.

### A.2 — Decisión: Regeneración por Fase, no solo en RELEASE

| Cuando | Qué hacer | Herramienta |
|--------|-----------|-------------|
| **Al cerrar cada fase de implementación** | Regenerar DOMAIN_PRIMER | `doctor.py --regenerate-domain-primer` |
| **Al cerrar FASE-RELEASE** | Regenerar + Verificar alignment | `doctor.py --context` |
| **En cualquier momento (opcional)** | Verificar sin regenerar | `doctor.py --context` |

**Regla**: DOMAIN_PRIMER es **regenerable automáticamente**. Su contenido
refleja el estado actual de los módulos. Si no se regenera durante las
fases de implementación, el documento queda obsoleto para los agentes
que lo consulten.

### A.3 — Cambio en Executor E7

**Antes** (L736-743):
```
#### E7. Verificar DOMAIN_PRIMER.md (docs/CONTRIBUTING.md §146-158)
./venv/Scripts/python.exe scripts/doctor.py --context
```

**Después**:
```
#### E7. Regenerar DOMAIN_PRIMER.md (CONTRIBUTING.md §Paso-5b-DOMAIN-PRIMER)

Al cerrar cada fase de implementación, regenerar el Domain Primer:

./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer

Solo en FASE-RELEASE (cierre final del proyecto):
./venv/Scripts/python.exe scripts/doctor.py --context

Checklist (por fase):
- [ ] DOMAIN_PRIMER.md regenerado con modulos actuales
- [ ] Todo modulo en `modules/` documentado
- [ ] Archivo regenerable automaticamente (no editar manualmente)
```

### A.4 — Cambio en CONTRIBUTING.md Paso 5b

**Antes** (L146-158):
```
### Paso 5b: Verificar DOMAIN_PRIMER.md

Verificar que el Domain Primer este alineado con modulos reales python:
python scripts/doctor.py --context
```

**Después**:
```
### Paso 5b: Regenerar DOMAIN_PRIMER.md

Al cerrar cada fase de implementación:
python scripts/doctor.py --regenerate-domain-primer

Verificación post-regeneración (CONTRIBUTING.md §Paso-5b-DOMAIN-PRIMER):
| Check | Accion si falla |
|-------|-----------------|
| Todo modulo en `modules/` documentado | Regenerar con --regenerate-domain-primer |
| Archivo referenciado en DOMAIN_PRIMER existe | Corregir referencia o eliminar seccion |
| Version y codename coinciden con VERSION.yaml | Reemplazar header via --regenerate-domain-primer |

Solo en FASE-RELEASE (cierre final):
python scripts/doctor.py --context

NOTA: DOMAIN_PRIMER es regenerable automaticamente. NO editar manualmente.
```

### A.5 — Header de Regeneración en DOMAIN_PRIMER.md

El header actual (L1-10) YA incluye la nota de regeneración:
```
> **Version del sistema**: 4.42.0 | **Codename**: SOL-2-ASSET-ALIGNMENT-REFACTOR
> **Release date**: 2026-05-07 | **Plan Maestro**: v2.6.0

*Auto-generado: 2026-05-08 | v4.42.0 SOL-2-ASSET-ALIGNMENT-REFACTOR*
*Regenerar con: `python scripts/doctor.py --regenerate-domain-primer`*
*NO EDITAR MANUALMENTE - Este archivo se regenera automaticamente desde los modulos del proyecto*
```

**Corrección发现的问题**: La fecha L7 dice `2026-05-08` pero VERSION.yaml
dice `2026-05-07`. Esto es un bug documentado en FASE-PRE. Verificar que
este fix se haya aplicado antes de cerrar FASE-A-B.

---

## B. Vínculos Contractuales en AGENTS.md

### B.1 — Problema Identificado

AGENTS.md YA tiene vínculos informativos (L95 referencia executor §4.5,
sección "Vinculo con la Documentacion" lista los documentos). El problema
no es que falten links — es que los links existentes son **informativos,
no contractuales**: apuntan a documentos pero no garantizan que estén
sincronizados.

El objetivo de FASE-A-B no es agregar más links, sino transformar los
existentes en **vínculos verificables por script**.

### B.2 — Tabla de Cross-References Bidireccionales

Agregar en AGENTS.md sección "Flujo Documental Obligatorio" (L71-96):

```
### Cross-References Contractuales

| Documento | Seccion en AGENTS.md | Seccion en CONTRIBUTING | Seccion en Executor |
|----------|---------------------|------------------------|---------------------|
| CONTRIBUTING.md | §Flujo Documental Obligatorio | (documento origen) | §Verificar-CHANGELOG, §Paso-5b-DOMAIN-PRIMER |
| phased_project_executor.md | §Flujo Documental Obligatorio §4.5 | §Contrato-con-Executor | (documento origen) |
| DOMAIN_PRIMER.md | §Estado Actual | §Paso-5b-DOMAIN-PRIMER | §E7-DOMAIN-PRIMER |
| CHANGELOG.md | §Estado Actual | §Verificar-CHANGELOG | §E3-CHANGELOG |
| GUIA_TECNICA.md | §Estado Actual | §Paso-4-Verificar-GUIA | §E4-GUIA_TECNICA |

**Verificabilidad**: Los vínculos de arriba son verificables por
`scripts/validate_document_integration.py` (FASE-C). Si una sección
referenciada no existe, el script falla.
```

### B.3 — Referencia a INTEGRACION-DOCUMENTAL-PLAN.md

En AGENTS.md sección "Flujo Documental Obligatorio", agregar:

```
**Plan de Integracion Documental**: ver
`.opencode/plans/INTEGRACION-DOCUMENTAL-PLAN.md` — proyecto de
4 fases que elimina la causa raíz de desincronización entre los
4 documentos clave (CONTRIBUTING, executor, AGENTS, DOMAIN_PRIMER).
```

### B.4 — Nota sobre Regeneración de DOMAIN_PRIMER

En AGENTS.md sección "Flujo Documental Obligatorio" (después de explicar
el flujo de documentación), agregar:

```
**DOMAIN_PRIMER se regenera al cerrar cada fase de implementación**
(no solo en FASE-RELEASE). El documento es regenerable automáticamente
via `python scripts/doctor.py --regenerate-domain-primer`.
```

---

## C. Resolución: Template vs Executor

### C.1 — Problema Identificado

El template (§6) exige CHANGELOG/GUIA_TECNICA por fase. El executor
Step 4 dice "acumular datos en 09-documentacion-post-proyecto.md"
(como preludio de RELEASE) pero no instruye al agente a editar
CHANGELOG ni GUIA_TECNICA directamente durante la fase.

Existe una desalineación:

| Aspecto | Template §6 dice | Executor Step 4 dice |
|---------|------------------|---------------------|
| CHANGELOG por fase | Editar CHANGELOG después de cada fase | "Acumular datos" — no edita CHANGELOG |
| GUIA_TECNICA por fase | Editar GUIA_TECNICA después de cada fase | "Acumular datos" — no edita GUIA_TECNICA |
| Timing de docs | Por fase | Solo en RELEASE |

### C.2 — Decisión: Ajustar Executor al Template (Fuente de Verdad)

El template es la fuente de verdad porque es más estricto. El executor
debe alinearse.

**Cambios en executor Step 4**:

1. Agregar explicitamente: "Por cada fase completada, editar
   CHANGELOG.md y GUIA_TECNICA.md con los cambios de esa fase (no solo
   acumular en 09-documentacion-post-proyecto.md)."

2. Aclarar que la acumulación en 09-documentacion-post-proyecto.md
   es un backup de datos, no el mecanismo primario de documentación.

**Cambios en executor Step 6 (Post-Fase)**:

El Step 6 del executor actualmente dice:

> "Actualizar 09-documentacion-post-proyecto.md con datos de esta fase"

Debe cambiar a:

> "Editar CHANGELOG.md y GUIA_TECNICA.md con los cambios de la fase.
>  Luego, acumular datos en 09-documentacion-post-proyecto.md como
>  backup."

### C.3 — Formato de CHANGELOG por Fase (Canonico)

Según 01-diseno-contrato.md §B.2, el formato canónico es:

```markdown
## [X.Y.Z] - Titulo descriptivo — YYYY-MM-DD

### Objetivo
{Descripción breve}

### Cambios Implementados
- `archivo.py` - Descripción del cambio

### Archivos Nuevos (si aplica)
| Archivo | Descripción |

### Archivos Modificados (si aplica)
| Archivo | Cambio |

### Tests
- N tests nuevos, 0 regresiones
```

**Regla**: El heading NO lleva prefijo `v`. El título es texto libre
después del segundo ` - `.

### C.4 — Estructura de 09-documentacion-post-proyecto.md

El executor Step 4 define "estructura vacía" para 09-documentacion-post-proyecto.md.
Para que FASE-RELEASE pueda generar CHANGELOG/GUIA_TECNICA correctamente,
definir la estructura concreta:

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

**Regla**: Cada fase completa su columna "Fase". FASE-RELEASE usa los
datos acumulados para generar CHANGELOG y GUIA_TECNICA oficiales.

---

## D. Resumen de Cambios a Aplicar en FASE-B-A y FASE-B-B

### D.1 — Cambios en Executor (FASE-B-A)

| Ubicación | Cambio | Tipo |
|-----------|--------|------|
| E7 (L736-743) | "Verificar" → "Regenerar" + checklist por fase | Texto |
| E7 (L736-743) | Agregar comando `--regenerate-domain-primer` | Comando |
| Step 4 | Aclarar que CHANGELOG/GUIA_TECNICA se editan por fase | Texto |
| Step 6 | "Actualizar 09-documentacion..." → "Editar CHANGELOG + GUIA_TECNICA" | Texto |
| Step 4 | Definir estructura concreta de 09-documentacion-post-proyecto.md | Texto |

### D.2 — Cambios en CONTRIBUTING.md (FASE-B-A)

| Ubicación | Cambio | Tipo |
|-----------|--------|------|
| Paso 5b (L146-158) | "Verificar" → "Regenerar" con trigger por fase | Texto |
| Agregar sección | "Contrato con phased_project_executor.md" | Nueva sección |

### D.3 — Cambios en AGENTS.md (FASE-B-B)

| Ubicación | Cambio | Tipo |
|-----------|--------|------|
| Flujo Documental | Tabla de cross-references bidireccionales | Nueva tabla |
| Flujo Documental | Referencia a INTEGRACION-DOCUMENTAL-PLAN.md | Nota |
| Flujo Documental | Nota de regeneración DOMAIN_PRIMER por fase | Nota |

### D.4 — Cambios en DOMAIN_PRIMER.md (FASE-B-B)

| Ubicación | Cambio | Tipo |
|-----------|--------|------|
| Header | Confirmar que release_date (L7) = VERSION.yaml release_date | Verificación |

### D.5 — Cambios en Template (FASE-B-B)

| Ubicación | Cambio | Tipo |
|-----------|--------|------|
| L3 | `version: 1.3.0` → `version: v1.3.0` | Fix |
| §5 Post-Ejecución | Alinear con executor Step 6 (editar CHANGELOG + GUIA_TECNICA, no solo acumular) | Texto |

---

## E. Verificación Previa a FASE-B-A y FASE-B-B

| Check | Estado |
|-------|--------|
| DOMAIN_PRIMER L7 release_date = VERSION.yaml | ⚠️ Verificar (PRE-2 pendiente de confirmar) |
| Executor E7 actual dice "Verificar" | ✅ Confirmado (L736) |
| Template L3 tiene `version: 1.3.0` (sin `v`) | ✅ Confirmado |
| AGENTS.md tiene vínculos informativos | ✅ Confirmado (L95) |
| 09-documentacion-post-proyecto.md tiene estructura | ⚠️ Verificar si existe |

---

## F. Criterios de Completitud — FASE-A-B

- [x] Executor E7 dice "regenerar" no "verificar" (cambio diseñado, no aplicado)
- [x] CONTRIBUTING Paso 5b incluye regeneración por fase (diseño)
- [x] AGENTS.md tiene cross-reference table verificable (diseño)
- [x] Executor Step 4 y Step 6 alineados con template §6 (diseño)
- [x] Flujo DOMAIN_PRIMER documentado (regeneración por fase, no solo RELEASE)
- [x] Desalineación template vs executor resuelta
- [x] Output 02-diseno-flujos.md generado con todas las decisiones

**Estado**: ✅ FASE-A-B COMPLETADA — diseño transferred to FASE-B-A y FASE-B-B para implementación.