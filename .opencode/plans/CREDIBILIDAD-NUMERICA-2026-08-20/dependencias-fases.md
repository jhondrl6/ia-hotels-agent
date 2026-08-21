# Dependencias entre Fases — CREDIBILIDAD-NUMERICA-2026-08-20

> Fuente: `01-plan-maestro.md §2`. Actualizar estados en cada sesión (Cierre Obligatorio de Sesión del executor).

## Diagrama ASCII de Dependencias

```
FASE-P0-A (pricing único) ✅
    │
    ├──→ FASE-P0-B (gate pricing_compliance consume la fuente única) ✅
    │
FASE-P0-C (encoding) ✅  [independiente]
    │
FASE-P1-A (benchmark maestro) ✅
    │
    ├──→ FASE-P1-B (fallback región + OTA; usa benchmark maestro)
    │        │
    │        └──→ FASE-P1-C (cablea master al hook + cap plausibilidad +
    │                         trazabilidad rango; consume benchmarks estables + OTA)
    │
FASE-P1-D (verdad sitio vivo)  [independiente de P1-A/B/C]
    │
    ├──→ FASE-P2-A (coherence acepta "verificado en producción"; occupancy label)
    │
FASE-P2-B (prospectos + docs)  [independiente; docs de pricing requieren P0-A ✅]
    │
    ▼
FASE-E2E-ZIONE (requiere: P0-A,B,C + P1-A,B,C,D + P2-A,B todas ✅)
    │
    ▼
FASE-RELEASE-4.72.0 (requiere E2E ✅ — regla de dependencia del executor)
```

## Tabla de Conflictos Potenciales de Archivos

| Archivo | Fases que lo tocan | Conflicto | Mitigación |
|---------|--------------------|-----------|------------|
| `modules/commercial_documents/hook_pdf_generator.py` | P0-A (pricing dinámico), P1-C (rango/trazabilidad), P0-C (encoding writer) | Alto — 3 fases editan el mismo módulo | Orden estricto P0-A → P0-C → P1-C; cada fase rebasa los tests de la anterior; P0-C solo toca `open()`/encoding, nunca lógica |
| `modules/commercial_documents/v4_proposal_generator.py` | P0-A (constantes fallback de pricing L136-138) | Bajo | Fase única propietaria; comparte la fuente pricing.yaml con hook_pdf_generator |
| `modules/orchestration_v4/two_phase_flow.py` | P1-B (F5: comisión OTA L245/L318 — SOLO esas líneas), P1-C (cableado + cap + trazabilidad), P1-D (caller `validate_whatsapp` L371) | Medio — 3 fases lo editan | Orden secuencial P1-B → P1-C → P1-D (garantizado por dependencias); P1-B tiene restricción explícita de tocar solo líneas OTA; cada fase ejecuta la suite orchestration_v4 |
| `modules/orchestration_v4/onboarding_controller.py` | P1-C (cableado `plan_maestro_data` L58-61) | Bajo | Fase única propietaria |
| `data/benchmarks/regional_adr_2026.json` | P1-A (maestro), P1-B (fallback lo consume) | Medio | P1-B es solo consumidor; no edita el archivo |
| `config/regional_benchmarks.yaml` | P1-A (deprecación/sync), P2-B (docs que lo citan) | Bajo | P2-B solo actualiza docs que lo referencian |
| `modules/financial_engine/scenario_calculator.py` + `calculator_v2.py` + `inputs_contract.py` + `modules/utils/benchmarks.py` | P1-B (F5: OTA parametrizada) | Bajo | Fase única propietaria |
| `modules/auditors/v4_comprehensive.py` | P1-B (F3: fallback región L1466), P1-D (caller `validate_whatsapp` L1557) | Medio | P1-D posterior a P1-B (orden secuencial); zonas distintas del archivo |
| `AGENTS.md` | P0-B (gate count 12→13, D5), RELEASE (sync de versión vía sync_versions.py) | Medio | P0-B valida con `validate_agents_md.py` en la misma fase; RELEASE re-valida en E8 |
| `main.py` | P1-D (caller `validate_whatsapp` L1735, si el cambio de firma no es backwards-compatible) | Bajo | Fase única propietaria |
| `modules/data_validation/cross_validator.py` | P1-D (sedes) | Bajo | Fase única propietaria |
| `modules/asset_generation/pain_ledger.py` | P1-D (propagación site_verification) | Bajo | Fase única propietaria |
| `modules/commercial_documents/coherence_validator.py` | P2-A (F14) | Bajo | Fase única propietaria; requiere P1-D ✅ para consumir el nuevo estado |
| `modules/quality_gates/publication_gates.py` | P0-B (gate nuevo), P1-C (posible campo de rango) | Medio | P1-C no agrega gate nuevo; si necesita tocar el orquestador de gates, coordinar con lo entregado en P0-B |
| Writers JSON/MD globales (encoding) | P0-C (fix), todas las fases posteriores (usan writers corregidos) | Bajo | P0-C antes de E2E; fases posteriores no re-introducen `open()` sin encoding (test anti-regresión en P0-C) |

## Notas de Recuperación

- Si `FASE-P1-D` queda `⏳ INCOMPLETA` por agotamiento: dividir en `FASE-P1-D-A` (solo F12) y `FASE-P1-D-B` (solo F13) y actualizar este archivo.
- `FASE-E2E-ZIONE` NO puede ejecutarse con ninguna dependencia pendiente: verificar ✅ en `06-checklist-implementacion.md` antes de iniciar la sesión.
- `FASE-RELEASE-4.72.0` aborta si E2E no está ✅ (Plan de Recuperación del executor).
