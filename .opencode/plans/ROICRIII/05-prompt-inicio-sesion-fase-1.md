# FASE-1 — Motor Financiero Unificado (A1+A2+A3)

**ID**: ROICRIII-FASE-1
**Objetivo**: Unificar el doble motor de cálculo en `_prepare_template_data()` para que exista UN SOLO origen de verdad para la recuperación a 6 meses y el ROI.
**Dependencias**: Ninguna (primera fase del plan)
**Complejidad**: 🔴 ALTA — Modifica el método más largo del generator (~700 líneas) con dos paths de cálculo interrelacionados
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La v4.55.0 introdujo una regresión crítica: `_prepare_template_data()` calcula DOS totales de recuperación distintos usando fuentes diferentes:
1. `total_recovered` (L~968): `effective_monthly_gain * 6` → produce $1.069.410
2. `_maturity_result.total_recuperacion_6m` (L~904): curva de maduración → produce $5.041.935

El template V6 muestra ambos números en secciones distintas (bullets "Total 6 meses" L~115 y Curva de Maduración L~137), creando contradicción visible (ROI 0.45X vs 2.10X).

**Los rows individuales (rec_m1..rec_m6) YA vienen de la curva de maduración** (`_rec_map`, L~801). Solo el TOTAL está inconsistente.

---

## Tareas

### T1: Unificar total_recovered con la curva de maduración [A1]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

En el método `_prepare_template_data()`, grep para `'total_recovered':` y encontrar la asignación actual.

**ANTES** (patrón a buscar):
```python
'total_recovered': format_cop(effective_monthly_gain * 6),
```

**DESPUÉS**:
```python
'total_recovered': format_cop(_maturity_result.total_recuperacion_6m),
```

**También** unificar `net_benefit`:
**ANTES**:
```python
'net_benefit': format_cop((effective_monthly_gain - monthly_investment) * 6),
```
**DESPUÉS**:
```python
'net_benefit': format_cop(_maturity_result.total_recuperacion_6m - (monthly_investment * 6)),
```

**Criterios**:
- [ ] `grep -n "total_recovered" v4_proposal_generator.py` muestra UNA sola fuente: `_maturity_result.total_recuperacion_6m`
- [ ] `grep -n "effective_monthly_gain \* 6" v4_proposal_generator.py` NO aparece en total_recovered ni net_benefit
- [ ] No SyntaxError: `python -c "import modules.commercial_documents.v4_proposal_generator"`

### T2: Unificar ROI a un solo número [A2]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Grep para `'roi_6m':` en `_prepare_template_data()`.

**ANTES**:
```python
'roi_6m': roi_6_months,
```

**DESPUÉS**: Calcular el ROI usando la recuperación de la curva de maduración (no effective_monthly_gain):
```python
'roi_6m': round(_maturity_result.total_recuperacion_6m / (monthly_investment * 6), 2),
```

**NOTA**: Verificar si `calcular_metricas_roi` y `formatear_roi_para_propuesta` existen en `modules/financial_engine/roi_formatter.py`. Si existen, usarlos. Si no, usar el cálculo directo de arriba. NO inventar imports.

**Criterios**:
- [ ] `roi_6m` usa `_maturity_result.total_recuperacion_6m` como numerador
- [ ] El ROI para Castilla Real (fuga=$3.74M, fee=$400K) debe ser ~2.10X
- [ ] No hay imports nuevos que no existan en el codebase

### T3: Eliminar bullets "Total 6 meses" redundantes del template V6 [A3]

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md`

Grep para `"Total 6 meses"` o `total_recovered` en el template.

**ACCIÓN**: Eliminar la sección de bullets que muestra el total redundante (Invierte/Recupera/Beneficio neto/ROI usando `total_recovered`). La tabla mes-a-mes se MANTIENE (solo los bullets debajo).

**IMPORTANTE**: MANTENER la tabla de proyección mes a mes (inv_m1..rec_m1 etc.). Solo eliminar los 4-5 bullets que están DEBAJO de la tabla y que muestran el total usando `${total_recovered}` y `${roi_6m}`.

**Criterios**:
- [ ] `grep "Total 6 meses" propuesta_v6_template.md` → vacío
- [ ] La tabla mes a mes con columnas Invierte/Recuperación/Beneficio/Pilar SIGUE presente
- [ ] `${pain_ratio_note}` y la sección de trazabilidad SIGUEN presentes
- [ ] El ROI solo se muestra en la sección CAPEX/OPEX (no duplicado en la tabla simple)

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_curva_maduracion_suma_correcta` | `tests/commercial_documents/test_financial_coherence.py` | total = $5.041.935 |
| `test_roi_unificado_con_fee_real` | `tests/commercial_documents/test_financial_coherence.py` | ROI = 2.10X |
| `test_net_benefit_positivo_con_curva` | `tests/commercial_documents/test_financial_coherence.py` | net > 0 ($2.64M) |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_financial_coherence.py -v
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short  # regression check
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`** — Marcar FASE-1 como ✅ Completada
2. **`06-checklist-implementacion.md`** — Actualizar estado
3. **`09-documentacion-post-proyecto.md`** — Sección C: correcciones críticas
4. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-1 --desc "Unificar_motor_financiero_A1_A2_A3" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" --tests "3" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] `total_recovered` unificado a `_maturity_result.total_recuperacion_6m`
- [ ] `roi_6m` calculado con curva de maduración (resultado ~2.10X)
- [ ] Bullets "Total 6 meses" eliminados del template V6
- [ ] 3 tests nuevos pasan
- [ ] No regresiones en tests existentes
- [ ] run_all_validations.py --quick pasa
- [ ] Post-ejecución completada (log + dependencias + docs)

---

## Restricciones

- NO modificar `pricing_calculator.py` ni `pillar_maturity_curve.py` en esta fase
- NO modificar la lógica de `effective_monthly_gain` (puede usarse en otros lugares)
- NO añadir imports de funciones que no existan en el codebase (verificar con grep primero)
- Límite: 60 iteraciones de agente
- Si se agotan las iteraciones, guardar progreso parcial en dependencias-fases.md

---

## Notas de Ejecución

**⚠️ Plan line numbers are ALWAYS stale.** Los números de línea en este prompt (L~968, L~904, L~801) son orientativos. SIEMPRE hacer grep para encontrar la ubicación real del código antes de parchear.

**Dict-literal pitfall**: Si `_prepare_template_data()` construye un diccionario literal grande, NO insertar statements (if/for/function calls) DENTRO del literal. Pre-calcular fuera del dict.

**Verificar _maturity_result**: Grep para `_maturity_result` en el método para confirmar que la variable existe y tiene `.total_recuperacion_6m`. Si la variable se llama diferente en el código vivo, adaptar.
