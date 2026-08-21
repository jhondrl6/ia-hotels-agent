# Plan Maestro — CREDIBILIDAD-NUMERICA-2026-08-20

> **Versión objetivo**: v4.72.0
> **Fuente**: CONTEXT-VALIDACION-COMERCIAL-CODIGO-VIVO-2026-08-19.md (§2 fallos F1-F10, §6.3 F11, §7.1 F12-F14, §3.3 priorización P0-P3)
> **Alcance**: P0 + P1 + P2 (26 elementos de la matriz de cobertura). P3 (deployer real, Express 5 páginas, monitoreo) queda EXPLÍCITAMENTE FUERA — post-validación de willingness-to-pay.

---

## 1. Mapeo Fallos → Fases → Archivos Principales

| Fallo | Descripción | Prioridad | Fase | Archivos principales (verificados en recon) |
|-------|-------------|-----------|------|----------------------------------------------|
| F1 | 5 fuentes de pricing contradictorias; constantes hardcodeadas en hook PDF; `is_compliant:false` no bloquea | P0 | P0-A, P0-B | `modules/commercial_documents/hook_pdf_generator.py` (constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE`), `modules/commercial_documents/v4_proposal_generator.py` (constantes fallback `MONTHLY_PACKAGE_PRICE`/`SETUP_FEE` L136-138, usadas en L548/L840/L922/L1005-1008/L1760 — duplican `packages` de pricing.yaml), `config/pricing.yaml`, `modules/quality_gates/publication_gates.py` |
| F7 | Encoding corrupto en artefactos (cp1252 por defecto en Windows) | P0 | P0-C | Todos los writers de artefactos (`open()`/`json.dump` sin `encoding='utf-8'`); evidencia: `delivery_quality_report.json` con UnicodeDecodeError |
| F2 | 3 valores de ADR para eje_cafetero ($285K/$420K/$200K) | P1 | P1-A | `config/regional_benchmarks.yaml` (ADR plano; también pain_narratives/confidence usados por diagnóstico y propuesta) vs `data/benchmarks/regional_adr_2026.json` (ADR por categoría; gana en runtime vía `modules/financial_engine/regional_adr_resolver.py`) vs `data/benchmarks/plan_maestro_data.json` (tercera fuente: cascada resolver → plan_maestro → default; 9+ consumidores) + docs comerciales |
| F4 | Bogotá en YAML pero ausente en JSON runtime | P1 | P1-A | Mismos que F2; verificar `REGION_ALIASES` en regional_adr_resolver.py (L136-138) y region_map en v4_comprehensive.py |
| F3 | Fallback `'colombia'→'caribe'` infla fuga 2.3-3.2x | P1 | P1-B | `modules/auditors/v4_comprehensive.py` (mapa de fallback de región, zona L1466 — verificar en ejecución) |
| F5 | Comisión OTA 15% hardcodeada vs 17-25% narrativa | P1 | P1-B | 5 sitios en 3 módulos: `modules/financial_engine/scenario_calculator.py` (L96, L118 `default_ota_commission`, L543 fuente `'industry_standard_15pct'`), `calculator_v2.py` (L442/L466), `inputs_contract.py` (L47), `modules/orchestration_v4/two_phase_flow.py` (L245 y L318), `modules/utils/benchmarks.py` (L28). Config: `config/financial_defaults.yaml` YA tiene `comision_ota: {min: 0.18, base: 0.20, max: 0.22}` (L14-17), con flatten en `financial_factors.py` (L78-86) y consumo en `main.py` L361 — usar ese campo, NO crear uno nuevo (D2) |
| F6 | Rango del hook 23x entre extremos | P1 | P1-C | `modules/orchestration_v4/two_phase_flow.py` + `onboarding_controller.py`. Causa raíz verificada: `_get_regional_benchmarks` (L215-230) devuelve `default_benchmarks` hardcodeados (min_rooms 15, max_rooms 50, min_adr 120000) porque `plan_maestro_data` NUNCA se pasa — `OnboardingController.__init__` (L58-61) es el único caller productivo y no lo pasa, aunque el constructor lo acepta (L93). El cap DEBE acompañarse del cableado (D4) |
| F11 | Sin verificación de continuidad Hook→Express ni narrativa de delta | P1 | P1-C | `modules/orchestration_v4/two_phase_flow.py`, `hook_pdf_generator.py` (`fuga_minima`/`fuga_maxima`), consistency checker |
| F12 | Falso positivo WhatsApp por cruce entre sedes | P1 | P1-D | `modules/data_validation/cross_validator.py` (`validate_whatsapp`, def L123) + 3 callers productivos: `main.py` L1735, `modules/auditors/v4_comprehensive.py` L1557, `modules/orchestration_v4/two_phase_flow.py` L371; scrapers de números web |
| F13 | `no_whatsapp_visible` HIGH con botón existente; `site_verification` no propagada | P1 | P1-D | `modules/asset_generation/pain_ledger.py`, diagnóstico (`v4_diagnostic_generator.py`), layer de site verification existente |
| F14 | Discrepancia coherence (FAILED) vs gate (PASSED) sobre `whatsapp_button` | P1/P2 | P2-A | `modules/commercial_documents/coherence_validator.py` (`promised_assets_exist`), gate `proposal_asset_alignment` |
| F8 | Occupancy con provenance mal etiquetado (valor ya corregido vía FASE-F recovery; etiqueta residual) | P2 | P2-A | Rutas de inyección Tier A en `main.py` / `harness_handlers.py` — verificar etiqueta `data_sources.occupancy` |
| F9 | Lista de prospectos no ejecutable (66 "Pendiente verificar", 1 teléfono) | P2 | P2-B | Nuevo script de pre-carga GBP batch; `evidence/Ingresos/01_Lista_Prospectos_Eje_Cafetero.md` |
| F10 | Documentación comercial desactualizada vs código | P2 | P2-B | `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md`, `docs/PRECIOS_PAQUETES.md` |
| C9 | Tiempo de corrida fresh desconocido | P2 | E2E | Medido en la corrida única de Zi One (output-dir default `output/v4_complete` — fresco para artefactos; PERO caches GLOBALES cálidos persisten: `data/cache/places_cache.json`, `data/cache/scraped_sites.json` — ver scraper_fallback.py L13-14. Registrar como "tiempo con caches cálidos") |

## 2. Secuencia y Justificación de Orden

```
P0 (prerrequisito absoluto, condición dura 1)
  P0-A pricing unificado ──→ P0-B gate pricing_compliance (consume P0-A)
  P0-C encoding (independiente)
        │
        ▼
P1 (cifra de fuga defendible, antes del primer hook)
  P1-A benchmark maestro ──→ P1-B fallback+OTA ──→ P1-C cap+trazabilidad
                                                      (consume benchmark estable)
  P1-D verdad sitio vivo (independiente de P1-A/B/C)
        │
        ▼
P2 (trazabilidad y ejecutabilidad comercial)
  P2-A coherence+occupancy (depende de P1-D para estado "verificado en producción")
  P2-B prospectos+docs (independiente; F1 debe estar cerrado para actualizar docs de pricing)
        │
        ▼
E2E-ZIONE (requiere TODAS las fases previas ✅)
        │
        ▼
FASE-RELEASE-4.72.0 (requiere E2E ✅)
```

## 3. Presupuesto de Complejidad por Fase

| Fase | Tareas (R3) | Comando largo | Complejidad | Delegable |
|------|-------------|---------------|-------------|-----------|
| P0-A | 4 (línea base + investigación pricing + refactor + tests) | 0 | Media | No |
| P0-B | 3 (diseño gate + registro + tests) | 0 | Media | No |
| P0-C | 3 (auditoría writers + fix + verificación artefactos) | 0 | Baja-Media (alcance amplio, fix mecánico) | Sí |
| P1-A | 4 (diseño maestro + migración + sync + tests) | 0 | Media-Alta | No |
| P1-B | 4 (baseline auditors + fix F3 + fix F5 + tests) | 0 | Baja-Media | Sí (2 tracks) |
| P1-C | 4 (cableado benchmark→hook D4 + cap F6 + trazabilidad F11 + tests) | 0 | Alta (diseño de falsabilidad) | No |
| **P1-D** | 4 (investigación + mapeo sedes F12 + propagación F13 + tests) | 0 | **MÁXIMA** | No |
| P2-A | 3 (F14 + F8 residual + tests) | 0 | Media | No |
| P2-B | 3 (script pre-carga + gate completitud + docs) | 0 | Media | No |
| E2E | 3 (verificar fixes + lecciones + docs) | 1 (v4complete) | Media (ejecución) | v4complete vía subagente |
| RELEASE | E1-E8 estándar | 0 | Baja | Sí |

## 4. Condiciones de Éxito del Plan (verificadas en FASE-E2E-ZIONE)

| # | Verificación | Expected en corrida Zi One |
|---|--------------|----------------------------|
| V1 | Precio en Hook PDF == precio en `financial_scenarios.json` | Un solo valor, desde `config/pricing.yaml` |
| V2 | Gate `pricing_compliance` presente en gate_report | PASSED para Zione. Diseño floor-aware (P0-B): BLOCKING solo si `pain_ratio > pain_ratio_gate_max` del tier (0.32 boutique); WARNING si fuera del rango ideal 0.03-0.06 con floor aplicado. Con umbrales globales como blocking, el ratio estructural 0.0724 de Zione haría imposible V12 |
| V3 | Artefactos JSON del ZIP leen sin UnicodeDecodeError | `delivery_quality_report.json` legible utf-8 |
| V4 | Un solo ADR de benchmark para eje_cafetero | Mismo valor en YAML/JSON/diagnóstico |
| V5 | Fallback 'colombia' resuelve a default conservador | No aparece `caribe` para dirección país-genérico |
| V6 | `ota_commission_source` reporta rango y fuente | Rango configurable, fuente citada |
| V7 | Rango del hook acotado (cap de plausibilidad) | Ratio max/min razonable (definido en P1-C) |
| V8 | Sin BRECHA 1 falsa de WhatsApp multi-sede | GBP Pereira vs web Pereira comparados por sede |
| V9 | `no_whatsapp_visible` resuelto/verificado en pain_ledger | No DETECTED HIGH si botón existe en sitio vivo |
| V10 | Coherence y gate de acuerdo sobre `whatsapp_button` | Ambos PASSED (estado "verificado en producción") |
| V11 | `data_sources.occupancy` con etiqueta correcta | `onboarding` para dato Tier A inyectado |
| V12 | Coherence ≥ 0.8 y gates sin regresión | READY_FOR_PUBLICATION (alcanzable gracias al diseño floor-aware de V2; sin regresión = sin fallos NUEVOS vs línea base §6) |
| V13 | Tiempo de corrida medido (C9) | Dato registrado en 10-analisis como "tiempo con caches cálidos" (los caches globales no se limpian con output-dir nuevo) |

## 5. Fuera de Alcance (explícito)

- P3: deployer real, Express 5 páginas, monitoreo mensual automatizado (post primer cliente pagado).
- Modificación de `ROADMAP.md` y ejecución de la batería de prospectos (F9 entrega el script; la ejecución batch es operativa).
- `observations.json`: solo lectura en este plan. Ciclo de retroalimentación benchmark ← observations documentado en P1-A (D3b), implementación diferida a P1-C/P2.
- Contacto comercial con prospectos.

## 6. Línea Base de Tests y Regla de Interpretación (verificada 2026-08-20)

**Línea base v4.71.0 (evidencia de ejecución, NO estimada)** — las suites que este plan toca tienen
**22 fallos preexistentes**:

| Suite | Archivo | Fallos |
|-------|---------|--------|
| tests/commercial_documents/ | `test_proposal_confidence_disclosure.py` | 5 (TestAssetQualityTable ×5) |
| tests/commercial_documents/ | `test_proposal_dynamic.py` | 7 (DynamicFiltering ×2, BackwardsCompatibility ×3, TechnicalAssetsTable ×1, Fase3LookupUnification ×1) |
| tests/financial_engine/ | `test_calculator_v2.py` | 2 (TestRecoveryFactorROI ×2) |
| tests/financial_engine/ | `test_pricing_resolution_wrapper.py` | 8 (TestActiveMode ×4, TestCanaryMode ×1, TestCalculatePriceWithShadowFunction ×1, TestEdgeCases ×1, TestIntegration ×1) |

**Regla obligatoria en TODAS las fases**: "suite sin regresiones" / "0 fallos" significa
**sin fallos NUEVOS respecto a esta línea base** — NO arreglar los preexistentes (quedarían como
seguimiento; arreglarlos diluiría el foco del plan). El AGENTS.md dice "0 regresión" pero la
ejecución viva muestra estos 22; el criterio operativo es la línea base documentada aquí.

**Acción P0-A (primera fase)**: capturar la línea base completa ANTES de cualquier cambio:
```powershell
.\venv\Scripts\python.exe -m pytest tests/commercial_documents tests/financial_engine tests/quality_gates tests/data_validation tests/orchestration_v4 -q --tb=no *> evidence/BASELINE-TESTS-v4.71.0.txt
```
(usar redirección a archivo, no pipe — lección L6 del plan RC1-RC2).

## 7. Decisiones de Diseño Obligatorias (pre-resueltas contra código vivo)

Estas decisiones estaban abiertas o contradichas en la versión original del plan; quedan resueltas
aquí para que los prompts las ejecuten sin re-abrir el análisis:

1. **D1 (P0-B, pricing_compliance floor-aware)**: `is_compliant` actual (pricing_calculator.py
   L372/L417) usa gates globales 0.03-0.06. Para fugas < 6.67M/mes con floor 400K, NINGÚN precio
   cumple → bloquear con ese criterio haría imposible V12. El gate usa como umbral BLOCKING el
   `pain_ratio_gate_max` del tier (0.32 boutique, ya existe en pricing.yaml) y WARNING por fuera del
   rango ideal cuando `operational_floor` aplicado. Precedente: PATCH-A en
   `coherence_validator._check_price_matches_pain` (max_ratio 0.50 para min_price floors).
2. **D2 (P1-B, comisión OTA)**: usar el campo EXISTENTE `comision_ota` de financial_defaults.yaml
   (0.18-0.22, dentro de la narrativa 17-25%) + añadir `source`. NO crear `ota_commission` nuevo.
   Cobertura: los 5 sitios hardcodeados (ver F5 §1); el flatten `comision_ota_min/base/max` ya
   existe en `financial_factors.py` L78-86 — los consumidores (`main.py` L361,
   `plan_validator.py` L38) no deben romperse.
3. **D3 (P1-A, benchmark master)**: **Resuelta: JSON (`regional_adr_2026.json`) como master.**
   Rationale: ya gana en runtime, estructura por categoría (boutique/standard) más granular
   que ADR plano del YAML, `default_region = "eje_cafetero"` alineado con nicho fundacional.
   YAML se adapta como vista legible o se depreca. La dimensión plano-vs-categoría y el
   destino de `plan_maestro_data.json` (tercera fuente viva con 9+ consumidores:
   regional_adr_resolver, v4_proposal_generator, v4_diagnostic_generator, scraper_fallback,
   dynamic_impact, utils/benchmarks, plan_validator, financial_factors) quedan documentados
   en `10-analisis-post-implementacion.md`.
   **D3b (retroalimentación benchmark ← observations)**: `observations.json` es activo
   estratégico creciente (contacto personal hotelero). El mecanismo de recalibración de
   benchmarks a partir de observaciones Tier A (umbral: ≥3 hoteles VERIFIED por región)
   se documenta en P1-A pero se implementa en fase posterior (P1-C o P2).
4. **D4 (P1-C, rango del hook)**: cablear el rango al benchmark master ANTES de aplicar el cap
   (el cap sobre defaults hardcodeados acota un rango fabricado). El constructor de
   `TwoPhaseOrchestrator` ya acepta `plan_maestro_data` (two_phase_flow.py L93); el cableado es
   en `OnboardingController` (L58-61) + alinear keys de región (`regions.get(region, default)` L230).
5. **D5 (P0-B, AGENTS.md)**: el conteo de gates en AGENTS.md es estático ("12 publication gates")
   y `validate_agents_md.py` check_3 lo compara contra el código. Actualizarlo EN P0-B (12→13,
   blocking 9→10) y validar con `python scripts/validate_agents_md.py`.
6. **D6 (P0-A, pricing.yaml fuente única)**: pricing.yaml es la única fuente de precios;
   `hook_pdf_generator.py` y `v4_proposal_generator.py` (constantes fallback `MONTHLY_PACKAGE_PRICE`/
   `SETUP_FEE` L136-138) consumen de ahí.

**Numeración unificada**: la tabla "Decisiones Arquitectónicas" del `10-analisis-post-implementacion.md`
refleja estas mismas D1-D6 (pre-resueltas) más D7 (cap percentil vs ratio — se decide en P1-C) y
D8 (estado "verificado en producción" — se decide en P1-D). Los prompts referencian estos IDs.
