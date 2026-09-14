# Documentación Post-Proyecto — TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Versión objetivo**: 4.77.0
> **Propósito**: Acumular datos por fase para que FASE-RELEASE genere CHANGELOG y GUIA_TECNICA oficiales.
> **Creado**: 2026-09-14 en la sesión de ajuste (el executor lo exigía desde la concepción; se instala vacío y se acumula al cierre de cada fase — no se rellena de memoria al final).

---

## Sección A: Módulos Nuevos / Modificados

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| **_(ninguno — P1 es fase de decisión: sin assets, sin código de producción)_** | — | Verificable en `git status` del commit de cierre: solo `.opencode/plans/…` y `evidence/FASE-P1/` | P1 |
| Tribunal certificador P6 — Bot 3 (assets) | `modules/quality_gates/tribunal/asset_reviewer.py` | AC-F1 dos capas: `_resolve_delivery_dir` ya no devuelve un `.zip` como `Path` (raíz DA-P1.5); nuevos `_resolve_delivery_zip` + `_read_implementation_order` (dir-first, luego `zipfile.read("IMPLEMENTATION_ORDER.md")`) con 4 estados `OK`/`ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN` publicados en `_impl_order_check`; `_is_template_stub` reescrito a criterio estructural (secciones con 0 contenido real, excluyendo boilerplate). Commit `0d4d072` | P3-A |
| Tribunal certificador P6 — Juez | `modules/quality_gates/tribunal/judge.py` | AC-F2: `_read_evidence_tier` reescrito (scenarios-first vía `FINANCIAL_SCENARIOS_PATTERN` → `breakdown.evidence_tier`, MANIFEST solo fallback, `"C"` por defecto). AC-F4: `FIRST_FLOOR_TIERS` extendido a `{"B","B+","C"}` (la clave es `"B+"`, como serializa `EvidenceTier.B_PLUS`). Commit `0d4d072` | P3-A |
| Tests del tribunal | `tests/quality_gates/tribunal/test_p3a_zip_tier_firstfloor.py` (nuevo, 21 tests) · `tests/quality_gates/tribunal/test_judge.py` (fixture `tmp_audit_dir` poda `financial_scenarios_*.json` para que los tests de tier por MANIFEST ejerciten el fallback) | Cobertura AC-F1 (capa1 ZIP-aware + capa2 estructural + R2.6 sobre baseline real), AC-F2 (scenarios/fallback/sonda real) y AC-F4 (`B+`). Tribunal pasa de 114 a 135 tests | P3-A |

**Guía por fase**: P1 no produce filas (decisión). P2: `judge.py`/`main.py`/`delivery_packager.py` según O elegida. P3-A: `asset_reviewer.py`/`judge.py`. P3-B: `acta_writer.py`/`main.py` (solo Q5=a)/test barreda. P4: ninguna (observación). RELEASE: docs.

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| **Contrato del veredicto enriquecido** (documento, no código) | `evidence/FASE-P1/` | Matriz recomendación→veredicto de 8 pasos, consecuencia del bloqueo (escalar: ZIP suprimido + `corrective_actions` + humano decide), **cuatro** estados por revisor y kill switch heredado. **Vinculante** para P2/P3-A/P3-B | P1 |
| **Prompt de FASE-P2** | `.opencode/plans/<PLAN>/` | `05-prompt-inicio-sesion-fase-P2.md`, con O1-cuarentena y la cláusula "no re-decidir" | P1 |
| Enforcement del tribunal (los dientes) | `tribunal/`, `main.py`, `delivery/` | **No existe todavía**: P1 lo especificó, P2 lo implementa | P2 (pendiente) |
| **Detección ZIP-only de plantilla vacía** (AC-F1) | `asset_reviewer.py` | `EMPTY_DELIVERY_TEMPLATE` ahora dispara leyendo `IMPLEMENTATION_ORDER.md` **desde el ZIP** en el régimen single-write ZIP-only real (antes el resolutor caía al `.zip` como `Path` fantasma y nunca leía). Distingue 4 estados (NR8): hallazgo OK / `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN`; un fallo de lectura **nunca** publica "vacío" | P3-A |
| **Stub estructural, no conteo de líneas** (AC-F1) | `asset_reviewer.py` | `_is_template_stub` decide por estructura (≥1 sección declarada y todas con 0 contenido real, excluyendo `---` y boilerplate Fecha/Score/footer; ó 0 bytes) en vez de `non_empty_lines <= 3` — el stub real de 468 bytes pasaba por contenido válido | P3-A |
| **Tier del acta desde la fuente pre-packaging** (AC-F2) | `judge.py` | El acta lee `evidence_tier` de `financial_scenarios_*.json → breakdown.evidence_tier` (la fuente que existe antes del packaging), con MANIFEST solo de fallback; antes leía un `MANIFEST.json` que en el flujo real aún no existe y caía a `"C"` en silencio. Sonda sobre artefacto real: acta `"B"` == pipeline `"B"` | P3-A |
| **Primer piso coherente en B+** (AC-F4) | `judge.py` | `FIRST_FLOOR_TIERS` incluye `"B+"` (serialización de `EvidenceTier.B_PLUS`); `first_floor_rule.reason` ya no declara "sin restricción de primer piso" en un caso cuyo veredicto sale condicional | P3-A |

## Sección D: Métricas Acumulativas

| Métrica | Pre-plan (v4.76.0) | Al cerrar P1 | Al cerrar P2 | Al cerrar P3-A | Al cerrar P3-B | Al cerrar P4 | Final (v4.77.0) |
|---------|--------------------|--------------|--------------|----------------|----------------|--------------|------------------|
| Funciones test (canónico `grep -rE "^\s*def test_" tests --include=*.py`) | 4.063 | **4.063** (sin cambio) | — | **4.129** (+21 propios de P3-A; el salto desde 4.063 incluye **+45 ajenos** del plan PASO0-VERIFICADOR-CAPITALIZACION entrados entre v4.76.0 y P3-A — `test_build_lesson_index.py` + `test_validate_lesson_capitalization.py`) | — | — | — |
| Archivos `test_*.py` | 293 | **293** (sin cambio) | — | **296** (+1 propio `test_p3a_zip_tier_firstfloor.py`; +2 ajenos PASO0) | — | — | — |
| Fallos conocidos (suite en HEAD) | 3 (2 ajenos + barreda/D-V.1) | **3** (sin cambio) | — | **4** idénticos en PRE y POST (`test_faq_generator_output_is_jsonld`, `test_function_default_flags` flaky, `test_barreda_un_solo_emisor_de_la_clave` [deuda P3-B], `test_diagnostic_includes_geo_metrics`) → **0 regresiones de P3-A**; delta R2.7 +21 íntegro en `passed` (4.070→4.091) | ⟨P3-B cierra barreda → 3⟩ | — | — |
| `--quick` checks | 9/9 | **9/9** (2026-09-14 14:00, medido en el cierre; re-verificado por los 7 hooks de `fd8e4f4`) | — | **9/9** (743 citas históricas, 0 nuevas, 0 crecimientos; hooks 7/7 en `0d4d072`) | — | — | — |
| Iteraciones de fase (unidad declarada, D-V2.1) | — | ≈30 `ids` / ≈58 `tool_use` | — | **106 `ids` / 126 `tool_use`** — medido con `measure_iterations.py`, corte = commit `0d4d072`. **El instrumento SÍ alcanzó el transcript → D-V2.1 NO se reprodujo.** Presupuesto 20 superado → L-P3A.1 | — | — | — |

> La fila de barreda asume que P3-B se ejecuta con Q5≠(a) o (a); si P4 se difiere, la columna P4 se marca "Diferida" con referencia a la decisión.

## Sección E: Archivos Afiliados Actualizados

| Archivo | Actualizado en | Nota |
|---------|----------------|------|
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P1` (**sin** `--release`) | P1 | Registro de fase de decisión |
| `REGISTRY.md` vía `log_phase_completion.py --fase FASE-P3-A --check-manual-docs` (**sin** `--release`) | P3-A | Registro de fase de ejecución; `CHANGELOG`/`GUIA_TECNICA` siguen acumulándose en este `09` §A/§B hasta RELEASE |
| `evidence/FASE-P3-A/` (NR1 `nr1_baseline_pre.txt`/`nr1_baseline_post.txt`/`nr1_delta_r2_7.md`, 4 pares NR7 `NR7-AC-F1-capa1.txt`/`-capa2.txt`/`NR7-AC-F2.txt`/`NR7-AC-F4.txt` + runner `nr7_mutation_checks.py`, sonda `verify_probe_ac_f1_f2_f4.py` + `probe-post-fix.txt`) | P3-A | Evidencia de cierre: delta R2.7 (+21) y mutation checks verde/rojo por AC (NR7). Commit `0d4d072` |
| `06-checklist-implementacion.md` · `dependencias-fases.md` · `README.md` · este `09` · `10-analisis-post-implementacion.md` · `00-lecciones-capitalizadas.md` | P3-A | Cierre documental: fila 3a ✅ + iteraciones, tabla/diagrama de dependencias, progreso 2/6, §A/§B/§D/§E, Resumen de Ejecución + L-P3A.1, "Estado al cerrar P3-A" en §2 |
| `01-plan-maestro.md` | P1 | §1 orden y presupuesto · §2.1 confirmado y agravado · §3 O1-cuarentena · §6 **ACs finales** (17 filas + columna NR7) |
| `06-checklist-implementacion.md` | P1 | Estado Global, checklist de P1 cerrado, y P3-A/P3-B/P2 reescritos con lo decidido |
| `dependencias-fases.md` | P1 | Diagrama y tabla reordenados (P3→P2) · **FASE-VERIFY cerrada en no activa** · prompt de P2 marcado como creado |
| `README.md` · `00-lecciones-capitalizadas.md` · `10-analisis-post-implementacion.md` · este `09` | P1 | Progreso 1/6 · §3.b resuelto · DA-P1.1…DA-P1.10 + 5 lecciones · aporte de fase |
| **`AGENTS.md` / `CHANGELOG.md` / `GUIA_TECNICA.md` / `VERSION.yaml`** | **P1: NO** | P1 no toca documentos versionados. Lo que **RELEASE debe publicar** al cerrar 4.77.0: (1) la decisión de enforcement y su consecuencia; (2) el orden P3→P2 y por qué; (3) que **no hubo sesión FASE-VERIFY** y AC-V1 la sustituyó; (4) **AC-F5 cambia el `evidence_tier` de corridas reales** — comportamiento visible, se declara (DA-P1.8); (5) el acta deja de omitir la sección de revisores y pasa a listar **cuatro** estados |

## Aporte de FASE-P1 para GUIA_TECNICA

- **Técnico**: `_read_evidence_tier` depende de un `MANIFEST.json` que en el flujo real aún no existe, así que el acta operaba con `"C"` por fallback silencioso; `_is_template_stub` contaba frontmatter como contenido; `acta_writer` suprimía la sección de revisores cuando estaba vacía. Los tres son de la misma familia —**ausencia publicada como hallazgo**— que NR8/`DA-C3` prohíben.
- **De proceso**: el Paso 0 de P1 cumplió en producir evidencia propia — los tres hechos del párrafo anterior no estaban en el plan y cambiaron dos ACs (nace AC-F6; AC-F2 se re-enuncia). Contraste honesto: **la misma tarea re-afirmó lo que ya decía §2.1**; confirmar no es descubrir.
- **Comercial**: G0 queda **encarrilado, no cerrado**. P1 quita la objeción de diseño; el dato sigue dependiendo de T3a/T3b (un hotel que dé sus números y su analítica), y este plan ya no finge tenerlo.

## Aporte de FASE-P3-A para GUIA_TECNICA

- **Técnico**: AC-F1 y AC-F2 eran **el mismo defecto con dos víctimas** (DA-P1.5): `_resolve_delivery_dir` (Bot 3) y `_read_evidence_tier` (Juez) estaban escritos contra un directorio descomprimido que el packaging single-write ZIP-only nunca produce, y ambos caían a un fallback silencioso (el `.zip` como `Path`, o `"C"` como tier). La cura no fue una función compartida sino **una única fuente de verdad por hecho**: el resolutor de entrega lee un ZIP sea miembro del ZIP o directorio (4 estados NR8, un fallo de lectura nunca publica "vacío"), y el tier se lee de `financial_scenarios_*.json` que existe **antes** del packaging. Detalle que muerde: `EvidenceTier.B_PLUS` **serializa como `"B+"`**, no `"B_PLUS"` — `FIRST_FLOOR_TIERS` llevaba la clave equivocada y por eso el primer piso no se aplicaba en `B+`.
- **De proceso**: el presupuesto era 20 iteraciones y se midieron **106 `ids` / 126 `tool_use`** (corte = commit `0d4d072`). Causa medida: una fase de detección/fidelidad cuyo NR1 (R2.7) es la **suite completa** (4.130 tests, ~7-9 min por corrida, dos corridas pre/post) más **4 pares NR7** de mutation check no cabe en un presupuesto pensado para una fase de código acotada. El instrumento `measure_iterations.py` **sí alcanzó el transcript** — la limitación D-V2.1 ("no alcanza bajo el cliente actual") **no se reprodujo**, así que la cifra es medida, no auto-reportada.
- **Comercial**: el acta deja de decir `evidence_tier C` cuando el pipeline dice `B` (sonda sobre artefacto real FASE-I: acta `"B"` == pipeline `"B"`), y deja de callar el defecto de entrega vacía en régimen ZIP-only. **Fidelidad restaurada**; el *enforcement* (que el veredicto consuma estos hallazgos y suprima el ZIP) sigue pendiente en P2 — P3-A arregla lo que el acta **dice**, no todavía lo que **hace**.

---

## Volcado para FASE-RELEASE

RELEASE (Tarea 3) verifica que cada fase cerrada ✅ tenga su aporte aquí; una fase sin fila en A/B/D/E se marca en el `10-analisis` como omisión detectada en el cierre, no se inventa.
