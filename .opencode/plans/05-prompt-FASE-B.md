# FASE-B: AEO Real Measurement — SerpAPI + Refactor _calculate_aeo_score

**ID**: FASE-B
**Objetivo**: Refactorizar `_calculate_aeo_score()` para que mida resultado (featured snippets capturados) y no solo infraestructura (schema válido). Integrar SerpAPI como fuente de datos real.
**Dependencias**: FASE-A completada (estructura 4 pilares disponible)
**Duración estimada**: 3-4 horas
**Skill**: `test-driven-development`, `iah-cli-phased-execution`

---

## Contexto

### Problema actual
`_calculate_aeo_score()` (v4_diagnostic_generator.py L1401-1455) mide 4 componentes × 25pts:
1. Schema Hotel válido (25pts) → infraestructura, no resultado
2. FAQ Schema válido (25pts) → infraestructura, no resultado
3. Open Graph detectado (25pts) → infraestructura, no resultado
4. Citabilidad >= 70 (25pts) → **esto es IAO, no AEO** (se movió en FASE-A)

Ninguno mide si el hotel realmente captura featured snippets o "People Also Ask".

### Qué es AEO correctamente
AEO = "Para que te CITEN" — Google extrae tu dato como respuesta directa para preguntas factuales.
Métricas correctas:
- Featured snippets capturados (posición cero)
- "People Also Ask" presence
- Speakable schema
- Cobertura de queries factuales (horario, precio, dirección)

### Fuentes de datos
- **SerpAPI**: Free tier 100/mes, detecta featured snippets y PAA. $50/mes para más.
- **Google Search Console**: Gratis, pero ADVISORY (necesita credenciales).
- La medición real de snippets es un PROXY: si Google te da posición cero, Siri/Google Assistant usan ese dato.

### Estado post-FASE-A
- CHECKLIST_AEO ya tiene los pesos correctos (schema_faq 25, open_graph 15, etc.)
- `_extraer_elementos_aeo()` ya extrae elementos AEO específicos
- `_calculate_aeo_score()` usa la interfaz vieja de 4 componentes

---

## Tareas

### Tarea 1: Crear módulo AEO Snippet Tracker

**Objetivo**: Nuevo módulo que consulta SerpAPI para verificar featured snippets.

**Archivos a crear**:
- `modules/auditors/aeo_snippet_tracker.py`
- `tests/auditors/test_aeo_snippet_tracker.py`

**Interfaz**:
```python
@dataclass
class SnippetResult:
    query: str                    # Query factual ejecutada
    has_snippet: bool             # Si hay featured snippet
    snippet_source: Optional[str] # URL del sitio que captura el snippet
    is_our_hotel: bool            # Si el snippet es de nuestro hotel
    snippet_type: Optional[str]   # "paragraph" | "list" | "table"
    people_also_ask: List[str]    # Preguntas relacionadas
    
@dataclass  
class AEOSnippetReport:
    hotel_url: str
    queries_tested: int
    snippets_captured: int        # Cuántos snippets captura el hotel
    snippets_competitor: int      # Cuántos captura la competencia
    paa_presence: int             # Veces que aparece en People Also Ask
    snippet_score: int            # 0-100
    queries: List[SnippetResult]
    source: str                   # "serpapi" | "gsc" | "stub"

class AEOSnippetTracker:
    QUERIES_FACTUALES = [
        "hotel {nombre} horario",
        "hotel {nombre} telefono",
        "hotel {nombre} direccion",
        "hoteles boutique en {ciudad}",
        "mejor hotel cerca de {landmark}",
    ]
    
    def __init__(self, serpapi_key: Optional[str] = None):
        """
        Si serpapi_key es None, retorna datos stub/parciales.
        SerpAPI free tier: 100 queries/mes.
        """
        ...
    
    def check_snippets(self, hotel_name: str, hotel_url: str, 
                       location: str = "", landmark: str = "") -> AEOSnippetReport:
        """Ejecuta queries factuales y verifica snippets."""
        ...
```

**Criterios de aceptación**:
- [ ] Módulo creado con interfaz limpia
- [ ] Si no hay SerpAPI key, retorna stub con source="stub" (no crashea)
- [ ] Si hay key, ejecuta queries y parsea resultados
- [ ] Costo API declarado: $0 (free tier) a $50/mes
- [ ] Tests unitarios con datos mock pasan

### Tarea 2: Refactorizar _calculate_aeo_score()

**Objetivo**: Reescribir la función para usar CHECKLIST_AEO de FASE-A + datos de AEOSnippetTracker.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L1401-1455)

**Nueva lógica**:
```python
def _calculate_aeo_score(self, audit_result: V4AuditResult) -> str:
    """
    AEO Score: Para que te CITEN (posición cero / featured snippets).
    
    Componentes (basado en CHECKLIST_AEO de FASE-A):
    - schema_faq (25pts): FAQ Schema válido (fuente directa para snippets)
    - open_graph (15pts): OG tags presentes (metadatos para posición cero)
    - schema_hotel_aeo (15pts): Schema Hotel detallado (extracción factual)
    - contenido_factual (20pts): Horarios/precios/servicios accesibles en página
    - speakable_schema (10pts): Markup específico para voz
    - imagenes_alt_aeo (15pts): Alt text como fuente para image snippets
    
    NOTA: Snippet Score real (SerpAPI) se integra como override cuando hay datos.
    """
    elementos = self._extraer_elementos_aeo(audit_result)
    base_score = calcular_score_aeo(elementos)
    
    # Si hay datos reales de snippets (SerpAPI), ajustar score
    snippet_report = getattr(audit_result, 'aeo_snippets', None)
    if snippet_report and snippet_report.source != "stub":
        # Ponderar: 60% checklist + 40% resultado real
        real_score = snippet_report.snippet_score
        base_score = int(base_score * 0.6 + real_score * 0.4)
    
    return str(min(100, max(0, base_score)))
```

**Criterios de aceptación**:
- [ ] Función usa CHECKLIST_AEO de FASE-A (no pesos hardcodeados)
- [ ] Citabilidad YA NO está en AEO (se movió a IAO en FASE-A)
- [ ] Si hay SerpAPI data, se pondera 60/40
- [ ] Si no hay SerpAPI, usa solo checklist (backward compat)
- [ ] Retorna "0" si no hay datos

### Tarea 3: Integrar AEOSnippetTracker en el flujo v4audit

**Objetivo**: Añadir la verificación de snippets al flujo de auditoría.

**Archivos afectados**:
- `modules/auditors/v4_comprehensive.py` (añadir llamada a AEOSnippetTracker)

**Cambios**:
```python
# En v4_comprehensive.py, donde se llama a CitabilityScorer (L959):
# Añadir después:
aeo_tracker = AEOSnippetTracker(serpapi_key=os.getenv('SERPAPI_KEY'))
snippet_report = aeo_tracker.check_snippets(
    hotel_name=result.hotel_name,
    hotel_url=result.url,
    location=hotel_location,
)
# Almacenar en audit_result para uso en diagnóstico
```

**Criterios de aceptación**:
- [ ] AEOSnippetTracker se instancia con API key de env
- [ ] Si falla la API, no crashea el flujo (graceful degradation)
- [ ] Resultado se almacena accesible para _calculate_aeo_score()
- [ ] Costo por hotel: 5-10 queries SerpAPI (dentro del free tier)

### Tarea 4: Actualizar tests

**Objetivo**: Actualizar test_aeo_score.py para la nueva lógica.

**Archivos afectados**:
- `tests/commercial_documents/test_aeo_score.py`

**Tests nuevos necesarios**:
- `test_aeo_score_no_citability`: Citabilidad no debe estar en AEO
- `test_aeo_score_uses_checklist_aeo`: Usa pesos de CHECKLIST_AEO
- `test_aeo_score_with_serpapi`: Con SerpAPI data, pondera 60/40
- `test_aeo_score_without_serpapi`: Sin SerpAPI, usa solo checklist
- `test_snippet_tracker_stub`: Sin API key, retorna stub
- `test_snippet_tracker_mock`: Con datos mock, parsea correctamente

**Criterios de aceptación**:
- [ ] Tests viejos adaptados a nueva lógica
- [ ] Tests nuevos para SerpAPI integration
- [ ] Tests nuevos para AEOSnippetTracker
- [ ] Todos pasan sin regresiones

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| AEO sin citabilidad | `tests/commercial_documents/test_aeo_score.py` | citability NO aparece en score AEO |
| AEO con SerpAPI | `tests/commercial_documents/test_aeo_score.py` | Ponderación 60/40 correcta |
| Snippet tracker stub | `tests/auditors/test_aeo_snippet_tracker.py` | No crashea sin API key |
| Snippet tracker mock | `tests/auditors/test_aeo_snippet_tracker.py` | Parsea resultados correctamente |
| Suite completa | — | 385+ tests, 0 regresiones |

**Comandos de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_aeo_score.py tests/auditors/test_aeo_snippet_tracker.py -v
./venv/Scripts/python.exe -m pytest tests/ -x --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** → Marcar FASE-B como completada
2. **`06-checklist-implementacion.md`** → Marcar items de FASE-B
3. **`09-documentacion-post-proyecto.md`** → Sección A: módulos nuevos, Sección D: métricas
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "AEO Real Measurement: SerpAPI integration + refactor _calculate_aeo_score" \
    --archivos-nuevos "modules/auditors/aeo_snippet_tracker.py,tests/auditors/test_aeo_snippet_tracker.py" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/auditors/v4_comprehensive.py" \
    --tests "390" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `modules/auditors/aeo_snippet_tracker.py` creado con interfaz limpia
- [ ] `_calculate_aeo_score()` refactorizado (usa CHECKLIST_AEO + SerpAPI)
- [ ] Citabilidad eliminada de AEO score (pertenece a IAO)
- [ ] AEOSnippetTracker integrado en v4_comprehensive.py
- [ ] Graceful degradation sin API key (no crashea)
- [ ] Tests nuevos pasan
- [ ] Tests existentes pasan (0 regresiones)
- [ ] log_phase_completion.py ejecutado

---

## Restricciones

- NO añadir dependencias nuevas (usar `requests` o `httpx` que ya existen)
- SerpAPI key: leer de `SERPAPI_KEY` en `.env`. Si no existe, modo stub.
- Costo API explícito: $0/mes (free tier 100 queries) o $50/mes
- NO modificar paquetes comerciales ni templates (FASE-D)
- NO implementar LLM Mention Checker (FASE-C)
- NO intentar medición directa de voz (Siri/Alexa) — proxy solo
- Python: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

---

## Dependencias de datos externos

| Fuente | Requiere API Key | Costo | Fallback si no hay key |
|--------|-----------------|-------|----------------------|
| SerpAPI | `SERPAPI_KEY` en .env | Free: 100/mes | Retorna stub, score basado solo en checklist |
| Google Search Console | `GSC_SITE_URL` + creds | Gratis | Ya es ADVISORY, no cambia |
