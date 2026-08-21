# Guía Técnica - IA Hoteles Agent

**Versión:** v4.71.0 (Coherencia Propuesta-Diagnóstico, Gates Comerciales y Entrega)
**Última actualización:** 2026-08-20

---

### Notas de Cambios v4.72.0-WIP — FASE-P0-A: Fuente única de pricing

**Fecha:** 2026-08-20

**Resumen**: Eliminación de constantes de pricing hardcodeadas en `hook_pdf_generator.py` y `v4_proposal_generator.py`. Ambos módulos ahora consumen `config/pricing.yaml` vía `_load_pricing_config()` (reutilizando infraestructura del financial engine). Nuevo campo `express_price` en pricing.yaml.

**Módulos afectados**: `modules/commercial_documents/hook_pdf_generator.py`, `modules/commercial_documents/v4_proposal_generator.py`, `modules/financial_engine/pricing_calculator.py`, `config/pricing.yaml`

**Problema**: 3 fuentes Python no sincronizadas de pricing (constantes en hook PDF, constantes en propuesta, pricing.yaml). El cliente podría ver $400K en el Hook PDF y $500K en la propuesta del mismo output.

**Solución**: D6 — pricing.yaml como fuente única. Constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE` (hook) y `MONTHLY_PACKAGE_PRICE/SETUP_FEE` (propuesta) eliminadas. Método `_get_pricing_packages()` con caché de instancia en ambos generadores.

**⚠️ Cambio de comportamiento documentado**:
- Hook PDF y propuesta comercial ahora leen precios de `config/pricing.yaml` dinámicamente. Cambios en pricing.yaml se reflejan automáticamente en ambos documentos sin editar código.
- El cache de pricing es a nivel de instancia (no módulo), por lo que cambios en pricing.yaml entre instancias de generadores se reflejan correctamente.

**Backwards compatibility**: API pública sin cambios. `HookPDFGenerator.__init__()` y `V4ProposalGenerator.__init__()` mantienen la misma firma. Tests existentes siguen pasando (valores numéricos de pricing.yaml coinciden con las constantes eliminadas).

**Tests**: +3 tests contrato F1 (TestPricingContractF1). 0 regresiones.

---

### Notas de Cambios v4.72.0-WIP — FASE-P0-B: Gate pricing_compliance floor-aware

**Fecha:** 2026-08-21

**Resumen**: Nuevo gate de publicación `pricing_compliance` (gate 13, BLOCKING). Diseño floor-aware (D1): BLOCKED solo si `pain_ratio > pain_ratio_gate_max` del tier (0.32 boutique); WARNING si fuera del rango ideal 0.03-0.06 con `operational_floor` aplicado. Sin este diseño, hoteles con fuga < $6.67M/mes y floor 400K nunca podrían cumplir ratio ≤ 0.06.

**Módulos afectados**: `modules/quality_gates/publication_gates.py`, `modules/assessment_builder.py`, `main.py`, `AGENTS.md`

**Problema**: `financial_scenarios.json` reporta `is_compliant: false` (pain_ratio 0.0724 > 0.06 del gate global) y ningún gate lo bloquea. Un gate BLOCKING con umbral global 0.06 haría imposible la publicación de hoteles con floor aplicado.

**Solución**: D1 — Gate floor-aware. Umbral BLOCKING = `pain_ratio_gate_max` del tier (0.32 boutique, ya en pricing.yaml). WARNING si ratio fuera del rango ideal con floor aplicado (structural inflation). Precedente: PATCH-A en `coherence_validator._check_price_matches_pain` (max_ratio 0.50 para floors).

**Backwards compatibility**: El nuevo gate no afecta los 12 existentes. `AssessmentBuilder.with_pricing()` es optional (sin pricing_data → gate PASSED/skipped). AGENTS.md actualizado a 13 gates (validate_agents_md.py PASS).

**Tests**: +18 tests nuevos (TestPricingComplianceGate). 0 regresiones (340 passed en quality_gates).

---

### Notas de Cambios v4.72.0-WIP — FASE-P0-C: Encoding utf-8 en writers de artefactos

**Fecha:** 2026-08-21

**Resumen**: Fix del fallo F7 — todos los writers de artefactos (`Path.write_text()`) en `modules/` ahora usan `encoding='utf-8'` explícito. Causa raíz: Windows usa cp1252 por defecto en `open()`/`write_text()` sin encoding, produciendo mojibake y `UnicodeDecodeError` en artefactos JSON de entrega.

**Módulos afectados**: `modules/quality_gates/delivery_quality_report.py`, `modules/utils/config_checker.py`

**Problema**: `delivery_quality_report.json` dentro del ZIP de entrega lanzaba `UnicodeDecodeError` (byte 0xf3). Mojibake "B+ ? Datos fuente" en diagnóstico. El writer `save()` usaba `path.write_text(json.dumps(...))` sin encoding.

**Solución**: Agregado `encoding="utf-8"` en 3 writers (1 crítico en delivery_quality_report + 2 preventivos en config_checker). Test de contrato anti-regresión con auditoría estática AST que verifica que NINGÚN `write_text()` en `modules/` carezca de encoding.

**Backwards compatibility**: 100%. El fix no cambia lógica de negocio, solo agrega encoding explícito. Los readers ya usaban `encoding="utf-8"` (ver `_load_json` en delivery_quality_report.py).

**Tests**: +4 tests nuevos (TestDeliveryQualityReportEncoding + TestEncodingContractStatic). 470 passed en suite delivery+quality_gates+encoding. 0 regresiones.

---

### Notas de Cambios v4.71.0 — Coherencia Propuesta-Diagnóstico, Gates Comerciales y Entrega

**Fecha:** 2026-08-05

**Resumen**: Eliminación de 3 causas raíz residuales del plan v4.70.0: RC1 (propuesta con costos hardcodeados que no consumen `opportunity_scores`), RC2 (gates comerciales con inputs no cableados + ZIP con reportes BLOCKING junto a docs PASSED), RC3 (higiene documental sin enforcement). Plan RC1-RC2-ENTREGA-COHERENTE-2026-08-04 con 7 fases (A-F + RELEASE), verificado E2E con Zi One Luxury (coherence 0.9238, READY_FOR_PUBLICATION).

**Módulos afectados**: `modules/commercial_documents/`, `modules/quality_gates/`, `modules/delivery/`, `modules/financial_engine/`, `main.py`, `scripts/run_all_validations.py`

**Problema** (3 causas raíz):
- **RC1 (ALTA)**: `BREACH_BY_ASSET` estático en `v4_proposal_generator.py` con costos factor 0.671× respecto al diagnóstico. El pipeline produce `opportunity_scores` pero la propuesta no los consume.
- **RC2 (MEDIA)**: `CG-CLAIM-VS-EVIDENCE` dispara falso positivo con texto condicional; `CG-TIER-CONSISTENCY` pasa vacuo siempre; ZIP transporta `commercial_gates_report` BLOCKING junto al doc PASSED.
- **RC3 (BAJA)**: Prompts con `--release` en fases intermedias, conteos desactualizados, evidencia no preservada.

**Solución**: 7 fases de implementación (A-F + RELEASE):
1. **FASE-A**: Cuarentena de 3 tests patológicos + lista segura (40 tests aislados)
2. **FASE-B**: `_build_dynamic_breach_map()` — mapa inverso `pain_solution_mapper` → `opportunity_scores`. `BREACH_BY_ASSET` estático eliminado
3. **FASE-C**: `CG-CLAIM-VS-EVIDENCE` split por oraciones + filtro condicionales; `CG-TIER-CONSISTENCY` cableado con `_extract_text_tier()`
4. **FASE-D**: Política ZIP (`_is_excluded_from_zip`) + fallback loader onboarding + occupancy label veraz
5. **FASE-E**: Enforcement `_check_prompts_no_release()` en `run_all_validations.py` + conteos fuente viva
6. **FASE-F**: Run E2E único Zi One Luxury (coherence 0.9238) + recuperación S5b (occupancy_source en FASE-K + PrecisionValidator)
7. **FASE-RELEASE**: Version bump, CHANGELOG, GUIA_TECNICA, sync, validaciones

**⚠️ Cambio de comportamiento documentado**:
- **Tabla de servicios dinámica**: La propuesta ahora consume `opportunity_scores` del pipeline. Costos, ranks y labels son idénticos a los del diagnóstico (construcción dinámica vía mapa inverso).
- **CG-CLAIM-VS-EVIDENCE**: Ya no dispara falso positivo con texto condicional ("si...no aparece"). Split por oraciones + filtro de marcadores condicionales.
- **CG-TIER-CONSISTENCY**: Ahora valida inputs reales. `None` → FAIL explícito (nunca pasa vacuo). Caller cablea `frontmatter_tier` + `text_tier`.
- **Política ZIP**: `commercial_gates_report*` excluido del ZIP de cliente. Filtro por run más reciente (mtime cutoff).

**Backwards compatibility**: La firma de `validate_diagnostic()` recibe nuevos parámetros (`frontmatter_tier`, `text_tier`) — ambos opcionales con default `None`. Si no se proveen, el gate falla explícitamente (comportamiento deseado). API pública de `v4complete` sin cambios.

**Tests**: +58 tests nuevos (9 FASE-B + 20 FASE-C + 23 FASE-D + 6 FASE-F/S5b). 0 regresiones. 3,233 tests collected (post-cuarentena FASE-A). V1-V10: 10/10 PASS.

**E2E verificación**: Zi One Luxury — coherence 0.9238, READY_FOR_PUBLICATION (12 gates: 11 passed + 1 WARNING advisory `asset_confidence`, 0 blocking). Onboarding real ("4 campos confirmados"). Run oficial `output/v4_verify_4.71.0` + recuperación S5b `output/v4_verify_s5b`.

**Seguimientos abiertos**:
- S5b: ✅ CERRADO (recuperación aplicada, 6 tests anti-regresión)
- S8: Tier B+ (frontmatter) vs D (texto) — inconsistencia de contenido real detectada por CG-TIER-CONSISTENCY (MEDIA, próximo release)
- S9: Numeración divergente en brechas (BAJA, cosmético)

---

### Notas de Cambios v4.70.0 — Coherencia Módulo-Entrega

**Fecha:** 2026-08-04

**Resumen**: Eliminación de 21 desconexiones módulo↔entrega (D1-D12 + N1-N9) detectadas en el
diagnóstico V6 de Zione. El plan COHERENCIA-MODULO-ENTREGA-2026-08-03 corrigió problemas de
veracidad de contenido, honestidad financiera, gates de calidad, textos dinámicos, freshness
de artefactos y pulido de texto, verificados E2E con Zi One Luxury (coherence 0.9168, Tier B+).

**Módulos afectados**: `modules/commercial_documents/`, `modules/financial_engine/`,
`modules/quality_gates/`, `modules/delivery/`, `main.py`, `config/regional_benchmarks.yaml`

**Problema**: 21 desconexiones entre lo que los módulos calculan y lo que los documentos entregan:
- D1-D2: Contenido falso ("Sin Meta Tags" con 8 tags detectados, conteo de brechas inconsistente)
- D3-D4, N1: Finanzas divergentes (costos diferentes entre doc y report, escenarios ocultados, recuperación 6m inconsistente)
- D5, N2: Gates que no detectan contradicciones doc↔audit
- D6-D8: Textos estáticos que mienten (performance, reviews, atribución GEO)
- D9-D12, N3-N8: Freshness, duplicados, labels incorrectos, texto en portugués, truncamiento

**Solución**: 6 fases de implementación (A-E + RELEASE):
1. **FASE-A**: `_pain_to_brecha` usa `pain.name`/`description`; detección única de brechas; template con conteo dinámico
2. **FASE-B**: `estimated_monthly_cop` alineado con pesos normalizados; fórmula única `calcular_recuperacion_6m()` en `pillar_maturity_curve.py`
3. **FASE-C-A**: `_coverage_gate` reestructurado; nuevo gate `_doc_audit_consistency_gate` (WARNING, DEC-C1)
4. **FASE-C-B**: Performance dinámico (lee `performance.status`); reviews parametrizadas; atribución GEO corregida
5. **FASE-D**: `TARGET_GBP_PHOTOS=40`; dedup redes; `_occupancy_source` tracking; freshness v4_audit; pulido texto
6. **FASE-E**: E2E Zi One Luxury — 21/21 verificados, coherence 0.9168, Tier B+

**⚠️ Cambio de comportamiento documentado**:
- **Pesos sobre N real (D2)**: Los costos de brecha ahora se calculan sobre el N real de brechas detectadas (no sobre un número fijo). Esto cambia las cifras de TODOS los hoteles.
- **Fórmula única de recuperación (N1)**: `calcular_recuperacion_6m()` usa una sola fórmula con curva de maduración 4 pilares. Esto cambia las cifras de recuperación de TODOS los hoteles.

**Backwards compatibility**: API pública sin cambios. Nuevos campos opcionales en `HotelFinancialData` (`ga4_enabled`, `gsc_enabled` ya existían desde v4.68.0). Gate `doc_audit_consistency` nace en modo WARNING (no bloquea publicación).

**Tests**: +35 tests nuevos (6 FASE-A + 8 FASE-B + 13 FASE-C-A + 8 FASE-C-B). 0 regresiones en código modificado. 21/21 hallazgos verificados E2E.

**E2E verificación**: Zi One Luxury — coherence 0.9168, evidence_tier B+, 12 gates PASSED, coverage_no_silent_drop 8+1/9, ZIP sin históricos. Run final `output/v4_verify_4.70.0` (timestamp 20260804_124443).

**Seguimientos abiertos**:
- S5: label `"occupancy": "regional"` residual en `breakdown` de `financial_scenarios.json` (el valor y `financial_sources` del gate_report son correctos)
- S6: `execution_trace` lista `pagespeed_api` en executed Y skipped (deduplicar señal)
- S7: loader de onboarding sin fallback a `output/clientes` con `--output` alternativo (workaround documentado)

---

### Notas de Cambios v4.69.0 — Delivery ZIP Single-Write Architecture

**Fecha:** 2026-08-01

**Resumen**: Corrección del fallo crítico de delivery packaging. El pipeline v4complete generaba
contenido correcto pero NUNCA materializaba el ZIP de entrega. Causa raíz: arquitectura 3-pass
measure-then-mutate con README post-medición (-18 bytes) y self-reference inestable del MANIFEST.

**Módulos afectados**: `modules/delivery/`, `main.py`

**Problema**: Delivery ZIP nunca se materializaba: Bug 1 (README post-medición -18 bytes), Bug 2 (self-reference inestable), Bug 3 (tests con 5% tolerancia)

**Solución**: Single-write architecture: calcular en memoria, escribir UNA vez, fixed-point iteration para MANIFEST self-reference

**Backwards compatibility**: API pública de `package()` sin cambios. Modo legacy preservado.

**Cambios principales**:

1. **Single-write architecture** — Elimina 3-pass measure-then-mutate. Contenido calculado en memoria y escrito una sola vez.
2. **Fixed-point iteration** — MANIFEST self-reference resuelto con iteración a punto fijo (converge en ≤3 iteraciones).
3. **Error handling NF-3** — Severidad ERROR en fallo de delivery (antes WARNING silencioso).
4. **Cleanup NF-4** — Archivos temporales eliminados post-packaging.
5. **Datetime NF-5** — Timestamps ISO 8601 en MANIFEST.
6. **Tests exactos** — Tolerancia 5% eliminada, validación exacta por archivo.

---

### Notas de Cambios v4.68.0 — Evidence Tier Honesty

**Fecha:** 2026-07-31

**Resumen**: Corrección de falsa confianza en el Evidence Tier de v4complete. El sistema ahora
verifica `ga4_enabled`/`gsc_enabled` antes de asignar Tier A. Nuevo tier intermedio B_PLUS
para hoteles con datos operativos verificados pero sin GA4/GSC. Nuevo gate comercial
CG-EVIDENCE-TIER-CONSISTENCY (BLOCKING, per-hotel) que bloquea delivery si Tier A sin GA4+GSC.

**Cambios principales**:

1. **EvidenceTier.B_PLUS** — Nuevo valor de enum `"B+"` con disclaimer honesto:
   "Datos operativos verificados de su hotel. Para subir a Tier A, conecte GA4 y Search Console."
   Tier A ahora requiere `ga4_enabled AND gsc_enabled`. Sin GA4/GSC → máximo B+.

2. **`_determine_evidence_tier()` refactorizado** — Ahora recibe y consulta `ga4_enabled`/`gsc_enabled`
   como flags booleanos. `HotelFinancialData` extendido con dos campos nuevos. La fuente de verdad
   es unificada: el tier, el disclaimer, y el CTA derivan de la misma consulta.

3. **Gate CG-EVIDENCE-TIER-CONSISTENCY** — Nuevo gate comercial BLOCKING que recibe params per-hotel
   (`ga4_available`, `gsc_available`, `financial_json`). Bloquea delivery si Tier A + !GA4.
   Para tiers != A, retorna INFO (no visible en reportes). Respeta arquitectura per-hotel:
   NO usa `os.getenv` global.

4. **Proposal honesty** — `has_onboarding` ahora es dinámico (sin fallback silencioso a False).
   Disclaimer condicional por tier real. `precision_tier` visible en template diagnóstica.
   Relationship text dinámico.

5. **MANIFEST enrichment** — `quality_metadata` agregado a MANIFEST.json en `delivery_packager.py`
   (evidencia, tier, GA4/GSC flags).

6. **Consumers downstream limpios** — `hook_pdf_generator` acepta B+. `publication_gates`
   `tier_message` usa lógica dinámica. Default `evidence_tier` en diagnostic generator es "C"
   (conservador).

**20 hallazgos resueltos**: 12 originales del plan (H1-H12) + 8 nuevos de auditoría pre-ejecución
(NP1-NP8). Ver `CHANGELOG.md [4.68.0]` para matriz completa.

**Módulos afectados**: `data_structures.py`, `scenario_calculator.py`, `hook_pdf_generator.py`,
`publication_gates.py`, `v4_diagnostic_generator.py`, `v4_proposal_generator.py`,
`commercial_gate.py`, `delivery_packager.py`, `diagnostico_v6_template.md`, `main.py`

**Tests**: 22 tests nuevos en `test_evidence_tier.py`. 5 suites pre-existentes validadas sin
regresiones (NP3). Total: 3,180 tests, 0 regresiones introducidas por B_PLUS.

**v4complete E2E**: Zi One Luxury (Tier B+, honesto), Hotel Vísperas control sin onboarding
(Tier B, sin regresión). 20/20 hallazgos verificados.

**Backwards compatibility**: Total. `B_PLUS` es un nuevo valor de enum que no rompe consumidores
existentes. `_determine_evidence_tier()` mantiene firma compatible (nuevos params son opcionales).
Gate CG-EVIDENCE-TIER-CONSISTENCY retorna INFO para tiers != A (no bloquea pipelines existentes).

### Notas de Cambios v4.67.0 — Onboarding Injection Fix

**Fecha:** 2026-07-29

**Resumen**: Corrección del gap de inyección de datos entre `onboard` y `v4complete`.
El matching de datos de onboarding ahora usa URL normalizada como identidad canónica,
eliminando la dependencia de slug derivado de nombre. Nuevo fallback a `observations.json`
cuando no hay YAML de onboarding.

**Mecanismo de matching por URL**:

1. **`_normalize_url()`** — Función pura de normalización de URLs. Ignora protocolo,
   www, trailing slash, path, y query string. Produce una clave determinística para
   matching. Ejemplo: `https://www.hotel.com/?ref=1` → `hotel.com`.

2. **`_load_latest_onboarding_data()`** — Reescrita con iteración por glob sobre
   `data/onboarding/` + matching por URL normalizada. Acepta parámetro `output_dir`
   configurable. Si no encuentra YAML, aplica fallback a `observations.json` vía
   `_observation_to_onboarding_format()`.

3. **Fallback a `observations.json`** — `_observation_to_onboarding_format()` convierte
   registros de `data/hotel_observations/observations.json` al formato de onboarding YAML,
   usando `website` como clave de matching. Esto permite que hoteles con observaciones
   pero sin onboarding formal igual reciban inyección de datos.

**Módulos afectados**: main.py, modules/onboarding/data_loader.py,
modules/financial_engine/scenario_calculator.py, data/hotel_observations/observations.json

**Bugs resueltos**: Slug mismatch onboard↔v4complete, ventana de frescura hardcodeada,
hotel_url ignorado, output_dir hardcodeado, user_provided invisible al tiering

**Backwards compatibility**: Total. `_normalize_url()` es función nueva sin consumidores
previos. `_load_latest_onboarding_data()` mantiene firma compatible. Fallback a
observations.json es opt-in (solo se activa si no hay YAML).

### Notas de Cambios v4.66.0 — DT-4 Residual Fixes

**Fecha:** 2026-07-28

**Resumen**: Corrección de la causa raíz del coverage gate failure: pain_ledger_resolved
no se inyectaba (faltaba hotel_id/ en el path), SitePresence con shapes incompatibles,
coherence/alignment sin fuente única, gates con doble ejecución, y divergencia delivery-vs-gate.

**Módulos afectados**: assessment_builder, v4_asset_orchestrator, coherence_validator,
publication_gates, delivery_quality_report, alignment_result, site_presence_adapter, main

**Problema**: El coverage gate (coverage_no_silent_drop) fallaba por dos causas raíz:
1. El path de pain_ledger_resolved.json en main.py:2690 no incluía hotel_id/ — el archivo
   reconciliado existía en disco pero nunca se cargaba.
2. SitePresence se calculaba 4+ veces con shapes incompatibles (dataclass, dict, enum, SimpleNamespace).

Adicionalmente: el score de coherencia no tenía fuente única, los gates se ejecutaban dos veces
mutando el assessment, y el delivery_quality_report divergía del gate_report en alignment totals
porque from_asset_alignment_matrix() leía el JSON estático pre-enriquecimiento SitePresence.

**Solución**:
1. Campo `pain_ledger_resolved` en AssessmentPayload + builder method + path corregido en main.py
2. Adapter canónico `normalize_site_presence()` que acepta dataclass/dict/enum → dict unificado
3. `final_coherence_report` como fuente única (pre/post conservados como trazabilidad)
4. `AlignmentResult` DTO compartido; `from_asset_alignment_matrix()` cross-referencea SitePresence
5. `check_publication_readiness()` deriva de gate_results existentes sin re-ejecutar

**Issues comerciales conocidos**:
- CG-ROI-NEGATIVE: Zi One requiere onboarding con datos reales (actualmente usa defaults regionales)
- CG-TECH-JARGON: Jerga técnica en vista gerencia; no bloqueante

**Backwards compatibility**:
- Campos nuevos con default factory=list → consumidores existentes no afectados
- `check_publication_readiness()` mantiene firma original
- `CoherenceValidator.validate()` mantiene site_presence_report como keyword opcional
- `from_asset_alignment_matrix()` mantiene site_presence_report=None como default
- `DeliveryQualityReportGenerator.generate()` mantiene site_presence_report=None como default

### Notas de Cambios v4.65.0 — Root Cause Reconciliation (DT-4)

**Fecha:** 2026-07-27

**Resumen**: Resolución de la causa raíz transversal post-DT-3: 3 fuentes de verdad no consolidadas
para "este pain está resuelto?". Implementación de reconciliador post-orchestrator + 4 fixes
complementarios (commercial gates visibles, reinterpretación optimista, monthly_report alignment,
rename gates coverage). 4 bugs (2 CRÍTICOS, 2 MEDIOS) + 5 hallazgos resueltos.

**Módulos afectados**: `modules/orchestration/` (NUEVO), `modules/asset_generation/v4_asset_orchestrator.py`,
`modules/quality_gates/publication_gates.py`, `modules/quality_gates/coherence_validator.py`,
`modules/quality_gates/commercial_gate.py`, `modules/quality_gates/delivery_quality_report.py`,
`modules/commercial_documents/v4_proposal_generator.py`,
`modules/asset_generation/proposal_asset_alignment.py`, `main.py`

**Problema**: 3 sistemas evaluaban independientemente si un pain estaba resuelto (pain_ledger,
proposal_asset_matrix, skipped_assets) sin reconciliación post-orquestador. Esto causaba falsos
positivos en coverage gate (BUG-6), divergencia G9 (BUG-9), commercial gates invisibles (BUG-7),
optimista negativo bloqueante (BUG-8), y monthly_report contando en alignment (BUG-10).

**Solución**:
- FASE-0: `PostOrchestratorReconciler` en `modules/orchestration/` — nuevo módulo que consolida
  3 fuentes en `pain_ledger_resolved.json` con estados unificados (ASSET_GENERATED, MAPPED_TO_SERVICE,
  JUSTIFIED_SKIP). Cableado en `v4_asset_orchestrator.py` post-generación. Coverage gate lee
  `pain_ledger_resolved` con fallback a `pain_ledger`. `ASSET_GENERATED` en `_JUSTIFIED_STATUSES`.
  `_check_whatsapp_verified()` acepta `site_presence_report` opcional para boost de confidence.
- FASE-2: `commercial_gates_report.json` persistido en v4_audit. `BLOCKED_BY_GATES.md` ampliado
  con sección commercial gates + acción corregida (ya no dice "vuelva a ejecutar").
- FASE-1: `_check_scenario_negative` degrada a WARNING cuando optimista<0<realista.
  `_check_scenario_order` hace PASS en break-even.
- FASE-3: `monthly_report` removido de `PROPOSAL_SERVICE_TO_ASSET`.
- FASE-4: Publication G11 `coverage` → `coverage_no_silent_drop`. Delivery G7 `coverage_gate` → `coverage_failure_rate`.

**Tests**: 3104 tests totales (0 regresiones). Nuevos tests: FASE-0 (3 reconciliador), FASE-1 (4 BUG-8),
FASE-2 (5 persistencia + BLOCKED_BY_GATES), FASE-3 (14 actualizados), FASE-4 (279 actualizados).

**v4complete Zi One Luxury**: Exit 0, 73 archivos. Reconciliador: 9 entries (8 ASSET_GENERATED + 1 MAPPED_TO_SERVICE).
Commercial gates: 3 gates (1 BLOCKING + 2 WARNING). Gate names confirmados. monthly_report excluido.

**Hallazgos residuales**: `MAPPED_TO_SERVICE` no está en `_JUSTIFIED_STATUSES` — coverage gate sigue FAIL
en `no_whatsapp_visible` (el status no se reconoce como justificado). Coherence `whatsapp_verified` score 0.30
— el boost de SitePresence no se activó para Zi One. Ambos requieren follow-up post-release.

**Backwards compatibility**: ✅ `pain_ledger_resolved` tiene fallback a `pain_ledger`. Coverage gate funciona
igual sin reconciliador. Gate names antiguos solo afectan reportes, no lógica. Sin breaking changes.

### Notas de Cambios v4.64.0 — Tech Debt Resolution (DT-3)

**Fecha:** 2026-07-25

**Resumen**: Resolución de 4 bugs de technical debt post-DT-2 (1 CRÍTICO, 3 MEDIOS).
Corrección sistémica de rutas flat → per-hotel, unificación de ProposalAssetMatrix +
AlignmentReport en AssetAlignmentMatrix, y fixes al gate G9.

**Módulos afectados**: `main.py`, `modules/quality_gates/delivery_quality_report.py`,
`modules/asset_generation/proposal_asset_alignment.py`,
`modules/commercial_documents/v4_proposal_generator.py`

**Problema**: Post-DT-2, 3 archivos JSON se leían de ruta flat inexistente causando
pain_ledger vacío (BUG-1). G9 aparecía en blocking_gates y warning_gates simultáneamente
(BUG-2) y evaluaba asset_path en vez de status (BUG-3). ProposalAssetMatrix y
AlignmentReport tenían taxonomías divergentes (BUG-4/P-04).

**Solución**:
- BUG-1: Helper `_get_pipeline_path()` que resuelve rutas per-hotel dinámicamente.
  3 rutas flat corregidas en main.py (L2571, L2572, L2650).
- BUG-2: Constante `BLOCKING_GATE_NAMES` usada para generar ambas listas (blocking y
  warning), eliminando la duplicación.
- BUG-3: Helper `_is_service_aligned()` evalúa status (LINKED=True, NO_BREACH=True,
  resto=False). `actionable_services` excluye NO_BREACH. Pass condition verifica
  `all(not aligned)` → False (hay servicios sin asset).
- BUG-4/P-04: `AssetAlignmentMatrix` con `AlignmentStatus` enum (LINKED, NO_BREACH,
  MISSING_ASSET). Taxonomía unificada que reemplaza ProposalAssetMatrix y AlignmentReport.
  Consumidores migrados: G9, publication_gates.py, v4_proposal_generator.py.

**Helper `_get_pipeline_path()`**: Resuelve rutas de pipeline per-hotel desde
`pipeline_dir / hotel_slug / filename`. Si el archivo per-hotel no existe, devuelve
la ruta flat como fallback (backward compatible).

**AssetAlignmentMatrix**: Clase unificada en `proposal_asset_alignment.py` con:
- `AlignmentStatus` enum: LINKED (servicio tiene asset), NO_BREACH (servicio no necesita
  asset), MISSING_ASSET (servicio debería tener asset pero no lo tiene)
- `build(delivery_context, pain_ledger)` → matriz con entradas por servicio
- Consumido por G9 para status-based evaluation (NO_BREACH no bloquea, MISSING_ASSET sí)

**Tests**: 86 tests existentes PASS (0 regresiones) + 14 tests nuevos AssetAlignmentMatrix
(14/14 PASSED). v4complete Zi One Luxury verificado: BUG-1 (9 entries pain_ledger),
BUG-2 (solo blocking), BUG-3 (NO_BREACH no bloquea), BUG-4 (AssetAlignmentMatrix unificado).

**Backwards compatibility**: ✅ `_get_pipeline_path()` tiene fallback a ruta flat.
AssetAlignmentMatrix mantiene el mismo contrato JSON. G9 mantiene comportamiento
bloqueante para MISSING_ASSET. Tests existentes sin cambios.

### Notas de Cambios v4.63.2 — Delivery Contract Residual Fixes (DT-2)

**Fecha:** 2026-07-25

**Resumen**: Corrección de 7 findings residuales post-DT-1 en el delivery contract.
El quality report ahora usa el score de coherencia post-generación, el G9 gate
evalúa alineación real (ya no hardcodea default True), los advisory assets tienen
exclusión mutua en secciones del README, y la proposal_asset_matrix se empaqueta
en el ZIP de entrega.

**Módulos afectados**: `modules/delivery/delivery_packager.py`, `modules/delivery/delivery_context.py`,
`modules/quality_gates/delivery_quality_report.py`, `modules/asset_generation/proposal_asset_alignment.py`,
`modules/commercial_documents/v4_proposal_generator.py`, `tests/delivery/test_delivery_contract.py`

**Cambios**:
- P-01: README Overview conteo post-manifest (recalculado después de Pass 3)
- P-02: Exclusión mutua advisory assets en secciones state-based del README
- P-03: delivery_quality_report usa coherence score post-generación (`coherence_validation_post_gen.json`)
- P-04: proposal_asset_matrix path alineado con DeliveryContext (divergencia documentada como deuda v4.64.0)
- P-05: G9 proposal_asset_alignment gate implementado (evalúa alineación real, ya no default True)
- P-06: proposal_asset_matrix.json empaquetado en el ZIP de entrega
- P-07: Comparación string-vs-enum unificada a `DeliveryAssetState.DELIVERED`

**Tests**: 28 tests existentes + 14 nuevos = 42 tests de contrato (42/42 PASSED).
v4complete Zi One Luxury: verificación E2E de 7 fixes (S-1 a S-9).

**Backwards compatibility**: ✅ El packager mantiene comportamiento legacy sin DeliveryContext.
Los filtros de advisory son aditivos (no rompen comportamiento previo). G9 es evaluado
pero solo bloquea si `GATE_BLOCKING_ENABLED=true`.

### Notas de Cambios v4.63.1 — Delivery Contract

**Fecha:** 2026-07-24

**Resumen**: El sistema de delivery ahora garantiza consistencia cross-artifact
(README ↔ MANIFEST ↔ ZIP) mediante un contrato canónico de estados de assets.

**Módulos afectados**: `modules/delivery/`, `modules/assessment_builder.py`

**Arquitectura**: `DeliveryAssetState` → `DeliveryAssetEntry` (con `is_advisory`) → `DeliveryContext` (con `from_asset_generation_report()`) →
template modular → validación post-zip obligatoria.

**Backwards compatibility**: El packager mantiene comportamiento legacy si no recibe
`DeliveryContext`. La template legacy se reemplazó completamente; los placeholders
nuevos quedan vacíos en modo legacy.

### Notas de Cambios v4.63.0 — ASSET-ALIGNMENT

**Fecha:** 2026-07-23

**Módulos afectados:**
- `modules/quality_gates/delivery_quality_report.py`
- `modules/commercial_documents/pain_solution_mapper.py`
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/service_catalog.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `modules/asset_generation/open_graph_generator.py`
- `modules/asset_generation/conditional_generator.py`
- `modules/asset_generation/proposal_asset_matrix.py`
- `modules/delivery/delivery_packager.py`
- `main.py`

**Problema:**
Gate 9 (`proposal_asset_alignment`) BLOCKED era ignorado por 3 capas de bypass en delivery_quality_report (key name mismatch, hardcoded passed=True, GATE_BLOCKING_ENABLED default off). Gaps Pain→Asset: `low_seo_score` no existía como pain type, `no_og_tags` solo se activaba con 0 OG tags (no detectaba tags incompletos), OpenGraphGenerator no aceptaba tags existentes. Clave duplicada `whatsapp_conflict` en PAIN_TO_ASSET. Propuesta mostraba servicios sin asset generado como "Pendiente". SERVICE_TO_ASSET_LOOKUP derivado de fuente incorrecta.

**Solución:**
- FASE-1: delivery_quality_report consume key correcta (`proposal_asset_alignment`) + blocking_gates; GATE_BLOCKING_ENABLED default `true`
- FASE-2: Nuevo pain `low_seo_score` (web_score < 40 → optimization_guide); `no_og_tags` modo enhance_existing; OpenGraphGenerator acepta existing_og_tags; clave duplicada eliminada
- FASE-3: `_generate_dynamic_services_table()` condicional; SERVICE_TO_ASSET_LOOKUP unificado con PROPOSAL_SERVICE_TO_ASSET
- FASE-4: Template Tier C variable + serialización dicts + MANIFEST dinámico + label financiero + test fix
- FASE-5: v4complete Zi One Luxury — Gate 9 PASSED, coherence ≥ 0.80, 13 hallazgos verificados

**Tests:** 16 tests nuevos (5 bypass fix + 5 enhance_existing + 6 conditional/lookup). 0 regresiones. v4complete Zi One Luxury: Gate 9 PASSED.

**Backwards compatibility:** ✅ GATE_BLOCKING_ENABLED se puede desactivar con env var. Propuesta condicional no elimina servicios, los marca como disponibles. OpenGraphGenerator sin existing_og_tags mantiene comportamiento original.

---

### Notas de Cambios v4.62.0 — BUGS-ONBOARDING-ADR

**Fecha:** 2026-07-22

**Módulos afectados:**
- `main.py`
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/v4_proposal_generator.py`

**Problema:**
- ADR y occupancy del onboarding no se propagaban al harness financiero. El pipeline ignoraba estos datos y usaba benchmarks regionales.
- CTAs "Complete el onboarding" aparecían incluso cuando ya existía onboarding (7 superficies).
- Taxonomía de fuentes (ADRSource) inconsistente entre diagnóstico, propuesta y JSON.

**Solución:**
- Propagación directa de ADR y occupancy del onboarding al harness payload.
- ADRSource enum unificado entre módulos.
- CTAs condicionadas a `has_onboarding`.
- ValidationSummary refleja fuente real del valor.

**Tests:** e2e onboarding pipeline + 0 regresiones.

---

### Notas de Cambios v4.60.1 — FASE-1 (BUGFIX-LUXOR)

**Fecha:** 2026-07-06

**Módulos afectados:**
- `main.py` (~L1942)
- `modules/auditors/v4_comprehensive.py` (`_audit_competitors`)

**Problema:**
- BUG-2: `calc_result` referenciado fuera del bloque `if not use_harness_for_financials:` donde se define, causando `UnboundLocalError` cuando el harness SÍ se usa.
- BUG-1: `_audit_competitors` hardcodeaba `lat=0.0, lng=0.0` ignorando `gbp_result.lat/lng` reales de Places API.

**Solución:**
- BUG-2: Línea `calc_result.metadata` reemplazada por `financial_breakdown.evidence_tier` + `disclaimer` (disponibles en ambos caminos de ejecución).
- BUG-1: Usar `gbp_result.lat/lng` + validación de rango Colombia (lat 0-13, lng -82 a -66). Si coords son 0.0 o fuera de rango, retornar `[]` sin llamar la API.

**Backwards compatibility:** ✅ Sin breaking changes. `financial_breakdown` ya tenía `evidence_tier` y `disclaimer`. `gbp_result` ya tenía `lat`/`lng` desde Places API.

**Tests:** 4 tests de regresión nuevos (3 BUG-1 + 1 BUG-2), 0 regresiones.

---

### Notas de Cambios v4.60.1 — FASE-2 (BUGFIX-LUXOR)

**Fecha:** 2026-07-06

**Módulos afectados:**
- `modules/auditors/llm_mention_checker.py`
- `config/provider_registry.yaml`

**Problema:** `llm_mention_checker.py` hardcodeaba modelo `openai/gpt-4o` en los payloads a OpenRouter, causando error 404 cuando el modelo no existía en el catálogo de OpenRouter.

**Solución:** Externalizar modelo al `provider_registry.yaml`. `llm_mention_checker.py` ahora lee `default_model` del registry con fallback `openai/gpt-4.1`.

**Backwards compatibility:** ✅ Sin breaking changes. Si el registry no tiene `default_model`, usa fallback.

**Tests:** 4 tests de modelo dinámico (not hardcoded, from registry, payload usa registry, fallback). 0 regresiones.

---

### Notas de Cambios v4.60.1 — FASE-3 (BUGFIX-LUXOR)

**Fecha:** 2026-07-06

**Módulos afectados:**
- `main.py` (bloque FASE 3.6 eliminado; `hotel_data` reubicado al post-gen scrub)

**Problema:** FASE 3.6 del content scrubber corría antes de que los documentos existieran, produciendo warnings `[SKIP] Diagnostic/Proposal document not available for scrubbing`. Los scrubs reales ocurrían post-T4FIX y post-gen.

**Solución:** Eliminado el bloque FASE 3.6 (~106 líneas: ContentScrubber + DocumentQualityGate). Las variables `quality_gate_issues/blockers/warnings` no tenían consumidores downstream. `hotel_data` fue reubicado al bloque post-gen scrub (único consumidor real).

**Backwards compatibility:** ✅ Sin breaking changes — los scrubs funcionales post-T4FIX y post-gen se preservaron intactos.

**Tests:** 24/24 tests existentes del scrubber pasan, 0 regresiones.

---

### Notas de Cambios v4.60.1 — FASE-4 (BUGFIX-LUXOR)

**Fecha:** 2026-07-06

**Módulos afectados:**
- `modules/auditors/v4_comprehensive.py` (`_run_seo_elements_audit`, nuevos métodos `_is_spa()`, `_render_with_playwright()`)

**Problema:** Sitios SPA (JavaScript app shell) retornaban HTML vacío al fetcher HTTP. El SEO elements detector no encontraba OG tags (falso negativo). AEO score incorrecto: 25 pts del componente Open Graph se perdían.

**Solución:** Detectar SPAs con heurística (scripts pero < 3 meta tags y 0 OG tags) y renderizar con Playwright como fallback antes de parsear. Fallback graceful si Playwright falla (ImportError, timeout, o chromium no disponible) — retorna resultado sobre HTML estático sin crashear.

**Backwards compatibility:** ✅ Sin breaking changes — `detect()` en `seo_elements_detector.py` permanece sin cambios. Playwright se usa solo cuando se detecta SPA; sitios normales no se ven afectados. Si Playwright falla, fallback a BeautifulSoup (comportamiento original).

**Tests:** 7 tests nuevos SPA rendering (4 detección + 3 integración mock/fallback). 148/149 auditor tests pasan (0 regresiones).

**Dependencias:** Playwright v1.58.0 + chromium (ya instalados).

### Notas de Cambios v4.60.1 — FASE-5 (Verificación E2E)

**Fecha:** 2026-07-06

**Módulos afectados:**
- Ninguno (fase de verificación — ejecución v4complete sin cambios de código)

**Resultado:** v4complete ejecutado exitosamente para Luxorhotel con todos los fixes de FASE-1 a FASE-4.
- BUG-1: ✅ Coordenadas reales usadas (lat:4.81, lng:-75.70)
- BUG-2: ✅ Sin UnboundLocalError en FASE-K
- BUG-4a: ⚠️ OpenRouter 404 persiste en llm_mention_checker (modelo `qwen/qwen3.6-plus:free`). DeepSeek usado como fallback exitoso.
- BUG-4b: Gemini 403 — fuera del plan (acción del usuario)
- BUG-5: ✅ Scrubs funcionando (post-T4FIX + post-gen), sin [SKIP]
- BUG-6: ✅ Playwright SPA fallback presente en código. Luxorhotel no triggeró heurística (≥3 meta tags)
- Coherence score: 0.80 | Publication Gates: 11/11 | READY_FOR_PUBLICATION
- 0 regresiones

**Backwards compatibility:** N/A (sin cambios de código).

**Tests:** 0 tests nuevos. 0 regresiones detectadas en suite completa.

### Notas de Cambios v4.60.0 — CAPEX-BREAKDOWN-FIX

**Fecha:** 2026-05-29

**Módulos afectados:**
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `tests/test_capex_rename.py`

**Problema:** Tablas markdown anidadas en CAPEX breakdown (template) + código muerto en generator (9 orphan keys, coherence checklist nunca usado, fallback sin header row).

**Solución:**
- F1: Placeholder `${capex_breakdown_table}` movido a sección propia — fix tablas markdown anidadas
- F7: Eliminadas 9 keys huérfanas del template data dict
- F8: Fallback de `_build_capex_breakdown_table()` ahora incluye header row
- F6: Eliminado `_build_coherence_checklist()` + `'coherence_checklist'` — código muerto YAGNI
- FASE-4: Verificación E2E v4complete Hotel Castilla Real — 11/11 gates PASS, coherence 0.85

**Backwards compatibility:** Sí. Fix de rendering sin cambios en API pública ni breaking changes.

**Tests:** test_capex_rename.py (integridad de pipes en tabla CAPEX) — 8/8 passing, 0 regresiones.

---

### Notas de Cambios v4.59.0

**Fecha:** 2026-05-29

**Módulos afectados:**
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/quality_gates/publication_gates.py`
- `config/regional_benchmarks.yaml`

**Problema:** 5 gaps comerciales donde datos se producían pero no se renderizaban (CAPEX), no existían (Status Quo, Closing Pitch), o se mostraban como placeholders vacíos (ADR). Además, 2 gates evaluaban evidence tier inconsistente.

**Solución:**
- Template fix: añadir placeholder `${capex_breakdown_table}`
- Pipeline fix: método `_build_status_quo_table()`, `_build_closing_pitch()`
- Data fix: ADR en `regional_benchmarks.yaml` + cascada en coherence checklist
- Gate fix: `financial_validity` usa `evidence_tier` formal
- Debt: template embebido L575-605 eliminado

**Backwards compatibility:** Sí. Nuevos placeholders son opcionales — si no se producen, el template los ignora. Gates más precisos no cambian FAIL/PASS umbral.

---

### Notas de Cambios v4.53.0 — PROPUESTA-COMERCIAL

**Fecha:** 2026-05-26

**Descripción:** Cierre del proyecto PROPUESTA-COMERCIAL. 14 hallazgos corregidos en 5 fases de implementación.

**Módulos afectados:**
- `modules/commercial_documents/v4_proposal_generator.py` — CODE-1/3/4, CROSS-1/2/4/5, V-2/3/4/5/6, A-1/2/3
- `modules/commercial_documents/v4_diagnostic_generator.py` — CROSS-1
- `modules/commercial_documents/templates/propuesta_v6_template.md` — Variables financieras, tabla dinámica, labels
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — CROSS-1
- `modules/commercial_documents/commercial_gate.py` — CODE-2, V-3, A-1
- `modules/commercial_documents/publication_gates.py` — CROSS-6

**Problema:** Variables financieras inconsistentes entre template y generator, gates desincronizados, mapping brecha→servicio incompleto, indicadores de estado ambiguos, typos en copy.

**Solución:**
- CODE-1/3/4: Unificación de todas las variables financieras sobre `effective_monthly_gain`
- CODE-2: Gate CG-ROI-NEGATIVE sincronizado con tabla ROI
- CROSS-1: Puente dual fuga bruta/recuperación efectiva en diagnóstico y propuesta
- CROSS-2: Mapping brecha→servicio con trazabilidad en tabla de propuesta
- CROSS-4: Indicador de WhatsApp refleja conflicto real detectado
- V-2: Labels de estado unificados: "⚠️ En preparación" → "En proceso de activación — Semana 2"
- V-3: Gate CG-TECH-JARGON expandido con 8 nuevos términos; tabla de costos IAO movida a anexo técnico
- A-1: Eliminado fallback frágil de búsqueda de string en `has_onboarding`
- CROSS-5: Confidence score visible en tabla de servicios de propuesta
- A-2: Umbral AEO unificado a 30 en ambas tablas
- V-4: Cupo limitado justificado con número
- V-5: Garantía incluye mecanismo de tracking propio Día 7
- V-6: Placeholder de prueba social agregado al template
- A-3: Typo "PASSO" → "PASO" corregido
- CROSS-6: Gates NOT_READY ahora bloquean generación de documentos cliente (GATE_BLOCKING_ENABLED)

**Cambio de comportamiento (CROSS-6):**
Gates con status NOT_READY ahora bloquean la generación de documentos para el cliente. Anteriormente, los gates advisory (WARNING) permitían generar documentos igualmente. Con CROSS-6, si cualquier gate crítico retorna NOT_READY, los documentos cliente (`diagnostico_*.md`, `propuesta_*.md`) NO se escriben a disco. Assets técnicos y delivery package aún se generan. Para deshabilitar: `export GATE_BLOCKING_ENABLED=false`.

**Backwards compatibility:** API pública sin cambios. CROSS-6 es configurably blocking via env var.

---

### Notas de Cambios v4.51.1 — COPYWRITING-REFACTOR

**Fecha:** 2026-05-25

**Descripción:** Templates V6 reestructurados con vista gerencia (dueño) en secciones 1-6 y anexo técnico en 7+. Scenario clamp en `_build_scenario_table_rows`. Tier consistency en `_build_financial_placeholders`.

**Módulos afectados:**
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Reordenado: dueño primero
- `modules/commercial_documents/templates/propuesta_v6_template.md` — OTA narrative, quick wins accionables
- `modules/commercial_documents/v4_diagnostic_generator.py` — Scenario clamp, tier consistency, breach sanitization
- `modules/commercial_documents/v4_proposal_generator.py` — Commercial gate integration
- `modules/quality_gates/commercial_gate.py` (NUEVO) — 8 gates (5 BLOCKING + 3 WARNING)

**Problema:** Los templates no estaban optimizados para conversión comercial en hoteles boutique colombianos. Pain principal (comisiones OTA, WhatsApp conflicts) no lideraba la narrativa.

**Solución:** COPY-A restructura templates V6 (vista dueño → Anexo Técnico). COPY-B integra commercial_gate.py con 8 gates comerciales. COPY-C valida E2E con Hotel Castilla Real (coherence ≥ 0.80).

**Backwards compatibility:** Cambios de copywriting, no cambia API pública.

---

### Notas de Cambios v4.50.0 — AssessmentBuilder

**Módulos afectados:**
- `modules/assessment_builder.py` (NUEVO)
- `modules/quality_gates/publication_gates.py`
- `main.py`

**Problema:** El diccionario `assessment` que alimenta los 11 publication gates se construía
manualmente en 3 etapas separadas (~87 líneas) sin tipado ni validación. Cada gate implementaba
4-6 fallbacks defensivos (~129 líneas de extractores) porque el dict no tenía schema. Campos
zombie (`quality_gate_*`, `coherence_checks`) se acumulaban sin consumidores.

**Solución:** `AssessmentBuilder` centraliza la construcción en una clase con dataclass tipado
(`AssessmentPayload`, 28 campos). API fluida: `.with_core().with_validation()...build()`.
Los extractores se simplifican a acceso directo (ahorro ~100 líneas). Campos zombie eliminados.

**Backwards compatibility:** El builder produce un `Dict[str, Any]` idéntico al contrato
existente de `run_publication_gates()`. No se rompe ninguna interfaz pública.

**Tests:** 34 tests nuevos. v4complete E2E verificado sin regresiones.

---

### Notas de Cambios v4.49.0 — AGENTSMD-DRIFT — 2026-05-26

**Módulos afectados:** AGENTS.md, scripts/validate_agents_md.py, docs/CONTRIBUTING.md

**Problema:** AGENTS.md tenía drift factual en 4 secciones post-FASE-0 y PIPELINE-FIX. El header se sincronizaba vía version-sync pero el body no tenía mecanismo de auditoría. ROADMAP.md sí estaba actualizado.

**Solución:**
1. Corrección editorial one-shot de AGENTS.md (9 pasos) — sincronización completa con código vivo
2. Script `validate_agents_md.py` con 6 checks automáticos (modules_exist, test_count, gate_count, fase0_modules, no_deprecated_active, scripts_exist)
3. Integración en flujo post-fase de CONTRIBUTING.md (Paso 5.5 obligatorio)

**Backwards compatibility:** Total. Cambios editoriales en documentación y nuevo script de validación. Sin cambios en API, pipeline, ni lógica de negocio.

**Tests:** Sin cambios en suite de tests (2,743 tests, 0 regresiones).

---

### Notas de Cambios v4.48.0 — PIPELINE-FIX — 2026-05-23

**Módulos afectados**: `main.py`, `modules/asset_generation/v4_asset_orchestrator.py`, `ROADMAP.md`

**Problema (dos bugs críticos)**:
1. Assessment dict bridge: `main.py:2652-2694` construye assessment manualmente sin cargar artefactos que YA existen en disco/memoria (`pain_ledger`, `diagnostic_pain_ids`, `proposal_pain_ids`, `financial_evidence_tier`, `tier_c_onboarding_required`). Esto causaba 2 gates BLOCKED falsos (`coverage`, `tier_c_onboarding_required`) y `proposal_asset_matrix.json` sin generar.
2. Métrica `delivery_ready_percentage` distorsionaba el indicador comercial: usaba `preflight_status WARNING` en vez de `confidence_score ≥ 0.65`, resultando en 50% en vez de ~83%.

**Solución**:
- **PF-1**: `main.py` ahora carga `pain_ledger_entries` del scope externo, lee `pain_ledger.json` del directorio del hotel, e inyecta los 4 campos (`pain_ledger_entries`, `diagnostic_pain_ids`, `proposal_pain_ids`, `financial_evidence_tier`) al assessment dict. Pasa `pain_ledger` a `v4_proposal_generator.generate()` para habilitar `ProposalAssetMatrix.save()`.
- **PF-2**: Fórmula `delivery_ready_pct` cambia de `preflight_status == "WARNING"` → `confidence_score >= 0.65` (umbral inclusivo). Resultado: 10/12 assets = 83.33%.
- **PF-3**: E2E Hotel Castilla Real — coherence 0.8261 ≥ 0.80, coverage PASS (0 untracked), tier_c_onboarding PASS (tier B real), evidence_coverage 95%.
- **PF-4**: Documentación — `tier_c_onboarding_required` gate documentado en ROADMAP, tabla mapping 4 gates conceptuales → 11 gates reales.

**Gates resueltos (bug del pipeline)**: 4/4 (coverage, tier_c_onboarding, delivery_ready, evidence_coverage)

**Gates data-dependent (no bug, requieren datos reales)**: 5 (proposal_asset_matrix, G8 asset_confidence, G8 asset_specificity, financial_validity, asset_specificity)

**Backwards compatibility**: Total. Bugfix de pipeline — no cambia API pública ni comportamiento de generación de assets.

---

### Notas de Cambios v4.47.0 — ADVISORY-WARNINGS

**Módulos afectados**: `v4_diagnostic_generator.py`, `delivery_quality_report.py`

**Problema**: IA-Readiness Critical (score < 50) aparecía como una fila más en la tabla de diagnóstico sin explicitar el riesgo comercial al hotelero. No quedaba registro persistente en los reportes de calidad.

**Solución**:
- Alerta blockquote en diagnóstico cuando IA-Readiness es Critical
- Nuevo campo `advisory_warnings` en DeliveryQualityReport con entry `IA_READINESS_CRITICAL`
- `blocking=False` — no aborta ZIP ni afecta overall_confidence

**Backwards compatibility**: Total. Campo nuevo (`advisory_warnings`) con default `[]`. Template soporta nueva variable pero mantiene comportamiento existente.

---

### v4.46.1 — FIX-ENCODING-SISTEMICO: Prevención de Memory Leak por Encoding — 2026-05-14

**Módulos afectados**: `scripts/verify_ga4.py`, `scripts/validate_structure.py`, `scripts/update_benchmarks.py`, `scripts/validate_document_integration.py`, `docs/CONTRIBUTING.md`, `docs/contributing/documentation_rules.md`

**Problema**:
- `python.exe` (Windows) consumió 42.5 GB de memoria virtual y congeló el sistema (2026-05-13 22:16)
- Causa raíz: scripts con `print()` de caracteres Unicode (tildes, flechas, emojis) en stdout configurado en `cp1252` → `UnicodeEncodeError` → pipe rota → memory leak
- Mecanismo de 3 capas: (1) Python imprime carácter fuera de cp1252, (2) excepción rompe pipe Hermes↔Python, (3) Hermes re-ejecuta sin limpiar proceso zombie → buffers huérfanos se acumulan
- 5 re-ejecuciones en 3 minutos sin limpieza de procesos fallidos

**Solución (3 fases + documentación)**:
1. **FASE-A (Parche inmediato)**: `TextIOWrapper` con UTF-8 en stdout/stderr de `validate_document_integration.py` (script que disparó el incidente)
2. **FASE-B (Parche sistémico)**: `reconfigure()` UTF-8 en 3 scripts que carecían de fix (`verify_ga4.py`, `validate_structure.py`, `update_benchmarks.py`). Verificación de 4 scripts que ya tenían protección.
3. **FASE-C (Configuración Hermes)**: `tool_loop_guardrails.hard_stop_enabled: true` + `hard_stop_after.exact_failure: 3` — detiene re-ejecución automática tras 3 fallos del mismo comando
4. **FASE-D (Documentación)**: Sección "Encoding en scripts Python" en CONTRIBUTING.md con patrón estándar `reconfigure()`. Regla de gate en documentation_rules.md.

**Patrón estándar** (3 líneas al inicio del script, antes de cualquier `print()`):
```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
```

**Backwards compatibility**: 100%. El fix no cambia comportamiento, solo previene crash en Windows. En Linux/macOS, `sys.stdout.encoding` ya es UTF-8 por defecto y `reconfigure()` es no-op.

**Tests**: `run_all_validations.py --quick` 5/5 PASS sin regresiones. 3 scripts parcheados ejecutan sin `UnicodeEncodeError` en WSL.

---

### v4.46.0 — FASE-0 RELEASE: Delivery Quality — Primer Piso de Entrega Confiable — 2026-05-13

**Módulos afectados**: `asset_generation/pain_ledger.py` (NUEVO), `asset_generation/data_derivation_layer.py` (NUEVO), `quality_gates/delivery_quality_report.py` (NUEVO), `quality_gates/human_checklist_generator.py` (NUEVO), `asset_generation/v4_asset_orchestrator.py`, `asset_generation/conditional_generator.py`, `asset_generation/preflight_checks.py`, `asset_generation/proposal_asset_alignment.py`, `quality_gates/publication_gates.py`, `main.py`

**Problema**:
- El pipeline v4 generaba assets sin trazabilidad sistemática de brechas → entrega
- No existía un gate de cobertura que garantizara que toda brecha detectada estaba representada en diagnóstico y propuesta
- Los assets se generaban con confidence=0.5 cuando campos requeridos no existían en validated_data, sin distinguir entre campos esenciales y opcionales
- No había QA bloqueante pre-ZIP: el empaquetado procedía incluso con assets de baja confianza

**Solución (8 fases: 0A-0H)**:
1. **FASE-0A (Baseline)**: Auditoría completa del pipeline existente. Matriz brecha→diagnóstico→oportunidad→propuesta→asset→estado→evidencia con 14 filas. GAPs H1-H6 verificados contra código.
2. **FASE-0B (PainLedger)**: Facade sobre PainSolutionMapper que produce `pain_ledger.json` con pain_id, source_module, severity, confidence, status, human_label, evidence_refs
3. **FASE-0C (CoverageGate)**: Nuevo gate en `publication_gates.py` que verifica `brechas_en_diagnostico + brechas_justificadas == brechas_detectadas`. Integrado en `run_publication_gates()`.
4. **FASE-0D (ProposalAssetMatrix)**: Matriz dinámica servicio→brecha→asset con `ProposalAssetMatrix` dataclass. Output: `proposal_asset_matrix.json`.
5. **FASE-0E (DeliveryQualityReport)**: QA bloqueante pre-ZIP. Reporte con status (PASS/FAIL/WARNING), coverage_gate, proposal_asset_gate, asset_specificity_gate, evidence_gate. ZIP abortado si status=FAIL.
6. **FASE-0F (HumanChecklist)**: `HumanChecklistGenerator` deriva checklist ≤10 items del delivery_quality_report.
7. **FASE-0G (E2E)**: Verificación controlada con hotel real (hotelcastillareal). G6=PASS(0.81), G7=PASS(0 UNTRACKED), G8=FAIL motivando 0H.
8. **FASE-0H (G8 Root-Cause Hardening)**: DataDerivationLayer deriva 5 campos del audit sin APIs nuevas. Contrato REQUIRED/RECOMMENDED con scoring semántico: RECOMMENDED+fallback=0.8 (vs REQUIRED=0.5).

**Backwards compatibility**: 100% — PainLedger y CoverageGate son additivos (no modifican comportamiento existente). `priority` default es `REQUIRED`. Derivación se activa solo si `audit_report_raw` se pasa (parámetro opcional). DeliveryQualityReport es no bloqueante por defecto (solo FAIL si se configura explícitamente).

**Tests**: 60+ tests nuevos (pain_ledger × TDD, 11 coverage_gate, 6 proposal_asset_matrix, 10 delivery_quality_report, 6 human_checklist, 26 derivation+scoring). 0 regresiones en módulos modificados. Hotel Castilla Real fixture: 9/12 assets ≥0.65 (vs 0/8 baseline pre-0H).

---

### v4.45.0 — FASE-0H-G8: Data Derivation + REQUIRED/RECOMMENDED Preflight Contract — 2026-05-13

**Módulos afectados**: `asset_generation/data_derivation_layer.py` (NUEVO), `asset_generation/v4_asset_orchestrator.py`, `asset_generation/asset_catalog.py`, `asset_generation/preflight_checks.py`, `asset_generation/conditional_generator.py`

**Problema**:
- G8 FAIL: 8/12 assets con confidence=0.5 porque `required_field` no existía en `validated_data`
- `_calculate_confidence_score()` penalizaba WARNING genérico (0.5) sin distinguir campos opcionales de esenciales
- Campos como `og_tags_detected`, `org_data` existían en el `audit_report` pero no se derivaban a `validated_data`

**Solución**:
1. **DataDerivationLayer** (`data_derivation_layer.py`): Deriva 5 campos del `audit_report` existente — `og_tags_detected` (desde `seo_elements`), `org_data` (desde `schema` + `gbp`), `ga4_available` (desde `ai_crawlers`), `organic_traffic` (desde `performance`/`llm_report` proxies), `metadata` (desde `audit.metadata`)
2. **Contrato REQUIRED/RECOMMENDED**: Nuevo campo `priority` en `AssetCatalogEntry` y `PreflightCheck`. 4 assets reclasificados a RECOMMENDED (`analytics_setup_guide`, `indirect_traffic_optimization`, `og_tags_guide`, `org_schema`)
3. **Scoring semántico**: `_calculate_confidence_score()` asigna 0.8 a WARNING con `RECOMMENDED+fallback` (vs 0.5 para REQUIRED)
4. **_evaluate_check() dict-tolerant**: Maneja tanto `DataPoint` objects como `dict` derivados; aplica heurística ESTIMATED (0.7) a dicts con datos reales sin metadatos explícitos

**Backwards compatibility**: 100% — `priority` default es `REQUIRED`; derivación se activa solo si `audit_report_raw` se pasa (parámetro opcional); scoring preexistente sin cambios para REQUIRED.

**Tests**: 26 tests nuevos (18 derivation + 8 scoring/fixture). Hotel Castilla Real fixture: 8/8 assets afectados ≥ 0.65 (vs 0/8 baseline). 0 regresiones en módulos modificados.

---

### v4.44.0 — FASE-1-COH: Unificar CoherenceValidator ↔ CoherenceGate — 2026-05-11

**Módulos afectados**: quality_gates/coherence_gate.py, main.py

**Problema**:
- `CoherenceGate` tenía `_validator` instanciado (L158) pero `execute()` jamás lo llamaba — solo comparaba un float contra threshold
- `v4_complete_report` mostraba 2 campos de coherence_score (pre + post) sin trazabilidad clara
- El validator producía un `CoherenceReport` completo con 6 checks, errores y warnings que el gate ignoraba

**Solución**:
- `CoherenceGate.execute()` acepta ahora datos completos (diagnostic, proposal, assets, validation_summary) y delega a `execute_from_validator()` que llama a `_validator.validate()` como fuente única de verdad
- `CoherenceGateResult` gana campos `checks`, `validator_errors`, `validator_warnings` con los datos del `CoherenceReport`
- `main.py`: assessment dict enriquecido con `coherence_checks/errors/warnings`; `v4_complete_report` unificado a un solo `coherence_score`
- Backward compatibility: `execute(0.85)` legacy sigue funcionando sin cambios

**Backwards compatibility**: 100% — `execute(float)` legacy intacto, `CoherenceGateResult.to_dict()` excluye nuevos campos cuando son None.

**Tests**: 7 tests nuevos de integración (TestCoherenceGateValidatorIntegration). 31/31 total, 0 regresiones.

---

### v4.44.0 - 2026-05-11 — TERMALES-COHERENCE-FIX (FASE-1 a FASE-5)

**Módulos afectados**: asset_generation, commercial_documents, quality_gates, main.py

**Problema**:
- FASE-1: Coherence post-generación no validaba assets generados contra catálogo prometido
- FASE-2: Propuesta incompleta: menos de 8 servicios, gate umbral inconsistente
- FASE-3: Monthly report fallaba con 'list' object has no attribute 'items', sin disclaimer de fallback
- FASE-4: Brechas financieras normalizaban mal, pain_ratio y recovery_factor confundidos
- FASE-5: Necesidad de verificación E2E completa del pipeline v4complete

**Solución**:
- FASE-1: Coherence post-generación: _validate_post_generation() en orchestrator consume post_coherence_score
- FASE-2: Propuesta completa con 8 servicios, assets técnicos visibles, umbral gate 0.8 robusto
- FASE-3: Monthly report fail-safe con try/except+retry, disclaimer de fallback, bug fix runtime
- FASE-4: Normalización de brechas al valor central, separación explícita pain_ratio vs recovery_factor
- FASE-5: Verificación E2E con v4complete para Termales Santa Rosa de Cabal

**Backwards compatibility**: 100% — cambios internos de coherencia y generación, API pública sin cambios.

**Tests**: 12 tests nuevos (3 por fase), 0 regresiones. run_all_validations.py --quick: 4/4 pass.

---

### v4.44.1 — FASE-6-HOTFIX: G1/G6/G7 hotfix — 2026-05-12

**Módulos afectados**: main.py, asset_generation/conditional_generator.py, asset_generation/asset_catalog.py, asset_generation/v4_asset_orchestrator.py

**Problema**:
- G1: `coherence_validation.json` contenía score pre-generación (0.81) mientras el Publication Gate usaba score post-geo (0.826) — divergencia de 0.016
- G7: `whatsapp_conflict_guide` con confidence=0.5 (ESTIMATED) por WARNING en preflight, pero el conflicto detectado es evidencia real, no deficiencia. Gate FASE-4 exige >= 0.7
- G6: `hotel_schema.json` parcialmente poblado sin onboarding real — NO es bug, es limitación de datos

**Solución**:
- G1: **Causa raíz**: `CoherenceReport.save()` siempre escribía a `coherence_validation.json` ignorando el nombre de archivo. Fix en 3 partes:
  1. `coherence_validator.py`: `save()` acepta full paths (detecta `.json` suffix)
  2. `v4_asset_orchestrator.py` L447: pasa path completo al `save()` post-gen → crea `coherence_validation_post_gen.json` distinto
  3. `main.py` post-T4FIX: copia `coherence_validation_post_gen.json` → `coherence_validation.json` para sincronizar el archivo oficial
- G7: En `conditional_generator.py`, cuando `asset_type=="whatsapp_conflict_guide"` y preflight tiene WARNING, asignar confidence=0.8 y no usar prefijo `ESTIMATED_` (el conflicto detectado ES el asset). En `asset_catalog.py`, subir `required_confidence` de 0.5 a 0.7
- G6: WON'T FIX — documentado en docstring de `_extract_validated_fields` y `evidence/FASE-6-HOTFIX/G6_WONT_FIX.md`. La solución real es onboarding del hotel

**Backwards compatibility**: 100% — G1 usa copy (no recalcula), G7 solo afecta a whatsapp_conflict_guide, G6 solo documentación

**Tests**: Validación de sintaxis Python: 4/4 archivos OK. run_all_validations.py --quick: 4/5 (1 falla por version sync pre-existente)

---

### v4.43.1 - 2026-05-09 — PATCH-E2E Termales Santa Rosa de Cabal (FASE-2-PATCH-C)

**Módulos afectados**: Ninguno (fase de verificacion E2E)

**Problema**:
- Necesidad de verificar que los 6 patches aplicados en FASE-2-PATCH-A y FASE-2-PATCH-B restauran las 7 metricas de exito para Termales Santa Rosa de Cabal

**Solución**:
- **FASE-2-PATCH-C**: Ejecucion v4complete + verificacion de 7 metricas
  - M1 (sin {{if}}): PASS — 0 templates con condicionales sin procesar
  - M3 (monthly_report dinamico): PASS — tabla genera desde asset_generation_report.json
  - M4 (sin [PENDING_*]): PASS — scrubber Rule 6 detecta todos los marcadores
  - M5 (WhatsApp detectado): PASS — whatsapp_button presente en sitio (href + clases CSS)
  - M6 (hotel_schema_detected): FAIL — sitio solo tiene Organization schema, no Hotel schema
  - M7 (sin placeholder telefonico): PASS — telefono real de GBP usado en propuesta

**Hallazgo residual**: Hotel schema no detectado en termales.com.co. El sitio solo implementa Organization schema (5 schemas total). Gate proposal_asset_alignment: 40% (3 servicios sin assets generados: SEO Local, Informe Mensual, Open Graph).

**Backwards compatibility**: 100% — sin cambios de codigo en esta fase.

**Tests**: Verificacion E2E via v4complete. No tests nuevos. run_all_validations.py --quick: 5/5 pass.

---

### v4.43.0 - 2026-05-08 — Termales Refactor (FASE-1-A, FASE-1-B, FASE-2-A, FASE-3)
**Proyecto:** IA Hoteles Agent CLI

---

### v4.43.0 - 2026-05-08 — Termales Refactor (FASE-1-A, FASE-1-B, FASE-2-A, FASE-3)

**Módulos afectados**: commercial_documents, postprocessors, asset_generation, quality_gates

**Problema**:
- FASE-1-A: Template engine string.Template no procesaba {{if}}...{{endif}}; coherence usaba catálogo estático (no generados)
- FASE-1-B: Content scrubber no detectaba [PENDING_*]; monthly_report era estático con rows hardcoded
- FASE-2-A: SitePresenceChecker fallaba silenciosamente (except Exception ocultaba errores); generadores usaban contenido genérico
- FASE-3: Gates no bloqueantes permitían publicar documentos defectuosos (alignment < 50% solo WARNING)

**Solución**:
- **FASE-1-A**: Pre-procesador regex para {{if}}...{{endif}} antes de safe_substitute. Coherence validator usa generated_assets como fuente de verdad con fallback al catálogo.
- **FASE-1-B**: Rule 6 en content_scrubber detecta [PENDING_*] y bloquea publicación (block_publication=True). Monthly report genera tabla dinámica desde asset_generation_report.json.
- **FASE-2-A**: SitePresenceChecker hardening (except loguea error + retorna status=unknown). IndirectTraffic lee audit_report.json. FAQ scraping ligero del sitio.
- **FASE-3**: Alignment < 50% → BLOCKED (antes WARNING). Nuevo gate tier_c_onboarding_required para propuestas Tier C.

**Backwards compatibility**: 100%. generated_assets=None cae a fallback catálogo. audit_report_path/site_url son opcionales. Rule 6 es breaking change para [PENDING*] que antes pasaba limpio.

**Tests**: 64 tests nuevos (11+5+24+24). run_all_validations.py --quick: 4/4 pass. 0 regresiones.

---

### v4.42.1 - 2026-05-07 — SOL-2-PATCH (PATCH-A/B/C/RELEASE)

**Módulos afectados**: coherence_validator, v4_asset_orchestrator, publication_gates

**Problema**: Falsos positivos en contexto 07 (mensaje duplicado de assets faltantes), dead code detectado en SitePresenceChecker, y trampas temporales en prompts históricos (notas POST-EJECUCION faltantes).

**Solución**:
- PATCH-A: Micro-fixes — deduplicar mensaje coherence_validator, docstring site_verification_applied, logging publication_gates
- PATCH-B: Parcheo de prompts históricos SOL2-A y SOL2-B con notas POST-EJECUCION
- PATCH-C: Investigación skipped_assets + v4complete baseline Termales Santa Rosa de Cabal

**Backwards compatibility**: 100% — sin cambios de API, solo micro-fixes y documentación.

**Tests**: 0 tests nuevos, 0 regresiones.

---

### v4.42.0 - 2026-05-07 — SOL-2 Asset Alignment Refactor (FASE-SOL2-A/B/C/D)

**Módulos afectados**: quality_gates, asset_generation, commercial_documents

**Problema**: Dos validadores (coherence_validator y proposal_asset_alignment_gate) reportaban resultados inconsistentes para el mismo hotel. Existían refs fantasma a módulos inexistentes (deployment_assistant en docs). El 7mo servicio (AEO/llms_txt) no estaba cubierto por el gate.

**Solución**:
- FASE-SOL2-A: Eliminar ghost refs en AGENTS.md e INDICE_DOCUMENTACION.md. Verificar SitePresenceChecker opera correctamente.
- FASE-SOL2-B: Agregar llms_txt a PROPOSAL_SERVICE_TO_ASSET (7 servicios). Unificar baseline de coherencia. Documentar promised_by=["always"] con causalidad completa.
- FASE-SOL2-C: Verificación E2E con v4complete para Termales Santa Rosa de Cabal (coherence 0.89, 6/9 PASSED).
- FASE-SOL2-D: Auditoría de campos fantasma (GAP-G: falso positivo — campos calculados dinámicamente en v4_asset_orchestrator.py). Coherence score documentado como fuente única de verdad.

**Backwards compatibility**: Sí — cambios internos de reporting, API pública sin cambios. Coherence score puede variar levemente por unificación de baseline.

---

### v4.41.1 - 2026-05-07 — Correccion Post-Validacion Termales (PATCH-A/B/C)

**Resumen general:** Correcciones post-validacion de ejecucion Termales: coherence score unificado post-assets, ajuste de price_matches_pain, filtrado de servicios por pain_ids, y adicion de disclaimers Tier C en propuesta.

**Módulos afectados:**
- `main.py` — Coherence score post-assets usado en YAML header
- `modules/commercial_documents/coherence_validator.py` — Ajuste de calculo/threshold price_matches_pain
- `modules/commercial_documents/proposal_generator.py` — Filtro de servicios por pain_ids + disclaimer Tier C
- `modules/asset_generation/proposal_asset_alignment.py` — Alineacion propuesta-assets
- `modules/quality_gates/proposal_asset_alignment_gate.py` — Documentacion mismatch estatico vs dinamico

**Problema:**
Validacion post-ejecucion Termales detecto: divergencia de coherence score (2.67 pts entre pre y post assets), price_matches_pain en 0.0, 3 assets faltantes en alineacion, y disclaimers Tier C ausentes en propuesta.

**Solucion:**
- SOL-1: Usar coherence score post-assets en YAML header del diagnostico
- SOL-2: Filtrar servicios de propuesta solo aquellos con pain_ids detectados
- SOL-3: Agregar disclaimer Tier C condicional en propuesta
- SOL-4: Ajustar calculo/threshold de price_matches_pain en coherence_validator
- SOL-5: Documentar en docstring la diferencia entre alineacion estatica y dinamica

**Backwards Compatibility:**
- SOL-1: Cambio visible en YAML header (score puede ser menor post-assets)
- SOL-2: Propuesta puede listar menos servicios (solo los asociados a pains detectados)

**Tests:**
- run_all_validations.py --quick: 4/4 pass
- 0 regresiones

---

### FASE-PROP-D - 2026-05-06 — Google Maps Asset: Eliminación de Promesa Falsa

**Resumen general:** `geo_playbook` marcado como DEPRECATED en asset_catalog y eliminado de todos los mapeos activos. El servicio "Google Maps Optimizado" ya había sido removido de `PROPOSAL_SERVICE_TO_ASSET` en v4.40.2; esta fase completa la limpieza de referencias residuales.

**Módulos afectados:**
- `modules/asset_generation/asset_catalog.py` — `geo_playbook` status cambiado de `IMPLEMENTED` a `DEPRECATED`, `promised_by=[]`
- `modules/commercial_documents/pain_solution_mapper.py` — `low_gbp_score` ya no mapea a `geo_playbook` (solo `review_plan`)
- `modules/asset_generation/conditional_generator.py` — Eliminado `geo_playbook` de `_standard_assets` y del handler `elif`
- `modules/asset_generation/asset_diagnostic_linker.py` — Eliminadas justificación, impact map y metadata de `geo_playbook`
- `modules/asset_generation/site_presence_checker.py` — Eliminada entrada `geo_playbook` del diccionario de assets

**Problema:**
El gate de proposal_asset_alignment reportaba `geo_playbook` como missing porque `PROPOSAL_SERVICE_TO_ASSET` mapeaba "Google Maps Optimizado" → `geo_playbook`, pero el asset nunca se generaba en el pipeline estándar. El delivery GEO (`GeoContentGenerator`) ya genera `geo_playbook.md` con contenido equivalente, haciendo el asset del catálogo redundante.

**Solución:**
1. Verificar que `PROPOSAL_SERVICE_TO_ASSET` ya no contiene "Google Maps Optimizado" ✓
2. Marcar `geo_playbook` como `DEPRECATED` en `ASSET_CATALOG` ✓
3. Eliminar `geo_playbook` de `PAIN_SOLUTION_MAP["low_gbp_score"]` ✓
4. Limpiar `conditional_generator.py`, `asset_diagnostic_linker.py`, `site_presence_checker.py` ✓
5. Tests: 10 nuevos (5 en asset_catalog + 5 en proposal_generator) ✓

**Backwards compatibility:** ✅ Total. El delivery pipeline (`GeoContentGenerator`) sigue generando `geo_playbook.md` independientemente. Solo se elimina la generación duplicada del asset pipeline estándar.

**Tests:**
- `test_asset_catalog.py`: 21/21 PASS (incluyendo 5 nuevos de FASE-PROP-D)
- `test_proposal_generator.py`: 15/15 PASS (incluyendo 5 nuevos de FASE-PROP-D)
- `run_all_validations.py --quick`: 4/4 PASS

---

### v4.40.2 - 2026-05-05 — PATCH: Refactor CTA Onboarding (Fase REFACTOR-CTA-C)

**Resumen general:** Refactorizar el CTA de onboarding en diagnóstico Tier C para listar explícitamente los 4 datos requeridos (habitaciones, reservas mensuales, valor promedio de reserva COP, porcentaje canal directo).

**Módulos afectados:**
- `modules/commercial_documents/v4_diagnostic_generator.py` — String `show_onboarding_cta` refactorizado

**Problema:**
El CTA de onboarding en diagnóstico Tier C decía "complete el onboarding con sus datos reales" sin especificar cuáles datos. El usuario no sabía qué información necesitaba proporcionar.

**Solución:**
Se refactorizó el string `show_onboarding_cta` para listar explícitamente los 4 datos requeridos: número de habitaciones, reservas mensuales promedio, valor promedio de reserva (COP) y porcentaje de canal directo.

**Backwards Compatibility:** Sí. Solo cambio de string, sin modificación de APIs ni estructuras de datos.

---

### v4.40.1 - 2026-05-05 — Scoring Transparency (Fases SCORING-A, SCORING-B, SCORING-C)

**Resumen general:** Transparentar el sistema de scoring de los 4 pilares (SEO, GEO, AEO, IAO) en el diagnóstico generado por v4complete, mostrando todos los factores del checklist con marcadores visuales.

**Módulos afectados:**
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_scoring_breakdown()` modificado
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — 3 nuevos placeholders

**Problema:**
`_build_scoring_breakdown()` filtraba factores con valor `False`, ocultando información al cliente sobre qué indicadores faltaban. Además, solo GEO tenía breakdown en el diagnóstico; SEO, AEO e IAO tenían checklists, calculadores y extractores implementados pero sin representación en el output.

**Solución:**

#### SCORING-A: Fix de Filtrado en _build_scoring_breakdown()
- Módulos: `v4_diagnostic_generator.py`
- Problema: Solo mostraba factores TRUE, ocultando gaps al cliente
- Solución: Iteración completa con marcadores visuales (✅ para TRUE, ~~tachado~~ para FALSE)
- Backwards compatible: Sí (solo cambia presentación, no scores)

#### SCORING-B: Extensión a los 4 Pilares
- Módulos: `v4_diagnostic_generator.py`, `diagnostico_v6_template.md`
- Problema: Solo GEO tenía breakdown; SEO/AEO/IAO no tenían representación
- Solución: 3 nuevas asignaciones (`seo_score_breakdown`, `aeo_score_breakdown`, `iao_score_breakdown`) + 3 placeholders en template
- Backwards compatible: Sí (templates sin los placeholders funcionan igual)

**Tests:**
- Validación funcional vía v4complete con Hotel Castilla Real
- `run_all_validations.py --quick` pasa 4/4

---

### v4.40.0 - 2026-05-04 — Financial Evidence Engine (Fases FIN-1A, FIN-1B, FIN-2A, FIN-2B, FIN-3, CHAN-1, CHAN-2, FIN-4)

**Resumen general:** Eliminar falsa precisión financiera ($2.610.000 COP/mes desde defaults) implementando
Financial Evidence Engine + Regional Benchmark Fallback + Evidence-Based Channel Prioritization.

**Módulos afectados:**
- `modules/financial_engine/financial_evidence.py` (NUEVO) — Dataclasses epistémicas
- `modules/financial_engine/precision_validator.py` (NUEVO) — Validador de precisión financiera
- `modules/financial_engine/channel_evidence_resolver.py` (NUEVO) — Inferencia de canal por evidencia
- `data/benchmarks/regional_adr_2026.json` (NUEVO) — Benchmarks 2026 estructurados
- `modules/financial_engine/scenario_calculator.py` — FinancialEvidence en FinancialScenario
- `modules/financial_engine/no_defaults_validator.py` — SOURCE_EPISTEMIC_MAP + precision tier
- `modules/financial_engine/regional_adr_resolver.py` — Metadata epistémica en resultados
- `modules/financial_engine/feature_flags.py` — Caribe en validated_regions
- `modules/financial_engine/adr_resolution_wrapper.py` — epistemic_status + can_show_exact
- `modules/financial_engine/opportunity_scorer.py` — channel_context + multiplicadores
- `modules/commercial_documents/v4_diagnostic_generator.py` — Render rangos + channel_context

**Problema:** Sistema no distinguía fuentes de datos — usaba defaults hardcodeados ($2.610.000 COP/mes) sin indicar nivel de certeza. No había forma de saber si un valor venía de scraping real, benchmark regional, o un fallback silencioso.

**Solución:**

#### FIN-1A: Epistemic Metadata Model
- Módulos: `financial_evidence.py` (NUEVO), `scenario_calculator.py`
- Problema: Sistema no distinguía fuentes de datos
- Solución: `FinancialEvidence` dataclass con `EpistemicStatus`, `PrecisionTier`
- Backwards compatible: Sí (`FinancialScenario.financial_evidence` opcional)
- Tests: 8

#### FIN-1B: NoDefaultsValidator Ampliado
- Módulos: `precision_validator.py` (NUEVO), `no_defaults_validator.py`
- Solución: `SOURCE_EPISTEMIC_MAP` granular + `PrecisionValidator`
- Backwards compatible: Sí (`SUSPECT_SOURCES` se mantiene)
- Tests: 8

#### FIN-2A: Regional Benchmark 2026
- Módulos: `regional_adr_2026.json` (NUEVO), `regional_adr_resolver.py`
- Solución: Datos 2026 del Benchmarking.md a JSON operativo con metadata
- Tests: 8

#### FIN-2B: Feature Flags + Fallback Chain
- Módulos: `feature_flags.py`, `adr_resolution_wrapper.py`
- Solución: Caribe validado, `epistemic_status` en toda la cadena ADR
- Tests: 8

#### FIN-3: Rendering Condicional
- Módulos: `v4_diagnostic_generator.py`, templates
- Solución: Rangos + advertencias + CTA según precision tier
- Tests: 6

#### CHAN-1: Channel Evidence Resolver
- Módulos: `channel_evidence_resolver.py` (NUEVO)
- Solución: Inferencia de canal sin hardcodear WhatsApp
- Tests: 8

#### CHAN-2: OpportunityScorer + Channel Weights
- Módulos: `opportunity_scorer.py`, `v4_diagnostic_generator.py`
- Solución: `channel_context` opcional con multiplicadores trazables
- Tests: 8

#### FIN-4: E2E Combinado
- Hotel: Castilla Real (hotelcastillareal.com)
- Resultado: Coherence >= 0.8, 1 sola ejecución v4complete

**Backwards compatibility:** ✅ Compatible. `FinancialEvidence` opcional, `precision_tier` y `can_show_exact` con defaults seguros.

**Tests:** 54 tests nuevos, 0 regresiones.

### v4.39.0 - 2026-05-02 — Scoring Transparency (Fases SCORING-1, SCORING-2, SCORING-3)

**Resumen general:** Agregar transparencia al scoring GEO/AEO/SEO/IAO: breakdown visible por pilar, sección "Este score NO mide" por pilar, y documento `scoring_methodology.md` linkado desde frontmatter.

**Módulos afectados:** `modules/commercial_documents/v4_diagnostic_generator.py`, `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Problema:** El scoring GEO/AEO/SEO/IAO no era transparente sobre qué factores mide y cuáles excluye. Un hotel con 203 reviews y respuesta <24h podía bajar su score por fotos faltantes — el owner no entendía por qué.

**Solución:**
- Agregada función `_build_scoring_breakdown()` que muestra breakdown por pilar: "GEO 62/100 = Fotos(15%) + NAP(15%) + ..."
- Agregada función `_build_excluded_factors_section()` que lista factores NO medidos por pilar
- Template actualizado para mostrar breakdown debajo de tabla de scores y sección "Este score NO mide"
- Nuevo documento `docs/scoring_methodology.md` con metodología completa linkado desde frontmatter

**Backwards compatibility:** ✅ Compatible hacia atrás. No cambia la lógica de cálculo de scores. Solo agrega transparencia al output.

**Tests:** Tests existentes en `tests/commercial_documents/` sin regresiones.

### v4.38.0 - 2026-05-01 — FEATURE-CONFIG-EXTRACTION (Fases CONFIG-1 a CONFIG-8)

**Resumen general:** Migración de 31 hardcodes a 6 archivos YAML con schema validado. Corrección de 7 causas raíz del TECHNICAL_DEBT_2026-04-29. Backwards compatible: sin YAML usa defaults documentados.

**Módulos afectados:** `pricing_calculator.py`, `scenario_calculator.py`, `loss_projector.py`, `financial_factors.py`, `v4_proposal_generator.py`, `v4_diagnostic_generator.py`, `sync_versions.py`, `sync_config.yaml`, `propuesta_v6_template.md`

**Problema:** 31 valores hardcodeados en 8 archivos Python + bug sync_versions (doble escape YAML L101-103) causaban datos falsos (fallbacks silenciosos), versiones stale (GUIA_TECNICA nunca se actualizaba), y parámetros financieros inconfigurables sin tocar código.

**Solución:** Extracción a 6 archivos YAML (`pricing.yaml`, `scenarios.yaml`, `financial_defaults.yaml`, `fallbacks.yaml`, `commercial.yaml`, `regional_benchmarks.yaml`) + loader genérico `yaml_loader.py` con caching y fallback. Cada módulo lee de YAML si existe, si no usa defaults documentados.

**Backwards compatibility:** Sin YAML, el sistema funciona idénticamente con defaults hardcodeados documentados. Con YAML, todos los valores son configurables sin tocar código.

**Tests:** 60 tests en `tests/config/` (migración, fallback, schema, integración).

### v4.38.0 - 2026-04-30 — FASE-CONFIG-6: Config Reconnect + Deprecación Módulos Huérfanos

**Resumen:** Reconectar `settings.yaml` con punteros a archivos de configuración activos y deprecar 4 módulos huérfanos que no tenían callers en el pipeline v4complete. También se corrigió un bug en `AnalyticsStatus.is_complete()` / `is_any_missing()`.

**CR-H-01: settings.yaml desconectado:**
- **Problema:** `settings.yaml` contenía `apis:` con `google_analytics:`, `google_search_console:`, `profound:`, `semrush:` pero NINGUN módulo del pipeline leía de él.
- **Solución:** Agregado header deprecación en `settings.yaml` apuntando a archivos activos: `config/pricing.yaml`, `config/scenarios.yaml`, `config/regional_benchmarks.yaml`, `config/pain_narratives.yaml`.
- **Módulos afectados:** `config/settings.yaml`

**Módulos huérfanos deprecados (CR-H-02 a CR-H-05):**
- `modules/analytics/profound_client.py` — Stub sin callers en pipeline
- `modules/analytics/semrush_client.py` — Stub sin callers en pipeline
- `modules/analytics/data_aggregator.py` — Sin uso; funciones cubiertas por `GoogleAnalyticsClient` y `GoogleSearchConsoleClient`
- `modules/delivery/generators/aeo_metrics_gen.py` — Sin callers en pipeline; generación AEO vía `PainSolutionMapper` y `OpportunityScorer`

**Todos emiten `DeprecationWarning`** en import con mensaje pointing a v5.0.0 removal.

**CR-H-06: Bug en `AnalyticsStatus.is_complete()` / `is_any_missing()`:**
- **Problema:** `is_complete()` requería `ga4 AND profound AND semrush AND gsc` — siempre retornaba `False` porque profound/semrush siempre `False` (stubs). `is_any_missing()` tenía el mismo problema.
- **Solución:** Ambos métodos ahora solo verifican fuentes ACTIVAS: `GA4` y `GSC`. Los campos `profound_*` y `semrush_*` se mantienen por backwards compatibility pero se ignoran en la lógica.
- **Módulos afectados:** `data_models/analytics_status.py`, `modules/commercial_documents/v4_diagnostic_generator.py`

### FASE-CONFIG-8: Suite de Tests de Regresión + Blindaje Config

**Resumen:** Blindaje post-migración YAML con 60 tests de regresión que verifican que los valores se leen de config files, no de hardcodes. Además se corrigieron bugs en `doctor.py` (encoding UTF-8) y `settings.yaml` (YAML inválido).

**Bug fix — doctor.py encoding (2 sitios, líneas 118 y 241):**
- **Problema:** `open(yaml_file)` sin `encoding='utf-8'` causaba fallo en Windows al leer YAML con caracteres Unicode (ñ, á, é, etc.). Afectaba tanto `run_status()` como la función de validación general.
- **Solución:** Agregado `encoding='utf-8'` en ambos `open()`.
- **Módulos afectados:** `scripts/doctor.py`

**Bug fix — settings.yaml YAML inválido:**
- **Problema:** `elite:` en línea 179 estaba sin indentación (indent 0) cuando debía estar a indent 2 (hermano de `starter_geo:`, `piloto_30d:`, `pro_aeo:`, `elite_plus:`). Esto hacía que `yaml.safe_load()` fallara con `ParserError`.
- **Solución:** Agregados 2 espacios de indentación para alinear con siblings.
- **Módulos afectados:** `config/settings.yaml`

**Tests de regresión creados (8 archivos, 60 tests):**
- `tests/config/test_config_pricing.py` — Valores pricing leídos de YAML, no hardcodeados
- `tests/config/test_config_scenarios.py` — Factores de escenario (recovery, ota_shift) desde YAML
- `tests/config/test_config_fallbacks.py` — Valores de fallback desde YAML
- `tests/config/test_config_commercial.py` — ROI cap, garantías desde YAML
- `tests/config/test_config_benchmarks.py` — Benchmarks regionales y pain_narratives desde YAML
- `tests/config/test_config_fallback.py` — YAML ausente → defaults documentados (no crash)
- `tests/config/test_config_schema.py` — YAML inválido/fuera de rango → error descriptivo
- `tests/config/test_config_integration.py` — Cambio YAML reflejado en módulo

**doctor.py --status:**
- Nueva sección "Config Files" en SYSTEM_STATUS.md
- Lista 9 YAML en `config/`, valida `version` + `description` en cada uno
- Resultado: 9/9 healthy

**Limpieza de exports:**
- `modules/analytics/__init__.py` ahora solo exporta: `GoogleAnalyticsClient`, `GoogleSearchConsoleClient`, `GSCQueryData`, `GSCPageData`, `GSCReport`

**Backwards Compatibility:** ✅ Total. Módulos deprecados siguen importables; campos deprecated de `AnalyticsStatus` se mantienen.

**Tests:** 15 tests nuevos en `tests/test_config_extraction_6.py`

---

### v4.36.1 - 2026-04-28 — Corrección Estado Entregables Propuesta

**Resumen:** Correccion del bloque "Estado de los Entregables" en la propuesta comercial. El bloque mostraba estados incorrectos: WhatsApp como pendiente cuando ya existia en produccion, Schema y FAQ como "Completo" sin verificacion real.

**Problema:** La propuesta comercial usaba `confidence` del generador de assets para determinar el estado de entrega, sin verificar presencia real en el sitio del hotel. `site_presence_report` no se propagaba por la cadena de llamadas hasta `_confidence_to_nivel_significado()`.

**Solucion:** Se cerró la cadena de llamadas para `site_presence_report`. Ahora `main.py` invoca `SitePresenceChecker` antes de generar la propuesta, y el resultado se propaga por toda la cadena: `generate()` → `_prepare_template_data()` → `_generate_asset_quality_table()` → `_confidence_to_nivel_significado()`. Este último ahora usa `presence real` del asset para determinar el estado, no solo el confidence del generador.

**Modulos afectados:** `modules/commercial_documents/v4_proposal_generator.py`, `main.py`, `tests/asset_generation/test_proposal_alignment.py`

**Backwards Compatibility:** ✅ Totalmente compatible. Si `site_presence_report=None`, el comportamiento es idéntico al anterior. El parámetro es `Optional` en toda la cadena.

**Tests:** 2 tests nuevos en test_proposal_alignment.py + fix tilde "Boton" → "Botón"

---

### v4.36.0 - 2026-04-26 — PATCH Forense AmaziliaHotel

**Resumen:** Correccion de 4 issues criticos identificados en auditoria forense. El release unifica el asset hotel_schema, corrige etiquetado de Comision OTA, repara el template open_graph con cableado pain_id, y agrega verificacion de presencia real en gate_report.

**FASE-A — hotel_schema dual unificado:**
- **Problema:** El sistema generaba dos schemas para hotel_schema: uno basico vacio y uno rico (geo_enriched). Cuando existia el schema rico, el sistema no lo usaba consistentemente.
- **Solucion:** `_generate_hotel_schema()` ahora hace pre-check de `geo_enriched/hotel_schema_rich.json`. Si existe y es JSON-LD valido, lo retorna directamente. El bridge en v4_asset_orchestrator aplica SIEMPRE para hotel_schema si el schema rico existe.
- **Módulos afectados:** `modules/asset_generation/conditional_generator.py`, `modules/asset_generation/v4_asset_orchestrator.py`

**FASE-B — Comision OTA label corregido:**
- **Problema:** El diagnostico comercial mostraba incorrectamente el label "Comision OTA" en la seccion de hallazgos financieros.
- **Solucion:** Corregido el etiquetado en `v4_diagnostic_generator.py` para mostrar correctamente el porcentaje de comision.
- **Módulos afectados:** `modules/commercial_documents/v4_diagnostic_generator.py`

**FASE-C — open_graph template + pain_id cableado:**
- **Problema:** El template open_graph no estaba completo y el cableado de pain_id hacia el asset `no_og_tags` no generaba el asset correctamente.
- **Solucion:** Template reparado con todos los meta tags necesarios. Cableado `no_og_tags` pain_id hacia `open_graph` asset integrado en pain_solution_mapper y conditional_generator.
- **Módulos afectados:** `modules/asset_generation/templates/open_graph_template.html`, `modules/pain_solution_mapper.py`, `modules/asset_generation/conditional_generator.py`
- **Archivos nuevos:** `modules/asset_generation/templates/open_graph_template.html`

**FASE-D — gate_report presence check:**
- **Problema:** gate_report no verificaba la presencia real del asset en el sitio del hotel.
- **Solucion:** Agregada verificacion de presencia en sitio real antes de marcar asset como entregado. Gate integrado en publication_gates.
- **Módulos afectados:** `modules/asset_generation/proposal_asset_alignment.py`, `modules/quality_gates/publication_gates.py`
- **Archivos nuevos:** `tests/quality_gates/test_gate_presence.py`

**Backwards Compatibility:** ✅ Verificada. Todas las fases son retrocompatibles. El sistema mantiene funcionalidad existente sin cambios de comportamiento para usuarios previos.

**Tests:**
- `TestHotelSchemaRichPreference`: 5/5 PASS
- `test_conditional_generator.py`: 32/32 PASS
- `test_geo_enriched_bridge.py`: 17/17 PASS
- `test_gate_presence.py`: 12/12 PASS (nuevos)
- Suite completa obligatoria: 61/61 PASS

### v4.35.0 - 2026-04-23 — INTERVENCIÓN AMABILIA: FASE-A (parcial)

**Resumen:** Corrección de test drift y alineación de catálogos de servicios. Primera fase de intervención Amazilia Hotel.

**FASE-A — Alineación Test Drift + Catálogos (2026-04-23):**
- `test_proposal_confidence_disclosure.py` — Fix drift: 6 → 7 servicios, eliminado "Visibilidad en ChatGPT" (ya no existe), agregado "Página de FAQ" y "Meta Tags Sociales (Open Graph)"
- `service_catalog.py` — Reemplazado "Barra de Reserva Móvil" por "Informe Mensual" (alineado con PROPOSAL_SERVICE_TO_ASSET)
- `proposal_asset_alignment.py` — Corregido tilde "Boton" → "Botón", "Pagina" → "Página"
- `pain_solution_mapper.py` — Agregado `no_monthly_report` a PAIN_SOLUTION_MAP y `monthly_report` a ASSET_NAMES
- `test_proposal_dynamic.py` — Actualizado test que usaba pain_id `no_motor_reservas` (ya fuera del catálogo)

**Criterio de éxito:** 19/19 PASS en commercial_documents, 4/4 validations.

### v4.34.0 - 2026-04-23 — FAQ y Open Graph en Propuesta Comercial

**Resumen:** Corregir desalineamiento entre diagnóstico de brechas y propuesta comercial. FAQ y Open Graph ahora aparecen como servicios en la propuesta.

**Módulos afectados:**
1. `proposal_asset_alignment.py` — PROPOSAL_SERVICE_TO_ASSET: 5 → 7 entradas
2. `pain_solution_mapper.py` — ASSET_NAMES completados con `open_graph` y `og_tags_guide`
3. `propuesta_v6_template.md` — Tabla principal hardcodeada: 5 → 7 filas

**Problema:**
- La propuesta comercial listaba 5 servicios fijos en tabla principal hardcodeada
- El diagnóstico detectaba 7 brechas reales (incluyendo FAQ y Open Graph)
- Cliente pagaba por resolver problemas que la propuesta no mencionaba

**Solución:**
- Agregadas 2 entradas a PROPOSAL_SERVICE_TO_ASSET: "Página de FAQ" → "faq_page", "Meta Tags Sociales (Open Graph)" → "open_graph"
- ASSET_NAMES completado: `open_graph` → "Meta Tags Sociales (Open Graph)", `og_tags_guide` → "Guía de Open Graph"
- Tabla principal del template actualizada de 5 a 7 filas

**Backwards Compatibility:** ✅ Compatible. Solo agrega servicios, no modifica lógica existente.

### v4.33.0 - 2026-04-21 — AMH REFACTOR V3-ALT Release

**Resumen:** Fix hotel_schema vacio — datos GBP no llegaban a validated_data. Fallbacks completos chain: schema → cross_validation → gbp → hardcode.

**Módulos afectados:**
1. `v4_asset_orchestrator.py` — `_extract_validated_fields()` con fallbacks completos para telephone, geo, address, rating, review_count
2. `geo_enriched_bridge.py` — GEO-BRIDGE quality gate rechaza reemplazos de calidad inferior
3. `conditional_generator.py` — MINIMUM-DATA-GUARANTEE + Data Rescue flag (penaliza a 0.3 si fallbacks fallan)

**Problema:**
- hotel_schema generaba `@type: LodgingBusiness` pero con campos vacios
- Causa raiz: `_extract_validated_fields()` no extraia datos del audit_result correctamente
- Fallbacks no estaban encadenados

**Solucion:**
- Telefono: `audit_result.schema.properties → audit_result.validation.phone_web → audit_result.gbp.phone`
- Geo: `audit_result.gbp.lat/lng` (validado rango Colombia)
- Address: `audit_result.gbp.formatted_address`
- Rating: `audit_result.schema.properties.rating → audit_result.gbp.rating`
- Review count: `audit_result.gbp.reviews`
- Country: hardcode "CO" como garantia minima

**Backwards Compatibility:** Compatible — fallbacks solo activan cuando datos no existen

**Tests:** 285 tests pass, E2E Certification (hotel_schema con datos reales)

---

### AMAZILIAHOTEL-REFACTOR-V2 - 2026-04-20 (FASE-5 a FASE-8 Completas)

**Resumen:** Corrección de GAPs E2E identificados en veredicto forense — score de 63.8 a >=80. 7 fases ejecutadas.

**Módulos afectados:**
- `modules/asset_generation/conditional_generator.py` — `_generate_faq_page()` ahora genera JSON-LD FAQPage (era CSV)
- `modules/asset_generation/monthly_report_generator.py` — 37 blanks `_____` → "Por confirmar"
- `modules/commercial_documents/templates/propuesta_v6_template.md` — Voice/AEO eliminados, ROI dinámico
- `modules/commercial_documents/v4_proposal_generator.py` — region `.replace("_", " ").title()` (ya implementado)
- `modules/asset_generation/proposal_asset_alignment.py` — entrada Voice/Búsqueda por Voz eliminada

**Problema/Solución:**
- G4: faq_page generaba CSV → JSON-LD con `@type: FAQPage`
- G7: monthly_report tenía 27 blanks `_____` → "Por confirmar"
- G9/G10: Voice/AEO prometeros sin implementación real → eliminados de template y alignment
- G13: "eje_cafetero" lowercase → "Eje Cafetero" (sanitización ya estaba en generator)

**Backwards compatible:** Sí. Formato JSON-LD para faq_page es schema.org estándar.

**Tests:** 28/28 regression tests PASS (conditional_generator + pain_solution_mapper).

---

### PATCH-1 (AMAZILIAHOTEL) - 2026-04-20 — Places API FieldMask + Lat/Lng Extraction

**Módulos afectados:**
- `modules/auditors/v4_comprehensive.py` — X-Goog-FieldMask ahora incluye `places.location`
- `modules/asset_generation/conditional_generator.py` — `_is_valid_colombia_coords()` rechaza (0,0)

**Problema/Solución:**
- Places API FieldMask no incluía `places.location` → API devolvía coordenadas pero el código nunca las recibía
- PlaceData se creaba con `lat=0.0, lng=0.0` hardcodeados → ahora usa `api_lat`/`api_lng` del response
- `_is_valid_colombia_coords` aceptaba (0,0) como válido → ahora lo rechaza explícitamente

**Backwards compatible:** Sí. Comportamiento interno sin cambios para casos válidos.

---

### PATCH-3 (AMAZILIAHOTEL) - 2026-04-20 — Region Title Case en JSON Outputs

**Módulo afectado:**
- `main.py` — 3 puntos de serialización en JSON

**Problema/Solución:**
- G13: outputs (`audit_report.json`, `v4_complete_report.json`) mostraban `region = "eje_cafetero"` (lowercase)
- Fix de FASE-7 en `v4_proposal_generator.py` no alcanzaba los puntos de serialización de main.py
- `_detect_region_from_url` sigue retornando lowercase (requerido por `feature_flags.py:48` matching exacto)
- .title() aplicado SOLO en 3 puntos de output: dict de reporte (~2738), assessment (~2538), hotel_data (~2289)

**Backwards compatible:** Sí. Valor interno de region sin cambios; solo cambia presentación en JSON.

---

### AMAZILIAHOTEL-FASE-3 - 2026-04-19 (Corrección Bugs Generadores)

**Resumen:** 4 bugs sistémicos corregidos en generadores independientes de BookingScraper.

**Módulos afectados:**
- `modules/quality_gates/coherence_gate.py` — H10: Importa CoherenceValidator como fuente única de verdad para coherence score
- `modules/commercial_documents/v4_diagnostic_generator.py` — H10: Fallback `_calculate_coherence_score()` documentado; solo se ejecuta cuando el gate no pasa score pre-calculado
- `modules/geo_enrichment/geo_enrichment_layer.py` — H4: Generación legacy de llms.txt marcada DEPRECATED; fuente oficial es `llms_txt/`
- `modules/asset_generation/asset_catalog.py` — H3: `faq_page` output_name corregido a extensión `.json`

**Problema/Solución:**
- H3: faq_page generaba .csv con contenido JSON-LD → output_name corregido en catalog
- H4: 2 generators creaban llms.txt en 2 carpetas → geo_enrichment_layer marca como DEPRECATED
- H10: coherence_gate y diagnostic_generator tenían cálculos diferentes → gate usa CoherenceValidator
- H12: paths Windows (`C:\`) en output → eliminados

**Backwards compatible:** Sí. API pública de coherence_score sin cambios. geo_enriched/llms.txt se mantiene como deprecated por compatibilidad.

**Tests:** 39/39 pasan (coherence 31 + llmstxt 8).

---

### AMAZILIAHOTEL-FASE-4 - 2026-04-19 (Asset B4 Open Graph)

**Resumen:** Nuevo asset Open Graph Meta Tags creado para cerrar brecha B4 ($379K/mes expuesto).

**Módulos afectados:**
- `modules/asset_generation/open_graph_generator.py` — NUEVO: OpenGraphGenerator con datos GBP verificados
- `modules/asset_generation/asset_catalog.py` — Entry `open_graph` con status IMPLEMENTED
- `modules/asset_generation/conditional_generator.py` — Handler `open_graph` en `_generate_content()` L482

**Arquitectura:** OpenGraphGenerator genera HTML con meta tags OG, Twitter Card, y JSON-LD Hotel schema. Se integra al pipeline via ConditionalGenerator (handler automático desde ASSET_CATALOG). Datos fuente: GBP verificado (rating, reviews, address, phone).

**Backwards compatible:** Sí. Asset nuevo, no afecta generación existente.

**Tests:** 9/9 pasan (open_graph).

### AMAZILIAHOTEL-FASE-5 - 2026-04-20 (Decisiones Producto + Quality Gates)

**Resumen:** Implementar decisiones de producto corrigiendo bug sistémico `promised_by=["always"]` en asset_catalog.py. WhatsApp y Voice eliminados de pipeline.

**Decisiones implementadas:**
- D1: WhatsApp ELIMINAR — hotel ya tiene WhatsApp (573104019049 = GBP phone). Bug `promised_by=["always"]` causaba generación automática sin verificación.
- D2: Voice ELIMINAR pipeline — sin brecha real. Tag `promised_by=["always_aeo"]` generaba siempre sin verificación.
- D3: Informe Mensual MANTENER reclasificado — servicio incluido legítimo, no fix de brecha.

**Módulos afectados:**
- `modules/asset_generation/asset_catalog.py` — `promised_by` corregido para WhatsApp y Voice

**Lección aprendida:** Tags `promised_by=["always"]` y `promised_by=["always_aeo"]` generan assets sin verificar brecha real. Siempre verificar si el hotel YA tiene el asset antes de generarlo.

**Tests:** 4/4 pasan.

### AMAZILIAHOTEL-FASE-6 - 2026-04-20 (Corrección Documentos Comerciales)

**Resumen:** Corregir claims falsos y ROI inflado en documentos comerciales. Aplicar decisiones de FASE-5 al output del cliente.

**Correcciones aplicadas a `02_PROPUESTA_COMERCIAL`:**
- WhatsApp eliminado de tabla problemas y servicios (claim "No hay botón de WhatsApp" era FALSO)
- Voice eliminado de servicios (sin brecha real)
- Servicios reorganizados en "Servicios de Optimización" (GEO, IAO, SEO, Datos) + "Servicios Incluidos" (Informe Mensual)
- ROI: 20X → 3X Tier C / hasta 20X con GA4. Disclaimer Tier C visible.
- Timeline: "Botón de WhatsApp instalado" eliminado (ya existe)

**Documentos modificados:**
- `output/v4_complete/02_PROPUESTA_COMERCIAL_*.md` — 7 líneas eliminadas, sección servicios reescrita, ROI corregido
- `output/v4_complete/01_DIAGNOSTICO_*.md` — NO modificado (ya era correcto: 4 brechas B1-B4, sin WhatsApp)

**Tests:** 105/105 pasan (commercial_documents suite completa). 0 regresiones.

------

## Notas de Cambios

### v4.57.0 — Financial Coherence & Asset Semantics Rescue

**Fecha:** 2026-05-28

**Módulos Afectados**
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/service_catalog.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `config/commercial.yaml`

**Problema**
La v4.55.0 introdujo doble motor de cálculo en `_prepare_template_data()`:
1. `total_recovered` usaba `effective_monthly_gain * 6` (path del pain_ratio)
2. `_maturity_result.total_recuperacion_6m` usaba curva de maduración

Resultado: dos ROIs distintos (0.45X vs 2.10X) en el mismo documento → destrucción de confianza comercial.

**Solución**
Unificar TODA la proyección financiera al motor de curva de maduración (`pillar_maturity_curve.py`).
El `effective_monthly_gain` se mantiene para otros cálculos internos pero NO para el total renderizado.

**Backwards Compatibility**
- **Sin breaking changes**: La API pública no cambió
- `_prepare_template_data()` retorna el mismo dict con valores corregidos
- `asset_semantics_validator` es aditivo (solo filtra, no cambia firma)
- Template V6: `${pilot_section}` y `${trazabilidad_origen}` son nuevos placeholders (opcionales, retornan "" si no aplican)

---

### v4.35.0 - 2026-04-23 — Propuesta Dinámica desde Pain Detection

**Resumen:** La propuesta comercial ahora se genera dinámicamente desde los pains detectados, en vez de un diccionario estático de 7 servicios.

**Problema:** `PROPOSAL_SERVICE_TO_ASSET` tenía 7 entradas fijas. La tabla principal del template estaba hardcodeada. Esto causaba desalineamiento: servicios ofrecidos que el hotel no necesitaba, y pains detectados sin servicio correspondiente.

**Solución:**
- Creado `SERVICE_CATALOG` en `modules/commercial_documents/service_catalog.py`: catálogo de servicios vendibles con mapeo `pain_id → servicio`
- Refactorizado `_generate_asset_quality_table()` para iterar sobre `detected_pains` en vez de sobre `PROPOSAL_SERVICE_TO_ASSET`
- Tabla principal del template ahora dinámica (placeholder `${dynamic_services_table}`)

**Módulos afectados:**
- `modules/commercial_documents/service_catalog.py` (NUEVO)
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`

**Backwards Compatibility:** Compatible. `PROPOSAL_SERVICE_TO_ASSET` se mantiene para backwards compatibility de gates de publicación.

**Tests:**
- `test_proposal_dynamic.py`: 14/14 PASS
- `test_proposal_alignment.py`: 13/13 PASS
- `run_all_validations.py --quick`: 4/4 PASS

---

### SPARK-FIX - 2026-04-18 (Reparación comando spark)

**Resumen:** Comando `spark` reparado. Fallaba con `TypeError: 'NoneType' object is not callable` porque dependía de `modules.orchestrator.pipeline` (AnalysisPipeline/PipelineOptions) que nunca existió en el repositorio.

**Causa Raíz:** `modules/orchestrator/` nunca fue committeado. El import try/except en main.py:21 siempre caía a `ORCHESTRATOR_AVAILABLE = False`, `PipelineOptions = None`. El harness traga el error (success=True, datos vacíos en 0.07s) y el modo legacy falla con TypeError.

**Arquitectura nueva:** Bridge directo V4ComprehensiveAuditor → SparkGenerator.
- `_map_audit_to_spark_data()`: Mapea V4AuditResult → GeoStageResult + IAStageResult
- `_detect_financial_region()`: Detecta región para FinancialFactors
- Usa FinancialFactors.get_config(region) para cálculo de pérdida mensual
- Dos paths corregidos: _spark_handler (harness) y _run_spark_legacy (CLI directo)

**Módulos afectados:** `main.py` (+130 líneas). SparkGenerator, GapAnalyzer, FinancialFactors sin cambios.

**Backwards compatible:** Sí. SparkGenerator recibe los mismos tipos (GeoStageResult, IAStageResult). Output idéntico (4 archivos).

**Verificación:** `spark --url "https://hotelvisperas.com" --bypass-harness` → GBP 72/100, Pérdida $20.6M COP/mes. 9 tests pasados.

---

### v4.31.1 - 2026-04-18 (Reescritura ROADMAP.md — audit v2)

**Resumen:** ROADMAP.md reescrito completamente con base en ROADMAP_AUDIT_2026-04-18.md. Cambio de paradigma: de "tracción y escalamiento" a "supervivencia comercial — primer cliente pago en 6 semanas".

**Corrección técnica:** `v4lite` no existe como comando CLI. Lo que existe es `spark` (diagnóstico rápido <5 min, stages geo+ia). Todas las referencias operativas corregidas en ROADMAP.md.

**Cambios estructurales:**
- FASE 0.5 nueva: Validación de dolor + ICP + outreach con spark pre-ejecutado
- FASE 1 redefinida: Landing mínima + outreach personalizado + primer Express pago ($120k COP)
- FASE 1.5 nueva: Instagram como canal de captura activa (paralelo)
- FASE 2 redefinida: 3-5 Express + 1 implementación + 1 palanca asimétrica
- FASES 3-4: diferidas hasta tener datos reales de clientes
- FASES 5-7: movidas a ANEXO "Visión 12-24 meses" con disparadores endurecidos
- Diagnóstico gratuito eliminado como estrategia 1:1 (solo como contenido público)
- OKRs redefinidas: métricas de supervivencia, no de tracción

**Archivos modificados:**
- `ROADMAP.md` — Reescritura completa. Horizonte 90 días. Fuente: audit temporal 2026-04-18

**Backwards compatibility:** No aplica (cambio documental, no de código). Pipeline v4complete y spark funcionan igual.

---

### v4.31.1 - 2026-04-15 (Fixes Residuales A3 + D7)

#### Fix A3: hotel_data nunca se creaba con schema vacio

**Causa Raiz:** `hotel_data = {}` estaba dentro del bloque `if schema.properties:` en `_extract_validated_fields()`. Cuando `schema.properties = {}` (dict vacio, evaluado como falsy en Python), el bloque se saltaba completamente y `hotel_data` nunca se creaba. El Monthly Report recibia `None` para `name` y caia al fallback generico "Hotel".

**Solucion:**

1. `hotel_data = {}` ahora se crea SIEMPRE (antes del `if schema.properties:`)
2. Se usa `.update()` para enriquecer desde schema cuando este tiene datos
3. Fallback chain para `name`: `audit_result.hotel_name` (siempre disponible) → `gbp.name` → `metadata.title`

**Archivo:** `modules/asset_generation/v4_asset_orchestrator.py`

#### Fix D7: Propuesta mostraba ❌ para assets generados

**Causa Raiz:** La tabla de calidad en la propuesta usaba `asset_plan` (10 items - solo pain-mapped) en vez de `asset_result.generated_assets` (12 items - incluye `promised_by="always"`). Los 3 assets automaticos (voice_assistant_guide, whatsapp_button, monthly_report) no estaban en `asset_plan` y aparecian como "❌ No generado".

**Solucion:**

1. `assets_for_quality` ahora se construye desde `asset_result.generated_assets` cuando esta disponible
2. Fallback a `asset_plan` si `asset_result` no esta disponible o `generated_assets` esta vacio
3. La propuesta ahora muestra los 12 assets generados con su confidence_score real

**Archivo:** `main.py` (~L2190-2215)

#### Tests

- 109 tests de regresion pasan
- `py_compile` en ambos archivos: OK
- v4complete en amaziliahotel.com: 12 assets generados (incluye los 3 problematicos)

---

### v4.31.0 - 2026-04-14 (FASE-PERSONALIZATION + FASE-BUGFIXES)

#### FASE-PERSONALIZATION: Generators con Audit Data

**Objetivo:** Modificar generators para recibir y usar `validated_data["hotel_data"]` como contexto.

**Problema resuelto:** Generators producían assets genéricos (name="Hotel", url vacía, región genérica) porque no recibían datos del audit.

**Archivos Nuevos:**

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/geo_playbook_generator.py` | Reimplementado con hotel_data + gbp_data. Genera playbook geográfico personalizado. |

### FASE-3 - 2026-04-19 (Corrección Bugs Generadores)

**Resumen:** Corrección de 4 bugs independientes de generadores de assets. Mejora de consistencia y portabilidad.

**Cambios:**

1. **H3: faq_page extensión .csv → .json (JSON-LD)**
   - `modules/asset_generation/asset_catalog.py`: Cambio template/output_name de .csv a .json
   - `modules/delivery/generators/faq_gen.py`: Genera JSON-LD schema.org FAQPage en lugar de CSV
   - Formato: `{"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [...]}`

2. **H4: llms.txt duplicado consolidado**
   - `modules/geo_enrichment/geo_enrichment_layer.py`: geo_enriched/llms.txt marcado como DEPRECATED
   - Fuente oficial: llms_txt/ (generado por modules/asset_generation/llmstxt_generator.py)
   - Header HTML comment indica deprecation y apunta a fuente oficial

3. **H10: Coherence metric unificada**
   - `modules/quality_gates/coherence_gate.py`: Importa CoherenceValidator como fuente única
   - CoherenceGate ahora usa CoherenceValidator internamente
   - API pública mantiene compatibilidad (CoherenceGateResult)
   - Evita métricas duplicadas (0.89 vs FALSE)

4. **H12: Paths Windows (WSL) relativos**
   - `modules/asset_generation/v4_asset_orchestrator.py`: Método _to_relative_path()
   - AssetGenerationResult.to_dict() convierte paths absolutos a relativos
   - Evita paths C:\Users\Jhond\... en JSON de reportes

**Archivos modificados:**
- `modules/asset_generation/asset_catalog.py` (faq_page .csv → .json)
- `modules/delivery/generators/faq_gen.py` (CSV → JSON-LD)
- `modules/geo_enrichment/geo_enrichment_layer.py` (deprecated header)
- `modules/quality_gates/coherence_gate.py` (unificación coherence)
- `modules/asset_generation/v4_asset_orchestrator.py` (paths relativos)

**Backwards compatible:** Sí. Cambios internos, API pública sin cambios.

---
| `modules/asset_generation/optimization_guide_generator.py` | Reimplementado con hotel_data + metadata_data. Genera guía SEO personalizada. |

**Archivos Modificados:**

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/conditional_generator.py` | Propaga hotel_data a todos los generators que lo necesitaban. Wrappers legacy para backward compatibility. |
| `modules/asset_generation/monthly_report_generator.py` | Refactorizado — ahora extrae name, city, website, phone, email, address de hotel_data. |
| `modules/asset_generation/llmstxt_generator.py` | Ya usaba hotel_data correctamente (sin cambios). |

**Tests:** 223 passed (5 failures preexistentes en voice_assistant/voice_keywords — causa raíz diferente).

---

#### FASE-BUGFIXES: Corrección Bugs Específicos

**Objetivo:** Corregir 4 bugs específicos en assets individuales.

**D4 — WhatsApp Button:** `detected_via_html` no existía en iah-cli (0 matches). No requirió fix.

**D5 — Review Widget:**

| Antes | Después |
|-------|---------|
| ★★★★★ hardcoded con "Excelente servicio y ubicación" | Lógica condicional: si `rating==0` o `review_count==0` → "Aún no hay reseñas disponibles". Si hay datos → estrellas reales + rating numérico + conteo. |

**D6 — Organization Schema:**

| Antes | Después |
|-------|---------|
| `url: "https://example.com"` fallback para campos vacíos | Campos omitidos del JSON si no tienen datos reales. `url`, `logo`, `contactPoint` solo incluidos si tienen valor. |

**D7 — Propuesta "No generado":**

| Antes | Después |
|-------|---------|
| Marcaba ❌ basado en flags internos | Verifica `Path(asset.path).exists()` — ✅ si archivo existe físicamente. |

**Archivos Modificados:**

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/conditional_generator.py` | _generate_review_widget() con lógica condicional; _generate_org_schema() elimina placeholder. |
| `tests/asset_generation/test_content_gates.py` | test_org_schema_with_empty_data actualizado para reflejar comportamiento correcto (campos omitidos). |
| `main.py` | Línea 2375: `icon = "✅" if Path(asset.path).exists() else "❌"` |

**Tests:** 223 passed | Greps: 0 `detected_via_html`, 0 `Excelente servicio`, 0 `example.com`.

---

### v4.30.0 - 2026-04-13

**Fix crítico:** Places API (New) no encontraba hoteles con schema.org basura.

- `modules/auditors/v4_comprehensive.py` — Nuevo método `_build_search_queries()`: genera múltiples variaciones de query validando schema_props antes de usarlos.
- **Impacto:** geo_score pasa de 0/100 (falso) a score real.

---

### v4.29.0 - 2026-04-13

**Fix:** geo_enriched → Delivery Bridge.

- `modules/asset_generation/geo_enriched_bridge.py` — Bridge que conecta `geo_enriched/` con delivery package.
- `modules/delivery/asset_bridge.py` — Copia archivos de geo_enriched al delivery con metadata de confianza.

---

### v4.28.0 - 2026-04-12

**FASE-E: Voice Readiness Proxy Score.**
- `modules/auditors/voice_readiness_proxy.py` — Score basado en PROXY (inputs que alimentan asistentes de voz).
- 4 componentes: GBP 30%, Schema 25%, Snippets 25%, Factual 20%.

---

## Arquitectura de Generators

```
validated_data (dict)
├── hotel_data        → name, url, telephone, address, lat, lng, ...
├── phone_web         → teléfono scrapado
├── phone_gbp         → teléfono de GBP
├── gbp_rating        → rating real de Google
├── gbp_review_count  → reviews reales
├── metadata_data     → CMS, meta descriptions, ...
└── gbp_data          → datos completos de Google Business Profile

conditional_generator.py
├── _generate_hotel_schema()      → usa hotel_data.lat/lng
├── _generate_llms_txt()           → usa hotel_data.name/url/region
├── _generate_geo_playbook()       → usa hotel_data + gbp_data
├── _generate_review_widget()      → usa gbp_rating/gbp_review_count
├── _generate_org_schema()         → usa hotel_data (url/telefono)
├── _generate_optimization_guide() → usa hotel_data + metadata_data
└── _generate_monthly_report()    → usa hotel_data
```

---

## Módulos Principales

| Módulo | Función | Estado |
|--------|---------|--------|
| `data_validation/` | Validación cruzada web+GBP+input | ✅ Activo |
| `modules/financial_engine/` | Escenarios conservador/realista/optimista | ✅ Activo |
| `modules/orchestration_v4/` | Flujo dos fases: Hook → Validación | ✅ Activo |
| `modules/asset_generation/` | Generación condicional con gates | ✅ Activo |
| `modules/auditors/` | APIs externas (Rich Results, Places, PageSpeed) | ✅ Activo |
| `modules/asset_generation/geo_enriched_bridge.py` | GEO → Delivery bridge | ✅ Activo |

---

## Notas de Cambios v4.35.1 — Trazabilidad Publication Gates (2026-04-25)

### Problema

Auditoría 2026-04-24 identificó 4 desconexiones documentales en el bloque "Calidad Garantizada":

1. **README L306**: Decía "6 Publication Gates" — el código tiene 9 (6 blocking + 3 advisory)
2. **Workflow v4_complete.md L95**: Referenciaba `v4_coherence_validator`, comando inexistente (fusionado en v4_quality_validator)
3. **PublicationGatesOrchestrator docstring**: Decía "5 critical gates" — tiene 9 entradas
4. **AGENTS.md**: Coherence Score fijo en 0.84 — la ejecución más reciente arrojó 0.89

### Solución

| Archivo | Cambio |
|---------|--------|
| `README.md` | "6" → "9 Publication Gates (6 blocking + 3 advisory)" + descripción gates 7-9 |
| `.agents/workflows/v4_complete.md` | `v4_coherence_validator` → `v4_asset_conditional` (comando real) |
| `modules/quality_gates/publication_gates.py` | Docstring "5 critical" → "9 publication gates" con lista completa |
| `AGENTS.md` | Coherence Score: "varía por ejecución; umbral: 0.8" |

### Backwards Compatibility

✅ Sin impacto. Solo correcciones documentales. Ningún comportamiento de código cambiado.

### Módulos Afectados

- `modules/quality_gates/publication_gates.py` — solo docstring
- `README.md` — solo bloque "Calidad Garantizada"
- `.agents/workflows/v4_complete.md` — solo paso 9
- `AGENTS.md` — solo tabla de estado

### FASE-TRAZABILIDAD-REFINEMENT — Correccion de Hallazgos D1-D4 (2026-04-25)

**Problema:** 4 hallazgos pendientes identificados post-TRAZABILIDAD-DOCS+PATCH + situacion GEO Score dual (dos fuentes generaban "GEO Score" con propositos distintos).

**Cambios por hallazgo:**

| Hallazgo | Solucion | Archivo |
|----------|----------|---------|
| D1: WARNING no afecta readiness | `summary.warnings` agregado a `check_publication_readiness()`. Warnings visibles en `gate_report.json` sin bloquear publicacion (Opcion C). | `publication_gates.py` L1013-1019 |
| D2: Tier C invisible en encabezado | `financial_tier_suffix` ("estimado -- Tier C") + `financial_tier_banner` (banner amarillo) cuando `tier == "C"`. | `v4_diagnostic_generator.py` L767-795, `diagnostico_v6_template.md` L70-73 |
| D3: Salud Tecnica GEO = 0/100 (bug lectura) | Key fix: `geo_flow_data.get('geo_score')` → `geo_assessment.get('total_score')`. Lee `geo_assessment.total_score: 23` en vez de key inexistente. | `v4_diagnostic_generator.py` L1273-1275 |
| D4: coherence=0.89 con assets baja confianza | `_build_asset_confidence_note()` cuenta assets con `confidence_score < 0.7`, genera nota en seccion Validacion de Calidad. | `v4_diagnostic_generator.py` L1877-1899, `diagnostico_v6_template.md` L85 |

**Decision arquitectonica GEO Score:**

- `_calculate_geo_score()` (GBP / Google Places API) = fuente **autoritativa** de GEO Score (externa, verificable, objetiva).
- `geo_flow` / GEOAssessment = mide **AI crawler readiness** (robots.txt, llms.txt, schema.org, meta tags). NO es duplicado del GBP geo_score. NO se depreca.
- `main.py` L2620: serializa `readiness_report.summary.warnings` al `gate_report.json`.

**Backwards Compatibility:** Sin cambios en API publica. Solo se agregaron variables nuevas al template_data y un key nuevo en el summary dict.

### FASE-1-AMAZILIA-CORRECCION — Correccion Hallazgos VALIDATE-v2 (2026-04-27)

**Problema:** 4 hallazgos verificados en diagnostico VALIDATE-v2 para Amazilia Hotel.

**Cambios por hallazgo:**

| Hallazgo | Solucion | Archivo |
|----------|----------|---------|
| M3: can_use inconsistente | Unificado: `can_use = preflight_status != "BLOCKED"` en ambos `v4_asset_orchestrator.py` L868 y `asset_metadata.py` L151-169. Antes: orchestrator usaba logica compleja con `confidence_level != "CONFLICT"`, metadata rechazaba si `confidence_score < 0.5`. | `v4_asset_orchestrator.py` L868, `asset_metadata.py` L151-169 |
| H1: local_content_page "Unknown asset type" | Handler agregado en `conditional_generator.py` L541-551. Llama `LocalContentGenerator.generate_content_set()` y serializa `LocalContentSet` a markdown para compatibilidad con pipeline. | `conditional_generator.py` L541-551 |
| N1: Header dual en metricas IA | Eliminado `## [NEW] Metricas de Optimizacion para IA` de `_build_geo_problems_table()`. Template ya provee `### Metricas de Acceso para IA`. Solo queda un header. | `v4_diagnostic_generator.py` L1304-1309 |
| M4: Backslashes en JSON de paths | `_to_relative_path()` ya normaliza a forward slashes. `output_dir` se serializa via `result.to_dict()` → `_to_relative_path()`. Confirmado: paths en `asset_generation_report.json` usan `/`. | `v4_asset_orchestrator.py` L95-117 |

**No corregidos en esta sesion (deferidos):**

| Hallazgo | Razon de defer |
|----------|----------------|
| T4: "Salud Tecnica GEO" timing | Requiere reorderar pipeline FASE 3.5 vs FASE 4 — es cambio arquitectonico complejo, se maneja en sesion independiente. |

**Tests:** 251/252 passed (1 fallo pre-existente en `test_proposal_alignment.py::test_known_mappings` — `KeyError: 'Boton de WhatsApp'`, no relacionado a estos cambios).
**Validaciones:** 4/4 passed.

## Notas de Cambios v4.37.0

**Módulos afectados**: `v4_proposal_generator`, `v4_diagnostic_generator`, `two_phase_flow`, `scenario_calculator`, `version_consistency_checker`

**Problema**: Auditoría forense (ContextMv2.md) reveló 2 bugs de credibilidad comercial y 6 hardcodes/stubs que producían datos falsos en la propuesta. version_consistency_checker.py crasheaba en Windows cp1252. VERSION.yaml desincronizado de CHANGELOG.

**Solución**:
- BUG-1/2: Corrección de formato ROI y explicación de pain_ratio en proyección financiera
- H-1→H-6: Eliminación de placeholders y stubs silenciosos; datos ahora provienen de fuentes reales o se marcan explícitamente como no disponibles
- Unicode fix: sys.stdout.reconfigure(encoding="utf-8") siguiendo patrón de log_phase_completion.py
- derive_version_from_changelog.py: Nuevo script para derivar VERSION.yaml desde CHANGELOG

**Backwards compatibility**: Total. Los fixes son incrementales. Templates existentes siguen funcionando. Los stubs que antes retornaban False ahora retornan estado real o marcador textual.

**Deuda técnica documentada**: 19 hardcodes (H-9→H-27) en pricing, escenarios y fallbacks catalogados en docs/technical_debt/ para proyecto futuro de extracción de configuración.

**Tests**: ~2363 tests sin regresiones. v4complete verificado con coherence >= 0.80.

## Notas de Cambios v4.41.0 — PROPOSAL-COMERCIAL-FIX (2026-05-06)

**Módulos afectados**: `v4_diagnostic_generator`, `v4_proposal_generator`, `main.py`, `asset_catalog`, `pain_solution_mapper`, `conditional_generator`, `asset_diagnostic_linker`, `site_presence_checker`

**Problema**: 7 defectos comerciales en el flujo de propuesta v4: coherence score invented by fallback, WhatsApp conflicts no visible, pain_ratio sin explicación, geo_playbook redundante, planes SEO/AEO genéricos, Tier C sin advertencia, y evidencia JSON sin ruta persistente.

**Solución**:

- **FASE-PROP-A** — Coherence Score Unificado: Pipeline reordenado (CoherenceValidator antes de `diagnostic_gen.generate()`). Diagnóstico usa valor real. Template muestra `gate_status`. Fallback `_calculate_coherence_score()` deprecado.

- **FASE-PROP-B** — WhatsApp Conflict Status: `_confidence_to_nivel_significado()` detecta conflictos WhatsApp. Tabla de calidad los muestra cuando `whatsapp_status='conflict'`.

- **FASE-PROP-C** — Proyecciones Financieras Transparentes: `pain_ratio_note` reescrito para explicar `pain_ratio` y `recovery_factor`. Placeholder `${pain_ratio_note}` en template.

- **FASE-PROP-D** — geo_playbook DEPRECATED: `geo_playbook` eliminado de `asset_catalog.py` (status DEPRECATED), `pain_solution_mapper.py` (low_gbp_score solo → review_plan), `conditional_generator.py`, `asset_diagnostic_linker.py`, `site_presence_checker.py`. Funcionalidad cubierta por delivery GEO existente.

- **FASE-PROP-E** — SEO/AEO Plans por Score: `_build_7_day_plan()` y `_build_30_day_plan()` incluyen acciones específicas cuando score SEO < 30 o score AEO < 30. Tabla de calidad incluye AEO cuando `score_aeo < 30`.

- **FASE-PROP-F** — Tier C Warning: `_prepare_template_data()` extrae `financial_evidence_tier` desde `financial_breakdown.evidence_tier` (fallback: "C"). Template muestra banner ⚠️ condicional para Tier C.

- **FASE-PROP-G** — Rutas Persistentes: `_make_evidence_path(hotel_id, basename)` crea `output/v4_complete/{hotel_id}/v4_audit/{basename}_{timestamp}.json`. JSONs de audit report, gate report y financial scenarios ahora incluyen `hotel_id` en ruta. Subdirectorios creados con `os.makedirs(..., exist_ok=True)`.

**Backwards compatibility**: Sí. geo_playbook deprecation es transparente (no se prometía en producción). Coherence unificado, Tier C warning y pain_ratio_note son adiciones o cambios de presentación. Rutas persistentes no afectan lectura legacy (solo writes nuevos).

**Tests**: ~25 tests nuevos. `run_all_validations.py --quick` pasa 4/4. 0 regresiones.

---

### v4.42.1 - 2026-05-08 — FASE-2-A: Detection & Enrichment Hardening

**Módulos afectados**: `publication_gates`, `proposal_asset_alignment`, `indirect_traffic_optimization_gen`, `faq_gen`

**Problema**:
- FIX-5: `except Exception` en `_proposal_asset_alignment_gate()` tragaba errores de `SitePresenceChecker` silenciosamente, seteando `site_presence_report = None`. Esto causaba que assets no verificables se marcaran como "missing" en vez de "indeterminate".
- FIX-6: `IndirectTrafficOptimizationGenerator.generate()` generaba recomendaciones genéricas sin consultar datos reales del hotel (GBP reviews, schemas, performance).
- FIX-7: `FAQGenerator.generate_list()` usaba solo `hotel_data.get('servicios')` sin verificar el sitio real del hotel para detectar servicios específicos (termas, spa, cascadas).

**Solución**:
- **FIX-5 — SitePresenceChecker Hardening**: `publication_gates.py`: el `except` ahora loguea `logger.error()` con traceback completo y retorna `{'presence_status': 'unknown', 'error': str(e), 'assets_checked': {...}}` en vez de `None`. `proposal_asset_alignment.py`: nuevo campo `indeterminate` en `AlignmentReport`. `verify_proposal_asset_alignment()` detecta dict con `presence_status='unknown'` y marca assets como `indeterminate` en vez de `missing`. El gate incluye conteo de `indeterminate` en el mensaje sin bloquear la publicación.
- **FIX-6 — Audit-Aware Traffic**: `indirect_traffic_optimization_gen.py`: nuevo parámetro `audit_report_path` en `generate()`. Lee `audit_report.json` y genera sección "Diagnóstico Data-Driven" con datos reales de GBP (reseñas, rating), schemas detectados, performance (PageSpeed). Incluye "Acciones Prioritarias" con severidad [Crítico]/[Alta]/[Media] basadas en los datos.
- **FIX-7 — Site-Aware FAQ**: `faq_gen.py`: nuevo método `_extract_services_from_site(url)` que hace scraping ligero (requests + BeautifulSoup) para detectar 20 keywords de servicios (termas, spa, cascadas, masaje, senderismo, etc.). `generate()` y `generate_list()` aceptan `site_url` opcional. Los servicios detectados se combinan con `hotel_data.servicios` (sin duplicar) y se incluyen en el prompt del LLM.

**Backwards compatibility**: 100%. `audit_report_path` y `site_url` son parámetros opcionales con default `None`. `AlignmentReport.indeterminate` es campo nuevo; `to_dict()` lo incluye solo si no está vacío. Código existente que no pase estos parámetros funciona exactamente igual.

**Tests**: 24 tests nuevos (7 hardening + 8 traffic + 9 FAQ). `run_all_validations.py --quick` pasa 5/5. 0 regresiones.

---

### v4.44.1 - 2026-05-11 — FASE-2-DEFAULT: Eliminar defaults hardcodeados cross-hotel

**Módulos afectados**: `open_graph_generator.py`, `conditional_generator.py`

**Problema**:
- `open_graph_generator.py` tenía defaults hardcodeados de 'Amazilia Hotel Campestre' en hotel_name (L87), rating=4.5/review_count=202 (L94), website_url='https://amaziliahotel.com/' (L107) y dentro del HTML comentario (L231).
- `conditional_generator.py` L523 usaba métodos privados `_generate_html()` y `_extract_og_data()` de OpenGraphGenerator, bypassing la lógica pública.

**Solución**:
- **hotel_name**: Validación explícita con `ValueError` si falta o vacío. fallback de 'hotel_name' → 'name' (sin default hardcodeado).
- **rating/review_count**: Sin defaults; `None` si no presente → omitidos del markup.
- **website_url**: Validación explícita con `ValueError` si falta.
- **generate_content() público**: Nuevo método público en `OpenGraphGenerator` para uso por `conditional_generator` sin invocar métodos privados.
- **HTML comment dinámico**: `<!-- Open Graph Meta Tags for {og_data.hotel_name} -->` en vez de hardcode 'Amazilia Hotel Campestre'.

**Backwards compatibility**: Sí. Métodos públicos `generate()` y `generate_content()` operan igual. El único cambio breaking sería si código externo dependiera del fallback 'Amazilia Hotel Campestre' — ahora lanza `ValueError`.

**Tests**: 11 tests nuevos (FASE-2-DEFAULT). `run_all_validations.py --quick` pasa 5/5. 0 regresiones en tests existentes (7 pre-existentes de `test_open_graph_generation.py`).

## Notas de Cambios v4.49.0 — HOOK-PDF (2026-07-09)

**Módulos afectados**: `commercial_documents` (nuevo módulo `hook_pdf_generator`), `main.py`, `data_structures.py`

**Problema**: Output de v4complete es técnico (.md + JSON); hoteleros no leen JSON-LD. Se necesitaba un PDF gancho de 2 páginas "¿Cuánto pierde su hotel?" con datos del propio hotel para pre-venta.

**Solución**:
- **`HookPDFData`** dataclass en `data_structures.py` (34 campos): datos del hotel, financieros, scores 4 pilares, top 3 brechas, pricing, evidence_tier.
- **`HookPDFGenerator`** en `hook_pdf_generator.py` con pipeline: `extract_data()` → `validate_data()` (8 checks) → `render_html()` → `generate()` (weasyprint).
- **Comando CLI** `hook-pdf` en `main.py` con args: `--output-dir`, `--template`, `--style`, `--dry-run`, `--force`, `--verbose`.
- **Template** `templates/hook_template.md` (HTML con 34 placeholders `{{CAMPO}}`) + `templates/hook_styles.css`.
- **36 tests unitarios** en `tests/commercial_documents/test_hook_pdf_generator.py` cubren: extract_data, validate_data (8 validaciones), render_html, generate (dry-run + real), formato COP, slugify, glob pattern, tier detection.

**Backwards compatibility**: Sí. Módulo nuevo, no modifica archivos existentes excepto `__init__.py` (nuevos exports) y `main.py` (nuevo comando choice). Tests existentes no afectados (256 tests en suite completa).

**Tests**: 36 tests nuevos. 256/256 pasando. 0 regresiones.

**E2E (FASE-4 — 2026-07-10)**:
- v4complete regenerado para Luxorhotel (176s, exit 0). Expected monthly: $3.741.696 COP, Tier B.
- PDF generado: `deliveries/luxorhotel_gancho.pdf` (27,552 bytes, 1.486s).
- 2 páginas exactas. Cero placeholders `{{...}}` sin reemplazar (34/34 resueltos).
- Cifra gancho: 28pt (≥24pt requerido). Disclaimer Tier B visible en página 1.
- 34 campos cross-validados contra `01_DIAGNOSTICO` + `02_PROPUESTA` + `v4_complete_report.json`. Sin discrepancias.
- `--dry-run` funcional. Tiempo generación <30s (1.486s).
