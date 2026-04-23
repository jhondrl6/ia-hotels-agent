# Mapeo Pain → Servicio: Gap Analysis

> **Generado por**: FASE-CAUSAL-DIAG  
> **Fecha**: 2026-04-23  
> **Proyecto**: iah-cli v4.34.0

---

## Resumen Ejecutivo

**PROBLEMA**: La propuesta comercial genera exactamente **7 servicios estáticos** (desde `PROPOSAL_SERVICE_TO_ASSET`), pero `pain_solution_mapper` detecta **25 pains** que mapean a **30+ assets potenciales**. Esto causa desalineamiento entre el diagnóstico y la propuesta.

---

## 1. PAIN_SOLUTION_MAP — 25 Pains Detectables

| # | Pain ID | Nombre | Severity | Assets Mapeados |
|---|---------|--------|----------|-----------------|
| 1 | `no_whatsapp_visible` | Sin WhatsApp Visible | high | `whatsapp_button` |
| 2 | `whatsapp_conflict` | Conflicto de WhatsApp | high | `whatsapp_button`, `whatsapp_conflict_guide` |
| 3 | `no_faq_schema` | Sin Schema FAQ | medium | `faq_page` |
| 4 | `low_gbp_score` | Bajo Score GBP | high | `geo_playbook`, `review_plan` |
| 5 | `no_motor_reservas` | Sin Motor de Reservas | high | `barra_reserva_movil` |
| 6 | `no_hotel_schema` | Sin Schema Hotel | high | `hotel_schema` |
| 7 | `poor_performance` | Performance Deficiente | medium | `performance_audit`, `optimization_guide` |
| 8 | `no_org_schema` | Sin Schema Organization | low | `org_schema` |
| 9 | `missing_reviews` | Falta de Reviews | medium | `review_widget`, `review_plan` |
| 10 | `low_ota_divergence` | Alta Dependencia OTAs | high | `direct_booking_campaign` |
| 11 | `metadata_defaults` | Metadatos por Defecto | high | `optimization_guide` |
| 12 | `missing_llmstxt` | Sin llms.txt | low | `llms_txt` |
| 13 | `no_analytics_configured` | Sin Analytics Configurado | medium | `analytics_setup_guide` |
| 14 | `low_organic_visibility` | Baja Visibilidad Organica | medium | `indirect_traffic_optimization` |
| 15 | `no_ga4_enhanced` | GA4 sin Configuracion Avanzada | low | `analytics_setup_guide` |
| 16 | `ai_crawler_blocked` | Crawlers IA Bloqueados | medium | `llms_txt` |
| 17 | `low_citability` | Contenido Poco Citable | medium | `optimization_guide` |
| 18 | `low_ia_readiness` | Baja Preparacion IA | high | `hotel_schema`, `llms_txt`, `local_content_page` |
| 19 | `no_schema_reviews` | Sin Schema de Reviews | high | `hotel_schema` |
| 20 | `no_ssl` | Sin SSL/HTTPS | high | `ssl_guide` |
| 21 | `no_og_tags` | Sin Open Graph Tags | medium | `og_tags_guide`, `open_graph` |
| 22 | `missing_alt_text` | Imagenes sin Texto Alternativo | medium | `alt_text_guide` |
| 23 | `no_blog_content` | Blog Inactivo | low | `blog_strategy_guide` |
| 24 | `no_social_links` | Sin Presencia en Redes | low | `social_strategy_guide` |
| 25 | `low_content_length` | Contenido Muy Corto | medium | `optimization_guide` |

---

## 2. PROPOSAL_SERVICE_TO_ASSET — 7 Servicios Estáticos

| Servicio (Propuesta) | asset_type | Pains que lo generan |
|---------------------|------------|---------------------|
| Google Maps Optimizado | `geo_playbook` | `low_gbp_score` |
| SEO Local | `optimization_guide` | `poor_performance`, `metadata_defaults`, `low_citability`, `low_content_length` |
| Boton de WhatsApp | `whatsapp_button` | `no_whatsapp_visible`, `whatsapp_conflict` |
| Datos Estructurados | `hotel_schema` | `no_hotel_schema`, `low_ia_readiness`, `no_schema_reviews` |
| Informe Mensual | `monthly_report` | **NINGUNO** (no existe pain que lo mapee) |
| Pagina de FAQ | `faq_page` | `no_faq_schema` |
| Meta Tags Sociales (Open Graph) | `open_graph` | `no_og_tags` |

---

## 3. GAP ANALYSIS

### 3.1 Servicios SIN pain correspondiente (en PROPOSAL_SERVICE_TO_ASSET pero no generados por pain detection)

| Servicio | asset_type | Gap |
|----------|------------|-----|
| `Informe Mensual` | `monthly_report` | **NO HAY PAIN QUE LO GENERE** |

Este servicio aparece en la propuesta pero ningún pain en `PAIN_SOLUTION_MAP` lo genera. Es un servicio "hardcodeado" sin justificación desde el diagnóstico.

### 3.2 Pains SIN representación en PROPOSAL_SERVICE_TO_ASSET

| Pain ID | Nombre | Assets | ¿En propuesta? |
|---------|--------|--------|----------------|
| `no_motor_reservas` | Sin Motor de Reservas | `barra_reserva_movil` | NO |
| `missing_reviews` | Falta de Reviews | `review_widget`, `review_plan` | NO |
| `low_ota_divergence` | Alta Dependencia OTAs | `direct_booking_campaign` | NO |
| `missing_llmstxt` | Sin llms.txt | `llms_txt` | NO |
| `no_analytics_configured` | Sin Analytics | `analytics_setup_guide` | NO |
| `low_organic_visibility` | Baja Visibilidad Organica | `indirect_traffic_optimization` | NO |
| `no_ga4_enhanced` | GA4 sin Configuracion | `analytics_setup_guide` | NO |
| `ai_crawler_blocked` | Crawlers IA Bloqueados | `llms_txt` | NO |
| `no_org_schema` | Sin Schema Organization | `org_schema` | NO |
| `no_ssl` | Sin SSL/HTTPS | `ssl_guide` | NO |
| `no_og_tags` | Sin Open Graph Tags | `og_tags_guide` | NO (solo `open_graph`) |
| `missing_alt_text` | Imagenes sin Alt | `alt_text_guide` | NO |
| `no_blog_content` | Blog Inactivo | `blog_strategy_guide` | NO |
| `no_social_links` | Sin Redes Sociales | `social_strategy_guide` | NO |

**13 de 25 pains NO tienen representación en la propuesta comercial.**

### 3.3 Servicios duplicados en la propuesta (referencias al MISMO asset)

| asset_type | Servicios que lo referencian |
|------------|----------------------------|
| `whatsapp_button` | "Boton de WhatsApp" |
| `hotel_schema` | "Datos Estructurados" |
| `open_graph` | "Meta Tags Sociales (Open Graph)" |

---

## 4. Flujo Actual vs Flujo Deseado

### Flujo Actual (ESTÁTICO)
```
detect_pains() → 25 pains detectados
       ↓
pain_solution_mapper.map_to_solutions() → 30+ assets
       ↓
BUT: propuesta usa PROPOSAL_SERVICE_TO_ASSET (7 entries) ← IGNORA detected pains
       ↓
propuesta_v6_template.md → tabla FIJA de 7 servicios
```

### Flujo Deseado (DINÁMICO)
```
detect_pains() → 25 pains detectados
       ↓
Por cada pain → mapear a servicios del SERVICE_CATALOG
       ↓
SERVICE_CATALOG: servicios vendibles con metadata (descripcion, categoria, pain_asociado)
       ↓
propuesta_generada → tabla DINÁMICA: solo servicios cuyos pains fueron detectados
```

---

## 5. Duplicación de Código

**PROBLEMA CRÍTICO**: `_generate_asset_quality_table` está DEFINIDO DOS VECES en `v4_proposal_generator.py`:
- **Primera definición**: línea ~654
- **Segunda definición**: línea ~1084

Ambas hacen exactamente lo mismo (recorren `PROPOSAL_SERVICE_TO_ASSET`). La segunda definición "machaca" la primera. El método que realmente se usa depende del orden de parsing de Python.

---

## 6. Estructura de la Propuesta V6

### Tabla Principal (HARDCODEADA en template)
Líneas 44-52 de `propuesta_v6_template.md`:
```
| Servicio | Qué obtiene |
|----------|-------------|
| ✅ Google Maps Optimizado (GEO) | ... |
| ✅ SEO Local (SEO) | ... |
| ✅ Botón de WhatsApp | ... |
| ✅ Datos Estructurados | ... |
| ✅ Informe Mensual | ... |
| ✅ Página de FAQ | ... |
| ✅ Meta Tags Sociales (Open Graph) | ... |
```

Esta tabla es **FIJA** — siempre muestra los 7 mismos servicios, sin importar qué pains se detectaron.

### Tabla Secondary (`${asset_quality_table}`)
Generada por `_generate_asset_quality_table()` que itera sobre `PROPOSAL_SERVICE_TO_ASSET`. También estática.

---

## 7. Conclusion

La propuesta comercial tiene **2 capas estáticas** que IGNORAN completamente los pains detectados:
1. La tabla principal de servicios en el template (7 filas fijas)
2. La tabla de calidad `${asset_quality_table}` (7 filas basadas en `PROPOSAL_SERVICE_TO_ASSET`)

**，即使检测到 25 个 pain，提案也只显示 7 个服务。**

La solución (Opción C del plan) requiere:
1. Crear `SERVICE_CATALOG` como catálogo independiente de servicios vendibles
2. Refactorizar `_generate_asset_quality_table` para iterar sobre los pains detectados
3. Mantener `PROPOSAL_SERVICE_TO_ASSET` para backwards-compat del gate de publicación
4. Eliminar la duplicación del método `_generate_asset_quality_table`
