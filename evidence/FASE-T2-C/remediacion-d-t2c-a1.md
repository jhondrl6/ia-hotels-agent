# Remediación D-T2C-A1 — FASE-T2-C (2026-09-11)

Post-auditoría forense de FASE-T2-C. Esta evidencia es aditiva: no modifica ni reemplaza
`baseline-pre-post.md` ni `evidencia-final.md` de la fase original.

## Que se remedia

El desvío D-T2C-A1 (registro completo en `10-analisis-post-implementacion.md`
§Desvío registrado y en la adenda del prompt de la fase) dejaba un estado residual:
ningún test ejercitaba los tres métodos reales de `v4_proposal_generator.py` que
construyen `presence_lookup`. Los 7 tests de la fase re-implementaban la lógica del
lookup o leían `main.py` como texto — pasaban sin tocar el código modificado.

## Que se agrego

Clase `TestPresenceLookupLiveConsumers` en
`tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` (11 tests), que
instancia `V4ProposalGenerator` real y ejecuta:

- `_generate_dynamic_services_table` — dict canónico `exists` y `exists_with_issues`
  (→ «ℹ️ Presente en sitio» en la fila del servicio, derivada de
  `PROPOSAL_SERVICE_TO_ASSET`, sin hardcode), `not_exists` / `None` / `results` vacíos /
  objeto sin `results` (→ sin claim de presencia, sin crash), y objeto con `.results`
  (compat dataclass preservada).
- `_generate_technical_assets_table` — dict canónico vs `None`.
- `_generate_asset_quality_table` — dict canónico (→ «✅ Día 1 (Verificado)») vs `None`.

El delta del desvío queda fijado por contrato: con dict canónico los consumidores vivos
reciben presencia; con `None` el comportamiento es idéntico al pre-T2-C.

## Tambien se cerro (documental)

- Anotación D2 en el prompt de la fase: el entregable prescrito
  `tests/quality/test_asset_semantics_registry.py` nunca se creó; S9 quedó certificado
  por `test_invalid_mappings_valida_contra_capa1` (preexistente) sin código nuevo. El
  REGISTRY de la ejecución real quedó limpio (no registró el archivo fantasma).

## Resultados medidos

| Instrumento | Resultado |
|-------------|-----------|
| `test_s_e2_generate_proposal_false.py` | 18/18 verdes (7 originales + 11 nuevos) |
| `tests/quality_gates/tribunal/ + tests/commercial_documents/` | 489 verdes |
| Colectados (`pytest tests/ --collect-only -q`) | 4,018 → 4,029 |
| `run_all_validations.py --quick` | TOTAL PASS (8/8) |

## No-cambios

- Ninguna línea de producción modificada (solo tests + docs del plan).
- La decisión conservada del desvío no se revierte: los bloques `presence_lookup`
  permanecen reactivados con justificación documentada.
- Verificación de veracidad «Presente en sitio» contra el sitio real: NO esta en
  alcance — es criterio de FASE-E2E (registrado en `dependencias-fases.md`).
