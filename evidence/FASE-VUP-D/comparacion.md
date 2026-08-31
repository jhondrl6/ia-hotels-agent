# FASE-D — Comparación vs baseline H2 (VALIDADOR-URL-PROPIA)

**Run nuevo**: `output/FASE-D_salentoreal_post_guard/` — `v4complete --url https://www.hotelsalentoreal.com/`
**Fecha run**: 2026-08-31 17:25:02Z → 17:28:14Z (pared ~3 min) | **EXIT_CODE=0**
**Baseline**: `output/salentoreal_final_v4c_h2/` (FASE-SR-H2, 2026-08-28, smoke 7/7)
**Método**: `verificar_no_regresion.py` (parseo JSON UTF-8, sin regex de consola) → `verificacion_resultados.json`

## Tabla antes/después

| Métrica | Baseline H2 (2026-08-28) | Run post-guard (2026-08-31) | Δ / veredicto |
|---|---|---|---|
| Exit code | 0 | 0 | = |
| `hotel_id` (target_id) | `hotel_hotelsalentoreal.com` | `hotel_hotelsalentoreal.com` | = identidad correcta |
| `url` | `https://www.hotelsalentoreal.com/` | `https://www.hotelsalentoreal.com/` | = |
| coherence_score | 0.88 | 0.88 | = (≥ 0.8 ✓) |
| Readiness | READY_FOR_PUBLICATION | READY_FOR_PUBLICATION, blocking_issues=[] | = |
| Gates (13) | 13/13 PASSED | 13/13 PASSED, 0 regresiones, 0 faltantes, 0 extra | = perfil idéntico |
| Plan de assets | analytics_setup_guide(W,0.8), indirect_traffic_optimization(W,0.8), llms_txt(P,1.0), monthly_report(P,1.0) | idéntico (tipo, preflight, confianza) | = determinismo L-PF12 ✓ |
| Pains→assets | 3 pains MEDIUM → ASSET_GENERATED (no_analytics_configured, low_organic_visibility, ai_crawler_blocked) | idéntico; matriz sin diff_keys | = |
| Escenarios COP/mes | conservative 6,571,622.4 / realistic 4,042,752.0 / optimistic 1,264,435.2 | idénticos (byte-equal en `financial_data`) | = |
| Onboarding | defaults (Tier B: `direct_channel_percentage: "default"`) | "Using defaults (no fresh onboarding data found)" (log:166) | = equivalencia F5 ✓ |
| Guard URL propia | n/a (pre-guard) | 0 rechazos durante el run; única aparición de "guard" es la ruta del directorio de salida | ✓ ortogonal (AC3/AC8) |
| ZIP delivery | `hotelsalentoreal_20260828.zip` | `hotelsalentoreal_20260831.zip` | = (nombre con fecha) |

## Verificación automatizada: 7/7 checks PASSED

1. ✅ `1_target_id_hotelsalentoreal` — hotel_id y URL correctos
2. ✅ `2_coherence_ge_0.8` — 0.88 (igual al baseline)
3. ✅ `3_ready_for_publication` — sin blocking issues
4. ✅ `4_gates_sin_regresion_blocking` — 13 gates, perfil idéntico al baseline
5. ✅ `5_plan_assets_equivalente` — 4 assets, mismos tipos/preflight/confianza
6. ✅ `6_pains_to_assets_equivalente` — pain_ledger_resolved y proposal_asset_matrix idénticos
7. ✅ `7_financiera_identica_baseline` — escenarios byte-equal

## Anomalías observadas (clasificación L14, ninguna imputable al guard)

| Anomalía | Clasificación | Evidencia |
|---|---|---|
| Log:2,4 — `LLM query failed for gemini: 403 Forbidden` | Infraestructura (API key); el pipeline continuó y terminó exit 0 | providers opcionales de narrativa; exit 0 |
| Log:138 — `[3/5] performance metrics Status: ERROR (API key not valid)` | Infraestructura preexistente | `pagespeed_api` también `skipped` en el audit report del baseline H2 |

## Conclusión

AC3/AC8 verificados empíricamente: el guard de URL propia es ortogonal al flujo tradicional.
El E2E post-guard sobre sitio propio reproduce el baseline H2 con equivalencia exacta en
identidad, coherencia, gates, plan de assets, pains→assets y cifras financieras, corriendo
en las mismas condiciones (defaults, sin YAML de onboarding en `clientes/`).
