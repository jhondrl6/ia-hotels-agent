# FASE-1: Diagnostico - Mapeo de hotel_data a GEO Fields

**ID**: FASE-1
**Objetivo**: Crear el mapeo completo entre los campos de hotel_data y los campos que GEO Optimizer necesita para generar sus 42 checks
**Dependencias**: Ninguna
**Duracion estimada**: 1-2 horas
**Skill**: systematic-debugging

---

## Contexto

El proyecto GEO Enrichment Integration busca integrar capacidades de GEO (Generative Engine Optimization) al pipeline de iah-cli como capa de enrichment ortogonal. El objetivo es fortalecer los assets existentes sin generar desconexiones.

### Base Tecnica Disponible
- Estructura de directorios: `modules/geo_enrichment/` (por crear)
- Hotel data model: `data_models/canonical_assessment.py`
- Assets actuales: `modules/asset_generation/`
- Tests base: ~1700+ test functions

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ⏳ En progreso |

---

## Tareas

### Tarea 1: Analizar hotel_data fields disponibles

**Objetivo**: Identificar todos los campos que hotel_data provee

**Accion**: Ejecutar grep para encontrar la estructura de CanonicalAssessment y campos relacionados:

```bash
grep -n "class CanonicalAssessment" data_models/canonical_assessment.py
grep -n "hotel_name\|whatsapp\|adr\|ubicacion\|amenities\|description" data_models/canonical_assessment.py
```

**Criterios de aceptacion**:
- [ ] Lista completa de campos hotel_data identificada
- [ ] Cada campo categorizado por tipo (string, float, bool, list)

### Tarea 2: Mapear hotel_data a los 42 metodos GEO

**Objetivo**: Crear documento de mapeo hotel_data → GEO requirements

**Accion**: Consultar README.md de geo-optimizer-skill para los 42 metodos en 8 areas:

| Area GEO | Puntos | Campos hotel_data necesarios |
|----------|--------|------------------------------|
| Robots.txt | /18 | url, site_url |
| llms.txt | /18 | hotel_name, description, amenities, location |
| Schema JSON-LD | /16 | name, url, telephone, address, amenityFeature, review |
| Meta Tags | /14 | title, description, canonical |
| Content | /12 | h1, statistics, external_citations, heading_hierarchy |
| Brand & Entity | /10 | brand_name, knowledge_graph_links |
| Signals | /6 | html_lang, rss_feed, date_modified |
| AI Discovery | /6 | ai_txt, ai_summary_json, ai_faq_json |

**Criterios de aceptacion**:
- [ ] Documento `GEO_FIELD_MAPPING.md` creado en `.opencode/plans/`
- [ ] Tabla de coberturahotel_data vs GEO requirements
- [ ] Identificar gaps: campos que GEO necesita pero hotel_data no provee

### Tarea 3: Identificar gaps y estrategias de obtencion

**Objetivo**: Documentar que hacer con campos faltantes

**Criterios de aceptacion**:
- [ ] Lista de gaps con fuente alternativa (scraping, benchmark, default)
- [ ] Indicador de si el gap es BLOCKING o MITIGABLE

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| N/A (fase de diagnostico) | - | - |

Esta fase es de diagnostico, no genera codigo ejecutable. El unico entregable es el documento de mapeo.

**Comando de validacion**:
```bash
# Solo verificacion de formato
ls -la .opencode/plans/GEO_FIELD_MAPPING.md
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`.opencode/plans/README.md`**
   - Marcar FASE-1 como ✅ Completada
   - Agregar fecha de finalizacion

2. **`.opencode/plans/GEO_FIELD_MAPPING.md`** (si no existe, crear)
   - Documento de mapeo completo

3. **Documentacion de diagnostico**
   - Agregar notas de gaps encontrados

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] **Documento de mapeo existe**: `GEO_FIELD_MAPPING.md` en `.opencode/plans/`
- [ ] **Cobertura documentada**: Tabla con 42 metodos vs campos hotel_data
- [ ] **Gaps identificados**: Lista de campos faltantes con estrategia
- [ ] **README.md actualizado**: FASE-1 marcada como completada

---

## Restricciones

- No modificar ningun archivo de codigo en esta fase
- Solo analisis y documentacion
- Si un campo es critico para GEO y no existe en hotel_data, documentar como gap BLOCKING

---

## Prompt de Ejecucion

```
Actua como data analyst.

OBJETIVO: Crear mapeo completo entre hotel_data y los 42 metodos de GEO Optimizer

CONTEXTO:
- Proyecto: GEO Enrichment Integration para iah-cli
- Campo de estudio: geo-optimizer-skill de Auriti-Labs
- Objetivo: Integrar sin generar desconexiones

TAREAS:
1. Identificar estructura de hotel_data (campos disponibles)
2. Listar los 42 metodos GEO por area (8 areas)
3. Crear tabla de mapeo: campo hotel_data → requerimiento GEO
4. Identificar gaps y estrategias de obtencion

ENTREGABLE:
- Documento GEO_FIELD_MAPPING.md en .opencode/plans/
- Tabla de cobertura
- Lista de gaps con severidad
```
