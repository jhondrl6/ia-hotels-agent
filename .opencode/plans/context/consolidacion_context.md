
# CONTEXTO COMPLETO: Consolidacion AEO/IAO

## ORIGEN DEL PROBLEMA

El diagnostico V6 genera un scorecard con estas filas:
```
| Google Maps (GEO)           | 72/100 | 55/100 | Superior |
| Perfil de Google Business   | 86/100 | 30/100 | Superior |
| Visibilidad en IA (AEO)     | --     | 15/100 | Pendiente |
| Optimizacion ChatGPT (IAO)  | 25/100 | 10/100 | Pendiente |
| SEO Local                   | 30/100 | 65/100 | Bajo |
```

**Problema**: AEO e IAO son redundantes. El `_calculate_iao_score()` sin GA4 hace fall back a `_calculate_schema_infra_score()`. O sea AEO y IAO miden la misma infraestructura pero se presentan como scores separados.

**Regla de negocio**: Si el diagnostico no tiene un Asset para resolver el dolor, no va. Si no puede medirlo con datos reales del audit, no genera score.

## DECISIONES ARQUITECTONICAS

1. **IAO eliminado**. No es un score valido. La "optimizacion para ChatGPT/Perplexity" es resultado de hacer bien el AEO, mas factores externos (citabilidad) que no se controlan con assets.

2. **Voice readiness eliminado**. El metodo `_calculate_voice_readiness_score()` ya retorna literalmente `"--"`. Nunca midio nada. SpeakableSchema es parte de AEO.

3. **AEO queda como score unico de infraestructura**. Mide Schema Hotel + FAQ + Reviews + Open Graph. Todo medible con el audit web. Tiene assets asociados.

4. **Scorecard consolidado**:
```
| Google Maps (GEO)           | XX/100 | 55/100 | ... |
| Perfil de Google Business   | XX/100 | 30/100 | ... |
| AEO - Infraestructura IA    | XX/100 | 15/100 | ... |
| SEO Local                   | XX/100 | 65/100 | ... |
```
(4 filas, no 5)

5. **GAP analyzer**: redistribuye la perdida entre 2 pilares (GBP + AEO) en vez de 3 (GBP + AEO + IAO).

6. **GA4**: no se toca la logica de GA4. Si eventualmente se configura, el IAO score desaparece igual, pero el AEO score puede enriquecerse con datos reales. Eso es trabajo de otra fase.

## MAPA DE ARCHIVOS AFECTADOS

### Fase 1 - Scorecard + Generator
- `modules/commercial_documents/v4_diagnostic_generator.py`:
  - Eliminar `_calculate_iao_score()` (linea 1145+)
  - Eliminar `_calculate_score_ia()` (linea 1163+)
  - Eliminar `_calculate_voice_readiness_score()` (linea 1137)
  - Eliminar `'iao_score'` y `'iao_status'` de `_prepare_template_data()`
  - Eliminar `'voice_readiness_score'` y `'voice_readiness_status'` de `_prepare_template_data()`
  - En `_inject_analytics()`, eliminar referencias a `iao_score`
  - Eliminar `_calculate_schema_infra_score()` (o renombrar a `_calculate_aeo_score` para claridad)
- `modules/commercial_documents/templates/diagnostico_v6_template.md`:
  - Eliminar linea 49: `Visibilidad en IA (AEO)`
  - Reemplazar linea 50: `Optimizacion ChatGPT` -> `AEO - Infraestructura para IAs`
  - Benchmark cambiar de 10/100 a 15/100 (el benchmark de AEO que ya existia)

### Fase 2 - GAP Analyzer
- `modules/analyzers/gap_analyzer.py`:
  - Eliminar `iao_benchmark`, `iao_score`, `gap_iao` (lineas 285-334 aprox)
  - Redistribuir `peso_iao` proporcionalmente a `peso_geo` y `peso_aeo`
  - Eliminar "Pilar 3: Momentum IA" de las brechas

### Fase 3 - Report Builder + Dead Code
- `modules/generators/report_builder.py`:
  - Eliminar `_calculate_iao_score()` (linea 1592)
  - Eliminar filas de IAO en scorecards que genera (lineas ~1298, 847, etc.)
  - Redistribuir pesos si tiene logica similar al gap_analyzer
- `modules/delivery/generators/aeo_metrics_gen.py`:
  - NO eliminar. Este modulo es tecnico/interno, no comercial.
  - SOLO tocar si genera conflictos con los cambios de Fase 1+2.

### Fase 4 - Release
- `CHANGELOG.md`: agregar entrada 4.21.0
- `REGISTRY.md`: registrar todas las fases
- Version en codigo si aplica

## REFERENCIAS TECNICAS

### ELEMENTO_KB_TO_PAIN_ID (v4_diagnostic_generator.py linea 40)
Mapea los elementos del checklist (medibles) a pain_ids y assets. Esta es la fuente de verdad de lo que SE PUEDE medir y SE PUEDE resolver:

```python
ELEMENTO_KB_TO_PAIN_ID = {
    "ssl":                ("no_ssl",              "ssl_guide",           None),
    "schema_hotel":      ("no_hotel_schema",     "hotel_schema",        None),
    "schema_reviews":     ("no_schema_reviews",   "hotel_schema",        None),
    "LCP_ok":             ("poor_performance",    "performance_audit",   "optimization_guide"),
    "CLS_ok":             ("poor_performance",    "optimization_guide",  None),
    "contenido_extenso":  ("low_citability",      "optimization_guide",  None),
    "open_graph":         ("no_og_tags",          "og_tags_guide",       None),
    "schema_faq":         ("no_faq_schema",      "faq_page",            None),
    "nap_consistente":    ("whatsapp_conflict",  "whatsapp_button",     None),
    "imagenes_alt":       ("missing_alt_text",    "alt_text_guide",      None),
    "blog_activo":        ("no_blog_content",     "blog_strategy_guide", None),
    "redes_activas":      ("no_social_links",     "social_strategy_guide", None),
}
```

### Score AEO (schema_infra_score) actual
Calcula score basado en: Schema Hotel (peso mayor), Schema FAQ, Schema Reviews, Open Graph. Esto es medible directamente del audit web.

### IAO score actual (el que se elimina)
Con GA4: usa IATester + GA4 para calcular score de menciones en ChatGPT/Perplexity.
Sin GA4 (caso real actual): fall back a schema_infra_score = AEO.

### Voice Readiness (el que se elimina)
Ya retorna `"--"` hardcodeado. Dead code puro.
