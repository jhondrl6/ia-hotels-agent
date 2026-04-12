# FASE-E: Voice Readiness Proxy Score

**ID**: FASE-E
**Objetivo**: Crear un score de Voice Readiness basado en PROXY (inputs que alimentan asistentes de voz) en lugar de medición directa (Siri/Alexa). Medir los FACTORES que determinan si voz te menciona, no lo que voz responde.
**Dependencias**: FASE-A completada (estructura 4 pilares). Independiente de B/C/D.
**Duración estimada**: 2-3 horas
**Skill**: `test-driven-development`, `iah-cli-phased-execution`

---

## Contexto

### Por qué PROXY y no medición directa
En sesiones anteriores se intentó medir directamente qué responde Siri/Alexa. Resultado:
- NO existe API para consultar qué responde Siri programáticamente
- NO hay "Siri Search Console" ni "Alexa Rank Tracker"
- Simular consultas de voz con TTS+STT es hacky e inescalable
- Cada asistente tiene fuentes distintas (Siri=Apple Maps+Google, Alexa=Bing+Yelp)

### La alternativa viable: medir los INPUTS
En lugar de medir lo que Siri RESPONDE, medimos los datos que Siri/Google Assistant consumen:
1. Google featured snippet capture (si Google te da posición cero, Google Assistant usa ese dato)
2. GBP completeness (Google Assistant usa GBP)
3. Apple Business Connect listing (Siri usa Apple Maps)
4. Schema.org FAQ + LocalBusiness (voz extrae datos estructurados)
5. Speakable markup (schema específico para voz)

### Ya tenemos la mayoría de estos datos
- GBP completeness: `audit_result.gbp.geo_score` (ya funciona)
- Schema FAQ: `audit_result.schema.faq_schema_valid` (ya funciona)
- Schema LocalBusiness: `audit_result.schema.hotel_schema_valid` (ya funciona)
- Featured snippets: `AEOSnippetTracker` de FASE-B (si está completada)

---

## Tareas

### Tarea 1: Crear módulo Voice Readiness Proxy

**Objetivo**: Módulo que calcula readiness para voz basado en inputs medibles.

**Archivos a crear**:
- `modules/auditors/voice_readiness_proxy.py`
- `tests/auditors/test_voice_readiness_proxy.py`

**Interfaz**:
```python
from dataclasses import dataclass
from typing import Dict, Optional, List

@dataclass
class VoiceReadinessResult:
    score: int                           # 0-100
    level: str                           # "critical" | "basic" | "good" | "excellent"
    components: Dict[str, Dict]          # Desglose por componente
    recommendations: List[str]           # Acciones para mejorar
    data_sources: List[str]              # Qué fuentes alimentaron el score
    
    # Componentes individuales
    gbp_completeness: int                # 0-100 (de GBPData)
    schema_for_voice: int                # 0-100 (FAQ + LocalBusiness + Speakable)
    featured_snippets: int               # 0-100 (de AEOSnippetTracker si disponible)
    factual_coverage: int                # 0-100 (horario, dirección, teléfono en schema)
    
class VoiceReadinessProxy:
    """
    Score de readiness para asistentes de voz basado en PROXY.
    
    NO consulta Siri/Alexa directamente.
    Mide los INPUTS que alimentan los asistentes de voz.
    """
    
    # Pesos de componentes
    WEIGHTS = {
        "gbp_completeness": 30,   # Google Assistant usa GBP
        "schema_for_voice": 25,   # Voz extrae de schema estructurado
        "featured_snippets": 25,  # Si Google te da pos 0, Assistant lo usa
        "factual_coverage": 20,   # Datos factuales accesibles (horario, precio)
    }
    
    def calculate(self, audit_result, snippet_report=None) -> VoiceReadinessResult:
        """
        Calcula Voice Readiness desde datos de auditoría.
        
        Args:
            audit_result: V4AuditResult con datos GBP, schema, etc.
            snippet_report: AEOSnippetReport (opcional, de FASE-B)
        
        Returns:
            VoiceReadinessResult con score 0-100 y desglose.
        """
        ...
    
    def _assess_gbp_completeness(self, gbp_data) -> int:
        """
        30pts del score. ¿GBP tiene todo lo que Google Assistant necesita?
        - Nombre: sí/no (10pts)
        - Dirección: sí/no (5pts)
        - Teléfono: sí/no (5pts)
        - Horarios: sí/no (5pts)
        - Website: sí/no (5pts)
        """
        ...
    
    def _assess_schema_for_voice(self, schema_data) -> int:
        """
        25pts del score. ¿Schema está optimizado para extracción por voz?
        - LocalBusiness/Hotel schema: sí/no (10pts)
        - FAQ schema: sí/no (8pts)
        - Speakable schema: sí/no (7pts) → nuevo check
        """
        ...
    
    def _assess_featured_snippets(self, snippet_report) -> int:
        """
        25pts del score. ¿Google te da posición cero en queries factuales?
        - snippet_report de AEOSnippetTracker (FASE-B)
        - Si no hay datos (FASE-B no completada): usar proxy de schema
        """
        if snippet_report and snippet_report.source != "stub":
            return snippet_report.snippet_score
        # Fallback: estimar desde schema coverage
        ...
    
    def _assess_factual_coverage(self, audit_result) -> int:
        """
        20pts del score. ¿Datos factuales accesibles en la página?
        - Horarios en texto visible: sí/no (5pts)
        - Teléfono visible: sí/no (5pts)
        - Dirección visible: sí/no (5pts)
        - Precios/rangos visibles: sí/no (5pts)
        """
        ...
```

**Criterios de aceptación**:
- [ ] Módulo creado con interfaz limpia
- [ ] 4 componentes con pesos sumando 100
- [ ] Si FASE-B no está completada, usa fallback desde schema
- [ ] No requiere API keys externas (usa datos del audit)
- [ ] Tests con datos mock pasan

### Tarea 2: Integrar en el pipeline de diagnóstico

**Objetivo**: Añadir Voice Readiness como variable disponible en templates.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/data_structures.py`

**Cambios**:
```python
# En _prepare_template_data():
from modules.auditors.voice_readiness_proxy import VoiceReadinessProxy

voice_proxy = VoiceReadinessProxy()
snippet_report = getattr(audit_result, 'aeo_snippets', None)
voice_result = voice_proxy.calculate(audit_result, snippet_report)

# Añadir al dict de template:
'voice_readiness_score': str(voice_result.score),
'voice_readiness_level': voice_result.level,
'voice_readiness_recommendations': voice_result.recommendations,
```

```python
# En DiagnosticSummary:
voice_readiness_score: Optional[int] = None
voice_readiness_level: Optional[str] = None
```

**Criterios de aceptación**:
- [ ] Voice Readiness calculado y disponible en templates
- [ ] DiagnosticSummary tiene campos voice_readiness_*
- [ ] No crashea si FASE-B no se ha ejecutado

### Tarea 3: Tests

**Tests necesarios**:
- `test_voice_readiness_full_data`: Con todos los datos disponibles
- `test_voice_readiness_no_gbp`: Sin GBP data → score bajo
- `test_voice_readiness_no_schema`: Sin schema → score bajo
- `test_voice_readiness_no_snippets`: Sin snippet report → fallback funciona
- `test_voice_readiness_weights`: Componentes ponderados correctamente
- `test_voice_readiness_levels`: Rangos correctos (critical/basic/good/excellent)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Full data | `tests/auditors/test_voice_readiness_proxy.py` | Score 70-100 con datos completos |
| No GBP | `tests/auditors/test_voice_readiness_proxy.py` | Score bajo (<40) sin GBP |
| No schema | `tests/auditors/test_voice_readiness_proxy.py` | Score bajo sin schema |
| No snippets | `tests/auditors/test_voice_readiness_proxy.py` | Fallback funciona |
| Integration | `tests/commercial_documents/test_aeo_score.py` | voice_readiness_score en template |
| Suite completa | — | 395+ tests, 0 regresiones |

**Comandos de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/auditors/test_voice_readiness_proxy.py -v
./venv/Scripts/python.exe -m pytest tests/ -x --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** → Marcar FASE-E como completada
2. **`06-checklist-implementacion.md`** → Marcar items de FASE-E
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E \
    --desc "Voice Readiness Proxy: score basado en inputs (no medición directa Siri/Alexa)" \
    --archivos-nuevos "modules/auditors/voice_readiness_proxy.py,tests/auditors/test_voice_readiness_proxy.py" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/data_structures.py" \
    --tests "400" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `modules/auditors/voice_readiness_proxy.py` creado
- [ ] 4 componentes proxy con pesos correctos
- [ ] Integrado en pipeline de diagnóstico
- [ ] Fallback funciona sin AEOSnippetTracker (FASE-B)
- [ ] DiagnosticSummary tiene campos voice_readiness_*
- [ ] Tests nuevos pasan
- [ ] Suite completa pasa (0 regresiones)
- [ ] log_phase_completion.py ejecutado

---

## Restricciones

- **NO** consultar APIs de Siri, Alexa, Google Assistant directamente
- **NO** usar TTS/STT para simular queries de voz
- **NO** crear webhooks ni subscripciones a plataformas de voz
- Voice Readiness es un SCORE DERIVADO, no un 5to pilar. Es un sub-score de AEO.
- No requiere API keys (usa datos del audit existente)
- Si FASE-B no se completó, usar fallback (estimación desde schema)
- Python: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`
