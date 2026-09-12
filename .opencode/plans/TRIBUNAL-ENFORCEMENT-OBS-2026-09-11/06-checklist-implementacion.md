# 06 — Checklist de Implementación: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: Una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Fuente de estado**: este archivo + `dependencias-fases.md`.

---

## Estado Global

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 0 | Precondición: FASE-RELEASE-4.76.0 (predecesor) | ✅ Completada | 2026-09-11 | 2026-09-11 | — | v4.76.0 publicada (local, sin push) + archivado R2.5 en `bd2bf57` — puerta de P1 abierta |
| 1 | FASE-P1 | ⬜ Pendiente | — | — | — | Decisión Q1–Q4 + contrato del veredicto enriquecido + ACs finales |
| 2 | FASE-P2 | ⬜ Pendiente | — | — | — | Refactor de ordenamiento (solo si Q1=sí; opción O1/O2/O3) |
| 3 | FASE-P3 | ⬜ Pendiente | — | — | — | Fixes: AC8 + tier acta + barreda D-V.1 + versión acta |
| 4 | FASE-P4 | ⬜ Pendiente | — | — | — | Corrida observación Tier A + informe (requiere datos reales T3) |
| 5 | FASE-RELEASE-4.77.0 | ⬜ Pendiente | — | — | — | Cierre + archivado R2.5 |

---

## Checklist por Fase

### Precondición — FASE-RELEASE-4.76.0 del predecesor

- [x] VERSION.yaml = 4.76.0 y `version_consistency_checker.py` pasa (hook pre-commit `bd2bf57`, 5/5 en verde)
- [x] Plan TRIBUNAL-OFFLINE-2026-09-09 archivado en `Archives/` (R2.5, 12 renombres, `--quick` 8/8 post-archivado)
- [x] Endosos D-V.1 (whitelist barreda) y D-V.3 (executor) ejecutados o explícitamente reasignados a este plan
  - D-V.3 **ejecutado**: executor v2.20.0 → v2.21.0 con R2.6 y R2.7. Ninguna de las dos tiene verificador
    mecánico todavía → esa parte queda **reasignada a P1** (ver §Deuda de proceso).
  - D-V.1 **reasignado**: la whitelist del emisor barreda es FASE-P3; `test_barreda_un_solo_emisor_de_la_clave`
    sigue en rojo y v4.76.0 se publicó así, con la limitación declarada.

### FASE-P1 — Decisión y contrato

- [ ] `evidence/FASE-P1/research-estado.md` con mapa confirmado símbolo-por-símbolo (R2.2)
- [ ] Q1 (¿enforcement?) decidida con el usuario
- [ ] Q2 (opción O1/O2/O3) y Q2b (remediación AC8) decididas — o O4 documentado
- [ ] Q3 (secuenciación) y Q4 (hotel + datos T3) decididas
- [ ] `evidence/FASE-P1/decision-enforcement.md` con contrato del veredicto enriquecido + rationale (formato DA-*)
- [ ] ACs finales con artefacto + clave (R2.4) fijados en `01-plan-maestro.md` §6
- [ ] `06-checklist` + `dependencias-fases` actualizados con lo decidido
- [ ] `log_phase_completion.py --fase FASE-P1` ejecutado (SIN `--release`)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] NO modificó código de producción
- [ ] Commit de cierre de fase

### FASE-P2 — Refactor de ordenamiento (solo si Q1=sí)

- [ ] Opción elegida implementada (O1/O2/O3) manteniendo never-block
- [ ] Camino de bloqueo ejercitado: recomendación BLOQUEAR de revisor → ZIP no emitido (AC-E2)
- [ ] `acta_revision.json` → `reviewer_reports` no vacío con los 4 revisores (AC-E1)
- [ ] Never-block: fallo de un revisor no rompe la corrida (AC-E3)
- [ ] NR3: una sola ruta de bloqueo (grep en `main.py`)
- [ ] NR2: tribunal no reimplementa gates (grep en `tribunal/*.py`)
- [ ] Tests retro sobre `output/` vivo + corrida E2E del predecesor
- [ ] Baseline pre/post medido con instrumento (NR1)
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P3 — Fixes localizados

- [ ] AC8: `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only real (AC-F1, sonda re-ejecutable)
- [ ] `evidence_tier` del acta == MANIFEST en corrida real (AC-F2)
- [ ] Whitelist barreda test-only (AC-F3, D-V.1)
- [ ] `acta_writer.py` lee versión de `VERSION.yaml`
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P4 — Corrida de observación Tier A

- [ ] Datos operativos reales recibidos con fuente declarada (T3)
- [ ] Corrida v4complete + onboarding ejecutada (delegate_task, exit 0)
- [ ] Informe `evidence/FASE-P4/informe-observacion.md` con los 7 puntos del plan maestro §5
- [ ] Provisionalidad de `APROBADO-PARA-ENTREGA` registrada si enforcement no cerrado
- [ ] Delta vs corrida E2E del predecesor (R2.3)
- [ ] NO se usó como entrega a cliente

### FASE-RELEASE-4.77.0 — Cierre

- [ ] ACs certificados contra artefacto real (patrón VERIFY, AC-V1)
- [ ] VERSION.yaml → 4.77.0 + `sync_versions.py` + CHANGELOG + GUIA_TECNICA
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.77.0 --release 4.77.0`
- [ ] Plan archivado en `Archives/` (R2.5) + commit único de cierre

---

## Deuda de proceso — dueño: FASE-P1 (heredada del R2.5 del predecesor, medida 2026-09-11)

Ninguno de estos es código de producción. Son gates que dan ✅ sobre lo que no miden; P1 debe
decir cuáles entran al alcance de este plan y cuáles se documentan como límite declarado.

- [ ] **R2.6 y R2.7 sin verificador mecánico**: dos reglas obligatorias del executor v2.21.0 que hoy
  solo sostienen la disciplina de quien escribe. R2.7 es la que se puede instrumentar ya (la resta
  `suma_post − suma_pre == tests_nuevos` sobre dos conteos canónicos).
  - **Límite medido de R2.6 (2026-09-11)**: su baseline (`output/FASE-D_salentoreal_post_guard/`) está
    **fuera del repo** — la regla `output/*` de `.gitignore` lo excluye y `git ls-files` devuelve 0
    archivos. En un clon limpio el `skipif` de `test_honesty_reviewer_retro_reales.py` se cumple y el
    test **no corre**: la regla es inejecutable fuera de esta máquina. P1 debe decidir si se versiona
    un fixture mínimo (con hash y procedencia), si se documenta el requisito de entorno, o si R2.6 se
    publica como límite declarado.
- [ ] **`validate_plan_closure.py` cubre 1 de 8 planes (12,5 %)**: solo lee `10-analisis` de planes
  vivos y solo dispara si el encabezado dice `COMPLETADO`. La regla L-R.3 sigue siendo letra muerta.
- [ ] **Campo `Version actual` del REGISTRY lo escribe una persona**: `log_phase_completion.py` no lo
  toca (0 hits en `scripts/*.py`), así que la cura es un writer o un verificador, no el edit manual
  que se hizo en este release (L-R.2).
- [ ] **`validate_opencode_refs.py --fix` reescribe a ciegas**: hace `text.replace` sobre todo el
  archivo y destruye comandos históricos de planes ya archivados (en el predecesor convirtió el
  `git mv` del `05-prompt` en una ruta sin sentido y devolvió `[PASS]`). Workaround usado: escribir
  la ruta como plantilla `<PLAN>`. Arreglo propuesto: no reescribir dentro de bloques de código.
- [ ] **`version_consistency_checker.py` no lee encabezados `FASE-RELEASE-x.y.z`**: su regex excluye
  `.`, así que la fase recién registrada es invisible y reporta `FASE-T4-A`. Hoy es informativo
  (el check solo exige encontrar *alguna* fase), pero el hook muestra una fase equivocada.
- [ ] **L-R.1: la columna `Iteraciones` de este checklist no obliga a medir**. En el predecesor 8 de 9
  fases cerraron con `⚠️ sin medir (R2.1)` y aun así con ✅ de fase; el instrumento
  (`evidence/FASE-D/measure_iterations.py`) funcionó sin obstáculo alguno cuando se usó (RELEASE:
  31 ids / 43 `tool_use` con corte en `6bbdba7`). La cura exigida por la lección es una casilla
  obligatoria "Iteraciones (ids + tool_use, corte = commit de código)" por fase, de modo que un `—`
  impida cerrar el ✅. En este plan la columna existe pero admite el `—` sin consecuencia.

---

## Cierre del plan

- [ ] Todas las fases ✅
- [ ] ACs finales certificados
- [ ] NR1–NR6 sin violaciones
- [ ] Plan archivado (R2.5)
- [ ] `10-analisis-post-implementacion.md` completo (lecciones, decisiones, métricas)
- [ ] v4.77.0 publicada
