# AEO_KNOWLEDGE_BASE
# Auditory Engine Optimization — Hospitalidad Boutique, Eje Cafetero (2026)
# FORMAT: Optimizado para consumo por agentes de IA y generación de scripts
# VERSION: 1.0 | IDIOMA: ES | DOMINIO: Turismo/Hospitalidad/SaaS
# USO: Referencia técnica estructurada. Cada sección es autocontenida y referenciable.

---

## [META]

```yaml
titulo: "Marco Estratégico y Técnico de AEO para Hospitalidad Boutique — Eje Cafetero"
año: 2026
region_objetivo: "Eje Cafetero, Colombia (Caldas, Quindío, Risaralda)"
audiencia_primaria: "Desarrolladores SaaS, agentes IA, estrategas de marketing digital"
problema_raiz: "Los hoteles boutique pierden visibilidad frente a asistentes de voz e IA generativa por falta de datos estructurados"
solucion_propuesta: "Módulo SaaS de AEO que automatiza schema, sincroniza plataformas y genera archivos para IA"
paradigma_actual: "SEO → AEO + GEO (2026)"
```

---

## [GLOSARIO] Definiciones Técnicas

| ID | Término | Definición Técnica |
|----|---------|-------------------|
| G1 | AEO | Auditory Engine Optimization. Técnicas para ser la respuesta única en asistentes de voz (Alexa, Siri, Google Assistant). Objetivo: posición cero / fragmento destacado legible por TTS. |
| G2 | GEO | Generative Engine Optimization. Estrategias para ser citado en respuestas de LLMs (ChatGPT, Gemini, Perplexity). Requiere riqueza semántica y autoridad de entidad. |
| G3 | VEO | Optimización para consultas en lenguaje natural. Usa NLP y palabras clave de larga cola. |
| G4 | TTS | Text-to-Speech. Sistema de síntesis de voz que lee fragmentos destacados. |
| G5 | JSON-LD | JavaScript Object Notation for Linked Data. Formato recomendado para datos estructurados Schema.org. |
| G6 | GBP | Google Business Profile. Panel de gestión de presencia local en Google. |
| G7 | NAP | Nombre, Dirección, Teléfono. Trío de datos cuya consistencia es factor de confianza crítico entre plataformas. |
| G8 | PMS | Property Management System. Sistema central de gestión del hotel. |
| G9 | ASP | Alexa Smart Properties for Hospitality. Servicio Amazon para flotas de dispositivos Echo en habitaciones. |
| G10 | ASK | Alexa Skills Kit. Framework para desarrollar Skills personalizadas de Alexa. |
| G11 | LLM | Large Language Model. Modelo de lenguaje de gran tamaño (ej: GPT-4, Gemini). |
| G12 | llms.txt | Archivo de texto plano en raíz del dominio. Versión Markdown del sitio para rastreadores IA. Funciona como "conserje" para LLMs. |
| G13 | SpeakableSpecification | Propiedad Schema.org que marca secciones de una página aptas para ser leídas en voz. Duración recomendada: 20-30 segundos (~2-3 oraciones). |
| G14 | USP | Unique Selling Proposition. Propuesta de valor única del hotel. |
| G15 | Agentic Booking | Reserva iniciada y procesada por un asistente IA sin salir de la interfaz de búsqueda. |

---

## [COMPARATIVA] AEO vs GEO vs VEO

| Concepto | Objetivo Primario | Mecanismo de Interacción | Longitud Contenido | Tono |
|----------|-------------------|--------------------------|---------------------|------|
| AEO | Selección como respuesta única de voz | Fragmentos destacados + datos estructurados para TTS | 40-60 palabras | Natural, conversacional |
| GEO | Inclusión en resúmenes narrativos de IA | Autoridad de entidad, citas en fuentes de confianza, riqueza semántica | 150-300 palabras | Autoritativo, basado en datos |
| VEO | Reconocimiento de consultas en lenguaje natural | NLP + palabras clave de larga cola | Variable | Lenguaje natural |

---

## [SCHEMA] Propiedades Schema.org Críticas para Hoteles

### Jerarquía de Tipos (IMPORTANTE para IA)
```
INCORRECTO: LocalBusiness
CORRECTO:   Hotel > LodgingBusiness > LocalBusiness
ACCIÓN:     Cambiar tipo Schema de LocalBusiness a Hotel (impacto máximo, esfuerzo mínimo)
```

### Propiedades Esenciales (JSON-LD)

| Propiedad Schema | Función Técnica | Impacto en Voz/IA | Prioridad |
|------------------|-----------------|-------------------|-----------|
| `@type: "Hotel"` | Define entidad principal como alojamiento | Google Assistant entiende que ofrece pernoctación | CRÍTICA |
| `aggregateRating` | Señal de confianza y calidad | Asistentes priorizan entidades con valoraciones altas para recomendaciones "el mejor hotel" | ALTA |
| `amenityFeature` | Detalles de servicios específicos | Responde consultas: "hotel con spa", "hotel con piscina climatizada" | ALTA |
| `geo` (Coordinates) | Precisión de localización lat/lng | Siri y Google Assistant resuelven consultas de proximidad "hoteles cerca de mí" | ALTA |
| `priceRange` | Clasificación de presupuesto | Filtra resultados "hotel boutique económico" o "de lujo" | MEDIA |
| `FAQPage` | Pares pregunta-respuesta | Fuente directa para responder políticas de check-in, mascotas, etc. | ALTA |
| `speakable` | Secciones aptas para voz | Evita lectura de menús de navegación o metadatos confusos | MEDIA |
| `HotelRoom` | Detalles por tipo de habitación | Permite consultas granulares por tipo y características | ALTA |
| `Offer` | Precios y disponibilidad | Compatible con feeds de Google Hotels | ALTA |

### Plantilla JSON-LD Base para Hotel Boutique
```json
{
  "@context": "https://schema.org",
  "@type": "Hotel",
  "name": "[NOMBRE_HOTEL]",
  "description": "[DESCRIPCION_USP_40_60_PALABRAS]",
  "url": "[URL_OFICIAL]",
  "telephone": "[TELEFONO]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[DIRECCION]",
    "addressLocality": "[CIUDAD]",
    "addressRegion": "Eje Cafetero",
    "addressCountry": "CO"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "[LAT]",
    "longitude": "[LNG]"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[VALOR]",
    "reviewCount": "[CANTIDAD]"
  },
  "amenityFeature": [
    {"@type": "LocationFeatureSpecification", "name": "[AMENIDAD]", "value": true}
  ],
  "priceRange": "[RANGO_$$]",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": ["[SELECTOR_CSS_DESCRIPCION]", "[SELECTOR_CSS_SERVICIOS]"]
  }
}
```

---

## [PLATAFORMAS] Requisitos por Asistente de Voz

### Google Assistant + Google Business Profile (GBP)

| Elemento GBP | Requisito para IA/Voz | Acción en SaaS |
|--------------|----------------------|----------------|
| Atributos de Hotel | Wi-Fi, AC, accesibilidad (detalles técnicos) | Sincronización automática de amenidades desde PMS → GBP |
| Reseñas con Fotos | Formato "Historias", menciones de servicios | Análisis de sentimiento de reseñas para destacar frases citables por IA |
| Integración WhatsApp | Comunicación en tiempo real | Módulo de chat centralizado (GBP + WhatsApp) para personal |
| Precios en Tiempo Real | Conexión con Google Hotels | Feed de precios XML con precisión de tarifa para respuestas de voz |
| Reserve with Google API | Agentic Booking sin salir de búsqueda | Motor de reservas compatible con API de Reserve with Google |

**Nota técnica:** Google Assistant en 2026 actúa como intermediario directo ("Agentic Booking"). El motor de reservas DEBE ser compatible con la API de "Reserve with Google".

---

### Apple Siri + Apple Business Connect

| Requisito | Descripción | Acción Estratégica |
|-----------|-------------|-------------------|
| Verificación de Ubicación | Confirmación oficial de la propiedad | Usar número D-U-N-S o documentos comerciales para autoridad |
| Showcases (Vitrinas) | Publicaciones dinámicas de ofertas | Programar contenido visual (catas de café, eventos locales) |
| Siri Actions | Integración de comandos directos | Configurar botones: "Llamar", "Cómo llegar" |
| Categorización Precisa | Categorías específicas | Seleccionar "Hotel Boutique" o "Alojamiento Rural" (NO categorías genéricas) |
| Fotos Alta Resolución | Exterior e interior | Determinante para tarjeta de lugar enriquecida en Siri |
| Consistencia NAP | Nombre, Dirección, Teléfono | Datos idénticos en Apple, Google y sitio web |

**Trigger de voz objetivo:** "Hey Siri, busca hoteles boutique cerca de mí"

---

### Amazon Alexa (ASK + ASP for Hospitality)

#### Nivel 1: Visibilidad Externa (Búsqueda de Voz)
```
Herramienta: Alexa Skills Kit (ASK)
Capacidad: Skill personalizada del hotel
Ejemplo de consulta habilitada: "Alexa, pregunta a [Nombre Hotel] si tiene disponibilidad este fin de semana"
```

#### Nivel 2: Experiencia In-Room (Alexa Smart Properties)
```
Herramienta: ASP for Hospitality (servicio por invitación / proveedores certificados)
Integración: PMS ↔ Consola de gestión Alexa
Capacidades habilitadas:
  - Solicitudes de servicio de habitaciones por voz
  - Check-out por voz
  - Órdenes de trabajo automáticas desde intents de Alexa
Privacidad: Grabaciones NO guardadas, sin datos personales del huésped requeridos
```

#### Arquitectura SaaS para Alexa
```
Alexa Intent → API Bridge → PMS/Sistema de Gestión Hotel → Orden de Trabajo
```

---

## [CONTENIDO] Directrices para Redacción AEO/GEO

### Regla de Oro: Específico > Vago
```
INCORRECTO: "experiencia inolvidable"
CORRECTO:   "Habitaciones con cafeteras Nespresso, cortinas blackout y duchas de efecto lluvia"
```

### Formato por Canal

| Característica | AEO (Voz) | GEO (IA Generativa) |
|----------------|-----------|---------------------|
| Estructura | Pregunta directa + respuesta concisa | Resúmenes narrativos con detalles contextuales |
| Longitud | 40-60 palabras | 150-300 palabras |
| Tono | Natural, conversacional | Autoritativo, basado en datos específicos |
| Formato visual | Listas con viñetas y tablas | Párrafos con encabezados claros |
| Uso de datos | Fragmentos aislados para TTS | Riqueza semántica completa |

### SpeakableSpecification — Reglas Técnicas
- Duración de audio: 20-30 segundos por sección
- Equivalencia: ~2-3 oraciones concisas
- Implementación: Selectores CSS o XPaths apuntando al contenido narrativo del hotel
- Evita: Menús de navegación, metadatos, scripts de marketing

---

## [GEO] Estrategia para ChatGPT, Gemini y Perplexity

### Grafo de Conocimiento — Fuentes Objetivo

| Tipo de Fuente | Ejemplos | Peso en LLMs |
|----------------|----------|-------------|
| Publicaciones de alta autoridad | Condé Nast Traveler, Forbes Travel | MUY ALTO |
| Guías locales reputadas | Guías de Caldas, Quindío, turismo.gov.co | ALTO |
| Foros de viajeros | Reddit (r/Colombia, r/travel) | MEDIO |
| Directorios especializados | Booking, TripAdvisor (con reseñas textuales) | MEDIO |
| Propio sitio web | Blog, páginas de servicios, FAQs | MEDIO |

### Reglas de Consistencia Semántica
```
Si las reseñas mencionan consistentemente: "perfecto para familias"
→ El LLM aprende la asociación semántica
→ Recomienda el hotel para búsquedas de "hotel familiar en el Eje Cafetero"

Implicación SaaS: Monitorear y reforzar las asociaciones semánticas positivas en reseñas
```

---

## [LLMS_TXT] Estructura del Archivo llms.txt

### Propósito
```
Archivo: /llms.txt (raíz del dominio)
Función: "Conserje" para rastreadores IA — versión Markdown del sitio sin ruido HTML
Innovación: 2025-2026
Herramienta de generación: Firecrawl
```

### Estructura Recomendada
```markdown
# [Nombre del Hotel Boutique]

[Descripción USP única en UNA oración — el valor diferencial del hotel]

## Servicios
- [URL página Spa]
- [URL página Restaurante]
- [URL página Experiencias Cafeteras]
- [URL otras experiencias]

## Habitaciones
[Detalles técnicos de cada tipo de habitación en formato Markdown]
- Tipo 1: [nombre], [m²], [capacidad], [amenidades específicas]
- Tipo 2: [nombre], [m²], [capacidad], [amenidades específicas]

## Políticas
- Mascotas: [sí/no + condiciones]
- Niños: [política]
- Cancelación: [términos]
- Check-in / Check-out: [horarios]

## Contexto Geográfico
[Proximidad a: Paisaje Cultural Cafetero, Valle del Cocora, Salento, Termales de Santa Rosa, etc.]
```

---

## [COLOMBIA] Contexto Regional — Eje Cafetero

### Entidades Geográficas Clave (para Asociación Semántica)
```yaml
entidades_obligatorias_en_contenido:
  - "Paisaje Cultural Cafetero"
  - "Valle del Cocora"
  - "Salento"
  - "Termales de Santa Rosa"
  - "Nevado del Ruiz"  # si aplica por ubicación
  - "Eje Cafetero"
  - nombre_municipio_especifico

departamentos_cubiertos:
  - Caldas
  - Quindío
  - Risaralda

dato_estadistico: "58% de consumidores usa búsqueda por voz para encontrar negocios locales"
tendencia_colombia_2026: "Caldas y Quindío lideran índices de satisfacción turística en Colombia"
```

### Estrategia Multilingüe
```
Idioma primario:   Español (turistas nacionales)
Idioma secundario: Inglés (turistas internacionales)
Acción técnica:    Metadatos y schemas presentes en AMBOS idiomas
Razón:             Asistentes modernos (Alexa, Google) permiten cambio dinámico de idioma
Riesgo sin esto:   Pérdida de tráfico de voz de turistas extranjeros
```

---

## [KPIs] Métricas de Medición AEO/GEO

### KPIs Clave

| Métrica | Definición | Herramienta Sugerida |
|---------|-----------|----------------------|
| AI Visibility Score | % de menciones en respuestas IA para un conjunto de prompts definidos | Semrush AI Toolkit, Profound |
| Share of Voice (SoV) | Cuota de menciones vs. competidores en el sector | Profound Agent Analytics |
| Tasa de Citación | Frecuencia con que la IA incluye enlace al sitio como fuente | MentionDesk, Semrush |
| Sentiment Score | Tono (positivo/negativo) que la IA usa para describir la marca | Semrush Brand Performance |

### Fórmula ROI del Módulo SaaS

```
ROI = ((Ahorro Operativo + Ingresos por Reservas Directas) - Costo de Software)
      ÷ Costo de Software × 100

Ahorro Operativo = Automatización de respuestas a preguntas frecuentes
                   (reducción de tiempo del personal en correos/llamadas básicas)
Ingresos Directos = Reservas capturadas vía Agentic Booking / Reserve with Google
```

---

## [VENDORS] Herramientas y Plataformas Líderes (2025-2026)

| Herramienta | Tipo | Capacidad Clave | Uso en SaaS |
|------------|------|-----------------|-------------|
| **Profound** | Analytics IA | Seguimiento en 10 motores de respuesta principales. API para desarrolladores con datos de menciones, citas y sentimiento | Integrar API en dashboard del módulo SaaS |
| **Semrush AI Toolkit** | Research + Analytics | "Prompt Research": descubrir qué pregunta la audiencia a la IA, posicionamiento de competidores | Análisis de keywords de voz y gaps competitivos |
| **HiJiffy / Seekda** | Hospitalidad + IA | Motores de reserva conversacionales, alimentan grafos de conocimiento de Google y Gemini | Evaluación como alternativa o complemento al módulo |
| **Firecrawl** | Generación llms.txt | Genera automáticamente versiones legibles por IA de sitios web existentes | Automatizar generación del llms.txt para clientes |

---

## [ROADMAP] Checklist de Implementación SaaS

### Módulos del Sistema

| # | Módulo | Descripción Técnica | Prioridad | Esfuerzo | Impacto |
|---|--------|---------------------|-----------|---------|---------|
| M1 | **Schema Automatizado** | Generación dinámica JSON-LD para: Hotel, HotelRoom, Offer, FAQPage. Input: datos del inventario PMS → Output: código sin intervención del usuario | MÁXIMA | Bajo | Muy Alto |
| M2 | **Sincronizador de Entidades** | Interfaz única que actualiza amenidades y fotos en GBP + Apple Business Connect + Alexa simultáneamente | ALTA | Medio | Alto |
| M3 | **Gestor SpeakableSpecification** | UI para que el hotelero marque párrafos específicos como "favoritos para voz" | ALTA | Bajo | Medio |
| M4 | **Generador llms.txt Adaptativo** | Genera automáticamente llms.txt desde páginas de servicios y habitaciones del CMS | ALTA | Bajo | Medio |
| M5 | **Analíticas de Visibilidad IA** | Integración API Profound: dashboard mostrando menciones del hotel en ChatGPT/Perplexity por mes | MEDIA | Alto | Muy Alto |
| M6 | **API Bridge Alexa→PMS** | Traducción de intents de Alexa en órdenes de trabajo dentro del PMS | MEDIA | Alto | Alto |
| M7 | **Reserve with Google Connector** | Conectar motor de reservas del hotel con API de Reserve with Google | MEDIA | Alto | Muy Alto |

### Priorización Estratégica

| Prioridad | Tarea Clave | Esfuerzo | Impacto |
|-----------|------------|---------|---------|
| 🔴 MÁXIMA | Corrección tipo Schema: `LocalBusiness` → `Hotel` | Bajo | Muy Alto |
| 🟠 ALTA | Implementar secciones FAQ con marcado estructurado en páginas de habitaciones | Medio | Alto |
| 🟠 ALTA | Despliegue de archivo `llms.txt` en raíz del sitio | Bajo | Medio |
| 🟡 MEDIA | Conexión con API Reserve with Google (Agentic Booking) | Alto | Muy Alto |

---

## [ARQUITECTURA] Flujo de Datos del Sistema AEO SaaS

```
[PMS del Hotel]
      │
      ▼
[Módulo SaaS AEO]
      │
      ├──► [JSON-LD Generator] ──► sitio web del hotel (Schema.org)
      │                                    │
      │                                    ▼
      │                        [Google Crawl → Hotel Pack → Google Assistant]
      │
      ├──► [GBP Sync] ──► Google Business Profile ──► Google Assistant / Maps
      │
      ├──► [Apple Sync] ──► Apple Business Connect ──► Siri / Apple Maps
      │
      ├──► [Alexa Bridge] ──► Alexa Skills Kit / ASP ──► Amazon Echo
      │
      ├──► [llms.txt Generator] ──► /llms.txt en raíz ──► ChatGPT / Perplexity / Gemini crawlers
      │
      ├──► [SpeakableSpec Manager] ──► CSS selectors ──► Google Assistant TTS
      │
      └──► [Analytics Dashboard]
                    │
                    ├── Profound API (AI Visibility Score)
                    ├── Semrush API (Share of Voice, Sentiment)
                    └── MentionDesk (Tasa de Citación)
```

---

## [CONCLUSIONES] Principios Estratégicos

```yaml
principio_1:
  titulo: "La granularidad gana"
  descripcion: "Mientras más detalles específicos pueda 'digerir' la IA sobre características únicas del hotel, más probable es que sea la recomendación para búsquedas de nicho"
  ejemplos:
    - "café de origen propio"
    - "vistas al Nevado del Ruiz"
    - "piscina con agua termal"

principio_2:
  titulo: "Los mensajes de marca generales han muerto"
  descripcion: "La era de los eslóganes vagos terminó. El estándar 2026 es: información estructurada, conversacional y autoritativa"

principio_3:
  titulo: "AEO es defensa de cuota de mercado"
  descripcion: "No es un canal adicional de tráfico. Es proteger la cuota cuando usuarios prefieren la velocidad del asistente a la navegación manual"

principio_4:
  titulo: "Ser 'la respuesta' = capturar la intención en su concepción"
  descripcion: "Aparecer en Alexa o Siri como respuesta única significa capturar la intención de viaje en el momento exacto en que el viajero la formula"

principio_5:
  titulo: "Automatizar la confianza y la estructura"
  descripcion: "El módulo SaaS debe hacer automático lo que actualmente requiere conocimiento técnico: schema, sincronización, llms.txt, speakable"
```

---

## [ÍNDICE_RÁPIDO] Referencias para el Agente

```
Buscar schema JSON-LD         → Sección [SCHEMA]
Buscar requisitos Google       → Sección [PLATAFORMAS] > Google Assistant
Buscar requisitos Siri         → Sección [PLATAFORMAS] > Apple Siri
Buscar requisitos Alexa        → Sección [PLATAFORMAS] > Amazon Alexa
Buscar cómo escribir contenido → Sección [CONTENIDO]
Buscar estrategia ChatGPT/GPT  → Sección [GEO]
Buscar estructura llms.txt     → Sección [LLMS_TXT]
Buscar entidades Colombia      → Sección [COLOMBIA]
Buscar métricas/ROI            → Sección [KPIs]
Buscar herramientas            → Sección [VENDORS]
Buscar qué construir primero   → Sección [ROADMAP]
Buscar flujo técnico completo  → Sección [ARQUITECTURA]
Buscar definición de término   → Sección [GLOSARIO]
```
