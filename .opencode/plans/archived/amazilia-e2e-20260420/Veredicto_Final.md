# VEREDICTO FORENSE E2E — Amaziliahotel Post-Refactor
**Fecha**: 2026-04-20
**Ejecución**: v4complete --url https://amaziliahotel.com/
**Commit base**: cdd9991
**Score objetivo**: >= 80/100

---

## FASE-2: Coherencia Diagnóstico ↔ Propuesta ↔ Assets

### 2.1 Tri-Play: Brechas → Servicios → Assets

| Brecha | Servicio en Propuesta | Estado |
|--------|----------------------|--------|
| B1: Sin Schema Hotel | Datos Estructurados | ✅ |
| B2: Sin FAQ Rich Snippets | Datos Estructurados | ✅ |
| B3: Metadatos por Defecto | SEO Local | ✅ |
| B4: Sin Open Graph | NO tiene servicio explícito | ⚠️ |

### 2.1.2 Coherencia Financiera

| Check | Esperado | Actual | Estado |
|-------|----------|--------|--------|
| Tier C mencionado | Sí | NO | ❌ |
| ROI base 3X | 3X | 20X | ❌ |
| 20X solo con GA4 | Sí | Directo sin GA4 | ❌ |

### 2.1.3 Servicios ELIMINADOS (FASE-5)

| Servicio | Estado en propuesta | Veredicto |
|----------|-------------------|-----------|
| WhatsApp | "Boton de WhatsApp" con ❌ No generado | ❌ SIGUE COMO SERVICIO |
| Voice/Búsqueda por Voz | "Búsqueda por Voz" con ❌ No generado | ❌ SIGUE COMO SERVICIO |
| Informe Mensual | "Informe Mensual" como servicio | ⚠️ OK (incluido) |

### 2.2 Matriz de Fidelidad

| Afirmación en Propuesta | Dato en Diagnóstico | Veredicto |
|------------------------|---------------------|-----------|
| "$2.610.000 COP/mes" | financial_value: 2.610.000 | ✅ |
| "No aparece en ChatGPT" | AEO 0/100 | ✅ |
| ROI 20X (Tier C) | Tier C, GA4 no configurado | ❌ Debió ser 3X |

**FASE-2 Veredicto: 3 inconsistencias (tolerable: <=1) → FALLO**

---

## FASE-3: Auditoría de Assets Post-Ejecución

### 3.1 Assets generados

- ESTIMATED: 67 archivos
- REAL/VERIFIED: 0 archivos
- TOTAL: 50 archivos (sin metadata/audit)

### 3.2 Validación de GAPs corregidos

| GAP | Pre-refactor | Post-ejecución | Veredicto |
|-----|-------------|----------------|-----------|
| G1: research.json | confidence 0.0 | confidence 0.25, solo booking | ⚠️ PARCIAL |
| G2: hotel_schema | genérico | TODOS campos vacíos (tel, addr, geo) | ❌ NO |
| G3: B4 Open Graph | NO existía | EXISTE pero ESTIMATED | ⚠️ PARCIAL |
| G4: faq_page extensión | .csv | STILL .csv | ❌ NO |
| G5: llms.txt duplicado | 2 versiones | 2 versiones (geo + llms_txt) | ❌ NO |
| G6: optimization_guide | contradicción title tag | Sin contradicción | ✅ SÍ |
| G7: monthly_report | _____ blanks | 27 blanks encontrados | ❌ NO |
| G8: WhatsApp eliminado | promised_by=always | _DEPRECATED + html sigue | ⚠️ PARCIAL |
| G9: Voice eliminado | promised_by=always_aeo | _DEPRECATED + files siguen | ⚠️ PARCIAL |
| G10: ROI 3X | 20X directo | STILL 20X en propuesta | ❌ NO |
| G11: coherence duplicada | 0.89 vs 0.86 | 0.89 (unificado) | ✅ SÍ |
| G12: paths Windows | C:\... | 0 matches | ✅ SÍ |
| G13: "eje_cafetero" | lowercase | 3 veces lowercase | ❌ NO |
| G14: "COP COP" | duplicado | 5 veces en propuesta | ❌ NO |

**Resumen GAPS**: 4/14 corregidos (G6, G11, G12 + G8/G9 parcial) = 28.6%

### 3.3 Coherencia interna

- coherence_validation.json: is_coherent=true, overall_score=0.88 ✅
- coherence_score diagnóstico: 0.89 ✅
- Consistency checker: CONSISTENTE, 0 hard conflicts ✅

---

## FASE-4: Score Forense Recalculado

| Dimensión | Peso | Score | Cálculo |
|-----------|------|-------|---------|
| Cobertura brechas B1-B4 | 25% | 100% | 4/4 brechas tienen servicio |
| Assets con datos reales | 25% | 8.3% | 1/12 (solo llms_txt) |
| Assets justificados (pain_ids) | 15% | 91% | coherence_validation |
| Sin duplicación | 10% | 83.3% | 10/12 sin duplicar (llms.txt x2) |
| Assets entregables | 25% | 70% | 7/10 entregables (sin WhatsApp/Voice) |

**SCORE FORENSE: (100*25 + 8.3*25 + 91*15 + 83.3*10 + 70*25) / 100 = 63.8/100**

---

## FASE-5: Nuevos GAPs detectados

| Nuevo GAP | Severidad | Descripción |
|-----------|-----------|-------------|
| NG1: Publication NOT_READY | ALTO | content_quality gate BLOCKED (COP COP en propuesta) |
| NG2: 10 assets con "Insufficient confidence" | MEDIO | Solo llms_txt pasó preflight |
| NG3: LLMs OpenRouter/Gemini fallaron | MEDIO | 504/404 durante ejecución, datos IAO parciales |
| NG4: Google Maps API key invalid | ALTO | Places API 400, geo_score=0 falso |
| NG5: Propuesta no scrubbeada | MEDIO | Content Scrubber solo corrió en diagnóstico |

**Total nuevos GAPs: 5 (umbral tolerable: <=2) → FALLO**

---

## FASE-6: Veredicto Final

### Criterios de aprobación

| Criterio | Umbral | Actual | Estado |
|----------|--------|--------|--------|
| Score forense | >= 80 | **63.8** | ❌ |
| Coherence validation | is_coherent: true | true | ✅ |
| GAPs pre-existentes resueltos | >= 11/14 (80%) | **4/14 (28.6%)** | ❌ |
| GAPs nuevos detectados | <= 2 | **5** | ❌ |
| Tests pasando | 100% | 100% (2136 pass) | ✅ |

### Condiciones: Score 63.8 (<80) + GAPs 4/14 (<8/14) + nuevos GAPs 5 (>2)

# VEREDICTO: RECHAZADO ❌

---

## Análisis causal: Por qué los fixes no se reflejan

Los fixes de FASE-1 a FASE-6 se aplicaron al CODEBASE, pero la ejecución v4complete
expone problemas de **pipeline/data flow**, no solo de código:

1. **Código ≠ Output**: Los fixes en `asset_catalog.py` (DEPRECATED voice) y
   `v4_diagnostic_generator.py` (ROI 3X) NO afectan el pipeline v4complete porque
   el generador de propuesta (`v4_proposal_generator.py`) tiene lógica propia de ROI
   y el catálogo se usa parcialmente.

2. **API failures cascading**: Google Maps API key invalid → Places 400 →
   geo_score=0, lat/lng=0.0, hotel_schema campos vacíos.
   Esto NO es un code bug — es un ENV issue.

3. **Content Scrubber scope**: Solo scrubbió el diagnóstico, NO la propuesta.
   Resultado: "COP COP" corregido en diagnóstico pero 5 instancias en propuesta.

4. **faq_page genera .csv**: El handler de faq_page en `conditional_generator.py`
   sigue generando .csv (no JSON-LD como el fix de FASE-3).

## Acciones requeridas para APROBACIÓN

### CRÍTICO (bloquea entrega)
1. **Fix ROI**: `v4_proposal_generator.py` debe usar 3X para Tier C, 20X solo con GA4
2. **Fix Content Scrubber**: Aplicar a AMBOS archivos (diagnóstico + propuesta)
3. **Fix faq_page handler**: conditional_generator.py debe generar JSON-LD, no .csv
4. **Fix hotel_schema**: conditional_generator._generate_hotel_schema() debe usar datos reales del audit
5. **Fix monthly_report blanks**: Eliminar "_____" del template

### ALTO (plan de seguimiento)
6. Eliminar WhatsApp/Voice como servicios vendibles en propuesta
7. Fix "eje_cafetero" → "Eje Cafetero" en propuesta
8. Investigar Google Maps API key (o documentar como env limitation)

---

*Generado: 2026-04-20 12:30*
*Evidencia: evidence/amazilia-e2e-20260420/*
*Logs: ejecucion_20260420_122645.log*
