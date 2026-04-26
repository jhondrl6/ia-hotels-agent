# PLAN DE AUDITORÍA FORENSE
## 01_DIAGNOSTICO_Y_OPORTUNIDAD — Amaziliahotel
**Timestamp generación:** 2026-04-25 22:24:39
**Propósito:** Verificar si el contenido del documento de diagnóstico corresponde efectivamente a lo producido por los módulos, y si el contenido hardcodeado es mínimo.

---

## PRE-FLIGHT: Validaciones Previas al Análisis

### [PF-1] VerificarDualBookingScraper
Hay DOS `BookingScraper` classes en el codebase:
- `modules/scrapers/booking_scraper.py` — LEGACY STUB (no usado por v4complete)
- `modules/providers/autonomous_researcher.py` — REAL con httpx + fallback GBP (USA-DO por v4complete)

```bash
grep -n "BookingScraper" /mnt/c/Users/Jhond/Github/iah-cli/tests/scrapers/test_booking_scraper.py | head -5
```
**Verificar:** El test importa desde `autonomous_researcher`. Si es así, el scraper real está activo.

### [PF-2] Tests Suite Verde
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && python -m pytest tests/ -x -q --tb=short 2>&1 | tail -20
```
**Verificar:** 0 regresiones antes de confiar en resultados del pipeline.

### [PF-3] Consistencia de Timestamps
Verificar que todos los archivos del directorio `amaziliahotel/` correspondan a la misma ejecución (2026-04-25 22:XX).
```bash
ls -la /mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/amaziliahotel/*/
```

---

## MATRIZ DE VERIFICACIÓN: Afirmaciones del Diagnóstico vs. Datos Reales

### A. DATOS DEL FRONT matter (YAML header)

| # | Afirmación en Diagnóstico | Archivo de Fuente | Valor Esperado | Verificado? |
|---|--------------------------|-------------------|-----------------|-------------|
| A1 | `coherence_score: 0.8911` | `v4_complete_report.json` → `coherence_score` | 0.8911111111111112 | ❓ |
| A2 | `financial_evidence_tier: "C"` | `financial_scenarios.json` → `breakdown.evidence_tier` | "C" | ❓ |
| A3 | `financial_value_central: 2610000` | `financial_scenarios.json` → `expected_monthly_cop` | 2610000.0 | ❓ |
| A4 | `financial_value_range: [2088000, 3132000]` | Calculado: 2610000 × 0.8, × 1.2 | [2088000, 3132000] | ❓ |
| A5 | `financial_method: "proportional_normalized"` | `financial_scenarios.json` → ? | ¿Existe este campo? | ❓ |

**Archivos a leer:**
- `v4_complete_report.json` (line 1-320)
- `financial_scenarios.json` (ya leído — line 1-44)

### B. SCORES DE VISIBILIDAD DIGITAL (Sección "Score de Visibilidad Digital")

| # | Afirmación en Diagnóstico | Fuente de Datos | Valor Esperado | Verificado? |
|---|--------------------------|-----------------|-----------------|-------------|
| B1 | SEO Local: 25/100 | ¿De dónde sale? | — | ❓ |
| B2 | GEO: 62/100 | `audit_report.json` → `gbp.geo_score` | 62 | ❓ |
| B3 | AEO: 0/100 | ¿De dónde sale? | — | ❓ |
| B4 | IAO: 33/100 | ¿De dónde sale? | — | ❓ |
| B5 | Promedio SEO: 59/100 | Benchmark regional | — | ❓ |
| B6 | Promedio GEO: 89/100 | Benchmark regional | — | ❓ |
| B7 | Promedio AEO: 44/100 | Benchmark regional | — | ❓ |

**Verificación:** Los scores (B1, B3, B4) que NO aparecen en `audit_report.json` ni en `v4_complete_report.json` son **hardcoded benchmarks** — verificar si están en algún módulo.

### C. MÉTRICAS DE ACCESO PARA IA (Nueva Sección [NEW])

| # | Métrica | Diagnóstico | Fuente Real | Verificado? |
|---|---------|-------------|-------------|-------------|
| C1 | Accesibilidad IA | 0.50/1.00, 14 bloqueados | `audit_report.json` → `ai_crawlers.overall_score=0.5` | ❓ |
| C2 | Citabilidad | 51.7/100, 3 bloques | `audit_report.json` → `citability.overall_score=51.67` | ❓ |
| C3 | IA-Readiness | 33.2/100 | `audit_report.json` → `ia_readiness.overall_score=33.2045` | ❓ |
| C4 | Salud Técnica GEO | 23/100 | No aparece en audit_report.json | ❓ |

**Investigación:** `Salud Técnica GEO: 23/100` NO está en `audit_report.json`. Buscar en `geo_enriched/sync_report.md` u otro archivo.

### D. GBP Y DATOS VERIFICADOS (Sección "Lo que ya funciona")

| # | Afirmación | Fuente | Valor Real | Verificado? |
|---|-----------|--------|------------|-------------|
| D1 | WhatsApp: +57 3104019049 | `audit_report.json` → `validation.phone_web` | "+57 3104019049" | ❓ |
| D2 | GBP: 202 reviews, 4.5/5 | `audit_report.json` → `gbp` | reviews:202, rating:4.5 | ❓ |
| D3 | Redes sociales: Facebook, Instagram, YouTube | `audit_report.json` → `seo_elements.social_links_found` | 3 links | ❓ |

### E. BRECHAS Y COSTOS (Sección "Trazabilidad: Brechas Identificadas")

| # | Brecha | Costo/月 en Diagnóstico | Cálculo | Verificado? |
|---|--------|------------------------|---------|-------------|
| E1 | BRECHA 1: Sin Schema Hotel | $567,414 | 21% × $2,610,000 | ❓ |
| E2 | BRECHA 2: Metadatos CMS | $227,070 | 8% × $2,610,000 | ❓ |
| E3 | BRECHA 3: Baja Prep IA | $340,344 | 13% × $2,610,000 | ❓ |
| E4 | BRECHA 4: Sin FAQ | $272,223 | 10% × $2,610,000 | ❓ |
| E5 | BRECHA 5: Maps sub-óptimo | $680,949 | 26% × $2,610,000 | ❓ |
| E6 | BRECHA 6: IA Bloqueada | $340,344 | 13% × $2,610,000 | ❓ |
| E7 | BRECHA 7: Sin Org Schema | $181,656 | 6% × $2,610,000 | ❓ |

**Verificación:** Los porcentajes (21%, 8%, 13%, 10%, 26%, 13%, 6%) deben salir del módulo `opportunity_scorer.py`. Si están hardcoded en el prompt del LLM, es un problema.

### F. ESCENARIOS FINANCIEROS (Sección "Escenarios de Recuperación")

| # | Escenario | Valor en Diagnóstico | Valor en financial_scenarios.json | Verificado? |
|---|-----------|---------------------|-----------------------------------|-------------|
| F1 | Conservador | $5,076,000/mes | 5,076,000.0 | ❓ |
| F2 | Realista | $2,610,000/mes | 2,610,000.0 | ❓ |
| F3 | Optimista | $-189,000/mes | -189,000.0 | ❓ |

### G. ASSETS GENERADOS — TRAZABILIDAD

| # | Asset | Archivo Generado | Coherence en Diagnóstico | Gate Report | Verificado? |
|---|-------|-----------------|--------------------------|-------------|-------------|
| G1 | hotel_schema | `ESTIMATED_hotel_schema_*.json` | Mencionado en BRECHA 1 | WARNING | ❓ |
| G2 | llms_txt | `ESTIMATED_llms_*.txt` | Coherence Score | PASSED (0.85) | ❓ |
| G3 | faq_page | `ESTIMATED_faqs_*.json` | BRECHA 4 | PASSED (0.85) | ❓ |
| G4 | geo_playbook | `ESTIMATED_geo_playbook_*.md` | BRECHA 5 | WARNING | ❓ |
| G5 | org_schema | `ESTIMATED_org_schema_*.json` | BRECHA 7 | WARNING | ❓ |
| G6 | optimization_guide | `ESTIMATED_guia_*.md` | BRECHA 2, 3 | WARNING | ❓ |
| G7 | analytics_setup_guide | `ESTIMATED_guia_configuracion_ga4_*.md` | No mentioned explicitly | WARNING | ❓ |
| G8 | review_plan | `ESTIMATED_plan_reviews_*.md` | No mentioned explicitly | WARNING | ❓ |
| G9 | indirect_traffic_optimization | `ESTIMATED_optimizacion_trafico_*.md` | BRECHA 6 | WARNING | ❓ |
| G10 | monthly_report | `ESTIMATED_informe_mensual_*.md` | No mentioned explicitly | WARNING | ❓ |

### H. ASSETS DUPLICADOS EN geo_enriched/ vs. raíz amaziliahotel/

| # | Archivo | geo_enriched/ | amaziliahotel/ | ¿Idéntico? |
|---|---------|--------------|----------------|------------|
| H1 | llms.txt | 1055 bytes | 1055 bytes | ❌ (diff arriba: son IGUALES) |
| H2 | hotel_schema_rich.json | richer (@graph, Hotel) | simpler (LodgingBusiness) | ❌ Diferentes |
| H3 | faq_schema.json | 1745 bytes | ¿existe en faq_page/? | ❓ |

**Investigación especial:** Los archivos en `geo_enriched/` tienen timestamps 22:11 (más antiguos) mientras los `ESTIMATED_` tienen 22:24. Son de ejecuciones distintas. ¿Cuál es la versión oficial?

### I. SERVICES PROMETIDAS EN 02_PROPUESTA vs. ASSETS REALES

**Del gate_report.json → `proposal_asset_alignment`:**

| Service | Asset Prometido | ¿Generado? | Archivo |
|---------|----------------|-----------|---------|
| Página de FAQ | faq_page | ✅ | ESTIMATED_faqs_*.json |
| Google Maps Optimizado | geo_playbook | ✅ | ESTIMATED_geo_playbook_*.md |
| SEO Local | optimization_guide | ✅ | ESTIMATED_guia_optimizacion_*.md |
| Datos Estructurados | hotel_schema | ✅ | ESTIMATED_hotel_schema_*.json |
| Informe Mensual | monthly_report | ✅ | ESTIMATED_informe_mensual_*.md |
| Botón de WhatsApp | whatsapp_button | ❌ FALTANTE | — |
| Meta Tags Sociales (Open Graph) | open_graph | ❌ FALTANTE | — |

**Issue crítico:** 2 servicios prometidos NO tienen assets generados. Esto es una desconexión.

### J. WHATSAPP VERIFICADO

El diagnóstico dice "✅ WhatsApp verificado — Canal directo funcional (+57 3104019049)".
- `audit_report.json` → `validation.whatsapp_status: "verified"`
- `audit_report.json` → `phone_web: "+57 3104019049"` y `phone_gbp: "310 4019049"`
- ✅ COHERENTE.

---

## CÁLCULO DE SCORES FORENSES

### J.1 Forensic Score (5 dimensiones, pesos: 25/25/15/10/25)

| Dimensión | Cálculo | Score |
|-----------|---------|-------|
| Cobertura brechas | 7 brechas con gap_id / 7 brechas = 100% | 100% × 0.25 = 25 |
| Datos reales | GBP phone ✅, rating ✅, reviews ✅, address ✅ / assets 10 con confidence 0.5 (8) + 0.85 (2) = mix | ~70% × 0.25 = 17.5 |
| Justificacion (pain_ids) | research.json confidence=0.25 (muy bajo) | 25% × 0.15 = 3.75 |
| Sin duplicar | geo_enriched vs amaziliahotel/ = 2 versiones de llms.txt (idénticas) + hotel_schema (diferentes) | ~80% × 0.10 = 8 |
| Entregables | delivery_ready: true (v4_complete_report) | 100% × 0.25 = 25 |
| **TOTAL** | | **~79.25/100** |

### J.2 Tri-Play Score (4 dimensions × 7 servicios)

| Service | Brecha en Diagnóstico? | Servicio en Propuesta? | Asset con datos reales? | Promesa medible? |
|---------|----------------------|----------------------|----------------------|-----------------|
| FAQ Page | ✅ BRECHA 4 | ✅ | ✅ (FAQPage con 5 Q&A) | ⚠️ Sin GA4 |
| Google Maps | ✅ BRECHA 5 | ✅ | ✅ (GBP real: 202 reviews, 4.5★) | ⚠️ Sin GA4 |
| SEO Local | ✅ BRECHA 2 | ✅ | ✅ (metadata audit real) | ⚠️ Sin GSC |
| Datos Estructurados | ✅ BRECHA 1, 7 | ✅ | ⚠️ hotel_schema: LodgingBusiness vacío, sin amenities | ❌ No medible sin crawl |
| Informe Mensual | ❌ No mencionada | ✅ | ❌ (monthly_report con ESTIMATED) | ❌ Sin GA4 |
| WhatsApp Button | ❌ No-mentioned-as-brecha | ✅ | ❌ Asset no generado | N/A |
| Open Graph | ❌ No-mentioned-as-brecha | ✅ | ❌ Asset no generado | N/A |

**Services válidos (todos 4 dims):** 3/7 = 43%
**Dimensiones pasadas:** ~15/28 = 54%

---

## ERRORES DETECTADOS EN EL DIAGNÓSTICO (Preliminar)

| # | Error | Tipo | Severidad |
|---|-------|------|-----------|
| ERR-1 | "Salud Técnica GEO: 23/100" no existe en `audit_report.json` ni `v4_complete_report.json` — posible hallucination o hardcode | HALLUCINATION/HARDCODED | ALTO |
| ERR-2 | `research.json` confidence=0.25 (BookingScraper fallback a GBP) — scraper real activo según PF-1, pero research no usa el fallback correctamente | DATA GAP | MEDIO |
| ERR-3 | 2 servicios prometidos en proposal_asset_alignment NO tienen assets (whatsapp_button, open_graph) — desconexión Diagnóstico ↔ Assets | DESCONEXION | CRITICO |
| ERR-4 | `geo_enriched/` y `amaziliahotel/` tienen VERSIONES DIFERENTES de hotel_schema_rich.json — ¿Cuál es la oficial? | DUPLICACION CONFLICTIVA | ALTO |
| ERR-5 | "Por que importa: 21%" en BRECHA 1 es hardcoded en prompt (no viene de módulo) — el % no tiene fuente de módulo | HARDCODED | MEDIO |
| ERR-6 | `financial_value_range: [2088000, 3132000]` — el rango no existe en `financial_scenarios.json`, es calculado en el documento | HARDCODED CALC | BAJO |
| ERR-7 | Benchmark promedios (SEO 59, GEO 89, AEO 44) — no verificables, benchmarks de dominio público | HARDCODED | BAJO |

---

## DEPENDENCIAS Y BLOQUEOS

| Item | ¿Bloquea? | Depende de |
|------|-----------|------------|
| ERR-3 (missing whatsapp_button, open_graph) | Alta prioridad | modules/asset_generation/asset_catalog.py — ¿están declarados? |
| ERR-4 (versiones conflicto hotel_schema) | SEO real | Pipeline de geo_enriched vs asset_generation |
| ERR-2 (research confidence 0.25) | Afecta coherence score | BookingScraper fallback — ¿se usa GBP como fallback? |

---

## PRÓXIMOS PASOS (Basados en Hallazgos)

1. **Si ERR-3 (missing assets) es confirmed:** Verificar si `whatsapp_button` y `open_graph` están en `asset_catalog.py`. Si no existen, el pipeline nunca los generó — crear FASE-PATCH para añadirlos.
2. **Si ERR-4 confirmado:** El pipeline genera DOS versiones de hotel_schema. Determinar cuál es la oficial — o unificar.
3. **PF-1 confirmation:** Si BookingScraper real está activo, el confidence=0.25 en research.json sugiere que el fallback a GBP no se está usando — revisar `autonomous_researcher.py`.
4. **Si ERR-1 confirmado:** "Salud Técnica GEO: 23/100" no viene de ningún módulo — es hallucination pura del LLM.

---

## CHECKLIST DE VERIFICACIÓN

- [ ] PF-1: Dual BookingScraper — ¿Cuál está activo?
- [ ] PF-2: Tests — ¿Suite verde?
- [ ] PF-3: Timestamps — ¿todos de la misma ejecución?
- [ ] A1-A5: YAML front matter vs. JSONs fuente
- [ ] B1-B7: Scores visibilidad — ¿de módulo o hardcoded?
- [ ] C1-C4: Métricas IA — ¿de dónde sale "Salud Técnica GEO: 23"?
- [ ] D1-D3: GBP verificado
- [ ] E1-E7: Porcentajes de brechas — ¿de módulo opportunity_scorer?
- [ ] F1-F3: Escenarios financieros
- [ ] G1-G10: Assets — ¿todos existen?
- [ ] H1-H3: Duplicados geo_enriched vs. raíz
- [ ] I1-I7: Servicios vs. assets
- [ ] J1-J7: Tri-play validation
- [ ] ERR-1 a ERR-7: Confirmar cada error
- [ ] Calcular Forensic Score final
- [ ] Calcular Tri-Play Score final
- [ ] Producir RESULTS.md consolidado
