# Guía Técnica IA Hoteles Agent CLI

**Ultima actualizacion:** 13 Abril 2026
||**Version:** 4.28.0 (4 Pilares Alignment + Voice Readiness Proxy)
||**Audiencia:** Desarrolladores, DevOps, Contribuidores

## Notas de Cambios — v4.28.0 (FASE-LLMSTXT-FIX + FASE-ASSETS-VALIDACION)

**Fecha:** 13 Abril 2026
**Fases:** FASE-LLMSTXT-FIX + FASE-ASSETS-VALIDACION (ejecutadas en paralelo)

### Resumen

Dos fases complementarias que cierran desconexiones críticas del pipeline de generación de assets.

**FASE-LLMSTXT-FIX** resuelve D3 del AUDIT: el generador de llms.txt producía placeholders vacíos ("Hotel", URL "", "N/A") a pesar de que `geo_enriched/llms.txt` ya contenía datos reales. El fix agrega una cadena de fallback: generador → geo_enriched → hotel_data del audit → PENDIENTE_ONBOARDING. Nunca placeholders engañosos.

**FASE-ASSETS-VALIDACION** resuelve D4 del AUDIT: 3 de 7 servicios prometidos en la propuesta comercial no generaban asset (voice_assistant_guide, whatsapp_button, monthly_report). El cliente pagaba por servicios que no recibía. Ahora 7/7 servicios tienen asset garantizado.

### Módulos Afectados

#### 1. modules/asset_generation/llmstxt_generator.py
- Nuevo parámetro `geo_enriched_path: Optional[Path]` en `generate()` y `generate_from_assessment()`
- Si `geo_enriched_path / "llms.txt"` existe y tiene >50 chars → retorna ese contenido directamente
- Warning log cuando hotel name es genérico ("Hotel") o vacío
- **Cadena de fallback**: geo_enriched → GEO bridge (post-generación) → hotel_data → PENDIENTE_ONBOARDING

#### 2. modules/asset_generation/conditional_generator.py
- `_generate_content()` acepta `hotel_id: str = ""` (backward compat)
- En branch `llms_txt`: construye `geo_enriched_path = output_dir / hotel_id / "geo_enriched"` y pasa al generador
- Nuevo handler de contenido para `monthly_report`

#### 3. modules/asset_generation/monthly_report_generator.py (NUEVO)
- Generador de informe mensual con KPIs de seguimiento
- Contenido: hotel + período, KPIs monitoreados (tráfico web, GBP views, reservas directas, WhatsApp clicks), checklist acciones mensuales, "Próximos pasos" basado en assets entregados
- No requiere datos reales — plantilla de seguimiento para el cliente

#### 4. modules/asset_generation/proposal_asset_alignment.py (NUEVO)
- Verificador propuesta→asset con mapeo de 7 servicios
- `verify_proposal_asset_alignment()`: retorna AlignmentReport (aligned/missing/low_quality)
- `PROPOSAL_SERVICE_TO_ASSET`: fuente de verdad (7 mapeos servicio → asset)

#### 5. modules/asset_generation/asset_catalog.py
- Nuevo entry `monthly_report` (promised_by=["always"])
- `whatsapp_button.promised_by` += "always" (se genera siempre)
- `voice_assistant_guide.promised_by` += "always_aeo" (se genera siempre que propuesta promete AEO)

#### 6. modules/quality_gates/publication_gates.py
- Gate 9: `proposal_asset_alignment_gate` (WARNING mode)
- Verifica que los 7 servicios de la propuesta tengan assets generados
- Total gates: 8 → 9

### Tests
- test_llmstxt_generator.py: 8 tests (fallback, warnings, backward compat)
- test_monthly_report.py: 12 tests
- test_voice_guide_generation.py: 9 tests
- test_whatsapp_button.py: 11 tests
- test_proposal_alignment.py: 13 tests
- test_proposal_alignment_gate.py: 7 tests
- **Total nuevos: 60 tests, 0 regresiones**

### Backwards Compatibility
- `generate(hotel_data)` sin `geo_enriched_path` funciona igual (default None)
- `generate_from_assessment` forwarda el parámetro opcional
- Gate 9 es WARNING (no bloquea publicación)
- Assets nuevos funcionan sin datos de onboarding (plantillas genéricas)
- `proposed_by` es aditivo — no altera lógica existente

---

## Notas de Cambios — v4.29.0: geo_enriched Bridge (EN PROGRESO)

**Fecha:** 13 Abril 2026
**Fase:** FASE-GEO-BRIDGE

### Resumen
FASE-GEO-BRIDGE crea el bridge que conecta `geo_enriched/` (datos reales del GEO Flow) con el pipeline de delivery de assets. Anteriormente, los assets se generaban con confidence 0.5 (placeholders) mientras `geo_enriched/` contenía los datos reales pero nunca se entregaban al cliente.

### Módulos Afectados

#### 1. modules/asset_generation/geo_enriched_bridge.py (NUEVO)
- Nueva función `try_enrich_from_geo_enriched()`: dados asset_type, content, y confidence < 0.7, busca versión enriquecida en `geo_enriched/`
- Mapeo de assets: `hotel_schema` → `hotel_schema_rich.json`, `llms_txt` → `llms.txt`, `faq_page` → `faq_schema.json`
- Confidence boost: 0.5 → 0.85 cuando enrichment disponible
- Detección de placeholders: rechaza contenido genérico ("Hotel", "https://your-website.com")

#### 2. modules/asset_generation/v4_asset_orchestrator.py (FASE-GEO-BRIDGE)
- Import de `try_enrich_from_geo_enriched`
- Integration point: después de `_generate_with_coherence_check()`, antes de agregar a lista `generated`
- Si `confidence < 0.7` y archivo existe en `geo_enriched/`: sobreescribe archivo en disco y actualiza `GeneratedAsset.confidence_score = 0.85`

---

### FASE-CONF-GATE: Asset Confidence Gate (Gate #8)

**Fecha:** 13 Abril 2026
**Fase:** FASE-CONF-GATE

#### Resumen
Gate #8 en publication gates que valida `confidence_score` de assets generados. Usa estrategia conservadora (Opción A): assets con confidence < 0.7 generan WARNING (no bloquean publicación). El cliente recibe alerta de calidad sin impedir la entrega.

#### Módulos Afectados

##### modules/quality_gates/publication_gates.py
- `GateStatus.WARNING` agregado al enum (4 estados: PASSED, FAILED, BLOCKED, WARNING)
- `_asset_confidence_gate()`: nuevo gate #8 en `PublicationGatesOrchestrator`
- Threshold: 0.7 (configurable)
- Comportamiento:
  - Sin `generated_assets` en assessment → PASSED (backward compat)
  - Todos >= 0.7 → PASSED
  - Algunos < 0.7 → WARNING con detalles (tipo, score de cada asset bajo)
- Total gates: 7 → 8

#### Backwards Compatibility
- Gate registrado en orchestrator junto a gates 1-7
- Assessment sin `generated_assets` → gate pasa (no rompe flujos existentes)
- `passed=True` en WARNING → `is_ready_for_publication()` sigue retornando True

---

## Notas de Cambios — v4.28.0: 4 Pilares Alignment + Voice Readiness Proxy

**Fecha:** 12 Abril 2026

### Resumen

FASE-D alinea toda la cadena de generación (diagnóstico → propuesta → gap analyzer → benchmarks) al modelo de 4 pilares (SEO+GEO+AEO+IAO). FASE-E introduce Voice Readiness Proxy como sub-score de AEO basado en inputs medibles (no medición directa Siri/Alexa).

### Módulos Afectados

#### 1. modules/analyzers/gap_analyzer.py (FASE-D)
- Expandido de 2 gaps (GEO+AEO) a **4 gaps (SEO+GEO+AEO+IAO)**
- Nuevos benchmarks: `seo_score_ref=50`, `iao_score_ref=15`
- Ponderación proporcional por pilar (suma = 1.0)
- `_map_brecha_to_paquete()` actualizado para 6 nuevos tipos de brecha

#### 2. modules/financial_engine/opportunity_scorer.py (FASE-D)
- Nuevas brechas IAO: `no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals`
- Nuevas brechas SEO: `no_meta_descriptions`, `poor_heading_structure`

#### 3. scripts/update_benchmarks.py (FASE-D)
- Nueva función `calculate_iao_score(hotel)` con 5 checks (20pts c/u, max 100):
  - `has_llms_txt`, `has_schema_entity`, `citability_score>50`, `allows_ai_crawlers`, `has_sames_as_links`
- `iao_avg` calculado por región
- `iao_score_ref` guardado por región en `plan_maestro_data.json`

#### 4. modules/utils/benchmarks.py (FASE-D)
- `iao_score_ref` añadido a `DEFAULT_DATA["regiones"]["default"]`

#### 5. modules/generators/report_builder.py (FASE-D) — ⚠️ DEPRECATED
- Comentario DEPRECATED añadido: "Este módulo pertenece al comando 'spark' (deprecado). El pipeline activo 'v4complete' usa V4DiagnosticGenerator + V4ProposalGenerator"
- Sección ANALISIS 4-PILARES expandida para mostrar SEO, GEO, AEO, IAO con scores

#### 6. modules/commercial_documents/templates/diagnostico_v6_template.md (FASE-D)
- Fila IAO añadida: `${iao_score}/100` (Para que te RECOMIENDEN)
- Labels de tabla alineados a narrativa comercial:
  - SEO Local (Para que te ENCUENTREN)
  - Google Maps (Para que te UBICQUEN)
  - AEO (Para que te CITEN)
  - IAO (Para que te RECOMIENDEN)
- Fila Visibilidad Digital (Global) con `${score_global}`

#### 7. modules/commercial_documents/v4_diagnostic_generator.py (FASE-D, FASE-E)
- `_get_regional_benchmarks()` ahora retorna 4 benchmarks incluyendo `iao_score_ref`
- Integración de `VoiceReadinessProxy.calculate()` en `_prepare_template_data()`
- Campos `voice_readiness_score` y `voice_readiness_level` disponibles en templates

#### 8. modules/commercial_documents/v4_proposal_generator.py (FASE-D)
- `score_global` es ahora la métrica principal para sugerir paquete
- Fallback: `score_tecnico` (backward compatibility)
- Alias `score_tecnico` mantenido en template data

#### 9. modules/auditors/voice_readiness_proxy.py (FASE-E) — NUEVO
- Módulo que calcula Voice Readiness basado en PROXY (inputs que alimentan asistentes de voz)
- **NO consulta APIs de Siri/Alexa/Google Assistant directamente**
- 4 componentes con pesos:
  - GBP completeness: 30pts (nombre, dirección, teléfono, horarios, website)
  - Schema for voice: 25pts (LocalBusiness, FAQ, Speakable)
  - Featured snippets: 25pts (AEOSnippetTracker o fallback desde schema)
  - Factual coverage: 20pts (horarios, teléfono, dirección, precios en texto)
- Niveles: critical (0-25), basic (26-50), good (51-75), excellent (76-100)
- Fallback graceful si FASE-B no completada (usa schema como proxy de snippets)

#### 10. modules/commercial_documents/data_structures.py (FASE-E)
- `DiagnosticSummary` tiene ahora:
  - `voice_readiness_score: Optional[int] = None`
  - `voice_readiness_level: Optional[str] = None`

#### 11. main.py (FASE-E)
- Pasa `voice_readiness_score` y `voice_readiness_level` al DiagnosticSummary

### Backwards Compatibility
- `score_tecnico` mantenido como alias de `score_global` (no breaking change)
- `report_builder.py` marcado DEPRECATED pero funcional
- Voice Readiness usa fallback si `aeo_snippets` no disponible (FASE-B no ejecutada)

### Tests
- 628 tests passing (0 regresiones)
- Errors pre-existentes en `data_validation/` y `observability/` (módulos faltantes)

### Documentacion Post-Implementacion (v4.28.0 docs-only)

**Problema:** README.md y AGENTS.md no reflejaban la implementacion de 4 pilares (SEO/GEO/AEO/IAO) ni Voice Readiness Proxy. Test count desactualizado. Residual `modelo_pilares: "2 Pilares GEO + JSON"` en gap_analyzer.py.

**Solucion:**
- README.md: seccion "Que es" expandida con tabla 4 pilares + progresion + score_global. Nueva seccion Voice Readiness Proxy con componentes/niveles/restricciones. Test count actualizado.
- AGENTS.md: modulo voice_readiness_proxy.py en tabla, mejoras actualizadas, tests corregidos.
- gap_analyzer.py: `modelo_pilares` corregido de "2 Pilares" a "4 Pilares SEO+GEO+AEO+IAO".

**Backwards-compat:** Cambios puramente documentales. Sin impacto en APIs, scores ni outputs.

---

## Notas de Cambios — Ciclo 2: RegionalADR + Validator Source-Aware

**Fecha:** 11 Abril 2026

### Resumen

Dos fases independientes ejecutadas en paralelo: FASE-I activa el RegionalADRResolver con whitelist por regiones validadas (eje_cafetero, antioquia), FASE-J extiende el NoDefaultsValidator para detectar fuentes sospechosas (legacy_hardcode, default) y hace el template honesto sobre la verificabilidad de los datos.

### Módulos Afectados

#### 1. modules/financial_engine/feature_flags.py (FASE-I)
- Nuevo campo `validated_regions: tuple = ("eje_cafetero", "antioquia")` — whitelist de regiones donde se usa ADR regional
- Nuevo método `should_use_regional_for(region: str) -> bool` — combina flag enabled + whitelist
- `from_env()` lee `FINANCIAL_REGIONAL_VALIDATED_REGIONS` (comma-separated)
- Caribe explícitamente excluido (36.7% diff vs legacy detectado en FASE-H)

#### 2. modules/financial_engine/adr_resolution_wrapper.py (FASE-I)
- `resolve()` llama `flags.should_use_regional_for(region)` ANTES de resolver regional
- Regiones no validadas caen a legacy ($300K hardcode) sin shadow comparison
- Cadena: user_provided > web_scraping > regional (si validada) > legacy

#### 3. modules/financial_engine/harness_handlers.py (FASE-I)
- `financial_calculation_handler()` resuelve occupancy regional si la región está validada
- Fallback a default 0.50 si región no validada

#### 4. modules/financial_engine/no_defaults_validator.py (FASE-J)
- Nuevo `SUSPECT_SOURCES = {"legacy_hardcode", "default", "unknown", "hardcoded", "estimated"}`
- `validate()` acepta `sources: Optional[Dict[str, str]]` (backward compatible)
- Warnings por fuentes sospechosas NO bloquean el cálculo (solo documentan)
- Propiedades nuevas: `has_suspect_sources`, `suspect_fields`, `source_reliability` (verified/estimated/unverified)

#### 5. modules/financial_engine/calculator_v2.py (FASE-J)
- `calculate()` acepta `data_sources` opcional, lo pasa al validator
- Metadata del resultado incluye `source_reliability` y `suspect_fields`

#### 6. modules/commercial_documents/templates/diagnostico_v6_template.md (FASE-J)
- Título condicional: `${financial_title_label}` (antes: hardcoded "Comisión OTA Actual (verificable)")
- Monto con asterisco: `${ota_commission_formatted} COP/mes${estimate_asterisk}`
- Nota condicional: `* Dato basado en estimaciones. Conecte GA4 para mayor precision.`

#### 7. modules/commercial_documents/v4_diagnostic_generator.py (FASE-J)
- `_build_financial_title_label(source_reliability)` → label según verificabilidad
- Placeholders: `financial_title_label`, `estimate_asterisk`, `estimate_footnote`

### Backwards Compatibility
- Sin `sources` param en validate() = comportamiento idéntico al anterior
- `can_calculate` sigue bloqueando solo 0/None/"" (warnings nunca bloquean)
- Regiones no validadas en whitelist = legacy automático (sin breaking change)

### Tests
- FASE-I: 4 tests feature_flags + 16 fixtures fix adr_wrapper (todos PASS)
- FASE-J: 8 tests source-aware (todos PASS)
- Suite regresión: 385/385 PASS, 0 regresiones

### Configuración (.env)
```
FINANCIAL_REGIONAL_ADR_ENABLED=True
FINANCIAL_REGIONAL_VALIDATED_REGIONS=eje_cafetero,antioquia
```

---

## Notas de Cambios v4.26.0 - Brecha Architectural Fix

**Fecha:** 10 Abril 2026

### Resumen

La propuesta V6 no consumía brechas reales del diagnóstico — usaba distribución fija 40/30/20/10 generando "phantom costs" (brechas ficticias con costo > $0 cuando el hotel tenía < 4 problemas reales). También había conflicto dual source (_inject_brecha_scores vs _get_brecha_*) y _identify_brechas ejecutándose 9x por generación.

### Módulos Afectados

#### 1. modules/commercial_documents/v4_proposal_generator.py (FASE-F)
- Eliminada distribución fija 40/30/20/10 en `_build_brecha_data()`
- Ahora consume `brechas_reales` con `impacto` real de `_identify_brechas()`
- Fallback a `top_problems` cuando `brechas_reales=None`

#### 2. modules/commercial_documents/v4_diagnostic_generator.py (FASE-G, FASE-H)
- `_inject_brecha_scores()` ya no sobrescribe nombre/costo/detalle (solo actualiza scores)
- Cache implementado para `_identify_brechas()`: 9x → 1x por generación
- `pain_to_type` cleanup: `low_ia_readiness` removido

#### 3. modules/commercial_documents/data_structures.py (FASE-I)
- Scenario: eliminada definición muerta (12 líneas)
- `calculate_quick_wins`: eliminada definición muerta (40 líneas)
- `extract_top_problems`: eliminada definición muerta (55 líneas)
- DiagnosticSummary: agregado campo `brechas_reales`

### Backwards Compatibility
- Si `brechas_reales=None`, proposal generator usa `top_problems` (comportamiento anterior preservado)
- Templates V4/V6 backward compatible con datos新旧混合

### Tests
- FASE-F: 5 testsphantom costs (todos PASS)
- FASE-G: 5 tests dual source (todos PASS)
- FASE-H: 4 tests cache + cleanup (todos PASS)
- FASE-I: 4 tests deduplication (todos PASS)
- Total: 18 tests nuevos, 0 regresiones

### Validación E2E (amaziliahotel.com)
- Brechas detectadas: 4 (antes: 6 con phantom costs)
- Costos por brecha: $783.000, $375.840, $313.200, $250.560 COP (proporcionales, no 40/30/20/10)
- Coherence: 0.92 (antes: 0.84)
- Publication: READY_FOR_PUBLICATION

## Notas de Cambios v4.25.3 - Fix AEO Score "Pendiente de datos"

**Fecha:** 8 Abril 2026

### Resumen

El score AEO del diagnostico v4complete mostraba "0 (Pendiente de datos)" en todos los hoteles porque `_calculate_aeo_score()` solo usaba PageSpeed API. Se implemento scoring completo de 4 componentes y deteccion real de Open Graph. FASE-C verifico la integracion end-to-end sin regresiones.

### Modulos Afectados

#### 1. seo_elements_detector.py (FASE-A)
- Stub reemplazado con implementacion real BeautifulSoup
- `_detect_open_graph()`: detecta `<meta property="og:*">`, requiere og:title + og:description
- `_detect_images_alt()`: cuenta imagenes sin atributo alt, pasa si <20%
- `_detect_social_links()`: detecta 8 dominios sociales

#### 2. v4_diagnostic_generator.py (FASE-B)
- `_calculate_aeo_score()` reescrito (lineas 1324-1378):
  - **ANTES**: solo verificaba `performance.mobile_score` → "0 (Pendiente de datos)" si PageSpeed fallaba
  - **AHORA**: scoring de 4 componentes x 25pts = 100pts:
    - Schema Hotel valido → +25pts (detectado no valido → +10pts)
    - FAQ Schema valido → +25pts (detectado no valido → +10pts)
    - Open Graph detectado → +25pts (via `hasattr` para compatibilidad)
    - Citabilidad tiers → 70→+25, 40→+15, >0→+5, None→0pts
  - Retorna string numerico ("0", "25", "50", etc.) compatible con `_get_score_status()`
  - Usa `hasattr()` para `seo_elements` y `citability` (campos opcionales en V4AuditResult)

#### 3. Templates (FASE-C verificado, sin cambios)
- v6 linea 49: `${aeo_score}/100` → renderiza numero (ej: "50/100")
- v4 linea 40: `${schema_infra_score}` → mapeado a `_calculate_aeo_score()` (L514)

### Backwards Compatibility
- Interfaz de `SEOElementsResult` sin cambios (mismos campos, mismos tipos)
- `_calculate_aeo_score()` retorna string numerico compatible con `_get_score_status()`
- Templates no requieren cambios (`${aeo_score}` renderiza numero como antes)
- Benchmark regional `aeo_score_ref` (default 20) sigue siendo coherente

### Tests
- 24 tests nuevos (9 FASE-A + 15 FASE-B)
- 0 regresiones
- `run_all_validations.py --quick` 4/4 pasan

### FASE-D: 5 Bugs Medios + seo_elements Serialization

**Resumen**: Corrección de 5 bugs medios (dead code, claves duplicadas, inconsistencia de confidence, pipe markdown, sufijo /100) + serialización faltante de `seo_elements` en `V4AuditResult.to_dict()`.

**Modulos afectados**:

#### 3a. v4_diagnostic_generator.py (FASE-D)
- **MED-1**: Eliminación de 148 líneas dead code — dos definiciones de `_compute_opportunity_scores` e `_inject_brecha_scores`. La segunda definición (FASE-C) es la productiva; la primera (FASE-B legacy) silenciaba a la segunda por shadowing.
- **MED-2**: Eliminadas 4 claves `*_regional_avg` duplicadas en dict de template data. Python usaba la última silenciosamente.
- **MED-3**: `confidence.value` → `confidence.value.upper()` en WhatsApp. Otros campos ya usaban 'ESTIMATED'/'VERIFIED' en mayúsculas.
- **MED-4**: Tabla markdown scorecard — filas tenían `||` o `|||` al inicio en vez de `|`, rompiendo alineación.
- **MED-5**: AEO score en template ahora incluye `/100` para consistencia visual.

#### 3b. v4_comprehensive.py (FASE-D)
- **SER-1**: `V4AuditResult.to_dict()` ahora serializa campo `seo_elements` completo (8 campos: open_graph, imagenes_alt, redes_activas, confidence, notes, open_graph_tags, images_without_alt, social_links_found). Sin este fix, `audit_report.json` perdía datos OG, imágenes sin alt y enlaces sociales.
- **SER-1**: `"seo_elements_detection"` agregado a `executed_validators` en la auditoría.

**Arquitectura**: `to_dict()` es el serializador usado por `main.py` para persistir `audit_report.json`. Antes de SER-1, el detector `SEOElementsDetector` ejecutaba y asignaba resultado a `V4AuditResult.seo_elements`, pero el JSON persistido no contenía esos datos. El pipeline de datos fluye: Detector → V4AuditResult.seo_elements → to_dict() → audit_report.json. SER-1 cierra la brecha de persistencia.

**Backwards Compatibility**: Totalmente backwards compatible. `seo_elements` es campo opcional (`Optional[SEOElementsResult]`). El bloque `if self.seo_elements:` solo agrega al dict si existe. Eliminación de dead code no afecta comportamiento (métodos eliminados nunca se ejecutaban).

---

### Corrección Falsos Positivos — FASE-A/B/C/D (v4.25.3)

**Fecha:** 9 Abril 2026

#### Resumen

Tres falsos positivos/errores de narrativa detectados en diagnóstico de amaziliahotel.com. FASE-D validó E2E sin cambios de código — coherence 0.84, READY_FOR_PUBLICATION.

#### Modulos Afectados

**FASE-A — WhatsApp Detection Fix:**
- `v4_comprehensive.py`: `_detect_whatsapp_from_html(html)` escanea HTML por patrones wa.me, api.whatsapp.com, whatsapp://, clases CSS whatsapp. Conectado a `_run_cross_validation()` via `whatsapp_html_detected`.
- `data_structures.py`: Campo `whatsapp_html_detected: bool = False` en `ValidationSummary`.
- `v4_diagnostic_generator.py`: Condición de brecha WhatsApp ahora verifica `phone_web` OR `whatsapp_html_detected` (L1806-1808). Quick wins y tabla brechas actualizados.

**FASE-B — Citability Narrative Fix:**
- `v4_diagnostic_generator.py`: Lógica distingue `blocks_analyzed=0` (narrativa "no discoverable") vs score bajo real (narrativa "poco estructurado").
- `opportunity_scorer.py`: Justificación `low_citability` genérico en vez de asumir contenido malo.

**FASE-C — Regional Template Fix:**
- `diagnostico_v6_template.md`: Typo "yRevisan" → "y Revisan" corregido.
- `v4_diagnostic_generator.py`: `_build_regional_context()` — Eje Cafetero, San Andrés, Llanos Orientales, Costa Atlántica agregados a `region_contexts`. Fallback genérico mejorado.

#### Backwards Compatibility
- Sin cambios en API pública. `ValidationSummary.whatsapp_html_detected` default `False` (backward compatible).
- Templates no requieren regeneración (cambios son en lógica de generación, no en output format).

#### Tests
- 3 nuevos tests `blocks_analyzed=0` en `test_diagnostic_brechas.py`
- 218 passed, 7 pre-existentes (sin relación con cambios)
- FASE-D E2E: coherence 0.84, 5/6 gate checks

#### Validación E2E (FASE-D)
- Hotel: amaziliahotel.com
- Fix WhatsApp: funcional (sitio genuinamente no tiene WhatsApp — brecha legítima)
- Fix Citability: funcional (blocks=0 genera "No Discoverable", no "poco estructurado")
- Fix Regional: parcial (yRevisan corregido, región=nacional persiste como fallback)

---

### Corrección Integridad de Datos — FASE-E (v4.25.3)

**Fecha:** 9 Abril 2026

#### Resumen

Datos detectados correctamente en capas tempranas del pipeline no se propagaban a consumidores intermedios/finales. FASE-E elimina 2 persistencias de datos incorrectos: (1) `whatsapp_html_detected` no llegaba a pain_solution_mapper, ValidationSummary ni coherence_validator; (2) región se quedaba en "nacional" cuando la URL no contenía keywords geográficas pero GBP sí tenía dirección regional.

#### Módulos Afectados

**FASE-E Workstream WhatsApp (W1-W4):**
- `main.py` (W1): Nueva rama `elif getattr(audit_result.validation, 'whatsapp_html_detected', False)` después de `elif whatsapp_web:` (L1766+). Crea `ValidatedField("whatsapp_number", "detected_via_html", ESTIMATED, sources=["HTML"], 0.6)`.
- `modules/commercial_documents/pain_solution_mapper.py` (W2): `detect_pains()` recibe `whatsapp_html_detected=False`. Condición L332: `if (not whatsapp_field or ...) and not whatsapp_html_detected`. Caller en main.py pasa `whatsapp_html_detected=getattr(audit_result.validation, 'whatsapp_html_detected', False)`.
- `modules/scrapers/web_scraper.py` (W3): `_extract_contact()` agrega parseo de `tel:` links después de regex patterns. Solo si `'telefono' not in contact` (fallback, no override).
- `modules/commercial_documents/coherence_validator.py` (W4): `validate()` recibe `whatsapp_html_detected=False`, lo pasa a `_check_whatsapp_verified()`. Si `not whatsapp_field and whatsapp_html_detected` → score 0.5 parcial (no 0.0 penalizante).

**FASE-E Workstream Regional (R1-R3):**
- `main.py` (R1): Nueva función `_infer_region_from_address(address) -> str | None`. REGION_PATTERNS: eje_cafetero (armenia, quindio, pereira, etc.), caribe, antioquia, centro, valle, llanos, san_andres. Inserción post-audit (~L1479): si `region == "nacional"` y `audit_result.gbp.address` existe → re-evalúa.
- `modules/commercial_documents/v4_diagnostic_generator.py` (R2): L413 sanitización: `if _raw.lower() in ("nacional", "general", "default", "unknown") → "Colombia"`, else `_raw.replace("_", " ").title()`.
- `main.py` (R3): `_detect_region_from_url()` keywords Eje Cafetero ampliadas: +cafetero, finca, montenegro, filandia, circasia, termales.

#### Backwards Compatibility
- `pain_solution_mapper.detect_pains()`: nuevo parámetro `whatsapp_html_detected=False` es backward compatible.
- `coherence_validator.validate()` y `_check_whatsapp_verified()`: nuevo parámetro `whatsapp_html_detected=False` es backward compatible.
- `_infer_region_from_address()`: función nueva, no afecta código existente.
- Scraper: fallback `tel:` solo agrega si `'telefono' not in contact` — no override de datos existentes.

#### Validación E2E
- Hotel: amaziliahotel.com
- **Región: eje_cafetero** (antes persistía "nacional" a pesar de FASE-C fix parcial)
- Coherence: 0.84 ≥ 0.80 — Pasa gate
- Publication: READY_FOR_PUBLICATION
- whatsapp_button generado — no generó pain falso "no_whatsapp_visible"

---

## Notas de Cambios v4.21.0 - Consolidacion AEO/IAO

**Fecha:** 6 Abril 2026
**Version:** 4.25.0 (FASE-E: Micro-Content Local Generator)

## Notas de Cambios v4.25.0 - Micro-Content Local Generator

**Fecha:** 6 Abril 2026
**Version:** 4.25.0 (FASE-E: Micro-Content Local Generator)

### Resumen

Generador de 3-5 paginas de contenido local orientadas a keywords long-tail para hoteles boutique del Eje Cafetero. Add-on comercial vendible ($50K COP por 3 paginas) al Kit Hospitalidad Digital. Cada pagina tiene keyword target, 800-1200 palabras, schema Article JSON-LD, y link a reservas directas.

### Modulos Afectados

#### 1. modules/asset_generation/local_content_generator.py (NUEVO)
- Dataclasses: LocalContentPage (keyword_target, title, slug, content_md, schema_article, internal_links, meta_description, word_count), LocalContentSet (hotel_name, location, pages, total_word_count)
- LocalContentGenerator.generate_content_set(): genera 3-5 paginas segun tipo de hotel
- KEYWORD_TEMPLATES por tipo: termales (5), parque_natural (5), pueblo_patrimonio (5), cafe (5), boutique (5), general (5)
- KEYWORD_PRIORITY: heuristica de volumen estimado para ordenar keywords
- Contenido expandible: 6-8 secciones por pagina (intro, contexto, informacion, practica, cultura, recomendaciones, datos_utiles, conclusion)
- Schema Article JSON-LD con @context, @type, headline, description, author, publisher, keywords, inLanguage
- Meta description 150-160 chars
- Internal links: home del hotel + link a reservas WhatsApp
- content_passes_scrubber(): metodo estatico que detecta frases AI genericas
- Compatible con ContentScrubber de FASE-B

#### 2. modules/asset_generation/templates/local_content/page_template.md (NUEVO)
- Template de prompt para generacion LLM
- Reglas: 800-1200 palabras, 4-5 secciones H2, tono informativo no vendedor

#### 3. modules/asset_generation/templates/local_content/keyword_selection.md (NUEVO)
- Guia para seleccionar keywords por tipo de hotel con priorizacion

#### 4. modules/asset_generation/asset_catalog.py (MODIFICADO)
- Entrada local_content_page registrada con status IMPLEMENTED

### Tests
15 tests nuevos en test_local_content_generator.py. 0 regresiones.

**Version:** 4.23.0 (FASE-D: Google Search Console Integration)

### Resumen

Integracion de Google Search Console como fuente de datos para el diagnostico, pasando de estimaciones cualitativas ("0% confianza") a datos reales de keywords, posiciones y CTR del hotel. GSC es 100% opcional -- el flujo v4complete funciona completamente sin GSC.

### Modulos Afectados

#### 1. modules/analytics/google_search_console_client.py (NUEVO)
- Cliente GSC usando webmasters v3 API con service account
- Dataclasses: GSCQueryData, GSCPageData, GSCReport
- Metodos: is_configured(), get_search_analytics(), get_top_opportunities()
- Graceful fallback: retorna GSCReport con is_available=False sin credenciales
- Reutiliza las mismas credenciales de GA4 (config/google-analytics-key.json)
- Scope: https://www.googleapis.com/auth/webmasters.readonly
- Costo API: GRATIS

#### 2. modules/analytics/data_aggregator.py (NUEVO)
- Unifica datos GA4 + GSC en UnifiedAnalyticsData
- Confidence level: LOW (0 fuentes), MEDIUM (1 fuente), HIGH (2 fuentes)
- Metricas derivadas: estimated_ia_visibility, organic_health_score
- Graceful degradation: funciona sin GSC, sin GA4, o sin ambos

#### 3. modules/onboarding/add_gsc_step.py (NUEVO)
- Paso GSC opcional en onboarding del hotel
- ask_gsc_during_onboarding(): pregunta si tiene GSC, pide site_url
- apply_gsc_config(): guarda configuracion GSC en config del hotel

#### 4. modules/commercial_documents/v4_diagnostic_generator.py (MODIFICADO)
- Integration GSC en seccion "Fuentes de Datos" del diagnostico
- Con GSC: muestra impresiones, posiciones, CTR reales
- Sin GSC: fallback honesto con instruccion de activacion

#### 5. data_models/analytics_status.py (MODIFICADO)
- Agregados campos: gsc_available, gsc_error, gsc_status_text
- Nueva funcion: gsc_status_for_template()

### Tests

33 tests nuevos: 14 en test_google_search_console_client.py + 19 en test_data_aggregator.py.

## Notas de Cambios v4.21.0 - Consolidacion AEO/IAO

**Fecha:** 4 Abril 2026

### Resumen

Eliminacion de redundancia entre scores AEO e IAO (ambos median infraestructura de datos estructurados) y score de Voice Readiness (hardcodeado "--"). Se unifico todo bajo un unico score AEO. Adicionalmente, gap_analyzer se reestructuro de 3 a 2 pilares.

### Modulos Afectados

#### 1. v4_diagnostic_generator.py
**Problema**: 3 metodos redundantes o dead code: `_calculate_iao_score()` (fallback a `_calculate_schema_infra_score()`), `_calculate_score_ia()` (duplicado), `_calculate_voice_readiness_score()` (retornaba "--" hardcodeado).
**Solucion**:
- Eliminados `_calculate_iao_score()`, `_calculate_score_ia()`, `_calculate_voice_readiness_score()`
- Renombrado `_calculate_schema_infra_score()` -> `_calculate_aeo_score()`
- Template v6: scorecard de 5 filas a 4 filas (GEO, GBP, AEO, SEO)
- Variables de template eliminadas: `iao_score`, `iao_status`, `voice_readiness_score`, `voice_readiness_status`

#### 2. gap_analyzer.py
**Problema**: Modelo de 3 pilares incluia "Momentum IA" (basado en IAO, score redundante).
**Solucion**:
- Eliminada referencia a "Momentum IA" / 3 pilares
- Redistribuido a 2 pilares: Pilar 1 (GBP & Voz Cercana) + Pilar 2 (Datos JSON-LD para IA / AEO)
- Prompt del LLM actualizado al modelo 2-Pilares

#### 3. report_builder.py
**Problema**: Metodo `_calculate_iao_score()` duplicado + referencias a IAO en scorecards.
**Solucion**:
- Eliminado `_calculate_iao_score()` y todas las referencias a IAO
- Scorecard V6 simplificado: eliminada fila "Score IA Avanzado (IAO)"

### Backwards Compatibility

- Variables de template eliminadas (iao_score, iao_status, voice_readiness_score, voice_readiness_status): si algun template personalizado las referencia, fallara con KeyError en Template.safe_substitute()
- Metodos eliminados son internos, no son API publica del modulo

---

### RESTAURACION: FASE-C (2026-04-12) — IAO como pilar independiente

**Problema**: FASE-CAUSAL elimino `_calculate_iao_score()` asumiendo que IAO y AEO "ambos median infraestructura de datos estructurados". Esto era INCORRECTO: AEO mide posicion cero en Google (buscador), IAO mide recomendacion en LLMs (agentes). Son canales diferentes.

**Restauracion**:
- `_calculate_iao_score_from_audit()` restaurado en `v4_diagnostic_generator.py` con logica correcta de 7 componentes (CHECKLIST_IAO)
- Nuevo modulo `modules/auditors/llm_mention_checker.py`: consulta OpenRouter/Gemini/Perplexity para detectar menciones del hotel
- Ponderacion 50/50: 50% checklist infraestructura + 50% resultado real de LLM mentions
- `_extraer_elementos_iao()` mejorado: crawler_access usa ai_crawlers, schema_advanced usa org_schema_detected, brand_signals detecta SameAs
- Variables template `iao_score/iao_status/iao_regional_avg` restauradas
- `DiagnosticSummary` ampliado con `iao_status`, `iao_regional_avg`, `llm_report_summary`
- Integracion en `v4_comprehensive.py`: Step 2.11 ejecuta LLMMentionChecker

**Arquitectura**: SEO (base) -> AEO (posicion cero) -> IAO (recomendacion IA). GEO lateral complementario.

**Costo**: $0-0.30/hotel (5 queries x 3 providers). Sin API keys: modo stub sin crashear.
- El score AEO (_calculate_aeo_score) fue reescrito en v4.25.3: scoring de 4 componentes x 25pts (Schema valido + FAQ valido + OG detectado + Citabilidad). Ya NO mantiene la logica del anterior schema_infra_score
- aeo_metrics_gen.py se mantiene como modulo tecnico interno

## Notas de Cambios v4.20.0 - Agent Harness v3.2.0 Refactor

**Fecha:** 3 Abril 2026

### Resumen

Refactor arquitectonico completo del modulo `agent_harness`. Se corrigio un syntax error critico en core.py linea 65 que impedia la delegacion recursiva de tareas, y se agregaron mejoras de fondo en thread safety, timeout protection, background task lifecycle, validacion per-task, y error learning. Version del harness: 0.3.0 -> 3.2.0.

### Modulos Afectados

#### 1. agent_harness/core.py (Orchestrator)
**Problema**: Linea 65 tenia codigo corrupto (`tokens=shlex....cmd)`) que causaba SyntaxError al intentar delegacion recursiva. Ademas, sin timeout, sin background tracking, sin validacion por tipo.
**Solucion**: 
- Fix sintaxis: `tokens = shlex.split(command)`
- `_execute_with_timeout()` con threading.Timer y configurable `default_task_timeout`
- BackgroundTaskInfo lifecycle con poll automatico
- `register_validator(task_name, fn)` para validacion per-task
- Graceful fallback de UIColors si el modulo no existe

#### 2. agent_harness/memory.py (Memory Manager)
**Problema**: Race conditions en append_log() concurrente, scan lineal O(N) de todas las sesiones por cada lookup.
**Solucion**:
- Thread safety con threading.Lock por archivo de sesion
- Escritura atomica con .tmp + rename
- Indice invertido `target_index.json` para lookup O(1) de target_id a sesiones relevantes
- `rebuild_index()` para reconstruccion en caso de corrupcion

#### 3. agent_harness/skill_router.py (Skill Router)
**Problema**: Paths relativos al CWD que fallan si se ejecuta desde otro directorio.
**Solucion**: PROJECT_ROOT resuelto como `Path(__file__).resolve().parent.parent`, todos los paths absolutos.

#### 4. agent_harness/skill_executor.py (Skill Executor)
**Problema**: dry_run=True como default (footgun), sin metricas de uso de skills.
**Solucion**: dry_run=False como default, SkillMetricsCollector persistido en CSV con stats de invocaciones, tasa de exito y duracion promedio.

#### 5. agent_harness/self_healer.py (Self Healer)
**Problema**: PlanValidator import hard al inicio, errores desconocidos se perdian sin tracking.
**Solucion**: Lazy import de PlanValidator con graceful fallback, ErrorLearner que captura y sugiere entradas al catalogo de errores.

#### 6. agent_harness/mcp_client.py (MCP Client)
**Problema**: asyncio.run() falla si hay event loop corriendo (nested loop error).
**Solucion**: Deteccion de loop + threading fallback + soporte para nest_asyncio.

#### 7. agent_harness/types.py (Type Definitions)
**Nuevo**: BackgroundTaskInfo, TaskValidator Protocol, SkillMetrics dataclass con properties success_rate y avg_duration.

## Notas de Cambios v4.19.0 - Agent Ecosystem Integration

**Fecha:** 3 Abril 2026

### Resumen

Integracion del ecosistema de agentes (.agent/, .agents/workflows/) al flujo de desarrollo diario con validacion automatica pre-commit. DOMAIN_PRIMER.md deja de ser una isla de documentacion stale y ahora tiene ciclo de vida semi-automatico con regeneracion via Doctor CLI.

### Modulos de Documentacion Afectados

#### 1. DOMAIN_PRIMER.md (v4.0.0 -> v4.19.0)

**Problema**: El archivo llevaba 5 versiones y ~5 semanas desactualizado. Modulos como analytics, geo_enrichment, quality_gates, auditors no estaban documentados. Conteo de tests falso (decia 338, directorio vacio).

**Solucion**: Regeneracion completa con escaneo en vivo de 19 modulos, 138 archivos Python, 248 clases.

#### 2. CONTRIBUTING.md

**Cambio**: Agregado DOMAIN_PRIMER.md a tablas de actualizacion manual y seccion Regenerable. Nuevo Paso 5b para verificacion post-documentacion.

#### 3. procedures.md §4

**Cambio**: Renombrado "Modificar Decision Engine" -> "Modificar Financial Engine o agregar modulos nuevos". Eliminada referencia a script fantasma `generate_domain_primer.py`.

#### 4. scripts/validate_context_integrity.py

**Cambio**: Agregados 7 modulos nuevos al mapa de validacion: analytics, geo_enrichment, quality_gates, auditors, commercial_documents, delivery, providers. Removido modulo muerto decision_engine.

#### 5. scripts/doctor.py

**Nuevo flag**: `--regenerate-domain-primer` - escanea modulos en vivo y regenera DOMAIN_PRIMER.md automaticamente.

### Scripts Afectados

| Script | Cambio |
|--------|--------|
| `doctor.py` | Nuevo flag `--regenerate-domain-primer` |
| `log_phase_completion.py` | Nuevo flag `--check-domain-primer`, DOMAIN_PRIMER en MANUAL_DOCS |
| `validate_context_integrity.py` | Modulos nuevos en module_files map |

### Backwards Compatibility

Sin cambios breaking. Solo documentacion y nuevo flag en doctor.py.

---

## Notas de Cambios v4.12.0 - GA4 Integration

**Fecha:** 1 Abril 2026

### Resumen

Integracion de Google Analytics 4 como metodo #5 de medicion de trafico indirecto post-consulta IA. Implementacion completa con cliente real, consolidacion de modelos de datos, y wiring en pipeline de diagnostico.

### Modulos Principales

#### 1. GoogleAnalyticsClient

**Proposito**: Cliente para GA4 Data API que mide trafico indirecto (sesiones que sugieren consulta previa en IA).

**Ubicacion**: `modules/analytics/google_analytics_client.py`

**Caracteristicas**:
- Lazy initialization con caching
- Graceful fallback cuando GA4 no esta configurado
- Soporte para date_range: last_30_days, last_90_days
- Retorna estructura: sessions_indirect, sessions_direct, sessions_referral, top_sources, data_source, date_range, note

**Metodos principales**:
- `is_available()` - Verifica si GA4 esta configurado y disponible
- `get_indirect_traffic(date_range)` - Obtiene metricas de trafico indirecto

**Variables de entorno requeridas**:
- `GA4_PROPERTY_ID`: ID de propiedad GA4
- `GA4_CREDENTIALS_PATH`: Ruta al archivo JSON de service account

**Dependencia externa**: `google-analytics-data` (pip install)

#### 2. IndirectTrafficMetrics (Consolidado)

**Proposito**: Dataclass para almacenar metricas de trafico indirecto de GA4.

**Ubicacion**: `data_models/aeo_kpis.py` (linea 70)

**Campos**:
| Campo | Tipo | Default | Descripcion |
|-------|------|---------|-------------|
| sessions_indirect | int | 0 | Sesiones de trafico indirecto |
| sessions_direct | int | 0 | Sesiones de trafico directo |
| sessions_referral | int | 0 | Sesiones de trafico referral |
| data_source | str | N/A | Fuente de datos (GA4 o N/A) |
| top_sources | list | [] | Lista de fuentes principales |
| date_range | Optional[str] | None | Rango de fechas consultado |
| note | Optional[str] | None | Nota adicional o error |

**Metodos**:
- `to_dict()` - Serializa a diccionario
- `from_ga4_response(response)` - Factory method desde respuesta de GA4

#### 3. IA Readiness Calculator (GA4 Weight)

**Proposito**: Score compuesto IA-readiness con componente GA4.

**Ubicacion**: `modules/auditors/ia_readiness_calculator.py`

**Weights actualizados**:
| Componente | Peso |
|------------|------|
| schema_quality | 0.22 |
| crawler_access | 0.22 |
| citability | 0.23 |
| llms_txt | 0.09 |
| brand_signals | 0.14 |
| ga4_indirect | 0.10 |

**Redistribucion**: Cuando GA4 no disponible (ga4_indirect_score=None), el peso de 0.10 se redistribuye proporcionalmente entre los componentes disponibles.

#### 4. Diagnostic Generator (GA4 Wiring)

**Proposito**: Integracion de GA4 en calculo de score IAO.

**Ubicacion**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Flujo en `_calculate_score_ia()`**:
1. Intentar IATester (existente)
2. Intentar GA4 para trafico indirecto (opcional, non-blocking)
3. Si GA4 disponible: construir AEOKPIs con IATester + GA4 datos, calcular composite_score
4. Fallback: retornar score de IATester directamente

**Fix en `_calculate_iao_score()`**: Ahora tiene fallback explicito a `_calculate_schema_infra_score()` cuando IATester retorna None o -1.

### Arquitectura de Integracion

    AUDITORIA (V4ComprehensiveAuditor)
        |
        v
    _calculate_iao_score(audit_result, hotel_data)
        |
        +-- IATester.test_hotel(hotel_data)
        |       |
        |       v
        |   ia_score (0-100)
        |
        +-- GoogleAnalyticsClient.get_indirect_traffic()
        |       |
        |       v
        |   IndirectTrafficMetrics
        |
        +-- AEOKPIs(ia_visibility=ia_score, indirect_traffic=ga4_metrics)
                |
                v
            calculate_composite_score()
                |
                v
            score_ia (0-100)

### Backwards Compatibility

- GA4 es completamente opcional
- Todos los paths de GA4 estan envueltos en try/except
- Sin GA4: pipeline funciona con IATester + BingProxy solamente
- Sin GA4: IA readiness redistribuye peso proporcionalmente

---

## Notas de Cambios v4.18.0 - GA4 Multi-Hotel Architecture

**Fecha:** 2 Abril 2026
**FASE:** ANALYTICS-E2E-CERT-01

### Resumen

Evolucion de la integracion GA4 a arquitectura multi-hotel. El `property_id` se pasa por hotel via flag CLI en vez de variable global. Se implementa deteccion fallback automatica de `low_organic_visibility` en el mapper de pain-points. Certificacion E2E completada con 12/12 items PASADOS.

### Certificacion E2E

| Item | Estado |
|------|--------|
| 1-12 | PASADOS (12/12) |

**Resultado:** CERTIFICADO - Todos los escenarios verificados.

### GA4 Multi-Hotel: property_id por Hotel

El `property_id` ya no se lee desde `.env` como valor global. Ahora se pasa explicitamente por hotel mediante el flag CLI:

```
--ga4-property-id <PROPERTY_ID>
```

**Rationale:** Cada hotel tiene su propia propiedad GA4. Un valor global en `.env` limita la operacion a un solo hotel por ejecucion.

**Service account (global, compartido):**
```
config@dian-467401.iam.gserviceaccount.com
```

### Escenarios Probados

#### Escenario 1: Sin GA4
- Pipeline funciona normalmente con IATester + BingProxy
- Sin errores ni warnings de GA4
- IA readiness redistribuye peso proporcionalmente

#### Escenario 2: Con GA4 sin acceso
- Service account configurada pero sin permisos sobre la propiedad
- GoogleAnalyticsClient retorna metrics con `data_source=error`
- Pipeline continua sin interrupcion
- Warning logueado en output

#### Escenario 3: Con GA4 con acceso
- Service account con permisos otorgados
- Metricas reales de trafico indirecto obtenidas
- `data_source=GA4` en IndirectTrafficMetrics
- Composite score incluye componente ga4_indirect (peso 0.10)

### Archivos Modificados

#### 1. main.py
**Cambio:** Nuevo flag `--ga4-property-id` en CLI args.
- Se pasa como parametro al inicializar `GoogleAnalyticsClient`
- Valor por defecto: `None` (sin GA4)

#### 2. v4_diagnostic_generator.py
**Cambio:** 4 metodos actualizados para aceptar y propagar `property_id`.
- Metodos afectados reciben `ga4_property_id` como parametro
- `GoogleAnalyticsClient` se instancia con `property_id` explicito
- Flujo de GA4 completamente condicional al valor de `property_id`

#### 3. pain_solution_mapper.py
**Cambio:** Deteccion fallback automatica de `low_organic_visibility`.
- **FASE ANALYTICS-E2E-CERT-01:** Si el pain-point `low_organic_visibility` no se detecta por IA Tester, se evalua con fallback heuristico basado en metricas GA4 disponibles
- Integracion transparente: el mapper no requiere cambios en su API publica

### GoogleAnalyticsClient - Cambios de API

**Antes (v4.12.0):**
```python
client = GoogleAnalyticsClient()  # Lee GA4_PROPERTY_ID de .env
```

**Ahora (v4.18.0):**
```python
client = GoogleAnalyticsClient(property_id="123456789")  # Parametro explicito
```

El constructor ahora recibe `property_id` como parametro obligatorio (opcional con default `None`). Ya no lee de `.env`.

### Configuracion .env

```env
# GA4_PROPERTY_ID=123456789          # COMENTADO - ya no se usa globalmente
GA4_CREDENTIALS_PATH=/path/to/credentials.json  # ACTIVO - ruta global al JSON de service account
```

- `GA4_PROPERTY_ID`: **Comentado**. Reemplazado por `--ga4-property-id` en CLI.
- `GA4_CREDENTIALS_PATH`: **Activo**. La ruta al JSON de service account sigue siendo global (compartida entre hoteles).

### Dependencia

```
google-analytics-data  # Instalada como dependencia del proyecto
```

### Backwards Compatibility

- Sin `--ga4-property-id`: comportamiento identico a versiones sin GA4
- `.env` con `GA4_PROPERTY_ID` activo: sera ignorado por el nuevo constructor (warning en log)
- Todos los paths GA4 envueltos en try/except
- Pipeline funciona completamente offline sin GA4

---

## Notas de Cambios BRECHAS-DINAMICAS (v4.25.3)

### Problema
El pipeline mostraba máximo 4 brechas en el diagnóstico debido a hardcode en 3 capas:
1. **Templates**: 4 ranuras hardcodeadas (`${brecha_1_detalle}`, etc.)
2. **Generator**: `min(..., 4)` truncaba a 4 brechas
3. **Scorer**: Solo 7 tipos mapeados en SEVERITY/EFFORT/IMPACT_MAP

### Solución
- Templates: ranuras hardcode → `${brechas_section}` dinámica
- Generator: métodos `_build_brechas_section()` y `_build_brechas_resumen_section()` generan N secciones
- Scorer: 5 nuevos tipos mapeados (total: 12 tipos)
- Mapper: fix duplicate `low_ia_readiness`, fix `optimization_guide.promised_by`

### Módulos Afectados
| Módulo | Cambio | Fase |
|--------|--------|------|
| `v4_diagnostic_generator.py` | `_build_brechas_section()`, `_build_brechas_resumen_section()`, `_inject_brecha_scores()` truncation fix | A+B |
| `templates/diagnostico_v6_template.md` | `${brechas_section}` placeholder | A |
| `templates/diagnostico_v4_template.md` | `${brechas_section}` placeholder | A |
| `opportunity_scorer.py` | 5 nuevos tipos en maps | C |
| `pain_solution_mapper.py` | Duplicate fix | D |
| `asset_catalog.py` | `promised_by` fix | D |

### Backward Compatibility
- Diagnóstico con ≤4 brechas: formato idéntico al anterior
- Diagnóstico con >4 brechas: secciones adicionales, tabla resumen expandida
- Coherence score: unaffected (0.84 en validación E2E)
- Tests existentes: 0 regresiones
