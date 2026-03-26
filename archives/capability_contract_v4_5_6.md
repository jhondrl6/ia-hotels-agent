# Capability Contract v4.5.6

**Proyecto**: IA Hoteles CLI - NEVER_BLOCK v4.5.6
**Fecha**: 2026-03-23
**Estado**: ✅ PROYECTO CERRADO

---

## Resumen Ejecutivo

Este documento define el contrato de capacidades (Capability Contract) del sistema IA Hoteles CLI v4.5.6. Cada capability del sistema está documentada con su estado de conexión, módulo responsible, y output producido.

---

## Matriz de Capabilities

| Capability | Estado | Módulo | Invocación | Output |
|------------|--------|--------|------------|--------|
| `benchmark_resolver` | ✅ Connected | `modules/providers/benchmark_resolver.py` | `preflight_checks.py`, `conditional_generator.py` | `metadata.disclaimers`, `benchmark_data` |
| `disclaimer_generator` | ✅ Connected | `modules/providers/disclaimer_generator.py` | `conditional_generator.py` | `metadata.disclaimers` |
| `autonomous_researcher` | ✅ Connected | `modules/providers/autonomous_researcher.py` | On-demand (no en flujo principal por defecto) | `ResearchResult` (en memoria, no persiste) |
| `asset_content_validator` | ✅ Connected | `modules/asset_generation/asset_content_validator.py` | `conditional_generator.py` | `ValidationResult`, `asset.failed` |
| `preflight_checks` | ✅ Connected | `modules/asset_generation/preflight_checks.py` | `conditional_generator.py` | `preflight_status` |
| `coherence_validator` | ✅ Connected | `modules/commercial_documents/coherence_validator.py` | `v4_asset_orchestrator.py` | `CoherenceReport` |
| `publication_gates` | ✅ Connected | `modules/quality_gates/publication_gates.py` | `onboarding_controller.py` | `PublicationGateResult[]` |
| `cross_validator` | ✅ Connected | `modules/data_validation/cross_validator.py` | `onboarding_controller.py`, `two_phase_flow.py` | `conflict_report`, `confidence_scores` |
| `scenario_calculator` | ✅ Connected | `modules/financial_engine/scenario_calculator.py` | `two_phase_flow.py` | `FinancialScenario` dict |
| `data_assessment` | ✅ Connected | `modules/asset_generation/data_assessment.py` | `v4_asset_orchestrator.py` | `DataAssessmentResult` |

**Total**: 10 capabilities
**Connected**: 10
**Disconnected**: 0
**Huérfanas**: 0 ✅

---

## capability: `autonomous_researcher`

### Descripción

El `AutonomousResearcher` es un módulo de **investigación silenciosa (NEVER_BLOCK)** que busca información de hoteles en múltiples fuentes públicas.

### Comportamiento

```
COMPORTAMIENTO: Silent Research (NEVER_BLOCK)
OUTPUT: ResearchResult (en memoria)
PERSISTENCIA: No persiste a archivo por defecto
NOTA: El llamador decide si persistir/registrar resultados
```

### Fuentes consultadas

1. **Google Business Profile (GBP)**: Datos estructurados del hotel
2. **Booking.com**: Información de disponibilidad y precios
3. **TripAdvisor**: Reviews y ratings
4. **Instagram/Facebook**: Presencia en redes sociales

### Interfaz

```python
class AutonomousResearcher:
    def research(self, hotel_name: str, url: str, 
                 sources: Optional[List[str]] = None) -> ResearchResult:
        """
        Investiga un hotel en múltiples fuentes públicas.
        
        Returns:
            ResearchResult con datos encontrados, confidence y fuentes
            
        NOTE: Este método ejecuta investigación silenciosa (NEVER_BLOCK).
        Los resultados se devuelven como ResearchResult pero NO se escriben
        a archivos de output por defecto. El llamador es responsable de
        persistir/registrar los resultados si es necesario.
        """
```

### ResearchResult

```python
@dataclass
class ResearchResult:
    found: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
```

### Cálculo de Confidence

```python
# Fuentes consultadas vs confidence:
- 0 fuentes: 0.0
- 1 fuente: 0.3
- 2 fuentes: 0.5
- 3 fuentes: 0.7
- 4+ fuentes: 0.8

# Boost por campos coincidentes:
field_boost = min(matching_fields * 0.05, 0.15)

# Penalty por conflictos:
conflict_penalty = len(conflicts) * 0.15

confidence = base_confidence + field_boost - conflict_penalty
```

### Decisión de Diseño

**P: ¿Por qué autonomous_researcher no persiste a archivo?**

R: El diseño NEVER_BLOCK prioriza la ejecución silenciosa. El módulo:
- Devuelve resultados en memoria para uso inmediato
- Usa logging para debugging (no persistence)
- Permite al llamador decidir qué datos persistir

Esto evita archivos intermedios innecesarios y mantiene el flujo limpio.

---

## capability: `coherence_validator`

### Descripción

El `CoherenceValidator` valida que el diagnóstico, propuesta y assets están alineados y son coherentes entre sí.

### Checks Realizados

| Check | Peso | Descripción |
|-------|------|-------------|
| `problems_have_solutions` | 1.5 | Cada problema tiene al menos una solución |
| `assets_are_justified` | 1.0 | Cada asset está justificado por un problema |
| `financial_data_validated` | 1.5 | Datos financieros vienen de fuentes validadas |
| `whatsapp_verified` | 0.5 | WhatsApp verificado antes de usar |
| `price_matches_pain` | 1.0 | Precio proporcional al dolor financiero |
| `promised_assets_exist` | 2.0 | Assets prometidos existen en el generador |

### Cálculo del Coherence Score

```python
weighted_score = sum(c.score * CHECK_WEIGHTS[c.name] for c in checks)
total_weight = sum(CHECK_WEIGHTS[c.name] for c in checks)
overall_score = weighted_score / total_weight
```

### Estados del Coherence Gate

| Score | Status | Publicación |
|-------|--------|-------------|
| >= 0.8 | CERTIFIED | READY_FOR_CLIENT |
| 0.5-0.8 | REVIEW | REQUIRES_REVIEW |
| < 0.5 | DRAFT_INTERNAL | DRAFT_INTERNAL |

---

## capability: `publication_gates`

### Gates Bloqueantes

1. **hard_contradictions**: Bloquea si hay conflictos HARD sin resolver (count > 0)
2. **evidence_coverage**: Bloquea si coverage < 95%
3. **financial_validity**: Bloquea si hay default values en datos financieros
4. **coherence**: Bloquea si coherence < 0.8
5. **critical_recall**: Bloquea si recall < 90%
6. **ethics**: Bloquea si hay problemas éticos

### Flujo

```
Assessment → PublicationGatesOrchestrator.run_all() → PublicationGateResult[]
```

---

## capability: `data_assessment`

### Descripción

Evalúa la disponibilidad y calidad de datos del hotel para determinar el path de generación apropiado.

### Clasificación

| Classification | Score | Path | Assets |
|---------------|-------|------|--------|
| LOW | < 30% | Fast | 3-4 |
| MED | 30-70% | Standard | 6-7 |
| HIGH | > 70% | Full | 9+ |

### Métricas Evaluadas

- **Core hotel data** (peso 25%): name, phone, address, email, website, description
- **GBP data** (peso 35%): reviews, photos, rating, reviews_count
- **SEO data** (peso 20%): schema_markup, meta_description, title_tag, headings
- **Web scraping** (peso 20%): Success/Failure

---

## Verificación de Huérfanas

Para verificar que no hay capabilities huérfanas:

```bash
# Verificar que todas las capabilities conectadas
grep -r "def " modules/providers/ | grep -E "(benchmark_resolver|disclaimer_generator|autonomous_researcher)"

# Verificar invocaciones
grep -r "from.*providers" modules/ | head -20
```

---

## Changelog

| Fecha | Cambio |
|-------|--------|
| 2026-03-23 | v4.5.6 - Documento inicial creado (FASE 5) |

---

**Estado**: ✅ CERRADO - 0 capabilities huérfanas
