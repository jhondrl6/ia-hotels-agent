# Decision de Integracion — FASE-T1

**Fecha**: 2026-09-10
**Fase**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T1

## Rutas de Bloqueo del ZIP Identificadas en `main.py`

| # | Ruta | Simbolo/Condicion | Efecto |
|---|------|-------------------|--------|
| 1 | Gate blocking (L2997) | `GATE_BLOCKING_ENABLED` + `readiness_report["status"] == "NOT_READY"` | Elimina docs cliente, escribe `BLOCKED_BY_GATES.md` |
| 2 | Delivery quality FAIL (L3217) | `delivery_quality_report.status == "FAIL"` o `_claim_escalated` | `delivery_zip_path = None` (skip ZIP) |
| 3 | Packaging exception (L3293) | Excepcion en `DeliveryPackager.package()` | `delivery_zip_path = None` |

## Decision: Ruta 2

**Ruta elegida**: Ruta 2 — junto a `delivery_quality_report`.

**Razon**:
- Es la ruta de bloqueo por **calidad post-generacion**, que es exactamente lo que el Juez certifica.
- La Ruta 1 es pre-generacion (publication gates), ya tiene su propio mecanismo.
- La Ruta 3 es un fallback de error, no un mecanismo de decision.
- El Juez se ejecuta **despues** del `delivery_quality_report` y **antes** de la decision del ZIP.

**Kill switch `GATE_BLOCKING_ENABLED`**: NO afecta al Juez. El Juez tiene su propia logica de never-block (try/except que produce `acta = None` si falla). El kill switch controla la Ruta 1 (publication gates), que es ortogonal.

## Regla de Resolucion de `deliveries_dir`

El Juez recibe `deliveries_dir` como parametro. En `main.py`, se resuelve por glob:
```python
deliveries_dirs = list(output_dir.glob("deliveries"))
deliveries_dir = deliveries_dirs[0] if deliveries_dirs else output_dir / "deliveries"
```

Dentro del Juez, el `MANIFEST.json` se busca en `<deliveries_dir>/<hotel_id>_*/MANIFEST.json` (glob del mas reciente).

## Punto de Integracion

```
delivery_quality_report → TribunalJudge → decision ZIP
```

El veredicto del Juez fuerza `delivery_zip_path = None` cuando `blocks_delivery_zip(acta)` es verdadero, es decir para `BLOQUEADO` y `DEVOLVER-CORRECCIONES`, alimentando la misma condicion que ya evalua `delivery_quality_report.status == "FAIL"`. La politica vive en `BLOCKING_VERDICTS` (`judge.py`); `main.py` no compara strings de veredicto. Registrado como decision D-T1.1 en `10-analisis-post-implementacion.md`.

## Criterio de Narracion `total_services` (S-HF1)

Se decide: `total_services` se lee de `proposal_asset_matrix.json → alignment.promised_services_total`. Es el criterio de narracion (cuantos servicios prometio la propuesta), NO de serializacion del acta. El acta solo reporta el status de P6.5 (primer piso) con la razon del tier.
