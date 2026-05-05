# 05-prompt-inicio-sesion-fase-FIN-4B.md

**Fase**: FIN-4B — Implementación de Integración Pipeline  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-4A ✅ (gap analysis completado en `evidence/FIN-4A/gap_analysis.md`)  
**Bloquea a**: RELEASE  
**Modo**: DIRECTO (código puro, 4 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

---

## Objetivo

Implementar los 4 fixes documentados en `evidence/FIN-4A/gap_analysis.md` para que:
1. `financial_scenarios.json` use ADR regional (no $300K legacy) cuando feature flags están activos
2. `v4_complete_report.json` incluya `opportunity_scores` con channel_multiplier
3. `v4_complete_report.json` incluya `channel_context` con dominant_channel y confidence
4. `financial_scenarios.json` incluya `precision_tier` y `can_show_exact_money`

---

## Pre-Flight (OBLIGATORIO antes de cualquier código)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Cargar el gap analysis
if [ -f evidence/FIN-4A/gap_analysis.md ]; then
    echo "✅ gap_analysis.md encontrado"
    cat evidence/FIN-4A/gap_analysis.md | head -80
else
    echo "❌ ERROR: gap_analysis.md no encontrado. Ejecutar FIN-4A primero."
    exit 1
fi
```

---

## Tareas

### T1: Fix GAP-1 — ADR regional vía feature flags

**Archivo afectado**: El identificado en `gap_analysis.md` GAP-1

**Acción**: Según el gap analysis:
- `FinancialFeatureFlags.from_env()` **SÍ** lee env vars correctamente — **no modificar**
- El bug real es **case-sensitivity** en `should_use_regional_for()`: `"Eje Cafetero"` (title case del DOM) no matchea `"eje_cafetero"` (lowercase en `validated_regions`)
- Fix: normalizar comparación en `feature_flags.py:should_use_regional_for()` (ej: `region.lower()`)
- Alternativa: normalizar la región cuando se extrae del hotel (onboarding/detector)

**Verificación unitaria** (ANTES de cualquier v4complete):
```bash
./venv/Scripts/python.exe -c "
import os
os.environ['FINANCIAL_REGIONAL_ADR_ENABLED'] = 'true'
os.environ['FINANCIAL_REGIONAL_ADR_MODE'] = 'active'

from modules.financial_engine.adr_resolution_wrapper import ADRResolutionWrapper
from modules.financial_engine.feature_flags import FinancialFeatureFlags

flags = FinancialFeatureFlags.from_env()
wrapper = ADRResolutionWrapper(feature_flags=flags)

# Test 1: lowercase (ya funciona)
result = wrapper.resolve(region='eje_cafetero')
print(f'Lowercase ADR: {result.adr_cop}, Source: {result.source}')

# Test 2: title case (el bug real — debe funcionar tras el fix)
result2 = wrapper.resolve(region='Eje Cafetero')
print(f'Title case ADR: {result2.adr_cop}, Source: {result2.source}')
print(f'Case insensitive fix: {result2.adr_cop != 300000}')
"
```

**Criterio**: `result2.adr_cop != 300000` y `result2.source` contiene `regional` o `benchmark`.

---

### T2: Fix GAP-2 — opportunity_scores en v4_complete_report.json

**Archivo afectado**: `main.py:2944` (el dict `report` se construye en `main.py:2859-2944` y se escribe en `2946-2948`)

**Acción**: Inyectar `opportunity_scores` (ya calculados por `v4_diagnostic_generator._compute_opportunity_scores()`) en el JSON de reporte.

**Estrategia**: 
- `_compute_opportunity_scores()` ya existe en `v4_diagnostic_generator.py:2848` y se ejecuta durante la generación del diagnóstico
- Lo que falta es **persistir su resultado** al dict `report` de `main.py:2944`
- Opción A: que `diagnostic_gen.generate()` retorne un dict con `opportunity_scores` que se pase al report builder
- Opción B: llamar `diagnostic_gen._compute_opportunity_scores()` desde `main.py` y agregar al dict `report`
- Cada score debe incluir: `brecha_id`, `brecha_name`, `severity_score`, `effort_score`, `impact_score`, `total_score`, `base_total_score`, `channel_multiplier`, `channel_reason`, `estimated_monthly_cop`, `rank`

**Verificación unitaria**:
```bash
./venv/Scripts/python.exe -c "
import json
# Verificar que el campo existe en el schema del report
# (test unitario sin v4complete)
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
gen = V4DiagnosticGenerator()
# Verificar que _compute_opportunity_scores es accesible
assert hasattr(gen, '_compute_opportunity_scores') or hasattr(gen, 'get_opportunity_scores'), \
    'opportunity_scores must be accessible'
print('✅ T2: API verificada')
"
```

---

### T3: Fix GAP-3 — channel_context en v4_complete_report.json

**Archivo afectado**: `main.py:2944` — mismo punto de fuga que GAP-2. `_resolve_channel_context()` se ejecuta internamente en `v4_diagnostic_generator.py:2845` pero su resultado nunca se persiste al JSON.

**Acción**: Inyectar `channel_context` (ya resuelto por `v4_diagnostic_generator._resolve_channel_context()`) en el JSON de reporte.

**Campos requeridos**:
```json
{
  "channel_context": {
    "dominant_channel": "whatsapp|direct|social|unknown",
    "confidence": "high|medium|low",
    "channel_weights": {"whatsapp": 1.0, "direct": 0.8, ...},
    "evidence_sources": ["web_cta_detected", "gbp_whatsapp_button", ...]
  }
}
```

**Verificación unitaria**:
```bash
./venv/Scripts/python.exe -c "
import json
# Verificar que _resolve_channel_context es accesible
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
gen = V4DiagnosticGenerator()
assert hasattr(gen, '_resolve_channel_context') or hasattr(gen, 'resolve_channel_context'), \
    'channel_context resolution must be accessible'
print('✅ T3: API verificada')
"
```

---

### T4: Fix GAP-4 — precision_tier en financial_scenarios.json

**Archivo afectado**: El identificado en `gap_analysis.md` GAP-4

**Acción**: Agregar `precision_tier` y `can_show_exact_money` al JSON output de escenarios financieros.

**Estrategia**:
- `FinancialEvidence.to_dict()` (`financial_evidence.py:94-103`) ya incluye `financial_precision_tier` y `can_show_exact_money`
- **Opción preferida**: invocar `FinancialEvidence.to_dict()` en `main.py:1876-1896` (donde se escribe `financial_scenarios.json`) y agregar su resultado al dict
- **Alternativa**: llamar `PrecisionValidator.validate()` directamente desde `main.py` y agregar los campos manualmente
- Campos requeridos en `financial_scenarios.json`:
```json
{
  "precision_tier": "A|B|C",
  "can_show_exact_money": true|false
}
```

**Verificación unitaria**:
```bash
./venv/Scripts/python.exe -c "
from modules.financial_engine.precision_validator import PrecisionValidator
from modules.financial_engine.financial_evidence import FinancialEvidence, EpistemicStatus

evidence = FinancialEvidence(
    adr_source='regional_v410', adr_epistemic=EpistemicStatus.REFERENCED,
    rooms_source='hotel_data', rooms_epistemic=EpistemicStatus.ESTIMATED,
    occupancy_source='default', occupancy_epistemic=EpistemicStatus.DEFAULTED,
)
validator = PrecisionValidator()
result = validator.validate(evidence)
print(f'Tier: {result.precision_tier}')
print(f'Can show exact: {result.can_show_exact_money}')
assert result.precision_tier in ('A', 'B', 'C'), f'Tier inválido: {result.precision_tier}'
assert isinstance(result.can_show_exact_money, bool), 'can_show_exact debe ser bool'
print('✅ T4: PrecisionValidator funcional')
"
```

---

## Tests Obligatorios

| Test archivo | Cantidad | Criterio |
|-------------|:--------:|----------|
| `tests/financial_engine/test_financial_4b_integration.py` | 8 | 2 tests por GAP: unitario + integración |

### Estructura sugerida de tests:

```python
# test_financial_4b_integration.py

def test_gap1_should_use_regional_is_case_insensitive():
    """"Eje Cafetero" debe matchear contra validated_regions "eje_cafetero"."""
    ...

def test_gap1_adr_not_300k_legacy_with_flags():
    """Con FINANCIAL_REGIONAL_ADR_ENABLED=true, ADR ≠ 300000."""
    ...

def test_gap2_report_includes_opportunity_scores():
    """v4_complete_report builder acepta e incluye opportunity_scores."""
    ...

def test_gap2_opportunity_scores_have_channel_multiplier():
    """Cada score incluye channel_multiplier y channel_reason."""
    ...

def test_gap3_report_includes_channel_context():
    """v4_complete_report builder acepta e incluye channel_context."""
    ...

def test_gap3_channel_context_has_required_fields():
    """channel_context incluye dominant_channel, confidence, channel_weights."""
    ...

def test_gap4_financial_scenarios_has_precision_tier():
    """financial_scenarios.json incluye precision_tier."""
    ...

def test_gap4_can_show_exact_money_is_boolean():
    """can_show_exact_money es bool."""
    ...
```

---

## Criterios de Completitud

- [ ] T1 ✅: `ADRResolutionWrapper.resolve()` con flags activos retorna ADR ≠ $300K
- [ ] T2 ✅: `v4_complete_report.json` builder acepta campo `opportunity_scores`
- [ ] T3 ✅: `v4_complete_report.json` builder acepta campo `channel_context`
- [ ] T4 ✅: `financial_scenarios.json` builder acepta `precision_tier` y `can_show_exact_money`
- [ ] Tests: 8 nuevos, 0 regresiones
- [ ] `log_phase_completion.py` ejecutado
- [ ] Plan actualizado: checklist maestro marcado

---

## Restricciones

- Máximo 60 iteraciones
- **NO ejecutar v4complete** — solo código + tests unitarios
- Respetar los file:line del `gap_analysis.md` de FIN-4A
- Si un fix requiere cambio de arquitectura → documentarlo como decisión de negocio pendiente
- Los archivos que reciben `opportunity_scores`/`channel_context` deben tratarlos como **opcionales** (None-safe) para no romper flujos existentes

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Ejecutar tests
./venv/Scripts/python.exe -m pytest tests/financial_engine/test_financial_4b_integration.py -v

# Log de fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-4B \
    --desc "Integración pipeline: 4 GAPs cableados al output (ADR regional, opportunity_scores, channel_context, precision_tier)" \
    --archivos-nuevos "tests/financial_engine/test_financial_4b_integration.py" \
    --tests "8" \
    --check-manual-docs
```
