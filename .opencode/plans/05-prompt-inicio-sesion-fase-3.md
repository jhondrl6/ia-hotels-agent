# FASE-3: Modulo GEO Enrichment Layer - Generacion condicional por caso operativo

**ID**: FASE-3
**Objetivo**: Crear `modules/geo_enrichment/geo_enrichment_layer.py` que genera assets enriquecidos condicionalmente segun el score band Y el caso operativo
**Dependencias**: FASE-2 (GEO Diagnostic implementado)
**Duracion estimada**: 2-3 horas
**Skill**: systematic-debugging

---

## Casos Operativos (DELIVERABLES)

Este es el caso operativo real que DEBE funcionar:

| Caso | GEO Score | Archivos Generados |
|------|-----------|-------------------|
| **MINIMAL (Caso A)** | 86-100 (EXCELLENT) | Solo `geo_badge.md` |
| **LIGHT (Caso B)** | 68-85 (GOOD) | `geo_badge.md`, `geo_dashboard.md`, `geo_checklist_min.md` |
| **FULL (Casos C/D)** | <68 (FOUNDATION/CRITICAL) | `geo_dashboard.md`, `llms.txt`, `hotel_schema_rich.json`, `faq_schema.json`, `geo_fix_kit.md` |

**CRÍTICO**: El Caso A (EXCELLENT - GEO no necesita mejora) es el caso operativo válido. El sistema debe funcionar sin errores cuando el diagnóstico indica que GEO está bien.

---

## Contexto

La FASE-2 implemento el modulo de diagnostico GEO. Ahora se implementa la capa de enrichment que genera los archivos enriquecidos de forma condicional segun el score band.

### Arquitectura de Decision

```
[GEO Assessment]
      │
      ├─ Band.EXCELLENT (86-100) → Genera: geo_badge.md, dashboard_minimal
      ├─ Band.GOOD (68-85) → Genera: geo_badge.md, dashboard, checklist_min
      ├─ Band.FOUNDATION (36-67) → Genera: llms.txt, schema_rich, faq_schema, dashboard
      └─ Band.CRITICAL (0-35) → Genera: + robots_fix, seo_fix_kit, propuesta_seccion
```

### Archivos a Generar por Band

| Band | Archivos |
|------|----------|
| EXCELLENT | `geo_badge.md`, `geo_dashboard.md` |
| GOOD | `geo_badge.md`, `geo_dashboard.md`, `geo_checklist_min.md` |
| FOUNDATION | + `llms.txt`, `hotel_schema_rich.json`, `faq_schema.json`, `geo_fix_kit.md` |
| CRITICAL | + `robots_fix.txt`, `seo_fix_kit.md`, seccion en propuesta |

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2 | ✅ Completada |
| FASE-3 | ⏳ En progreso |

---

## Tareas

### Tarea 1: Implementar GEOEnrichmentLayer

**Objetivo**: Clase principal que orquesta la generacion de assets segun band

**Archivos afectados**:
- `modules/geo_enrichment/geo_enrichment_layer.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Metodo `generate(hotel_data, geo_assessment, output_dir)` retorna lista de archivos generados
- [ ] Decision condicional segun band
- [ ] Logs claros de que se genero y por que

### Tarea 2: Implementar LLMsTxtGenerator

**Objetivo**: Generador de llms.txt segun especificacion GEO

**Archivos afectados**:
- `modules/geo_enrichment/llms_txt_generator.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Genera archivo con H1, descripcion citable, secciones
- [ ] Incluye: nombre, ubicacion, amenities, CTA, contacto
- [ ] Formato compatible con ChatGPT, Perplexity, Claude

### Tarea 3: Implementar HotelSchemaEnricher

**Objetivo**: Enriquecedor del schema.org basico a version rica con 16+ campos

**Archivos afectados**:
- `modules/geo_enrichment/hotel_schema_enricher.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Toma schema existente y agrega campos faltantes
- [ ] Agrega: geo, image, priceRange, amenityFeature, aggregateRating
- [ ] Valida que el schema enriquecido sea valido JSON-LD

### Tarea 4: Implementar GEODashboard

**Objetivo**: Generador de dashboard con scoring bands y gaps

**Archivos afectados**:
- `modules/geo_enrichment/geo_dashboard.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Incluye score total con banda
- [ ] Breakdown por area (8 areas)
- [ ] Lista de gaps priorizados
- [ ] Recomendaciones de siguiente paso

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_enrichment_layer_excellent.py` | `tests/geo_enrichment/test_enrichment_layer_excellent.py` | Solo 2 archivos para EXCELLENT |
| `test_enrichment_layer_critical.py` | `tests/geo_enrichment/test_enrichment_layer_critical.py` | 7+ archivos para CRITICAL |
| `test_llms_txt_generator.py` | `tests/geo_enrichment/test_llms_txt_generator.py` | Contenido valido |
| `test_hotel_schema_enricher.py` | `tests/geo_enrichment/test_hotel_schema_enricher.py` | Schema valido con 16+ campos |
| `test_geo_dashboard.py` | `tests/geo_enrichment/test_geo_dashboard.py` | Band y gaps correctos |

**Comando de validacion**:
```bash
python -m pytest tests/geo_enrichment/ -v
python scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`.opencode/plans/README.md`**
   - Marcar FASE-3 como ✅ Completada
   - Agregar fecha de finalizacion

2. **Verificar Capability Contract**
   - GEOEnrichmentLayer debe aparecer como "conectada" en capabilities.md
   - Punto de invocacion: se definira en FASE-4

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] **GEOEnrichmentLayer implementado**: Genera archivos segun band
- [ ] **LLMsTxtGenerator**: Genera llms.txt valido
- [ ] **HotelSchemaEnricher**: Schema con 16+ campos
- [ ] **GEODashboard**: Dashboard con bands y gaps
- [ ] **Tests pasan**: Todos los tests de enrichment ejecutan
- [ ] **Condicionalidad funciona**: Diferentes outputs segun band

---

## Restricciones

- Todos los archivos se generan en subdirectorio `geo_enriched/` (no reemplazar originals)
- El metodo principal `generate()` retorna lista de archivos generados
- No debe invocar pipeline existente de assets
- La propuesta commercial NO se modifica, solo se enriquece con referencia a assets GEO

---

## Prompt de Ejecucion

```
Actua como backend developer.

OBJETIVO: Implementar capa de enrichment GEO condicional por score band

CONTEXTO:
- FASE-2 completo: geo_diagnostic.py con scoring
- Arquitectura: decision tree por band (EXCELLENT/GOOD/FOUNDATION/CRITICAL)
- Archivos enriquecidos van en geo_enriched/ (no reemplazar)

TAREAS:
1. Implementar GEOEnrichmentLayer con generate(hotel_data, geo_assessment, output_dir)
2. Implementar LLMsTxtGenerator para llms.txt
3. Implementar HotelSchemaEnricher para schema rico
4. Implementar GEODashboard para dashboard con bands
5. Tests para cada generador

REGLAS:
- generate() retorna lista de archivos generados
- Decision condicional: band determina archivos a generar
- geo_enriched/ subdirectorio para evitar colisiones
- 0 dependencias con pipeline de assets existente
```
