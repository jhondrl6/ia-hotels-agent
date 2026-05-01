# FASE-CONFIG-8: Suite de Tests de Regresión + Blindaje

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~46 iteraciones
**Dependencias:** FASE-CONFIG-7 (v4complete ya verificó que los fixes funcionan)
**Fase siguiente:** FASE-RELEASE-4.38.0

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §Plan de Implementación Corregido, FASE-CONFIG-7 original (líneas 403-405)

Después de 7 fases de implementación y validación E2E, esta fase blinda el sistema con tests exhaustivos para prevenir regresiones. El objetivo es garantizar que los hardcodes NO vuelvan a aparecer.

---

## Tareas Específicas

### Tarea 1: Tests de migración por archivo YAML
Crear tests que verifiquen CADA valor se lee de YAML, no de hardcode:

**test_config_pricing.py:**
- Test: `pricing.yaml → tiers.boutique.min_price == 1200000`
- Test: `pricing.yaml → gates.min_ratio == 0.03`
- Test: `pricing_calculator.py` NO contiene `TIER_CONFIG = {` (dict hardcodeado)
- Test: `pricing_calculator.py` NO contiene `GATE_MIN_RATIO = 0.03`

**test_config_scenarios.py:**
- Test: `scenarios.yaml → recovery_factors.conservative == 0.15`
- Test: `scenarios.yaml → ota_shift.minimal == 0.05`
- Test: `scenario_calculator.py` NO contiene `minimal_improvement = 0.05`
- Test: `scenario_calculator.py` NO contiene `moderate_shift = 0.10`

**test_config_fallbacks.py:**
- Test: `fallbacks.yaml → scores.benchmark_score == 58`
- Test: `v4_proposal_generator.py` NO contiene `benchmark_score = 58`
- Test: `v4_diagnostic_generator.py` NO contiene `voice_readiness = '0'`

**test_config_commercial.py:**
- Test: `commercial.yaml → roi.cap == 5.0`
- Test: `commercial.yaml → guarantees.satisfaction_days == 90`
- Test: `v4_proposal_generator.py` NO contiene `def _build_guarantees_section`
- Test: `propuesta_v6_template.md` NO contiene `90 días` literal (usa placeholder)

**test_config_benchmarks.py:**
- Test: `regional_benchmarks.yaml → regions.eje_cafetero.pain_narratives.no_whatsapp_visible == 0.20`
- Test: `v4_diagnostic_generator.py` NO contiene `'no_whatsapp_visible': 0.20`

### Tarea 2: Tests de fallback y schema
- **test_config_fallback.py:** YAML ausente → usa defaults documentados (no crashea)
- **test_config_fallback.py:** YAML presente pero con campo faltante → error claro
- **test_config_schema.py:** YAML con valor inválido (string en vez de float) → error descriptivo
- **test_config_schema.py:** YAML con valor fuera de rango → warning o error
- **test_config_integration.py:** Cambiar YAML → reiniciar módulo → valor reflejado

### Tarea 3: Update doctor.py
- Agregar verificación de integridad de config files en `doctor.py --status`:
  - Listar todos los YAML en config/
  - Validar schema de cada uno
  - Reportar archivos faltantes o corruptos
- Agregar sección "Config Files" en SYSTEM_STATUS.md

### Tarea 4: Ejecutar todas las validaciones
```bash
# Suite completa de tests
venv/Scripts/python.exe -m pytest tests/ -x --tb=short -q

# Validaciones del ecosistema
venv/Scripts/python.exe scripts/run_all_validations.py --quick
venv/Scripts/python.exe scripts/doctor.py --status

# Verificar que no hay hardcodes residuales
grep -rn "= 58\|= 50\|= '70'\|= '0'" modules/commercial_documents/ | grep -v "#\|test_\|YAML"
```
- Todos los tests deben pasar
- run_all_validations.py --quick debe mostrar 4/4
- doctor.py --status debe listar todos los YAML como healthy

---

## Archivos Involucrados

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `tests/config/test_config_pricing.py` | NUEVO | Tests de migración pricing |
| `tests/config/test_config_scenarios.py` | NUEVO | Tests de migración scenarios |
| `tests/config/test_config_fallbacks.py` | NUEVO | Tests de migración fallbacks |
| `tests/config/test_config_commercial.py` | NUEVO | Tests de migración commercial |
| `tests/config/test_config_benchmarks.py` | NUEVO | Tests de migración benchmarks |
| `tests/config/test_config_fallback.py` | NUEVO | Tests de fallback (YAML ausente/corrupto) |
| `tests/config/test_config_schema.py` | NUEVO | Tests de schema validation |
| `tests/config/test_config_integration.py` | NUEVO | Tests de integración |
| `scripts/doctor.py` | MODIFICAR | Agregar verificación de config files |

---

## Criterios de Completitud

- [ ] Tests de migración para los 6 archivos YAML
- [ ] Tests de fallback (YAML ausente → defaults)
- [ ] Tests de schema (YAML inválido → error)
- [ ] doctor.py --status incluye sección "Config Files"
- [ ] Todos los tests pasan (0 regresiones)
- [ ] run_all_validations.py --quick: 4/4
- [ ] Cobertura: >= 80% de los 31 hardcodes tienen test de migración
- [ ] grep de hardcodes en modules/ retorna 0 resultados (o solo comentarios/tests)

---

## Restricciones

- **NO modificar** lógica de negocio
- **NO modificar** YAML config (solo leerlos en tests)
- **NO ejecutar** v4complete
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-8
cp tests/config/*.py evidence/fase-config-8/ 2>/dev/null || true
cp scripts/doctor.py evidence/fase-config-8/

venv/Scripts/python.exe scripts/log_phase_completion.py     --fase FASE-CONFIG-8     --desc "Suite de tests de regresión: migración por YAML, fallback, schema, integración. doctor.py actualizado con verificación de config files."     --archivos-nuevos "tests/config/test_config_pricing.py,tests/config/test_config_scenarios.py,tests/config/test_config_fallbacks.py,tests/config/test_config_commercial.py,tests/config/test_config_benchmarks.py,tests/config/test_config_fallback.py,tests/config/test_config_schema.py,tests/config/test_config_integration.py"     --archivos-mod "scripts/doctor.py"     --tests "30"     --check-manual-docs
```

**Siguiente fase (ÚLTIMA):**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-RELEASE-4.38.0.md siguiendo .agents/workflows/phased_project_executor.md
```
