# Análisis Post-Implementación — ONBOARDING-INJECTION-GAP-2026-07-29

> **Completar después de FASE-RELEASE**
> **Template — los datos de ejecución se llenan al final de cada fase**

---

## 1. Resumen de Ejecución

| Fase | Título | Sesión | Iteraciones | Estado | delegate_task | Completitud |
|------|--------|--------|-------------|--------|---------------|-------------|
| FASE-0-A | Loader + normalize_url + frescura | 2026-07-29 | 1 | ✅ COMPLETADA | ❌ (DIRECTO) | 3/3 tareas, 616 tests OK |
| FASE-1 | Taxonomía + deprecación | — | — | ⬜ | ✅ SUBAGENTE | — |
| FASE-2 | observations.json | — | — | ⬜ | ❌ (DIRECTO) | — |
| FASE-3 | Tests regresión | — | — | ⬜ | ⚠️ PARCIAL | — |
| FASE-RELEASE | v4complete + release | — | — | ⬜ | ⚠️ MIXTO | — |

---

## 2. Fase de Mayor Complejidad Técnica: FASE-0

### ¿Por qué fue la más compleja?

1. **Reescritura de función core**: `_load_latest_onboarding_data()` pasó de ~50 líneas con matching por slug a ~55 líneas con matching por URL + fallback + frescura
2. **Tres puntos de modificación**: `run_onboard_mode()` (CAMBIO A), `run_v4_complete_mode()` (CAMBIO B), `_load_latest_onboarding_data()` (CAMBIO C) — todos en `main.py` (146KB)
3. **Nueva función auxiliar**: `_normalize_url()` con 5 reglas de normalización
4. **5 bugs resueltos simultáneamente**: B1, B2, N3, N4, N5

### Mitigaciones aplicadas
- _(completar post-ejecución)_
- Diseño determinístico: URL como clave canónica inmutable
- `_normalize_url()` es función pura — 5 reglas fijas, sin side effects
- Comportamiento degradado seguro: si matching falla → defaults regionales (mismo que antes)

### Qué funcionó
- Patch unico en `main.py`: reemplazo de la funcion completa + adicion de `_normalize_url()` en una sola operacion
- LSP diagnostico detecto `os` no importado → corregido agregando `import os` local en el bloque de frescura
- 616 tests pasan sin regresiones (2 failures pre-existentes en `test_llm_mention_checker` y `test_coherence_generated_assets`)
- `git stash` confirmo que los failures son pre-existentes (no introducidos por FASE-0-A)

### Qué no funcionó / pitfalls
- `import main` bloqueado por safety guard de WSL → verificacion via `grep` y `pytest` en su lugar
- `test_llm_mention_checker.py::test_default_model_from_registry` falla (pre-existente, OpenRouter model deprecado)

---

## 3. delegate_task Viability — Lecciones Aprendidas

| Fase | ¿Se usó? | ¿Funcionó? | Lección |
|------|----------|------------|---------|
| FASE-0-A | ❌ No viable | — | Funciones core con modificaciones multi-punto requieren contexto completo del flujo bimodal. Patch directo en 1 operacion: ~60 lineas reemplazadas. |
| FASE-1 | _(completar)_ | _(completar)_ | _(completar)_ |
| FASE-2 | ❌ No viable | — | Modificaciones incrementales sobre código reescrito en fase anterior requieren contexto acumulado |
| FASE-3 | _(completar)_ | _(completar)_ | _(completar)_ |
| FASE-RELEASE | _(completar)_ | _(completar)_ | v4complete en subagente: ¿timeout? ¿WSL venv funcionó? |

---

## 4. Matriz de Verificación de Hallazgos

| # | Hallazgo | Fix | Verificación en output | PASS/FAIL | Evidencia |
|---|----------|-----|------------------------|-----------|-----------|
| B1 | Slug mismatch | CAMBIO A+C | "Onboarding data loaded: N campos" en log | ✅ (codigo) | Loader reescrito con glob+URL matching. Falta CAMBIO A (FASE-0-B) para que YAML tenga `hotel.url`. |
| B2 | Frescura 24h | Fix 3 | Datos 2026-07-23 no rechazados | ✅ (codigo) | Ventana hardcodeada eliminada. `ONBOARDING_FRESHNESS_HOURS` opt-in implementado. |
| N3 | hotel_url ignorado | CAMBIO C | `hotel_url` usado en matching | ✅ (codigo) | Loader lee `data['hotel']['url']` de cada YAML y normaliza para matching. |
| N4 | output_dir hardcodeado | CAMBIO B | `output_dir` parametrizado | ⬜ | _(completar en FASE-0-B)_ |
| N5 | Sin identity resolver | CAMBIO A+C | URL como clave canónica | ✅ (parcial) | `_normalize_url()` implementada como resolvedor canónico. Falta CAMBIO A para persistir URL. |
| §10a | user_provided invisible | Fix 4 | `adr_source="user_provided"` → Tier A | ⬜ | _(completar)_ |
| §10b | audit deprecado | Fix 5 | Mensaje sugiere `v4complete` | ⬜ | _(completar)_ |
| §10c | observations.json | Fix 6 | Fallback funcional | ⬜ | _(completar)_ |

---

## 5. Métricas de Éxito

| Métrica | Antes (Tier B) | Esperado (Tier A) | Real | PASS/FAIL |
|---------|---------------|-------------------|------|-----------|
| rooms | 10 | **34** | ⬜ | ⬜ |
| adr_cop | 420,000 | **290,000** | ⬜ | ⬜ |
| occupancy_rate | 0.512 | **0.784** | ⬜ | ⬜ |
| direct_channel_pct | 0.2 | **0.4** | ⬜ | ⬜ |
| evidence_tier | B | **A** | ⬜ | ⬜ |
| ROICR | 0.7x | **1.3x** | ⬜ | ⬜ |
| Fuga realista/mes | $3.7M | **$7.2M** | ⬜ | ⬜ |
| Pain ratio | 5.2% | **1.9%** | ⬜ | ⬜ |

---

## 6. Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación | ¿Ocurrió? |
|--------|-------------|---------|------------|-----------|
| v4complete timeout (900s) | Media | Alto | Verificar archivos parciales; re-ejecutar si necesario | ⬜ |
| WSL venv no ejecutable por subagente | Media | Alto | Subagente usa `terminal()` con path Windows explícito | ⬜ |
| YAMLs viejos sin `hotel.url` rompen matching | Alta | Medio | Loader retorna None → mismo comportamiento que antes | ⬜ |
| `observations.json` sin campo `website` | Alta | Bajo | Se agrega `website` en FASE-2; fallback es silencioso | ⬜ |
| Tests no importables desde WSL | Media | Medio | Agente principal ejecuta tests con venv Windows | ⬜ |
| Regresión en hoteles sin onboarding | Baja | Alto | Si matching falla → defaults (sin cambios de comportamiento) | ⬜ |

---

## 7. Lecciones Aprendidas

_(Completar post-ejecución de todas las fases)_

### Diseño
- _(completar)_

### Ejecución
- _(completar)_

### delegate_task
- _(completar)_

### WSL + Windows venv
- _(completar)_

### Qué se haría diferente
- _(completar)_

---

## 8. Deuda Técnica Identificada

| Item | Severidad | Descripción | Acción recomendada |
|------|-----------|-------------|-------------------|
| `website` en observations.json | Baja | Los 6 hoteles existentes pueden no tener `website`. Se agregó para Zi One Luxury en FASE-2. | Backfill para los 5 restantes |
| `_load_latest_onboarding_data()` sin caché | Baja | Iteración O(N) sobre archivos YAML. OK para <50 hoteles. | Indexar si N > 100 |
| `generate_slug()` aún en main.py | Baja | Se mantiene en `run_onboard_mode()` pero ya no en el loader | Sin acción — OK |

---

*Template generado 2026-07-29. Completar después de FASE-RELEASE.*
