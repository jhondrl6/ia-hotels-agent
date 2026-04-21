# RESULTADOS AUDITORIA FORENSE: Amaziliahotel v4complete
# Fecha: 2026-04-19
# Fuente: AMAZILIAHOTEL_FORENSIC_AUDIT_PLAN.md + verificacion contra archivos reales
# Proposito: Base unica para planificar refactorizacion en nueva sesion

---

## VEREDICTO

| Campo | Valor |
|-------|-------|
| Estado | **RECHAZADO** |
| Score Forense | **16/100** (umbral aprobacion: 80) |
| Tri-Play Validos | **0/7 servicios** |
| Dimensiones Tri-Play | 11/28 = 39% |
| Problemas Criticos | 3 |
| Problemas Altos | 5 |
| Problemas Medios | 4 |
| Workflows Afectados | 3 (v4_complete, v4_asset_conditional, v4_quality_validator) |

---

## SCORE FORENSE DETALLADO

| Dimension | Score | Peso | Contribucion |
|-----------|-------|------|-------------|
| Cobertura brechas B1-B4 | 32% | 25% | 8.1 |
| Assets con datos reales | 0% | 25% | 0.0 |
| Assets justificados (pain_ids) | 0% | 15% | 0.0 |
| Assets sin duplicar | 83% | 10% | 8.3 |
| Assets entregables | 0% | 25% | 0.0 |
| **TOTAL** | | | **16/100** |

---

## TRI-PLAY: Diagnostico -> Propuesta -> Assets

Regla: VALIDO = (Brecha en Diagnostico) AND (Servicio en Propuesta) AND (Asset con datos reales) AND (Promesa medible)

| Servicio | Brecha | Propuesta | Datos reales | Medible | Veredicto |
|----------|--------|-----------|--------------|---------|-----------|
| GEO (Google Maps) | SI | SI | NO | NO | INVALIDO (2/4) |
| IAO (ChatGPT/IA) | SI | SI | NO | NO | INVALIDO (2/4) |
| AEO (Voz) | NO | SI | NO | NO | INVALIDO (1/4) |
| SEO Local | SI | SI | NO | NO | INVALIDO (2/4) |
| WhatsApp | NO | SI | NO | NO | INVALIDO (1/4) |
| Datos Estructurados | SI | SI | NO | NO | INVALIDO (2/4) |
| Informe Mensual | NO | SI | NO | NO | INVALIDO (1/4) |

**Ningun servicio cumple las 4 dimensiones. La causa raiz es la misma para 6/7: "Datos reales" y "Promesa medible" fallan porque BookingScraper es un stub.**

---

## COBERTURA B1-B4

| Brecha | Costo/mes COP | Asset | Estado |
|--------|---------------|-------|--------|
| B1: Sin Schema Hotel (45%) | $1,186,245 | hotel_schema/ESTIMATED_*.json | PARCIAL - existe pero generico (address=None, tel=None, geo=None) |
| B2: Sin FAQ Rich Snippets (21%) | $569,502 | faq_page/ESTIMATED_*.csv | PARCIAL - existe pero ext .csv con contenido JSON-LD (bug formato) |
| B3: Metadatos por Defecto (18%) | $474,498 | optimization_guide/ESTIMATED_*.md | PARCIAL - existe pero con contradiccion interna (title tag detectado Y no detectado) |
| B4: Sin Open Graph (14%) | $379,755 | NINGUNO | **SIN CUBRIR** - no hay asset generado |

---

## HALLAZGOS CRITICOS (3)

### C1: BookingScraper es STUB
- **Archivo:** `modules/scrapers/booking_scraper.py` linea 33-81
- **Evidencia:** research.json confidence=0.0, sources_checked=[], data_found={}
- **Cascada:** Causa H1, H2, H6, H9, H11 (5 de 12 hallazgos)
- **Impacto:** 75% de assets son ESTIMATED (plantillas sin datos)
- **Fix:** Implementar scraping real o usar fuente alternativa (SerpAPI/Google Places)

### C2: 0% de assets tienen datos verificados
- **Evidencia:** research.json vacio -> pipeline genera con confidence=0.5 fallback
- **12 de 12 metadata.json:** pain_ids_resolved = MISSING (ninguno vinculado a brecha)
- **Solo 3 de 12 assets** tienen confidence > 0.5 (hotel_schema, faq_page, llms_txt = 0.85)
- **Pero:** esos 0.85 son del preflight check, NO de datos verificados de fuentes reales

### C3: B4 Open Graph sin cobertura ($379K/mes expuesto)
- **Evidencia:** No existe carpeta open_graph_meta/ en output/
- **Diagnostico detecta:** "Sin Meta Tags Sociales (Open Graph)" como brecha B4
- **Propuesta ignora:** No hay servicio que atienda B4
- **Asset inexistente:** 0% cobertura

---

## HALLAZGOS ALTOS (5)

| # | Hallazgo | Archivo responsable | Linea | Naturaleza |
|---|----------|---------------------|-------|------------|
| A1 | faq_page ext .csv con contenido JSON-LD | `modules/asset_generation/faq_generator.py` | ~120 | Bug formato |
| A2 | optimization_guide contradiccion title tag | `modules/asset_generation/optimization_generator.py` | ~80-90 | Datos inconsistentes |
| A3 | monthly_report plantilla vacia (46 blanks) | `modules/asset_generation/report_generator.py` | ~50 | has_real_data=False |
| A4 | Propuesta comercial: ROI 20X sin base Tier C | Propuesta generator | N/A | Inflacion comercial |
| A5 | Propuesta: 2 servicios inventados (WhatsApp, Informe) sin brecha | Propuesta generator | N/A | Desalineacion diagnostico-propuesta |

---

## HALLAZGOS MEDIOS (4)

| # | Hallazgo | Detalle |
|---|----------|---------|
| M1 | hotel_schema duplicado (2 carpetas) | hotel_schema/ y geo_enriched/hotel_schema_rich.json - NO identicos pero mismo proposito |
| M2 | llms.txt duplicado (2 carpetas) | llms_txt/ y geo_enriched/llms.txt - NO identicos (contenido diferente) |
| M3 | voice_assistant_guide (3 archivos) sin justificacion | pain_ids_resolved=MISSING, no hay brecha en diagnostico |
| M4 | whatsapp_button numero no verificado | 573104019049 coincide con GBP phone 310 4019049 - verificar si es el mismo |

---

## CLASIFICACION SISTEMICO vs ESPECIFICO

| Tipo | Count | % | Hallazgos |
|------|-------|---|-----------|
| **SISTEMICO** (bug pipeline) | 10 | 83% | C1, C2, C3, A1, A2, A3, M1, M2, M3, M4 |
| **ESPECIFICO** (caso Amaziliahotel) | 2 | 17% | Contradiccion datos entrada (title tag), placeholder "en  en" |

**El 83% de bugs se resuelve corrigiendo UNA pieza: BookingScraper.scrape()**

---

## CORRECCIONES AL PLAN ORIGINAL

El plan de auditoria tenia 3 errores documentados:

1. **Linea 31-33 (pain_ids):** Plan dice hotel_schema, faq_page, optimization_guide tienen pain_ids. **REALIDAD:** TODOS los 25 metadata.json tienen pain_ids_resolved = MISSING.

2. **Linea 114 (llms.txt):** Plan dice contenido "identico". **REALIDAD:** NO son identicos (mismo tamano 802 chars, contenido diferente).

3. **Linea 526 (score coherencia):** Plan dice "18% (4/22 checks)". **REALIDAD RECALCULADA:** 39% dimensiones pasadas (11/28), 0/7 servicios validos.

---

## DATOS DE REFERENCIA

### Archivos fuente verificados
```
output/v4_complete/
  01_DIAGNOSTICO_Y_OPORTUNIDAD_20260415_113914.md
  02_PROPUESTA_COMERCIAL_20260415_113915.md
  audit_report.json
  v4_complete_report.json
  financial_scenarios.json
  amaziliahotel/
    research_e2623f16b1ee_Amaziliahotel.json
    (16 subcarpetas, 25 metadata files)
```

### Scores del pipeline original
```
coherence_score: 0.8911111111111112
phase_4_publication_gates: ready=False, status=NOT_READY
phase_5_consistency_check: is_consistent=True, confidence=0.8
evidence_tier: C
financial: conservative=5,076,000 | realistic=2,610,000 | optimistic=-189,000
```

### GBP verificado
```
nombre: Amazilia Hotel Campestre
rating: 4.5 | reviews: 202 | photos: 10
phone: 310 4019049
address: mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda
geo_score: 62/100
```

### WhatsApp numero en asset vs GBP
```
Asset: 573104019049
GBP:   310 4019049
Mismo numero: SI (con prefijo pais 57)
```

---

## TRAZABILIDAD: Hallazgo -> Archivo .py -> Funcion -> Linea

| ID | Hallazgo | Archivo | Funcion | Linea | Tipo bug |
|----|----------|---------|---------|-------|----------|
| H1 | research.json vacio | booking_scraper.py | scrape() | 33-81 | STUB |
| H2 | hotel_schema generico | booking_scraper.py | scrape() | 58-70 | STUB cascada |
| H3 | faq_page ext .csv | faq_generator.py | _generate_faq_csv() | ~120 | Formato |
| H4 | llms.txt duplicado | llmstxt_generator.py + geo_enricher.py | 2 generators | N/A | Arquitectura |
| H5 | optimization_guide contradiccion | optimization_generator.py | _analyze_metadata() | ~80-90 | Datos entrada |
| H6 | monthly_report vacio | report_generator.py | generate_monthly_report() | ~50 | has_real_data=False |
| H7 | whatsapp_button sin brecha | whatsapp_generator.py | generate_button() | ~30 | Config vs brecha |
| H8 | voice_assistant_guide sin brecha | voice_generator.py | generate_guides() | ~20 | Config vs brecha |
| H9 | 75% assets ESTIMATED | v4_asset_orchestrator.py | _generate_with_coherence_check() | 269 | confidence=0 fallback |
| H10 | Coherence 0.89 vs is_coherent=FALSE | coherence_gate.py + diagnostic_generator.py | 2 calculadores | N/A | Metricas duplicadas |
| H11 | delivery_ready 25% | publication_gates.py | check_delivery_ready() | ~40 | Cascada stub |
| H12 | Paths Windows | asset_report.py | _format_paths() | ~60 | Entorno WSL |

---

## DEPENDENCIAS PARA REFACTORIZACION

```
C1 (BookingScraper real)  [PRIORIDAD MAXIMA - bloquea todo]
├── H1 research.json vacio -> se resuelve solo
├── H2 hotel_schema generico -> requiere C1 + regenerar schema
├── H6 monthly_report vacio -> requiere C1 + datos reales
├── H9 75% ESTIMATED -> se resuelve solo (confidence sube)
├── H11 delivery_ready 25% -> se resuelve solo (gate pasa)
└── C3 B4 Open Graph -> independiente, generar asset nuevo

H3 faq_page formato [INDEPENDIENTE - bug generador]
H5 optimization_guide [REQUIERE C1 - datos de entrada]
H4 duplicados [INDEPENDIENTE - consolidar carpetas]
H7/H8 assets sin brecha [DECISION DE PRODUCTO]
H10 coherence metric [INDEPENDIENTE - unificar calculadores]
H12 paths Windows [INDEPENDIENTE - usar paths relativos]
```

---

## RESUMEN PARA NUEVA SESION

**Para planificar la refactorizacion, necesitas 3 cosas de este documento:**

1. **Que corregir:** 12 hallazgos (H1-H12) con trazabilidad exacta a archivo/funcion/linea
2. **Por donde empezar:** C1 (BookingScraper) es el cuello de botella - resuelve 5/12 hallazgos por cascada
3. **Que decidir:** 2 items requieren decision de producto (H7 whatsapp, H8 voice_assistant, monthly_report mantener/eliminar)

**Secuencia logica de refactorizacion (propuesta):**
- Fase 1: C1 BookingScraper (bloqueante)
- Fase 2: Regenerar assets con datos reales (H2, H5, H6)
- Fase 3: Corregir bugs generadores (H3, H4, H10, H12)
- Fase 4: Generar asset B4 Open Graph (C3)
- Fase 5: Decisiones de producto (H7, H8) + implementar quality gate (H9, H11)

---

*Documento generado: 2026-04-19 por Hermes Agent*
*Basado en: AMAZILIAHOTEL_FORENSIC_AUDIT_PLAN.md + verificacion contra output real*
*Proposito: Referencia unica para sesion de planificacion de refactorizacion*
