# Guía Técnica - IA Hoteles Agent

**Versión:** v4.43.0 (TERMALES-REFACTOR)
**Última actualización:** 2026-05-09

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

