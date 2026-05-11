# FASE-4: Corrección Financiera (H3, H4 — MEDIO)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.  
> **Tipo de ejecución**: DIRECTA (código puro, sin comandos largos)  
> **Límite de iteraciones**: Máximo 60. Budget estimado: ~25 trabajo + ~15 docs = ~40.

## Contexto previo

FASE-1, FASE-2 y FASE-3 completadas. Coherence, propuesta y monthly_report están corregidos.

**Hallazgos a resolver**:
- **H3 (MENOR)**: Suma de brechas ($3,742,069) ≠ `financial_value_central` ($3,741,696). Diferencia: 373 COP (0.01%). Causa: distribución equitativa sin normalización.
- **H4 (MENOR)**: El template confunde `pain_ratio` (41% = porción del dolor abordable) con `recovery_factor` (20% = efectividad real). Muestra $1.5M como ganancia proyectada cuando la real es ~$305K.

## Objetivo de esta fase

Eliminar discrepancia de redondeo en brechas y separar claramente los conceptos financieros `pain_ratio` y `recovery_factor` en la propuesta.

### Tareas

- [x] **T1: Normalizar distribución de brechas al valor central exacto**
  - Archivo: `modules/commercial_documents/v4_proposal_generator.py` — `_build_brecha_data()` (L1374-1403)
  - Actualmente: divide `financial_value_central` entre número de problemas de forma equitativa
  - Cambio: usar pesos de `OpportunityScorer` (impacto de `brechas_reales`) si existen; si no, distribución equitativa
  - Paso final: normalizar la suma al `financial_value_central` exacto (ajustar última brecha para que cuadre)
  - Ejemplo: si suma da $3,742,069 y central es $3,741,696, restar 373 COP de la última brecha
  - Asegurar que porcentajes mostrados se calculen DESPUÉS de la normalización

- [x] **T2: Separar conceptos pain_ratio vs recovery_factor en template**
  - Archivo: `modules/commercial_documents/v4_proposal_generator.py` — método que inyecta variables financieras al template
  - Template: `propuesta_v6_template.md` (u otro template activo)
  - Cambios:
    1. Mostrar `pain_ratio` como "Porción del dolor abordable: 41%"
    2. Mostrar `recovery_factor` como "Efectividad esperada de recuperación: 20% (realista)"
    3. Mostrar ganancia proyectada REAL: `$3,741,696 × 0.4082 × 0.20 = ~$305,472 COP/mes`
    4. Eliminar o corregir texto que dice "el 41% representa la porción que consideramos recuperable con IAO" → cambiar a "el 41% representa el dolor financiero abordable; aplicando un factor de efectividad del 20%, la proyección realista es de ~$305K COP/mes"

- [x] **T3: Tests y validaciones**
  - Test: `_build_brecha_data()` retorna brechas cuya suma exacta es `financial_value_central` (sin diferencia de redondeo)
  - Test: Template data contiene `pain_ratio`, `recovery_factor` y `projected_real_gain` separados
  - Test: Propuesta renderizada menciona ambos conceptos con valores correctos
  - Ejecutar `run_all_validations.py --quick` y confirmar 4/4

### Restricciones

- **NO** modificar `financial_scenarios.json` ni el motor financiero (los inputs son correctos)
- **NO** cambiar el cálculo de `pain_ratio` ni `recovery_factor` (son correctos por separado)
- **NO** ejecutar `v4complete` en esta fase
- Preservar formato de moneda COP (sin decimales, con separadores de miles)

### Criterios de completitud

- [x] Suma de brechas en propuesta = `financial_value_central` exacto (0 COP de diferencia)
- [x] Template distingue claramente pain_ratio (41%) vs recovery_factor (20%)
- [x] Ganancia proyectada mostrada es ~$305K COP/mes, no ~$1.5M COP/mes
- [x] Tests nuevos pasan (mínimo 3)
- [x] Tests existentes no tienen regresiones
- [x] `run_all_validations.py --quick` pasa 4/4

### Próxima sesión

FASE-5: Verificación E2E — v4complete para Termales Santa Rosa de Cabal.
