# FASE-CONFIG-3B: Extracción de Escenarios Financieros a YAML (CR-4 scenarios)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~46 iteraciones
**Dependencias:** FASE-CONFIG-3A (patrón YAML + pricing_calculator ya refactorizado)
**Fase siguiente:** FASE-CONFIG-4 o FASE-CONFIG-5 (en paralelo)

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 2 Grupo B + §HALLAZGO 3 Grupos E, H

### Hardcodes a Extraer (12 valores en 4 archivos)

| ID | Elemento | Archivo | Línea | Valor Actual |
|----|----------|---------|-------|-------------|
| H-14a | recovery_factor conservador | v4_proposal_generator.py | L524 | 0.15 |
| H-14b | recovery_factor realista | v4_proposal_generator.py | L486 | 0.20 |
| H-14c | recovery_factor optimista | v4_proposal_generator.py | L528 | 0.25 |
| H-17 | Scenario weights | v4_proposal_generator.py | L1101 | 0.70/0.20/0.10 |
| H-20 | degradation_rate | loss_projector.py | L65 | 0.02 |
| H-21 | OTA shifts | scenario_calculator.py | L178,243,286 | 0.05/0.10/0.20 |
| H-22 | ia_boost | scenario_calculator.py | L471 | 0.05 |
| N-01 | pain_ratio default | v4_proposal_generator.py | L204 | 0.20 |
| N-11 | SUPERPOSITION_FACTOR | financial_factors.py | L50 | 0.7 |
| N-11b | DEFAULTS dict (12 valores) | financial_factors.py | ~L20-48 | comision_ota, penalizacion, revpar, etc. |

---

## Tareas Específicas

### Tarea 1: Crear config/scenarios.yaml + config/financial_defaults.yaml

**config/scenarios.yaml:**
```yaml
version: "1.0.0"
recovery_factors:
  conservative: 0.15
  realistic: 0.20
  optimistic: 0.25
scenario_weights:
  conservative: 0.70
  realistic: 0.20
  optimistic: 0.10
degradation_rate: 0.02
ota_shift:
  minimal: 0.05
  moderate: 0.10
  optimistic: 0.20
ia_boost: 0.05
pain_ratio_default: 0.20
```

**config/financial_defaults.yaml:**
```yaml
version: "1.0.0"
superposition_factor: 0.7
factor_captura_aila: 0.70
comision_ota:
  min: 0.18
  base: 0.20
  max: 0.22
penalizacion_invisibilidad_ia: 0.05
revpar_cop: 197120
reservas_ota_proporcion: 0.65
reservas_directo_proporcion: 0.35
uso_ia_proporcion_min: 0.10
uso_ia_proporcion_max: 0.20
# ... resto de DEFAULTS de financial_factors.py
```

### Tarea 2: Refactorizar scenario_calculator.py
- H-21: Reemplazar `minimal_improvement=0.05`/`moderate_shift=0.10`/`optimistic_shift=0.20` con carga de `scenarios.yaml → ota_shift`
- H-22: Reemplazar `_get_ia_boost_percentage()` return 0.05 con carga de YAML → `ia_boost`
- Mantener TODOs como recordatorio (GA4 integration futura)
- Método `_load_scenario_config()` con cache

### Tarea 3: Refactorizar loss_projector.py + financial_factors.py + v4_proposal_generator.py
- **loss_projector.py L65 (H-20):** degradation_rate → `scenarios.yaml`
- **financial_factors.py L50 (N-11):** SUPERPOSITION_FACTOR → `financial_defaults.yaml`
- **financial_factors.py ~L20-48 (N-11b):** DEFAULTS dict → `financial_defaults.yaml`
- **v4_proposal_generator.py L204 (N-01):** pain_ratio default → `scenarios.yaml`
- **v4_proposal_generator.py L486,524,528 (H-14):** recovery_factors → `scenarios.yaml`
- **v4_proposal_generator.py L1101 (H-17):** scenario_weights → `scenarios.yaml`

### Tarea 4: Tests
- Test: scenarios.yaml presente → todos los módulos usan valores de YAML
- Test: financial_defaults.yaml presente → DEFAULTS de YAML
- Test: YAML ausente → fallback a defaults documentados
- Test: YAML corrupto → error de schema
- Test: scenario_calculator con valores personalizados de ota_shift
- Test: v4_proposal_generator con recovery_factors personalizados
- Verificar: `grep -rn "0\.05\|0\.10\|0\.20" modules/financial_engine/scenario_calculator.py` no retorna hardcodes

---

## Archivos Involucrados

| Archivo | Tipo | Hardcodes |
|---------|------|-----------|
| `config/scenarios.yaml` | NUEVO | H-14, H-17, H-20, H-21, H-22, N-01 |
| `config/financial_defaults.yaml` | NUEVO | N-11, N-11b |
| `modules/financial_engine/scenario_calculator.py` | MODIFICAR | H-21, H-22 |
| `modules/financial_engine/loss_projector.py` | MODIFICAR | H-20 |
| `modules/utils/financial_factors.py` | MODIFICAR | N-11, N-11b |
| `modules/commercial_documents/v4_proposal_generator.py` | MODIFICAR | H-14, H-17, N-01 |

---

## Criterios de Completitud

- [ ] `config/scenarios.yaml` creado + schema validado
- [ ] `config/financial_defaults.yaml` creado + schema validado
- [ ] H-14a/b/c, H-17, H-20, H-21, H-22 → YAML (6 hardcodes)
- [ ] N-01, N-11, N-11b → YAML (3 hardcodes)
- [ ] Tests: ambos YAML presentes, ausentes, corruptos
- [ ] scenario_calculator.py sin hardcodes de shift/boost
- [ ] financial_factors.py sin DEFAULTS hardcodeados

---

## Restricciones

- **NO modificar** pricing_calculator.py (ya refactorizado en CONFIG-3A)
- **NO modificar** templates
- **NO ejecutar** v4complete
- **NO crear** YAML de pricing (ya existe)
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-3b
cp config/scenarios.yaml config/financial_defaults.yaml evidence/fase-config-3b/
cp modules/financial_engine/scenario_calculator.py evidence/fase-config-3b/
cp modules/financial_engine/loss_projector.py evidence/fase-config-3b/
cp modules/utils/financial_factors.py evidence/fase-config-3b/

venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-3B     --desc "Extracción de escenarios financieros: recovery_factors, weights, degradation, OTA shifts, ia_boost, pain_ratio, defaults financieros"     --archivos-nuevos "config/scenarios.yaml,config/financial_defaults.yaml"     --archivos-mod "modules/financial_engine/scenario_calculator.py,modules/financial_engine/loss_projector.py,modules/utils/financial_factors.py,modules/commercial_documents/v4_proposal_generator.py"     --tests "6"     --check-manual-docs
```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-4.md siguiendo .agents/workflows/phased_project_executor.md
```
