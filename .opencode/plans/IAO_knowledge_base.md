# IAO_HOTEL_KNOWLEDGE_BASE
# Versión: 1.0 | Optimizado para consumo por agente IA
# Dominio: Optimización para Inteligencia Artificial (IAO) — Hoteles Boutique
# Tarea del agente: Auditar sitios web de hoteles, generar diagnósticos JSON, priorizar mejoras y producir propuestas comerciales

---

## [META]

```yaml
kb_version: "1.0"
fecha: "2026-03-30"
dominio: "IAO - IA Optimization para hoteles boutique"
region_objetivo: "Colombia (adaptable a LATAM)"
idioma_salida: "Español"
tareas_soportadas:
  - auditar_sitio_web
  - generar_diagnostico_json
  - comparar_competidores
  - generar_propuesta_comercial
  - ejecutar_pipeline_scraping
  - responder_preguntas_iao
agente_debe_saber:
  - IAO es la evolución del SEO clásico hacia visibilidad en respuestas de IA (ChatGPT, Gemini, Perplexity)
  - El marcado estructurado (Schema.org JSON-LD) es el mecanismo principal de señalización
  - Core Web Vitals son umbral técnico mínimo; sin ellos, el contenido puede no ser indexado correctamente
  - NAP consistency es crítica para confianza local
```

---

## [GLOSARIO]

> IDs referenciables para uso en prompts y código: `[TERM:nombre]`

| ID | Término | Definición |
|---|---|---|
| `[TERM:IAO]` | IAO (IA Optimization) | Conjunto de prácticas para que sistemas de IA (LLMs, motores de búsqueda generativos) extraigan, citen y presenten correctamente el contenido de un sitio web. Evolución del SEO clásico. |
| `[TERM:SCHEMA]` | Schema.org / JSON-LD | Vocabulario estándar de marcado estructurado. Los hoteles usan tipos `Hotel` o `LodgingBusiness`. Se implementa como `<script type="application/ld+json">`. |
| `[TERM:EEAT]` | E-E-A-T | Experience, Expertise, Authoritativeness, Trustworthiness. Señales que Google/IA usan para evaluar credibilidad de una fuente. |
| `[TERM:NAP]` | NAP Consistency | Name, Address, Phone. La coherencia de estos datos en web, Google Business y directorios es requisito de SEO local. |
| `[TERM:CWV]` | Core Web Vitals | Métricas de rendimiento de Google: LCP, INP/FID, CLS. Umbrales definidos en `[SECTION:CWV_THRESHOLDS]`. |
| `[TERM:LCP]` | LCP | Largest Contentful Paint. Tiempo en que el elemento visual más grande es renderizado. |
| `[TERM:CLS]` | CLS | Cumulative Layout Shift. Mide estabilidad visual durante carga. |
| `[TERM:INP]` | INP / FID | Interaction to Next Paint / First Input Delay. Mide respuesta a interacción. |
| `[TERM:KGO]` | KGO | Knowledge Graph Optimization. Técnica de conectar entidades del sitio con bases de conocimiento externas (Wikipedia, Wikidata) via `sameAs`. |
| `[TERM:USP]` | USP | Unique Selling Proposition. Propuesta de valor diferencial del hotel. Debe aparecer explícita en el contenido. |
| `[TERM:RICH_RESULTS]` | Rich Results | Resultados enriquecidos en Google SERPs (estrellas, FAQs, precios) generados a partir de Schema.org válido. |
| `[TERM:FAQA]` | FAQPage Schema | Tipo de Schema.org que estructura preguntas y respuestas. Alto impacto en visibilidad de IA generativa. |
| `[TERM:PSI_API]` | PageSpeed Insights API | API gratuita de Google para medir Core Web Vitals de forma programática. |
| `[TERM:PYDANTIC]` | Pydantic | Librería Python para validación y serialización de modelos de datos con tipado. |

---

## [SECTION:SCHEMA_REQUIRED_FIELDS]
### Schema.org — Campos obligatorios y opcionales para Hotel/LodgingBusiness

```yaml
schema_type: "Hotel"  # alternativa: LodgingBusiness (ambos válidos)
parent_type: "LocalBusiness"

campos_obligatorios:
  - name          # Nombre completo sin siglas ambiguas
  - address:
      type: PostalAddress
      fields: [streetAddress, addressLocality, addressRegion, postalCode]
  - telephone     # Con prefijo internacional: "+57XXXXXXXXXX"

campos_alto_impacto_IA:
  - aggregateRating:
      type: AggregateRating
      fields: [ratingValue, reviewCount]
      prioridad: ALTA  # Genera estrellas en rich results
  - review:
      type: Review
      fields: [author, datePublished, reviewBody]
  - image:
      type: ImageObject
      nota: "Usar alt descriptivo en español"

campos_recomendados:
  - offers / aggregateOffer   # Precios y disponibilidad
  - priceRange                # Rango textual, ej: "$$"
  - amenityFeature            # WiFi, piscina, etc.
  - openingHoursSpecification
  - ContactPoint:
      fields: [telephone, email, contactType]
  - geo:
      type: GeoCoordinates
      fields: [latitude, longitude]
  - acceptedPaymentMethod
  - url                       # URL canónica del sitio

schemas_adicionales_valiosos:
  - FAQPage       # Para preguntas frecuentes → impacto directo en LLMs
  - HowTo         # Para instrucciones "Cómo llegar"
  - VideoObject   # Si hay recorrido virtual
  - sameAs        # Links a Wikipedia, Google KB → KGO
```

---

## [SECTION:SCHEMA_TEMPLATE]
### Plantilla JSON-LD completa — Lista para completar con variables

```json
{
  "@context": "https://schema.org",
  "@type": "Hotel",
  "name": "{{HOTEL_NAME}}",
  "url": "{{HOTEL_URL}}",
  "telephone": "{{PHONE_INTL}}",
  "email": "{{CONTACT_EMAIL}}",
  "description": "{{HOTEL_DESCRIPTION_MIN_300_WORDS}}",
  "priceRange": "{{PRICE_RANGE}}",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "{{STREET_ADDRESS}}",
    "addressLocality": "{{CITY}}",
    "addressRegion": "{{DEPARTMENT}}",
    "postalCode": "{{POSTAL_CODE}}",
    "addressCountry": "CO"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "{{LAT}}",
    "longitude": "{{LNG}}"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{RATING_VALUE}}",
    "reviewCount": "{{REVIEW_COUNT}}"
  },
  "image": {
    "@type": "ImageObject",
    "url": "{{IMAGE_URL}}",
    "description": "{{IMAGE_ALT_ES}}"
  },
  "amenityFeature": [
    {"@type": "LocationFeatureSpecification", "name": "WiFi gratuito", "value": true},
    {"@type": "LocationFeatureSpecification", "name": "{{AMENITY_2}}", "value": true}
  ],
  "sameAs": [
    "{{TRIPADVISOR_URL}}",
    "{{BOOKING_URL}}",
    "{{GOOGLE_BUSINESS_URL}}"
  ]
}
```

---

## [SECTION:CWV_THRESHOLDS]
### Core Web Vitals — Umbrales de rendimiento

| Métrica | Umbral BUENO | Umbral NECESITA_MEJORA | Umbral MALO | Prioridad IAO |
|---|---|---|---|---|
| `LCP` | ≤ 2500ms | 2500–4000ms | > 4000ms | **ALTA** |
| `INP` (antes FID) | ≤ 200ms | 200–500ms | > 500ms | ALTA |
| `CLS` | ≤ 0.1 | 0.1–0.25 | > 0.25 | ALTA |
| Carga total | < 3000ms | 3000–5000ms | > 5000ms | MEDIA |
| Tamaño página | < 1MB | 1–3MB | > 3MB | MEDIA |

```yaml
advertencias_criticas:
  slider_portada:
    problema: "Los sliders suelen contener el elemento LCP dominante"
    impacto: "LCP alto → ranking penalizado"
    accion: "Desactivar o reemplazar con imagen estática optimizada"
    prioridad: ALTA

  formato_imagen:
    recomendado: "WebP con fallback JPEG"
    nota: "Dimensiones CSS deben coincidir con dimensiones reales del archivo"

  mobile:
    font_size_base: "≥ 16px CSS"
    touch_target_min: "44×44 px CSS"
    patron: "Responsive Design (mobile-first)"
```

---

## [SECTION:EEAT_SIGNALS]
### Señales E-E-A-T — Cómo demostrar autoridad y confianza

```yaml
señales_obligatorias:
  - google_business_profile:
      estado: "Verificado y completo"
      prioridad: ALTA
  - nap_consistency:
      alcance: [sitio_web, google_business, tripadvisor, booking, directorios_locales]
      prioridad: ALTA
  - ssl_https:
      todo_el_sitio: true
      prioridad: ALTA

señales_recomendadas:
  - fotos_equipo_real: true
  - nombre_propietarios_visible: true
  - certificaciones:
      ejemplos: ["Turismo sostenible NTS-TS", "Registro Nacional de Turismo"]
  - premios_y_reconocimientos: true
  - membresías:
      ejemplos: ["Cotelco", "Acodres", "ProColombia"]
  - redes_sociales_activas:
      plataformas: [Instagram, Facebook]
      frecuencia_mínima: "1 post/semana"
  - blog_activo:
      frecuencia_mínima: "1 artículo/mes"
      min_palabras: 600

señales_de_contenido:
  - contenido_unico: true
  - min_palabras_pagina_principal: 300
  - usp_explicita: true
  - politica_cancelacion_clara: true
  - aviso_privacidad: true        # GDPR / Ley 1581 Colombia
  - terminos_reserva: true
```

---

## [SECTION:SCRAPING_METHODS]
### Métodos de extracción — Cuándo usar cada herramienta

| Situación | Herramienta | Velocidad | Complejidad |
|---|---|---|---|
| HTML estático simple | `requests` + `BeautifulSoup4` | Rápida | Baja |
| JavaScript dinámico / SPA | `Playwright` | Media-rápida | Media |
| Crawling completo del sitio | `Scrapy` | Alta (async) | Alta |
| Contenido mixto (estático+JS) | `Scrapy` + `Playwright` | Media | Alta |
| Métricas de rendimiento | `PageSpeed Insights API` | API call | Baja |
| Validación de Schema | `Rich Results Test API` / `jsonschema` | Rápida | Baja |

---

## [SECTION:CODE_SCRAPING_STATIC]
### Código — Scraping HTML estático

```python
import requests
from bs4 import BeautifulSoup
import json

def fetch_html(url: str) -> BeautifulSoup:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; IAOBot/1.0)"}
    res = requests.get(url, headers=headers, timeout=10)
    res.raise_for_status()
    return BeautifulSoup(res.text, "lxml")
```

---

## [SECTION:CODE_SCRAPING_DYNAMIC]
### Código — Scraping JS dinámico con Playwright

```python
from playwright.sync_api import sync_playwright

def fetch_dynamic_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        page.wait_for_load_state("networkidle")
        html = page.content()
        browser.close()
    return html
```

> **Nota del agente:** Playwright es preferido sobre Selenium para páginas SPA por mayor velocidad y estabilidad.

---

## [SECTION:CODE_SCHEMA_EXTRACTION]
### Código — Extracción y detección de Schema JSON-LD

```python
import json
from bs4 import BeautifulSoup

TIPOS_HOTEL = {"Hotel", "LodgingBusiness", "LocalBusiness"}

def extraer_schemas(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    schemas = []
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            schemas.append(data)
        except (json.JSONDecodeError, TypeError):
            pass
    return schemas

def detectar_schema_hotel(schemas: list[dict]) -> bool:
    for s in schemas:
        tipo = s.get("@type", "")
        if isinstance(tipo, list):
            if any(t in TIPOS_HOTEL for t in tipo):
                return True
        elif tipo in TIPOS_HOTEL:
            return True
    return False

def detectar_aggregate_rating(schemas: list[dict]) -> dict | None:
    for s in schemas:
        if "aggregateRating" in s:
            return s["aggregateRating"]
    return None
```

---

## [SECTION:CODE_SCHEMA_VALIDATION]
### Código — Validación de Schema con jsonschema

```python
from jsonschema import validate, ValidationError

SCHEMA_HOTEL_MINIMO = {
    "type": "object",
    "required": ["@context", "@type", "name", "address", "telephone"],
    "properties": {
        "@context": {"type": "string"},
        "@type": {"type": "string"},
        "name": {"type": "string"},
        "telephone": {"type": "string"},
        "address": {
            "type": "object",
            "required": ["streetAddress", "addressLocality"]
        }
    }
}

def validar_schema(data: dict) -> tuple[bool, str]:
    try:
        validate(instance=data, schema=SCHEMA_HOTEL_MINIMO)
        return True, "válido"
    except ValidationError as e:
        return False, str(e.message)
```

---

## [SECTION:CODE_PERFORMANCE_METRICS]
### Código — Captura de Core Web Vitals

```python
import subprocess, json

def obtener_cwv_lighthouse(url: str, output_path: str = "report.json") -> dict:
    """Requiere Lighthouse CLI instalado: npm install -g lighthouse"""
    subprocess.run([
        "lighthouse", url,
        "--only-categories=performance",
        "--output=json",
        f"--output-path={output_path}",
        "--quiet"
    ], check=True)
    with open(output_path) as f:
        report = json.load(f)
    audits = report.get("audits", {})
    return {
        "LCP": audits.get("largest-contentful-paint", {}).get("numericValue"),
        "CLS": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        "TBT": audits.get("total-blocking-time", {}).get("numericValue"),
        "score_performance": report.get("categories", {}).get("performance", {}).get("score")
    }
```

---

## [SECTION:DATA_MODEL]
### Modelo de datos — Diagnóstico IAO (Pydantic)

```python
from pydantic import BaseModel, HttpUrl
from typing import Optional

class ElementosDetectados(BaseModel):
    schema_hotel: bool
    schema_reviews: bool
    schema_faq: bool
    open_graph: bool
    ssl: bool
    nap_consistente: Optional[bool]
    LCP_ms: Optional[float]
    CLS: Optional[float]
    INP_ms: Optional[float]
    contenido_extenso: bool   # len(texto) > 300 palabras

class Recomendacion(BaseModel):
    prioridad: str   # "alta" | "media" | "baja"
    accion: str
    impacto: str
    esfuerzo: str    # "bajo" | "medio" | "alto"

class DiagnosticoIAO(BaseModel):
    url: HttpUrl
    fecha_analisis: str
    cumplimiento: int            # 0-100
    elementos: ElementosDetectados
    faltantes: list[str]
    recomendaciones: list[Recomendacion]
    paquete_sugerido: Optional[str]  # "basico" | "avanzado" | "premium"
```

---

## [SECTION:OUTPUT_JSON_TEMPLATE]
### Plantilla — JSON de salida del diagnóstico

```json
{
  "url": "{{URL}}",
  "fecha_analisis": "{{FECHA_ISO}}",
  "cumplimiento": "{{SCORE_0_100}}",
  "elementos": {
    "schema_hotel": "{{BOOL}}",
    "schema_reviews": "{{BOOL}}",
    "schema_faq": "{{BOOL}}",
    "open_graph": "{{BOOL}}",
    "ssl": "{{BOOL}}",
    "nap_consistente": "{{BOOL_OR_NULL}}",
    "LCP_ms": "{{FLOAT_OR_NULL}}",
    "CLS": "{{FLOAT_OR_NULL}}",
    "INP_ms": "{{FLOAT_OR_NULL}}",
    "contenido_extenso": "{{BOOL}}"
  },
  "faltantes": [
    "{{ELEMENTO_FALTANTE_1}}",
    "{{ELEMENTO_FALTANTE_2}}"
  ],
  "recomendaciones": [
    {
      "prioridad": "alta",
      "accion": "{{ACCION}}",
      "impacto": "{{IMPACTO_ESPERADO}}",
      "esfuerzo": "{{ESFUERZO}}"
    }
  ],
  "paquete_sugerido": "{{basico|avanzado|premium}}"
}
```

---

## [SECTION:PIPELINE_ARCHITECTURE]
### Arquitectura del pipeline de auditoría IAO

```
┌─────────────────────────────────────────────────────────┐
│                  PIPELINE IAO AUDIT                      │
└─────────────────────────────────────────────────────────┘

  [INPUT]
  URL del hotel (o lista de URLs)
        │
        ▼
  ┌─────────────┐
  │  STAGE 1    │  Crawler inicial
  │  URL LIST   │  → Sitemap.xml o lista manual
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 2    │  Fetch & Render
  │  HTML FETCH │  → Requests (estático) | Playwright (dinámico)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 3    │  Parseo & Extracción
  │  PARSE      │  → Schema JSON-LD, meta tags, NAP, texto
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 4    │  Validación & Scoring
  │  VALIDATE   │  → jsonschema, conteo palabras, checklist
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 5    │  Métricas de rendimiento
  │  PERF       │  → PageSpeed API | Lighthouse CLI
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 6    │  Almacenamiento
  │  STORAGE    │  → SQLite / JSONLines (modelo Pydantic)
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │  STAGE 7    │  Output
  │  REPORT     │  → JSON diagnóstico | Propuesta comercial
  └─────────────┘
```

---

## [SECTION:PRIORITY_MATRIX]
### Matriz de priorización — Impacto IA vs Esfuerzo

> **REGLA DEL AGENTE:** Recomendar siempre en orden de prioridad de esta tabla. No invertir orden.

| Elemento | Impacto IA | Esfuerzo | **Prioridad** | ROI |
|---|---|---|---|---|
| Schema `AggregateRating` (reseñas) | Alto | Bajo | **🔴 ALTA** | Genera estrellas en rich results |
| SSL / HTTPS todo el sitio | Medio | Bajo | **🔴 ALTA** | Seguridad + ranking |
| Optimizar LCP (desactivar slider) | Alto | Medio | **🔴 ALTA** | Core Web Vitals crítico |
| Contenido único extenso (>300 palabras) | Alto | Alto | **🔴 ALTA** | Autoridad de contenido |
| Schema `Hotel` básico | Alto | Bajo | **🔴 ALTA** | Base mínima de indexación IA |
| Open Graph + Twitter Cards | Medio | Bajo | **🟡 MEDIA** | Compartibilidad social |
| NAP consistente (Google Business) | Medio | Bajo | **🟡 MEDIA** | SEO local |
| Schema `FAQPage` | Medio | Medio | **🟡 MEDIA** | Respuestas directas en LLMs |
| Reviews visibles en sitio | Medio | Medio | **🟡 MEDIA** | E-E-A-T |
| Certificaciones y E-E-A-T | Medio | Medio | **🟡 MEDIA** | Confianza institucional |
| Blog activo (1/mes) | Medio | Alto | **🟡 MEDIA** | Señal de actividad |
| Redes sociales activas | Bajo | Bajo | **🟢 BAJA** | Señal secundaria |

---

## [SECTION:PACKAGES_COMMERCIAL]
### Paquetes comerciales — Estructura de propuesta

```yaml
paquete_basico:
  nombre: "IAO Esencial"
  incluye:
    - Schema Hotel + AggregateRating
    - Open Graph y Twitter Cards
    - SSL verificado
    - NAP consistency check
    - Reporte JSON diagnóstico
  impacto_esperado: "Rich results con estrellas, indexación correcta en IA"
  esfuerzo: "bajo"

paquete_avanzado:
  nombre: "IAO Avanzado"
  incluye:
    - Todo lo de Básico
    - Optimización LCP (imagen/slider)
    - Schema FAQPage
    - Schema HowTo (Cómo llegar)
    - Auditoría Core Web Vitals
    - Recomendaciones de contenido
  impacto_esperado: "Visibilidad en respuestas de ChatGPT/Gemini, mejora ranking"
  esfuerzo: "medio"

paquete_premium:
  nombre: "IAO Premium"
  incluye:
    - Todo lo de Avanzado
    - KGO (sameAs a Wikipedia/Wikidata)
    - VideoObject schema
    - Monitoreo continuo (scripts CI)
    - Blog strategy + E-E-A-T completo
    - Análisis de competidores (3-5 hoteles)
    - Dashboard de seguimiento IA
  impacto_esperado: "Posicionamiento como referencia en Knowledge Graph regional"
  esfuerzo: "alto"
```

---

## [SECTION:COMPETITOR_ANALYSIS]
### Protocolo de análisis de competidores

```yaml
objetivo: "Establecer benchmarks de Schema, rendimiento y señales E-E-A-T"
muestra: "3-5 hoteles boutique de la misma región"

elementos_a_comparar:
  - schemas_presentes: [Hotel, FAQPage, HowTo, VideoObject]
  - aggregate_rating: {presente: bool, valor: float}
  - LCP_ms: float
  - CLS: float
  - tiene_blog: bool
  - redes_activas: bool
  - certificaciones_visibles: bool

metodo_extraccion: |
  # Buscar JSON-LD en competidor
  scripts = soup.find_all("script", {"type": "application/ld+json"})
  # Comparar campos presentes vs checklist IAO

output: "Tabla comparativa → identificar gaps del cliente vs benchmark"
```

---

## [SECTION:IA_VISIBILITY_MEASUREMENT]
### Medición de visibilidad en IA

> No hay métricas estándar de IA. Usar estas proxies:

| Método | Herramienta | Frecuencia |
|---|---|---|
| Knowledge Panels / Featured Snippets | Google Search Console | Semanal |
| Aparición en respuestas IA | API OpenAI (queries automatizadas) | Mensual |
| AI Visibility tracking | SEMrush AI Visibility Checker | Mensual |
| Share of AI answers (marca/región) | Pruebas manuales / automatizadas | Mensual |
| Tráfico indirecto post-consulta IA | Google Analytics (conversiones) | Mensual |

```python
# Ejemplo: verificar si IA cita el hotel
# (requiere API key de OpenAI)
def test_ia_cita_hotel(hotel_name: str, ciudad: str) -> str:
    preguntas = [
        f"¿Cuáles son los mejores hoteles boutique en {ciudad}?",
        f"¿Dónde quedarse en {ciudad} para una experiencia única?",
        f"Recomiéndame hoteles en {ciudad}"
    ]
    # Llamar a API OpenAI con cada pregunta
    # Verificar si hotel_name aparece en la respuesta
    ...
```

---

## [SECTION:TOOLS_REGISTRY]
### Registro de herramientas — Todas gratuitas/open-source

```yaml
scraping:
  - nombre: requests
    uso: HTML estático
    install: "pip install requests"
  - nombre: BeautifulSoup4
    uso: Parsing HTML
    install: "pip install beautifulsoup4 lxml"
  - nombre: Playwright
    uso: JS dinámico, SPA
    install: "pip install playwright && playwright install chromium"
    nota: "Preferido sobre Selenium por velocidad y estabilidad"
  - nombre: Scrapy
    uso: Crawling masivo
    install: "pip install scrapy"

validacion:
  - nombre: jsonschema
    uso: Validación programática JSON-LD
    install: "pip install jsonschema"
  - nombre: Rich Results Test
    url: "https://search.google.com/test/rich-results"
    uso: Validación visual Schema Google
  - nombre: Schema Markup Validator
    url: "https://validator.schema.org/"
    uso: Validación completa schema.org

rendimiento:
  - nombre: PageSpeed Insights API
    url: "https://developers.google.com/speed/docs/insights/v5/get-started"
    uso: CWV automático
    costo: Gratuito con API key
  - nombre: Lighthouse CLI
    install: "npm install -g lighthouse"
    uso: Auditoría local completa

datos_y_modelos:
  - nombre: Pydantic
    uso: Modelos de datos tipados, validación
    install: "pip install pydantic"
  - nombre: SQLite3
    uso: Almacenamiento local de resultados
    nota: "Built-in en Python"
  - nombre: JSON Lines (.jsonl)
    uso: Exportación simple, compatible con pipelines
```

---

## [SECTION:CHECKLIST_IAO]
### Checklist IAO — Para auditoría rápida

```yaml
checklist_critico:  # Fallar cualquiera = impacto alto
  - [ ] SSL/HTTPS activo en todo el sitio
  - [ ] Schema @type Hotel o LodgingBusiness presente
  - [ ] name, address, telephone en Schema
  - [ ] aggregateRating en Schema
  - [ ] LCP ≤ 2500ms
  - [ ] CLS ≤ 0.1
  - [ ] Contenido mínimo 300 palabras en homepage

checklist_importante:  # Fallar = impacto medio
  - [ ] Open Graph tags (og:title, og:description, og:image, og:locale)
  - [ ] Twitter Card tags
  - [ ] NAP consistente con Google Business
  - [ ] FAQPage Schema presente
  - [ ] Imágenes con alt descriptivo en español
  - [ ] Formato WebP con fallback JPEG
  - [ ] Font-size base ≥ 16px
  - [ ] Touch targets ≥ 44×44px

checklist_deseable:  # Fallar = impacto bajo
  - [ ] Schema HowTo (cómo llegar)
  - [ ] VideoObject si hay recorrido virtual
  - [ ] sameAs a TripAdvisor, Booking, Google Business
  - [ ] Blog activo (1 artículo/mes mínimo)
  - [ ] Redes sociales enlazadas y activas
  - [ ] Aviso de privacidad y términos de reserva
  - [ ] Sitemap.xml en Google Search Console
  - [ ] robots.txt correcto
```

---

## [SECTION:SCORING_ALGORITHM]
### Algoritmo de scoring — Cálculo de cumplimiento (0-100)

```python
def calcular_cumplimiento(elementos: dict) -> int:
    """
    Pesos por elemento. Total máximo = 100.
    """
    pesos = {
        "ssl":               10,
        "schema_hotel":      15,
        "schema_reviews":    15,  # AggregateRating
        "LCP_ok":            10,  # LCP <= 2500ms
        "CLS_ok":             5,  # CLS <= 0.1
        "contenido_extenso": 10,
        "open_graph":         5,
        "schema_faq":         8,
        "nap_consistente":    7,
        "imagenes_alt":       5,
        "blog_activo":        5,
        "redes_activas":      5,
    }
    score = 0
    score += pesos["ssl"] if elementos.get("ssl") else 0
    score += pesos["schema_hotel"] if elementos.get("schema_hotel") else 0
    score += pesos["schema_reviews"] if elementos.get("schema_reviews") else 0
    lcp = elementos.get("LCP_ms")
    score += pesos["LCP_ok"] if lcp and lcp <= 2500 else 0
    cls = elementos.get("CLS")
    score += pesos["CLS_ok"] if cls is not None and cls <= 0.1 else 0
    score += pesos["contenido_extenso"] if elementos.get("contenido_extenso") else 0
    score += pesos["open_graph"] if elementos.get("open_graph") else 0
    score += pesos["schema_faq"] if elementos.get("schema_faq") else 0
    score += pesos["nap_consistente"] if elementos.get("nap_consistente") else 0
    score += pesos["imagenes_alt"] if elementos.get("imagenes_alt") else 0
    score += pesos["blog_activo"] if elementos.get("blog_activo") else 0
    score += pesos["redes_activas"] if elementos.get("redes_activas") else 0
    return min(score, 100)

def sugerir_paquete(score: int) -> str:
    if score < 40:   return "basico"
    if score < 70:   return "avanzado"
    return "premium"
```

---

## [SECTION:QUICK_INDEX]
## Índice rápido — Para X → ir a sección [Y]

| Necesito... | Ir a |
|---|---|
| Saber qué campos poner en el Schema del hotel | `[SECTION:SCHEMA_REQUIRED_FIELDS]` |
| Una plantilla JSON-LD lista para completar | `[SECTION:SCHEMA_TEMPLATE]` |
| Los umbrales exactos de Core Web Vitals | `[SECTION:CWV_THRESHOLDS]` |
| Código para hacer scraping de HTML estático | `[SECTION:CODE_SCRAPING_STATIC]` |
| Código para sitios con JavaScript dinámico | `[SECTION:CODE_SCRAPING_DYNAMIC]` |
| Extraer Schema JSON-LD de un sitio | `[SECTION:CODE_SCHEMA_EXTRACTION]` |
| Validar un Schema programáticamente | `[SECTION:CODE_SCHEMA_VALIDATION]` |
| Obtener LCP/CLS con Lighthouse | `[SECTION:CODE_PERFORMANCE_METRICS]` |
| El modelo de datos Pydantic del diagnóstico | `[SECTION:DATA_MODEL]` |
| La plantilla JSON del output del diagnóstico | `[SECTION:OUTPUT_JSON_TEMPLATE]` |
| Ver el flujo completo del pipeline | `[SECTION:PIPELINE_ARCHITECTURE]` |
| Saber qué recomendar primero (prioridades) | `[SECTION:PRIORITY_MATRIX]` |
| Estructurar una propuesta comercial en paquetes | `[SECTION:PACKAGES_COMMERCIAL]` |
| Analizar competidores | `[SECTION:COMPETITOR_ANALYSIS]` |
| Medir si la IA cita el hotel | `[SECTION:IA_VISIBILITY_MEASUREMENT]` |
| Ver todas las herramientas disponibles | `[SECTION:TOOLS_REGISTRY]` |
| Hacer una auditoría rápida con checklist | `[SECTION:CHECKLIST_IAO]` |
| Calcular el score de cumplimiento (0-100) | `[SECTION:SCORING_ALGORITHM]` |
| Entender un término técnico | `[GLOSARIO]` |

---
*FIN DE KB — IAO_HOTEL_KNOWLEDGE_BASE v1.0*
