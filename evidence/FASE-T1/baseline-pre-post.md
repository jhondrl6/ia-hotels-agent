# Baseline FASE-T1

**Fecha**: 2026-09-10

## Pre-Baseline

| Metrica | Valor |
|---------|-------|
| Tests collectados | 3944 |
| Version | v4.75.0 |
| Estado | Clean (pre-T1) |

## Post-Baseline

| Metrica | Valor |
|---------|-------|
| Tests collectados | 3961 |
| Tests nuevos tribunal | 17 |
| Delta | +17 |
| Validations | 8/8 PASS |
| Tribunal tests | 17/17 PASS |

## Archivos Nuevos

- `modules/quality_gates/tribunal/__init__.py`
- `modules/quality_gates/tribunal/judge.py`
- `modules/quality_gates/tribunal/acta_writer.py`
- `tests/quality_gates/tribunal/__init__.py`
- `tests/quality_gates/tribunal/test_judge.py`
- `tests/quality_gates/tribunal/test_acta_serialization.py`

## Archivos Modificados

- `main.py` (integracion tribunal + Ruta 2 ZIP blocking)

## Criterios de Completitud

- [x] AC1: `acta_revision.json` con clave `verdict` legible
- [x] AC2: Tier B/C → `APROBADO-CONDICIONAL-PENDING-ONBOARDING`
- [x] AC3: `acta_revision.md` con 6 clausulas P6
- [x] AC4: Una ruta de bloqueo, no cuarta
- [x] NR1 (medido en colectados): `collected_post = collected_pre + tests nuevos` → 3944 + 17 = 3961. **No medido en `passed`**: la suite completa no se ejecutó y arrastra 7 fallos preexistentes ajenos al plan (`test_never_block_integration.py`)
- [x] NR3: `run_all_validations.py --quick` TOTAL PASS
- [x] NR4: Tribunal no reimplementa gates
- [ ] S-HF1: ⚠️ **abierto**. Quedó documentado dos veces y de forma contradictoria: `decision-integracion.md` cita `proposal_asset_matrix.json → alignment.promised_services_total`, clave que no existe en ningún artefacto real (en FASE-I `alignment` es `null`); `baseline-pre-post.md` y el código usan `summary.promised`. Además `total_services` no aparece en ningún archivo del tribunal ni del acta. Unificar en `decision-integracion.md` y decidir si el acta debe reportarlo
