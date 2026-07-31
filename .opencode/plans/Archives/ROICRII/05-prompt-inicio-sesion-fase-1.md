# FASE-1: Unificar ROI — Eliminar Motores Inline, Usar roi_formatter como Motor Único

**Plan**: ROICRII
**Tipo**: Código+Tests
**Hallazgos**: CRIT-01, IMP-02
**Prerrequisito**: Ninguno
**Iteración estimada**: 35-45

---

## Objetivo

Eliminar los dos métodos inline de cálculo de ROI (`_calculate_roi()` L1492 y `_calculate_roi_saas()` L1534) en `v4_proposal_generator.py` y reemplazar TODAS sus llamadas por el motor ya implementado `roi_formatter.py` (L25: importado pero 0 calls). Cambiar formato de `:.1f` a `:.2f` en los 3 sitios.

---

## Hallazgos a Resolver

### CRIT-01: Tres sistemas ROI paralelos
**Evidencia verificada (grep 2026-05-27)**:
- `_calculate_roi()` L1492: `(gain * recovery_factor) / investment` → genera `roi_6_months` con `:.1fX`
- `_calculate_roi_saas()` L1534: `total_recuperacion / inversion_opex` → genera `roi_saas` con `:.1fX`
- `roi_formatter.py` L25: `calcular_metricas_roi()` + `formatear_roi_para_propuesta()` — **importado pero 0 calls**

### IMP-02: Formato `:.1f` produce display incorrecto
**Evidencia**: roi_formatter.py:81 usa `f"{metrics.roi_saas:.1f}X"` — si roi_saas=1.05, display es "1.1X".

---

## Tareas

### Tarea 1A: Cambiar formato `:.1f` → `:.2f` en roi_formatter.py
**Archivo**: `modules/financial_engine/roi_formatter.py`
**Línea**: L81
**Cambio ANTES**:
```python
"roi_saas": f"{metrics.roi_saas:.1f}X",
```
**Cambio DESPUÉS**:
```python
"roi_saas": f"{metrics.roi_saas:.2f}X",
```

**Verificación**: `grep ":\.2f" modules/financial_engine/roi_formatter.py` retorna 1 match.

### Tarea 1B: Reemplazar TODAS las llamadas a `_calculate_roi()` y `_calculate_roi_saas()` por `calcular_metricas_roi()` + `formatear_roi_para_propuesta()`
**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Llamadas a reemplazar** (verificadas con grep):
- L710: `roi_6_months = self._calculate_roi(monthly_investment, projected_monthly_gain, 6, recovery_factor=...)`
- L810: `'conservative_roi': self._calculate_roi(...)` 
- L814: `'optimistic_roi': self._calculate_roi(...)`
- L854: `'roi_saas': self._calculate_roi_saas(total_recuperacion, inversion_opex, inversion_capex)`

**Estrategia**: Calcular `calcular_metricas_roi()` UNA VEZ con los datos del hotel, luego usar `formatear_roi_para_propuesta()` para obtener el dict con todas las variantes (conservative, realistic, optimistic, saas).

**NOTA**: Antes de implementar, leer `roi_formatter.py` completo para entender su API exacta (qué inputs necesita, qué outputs produce). NO asumas la firma — lee el código.

### Tarea 1C: Eliminar métodos inline `_calculate_roi()` (L1492-1515) y `_calculate_roi_saas()` (L1534-1554)
**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Eliminar ambos métodos. El import L25 ya trae `calcular_metricas_roi, formatear_roi_para_propuesta` — solo falta usarlos.

**Verificación**: `grep "_calculate_roi\b" modules/commercial_documents/v4_proposal_generator.py` debe retornar SOLO el import de roi_formatter, NO definiciones inline.

### Tarea 1D: Tests — actualizar fixtures + crear test de unificación
**Archivo**: `tests/test_roi_unification.py` (nuevo)

Crear tests que verifiquen:
1. `_calculate_roi` ya NO existe como método de la clase
2. `roi_formatter.calcular_metricas_roi()` produce roi_saas con formato `:.2f` (2 decimales)
3. Solo hay UNO motor de ROI (0 métodos inline, 1 import activo)
4. Para Castilla Real: roi_saas > 0 (no negativo)

**Ejecución**: `pytest tests/test_roi_unification.py -v`

---

## Verificación Final FASE-1

```bash
# 1. Solo roi_formatter como motor
grep -c "def _calculate_roi\b\|def _calculate_roi_saas\b" modules/commercial_documents/v4_proposal_generator.py
# Expected: 0

# 2. roi_formatter import ACTIVO (no solo import)
grep -c "calcular_metricas_roi\|formatear_roi_para_propuesta" modules/commercial_documents/v4_proposal_generator.py
# Expected: ≥3 (1 import + ≥2 calls)

# 3. Formato .2f en roi_formatter
grep ":\.2f" modules/financial_engine/roi_formatter.py
# Expected: 1 match

# 4. Tests pasando
pytest tests/test_roi_unification.py -v
# Expected: all passed
```

---

## Log Phase

Al completar, ejecutar:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase.py --phase "FASE-1" --plan "ROICRII" --status "completed" --desc "ROI_unificado_roi_formatter_motor_unico_formato_2f"
```

---

## Documentación Post-Fase

Actualizar `09-documentacion-post-proyecto.md` con:
- Qué se hizo (unificación ROI)
- Archivos modificados (roi_formatter.py, v4_proposal_generator.py)
- Tests nuevos (test_roi_unification.py)
- Estado de hallazgos CRIT-01 e IMP-02
