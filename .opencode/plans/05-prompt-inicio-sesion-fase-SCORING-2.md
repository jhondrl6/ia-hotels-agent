# 05-prompt-inicio-sesion-fase-SCORING-2.md

> **FASE:** FASE-SCORING-2
> **Objetivo:** Actualizar template y crear `docs/scoring_methodology.md`
> **Contexto previo:** FASE-SCORING-1 completada ✅ — funciones Python implementadas

---

## TAREAS

### 1. Leer estado de FASE-SCORING-1

Abre `modules/commercial_documents/v4_diagnostic_generator.py` y verifica que `_build_scoring_breakdown()` y `_build_excluded_factors_section()` existen (buscar con grep).

### 2. Actualizar `diagnostico_v6_template.md`

Lee el template completo:

```bash
cat modules/commercial_documents/templates/diagnostico_v6_template.md
```

**Cambios necesarios:**

**A) Frontmatter (líneas 1-15):** Agregar después del campo `financial_ota_commission_real`:

```yaml
scoring_methodology_url: ./scoring_methodology.md
```

**B) Debajo de la tabla de scores (después de línea 58):** Agregar:

```
${geo_score_breakdown}

> ⚠️ **Nota sobre el score GEO**: El desglose arriba usa la metodología del checklist GEO (calcular_score_geo), que pondera 6 factores técnicos. El score en la tabla principal (${geo_score}) puede diferir porque viene directamente del geo_score de Google Business Profile, que usa su propio algoritmo. Ambos son válidos — miden aspectos complementarios de tu presencia en Google Maps.

${excluded_factors_section}
```

**C) Al final del documento (antes del footer/cierre):** Agregar nueva sección:

```
---

## 📐 Metodología de Scoring

El score de Visibilidad Digital se calcula sobre 4 pilares independientes (0-100 c/u):

| Pilar | Qué mide | Qué NO mide |
|-------|---------|-------------|
| **SEO Local** | SSL, Schema Hotel, Velocidad, Alt text, Blog | Contenido editorial, backlinks |
| **GEO** | Presencia en Google Maps, fotos, NAP, horario | Tasa de respuesta a reseñas, tiempo de respuesta, calidad de respuestas |
| **AEO** | FAQ Schema, OG Tags, Schema Hotel detallado, Contenido factual | Volumen de tráfico, conversiones |
| **IAO** | Citabilidad, acceso de crawlers IA, llms.txt, señales de marca | Tráfico directo, Revenue, NPS |

> ⚠️ **Divergencia GEO**: El score GEO mostrado en la tabla principal proviene directamente del `geo_score` de Google Business Profile (algoritmo de Google). El desglose mostrado arriba usa la metodología del checklist GEO de iah-cli (6 factores con pesos fijos). Ambos scores pueden diferir — son mediciones complementarias, no redundantes. El checklist GEO evalúa factores técnicos que tú controlas; el GBP score refleja la evaluación de Google.

**Referencias:** [Metodología completa de scoring](./scoring_methodology.md)
```

### 3. Crear `docs/scoring_methodology.md`

Crea el archivo con:

```markdown
# Metodología de Scoring — Visibilidad Digital

**Versión:** 1.0  
**Última actualización:** 2026-05-02  
**Documento hijo de:** `diagnostico_v6_template.md`

---

## Visión General

El score de Visibilidad Digital se calcula sobre 4 pilares independientes, cada uno en escala 0-100:

- **SEO Local** (Para que te ENCUENTREN): 25% del score global
- **GEO** (Para que te UBICQUEN): 25% del score global
- **AEO** (Para que te CITEN): 25% del score global
- **IAO** (Para que te RECOMIENDEN): 25% del score global

**Score Global** = promedio simple de los 4 pilares (peso igual 25% c/u)

---

## Pilar SEO Local

**Objetivo:** Medir qué tan bien posiciona Google tu sitio para búsquedas locales.

### Factores medidos (100 pts total)

| Factor | Peso | Descripción |
|--------|------|-------------|
| SSL | 15% | Certificado HTTPS vigente |
| Schema Hotel | 20% | Schema.org markup para hoteles |
| LCP_ok | 20% | Largest Contentful Paint < 2.5s |
| CLS_ok | 10% | Cumulative Layout Shift < 0.1 |
| imagenes_alt | 15% | Texto alternativo en imágenes |
| blog_activo | 10% | Blog con contenido reciente |
| schema_reviews | 10% | Schema de reseñas presente |

### Factores NO medidos

- Contenido editorial (profundidad de artículos)
- Perfil de backlinks
- Domain authority externo

---

## Pilar GEO (Google Business Profile)

**Objetivo:** Medir presencia y consistencia en Google Maps y GBP.

### Factores medidos (100 pts total)

| Factor | Peso | Descripción |
|--------|------|-------------|
| nap_consistente | 15% | Nombre, dirección, teléfono consistentes |
| redes_activas | 10% | Redes sociales con actividad reciente |
| geo_score_gbp | 30% | Score de presencia en Google Maps |
| fotos_gbp | 15% | Fotos de calidad en GBP (mínimo 10) |
| horario_gbp | 15% | Horario correcto y actualizado |
| schema_reviews_geo | 15% | Reseñas con schema y ubicación |

### Factores NO medidos

- **Tasa de respuesta a reseñas** — el % de reseñas respondidas
- **Tiempo de respuesta** — cuánto tarda en responder a reseñas
- **Calidad de las respuestas** — redactacción de las respuestas
- **Engagement rate** — interacción con las reseñas
- **Review recency** — antigüedad de las reseñas más nuevas
- **Review velocity** — velocidad de llegada de reseñas

> **Nota:** Un hotel con 203 reseñas, 4.5★ y respuesta en <24h puede bajar su score GEO si le faltan fotos en GBP o tiene inconsistencia NAP. El score no refleja la calidad de su engagement con reseñas.

> ⚠️ **Dual-score GEO**: iah-cli calcula DOS scores GEO: (1) el `geo_score` de Google Business Profile (mostrado en la tabla principal del diagnóstico), y (2) el score del checklist GEO (mostrado en el desglose). El checklist evalúa 6 factores técnicos con pesos fijos; el GBP score es un algoritmo propietario de Google. Ambos scores pueden diferir — no son redundantes, son complementarios.

---

## Pilar AEO (Answer Engine Optimization)

**Objetivo:** Medir qué tan bien puede una IA responder preguntas sobre tu negocio.

### Factores medidos (100 pts total)

| Factor | Peso | Descripción |
|--------|------|-------------|
| schema_faq | 25% | FAQ Schema para preguntas frecuentes |
| open_graph | 15% | Open Graph tags para social sharing |
| schema_hotel_aeo | 15% | Schema Hotel detallado (servicios, habitaciones) |
| contenido_factual | 20% | Horarios, precios, servicios accesibles |
| speakable_schema | 10% | Schema speakable para contenido voice-friendly |
| imagenes_alt_aeo | 15% | Alt text descriptivo para extracción visual |

### Factores NO medidos

- Volumen de tráfico
- Conversiones (reservas, llamadas)

---

## Pilar IAO (IA Optimization)

**Objetivo:** Medir qué tan bien indexan y citan las IAs (ChatGPT, Perplexity) tu negocio.

### Factores medidos (100 pts total)

| Factor | Peso | Descripción |
|--------|------|-------------|
| citability_score | 20% | Score de citabilidad (fuentes disponibles) |
| contenido_extenso | 15% | Contenido KB > 3000 palabras |
| llms_txt_exists | 15% | Archivo llms.txt presente |
| crawler_access | 15% | Acceso para crawlers de IA |
| brand_signals | 10% | Señales de marca (SameAs, enlaces sociales) |
| ga4_indirect | 10% | Tráfico indirecto vía GA4 (señal advisory) |
| schema_advanced | 15% | Schema Entity + SameAs avanzado |

### Factores NO medidos

- Tráfico directo
- Revenue
- NPS (Net Promoter Score)

---

## Score Global

```
Score Global = (SEO + GEO + AEO + IAO) / 4
```

Los 4 pilares tienen peso igual (25% cada uno). No hay ponderación por importancia o dificultad.

---

## Limitaciones Conocidas

1. El score es un proxy de visibilidad, no una predicción de reservas.
2. Los factores excluidos (respuesta a reseñas, engagement) pueden tener impacto real en conversión que no se refleja en el score.
3. Los promedios regionales son referencias relativas, no umbrales absolutos.
4. El score no mide contenido de calidad, solo presencia técnica.

---

## Historial de Cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0 | 2026-05-02 | Versión inicial con breakdown de 4 pilares y factores excluidos |
