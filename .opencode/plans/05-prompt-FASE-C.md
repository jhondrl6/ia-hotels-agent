# FASE-C: IAO Restoration + LLM Mention Checker

**ID**: FASE-C
**Objetivo**: Restaurar el score IAO (eliminado incorrectamente en v4.21.0), crear el módulo LLM Mention Checker que consulta OpenAI/Gemini/Perplexity para detectar menciones del hotel, y conectar ambos al pipeline de diagnóstico.
**Dependencias**: FASE-B completada (AEO correcto es prerequisito de IAO)
**Duración estimada**: 4-5 horas
**Skill**: `test-driven-development`, `iah-cli-phased-execution`

---

## Contexto

### Historial
- IAO existió como score separado hasta v4.21.0
- Eliminado: `_calculate_iao_score()`, `_calculate_score_ia()`, `_calculate_voice_readiness_score()`
- Razón de eliminación: "ambos median infraestructura de datos estructurados" → **FALSO**
- AEO mide posición cero en Google (buscador). IAO mide recomendación en LLMs (agentes). Son canales diferentes.

### Qué es IAO correctamente
IAO = "Para que te RECOMIENDEN" — ChatGPT/Perplexity/Gemini te menciona como recomendación.
AEO = dato factual corto ("¿horario?" → "8am-8pm"). IAO = síntesis compleja ("¿hotel tranquilo para trabajar cerca de la UTP?" → TE RECOMIENDA).

### Arquitectura de progresión
```
SEO (base) → AEO (construye sobre SEO) → IAO (construye sobre AEO)
  │              │                           │
  └──── GEO (lateral, complementario) ───────┘
```

### Regla crítica: OpenAI SIEMPRE via OpenRouter
- NUNCA `from openai import OpenAI` directo
- Siempre via OpenRouter: endpoint `https://openrouter.ai/api/v1`
- El módulo existente `ia_tester.py` usa OpenAI directo → NO replicar ese patrón
- Gemini: via Google API directo (no OpenRouter)
- Perplexity: via su API propio

### Módulos reutilizables (ya existen)
- `citability_scorer.py` → mide calidad para IA → pertenece a IAO
- `ia_readiness_calculator.py` → 6 componentes → base del score IAO
- `ai_crawler_auditor.py` → verifica robots.txt para IA crawlers → componente IAO
- `llmstxt_generator.py` → genera llms.txt → activo IAO directo
- `profound_client.py` → interfaz correcta, implementación STUB → reemplazar con LLM Mention Checker propio

---

## Tareas

### Tarea 1: Crear LLM Mention Checker

**Objetivo**: Módulo que consulta LLMs y detecta si el hotel es mencionado en recomendaciones.

**Archivos a crear**:
- `modules/auditors/llm_mention_checker.py`
- `tests/auditors/test_llm_mention_checker.py`

**Interfaz**:
```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class LLMQueryResult:
    provider: str           # "openrouter" | "gemini" | "perplexity"
    query: str              # Query ejecutada
    response_text: str      # Respuesta completa del LLM
    hotel_mentioned: bool   # Si el hotel fue mencionado
    mention_context: str    # Contexto de la mención
    ranking_position: Optional[int]  # Posición en lista (1=primero)
    competitors_mentioned: List[str]  # Competidores mencionados

@dataclass
class LLMReport:
    hotel_name: str
    hotel_url: str
    location: str
    queries_tested: int
    total_mentions: int           # Veces mencionado en todas las queries
    avg_ranking: Optional[float]  # Ranking promedio cuando es mencionado
    mention_rate: float           # mentions / queries_tested (0.0-1.0)
    providers_used: List[str]
    query_results: List[LLMQueryResult]
    mention_score: int            # 0-100
    source: str                   # "llm_check" | "stub"
    
    @property
    def share_of_voice(self) -> float:
        """Porcentaje de menciones vs competencia."""
        ...

class LLMMentionChecker:
    """
    Consulta LLMs para detectar menciones del hotel en recomendaciones.
    
    REGLA: OpenAI SIEMPRE via OpenRouter. NUNCA import openai SDK directo.
    """
    
    PROBING_QUERIES = [
        "Recomiéndame un hotel boutique en {location}",
        "¿Cuál es el mejor hotel para parejas en {location}?",
        "Hoteles con encanto cerca de {landmark}",
        "¿Dónde hospedarse en {location} que tenga buena vista?",
        "Hotel tranquilo para trabajar en {location}",
    ]
    
    def __init__(self, openrouter_key: Optional[str] = None,
                 gemini_key: Optional[str] = None,
                 perplexity_key: Optional[str] = None):
        """
        Al menos una key requerida. Si todas son None, retorna stub.
        
        Costo estimado por hotel:
        - OpenRouter: ~$0.01-0.03/query (5 queries = $0.05-0.15)
        - Gemini: GRATIS (free tier generoso)
        - Perplexity: ~$0.02-0.05/query
        """
        ...
    
    def check_mentions(self, hotel_name: str, hotel_url: str,
                       location: str, landmark: str = "") -> LLMReport:
        """Ejecuta queries de recomendación y analiza menciones."""
        ...
    
    def _query_openrouter(self, query: str) -> Optional[str]:
        """Llama OpenRouter API. NUNCA usar openai SDK directo."""
        import requests
        headers = {
            "Authorization": f"Bearer {self._openrouter_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "google/gemini-2.0-flash-001",  # Modelo barato
            "messages": [{"role": "user", "content": query}],
        }
        # POST to https://openrouter.ai/api/v1/chat/completions
        ...
    
    def _query_gemini(self, query: str) -> Optional[str]:
        """Llama Gemini API directo (no via OpenRouter)."""
        import requests
        # GET https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent
        ...
    
    def _query_perplexity(self, query: str) -> Optional[str]:
        """Llama Perplexity API. Mejor para IAO porque cita fuentes."""
        ...
    
    def _parse_mentions(self, response: str, hotel_name: str) -> dict:
        """Detecta si el hotel fue mencionado y en qué contexto."""
        ...
```

**Criterios de aceptación**:
- [ ] Módulo creado con interfaz limpia
- [ ] OpenRouter como provider principal (NUNCA openai SDK)
- [ ] Gemini como segundo provider (gratis)
- [ ] Perplexity como tercer provider (mejor para IAO)
- [ ] Sin API keys: modo stub, no crashea
- [ ] Costo por hotel: $0.05-0.15 (5 queries)
- [ ] Tests con datos mock pasan

### Tarea 2: Crear _calculate_iao_score()

**Objetivo**: Restaurar la función eliminada en v4.21.0, usando CHECKLIST_IAO de FASE-A + datos de LLMMentionChecker.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`

**Implementación**:
```python
def _calculate_iao_score(self, audit_result: V4AuditResult) -> str:
    """
    IAO Score: Para que te RECOMIENDEN (menciones en LLMs).
    
    Componentes (basado en CHECKLIST_IAO de FASE-A):
    - citability_score (20pts): Contenido citable por IAs
    - contenido_extenso (15pts): Contenido profundo y estructurado
    - llms_txt_exists (15pts): Archivo llms.txt estándar generado
    - crawler_access (15pts): robots.txt permite IA crawlers
    - brand_signals (10pts): SameAs, enlaces sociales, identidad digital
    - ga4_indirect (10pts): Tráfico indirecto desde plataformas IA
    - schema_advanced (15pts): Entity schema + SameAs
    
    NOTA: LLM Mention Score real se integra como override cuando hay datos.
    """
    elementos = self._extraer_elementos_iao(audit_result)
    base_score = calcular_score_iao(elementos)
    
    # Si hay datos reales de LLM mentions, ajustar score
    llm_report = getattr(audit_result, 'llm_report', None)
    if llm_report and llm_report.source != "stub":
        # Ponderar: 50% checklist + 50% resultado real
        real_score = llm_report.mention_score
        base_score = int(base_score * 0.5 + real_score * 0.5)
    
    return str(min(100, max(0, base_score)))
```

**Criterios de aceptación**:
- [ ] Función restaurada con lógica correcta
- [ ] Usa CHECKLIST_IAO de FASE-A
- [ ] Citabilidad está en IAO (no en AEO)
- [ ] Integración con LLMMentionChecker (50/50 si hay datos reales)
- [ ] Retorna "0" si no hay datos

### Tarea 3: Integrar LLMMentionChecker en v4audit

**Objetivo**: Añadir verificación de menciones al flujo de auditoría.

**Archivos afectados**:
- `modules/auditors/v4_comprehensive.py`

**Cambios**: Similar a FASE-B con AEOSnippetTracker:
- Instanciar LLMMentionChecker con keys de env
- Ejecutar check_mentions() 
- Almacenar resultado accesible para _calculate_iao_score()
- Graceful degradation si no hay keys

**Criterios de aceptación**:
- [ ] LLMMentionChecker integrado en flujo v4audit
- [ ] No crashea sin API keys
- [ ] Resultado accesible para diagnóstico

### Tarea 4: Actualizar DiagnosticSummary con IAO fields

**Objetivo**: Añadir campos IAO específicos al dataclass (complementando FASE-A).

**Archivos afectados**:
- `modules/commercial_documents/data_structures.py`

**Campos adicionales**:
```python
# En DiagnosticSummary:
score_iao: Optional[int] = None       # Ya creado en FASE-A, verificar
iao_status: Optional[str] = None      # Nuevo
iao_regional_avg: Optional[int] = None  # Nuevo
llm_report_summary: Optional[Dict] = None  # Resumen del LLM report
```

**Criterios de aceptación**:
- [ ] Campos IAO añadidos a DiagnosticSummary
- [ ] score_iao se llena desde _calculate_iao_score()

### Tarea 5: Actualizar _prepare_template_data() con IAO

**Objetivo**: Restaurar las variables de template `iao_score`, `iao_status` que fueron eliminadas en FASE-CAUSAL-01.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (sección template data)

**Cambios**:
```python
# IAO score (restaurado)
'iao_score': self._calculate_iao_score(audit_result),
'iao_status': self._get_score_status(self._calculate_iao_score(audit_result), iao_regional['value']),
'iao_regional_avg': str(iao_regional['value']),
```

**Criterios de aceptación**:
- [ ] `iao_score`, `iao_status`, `iao_regional_avg` inyectados en template
- [ ] Variables eliminadas en FASE-CAUSAL-01 restauradas

### Tarea 6: Tests

**Archivos a crear/modificar**:
- `tests/commercial_documents/test_iao_score.py` (NUEVO)
- `tests/auditors/test_llm_mention_checker.py` (NUEVO)
- `tests/data_validation/test_aeo_kpis.py` (modificar)

**Tests necesarios**:
- `test_iao_score_basic`: Score sin datos = 0
- `test_iao_score_with_citability`: Citabilidad alta incrementa score
- `test_iao_score_with_llm_report`: Con LLM data, ponderación 50/50
- `test_iao_score_not_in_aeo`: Confirmar citabilidad ya NO está en AEO
- `test_llm_checker_stub`: Sin keys, retorna stub
- `test_llm_checker_mock`: Con datos mock, parsea menciones correctamente
- `test_llm_checker_openrouter_only`: Solo OpenRouter key
- `test_llm_checker_gemini_only`: Solo Gemini key

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| IAO score básico | `tests/commercial_documents/test_iao_score.py` | Retorna 0-100 |
| IAO con LLM | `tests/commercial_documents/test_iao_score.py` | Ponderación 50/50 |
| LLM checker stub | `tests/auditors/test_llm_mention_checker.py` | No crashea sin keys |
| LLM checker mock | `tests/auditors/test_llm_mention_checker.py` | Detecta menciones |
| Suite completa | — | 390+ tests, 0 regresiones |

**Comandos de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_iao_score.py tests/auditors/test_llm_mention_checker.py -v
./venv/Scripts/python.exe -m pytest tests/ -x --tb=short
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** → Marcar FASE-C como completada
2. **`06-checklist-implementacion.md`** → Marcar items de FASE-C
3. **`09-documentacion-post-proyecto.md`** → Sección A: módulos nuevos
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C \
    --desc "IAO Restoration: LLM Mention Checker + _calculate_iao_score restaurado" \
    --archivos-nuevos "modules/auditors/llm_mention_checker.py,tests/auditors/test_llm_mention_checker.py,tests/commercial_documents/test_iao_score.py" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/data_structures.py,modules/auditors/v4_comprehensive.py" \
    --tests "395" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `modules/auditors/llm_mention_checker.py` creado
- [ ] `_calculate_iao_score()` restaurado y funcionando
- [ ] LLMMentionChecker integrado en v4_comprehensive.py
- [ ] Variables template `iao_score`/`iao_status` restauradas
- [ ] DiagnosticSummary tiene campos IAO completos
- [ ] Citabilidad está en IAO (no en AEO)
- [ ] OpenRouter como provider (NUNCA openai SDK directo)
- [ ] Tests nuevos pasan
- [ ] Suite completa pasa (0 regresiones)
- [ ] log_phase_completion.py ejecutado

---

## Restricciones

- **REGLA CRÍTICA**: OpenAI SIEMPRE via OpenRouter. NUNCA `from openai import OpenAI`.
- NO implementar medición directa de voz (Siri/Alexa) → proxy measurement
- NO cambiar paquetes comerciales ni templates de propuesta (FASE-D)
- NO crear nuevos assets (eso es FASE-D)
- API keys desde `.env`: `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `PERPLEXITY_API_KEY`
- Costo total por hotel: $0.05-0.20 USD (5 queries x 3 providers)
- Python: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

---

## Dependencias de datos externos

| Fuente | Requiere API Key | Costo | Fallback |
|--------|-----------------|-------|----------|
| OpenRouter | `OPENROUTER_API_KEY` | ~$0.01-0.03/query | Stub |
| Gemini | `GEMINI_API_KEY` | GRATIS (free tier) | Stub |
| Perplexity | `PERPLEXITY_API_KEY` | ~$0.02-0.05/query | Stub |
