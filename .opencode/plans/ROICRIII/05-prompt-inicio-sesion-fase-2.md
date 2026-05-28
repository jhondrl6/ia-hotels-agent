# FASE-2 — Pain Ratio Note + Trazabilidad Financiera (A4+A5)

**ID**: ROICRIII-FASE-2
**Objetivo**: Corregir el porcentaje de inversión vs fuga y eliminar el "13% número mágico" en la trazabilidad financiera.
**Dependencias**: FASE-1 ✅ (motor financiero unificado)
**Complejidad**: 🟡 MEDIA — Modifica texto dinámico en data dict, no lógica de cálculo
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Dos problemas de texto en la propuesta comercial:

1. **NEW-CRIT-02**: `pain_ratio_note` muestra "14%" (o similar) que no coincide con el cálculo real fee/fuga = 10.69% para Castilla Real. El `pain_ratio` interno (~13.6%) es un artefacto del pipeline de pricing, no el porcentaje que el cliente debe ver.

2. **NEW-CRIT-03**: La trazabilidad dice "13% del dolor priorizado × 35% de recuperación conservadora" donde "13%" es el `pain_ratio` inflado por floor pricing. NO es un porcentaje documentado ni trazable.

---

## Tareas

### T1: Corregir pain_ratio_note — usar porcentaje inversión/fuga real [A4]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Grep para `pain_ratio_note` en `_prepare_template_data()`.

**ANTES** (patrón a buscar):
```python
'pain_ratio_note': (
    f"... representa el {pain_ratio:.0%} de su pérdida ..."
```

**DESPUÉS**: Calcular el porcentaje real de inversión vs fuga y usarlo. IMPORTANTE: calcular la variable UNA SOLA VEZ antes del dict literal, NO repetir el cálculo.

```python
# Pre-calcular ANTES del dict literal:
_pct_inv_vs_fuga = round((monthly_investment / abs(raw_monthly_loss)) * 100, 1)

# Dentro del dict:
'pain_ratio_note': (
    f"**Nota de proyección**: La inversión mensual de ${int(monthly_investment):,} COP "
    f"representa solo el {_pct_inv_vs_fuga}% "
    f"de su fuga mensual estimada (${int(abs(raw_monthly_loss)):,}). "
    f"El otro {round(100 - _pct_inv_vs_fuga, 1)}% "
    f"seguiría perdiéndose cada mes si no implementamos el Kit 4 Pilares."
),
```

**Verificar**: Que `monthly_investment` y `raw_monthly_loss` existan en el scope del método. Grep para confirmar. Si `raw_monthly_loss` se llama diferente, adaptar.

**Criterios**:
- [ ] `pain_ratio_note` NO usa el `pain_ratio` interno para mostrar al cliente
- [ ] Para Castilla Real: fee=$400K, fuga=$3.74M → muestra "10.7%" (no "14%" ni "41%")
- [ ] La variable `_pct_inv_vs_fuga` se calcula UNA vez (no 3 veces = bug de drift)

### T2: Corregir trazabilidad financiera — eliminar "13% número mágico" [A5]

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

Grep para `fuga_total_6m`, `recuperacion_proyectada_6m`, `trazabilidad` en `_prepare_template_data()`.

**MANTENER** `pain_pct` y `recov_pct` — el template V6 los usa (`${pain_pct}% × ${recov_pct}%`).

**ANTES**:
```python
'recuperacion_proyectada_6m': format_cop(effective_monthly_gain * 6),
```

**DESPUÉS**:
```python
'fuga_total_6m': format_cop(abs(raw_monthly_loss) * 6),
'recuperacion_proyectada_6m': format_cop(_maturity_result.total_recuperacion_6m),
'pain_pct': int(pain_ratio * 100),       # MANTENER — template V6 lo usa
'recov_pct': int(recovery_realistic * 100),  # MANTENER — template V6 lo usa
'trazabilidad_origen': (
    f"Fuga mensual (${int(abs(raw_monthly_loss)):,}) × "
    f"Curva de Maduración 4 Pilares (GEO→SEO→AEO→IAO) × "
    f"Recovery Factor {int(recovery_realistic * 100)}%"
),
```

**También** en el template `propuesta_v6_template.md`, añadir `${trazabilidad_origen}` después de la línea de trazabilidad existente:

Grep para `"Trazabilidad financiera"` en el template y añadir:
```markdown
> **Origen**: ${trazabilidad_origen}.
```

**Verificar**: Que `recovery_realistic` exista en el scope. Grep para confirmar.

**Criterios**:
- [ ] `recuperacion_proyectada_6m` usa `_maturity_result.total_recuperacion_6m` (no effective_monthly_gain * 6)
- [ ] `trazabilidad_origen` existe en el data dict
- [ ] Template V6 renderiza `${trazabilidad_origen}`
- [ ] No SyntaxError

---

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| `test_porcentaje_inversion_vs_fuga` | `tests/commercial_documents/test_financial_coherence.py` | 10.7% correcto |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_financial_coherence.py -v
./venv/Scripts/python.exe -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-2 como ✅ Completada
2. **`06-checklist-implementacion.md`** — Actualizar estado
3. **`09-documentacion-post-proyecto.md`** — Sección C: correcciones críticas
4. **log_phase_completion.py**:
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe" scripts/log_phase_completion.py --fase FASE-2 --desc "Pain_ratio_note_trazabilidad_A4_A5" --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" --tests "1" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `pain_ratio_note` muestra porcentaje inversión/fuga real (no pain_ratio interno)
- [ ] `recuperacion_proyectada_6m` unificado con curva de maduración
- [ ] `trazabilidad_origen` añadido al data dict y template
- [ ] Test nuevo pasa + no regresiones
- [ ] run_all_validations.py --quick pasa
- [ ] Post-ejecución completada

---

## Restricciones

- NO modificar la lógica de `pain_ratio` o pricing (eso es el pipeline de pricing, no la propuesta)
- NO eliminar `pain_pct` ni `recov_pct` — el template V6 los necesita
- Límite: 60 iteraciones
