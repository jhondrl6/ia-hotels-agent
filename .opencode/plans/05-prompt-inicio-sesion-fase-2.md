# FASE-2: Modulo GEO Diagnostic - Scoring con 42 metodos y 4 bands

**ID**: FASE-2
**Objetivo**: Crear `modules/geo_enrichment/geo_diagnostic.py` con la logica de scoring GEO basada en los 42 metodos y las 4 bandas de score
**Dependencias**: FASE-1 (mapeo de campos completado)
**Duracion estimada**: 2-3 horas
**Skill**: systematic-debugging, test-driven-development

---

## Contexto

La FASE-1 creo el mapeo entre hotel_data y los 42 metodos GEO. Ahora se implementa el modulo de diagnostico que evaluara cada sitio hotelero contra estos metodos.

### Base Tecnica Disponible
- Mapeo de campos: `.opencode/plans/GEO_FIELD_MAPPING.md`
- Estructura del proyecto: seguir patrones en `modules/asset_generation/`
- Tests: usar TDD, crear tests primero

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-1 | ✅ Completada |
| FASE-2 | ⏳ En progreso |

---

## Tareas

### Tarea 1: Crear estructura del modulo geo_enrichment

**Objetivo**: Crear directorio y archivo __init__.py

**Archivos afectados**:
- `modules/geo_enrichment/__init__.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Directorio `modules/geo_enrichment/` creado
- [ ] `__init__.py` exporta las clases principales
- [ ] Estructura consistente con otros modulos del proyecto

### Tarea 2: Implementar GEOBand enum y ScoreBreakdown

**Objetivo**: Definir las bandas de score y la estructura de desglose

**Archivos afectados**:
- `modules/geo_enrichment/geo_diagnostic.py` (NUEVO)

**Criterios de aceptacion**:
- [ ] Enum GEOBand: EXCELLENT (86-100), GOOD (68-85), FOUNDATION (36-67), CRITICAL (0-35)
- [ ] Dataclass ScoreBreakdown con 8 areas
- [ ] Metodo get_band() que retorna GEOBand

```python
class GEOBand(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FOUNDATION = "foundation"
    CRITICAL = "critical"

@dataclass
class ScoreBreakdown:
    robots: int  # /18
    llms: int    # /18
    schema: int  # /16
    meta: int    # /14
    content: int # /12
    brand: int   # /10
    signals: int # /6
    ai_discovery: int # /6
```

### Tarea 3: Implementar los 42 metodos de verificacion

**Objetivo**: Implementar las verificaciones de cada area segun GEO

**Criterios de aceptacion**:
- [ ] robots_check() - 22 AI bots en 3 tiers
- [ ] llms_check() - presencia, H1, blockquote, secciones, links
- [ ] schema_check() - WebSite, Organization, FAQPage, Article, richness
- [ ] meta_check() - title, description, canonical, OG
- [ ] content_check() - H1, statistics, citations, heading hierarchy
- [ ] brand_check() - coherence, knowledge graph links
- [ ] signals_check() - lang, RSS, freshness
- [ ] ai_discovery_check() - ai.txt, /ai/summary.json, /ai/faq.json, /ai/service.json

### Tarea 4: Implementar metodo diagnose()

**Objetivo**: Metodo principal que dado un site_url retorna GEOAssessment

**Criterios de aceptacion**:
- [ ] Recibe site_url y hotel_data
- [ ] Ejecuta los 42 checks
- [ ] Calcula score total (0-100)
- [ ] Retorna GEOAssessment con breakdown por area y band

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| `test_geo_band_enum.py` | `tests/geo_enrichment/test_geo_band_enum.py` | 4 bands correctos |
| `test_score_breakdown.py` | `tests/geo_enrichment/test_score_breakdown.py` | 8 areas inicializadas |
| `test_diagnose_hotelvisperas.py` | `tests/geo_enrichment/test_diagnose_hotelvisperas.py` | Score 34-45 para visperas |
| `test_band_classification.py` | `tests/geo_enrichment/test_band_classification.py` | Clasificacion correcta |

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
   - Marcar FASE-2 como ✅ Completada
   - Actualizar fecha de finalizacion

2. **`.opencode/plans/dependencias-fases.md`**
   - Verificar que FASE-1 esta marcada como dependencia satisfecha

3. **Documentacion de capacidad**
   - Si se crea nueva capability, documentar en capabilities.md

---

## Criterios de Completitud (CHECKLIST)

⚠️ Verificar ANTES de marcar como ✅ COMPLETADA ⚠️

- [ ] **Tests pasan**: Todos los tests en `tests/geo_enrichment/` ejecutan exitosamente
- [ ] ** GEOBand enum correcto**: 4 bands con rangos correctos
- [ ] **42 metodos implementados**: Cada metodo del mapeo FASE-1 implementado
- [ ] **diagnose() funcional**: Retorna GEOAssessment con breakdown y band
- [ ] **hotelvisperas.com evaluado**: Score obtenido documentado
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa

---

## Restricciones

- El modulo debe ser COMPLETAMENTE ORTOGONAL al pipeline existente
- No debe invocar ni depender de modules/asset_generation/conditional_generator.py
- Solo recibe hotel_data como input, no lo modifica
- Los 42 metodos deben ser implementados como metodos separados para trazabilidad

---

## Prompt de Ejecucion

```
Actua como backend developer.

OBJETIVO: Implementar modules/geo_enrichment/geo_diagnostic.py con scoring GEO

CONTEXTO:
- FASE-1 completo: mapeo de 42 metodos disponible
- Siguiente paso: integrarlos en modulo funcional
- Importancia de tests primero (TDD)

TAREAS:
1. Crear estructura de modulo
2. Implementar GEOBand enum y ScoreBreakdown
3. Implementar los 42 metodos de verificacion
4. Implementar metodo diagnose() principal
5. Crear tests para cada componente

REGLAS:
- 42 metodos como metodos separados (para debugging)
- diagnose() recibe site_url + hotel_data, retorna GEOAssessment
- Output debe incluir breakdown por area + band + score total
- NINGUNA dependencia con pipeline existente (ortogonal)
```
