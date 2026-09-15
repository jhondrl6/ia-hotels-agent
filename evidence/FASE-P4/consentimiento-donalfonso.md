# Consentimiento y frescura para la corrida de observación — Hotel Don Alfonso

**Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 / FASE-P4
**Fecha de registro**: 2026-09-14
**Resuelve**: línea roja (iii) de DA-P1.9 (`evidence/FASE-P1/decision-enforcement.md` §Decisión DA-P1.9) — "consentimiento y frescura registrados **antes** de la corrida".

## Quién declara

El **operador del proyecto** (usuario de esta sesión), al responder la tanda de decisión de
Tarea 1 el 2026-09-14:

| Pregunta | Respuesta registrada |
|---|---|
| ¿Con qué hotel se corre la observación? | **Hotel Don Alfonso** — `https://hoteldonalfonso.com/` |
| ¿Frescura del dato? | **Aceptar con límite escrito** (el dato tiene 54 días y no existe verificador mecánico activo) |

El agente **no** llenó ni modificó dato operativo alguno (línea roja i). El registro de esta sección
consigna una autorización declarada por el dueño de la relación comercial, no un dato del hotel.

## Alcance de la autorización

- Uso de los datos operativos **ya entregados** por el hotel en 2026-07-22 para **una corrida de
  observación/diagnóstico**.
- **NO es entrega a cliente**: la restricción de la fase prohíbe entregar el ZIP resultante a tercero
  como producto (`05-prompt-inicio-sesion-fase-P4.md` §Restricciones).
- El hotel no recibe el informe ni las cifras de esta corrida como parte de esta autorización.

## Datos que consume la corrida (fuente declarada)

Origen: `data/hotel_observations/observations.json`, entrada `Hotel Don Alfonso`. El pipeline los
resuelve por URL normalizada en el fallback del cargador (`_load_latest_onboarding_data` →
`_observation_to_onboarding_format`), **sin** que exista `output/clientes/hoteldonalfonso_onboarding.yaml`.

| Campo | Valor | Metadata de procedencia |
|---|---|---|
| `rooms` | 11 | `source: contacto_directo` |
| `monthly_reservations` | 140 | `confidence: 0.95` |
| `avg_reservation_cop` / `adr_cop` | 330 000 | `epistemic_status: verified` |
| `direct_channel_percentage` | 30.0 | `collected_at: 2026-07-22` |
| `occupancy_rate` (derivado) | 0.4242 | `region: eje_cafetero`, `category: boutique_10_25` |

## Límite de frescura aceptado (AC-O0 en su pata de frescura)

- Edad del dato al momento de la corrida: **54 días** (captura 2026-07-22, corrida 2026-09-14).
- **No hay verificador mecánico**: el cargador solo aplica un límite si la variable de entorno
  `ONBOARDING_FRESHNESS_HOURS` está definida, y no lo está. La regla "Vigencia análisis < 20 días" de
  `agent_harness/memory.py` gobierna la reutilización de análisis previos, **no** la edad del dato de
  onboarding — son dos relojes distintos y este plan no los unifica.
- Consecuencia para el informe: cualquier cifra de la corrida descansa en un dato operativo de hace
  ~8 semanas. Se declara como límite de la fase, no como fallo de la corrida.

## Contradicción interna del dato, registrada antes de correr

`is_transit_hotel: false` (clasificación por heurística de occupancy: 42.4 % > 30 %) **contradice**
`hotel_self_label: "paso"` (auto-etiqueta del hotel). El propio `notes` de la observación lo declara:
*"Clasificación por heurística occupancy (42.4% > 30% = destino), contradice etiqueta original del
hotel"*. No se corrige aquí: la línea roja de este plan prohíbe al agente tocar dato del hotel, y el
hallazgo es material para el punto 6 del informe (`precision_tier`, bases de pérdida).
