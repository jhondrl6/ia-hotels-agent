# FASE-P1: Decisión de Enforcement + Contrato del Veredicto Enriquecido

**ID**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P1
**Objetivo**: Decidir con el usuario (Q1–Q4) si el tribunal debe enforcear y mediante qué opción (O1–O4), fijar el contrato del veredicto enriquecido (cómo `_compute_verdict` consume `reviewer_reports`) y los ACs finales del plan. **Sesión de decisión: sin código de producción.**
**Dependencias**: FASE-RELEASE-4.76.0 del plan TRIBUNAL-OFFLINE-2026-09-09 ✅ (cerrada 2026-09-11 en `bd2bf57` — v4.76.0 publicada localmente, sin push; plan archivado R2.5)
**Complejidad técnica**: **MEDIA** — decisión arquitectónica + de producto cross-module
**Modo de ejecución**: **DIRECTO** (agente principal). NO delegable: decisión que afecta el flujo de entrega completo.
**Skill**: `phased_project_executor.md` v2.21.0 (añade R2.6 y R2.7, aún sin verificador mecánico)

---

## Contexto

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| TRIBUNAL-OFFLINE-2026-09-09 (9/9) | ✅ Cerrado 2026-09-11 en `bd2bf57` — certificación 15 ✅ + **AC8 ❌**, que abre este plan. Documentos en `Archives/TRIBUNAL-OFFLINE-2026-09-09/` (R2.5) |
| FASE-RELEASE-4.76.0 (predecesor) | ✅ Completada 2026-09-11 — v4.76.0 publicada **localmente, sin push ni tag**; `--quick` 8/8; precondición de esta fase cumplida |
| Deuda de gates medida en ese R2.5 | ⚠️ **Heredada a P1** — 6 ítems en §Deuda de proceso de `06-checklist-implementacion.md` (R2.6/R2.7 sin verificador mecánico + baseline de R2.6 fuera del repo, `validate_plan_closure.py` 1/8, `Version actual` del REGISTRY escrita a mano, reescrito ciego de `validate_opencode_refs.py --fix`, regex de `version_consistency_checker.py`, y L-R.1: la columna `Iteraciones` no obliga a medir) |
| FASE-P1 | ← ESTA FASE |

### Resumen del estado certificado (FASE-VERIFY)

- El tribunal **audita pero no enforcea**: `reviewer_reports` queda `[]` porque el Juez corre antes del packaging y los revisores después (necesitan `MANIFEST.json`/`ASSETS/` del packaging single-write ZIP-only). En la corrida real, Bot 1 recomendó BLOQUEAR y Bot 4 DEVOLVER-PRUEBAS; el ZIP se emitió igual.
- **AC8 ❌**: `EMPTY_DELIVERY_TEMPLATE` no dispara en régimen ZIP-only (2 capas: `_resolve_delivery_dir()` cae al `.zip`; `_is_template_stub()` cuenta `---`/boilerplate como contenido).
- **Fidelidad del acta**: `evidence_tier C` vs MANIFEST real `B` (timing). Precedente de fix: `_extract_evidence_tier` de `honesty_reviewer.py` ya lee `financial_scenarios.breakdown.evidence_tier`.
- **Régimen Tier A nunca ejercitado**: con dato real el primer piso se levanta y `APROBADO-PARA-ENTREGA` es alcanzable — hoy sin reflejar objeciones de revisores.

### Fuentes obligatorias (Paso 0 — leer ANTES de decidir)

| Fuente | Qué aporta |
|--------|-----------|
| `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | L-E2E.1, L-E2E.3, L-V.1–L-V.4, D-V.1–D-V.4, L-R.1–L-R.4, §Seguimientos abiertos |
| `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/MATRIZ-CERTIFICACION.md` | Estado certificado AC1–AC19 + delta + greps |
| `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/05-prompt-inicio-sesion-fase-T1.md` | Matriz findings→veredicto de T1 (base del contrato enriquecido) |
| `evidence/FASE-T1/decision-integracion.md` del predecesor | Las 3 rutas de bloqueo del ZIP; Ruta 2 elegida |
| `01-plan-maestro.md` de ESTE plan (§2, §3, §6) | El nudo técnico, las opciones O1–O4, ACs borrador |
| §Deuda de proceso de `06-checklist-implementacion.md` (ESTE plan) | Los 6 defectos de gate medidos en el R2.5 del predecesor, cuyo dueño es P1 — decidir cuáles entran al alcance antes de abrir P2/P3 |

### Lecciones aplicables (Paso 0)

| Lección | Aplicación en P1 |
|---------|------------------|
| L-V.2: VERIFY re-lee artefactos, no hereda conclusiones | Confirmar el mapa con símbolos, no confiar en notas previas |
| L-V.1: fixture ≠ régimen real | El contrato de P2 debe incluir test contra artefactos reales/ZIP-only |
| R2.4: AC legible en artefacto | Los ACs finales declaran artefacto + clave |
| §15.4.1: contrato ANTES de implementadores | P1 fija el contrato; P2/P3 lo ejecutan sin re-decidir |

---

## Tareas (R3: 3 tareas, sin comandos largos)

### Tarea 1: Research del estado actual (solo lectura)

**Objetivo**: Confirmar con símbolos el mapa del nudo técnico y verificar qué endosos del predecesor ya ejecutó RELEASE-4.76.0.

**Archivos a leer** (por símbolo, R2.2):
- `modules/quality_gates/tribunal/judge.py` — `TribunalJudge.evaluate`, `_compute_verdict`, `blocks_delivery_zip`, `FIRST_FLOOR_TIERS`
- `main.py` — condición ZIP-skip (junto a `delivery_quality_report` y `_claim_escalated`), bloque FASE 7 de revisores
- `modules/delivery/delivery_packager.py` — `package()`, escritura single-write ZIP-only
- `modules/quality_gates/tribunal/asset_reviewer.py` — `_resolve_delivery_dir`, `_is_template_stub`, `_check_implementation_order`
- `modules/quality_gates/tribunal/honesty_reviewer.py` — `_extract_evidence_tier`
- Docs del predecesor en `Archives/` — D-V.3 (¿se endureció el executor?), versión hardcodeada en `acta_writer.py`

**Criterios de aceptación**:
- [ ] `evidence/FASE-P1/research-estado.md`: mapa confirmado símbolo-por-símbolo + estado de D-V.1/D-V.3/endosos
- [ ] Cero modificaciones de código

### Tarea 2: Decisión con el usuario (una tanda de preguntas, AskUserQuestion)

| # | Pregunta | Opciones |
|---|----------|----------|
| **Q1** | ¿Debe el tribunal enforcear (bloquear el ZIP con las objeciones de sus revisores)? | (a) Sí, con refactor · (b) No — auditoría-only documentada (O4) · (c) Decidir tras la corrida de observación P4 |
| **Q2** | Si Q1=(a): ¿qué opción de ordenamiento? (plan maestro §3) | O1 metadata pre-ZIP · O2 estado en memoria · O3 dos pasadas staging |
| **Q2b** | ¿Remediación de AC8? | (a) `_resolve_delivery_dir()` lee `IMPLEMENTATION_ORDER.md` del ZIP vía `zipfile` · (b) recalibrar `_is_template_stub()` (excluir `---`/boilerplate) |
| **Q3** | ¿Secuenciación? | (a) P2 (enforcement) antes de P4 — recomendado si el acta va a cliente · (b) P4 primero como diagnóstico puro |
| **Q4** | ¿Hotel y datos para P4? (precondición T3) | Quién provee `rooms`/`occupancy_rate`/`direct_channel_percentage`/`ADR` con fuente; URL propia; consentimiento |

**Criterios de aceptación**:
- [ ] Q1–Q4 respondidas y registradas en `evidence/FASE-P1/decision-enforcement.md`
- [ ] Si Q1=(c): P4 se reordena antes de P2 y el veredicto provisional queda documentado

### Tarea 3: Contrato del veredicto enriquecido + ACs finales + checklist

**Contenido de `evidence/FASE-P1/decision-enforcement.md`**:
1. Decisión Q1–Q4 con rationale y alternativas rechazadas (formato DA-*)
2. **Contrato del veredicto enriquecido** (si Q1=sí): cómo `_compute_verdict` consume `reviewer_reports` — matriz recomendación→veredicto propuesta (hereda T1: finding CRITICAL o veredicto BLOQUEAR de revisor → DEVOLVER-CORRECCIONES/BLOQUEADO; WARNING no degrada bajo el primer piso), punto del flujo donde corre (según O1/O2/O3), never-block preservado, NR3 (sin cuarta ruta)
3. ACs finales desde el borrador §6 del plan maestro, cada uno con artefacto + clave (R2.4); añadir/borrar según la decisión
4. Plan de P2/P3 actualizado con lo decidido (qué fase hace qué)

**Criterios de aceptación**:
- [ ] Contrato fijado ANTES de P2/P3 (regla §15.4.1 heredada)
- [ ] ACs finales con artefacto + clave
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
6. **`10-analisis-post-implementacion.md`** de este plan: crear con Resumen de Ejecución + lecciones (mínimo 3)

**NO esperar a la siguiente sesión.**

---

## Criterios de Completitud (CHECKLIST)

- [ ] Q1–Q4 decididas y documentadas
- [ ] `research-estado.md` con mapa confirmado símbolo-por-símbolo
- [ ] Contrato del veredicto enriquecido fijado (o O4 documentado)
- [ ] ACs finales con artefacto + clave
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada (6 puntos)

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Presupuesto**: 30 iteraciones, medido con `evidence/FASE-D/measure_iterations.py`, corte en commit (R2.1)
- **NO modificar código de producción** (sesión de decisión; P2/P3 ejecutan)
- **NO ejecutar v4complete** (la corrida de observación es P4)
- **NO modificar ROADMAP.md**
- **NO usar números de línea** (R2.2: citar símbolos)
- **NO delegar a subagente** (decisión cross-module)
- **El contrato fijado aquí obliga a P2/P3**: cambios posteriores requieren decisión explícita registrada
