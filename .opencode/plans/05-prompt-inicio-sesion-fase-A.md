# FASE-A: Data Structures — FinancialBreakdown + Scenario Extendido

**ID**: FASE-A
**Objetivo**: Crear las estructuras de datos base que soportan el rediseño del motor financiero: nuevo dataclass `FinancialBreakdown`, extensión de `Scenario` con campo `monthly_loss_central`, y el enum `EvidenceTier`.
**Dependencias**: Ninguna (es la fundación)
**Duración estimada**: 1.5-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El motor financiero actual tiene dos problemas estructurales en las dataclasses:

1. **`Scenario`** (data_structures.py:83) solo tiene `monthly_loss_min` y `monthly_loss_max`. No hay valor central. El diagnóstico consume `monthly_loss_max` como cifra principal, inflando el valor un 20%.

2. **No existe `FinancialBreakdown`**. La fórmula actual produce un solo número (`monthly_loss_cop`) que mezcla comisión OTA verificable con supuestos de mejora. No hay forma de separar hechos de hipótesis.

3. **No hay Evidence Tier**. No se puede etiquetar un valor como VERIFIED vs ESTIMATED.

El rediseño requiere que estas estructuras existan ANTES de que el ScenarioCalculator y los generadores puedan usarlas.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| (Ninguna — esta es la primera) | — |

### Base Técnica Disponible
- Archivo: `modules/commercial_documents/data_structures.py` (409 líneas)
- Dataclass actual `Scenario` en línea 83
- Dataclass actual `FinancialScenarios` en línea 106
- Tests: `tests/financial_engine/test_scenario_calculator.py`, tests generales en `tests/`
- Referencia completa del problema: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md`

---

## Tareas

### Tarea 1: Agregar campo `monthly_loss_central` a `Scenario`

**Objetivo**: Añadir un campo opcional para el valor central del rango, que será el valor principal de presentación.

**Archivo afectado**: `modules/commercial_documents/data_structures.py`

**Cambios específicos**:
```python
@dataclass
class Scenario:
    monthly_loss_min: int
    monthly_loss_max: int
    probability: float
    description: str
    assumptions: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    monthly_opportunity_cop: int = 0
    monthly_loss_central: Optional[int] = None  # NUEVO — valor central de presentación
```

**Reglas**:
- `monthly_loss_central` es `Optional[int]` con default `None` — no romper backwards compatibility
- Si es `None`, los métodos existentes (`format_loss_cop`, `is_equilibrium_or_gain`) deben seguir usando `monthly_loss_max` como antes (legacy fallback)
- Si tiene valor, `format_loss_cop()` debe usar `monthly_loss_central` en vez de `monthly_loss_max`
- `is_equilibrium_or_gain()` debe usar `monthly_loss_central` si existe, sino `monthly_loss_max`

**Criterios de aceptación**:
- [ ] `Scenario` tiene campo `monthly_loss_central: Optional[int] = None`
- [ ] `format_loss_cop()` usa central si existe, max como fallback
- [ ] `is_equilibrium_or_gain()` usa central si existe, max como fallback
- [ ] Crear Scenario sin `monthly_loss_central` funciona igual que antes (backward compat)
- [ ] Tests existentes no se rompen

### Tarea 2: Crear dataclass `FinancialBreakdown`

**Objetivo**: Nuevo dataclass que separa la composición del cálculo financiero en capas verificables vs estimadas.

**Archivo afectado**: `modules/commercial_documents/data_structures.py` (agregar DESPUÉS de `FinancialScenarios`)

**Estructura**:
```python
@dataclass
class FinancialBreakdown:
    """Desglose financiero por capas: verificable vs estimado."""
    
    # CAPA 1: Datos verificables (hechos del hotel + comisión OTA)
    monthly_ota_commission_cop: float      # Ej: $5,400,000
    ota_commission_basis: str              # Ej: "120 noches OTA × $300K ADR × 15%"
    ota_commission_source: str             # Ej: "onboarding" | "scraping" | "benchmark"
    
    # CAPA 2A: Ahorro por migración OTA→directo (hipótesis)
    shift_savings_cop: float               # Ej: $540,000
    shift_percentage: float                # Ej: 0.10
    shift_source: str                      # Ej: "benchmark: hoteles con presencia digital mejorada"
    
    # CAPA 2B: Ingresos nuevos por visibilidad IA (hipótesis)
    ia_revenue_cop: float                  # Ej: $2,250,000
    ia_boost_percentage: float             # Ej: 0.05
    ia_source: str                         # Ej: "estimado: sin datos GA4"
    
    # META
    evidence_tier: str                     # "A" | "B" | "C"
    disclaimer: str                        # Texto honesto sobre confianza del dato
    hotel_data_sources: Dict[str, str] = field(default_factory=dict)
    # Dict de fuente por dato: {"adr": "onboarding", "rooms": "onboarding", "occupancy": "benchmark"}
```

**Criterios de aceptación**:
- [ ] `FinancialBreakdown` existe con todos los campos documentados
- [ ] Cada campo tiene tipo anotado y docstring
- [ ] `hotel_data_sources` es un dict que mapea cada input a su fuente
- [ ] El dataclass se puede instanciar sin errores

### Tarea 3: Crear enum `EvidenceTier`

**Objetivo**: Enumeración estándar para clasificar la calidad de la evidencia financiera.

**Archivo afectado**: `modules/commercial_documents/data_structures.py` (agregar ANTES de `FinancialBreakdown`)

**Estructura**:
```python
class EvidenceTier(Enum):
    """Clasificación de calidad de evidencia financiera."""
    A = "A"  # GA4 + GSC conectados — datos verificables
    B = "B"  # Benchmarks regionales + scraping — estimado con base
    C = "C"  # Solo scraping básico — estimado con baja confianza
    
    @property
    def disclaimer(self) -> str:
        if self == EvidenceTier.A:
            return "Basado en datos de Google Analytics y Search Console verificados."
        elif self == EvidenceTier.B:
            return "Estimación basada en benchmarks regionales y datos de su web. Para mayor precisión, conecte Google Analytics 4."
        else:
            return "Estimación basada en datos limitados de su web. Conecte Google Analytics 4 para un diagnóstico más preciso."
```

**Criterios de aceptación**:
- [ ] `EvidenceTier` enum con valores A, B, C
- [ ] Cada tier tiene `disclaimer` property con texto honesto
- [ ] Importable desde `data_structures`

### Tarea 4: Tests de las nuevas estructuras

**Objetivo**: Tests unitarios que validen las nuevas estructuras y backward compatibility.

**Archivo afectado**: Crear `tests/test_financial_breakdown.py`

**Tests requeridos**:
```python
# 1. Scenario con monthly_loss_central=None (backward compat)
def test_scenario_backward_compat():
    s = Scenario(monthly_loss_min=100, monthly_loss_max=120, probability=0.5, description="test")
    assert s.format_loss_cop() uses monthly_loss_max  # 120

# 2. Scenario con monthly_loss_central
def test_scenario_with_central():
    s = Scenario(monthly_loss_min=100, monthly_loss_max=120, probability=0.5, 
                 description="test", monthly_loss_central=110)
    assert s.format_loss_cop() uses central  # 110

# 3. FinancialBreakdown instanciación completa
def test_financial_breakdown_full():
    fb = FinancialBreakdown(
        monthly_ota_commission_cop=5400000,
        ota_commission_basis="120 noches × $300K × 15%",
        ota_commission_source="onboarding",
        shift_savings_cop=540000,
        shift_percentage=0.10,
        shift_source="benchmark",
        ia_revenue_cop=2250000,
        ia_boost_percentage=0.05,
        ia_source="estimado",
        evidence_tier="C",
        disclaimer="Estimación basada en datos limitados."
    )
    assert fb.monthly_ota_commission_cop == 5400000

# 4. EvidenceTier disclaimers
def test_evidence_tier_disclaimers():
    assert "Google Analytics" in EvidenceTier.A.disclaimer
    assert "benchmarks" in EvidenceTier.B.disclaimer
    assert "limitados" in EvidenceTier.C.disclaimer

# 5. is_equilibrium_or_gain con central
def test_equilibrium_with_central():
    s_loss = Scenario(min=-100, max=-50, prob=0.5, desc="test", monthly_loss_central=-80)
    s_gain = Scenario(min=-100, max=10, prob=0.5, desc="test", monthly_loss_central=5)
    assert s_loss.is_equilibrium_or_gain() == False
    assert s_gain.is_equilibrium_or_gain() == True
```

**Criterios de aceptación**:
- [ ] Los 5 tests pasan
- [ ] Tests existentes del proyecto no se rompen (`python -m pytest tests/ -x -q`)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_scenario_backward_compat | `tests/test_financial_breakdown.py` | Pasa sin errores |
| test_scenario_with_central | `tests/test_financial_breakdown.py` | Pasa sin errores |
| test_financial_breakdown_full | `tests/test_financial_breakdown.py` | Pasa sin errores |
| test_evidence_tier_disclaimers | `tests/test_financial_breakdown.py` | Pasa sin errores |
| test_equilibrium_with_central | `tests/test_financial_breakdown.py` | Pasa sin errores |
| Suite completa | `tests/` | 0 failures, 0 errors |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_financial_breakdown.py -v
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -20
```

---

## Restricciones

- NO modificar `ScenarioCalculator` ni `FinancialCalculatorV2` — eso es FASE-B
- NO modificar `v4_diagnostic_generator.py` — eso es FASE-C/F
- NO modificar `main.py` — eso es FASE-G
- El campo `monthly_loss_central` debe ser `Optional` con default `None` para backward compatibility
- Los métodos existentes de `Scenario` deben funcionar idéntico si `monthly_loss_central=None`

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-A como ✅ Completada con fecha
2. **`06-checklist-implementacion.md`** — Marcar FASE-A como completada
3. **`09-documentacion-post-proyecto.md`** — Sección A: agregar nuevos dataclasses, Sección D: actualizar conteo de tests
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "Data Structures: FinancialBreakdown + Scenario.monthly_loss_central + EvidenceTier" \
    --archivos-mod "modules/commercial_documents/data_structures.py" \
    --archivos-nuevos "tests/test_financial_breakdown.py" \
    --tests "5"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `Scenario.monthly_loss_central` agregado con backward compat
- [ ] `FinancialBreakdown` dataclass creado con todos los campos
- [ ] `EvidenceTier` enum creado con disclaimers
- [ ] 5 tests nuevos pasan
- [ ] Suite completa de tests pasa sin errores
- [ ] `dependencias-fases.md` actualizado
- [ ] `log_phase_completion.py` ejecutado
