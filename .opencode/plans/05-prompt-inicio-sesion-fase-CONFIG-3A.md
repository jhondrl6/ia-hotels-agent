# FASE-CONFIG-3A: Extracción de Pricing a YAML (CR-4 pricing)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~42 iteraciones
**Dependencias:** FASE-CONFIG-2 (patrón de carga YAML establecido)
**Fase siguiente:** FASE-CONFIG-3B

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 2, Grupo B + §HALLAZGO 3, Grupo H

### Problema

El sistema de pricing está completamente hardcodeado. Cambios comerciales requieren editar código Python:

| ID | Elemento | Archivo | Línea | Valor |
|----|----------|---------|-------|-------|
| H-19 | TIER_CONFIG completo | pricing_calculator.py | L47-69 | 3 tiers con percentages, min/max |
| N-12 | GATE ratios | pricing_calculator.py | L72-74 | 0.03 / 0.06 / 0.045 |
| H-18a | min_price BOUTIQUE | pricing_calculator.py | L52 | 1,200,000 |
| H-18b | Pricing floor fallback | v4_proposal_generator.py | L1104 | 800,000 (INCONSISTENTE con H-18a) |

**Inconsistencia H-18b:** `TIER_CONFIG` define `min_price: 1_200_000` para BOUTIQUE, pero `_estimate_monthly_investment()` usa `800000` como floor. Son DOS hardcodes distintos para "precio mínimo" en DOS archivos. Inconsistencia comercial.

---

## Tareas Específicas

### Tarea 1: Crear config/pricing.yaml
Estructura:
```yaml
# config/pricing.yaml
version: "1.0.0"
description: "Configuración de pricing y tiers para cálculo de paquetes"

tiers:
  boutique:
    percentage: 0.035
    min_price: 1200000
    max_price: 2500000
    description: "Hoteles boutique y pequeños"
  premium:
    percentage: 0.045
    min_price: 2500000
    max_price: 5000000
    description: "Hoteles premium y medianos"
  luxury:
    percentage: 0.06
    min_price: 5000000
    max_price: 12000000
    description: "Hoteles de lujo y grandes"

gates:
  min_ratio: 0.03
  max_ratio: 0.06
  ideal_ratio: 0.045

packages:
  monthly_default: 1200000   # COP
  setup_fee_default: 2500000  # COP
  floor_price: 1200000        # UNIFICADO: antes era 800K en v4_proposal_generator.py
```

**Decisión H-18b:** El floor canónico es 1,200,000 (TIER_CONFIG). El valor 800,000 en `v4_proposal_generator.py` era un remanente inconsistente.

### Tarea 2: Refactorizar pricing_calculator.py
- Reemplazar `TIER_CONFIG` hardcodeado (L47-69) con carga de `config/pricing.yaml → tiers`
- Reemplazar `GATE_MIN_RATIO/MAX_RATIO/IDEAL_RATIO` (L72-74) con carga de YAML → `gates`
- Implementar `_load_pricing_config()` con:
  - Carga de YAML + cache en módulo
  - Schema validation (tipos, rangos)
  - Fallback a defaults hardcodeados SOLO si YAML no existe (backwards compatibility)
- Log warning si se usa fallback

### Tarea 3: Resolver H-18b + refactorizar v4_proposal_generator.py
- Reemplazar `800000` en `_estimate_monthly_investment()` (L1104) con carga de `pricing.yaml → packages.floor_price`
- O mejor: delegar a `pricing_calculator.py` que ya tendrá el floor correcto
- Verificar que NO queden referencias a 800,000 como floor en ningún archivo

### Tarea 4: Tests
- Test: `pricing.yaml` presente → TIER_CONFIG usa valores de YAML
- Test: `pricing.yaml` ausente → fallback a defaults (backwards compatibility)
- Test: `pricing.yaml` corrupto → error de schema descriptivo
- Test: floor_price unificado (1.2M) en TODOS los cálculos de pricing
- Test: `_estimate_monthly_investment()` usa floor de YAML, no hardcode
- Verificar con `grep -rn "800000" modules/` que no queden remanentes

---

## Archivos Involucrados

| Archivo | Tipo | Hardcodes |
|---------|------|-----------|
| `config/pricing.yaml` | NUEVO | H-18a, H-18b, H-19, N-12 |
| `modules/financial_engine/pricing_calculator.py` | MODIFICAR | H-19 (L47-69), N-12 (L72-74), H-18a (L52) |
| `modules/commercial_documents/v4_proposal_generator.py` | MODIFICAR | H-18b (L1104) |

---

## Criterios de Completitud

- [x] `config/pricing.yaml` creado con schema validado
- [x] H-19: TIER_CONFIG → YAML (pricing_calculator.py ya no tiene el dict hardcodeado)
- [x] N-12: GATE ratios → YAML
- [x] H-18a: min_price BOUTIQUE → YAML
- [x] H-18b: Inconsistencia 800K vs 1.2M RESUELTA (floor unificado en YAML)
- [x] `grep -rn "800000" modules/` no retorna resultados en lógica de pricing
- [x] Tests: YAML presente, ausente, corrupto, floor unificado
- [x] Backwards compatibility: sin YAML, usa defaults (no crashea)

**Estado: ✅ COMPLETADA — 2026-04-30**
**Tests:** 407 passed (38 pricing_calculator + 369 otros módulos)

---

## Restricciones

- **NO modificar** scenario_calculator.py (eso es FASE-CONFIG-3B)
- **NO modificar** templates
- **NO ejecutar** v4complete
- **NO crear** otros YAML (solo pricing.yaml)
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-3a
cp config/pricing.yaml evidence/fase-config-3a/
cp modules/financial_engine/pricing_calculator.py evidence/fase-config-3a/
cp modules/commercial_documents/v4_proposal_generator.py evidence/fase-config-3a/

venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-3A     --desc "Extracción de pricing a config/pricing.yaml: TIER_CONFIG, GATE ratios, floor_price unificado (1.2M). Resuelta inconsistencia H-18b."     --archivos-nuevos "config/pricing.yaml"     --archivos-mod "modules/financial_engine/pricing_calculator.py,modules/commercial_documents/v4_proposal_generator.py"     --tests "5"     --check-manual-docs
```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-3B.md siguiendo .agents/workflows/phased_project_executor.md
```
