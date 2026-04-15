# Guía Técnica - IA Hoteles Agent

**Versión:** v4.31.1
**Última actualización:** 2026-04-15
**Proyecto:** IA Hoteles Agent CLI

---

## Notas de Cambios

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
