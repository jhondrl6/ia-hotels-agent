# Antes / después — FASE-E2E contra el baseline congelado del 2026-10-12

> **Medido el 2026-10-24 sobre los artefactos que escribió esta corrida** (`output/v4_complete/…`, copia en
> `corrida/`) y sobre `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/corrida/` del baseline, en solo lectura.
> Esta tabla es la fuente del dato; `10-analisis-post-implementacion.md` la **referencia**, no la re-transcribe.

| Clave leída | Artefacto y clave | Baseline 2026-10-12 | Corrida 2026-10-24 | Lectura |
|---|---|---|---|---|
| Veredicto | `acta_revision.json` → `verdict` | `BLOQUEADO` | **`APROBADO-CONDICIONAL`** | AC2 ejercitado en producción, no solo en test |
| Motivo del condicional | `acta_revision.json` → `conditional_reason` | `null` (no existía la clave) | **`ANALYTICS_CEILING`** | la causa distingue el techo real de analytics; no es `ONBOARDING_INCOMPLETE`, que habría significado loader fail-closed |
| `summary.over_presentations` | `revision_honestidad.json` → `summary` | **2** (CRITICAL, suprime el ZIP) | **0** | AC1 ejercitado con el revisor real sobre el paquete renderizado |
| `total_findings` del revisor | idem | 3 | 1 (`undisclosed_warnings`) | el hallazgo que queda no es un claim absoluto |
| tier de evidencia | `acta_revision.json` → `evidence_tier` | `B+` | `B+` | **sigue B+**: el techo es real y se declara; la cura no sube el tier, cambia el veredicto |
| Pérdida realista | `financial_scenarios_*.json` → `scenarios.realistic` | 3.511.200 COP/mes | **3.511.200 COP/mes** | idéntica, y re-medida desde cero (mismo `input_data`: rooms 11, ADR 330.000, occupancy 0.42424…, canal 30 %) |
| Escenarios | `scenarios` | cons 6.176.940 / opt 582.120 | cons 6.176.940 / opt 582.120 | sin deriva |
| Brechas `PainSolutionMapper` | `pain_ledger.json` → `entries` | 11 | **11** | re-medidas; no es «0 porque el lector falló» ni «11 por préstamo del baseline» (`L-PF10`) |
| Publicación | `acta_revision.json` → `package_evidence.suppressed` | `true` (ZIP suprimido) | **`false`** | cuarentena publicada y renombrada |
| ZIP real | `deliveries/` | 0 entradas | **`donalfonsohotel_20261024.zip`, 94.432 B, sha256 `eeae4001625a7299…`, 82 miembros** | AC7: ZIP real, no un registro |
| Gates | `gate_report_*.json` → `readiness` | no READY | **`READY_FOR_PUBLICATION`**, 13 gates, 0 blocking fallidos | 2 advertencias divulgadas: `asset_confidence` (1 asset < 0,7) y `pricing_compliance` (pain_ratio 0,1574 fuera de banda ideal, piso operativo de 400.000 aplicado, gate_max boutique OK) |
| Coherencia | `v4_complete_report.json` → `coherence_score` | ≥ 0,8 | **0,926969696969697** | gate de coherencia pasado con holgura |
| URL del run | `gate_report_*.json` → `hotel_url` | `https://www.donalfonsohotel.com/` | `https://www.donalfonsohotel.com/` | grafía del baseline conservada; **nunca** `hoteldonalfonso.com` (asiento §5) |

## Dos hallazgos de la corrida, documentados con dueño y sin corregir en esta fase

La restricción de la fase prohíbe tocar código: ambos se registran como deuda con dueño.

1. **El paquete entrega dos corridas mezcladas.** De sus 82 miembros, **26 llevan timestamp `20261012`** y 28
   `20261024`; **22 assets existen en dos versiones** (p. ej. `ASSETS/faq_page/ESTIMATED_faqs_20261012_165705.json` y
   `…_20261024_155113.json`). El `DeliveryPackager` barre el directorio de salida del hotel, que conserva los assets
   de la corrida anterior, así que un cliente que recibió el paquete del 2026-10-12 recibe ahora dos generaciones
   superpuestas. Es el caso que el pre-vuelo declaraba bajo `L-PF11` (aislamiento del análisis previo), pero **no
   por la memoria ni por `--force-new`**: por el barrido del directorio de assets. Ningún instrumento del plan lo
   cortaba: `run_all_validations.py` y el tribunal no miran la composición del ZIP. **Dueño: Operador** — necesita
   fase propia (cambio de producto: limpiar o aislar `output/v4_complete/<hotel_id>/` antes de empaquetar).
2. **El nombre comercial sale del slug de la URL, no del onboarding.** `v4_complete_report.json` declara
   `hotel_name: "Donalfonsohotel"` mientras el YAML inyectado dice `hotel.nombre: "Hotel Don Alfonso"`; el documento
   del cliente se dirige al hotel por el dominio. Productor: `_extract_hotel_name_from_url` cuando `args.nombre` no
   se pasa. **Dueño: Operador**, con la misma valla (fuera del alcance de esta fase, que no toca el render).

## Lo que la corrida **no** prueba

- No sube el tier: `B+` con techo de analytics es el estado real del hotel; el veredicto honesto es
  `APROBADO-CONDICIONAL`, no `APROBADO`.
- No divulga la edad del dato al cliente: la captura `2026-07-22` (94 días) vive en el YAML, en `preflight.json` y
  en este asiento, pero no en `01_DIAGNOSTICO` ni en `02_PROPUESTA`. Dueño: Operador, sede FASE-VERIFY o fase propia.
- Los dos documentos comerciales **no imprimen ninguna URL** (0 coincidencias de `https?://`), así que el riesgo de
  «estampar una web que no es la del hotel» no se materializa en este camino: se materializaba por el fallback del
  warehouse, que la corrida no tomó.
