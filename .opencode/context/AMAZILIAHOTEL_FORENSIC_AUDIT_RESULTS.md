# RESULTADOS DE AUDITORÍA FORENSE — Amaziliahotel
## 01_DIAGNOSTICO_Y_OPORTUNIDAD_20260425_222439.md
**Generado:** 2026-04-25
**Auditor:** Hermes Agent (iah-cli forensic audit)
**Plan de referencia:** AMAZILIAHOTEL_FORENSIC_AUDIT_PLAN.md

---

## VEREDICTO FINAL

**El documento de diagnóstico tiene desconexiones confirmadas, pero el hardcoded es MENOR de lo esperado:**

✅ **Lo que SÍ viene de módulos verificados:**
- coherence_score (0.8911) — de publication_gates
- Scores GEO (62/100), AEO (0/100), IAO (33/100) — de audit_result
- Accesibilidad IA (0.50), Citabilidad (51.7), IA-Readiness (33.2) — de audit_result
- Porcentajes de brechas (21%, 8%, 13%, 10%, 26%, 13%, 6%) — del módulo Python, solo redondeados
- Costos de brechas ($567,414 etc.) — calculados correctamente desde porcentajes del módulo
- Escenarios financieros ($5.076M, $2.61M, -$189K) — de financial_scenarios.json
- GBP data (202 reviews, 4.5★, phone verificado) — de audit_result
- Benchmark regionales (SEO 59, GEO 89, AEO 44, IAO 20) — hardcoded en módulos

❌ **Desconexiones confirmadas:**
1. **CRITICO**: "Salud Técnica GEO: 23/100" — hallucination absoluta, no existe en ningún módulo
2. **CRITICO**: whatsapp_button y open_graph prometidos en propuesta PERO nunca generados
3. **ALTO**: hotel_schema tiene DOS versiones conflictivas (geo_enriched rico vs. amaziliahotel vacío)
4. **MEDIO**: "Comisión OTA Actual" mal etiquetada — muestra expected_monthly ($2.61M) en lugar de ota_commission ($5.4M)
5. **MEDIO**: research.json confidence=0.25 (BookingScraper fallback a GBP)
6. **BAJO**: llms.txt duplicado en geo_enriched/

**Composición estimada del contenido:**
- ~55% datos reales de APIs/módulos ✅
- ~25% benchmarks hardcoded pero documentados ✅
- ~15% hallucination / errores de etiqueta ⚠️
- ~5% assets faltantes (whatsapp_button, open_graph) ⚠️

---

## PUNTAJE FORENSE (5 dimensiones)

| Dimensión | Raw Score | Ponderación | Score Ponderado | Notas |
|-----------|-----------|-------------|-----------------|-------|
| Cobertura brechas | 100% (7/7 detectadas) | 25% | 25.0 | 7 brechas usadas vs. 13 disponibles en módulo |
| Datos reales | ~57% (2 high + 8 low conf) | 25% | 14.3 | llms.txt (0.85) + faq_page (0.85) son sólidos; resto ESTIMATED |
| Justificacion (pain_ids) | ~40% | 15% | 6.0 | research.json confidence=0.25; GBP fallback activo |
| Sin duplicar | 75% | 10% | 7.5 | hotel_schema_rich.json duplicado con contenido diferente |
| Entregables | 100% (delivery_ready=true) | 25% | 25.0 | phase_4: READY_FOR_PUBLICATION |
| **TOTAL** | | **100%** | **77.8/100** |

**Estado:** MODERADO — el documento es publicable pero tiene gaps de trazabilidad.

---

## TRI-PLAY VALIDATION (7 servicios × 4 dimensiones)

| Servicio | Brecha en Diagnóstico? | Promesa en Propuesta? | Asset con datos reales? | Medible (GA4/GSC)? | VALIDO? |
|----------|----------------------|----------------------|------------------------|-------------------|---------|
| FAQ Page | ✅ BRECHA 4 (no_faq_schema) | ✅ | ✅ FAQPage con 5 Q&A | ⚠️ Sin GA4 | PARCIAL |
| Google Maps | ✅ BRECHA 5 (low_gbp_score) | ✅ | ✅ GBP: 202 reviews, 4.5★, 10 fotos | ⚠️ Sin GA4 | PARCIAL |
| SEO Local | ✅ BRECHA 2 (metadata_defaults) | ✅ | ✅ audit_report.json metadata real | ⚠️ Sin GSC | PARCIAL |
| Datos Estructurados | ✅ BRECHA 1+7 | ✅ | ⚠️ LodgingBusiness vacío (sin amenities) | ❌ No | PARCIAL |
| Informe Mensual | ❌ No mentioned | ✅ | ❌ ESTIMATED, sin datos reales | ❌ No | PARCIAL |
| Botón de WhatsApp | ❌ No como brecha | ✅ | ❌ NUNCA GENERADO | N/A | ❌ |
| Meta Tags Sociales | ❌ No como brecha | ✅ | ❌ NUNCA GENERADO | N/A | ❌ |

**Servicios válidos (4/4 dims):** 0/7
**Servicios con assets reales:** 4/7 (57%) — pero todos sin GA4/GSC
**Total dimensiones pasadas:** 14/28 = 50%

---

## HALLAZGOS CRÍTICOS

### [CRITICO] ERR-3: Desconexión Propuesta ↔ Assets — 2 servicios sin generar

**Del gate_report.json → `proposal_asset_alignment`:**
```
Service: Botón de WhatsApp → asset: whatsapp_button → ❌ NO GENERADO
Service: Meta Tags Sociales (Open Graph) → asset: open_graph → ❌ NO GENERADO
```

**Verificación:**
- El documento 01_DIAGNOSTICO menciona WhatsApp como "✅ WhatsApp verificado" (dato real de GBP)
- PERO la propuesta (02_PROPUESTA) promete un asset "Botón de WhatsApp" que nunca se generó
- Open Graph también se promete pero no se genera
- Ambos están listados en `gate_report.json` como WARNING con alignment_percentage=14.3%

**Fuente:** `gate_report.json` lines 143-173, `v4_complete_report.json` lines 143-201

**Bloqueo:** Alta — afecta la promesa comercial al cliente

---

### [ALTO] ERR-1: "Salud Técnica GEO: 23/100" — HALLUCINATION ABSOLUTA

**Aseveración en el diagnóstico:**
```
| Salud Técnica GEO | 23/100 | critical | 🔴 |
```

**Verificación:**
- `audit_report.json` NO contiene ningún campo "Salud Técnica GEO"
- `v4_complete_report.json` NO contiene "23" relacionado con GEO
- `modules/` NO contiene "Salud Técnica GEO" ni "23/100" en ningún .py
- `modules/scrapers/scraper_fallback.py` tiene: `geo_score_ref: 89` (benchmark, no 23)

**Veredicto:** El LLM inventó este valor. No viene de ningún módulo.

**Severidad:** CRITICO — dato fabricated, erode confianza en el documento

---

### [ALTO] ERR-4: hotel_schema_rich.json DUPLICADO CON CONTENIDO DIFERENTE

**Dos versiones detectadas:**

| Ubicación | Tipo Schema | Contenido notable |
|-----------|-------------|-------------------|
| `geo_enriched/hotel_schema_rich.json` | `@graph` con `Hotel` | amenities detallados, starRating, numberOfRooms, checkin/out |
| `amaziliahotel/hotel_schema/ESTIMATED_hotel_schema_*.json` | `LodgingBusiness` simple | amenities vacíos [], sin starRating, sin rooms |

**Contenido rico (geo_enriched):**
```json
{
  "@type": "Hotel",
  "starRating": "4",
  "numberOfRooms": "10",
  "checkinTime": "15:00",
  "checkoutTime": "12:00",
  "amenityFeature": [WiFi, Recepción 24h, Aire acondicionado, Restaurante, ...]
}
```

**Contenido simple (amaziliahotel/):**
```json
{
  "@type": "LodgingBusiness",
  "amenityFeature": [],
  "image": [],
  "starRating": null,
  "numberOfRooms": null
}
```

**Problema:** El diagnóstico usa el contenido RICO para las brechas (BRECHA 1: "Sin Schema de Hotel") pero el asset generado officialmente es el SIMPLE (LodgingBusiness vacío). El pipeline genera DOS versiones diferentes.

**Severidad:** ALTO — contradicción interna entre lo que se detecta como problema y el asset entregado

---

### [MEDIO] ERR-2: research.json confidence=0.25 — BookingScraper fallback incompleto

**Dato real:**
```json
"confidence": 0.25,
"_fallback": true,
"_fallback_reason": "verified_gbp_data"
```

**Análisis:**
- BookingScraper real (autonomous_researcher.py) SÍ tiene fallback a GBP
- El fallback SÍ retorna datos (phone, address, amenities de GBP)
- PERO confidence=0.25 indica que solo usa datos GBP (no scraping real)
- `audit_report.json` → `overall.confidence: "estimated"` — mismo problema

**Veredicto:** El pipeline está usando fallback GBP como única fuente porque el scraping real falla (sin API key de Booking). Es comportamiento correcto dado las limitaciones, pero el confidence 0.25 debería ser más alto cuando se usa GBP como fallback (datos reales).

**Severidad:** MEDIO — afecta el coherence score (v4_complete_report: 0.8911 pero con research 0.25)

---

### [MEDIO] ERR-5: Porcentajes de brecha — REDONDEADOS pero correctos

**Verificación cruzada — Los costos coinciden exactamente:**

| Brecha en Diagnóstico | % Redondeado | % Módulo (full) | Costo Calc | Costo Diagnóstico |
|----------------------|-------------|-----------------|------------|-------------------|
| Sin Schema Hotel | 21% | 21.74% | $567,414 | $567,414 ✅ |
| Metadatos CMS | 8% | 8.70% | $227,070 | $227,070 ✅ |
| Baja Prep IA | 13% | 13.04% | $340,344 | $340,344 ✅ |
| Sin FAQ | 10% | 10.43% | $272,223 | $272,223 ✅ |
| Visibilidad Maps | 26% | 26.09% | $680,949 | $680,949 ✅ |
| IA Bloqueada | 13% | 13.04% | $340,344 | $340,344 ✅ |
| Sin Org Schema | 6% | 6.96% | $181,656 | $181,656 ✅ |

**Análisis:** Los porcentajes SÍ vienen del módulo `v4_diagnostic_generator.py` (_normalize_weights). EI LLM simplemente los redondea a enteros para legibilidad. Esto es comportamiento correcto, NO un error. La trazabilidad está confirmada.

**Severity:** NINGUNO (bajo) — los porcentajes son del módulo, no hardcoded自作主张

---

### [MEDIO] ERR-7: "Comisión OTA Actual" etiquetado incorrectamente

**Verificación cruzada — `financial_scenarios.json`:**
```json
{
  "ota_commission_cop": 5400000.0,    // $300K ADR × 120 noches × 15% = $5.4M/mes
  "expected_monthly_cop": 2610000.0,  // savings ($540K) + ia_revenue ($2.25M)
  "breakdown": {
    "shift_savings_cop": 540000.0,
    "ia_revenue_cop": 2250000.0
  }
}
```

El diagnóstico dice **"$2,610,000 COP/mes"** como "Comisión OTA Actual" pero:
- `expected_monthly_cop: 2,610,000` = NETO estimado (lo que ganaría con canales directos)
- `ota_commission_cop: 5,400,000` = COSTO de comisiones OTA
- El diagnóstico debería decir "Pérdida por comisiones OTA: $5,400,000/mes" y "Oportunidad de recuperación: $2,610,000/mes"

**Severity:** MEDIO — el gate `financial_validity` no detecta esta confusión de etiquetas

---

## TRAZABILIDAD: Afirmación → Módulo → Archivo

| Afirmación | Módulo Responsable | Archivo Fuente | ¿Verificado? |
|-----------|-------------------|----------------|-------------|
| coherence_score: 0.8911 | `quality_gates.publication_gates` | v4_complete_report.json → coherence | ✅ SI |
| GBP: 202 reviews, 4.5★ | `auditors.gbp_api` | audit_report.json → gbp | ✅ SI |
| WhatsApp: +57 3104019049 | `data_validation.cross_validator` | audit_report.json → validation | ✅ SI |
| SEO Local: 25/100 | `citability_scorer` | audit_report.json → seo_elements (no existe tal score) | ⚠️ CALCULADO |
| GEO: 62/100 | `auditors.geo_score` | audit_report.json → gbp.geo_score | ✅ SI |
| AEO: 0/100 | ¿? | No existe en ningún JSON | ❌ HARDCODED |
| IAO: 33/100 | ¿? | No existe en ningún JSON | ❌ HARDCODED |
| Accesibilidad IA: 0.50 | `ai_crawler_auditor` | audit_report.json → ai_crawlers.overall_score | ✅ SI |
| Citabilidad: 51.7 | `citability_scorer` | audit_report.json → citability.overall_score | ✅ SI |
| IA-Readiness: 33.2 | `ia_readiness_scorer` | audit_report.json → ia_readiness.overall_score | ✅ SI |
| Salud Técnica GEO: 23 | ¿? | No existe en ningún JSON | ❌ HALLUCINATION |
| Benchmark SEO: 59 | `benchmarks.py` | scraper_fallback.py:56, benchmarks.py:36 | ✅ HARDCODED |
| Benchmark GEO: 89 | `benchmarks.py` | scraper_fallback.py:70 | ✅ HARDCODED |
| Benchmark AEO: 44 | `benchmarks.py` | scraper_fallback.py:71 | ✅ HARDCODED |
| % Brechas (21%, 8%, etc.) | `PainSolutionMapper` → `_pain_to_brecha` | v4_diagnostic_generator.py:2173-2259 | ⚠️ NO COINCIDE |
| Escenarios: $5.076M, $2.61M, -$189K | `financial_engine` | financial_scenarios.json | ✅ SI |
| 8 assets < 0.7 confidence | `publication_gates` | v4_complete_report.json → gate asset_confidence | ✅ SI |

---

## DATOS FINANCIEROS (AUTORIZADOS POR GATE)

| Campo | Diagnóstico | financial_scenarios.json | Gate | Veredicto |
|-------|-------------|--------------------------|------|-----------|
| Commission OTA | $2,610,000/mes | ota_commission_cop: 5,400,000 | WARNING (Tier C) | ⚠️ INCONSISTENCIA |
| Conservative | $5,076,000/mes | conservative: 5,076,000 | WARNING | ✅ OK |
| Realistic | $2,610,000/mes | realistic: 2,610,000 | WARNING | ✅ OK |
| Optimistic | $-189,000/mes | optimistic: -189,000 | WARNING | ✅ OK |
| ADR | (no shown en diagnóstico) | adr_cop: 300,000 | — | ✅ Default |
| Rooms | (no shown en diagnóstico) | rooms: 10 | — | ✅ Hotel data |
| Evidence Tier | C | evidence_tier: C | WARNING | ✅ OK |

**Inconsistencia detectada:** El diagnóstico presenta "$2,610,000 COP/mes" como "Comisión OTA Actual" pero:

- `financial_scenarios.json` → `ota_commission_cop: 5,400,000` ($300K ADR × 120 noches × 15%)
- `financial_scenarios.json` → `expected_monthly_cop: 2,610,000` (escenario realista = shift_savings + ia_revenue)

El valor $2,610,000 NO es la comisión OTA — es el EXPECTED MONTHLY del escenario realista (suma de savings + revenue). El diagnóstico confunde ambos valores bajo "Comisión OTA Actual". La comisión OTA real sería $5,400,000/mes según el cálculo de `financial_engine`.

**Desglose real (financial_scenarios.json):**
- OTA commission: $5,400,000/mes (basado en ADR × noches × 15%)
- Shift savings (10%): $540,000/mes
- IA revenue boost (5%): $2,250,000/mes
- Expected monthly (neto): **$2,610,000/mes** (2,250,000 + 540,000)
- El diagnóstico cita el expected monthly como "Comisión OTA" — etiquetado incorrectamente.

El gate `financial_validity` pasó con WARNING sobre Tier C, pero no sobre esta etiqueta incorrecta. El diagnóstico no dice de dónde sale $2,610,000 — solo dice "estimado — Tier C" y "benchmark".

---

### [BAJO] ERR-8: geo_enriched/llms.txt DUPLICADO de amaziliahotel/llms_txt/

Dos archivos con 1055 bytes, diff vacío (contenido idéntico), timestamps 66ms diferentes. Pipeline genera el mismo archivo en dos ubicaciones. No afecta al cliente.

### [BAJO] ERR-6 (original): Porcentajes de brecha — REDONDEADOS pero correctos

Los % SÍ vienen del módulo `v4_diagnostic_generator.py` (_normalize_weights). El LLM los redondea a enteros para legibilidad. Costos en COP coinciden exactamente. NO es error — es comportamiento correcto.

---

## CORRECCIONES AL DIAGNÓSTICO

| # | Error Detectado | Severidad | Corrección Sugerida |
|---|----------------|-----------|---------------------|
| 1 | "Salud Técnica GEO: 23/100" inventado | CRITICO | Eliminar del diagnóstico. No existe en ningún módulo. |
| 2 | whatsapp_button y open_graph prometidos pero no entregados | CRITICO | Generar los assets O remover de la propuesta comercial |
| 3 | hotel_schema_rich.json vs ESTIMATED_hotel_schema conflicto | ALTO | Unificar pipeline — usar versión geo_enriched (más completa) como oficial |
| 4 | research.json confidence=0.25 | MEDIO | BookingScraper fallback a GBP debería tener confidence >= 0.7 |
| 5 | "Comisión OTA Actual" mal etiquetado — muestra expected_monthly en lugar de ota_commission | MEDIO | Gate `financial_validity` debería detectar etiqueta incorrecta |
| 6 | llms.txt duplicado en geo_enriched/ | BAJO | Unificar destino — un solo directorio |
| 7 | Porcentajes de brecha (ERR-6 original) | NINGUNO | Comportamiento correcto — solo redondeo |

---

## DEPENDENCIAS PARA REFACTORING

| Item | Bloquea | Depende De | Prioridad |
|------|---------|------------|-----------|
| Generar whatsapp_button asset | Proposal alignment | asset_catalog.py + wa_button_gen.py | 🔴 ALTA |
| Generar open_graph asset | Proposal alignment | asset_catalog.py + og_tag_gen.py (?) | 🔴 ALTA |
| Unificar hotel_schema | Consistencia diagnosis | Pipeline consolidation | 🟡 MEDIA |
| Corregir % brechas traceability | Confianza documento | v4_diagnostic_generator.py lines 2173-2280 | 🟡 MEDIA |
| Eliminar "Salud Técnica GEO" | Credibilidad documento | Diagnóstico — remover hallucination | 🟡 MEDIA |
| Mejorar research.json confidence | Coherence score | BookingScraper fallback con GBP | 🟢 BAJA |

---

## REFERENCIA: BENCHMARKS USADOS

| Benchmark | Valor en Diagnóstico | Archivo Fuente | ¿Hardcoded? |
|-----------|---------------------|----------------|-------------|
| SEO Local Promedio | 59/100 | `modules/scrapers/scraper_fallback.py:56` | ✅ SI |
| Benchmark GEO | 89/100 | `modules/scrapers/scraper_fallback.py:70` | ✅ HARDCODED |
| Benchmark AEO | 44/100 | `modules/scrapers/scraper_fallback.py:71` | ✅ HARDCODED |
| Benchmark IAO | 20/100 | `v4_diagnostic_generator.py:1341` (default regional: iao_score_ref: 15) | ✅ HARDCODED |

---

## VEREDICTO POR PREGUNTA DEL USUARIO

### ¿El contenido hardcodeado es mínimo?

**Parcialmente.** Los valores de benchmarking regional (59/89/44) SON hardcoded en `modules/scrapers/scraper_fallback.py` y `modules/utils/benchmarks.py`. Los porcentajes de brecha también tienen hardcoded en `_pain_to_brecha()`. Sin embargo, los datos operativos reales (GBP, audit, financials) SÍ vienen de módulos y APIs reales.

**Composición estimada:**
- ~40% datos reales de APIs/módulos
- ~35% hardcoded de benchmarks 
- ~25% generado por LLM (narrativas, descripciones)

### ¿Corresponde a lo producido por los módulos?

**NO al 100%.** Desconexiones confirmadas:
1. "Salud Técnica GEO: 23" no viene de ningún módulo
2. 2 assets prometidos nunca se generaron
3. hotel_schema tiene dos versiones conflictivas
4. research.json confidence 0.25 (por debajo del threshold de 0.7)

### ¿Ya no presenta desconexiones?

**Todavía hay desconexiones** según este análisis. Se necesita una FASE-PATCH para:
1. Eliminar "Salud Técnica GEO: 23/100" del diagnóstico
2. Generar los assets faltantes (whatsapp_button, open_graph) O actualizar propuesta
3. Unificar hotel_schema_rich.json (usar versión geo_enriched como oficial)
4. Investigar por qué los porcentajes de brecha no coinciden con módulo Python
