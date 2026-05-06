# Prompt de Inicio de Sesion — FASE-REFACTOR-CTA-A (Fix Codigo + Tests)

## Contexto

En el diagnostico v4, cuando un hotel esta en **Tier C** (datos limitados), el CTA de onboarding promete "datos reales" pero **no especifica cuales son**. El hotelero no sabe que informacion preparar.

**Texto actual (v4_diagnostic_generator.py:1108-1112):**
```python
show_onboarding_cta = (
    "\n> **Quiere saber su cifra exacta?** "
    "Complete el [onboarding con sus datos reales] "
    "para ver el calculo preciso de su perdida mensual.\n"
)
```

**Los 4 datos minimos que el onboarding solicita** (`modules/onboarding/forms.py`):
1. `habitaciones` — Numero de habitaciones del hotel
2. `reservas_mes` — Reservas mensuales promedio
3. `valor_reserva_cop` — Valor promedio de reserva (COP)
4. `canal_directo_pct` — Porcentaje de reservas por canal directo

## Tareas Especificas

### Tarea 1: Refactorizar el CTA en el generador

**Archivo:** `modules/commercial_documents/v4_diagnostic_generator.py`  
**Lineas:** ~1108-1112

Reemplazar el string `show_onboarding_cta` por uno que liste explicitamente los 4 datos. Texto objetivo:

```python
show_onboarding_cta = (
    "\n> **Quiere saber su cifra exacta?** "
    "Complete el onboarding con sus datos reales: "
    "numero de habitaciones, reservas mensuales promedio, "
    "valor promedio de reserva (COP) y porcentaje de canal directo. "
    "Asi podra ver el calculo preciso de su perdida mensual.\n"
)
```

**Reglas del fix:**
- Mantener formato Markdown (`> **bold**`)
- No usar links `[...]` si no son funcionales
- Mantener `\n` inicial y final
- Texto claro, ~2 lineas maximo

### Tarea 2: Actualizar tests

**Archivo:** `tests/commercial_documents/test_precision_rendering.py`  
**Metodo:** `test_tier_c_shows_onboarding_cta` (lineas ~204-217)

Actualizar assertions para verificar que el CTA contiene los 4 datos especificos:

```python
def test_tier_c_shows_onboarding_cta(self):
    """Tier C: CTA de onboarding presente y especifico."""
    gen = V4DiagnosticGenerator()
    scenarios = make_scenarios()
    validation_summary = make_validation_summary_tier_c()

    result = gen._prepare_financial_template_vars(
        scenarios, validation_summary, analytics_data=None,
    )

    cta = result['show_onboarding_cta']
    assert cta != ''
    assert 'onboarding' in cta.lower()
    assert 'Quiere saber su cifra exacta' in cta
    # Verificar que los 4 datos requeridos estan mencionados
    assert 'habitaciones' in cta.lower()
    assert 'reservas' in cta.lower()
    assert 'reserva' in cta.lower()
    assert 'canal directo' in cta.lower()
```

### Tarea 3: Ejecutar tests

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_precision_rendering.py -v
```

Verificar:
- `test_tier_c_shows_onboarding_cta` PASA
- Todos los demas tests de ese archivo PASAN
- Si falla, corregir antes de continuar

### Tarea 4: Actualizar plan de fase

- Marcar T1-T3 como completadas en este prompt
- Estado de fase: **COMPLETADA** o **INCOMPLETA** con checkpoint

## Criterios de Completitud

- [x] El CTA en `v4_diagnostic_generator.py` menciona explicitamente los 4 datos del onboarding
- [x] Los tests en `test_precision_rendering.py` validan la presencia de esos 4 datos
- [x] Todos los tests de `test_precision_rendering.py` pasan (12/12 PASS)

## Restricciones

- **Maximo 60 iteraciones** por sesion (R2)
- **No ejecutar v4complete** — esta fase es puramente codigo+tests
- **No modificar ROADMAP.md**
- Backwards compatibility: solo cambio de string

## Archivos Involucrados

| Archivo | Tipo de Cambio | Lineas Aprox |
|---------|----------------|--------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Modificacion | 1108-1112 |
| `tests/commercial_documents/test_precision_rendering.py` | Modificacion | ~204-217 |

## Post-Ejecucion

1. Marcar esta fase como ✅ en `.opencode/plans/06-checklist-implementacion.md`
2. Anotar estado: completada o incompleta con checkpoint
3. La siguiente sesion ejecutara **FASE-REFACTOR-CTA-B** (v4complete + verificacion)
