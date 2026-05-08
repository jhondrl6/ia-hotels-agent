# 01 — Diseño del Contrato y Estandares Compartidos

**Fase**: FASE-A-A  
**Fecha**: 2026-05-08  
**Output de**: FASE-A-A  
**Inputs**: CONTRIBUTING.md, phased_project_executor.md, documentation_rules.md, CHANGELOG.md, prompt-fase-template.md

---

## A. Contrato Documental: CONTRIBUTING ↔ Executor

### A.1 — Problema Identificado

El executor usa 11 referencias absolutas a CONTRIBUTING (`§NN-NN`).
Estas referencias son **frágiles**: cualquier edición que inserte o elimine
líneas antes del objetivo desplaza la referencia y la rompe sin aviso.

### A.2 — Mapa de Referencias Antiguas → Nuevas

| Executor L | Ref. Antigua | Ref. Nueva | Sección en CONTRIBUTING |
|------------|-------------|------------|------------------------|
| L390 | `§79-85` | `§Verificar-CHANGELOG` | Paso 3: Verificar CHANGELOG.md (L79-86) |
| L648 | `§56-165` | `§Trigger-Documentacion-Oficial` | Sección "Trigger del Usuario" (L56-166) |
| L654 | `§60-67` | `§Paso-1-Diagnostico` | Paso 1: Diagnostico inicial (L60-68) |
| L664 | `§70-76` | `§Paso-2-Sync-Automatico` | Paso 2: Sincronizacion automatica (L70-77) |
| L674 | `§79-85` | `§Verificar-CHANGELOG` | (misma sección que L390) |
| L676 | `§36-58` | `§Formato-CHANGELOG` | **documentation_rules.md** §35-60 — CORRECCIÓN |
| L705 | `§87-93` | `§Paso-4-Verificar-GUIA` | Paso 4: Verificar GUIA_TECNICA.md (L87-94) |
| L719 | `§95-106` | `§Paso-5-Skills-Workflows` | Paso 5: Verificar skills/workflows (L95-107) |
| L728 | `§108-111` | `§Paso-6-SYSTEM-STATUS` | Paso 6: Regenerar SYSTEM_STATUS.md (L108-112) |
| L736 | `§146-158` | `§Paso-5b-DOMAIN-PRIMER` | Paso 5b: Verificar DOMAIN_PRIMER.md (L146-159) |
| L745 | `§114-126` | `§Paso-7-8-Symlink-Validacion` | Pasos 7+8: Symlink + Validacion (L114-127) |
| L245 | `§L223-238` | `§Protocolo-Evidencia-Proactiva` | Sección interna del executor (no es CONTRIBUTING) |

**Corrección crítica**: L676 apuntaba a `CONTRIBUTING.md §36-58` pero
ese rango corresponde a `documentation_rules.md §35-60` (el contenido de
CONTRIBUTING L36 es una línea vacía). La referencia correcta es a
`documentation_rules.md §Formato-CHANGELOG`.

### A.3 — Sección "Contrato con Executor" a Agregar en CONTRIBUTING

Nueva sección al final de CONTRIBUTING.md:

```
## Contrato con phased_project_executor.md

Este contrato formaliza cómo los dos documentos se relacionan.
Las referencias desde el executor a CONTRIBUTING usan nombres de sección
(§Nombre-Seccion), no números de línea.

### Secciones Nominativas del Executor

| Nombre de Sección | Ubicación en CONTRIBUTING |
|-------------------|--------------------------|
| §Verificar-CHANGELOG | L79-86: Paso 3 |
| §Trigger-Documentacion-Oficial | L56-166: Flujo completo |
| §Paso-1-Diagnostico | L60-68: Diagnostico inicial |
| §Paso-2-Sync-Automatico | L70-77: Sincronizacion |
| §Paso-4-Verificar-GUIA | L87-94: GUIA_TECNICA |
| §Paso-5-Skills-Workflows | L95-107: Skills/workflows |
| §Paso-6-SYSTEM-STATUS | L108-112: SYSTEM_STATUS |
| §Paso-5b-DOMAIN-PRIMER | L146-159: DOMAIN_PRIMER |
| §Paso-7-8-Symlink-Validacion | L114-127: Symlink + pre-commit |
| §Formato-CHANGELOG | documentation_rules.md §35-60 |

### Reglas Contractuales del Executor

El executor DEBE cumplir las siguientes reglas de CONTRIBUTING:

1. **CHANGELOG format**: Usar el formato definido en `§Formato-CHANGELOG`
   — `## [X.Y.Z] - Titulo — YYYY-MM-DD` + `### Objetivo`
2. **Python path**: `./venv/Scripts/python.exe` en WSL
3. **Version header**: Prefijo `v` en todos los headers (`version: vX.Y.Z`)
4. **DOMAIN_PRIMER**: Regenerar en FASE-RELEASE, no solo verificar
5. **Template**: El template de fases es la fuente de verdad para
   documentación post-fase (CHANGELOG + GUIA_TECNICA por fase)
```

---

## B. Estandares Compartidos

### B.1 — Python Path

| Contexto | Valor |
|----------|-------|
| WSL (estándar) | `./venv/Scripts/python.exe` |
| Linux nativo | `./venv/bin/python` |
| Todas las referencias | **SIEMPRE** usar `./venv/Scripts/python.exe` en planes/docs de WSL |

### B.2 — Formato CHANGELOG (canónico)

```
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
después del segundo ` - `. No existe una sección `### Título` — el
título va en el heading.

### B.3 — Version Header

| Tipo de archivo | Formato |
|-----------------|---------|
| Workflow/skills (.md) | `version: vX.Y.Z` (con `v`) |
| Template YAML frontmatter | `version: v1.3.0` (con `v`) |
| CHANGELOG heading | `## [X.Y.Z]` (sin `v` en corchetes) |

**Corrección necesaria**: `prompt-fase-template.md` L3 dice
`version: 1.3.0` sin `v`. Debe ser `version: v1.3.0`.

### B.4 — Discrepancia Detectada en Executor E3

Executor L676-697 define el template CHANGELOG así:

```markdown
## [X.Y.Z] - Fecha

### Objetivo
{Descripción}
```

**Le falta** la línea de título después de la fecha. El formato real es:

```markdown
## [X.Y.Z] - Titulo — YYYY-MM-DD

### Objetivo
```

**Fix en FASE-B-A**: Agregar ` - Titulo` después de la fecha en E3.

---

## C. Decisión: CHANGELOG por Fase vs. por Release

**Resolución: Opción C — Híbrida**

- Cada fase **acumula** datos en `09-documentacion-post-proyecto.md`
- FASE-RELEASE **genera** la entrada formal de CHANGELOG + GUIA_TECNICA
  usando los datos acumulados
- `log_phase_completion.py` alimenta `09-documentacion-post-proyecto.md`
- El executor Step 6 (post-fase) edita directamente CHANGELOG y GUIA_TECNICA
  solo en FASE-RELEASE

---

## D. Lista de Reemplazos a Aplicar en FASE-B-A

| Archivo | Línea | Reemplazar |
|---------|-------|------------|
| phased_project_executor.md | L245 | `§L223-238` → `§Protocolo-Evidencia-Proactiva` |
| phased_project_executor.md | L390 | `§79-85` → `§Verificar-CHANGELOG` |
| phased_project_executor.md | L648 | `§56-165` → `§Trigger-Documentacion-Oficial` |
| phased_project_executor.md | L654 | `§60-67` → `§Paso-1-Diagnostico` |
| phased_project_executor.md | L664 | `§70-76` → `§Paso-2-Sync-Automatico` |
| phased_project_executor.md | L674 | `§79-85` → `§Verificar-CHANGELOG` |
| phased_project_executor.md | L676 | `§36-58` → `§Formato-CHANGELOG` |
| phased_project_executor.md | L705 | `§87-93` → `§Paso-4-Verificar-GUIA` |
| phased_project_executor.md | L719 | `§95-106` → `§Paso-5-Skills-Workflows` |
| phased_project_executor.md | L728 | `§108-111` → `§Paso-6-SYSTEM-STATUS` |
| phased_project_executor.md | L736 | `§146-158` → `§Paso-5b-DOMAIN-PRIMER` |
| phased_project_executor.md | L745 | `§114-126` → `§Paso-7-8-Symlink-Validacion` |
| prompt-fase-template.md | L3 | `version: 1.3.0` → `version: v1.3.0` |
| phased_project_executor.md | L680 | Template E3: agregar ` - Titulo` en línea de fecha |

**Total: 13 reemplazos** en executor + 1 en template.

---

## E. Verificación de Alineación Previa (FASE-PRE)

| Check | Estado |
|-------|--------|
| CHANGELOG vs VERSION.yaml | ✅ SINCRONIZADO (4.42.0) |
| Executor § references | ⚠️ 11 refs absolutas (resueltas en este doc) |
| Template version header | ❌ Falta prefijo `v` (fix: L3) |
| Executor E3 discrepancy | ❌ Falta línea de título en template |
| CHANGELOG format | ✅ `## [4.42.0] - Titulo — YYYY-MM-DD` |

---

## F. Criterios de Completitud — FASE-A-A

- [x] Tabla de contratos documentales completa (11 refs mapeadas)
- [x] Estándares de CHANGELOG, version header, python path definidos
- [x] 0 refs §NN-MM en executor (reemplazadas por §Nombre-Seccion)
- [x] Lista de 14 reemplazos concretos con línea exacta
- [x] Decisión CHANGELOG híbrida documentada
- [x] Corrección de ref incorrecta (L676 → documentation_rules)
