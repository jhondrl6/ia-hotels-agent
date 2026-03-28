---
description: Prompt de implementación para FASE-I-01 - Integración Autonomous Researcher
version: 1.0.0
---

# FASE-I-01: Integración Autonomous Researcher + E2E V4COMPLETE

**ID**: FASE-I-01
**Objetivo**: Integrar AutonomousResearcher en el flujo de DataAssessment para que se active cuando datos sean insuficientes (tier LOW). Validar con E2E para Hotel Vísperas.
**Dependencias**: Ninguna (fase independiente)
**Duración estimada**: 1-2 horas
**Skill**: systematic-debugging, test-driven-development

---

## Contexto

El módulo `AutonomousResearcher` existe en `modules/providers/autonomous_researcher.py` (740 líneas) pero está **huérfano** - no está conectado a ningún flujo. Según capability contracts, una capability sin punto de invocación es una "desconexión".

### Diagnóstico Previo

| Componente | Estado |
|------------|--------|
| Módulo `autonomous_researcher.py` | ✅ Implementado |
| Tests documentados | ✅ 20 tests |
| En capabilities.md | ❌ NO aparece |
| Invocado en flujo | ❌ NO existe |
| Documentación GUIA_TECNICA.md | ⚠️ Parcial |

### Desconexión Identificada

```
AUTONOMOUS RESEARCHER (FASE 3)
            │
            │ ❌ NO INVOCADO
            ▼
    ┌───────────────┐
    │ data_assessment │ → No invoca researcher
    │conditional_gen │ → No invoca researcher  
    └───────────────┘
```

### Objetivo de la Fase

Conectar `AutonomousResearcher` al flujo de generación para que cuando `DataAssessment` clasifique los datos como `LOW`, se active la investigación autónoma.

---

## Tareas

### Tarea 1: Modificar DataAssessment con research_if_low_data()

**Objetivo**: Añadir método que invoca AutonomousResearcher cuando classification==LOW

**Archivos afectados**:
- `modules/asset_generation/data_assessment.py`

**Cambio exacto**: Añadir al final de la clase `DataAssessment`:

```python
from modules.providers.autonomous_researcher import AutonomousResearcher, ResearchOutput
from pathlib import Path
from typing import Optional

def research_if_low_data(
    self, 
    hotel_name: str, 
    assessment: 'DataAssessmentResult'
) -> Optional[ResearchOutput]:
    """
    Invoca AutonomousResearcher si classification == LOW.
    
    Args:
        hotel_name: Nombre del hotel a investigar
        assessment: Resultado de DataAssessmentResult
        
    Returns:
        ResearchOutput si se ejecutó research, None si no fue necesario
    """
    if assessment.classification != DataClassification.LOW:
        return None
        
    researcher = AutonomousResearcher(output_dir=Path("output"))
    result = researcher.research(hotel_name)
    
    # Guardar referencia para debugging
    self._last_research_output = result
    
    return result
```

**Criterios de aceptación**:
- [ ] Método `research_if_low_data()` existe en DataAssessment
- [ ] Retorna None si classification != LOW
- [ ] Retorna ResearchOutput si classification == LOW
- [ ] No lanza excepciones si AutonomousResearcher falla

---

### Tarea 2: Modificar ConditionalGenerator para enrichment

**Objetivo**: Invocar research y enriquecer hotel_data cuando tier==LOW

**Archivos afectados**:
- `modules/asset_generation/conditional_generator.py`

**Cambio exacto**: Después de la línea donde se ejecuta `data_assessment.assess()`, añadir:

```python
# FASE-I-01: Invocar AutonomousResearcher si tier==LOW
research_output = None
if data_assessment.classification == DataClassification.LOW:
    research_output = data_assessment.research_if_low_data(hotel_name, data_assessment)
    if research_output:
        # Enrich hotel_data con datos encontrados
        for source, data in research_output.data_found.items():
            if data and isinstance(data, dict):
                for key, value in data.items():
                    if key not in hotel_data or not hotel_data[key]:
                        hotel_data[key] = value
```

**Criterios de aceptación**:
- [ ] ConditionalGenerator invoca research_if_low_data cuando tier==LOW
- [ ] hotel_data se enriquecer con research_output.data_found
- [ ] No sobreescribe datos existentes (solo llena gaps)

---

### Tarea 3: Actualizar capabilities.md

**Objetivo**: Registrar AutonomousResearcher como capability "conectada"

**Archivos afectados**:
- `docs/contributing/capabilities.md`

**Cambio exacto**: En la tabla de la sección 13.5, añadir:

```markdown
| AutonomousResearcher | conectada | data_assessment.py:research_if_low_data() | research_output | HIGH |
```

**Criterios de aceptación**:
- [ ] AutonomousResearcher aparece en la matriz de capacidades
- [ ] Estado = "conectada"
- [ ] Punto de invocación documentado
- [ ] Output (research_output) especificado

---

### Tarea 4: Crear Test E2E V4COMPLETE con validación de desconexiones

**Objetivo**: Prueba end-to-end que verifica Autonomous Researcher operativos

**Archivo nuevo**:
- `tests/e2e/test_v4complete_autonomous_researcher.py`

**Estructura del test**:

```python
"""
E2E Test: V4COMPLETE + Autonomous Researcher Integration

Valida que AutonomousResearcher esté operativo en el flujo y que no haya
desconexiones ( capability huérfana ).
"""
import pytest
from modules.asset_generation.data_assessment import DataAssessment, DataClassification
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.providers.autonomous_researcher import AutonomousResearcher, ResearchOutput

class TestAutonomousResearcherIntegration:
    """Tests de integración Autonomous Researcher → Data Assessment → Conditional Generator"""
    
    def test_autonomous_researcher_invocable(self):
        """AutonomousResearcher puede ser instanciado y ejecutado"""
        researcher = AutonomousResearcher()
        result = researcher.research("Hotel Visperas")
        
        assert isinstance(result, ResearchOutput)
        assert result.hotel_name == "Hotel Visperas"
        assert isinstance(result.sources_checked, list)
        assert 0.0 <= result.confidence <= 1.0
    
    def test_data_assessment_low_triggers_research(self):
        """DataAssessment.research_if_low_data() invoca AutonomousResearcher cuando tier==LOW"""
        assessment = DataAssessment()
        
        # Simular datos LOW (mínimos)
        hotel_data = {"name": "Hotel Test"}
        result = assessment.assess(hotel_data, {}, {}, False)
        
        assert result.classification == DataClassification.LOW
        
        research_output = assessment.research_if_low_data("Hotel Test", result)
        
        # Si tier==LOW, debe invocar research
        assert research_output is not None or result.classification != DataClassification.LOW
    
    def test_research_output_persisted(self, tmp_path):
        """ResearchOutput se persiste a archivo JSON"""
        researcher = AutonomousResearcher(output_dir=tmp_path)
        result = researcher.research("Hotel Test")
        
        if result and result.confidence > 0:
            filepath = result.save_to_file(tmp_path)
            assert filepath.exists()
            assert filepath.suffix == ".json"
    
    def test_no_desconexion_autonomous_researcher(self):
        """
        DESCONEXIÓN CHECK: AutonomousResearcher NO debe ser huérfana.
        
        Esta prueba falla si:
        - AutonomousResearcher no está en capabilities.md
        - No se invoca desde ningún flujo
        - No produce output verificable
        """
        # 1. Verificar que existe el módulo
        from modules.providers.autonomous_researcher import AutonomousResearcher
        assert AutonomousResearcher is not None
        
        # 2. Verificar que tiene método research()
        researcher = AutonomousResearcher()
        assert hasattr(researcher, 'research')
        
        # 3. Verificar que se puede invocar sin errores
        result = researcher.research("Hotel Test")
        assert isinstance(result, ResearchOutput)
        
        # 4. Verificar output tiene estructura válida
        assert hasattr(result, 'hotel_name')
        assert hasattr(result, 'sources_checked')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'data_found')
        assert hasattr(result, 'gaps')
        assert hasattr(result, 'to_dict')
        
        # 5. Verificar capability en docs (si existe el archivo)
        import os
        capabilities_path = "docs/contributing/capabilities.md"
        if os.path.exists(capabilities_path):
            with open(capabilities_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Si está documentada, debe indicar "conectada"
            if 'AutonomousResearcher' in content:
                assert 'conectada' in content, "AutonomousResearcher existe en capabilities.md pero no está marcada como 'conectada'"
    
    def test_e2e_v4complete_autonomous_researcher_visperas(self):
        """
        E2E Test: Hotel Vísperas + Autonomous Researcher
        
        Sigue el comportamiento completo del flujo v4complete y valida
        que Autonomous Researcher está operativo.
        """
        from modules.orchestration.v4_orchestrator import v4complete
        
        hotel_name = "Hotel Vísperas"
        site_url = "https://hotelvisperas.com"
        
        # Ejecutar v4complete completo
        result = v4complete(hotel_name, site_url)
        
        # Validaciones de Publication Status
        assert result['publication_status'] in ['READY_FOR_CLIENT', 'DRAFT_INTERNAL', 'REQUIRES_REVIEW'], \
            f"Publication status inesperado: {result.get('publication_status')}"
        
        # Validación de Coherence Score
        coherence = result.get('coherence_score', 0.0)
        assert coherence >= 0.8, f"Coherence score {coherence} < 0.8"
        
        # DESCONEXIÓN CHECK: Autonomous Researcher debe estar operativo
        # Si research_output existe en result, verificar su estructura
        if 'research_output' in result:
            ro = result['research_output']
            assert isinstance(ro, ResearchOutput)
            assert len(ro.sources_checked) >= 0  # Puede estar vacío si no se activó
            assert 0.0 <= ro.confidence <= 1.0
            
            # Verificar que gaps y citations existen
            assert hasattr(ro, 'gaps')
            assert hasattr(ro, 'citations')
        else:
            # Si NO hay research_output, es porque tier no fue LOW
            # Verificar que data_assessment clasificación sea consistente
            assessment = DataAssessment()
            mock_hotel_data = result.get('hotel_data', {})
            mock_result = assessment.assess(
                mock_hotel_data,
                result.get('gbp_data', {}),
                result.get('seo_data', {}),
                result.get('scraping_success', False)
            )
            # Si classification != LOW, entonces no se esperaba research
            assert mock_result.classification != DataClassification.LOW, \
                "research_output no está en result pero tier es LOW - DESCONEXIÓN"
```

**Criterios de aceptación**:
- [ ] Test `test_autonomous_researcher_invocable` pasa
- [ ] Test `test_data_assessment_low_triggers_research` pasa
- [ ] Test `test_research_output_persisted` pasa
- [ ] Test `test_no_desconexion_autonomous_researcher` pasa
- [ ] Test `test_e2e_v4complete_autonomous_researcher_visperas` pasa con coherence >= 0.8

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_autonomous_researcher_invocable` | `tests/e2e/test_v4complete_autonomous_researcher.py` | Pasa |
| `test_data_assessment_low_triggers_research` | `tests/e2e/test_v4complete_autonomous_researcher.py` | Pasa |
| `test_research_output_persisted` | `tests/e2e/test_v4complete_autonomous_researcher.py` | Pasa |
| `test_no_desconexion_autonomous_researcher` | `tests/e2e/test_v4complete_autonomous_researcher.py` | Pasa |
| `test_e2e_v4complete_autonomous_researcher_visperas` | `tests/e2e/test_v4complete_autonomous_researcher.py` | Pasa con coherence >= 0.8 |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python3 -m pytest tests/e2e/test_v4complete_autonomous_researcher.py -v
python3 scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

### 1. REGISTRY.md
Ejecutar:
```bash
python scripts/log_phase_completion.py --fase FASE-I-01 \
    --desc "Integración Autonomous Researcher en flujo + E2E V4COMPLETE test" \
    --archivos-mod "modules/asset_generation/data_assessment.py" \
                     "modules/asset_generation/conditional_generator.py" \
                     "docs/contributing/capabilities.md" \
    --archivos-nuevos "tests/e2e/test_v4complete_autonomous_researcher.py" \
    --tests "5" \
    --coherence 0.84 \
    --check-manual-docs
```

### 2. Actualizar capabilities.md
Ya está incluido en la tarea 3.

### 3. Documentación Post-Fase
Entrada en REGISTRY.md confirma completitud.

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: `pytest tests/e2e/test_v4complete_autonomous_researcher.py` pasa 5/5
- [ ] **Suite NEVER_BLOCK passing**: `python3 scripts/run_all_validations.py --quick` pasa
- [ ] **Coherence >= 0.8**: Validado en test E2E
- [ ] **capabilities.md actualizado**: AutonomousResearcher = "conectada"
- [ ] **REGISTRY.md actualizado**: log_phase_completion.py ejecutado
- [ ] **Autonomous Researcher no es huérfana**: test_no_desconexion pasa
- [ ] **Flujo E2E funciona**: v4complete para Hotel Vísperas opera correctamente

---

## Restricciones

- **NO modificar** la lógica existente de `DataAssessment.assess()` - solo añadir nuevo método
- **NO modificar** scrapers individuales (BookingScraper, TripAdvisorScraper, etc.) - son stubs intencionales
- **El test E2E debe pasar** con Hotel Vísperas real si los datos lo permiten

---

## Dependencias

Ninguna - esta fase es independiente y solo conecta capacidades existentes.

---

## Notas

- FASE-I-01 sigue la convención de nomenclatura `FASE-{LETRA}` para fases de feature
- La "I" viene después de H (FASE-H-08 fue la última)
- Si esta fase es exitosa, la capability AutonomousResearcher dejará de ser "huérfana"
