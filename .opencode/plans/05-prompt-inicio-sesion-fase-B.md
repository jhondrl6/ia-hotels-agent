# FASE-B: ScenarioCalculator — Narrativa por Capas (Verificable → Hipótesis)

**ID**: FASE-B
**Objetivo**: Rediseñar `ScenarioCalculator` para que produzca `FinancialBreakdown` como salida, separando comisión OTA verificable (Capa 1) de supuestos de mejora (Capa 2A/2B). El número principal deja de ser "pérdida neta" y pasa a ser "comisión OTA verificable".
**Dependencias**: FASE-A (FinancialBreakdown, EvidenceTier, Scenario.monthly_loss_central)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El `ScenarioCalculator` actual (`modules/financial_engine/scenario_calculator.py`, 361 líneas) produce un solo número `monthly_loss_cop` que mezcla:

```
pérdida = comisión_OTA_actual - ahorro_shift_OTA - boost_visibilidad_IA
```

La comisión OTA ($5.4M) es verificable. Los otros dos componentes son supuestos. El resultado ($2.6M) no es rastreable ni verificable.

El rediseño cambia el output del ScenarioCalculator para que produzca un `FinancialBreakdown` donde cada componente tiene fuente, valor y etiqueta (VERIFIED/ESTIMATED).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada — FinancialBreakdown, EvidenceTier, Scenario.monthly_loss_central existen |

### Base Técnica Disponible
- `modules/financial_engine/scenario_calculator.py` (361 líneas)
  - `ScenarioType(Enum)` — CONSERVATIVE, REALISTIC, OPTIMISTIC
  - `FinancialScenario(dataclass)` — scenario_type, monthly_loss_cop, probability, calculation_basis, confidence_score, assumptions, disclaimer
  - `HotelFinancialData(dataclass)` — rooms, adr_cop, occupancy_rate, ota_commission_rate, direct_channel_percentage, ota_presence
  - `ScenarioCalculator` — calculate_monthly_revenue(), calculate_scenarios()
- `modules/financial_engine/financial_calculator_v2.py` — wrapper que usa ScenarioCalculator
- `modules/commercial_documents/data_structures.py` — `FinancialBreakdown` (creado en FASE-A)
- Tests: `tests/financial_engine/test_scenario_calculator.py`, `test_calculator_v2.py`
- Referencia: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md` Secciones 10-11

---

## Tareas

### Tarea 1: Agregar método `calculate_breakdown()` a ScenarioCalculator

**Objetivo**: Nuevo método que retorna `FinancialBreakdown` en vez de un solo `monthly_loss_cop`.

**Archivo afectado**: `modules/financial_engine/scenario_calculator.py`

**Cambios**:
```python
from modules.commercial_documents.data_structures import FinancialBreakdown, EvidenceTier

class ScenarioCalculator:
    # ... métodos existentes NO se modifican ...
    
    def calculate_breakdown(self, hotel_data: HotelFinancialData) -> FinancialBreakdown:
        """
        Calcula desglose financiero por capas.
        
        CAPA 1: Comisión OTA verificable (hechos)
        CAPA 2A: Ahorro por migración OTA→directo (hipótesis con fuente)
        CAPA 2B: Ingresos por visibilidad IA (hipótesis con fuente)
        """
        # Capa 1: Comisión OTA = noches_OTA × ADR × comisión_rate
        nights_per_month = hotel_data.rooms * hotel_data.occupancy_rate * 30
        ota_nights = nights_per_month * (1 - hotel_data.direct_channel_percentage)
        monthly_ota_commission = ota_nights * hotel_data.adr_cop * hotel_data.ota_commission_rate
        
        # Capa 2A: Shift OTA→directo
        shift_savings = monthly_ota_commission * self._get_shift_percentage(hotel_data)
        
        # Capa 2B: IA revenue boost
        ia_revenue = self._get_ia_revenue_estimate(hotel_data, nights_per_month)
        
        # Evidence tier
        tier = self._determine_evidence_tier(hotel_data)
        
        # Fuentes de datos
        sources = self._trace_data_sources(hotel_data)
        
        return FinancialBreakdown(
            monthly_ota_commission_cop=monthly_ota_commission,
            ota_commission_basis=f"{int(ota_nights)} noches OTA × ${int(hotel_data.adr_cop):,} ADR × {hotel_data.ota_commission_rate*100:.0f}% comisión",
            ota_commission_source=sources.get('ota_commission', 'unknown'),
            shift_savings_cop=shift_savings,
            shift_percentage=self._get_shift_percentage(hotel_data),
            shift_source=sources.get('shift', 'hardcoded: sin GA4'),
            ia_revenue_cop=ia_revenue,
            ia_boost_percentage=self._get_ia_boost_percentage(hotel_data),
            ia_source=sources.get('ia_boost', 'estimado: sin datos GA4'),
            evidence_tier=tier.value,
            disclaimer=tier.disclaimer,
            hotel_data_sources=sources
        )
    
    def _determine_evidence_tier(self, hotel_data: HotelFinancialData) -> EvidenceTier:
        """Determina tier basado en disponibilidad de datos."""
        # Si tiene GA4+GSC → A
        # Si tiene benchmarks regionales → B
        # Si solo tiene scraping → C
        # Lógica: por ahora siempre C hasta que GA4 se integre
        return EvidenceTier.C
    
    def _get_shift_percentage(self, hotel_data: HotelFinancialData) -> float:
        """Porcentaje de migración OTA→directo. Documentar fuente."""
        # TODO: Reemplazar con dato de GA4 cuando esté disponible
        return 0.10  # Benchmark: hoteles con mejora digital
    
    def _get_ia_boost_percentage(self, hotel_data: HotelFinancialData) -> float:
        """Porcentaje de boost por visibilidad IA. Documentar fuente."""
        # TODO: Reemplazar con dato de GA4 cuando esté disponible
        return 0.05  # Estimado: sin datos GA4
    
    def _get_ia_revenue_estimate(self, hotel_data: HotelFinancialData, nights: float) -> float:
        """Estimación de ingresos nuevos por visibilidad IA."""
        return nights * hotel_data.adr_cop * self._get_ia_boost_percentage(hotel_data)
    
    def _trace_data_sources(self, hotel_data: HotelFinancialData) -> Dict[str, str]:
        """Trazabilidad: mapea cada input a su fuente."""
        return {
            'adr': getattr(hotel_data, 'adr_source', 'unknown'),
            'rooms': 'hotel_data',
            'occupancy': getattr(hotel_data, 'occupancy_source', 'unknown'),
            'ota_commission': 'industry_standard_15pct',
            'direct_channel': getattr(hotel_data, 'channel_source', 'unknown'),
            'shift': 'hardcoded: sin GA4',
            'ia_boost': 'estimado: sin datos GA4'
        }
```

**Criterios de aceptación**:
- [ ] `calculate_breakdown()` existe y retorna `FinancialBreakdown`
- [ ] `monthly_ota_commission_cop` se calcula correctamente (noches_OTA × ADR × comisión)
- [ ] Cada componente tiene su fuente documentada
- [ ] `evidence_tier` se asigna correctamente
- [ ] Los métodos existentes (`calculate_scenarios`, `calculate_monthly_revenue`) NO se modifican

### Tarea 2: Agregar campos de fuente a HotelFinancialData

**Objetivo**: El dataclass `HotelFinancialData` debe rastrear la fuente de cada dato.

**Archivo afectado**: `modules/financial_engine/scenario_calculator.py`

**Cambios**: Agregar campos opcionales a `HotelFinancialData`:
```python
@dataclass
class HotelFinancialData:
    rooms: int
    adr_cop: float
    occupancy_rate: float
    ota_commission_rate: float = 0.15
    direct_channel_percentage: float = 0.2
    ota_presence: float = 0.0
    # NUEVOS — trazabilidad de fuente
    adr_source: str = "unknown"
    occupancy_source: str = "unknown"
    channel_source: str = "unknown"
```

**Criterios de aceptación**:
- [ ] Los campos nuevos son opcionales (default "unknown")
- [ ] Backward compatible: instanciación existente funciona igual

### Tarea 3: Tests del nuevo cálculo por capas

**Archivo afectado**: Crear/actualizar `tests/financial_engine/test_scenario_calculator.py`

**Tests requeridos**:
```python
# 1. Comisión OTA se calcula correctamente
def test_breakdown_ota_commission_amazilia():
    hotel = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.5, 
                                direct_channel_percentage=0.2, ota_commission_rate=0.15)
    calc = ScenarioCalculator()
    breakdown = calc.calculate_breakdown(hotel)
    # 10 rooms × 0.5 occupancy × 30 days = 150 nights/mes
    # 80% OTA = 120 nights
    # 120 × 300K × 15% = 5,400,000
    assert breakdown.monthly_ota_commission_cop == 5400000

# 2. Capas están separadas
def test_breakdown_layers_separated():
    hotel = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.5)
    calc = ScenarioCalculator()
    breakdown = calc.calculate_breakdown(hotel)
    # Comisión OTA (Capa 1) debe ser > shift_savings (Capa 2A) + ia_revenue (Capa 2B)
    assert breakdown.monthly_ota_commission_cop > breakdown.shift_savings_cop
    assert breakdown.monthly_ota_commission_cop > breakdown.ia_revenue_cop

# 3. Evidence tier es C por defecto (sin GA4)
def test_breakdown_evidence_tier_c():
    hotel = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.5)
    calc = ScenarioCalculator()
    breakdown = calc.calculate_breakdown(hotel)
    assert breakdown.evidence_tier == "C"
    assert "limitados" in breakdown.disclaimer

# 4. Cada dato tiene fuente
def test_breakdown_data_sources():
    hotel = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.5,
                                adr_source="onboarding")
    calc = ScenarioCalculator()
    breakdown = calc.calculate_breakdown(hotel)
    assert breakdown.hotel_data_sources['adr'] == "onboarding"

# 5. Methods existentes siguen funcionando
def test_backward_compat_calculate_scenarios():
    hotel = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.5)
    calc = ScenarioCalculator()
    scenarios = calc.calculate_scenarios(hotel)  # no debe fallar
    assert scenarios is not None
```

**Criterios de aceptación**:
- [ ] 5 tests nuevos pasan
- [ ] Tests existentes de scenario_calculator siguen pasando

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_breakdown_ota_commission_amazilia | `tests/financial_engine/test_scenario_calculator.py` | Comisión = $5,400,000 |
| test_breakdown_layers_separated | `tests/financial_engine/test_scenario_calculator.py` | Capa 1 > Capa 2A y 2B |
| test_breakdown_evidence_tier_c | `tests/financial_engine/test_scenario_calculator.py` | Tier C por defecto |
| test_breakdown_data_sources | `tests/financial_engine/test_scenario_calculator.py` | Fuentes rastreables |
| test_backward_compat | `tests/financial_engine/test_scenario_calculator.py` | API existente funciona |
| Suite completa | `tests/` | 0 failures |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/financial_engine/test_scenario_calculator.py -v
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

---

## Restricciones

- NO eliminar métodos existentes de ScenarioCalculator (calculate_scenarios, calculate_monthly_revenue)
- NO modificar v4_diagnostic_generator, v4_proposal_generator — eso es FASE-E/F
- NO modificar main.py — eso es FASE-G
- Los valores hardcoded (10% shift, 5% IA boost) se mantienen pero ahora están DOCUMENTADOS con su fuente. La mejora a datos reales viene con GA4 (futuro)
- HotelFinancialData nuevos campos son Optional con defaults

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar FASE-B como completada
3. **`09-documentacion-post-proyecto.md`** — Sección A: agregar calculate_breakdown, Sección D: métricas
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "ScenarioCalculator: calculate_breakdown() con narrativa por capas verificable→hipótesis" \
    --archivos-mod "modules/financial_engine/scenario_calculator.py,tests/financial_engine/test_scenario_calculator.py" \
    --tests "5"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `calculate_breakdown()` retorna `FinancialBreakdown` correcto
- [ ] Comisión OTA se calcula con fórmula verificable
- [ ] Supuestos (shift %, IA boost %) están documentados con fuente
- [ ] `HotelFinancialData` tiene campos de trazabilidad
- [ ] 5 tests nuevos pasan
- [ ] Tests existentes pasan (backward compat)
- [ ] `log_phase_completion.py` ejecutado
