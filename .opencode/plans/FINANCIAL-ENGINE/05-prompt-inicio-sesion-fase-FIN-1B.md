# 05-prompt-inicio-sesion-fase-FIN-1B

**Fase**: FIN-1B — NoDefaultsValidator Ampliado + Precision Tier  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-1A ✅ (FinancialEvidence dataclass existe)  
**Bloquea a**: FIN-2A  

---

## Objetivo

Extender `NoDefaultsValidator` para clasificar fuentes con granularidad epistémica (no solo `verified`/`unverified`) y crear la lógica de `financial_precision_tier` que determine cómo se debe presentar cada cálculo financiero.

---

## Contexto de Fase Anterior (FIN-1A ✅)

FIN-1A creó:
- `modules/financial_engine/financial_evidence.py` con `FinancialEvidence`, `FieldEvidence`, `EpistemicStatus`, `PrecisionTier`, `build_financial_evidence()`
- `FinancialScenario.financial_evidence` como campo opcional
- `ScenarioCalculator` ya construye `FinancialEvidence` en output

Ahora necesitamos que el validator use estas clasificaciones.

---

## Tareas

### T1: Investigar `NoDefaultsValidator` actual

Leer `modules/financial_engine/no_defaults_validator.py` completo. Entender:
- `SUSPECT_SOURCES` set actual (línea 52-54)
- `ValidationWarning` dataclass (línea 43-48)
- `source_reliability` property (línea 80-82)
- `NoDefaultsValidationResult` estructura
- Cómo se usa en `calculator_v2.py` y `main.py`

### T2: Ampliar clasificación de fuentes

**Archivo**: `modules/financial_engine/no_defaults_validator.py`

Agregar:

```python
from modules.financial_engine.financial_evidence import EpistemicStatus, FieldEvidence

# Reemplazar SUSPECT_SOURCES binario con mapeo granular
SOURCE_EPISTEMIC_MAP: Dict[str, EpistemicStatus] = {
    "user_provided": EpistemicStatus.MEASURED,
    "web_scraping": EpistemicStatus.OBSERVED,
    "regional_v410": EpistemicStatus.REGIONAL_BENCHMARK,
    "legacy_hardcode": EpistemicStatus.DEFAULTED,
    "default": EpistemicStatus.DEFAULTED,
    "unknown": EpistemicStatus.DEFAULTED,
    "hardcoded": EpistemicStatus.DEFAULTED,
    "estimated": EpistemicStatus.DEFAULTED,
    "simulated": EpistemicStatus.SIMULATED,
}

def classify_source(source: str) -> EpistemicStatus:
    """Clasifica un source string en su estado epistémico."""
    return SOURCE_EPISTEMIC_MAP.get(source.lower(), EpistemicStatus.DEFAULTED)

def determine_precision_tier(
    adr_status: EpistemicStatus,
    occupancy_status: EpistemicStatus,
    channel_status: EpistemicStatus,
) -> str:
    """Determina el tier de precisión por peor fuente."""
    statuses = {adr_status, occupancy_status, channel_status}
    if EpistemicStatus.DEFAULTED in statuses or EpistemicStatus.SIMULATED in statuses:
        return "C"
    if EpistemicStatus.REGIONAL_BENCHMARK in statuses:
        return "B"
    if EpistemicStatus.CONFLICT in statuses:
        return "C"
    return "A"
```

Mantener `SUSPECT_SOURCES` por compatibilidad, pero marcarlo con comment `# LEGACY — usar SOURCE_EPISTEMIC_MAP`.

Agregar a `NoDefaultsValidationResult`:
```python
precision_tier: str = "C"  # Default conservador
field_epistemic: Dict[str, EpistemicStatus] = field(default_factory=dict)
can_show_exact_money: bool = False
```

### T3: Crear `PrecisionValidator` helper

**Archivo**: `modules/financial_engine/precision_validator.py` (NUEVO)

```python
class PrecisionValidator:
    """Valida precisión financiera y determina reglas de render."""

    @staticmethod
    def validate(
        adr_cop: float, adr_source: str,
        occupancy_rate: float, occupancy_source: str,
        direct_channel_pct: float, channel_source: str,
    ) -> NoDefaultsValidationResult:
        """Valida campos y determina tier + can_show_exact."""
        # 1. Clasificar cada fuente
        adr_status = classify_source(adr_source)
        occ_status = classify_source(occupancy_source)
        ch_status = classify_source(channel_source)

        # 2. Detectar bloques (None, 0, missing)
        blocks = []
        if not adr_cop or adr_cop <= 0:
            blocks.append(ValidationBlock(...))
        # ... mismo para occupancy y channel

        # 3. Determinar tier y reglas
        tier = determine_precision_tier(adr_status, occ_status, ch_status)
        can_show = all(
            s in {EpistemicStatus.MEASURED, EpistemicStatus.OBSERVED}
            for s in [adr_status, occ_status, ch_status]
        )

        return NoDefaultsValidationResult(
            can_calculate=len(blocks) == 0,
            blocks=blocks,
            precision_tier=tier,
            field_epistemic={
                "adr_cop": adr_status,
                "occupancy_rate": occ_status,
                "direct_channel_percentage": ch_status,
            },
            can_show_exact_money=can_show,
        )
```

### T4: Tests unitarios

**Archivo**: `tests/financial_engine/test_no_defaults_precision.py` (NUEVO)

Mínimo 8 tests:
1. `test_classify_source_user_provided` → MEASURED
2. `test_classify_source_web_scraping` → OBSERVED
3. `test_classify_source_regional_v410` → REGIONAL_BENCHMARK
4. `test_classify_source_legacy_hardcode` → DEFAULTED
5. `test_precision_tier_a_all_measured` → Tier A
6. `test_precision_tier_c_with_defaulted` → Tier C
7. `test_can_show_exact_true_all_measured` → True
8. `test_precision_validator_integration` → Validación completa con `PrecisionValidator.validate()`

---

## Criterios de Completitud

- [ ] `SOURCE_EPISTEMIC_MAP` existe en `no_defaults_validator.py`
- [ ] `classify_source()` y `determine_precision_tier()` funcionan
- [ ] `NoDefaultsValidationResult` tiene `precision_tier`, `field_epistemic`, `can_show_exact_money`
- [ ] `modules/financial_engine/precision_validator.py` existe
- [ ] `SUSPECT_SOURCES` original se mantiene (compatibilidad)
- [ ] `tests/financial_engine/test_no_defaults_precision.py` ≥8 tests pasando
- [ ] Tests existentes de `NoDefaultsValidator` sin regresiones

---

## Restricciones

- Máximo 60 iteraciones
- **NO eliminar `SUSPECT_SOURCES`** (compatibilidad hacia atrás)
- **NO modificar templates ni generators** (FIN-3)
- **NO tocar `feature_flags.py`** (FIN-2B)

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-1B \
    --desc "NoDefaultsValidator ampliado + precision tier por peor fuente" \
    --archivos-nuevos "modules/financial_engine/precision_validator.py,tests/financial_engine/test_no_defaults_precision.py" \
    --archivos-mod "modules/financial_engine/no_defaults_validator.py" \
    --tests "8" \
    --check-manual-docs
```
