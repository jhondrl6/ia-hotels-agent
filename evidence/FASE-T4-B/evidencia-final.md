# Evidencia Final — FASE-T4-B

> **Fecha**: 2026-09-11
> **Fase**: FASE-T4-B (Revisor de Honestidad NL — Bot 4)
> **Estado**: ⚠️ Completada con reserva (mismo tratamiento que FASE-T1 y FASE-T2-C)
> **Reserva**: auditoría forense del 2026-09-11 encontró que el revisor no funcionaba sobre los artefactos reales del pipeline. Remediación R1–R9 ejecutada el mismo día — ver §Remediación post-auditoría.
> **Dossier de auditoría**: «Auditoría forense FASE-T4-B + dossier de remediación (2026-09-11)», documento de sola lectura del auditor. **No versionado en este repositorio** (movido fuera por su autor el 2026-09-11). Sus mediciones quedaron reproducidas en `remediacion-d-t4b-a1.md` (salidas G1–G11) y en la sonda ejecutable `sonda_contraste_pre_post.py`.
>
> Este documento fue corregido tras la auditoría. Las afirmaciones fácticas que resultaron falsas están rectificadas aquí y su rastro documentado en `rectificacion-NR1.md`; el registro original de `tests_baseline_pre.txt` / `..._post.txt` se conservó íntegro (borrarlo sería destruir evidencia).

---

## Resumen de Ejecución

**Objetivo**: Implementar `HonestyReviewer` que detecta sobre-presentación de datos ESTIMATED como verificados, verifica los 3 escenarios financieros, y lee los commercial gates repartidos en DOS archivos (canónico + diagnóstico): **12 entradas = 10 gate_ids distintos** en la corrida real (el plan habló de "los 12 CG-*" asumiendo que eran distintos).

**Entregables de la fase**:
- `modules/quality_gates/tribunal/honesty_reviewer.py` (implementación completa)
- `tests/quality_gates/tribunal/test_honesty_reviewer.py` (7 tests, todos verdes)
- Documentación post-proyecto actualizada (09-documentacion, 10-analisis)

**Entregables añadidos por la remediación**: `artifact_paths.py` (resolutor compartido de rutas), `test_honesty_reviewer_retro_reales.py` (7), `test_tribunal_propuesta_ubicacion.py` (4), `test_honesty_reviewer_fidelidad_salida.py` (11), export en `__init__.py`, dos snapshots nuevos y `rectificacion-NR1.md`.

---

## Métricas de No-Regresión

### NR1 — Tests passed (delta con par pre/post)

**⚠️ Rectificado el 2026-09-11 tras la auditoría.** El par que registró la fase era inválido: `tests_baseline_pre.txt` (`8 failed, 3993 passed, 32 skipped, 4 xfailed`) y `tests_baseline_post.txt` (`3 failed, 3998 passed, 32 skipped, 4 xfailed`) **suman idéntico 4037**, y el relato que los acompañaba ("+5 no +7", "2 que dejaron de fallar", "5 tests preexistentes ahora pasan", "la implementación corrigió indirectamente algún comportamiento") era incoherente consigo mismo. La causa: **el snapshot "pre" se tomó después de crear el archivo de tests**, así que ya contenía los 7 tests de T4-B — cinco de ellos en rojo por el TDD. Los colectados lo confirman: 4.036 con el archivo de la fase, 4.029 sin él.

**Par correcto, medido el 2026-09-11**:

| Lado | Medición | Suma |
|------|----------|------|
| pre-fase **real** (`tests_baseline_pre_T4B_fase_real.txt`: suite completa excluyendo `test_honesty_reviewer.py` y los tres archivos de la remediación) | `3 failed, 3991 passed, 32 skipped, 4 xfailed` | 4.030 |
| post-fase (`tests_baseline_post.txt`, comportamiento de la suite con el archivo de la fase) | `3 failed, 3998 passed, 32 skipped, 4 xfailed` | 4.037 |

**Verificación NR1**: ✅ `3998 = 3991 + 7` — **sin términos de corrección ad-hoc**, y la suma difiere en exactamente `tests_nuevos = 7`. Los 3 fallos son los preexistentes registrados en `aba517a` y cancelan en ambos lados. La realidad siempre fue favorable; lo que fallaba era el registro.

**Regla operativa fijada** (R4.3): el baseline `pre` se toma **antes de crear el archivo de tests** y se verifica `passed_post = passed_pre + tests_nuevos`; si la resta de sumas da 0, el baseline está contaminado y el NR1 no puede declararse.

**Post-remediación** (`tests_baseline_post_T4B_remediacion.txt`, medido 2026-09-11): `3 failed, 4020 passed, 32 skipped, 4 xfailed`, 4.058 colectados. Misma regla aplicada a la remediación: `4020 = 3998 + 22` y `4.058 = 4.036 + 22` ✅, con los mismos 3 fallos preexistentes y skipped delta 0 (NR2).

### NR2 — Skipped estable

- Pre: 32 skipped
- Post: 32 skipped
- **Delta**: 0 ✅

### NR3 — Validaciones

```bash
python scripts/run_all_validations.py --quick
```

**Resultado**: 8/8 PASS ✅

---

## Hallazgos Técnicos

### 1. Commercial gates split en DOS archivos

**Problema**: Los commercial gates están distribuidos en:
- `commercial_gates_report.json` — 3 gates: `CG-ROI-NEGATIVE` (BLOCKING), `CG-OTA-NARRATIVE` (WARNING), `CG-TECH-JARGON` (WARNING)
- `commercial_gates_report_diagnostic_<ts>.json` — 9 entradas, incluyendo `CG-WHATSAPP-LEAD` (WARNING, `passed: False`)

**Impacto**: Leer solo el canónico pierde el único gate que falló en la corrida real.

**Solución**: `_merge_commercial_gates()` carga ambos archivos y consolida antes de reportar.

**Composición real medida** (corrida 2026-08-31 12:28, Tier B): **12 entradas = 10 gate_ids distintos**; los duplicados son `CG-OTA-NARRATIVE` y `CG-TECH-JARGON`, que viven en ambos archivos. Por severidad: 5 BLOCKING / 6 WARNING / 1 INFO como entradas, 4 / 5 / 1 como distintos. **Ninguna de las dos lecturas coincide con la descomposición que declara el plan** ("6 blocking + 4 warning + 2 adicionales"). `total_cg_count` reporta entradas y `distinct_cg_count` + `duplicate_gate_ids` hacen explícita la diferencia (decisión Q4 de la remediación).

**Rectificado en la auditoría**: esta sección afirmaba dos nombres de archivo y tres `gate_id` que no existen en el código ni en ningún artefacto. Describían una corrida que no corresponde ni a la realidad ni al fixture de la propia fase. Esos strings literales **no se reproducen aquí** (el criterio G6 del dossier los excluye de `evidence/` y `.opencode/`); solo figuran en el documento de auditoría del 2026-09-11, que no está versionado en este repo.

**Lección**: L-T4B.1 en `10-analisis-post-implementacion.md`

### 2. Regex de sobre-presentación en español

**Problema**: El patrón inicial `r"\b(verificado|confirmado|dato real|cifra exacta|validado)\b"` no capturaba "verificadas" (plural femenino).

**Impacto**: Test `test_over_presentation_detected` reportaba 0 findings cuando el fixture contenía "soluciones verificadas".

**Solución**: Patrón actualizado a `r"\b(verificad[oa]s?|confirmad[oa]s?|dato real|cifra exacta|validad[oa]s?)\b"` para cubrir todas las formas de género/número.

**Lección**: L-T4B.2 en `10-analisis-post-implementacion.md`

### 3. Detección de CG warnings no divulgados

**Problema**: El detector decidía "divulgado" buscando palabras sueltas (`whatsapp`, `número`, `mensaje`) en la propuesta. Una propuesta que solo lista el dato de contacto (`WhatsApp: 316 6296142`) pasaba el filtro y el warning quedaba sin señalar — falso negativo que se medirá en la corrida real (AC12 por segunda vía).

**Impacto**: `CG-WHATSAPP-LEAD` no se reportaba aunque la propuesta no divulgara el problema que el gate detectó.

**Solución actual (remediación R6, decisión Q2)**: `_check_cg_warning_undisclosed()` busca en la propuesta una frase de `DISCLOSURE_PHRASES_BY_GATE` que nombre **el problema detectado** (p. ej. "no aparece en la sección inicial", "número equivocado", "whatsapp web vs gbp"), no el `gate_id` literal (los IDs no aparecen en prosa comercial: daría falso positivo permanente) ni palabras sueltas (aparecen en menciones legítimas). Un `gate_id` sin entrada en la tabla **no se juzga**: sin criterio auditable no se afirma divulgación ni su ausencia.

**Nota de honestidad**: la redacción anterior de esta sección y L-T4B.3 afirmaban que el fix consistía en "buscar el ID del gate en la propuesta". El código no lo implementó: seguía con palabras sueltas, y `test_cg_whatsapp_lead_detected` pasaba solo porque el fixture no contenía la palabra "WhatsApp".

**Lección**: L-T4B.3 en `10-analisis-post-implementacion.md`

---

## Tests de la fase (7) — nombres verificados

| # | Test | Propósito |
|---|------|-----------|
| 1 | `test_reads_both_commercial_files` | Lee ambos archivos de commercial gates (`total_cg_count: 12`) |
| 2 | `test_cg_whatsapp_lead_detected` | Detecta `CG-WHATSAPP-LEAD` no divulgado en la propuesta |
| 3 | `test_over_presentation_detected` | Sobre-presentación de datos ESTIMATED como verificados |
| 4 | `test_missing_scenario_detected` | Escenarios financieros faltantes |
| 5 | `test_tier_mismatch_detected` | Claim con tier declarado ≠ tier real |
| 6 | `test_serialization_to_disk` | JSON escrito y re-leído (R2.4) |
| 7 | `test_mock_extractor_no_real_llm` | Los tests no llaman al LLM real |

**Ubicación**: `tests/quality_gates/tribunal/test_honesty_reviewer.py`

> **Rectificado**: la versión anterior de esta tabla listaba tres nombres sin definición en el repo y omitía `test_tier_mismatch_detected` y `test_mock_extractor_no_real_llm`, que el plan exigía explícitamente.

## Tests de la remediación (22)

| Archivo | n | Cubre |
|---------|---|-------|
| `test_honesty_reviewer_retro_reales.py` | 7 | R1.2 — el revisor sobre el baseline real `output/FASE-D_salentoreal_post_guard/` (skip explícito si el baseline no está) |
| `test_tribunal_propuesta_ubicacion.py` | 4 | R1 — contrato de **ubicación** de la propuesta (HonestyReviewer + AlignmentReviewer), resuelto sin depender del baseline |
| `test_honesty_reviewer_fidelidad_salida.py` | 11 | R6 (divulgación por frases), R8 (entradas vs distintos, tier propagado, nombre reportado, `all_gates` reducido), R9 (NR4: no rejulga un gate que pasó, no importa internals de gates) |

**Total tribunal**: 92 defs antes de la remediación → **114** después (10 archivos de test). Conteo con el método canónico de `AGENTS.md`: 4.038 → **4.060** funciones de test en el repo.

---

## Artefactos Generados

| Artefacto | Ubicación | Descripción |
|-----------|-----------|-------------|
| `honesty_reviewer.py` | `modules/quality_gates/tribunal/` | Implementación del revisor |
| `artifact_paths.py` | `modules/quality_gates/tribunal/` | **Remediación R1**: resolutor compartido de rutas (propuesta en `v4_complete/`) |
| `test_honesty_reviewer.py` | `tests/quality_gates/tribunal/` | 7 tests de la fase |
| `test_honesty_reviewer_retro_reales.py` | `tests/quality_gates/tribunal/` | **R1.2**: 7 tests sobre el baseline real |
| `test_tribunal_propuesta_ubicacion.py` | `tests/quality_gates/tribunal/` | **R1**: 4 tests del contrato de ubicación |
| `test_honesty_reviewer_fidelidad_salida.py` | `tests/quality_gates/tribunal/` | **R6/R8/R9**: 11 tests |
| `tests_baseline_pre.txt` / `..._post.txt` | `evidence/FASE-T4-B/` | Snapshots **originales de la fase** (contaminados, conservados sin editar) |
| `tests_baseline_pre_T4B_fase_real.txt` | `evidence/FASE-T4-B/` | **R4**: baseline pre-fase medido excluyendo los tests de T4-B y de su remediación |
| `tests_baseline_post_T4B_remediacion.txt` | `evidence/FASE-T4-B/` | **R4**: suite completa post-remediación |
| `rectificacion-NR1.md` | `evidence/FASE-T4-B/` | **R4**: qué se midió mal en NR1 y por qué |
| `evidencia-final.md` | `evidence/FASE-T4-B/` | Este documento |

> ⚠️ **`revision_honestidad.json` no se produjo en esta fase.** `find output/ -name "revision_*.json"` devuelve vacío: ninguno de los cuatro revisores está cableado en el pipeline (`main.py` solo invoca al Juez), así que el acta de Bot 4 se escribirá en **FASE-E2E**. La fase anterior la listaba como entregable generado.

---

## Documentación Actualizada

| Archivo | Cambio |
|---------|--------|
| `README.md` | Status: 5/9 → 6/9 sesiones; FASE-T4-B ⚠️ (reserva tras auditoría) |
| `dependencias-fases.md` | FASE-T4-B ⚠️; el contrato de "añade imports" en `__init__.py` queda cumplido con la remediación |
| `09-documentacion-post-proyecto.md` | Secciones A/B/D: +7 tests de fase y +22 de remediación; **total tribunal 92 → 114** (la cifra "81" del mensaje de commit no cuadraba con su propia descomposición 17+10+12+18+28+7); colectados post-T4-B **4.036** (no 4.025, y 4.018 ignoraba los +11 de la remediación D-T2C-A1) |
| `10-analisis-post-implementacion.md` | Fila T4-B ⚠️, L-T4B.1/3 corregidas, desvío D-T4B-A1, decisiones DA-T4B.1–.6 (Q1–Q4), seguimientos E2E, métricas re-medidas |
| `docs/contributing/REGISTRY.md` | Entrada `## FASE-T4-B - 2026-09-11` corregida (los 7 nombres reales + entrada de remediación vía `log_phase_completion.py`) |
| `AGENTS.md` | Cifra global de funciones de test: 3.934 → valor medido con el método canónico del propio documento |

---

## Criterios de Aceptación del plan (AC11 / AC12)

> La versión anterior de esta tabla numeró criterios como "AC1–AC10" de T4-B. En el plan maestro esa franja ya está ocupada (AC1–AC4 = T1, AC5–AC8 = T2-A/B, AC9–AC10 = T4-A) y a Bot 4 le corresponden **AC11** y **AC12**. Se corrige a la numeración del plan; la fuente autoritativa del estado es la matriz AC1–AC16 de `10-analisis-post-implementacion.md`.

| AC | Criterio | Estado | Base |
|----|----------|--------|------|
| AC11 | `revision_honestidad.json` con `findings[]` | ⬜ **pendiente FASE-E2E + VERIFY** | El artefacto no existe en `output/` porque ningún revisor está cableado (decisión Q1: el cableado es entregable de E2E). A nivel test, el acta se escribe y se re-leé en `test_honesty_reviewer.py` y `test_honesty_reviewer_retro_reales.py` |
| AC12 | `CG-WHATSAPP-LEAD` detectado | ⚠️ **verificado sobre artefactos reales a nivel test; certificación en artefacto exige E2E** | `test_cg_whatsapp_lead_detected` + el retro real afirman `findings[].cg_reference == "CG-WHATSAPP-LEAD"` con la propuesta de la corrida FASE-D. Antes de la remediación fallaba por dos vías independientes: el revisor no cargaba la propuesta (D1) y el heurístico de palabras sueltas lo clasificaba como divulgado (D5) |

Per R2.4, ningún AC se marca ✅ mientras no sea legible en el artefacto certificado.

**Lo que la fase sí cumplió** (sin numeración AC, para no colisionar con el plan maestro):
- `HonestyReviewer` implementado con patrón híbrido (extractor inyectable, capa determinista decide) y never-block
- Lee AMBOS archivos comerciales y consolida antes de reportar
- Detecta sobre-presentación, tier mismatch y escenarios faltantes
- Exportado por `modules/quality_gates/tribunal/__init__.py` (R2, tras la remediación)
- NR2: skipped 32 → 32, delta 0
- NR3: `run_all_validations.py --quick` 8/8 PASS
- Restricciones del plan respetadas: `main.py`, `judge.py`, `llm_extractor.py`, `ROADMAP.md` intactos; sin `v4complete`; sin LLM real en tests

---

## Próximos Pasos

1. **FASE-E2E**: Corrida Salento Real con tribunal completo (T1 + T2-A/B/C + T4-A/B)
2. **FASE-VERIFY**: Certificación formal de AC1-AC16 contra output E2E real
3. **FASE-RELEASE-4.76.0**: Cierre documental + version bump + archivado

---

## Notas Adicionales

**⚠️ Rectificada**: la versión anterior afirmaba un "bonus no planificado: 5 tests que fallaban pre-T4-B ahora pasan" y sugería que "la implementación de `HonestyReviewer` corrigió indirectamente algún comportamiento". No existe tal corrección. La explicación verdadera está en §Remediación R4 y en `rectificacion-NR1.md`: los cinco fallos que desaparecen eran **cinco de los propios tests de T4-B en rojo durante el TDD**, y el snapshot "pre" se tomó **después** de crear el archivo de tests, así que estaba contaminado.

**Patrón híbrido LLM+determinista**: T4-B replica el patrón de T4-A (LLM extrae, capa determinista decide). El `MockPromiseExtractor` permite tests offline sin llamadas LLM reales. Tras la remediación (R3.2), `review()` y `write_report()` **exigen** el extractor: ya no hay un default que instancie `LLMPromiseExtractor` y un futuro cableado en E2E debe decidir qué proveedor usa.

**Never-block pattern**: `HonestyReviewer` sigue el patrón de todos los revisores: retorna reportes de error, nunca lanza excepciones. El tribunal no puede romper v4complete.

---

## Remediación post-auditoría (2026-09-11)

Auditoría forense de sola lectura contra `05-prompt-inicio-sesion-fase-T4-B.md`. Veredicto de la auditoría: ajuste ~60 %, estado ✅ no soportado por la evidencia → **⚠️ Completada con reserva** ( precedente: T1, T2-C).

| Hallazgo | Severidad | Tarea | Estado tras la remediación |
|----------|-----------|-------|---------------------------|
| D1 — el revisor no funciona sobre los artefactos reales (`total_cg_count: 0`) | CRÍTICO | R1 | ✅ resuelto: resolutor compartido `artifact_paths.py`; sonda real → `propuesta cargada: True`, 12 entradas |
| D2 — `HonestyReviewer` sin export ni consumidor; `P6.5` bucle muerto | CRÍTICO | R2, R3 | ✅ export; ⚠️ consumidor diferido a FASE-E2E por decisión Q1 (Vía A) |
| D3 — NR1 mal documentado; baseline "pre" contenía los 7 tests de la fase | ALTO | R4 | ✅ recompuesto con baseline medido |
| D4 — falsedades factuales en `evidencia-final.md` y L-T4B.1 | ALTO | R5 | ✅ corregido en este documento |
| D5 — L-T4B.3 documentaba un fix ausente; AC12 fallaba por 2ª vía | ALTO | R6 | ✅ `DISCLOSURE_PHRASES_BY_GATE`, fijado con la propuesta real |
| D6 — 3 responsabilidades §5 ausentes sin registrar el recorte | MEDIO | R7 | ✅ diferido con dueño y nota (decisión Q3) |
| S1 — `total_cg_count` contaba entradas sin decirlo | MEDIO | R8.1 | ✅ `distinct_cg_count` + `duplicate_gate_ids` + findings deduplicados (decisión Q4) |
| S2 — `evidence_tier_declared` degradado a `"UNKNOWN"` | MEDIO | R8.2 | ✅ el tier del MANIFEST se propaga |
| S3 — `diagnostic_file` reportado podía no ser el leído | MEDIO | R8.3 | ✅ se resuelve una vez y se propaga el `Path` |
| S4 — claves fuera del schema del plan | BAJO | R8.4/R8.5 | ✅ `all_gates` reducido; extensiones registradas |
| S5 — `review()` sin extractor instanciaba el LLM real | BAJO | R3.2 | ✅ parámetro obligatorio |
| S6 — cifras de docs inconsistentes (4.025 vs 4.036; "81" vs 92) | BAJO | R5.6 | ✅ re-medidas |
| S7 — tensión NR4 sin nota ni grep de defensa | BAJO | R9 | ✅ nota + 2 tests de contrato |

**Lección transversal (insumo para `phased_project_executor.md`)**: cinco de las seis fallas compartían un mismo modo — 7/7 tests verdes sobre un fixture que clonaba el *contenido* de los artefactos reales pero no su *estructura de ubicación*, que era justo el requisito marcado ⚠️ CRÍTICO. T4-A (`AlignmentReviewer`) arrastraba el defecto idéntico, ahora corregido por la misma vía. El endurecimiento propuesto es un **gate de sonda retro**: toda fase que escriba un lector de artefactos debe incluir al menos un test contra `output/FASE-D_salentoreal_post_guard/` (con skip explícito si falta), y el ✅ de fase debe exigir que esa sonda haya pasado, no solo los mocks. Segunda corrección de forma: verificar que la suma `failed+passed+skipped+xfailed` del baseline `pre` **difiere** de la del `post` en exactamente el número de tests nuevos; una resta que dé 0 es la firma de un baseline contaminado.
