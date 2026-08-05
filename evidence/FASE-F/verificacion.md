# FASE-F — Verificación de Fixes (V1-V10)

**Plan**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04 / FASE-F
**Run E2E**: `output/v4_verify_4.71.0` — Zi One Luxury (https://zione.co/)
**Timestamps del run**: audit 20260805_154855 / docs 20260805_154910
**Fecha verificación**: 2026-08-05
**Script**: `temp/fase_f_verify.py` (parseo Python UTF-8, lección L15)
**Salida cruda**: `evidence/FASE-F/verificacion.txt`

## Condiciones del run

| Condición | Resultado |
|-----------|-----------|
| S7 verificado en aislamiento ANTES del run (`temp/verify_s7_loader.py`) | ✅ 3/3 PASS |
| Workaround L13 (copia YAML a `output/v4_verify_4.71.0/clientes/`) | ✅ aplicado |
| Log: "Onboarding data loaded: 4 campos confirmados" | ✅ presente |
| Log: "Using defaults" | ✅ ausente |
| Exit code del comando | 0 |
| Coherence | 0.9238 (≥ 0.8) |

## Resultados V1-V10

| # | Fix | Check | Resultado | Detalle |
|---|-----|-------|-----------|---------|
| V1 | RC1/N10 | Costos propuesta == `opportunity_scores` | ✅ PASS | 5 filas con costo vivo, todas coinciden (899.000 / 1.123.390 / 539.400 / 359.600 / 899.000) |
| V2 | RC1/N17 | Fila SEO Local → `low_seo_score` | ✅ PASS | fila referencia #6 → `low_seo_score` (no "Sin Schema Hotel") |
| V3 | RC1/N18 | WhatsApp rank vivo + label + costo real | ✅ PASS | rank=1, label "Conflicto de WhatsApp", costo 899.000; hardcode "Brecha #5: WhatsApp" count=0 |
| V4 | RC1/N19 | Sin fila "Schema Organization" fantasma | ✅ PASS | asset `org_schema` ausente en el run, 0 filas en propuesta |
| V5 | RC2/N11 | CG-CLAIM-VS-EVIDENCE sin falso positivo condicional | ✅ PASS | passed=true, "condicionales descartados" |
| V6 | RC2/N15 | CG-TIER-CONSISTENCY valida inputs reales | ✅ PASS | mensaje "Frontmatter dice tier 'B+' pero el texto dice tier 'D'" ≠ "Sin datos de tier para comparar" (el gate detectó una inconsistencia REAL del documento — WARNING, no blocking) |
| V7 | RC2/N16+N21 | ZIP limpio | ✅ PASS | 0 `commercial_gates_report*`, 0 timestamps ajenos al run (53 archivos) |
| V8 | S5 | `breakdown.data_sources.occupancy == "onboarding"` | ✅ PASS (tras S5b) | Inicialmente FAIL (`'regional'`); sesión de recuperación S5b (2026-08-05) corrigió 2 sitios en `main.py` (bloque FASE-K L2039 + input PrecisionValidator L2081). Re-verificado en run acotado 20260805_161042 (`evidence/FASE-F/s5b_rerun/`): `occupancy == "onboarding"` |
| V9 | D10 | Costos idénticos diagnóstico ↔ propuesta | ✅ PASS (con observación) | 5/5 costos idénticos; numeración divergente por diseño: diagnóstico numera por orden de aparición (BRECHA 1-10), propuesta por rank de opportunity (#N) — costos y nombres son consistentes |
| V10 | Coherencia global | 0 blocking + READY_FOR_PUBLICATION | ✅ PASS | readiness READY_FOR_PUBLICATION, blocking_issues=[], 12 gates (11 passed + 1 WARNING advisory `asset_confidence`), coherence 0.9238 |

**TOTAL: 10/10 PASS** (V8 cerrado en la sesión de recuperación S5b del 2026-08-05)

## Clasificación del fallo V8 (protocolo L14/L2) — RESUELTO en recuperación S5b

**Tipo: fallo de CÓDIGO — puntos de integración del fix S5 no cubiertos por FASE-D.**

- **Síntoma**: `financial_scenarios_20260805_154855.json → breakdown.data_sources.occupancy == "regional"`
  cuando el valor de occupancy usado (0.7843 = 800 reservas_mes / (34 hab × 30)) proviene del
  onboarding real.
- **Causa raíz**: DOS sitios en `main.py` recalculaban la condición con prioridad regional
  ignorando `_occupancy_source` (calculada correctamente en L1780):
  1. Bloque FASE-K (L2036): construcción de `HotelFinancialData` para
     `ScenarioCalculator.calculate_breakdown` → alimenta `breakdown.data_sources` del JSON.
  2. Input de `PrecisionValidator` (GAP-4, L2081): `_occ_source` → afecta `precision_tier`.
  Ambos se ejecutan SIEMPRE (independientes del camino harness/directo).
- **Cobertura real del fix S5 original (FASE-D)**: cubrió `harness_handlers.py` (L117-119) y los
  dicts `financial_sources` de main.py (L1899, L1958), pero NO estos dos sitios (lección L28:
  grepear TODOS los sitios de construcción antes de cerrar un fix de label).
- **Fix S5b aplicado (sesión de recuperación 2026-08-05)**: ambos sitios reutilizan
  `occupancy_source=_occupancy_source` / `_occ_source = _occupancy_source`.
- **Tests**: `tests/financial_engine/test_fase_f_recovery_s5b.py` (6 tests: 3 contrato estático
  anti-regresión sobre main.py + 3 comportamiento del camino FASE-K con datos de Zione).
- **Re-verificación**: run acotado 20260805_161042 (`output/v4_verify_s5b`,
  evidencia en `evidence/FASE-F/s5b_rerun/`): `data_sources.occupancy == "onboarding"`,
  occupancy_rate 0.7843 intacto, readiness READY_FOR_PUBLICATION.
- **Impacto del defecto**: solo trazabilidad/transparencia — el valor monetario siempre fue
  correcto. No afectó cifras, gates ni coherencia del run E2E oficial.

## Decisión de fase

FASE-F **✅ COMPLETA** (cerrada en la sesión de recuperación S5b del 2026-08-05):
- El run E2E ÚNICO oficial se ejecutó el 2026-08-05 (154910) con evidencia íntegra.
- V1-V10 = 10/10 PASS tras el fix S5b (re-verificación V8 en run acotado, según protocolo
  de recuperación acordado: el run oficial no se repite).
- Regresión: 0 (78 tests del batch S5b/loader + 208 de la lista segura FASE-A, todos passed).
- Validaciones: `run_all_validations.py --quick` 6/6 TOTAL PASS.

## Evidencia preservada (evidence/FASE-F/)

- `v4complete_run.log` — log completo del run (exit 0)
- `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260805_154910.md`
- `02_PROPUESTA_COMERCIAL_20260805_154910.md`
- 16 JSON de `v4_audit` (gate_report, commercial_gates, financial_scenarios, coherence, pain_ledger, etc.)
- `v4_complete_report.json`
- `zione_20260805.zip` (ZIP de entrega, 53 archivos)
- `verificacion.txt` (salida cruda del script)
- `validations_quick.txt` / `validations_quick_s5b.txt` (validaciones 6/6 pre y post S5b)
- `s5b_rerun/` (financial_scenarios + gate_report del run acotado de re-verificación V8)
- `v4complete_s5b_rerun.log` (log del run acotado S5b)
- `temp/verify_s7_loader.py` (verificación S7 pre-run)
