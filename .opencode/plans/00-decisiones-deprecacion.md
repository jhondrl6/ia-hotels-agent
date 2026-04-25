# Decisiones de Deprecación y Unificación

**Fecha**: 2026-04-25
**Origen**: Auditoría profundizada — 18 hallazgos (10 del contexto original + 8 nuevos)
**Principio rector**: "Los módulos entregan información que NO puede ser ignorada. Es capacidad instalada desaprovechada."

---

## Algoritmos y Funciones a DEPRECAR

### DEP-01: `_calculate_web_score()` → Reemplazada por `calcular_score_seo()`

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py` líneas 1373-1393

**Razón**:
- `_calculate_web_score()` usa un algoritmo custom simplificado (max 40pts performance + 30 schema + 20 FAQ + 10 validation)
- `calcular_score_seo()` usa CHECKLIST_SEO con pesos documentados (7 factores que suman 100pts)
- CHECKLIST_SEO es **consistente** con el patrón de los otros 3 pilares (GEO, AEO, IAO también usan CHECKLIST_*)
- Para Amaziliahotel: `_calculate_web_score()` da 10, `calcular_score_seo()` da 25. El valor 25 es más cercano a la realidad (reconoce HTTPS=15pts y GBP rating=10pts)

**Acción**:
1. Hacer que `_calculate_web_score()` delegue en `calcular_score_seo(_extraer_elementos_seo())`
2. Mantener `_calculate_web_score()` como wrapper para backward compat
3. Agregar deprecation warning en docstring
4. Eliminar el algoritmo custom antiguo

**Efecto en diagnóstico**: SEO pasará de ~10 a ~25 para Amaziliahotel. Más preciso y alineado.

---

### DEP-02: CHECKLIST_IAO standalone → Reemplazado por `ia_readiness.overall_score`

**Archivos**:
- `v4_diagnostic_generator.py` líneas 128-136 (CHECKLIST_IAO)
- `v4_diagnostic_generator.py` líneas 1424-1440 (`_calculate_iao_score_from_audit()`)
- `v4_diagnostic_generator.py` líneas 1896-1949 (`_extraer_elementos_iao()`)

**Razón**:
- CHECKLIST_IAO calcula un score basado en 7 flags booleanos con pesos fijos
- `ia_readiness.overall_score` (del módulo `ia_readiness`) usa un algoritmo más granular con componentes ponderados (schema_quality, crawler_access, citability, llms_txt, brand_signals)
- Para Amaziliahotel: CHECKLIST_IAO → 35 (antes del ajuste LLM), ia_readiness → 33.2. Valores cercanos pero ia_readiness es más completo
- Dos métricas para el mismo concepto = confusión

**Acción**:
1. `_calculate_iao_score_from_audit()` debe usar `audit_result.ia_readiness.overall_score` como fuente primaria
2. Si `ia_readiness` no está disponible → fallback a CHECKLIST_IAO
3. Deprecar `_extraer_elementos_iao()` standalone (mantener como fallback interno)
4. Documentar: IAO del diagnóstico = ia_readiness.overall_score

**Efecto en diagnóstico**: IAO = 33 (redondeado de 33.2) en vez de 17. Más alto pero más preciso.

---

### DEP-03: `_identify_brechas()` standalone thresholds → Delegar en `detect_pains()`

**Archivos**:
- `v4_diagnostic_generator.py` líneas 2001-2120+ (`_identify_brechas()`)
- `pain_solution_mapper.py` líneas 323-517 (`detect_pains()`)

**Razón**:
- Dos detectores con umbrales DIFERENTES para los MISMOS datos = fuente de desconexión
- `detect_pains()` es más completo (13 tipos vs 10 en brechas) y usa umbrales más realistas
- La divergencia causa que el diagnóstico muestre 4 brechas mientras asset_plan genera 7+ assets

**Acción**:
1. `_identify_brechas()` debe llamar a `detect_pains()` internamente y traducir `Pain → brecha`
2. Mantener `_identify_brechas()` como wrapper que agrega narrativa comercial
3. Unificar umbrales: usar los de `detect_pains()` como fuente de verdad
4. Agregar pain_ids faltantes en brechas: `no_org_schema`, `no_analytics_configured`, `ai_crawler_blocked`, `low_ia_readiness`
5. Agregar detección `no_og_tags` en `detect_pains()` (bidireccional)

**Efecto**: El diagnóstico y la propuesta siempre estarán alineados porque nacen del mismo detector.

---

## Templates y Secciones a RESTAURAR (NO deprecar)

### RES-01: `${geo_table}` / `${ia_metrics_table}` en template V6

**Situación actual**: `_build_geo_problems_table()` (línea 1154) computa métricas IA (crawlers, citability, ia_readiness) pero el template V6 eliminó `${geo_table}`. La información se calcula y se descarta.

**Acción**: RESTAURAR en template V6 como `${ia_metrics_table}`.

### RES-02: Hallazgos positivos

**Situación actual**: El diagnóstico solo muestra brechas (problemas). El audit detecta señales positivas (WhatsApp, HTTPS, redes sociales, 202 reviews, rating 4.5) que nunca se muestran.

**Acción**: CREAR `_build_positive_findings()` e insertar `${positive_findings}` en V6.

### RES-03: geo_flow_result como métrica complementaria

**Situación actual**: `geo_flow_result.json` muestra `total_score: 23, band: "critical"` pero el diagnóstico solo muestra GBP geo_score=62. Son dos mediciones complementarias del mismo dominio.

**Acción**: REFERENCIAR geo_flow_result en la tabla de métricas IA como "Salud Técnica GEO".

---

## Bugs a CORREGIR (incluidos en el plan)

### BUG-01: Escala crawler_access > 50 con score 0-1
- Línea 1927: `ai_crawlers.overall_score > 50` → debe ser `> 0.5`
- Suprime 15pts del IAO. Corrección: 1 línea.

### BUG-02: financial_validity gate ignora sources
- El gate no pasa `sources` a NoDefaultsValidator
- Infraestructura FASE-J ya existe (parámetro `sources` en validator)
- Corrección: pasar `assessment["financial_sources"]` al validator

---

## Lo que NO se depreca (se mantiene)

| Elemento | Razón |
|----------|-------|
| `_build_geo_problems_table()` | Se RESTAURA su consumo en V6, NO se depreca |
| `_build_regional_context()` hardcoded | Es narrativa comercial, no datos. OK que sea estático. |
| Template V6 "Antes vs Ahora" | Narrativa de ventas, no datos. OK hardcoded. |
| GBP geo_score como GEO primario | Es el dato más cercano a "realidad Google Maps". |
| `CoherenceValidator` | Funciona, es 1 de 9 gates. |
| `SERVICE_CATALOG` | Ya existe y funciona. |

---

## Resumen de decisiones

| # | Qué | Decisión | Impacto |
|---|-----|----------|---------|
| DEP-01 | `_calculate_web_score()` | DEPRECAR, reemplazar con CHECKLIST_SEO | SEO unificado, consistente con otros pilares |
| DEP-02 | CHECKLIST_IAO standalone | DEPRECAR, usar ia_readiness.overall_score | IAO unificado, más granular |
| DEP-03 | Umbrales duplicados detect_pains vs brechas | UNIFICAR en detect_pains() | Una sola fuente de verdad |
| RES-01 | IA metrics en V6 | RESTAURAR `${ia_metrics_table}` | Cliente ve datos que módulos ya producen |
| RES-02 | Hallazgos positivos | CREAR sección nueva | Balance: no solo problemas |
| RES-03 | geo_flow_result | REFERENCIAR como complemento | Transparencia: dos perspectivas GEO |
| BUG-01 | Escala crawler | CORREGIR `> 50` → `> 0.5` | 15pts IAO restaurados |
| BUG-02 | financial_validity sources | CORREGIR gate | Gate detecta defaults reales |
