# AUDITORÍA COMPLETA: Módulos vs Diagnóstico vs README vs Documentación

**Fecha**: 2026-04-24 (v2 - ampliada)
**Auditoría**: Desconexiones entre módulos, diagnóstico generado, README y documentación
**Documento auditado**: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260424_190826.md`
**Hotel**: amaziliahotel (Amazilia Hotel)
**Ejecución v4complete**: 2026-04-24 19:08

---

## 0. RESUMEN EJECUTIVO

**10 desconexiones identificadas** (4 CRÍTICAS, 6 MENORES).

El diagnóstico generado es **internamente coherente** (los 4 scores, las 4 brechas, los montos financieros son correctos entre sí). Pero existen **desconexiones sistémicas** entre lo que los módulos detectan y lo que finalmente aparece en el documento, y entre las garantías de calidad que el README promete y lo que el sistema realmente ejecuta.

**Datos verificados correctos en el diagnóstico**:
- SEO 10, GEO 62, AEO 0, IAO 17 → coinciden con audit_report.json
- 4 brechas (Schema Hotel, FAQ, Meta Tags, Open Graph) → coinciden con _identify_brechas()
- $2,610,000 mensual → coincide con financial_scenarios.json
- $1,186,245 + $569,502 + $474,498 + $379,755 = $2,610,000 → suma correcta
- coherence_score 0.8911 → coincide con v4_complete_report.json

---

## 1. AFIRMACIONES DEL README (fuente de promesas)

**Archivo**: `README.md`, líneas 299-307

```
## ✅ Calidad Garantizada

- **2,224 tests** de regresión pasando al 100% (suite completa)
- **TDD Gate**: Todo cambio comienza con un test que falla
- **Pre-commit hooks**: Validaciones automáticas en cada commit
- **Suite de regresión**: Amaziliahotel + Hotel Vísperas como casos de referencia
- **Coherence Score ≥ 0.8**: Validación cruzada documentos ↔ assets
- **6 Publication Gates**: hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall, ethics
- **183 tests postprocessors + commercial_documents + delivery**: 0 regresiones post-intervención Amazilia Hotel
```

---

## 2. DATOS REALES DEL AUDIT (audit_report.json)

| Campo | Valor | Escala |
|-------|-------|--------|
| gbp.geo_score | 62 | 0-100 |
| performance.mobile_score | null (API error) | 0-100 |
| citability.overall_score | 51.67 | 0-100 |
| org_schema_detected | false | bool |
| hotel_schema_detected | false | bool |
| faq_schema_detected | false | bool |
| og_tags_detected (open_graph) | false | bool |
| whatsapp_status | verified | string |
| metadata_defaults | true (has_default_description) | bool |
| ia_readiness.overall_score | 33.2 | 0-100 |
| ai_crawlers.overall_score | 0.5 | 0-1 (!) |
| aeo_snippets.snippet_score | 0 | 0-100 |
| GBP name | "Amazilia Hotel Campestre" | string |
| GBP rating | 4.5 | 1-5 |
| GBP reviews | 202 | int |
| GBP photos | 10 | int |

---

## 3. DATOS FINANCIEROS (financial_scenarios.json)

| Campo | Valor | Fuente |
|-------|-------|--------|
| expected_monthly_cop | 2,610,000 | — |
| ADR | 300,000 | **legacy_hardcode** |
| rooms | 10 | — |
| occupancy | 0.5 | **default** |
| direct_channel | — | **default** |
| shift | — | **hardcoded: sin GA4** |
| ia_boost | — | **estimado: sin datos GA4** |
| tier | boutique | — |
| Escenario conservador | 5,076,000 | — |
| Escenario realista | 2,610,000 | — |
| Escenario optimista | -189,000 | — |

**5 de 7 fuentes financieras son default/hardcode**.

---

## 4. DOS SISTEMAS DE DETECCIÓN (RAÍZ del problema)

### 4.1 Detector A: `detect_pains()` (pain_solution_mapper.py:323)

Detecta **~8-9 pains** con umbrales PERMISIVOS:

| Condición | Umbral | Se activó? |
|-----------|--------|------------|
| geo_score < 70 | 70 | SÍ (62 < 70) |
| mobile_score < 50 | 50 | NO (null) |
| citability < 50 | 50 | NO (51.67 >= 50) |
| no_hotel_schema | bool | SÍ |
| no_org_schema | bool | SÍ |
| no_faq_schema | bool | SÍ |
| metadata_defaults | bool | SÍ |
| no_analytics_configured | bool | SÍ |
| no_og_tags | **NO tiene detección** | — |
| ai_crawler_blocked | bool | SÍ |
| low_ia_readiness | bool | SÍ |

**Pains detectados**: ~8-9 (incluyendo low_gbp_score, no_org_schema, no_analytics_configured, etc.)

### 4.2 Detector B: `_identify_brechas()` (v4_diagnostic_generator.py:2001)

Detecta **4 brechas** con umbrales MÁS ESTRICTOS en algunos campos:

| Condición | Umbral | Se activó? |
|-----------|--------|------------|
| geo_score < 60 | 60 | NO (62 >= 60) |
| mobile_score < 70 | 70 | NO (null) |
| citability < 30 | 30 | NO (51.67 >= 30) |
| no_hotel_schema | bool | SÍ |
| no_faq_schema | bool | SÍ |
| metadata_defaults | bool | SÍ |
| no_og_tags | bool | SÍ |
| no_org_schema | **AUSENTE** | — |
| no_analytics | **AUSENTE** | — |
| ai_crawler | **AUSENTE** | — |

**Brechas detectadas**: 4 (no_hotel_schema, no_faq_schema, metadata_defaults, no_og_tags)

### 4.3 Tabla de divergencias

| Campo | detect_pains() | _identify_brechas() | Divergencia |
|-------|---------------|---------------------|-------------|
| geo_score | < 70 | < 60 | 10pts diferencia |
| mobile_score | < 50 | < 70 | 20pts diferencia (invertido!) |
| citability | < 50 | < 30 | 20pts diferencia |
| no_org_schema | SÍ detecta | **AUSENTE** | Estructural |
| no_analytics | SÍ detecta | **AUSENTE** | Estructural |
| ai_crawler | SÍ detecta | **AUSENTE** | Estructural |
| no_og_tags | **NO detecta** | SÍ detecta | Estructural invertido |
| low_ia_readiness | SÍ detecta | **AUSENTE** | Estructural |

**Consecuencia**: Para Amaziliahotel, detect_pains() produce ~8 pains → genera assets para esos pains. Pero _identify_brechas() solo muestra 4 brechas en el diagnóstico. El cliente ve 4 problemas, pero internamente se generan assets para 8+. La propuesta comercial puede mencionar servicios que el diagnóstico no justifica.

---

## 5. DESCONEXIONES IDENTIFICADAS

### CRÍTICA #1: financial_validity gate Pasa con datos default

**Archivos**: `modules/quality_gates/publication_gates.py` (gate 3), `financial_scenarios.json`

El gate `financial_validity` reporta: "All financial data validated - no default values detected" → **PASSED**.

Pero financial_scenarios.json muestra que 5 de 7 fuentes son default/hardcode:
- ADR: legacy_hardcode
- occupancy: default
- direct_channel: default
- shift: hardcoded: sin GA4
- ia_boost: estimado: sin datos GA4

**Impacto**: Datos financieros no validados pasan como validados. El diagnóstico presenta $2,610,000 como dato verificado cuando en realidad es estimación con datos mayormente default.

**Solución**: El gate debe verificar los campos `source` de cada parámetro financiero. Si la mayoría son default/hardcode, el gate debe WARNING (no bloquear, pero alertar).

---

### CRÍTICA #2: Divergencia detect_pains() (8-9) vs _identify_brechas() (4)

**Archivos**: `pain_solution_mapper.py:323`, `v4_diagnostic_generator.py:2001`

Sección 4.3 detalla la divergencia. El diagnóstico muestra 4 brechas al cliente pero internamente hay 8-9 pains generando assets.

**Pains omitidos del diagnóstico** (detectados por detect_pains pero no por _identify_brechas):
- low_gbp_score (geo=62 < 70 en pains, pero >= 60 en brechas)
- no_org_schema (no existe como brecha)
- no_analytics_configured (no existe como brecha)
- low_organic_visibility (no existe como brecha)
- low_ia_readiness (no existe como brecha)
- ai_crawler_blocked (no existe como brecha)

**Brecha en diagnóstico SIN detección en pains**: no_og_tags (existe en PAIN_SOLUTION_MAP pero detect_pains() no tiene lógica de detección para OG tags)

**Impacto**: Desconexión entre lo que el diagnóstico muestra y lo que el sistema realmente detecta y actúa. El cliente ve un panorama parcial.

---

### CRÍTICA #3: Dos cálculos SEO diferentes (10 vs 25)

**Archivos**: 
- `_calculate_web_score()` en `v4_diagnostic_generator.py` → SEO 10 (mostrado al cliente)
- `calcular_score_seo(_extraer_elementos_seo())` en scoring interno → SEO 25 (usado en score_global)

Ambos representan "SEO" pero usan algoritmos y pesos diferentes. El diagnóstico muestra 10, pero internamente el sistema calcula 25.

**Impacto**: Inconsistencia en métricas. Si un técnico consulta el JSON interno espera score=25, pero el cliente ve 10.

---

### CRÍTICA #4: Confusión IAO (17) vs ia_readiness (33.2)

**Archivos**:
- Diagnóstico: IAO = 17 (usando CHECKLIST_IAO con weighting LLM)
- audit_report.json: ia_readiness.overall_score = 33.2 (módulo diferente)

Ambos representan "preparación para IA" pero son métricas diferentes con valores diferentes.

**Impacto**: Consumidores del JSON (APIs, integraciones) esperan que ia_readiness = IAO del diagnóstico, pero 33.2 ≠ 17.

---

### MENOR #5: README dice 6 gates, código tiene 9

`PublicationGatesOrchestrator` (publication_gates.py:136-146) tiene 9 gates (6 blocking + 3 WARNING). README solo menciona 6.

### MENOR #6: Workflow referencia comando inexistente

`.agents/workflows/v4_complete.md` L95 invoca `v4_coherence_validator` que fue eliminado y fusionado en `v4_quality_validator.md`.

### MENOR #7: Bug escala crawler_access IAO

En `_extraer_elementos_iao()`:
```python
elementos["crawler_access"] = (...audit_result.ai_crawlers.overall_score > 50)
```
`ai_crawlers.overall_score = 0.5` (escala 0-1). La comparación `> 50` asume escala 0-100. Siempre False. Suprime 15pts del IAO.

### MENOR #8: geo_score 62 vs geo_flow_result 23

- audit_report.json: gbp.geo_score = 62
- geo_flow_result.json: geo_assessment.total_score = 23 (band: "critical")
Dos modelos GEO producen valores muy diferentes para el mismo hotel.

### MENOR #9: coherence_score múltiples valores

- 0.8911... (v4_complete_report.json y diagnóstico)
- 0.8789... (gate coherence)
- 0.88 (coherence_validation.json)
- 0.8 (phase_5_consistency_check)

### MENOR #10: Promedios regionales sin trazabilidad

Los valores "Promedio Regional" (59, 89, 44, 20) provienen de `_get_regional_benchmarks()` que carga `plan_maestro_data.json`. No se almacenan en JSON de output.

---

## 6. VEREDICTO POR AFIRMACIÓN README

| Afirmación README | Realidad | Tipo |
|-------------------|----------|------|
| "Coherence Score ≥ 0.8" | Score 0.89 presente | Parcial — número sin trace de gates |
| "Validación cruzada docs ↔ assets" | Solo el número | CRÍTICA — sin evidencia de validación |
| "6 Publication Gates" | 9 gates (6 blocking + 3 advisory) | MENOR — subestima |
| "Suite de regresión Amaziliahotel" | No mencionado en documento | N/A — promesa no rastreable |
| "183 tests = 0 regresiones" | No mencionado en documento | N/A — promesa no rastreable |

---

## 7. COBERTURA DEL PLAN ACTUAL vs DESCONEXIONES

(Actualizado v2: plan ampliado para cubrir las 4 CRÍTICAs)

| Desconexión | Plan la cubre? | Detalle |
|-------------|---------------|---------|
| CRÍTICA #1: financial_validity gate default | **SÍ** | RAIZ T1.1 — gate inspecciona financial_sources |
| CRÍTICA #2: pains(8-9) vs brechas(4) | **SÍ** | RAIZ T0 — umbrales + pain_ids estructurales + no_og_tags bidireccional |
| CRÍTICA #3: Dos cálculos SEO | **SÍ** | RAIZ T4.1 — unificar a un solo algoritmo |
| CRÍTICA #4: IAO vs ia_readiness | **SÍ** | RAIZ T4.2 — IAO = ia_readiness.overall_score |
| MENOR #5: README 6→9 gates | **SÍ** | FASE-DOCS |
| MENOR #6: Workflow ghost command | **SÍ** | FASE-DOCS |
| MENOR #7: Bug escala crawler | **DIFERIDA** | Post-VALIDATE |
| MENOR #8: geo_score 62 vs 23 | **DIFERIDA** | Post-VALIDATE |
| MENOR #9: Múltiples coherence | **PARCIAL** | Cableado de gates reduce ambigüedad |
| MENOR #10: Benchmarks sin trace | **DIFERIDA** | Post-VALIDATE |

**COBERTURA**: 4/4 CRÍTICAs cubiertas. 2/6 MENORES cubiertas (1 parcial). 3/6 MENOREs diferidas.

---

## 8. ACCIONES CORRECTIVAS SUGERIDAS (adicionales al plan)

### Para CRÍTICA #1: financial_validity gate con source validation
- El gate `_financial_validity_gate()` debe inspeccionar los campos `source` de financial_data
- Si mayoría son default/hardcode → WARNING (no blocking, pero reportado en gate_report.json)
- Agregar `financial_sources` al assessment dict

### Para CRÍTICA #2 (parte estructural): Unificar modelos de detección
- OPCIÓN A: Eliminar `_identify_brechas()` y usar directamente `detect_pains()` como fuente única del diagnóstico
- OPCIÓN B: Hacer que `_identify_brechas()` delegue en `detect_pains()` y traduzca pains → brechas
- OPCIÓN C: Alinear umbrales Y agregar pain_ids faltantes (no_org_schema, no_analytics, etc.) a `_identify_brechas()`

### Para CRÍTICA #3: Unificar cálculo SEO
- Elegir un único algoritmo y eliminar el duplicado
- El diagnóstico debe usar el mismo score que el score_global interno

### Para CRÍTICA #4: Unificar IAO vs ia_readiness
- OPCIÓN A: Eliminar ia_readiness y usar solo IAO del diagnóstico
- OPCIÓN B: Hacer que ia_readiness = IAO (unificar fórmulas)
- Documentar cuál es la fuente de verdad

### Para MENOR #7: Fix bug escala crawler_access
- Cambiar `> 50` por `> 0.5` (o normalizar a 0-100 antes de comparar)

---

## 9. ARCHIVOS CLAVE INVOLUCRADOS

| Rol | Archivo | Relevancia |
|-----|---------|------------|
| README promesa | `README.md:299-307` | Afirmaciones a auditar |
| Documento auditado | `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260424_190826.md` | Objeto de auditoría |
| Gates reales | `modules/quality_gates/publication_gates.py` | 9 gates (≠ 6 del README) |
| Coherence validator | `modules/commercial_documents/coherence_validator.py` | Fuente A del score (0-1) |
| Fallback scorer | `modules/commercial_documents/v4_diagnostic_generator.py:790-816` | Fuente B del score (0-100) |
| Generador diagnóstico | `modules/commercial_documents/v4_diagnostic_generator.py` | Genera el documento + _identify_brechas() |
| Pain detector | `modules/commercial_documents/pain_solution_mapper.py` | detect_pains() — 22 tipos |
| Service catalog | `modules/commercial_documents/service_catalog.py` | SERVICE_CATALOG — 8 entradas |
| Pain-solution map | `modules/commercial_documents/pain_solution_mapper.py:52` | PAIN_SOLUTION_MAP |
| Flujo principal | `main.py:2158-2233` | v4complete: coherence → gates insertion point → diagnóstico |
| Workflow v4 | `.agents/workflows/v4_complete.md:95` | Ghost command v4_coherence_validator |
| Datos audit | `output/v4_complete/audit_report.json` | Datos crudos del audit |
| Datos financieros | `output/v4_complete/financial_scenarios.json` | Fuentes default/hardcode |
| Reporte completo | `output/v4_complete/v4_complete_report.json` | Score + gates results |
| Docstring inexacto | `modules/quality_gates/publication_gates.py:117` | "5 critical gates" → debería decir 9 |
