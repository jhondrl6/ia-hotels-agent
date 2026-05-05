# 05-prompt-inicio-sesion-fase-FIN-4A.md

**Fase**: FIN-4A — Investigación de Gaps de Integración  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-4 ✅ (validación E2E completada, issues documentados)  
**Bloquea a**: FIN-4B  
**Modo**: DIRECTO (código puro, 4 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

---

## Objetivo

Investigar y documentar con precisión quirúrgica los 4 puntos exactos donde el pipeline de v4complete pierde los datos generados por los módulos FIN-1A/B → CHAN-2. NO implementar fixes. Producto final: `evidence/FIN-4A/gap_analysis.md` con file:line exacto del código que requiere cambio.

---

## Contexto de Fases Anteriores

- **FIN-1A/B**: `FinancialEvidence`, `PrecisionValidator`, `EpistemicStatus` implementados y testeados ✅
- **FIN-2A/B**: `regional_adr_2026.json`, `RegionalADRResolver`, `FinancialFeatureFlags` con fallback chain ✅
- **FIN-3**: Templates con `monthly_loss_display`, `precision_warning`, `show_onboarding_cta` ✅
- **CHAN-1**: `ChannelEvidenceResolver` sin hardcodear WhatsApp ✅
- **CHAN-2**: `OpportunityScorer` con `channel_context` + multiplicadores ✅
- **FIN-4**: v4complete Hotel Castilla Real — 4 issues documentados en `evidence/FIN-4/validation_report.md` ❌

### Issue Tracker (de FIN-4)

| ID | Issue | Severidad |
|----|-------|:---------:|
| **GAP-1** | ADR $300K legacy persiste (`input_data.adr_cop = 300000` en `financial_scenarios.json`) | CRÍTICO |
| **GAP-2** | `opportunity_scores` calculados en template pero NO en `v4_complete_report.json` | ALTO |
| **GAP-3** | `channel_context` calculado pero NO en `v4_complete_report.json` | ALTO |
| **GAP-4** | `precision_tier` + `can_show_exact_money` no aparecen en ningún JSON de output | MEDIO |

---

## Tareas

### T1: Trazar GAP-1 — ¿Por qué ADR no usa feature flags regionales?

**Objetivo**: Confirmar si `FinancialFeatureFlags.from_env()` lee las env vars `FINANCIAL_REGIONAL_ADR_ENABLED` y `FINANCIAL_REGIONAL_ADR_MODE`.

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar lectura de env vars en el flag
export FINANCIAL_REGIONAL_ADR_ENABLED=true
export FINANCIAL_REGIONAL_ADR_MODE=active
./venv/Scripts/python.exe -c "
from modules.financial_engine.feature_flags import FinancialFeatureFlags, RolloutMode
flags = FinancialFeatureFlags.from_env()
print(f'enabled={flags.regional_adr_enabled}')
print(f'mode={flags.regional_adr_mode}')
print(f'mode.value={flags.regional_adr_mode.value}')
print(f'should_use_regional(caribe)={flags.should_use_regional_for(\"caribe\")}')
print(f'should_use_regional(eje_cafetero)={flags.should_use_regional_for(\"eje_cafetero\")}')
print(f'is_active={flags.regional_adr_mode == RolloutMode.ACTIVE}')
"
```

**Si flags OK**: Trazar quién llama al `ADRResolutionWrapper` y si le pasa `feature_flags`. Verificar qué código genera `financial_scenarios.json.input_data.adr_cop`.

```bash
# Buscar dónde se setea input_data.adr_cop en la generación de financial_scenarios.json
grep -rn "input_data\|adr_cop.*300000\|adr_resolution_wrapper\|ADRResolutionWrapper" \
    modules/financial_engine/harness_handlers.py \
    modules/financial_engine/calculator_v2.py \
    modules/financial_engine/scenario_calculator.py 2>/dev/null
```

**Entregable T1**: Bloque markdown en `gap_analysis.md` con:
- Si `from_env()` lee env vars correctamente (SÍ/NO)
- Qué función/archivo:línea setea `input_data.adr_cop = 300000`
- Si esa función tiene acceso a `FinancialFeatureFlags` o `ADRResolutionWrapper`

---

### T2: Trazar GAP-2 — ¿Dónde se construye v4_complete_report.json?

**Objetivo**: Encontrar el código que escribe `v4_complete_report.json` y verificar si tiene acceso a `opportunity_scores`.

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Buscar dónde se escribe v4_complete_report.json
grep -rn "v4_complete_report\.json\|opportunity_scores.*report\|phase_3_scenarios" \
    modules/ main.py 2>/dev/null | grep -v __pycache__ | grep -v ".pyc" | grep -v "test_"
```

**Entregable T2**: Bloque markdown con:
- Archivo:línea que escribe `v4_complete_report.json`
- Campos que YA incluye (ej: `coherence_score`, `financial_data`)
- Si `opportunity_scores` está disponible en ese scope (el caller de `generate()` tiene el DiagnosticSummary con los scores?)
- Dónde se obtendrían los `opportunity_scores` para inyectarlos

---

### T3: Trazar GAP-3 — ¿Dónde está channel_context después de resolverse?

**Objetivo**: Confirmar que `_resolve_channel_context()` en `v4_diagnostic_generator.py:2741` retorna datos válidos (no None ni vacío), y trazar por qué no llegan a `v4_complete_report.json`.

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar qué retorna _resolve_channel_context para el audit_result de Hotel Castilla Real
./venv/Scripts/python.exe -c "
import json
with open('output/v4_complete/v4_complete_report.json', encoding='utf-8') as f:
    report = json.load(f)

# Revisar si channel_context está en algún lugar del JSON
import pprint
pprint.pprint({k: type(v).__name__ for k, v in report.items()})
print()
# Buscar en phases
phases = report.get('phases', {})
print('phases keys:', list(phases.keys()))
print('phase_2_validation:', json.dumps(phases.get('phase_2_validation', {}), indent=2, ensure_ascii=False))
"
```

**Entregable T3**: Bloque markdown con:
- `channel_context` existe en algún lugar del report JSON (SÍ/NO/dónde)
- Si `_resolve_channel_context` se ejecutó para Hotel Castilla Real (verificar en logs o inferir)
- Qué función/archivo recibe el resultado y por qué no lo persiste al reporte

---

### T4: Trazar GAP-4 — ¿Dónde está precision_tier después de calcularse?

**Objetivo**: Encontrar dónde `PrecisionValidator` calcula `precision_tier` y `can_show_exact_money`, y por qué no se escriben a `financial_scenarios.json`.

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar qué exports tiene PrecisionValidator
grep -n "precision_tier\|can_show_exact\|PrecisionValidator\|class Precision" \
    modules/financial_engine/precision_validator.py 2>/dev/null

# Verificar si financial_scenarios.json tiene campo para precision_tier
./venv/Scripts/python.exe -c "
import json
with open('output/v4_complete/financial_scenarios.json', encoding='utf-8') as f:
    fs = json.load(f)
keys = list(fs.keys())
print('Keys in financial_scenarios.json:', keys)
print('Has precision_tier:', 'precision_tier' in fs)
print('Has can_show_exact_money:', 'can_show_exact_money' in fs)
"
```

**Entregable T4**: Bloque markdown con:
- `PrecisionValidator` está correctamente implementado (SÍ/NO)
- Qué función genera `financial_scenarios.json` y si llama al `PrecisionValidator`
- File:line exacto donde se DEBE agregar `precision_tier` y `can_show_exact_money` al JSON

---

## Producto Final

Archivo: `evidence/FIN-4A/gap_analysis.md`

Estructura requerida:
```markdown
# Gap Analysis — Financial Engine Integration

## GAP-1: ADR Legacy no usa feature flags
- **file:line**: {path}:{line}
- **función**: {nombre}
- **causa raíz**: {explicación}
- **fix requerido**: {1-2 líneas de qué cambiar}

## GAP-2: opportunity_scores en v4_complete_report.json
...

## GAP-3: channel_context en v4_complete_report.json
...

## GAP-4: precision_tier en financial_scenarios.json
...

## Resumen para FIN-4B
| GAP | Archivo a modificar | Tipo de cambio | Estimado líneas |
|-----|---------------------|:--------------:|:---------------:|
| 1 | ... | ... | ... |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |
| 4 | ... | ... | ... |
```

---

## Criterios de Completitud

- [ ] T1: GAP-1 trazado con file:line exacto en `gap_analysis.md`
- [ ] T2: GAP-2 trazado con file:line exacto en `gap_analysis.md`
- [ ] T3: GAP-3 confirmado con evidencia de report JSON
- [ ] T4: GAP-4 trazado con verificación de `PrecisionValidator`
- [ ] Tabla resumen con estimados para FIN-4B
- [ ] `gap_analysis.md` guardado en `evidence/FIN-4A/`
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- Máximo 60 iteraciones
- **NO modificar código** — solo investigación
- **NO ejecutar v4complete** — ya existe el output en `output/v4_complete/`
- Si un GAP no se puede resolver con el output existente → marcarlo como "REQUIERE REPLAY" y explicar por qué

---

## Post-Ejecución

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-4A \
    --desc "Investigación de gaps de integración — 4 GAPs trazados a file:line" \
    --archivos-nuevos "evidence/FIN-4A/" \
    --tests "0" \
    --check-manual-docs
```
