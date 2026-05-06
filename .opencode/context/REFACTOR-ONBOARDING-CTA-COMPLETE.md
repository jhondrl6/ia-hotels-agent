# CONTEXTO: Refactorización del CTA de Onboarding en Diagnóstico Tier C

## Problema

**Línea 120 del documento generado:**  
```
> **¿Quiere saber su cifra exacta?** Complete el [onboarding con sus datos reales] para ver el cálculo preciso de su pérdida mensual.
```

**Pregunta legítima del hotelero:** *"¿Qué datos reales debo suministrar?"*

El CTA promete "datos reales" pero **no especifica cuáles son**. El hotelero no sabe qué información necesita preparar.

---

## Mapa de Código Relevant

### 1. Origen del Texto Problemático

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py`  
**Líneas:** 1108-1112

```python
show_onboarding_cta = (
    "\n> **¿Quiere saber su cifra exacta?** "
    "Complete el [onboarding con sus datos reales] "
    "para ver el cálculo preciso de su pérdida mensual.\n"
)
```

Este texto se inyecta en el template `diagnostico_v6_template.md` en la línea 88:
```
${show_onboarding_cta}
```

### 2. Datos Reales que el Onboarding Solicita

**Archivo:** `modules/onboarding/forms.py` (líneas 47-72)

| Campo interno | Pregunta CLI | Tipo | Rango |
|---------------|--------------|------|-------|
| `habitaciones` | "Número de habitaciones del hotel" | int | 1-500 |
| `reservas_mes` | "Reservas mensuales promedio" | int | 1-10,000 |
| `valor_reserva_cop` | "Valor promedio de reserva (en COP)" | int | $50,000-$5,000,000 |
| `canal_directo_pct` | "Porcentaje de reservas por canal directo" | float | 0-100% |

**Validadores:** `modules/onboarding/validators.py` (líneas 13-138)

### 3. Mapeo: Onboarding → Cálculo Financiero

**En `main.py` (líneas 1598-1614):**

```
datos_operativos.habitaciones      → rooms
datos_operativos.reservas_mes      → occupancy_rate = reservas_mes / (habitaciones * 30)
datos_operativos.valor_reserva_cop → adr_cop
datos_operativos.canal_directo_pct → direct_channel_pct = canal_directo_pct / 100
```

**Para que `can_show_exact=True` (Tier A/B), se necesitan:**
- `adr_cop` (del campo `valor_reserva_cop`)
- `occupancy_rate` (calculada desde `reservas_mes / habitaciones * 30`)
- `direct_channel_percentage` (calculado desde `canal_directo_pct / 100`)

### 4. Lógica de Tier y Exactitud

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1037-1115)

- **Default:** `precision_tier = "C"`, `can_show_exact = False`
- **Para Tier A/B:** `PrecisionValidator.validate()` debe retornar `can_show_exact_money = True`
- **PrecisiónValidator usa:** `adr_cop`, `occupancy_rate`, `direct_channel_percentage`

**Archivo:** `modules/financial_engine/precision_validator.py` (líneas 19-58)

```python
result = PrecisionValidator.validate(
    adr_cop=float(adr_cop),
    adr_source=adr_source,
    occupancy_rate=float(occupancy_rate),
    occupancy_source=occupancy_source,
    direct_channel_pct=float(direct_channel_pct),
    channel_source=channel_source,
)
precision_tier = result.precision_tier
can_show_exact = result.can_show_exact_money
```

### 5. Estructura del Template

**Archivo:** `modules/commercial_documents/templates/diagnostico_v6_template.md`

Líneas clave:
- L88: `${show_onboarding_cta}` — donde se inyecta el CTA problemático
- L113-118: Leyenda de Tier A/B/C
- L120: `${estimate_footnote}` — nota adicional de precisión

---

## Flujo Completo de Datos

```
Hotelero ejecuta onboarding CLI
    │
    ▼
modules/onboarding/forms.py::OnboardingForm.run_interactive()
    - Captura: habitaciones, reservas_mes, valor_reserva_cop, canal_directo_pct
    │
    ▼
main.py::v4_financial_calculation (AgentTask payload)
    - rooms = habitaciones
    - occupancy_rate = reservas_mes / (habitaciones * 30)
    - direct_channel_pct = canal_directo_pct / 100
    - adr_cop = valor_reserva_cop
    │
    ▼
main.py (líneas 1711-1717)
    - financial_sources = { adr_cop, occupancy_rate, direct_channel_percentage }
    │
    ▼
v4_diagnostic_generator.py::_build_financial_placeholders()
    - Usa PrecisionValidator.validate() → precision_tier + can_show_exact
    - Si can_show_exact=False → muestra show_onboarding_cta (líneas 1108-1112)
    │
    ▼
Template diagnostico_v6_template.md
    - ${show_onboarding_cta} en línea 88
    - "Complete el [onboarding con sus datos reales] para ver el cálculo preciso"
```

---

## Evidence Tier Classification

**Archivo:** `modules/commercial_documents/data_structures.py` (líneas 126-139)

```python
class EvidenceTier(Enum):
    A = "A"  # GA4 + GSC conectados — datos verificables
    B = "B"  # Benchmarks regionales + scraping — estimado con base
    C = "C"  # Solo scraping básico — estimado con baja confianza
```

**El Tier C se asigna cuando NO hay datos de validación suficientes.**

---

## Referencias Adicionales

- **Evidence Tiers:** `modules/commercial_documents/data_structures.py` líneas 126-140
- **Precision Validator:** `modules/financial_engine/precision_validator.py`
- **NoDefaults Validator:** `modules/financial_engine/no_defaults_validator.py`
- **Dynamic Impact Calculator:** `modules/utils/dynamic_impact.py` (líneas 45-105)
- **Template del Diagnóstico:** `modules/commercial_documents/templates/diagnostico_v6_template.md`

---

## Fix Requerido

**Objetivo:** Que el CTA de Tier C **liste explícitamente los 4 datos** que el hotelero debe suministrar.

**Cambio probable en:**
- `v4_diagnostic_generator.py` líneas 1108-1112
- Opcionalmente en `modules/commercial_documents/templates/diagnostico_v6_template.md` línea 120 (`${estimate_footnote}`)

**Verificación de impacto:**
- Si se agregan los 4 datos al CTA, ¿cambia la estructura del template o solo el texto?
- ¿Hay tests que validen el texto exacto del CTA?

---

## Notas para la Sesión de Refactorización

1. **No es solo un fix de texto** — el problema es que el documento promete "datos reales" sin especificar cuáles
2. **Los 4 datos son los mínimos** para que `can_show_exact=True` (Tier B+)
3. **El fix debe responder la pregunta del hotelero** antes de que la haga
4. **Verificar que no haya broken links** — el texto dice `[onboarding con sus datos reales]` pero no es un link funcional
