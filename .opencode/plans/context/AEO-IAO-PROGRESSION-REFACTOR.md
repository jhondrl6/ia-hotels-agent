# Contexto: Refactor 4 Pilares SEO/GEO/AEO/IAO — Arquitectura Correcta

**Fecha:** 2026-04-11
**Estado:** Análisis conceptual completo. Pendiente planificación de implementación.
**Alcance:** Redefinir la arquitectura de scores de visibilidad del sistema iah-cli.

---

## 1. PROBLEMA IDENTIFICADO

El código actual trata GEO, AEO, SEO e IAO como **pilares paralelos independientes**, cada uno con su propio score. Esto es conceptualmente incorrecto.

### Definiciones de referencia — Los 4 Pilares

| Sigla | Nombre | ¿PARA QUÉ SIRVE? |
|:---|:---|:---|
| **SEO** | Search Engine Optimization | **Para que te ENCUENTREN.** Aparecer en la lista de resultados de Google. Es la base de la visibilidad web. |
| **GEO** | Geographic Optimization | **Para que te UBIQUEN.** Atraer clientes físicos que están cerca y tienen intención inmediata de compra/visita. |
| **AEO** | Answer Engine Optimization | **Para que te CITEN.** Ser la fuente rápida de un dato concreto (horarios, precios, definiciones) sin que el usuario navegue. |
| **IAO** | Intelligent Agent Optimization | **Para que te RECOMIENDEN.** Ser la fuente confiable que la IA usa para razonar, comparar y sugerir soluciones complejas. |

### Ejemplo integrado (cafetería)

| Pilar | Query del usuario | Qué pasa |
|:---|:---|:---|
| **SEO** | "cafeterías con wifi en Pereira" | Apareces en top 10 de Google orgánico |
| **GEO** | "cafeterías cerca de mí" / mira el mapa | Sales en Google Maps con reseñas, fotos, horario |
| **AEO** | Siri: "¿A qué hora cierra El Grano Local?" | Siri lee tu ficha estructurada: "Cierra a las 8:00 PM" |
| **IAO** | ChatGPT: "Lugar tranquilo para trabajar 3h cerca de la UTP" | La IA analiza reseñas/web/foros y TE RECOMIENDA a ti |

### Diferencia crítica AEO vs IAO

- **AEO** = dato factual, directo, corto. Ej: "¿Horario?" → "8am-8pm". El usuario obtiene el dato y listo.
- **IAO** = síntesis, razonamiento, recomendación personalizada. Ej: "¿Dónde trabajar?" → La IA compara, analiza y te elige.

**No son lo mismo.** AEO es para consultas simples. IAO es para decisiones complejas.

### El error del código actual (3 errores concretos)

**Error 1:** IAO eliminado como "redundante con AEO" (v4.21.0).
> Justificación en código: "ambos median infraestructura de datos estructurados"

Falso. AEO e IAO NO son redundantes. AEO mide optimización para Google (buscador). IAO mide optimización para LLMs (agentes). Son canales diferentes.

**Error 2:** AEO mide infraestructura (schema válido, OG tags) en lugar de resultado (¿capturas posición cero?).
> Schema es un MEDIO para lograr AEO, no AEO en sí mismo.

**Error 3:** Citabilidad está dentro de AEO, cuando es concepto IAO.
> `_calculate_aeo_score()` incluye `citability.overall_score` — eso mide confianza para IA, no posición cero en Google.

---

## 2. ARQUITECTURA CORRECTA — 4 Pilares Complementarios con Dependencias

```
SEO (base)  ──→  AEO (construye sobre SEO)  ──→  IAO (construye sobre AEO)
    │                   │                              │
    └─── GEO (pilar lateral, complementario a todos) ──┘
```

**Regla fundamental:** Cada pilar de la progresión requiere el anterior.
- Sin SEO base → no puedes optimizar para posición cero (AEO)
- Sin AEO → no tienes estructura para que la IA te recomiende (IAO)
- GEO es complementario: necesitas presencia local para CUALQUIER pilar

### SEO — Para que te ENCUENTREN
- ¿Apareces en resultados de Google cuando buscan tu categoría?
- Métricas actuales en código: has_own_website, mobile_speed (LCP/CLS), schema básico
- Métricas faltantes: posición en SERPs, CTR orgánico, indexación, meta descriptions, heading structure

### GEO — Para que te UBICQUEN
- ¿Apareces en Google Maps cuando buscan cerca de ti?
- Métricas actuales en código: GBP rating, reviews, fotos, horarios, website (correcto)
- Métricas faltantes: NAP consistency verificada, Google Posts frequency, Q&A respondidas

### AEO — Para que te CITEN
- ¿Google te extrae como respuesta directa para preguntas factuales?
- **NO debe medir solo schema válido** — debe medir si efectivamente capturas snippets/respuestas
- Métricas faltantes: featured snippets capturados, "People also ask" presence, speakable schema, cobertura de queries factuales (horario, precio, definición)
- Lo que el código mide HOY como "AEO" es solo infraestructura parcial (schema + OG)

### IAO — Para que te RECOMIENDEN
- ¿ChatGPT/Perplexity te menciona cuando piden recomendaciones complejas?
- **Debe ser restaurado** — fue eliminado incorrectamente en v4.21.0
- Métricas faltantes: menciones en LLMs, fuentes citadas, tráfico referral desde plataformas de IA, schema avanzado (Entity, SameAs), presencia en fuentes que LLMs rastrean (foros, PDFs técnicos, reseñas estructuradas)
- Lo que el código mide HOY como "citabilidad" debería estar aquí, NO en AEO

---

## 3. ESTADO ACTUAL DEL CÓDIGO (mapeo de métricas)

### Archivos clave

| Archivo | Rol actual |
|---|---|
| `data_models/aeo_kpis.py` | Modelos de datos AEOKPI, VoiceReadinessScore, AEOKPIs, IndirectTrafficMetrics |
| `modules/commercial_documents/v4_diagnostic_generator.py` | `_calculate_aeo_score()` (L604), `calcular_cumplimiento()` (L75), `_extraer_elementos_de_audit()` (L1803) |
| `modules/analyzers/gap_analyzer.py` | Recomendación de paquetes basada en gaps (GEO + AEO como 2 pilares) |
| `modules/generators/report_builder.py` | Renderizado de scorecards 4-pilares (GEO, AEO, SEO, IAO en texto) |
| `scripts/update_benchmarks.py` | `calculate_aeo_score()`, `calculate_geo_score()`, `calculate_seo_score()` — promedios regionales |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Template comercial: presenta GEO, IAO, AEO, SEO como servicios paralelos |
| `modules/commercial_documents/data_structures.py` | `ValidationSummary` con `score_tecnico` (CHECKLIST_IAO), `score_ia` |

### AEO score actual (`_calculate_aeo_score`, L604)

4 componentes × 25pts = 100pts:
- Schema Hotel válido (25pts)
- FAQ Schema válido (25pts)
- Open Graph detectado (25pts)
- Citabilidad >= 70 (25pts)

**Problema:** "Citabilidad" es concepto IAO, no AEO. Está mal ubicado.

### CHECKLIST_IAO actual (`calcular_cumplimiento`, L75)

12 elementos con pesos:
- ssl (10), schema_hotel (15), schema_reviews (15), LCP_ok (10), CLS_ok (5)
- contenido_extenso (10), open_graph (5), schema_faq (8), nap_consistente (7)
- imagenes_alt (5), blog_activo (5), redes_activas (5)

**Problema:** Es un checklist técnico sin alineación conceptual a progresión. Mezcla elementos de SEO (LCP, CLS, ssl), AEO (schema, OG), GEO (nap) e IAO (contenido_extenso) sin distinguir capas.

### Métricas compartidas (redundancia)

| Métrica | Aparece en |
|---|---|
| `schema_hotel` | SEO score, AEO score, CHECKLIST_IAO |
| `schema_faq` | SEO score, AEO score, CHECKLIST_IAO |
| `open_graph` | AEO score, CHECKLIST_IAO |
| `LCP/CLS` | SEO score (mobile_speed), CHECKLIST_IAO |

### Historial de IAO en el código

- Existió como score separado hasta v4.21.0
- Eliminado: `_calculate_iao_score()`, `_calculate_score_ia()`, `_calculate_voice_readiness_score()`
- Aún persiste en:
  - Template comercial: "Visibilidad en ChatGPT (IAO)" (propuesta_v6_template.md L48)
  - CHECKLIST_IAO (nombre de la estructura de datos)
  - `score_tecnico` en ValidationSummary
  - Referencias en CHANGELOG.md, VERSION.yaml, REGISTRY.md
  - Archivos históricos en archives/outputs/

---

## 4. IMPACTO DEL REFACTOR

### Tests afectados (385 tests actuales, 0 regresiones)

| Archivo test | Qué testeaba IAO/AEO |
|---|---|
| `tests/commercial_documents/test_aeo_score.py` | `_calculate_aeo_score()` con 4 componentes |
| `tests/data_validation/test_aeo_kpis.py` | Modelos AEOKPI, AEOKPIs |
| `tests/asset_generation/test_fase_b_aeo_voice.py` | Voice readiness |
| `tests/test_audit_alignment.py` | Paquete "pro_aeo", "Elite IAO" |

### Variables de template que cambiarían

Actuales en `_prepare_template_data()`:
- `aeo_score`, `aeo_status`, `aeo_regional_avg`
- `seo_score`, `seo_status`, `seo_regional_avg`
- `schema_infra_score`, `schema_infra_status`
- Eliminadas: `iao_score`, `iao_status`, `voice_readiness_score`, `voice_readiness_status`

Necesarias en modelo de 4 pilares:
- `seo_score` (para que te ENCUENTREN)
- `geo_score` (para que te UBICQUEN)
- `aeo_score` (para que te CITEN — NO solo schema)
- `iao_score` (para que te RECOMIENDEN — restaurar)

### Alineación comercial existente (ya es correcta)

El template comercial `propuesta_v6_template.md` YA presenta los 4 pilares correctamente:

| Servicio en template | Pilar conceptual |
|---|---|
| Google Maps Optimizado (GEO) | Para que te UBIQUEN |
| Visibilidad en ChatGPT (IAO) | Para que te RECOMIENDEN |
| Búsqueda por Voz (AEO) | Para que te CITEN |
| SEO Local (SEO) | Para que te ENCUENTREN |

**El problema NO está en la presentación comercial, sino en la implementación técnica.** El cliente ya recibe la narrativa correcta. Lo que falta es que el código mida cada pilar con métricas alineadas a su propósito real.

### Paquetes comerciales afectados

En `modules/utils/benchmarks.py`:
- "Pro AEO" → ¿renombrar o redefinir?
- "Pro AEO Plus" → incluye IAO
- "Elite IAO" → legado, precio 7,500,000 COP

En `modules/analyzers/gap_analyzer.py`:
- Mapeo de pain a paquete: `"schema_faltante": "Pro AEO"`
- Modelo de 2 pilares: gap_geo + gap_aeo → ¿cómo reestructurar a 4?

---

## 5. VEREDICTO DE VIABILIDAD (Investigación completada 2026-04-11)

### CONCEPTUALIZACION: CORRECTA

La progresion SEO -> AEO -> IAO con GEO como pilar lateral es conceptualmente solida.
Las definiciones de cada pilar son precisas y comercialmente claras.

**VEREDICTO: VIABLE, con matices criticos.**

---

### 5A. CONVERGENCIA CON ESTRATEGIA OTA (RESPUESTA: CONVERGE TOTALMENTE)

Los 4 pilares SON el mecanismo de entrega para reducir costos OTA. Son inseparables:

| Pilar | Como reduce OTA | Canal que captura |
|---|---|---|
| SEO | Hotel aparece en Google antes que Booking.com | Busqueda web organica |
| GEO | Hotel aparece en Maps, viajero reserva directo | Busqueda local "cerca de mi" |
| AEO | Hotel es la respuesta directa (no link a OTA) | Voz y snippets Google |
| IAO | ChatGPT recomienda el hotel directo, sin OTA | Recomendacion IA |

El motor financiero (CAPA 1/2A/2B) calcula todo en funcion de comisiones OTA:
- CAPA 1: `ota_nights x ADR x commission_rate` = perdida mensual verificable
- CAPA 2A: ahorro por shift OTA->directo (10% realista, 20% optimista)
- CAPA 2B: nueva revenue por visibilidad IA (5% realista, 10% optimista)

El refactor NO es tangencial. Es la correccion del "como" tecnico para que la promesa
comercial (reducir OTA 25% en 6 meses) tenga metricas reales detras.

---

### 5B. ESTADO REAL DEL CODIGO (hallazgos del audit)

#### Fuentes de datos REALES (funcionan hoy):

| Fuente | Que provee | Estado |
|---|---|---|
| Web scraping | Schema, OG, alt, contenido | FUNCIONA |
| Google Places API | GBP geo_score, rating, reviews, NAP | FUNCIONA |
| PageSpeed API | Mobile/desktop, LCP, CLS, FID | FUNCIONA |
| Rich Results API | Validacion schema | FUNCIONA |

#### Fuentes STUB/MOCK (NO funcionan, retornan None):

| Fuente | Que proveeria | Estado |
|---|---|---|
| ProfoundClient | AI Visibility, Share of Voice, Citation Rate | STUB - NotImplementedError |
| GA4 Client | Trafico indirecto | ADVISORY - necesita credentials |
| GSC Client | Keywords, CTR, posiciones | ADVISORY - necesita GSC_SITE_URL |
| SemrushClient | Datos competencia | Presumiblemente STUB |

#### Metricas HEURISTICAS (sin datos reales):

| Metrica | Como se calcula | Realidad |
|---|---|---|
| `estimated_ia_visibility` | Heuristica GSC CTR+posicion | Sin datos reales |
| `iao_qualitative` | 6-signal scoring de checklist | Es el CHECKLIST_IAO reetiquetado |

#### Hallazgo critico: SISTEMA DUAL de scoring

Existen DOS sistemas paralelos que miden cosas similares de forma diferente:
1. **CHECKLIST_IAO** (12 elementos, 100pts) -> usado para recomendar paquetes (basico/avanzado/premium)
2. **4-Pilar scores** (GEO/Competitive/SEO/AEO, cada uno 0-100) -> usado para display en diagnostico

Ambos usan las mismas metricas (schema, OG, LCP) pero con pesos distintos.
El refactor DEBE unificar estos en un solo sistema coherente.

---

### 5C. LECCION DE SIRI (por qué falló antes y no repetir)

En sesiones anteriores se intentó implementar medicion directa de voz (Siri/Alexa).
Resultado: NO existe API para consultar qué responde Siri/Alexa programáticamente.
No hay "Siri Search Console". No hay "Alexa Rank Tracker".

**POR QUÉ NO REPETIR ESE ERROR:**
- Voice assistants NO proveen feedback de que responden
- Simular consultas de voz con TTS+STT es hacky e inscalable
- Cada assistant tiene fuentes distintas (Siri=Apple Maps+Google, Alexa=Bing+Yelp, GoogleAssistant=Knowledge Graph)

**ALTERNATIVA VIABLE (proxy measurement):**
En lugar de medir lo que Siri RESPONDE, medimos los INPUTS que alimentan a Siri:
1. Featured snippet capture en Google (si Google te da posicion cero, Siri/GoogleAssistant usan ese dato)
2. Apple Business Connect listing completo (Siri usa Apple Maps)
3. Google Business Profile completo (Google Assistant usa GBP)
4. Schema.org FAQ + LocalBusiness (voz extrae datos estructurados)
5. Speakable markup (schema especifico para voz)

Esto es medible, gratuito, y ataca la causa en lugar del sintoma.

---

### 5D. APIs DISPONIBLES PARA MEDIR AEO/IAO REALES

#### AEO (Position Zero / Featured Snippets):

| API | Que mide | Costo | Viabilidad iah-cli |
|---|---|---|---|
| **SerpAPI** | Featured snippets, SERP position | Free: 100/mes, $50/mes | MEJOR OPCION para empezar |
| Google Search Console | Clicks, impressions, CTR | GRATIS | Ya existe como ADVISORY |
| Serpstack | SERP scraping | Free: 100/mes, $29/mes | Alternativa |

#### IAO (Menciones en LLMs):

| API | Que mide | Costo | Viabilidad iah-cli |
|---|---|---|---|
| **OpenAI** via **OpenRouter** | Prompt "mejores hoteles en X", parsear menciones | ~$0.01-0.03/query | VIA OPENROUTER UNICAMENTE, nunca directo |
| **Gemini API** directo | Mencion en respuestas Gemini | Free tier generoso (60/min) | GRATIS para empezar |
| **Perplexity API** | Respuestas con citations, verificar si hotel es citado | ~$0.02-0.05/query | MEJOR para IAO (cita fuentes) |
| Profound (SaaS) | AI visibility score | $99-299/mes | DEMASIADO CARO para hoteles boutique |

**REGLA CRITICA: OpenAI SIEMPRE via OpenRouter. NUNCA importar openai SDK directo.**
- Modulo existente `ia_tester.py` usa `from openai import OpenAI` directo (gpt-4) -> MIGRAR a OpenRouter
- Nuevo LLM Mention Checker: nacer con OpenRouter desde el inicio
- OPENAI_API_KEY en .env: evaluar reemplazar por OPENROUTER_API_KEY
- Gemini: via Google API directo (propio, no OpenRouter)

#### Costo estimado total por hotel: $3-8 USD/mes
- OpenAI: ~$1-3/mes (50-100 queries)
- Gemini: GRATIS (free tier)
- Perplexity: ~$2-5/mes
- SerpAPI: GRATIS (100/mes suficiente para 1 hotel)

---

### 5E. MATRIZ DE RIESGO-BENEFICIO DEL REFACTOR

| Aspecto | Riesgo | Beneficio | Veredicto |
|---|---|---|---|
| Separar AEO de SEO | Medio: cambia scores que impactan comercial | Alto: metricas honestas, cliente ve progreso real | PROCEDER |
| Restaurar IAO | Bajo: no existia, solo se agrega | Alto: es la promesa comercial "ChatGPT te recomienda" | PROCEDER |
| Medir AEO real (snippets) | Medio: requiere API nueva (SerpAPI) | Alto: validar si optimizacion funciona | PROCEDER con SerpAPI free tier |
| Medir IAO real (LLM mentions) | Medio: requiere implementar LLM checker | Alto: respuesta a "funciona?" del cliente | PROCEDER con OpenAI/Gemini |
| Unificar CHECKLIST + 4-Pilar | Alto: cambia paquetes comerciales | Critico: elimina confusion interna | PROCEDER con cuidado |
| Medicion directa voz (Siri) | Alto: ya fallo, no hay API | Bajo: proxy measurement es suficiente | NO PROCEDER |

---

### 5F. LO QUE YA TENEMOS Y SIRVE (reutilizar)

| Activo | Reutilizable? | Como |
|---|---|---|
| `citability_scorer.py` | SI | Mide calidad de contenido para IA -> pertenece a IAO, no AEO |
| `ia_readiness_calculator.py` | SI | 6 componentes加权 -> base del score IAO restaurado |
| `ai_crawler_auditor.py` | SI | Verifica robots.txt para IA crawlers -> componente IAO |
| `llmstxt_generator.py` | SI | Genera llms.txt -> activo IAO directo (FREE, alta adopcion emergente) |
| `data_aggregator.py` | SI | Unifica GA4+GSC -> puede alimentar metricas AEO/IAO cuando haya credenciales |
| `profound_client.py` | PARCIALMENTE | Interface correcta, implementacion STUB -> reemplazar con LLM mention checker propio |
| `aeo_kpis.py` (data models) | SI | Modelos de datos correctos, solo reasignar campos |

### 5G. LO QUE FALTA CONSTRUIR

| Componente | Prioridad | Esfuerzo | Descripcion |
|---|---|---|---|
| LLM Mention Checker | ALTA | 2-3 dias | Modulo que consulta OpenAI/Gemini/Perplexity y detecta menciones del hotel |
| AEO Snippet Tracker | ALTA | 1-2 dias | Modulo que via SerpAPI verifica featured snippets capturados |
| Score Progression Model | ALTA | 1 dia | Logica SEO->AEO->IAO con gates/degradacion |
| CHECKLIST redistribution | MEDIA | 1 dia | Reasignar 12 elementos a 4 pilares coherentes |
| Package remapping | MEDIA | 0.5 dias | Actualizar pain->package con nuevos pilares |
| Voice Readiness Score (proxy) | BAJA | 1 dia | Scoring basado en inputs (GBP, schema, Apple Maps) NO en query directa |
| Template ajustes | BAJA | 0.5 dias | Ajustar nombres de variables en diagnostico/propuesta |

---

## 6. DECISIONES DE DISENO RESUELTAS

### 6.1 Redistribucion CHECKLIST_IAO -> 4 Pilares

**SEO (base - "que te ENCUENTREN"):**
- ssl (10pts), LCP_ok (10pts), CLS_ok (5pts), schema_hotel_base (15pts), imagenes_alt (5pts)
- Total: 45pts (ampliar con nuevas metricas SERP para llegar a 100)

**GEO (lateral - "que te UBICQUEN"):**
- nap_consistente (15pts), redes_activas (10pts), schema_reviews (15pts), geo_score_gbp (30pts), fotos_gbp (15pts), horario_gbp (15pts)
- Total: 100pts (ya existe geo_score funcional)

**AEO (posicion cero - "que te CITEN"):**
- schema_faq (20pts), open_graph (10pts), speakable_schema (15pts), featured_snippet_capture (25pts), people_also_ask (15pts), contenido_factual (15pts)
- Total: 100pts (requiere SerpAPI para medicion real de snippets)

**IAO (recomendacion IA - "que te RECOMIENDEN"):**
- citability_score (20pts), llms_txt_exists (10pts), crawler_access (15pts), llm_mention_rate (25pts), contenido_extenso (10pts), brand_signals (10pts), ga4_indirect (10pts)
- Total: 100pts (requiere LLM Mention Checker para medicion real)

### 6.2 Modelo de Score: OPCION A (independientes con advertencia)

- Cada pilar: score 0-100 independiente
- NO gate booleano (no bloquear metricas al cliente)
- SI advertencia visual: "Tu AEO es X pero tu SEO base es Y - mejorar SEO potenciara AEO"
- Score global: ponderado SEO(25%) + GEO(25%) + AEO(25%) + IAO(25%) = "Visibilidad Digital"

**Justificacion:** El cliente necesita ver TODOS los scores para tomar decisiones.
Un gate booleano esconderia informacion. La advertencia educa sin bloquear.

### 6.3 CHECKLIST_IAO: REEMPLAZAR por 4 checklists independientes

- Eliminar CHECKLIST_IAO como nombre
- Crear: CHECKLIST_SEO, CHECKLIST_GEO, CHECKLIST_AEO, CHECKLIST_IAO
- Cada uno con sus elementos y pesos propios
- El score_tecnico actual (CHECKLIST_IAO) se convierte en el promedio ponderado de los 4

### 6.4 Backwards compatibility

- Outputs existentes NO se regeneran
- Nuevos outputs usan estructura nueva
- Si archivo legacy referencia scores viejos, se marca como deprecated en documentacion
- Paquetes comerciales se renombran en NUEVA version (no romper los actuales hasta release)

### 6.5 Voice Readiness: PROXY, no medicion directa

- NO intentar query directa a Siri/Alexa (ya fallo antes)
- SI construir "Voice Readiness Proxy Score" basado en:
  1. Google featured snippet capture (SerpAPI)
  2. GBP completeness (ya tenemos)
  3. Apple Business Connect listing (manual/check)
  4. Schema.org FAQ + LocalBusiness (ya tenemos)
  5. Speakable markup (nuevo check)
- Esto mide los INPUTS que alimentan voz, no la salida

---

## 7. REGLAS PARA LA SESION DE PLANIFICACION

1. **Una fase por sesion** (regla del proyecto)
2. **Priorizar metricas con fuente de datos REAL**: no disenar scores sin pipeline de datos
3. **No romper outputs existentes**: versionar si es necesario
4. **Mantener presentacion comercial intacta**: template v6 ya presenta 4 pilares correctos
5. **Log de fase obligatorio**: `scripts/log_phase_completion.py`
6. **NO implementar medicion directa de voz**: usar proxy measurement unicamente
7. **Costo API explicito por componente**: cada metrica nueva debe declarar su costo mensual

---

## 8. FASES SUGERIDAS PARA IMPLEMENTACION

| Fase | Nombre | Alcance | Riesgo |
|---|---|---|---|
| FASE-A | Score Redistribution | Reasignar CHECKLIST_IAO a 4 pilares, unificar scoring dual | Medio |
| FASE-B | AEO Real Measurement | Integrar SerpAPI para featured snippets,重构 _calculate_aeo_score | Medio |
| FASE-C | IAO Restoration + LLM Checker | Restaurar score IAO, implementar LLM Mention Checker | Medio-Alto |
| FASE-D | Package & Template Alignment | Actualizar paquetes, templates, gap_analyzer a 4 pilares | Bajo |
| FASE-E | Voice Readiness Proxy | Score proxy basado en inputs (no medicion directa) | Bajo |
| FASE-F | Documentation & Validation | GUIA_TECNICA, CHANGELOG, REGISTRY, test regression suite | Bajo |

---

## 9. REFERENCIAS

- Definiciones AEO/IAO: proporcionadas por usuario 2026-04-11
- Consolidacion AEO/IAO v4.21.0: `docs/GUIA_TECNICA.md` L335-372
- CHANGELOG FASE-F (limpieza IAO): `CHANGELOG.md` L227-247
- VERSION.yaml: `FASE-IAO-06` (Analytics Transparency), `GAP-IAO-01-05` (GA4 Integration)
- Template comercial v6: `modules/commercial_documents/templates/propuesta_v6_template.md`
- CHECKLIST_IAO mapping: `modules/commercial_documents/v4_diagnostic_generator.py` L52-63
- Audit de codigo AEO/IAO: sesion 20260411_201717_ac51ef
- APIs investigacion: SerpAPI (featured snippets), OpenAI/Gemini/Perplexity (LLM mentions), llms.txt standard
- Motor financiero OTA: `modules/financial_engine/scenario_calculator.py` CAPA 1/2A/2B
- Pain-Solution mapping: `modules/commercial_documents/pain_solution_mapper.py` (low_ota_divergence = P1)
