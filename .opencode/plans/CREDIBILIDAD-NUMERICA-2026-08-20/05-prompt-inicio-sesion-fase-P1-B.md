# FASE-P1-B: Fallback Región Conservador (F3) + Comisión OTA Parametrizada (F5)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P1-B
**Objetivo**: Corregir el mapa de fallback de región (`'colombia'→'caribe'` infla la fuga 2.3-3.2x)
y parametrizar la comisión OTA con rango y fuente citada (hoy hardcodeada en 15%).
**Dependencias**: FASE-P1-A ✅ (benchmark maestro único ya implementado)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` — **fase DELEGABLE vía `delegate_task` (2 tracks paralelas)**

## Modo de Ejecución — delegate_task (AJUSTADO)

Esta fase tiene **2 tracks** (F3 en `modules/auditors/`; F5 en `modules/financial_engine/` +
`modules/orchestration_v4/two_phase_flow.py` + `modules/utils/benchmarks.py` — parametrización
mecánica sin decisión de diseño abierta: ya está pre-resuelta como **D2** en 01-plan-maestro §7),
lo que según las reglas del executor permite delegar a subagentes en paralelo:

```
SI el entorno de ejecución permite subagentes con acceso al venv del proyecto:
  → delegate_task(
      goal="Fix F3: fallback de region conservador",
      context="""
        FALLO F3: mapa de fallback en modules/auditors/v4_comprehensive.py (zona L1466,
        verificar leyendo el archivo completo) mapea 'colombia' -> 'caribe' ($950K boutique),
        inflando la fuga 2.3-3.2x cuando GBP solo dice 'Colombia'.
        FIX: 'colombia' debe resolver a default conservador ($300K), NO a caribe.
        Tests: pytest tests/auditors/ -v -k region (crear tests si no existen)
      """,
      timeout=400,
      toolsets=["file", "terminal"]
    )
  → delegate_task(
      goal="Fix F5: comision OTA parametrizada con rango y fuente",
      context="""
        FALLO F5: comisión OTA 15% hardcodeada en 5 sitios (3 módulos):
        - modules/financial_engine/scenario_calculator.py (L96 default 0.15, L118
          default_ota_commission=0.15, L543 fuente 'industry_standard_15pct')
        - modules/financial_engine/calculator_v2.py (L442, L466)
        - modules/financial_engine/inputs_contract.py (L47)
        - modules/orchestration_v4/two_phase_flow.py (L245 y L318)
        - modules/utils/benchmarks.py (L28 'comision_ota_base': 0.15, defaults propios)
        DECISIÓN D2 (01-plan-maestro §7): usar el campo EXISTENTE comision_ota de
        config/financial_defaults.yaml (L14-17: min 0.18, base 0.20, max 0.22) añadiéndole
        source. NO crear un campo nuevo ota_commission. El flatten comision_ota.{min,base,max}
        → comision_ota_min/base/max YA existe en modules/utils/financial_factors.py (L78-86).
        FIX: los 5 sitios leen de config (base para cálculo, rango para reporte);
        FinancialBreakdown.ota_commission_source (scenario_calculator L471) reporta
        rango + fuente real en financial_scenarios.json (reemplaza 'industry_standard_15pct').
        Tests: pytest tests/financial_engine/ tests/orchestration_v4/ tests/utils/ -q
        (crear tests si no existen)
      """,
      timeout=400,
      toolsets=["file", "terminal"]
    )
  → Agente principal integra, ejecuta tests completos y run_all_validations.py --quick
SI los subagentes NO pueden acceder al venv del proyecto (WSL/Windows):
  → Ejecución DIRECTA secuencial: primero F3, luego F5 (evita overhead de spawn fallido)
```

**Advertencia venv**: según lección de FASE-4 BUGS-ONBOARDING-ADR, subagentes WSL no comparten
el Python environment del venv Windows; imports como bs4/selenium fallan. Verificar antes de delegar.

**Regla**: el agente principal SIEMPRE ejecuta los tests finales y la validación completa — NO
delegar la verificación final.

## Contexto

CONTEXT §2 fallos **F3** y **F5**:
- **F3**: Si la dirección GBP solo dice "Colombia" (común en GBP incompletos del ICP objetivo),
  el ADR se resuelve como `caribe` ($950K boutique) en vez de default ($300K), sobreestimando
  la fuga 2.3-3.2x en el hook de venta.
- **F5**: Comisión OTA 15% hardcodeada en **5 sitios** (`scenario_calculator.py` L96/L118/L543,
  `calculator_v2.py` L442/L466, `inputs_contract.py` L47, `two_phase_flow.py` L245/L318,
  `utils/benchmarks.py` L28) vs 17-25% usada en la narrativa comercial. Subestima la fuga OTA en
  la cifra que ancla el pitch. **Decisión D2 pre-resuelta**: el campo `comision_ota` YA existe en
  `config/financial_defaults.yaml` (0.18-0.22) — NO crear campo nuevo.

P1 exige que la cifra de fuga sea defendible ante un hotelero escéptico.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A/B/C | ✅ Completadas |
| FASE-P1-A | ✅ Completada |

### Base Técnica Disponible
- `modules/auditors/v4_comprehensive.py` (mapa de fallback de región, zona L1466)
- Los 5 sitios de 0.15 (ver F5 arriba) en 3 módulos
- `config/financial_defaults.yaml` (`comision_ota: {min: 0.18, base: 0.20, max: 0.22}` L14-17 —
  fuente EXISTENTE; añadir `source` dentro del mismo campo)
- `modules/utils/financial_factors.py` (L78-86: flatten `comision_ota.{min,base,max}` →
  `comision_ota_min/base/max`; `_FALLBACK_DEFAULTS` L55-61) y `main.py` L361 (consumo de
  `comision_ota_base`) — NO romper estos consumidores
- Benchmark maestro único de FASE-P1-A

## Tareas

### T0: Capturar baseline de auditors (la línea base §6 del plan-maestro NO incluyó esa suite)
```powershell
.\venv\Scripts\python.exe -m pytest tests/auditors/ -q --tb=no *> evidence/BASELINE-TESTS-auditors-v4.71.0.txt
```
- [ ] Baseline guardada ANTES de cualquier cambio

### T1: Fix F3 — fallback de región conservador
**Archivos afectados**:
- `modules/auditors/v4_comprehensive.py` (mapa de fallback)
**Criterios de aceptación**:
- [ ] `'colombia'` resuelve a default conservador ($300K o el default que defina el benchmark maestro)
- [ ] No se resuelve a `caribe` ($950K) para direcciones país-genérico
- [ ] Tests de región pasan sin fallos NUEVOS vs baseline de auditors (T0)

### T2: Fix F5 — comisión OTA parametrizada (decisión D2 pre-resuelta)
**Archivos afectados** (los 5 sitios verificados en código vivo):
- `modules/financial_engine/scenario_calculator.py` (L96, L118, L543)
- `modules/financial_engine/calculator_v2.py` (L442, L466)
- `modules/financial_engine/inputs_contract.py` (L47)
- `modules/orchestration_v4/two_phase_flow.py` (L245, L318)
- `modules/utils/benchmarks.py` (L28)
- `config/financial_defaults.yaml` (añadir `source` al campo EXISTENTE `comision_ota` — NO crear campo nuevo)
**Criterios de aceptación**:
- [ ] Comisión OTA leída desde config en los 5 sitios, no hardcodeada
- [ ] `financial_scenarios.json` reporta rango y fuente en `ota_commission_source`
      (reemplaza `'industry_standard_15pct'` de L543)
- [ ] Consumidores existentes de `comision_ota_base` intactos (`financial_factors.py`,
      `main.py` L361, `plan_validator.py` L38)
- [ ] Tests de escenarios financieros: sin fallos NUEVOS vs línea base (§6: 10 preexistentes en
      financial_engine — ver `evidence/BASELINE-TESTS-v4.71.0.txt`)

### T3: Tests de contrato anti-regresión
**Criterios de aceptación**:
- [ ] Test F3: `'colombia'` → default conservador (no caribe)
- [ ] Test F5: comisión OTA configurable desde `financial_defaults.yaml` (campo `comision_ota`)
- [ ] Suites `tests/auditors/` y `tests/financial_engine/` sin fallos NUEVOS vs línea base
      (financial_engine: 10 preexistentes §6; auditors: baseline capturada en T0)
- [ ] Verificación grep (lección L28/L32 del plan RC1-RC2: el fix debe cubrir TODOS los sitios):
      buscar `0\.15|industry_standard_15pct` en `modules/financial_engine/`,
      `modules/orchestration_v4/two_phase_flow.py` y `modules/utils/benchmarks.py` →
      0 restantes como comisión OTA (los 0.15 de OTROS conceptos —curvas de madurez,
      recovery_factors, factores de scorer, umbrales de encoding— NO se tocan)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Fallback región | `tests/auditors/test_region_fallback.py` (nuevo o existente) | Contrato F3 pasa |
| Comisión OTA | `tests/financial_engine/test_ota_commission.py` (nuevo o existente) | Contrato F5 pasa |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/auditors/ tests/financial_engine/ -v
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P1-B ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones.
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P1-B --desc "Fallback region conservador (F3) + comision OTA parametrizada (F5)" --archivos-mod "modules/auditors/v4_comprehensive.py,modules/financial_engine/scenario_calculator.py,modules/financial_engine/calculator_v2.py,modules/financial_engine/inputs_contract.py,modules/orchestration_v4/two_phase_flow.py,modules/utils/benchmarks.py,config/financial_defaults.yaml" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] `'colombia'` resuelve a default conservador (verificado por test)
- [ ] Comisión OTA parametrizada con rango y fuente en los 5 sitios (verificado por test + grep)
- [ ] Suites auditors + financial_engine sin fallos NUEVOS vs línea base
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO modificar benchmark maestro (ya cerrado en P1-A).
- NO modificar cap de plausibilidad del hook (es FASE-P1-C); en two_phase_flow.py SOLO tocar
  las líneas de comisión OTA (L245/L318) — el resto del archivo es propiedad de FASE-P1-C.
- NO crear el campo `ota_commission` nuevo — usar `comision_ota` existente (decisión D2).
- NO ejecutar v4complete.
