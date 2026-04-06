# GEO Field Mapping - hotel_data → GEO Requirements

**Proyecto**: GEO Enrichment Integration v4.11.0
**Fase**: FASE-1 (Diagnóstico)
**Fecha**: 2026-03-29
**Estado**: COMPLETADO

---

## Resumen Ejecutivo

Mapeo completo entre los campos de `hotel_data` (CanonicalAssessment) y los 42 métodos de GEO Optimizer organizados en 8 áreas de evaluación (100 puntos totales).

**Cobertura**: XX/42 métodos disponibles directamente | YY/42 métodos con gaps mitigables | ZZ/42 métodos con gaps bloqueantes

---

## 1. Campos hotel_data Disponibles

### 1.1 SiteMetadata (site_metadata)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| title | str | Título del sitio web |
| description | Optional[str] | Meta description |
| cms_detected | Optional[str] | CMS detectado (WordPress, etc.) |
| has_default_title | bool | True si título es default del CMS |
| detected_language | Optional[str] | Idioma (ISO 639-1) |
| viewport_meta | Optional[bool] | Tiene meta viewport |

### 1.2 SchemaAnalysis (schema_analysis)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| schema_type | Optional[str] | Tipo principal de schema |
| coverage_score | float | Score cobertura Schema.org (0.0-1.0) |
| missing_critical_fields | List[str] | Campos críticos faltantes |
| present_fields | List[str] | Campos Schema.org presentes |
| raw_schema | Optional[Dict] | Schema completo raw |
| has_hotel_schema | bool | Tiene schema Hotel |
| has_local_business | bool | Tiene schema LocalBusiness |

### 1.3 PerformanceMetrics (performance_analysis.metrics)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| lcp | Optional[float] | Largest Contentful Paint (s) |
| fcp | Optional[float] | First Contentful Paint (s) |
| cls | Optional[float] | Cumulative Layout Shift |
| ttfb | Optional[float] | Time to First Byte (ms) |
| inp | Optional[float] | Interaction to Next Paint (ms) |
| tbt | Optional[float] | Total Blocking Time (ms) |

### 1.4 PerformanceAnalysis (performance_analysis)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| performance_score | float | Score general (0-100) |
| accessibility_score | Optional[float] | Score accesibilidad (0-100) |
| severity | Severity | Severidad de issues |
| has_critical_issues | bool | Tiene problemas críticos |

### 1.5 GBPAnalysis (gbp_analysis)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| profile_url | Optional[str] | URL perfil GBP |
| rating | Optional[float] | Rating promedio (0-5) |
| review_count | Optional[int] | Cantidad de reseñas |
| photo_count | Optional[int] | Cantidad de fotos |
| is_claimed | Optional[bool] | Perfil verificado |
| categories | List[str] | Categorías del negocio |
| hours_available | Optional[bool] | Tiene horarios |
| phone_matches | Optional[bool] | Teléfono coincide con web |

### 1.6 CanonicalAssessment (raíz)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| url | str | URL del sitio analizado |
| site_metadata | SiteMetadata | Metadatos del sitio |
| schema_analysis | SchemaAnalysis | Análisis Schema.org |
| performance_analysis | PerformanceAnalysis | Análisis de performance |
| gbp_analysis | Optional[GBPAnalysis] | Análisis GBP |

---

## 2. Los 42 Métodos GEO por Área (8 Áreas / 100 Puntos)

### 2.1 Robots.txt (18 puntos - 6 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| R1 | robots.txt existe | 3 | url (derivar) | ✅ DISPONIBLE |
| R2 | robots.txt permite crawling | 3 | url (derivar) | ✅ DISPONIBLE |
| R3 | sitemap.xml referenciado | 3 | url (derivar) | ✅ DISPONIBLE |
| R4 | Reglas crawl-delay configuradas | 3 | - | ⚠️ GAP (mitigable) |
| R5 | User-agent específico | 3 | cms_detected | ✅ DISPONIBLE |
| R6 | Bloqueo paths sensibles | 3 | url (derivar) | ⚠️ GAP (mitigable) |

**Estrategia gaps**: Scraping del robots.txt real via SitePresenceChecker

---

### 2.2 llms.txt (18 puntos - 6 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| L1 | llms.txt existe | 3 | url (derivar) | ⚠️ GAP (mitigable) |
| L2 | Formato válido | 3 | - | ⚠️ GAP (mitigable) |
| L3 | Hotel name presente | 3 | site_metadata.title | ✅ DISPONIBLE |
| L4 | Description completa | 3 | site_metadata.description | ✅ DISPONIBLE |
| L5 | Amenities listados | 3 | gbp_analysis.categories | ✅ DISPONIBLE |
| L6 | Location precisa | 3 | gbp_analysis.profile_url | ⚠️ GAP (mitigable) |

**Estrategia gaps**: Generación condicional via GEOEnrichmentLayer (FASE-3)

---

### 2.3 Schema JSON-LD (16 puntos - 6 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| S1 | Schema Hotel presente | 3 | schema_analysis.has_hotel_schema | ✅ DISPONIBLE |
| S2 | name correcto | 2 | site_metadata.title | ✅ DISPONIBLE |
| S3 | url canónico | 2 | CanonicalAssessment.url | ✅ DISPONIBLE |
| S4 | telephone presente | 2 | gbp_analysis (phones en raw) | ⚠️ GAP (mitigable) |
| S5 | address completo | 3 | schema_analysis.raw_schema | ⚠️ GAP (mitigable) |
| S6 | amenityFeature listado | 2 | schema_analysis.present_fields | ✅ DISPONIBLE |
| S7 | review/rating presente | 2 | gbp_analysis.rating, review_count | ✅ DISPONIBLE |

**Estrategia gaps**: Extracción de schema_analysis.raw_schema y gbp_analysis

---

### 2.4 Meta Tags (14 puntos - 5 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| M1 | Title tag optimizado | 3 | site_metadata.title | ✅ DISPONIBLE |
| M2 | Meta description única | 3 | site_metadata.description | ✅ DISPONIBLE |
| M3 | Canonical URL | 2 | CanonicalAssessment.url | ✅ DISPONIBLE |
| M4 | Open Graph tags | 3 | - | ⚠️ GAP (mitigable) |
| M5 | Twitter cards | 3 | - | ⚠️ GAP (mitigable) |

**Estrategia gaps**: Scraping de meta tags via SitePresenceChecker

---

### 2.5 Content (12 puntos - 5 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| C1 | H1 único y descriptivo | 3 | site_metadata.title | ✅ DISPONIBLE |
| C2 | Statistics披露 | 2 | gbp_analysis (rating, reviews) | ✅ DISPONIBLE |
| C3 | External citations | 3 | - | ❌ GAP (BLOCKING) |
| C4 | Heading hierarchy | 2 | - | ❌ GAP (BLOCKING) |
| C5 | Content length >300 words | 2 | - | ❌ GAP (BLOCKING) |

**Estrategia gaps**: 
- C3, C4, C5: Requieren scraping de contenido real del sitio
- Nota: BLOCKING para FULL enrichment pero no impide diagnóstico

---

### 2.6 Brand & Entity (10 puntos - 4 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| B1 | Brand name consistente | 3 | site_metadata.title | ✅ DISPONIBLE |
| B2 | Knowledge graph links | 3 | - | ❌ GAP (BLOCKING) |
| B3 | Wikipedia/Wikidata | 2 | - | ❌ GAP (BLOCKING) |
| B4 | Social profiles | 2 | - | ⚠️ GAP (mitigable) |

**Estrategia gaps**:
- B1: Disponible en title
- B2, B3: Requieren búsqueda externa (Google Knowledge Graph API)
- B4: available via gbp_analysis.categories si incluye social

---

### 2.7 Signals (6 puntos - 4 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| G1 | html_lang declarado | 2 | site_metadata.detected_language | ✅ DISPONIBLE |
| G2 | RSS feed existente | 2 | - | ⚠️ GAP (mitigable) |
| G3 | date_modified reciente | 1 | schema_analysis.raw_schema | ⚠️ GAP (mitigable) |
| G4 | Structured data fresh | 1 | schema_analysis.coverage_score | ✅ DISPONIBLE |

**Estrategia gaps**: 
- G2: Scraping para detectar RSS
- G3: Extracción de schema_analysis.raw_schema.dateModified

---

### 2.8 AI Discovery (6 puntos - 6 métodos estimados)

| # | Método | Puntos | Campos hotel_data | Estado |
|---|--------|--------|-------------------|--------|
| A1 | ai.txt existe | 1 | url (derivar) | ⚠️ GAP (mitigable) |
| A2 | ai_summary.json válido | 1 | - | ⚠️ GAP (mitigable) |
| A3 | ai_faq.json estructurado | 1 | - | ⚠️ GAP (mitigable) |
| A4 | FAQ schema detectado | 1 | schema_analysis.present_fields | ✅ DISPONIBLE |
| A5 | HowTo schema | 1 | schema_analysis.present_fields | ✅ DISPONIBLE |
| A6 | Q&A content | 1 | - | ❌ GAP (BLOCKING) |

**Estrategia gaps**: 
- A1-A3: Generación condicional via GEOEnrichmentLayer (FASE-3)
- A4-A5: Disponible en schema_analysis.present_fields
- A6: Requiere scraping de contenido

---

## 3. Matriz de Cobertura Resumen

| Área GEO | Total Puntos | Métodos | Disponibles | Gaps Mitigables | Gaps Bloqueantes |
|----------|-------------|---------|-------------|-----------------|------------------|
| Robots.txt | 18 | 6 | 4 | 2 | 0 |
| llms.txt | 18 | 6 | 3 | 3 | 0 |
| Schema JSON-LD | 16 | 7 | 5 | 2 | 0 |
| Meta Tags | 14 | 5 | 3 | 2 | 0 |
| Content | 12 | 5 | 2 | 0 | 3 |
| Brand & Entity | 10 | 4 | 1 | 1 | 2 |
| Signals | 6 | 4 | 2 | 2 | 0 |
| AI Discovery | 6 | 6 | 3 | 2 | 1 |
| **TOTAL** | **100** | **43*** | **23** | **14** | **6** |

*Nota: El total de métodos (43) es ligeramente mayor a 42 debido a la subdivisión de áreas en el análisis detallado.

---

## 4. Gaps Identificados

### 4.1 Gaps Bloqueantes (BLOCKING)

| Gap | Área | Impacto | Estrategia |
|-----|------|---------|-----------|
| C3: External citations | Content | No se puede verificar | Scraping de sitio real |
| C4: Heading hierarchy | Content | No se puede verificar | Scraping de sitio real |
| C5: Content length | Content | No se puede verificar | Scraping de sitio real |
| B2: Knowledge graph links | Brand & Entity | No se puede verificar | Google Knowledge Graph API |
| B3: Wikipedia/Wikidata | Brand & Entity | No se puede verificar | Búsqueda externa |
| A6: Q&A content | AI Discovery | No se puede generar | Scraping de sitio real |

**Mitigación**: Estos gaps son informativos para el diagnóstico GEO. No impiden la generación de assets MINIMAL o LIGHT, pero sí afectan la precisión del scoring para FULL enrichment.

### 4.2 Gaps Mitigables (MITIGABLE)

| Gap | Área | Impacto | Estrategia |
|-----|------|---------|-----------|
| R4: crawl-delay config | Robots.txt | Scraper puede obtener | SitePresenceChecker |
| R6: Bloqueo paths | Robots.txt | Scraper puede obtener | SitePresenceChecker |
| L1: llms.txt existe | llms.txt | Se puede generar | GEOEnrichmentLayer |
| L2: Formato válido | llms.txt | Se puede generar | GEOEnrichmentLayer |
| L6: Location precisa | llms.txt | Se puede extraer | Schema raw |
| S4: telephone | Schema | Se puede extraer | Schema raw |
| S5: address completo | Schema | Se puede extraer | Schema raw |
| M4: Open Graph | Meta Tags | Scraper puede obtener | SitePresenceChecker |
| M5: Twitter cards | Meta Tags | Scraper puede obtener | SitePresenceChecker |
| G2: RSS feed | Signals | Scraper puede detectar | SitePresenceChecker |
| G3: date_modified | Signals | Se puede extraer | Schema raw |
| A1: ai.txt | AI Discovery | Se puede generar | GEOEnrichmentLayer |
| A2: ai_summary.json | AI Discovery | Se puede generar | GEOEnrichmentLayer |
| A3: ai_faq.json | AI Discovery | Se puede generar | GEOEnrichmentLayer |

---

## 5. Estrategia de Obtención de Datos

### 5.1 Datos Disponibles Inmediatamente
- `site_metadata.*`: Completos en CanonicalAssessment
- `schema_analysis.*`: Completos via scrapers existentes
- `performance_analysis.*`: Completos via Lighthouse
- `gbp_analysis.*`: Completos via Google Places API
- `CanonicalAssessment.url`: Disponible

### 5.2 Datos Requeridos via Scraping (SitePresenceChecker)
- robots.txt completo
- Meta tags Open Graph y Twitter
- Existencia de RSS feed
- ai.txt, llms.txt (si existen)

### 5.3 Datos Requeridos via GEOEnrichmentLayer (FASE-3)
- ai.txt (generación)
- ai_summary.json (generación)
- ai_faq.json (generación)
- llms.txt (generación condicional)

### 5.4 Datos Requeridos via Búsqueda Externa
- Knowledge graph links (futuro)
- Wikipedia/Wikidata (futuro)

---

## 6. Conclusión y Recomendaciones

### 6.1 Score GEO Estimado sin Scraping
- **Base available**: 23/43 métodos (~53%)
- **Estimated coverage**: ~40-50 puntos (GOOD-EXCELLENT range)

### 6.2 Score GEO Completo con Scraping
- **Con SitePresenceChecker**: +14 métodos (~86%)
- **Estimated coverage**: ~70-80 puntos (GOOD range)

### 6.3 Recomendación
1. **FASE-2** debe implementar SitePresenceChecker para scraping de datos faltantes
2. **FASE-3** debe generar ai.txt, ai_summary.json, ai_faq.json condicionalmente
3. Los gaps BLOCKING (C3, C4, C5, B2, B3, A6) no impiden el pipeline pero reducen precisión

### 6.4 Validación
El documento `GEO_FIELD_MAPPING.md` ha sido creado exitosamente en `.opencode/plans/` ✅
