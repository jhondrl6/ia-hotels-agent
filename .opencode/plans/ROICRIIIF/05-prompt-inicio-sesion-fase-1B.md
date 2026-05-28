# FASE-1B: Gate Presence Fix Implementation (Usando Fix Recipe de FASE-1A)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: ✅ SUBAGENTE (delegate_task) — diagnóstico ya hecho, implementación mecánica
> **Complejidad**: 🟡 MEDIA (aplicación de recipe documentado)
> **RAM-friendly**: delegate_task aísla el contexto del subagente

## Contexto previo

FASE-1A completó el diagnóstico. El fix recipe está en `/tmp/roicriiif-fase-1a-fix-recipe.md` (o fue presentado al final de la sesión FASE-1A).

**Este archivo debe ser leído ANTES de generar el prompt de delegate_task** para inyectar la receta exacta en el subagente.

## Objetivo de esta fase

Implementar el fix del publication gate usando la receta de FASE-1A, escribir tests, verificar backward compatibility, y completar cascade de documentación.

### Flujo de sesión (parent agent)

1. **Leer fix recipe**: `read_file(path='/tmp/roicriiif-fase-1a-fix-recipe.md')` — extraer root cause y diffs propuestos
2. **Construir prompt de delegate_task**: Inyectar la receta COMPLETA en el prompt (self-contained)
3. **Delegar ejecución**: Con timeout razonable (~300s suficiente para patches + tests)
4. **Verificar resultados del subagente**: Confirmar tests pasan y no regresión

### Prompt para delegate_task (template — completar con fix recipe de FASE-1A)

```
Eres un agente de implementación de fixes para iah-cli.

OBJETIVO: Implementar fix del publication gate que no reconoce assets pre-existentes.

TRABAJO DIRECTO EN: /mnt/c/Users/Jhond/Github/iah-cli/

== ROOT CAUSE (de FASE-1A) ==
{INSERTAR SECCIÓN "Root Cause identificado" del fix recipe — texto literal}

== EVIDENCIA ==
{INSERTAR SECCIÓN "Evidencia" del fix recipe — citas archivo:línea}

== PATCHES A APLICAR ==
{INSERTAR SECCIÓN "Cambios propuestos" del fix recipe — ANTES/DESPUÉS literal}

== TESTS A ESCRIBIR ==
{INSERTAR SECCIÓN "Tests a escribir" del fix recipe — escenarios}

== INSTRUCCIONES DE EJECUCIÓN ==

1. Activar venv: cd /mnt/c/Users/Jhond/Github/iah-cli/ && source venv/bin/activate

2. Aplicar cada patch del fix recipe usando la herramienta patch (NO sed/awk)

3. Escribir tests en tests/ (archivo apropiado, e.g., tests/test_publication_gates_presence.py):
   - Test 1: asset con presence_status=EXISTS en pre-built report → counted as present_in_production
   - Test 2: asset sin pre-built report → fallback al gate's own checker (backward compat)
   - Usar mocks de SitePresenceChecker según los scenarios del fix recipe

4. Ejecutar tests: pytest tests/ -k "presence OR alignment OR gate" -v
   - Todos deben pasar
   - Si falla alguno: diagnosticar y ajustar (máx 2 intentos)

5. Validación de no-regresión: pytest tests/ -x --timeout=60 (o sin --timeout si no soportado)

6. Validación rápida: python scripts/run_all_validations.py --quick

== RESTRICCIONES ==

- NO modificar SitePresenceChecker ni ConditionalGenerator (funcionan correctamente)
- NO ejecutar v4complete (eso es FASE-4)
- Usar herramienta patch (no terminal sed/awk) para ediciones
- Priorizar pre-built report sobre re-chequeo; fallback a propio checker si no hay pre-built
- Verificar con grep que los cambios NO afectan otros sites/gates

== ENTREGABLES ==

- Lista de archivos modificados con diff summary
- Test file creado (path)
- Resultado de pytest (pass/fail con counts)
- Resultado de run_all_validations --quick
- Si algo falla: diagnóstico detallado con error completo
```

### Tareas (parent agent)

- [ ] **T1 — Leer fix recipe**: Leer `/tmp/roicriiif-fase-1a-fix-recipe.md` y extraer secciones clave
- [ ] **T2 — Construir prompt**: Completar el template de arriba con datos del fix recipe
- [ ] **T3 — Delegar a subagente**: Ejecutar delegate_task (timeout ~300-400s, toolsets: ['terminal', 'file'])
- [ ] **T4 — Verificar resultados**:
  - Tests pasan: revisar output de pytest
  - No regresión: revisar output de run_all_validations
  - Si subagente reporta problemas: NO reintentar en esta sesión — escalar a usuario
- [ ] **T5 — Cascade docs**:
  - Actualizar dependencias-fases.md (FASE-1B ✅)
  - Actualizar 06-checklist-implementacion.md (FASE-1 completa = 1A + 1B)
  - Actualizar REGISTRY.md
  - Ejecutar `log_phase_completion.py` con `--fase FASE-1B`

### Restricciones

- El subagente NO debe intentar re-diagnosticar (el diagnóstico ya está hecho en FASE-1A)
- Si el fix recipe tiene ambigüedades, el subagente debe aplicar la opción más conservadora
- Si los tests fallan después de 2 intentos, el subagente debe abortar y reportar (no reinventar)
- Parent agent NO debe cargar código fuente a contexto (el subagente lo maneja)

### Criterios de completitud

- [ ] Fix recipe aplicado correctamente (patches en archivos indicados)
- [ ] Tests nuevos pasan (≥2)
- [ ] run_all_validations.py --quick sin errores nuevos
- [ ] No regresión en tests existentes
- [ ] Subagente reportó success con evidencia (output de pytest)
- [ ] Cascade de docs actualizada (dependencias-fases.md, 06-checklist, REGISTRY)
- [ ] `log_phase_completion.py` ejecutado con `--fase FASE-1B`

### Ventaja de delegate_task aquí

La FASE-1B es **implementation over known recipe** — el trabajo pesado (debug, hipótesis, evidencia) ya lo hizo FASE-1A. El subagente solo tiene que:
1. Aplicar diffs conocidos
2. Escribir tests planificados
3. Ejecutar validaciones

Esto aísla el contexto del subagente (su RAM) del parent agent, reduciendo presión en la sesión principal.

### Próxima sesión

FASE-2: Asset Confidence Enrichment — direct execution, análisis iterativo de DOM scraping + scoring.
