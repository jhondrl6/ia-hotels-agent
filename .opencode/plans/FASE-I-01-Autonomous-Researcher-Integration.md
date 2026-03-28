# Plan FASE-I-01: Integración Autonomous Researcher + E2E V4COMPLETE

## 1. Objetivo

Integrar `AutonomousResearcher` en el flujo de generación para que se active cuando `DataAssessment` clasifique los datos como `LOW` (<30%). Validar con prueba E2E para Hotel Vísperas.

---

## 2. Diagnóstico (ya realizado)

| Componente | Estado |
|------------|--------|
| Módulo `autonomous_researcher.py` | ✅ Implementado (740 líneas) |
| Tests `test_autonomous_researcher.py` | ✅ 20 tests documentados |
| Capacidad en capabilities.md | ❌ NO aparece (huérfana) |
| Integración en `data_assessment.py` | ❌ NO invoked |
| Integración en `conditional_generator.py` | ❌ NO invoked |
| Documentación GUIA_TECNICA.md | ⚠️ Parcial (línea 232) |

---

## 3. Arquitectura de Integración

```
DataAssessment.assess()
       │
       ▼
┌─────────────────┐
│ classification  │
│    = LOW?       │
└────────┬────────┘
         │Sí
         ▼
┌─────────────────────────┐
│ AutonomousResearcher() │
│ .research(hotel_name)   │
└────────┬────────────────┘
         │
    sources_checked[]
    data_found{}
    confidence
         │
         ▼
   ¿confidence >= 0.5?
    /            \
  Sí              No
   │               │
   ▼               ▼
 Retry/          Benchmark
 fallback        Resolver
```

---

## 4. Archivos a Modificar

### 4.1 `modules/asset_generation/data_assessment.py`

**Cambio**: Añadir método `research_if_low_data()` que invoca AutonomousResearcher.

```python
from modules.providers.autonomous_researcher import AutonomousResearcher

def research_if_low_data(self, hotel_name: str, assessment: DataAssessmentResult) -> Optional[ResearchOutput]:
    """Invoca AutonomousResearcher si classification == LOW."""
    if assessment.classification != DataClassification.LOW:
        return None
    researcher = AutonomousResearcher()
    return researcher.research(hotel_name)
```

### 4.2 `modules/asset_generation/conditional_generator.py`

**Cambio**: Después de `DataAssessment`, si tier=LOW invocar research.

```python
# Después de data_assessment en generate_assets()
if data_assessment.classification == DataClassification.LOW:
    research_output = data_assessment.research_if_low_data(hotel_name, data_assessment)
    if research_output:
        # Enrich hotel_data con research_output.data_found
        enrich_hotel_data(research_output)
```

### 4.3 `docs/contributing/capabilities.md`

**Cambio**: Agregar AutonomousResearcher a matriz de capacidades.

```markdown
| AutonomousResearcher | conectada | data_assessment.py:research_if_low_data() | research_output | HIGH |
```

### 4.4 `docs/GUIA_TECNICA.md`

**Cambio**: Actualizar sección 232 para indicar que YA está integrado.

---

## 5. Prueba E2E V4COMPLETE Hotel Vísperas

### 5.1 Archivo
`tests/e2e/test_v4complete_autonomous_researcher.py`

### 5.2 Comportamiento a Validar

| Step | Checkpoint | Validación |
|------|------------|------------|
| 1 | Hotel Vísperas data assessment | classification = LOW/MED |
| 2 | AutonomousResearcher invoked | researcher.last_research_output is not None |
| 3 | Sources checked | ['gbp', 'booking', 'tripadvisor', 'instagram'] subset |
| 4 | Confidence score | 0.0 <= confidence <= 1.0 |
| 5 | ResearchOutput persisted | JSON file in output_dir |
| 6 | Gaps identified | gaps list populated |
| 7 | Cross-reference | conflicts list populated |
| 8 | Enrichment | hotel_data enriched with research data |

### 5.3 Estructura del Test

```python
def test_v4complete_autonomous_researcher_visperas():
    """E2E test: Hotel Vísperas + Autonomous Researcher integration."""
    # Arrange
    hotel_name = "Hotel Vísperas"
    site_url = "https://hotelvisperas.com"
    
    # Act
    result = v4complete(hotel_name, site_url)
    
    # Assert
    assert result['publication_status'] in ['READY_FOR_CLIENT', 'DRAFT_INTERNAL']
    assert result['coherence_score'] >= 0.8
    
    # Autonomous Researcher specific assertions
    assert result.get('research_output') is not None
    assert len(result['research_output'].sources_checked) >= 1
    assert 0.0 <= result['research_output'].confidence <= 1.0
```

---

## 6. Documentación Post-Fase

### 6.1 REGISTRY.md entrada

```
## FASE-I-01 - {date}
**Descripcion:** Integración Autonomous Researcher en flujo + E2E V4COMPLETE test

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/data_assessment.py` | research_if_low_data() |
| `modules/asset_generation/conditional_generator.py` | Enrichment desde research |
| `docs/contributing/capabilities.md` | AutonomousResearcher conectada |
| `docs/GUIA_TECNICA.md` | Documentación integración |

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| `tests/e2e/test_v4complete_autonomous_researcher.py` | E2E test Hotel Vísperas |

### Validaciones
- [ ] Tests passing (regression + nuevo)
- [ ] Suite NEVER_BLOCK passing
- [ ] Coherence >= 0.8
- [ ] Capability contract verificado (AutonomousResearcher = conectada)
```

### 6.2 Log script

```bash
python scripts/log_phase_completion.py --fase FASE-I-01 \
    --desc "Integración Autonomous Researcher en flujo + E2E V4COMPLETE test" \
    --archivos-mod "modules/asset_generation/data_assessment.py" \
                     "modules/asset_generation/conditional_generator.py" \
                     "docs/contributing/capabilities.md" \
                     "docs/GUIA_TECNICA.md" \
    --auto-sync
```

---

## 7. Secuencia de Ejecución

| Orden | Paso | Herramienta |
|-------|------|-------------|
| 1 | Modificar `data_assessment.py` | patch |
| 2 | Modificar `conditional_generator.py` | patch |
| 3 | Actualizar `capabilities.md` | patch |
| 4 | Actualizar `GUIA_TECNICA.md` | patch |
| 5 | Crear test E2E | write_file |
| 6 | Ejecutar tests | terminal (pytest) |
| 7 | Log fase | terminal (log_phase_completion.py) |
| 8 | Validación final | run_all_validations.py --quick |

---

## 8. Criterios de Éxito

- [ ] `AutonomousResearcher` aparece en capabilities.md como "conectada"
- [ ] Test E2E pasa con coherence >= 0.8
- [ ] `research_output` presente en resultado final de v4complete
- [ ] REGISTRY.md actualizado
- [ ] Suite NEVER_BLOCK passing
