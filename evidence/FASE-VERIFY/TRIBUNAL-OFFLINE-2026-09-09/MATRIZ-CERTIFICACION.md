# FASE-VERIFY — Matriz de certificación firmada

**Plan**: TRIBUNAL-OFFLINE-2026-09-09 · **Fecha**: 2026-09-11 · **HEAD al certificar**: `488cdbb`
**Modo**: DIRECTO, no delegable (executor §4.6) · **Cero código de producción tocado · cero `v4complete` re-ejecutado**

## Cómo se obtuvo esta evidencia

No se re-utilizó el log de ninguna fase. Lectura directa de artefactos reales + sonda propia re-ejecutable:

| Instrumento | qué lee |
|-------------|---------|
| `verify_probe_ac8.py` / `_out.txt` | acta viva (verdict/tier/cláusulas), `_resolve_delivery_dir()` sobre `deliveries/` vivo (ZIP-only), `_check_implementation_order()` en régimen vivo y contra el desempaquetado de evidencia, `_is_template_stub()` contra los 468 B reales |
| `verify_tests_tribunal.txt` | suite completa `tests/quality_gates/tribunal/` + `tests/test_asset_semantics_validator.py`: **123 passed / 0 failed** (AC10, AC15, AC16) |
| `greps_residuales.txt` | los 4 patrones del Paso 4: **0 matches en los 4** |
| `grep_ac4_main.txt` | `TribunalJudge`/`tribunal`/`_tribunal_blocks` en `main.py`: 1 instanciación, veredicto dentro de la condición ZIP-skip existente |
| Lectura directa | `evidence/FASE-E2E/*.json`, `output/v4_complete/hotelsalentoreal/v4_audit/` (vivo), `output/FASE-D_salentoreal_post_guard/` (baseline solo-lectura), `evidence/FASE-E2E/deliveries/*_unpacked/` (MANIFEST + IMPLEMENTATION_ORDER reales) |
| Test suelto | `test_invalid_mappings_valida_contra_capa1` (1 passed, contrato S9 preexistente) · `test_barreda_un_solo_emisor_de_la_clave` (**1 failed** — deuda del plan, ver D-V.1) |

## Balance

**AC1-AC16**: 15 ✅ · 0 ⚠️ · **1 ❌ (AC8)** — causa raíz fijada por sonda, routed a Seguimientos abiertos (VERIFY no modifica código).
**ACs propuestos (dueño VERIFY)**: AC17 ✅ · AC18 ✅ · AC19 ⚠️.
**NR**: NR4 ✅ (0 imports de `publication_gates` en tribunal) · NR5 ✅ (coherence 0.83 ≥ 0.80) · NR3 ✅ (`--quick` TOTAL PASS, ver `verify_validations.txt`) · NR1/NR2 declarados por fase (VERIFY añade 0 tests).
**Todo ❌/⚠️ tiene seguimiento con dueño.** Detalle en `10-analisis-post-implementacion.md` §Matriz, §Seguimientos.

## Matriz AC1-AC16 (Real + Status)

| AC | Expected | Real (leído del artefacto) | Status |
|----|----------|---------------------------|--------|
| AC1 | acta con `verdict` legible | `acta_revision.json` vivo + evidencia: `"verdict": "APROBADO-CONDICIONAL-PENDING-ONBOARDING"` (string válido) | ✅ |
| AC2 | Tier B/C → condicional | verdict condicional exacto + `evidence_tier: "C"` ∈ {B,C} + `first_floor_rule.applied: true` ("evidence_tier C → máximo condicional"). Nota: tier real = B (MANIFEST `quality_metadata` + `financial_scenarios.breakdown`); el acta sub-reporta C porque el Juez corre antes del packaging (L-E2E.1) — veredicto invariante (B y C ∈ FIRST_FLOOR_TIERS) | ✅ |
| AC3 | acta MD con 6 cláusulas P6 | `acta_revision.md`: secciones P6.1, P6.2, P6.3, P6.4, P6.5, P6.6 + Regla de Primer Piso, cada una con status/artefacto fuente/finding | ✅ |
| AC4 | UNA ruta, no cuarta | 1 instanciación de `TribunalJudge`; `blocks_delivery_zip(acta)` alimenta la condición ZIP-skip existente (Ruta 2 de `decision-integracion.md`, junto a `delivery_quality_report.status == "FAIL"` y `_claim_escalated`); revisores never-block no añaden ruta; grep G3: `two_phase_flow` 0 matches | ✅ |
| AC5 | `revision_diagnostico.json` con `findings[]` | lista no vacía: 1 finding CRITICAL con `severity`/`clause`/`source_artifact`/`description`/`pain_id` | ✅ |
| AC6 | recall vacuo marcado | finding con `finding_type == "VACUOUS_RECALL"` **en artefacto real** (el plan lo predecía test-level: L-T2A.2 refutada por la corrida — `gate_report.critical_recall.details: {}` real). Además test-level verde | ✅ |
| AC7 | `revision_assets.json` con `coverage_by_service[]` | lista de 4 entradas, cada una con `service`/`status`/`asset_path`/`finding` (+ `asset_exists_on_disk`); summary 4/4 coverage 1.0 | ✅ |
| AC8 | `IMPLEMENTATION_ORDER.md` vacío señalado | **finding `EMPTY_DELIVERY_TEMPLATE` AUSENTE** en `revision_assets.json` real, aunque el archivo real califica como "plantilla sin contenido por-hotel" (468 B; secciones ORDEN/GUÍA/CHECKLIST vacías). Sonda: capa 1 — `deliveries/` vivo es ZIP-only y `_resolve_delivery_dir()` cae al `.zip` (`<zip>/IMPLEMENTATION_ORDER.md` no existe → 0 findings); capa 2 — `_is_template_stub(contenido_real)` → **False** (non_empty_lines=10 > 3: los 5 `---` y el boilerplate Fecha/Score/footer cuentan como contenido; el fixture T2-B usaba un stub sintético headers-only). Tests verdes (fixture) ≠ régimen real | ❌ |
| AC9 | `revision_alineacion.json` con `service_matrix[]` | lista de 4 entradas con `service`/`status`/`verbal_promise_found`/`matrix_entry_found` (+ `pain_id`/`finding`); 4/4 ALINEADO | ✅ |
| AC10 | promesa sin matriz → `PROMESA-SIN-MATRIZ` | `test_promise_without_matrix_detected` PASSED (+ `..._escalates_verdict` PASSED); en la corrida real el régimen se sostiene: `promise_without_matrix: 0` sobre propuesta real sin promesas verbales fuera de matriz | ✅ |
| AC11 | `revision_honestidad.json` con `findings[]` | lista con 1 finding: `type: CG_WARNING_UNDISCLOSED`, `claim_text`, `evidence_tier_declared: "B"`, `cg_reference`; summary completo | ✅ |
| AC12 | CG-WHATSAPP-LEAD detectado | `findings[0].cg_reference == "CG-WHATSAPP-LEAD"` **en artefacto real** de la corrida E2E (gate WARNING `passed: false` del archivo de diagnóstico, no divulgado en propuesta). Cierra el residuo T4-B "falta el artefacto E2E" | ✅ |
| AC13 | acta + 6 cláusulas en output E2E | `acta_revision.json` vivo: `clauses_evaluated: 6` (P6.1/3/4/6 PASS; P6.2/5 NOT_EVALUABLE — diseño T1/D-T1.3) | ✅ |
| AC14 | 4 reportes en `v4_audit/` | `ls` vivo: `revision_diagnostico.json`, `revision_assets.json`, `revision_alineacion.json`, `revision_honestidad.json` presentes (los 4 también en evidencia + dentro del ZIP según MANIFEST) | ✅ |
| AC15 | S-E2 sin NameError | `test_s_e2_generate_proposal_false.py`: 18/18 PASSED (incl. `test_site_presence_snapshot_initialized_before_proposal_gate` y `TestPresenceLookupLiveConsumers` ×11 sobre generador real) | ✅ |
| AC16 | S9 contrato verde | `TestInvalidMappingsComplete` (keys pain_ids / no asset_type / no invertidos) 3/3 PASSED + `test_invalid_mappings_valida_contra_capa1` PASSED | ✅ |

## ACs propuestos §5.1/§5.4/§5.5 (dueño FASE-VERIFY, DA-T4B.3)

| AC | Responsabilidad | Real | Status |
|----|-----------------|------|--------|
| AC17 | §5.1 cifras con tier declarado | `financial_scenarios_*.json` declara `breakdown.evidence_tier: "B"` + `precision_tier: "C"` + `can_show_exact_money: false` + `tier_explanation` (los dos tiers + relación B→C). **Corrige la nota E2E** ("no declara evidence_tier" — sí existe en `breakdown`; el delta E2E solo miró el nivel raíz). Observación: `can_show_exact_money: false` coexiste con cifras exactas en la propuesta → seguimiento | ✅ |
| AC18 | §5.4 "recupera en X meses" con base visible | Propuesta real: tabla mes a mes (6 filas con % + pilar + acumulado), nota "¿Por qué no es lineal?", trazabilidad explícita. Aritmética exacta: Σ mensual = $5.447.608 = total declarado; $24.256.512 = 6 × $4.042.752; fuga/mes == `expected_monthly_cop` del artefacto financiero | ✅ |
| AC19 | §5.5 contradicción propuesta ↔ gates financieros | Sin contradicción dura: `doc_audit_consistency` PASSED (0); precio propuesta $400.000/mes == `monthly_price_cop` del gate; regla 50% consistente (fee 44% de recuperación mensual promedio). ⚠️ Tensión honesta: el gate `pricing_compliance` usa `expected_loss_cop` $1.960.000 (pain_ratio 0.2041) mientras la propuesta usa la fuga mensual $4.042.752 (9.9%) — dos bases de pérdida distintas y la del gate no es trazable desde los artefactos | ⚠️ |

## Delta antes/después (Paso 3, R2.3)

| Zona | Baseline FASE-D (2026-08-31, solo-lectura) | Output E2E (2026-09-11) | Delta |
|------|-------------------------------------------|------------------------|-------|
| Artefactos de tribunal en `v4_audit/` | 0 (15 archivos, ningún `acta_*`/`revision_*`) | 6 (acta json + acta md + 4 `revision_*.json`) | **+6** ✓ |
| Veredicto de entrega | (no existía) | `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | nuevo ✓ |
| Coherence canónico (`coherence_score_final`) | 0.88 | 0.83 | −0.05 (≥ 0.80 → NR5 PASS) ✓ |
| `is_coherent` | false | true (pre y post_gen) | esperado post-estabilización ✓ |
| `no_breach` servicios | 6 (entradas `alignment: no_breach` en matriz FASE-D; ref. post-estabilización FASE-I = 0) | 0 (`proposal_asset_matrix.alignment.no_breach` y `revision_alineacion.summary.no_breach`) | esperado: 0 ✓ |

## Greps residuales (Paso 4)

| Patrón | Dónde | Esperado | Real |
|--------|-------|----------|------|
| `"verdict": "APROBADO-PARA-ENTREGA"` | acta (evidence + viva) | 0 | **0** ✓ |
| `import.*publication_gates` | `tribunal/*.py` | 0 (NR4) | **0** ✓ |
| `two_phase_flow` | `main.py` | 0 | **0** ✓ |
| `"score": 1.0` hardcodeado | `tribunal/*.py` | 0 | **0** ✓ |

## Números que VERIFY puso sobre la mesa

| Medida | Valor |
|--------|-------|
| Suite tribunal + contrato S9 | **123 passed / 0 failed · 2.22 s** |
| Greps residuales | **0 matches en 4/4 patrones** |
| `run_all_validations.py --quick` | ver `verify_validations.txt` |
| Sonda AC8 | 2 capas confirmadas (ZIP-only layout + heurístico 10 > 3) |
| `test_barreda_un_solo_emisor_de_la_clave` | **1 failed** (deuda del plan — decisión D-V.1: autorizar emisor + whitelist) |
