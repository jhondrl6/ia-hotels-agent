# FASE-A: Unificar variables financieras (CODE-1/3/4) + Sincronizar gate ROI (CODE-2)

**ID**: FASE-A
**Objetivo**: Corregir 4 bugs de código que producen números contradictorios en la propuesta comercial: unificar `recovered_6m`, `net_benefit_6m` a `effective_monthly_gain` + sincronizar gate CG-ROI-NEGATIVE.
**Dependencias**: Ninguna (fase inicial)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La auditoría `Propuesta.md` (2026-05-26) identificó que el generador de propuesta (`v4_proposal_generator.py`) mantiene DOS variables para el mismo concepto financiero:

- `projected_monthly_gain` (L681): `raw_loss × pain_ratio` — **sin recovery_factor**
- `effective_monthly_gain` (L691): `raw_loss × pain_ratio × recovery` — **con recovery_factor**

El template usa `projected_monthly_gain` en `recovered_6m` (L796) y `net_benefit_6m` (L797), mientras que `total_recovered` (L824) y `_calculate_roi()` (L1354) ya usan `effective_monthly_gain`. Esto produce 3 "filosofías" distintas en la misma tabla, con contradicciones visibles para el cliente.

Además, el gate `CG-ROI-NEGATIVE` (L419-448 en `commercial_gate.py`) recibe `net_benefit_6m` calculado con `monthly_loss_central` (fuga bruta) mientras la tabla ROI usa `effective_monthly_gain` (recuperación neta). El gate puede pasar ✅ mientras la tabla muestra pérdida ❌.

### Evidencia verificada en código vivo

```python
# L681 — SIN recovery
projected_monthly_gain = int(raw_monthly_loss * pain_ratio)

# L691 — CON recovery  
effective_monthly_gain = int(raw_monthly_loss * pain_ratio * recovery_realistic)

# L796 — USA projected (BUG: optimista, sin recovery)
'recovered_6m': format_cop(projected_monthly_gain * 6),

# L797 — USA projected (BUG: optimista, sin recovery)
'net_benefit_6m': format_cop((projected_monthly_gain - monthly_investment) * 6),

# L824 — YA USA effective ✅ (referencia correcta)
'total_recovered': format_cop(effective_monthly_gain * 6),
```

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| — | (fase inicial) |

### Base Técnica Disponible
- Archivo principal: `modules/commercial_documents/v4_proposal_generator.py` (3100+ líneas)
- Gate: `modules/quality_gates/commercial_gate.py` — método `_check_roi_negative()` L419-448
- `effective_monthly_gain` YA existe en L691 y se usa correctamente en L770-780 (rec_m1..rec_m6, net_m1..net_m6)
- `total_recovered` (L824) YA es correcto — sirve como referencia

---

## Tareas

### Tarea 1: Cambiar `recovered_6m` (L796) de `projected_monthly_gain` → `effective_monthly_gain`

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` L796

**Cambio**:
```python
# ANTES
'recovered_6m': format_cop(projected_monthly_gain * 6),  # FASE-B: pain_ratio adjusted

# DESPUÉS
'recovered_6m': format_cop(effective_monthly_gain * 6),  # PROPUESTA-COMERCIAL FASE-A: unified to effective
```

**Criterios de aceptación**:
- [ ] `recovered_6m` coincide con `total_recovered` (L824)
- [ ] Sin cambios en otras variables

### Tarea 2: Cambiar `net_benefit_6m` (L797) de `projected_monthly_gain` → `effective_monthly_gain`

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py` L797

**Cambio**:
```python
# ANTES
'net_benefit_6m': format_cop((projected_monthly_gain - monthly_investment) * 6),  # FASE-B

# DESPUÉS
'net_benefit_6m': format_cop((effective_monthly_gain - monthly_investment) * 6),  # PROPUESTA-COMERCIAL FASE-A
```

**Criterios de aceptación**:
- [ ] `net_benefit_6m`, `roi_6m`, `recovered_6m`, `total_recovered` TODOS usan `effective_monthly_gain`
- [ ] La tabla de ROI ya no muestra $4.5M recuperados con ROI 0.1X simultáneamente

### Tarea 3: Verificar consistencia — grep de `projected_monthly_gain` en sección de placeholders

**Objetivo**: Confirmar que ningún otro placeholder en L793-830 usa `projected_monthly_gain` donde debería usar `effective_monthly_gain`.

**Comando**:
```bash
grep -n 'projected_monthly_gain' modules/commercial_documents/v4_proposal_generator.py
```

**Criterios de aceptación**:
- [ ] `projected_monthly_gain` solo se usa en: L681 (definición), L683-684 (cálculos internos de roi_6_months y break_even), L732, L756 (placeholders de ganancia bruta proyectada — estos SÍ deben usar projected)
- [ ] Los placeholders financieros de recuperación (L770-830) solo usan `effective_monthly_gain`

### Tarea 4: Sincronizar CG-ROI-NEGATIVE (CODE-2)

**Archivo**: `modules/quality_gates/commercial_gate.py` L419-448

**Problema**: El gate en L345 (`v4_proposal_generator.py`) calcula `monthly_gain = getattr(realistic, 'monthly_loss_central', None)` — esto es raw loss, sin pain_ratio ni recovery. El gate pasa si loss > investment, aunque la tabla muestre pérdida neta.

**Fix**: El `net_benefit_6m` que ya se pasa al validator (L364) debe recalcularse con `effective_monthly_gain`:
```python
# L339-350 en v4_proposal_generator.py — verificar que monthly_gain use effective_monthly_gain
net_monthly = monthly_gain - price_monthly  # monthly_gain debe ser post-recovery
net_benefit_6m = net_monthly * 6
```

**Criterios de aceptación**:
- [ ] `monthly_gain` en el cálculo del gate usa `effective_monthly_gain`, no `monthly_loss_central` crudo
- [ ] El gate falla cuando la tabla muestra ROI negativo

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Validación rápida | `python scripts/run_all_validations.py --quick` | 4/4+ checks |
| Tests de propuesta | `pytest tests/commercial_documents/ -v -k "proposal" --timeout=60` | Sin regresiones |
| Gate ROI | `pytest tests/quality_gates/ -v -k "roi" --timeout=60` | Sin regresiones |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-A como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items A1-A4 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar módulos en Sección A, funcionalidades en B
4. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "CODE-1/3/4: Unificar recovered_6m, net_benefit_6m a effective_monthly_gain + CODE-2: sincronizar gate CG-ROI-NEGATIVE" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/quality_gates/commercial_gate.py" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] L796: `recovered_6m` usa `effective_monthly_gain`
- [ ] L797: `net_benefit_6m` usa `effective_monthly_gain`
- [ ] `roi_6m`, `recovered_6m`, `net_benefit_6m`, `total_recovered` → misma base financiera
- [ ] Gate CG-ROI-NEGATIVE sincronizado con tabla ROI
- [ ] `run_all_validations.py --quick` pasa
- [ ] Tests de propuesta sin regresiones
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar templates (.md) — solo código Python
- NO ejecutar v4complete
- NO modificar `scenario_calculator.py`
- NO eliminar `projected_monthly_gain` — se sigue usando para placeholders de "ganancia bruta proyectada"
- Máximo 60 iteraciones de agente
- Solo modificar `v4_proposal_generator.py` y `commercial_gate.py`
