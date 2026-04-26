# FASE-TRAZABILIDAD-REFINEMENT: Plan de Correccion de Hallazgos

**Creado**: 2026-04-25
**Origen**: `.opencode/context/fase-trazabilidad-context.md`
**Estado**: Plan disenado — pendiente ejecucion
**Objetivo**: Resolver 4 items pendientes (D1-D4) + situacion GEO Score dual

---

## Resumen Ejecutivo

El diagnostico v4complete genera informacion confusa o incompleta en 4 areas:

| # | Problema | Impacto | Solucion |
|---|----------|---------|----------|
| D1 | WARNING no afecta readiness | Diagnostico muestra "READY" con datos Tier C | Agregar warnings al summary de readiness |
| D2 | Tier C invisible en encabezado financiero | Cliente ve "$2.6M/mes" sin saber que es estimado | Mostrar nivel de evidencia en el titulo y monto |
| D3 | Salud Tecnica GEO muestra 0/100 (bug de lectura) | Metrica de IA discovery rota — lee key incorrecta en JSON | Corregir path: `geo_assessment.total_score` |
| D4 | coherence=0.89 pero 8 assets bajo threshold | Impresion falsa de calidad | Agregar nota de transparencia en diagnostico |
| GEO | Dos fuentes de GEO Score — decision arquitectonica | Posible confusion | GBP prevalece (objetivo). geo_flow = AI discovery (distinto). |

---

## Decisiones de Diseno

### Decision GEO: GBP como fuente objetiva primaria

Se identificaron DOS modulos que generan un "GEO Score":

| Fuente | Modulo | Score | Naturaleza | Objetividad |
|--------|--------|-------|------------|-------------|
| **Pilar GEO** (tabla 4 Pilares) | `v4_diagnostic_generator.py:_calculate_geo_score()` L1393-1398 | 62/100 (ej: Amazilia) | GBP data de Google Places API | **EXTERNA — maxima objetividad** |
| **Salud Tecnica GEO** (tabla metricas IA) | `v4_diagnostic_generator.py` L1252-1264 lee `geo_flow_result.json` | 0/100 (BUG: deberia ser 23) | GEO Assessment interno (42 checks de AI readiness) | INTERNA — utilidad complementaria |

**VEREDICTO**: 
- `_calculate_geo_score()` (GBP/Google) PREVALECE como fuente autoritativa de GEO Score. Es externo, verificable, objetivo.
- El modulo `geo_flow` / `GEOAssessment` NO se depreca porque cumple un proposito DISTINTO: mide la preparacion del sitio web para AI crawlers (robots.txt, llms.txt, schema.org, meta tags, etc.) — NO es un duplicado del GBP geo_score.
- El bug de lectura en Salud Tecnica GEO (L1258: `geo_score` vs `geo_assessment.total_score`) se corrige.
- Para eliminar confusion, se renombra "Salud Tecnica GEO" → "Preparacion para IA Crawlers (GEO Tecnico)".

### Decision D1: WARNING en summary, no bloqueante

Se elige **Opcion C**: warnings visibles en el summary del readiness report, pero sin cambiar el estado `READY_FOR_PUBLICATION`. Razon:
- Tier C con defaults financieros es una estimacion legitima (benchmark regional)
- Bloquear publicacion por datos estimados seria excesivo para hoteles sin onboarding
- La transparencia (mostrar el warning) es suficiente

### Decision D2: Tier C visible en encabezado + banner

Se aplica **combinacion A+B**:
- El titulo financiero cambia a "Perdida Estimada por OTA" cuando Tier C
- El monto muestra etiqueta "(estimado — Tier C)"
- Banner visible sobre la seccion financiera explicando el nivel de evidencia

### Decision D4: Nota de transparencia

Cuando `asset_confidence` gate retorna WARNING, se agrega una linea en la seccion de Validacion de Calidad indicando cuantos assets tienen confianza baja y que se incluyen con disclaimer.

---

## Archivos a Modificar

| Archivo | Cambio | Items |
|---------|--------|-------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Corregir key geo_flow (L1258-1261) + Tier C en variables (L703+) + asset_confidence note | D3, D2, D4 |
| `modules/quality_gates/publication_gates.py` | Agregar warnings al summary (L1008-1014) | D1 |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Banner Tier C + etiqueta en monto (L68-76) | D2 |

---

## Validacion Final

Una UNICA ejecucion v4complete para **"Amazilia Hotel"** (asi aparece en Google Maps, web: https://amaziliahotel.com/) verificara:
- [ ] Pilar GEO muestra score real de GBP (NO 0/100 si el hotel existe en Google Maps)
- [ ] Salud Tecnica GEO muestra 23/100 (NO 0/100 unknown)
- [ ] Warnings financieros aparecen en gate_report.json
- [ ] Tier C es visible en encabezado financiero
- [ ] asset_confidence bajo genera nota de transparencia
- [ ] v4complete termina sin errores

---

## Estructura del Plan

```
.opencode/plans/FASE-TRAZABILIDAD-REFINEMENT/
├── README.md                                    ← Este archivo
├── 05-prompt-inicio-sesion-fase-TRAZABILIDAD-REFINEMENT.md
└── 06-checklist-implementacion.md
```
