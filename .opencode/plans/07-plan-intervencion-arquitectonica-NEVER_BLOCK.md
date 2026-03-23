# Plan: Intervención Arquitectónica NEVER_BLOCK

**Fecha**: 2026-03-22  
**Estado**: Planificación  
**Prioridad**: CRÍTICA - Bloqueante para viabilidad del negocio

---

## Diagnóstico del Problema

### Problema Observado
El sistema genera assets con **placeholders** ("Ciudad", "+57XXX", "$$+") cuando no tiene datos reales del hotel. Esto hace que los outputs **no sean implementables** → no agregan valor → el negocio es inviable.

### Caso Hotel Vísperas
- `optimization_guide`: BLOCKED por placeholders
- `hotel_schema`: BLOCKED por campos vacíos
- 5 assets ESTIMATED con confidence 0.5 (datos públicos insuficientes)

### Causa Raíz
```
Falta de datos reales → Sistema genera fallback → Fallback usa placeholders genéricos → Output no implementable
```

El sistema **sí tiene** mecanismo de fallback (line 113-127 en preflight_checks.py), pero el fallback **rellena con datos genéricos** en lugar de:
1. Usar benchmark regional
2. Ser transparente sobre limitaciones
3. Entregar valor parcial pero útil

---

## Principios de Diseño

### Principio 1: NEVER_BLOCK
> El sistema NUNCA se bloquea. Siempre entrega algo, aunque sea subóptimo.

### Principio 2: BENCHMARK_FALLBACK
> Cuando no hay datos reales, usar benchmark regional (hoteles similares en Pereira/Santa Rosa de Cabal) + disclaimer explícito.

### Principio 3: HONEST_CONFIDENCE
> Todo output incluye confidence score real y fuentes utilizadas.

### Principio 4: DELIVERY_READY
> Todo output que se entregue debe ser implementable. No placeholders, no campos vacíos.

---

## Arquitectura Propuesta

### Flujo Actual (PROBLEMA)
```
Hotel → Scraping → ¿Datos completos?
  → SÍ → Generar asset
  → NO → Fallback con placeholders → BLOCKED
```

### Flujo Propuesto (SOLUCIÓN)
```
Hotel → Scraping → ¿Datos suficientes?
  → SÍ (confidence ≥ 0.7) → Generar con datos reales → PASSED ✅
  → PARCIAL (0.5 ≤ confidence < 0.7) → Benchmark regional + disclaimer → ESTIMATED ⚠️
  → INSUFICIENTE (confidence < 0.5) → Investigación autónoma + benchmark → ESTIMATED ⚠️
```

**Investigación Autónoma** (nueva capacidad):
- Buscar en Google Business Profile
- Buscar en Booking.com, TripAdvisor
- Buscar en Instagram/Facebook del hotel
- Cross-reference con benchmark Pereira/Santa Rosa
- Si después de investigación confidence sigue < 0.5: entregar con disclaimer "Para accuracy > 0.8, necesita onboarding"

---

## Capacidad Contract

| Capability | Estado Actual | Estado Propuesto | Punto de Intervención |
|------------|---------------|------------------|----------------------|
| `metadata_validator` | Detecta placeholders post-generación | Se mueve a PRE-generación (gate) | `preflight_checks.py` |
| `benchmark_resolver` | NO EXISTE | NUEVA - Resuelve gaps con benchmark regional | `modules/providers/benchmark_resolver.py` |
| `autonomous_researcher` | NO EXISTE | NUEVA - Investiga hotel en fuentes públicas | `modules/providers/autonomous_researcher.py` |
| `confidence_annotator` | Parcial | MEJORADO - Anota todas las fuentes usadas | `asset_metadata.py` |
| `disclaimer_generator` | NO EXISTE | NUEVA - Genera disclaimers honestos | `modules/providers/disclaimer_generator.py` |

---

## Fases de Implementación

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FASE 0: Diagnóstico y Plan                           │
│  (Esta sesión - NO se implementa, solo se planifica)                   │
├─────────────────────────────────────────────────────────────────────────┤
│  - Validar matriz de capacidades                                        │
│  - Documentar archivos a modificar                                      │
│  - Crear tests TDD para cada fase                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 1: Benchmark Resolver (Foundation)                               │
│  - Crear `modules/providers/benchmark_resolver.py`                     │
│  - Usar datos de `data/benchmarks/plan_maestro_data.json`               │
│  - Integrar con preflight_checks.py                                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Entregable: Sistema puede resolver gaps con benchmark Pereira/Santa Rosa│
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 2: Disclaimer Generator                                           │
│  - Crear `modules/providers/disclaimer_generator.py`                    │
│  - Genera disclaimers honestos por nivel de confidence                  │
│  - Anota fuentes utilizadas en cada claim                               │
├─────────────────────────────────────────────────────────────────────────┤
│  Entregable: Assets incluyen disclaimer transparente                    │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 3: Autonomous Researcher                                         │
│  - Crear `modules/providers/autonomous_researcher.py`                   │
│  - Busca hotel en GBP, Booking, TripAdvisor, Instagram                  │
│  - Cross-reference y full confidence annotation                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Entregable: Sistema investiga automáticamente antes de generar         │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 4: Integration & Quality Gates                                    │
│  - Modificar `preflight_checks.py` - nuevo flujo NEVER_BLOCK           │
│  - Modificar `conditional_generator.py` - usar benchmark cuando falta   │
│  - Modificar `asset_content_validator.py` - NO permitir placeholders    │
│  - Modificar generadores específicos (hotel_schema, optimization_guide) │
├─────────────────────────────────────────────────────────────────────────┤
│  Entregable: Flujo completo NEVER_BLOCK con outputs implementables      │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│  FASE 5: Validación E2E                                                │
│  - Tests de regresión con Hotel Vísperas                                │
│  - Verificar que outputs NO tienen placeholders                        │
│  - Verificar coherence score se mantiene ≥ 0.8                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Entregable: 100% tests passing, outputs implementables                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Archivos a Modificar

### Fase 1: Benchmark Resolver
| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `modules/providers/benchmark_resolver.py` | NUEVO | CRÍTICA |
| `modules/providers/__init__.py` | Exportar nuevo módulo | ALTA |
| `data/benchmarks/plan_maestro_data.json` | Agregar datos Pereira/Santa Rosa | ALTA |

### Fase 2: Disclaimer Generator
| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `modules/providers/disclaimer_generator.py` | NUEVO | CRÍTICA |
| `modules/asset_generation/asset_metadata.py` | Agregar campo disclaimers | ALTA |

### Fase 3: Autonomous Researcher
| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `modules/providers/autonomous_researcher.py` | NUEVO | CRÍTICA |
| `modules/scrapers/` | Integrar búsqueda multi-fuente | ALTA |

### Fase 4: Integration
| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `modules/asset_generation/preflight_checks.py` | Nuevo flujo NEVER_BLOCK | CRÍTICA |
| `modules/asset_generation/conditional_generator.py` | Usar benchmark en fallback | CRÍTICA |
| `modules/asset_generation/asset_content_validator.py` | Bloquear placeholders ANTES de generar | CRÍTICA |
| `modules/generators/seo_report_builder.py` | No placeholders, usar benchmark | ALTA |
| `modules/delivery/generators/` | Todos los generadores con benchmark | ALTA |

### Fase 5: Validación
| Archivo | Cambio | Prioridad |
|---------|--------|-----------|
| `tests/test_benchmark_resolver.py` | NUEVO | CRÍTICA |
| `tests/test_disclaimer_generator.py` | NUEVO | CRÍTICA |
| `tests/test_autonomous_researcher.py` | NUEVO | CRÍTICA |
| `tests/regression/test_hotel_visperas.py` | Verificar outputs sin placeholders | CRÍTICA |

---

## Tests TDD (uno por fase)

### Fase 1 - Test Benchmark Resolver
```python
def test_benchmark_resolver_fills_missing_city():
    """Cuando falta 'city', debe usar benchmark Pereira como fallback."""
    resolver = BenchmarkResolver()
    result = resolver.resolve("telephone", None, {"region": "eje_cafetero"})
    assert result.value == "+576123000000"  # Benchmark Pereira
    assert "benchmark" in result.sources
    assert result.confidence == 0.6  # Benchmark es menor que real

def test_benchmark_resolver_respects_high_confidence():
    """Cuando hay datos reales, NO usa benchmark."""
    resolver = BenchmarkResolver()
    result = resolver.resolve("city", "Santa Rosa de Cabal", {})
    assert result.value == "Santa Rosa de Cabal"
    assert "scraping" in result.sources
    assert result.confidence == 0.9
```

### Fase 2 - Test Disclaimer Generator
```python
def test_disclaimer_for_estimated_confidence():
    """Asset con confidence 0.5 debe tener disclaimer explícito."""
    generator = DisclaimerGenerator()
    disclaimer = generator.generate(
        confidence=0.5,
        sources=["web_scraping", "benchmark_pereira"],
        gaps=["telephone", "address"]
    )
    assert "confidence 0.5" in disclaimer
    assert "benchmark" in disclaimer.lower()
    assert "telephone" in disclaimer

def test_no_disclaimer_for_verified():
    """Asset con confidence ≥ 0.9 NO necesita disclaimer."""
    generator = DisclaimerGenerator()
    disclaimer = generator.generate(confidence=0.95, sources=["web", "gbp"])
    assert disclaimer == ""  # Sin disclaimer
```

### Fase 3 - Test Autonomous Researcher
```python
def test_researcher_finds_hotel_on_gbp():
    """Debe encontrar datos del hotel en Google Business Profile."""
    researcher = AutonomousResearcher()
    result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
    assert result.found == True
    assert result.data["telephone"] is not None
    assert "gbp" in result.sources

def test_researcher_cross_references():
    """Debe hacer cross-reference de datos entre fuentes."""
    researcher = AutonomousResearcher()
    result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
    assert result.confidence >= 0.5  # Cross-reference mejora confidence
```

### Fase 4 - Test Never Block Integration
```python
def test_never_block_preflight_check():
    """Even with missing data, preflight must not BLOCK."""
    checker = PreflightChecker()
    validated_data = {}  # Sin datos
    
    report = checker.check_asset("hotel_schema", validated_data)
    
    # NEVER BLOCK - debe ser WARNING o PASSED, nunca BLOCKED
    assert report.overall_status != PreflightStatus.BLOCKED
    assert report.can_proceed == True

def test_no_placeholders_in_output():
    """Output nunca debe contener placeholders."""
    validator = AssetContentValidator()
    content = "Hotel en Ciudad, teléfono +57XXX"
    
    result = validator.validate_content(content)
    
    assert result.status == ContentStatus.INVALID
    assert any("placeholder" in i.issue_type for i in result.issues)
```

---

## Criteria de Éxito

| Criterio | Target | Validación |
|----------|--------|------------|
| Placeholders en outputs | 0 (cero) | `asset_content_validator` debe pasar 100% |
| Assets bloqueados | 0 (cero) | Sistema nunca BLOCKED |
| Confidence real en outputs | 100% | Todos los assets tienen confidence score honesto |
| Disclaimer presente | 100% si confidence < 0.9 | Test `test_disclaimer_for_estimated_confidence` |
| Benchmark usado como fallback | 100% cuando no hay datos | Test `test_benchmark_resolver_fills_missing_city` |
| Investigación autónoma | Funciona | Test `test_researcher_finds_hotel_on_gbp` |
| Coherence score | ≥ 0.8 | Sin degradación |

---

## Validación de Implementación

```bash
# Todas las fases deben pasar ANTES de continuar
pytest tests/test_benchmark_resolver.py -v
pytest tests/test_disclaimer_generator.py -v  
pytest tests/test_autonomous_researcher.py -v
pytest tests/test_never_block_integration.py -v

# Validación de outputs Hotel Vísperas
python main.py v4complete --url https://hotelvisperas.com
# Verificar: 0 placeholders, 0 BLOCKED, todos assets delivery-ready
```

---

## Dependencias entre Fases

```
FASE 1 (Benchmark) ──────┐
                         ├──→ FASE 4 (Integration)
FASE 2 (Disclaimer) ─────┤
                         │
FASE 3 (Researcher) ─────┘
                         │
                         ↓
                   FASE 5 (Validación)
```

**Nota**: Las fases 1, 2, 3 pueden desarrollarse en paralelo por diferentes agentes. Fase 4 requiere todas las anteriores. Fase 5 es la validación final.

---

## Estimación de Cambio

| Fase | Complejidad | Archivos Principales | Estimación |
|------|-------------|---------------------|------------|
| Fase 1 | Media | 3 | ~200 líneas |
| Fase 2 | Baja | 2 | ~100 líneas |
| Fase 3 | Alta | 5 | ~400 líneas |
| Fase 4 | CRÍTICA | 6 | ~500 líneas |
| Fase 5 | Media | 4 | ~200 líneas |
| **TOTAL** | - | ~20 | ~1400 líneas + tests |

---

## Siguiente Paso

**Ejecutar FASE 0.5: TDD Gate**

Crear los tests iniciales en `tests/test_never_block_architecture/`:
1. `tests/test_benchmark_resolver.py`
2. `tests/test_disclaimer_generator.py`
3. `tests/test_autonomous_researcher.py`
4. `tests/test_never_block_integration.py`

Cada test debe FALLAR inicialmente (TDD Gate), evidenciando el comportamiento esperado.

---

*Plan generado según phased_project_executor.md v1.5.0*
*Versión skill*: 1.0.0
