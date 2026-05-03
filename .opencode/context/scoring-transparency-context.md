# CONTEXTO: Scoring Transparency — GEO/AEO Scoring Methodology

**Creado:** 2026-05-02  
**Session anterior:** v4.38.0 — Feature Config Extraction  
**Problema referenciado:** `output/v4_complete/Analisis.md` — Área de oportunidad #4

---

## PROBLEMA A RESOLVER

El scoring GEO/AEO/SEO/IAO en iah-cli no es transparente sobre qué factores mide y cuáles excluye.

### Sintoma concrete (del ejercicio hotelero real)

- Hotel con 203 reviews, 4.5★, respuesta en <24h → GEO = 62/100
- El owner pregunta: "¿El score considera la calidad de respuestas a reseñas?"
- **Respuesta real:** No. Pero el diagnóstico no lo aclara.
- El score baja por fotos y NAP consistency, no por engagement con reviews.
- No existe un `scoring_methodology.md` linked desde el output.

### Problema sistematico

> El scoring usa metricas tecnicas (fotos, NAP, schema) pero no hay seccion de "que no mide". No existe un scoring_methodology.md linked desde el output que explique que pesa 20% vs que no esta en el radar.

---

## ESTADO ACTUAL DEL CODIGO

### Donde esta el scoring (fuente de verdad)

**Archivo:** `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py`

**Checklists definidos (lineas 149-191):**

```python
CHECKLIST_SEO = {
    "ssl":              15,
    "schema_hotel":      20,
    "LCP_ok":           20,
    "CLS_ok":           10,
    "imagenes_alt":     15,
    "blog_activo":      10,
    "schema_reviews":   10,
}  # Total: 100pts

CHECKLIST_GEO = {
    "nap_consistente":      15,
    "redes_activas":        10,
    "geo_score_gbp":        30,
    "fotos_gbp":            15,
    "horario_gbp":          15,
    "schema_reviews_geo":   15,
}  # Total: 100pts

CHECKLIST_AEO = {
    "schema_faq":           25,
    "open_graph":           15,
    "schema_hotel_aeo":     15,
    "contenido_factual":    20,
    "speakable_schema":      10,
    "imagenes_alt_aeo":     15,
}  # Total: 100pts

CHECKLIST_IAO = {
    "citability_score":     20,
    "contenido_extenso":    15,
    "llms_txt_exists":      15,
    "crawler_access":       15,
    "brand_signals":        10,
    "ga4_indirect":         10,
    "schema_advanced":      15,
}  # Total: 100pts
```

**Funciones de calculo (lineas 193-224):**
- `calcular_score_seo()` — linea 193
- `calcular_score_geo()` — linea 200
- `calcular_score_aeo()` — linea 207
- `calcular_score_iao()` — linea 214
- `calcular_score_global()` — linea 221 (promedio ponderado 4 pilares, peso igual 25% c/u)

### Donde se renderiza (template)

**Archivo:** `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/templates/diagnostico_v6_template.md`

**Tabla actual (lineas 52-57):**
```
|| **SEO Local** (Para que te ENCUENTREN) | ${seo_score}/100 | ${seo_regional_avg}/100 | ${seo_status} |
|| **GEO** (Para que te UBIQUEN) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
|| **AEO** (Para que te CITEN) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |
|| **IAO** (Para que te RECOMIENDEN) | ${iao_score}/100 | ${iao_regional_avg}/100 | ${iao_status} |
```

**Frontmatter actual (lineas 1-15):** No incluye link a scoring_methodology.

### Factores actualmente EXCLUIDOS del scoring GEO (no medidos)

1. `review_response_rate` — porcentaje de reseñas respondidas
2. `response_time` — tiempo de respuesta a reseñas
3. `response_quality` — calidad/redaccion de las respuestas
4. `engagement_rate` — interaccion con reseñas
5. `review_recency` — antiguedad de reseñas nuevas
6. `review_velocity` — velocidad de llegada de reseñas

### Factores EXCLUIDOS del scoring SEO

1. Contenido editorial (blog depth)
2. Perfil de backlinks
3. Domain authority externo

### Factores EXCLUIDOS del scoring AEO

1. Volumen de trafico
2. Conversiones

### Factores EXCLUIDOS del scoring IAO

1. Trafico directo
2. Revenue
3. NPS

---

## MOCK DE LA SALIDA ESPERADA

### Tabla de scores con breakdown

```
## 📊 ANALISIS ACTUAL: SU POSICION FRENTE A LA COMPETENCIA

### Score de Visibilidad Digital

|||| Indicador | Su Negocio | Promedio Regional | Estado |
||||-----------|------------|------------------|--------|
|| **SEO Local** (Para que te ENCUENTREN) | 58/100 | 55/100 | ✅ |
|| **GEO** (Para que te UBIQUEN) | 62/100 | 58/100 | ⚠️ |
|| **AEO** (Para que te CITEN) | 47/100 | 52/100 | 🔴 |
|| **IAO** (Para que te RECOMIENDEN) | 41/100 | 48/100 | 🔴 |

> **Desglose GEO 62/100** = Fotos(15%) + NAP Consistencia(15%) + Score GBP(30%) + Horario(15%) + Schema Reviews(15%) + Redes Activas(10%)

> **Este score NO mide:** tasa de respuesta a reseñas, tiempo de respuesta, calidad de las respuestas, engagement rate, ni antiguedad de reseñas nuevas.
```

### Nueva seccion al final del documento (antes del footer)

```
---

## 📐 Metodologia de Scoring

El score de Visibilidad Digital se calcula sobre 4 pilares independientes (0-100 c/u):

| Pilar | Que mide | Que NO mide |
|-------|---------|-------------|
| **SEO Local** | SSL, Schema Hotel, Velocidad, Alt text, Blog | Contenido editorial, backlinks |
| **GEO** | Presencia en Google Maps, fotos, NAP, horario | Tasa de respuesta a reseñas, tiempo de respuesta, calidad de respuestas |
| **AEO** | FAQ Schema, OG Tags, Schema Hotel detallado, Contenido factual | Volumen de trafico, conversiones |
| **IAO** | Citabilidad, acceso de crawlers IA, llms.txt, senales de marca | Trafico directo, Revenue, NPS |

> **Para el score GEO especificamente:** un hotel con 203 reseñas y respuesta <24h puede bajar su score por fotos faltantes o inconsistencia NAP — no por la calidad de su engagement con reseñas.

**Referencias:** [Metodologia completa de scoring](./scoring_methodology.md)
```

### Frontmatter sugerido

```yaml
---
scoring_methodology_url: ./scoring_methodology.md
scoring_pillars:
  seo: {total: 100, pillars: [...]}
  geo: {total: 100, pillars: [...], excluded: [...]}
  aeo: {total: 100, pillars: [...], excluded: [...]}
  iao: {total: 100, pillars: [...], excluded: [...]}
---
```

---

## ARCHIVOS A MODIFICAR

1. `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/v4_diagnostic_generator.py`
   - Agregar funcion `_build_scoring_breakdown(geo_score, elementos)` que retorne string con breakdown
   - Agregar funcion `_build_excluded_factors_section()` que retorne string con factores excluidos
   - Agregar template vars en `_prepare_template_data()`

2. `/mnt/c/Users/Jhond/Github/iah-cli/modules/commercial_documents/templates/diagnostico_v6_template.md`
   - Agregar `${geo_score_breakdown}` debajo de tabla de scores
   - Agregar `${excluded_factors_section}` antes del footer
   - Agregar `${scoring_methodology_url}` en frontmatter

3. `/mnt/c/Users/Jhond/Github/iah-cli/docs/scoring_methodology.md` **(NUEVO)**
   - Documento estatico con breakdown completo de cada pilar
   - Tabla de factores incluidos/excluidos por pilar
   - Ligado desde frontmatter del output

---

## CRITERIOS DE ÉXITO

1. Output del diagnostico muestra breakdown visible: "GEO 62/100 = Fotos(15%) + NAP(15%) + ..."
2. Seccion "Este score NO mide" visible debajo de la tabla de scores
3. Nueva seccion "Metodologia de Scoring" al final del documento
4. Link a `scoring_methodology.md` en frontmatter del output
5. Pregunta del owner ("¿El score considera la calidad de respuestas a reseñas?") respondida implicitamente por el documento sin necesidad de explicarla

---

## WORKFLOW A SEGUIR

Seguir `.agents/workflows/phased_project_executor.md`:
1 fase / sesion. Al terminar:
1. `python scripts/log_phase_completion.py --fase FASE-X --desc "..."`
2. `python scripts/sync_versions.py --check`
3. Verificar CHANGELOG.md y GUIA_TECNICA.md
4. `python scripts/run_all_validations.py --quick`

---

## COMANDOS DE REFERENCIA

```bash
# Test rapido del pipeline
cd /mnt/c/Users/Jhond/Github/iah-cli
python main.py v4complete --url https://amaziliahotel.com --region eje_cafetero --output output/test-scoring

# Generar diagnostico solo (sin assets)
python main.py stage --stage diagnostic --url https://amaziliahotel.com

# Ver validaciones
python scripts/run_all_validations.py --quick
```
