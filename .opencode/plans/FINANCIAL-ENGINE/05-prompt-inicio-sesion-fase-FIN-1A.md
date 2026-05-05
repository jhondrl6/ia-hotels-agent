# 05-prompt-inicio-sesion-fase-FIN-1A

**Fase**: FIN-1A — Epistemic Metadata Model  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: Ninguna (primera fase)  
**Bloquea a**: FIN-1B  

---

## Objetivo

Crear el modelo de metadata epistémica (`FinancialEvidence`) y propagarlo a través de los data structures financieros existentes (`FinancialScenario`, `ADRResolutionResult`, `FinancialCalculationResult`). Esta fase define los cimientos para que todo el sistema sepa, campo por campo, de dónde viene cada número y con qué confianza mostrarlo.

---

## Contexto de Arquitectura

El sistema actual ya tiene:
- `HotelFinancialData` con campos `adr_source`, `occupancy_source`, `channel_source` (tipo `str = "unknown"`) en `scenario_calculator.py`
- `ADRResolutionResult` con `source: str` y `confidence: str` en `adr_resolution_wrapper.py`
- `EvidenceTier` enum en `modules/commercial_documents/data_structures.py`
- `FinancialScenario` dataclass en `scenario_calculator.py`

Pero estos campos son planos (`str`), no estructurados. Se necesita un modelo unificado.

---

## Tareas

### T1: Crear `FinancialEvidence` dataclass

**Archivo**: `modules/financial_engine/financial_evidence.py` (NUEVO)

Crear dataclasses:

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

class EpistemicStatus(Enum):
    MEASURED = "measured"
    OBSERVED = "observed"
    REGIONAL_BENCHMARK = "regional_benchmark"
    DEFAULTED = "defaulted"
    SIMULATED = "simulated"
    CONFLICT = "conflict"

class PrecisionTier(Enum):
    A = "A"  # Todos los campos measured → cifra exacta
    B = "B"  # Mayoría measured/observed, al menos 1 regional_benchmark
    C = "C"  # Al menos 1 defaulted o simulated

@dataclass
class FieldEvidence:
    value: float
    source: str  # ej: "benchmarking_2026:eje_cafetero:boutique_10_25"
    epistemic_status: EpistemicStatus
    precision: str = "range"  # "exact" o "range"
    can_show_exact: bool = False

@dataclass
class FinancialEvidence:
    adr_cop: FieldEvidence
    occupancy_rate: FieldEvidence
    direct_channel_percentage: FieldEvidence
    ota_commission_rate: FieldEvidence = field(default_factory=lambda: FieldEvidence(
        value=0.15, source="industry_standard", 
        epistemic_status=EpistemicStatus.DEFAULTED,
        precision="range", can_show_exact=False
    ))

    @property
    def precision_tier(self) -> PrecisionTier:
        """Determina tier por peor fuente."""
        statuses = {self.adr_cop.epistemic_status, 
                     self.occupancy_rate.epistemic_status,
                     self.direct_channel_percentage.epistemic_status}
        if statuses == {EpistemicStatus.MEASURED}:
            return PrecisionTier.A
        if EpistemicStatus.DEFAULTED in statuses or EpistemicStatus.SIMULATED in statuses:
            return PrecisionTier.C
        return PrecisionTier.B

    @property
    def can_show_exact_money(self) -> bool:
        return all(
            f.epistemic_status in {EpistemicStatus.MEASURED, EpistemicStatus.OBSERVED}
            for f in [self.adr_cop, self.occupancy_rate, self.direct_channel_percentage]
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialización para financial_scenarios.json."""
        return {
            "adr_cop": {"value": self.adr_cop.value, "source": self.adr_cop.source,
                         "epistemic_status": self.adr_cop.epistemic_status.value,
                         "precision": self.adr_cop.precision,
                         "can_show_exact": self.adr_cop.can_show_exact},
            "occupancy_rate": {"value": self.occupancy_rate.value, ...},
            "direct_channel_percentage": {...},
            "financial_precision_tier": self.precision_tier.value,
            "can_show_exact_money": self.can_show_exact_money,
        }
```

### T2: Crear helper `build_financial_evidence()`

En el mismo archivo `financial_evidence.py`, crear función factory que reciba datos dispersos y construya el `FinancialEvidence`:

```python
def build_financial_evidence(
    adr_cop: float, adr_source: str, adr_status: EpistemicStatus,
    occupancy_rate: float, occupancy_source: str, occupancy_status: EpistemicStatus,
    direct_channel_pct: float, channel_source: str, channel_status: EpistemicStatus,
) -> FinancialEvidence:
    ...
```

Mapear desde los `source` strings actuales (`"user_provided"`, `"web_scraping"`, `"regional_v410"`, `"legacy_hardcode"`) a `EpistemicStatus`:
- `user_provided` → `MEASURED`
- `web_scraping` → `OBSERVED`
- `regional_v410` → `REGIONAL_BENCHMARK`
- `legacy_hardcode` → `DEFAULTED`

### T3: Integrar en `FinancialScenario` y `ScenarioCalculator`

**Archivo**: `modules/financial_engine/scenario_calculator.py`

- Agregar campo opcional `financial_evidence: Optional[FinancialEvidence] = None` a `FinancialScenario`
- En `ScenarioCalculator.calculate_scenarios()`, después de calcular escenarios, construir `FinancialEvidence` con la metadata disponible de `HotelFinancialData`
- Incluir `financial_evidence.to_dict()` en la serialización del output (se persiste en `financial_scenarios.json`)

**Archivo**: `modules/financial_engine/calculator_v2.py`

- Verificar que `FinancialCalculationResult.to_dict()` incluya `financial_evidence` si está disponible

### T4: Tests unitarios

**Archivo**: `tests/financial_engine/test_financial_evidence.py` (NUEVO)

Mínimo 8 tests:
1. `test_field_evidence_measured_can_show_exact` → MEASURED con can_show_exact=True
2. `test_field_evidence_defaulted_cannot_show_exact` → DEFAULTED con can_show_exact=False
3. `test_precision_tier_a_all_measured` → Tier A cuando todo es MEASURED
4. `test_precision_tier_b_regional_benchmark` → Tier B con regional_benchmark
5. `test_precision_tier_c_has_defaulted` → Tier C cuando hay DEFAULTED
6. `test_can_show_exact_money_true` → True cuando todo es MEASURED/OBSERVED
7. `test_can_show_exact_money_false_with_defaulted` → False con DEFAULTED
8. `test_build_financial_evidence_maps_sources_correctly` → Mapeo de source strings a EpistemicStatus

---

## Criterios de Completitud

- [ ] `modules/financial_engine/financial_evidence.py` existe con `FinancialEvidence`, `FieldEvidence`, `EpistemicStatus`, `PrecisionTier`, `build_financial_evidence()`
- [ ] `FinancialScenario` tiene campo opcional `financial_evidence`
- [ ] `ScenarioCalculator` construye `FinancialEvidence` y lo incluye en output
- [ ] `tests/financial_engine/test_financial_evidence.py` existe con ≥8 tests
- [ ] Todos los tests pasan: `./venv/Scripts/python.exe -m pytest tests/financial_engine/test_financial_evidence.py -v`
- [ ] No hay regresiones: `./venv/Scripts/python.exe -m pytest tests/financial_engine/ -v --tb=short`

---

## Restricciones

- Máximo 60 iteraciones del agente
- **NO modificar `plan_maestro_data.json`** (es legacy)
- **NO tocar `feature_flags.py`** (eso es FIN-2B)
- **NO modificar templates** (eso es FIN-3)
- Solo crear dataclasses + propagación + tests. Nada de rendering ni flags.

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar (completa o incompleta):

```bash
# 1. Registrar en REGISTRY.md
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-1A \
    --desc "Financial Evidence dataclass + epistemic metadata propagation" \
    --archivos-nuevos "modules/financial_engine/financial_evidence.py,tests/financial_engine/test_financial_evidence.py" \
    --archivos-mod "modules/financial_engine/scenario_calculator.py,modules/financial_engine/calculator_v2.py" \
    --tests "8" \
    --check-manual-docs

# 2. Actualizar checklist maestro
# Marcar esta fase como ✅ en 06-checklist-implementacion.md

# 3. Si fase incompleta por agotamiento:
#    - Marcar como ⏳ INCOMPLETA con checkpoint
#    - Listar qué falta
#    - Guardar evidencia en evidence/FIN-1A/
```
