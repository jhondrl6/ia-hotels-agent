# Checkpoint FASE-SR-C — Self-Healing Loop CG-CLAIM-VS-EVIDENCE (D-PF2)

**Fecha**: 2026-08-28 · **Plan**: SR-PIPELINE-FIXES-2026-08-27 · **Sesión 3** (~45/60 iteraciones, continuada post-compactación) · **Estado**: ✅ COMPLETADA

## Decisión implementada (D-PF2)

El gate BLOCKING `CG-CLAIM-VS-EVIDENCE` ya no "detecta, loggea y publica igual": al detectar un
claim factualmente falso (p. ej. "el hotel no aparece en Google Maps" con `place_found=True` y
`gbp_rating=4.5`), el diagnóstico se **regenera** usando el `suggestion` del gate como restricción
obligatoria (claim trazable textual) y se **re-valida** con la misma closure de validación
(`_validate_diagnostic` — 0 caminos paralelos). Máx. **1 regeneración** (guard anti-bucle).
Si persiste → `escalated_to_blocked` → **BLOCKED real**: main.py borra 01/02, escribe
`BLOCKED_BY_GATES.md` con la causa y **aborta el ZIP**. El registro "hidden from client" queda
intacto (auditoría) — solo cambió su consecuencia.

### Estrategias del healer (`claim_self_healing.py`)

| Tipo de oración | Estrategia |
|-----------------|------------|
| Condicional (`si…`, `podría`, `a menos que…`) | Intacta — no es claim factual |
| Instrucción al lector / claim de otro sujeto (`usted mismo`, `anote`, sujeto no-GBP) | Neutralizada con sinónimo ("no aparece" → "falta") — no inventa visibilidad |
| Sujeto GBP/Google/búsqueda (el sujeto del gate) | Reemplazada por el **claim trazable textual** del suggestion, preservando prefijo de lista/etiqueta/tabla y puntuación final |

- Escalada vía atributo `last_claim_healing: ClaimHealingResult` (status: `no_needed` /
  `resolved_by_regeneration` / `escalated_to_blocked` + `to_dict()`) — sin parsing de JSON.
- Never-block: excepción del loop → `logger.warning`, la generación continúa (arquitectura intacta).
- Traza persistida: clave `self_healing` en `commercial_gates_report_diagnostic_*.json`
  (consumidores verificados: ninguno lee esa clave).

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/claim_self_healing.py` | **NUEVO** (404 líneas) — `ClaimSelfHealer` (MAX_REGENERATIONS=1, guard anti-bucle con spy de revalidaciones), 3 estrategias de rewrite, constantes de rewrite, `ClaimHealingResult.to_dict()` |
| `modules/quality_gates/commercial_gate.py` | Regexes del gate extraídas a constantes de módulo compartidas (`CLAIM_VS_EVIDENCE_RE`, `CONDITIONAL_MARKERS_RE`) — fuente única de patrones gate↔healer (L-NC10/L27); sin cambio de comportamiento del gate |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Closure única `_validate_diagnostic` + loop self-healing cableado en `generate()`; `self.last_claim_healing`; payload `self_healing` en el JSON de gates |
| `main.py` | 4 ediciones: flag `_claim_escalated`; GATE BLOCKING extendido (`NOT_READY or _claim_escalated`); `BLOCKED_BY_GATES.md` con sección de causa; ZIP abortado si Delivery FAIL **o** `_claim_escalated` |
| `tests/quality_gates/test_claim_self_healing.py` | **NUEVO** (346 líneas) — 20 tests en 6 clases |

## Resultados de test

- Loop self-healing: **20 passed** (corrige claim 5 · instrucciones/otros sujetos 4 · escalado 2 · anti-bucle 3 · trazabilidad 3 · regresión gate 3) → `tests_loop_20passed.txt`
- Suite gates quality (commercial/claim/alignment): **79 passed, 0 failed** → `tests_quality_gates_commercial_claim.txt`
- Diagnostic generator: **27 passed, 0 failed** → `tests_diagnostic_generator.txt`
- Commercial gate + guardián estático L-SR1: **57 passed, 0 failed** → `tests_commercial_gate_static_guards.txt`
- `py_compile` OK (4 archivos tocados); greps de residuos: 0 caminos paralelos de regeneración (lógica solo en `claim_self_healing.py` + 1 punto de cableado); "hidden from client" intacto
- `run_all_validations.py --quick`: **6/6 TOTAL PASS** → `validations_quick_6of6.txt`

## Evidencia

- `fase_sr_c_code_diff.patch` — diff completo de código (3 archivos modificados)
- `new_claim_self_healing.py` / `new_test_claim_self_healing.py` — archivos nuevos completos
- 4 logs de suites pytest + `validations_quick_6of6.txt`

## Desviaciones y notas

- **Test citado no existe**: `tests/commercial_documents/test_commercial_gates.py` del prompt no
  existe en el repo → sustituido por `tests/quality_gates/test_commercial_gate.py` (suite real del
  gate, ya incluida en los 79/57). Registrado en 09 §Notas.
- **Autorrevisión corrigió 2 defectos antes de los tests finales**: `_TRAILING_PUNCT` (hack de
  reversa con `$` anclaba al inicio del original) y `_LIST_PREFIX` con `\s*` que consumía énfasis
  markdown (`*El hotel…` perdía el cierre de itálica).
- **Version Sync resuelto in-session**: `sync_versions.py` actualizó la fecha de 3 headers
  (AGENTS.md, .cursorrules, GUIA_TECNICA.md: 2026-08-24 → 2026-08-28). Causa raíz del FAIL
  preexistente: el patrón de versión (`agents_version:\s*[\d.]+`) no matchea el prefijo "v" de
  `v4.71.0` y no se verifica; el patrón de fecha sí. Fase SR-A/SR-B reportaron 5/6 por esto.
  Los headers NO fueron tocados por la lógica SR-C.
