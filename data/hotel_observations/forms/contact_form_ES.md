# Formulario de Recolección — Hotel Observations (FASE B)

**Propósito:** Estandarizar la captura de datos operacionales de hoteles
vía contacto directo (dueño, gerente, o administrador). FASE B extiende
el formulario FASE A con 3 preguntas adicionales para refinar la
clasificación paso/destino.

**Destino final:** este JSON se pega en
`data/hotel_observations/observations.json` como una nueva entrada del array
`observations`, adaptando los valores al schema.

---

## Antes de la llamada (preparación)

  1. Verifica que el hotel cumple el criterio de inclusión:
     - ¿Tiene ≤60 habitaciones? (boutique_10_25 o standard_26_60)
     - ¿Puedes obtener datos REALES, no estimados?

  2. Prepara contexto para el hotel (sin revelar el benchmark):
     - "Estamos caracterizando el mercado hotelero colombiano con datos
       reales para mejorar nuestras recomendaciones."
     - NO menciones: benchmark regional, occupancy, ratios.
     - NO reveles: que el hotel es "de paso" o "destino" — eso lo decides TÚ
       después con datos.

  3. Ten a mano el JSON template de abajo (en portapapeles o impreso).

---

## El formulario (lo que preguntas)

### Bloque A — Datos operacionales (5 preguntas, igual que FASE A)

| # | Pregunta al hotel | Campo JSON | Tipo | Ejemplo |
|---|-------------------|------------|------|---------|
| 1 | ¿Cuántas habitaciones tiene en operación? | `rooms` | int | `21` |
| 2 | En promedio, ¿cuántas reservas recibe al mes? | `monthly_reservations` | int | `15` |
| 3 | ¿Cuál es el valor promedio por reserva en COP? | `avg_reservation_cop` | float | `200000` |
| 4 | De cada 10 reservas, ¿cuántas llegan por canal directo (su web, walk-in, teléfono)? | `direct_channel_percentage` | float | `60.0` |
| 5 | ¿Su hotel es más de "paso" (viajeros que paran una noche de camino a otro destino) o más "destino" (viajeros que vienen específicamente a quedarse)? | `is_transit_hotel` (TÚ) | bool | decisión tuya |

### Bloque B — Datos FASE B (3 preguntas nuevas)

| # | Pregunta al hotel | Campo JSON | Tipo | Ejemplo |
|---|-------------------|------------|------|---------|
| 6 | En promedio, ¿cuántas noches se quedan sus huéspedes? | `avg_stay_nights` | float | `1.5` |
| 7 | ¿Cuál es el motivo principal por el que se hospedan? (negocios, turismo, tránsito de camino a otro lugar, o una mezcla) | `trip_purpose` | enum | `negocios` |
| 8 | Si usted tuviera que decirlo, ¿su hotel es más de paso o destino? | `hotel_self_label` | enum | `paso` |

**Notas sobre las preguntas FASE B:**

- **Pregunta 6** — NO preguntes "¿cuántas noches máximo?". Necesitas el
  PROMEDIO. Si el hotel dice "de 1 a 5 noches", pregunta "¿y en promedio
  cuántas noches se quedan?". Si no sabe, pide el dato del PMS o sugiere
  que revise las últimas 20 reservas.

- **Pregunta 7** — Acepta la respuesta tal como la da el hotel. Si dice
  "la mayoría viene por negocios" → `negocios`. Si dice "mitad y mitad" →
  `mixto`. Si dice "son personas que van de camino a Salento" → `transito`.
  NO sugieras opciones — deja que el hotel describa.

- **Pregunta 8** — Esta pregunta se hace DESPUÉS de las 7 anteriores, para
  no influir en las respuestas. Es la auto-etiqueta del hotel. Se captura
  pero NO se usa como input primario — la heurística v2 la usa solo como
  tiebreaker cuando los datos objetivos son ambiguos.

### Pregunta 5 — Clasificación paso/destino (TÚ, no el hotel)

NO preguntes al hotel "¿es de paso?". En su lugar, usa estas 2-3 preguntas
proxy y clasifica TÚ después:

| Pregunta proxy al hotel | Si respuesta típica... |
|-------------------------|------------------------|
| ¿Cuál es la duración promedio de estancia de sus huéspedes? | 1 noche → paso; 2+ noches → destino |
| ¿Los huéspedes preguntan por atracciones locales antes de reservar? | No → paso; Sí → destino |
| ¿Recibe huéspedes en días laborales o solo fines de semana/festivos? | Solo festivos → destino; cualquier día → paso |

### Bloque C — Metadata (la llenas TÚ, no el hotel)

| Campo JSON | Valor |
|------------|-------|
| `hotel_name` | nombre del hotel (slug) |
| `region` | `eje_cafetero`, `caribe`, `antioquia`, o `default` |
| `category` | `boutique_10_25` si rooms ≤ 25; `standard_26_60` si 26-60 |
| `source` | `contacto_directo` |
| `confidence` | `0.95` para contacto directo con dueño/gerente |
| `epistemic_status` | `verified` |
| `collected_at` | fecha de la llamada en formato `YYYY-MM-DD` |
| `is_transit_hotel_basis` | justificación textual de la clasificación paso/destino |
| `notes` | contexto adicional (opcional) |

---

## Template JSON (copia y adapta)

Copia este bloque, reemplaza los valores, y agrégalo al array `observations`
en `data/hotel_observations/observations.json`. **O usa el wizard
interactivo** (recomendado): `python3 scripts/add_observation.py` — calcula
los derivados, valida contra el schema, y guarda por ti.

```json
{
  "hotel_name": "NOMBRE_DEL_HOTEL_SLUG",
  "is_transit_hotel": true,
  "is_transit_hotel_basis": "JUSTIFICACIÓN_TEXTUAL. Mínimo 20 caracteres.",
  "rooms": 0,
  "monthly_reservations": 0,
  "avg_reservation_cop": 0,
  "direct_channel_percentage": 0.0,
  "avg_stay_nights": 1.0,
  "trip_purpose": "negocios",
  "hotel_self_label": "paso",
  "occupancy_rate": 0.0,
  "adr_cop": 0,
  "direct_channel_ratio": 0.0,
  "ota_percentage": 0.0,
  "region": "eje_cafetero",
  "category": "boutique_10_25",
  "source": "contacto_directo",
  "confidence": 0.95,
  "epistemic_status": "verified",
  "collected_at": "YYYY-MM-DD",
  "notes": "Contexto adicional opcional."
}
```

**Sí incluye los campos derivados** (`occupancy_rate`, `adr_cop`,
`direct_channel_ratio`, `ota_percentage`). El schema los trata como
`properties` opcionales pero los usa en las invariantes `allOf` (líneas
162-183): si los incluyes, deben coincidir con los canónicos ±tolerancia.
El wizard los calcula automáticamente; si pegas este template a mano,
calcula con:

```python
occupancy_rate       = monthly_reservations / (rooms * 30)
adr_cop              = avg_reservation_cop  # redundancia explicita
direct_channel_ratio = direct_channel_percentage / 100
ota_percentage       = 1.0 - direct_channel_ratio
```

---

## Después de la llamada (validación)

Una vez tengas el JSON adaptado:

  1. **Opción recomendada** — usa el wizard interactivo que calcula derivados
     y valida automáticamente:

     ```bash
     python3 scripts/add_observation.py
     ```

     Te pregunta los 5 canónicos + los 3 FASE B, calcula occupancy, sugiere
     clasificación paso/destino por heurística v2, pide
     `is_transit_hotel_basis` si es necesario, muestra preview, y guarda en
     `observations.json`.

  2. **Opción manual** — si prefieres pegar el JSON a mano:

     1. Ábrelo en un editor que valide JSON (VSCode con extensión, o jq).
     2. Pégalo al final del array `observations` en
        `data/hotel_observations/observations.json` (separado por coma del
        elemento anterior).
     3. Actualiza `last_updated` en el header del archivo a la fecha de hoy.

  3. Valida el archivo completo con:

     ```bash
     python3 scripts/validate.py
     ```

     El script usa `Path(__file__).parent` para resolver rutas, así que
     funciona desde cualquier cwd. No requiere rutas absolutas.

  4. Si validación OK, commit con mensaje descriptivo:
     `data: add Hotel [Nombre] observation ([paso/destino], [N] hab)`

---

## Heurística v2 — Clasificación paso/destino (FASE B)

La heurística v1 (solo occupancy) demostró en FASE A que 5/5 hoteles
contradicen su auto-etiqueta. La v2 incorpora los 3 campos nuevos como
señales primarias:

### Prioridad de señales (de mayor a menor)

| # | Señal | Peso | Descripción |
|---|-------|------|-------------|
| 1 | `avg_stay_nights` | PRIMARIA | Comportamiento real del huésped |
| 2 | `trip_purpose` | SECUNDARIA | Contexto del motivo de viaje |
| 3 | `occupancy_rate` | TERCIARIA | Confirmación de intensidad de demanda |
| 4 | `hotel_self_label` | TIEBREAKER | Solo cuando señales 1-3 son ambiguas |

### Reglas de clasificación

```
SI avg_stay_nights está disponible:
  SI avg_stay_nights <= 1.5           → PASO (alta confianza)
  SI avg_stay_nights >= 3.0           → DESTINO (alta confianza)
  SI 1.5 < avg_stay_nights < 3.0:
    SI trip_purpose in ["negocios", "transito"] → PASO
    SI trip_purpose == "turismo"                 → DESTINO
    SI trip_purpose == "mixto":
      SI occupancy < 15%                        → PASO (lean)
      SI occupancy > 30%                        → DESTINO (lean)
      SI 15% <= occupancy <= 30%:
        SI hotel_self_label == "paso"            → PASO (tiebreak)
        SI hotel_self_label == "destino"         → DESTINO (tiebreak)

SI avg_stay_nights NO está disponible (fallback FASE A):
  Usar heurística v1 (occupancy sola) + hotel_self_label como tiebreaker
```

### Implicación para scenario_calculator.py

El motor financiero NO necesita la clasificación paso/destino para calcular
comisiones OTA — eso es función de `rooms × occupancy × ADR × commission`.
La clasificación es útil para:
  - Segmentar escenarios (un hotel destino tiene más potencial de mejora)
  - Calibrar expectativas de shift OTA→directo
  - Personalizar el pitch comercial

**No tocar scenario_calculator.py hasta tener N≥10 observaciones con
los campos FASE B completos.**

---

## Privacidad y ética

  - **NO pedir ni almacenar:** nombre del dueño/gerente, email personal,
    teléfono directo del dueño, número de identificación.
  - **Sí pedir:** nombre del hotel, datos operacionales agregados.
  - Si el hotel pide confidencialidad, marcar `notes: "confidencialidad
    solicitada por el hotel"` y NO publicar el archivo en repos públicos
    sin consentimiento explícito.

---

## Anti-patrones (lo que NO hacer)

  ❌ **No infiera occupancy de tráfico web o seguidores de Instagram.**
    Eso es `evidencia_verificable`, NO `contacto_directo`. Confidence ≤ 0.7.

  ❌ **No use "estimación del gerente" como si fuera dato verificado.**
    Si el gerente dice "como 30 reservas/mes más o menos", es `estimated`,
    NO `verified`. Marque `confidence: 0.7`, `epistemic_status: "estimated"`.

  ❌ **No mezcle tiers en un mismo análisis.** Si una observación es
    `estimated`, sepárela del cálculo principal o descártela para Fase A.

  ❌ **No modifique `scenario_calculator.py` antes de tener N≥10 observaciones
    verificadas con campos FASE B.** Sin evidencia empírica, el cambio es opinático.

  ❌ **No estime `avg_stay_nights` sin preguntar al hotel.** Si no tienes
    el dato, deja el campo ausente. No inventes "1 noche porque parece paso" —
    eso contamina el dataset.

  ❌ **No sugieras opciones de `trip_purpose` al hotel.** Deja que describa
    libremente y clasifica TÚ después.

---

## Criterio de parada de FASE A (cuándo dejar de recopilar)

FASE A cierra cuando tengas **5 hoteles** con la distribución recomendada:

```
Estrato                                    | N
-------------------------------------------|---
Hotel de paso pequeño (<25 hab)            | 2
Hotel destino pequeño (<25 hab)            | 2
Hotel destino mediano (26-60 hab)          | 1
```

**Decisión GO/NO-GO a FASE B (N=15-20):**

```
Resultado de FASE A                            | Decisión
-----------------------------------------------|--------------
4/5 hoteles "de paso" con occupancy < 15%     | → FASE B (patrón confirmado)
4/5 hoteles "destino" con occupancy > 40%      | → FASE B (patrón confirmado)
Mezcla heterogénea sin patrón claro            | Replantear hipótesis
Luxor es caso aislado (los otros 4 normales)   | Cerrar línea
```

**FASE B cierra cuando N=15-20** con los 8 campos (5 canónicos + 3 FASE B)
y la heurística v2 produce clasificación consistente en ≥80% de las
observaciones.

---

**Versión:** 2.0.0 (2026-07-22, FASE B)
**Mantenedor:** usuario + agente (revisar tras cada FASE)
