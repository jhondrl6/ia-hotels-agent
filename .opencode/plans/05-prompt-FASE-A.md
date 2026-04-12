# FASE-A: Score Redistribution — CHECKLIST_IAO a 4 Pilares

**ID**: FASE-A
**Objetivo**: Eliminar el sistema dual de scoring (CHECKLIST_IAO + 4-Pilar scores), redistribuir los 12 elementos del CHECKLIST a 4 pilares coherentes (SEO/GEO/AEO/IAO), y unificar la fuente de verdad.
**Dependencias**: Ninguna (fase fundacional)
**Duración estimada**: 3-4 horas
**Skill**: `test-driven-development`, `iah-cli-phased-execution`

---

## Contexto

### Problema
El código tiene DOS sistemas paralelos de scoring que miden cosas similares con pesos distintos:
1. **CHECKLIST_IAO** (12 elementos, 100pts) → usado para sugerir paquetes (basico/avanzado/premium)
2. **4-Pilar scores** (GEO/Competitive/SEO/AEO, cada uno 0-100) → usado para display en diagnóstico

Ambos usan las mismas métricas (schema, OG, LCP) pero con pesos distintos. El CHECKLIST_IAO mezcla elementos de los 4 pilares sin distinguir capas.

### Decisión de diseño (ya resuelta)
- **OPCIÓN A**: Scores independientes 0-100 por pilar, SIN gate booleano
- Score global = promedio ponderado SEO(25%) + GEO(25%) + AEO(25%) + IAO(25%)
- Advertencia visual si un pilar superior supera al inferior (ej: "AEO 60 pero SEO 30")
- CHECKLIST_IAO se REEMPLAZA por 4 checklists: CHECKLIST_SEO, CHECKLIST_GEO, CHECKLIST_AEO, CHECKLIST_IAO

### Base técnica disponible
- Tests base: ~385 tests, 0 regresiones
- Python path: `./venv/Scripts/python.exe` (NO python3, NO .venv)
- Proyecto en `/mnt/c/Users/Jhond/Github/iah-cli`

---

## Tareas

### Tarea 1: Crear 4 diccionarios de pesos (CHECKLIST_SEO/GEO/AEO/IAO)

**Objetivo**: Reemplazar el diccionario único `pesos` de `calcular_cumplimiento()` por 4 diccionarios independientes, cada uno sumando 100pts.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L90-103)

**Nueva distribución de pesos** (confirmada en contexto del proyecto):

```python
CHECKLIST_SEO = {
    "ssl": 15,
    "schema_hotel": 20,       # Schema base = SEO fundamental
    "LCP_ok": 20,
    "CLS_ok": 10,
    "imagenes_alt": 15,
    "blog_activo": 10,
    "schema_reviews": 10,     # Reviews en schema = credibility SEO
}
# Total: 100pts

CHECKLIST_GEO = {
    "nap_consistente": 15,
    "redes_activas": 10,
    "geo_score_gbp": 30,      # Ya existe: audit_result.gbp.geo_score
    "fotos_gbp": 15,          # Ya existe: audit_result.gbp.photos
    "horario_gbp": 15,        # Ya existe: audit_result.gbp (check horarios)
    "schema_reviews_geo": 15, # Reviews con ubicación
}
# Total: 100pts

CHECKLIST_AEO = {
    "schema_faq": 25,         # FAQ = fuente directa para snippets
    "open_graph": 15,         # OG = metadatos para posición cero
    "schema_hotel_aeo": 15,   # Schema detallado para extracción factual
    "contenido_factual": 20,  # Horarios, precios, servicios accesibles
    "speakable_schema": 10,   # Schema específico voz (nuevo campo, default False)
    "imagenes_alt_aeo": 15,   # Alt text como fuente para image snippets
}
# Total: 100pts

CHECKLIST_IAO = {
    "citability_score": 20,   # Ya existe: audit_result.citability.overall_score
    "contenido_extenso": 15,  # Ya existe como elemento KB
    "llms_txt_exists": 15,    # Nuevo: check si llms.txt generado
    "crawler_access": 15,     # Ya existe: ai_crawler_auditor
    "brand_signals": 10,      # Nuevo: SameAs, enlaces sociales
    "ga4_indirect": 10,       # Ya existe (ADVISORY): GA4 indirect traffic
    "schema_advanced": 15,    # Schema Entity + SameAs (nuevo campo)
}
# Total: 100pts
```

**Criterios de aceptación**:
- [ ] 4 diccionarios creados, cada uno sumando exactamente 100
- [ ] Los 12 elementos originales del CHECKLIST_IAO están distribuidos entre los 4 nuevos
- [ ] Elementos nuevos (speakable_schema, llms_txt_exists, etc.) tienen default=False
- [ ] Imports correctos, sin circular dependencies

### Tarea 2: Crear 4 funciones calcular_score_pilar()

**Objetivo**: Reemplazar `calcular_cumplimiento()` por 4 funciones independientes.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L75-109)

**Implementación**:
```python
def calcular_score_seo(elementos: dict) -> int:
    """Score SEO: Para que te ENCUENTREN (0-100)."""
    if not elementos:
        return 0
    return min(100, sum(CHECKLIST_SEO[k] for k, v in elementos.items() if v is True and k in CHECKLIST_SEO))

def calcular_score_geo(elementos: dict) -> int:
    """Score GEO: Para que te UBICQUEN (0-100)."""
    # Similar pattern, pero también incorpora geo_score_gbp real
    ...
    
def calcular_score_aeo(elementos: dict) -> int:
    """Score AEO: Para que te CITEN (0-100)."""
    ...
    
def calcular_score_iao(elementos: dict) -> int:
    """Score IAO: Para que te RECOMIENDEN (0-100)."""
    ...

def calcular_score_global(seo: int, geo: int, aeo: int, iao: int) -> int:
    """Visibilidad Digital = promedio ponderado 4 pilares."""
    return int((seo * 0.25) + (geo * 0.25) + (aeo * 0.25) + (iao * 0.25))
```

**Criterios de aceptación**:
- [ ] `calcular_cumplimiento()` marcada como deprecated pero SIGUE FUNCIONANDO (backward compat)
- [ ] 4 funciones nuevas cada una retorna 0-100
- [ ] `calcular_score_global()` retorna 0-100
- [ ] `sugerir_paquete()` ahora recibe el score_global en lugar de score_tecnico

### Tarea 3: Actualizar _extraer_elementos_de_audit() para 4 pilares

**Objetivo**: La función actual (L1801-1860) extrae 12 elementos planos. Debe extraer elementos para cada pilar por separado, incluyendo los nuevos campos.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L1801-1860)

**Implementación**: Crear 4 funciones extractoras:
```python
def _extraer_elementos_seo(audit_result) -> dict
def _extraer_elementos_geo(audit_result) -> dict
def _extraer_elementos_aeo(audit_result) -> dict
def _extraer_elementos_iao(audit_result) -> dict
```

Mantener `_extraer_elementos_de_audit()` como wrapper que llama las 4 y combina para backward compat.

**Nuevos campos a extraer**:
- `speakable_schema`: Check si schema tiene speakable markup (default False por ahora)
- `llms_txt_exists`: Check si existe archivo llms.txt (usar llmstxt_generator.check_exists o similar)
- `crawler_access`: Usar ai_crawler_auditor (ya existe)
- `brand_signals`: Check SameAs links en schema (default False)
- `schema_advanced`: Check si tiene Entity schema + SameAs (default False)
- `contenido_factual`: Proxy = schema_hotel válido Y tiene horarios/precios en schema

**Criterios de aceptación**:
- [ ] 4 funciones nuevas extraen elementos correctos por pilar
- [ ] `_extraer_elementos_de_audit()` mantiene firma actual para backward compat
- [ ] Cada nuevo campo tiene default False cuando no hay datos
- [ ] No se rompe ningún test existente

### Tarea 4: Actualizar DiagnosticSummary para 4 pilares

**Objetivo**: Añadir campos de score por pilar al dataclass DiagnosticSummary.

**Archivos afectados**:
- `modules/commercial_documents/data_structures.py` (L280-308)

**Cambios**:
```python
@dataclass
class DiagnosticSummary:
    # ... campos existentes ...
    score_tecnico: Optional[int] = None   # DEPRECATED - mantener por backward compat
    
    # === NUEVOS CAMPOS 4 PILARES ===
    score_seo: Optional[int] = None       # 0-100
    score_geo: Optional[int] = None       # 0-100
    score_aeo: Optional[int] = None       # 0-100
    score_iao: Optional[int] = None       # 0-100
    score_global: Optional[int] = None    # Promedio ponderado
    
    # Checklist por pilar (para mostrar desglose en propuestas)
    elementos_seo: Optional[Dict[str, bool]] = None
    elementos_geo: Optional[Dict[str, bool]] = None
    elementos_aeo: Optional[Dict[str, bool]] = None
    elementos_iao: Optional[Dict[str, bool]] = None
```

**Criterios de aceptación**:
- [ ] Nuevos campos añadidos con defaults None
- [ ] `score_tecnico` se calcula como alias de `score_global` (backward compat)
- [ ] No se eliminan campos existentes

### Tarea 5: Actualizar _prepare_template_data() para incluir 4 pilares

**Objetivo**: Inyectar los nuevos scores en el diccionario de variables de template.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L504-570)

**Cambios**:
- Calcular los 4 scores y score_global
- Añadir `iao_score`, `iao_status`, `iao_regional_avg` al dict de template
- Añadir `score_global` y `score_global_status`
- Mantener variables existentes (`geo_score`, `aeo_score`, `seo_score`, `schema_infra_score`) como aliases

**Criterios de aceptación**:
- [ ] Template recibe `iao_score`/`iao_status`/`iao_regional_avg` (antes eliminados en FASE-CAUSAL-01)
- [ ] Template recibe `score_global`/`score_global_status`
- [ ] Variables v6 existentes (`geo_score`, `aeo_score`, `seo_score`) siguen funcionando
- [ ] `schema_infra_score` se mantiene como alias de `aeo_score` por backward compat

### Tarea 6: Actualizar ELEMENTO_KB_TO_PAIN_ID

**Objetivo**: Añadir mapeos para los nuevos elementos KB.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L52-67)

**Nuevos mapeos**:
```python
"speakable_schema": ("no_speakable", "voice_guide", None),
"llms_txt_exists":  ("no_llms_txt", "llms_txt", None),
"crawler_access":   ("ia_crawler_blocked", "optimization_guide", None),
"brand_signals":    ("weak_brand_signals", "org_schema", None),
"schema_advanced":  ("no_entity_schema", "org_schema", None),
"contenido_factual": ("no_factual_data", "hotel_schema", None),
```

**Criterios de aceptación**:
- [ ] Nuevos elementos tienen pain_id y asset asignados
- [ ] Los pain_ids nuevos se reflejan en PainSolutionMapper (o se crea ticket para FASE-D)
- [ ] ELEMENTOS_MONETIZABLES se recalcula automáticamente

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Tests pesos | `tests/commercial_documents/test_aeo_score.py` | 4 diccionarios suman 100 cada uno |
| Tests scoring | `tests/commercial_documents/test_aeo_score.py` | calcular_score_* retorna 0-100 |
| Tests extracción | `tests/commercial_documents/test_aeo_score.py` | _extraer_elementos_* extrae correctamente |
| Tests backward compat | `tests/commercial_documents/test_aeo_score.py` | calcular_cumplimiento() sigue funcionando |
| Tests DiagnosticSummary | `tests/data_validation/test_aeo_kpis.py` | Nuevos campos aceptan None sin error |
| Tests integración | `tests/test_audit_alignment.py` | v4complete no se rompe |
| Suite completa | — | 385+ tests, 0 regresiones |

**Comandos de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_aeo_score.py tests/data_validation/test_aeo_kpis.py -v
./venv/Scripts/python.exe -m pytest tests/ -x --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** → Marcar FASE-A como completada con fecha
2. **`06-checklist-implementacion.md`** → Marcar items de FASE-A como completados
3. **`09-documentacion-post-proyecto.md`** → Sección A: módulos modificados, Sección D: métricas
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "Score Redistribution: CHECKLIST_IAO a 4 pilares (SEO/GEO/AEO/IAO)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/data_structures.py" \
    --tests "385" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] 4 diccionarios de pesos creados (CHECKLIST_SEO/GEO/AEO/IAO)
- [ ] 4 funciones calcular_score_* creadas y funcionando
- [ ] calcular_score_global() implementado
- [ ] calcular_cumplimiento() marcada deprecated pero funcional
- [ ] sugerir_paquete() usa score_global
- [ ] _extraer_elementos_de_audit() actualizado con wrapper 4-pilar
- [ ] DiagnosticSummary tiene campos score_seo/geo/aeo/iao/global
- [ ] _prepare_template_data() inyecta iao_score y score_global
- [ ] ELEMENTO_KB_TO_PAIN_ID tiene nuevos elementos
- [ ] Tests existentes pasan (0 regresiones)
- [ ] Tests nuevos para 4-pilar scoring pasan
- [ ] log_phase_completion.py ejecutado
- [ ] dependencias-fases.md actualizado

---

## Restricciones

- NO eliminar funciones existentes (marcar deprecated)
- NO cambiar la interfaz de `_calculate_aeo_score()` actual (eso es FASE-B)
- NO añadir SerpAPI ni LLM Checker (eso es FASE-B/C)
- NO cambiar paquetes comerciales (eso es FASE-D)
- NO modificar templates directamente (eso es FASE-D)
- Los nuevos campos con datos no disponibles deben defaultear a False/None
- Python ejecutable: `./venv/Scripts/python.exe` (NO python3)
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`
