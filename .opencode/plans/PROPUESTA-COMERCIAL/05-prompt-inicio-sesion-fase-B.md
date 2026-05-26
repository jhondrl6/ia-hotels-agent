# FASE-B: Puente dual fuga bruta / recuperación efectiva (CROSS-1)

**ID**: FASE-B
**Objetivo**: Implementar el puente dual obligatorio (Opción C de la auditoría) en diagnóstico y propuesta: ambos documentos muestran "Fuga total estimada" + "Recuperación proyectada con servicio" con explicación visible de `pain_ratio × recovery_factor`.
**Dependencias**: FASE-A (usa `effective_monthly_gain` unificado en proposal generator)
**Duración estimada**: 1-2 horas (investigacion previa completada — ver abajo)
**Skill**: `iah-cli-phased-execution`

---

## Contexto

La auditoría `Propuesta.md` identificó el gap #1: el diagnóstico comunica **fuga bruta** ($22.4M/6m) y la propuesta vende **recuperación efectiva** ($1.8M/6m), generando un gap 12:1 sin explicación. La única mención de `41% × 20%` es una nota de 2 líneas en la propuesta.

**Decisión de producto ya tomada**: Opción C — Puente dual obligatorio. Ambos documentos muestran "Fuga total estimada" + "Recuperación proyectada con servicio" con explicación visible del mecanismo `pain_ratio × recovery_factor`.

### Resultado de la Investigación Previa (2026-05-26)

**El `v4_diagnostic_generator.py` NO tiene acceso a `pain_ratio` ni `recovery_factor`.** Solo recibe `FinancialScenarios` → `Scenario` objects (con `monthly_loss_central`, `monthly_loss_min/max`, etc.). El `pain_ratio` real (0.41 para Castilla Real) viene de `pricing_result.pain_ratio` que se calcula en el harness financiero — DESPUÉS del diagnóstico.

**Estrategia elegida: Opción A — Cargar `scenarios.yaml` en el diagnostic generator.**

El diagnostic generator YA importa `load_yaml_config` en L32 y lo usa en L77 (`load_yaml_config('regional_benchmarks')`) y L413 (`load_yaml_config('commercial')`). Solo hay que agregar una llamada a `load_yaml_config('scenarios')` para obtener `pain_ratio_default` (0.20) y `recovery_factors.realistic` (0.20). El texto en el template aclara "estimación conservadora inicial" — la propuesta usa el pain_ratio real del pricing.

**Nota importante**: Los números del diagnóstico y la propuesta NO serán idénticos. El diagnóstico usa defaults (20% × 20% = 4% de recuperación). La propuesta usa el pain_ratio real del hotel (~41%). Esto es intencional: el diagnóstico comunica urgencia con estimaciones conservadoras; la propuesta entrega precisión financiera.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (asumido) |

### Base Técnica Disponible

- Templates a modificar:
  - `modules/commercial_documents/templates/diagnostico_v6_template.md`
  - `modules/commercial_documents/templates/propuesta_v6_template.md`
- Generadores:
  - `v4_diagnostic_generator.py` — `_build_financial_placeholders()` en L998 (donde se agregan los 4 placeholders nuevos)
  - `v4_proposal_generator.py` — `_prepare_financial_template_vars()` (L674-825, YA tiene `effective_monthly_gain`, `pain_ratio`, `recovery_realistic`)
- En diagnostic generator:
  - `load_yaml_config` YA importado (L32) y usado en otros lugares
  - `base_value` YA disponible en `_build_financial_placeholders()` L1016: `base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max`
  - `format_cop` YA importado
- En proposal generator:
  - `effective_monthly_gain` YA existe en L691 (FASE-A lo unifica)
  - `pain_ratio` YA existe en L680
  - `recovery_realistic` YA existe en L690
  - `raw_monthly_loss` YA existe en L679

---

## Tareas

### Tarea 1: Agregar bloque de puente dual al template de diagnóstico

**Archivo**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Ubicación**: Sección 4 (Proyección Financiera), DESPUÉS de `${scenario_table}` y ANTES del cierre de sección.

**Nuevo bloque**:
```markdown
### 💰 Lo que está en juego

| | Fuga total estimada (6 meses) | Recuperación proyectada (6 meses) |
|---|---|---|
| **Monto** | ${fuga_total_6m} | ${recuperacion_proyectada_6m} |
| **Explicación** | Fuga bruta detectada en las 3 fugas digitales | Con pain_ratio ${pain_pct}% × recovery ${recov_pct}% |

> **¿Por qué la diferencia?** No toda la fuga digital es recuperable a corto plazo.  
> El **${pain_pct}%** de esta fuga es prioritaria y directamente remediable con nuestros servicios.  
> De ese porcentaje, proyectamos recuperar un **${recov_pct}%** en los primeros 6 meses.  
> Esto es conservador: a medida que los activos digitales maduran, el porcentaje de recuperación crece.
```

**Criterios de aceptación**:
- [ ] Tabla dual visible ANTES del cierre de Sección 4
- [ ] Placeholders `${fuga_total_6m}`, `${recuperacion_proyectada_6m}`, `${pain_pct}`, `${recov_pct}` definidos
- [ ] Explicación narrativa clara para el dueño no técnico

### Tarea 2: Agregar placeholders al generador de diagnóstico (Opción A)

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Ubicación precisa**: `_build_financial_placeholders()` método, L998. Insertar después de L1018 (`base_value = getattr(main, ...)`) y antes del `return` del dict de placeholders.

**Código a insertar**:

```python
# PROPUESTA-COMERCIAL FASE-B: Puente dual fuga bruta / recuperación efectiva
# Carga pain_ratio y recovery_factor desde scenarios.yaml (defaults conservadores)
# La propuesta usa el pain_ratio real del pricing; el diagnóstico usa defaults
# para comunicar el concepto con estimaciones conservadoras iniciales.
try:
    scenario_config = load_yaml_config('scenarios')
    pain_ratio_diag = scenario_config.get('pain_ratio_default', 0.20)
    recovery_diag = scenario_config.get('recovery_factors', {}).get('realistic', 0.20)
except Exception:
    pain_ratio_diag = 0.20
    recovery_diag = 0.20

raw_monthly_loss = base_value  # fuga bruta mensual (monthly_loss_central)
effective_monthly_gain_diag = int(raw_monthly_loss * pain_ratio_diag * recovery_diag)

# 4 placeholders para el puente dual
placeholders['fuga_total_6m'] = format_cop(raw_monthly_loss * 6)
placeholders['recuperacion_proyectada_6m'] = format_cop(effective_monthly_gain_diag * 6)
placeholders['pain_pct'] = int(pain_ratio_diag * 100)
placeholders['recov_pct'] = int(recovery_diag * 100)
```

**Dónde exactamente**: justo antes de la línea donde se construye el `return` del dict. Verificar con:
```bash
grep -n 'def _build_financial_placeholders' modules/commercial_documents/v4_diagnostic_generator.py
# → L998. El return está aproximadamente en L1090-1100.
sed -n '1014,1020p' modules/commercial_documents/v4_diagnostic_generator.py
# → base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
```

**Criterios de aceptación**:
- [ ] `load_yaml_config('scenarios')` se llama exitosamente (YA se usa en L77 y L413)
- [ ] `format_cop` YA está importado y disponible en el scope
- [ ] Los 4 placeholders se agregan al dict antes del `return`
- [ ] Si `load_yaml_config` falla, los defaults 0.20/0.20 se usan como fallback
- [ ] `pain_pct` y `recov_pct` son enteros (20, no 20.0)

### Tarea 3: Replicar puente dual en template de propuesta

**Archivo**: `modules/commercial_documents/templates/propuesta_v6_template.md`

**Ubicación**: Sección de ROI/Recuperación, junto a la tabla de recuperación mensual.

**Variables YA disponibles en proposal generator** (gracias a FASE-A):
- `effective_monthly_gain` → L691 (`raw_monthly_loss * pain_ratio * recovery_realistic`)
- `raw_monthly_loss` → L679
- `pain_ratio` → L680 (viene de `pricing_result.pain_ratio`, ~0.41 para Castilla Real)
- `recovery_realistic` → L690

**Código a agregar en `_prepare_financial_template_vars()`** (L674-825, antes del return):
```python
# PROPUESTA-COMERCIAL FASE-B: Puente dual para trazabilidad financiera
placeholders['fuga_total_6m'] = format_cop(raw_monthly_loss * 6)
placeholders['recuperacion_proyectada_6m'] = format_cop(effective_monthly_gain * 6)
placeholders['pain_pct'] = int(pain_ratio * 100)
placeholders['recov_pct'] = int(recovery_realistic * 100)
```

**Nuevo bloque en el template** (formato reducido — la propuesta ya tiene la tabla detallada):
```markdown
> 📊 **Trazabilidad financiera**: La fuga total estimada es de ${fuga_total_6m} en 6 meses.  
> Con nuestro servicio, la recuperación proyectada es de ${recuperacion_proyectada_6m}  
> (${pain_pct}% del dolor priorizado × ${recov_pct}% de recuperación conservadora).
```

**Criterios de aceptación**:
- [ ] Bloque de trazabilidad visible en sección financiera de la propuesta
- [ ] No duplica la tabla de recuperación mensual existente — la complementa
- [ ] Los placeholders se agregan al dict existente (no se crea uno nuevo)

### Tarea 4: Verificar placeholders y coherencia narrativa

**Objetivo**: Confirmar que los 4 placeholders existen en ambos generadores y que los templates renderizan correctamente. Los valores NUMÉRICOS diferirán por diseño (diagnóstico usa defaults 20%/20%, propuesta usa pain_ratio real del pricing).

**Verificación de existencia**:
```bash
grep -n 'fuga_total_6m\|recuperacion_proyectada_6m\|pain_pct\|recov_pct' \
  modules/commercial_documents/v4_diagnostic_generator.py \
  modules/commercial_documents/v4_proposal_generator.py
```

**Verificación en templates**:
```bash
grep -n 'fuga_total_6m\|recuperacion_proyectada_6m\|pain_pct\|recov_pct' \
  modules/commercial_documents/templates/diagnostico_v6_template.md \
  modules/commercial_documents/templates/propuesta_v6_template.md
```

**Criterios de aceptación**:
- [ ] Los 4 placeholders existen en AMBOS generadores (8 asignaciones totales)
- [ ] Los 4 placeholders son referenciados en AMBOS templates
- [ ] Sin placeholders vacíos o sin asignar
- [ ] La divergencia numérica entre diagnóstico y propuesta es esperada y está explicada en el texto del template ("estimación conservadora inicial" vs "cálculo preciso")

---

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Placeholder rendering | `pytest tests/commercial_documents/ -v -k "placeholder or template" --timeout=60` | Sin regresiones |
| Validación rápida | `python scripts/run_all_validations.py --quick` | 4/4+ checks |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-B como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items B1-B4 como ✅
3. **`09-documentacion-post-proyecto.md`**: Agregar cambios en Secciones A, B
4. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "CROSS-1: Puente dual fuga bruta/recuperación efectiva en diagnóstico + propuesta (Opción C)" \
    --archivos-mod "modules/commercial_documents/templates/diagnostico_v6_template.md,modules/commercial_documents/templates/propuesta_v6_template.md,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Template diagnóstico: tabla dual con fuga total + recuperación proyectada
- [ ] Template diagnóstico: explicación narrativa del mecanismo pain_ratio × recovery_factor
- [ ] Template propuesta: bloque de trazabilidad financiera
- [ ] Generador diagnóstico: 4 placeholders desde `scenarios.yaml` (defaults 20%/20%)
- [ ] Generador propuesta: 4 placeholders desde `pricing_result.pain_ratio` (valor real del hotel)
- [ ] Placeholders existen en ambos generadores (verificación con grep)
- [ ] Divergencia numérica entre docs es esperada y documentada en el texto
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `scenario_calculator.py` ni el motor financiero
- NO ejecutar v4complete
- NO eliminar contenido existente de los templates — solo agregar
- Máximo 60 iteraciones de agente
- El formato de tabla markdown debe ser compatible con renderizado GitHub/Notion
