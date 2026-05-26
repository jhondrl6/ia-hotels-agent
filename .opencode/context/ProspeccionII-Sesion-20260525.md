# Sesión: ProspecciónII.md — 4 patches + raíz "Comparan en reserva"

**Fecha**: 2026-05-25  
**Proyecto**: iah-cli · v4.52.0 DIAGNOSTIC-ALIGNMENT  
**Archivos tocados**: `v4_diagnostic_generator.py`, `diagnostico_v6_template.md`, `content_scrubber.py`, `v4_proposal_generator.py`

---

## Hallazgos de ProspecciónII.md

ProspecciónII.md contenía 5 observaciones de pulido sobre el output del diagnóstico.
La investigación demostró que 4 de las 5 eran patches directos, y que la #2 (reserva) tenía una causa raíz sistémica.

| # | Observación | Fuente | Acción | Estado |
|---|-------------|--------|--------|--------|
| 1 | Probabilidades 70/20/10 → etiquetas descriptivas | `v4_diagnostic_generator.py` L966-968 | Cambiar "Conservador/Realista/Optimista" → "Mínimo garantizable/Más probable/Máximo alcanzable" | ✅ Aplicado |
| 2 | "Comparan en reserva" truncado | Template ≠ output (Template OK, output corrupto) | **RAÍZ**: `content_scrubber.py` L53 `"booking": "reserva"` — aplicar fix y re-test | ✅ Aplicado |
| 3 | Quick Win #3 jerga técnica | `v4_diagnostic_generator.py` L1636 | Reformular a lenguaje comercial | ✅ Aplicado |
| 4 | "Perdida" sin tilde → "Pérdida" | 2 archivos `.py` (L2754 diag_gen, L193 proposal_gen) | Parchear tildes | ✅ Aplicado |
| 5 | Brecha 5 "IA Bloqueada" vs "IA sin guía" | Ya corregido en FASE-B de DIAGNOSTIC-ALIGNMENT | N/A — observación obsoleta | ✅ N/A |

---

## Patch 1: Escenario labels

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Líneas 965-969** (antes):
```python
("Conservador", cons_val, scenarios.conservative.probability),
("Realista",   real_val, scenarios.realistic.probability),
("Optimista",  opt_val,  scenarios.optimistic.probability),
```

**Después**:
```python
("Mínimo garantizable", cons_val, scenarios.conservative.probability),
("Más probable",        real_val, scenarios.realistic.probability),
("Máximo alcanzable",   opt_val,  scenarios.optimistic.probability),
```

**Verificación**: Output L214-216 muestra las nuevas etiquetas correctamente. Coherence 0.83, sin regresiones.

---

## Patch 2: Raíz de "Comparan en reserva" — CRÍTICO (sistémico)

### Problema
El template (`diagnostico_v6_template.md`) siempre tuvo la cadena correcta `Comparan en Booking`. Sin embargo, el output del diagnóstico mostraba `Comparan en reserva.com` y `comparan en reserva.com` en múltiples lugares. No había ningún archivo `.py` que contuviera "Comparan en reserva" — ni en git history.

### Causa raíz: `content_scrubber.py` EN_TO_ES

**Archivo**: `modules/postprocessors/content_scrubber.py`

Línea 53 original:
```python
EN_TO_ES = {
    "guests": "huéspedes",
    "guest": "huésped",
    "booking": "reserva",   # ← ESTE ERA EL PROBLEMA
    "checkin": "check-in",
    ...
}
```

El `_fix_mixed_language()` de ContentScrubber aplica `re.sub(r'\bbooking\b', 'reserva')` en todo el documento post-generación. Esto significa:

- `"Booking.com"` → `"reserva.com"` (contexto de marca destruido)
- `"Booking"` (solo) → `"reserva"` (palabra generica corrompida)
- Este es un **bug sistémico** — afecta a cualquier documento comercial generado por el pipeline

### Fix aplicado
```python
# NOTE: "booking" intentionally excluded — Booking is a brand name, not a generic English word
# in Spanish hotel marketing contexts, "Booking" is the recognized platform name
```

Se eliminó `"booking": "reserva"` del diccionario EN_TO_ES en `content_scrubber.py`.

**También verificar**: `modules/postprocessors/document_quality_gate.py` L56 tiene la misma entrada `"booking": "reserva"` — misma corrección requerida. La cadena EN_TO_ES está duplicada entre ambos archivos.

### Verificación
- v4complete #1 (20:05): Output corrupto — `reserva.com` y `reserva` para Booking
- v4complete #2 (20:07): Output limpio — `Comparan en Booking` y `Booking.com` ✅
- SCRUB log ahora solo muestra 2 fixes (COP COP + passo) — sin "booking → reserva"

---

## Patch 3: Quick Win #3 lenguaje comercial

**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Línea 1636** (antes):
```python
f"{win_number}. **DELEGAR A IA HOTELES AGENT: Configurar Schema de Hotel + FAQ en su web.** "
```

**Después**:
```python
f"{win_number}. **DELEGAR A IA HOTELES AGENT: Hacer que Google muestre sus preguntas frecuentes y datos del hotel en los resultados de búsqueda.** "
```

**Verificación**: Output L125 y L249 muestran la nueva versión comercial ✅

---

## Patch 4: Tilde "Pérdida"

**Archivos**: `v4_diagnostic_generator.py` L2754, `v4_proposal_generator.py` L193

| Archivo | Línea | Antes | Después |
|---------|-------|-------|---------|
| `v4_diagnostic_generator.py` | 2754 | `Perdida absoluta de reservas de IA` | `Pérdida absoluta de reservas de IA` |
| `v4_proposal_generator.py` | 193 | `"monetizacion": "Perdida de reservas moviles"` | `"monetizacion": "Pérdida de reservas moviles"` |

**Nota**: `v4_diagnostic_generator.py` L993-996 ya tenía labels correctos con tilde ("Pérdida Mensual Estimada"). Solo las dos strings de detalle/valorization estaban sin tilde.

**Verificación**: Output L47 y L241 muestran "Pérdida" con tilde ✅

---

## Bug conocido: TypeError en commercial_gate.py

**Archivo**: `modules/quality_gates/commercial_gate.py` L279

```
TypeError: '<' not supported between instances of 'Scenario' and 'Scenario'
  at _check_scenario_order()
```

**Contexto**: El escenario "optimista" de Hotel Castilla Real tiene valor negativo (-$270,950 COP/mes — representa equilibrio/ganancia). El gate `_check_scenario_order()` intenta comparar `optimistic < realistic` para validar el orden de escenarios, pero la comparación de objetos `Scenario` no está definida.

**Impacto**: No bloquea la ejecución — el error ocurre dentro del `validate_diagnostic()` pero el pipeline continúa y genera coherencia 0.83. El gate validation continúa aunque este check falle.

**Severidad**: MEDIA — no bloquea delivery, pero indica deuda técnica en el ordenamiento de escenarios.

**Para investigar**: Comparar cómo se comparan escenarios en `calculator_v2.py` vs `commercial_gate.py`. El fix probablemente requiere implementar `__lt__` en la clase `Scenario` o hacer la comparación en los valores numéricos (monthly_loss_central) en vez de los objetos.

---

## Dependencias pendientes

1. **`document_quality_gate.py` L56**: Mismo `"booking": "reserva"` en el EN_TO_ES local de ese archivo. Verificar si el scrubber en ese módulo también corrompe "Booking" o si es un diccionario independiente que no se usa.

2. **TypeError commercial_gate.py**: Investigar y corregir `_check_scenario_order()` para manejar escenarios con valores negativos.

---

## Para re-testear en próxima sesión

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Verificar que EN_TO_ES en content_scrubber.py ya no tiene "booking"
grep "booking" modules/postprocessors/content_scrubber.py

# Verificar que document_quality_gate.py no tiene el mismo problema
grep "booking" modules/postprocessors/document_quality_gate.py

# Run de validación rápida
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Ejecutar v4complete de prueba
./venv/Scripts/python.exe main.py v4complete --url "https://www.hotelcastillareal.com/" --output output/v4_complete

# Verificar output limpio
grep "Comparan en" output/v4_complete/v4_complete/01_DIAGNOSTICO_*.md | tail -3
grep "Mínimo garantizable" output/v4_complete/v4_complete/01_DIAGNOSTICO_*.md | tail -3
```