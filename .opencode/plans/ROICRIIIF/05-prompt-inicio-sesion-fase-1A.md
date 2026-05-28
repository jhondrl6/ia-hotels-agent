# FASE-1A: Gate Presence Diagnostic (GATE-PRESENCE Root Cause Analysis)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (solo lectura, sin patches)
> **Complejidad**: 🟡 MEDIA (lectura + trazabilidad)
> **RAM-friendly**: Usar execute_code para batching de greps; read_file con offset/limit
> **Estado**: ✅ COMPLETADA — 2026-05-28

## Contexto previo

ROICRIII (v4.57.0) dejó publication readiness bloqueado. El detector de WhatsApp funciona correctamente (conditional_generator skippa whatsapp_button con presence_status=EXISTS), pero el publication gate lo reporta como `missing` sin `presence_verified` flag.

**Esta fase es SOLO DIAGNÓSTICO**: no se toca código, solo se lee y se documenta un "fix recipe" para FASE-1B.

## Objetivo de esta fase

Identificar la causa raíz exacta del silent failure en el publication gate y producir un documento de "fix recipe" con:
- Líneas exactas a modificar
- Código actual vs código propuesto (diff)
- Justificación técnica de cada cambio

### Tareas (lectura sin parcheo)

- [ ] **T1 — Leer publicación_gates.py (gate's SitePresenceChecker)**:
  ```
  # RAM-saving: usar execute_code para batch
  read_file(path='modules/quality_gates/publication_gates.py', offset=850, limit=60)
  ```
  Identificar:
  - ¿Cómo invoca el gate su SitePresenceChecker?
  - ¿El try/except L872-881 traga excepciones? (ver `except Exception` vs `except SomeError`)
  - ¿Se usa `assessment.get("site_presence_report")` (L855)?
  - ¿Qué pasa si el pre-built report tiene whatsapp_button=EXISTS? ¿El gate lo consume o lo ignora?

- [ ] **T2 — Trazar data flow site_presence_report (batch grep)**:
  ```python
  # execute_code — 1 tool call en vez de 5+
  from hermes_tools import search_files
  greps = [
      ('site_presence_report', 'publication_gates.py'),
      ('site_presence_report', 'main.py'),
      ('site_presence_report', 'assessment_builder.py'),
      ('site_presence_report', 'proposal_asset_alignment.py'),
      ('presence_verified', 'proposal_asset_alignment.py'),
      ('present_in_production', 'proposal_asset_alignment.py'),
  ]
  results = {}
  for pattern, file_glob in greps:
      results[f"{pattern}@{file_glob}"] = search_files(pattern, file_glob=file_glob, path='/mnt/c/Users/Jhond/Github/iah-cli/modules', limit=10)
  print(json.dumps(results, indent=2))
  ```
  Objetivo: mapear dónde se produce `site_presence_report` y dónde se consume.

- [ ] **T3 — Leer proposal_asset_alignment.py (alignment logic)**:
  ```
  read_file(path='modules/asset_generation/proposal_asset_alignment.py', offset=215, limit=120)
  ```
  Identificar:
  - Función `verify_proposal_asset_alignment()` — sus parámetros
  - ¿Recibe site_presence_report como argumento?
  - ¿Cómo marca assets como "present_in_production"? (L261-272 en contexto)
  - ¿Qué dict structure espera?

- [ ] **T4 — Leer assessment_builder.py (how report is injected)**:
  ```
  read_file(path='modules/assessment_builder.py', offset=220, limit=25)
  ```
  Verificar `with_site_presence()` signature y qué key del assessment dict escribe.

- [ ] **T5 — Documentar fix recipe** (output de esta fase):
  Crear archivo temporal: `/tmp/roicriiif-fase-1a-fix-recipe.md` con:
  ```markdown
  # FASE-1A Fix Recipe: GATE-PRESENCE Root Cause

  ## Root Cause identificado:
  [Una de: (a) try/except silent, (b) pre-built report not consumed, (c) URL mismatch, (d) method signature incorrecta]

  ## Evidencia (líneas exactas):
  - [archivo:linea] — [qué dice el código]
  - [archivo:linea] — [data flow gap identificado]

  ## Cambios propuestos:
  ### Patch 1: [archivo]
  - ANTES: [código actual]
  - DESPUÉS: [código propuesto]
  - Justificación: [por qué]

  ### Patch 2: [archivo] (si aplica)
  ...

  ## Tests a escribir:
  1. test_XYZ_with_prebuilt_report: [descripción]
  2. test_XYZ_without_prebuilt_fallback: [descripción]

  ## Riesgos:
  - [qué podría fallar con esta estrategia]
  ```

### Restricciones

- ❌ NO modificar código fuente — SOLO lectura y análisis
- ❌ NO ejecutar tests (no hay código nuevo aún)
- ❌ NO ejecutar v4complete
- ✅ Usar offset/limit en read_file para no cargar archivos enteros a contexto
- ✅ Usar execute_code para batching de greps (reduce tool calls en ~5x)
- ✅ Documentar con evidencias citables (archivo:línea)

### Criterios de completitud

- [x] Root cause identificada con evidencia (cita archivo:línea)
- [x] Data flow `site_presence_report` mapeado completo (ConditionalGenerator → assessment → gate)
- [x] Fix recipe creado en `/tmp/roicriiif-fase-1a-fix-recipe.md` con diffs concretos
- [x] Al menos 1 test plan documentado con escenarios
- [x] Cascade mínima: REGISTRY.md marca ROICRIIIF-FASE-1A como completada
- [x] `log_phase_completion.py` ejecutado con `--fase ROICRIIIF-FASE-1A`

### RAM-Saving Tactics para esta fase

| Tactic | Cómo aplicar |
|--------|-------------|
| Batch greps | 1 execute_code con N search_files en vez de N tool calls |
| Scoped reads | offset/limit en vez de read_file completo |
| No code into context | Leer 60 líneas a la vez, máximo |
| Summary over dump | Fix recipe como resumen ejecutivo, no transcripción |
| Defer implementation | Todo el "qué" documentado; el "cómo" queda a FASE-1B |

### Próxima sesión

FASE-1B: Implementación del fix con el recipe de FASE-1A. Con receta clara, POSIBLE uso de delegate_task.
