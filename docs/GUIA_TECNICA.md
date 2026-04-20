# Guía Técnica - IA Hoteles Agent

**Versión:** v4.31.1
**Última actualización:** 2026-04-15
**Proyecto:** IA Hoteles Agent CLI

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

---

## Notas de Cambios

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
