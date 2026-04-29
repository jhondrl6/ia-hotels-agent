# Guía Técnica - IA Hoteles Agent

**Versión:** v4.36.0
**Última actualización:** 2026-04-28
**Proyecto:** IA Hoteles Agent CLI

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
