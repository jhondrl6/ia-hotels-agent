# 05-prompt-inicio-sesion-fase-FIN-3

**Fase**: FIN-3 — Rendering: Rangos, Advertencias y CTA  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-1A ✅, FIN-1B ✅, FIN-2A ✅, FIN-2B ✅  
**Bloquea a**: CHAN-1  

---

## Objetivo

Modificar el generador de diagnóstico (`v4_diagnostic_generator.py`) y las templates para que:
- Tier C/B → mostrar **rango** (no cifra exacta)
- Tier C/B → mostrar **advertencia** visible sobre fuente de datos
- Tier C/B → mostrar **CTA** para completar onboarding
- Nunca mostrar desglose con falsa precisión cuando `can_show_exact_money=False`

---

## Contexto de Fases Anteriores

- FIN-1A/B: `PrecisionTier`, `can_show_exact_money`, `PrecisionValidator` existen
- FIN-2A/B: `ADRResolutionResult` ya propaga `epistemic_status` y `can_show_exact`
- El generador actual ya usa `_compute_opportunity_scores()` y tiene variables de template

---

## Tareas

### T1: Investigar flujo de render financiero actual

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

- Leer `_compute_financial_scenarios()` o método equivalente que genera `financial_scenarios.json`
- Identificar dónde se pasan variables al template (ej: `${monthly_loss}`, `${adr_cop}`)
- Identificar la template de diagnóstico (probablemente `diagnostico_v6_template.md`)
- Verificar qué variables financieras recibe actualmente la template

**Archivo**: Templates en `modules/commercial_documents/templates/`

- Buscar `${monthly_loss}`, `${adr_cop}`, `${monthly_loss_cop}` u otras variables financieras
- Identificar dónde se renderiza la cifra de pérdida mensual
- Identificar formato actual del bloque financiero

### T2: Modificar `v4_diagnostic_generator.py`

Inyectar nuevas variables de template basadas en `PrecisionValidator`:

```python
from modules.financial_engine.precision_validator import PrecisionValidator
from modules.financial_engine.financial_evidence import EpistemicStatus

# En el método que prepara template_vars:
def _prepare_financial_template_vars(self, financial_scenarios, adr_result):
    # Validar precisión
    precision = PrecisionValidator.validate(
        adr_cop=adr_result.adr_cop,
        adr_source=adr_result.source,
        occupancy_rate=financial_scenarios.get("occupancy_rate", 0.5),
        occupancy_source=financial_scenarios.get("occupancy_source", "default"),
        direct_channel_pct=financial_scenarios.get("direct_channel", 0.2),
        channel_source=financial_scenarios.get("channel_source", "default"),
    )

    # Determinar si mostrar rango o cifra exacta
    if precision.can_show_exact_money:
        monthly_loss_display = f"${monthly_loss:,.0f} COP/mes".replace(",", ".")
        precision_badge = ""
    else:
        # Calcular rango: conservador → realista → optimista
        conservative = monthly_loss * 0.85
        optimistic = monthly_loss * 1.15
        monthly_loss_display = f"~${conservative:,.0f}–${optimistic:,.0f} COP/mes".replace(",", ".")
        precision_badge = self._build_precision_warning(precision)

    return {
        "monthly_loss_display": monthly_loss_display,
        "precision_tier": precision.precision_tier,
        "can_show_exact_money": precision.can_show_exact_money,
        "precision_warning": precision_badge,
        "adr_source_label": self._source_label(adr_result.epistemic_status),
        "show_onboarding_cta": precision.precision_tier in ("B", "C"),
        "financial_disclaimer": self._build_disclaimer(precision),
    }
```

Helper `_build_precision_warning()`:

```python
def _build_precision_warning(self, precision) -> str:
    if precision.precision_tier == "A":
        return ""
    
    lines = [
        "⚠️ **IMPORTANTE**: Esta estimación es preliminar.",
        "",
        "Base de cálculo:",
    ]
    for field, status in precision.field_epistemic.items():
        label = {"adr_cop": "ADR", "occupancy_rate": "Ocupación", 
                  "direct_channel_percentage": "Canal directo"}.get(field, field)
        source_note = {
            EpistemicStatus.REGIONAL_BENCHMARK: "benchmark regional (no dato confirmado del hotel)",
            EpistemicStatus.DEFAULTED: "default del sistema (no dato real)",
            EpistemicStatus.OBSERVED: "extraído de web (no confirmado por el hotel)",
        }.get(status, "fuente no verificada")
        lines.append(f"- **{label}**: {source_note}.")
    
    lines.extend([
        "",
        "📋 **Para convertir esta estimación en proyección exacta:**",
        "1. Confirme su tarifa promedio real",
        "2. Confirme su ocupación mensual",
        "3. Indique su porcentaje de reservas directas vs OTA",
    ])
    return "\n".join(lines)
```

### T3: Actualizar templates

**Archivos**: Templates de diagnóstico y propuesta en `modules/commercial_documents/templates/`

- Reemplazar `${monthly_loss}` (o equivalente) por `${monthly_loss_display}`
- Agregar bloque condicional para `${precision_warning}` (solo visible si Tier B/C)
- Agregar bloque condicional para CTA de onboarding
- Si hay desglose línea por línea (ej: "$530.613, $212.193..."), wrappearlo en condicional `${can_show_exact_money}`

Buscar en templates:
```bash
grep -rn "monthly_loss\|adr_cop\|perdida estimada" modules/commercial_documents/templates/
```

### T4: Tests de render

**Archivo**: `tests/commercial_documents/test_precision_rendering.py` (NUEVO)

Mínimo 6 tests:
1. `test_tier_a_shows_exact_money` → Sin advertencia, cifra exacta
2. `test_tier_c_shows_range_not_exact` → Rango "~$X–$Y", no cifra puntual
3. `test_tier_c_shows_warning` → Bloque de advertencia presente
4. `test_tier_c_shows_onboarding_cta` → CTA de onboarding presente
5. `test_regional_benchmark_source_label` → "benchmark regional" en label
6. `test_template_vars_injected_correctly` → Variables en template_vars dict

---

## Criterios de Completitud

- [ ] `v4_diagnostic_generator.py` inyecta `monthly_loss_display`, `precision_tier`, `can_show_exact_money`, `precision_warning`, `show_onboarding_cta`
- [ ] Templates actualizadas con nuevas variables
- [ ] Tier A → cifra exacta sin advertencia
- [ ] Tier B/C → rango + advertencia + CTA
- [ ] Nunca desglose arbitrario cuando `can_show_exact_money=False`
- [ ] `tests/commercial_documents/test_precision_rendering.py` ≥6 tests pasando
- [ ] Tests existentes de diagnostic generator sin regresiones

---

## Restricciones

- Máximo 60 iteraciones
- **NO ejecutar `v4complete`** (eso es FIN-4)
- **NO modificar `OpportunityScorer`** (CHAN-2)
- **NO tocar `feature_flags.py`**
- Templates deben mantener compatibilidad con Tier A (sin cambios visuales para datos reales)

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-3 \
    --desc "Rendering financiero: rangos, advertencias y CTA según precision tier" \
    --archivos-nuevos "tests/commercial_documents/test_precision_rendering.py" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/" \
    --tests "6" \
    --check-manual-docs
```
