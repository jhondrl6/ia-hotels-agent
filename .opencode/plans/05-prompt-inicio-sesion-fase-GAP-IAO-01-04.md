# GAP-IAO-01-04: Assets con PainSolutionMapper

**ID**: GAP-IAO-01-04
**Objetivo**: Conectar las recomendaciones del diagnóstico a los assets del conditional_generator
**Dependencias**: GAP-IAO-01-03 (propuesta con monetización)
**Duración estimada**: 1-2 horas
**Skill**: Ninguna específica (conectar lo que existe)

---

## Contexto

### Qué debe hacer esta fase

1. **Verificar** que PainSolutionMapper cubre todos los faltantes del CHECKLIST_IAO
2. **Conectar** recommendations del diagnóstico → conditional_generator
3. **Generar assets** solo para los faltantes específicos del hotel

### De FASE-0

```
DIAGNÓSTICO detecta: faltantes = ["schema_hotel", "schema_faq", "open_graph"]
    │
    ▼
PAIN_SOLUTION_MAP tiene: pain_id → asset
    │
    ▼
CONDITIONAL_GENERATOR genera: solo assets para pain_ids detectados
```

---

## Tareas

### Tarea 1: Verificar cobertura de PainSolutionMapper vs CHECKLIST_IAO

**Archivo**: `modules/commercial_documents/pain_solution_mapper.py`

**Comparar**:

| Elemento CHECKLIST_IAO | Pain ID en Mapper | Asset | Cobertura |
|------------------------|-------------------|-------|-----------|
| `ssl` | ? | ? | ? |
| `schema_hotel` | `no_hotel_schema` | `hotel_schema` | ✅ |
| `schema_reviews` | ? | ? | ? |
| `LCP_ok` | ? | ? | ? |
| `CLS_ok` | ? | ? | ? |
| `contenido_extenso` | `low_content` | ? | ? |
| `open_graph` | `no_og_tags` | ? | ? |
| `schema_faq` | `no_faq_schema` | `faq_page` | ✅ |
| `nap_consistente` | `nap_conflict` | ? | ? |
| `imagenes_alt` | ? | ? | ? |
| `blog_activo` | ? | ? | ? |
| `redes_activas` | ? | ? | ? |

**Criterios de aceptación**:
- [ ] Documentar qué elementos del CHECKLIST_IAO tienen Pain ID
- [ ] Documentar qué elementos NO tienen Pain ID
- [ ] Agregar Pain IDs faltantes si es necesario

### Tarea 2: Modificar conditional_generator para recibir recommendations

**Archivo**: `modules/asset_generation/conditional_generator.py`

**Necesario**: El método `generate()` recibe `asset_type` pero no `recommendations` ni `faltantes`.

**Opciones de implementación**:

**Opción A (recomendada)**: Crear método `generate_for_faltantes()` que reciba lista de faltantes:

```python
def generate_for_faltantes(
    self,
    faltantes: List[str],  # Lista de pain_ids del diagnóstico
    validated_data: Dict,
    hotel_name: str,
    hotel_id: str,
    hotel_context: Optional[Dict[str, Any]] = None,
    site_url: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Genera assets SOLO para los faltantes específicos.
    
    Args:
        faltantes: Lista de pain_ids detectados (ej: ["no_hotel_schema", "no_faq_schema"])
        ...
    """
    results = []
    
    # Mapear faltantes → assets
    PAIN_TO_ASSET = {
        "no_hotel_schema": "hotel_schema",
        "no_faq_schema": "faq_page",
        "no_og_tags": "og_tags",  # Si existe
        "nap_conflict": "nap_guide",  # Si existe
        # ... continuar
    }
    
    for faltante in faltantes:
        asset_type = PAIN_TO_ASSET.get(faltante)
        if asset_type:
            result = self.generate(
                asset_type=asset_type,
                validated_data=validated_data,
                hotel_name=hotel_name,
                hotel_id=hotel_id,
                hotel_context=hotel_context,
                site_url=site_url
            )
            results.append(result)
    
    return results
```

**Criterios de aceptación**:
- [ ] Método nuevo recibe lista de faltantes/pain_ids
- [ ] Solo genera assets para los faltantes detectados
- [ ] Mantiene backwards: `generate()` sigue funcionando igual

### Tarea 3: Actualizar Pain IDs faltantes en PainSolutionMapper

**Si hay elementos del CHECKLIST_IAO sin Pain ID**, agregarlos:

```python
# Agregar a PAIN_SOLUTION_MAP en pain_solution_mapper.py

"no_schema_reviews": {
    "assets": ["hotel_schema"],  # Con aggregateRating
    "confidence_required": 0.8,
    "priority": 1,
    "validation_fields": ["reviews_count"],
    "estimated_impact": "high",
    "name": "Sin Reseñas Estructuradas",
    "description": "No se detecta aggregateRating en Schema"
},

"low_lcp": {
    "assets": ["lcP_guide"],  # Guía optimización
    "confidence_required": 0.7,
    "priority": 1,
    "validation_fields": ["lcp_ms"],
    "estimated_impact": "high",
    "name": "LCP Lento",
    "description": "Largest Contentful Paint > 2500ms"
},

"no_og_tags": {
    "assets": ["og_tags_asset"],  # Asset meta tags
    "confidence_required": 0.6,
    "priority": 2,
    "validation_fields": ["og_title", "og_description"],
    "estimated_impact": "medium",
    "name": "Sin Open Graph",
    "description": "No se detectan meta tags de Open Graph"
},

"no_ssl": {
    "assets": ["ssl_guide"],  # Guía SSL
    "confidence_required": 0.9,
    "priority": 1,
    "validation_fields": ["ssl_detected"],
    "estimated_impact": "high",
    "name": "Sin SSL",
    "description": "Site no usa HTTPS o tiene problemas de certificado"
},
```

**Criterios de aceptación**:
- [ ] Todos los elementos críticos del CHECKLIST_IAO tienen Pain ID
- [ ] Cada Pain ID tiene al menos un asset
- [ ] PainSolutionMapper y Pain IDs de _identify_brechas() son consistentes

---

## Archivos a modificar

| Archivo | Qué modificar |
|---------|--------------|
| `modules/asset_generation/conditional_generator.py` | Agregar `generate_for_faltantes()` |
| `modules/commercial_documents/pain_solution_mapper.py` | Agregar Pain IDs faltantes |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`06-checklist-implementacion.md`**: Marcar GAP-IAO-01-04 como completada

2. **Ejecutar**:
```bash
python scripts/log_phase_completion.py \
    --fase GAP-IAO-01-04 \
    --desc "conditional_generator recibe faltantes → solo genera assets necesarios" \
    --archivos-mod "modules/asset_generation/conditional_generator.py,modules/commercial_documents/pain_solution_mapper.py" \
    --check-manual-docs
```

---

## Criterios de Completitud

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] PainSolutionMapper cubre todos los elementos del CHECKLIST_IAO
- [ ] Pain IDs en `_identify_brechas()` son consistentes con PainSolutionMapper
- [ ] `generate_for_faltantes()` existe y recibe lista de pain_ids
- [ ] Solo genera assets para faltantes detectados
- [ ] `generate()` original sigue funcionando (backwards)
- [ ] `log_phase_completion.py` ejecutado

---

## Flujo completo post-fase 04

```
AUDITORÍA
    │
    ▼
DIAGNÓSTICO (GAP-IAO-01-02)
    ├── detecta: elementos CHECKLIST_IAO
    ├── score_tecnico = calcular_cumplimiento()
    ├── score_ia = AEOKPIs.calculate_composite_score()
    ├── faltantes = elementos que fallan
    └── paquete = sugerir_paquete(score_tecnico)
    │
    ▼
PROPUESTA (GAP-IAO-01-03)
    ├── recibe: DiagnosticSummary con score y faltantes
    ├── monetiza: cada faltante = pérdida mensual
    └── recomienda: paquete + assets por faltante
    │
    ▼
ASSETS (GAP-IAO-01-04)
    ├── recibe: faltantes = ["schema_hotel", "schema_faq"]
    ├── PainSolutionMapper: pain_id → asset
    └── conditional_generator: solo genera para ["hotel_schema", "faq_page"]
```
