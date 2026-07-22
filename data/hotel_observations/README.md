# Hotel Observations

**Propósito:** Registro estructurado de observaciones operacionales reales de
hoteles individuales, recopiladas por contacto directo con el hotel o por
evidencia verificable (NO por inferencia web ni por benchmark regional).

**Caso de uso:** alimenta el motor financiero (`scenario_calculator.py`) con
datos Tier A (VERIFIED, confidence ≥0.9), en contraste con el Tier B
(ESTIMATED, benchmark regional) que usa `data/benchmarks/regional_adr_2026.json`.

---

## Por qué existe este directorio

`data/benchmarks/regional_adr_2026.json` representa el **segmento competitivo**
(lo que un hotel boutique_10_25 del Eje Cafetero DEBERÍA operar). NO
representa la realidad de un hotel específico que opera muy por debajo del
benchmark.

**Hallazgo validado contra código (2026-07-16, Hotel Luxor):**
aplicar benchmark regional a un hotel de paso sub-25 habitaciones produce
cifras de fuga financiera 5-15× mayores que las calculadas con datos reales
del hotel. Esto es un bug de modelo, no un bug de código.

Este directorio existe para acumular evidencia empírica de hoteles reales y,
cuando el patrón sea claro, alimentar la heurística
"hotel de paso vs destino" en el motor.

---

## Esquema

Validar contra `hotel_observations.schema.json` (JSON Schema Draft 2020-12).

### Campos canónicos (pedidos por el usuario)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `is_transit_hotel` | bool | ✅ | `true` = hotel de paso (baja rotación, baja ocupación, ADR bajo); `false` = hotel destino (alta rotación,ocupación media-alta) |
| `rooms` | int | ✅ | Número de habitaciones |
| `monthly_reservations` | int | ✅ | Reservas mensuales promedio |
| `avg_reservation_cop` | float | ✅ | Valor promedio por reserva en COP (NO ADR si hay segmentos, sí ADR si es single-rate) |
| `direct_channel_percentage` | float | ✅ | % de reservas que llegan por canal directo (web propia, walk-in, teléfono). Rango 0-100 |

### Campos derivados (consumibles por `scenario_calculator.py`)

Estos campos son DERIVADOS de los canónicos. Se incluyen en cada observación
para que el motor no tenga que recalcularlos y para que el JSON sea
self-contained.

| Campo | Tipo | Fórmula | Descripción |
|-------|------|---------|-------------|
| `occupancy_rate` | float | `monthly_reservations / (rooms × 30)` | Tasa de ocupación (0-1) |
| `adr_cop` | float | `= avg_reservation_cop` | ADR efectivo para el motor |
| `direct_channel_ratio` | float | `direct_channel_percentage / 100` | Versión ratio (0-1) para el motor |
| `ota_percentage` | float | `1.0 - direct_channel_ratio` | % implícito por OTAs |

### Campos de metadata (trazabilidad y calidad)

| Campo | Tipo | Obligatorio | Descripción |
|-------|------|-------------|-------------|
| `hotel_name` | string | ✅ | Nombre del hotel (slug o título) |
| `region` | string | ✅ | `eje_cafetero`, `caribe`, `antioquia`, `default` (debe matchear `regional_adr_2026.json`) |
| `category` | string | ✅ | `boutique_10_25` o `standard_26_60` (debe matchear benchmark) |
| `source` | string | ✅ | `contacto_directo`, `formulario_onboarding`, `evidencia_verificable` |
| `confidence` | float | ✅ | 0.0-1.0. `contacto_directo` con datos del dueño → 0.95. Inferencia → ≤0.7 |
| `epistemic_status` | string | ✅ | `verified` (Tier A) o `estimated` (Tier B/C) |
| `collected_at` | string (ISO 8601) | ✅ | Fecha de recolección |
| `notes` | string | ❌ | Contexto adicional (por qué se considera hotel de paso, etc.) |

---

## Convención de versionado

```json
{
  "version": "1.0.0",
  "last_updated": "2026-07-16",
  "source_role": "individual_hotel_observations",
  "epistemic_status_default": "verified",
  ...
}
```

`source_role` debe ser `individual_hotel_observations` para que el motor
pueda distinguirlo de `regional_benchmark` (usado por
`regional_adr_2026.json`).

---

## Validación

Antes de commit, validar con:

```bash
python3 scripts/validate.py
```

El script usa `Path(__file__).parent` para resolver rutas, así que funciona
desde cualquier cwd. Muestra el total de observaciones validadas y la fecha
de `last_updated`. Si hay errores, lista los primeros 10 con su path.

**Equivalente one-liner** (si prefieres no usar el script):

```bash
python3 -c "
import json
from jsonschema import Draft202012Validator
import pathlib
base = pathlib.Path('data/hotel_observations')
schema = json.load(open(base / 'hotel_observations.schema.json'))
data = json.load(open(base / 'observations.json'))
errors = list(Draft202012Validator(schema).iter_errors(data))
print('OK' if not errors else f'FAIL: {len(errors)} errors')
for e in errors[:3]: print(f'  - {e.message}')
"
```

Si `jsonschema` no está instalado:

```bash
# WSL (recomendado con PEP 668)
uv pip install --system jsonschema

# O dentro de un venv del proyecto
.venv/bin/pip install jsonschema
```

---

## Privacidad y uso ético

- **NO incluir datos personales del dueño/contacto** (nombre, email, teléfono
  directo). Solo datos operacionales agregados del hotel.
- **Pedir consentimiento** antes de registrar observaciones. Si el hotel
  entrega datos bajo acuerdo de confidencialidad, marcar
  `notes: "confidencialidad: <motivo>"` y excluir del dataset público.
- **No publicar el archivo** si contiene datos sensibles. Considerar moverlo
  a `data/hotel_observations/private/` si aplica.

---

## Procedimiento para agregar una observación

### Paso 1 — Recopilar los 5 datos canónicos

Usar el formulario estandarizado:
**`data/hotel_observations/forms/contact_form_ES.md`**

Resumen del formulario:
  1. ¿Cuántas habitaciones tiene en operación? → `rooms`
  2. ¿Cuántas reservas recibe en promedio al mes? → `monthly_reservations`
  3. ¿Cuál es el valor promedio por reserva en COP? → `avg_reservation_cop`
  4. ¿Qué % llega por canal directo (web propia, walk-in, teléfono)?
     → `direct_channel_percentage`
  5. ¿Hotel de paso o destino? → TÚ lo clasificas (NO preguntes al hotel)

**Reglas críticas:**
  - NO inferir occupancy de tráfico web (eso es `evidencia_verificable`,
    NO `contacto_directo`).
  - NO aceptar "estimación del gerente" como dato verificado.
  - Clasificar paso/destino con heurística occupancy + preguntas proxy
    (ver formulario).

### Paso 2 — Clasificar `is_transit_hotel`

Heurística objetiva (si tienes los 4 datos numéricos):
```
occupancy_rate = monthly_reservations / (rooms × 30)
Si occupancy < 15%  → probable paso
Si occupancy > 30%  → probable destino
Si 15-30%           → ambiguous, requiere preguntas proxy al hotel
```

**SIEMPRE documentar el criterio en `is_transit_hotel_basis`**
(mínimo 20 caracteres). El schema lo requiere cuando `is_transit_hotel=true`.

### Paso 3 — Calcular campos derivados

Estos campos se calculan automáticamente a partir de los canónicos:

```python
occupancy_rate       = monthly_reservations / (rooms * 30)
adr_cop              = avg_reservation_cop  # redundancia explícita
direct_channel_ratio = direct_channel_percentage / 100
ota_percentage       = 1.0 - direct_channel_ratio
```

**Puedes pre-calcularlos o dejar que el script de validación los
verifique.** El schema requiere consistencia (occupancy_rate calculado
debe coincidir ±0.001, lo mismo para ota_percentage).

### Paso 4 — Llenar metadata

Campos que NO salen del hotel sino del contexto de captura:

```json
{
  "hotel_name": "nombre-slug-del-hotel",
  "region": "eje_cafetero",        // debe matchear regional_adr_2026.json
  "category": "boutique_10_25",    // según rooms
  "source": "contacto_directo",
  "confidence": 0.95,              // 0.95 para contacto con dueño/gerente
  "epistemic_status": "verified",
  "collected_at": "2026-07-16",    // fecha de la llamada
  "notes": "Contexto opcional"
}
```

### Paso 5 — Agregar al JSON

**Opción A (recomendada) — usar el wizard:**

```bash
python3 scripts/add_observation.py
```

El wizard pregunta los 5 canónicos, calcula `occupancy_rate` y sugiere
clasificación paso/destino por heurística, exige `is_transit_hotel_basis`
si corresponde, calcula los 4 derivados, valida contra el schema, y guarda
en `observations.json` actualizando `last_updated` automáticamente.

**Opción B — manual:**

Abrir `observations.json`, agregar el objeto al final del array
`observations` (con coma separadora del elemento anterior). No olvidar
los 4 campos derivados.

**Actualizar `last_updated`** en el header del archivo a la fecha de hoy
(el wizard lo hace solo).

### Paso 6 — Validar antes de commit

```bash
python3 scripts/validate.py
```

### Paso 7 — Commit con mensaje descriptivo

```bash
git add data/hotel_observations/
git commit -m "data: add Hotel [Nombre] observation ([paso/destino], [N] hab)"
```

**NO commitear si la validación falla.** Corregir antes.

---

## Ejemplo completo (Hotel Luxor)

Para ver un ejemplo trabajado de cómo se ve una observación ya validada,
ver la entrada de `Hotel Luxor` en `observations.json`. Esa entrada es la
línea base contra la que se comparan las nuevas.

---

## Referencias

- **Formulario detallado:** `forms/contact_form_ES.md` — incluye guion
  de llamada, anti-patrones, criterios éticos.
- **Esquema:** `hotel_observations.schema.json` — contrato JSON Schema
  Draft 2020-12, valida invariantes.
- **Contexto del caso Luxor:** `.opencode/context/LUXOR-RECALIBRACION-FINANCIERA.md`
  — análisis que motivó este directorio.
- **FASE A — diseño experimental:** ver sección "Estado actual" abajo y
  `forms/contact_form_ES.md` §"Criterio de parada".

---

## Estado actual

**Versión:** 1.0.0
**Última actualización:** 2026-07-22
**Observaciones registradas:** 6 (Hotel Luxor + 5 hoteles Pereira)
**Estado:** Esquema definido, primera observación cargada, formulario
estandarizado disponible, scripts de validación y captura wizard
disponibles, pendiente FASE A de benchmarking (N=5 hoteles) antes de
extraer patrón. **Decisión 2026-07-16:** iniciar FASE A con N=5 (NOT N≥10)
— el test de Fase A es binario y con efecto grande esperado, 5 hoteles
son suficientes. Detalles en `forms/contact_form_ES.md` §"Criterio de
parada de FASE A".

---

## Relación con otros archivos del proyecto

| Archivo | Relación |
|---------|----------|
| `data/benchmarks/regional_adr_2026.json` | Este directorio lo complementa con datos individuales |
| `modules/financial_engine/scenario_calculator.py` | Consumidor futuro (hoy solo consume benchmark) |
| `agent_harness/memory.py` | Cache de sesión; este archivo es la fuente durable |
| `.opencode/context/LUXOR-RECALIBRACION-FINANCIERA.md` | Análisis del caso Luxor que motivó este directorio |
| `scripts/validate.py` | Validador portable (Draft 2020-12) del archivo `observations.json` |
| `scripts/add_observation.py` | Wizard interactivo para agregar observaciones con cálculo de derivados y validación |