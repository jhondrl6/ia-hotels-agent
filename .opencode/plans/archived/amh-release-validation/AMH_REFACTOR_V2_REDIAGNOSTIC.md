# Contexto: AMH_REFACTOR_V2 — Rediagnostico Post-RELEASE

## Ejecutable la sesion anterior

Fecha: 2026-04-20  
Fase: FASE-RELEASE (05-prompt-inicio-sesion-fase-RELEASE.md)  
Veredicto: RECHAZADO  
Evidencia: `evidence/amh-release-validation/VEREDICTO_FINAL_AMH_REFACTOR_V2.md`

---

## Problemas descubiertos en la ejecucion E2E

### 1. SCRUBBER BYPASS EN PROPUESTA (G14 — CRITICO)

**Sintoma**: 5x "COP COP" en proposal (lineas 30, 40, 105, 106, 107).  
**Sintoma directo**: Log muestra `[SKIP] Proposal document not available for scrubbing`.  
**Ubicacion del bypass**: El ContentScrubber se ejecuta en FASE 3.6, pero la propuesta se genera en FASE 3.5 DESPUES de la presentacion de ValidationSummary y ANTES de que el scrubber tenga la ruta al archivo de propuesta.  
**Codigo relevante**:
- `main.py`: ContentScrubber importado (2 instancias verificadas en pre-flight)
- `modules/content_scrubber.py`: existe y tiene logica de scrubbing
- La propuesta se genera en FASE 3.5, el scrubber en FASE 3.6 — timing parece correcto, pero la ruta del archivo propuesta no se pasa al scrubber o el archivo no existe todavia en ese momento.

**Fix ya en codigo (aparentemente inefectivo)**:
- ContentScrubber importado en main.py
- FASE-3 prometia que el scrubber limpiaria COP COP antes de la propuesta

### 2. HOTEL_SCHEMA CON LAT:0.0 (G2 — ALTO)

**Sintoma**: hotel_schema genera con todos los campos vacios (telephone/streetAddress/latitude MISSING).  
**Sintoma directo**: Log muestra `No places found for lat:0.0, lng:0.0`.  
**Causa aparente**: La consulta Places API se hace con coordenadas 0.0, 0.0 en lugar de coordenadas reales.  
**GBP data real disponible**:
- name: "Amazilia Hotel Campestre"
- rating: 4.5 (202 reviews)
- phone: "310 4019049"
- address: "mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda, Colombia"
- geo_score: 62 (verified)
- place_id: ChIJY8v6vep7OI4RdD22tR3SLRk

**Fix ya en codigo**:
- FASE-1: _build_search_queries usa nombre parseado (verificado en pre-flight)
- FASE-2: hotel_data.get para latitude/telephone/address (verificado en pre-flight)
- El problema es que el Places API no usa esas coordenadas porque las queries fallan

### 3. REGION LOWERCASE EN AUDIT_REPORT (G13)

**Sintoma**: audit_report.json muestra region "eje_cafetero" en lowercase.  
**Fix ya en codigo**: `modules/commercial_documents/v4_proposal_generator.py` linea 456 usa `.title()` sobre region.  
**Problema**: El audit_report se genera en FASE 2 y se guarda ANTES de que el proposal_generator aplique el fix de .title(). Ademas, el audit_report se genera a partir de la deteccion automatica de region (scraping + GBP), no del generator.

### 4. ASSET_CONFIDENCE BAJO (3/10 above 0.7)

**Sintoma**: Solo 3 de 10 assets con confidence >= 0.7.  
**Detalle**: Los assets se generan como ESTIMATED (confidence 0.5) porque las APIs reales no devolvieron datos verificables (PageSpeed API error, SerpAPI stub, etc.)

---

## Informacion clave para el proximo plan

### Archivos modificacos en FASE-1 a FASE-7

- `modules/auditors/v4_comprehensive.py` — FASE-1: _build_search_queries con nombre parseado
- `modules/asset_generation/conditional_generator.py` — FASE-2: hotel_schema con hotel_data.get (lat/tel/addr), FASE-5: FAQPage JSON-LD
- `main.py` — FASE-3: ContentScrubber importado
- `modules/commercial_documents/templates/propuesta_v6_template.md` — FASE-4: sin "24X", FASE-6: sin voice
- `modules/commercial_documents/v4_proposal_generator.py` — FASE-7: region .title()

### Archivos de evidencia

- `evidence/amh-release-validation/v4complete_release.log` — log completo de la ejecucion
- `evidence/amh-release-validation/VEREDICTO_FINAL_AMH_REFACTOR_V2.md` — veredicto completo
- `output/v4_complete/v4_complete_report.json` — reporte final con gates
- `output/v4_complete/audit_report.json` — audit con GBP data (geo_score=62 verified)

### Pre-flight de la sesion anterior

Todos los fixes de FASE-1 a FASE-7 estaban presentes en el codigo (verificado antes de ejecutar v4complete).

---

## Hipotesis para el nuevo plan

El problema NO es que los fixes no se escribieron en el codigo — todos estan en su lugar.  
El problema es que los fixes no se ejecutan correctamente en el pipeline v4complete por:

1. **Timing del scrubber**: La propuesta se genera en FASE 3.5 pero el scrubber en FASE 3.6 no recibe la ruta correcta del archivo, o la propuesta se genera DESPUES del scrubber.

2. **Consulta Places fallida**: Las coordenadas 0.0 indican que _build_search_queries devuelve query_name="Amaziliahotel" y query_location=None/invalido. Esto puede ser porque la region no se esta parseando correctamente desde la URL, o porque el GBP no hace fallback cuando no hay coordenadas.

3. **Region en audit_report**: Viene del scraper/GBP, no del proposal_generator — fix en proposal_generator no lo afecta.

---

## Criterios para el nuevo plan

- No iterar los mismos fixes (no re-escribir FASE-1 a FASE-7)
- Diagnosticar por que los fixes escritos no se ejecutan correctamente
- Centrarse en: timing del scrubber, query builder para Places, y como se determina la region para el audit_report
- Si se necesita un nuevo fix, debe ser sistematico (no half-measure)
