# FASE-P1: Decisión de Enforcement + Contrato del Veredicto Enriquecido

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P1
**Objetivo**: Decidir con el usuario (Q1–Q5 y Q1b) si el tribunal debe enforcear y mediante qué opción (O1–O4), fijar el contrato del veredicto enriquecido (cómo `_compute_verdict` consume `reviewer_reports`, **qué ocurre aguas abajo del bloqueo** y **cómo el acta distingue los tres estados de un revisor**) y los ACs finales del plan. **Sesión de decisión: sin código de producción.**
**Dependencias**: FASE-RELEASE-4.76.0 del plan TRIBUNAL-OFFLINE-2026-09-09 ✅ (cerrada 2026-09-11; plan archivado R2.5. **Higiene de cita corregida 2026-09-14**: el commit vivo es `3bdc14e` en `origin/master`; el `bd2bf57` citado originalmente es su duplicado pre-rebase y solo sobrevive en la rama local `backup/pre-sanidad-evidence-20260912`. v4.76.0 **ya está en origin** — el "sin push" de esta cabecera era cierto solo hasta el rebase — y su tag anotado `v4.76.0` (creado 2026-09-14) está **empujado a origin desde el 2026-09-14**)
**Complejidad técnica**: **MEDIA** — decisión arquitectónica + de producto cross-module
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: decisión que afecta el flujo de entrega completo.
**Skill**: `phased_project_executor.md` **v2.24.0** (la cabecera citaba v2.21.0 — versión de concepción. Desde entonces: v2.22.0 añadió el gate del Paso 0 con `00-lecciones-capitalizadas.md`, v2.23.0 ascendió NR7/NR8 a §R2.8/§R2.9 y §R2.10 fijó el orden del cierre, v2.23.1 corrigió la premisa de R2.10. R2.6/R2.7 siguen **sin verificador mecánico** — deuda de esta fase)

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| TRIBUNAL-OFFLINE-2026-09-09 (9/9) | ✅ Cerrado 2026-09-11 — certificación 15 ✅ + **AC8 ❌**, que abre este plan. Documentos en `Archives/TRIBUNAL-OFFLINE-2026-09-09/` (R2.5) |
| FASE-RELEASE-4.76.0 (predecesor) | ✅ Completada 2026-09-11 en `3bdc14e` — v4.76.0 **ya en `origin/master`** (la nota "sin push" de la concepción quedó superada por el rebase) y con tag anotado `v4.76.0` creado 2026-09-14; `--quick` **8/8** *(medición de ese día: el suite tenía ocho checks; hoy son **9** desde `4ac139a`, no es un dato desactualizado que deba corregirse)*; precondición de esta fase cumplida |
| `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` (ajeno a este plan) | ✅ Cerrado 2026-09-13 en `4ac139a` (V1 `42b12a1`, V2 `e02a688`): existe `scripts/validate_lesson_capitalization.py`, cableado como `[7/7]` del hook versionado y `[9/9]` de `--quick`. **A este plan no le corta nada**: está fechado 2026-09-11, bajo el corte `2026-09-12`, y el checker lo publica como `1 exentos por fecha anterior a 2026-09-12`. Su `00-` sí es conforme (es uno de los dos testigos reales de la suite) |
| Deuda de gates medida en ese R2.5 + Paso 0 horizontal | ⚠️ **Heredada a P1** — **8 ítems abiertos** (eran 9; el «Paso 0 sin verificador mecánico» quedó `[x]` el 2026-09-12 por el plan de acá arriba): 6 del R2.5 (R2.6/R2.7 sin verificador mecánico + baseline de R2.6 fuera del repo, `validate_plan_closure.py` 1/8, `Version actual` del REGISTRY escrita a mano, reescrito ciego de `validate_opencode_refs.py --fix`, regex de `version_consistency_checker.py`, y L-R.1 — **esta última ya aplicada a este plan**) + 2 del Paso 0 horizontal (normalización del flaky de orden en R2.7, Tier A inalcanzable en `v4complete`) |
| Deuda que **llega** del plan PASO0 y no estaba al escribir este prompt | (a) **«Verificador de conteos declarados en §4»**, con dueño FASE-P1 y la **premisa corregida**: la discordancia 19-declaradas / 18-filas que lo justificaba nunca existió — medido con `_filas` del propio verificador, ese `00-` tiene **19 y 19** y el del otro plan **18 y 18** (el 18 era de otro archivo, familia L-V2.3). P1 debe **re-justificarlo con un caso real o retirarlo**, no heredarlo. (b) **D-V2.1**: `evidence/FASE-D/measure_iterations.py` no alcanza el transcript de sesión bajo el cliente actual, así que la columna `Iteraciones` de este checklist se llenará con **auto-reporte y unidad declarada** (lo que R2.1 autoriza) y no con el instrumento |
| FASE-P1 | ← ESTA FASE |

### Resumen del estado certificado (FASE-VERIFY)

- El tribunal **audita pero no enforcea**: `reviewer_reports` queda `[]` porque el Juez corre antes del packaging y los revisores después (necesitan `MANIFEST.json`/`ASSETS/` del packaging single-write ZIP-only). En la corrida real, Bot 1 recomendó BLOQUEAR y Bot 4 DEVOLVER-PRUEBAS; el ZIP se emitió igual.
- **AC8 ❌**: `EMPTY_DELIVERY_TEMPLATE` no dispara en régimen ZIP-only (2 capas: `_resolve_delivery_dir()` cae al `.zip`; `_is_template_stub()` cuenta `---`/boilerplate como contenido).
- **Fidelidad del acta**: `evidence_tier C` vs MANIFEST real `B` (timing). Precedente de fix: `_extract_evidence_tier` de `honesty_reviewer.py` ya lee `financial_scenarios.breakdown.evidence_tier`.
- **Régimen Tier A nunca ejercitado**: con dato real el primer piso se levanta y `APROBADO-PARA-ENTREGA` es alcanzable — hoy sin reflejar objeciones de revisores.
- **Tier A inalcanzable con el cableado actual** (lectura de código 2026-09-12, **no certificada por VERIFY** — confirmarla en Tarea 1): `_compute_verdict` exige `evidence_tier == "A"`; `_determine_evidence_tier` lo devuelve solo con `ga4_enabled and gsc_enabled and has_verified_data`; el `HotelFinancialData` del bloque FASE-K de `main.py` fija ambas banderas en `False`. Con solo datos operativos el techo es `B_PLUS`. Detalle y consecuencias en `01-plan-maestro.md` §2.1 → decisión Q5.

### Fuentes obligatorias (Paso 0 — leer ANTES de decidir)

| Fuente | Qué aporta |
|--------|-----------|
| `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | L-E2E.1, L-E2E.3, L-V.1–L-V.4, D-V.1–D-V.4, L-R.1–L-R.4, §Seguimientos abiertos |
| `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/MATRIZ-CERTIFICACION.md` | Estado certificado AC1–AC19 + delta + greps |
| `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/05-prompt-inicio-sesion-fase-T1.md` | Matriz findings→veredicto de T1 (base del contrato enriquecido) |
| `evidence/FASE-T1/decision-integracion.md` del predecesor | Las 3 rutas de bloqueo del ZIP; Ruta 2 elegida |
| `01-plan-maestro.md` de ESTE plan (§2, §2.1, §3, §6, §9) | El nudo técnico, la cadena del tier, las opciones O1–O4, ACs borrador, el Paso 0 horizontal |
| §Deuda de proceso de `06-checklist-implementacion.md` (ESTE plan) | Los defectos de gate medidos en el R2.5 del predecesor + los tres del Paso 0 horizontal, cuyo dueño es P1 |
| `.opencode/plans/Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md` | L-PF3 (detect→ciclar→escalar con DTO tipado), L-PF6 y L-PF10 (detector roto que se publica como «0 hallazgos») |
| `.opencode/plans/Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | L-VUP-5 (una fase que no produce rojo es un falso verde), L-VUP-9 (`--help` antes de delegar), L-VUP-13 (defaults del loader de onboarding), L-VUP-1/14 (baseline y diff estructural) |
| `.opencode/plans/Archives/EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31/` | La regla que impide Tier A sin analítica conectada: base del Q5 y de T3b |
| `.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | R2.2/R2.4 (citar símbolos, AC legible en artefacto) — origen de las reglas que ya usa este plan |
| `.opencode/LECCIONES-INDEX.md` | Capa fría del Paso 0 (executor v2.22.0): `grep` del corpus completo por módulo/síntoma; su encabezado declara qué cubre y qué no |
| `00-lecciones-capitalizadas.md` (ESTE plan) | Fuente canónica de esta fase: las 8 consultas literales, las 19 lecciones con dueño y efecto, los 5 descartes y los 5 hallazgos de §3.b que P1 debe resolver |

### Lecciones aplicables (copiadas de `00-lecciones-capitalizadas.md` §2 — executor v2.22.0)

| Lección | Aplicación en P1 |
|---------|------------------|
| L-V.2: VERIFY re-lee artefactos, no hereda conclusiones | Confirmar el mapa con símbolos, **incluida la cadena de tier del §2.1**, no confiar en notas previas |
| L-V.1: fixture ≠ régimen real | El contrato de P2 debe incluir test contra artefactos reales/ZIP-only |
| L-SR5 / L-PF3: un gate que solo loggea no previene | Q1b: el contrato fija la consecuencia del bloqueo, no solo la matriz recomendación→veredicto |
| L-PF6 / L-PF10: un detector roto se publica como «sin hallazgos» | Q1 y AC-E0: `reviewer_reports` necesita tres estados distinguibles; hoy `[]` significa "nadie los pasó" |
| DA-C3: `vacío ≠ ausente` como contrato | **Pendiente en P1** (§3.b de `00-lecciones-capitalizadas.md`): es el ancestro conceptual de NR8; nombrarlo en AC-E0 o declarar que NR8 lo subsume |
| L-T4A.5 / L-T2C.4 / L-VUP-5: test vacuo | NR7: cada AC de detección o bloqueo se cierra con mutation check, no con suite verde |
| L-T2C.2: hoists en `main.py` con `except` anchos | Q5=(a) toca el bloque FASE-K: exigir test propio del tier con y sin analítica |
| L-VUP-6: delegar solo lo decidido | Q1b/Q5 se cierran **en P1**; el brief de P4 no puede reabrirlos |
| R2.4: AC legible en artefacto | Los ACs finales declaran artefacto + clave |
| §15.4.1: contrato ANTES de implementadores | P1 fija el contrato; P2/P3-A/P3-B lo ejecutan sin re-decidir |

**Consultas ejecutadas del Paso 0**: las 8 literales están en §1 de `00-lecciones-capitalizadas.md` (Q1–Q5 al notebook `iah-cli-lecciones` vía `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45`, narradas también en §9 de `01-plan-maestro.md`; Q6–Q8 al índice generado `.opencode/LECCIONES-INDEX.md`). Límite actualizado (coherente con la fila del PASO0-VERIFICADOR de arriba): `scripts/validate_lesson_capitalization.py` verifica la **forma** del `00-` (checkeable como `[7/7]`/`[9/9]` desde `e02a688`), pero **ningún check juzga la pertinencia** de las filas — esa sigue disciplinada por lectura humana, y vale L-R.4: se publica como límite declarado, no como cumplimiento probado.

---

## Tareas (R3: 3 tareas, sin comandos largos)

### Tarea 1: Research del estado actual (solo lectura)

**Objetivo**: Confirmar con símbolos el mapa del nudo técnico y verificar qué endosos del predecesor ya ejecutó RELEASE-4.76.0.

**Archivos a leer** (por símbolo, R2.2):
- `modules/quality_gates/tribunal/judge.py` — `TribunalJudge.evaluate`, `_compute_verdict`, `blocks_delivery_zip`, `FIRST_FLOOR_TIERS`, `_apply_first_floor_rule`, y dónde se inicializa `reviewer_reports`
- `main.py` — condición ZIP-skip (junto a `delivery_quality_report` y `_claim_escalated`), bloque FASE 7 de revisores, construcción de `HotelFinancialData` en el bloque FASE-K y su relación con `ga4_client.is_available()` / `analytics_data["use_ga4"]`
- `modules/financial_engine/scenario_calculator.py` — `_determine_evidence_tier`, `HotelFinancialData` (`ga4_enabled`, `gsc_enabled`), `EvidenceTier.B_PLUS`
- `modules/delivery/delivery_packager.py` — `package()`, escritura single-write ZIP-only
- `modules/quality_gates/tribunal/asset_reviewer.py` — `_resolve_delivery_dir`, `_is_template_stub`, `_check_implementation_order`
- `modules/quality_gates/tribunal/honesty_reviewer.py` — `_extract_evidence_tier`
- Docs del predecesor en `Archives/` — D-V.3 (¿se endureció el executor?), versión hardcodeada en `acta_writer.py`

**Criterios de aceptación**:
- [ ] `evidence/FASE-P1/research-estado.md`: mapa confirmado símbolo-por-símbolo + estado de D-V.1/D-V.3/endosos
- [ ] **§2.1 confirmado o refutado con evidencia** (cadena `_compute_verdict` → `_determine_evidence_tier` → banderas del bloque FASE-K): si se confirma, Q5 es obligatoria; si se refuta, registrar por qué y corregir `01-plan-maestro.md` §2.1 y §9
- [ ] Cero modificaciones de código

### Tarea 2: Decisión con el usuario (una tanda de preguntas, AskUserQuestion)

| # | Pregunta | Opciones |
|---|----------|----------|
| **Q1** | ¿Debe el tribunal enforcear (bloquear el ZIP con las objeciones de sus revisores)? | (a) Sí, con refactor · (b) No — auditoría-only documentada (O4) · (c) Decidir tras la corrida de observación P4 |
| **Q1b** | Si Q1=sí: ¿qué pasa **después** del bloqueo? (L-SR5/L-PF3 — un bloqueo sin consecuencia definida no previene nada) | (i) re-generar con el `suggestion` del revisor + 1 reintento con guard anti-bucle y luego escalar · (ii) entregar diagnóstico sin ZIP, sin reintento · (iii) abortar en seco y reportar |
| **Q2** | Si Q1=(a): ¿qué opción de ordenamiento? (plan maestro §3) | O1 metadata pre-ZIP · O2 estado en memoria · O3 dos pasadas staging |
| **Q2b** | ¿Remediación de AC8? | (a) `_resolve_delivery_dir()` lee `IMPLEMENTATION_ORDER.md` del ZIP vía `zipfile` · (b) recalibrar `_is_template_stub()` (excluir `---`/boilerplate) |
| **Q3** | ¿Secuenciación? | (a) P2 (enforcement) antes de P4 — recomendado si el acta va a cliente · (b) P4 primero como diagnóstico puro |
| **Q4** | ¿Hotel y datos para P4? (precondición T3a) | Quién provee `rooms`/`occupancy_rate`/`direct_channel_percentage`/`ADR` con fuente; URL propia; consentimiento. **Si no se cierra (nadie provee el dato con fuente): P4 se difiere con la misma mecánica que Q5=(c)** — escenario de cierre sin P4 registrado en `dependencias-fases.md`, no precondición abierta hasta RELEASE |
| **Q5** | ¿Cómo se resuelve que Tier A sea inalcanzable en `v4complete` (§2.1)? | (a) P3-B propaga las banderas reales al `HotelFinancialData` del bloque FASE-K (AC-F5, toca `main.py`) · (b) P4 se corre en `B_PLUS` declarando el techo · (c) P4 se difiere a un plan de analítica y este plan cierra sin corrida |
| **Q6** | ¿Qué estados debe distinguir el acta por revisor? (NR8, hoy inexistente) | (a) `sin hallazgos` / `artefacto ausente` / `lector fallido` con claves propias · (b) otro esquema que P1 fije — pero nunca un solo `[]` |

**Criterios de aceptación**:
- [ ] Q1–Q6 respondidas y registradas en `evidence/FASE-P1/decision-enforcement.md`
- [ ] **Q1b y Q5 no se difieren**: Q1b sin respuesta deja el contrato incompleto para P2; Q5 sin respuesta deja P4 inespecifiable
- [ ] Si Q1=(c): P4 se reordena antes de P2 y el veredicto provisional queda documentado
- [ ] Si Q5=(c) **o T3a no se cierra por Q4**: P4 se difiere — el README pasa a 5 sesiones y `dependencias-fases.md` elimina/ aplaza P4 con la decisión registrada (escenario "cierre válido sin P4", no en silencio), y el prompt de P2 pendiente de Q1 pasa a crearse aquí
- [ ] **Decisión FASE-VERIFY cerrada** en `dependencias-fases.md` (§4.6 del executor): la sesión de ajuste dejó la activación condicionada a lo que salga de Q1/Q4/Q5; P1 fija si hay sesión FASE-VERIFY propia o basta el patrón VERIFY de RELEASE (AC-V1)

### Tarea 3: Contrato del veredicto enriquecido + ACs finales + checklist

**Contenido de `evidence/FASE-P1/decision-enforcement.md`**:
1. Decisión Q1–Q6 con rationale y alternativas rechazadas (formato DA-*)
2. **Contrato del veredicto enriquecido** (si Q1=sí): cómo `_compute_verdict` consume `reviewer_reports` — matriz recomendación→veredicto propuesta (hereda T1: finding CRITICAL o veredicto BLOQUEAR de revisor → DEVOLVER-CORRECCIONES/BLOQUEADO; WARNING no degrada bajo el primer piso), punto del flujo donde corre (según O1/O2/O3), never-block preservado, NR3 (sin cuarta ruta)
3. **Sección "Consecuencia del bloqueo"** (Q1b): qué se regenera, con qué restricción, cuántos reintentos y qué ve el operador cuando persiste — con el nombre del DTO o clave que lo expresa (L-PF3 exige DTO tipado, no parsing de JSON)
4. **Sección "Tri-estado de revisores"** (Q6): claves del acta que distinguen sin hallazgos / artefacto ausente / lector fallido, y qué hace el Juez con cada una (NR8)
5. ACs finales desde el borrador §6 del plan maestro, cada uno con artefacto + clave (R2.4); **los de detección o bloqueo llevan escrita su verificación por mutation check (NR7)**; añadir/borrar según la decisión
6. Plan de P2/P3-A/P3-B actualizado con lo decidido (qué fase hace qué, incluido AC-F5 en P3-B si Q5=a)

**Criterios de aceptación**:
- [ ] Contrato fijado ANTES de P2/P3-A/P3-B (regla §15.4.1 heredada)
- [ ] Secciones "Consecuencia del bloqueo" y "Tri-estado de revisores" presentes y no vacías (AC-D1)
- [ ] ACs finales con artefacto + clave
- [ ] Ningún AC de detección o bloqueo sin su verificación NR7 escrita
- [ ] `06-checklist-implementacion.md` y `dependencias-fases.md` actualizados con lo decidido
- [ ] `log_phase_completion.py --fase FASE-P1 --desc "..." --check-manual-docs` ejecutado (SIN `--release`)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Commit de cierre de fase

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** de este plan: marcar FASE-P1 ✅ + reflejar la decisión
2. **`README.md`** de este plan: actualizar tabla de progreso
3. **`01-plan-maestro.md`**: fijar ACs finales y opción elegida
4. **`06-checklist-implementacion.md`**: marcar items de P1
5. **`evidence/FASE-P1/`**: `research-estado.md` + `decision-enforcement.md`
6. **`10-analisis-post-implementacion.md`** de este plan: **existe desde la sesión de ajuste 2026-09-14** — P1 rellena su fila en Resumen de Ejecución, añade sus lecciones (mínimo 3) y mantiene al día la sección "Lecciones capitalizadas de planes anteriores" con la tabla del §9 del plan maestro
7. **`09-documentacion-post-proyecto.md`**: **existe desde la sesión de ajuste 2026-09-14** — P1 acumula su sección (es fase de decisión: registra la decisión Q1–Q6; no produce módulos nuevos — si no hay cambios de código, se anota "sin assets — fase de decisión")

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] Q1–Q6 decididas y documentadas
- [ ] `research-estado.md` con mapa confirmado símbolo-por-símbolo + §2.1 confirmado o refutado
- [ ] Contrato del veredicto enriquecido fijado (o O4 documentado), con consecuencia del bloqueo y tri-estado
- [ ] ACs finales con artefacto + clave
- [ ] **Iteraciones medidas con unidad**: `ids` + `tool_use` con corte en el commit, escritas en `06-checklist-implementacion.md`. Un `—` en esa celda **no cierra la fase** (cura de L-R.1, aplicada desde este plan)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada (7 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Presupuesto**: 30 iteraciones, medido con `evidence/FASE-D/measure_iterations.py` reportando **`ids` y `tool_use` con corte en el commit** (R2.1 + L-R.1); el número va en la fila de P1 de `06-checklist-implementacion.md`
- **Q1b, Q5 y Q6 se cierran en esta sesión**: no se delegan a P2, P3-A, P3-B ni al brief de P4 (L-VUP-6 — delegar solo lo ya decidido)
- **NO modificar código de producción** (sesión de decisión; P2/P3-A/P3-B ejecutan)
- **NO ejecutar v4complete** (la corrida de observación es P4)
- **NO modificar ROADMAP.md**
- **NO usar números de línea** (R2.2: citar símbolos)
- **NO delegar a subagente** (decisión cross-module)
- **El contrato fijado aquí obliga a P2/P3-A/P3-B**: cambios posteriores requieren decisión explícita registrada
