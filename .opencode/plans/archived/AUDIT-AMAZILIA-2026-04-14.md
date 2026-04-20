# AUDITORÍA CRUZADA v4complete — Amaziliahotel
## Contexto para Planificación de Intervenciones (v2.0)

**Fecha:** 2026-04-14  
**Hotel:** Amaziliahotel  
**URL:** https://amaziliahotel.com/  
**Ejecución:** v4complete completada exitosamente (exit_code=0)  
**Coherence Score:** 0.84 (gate passed)  
**Publication Ready:** true  
**Entregable ZIP:** `output/v4_complete/deliveries/amaziliahotel_20260414.zip`

---

## 1. DATOS REALES VERIFICADOS DEL SITIO WEB

Contraste directo con HTML de https://amaziliahotel.com/ (236,644 chars):

```
Title:           "Amazilia | Hotel campestre en Pereira"
Meta description: VACÍA (confirmado)
Schema.org JSON-LD: 0 bloques (confirmado)
Open Graph:       0 tags (confirmado)
WhatsApp:         4 mentions en HTML, PERO sin enlaces wa.me/ directos
Teléfono:         tel:3104019049 (EXISTS, aparece 2 veces)
Imágenes:         21 con alt text, 20 con alt="" (vacío), 0 sin atributo alt
Google Maps embed: 1 referencia presente
Contenido rico:   spa (300 refs), habitaciones (5), piscina (2), restaurante (2),
                  campestre (4), Pereira (10), Eje Cafetero (2), Risaralda (2)
```

**GBP name real (Google Maps):** "Amazilia Hotel" (no "amaziliahotel")
**Región real:** Pereira, Risaralda, Eje Cafetero, Colombia  
**Segmento:** Hotel campestre/boutique con spa  
**Teléfono verificado:** +57 3104019049

---

## 2. ARCHIVOS GENERADOS POR v4complete

Ruta base: `/mnt/c/Users/Jhond/Github/iah-cli/output/v4_complete/`

### Documentos principales
- `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260414_091319.md` (7238 bytes)
- `02_PROPUESTA_COMERCIAL_20260414_091319.md` (7152 bytes)
- `audit_report.json` (6197 bytes)
- `financial_scenarios.json` (1400 bytes)
- `v4_complete_report.json` (12301 bytes)

### Assets generados (última versión cada uno)
Directorio: `output/v4_complete/amaziliahotel/`

| Asset | Archivo más reciente | Tamaño | Estado |
|-------|---------------------|--------|--------|
| hotel_schema | `hotel_schema/ESTIMATED_hotel_schema_20260414_091320.json` | 1190 bytes | PLACEHOLDER (coords NYC) |
| org_schema | `org_schema/ESTIMATED_org_schema_20260414_091321.json` | 258 bytes | VACÍO (example.com) |
| llms_txt | `llms_txt/ESTIMATED_llms_20260414_091321.txt` | 843 bytes | GENÉRICO |
| faq_page | `faq_page/ESTIMATED_faqs_20260414_091321.csv` | 1657 bytes | GENÉRICO |
| geo_playbook | `geo_playbook/ESTIMATED_geo_playbook_20260414_091320.md` | 585 bytes | VACÍO |
| review_plan | `review_plan/ESTIMATED_plan_reviews_20260414_091320.md` | 475 bytes | GENÉRICO |
| review_widget | `review_widget/ESTIMATED_widget_reviews_20260414_091321.html` | 505 bytes | FRAUDULENTO |
| whatsapp_button | `whatsapp_button/ESTIMATED_boton_whatsapp_20260414_091321.html` | 2033 bytes | ROTO |
| optimization_guide | `optimization_guide/ESTIMATED_guia_optimizacion_20260414_091320.md` | 3716 bytes | CONTRADICTORIO |
| analytics_setup_guide | `analytics_setup_guide/ESTIMATED_guia_configuracion_ga4_20260414_091321.md` | 4841 bytes | GENÉRICO |
| indirect_traffic_optimization | `indirect_traffic_optimization/ESTIMATED_optimizacion_trafico_indirecto_20260414_091321.md` | 5198 bytes | PLANTILLA |
| monthly_report | `monthly_report/ESTIMATED_informe_mensual_20260414_091321.md` | 5086 bytes | VACÍO (nombre "Hotel" genérico) |
| voice_assistant_guide | `voice_assistant_guide/google_assistant_checklist.md` + 2 más | ~4500 bytes total | PARCIAL |

### geo_enriched (datos internos, NO entregados al cliente)
Directorio: `output/v4_complete/amaziliahotel/geo_enriched/`

- `hotel_schema_rich.json` — MISMAS coordenadas NYC incorrectas
- `faq_schema.json` — MISMAS preguntas genéricas
- `llms.txt` — IDEM al entregado
- `robots_fix.txt` — Corrección PARCIAL (solo 4 de 14 crawlers) — NUNCA referenciado en assets
- `geo_badge.md` — Score GEO 23/100 CRITICAL
- `geo_dashboard.md` — Breakdown por área
- `geo_fix_kit.md` — Plan de acción (genérico)
- `seo_fix_kit.md` — Intervención crítica
- `sync_report.md` — Sync diagnóstico vs GEO (score 0.75)

---

## 3. DESCONEXIONES ENCONTRADAS (12 hallazgos)

### CRITICAL (3)

**D1 — Coordenadas GPS falsas (NYC en vez de Colombia)**
- Archivos afectados: `hotel_schema.json`, `geo_enriched/hotel_schema_rich.json`
- Valor actual: latitude "40.7128", longitude "-74.0060" (New York City)
- Valor real: ~4.81°N, -75.69°W (Pereira, Colombia)
- Módulo generador: `modules/asset_generation/` (hotel_schema_generator)
- Causa raíz: Default hardcodeado sin extracción de coordenadas del sitio/GBP
- **Evidencia:** `grep "40.7128" output/v4_complete/amaziliahotel/hotel_schema/*.json` → 5 matches

**D2 — Assets son plantillas genéricas, no soluciones específicas**
- 10 de 13 assets NO contienen datos reales del hotel
- El contenido del sitio (spa x300, Pereira x10, Eje Cafetero x2) NO se usa en ningún asset
- Módulo generador: múltiples generators en `modules/asset_generation/`
- Causa raíz: Los generators no reciben/usan datos del audit como contexto
- **Evidencia:** Contenido real del sitio vs ASSET_* en context/ — 0% overlap

**D12 — GBP query incorrecta (nombre "amaziliahotel" vs real "Amazilia Hotel")**
- GBP name resultado: "Amaziliahotel, Colombia: búsqueda de hoteles de Google" — esto es resultado de búsqueda, NO perfil
- GBP name real (Google Maps): "Amazilia Hotel" (Pereira, Colombia)
- rating: 0.0, reviews: 0, photos: 0 — datos insuficientes
- geo_score=0/100 es ARTEFACTO de query incorrecta, no diagnóstico real
- El audit lo clasificó como LOW pero debería ser CRITICAL
- Módulo: `modules/auditors/` GBP integration
- **Fix requerido**: Usar "Amazilia Hotel" Pereira, Colombia como query, no "amaziliahotel"
- **Implicación:** Todo el diagnóstico GEO se basa en datos inválidos por query incorrecta

### HIGH (5)

**D3 — Región "nacional" cuando el hotel es de Pereira/Eje Cafetero**
- Afecta: diagnóstico (línea 21: "esta zona en Colombia"), propuesta (línea 11: "Amaziliahotel - nacional", línea 20: "hotels en nacional")
- El HTML contiene "Pereira" 10 veces pero el region detector devuelve "nacional"
- Módulo: `main.py` región ~1511 o `modules/orchestration_v4/`
- **Evidencia:** Propuesta línea 11 y 20 confirmado con archivo real

**D4 — whatsapp_button con href="detected_via_html" (ROTO)**
- Archivo: `whatsapp_button/ESTIMATED_boton_whatsapp_20260414_091321.html`
- href="https://wa.me/detected_via_html?text=..."
- El sitio tiene tel:3104019049 pero el generator no lo usa
- Módulo: `modules/asset_generation/whatsapp_button_generator.py`
- **Evidencia:** `grep "detected_via_html" output/v4_complete/amaziliahotel/whatsapp_button/*.html` → 2 matches

**D5 — review_widget con review falso (5 estrellas, 0 reviews reales)**
- Muestra ★★★★★ y "Excelente servicio" inventado
- El audit confirmó: rating 0.0, 0 reviews
- Módulo: `modules/asset_generation/review_widget_generator.py`
- **Evidencia:** ASSET_review_widget.html líneas 4-5 = datos fraudulentos

**D6 — org_schema con url "https://example.com" y campos vacíos**
- url: "https://example.com" (PLACEHOLDER FALSO)
- logo: "" (vacío)
- telephone: "" (vacío)
- Módulo: `modules/asset_generation/org_schema_generator.py`
- **Evidencia:** `grep "example.com" output/v4_complete/amaziliahotel/org_schema/*.json` → 5+ matches

**D7 — Propuesta dice "No generado" para assets que SÍ existen**
- Búsqueda de Voz: dice ❌ pero voice_assistant_guide SÍ se generó (3 archivos)
- Botón de WhatsApp: dice ❌ pero whatsapp_button SÍ se generó
- Informe Mensual: dice ❌ pero monthly_report SÍ se generó
- Módulo: `main.py` propuesta generation (~líneas 2063-2098), el status no se propaga
- **Evidencia:** Propuesta líneas 67-71 vs archivos reales en directorio

### MEDIUM (3)

**D8 — optimization_guide se contradice**
- Línea: "Sin title tag configurado" → luego "Title tag personalizado detectado"
- Línea: "Sin meta description" → luego "Descripción personalizada detectada"
- Módulo: `modules/asset_generation/optimization_guide_generator.py`

**D9 — Teléfono real (3104019049) no capturado por audit**
- audit_report.json: phone_web = null
- El sitio tiene tel:3104019049 en 2 enlaces
- Módulo: `modules/auditors/` (web auditor, falta parsing de tel: links)

**D10 — robots.txt bloquea 14 IA crawlers pero robots_fix.txt solo corrige 4**
- audit.ai_crawlers.blocked_crawlers: 14 bots (GPTBot, ChatGPT-User, ClaudeBot, Claude-User, PerplexityBot, Google-Extended, Bytespider, FacebookBot, Applebot, DuckDuckBot, Baiduspider, YandexBot, Bingbot, Googlebot)
- geo_enriched/robots_fix.txt SOLO menciona: GPTBot, ChatGPT-User, Claude-Web, Google-Extended (4 de 14)
- El robots_fix.txt está INCOMPLETO — falta Googlebot, Bingbot, YandexBot, etc.
- geo_enriched/robots_fix.txt existe pero NINGÚN asset lo referencia
- Módulo: `modules/auditors/ai_crawler_auditor.py` + diagnostic generator

### LOW (1)

**D11 — "Images with Alt: False" es impreciso**
- Sitio tiene 21 con alt + 20 con alt="" — problema parcial, no total
- Diagnóstico lo presenta como si ninguna tuviera alt
- Módulo: auditor de SEO elements

---

## 4. NUEVOS GAPs DETECTADOS EN VALIDACIÓN CRUZADA

### GAP-1 (CRITICAL) — GBP completamente inválido
- El resultado "Amaziliahotel, Colombia: búsqueda de hoteles de Google" es claramente un resultado de búsqueda de Google, NO el perfil GBP real del hotel
- Esto significa que geo_score=0/100 no es un diagnóstico real — es un artefacto de API key inválida o búsqueda mal configurada
- Impacto: TODO el análisis GEO/IAO puede estar basado en datos falsos

### GAP-2 (MEDIUM) — monthly_report usa "Hotel" genérico en vez de "Amaziliahotel"
- ASSET_monthly_report.md línea 4: `**Hotel**: Hotel`
- El nombre del hotel se pierde en la generación del asset

### GAP-3 (MEDIUM) — llms_txt NO menciona nada del contenido real del sitio
- El sitio tiene "spa" (300 refs), "Pereira" (10 refs), "Eje Cafetero" (2 refs)
- El llms_txt solo dice "hotel boutique ubicado en Colombia" — genérico total
- No usa ningún dato extraído del sitio real

---

## 5. DATOS FINANCIEROS (cadena verificada consistente)

```json
{
  "input_data": {
    "rooms": 10,
    "adr_cop": 300000.0,
    "occupancy_rate": 0.5,
    "direct_channel_percentage": 0.2
  },
  "scenarios": {
    "conservative": 5076000.0,
    "realistic": 2610000.0,
    "optimistic": -189000.0
  },
  "pricing": {
    "tier": "boutique",
    "monthly_price_cop": 130500.0,
    "pain_ratio": 0.05
  },
  "breakdown": {
    "ota_commission_cop": 5400000.0,
    "evidence_tier": "C",
    "data_sources": {
      "adr": "legacy_hardcode",
      "rooms": "hotel_data",
      "occupancy": "default",
      "direct_channel": "default",
      "shift": "hardcoded: sin GA4",
      "ia_boost": "estimado: sin GA4"
    }
  }
}
```

**Consistencia:** Diagnóstico ($2.610.000) = Propuesta ($2.610.000) = JSON ($2.610.000) ✅  
**Confiabilidad:** Todos los inputs son defaults/hardcoded (Tier C) ⚠️

---

## 6. COHERENCE VALIDATION (datos del sistema)

Archivo: `amaziliahotel/v4_audit/coherence_validation.json`

```json
{
  "is_coherent": false,
  "overall_score": 0.84,
  "checks": [
    {"name": "problems_have_solutions", "passed": true, "score": 0.9},
    {"name": "assets_are_justified", "passed": false, "score": 0.79,
     "message": "Solo 78% de assets tienen justificación"},
    {"name": "financial_data_validated", "passed": true, "score": 0.7},
    {"name": "whatsapp_verified", "passed": false, "score": 0.7,
     "message": "WhatsApp con confidence 0.70 - requiere >= 0.9"},
    {"name": "price_matches_pain", "passed": true, "score": 0.8},
    {"name": "promised_assets_exist", "passed": true, "score": 1.0}
  ],
  "errors": [
    "[assets_are_justified] Solo 78% de assets tienen justificación",
    "[whatsapp_verified] WhatsApp con confidence 0.70 - requiere >= 0.9"
  ]
}
```

**Nota:** `is_coherent: false` pero el gate pasó porque el umbral es 0.8 y el score es 0.84. El gate valida ESTRUCTURA no CONTENIDO.

---

## 7. AUDIT REPORT (datos raw relevantes)

```json
{
  "schema": {
    "hotel_schema_detected": false,
    "faq_schema_detected": false,
    "org_schema_detected": false,
    "total_schemas": 0
  },
  "gbp": {
    "name": "Amaziliahotel, Colombia: búsqueda de hoteles de Google",
    "rating": 0.0,
    "reviews": 0,
    "photos": 0,
    "geo_score": 0,
    "confidence": "verified"
  },
  "metadata": {
    "cms_detected": "wordpress",
    "has_default_title": false,
    "has_default_description": true,
    "description": "<empty>"
  },
  "ai_crawlers": {
    "overall_score": 0.5,
    "blocked_crawlers": ["GPTBot","ChatGPT-User","ClaudeBot","Claude-User",
      "PerplexityBot","Google-Extended","Bytespider","FacebookBot",
      "Applebot","DuckDuckBot","Baiduspider","YandexBot","Bingbot","Googlebot"]
  },
  "citability": {
    "overall_score": 51.7,
    "blocks_analyzed": 3
  },
  "seo_elements": {
    "open_graph": false,
    "images_with_alt": false,
    "active_social": true
  },
  "validation": {
    "whatsapp_status": "unknown",
    "phone_web": null,
    "adr_status": "unknown"
  },
  "llm_report": {
    "mentions": 0,
    "mention_rate": 0.0,
    "mention_score": 0
  }
}
```

---

## 8. MÓDULOS FUENTE INVOLUCRADOS

Para cada intervención, estos son los módulos a modificar:

| Problema | Módulo(s) a modificar | Líneas clave en main.py |
|----------|----------------------|------------------------|
| Coordenadas GPS (D1) | `modules/asset_generation/*schema*generator*` | — |
| Assets genéricos (D2) | Todos los generators en `modules/asset_generation/` | — |
| GBP inválido (D12) | `modules/auditors/` GBP integration | — |
| Región "nacional" (D3) | Region extractor | ~1511 |
| whatsapp_button roto (D4) | `modules/asset_generation/whatsapp*generator*` | — |
| review_widget falso (D5) | `modules/asset_generation/review*widget*` | — |
| org_schema vacío (D6) | `modules/asset_generation/org*schema*` | — |
| Propuesta "No generado" (D7) | `main.py` propuesta generation | ~2063-2098 |
| optimization_guide contradicción (D8) | `modules/asset_generation/optimization*guide*` | — |
| Teléfono no capturado (D9) | `modules/auditors/` web auditor | — |
| robots_fix.txt incompleto (D10) | `modules/auditors/ai_crawler_auditor.py` + diagnostic gen | — |
| monthly_report "Hotel" genérico (GAP-2) | `modules/asset_generation/monthly_report*` | — |
| llms_txt genérico (GAP-3) | `modules/asset_generation/llmstxt_generator.py` | — |

**Flujo principal en main.py:** `run_v4_complete_mode()` líneas ~1396-2435  
**Paso crítico:** La generación de assets ocurre en FASE 4 (líneas ~2193-2225)  
**El gap central:** Los generators NO reciben el audit_report.json como contexto para personalizar

---

## 9. ESTRUCTURA DE DATOS PARA EL PLAN

El plan de intervenciones debe abordar:

1. **FASE de corrección de datos fuente** (coordenadas, región, teléfono, GBP)
2. **FASE de personalización de generators** (todos los assets deben recibir audit data)
3. **FASE de sincronización propuesta↔assets** (status real de entregables)
4. **FASE de validación de contenido** (no solo estructura, sino sustancia)
5. **FASE de corrección de bugs específicos** (whatsapp, review falso, org_schema)
6. **FASE de corrección robots_fix.txt** (incluir los 14 crawlers, no solo 4)

Cada fase debe incluir:
- Módulos específicos a modificar
- Tests a crear/modificar
- Validación con v4complete post-cambio
- Verificación con el mismo hotel (amaziliahotel.com) como smoke test

---

## 10. COMANDO DE RE-EJECUCIÓN PARA VALIDACIÓN

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/
```

Post-fix, verificar:
```bash
# Coordenadas correctas (NO 40.7128, -74.0060)
grep -c "40.7128" output/v4_complete/amaziliahotel/hotel_schema/*.json

# Región correcta (NO "nacional")
grep -n "nacional" output/v4_complete/01_DIAGNOSTICO*.md
grep -n "nacional" output/v4_complete/02_PROPUESTA*.md

# WhatsApp funcional (NO "detected_via_html")
grep "detected_via_html" output/v4_complete/amaziliahotel/whatsapp_button/*.html

# org_schema sin example.com
grep "example.com" output/v4_complete/amaziliahotel/org_schema/*.json

# review_widget sin estrellas falsas
grep -c "★★★★★" output/v4_complete/amaziliahotel/review_widget/*.html

# monthly_report con nombre real (NO "Hotel" genérico)
grep "Hotel" output/v4_complete/amaziliahotel/monthly_report/*.md | grep -v "Amaziliahotel"

# llms_txt con contenido real (debe mencionar Pereira, spa, Eje Cafetero)
grep -i "pereira\|spa\|eje cafetero" output/v4_complete/amaziliahotel/llms_txt/*.txt
```

---

## 11. INFORMACIÓN DE ENTORNO

```
iah-cli path: /mnt/c/Users/Jhond/Github/iah-cli
Python: venv/Scripts/python.exe (NUNCA system python3)
Version: v4.30.0
Provider: DeepSeek (LLM)
Google Maps API: disponible pero Places API falló (key inválida/corta)
SerpAPI: NO configurado (AEO stub)
GA4: NO configurado
WSL: sí (Windows paths via /mnt/c/)
```

---

## 12. PRIORIZACIÓN SUGERIDA

| Prioridad | Hallazgo | Razón |
|-----------|----------|-------|
| P1 | D12 (GBP inválido) | Invalida todo el diagnóstico GEO — dato base corrupto |
| P1 | D1 (Coordenadas NYC) | Afecta directamente SEO local y schema |
| P1 | D4 (WhatsApp roto) | Afecta conversión directa — cliente no puede reservar |
| P2 | D2 (Assets genéricos) | Causa raíz de la mayoría de problemas de calidad |
| P2 | D3 (Región "nacional") | Error visible en documento comercial |
| P2 | D7 (Propuesta vs assets) | Inconsistencia comercial que afecta venta |
| P3 | D5, D6, D8, D9, D10 | Bugs específicos que requieren fix individual |
| P3 | GAP-2, GAP-3 | Calidad de contenido, no bloqueantes |

---

*Contexto generado por auditoría cruzada v4complete - Hermes Agent*  
*Archivo: .opencode/plans/context/AUDIT-AMAZILIA-2026-04-14.md*  
*Versión: 2.0 (actualizado con validación cruzada)*  
*Propósito: Planificar intervenciones en sesión nueva para corregir fallas detectadas*
