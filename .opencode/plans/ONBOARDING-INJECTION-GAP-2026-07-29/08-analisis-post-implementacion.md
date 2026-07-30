# Análisis Post-Implementación — ONBOARDING-INJECTION-GAP-2026-07-29

> **Completar después de la ejecución de cada FASE**
> **Template — los datos de ejecución se llenan al final de cada fase**

---

## 1. Resumen de Ejecución

| Fase | Título | Sesión | Iteraciones | Estado | delegate_task | Completitud |
|------|--------|--------|-------------|--------|---------------|-------------|
| FASE-0-A | Loader + normalize_url + frescura | 2026-07-29 | 1 | ✅ COMPLETADA | ❌ (DIRECTO) | 3/3 tareas, 616 tests OK |
| FASE-0-B | CAMBIO A+B + template url | 2026-07-29 | 1 | ✅ COMPLETADA | ❌ (DIRECTO) | 3/3 tareas, 3 grep checks OK |
| FASE-1 | Taxonomía + deprecación | 2026-07-29 | 1 | ✅ COMPLETADA | ❌ (DIRECTO — 2 one-liners) | 2/2 tareas, 2 grep checks OK |
| FASE-2 | observations.json | 2026-07-29 | 1 | ✅ COMPLETADA | ❌ (DIRECTO) | 3/3 tareas: T0 website + T1 fallback + T2 helper |
| FASE-3 | Tests regresión | 2026-07-29 | 1 | ✅ COMPLETADA | ❌ (DIRECTO — fix + tests) | 3/3 tareas, 27 tests PASS, 0 regresiones |
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
| FASE-1 | ❌ No usado (DIRECTO) | N/A | El plan preveía SUBAGENTE, pero 2 one-liners independientes sin imports no justificaban el overhead. Patch directo en < 1 min: más rápido, más verificable (grep inmediato), sin riesgo de que el subagente malinterprete números de línea desplazados. |
| FASE-2 | ❌ No viable | — | Modificaciones incrementales sobre código reescrito en fase anterior requieren contexto acumulado |
| FASE-3 | ❌ No usado (DIRECTO) | N/A | El plan preveía PARCIAL delegate_task (solo escritura), pero el fix de `_normalize_url()` para URLs sin protocolo requería modificar main.py + ejecutar tests en el mismo contexto. 27 tests en 3 clases, ejecución directa en 0.48s: más rápido y permite depurar en tiempo real. |
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
| §10a | user_provided invisible | Fix 4 | `adr_source="user_provided"` → Tier A | ✅ (codigo) | `'user_provided'` agregado a tuple de `verified_sources` en `scenario_calculator.py` L494. grep confirma presencia. |
| §10b | audit deprecado | Fix 5 | Mensaje sugiere `v4complete` | ✅ (codigo) | 2 mensajes en `main.py` L1120 y L1125 actualizados: `audit --url <URL> --input-data {path}` → `v4complete --url <URL>`. grep `"v4complete --url"` confirma ambas lineas. |
| §10c | observations.json | Fix 6 | Fallback funcional | ✅ (codigo) | T0: 6 websites agregados a observations.json. T1: Fallback en _load_latest_onboarding_data() L3510. T2: _observation_to_onboarding_format() en L3419. Si no hay YAML, busca en observations.json por website normalizado. |

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
| `observations.json` sin campo `website` | Alta | Bajo | Se agrego `website` en FASE-2 T0 a los 6 observations existentes; fallback es silencioso | ✅ Resuelto |
| Tests no importables desde WSL | Media | Medio | Agente principal ejecuta tests con venv Windows | ✅ No ocurrió — `./venv/Scripts/python.exe -m pytest` funcionó sin problemas, 27/27 PASS |
| Regresión en hoteles sin onboarding | Baja | Alto | Si matching falla → defaults (sin cambios de comportamiento) | ⬜ |

---

## 7. Lecciones Aprendidas

_(Completar post-ejecución de todas las fases)_

### Diseño
- _(completar)_

### Ejecución
- **FASE-1 (2 one-liners)**: Cambios atómicos e independientes — si uno falla, el otro no se afecta. Las líneas reales (L1120, L1125) diferían de las documentadas en el plan (L1113, L1118) por desplazamiento post-FASE-0-A/B. Verificar siempre contra código vivo, nunca confiar en números de línea de un plan pre-escrito.
- **FASE-3 (tests de regresión)**: `_normalize_url()` no manejaba URLs sin protocolo (`urlparse("zione.co")` → netloc vacío). Detectado al correr el primer test. Fix de 2 líneas (`if '://' not in url: url = '//' + url`) antes de `urlparse`. Sin este fix, el caso #9 del plan habría fallado silenciosamente. Los tests atraparon el bug antes que producción.
- **FASE-0-A/B**: _(completar según ejecución real)_
- **WSL safety guard**: Bloquea `python3 -c` y pipes con heredocs. Verificación vía `grep` y `search_files` es el fallback confiable.

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
| `website` en observations.json | Baja | Los 6 hoteles ahora tienen `website`. Agregado en FASE-2 T0. | Ninguna — resuelto |
| `_load_latest_onboarding_data()` sin caché | Baja | Iteración O(N) sobre archivos YAML. OK para <50 hoteles. | Indexar si N > 100 |
| `generate_slug()` aún en main.py | Baja | Se mantiene en `run_onboard_mode()` pero ya no en el loader | Sin acción — OK |

---

*Template generado 2026-07-29. Completar después de FASE-RELEASE.*
