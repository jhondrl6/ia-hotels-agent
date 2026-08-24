# Workflows Deprecados — 2026-08-24

> Archivado desde `.agents/workflows/` el 2026-08-24 (version del proyecto: v4.72.2).

## Motivo

De los 17 skills del directorio, solo `phased_project_executor.md` tiene uso real y evolucion
activa. Los 16 archivos aqui archivados estaban congelados desde 2026-04/05 y su funcionalidad
o bien ya vive en codigo, o nunca paso de ser un stub:

| Grupo | Archivos | Razon |
|-------|----------|-------|
| Familia v4_* | `v4_complete.md`, `v4_asset_conditional.md`, `v4_financial_scenarios.md`, `v4_quality_validator.md`, `v4_regional_resolver.md`, `v4_regression_guardian.md` | Su logica la ejecuta el codigo: `main.py v4complete`, `modules/orchestration_v4/`, `modules/financial_engine/`, `modules/quality_gates/`. La regresion la cubre `tests/regression/` (26 tests via pytest) |
| Companion | `v4_regression_guardian.py` | Duplicado del flujo cubierto por `tests/regression/` |
| Stubs (~1.5 KB, sin evolucion) | `delivery_wizard.md`, `deployment_assistant.md`, `env_rerun.md`, `maintenance_autopilot.md`, `meta_skill_creator.md`, `monitor_bg.md`, `seo_technical.md`, `truth_protocol.md`, `watchdog_check.md` | Nunca se usaron; solo aportaban ruido al catalogo del SkillRouter |

## Seguridad de la remocion

- `agent_harness/skill_router.py` escanea el directorio dinamicamente; ningun codigo
  tiene dependencias duras a estos nombres.
- Sincronizacion documental aplicada en el mismo cambio: `AGENTS.md`,
  `.agents/workflows/README.md`, `INDICE_DOCUMENTACION.md`, `CHANGELOG.md`.

## Restauracion

Para restaurar un skill: mover el archivo de vuelta a `.agents/workflows/` y re-registrarlo
en `.agents/workflows/README.md` (validado por `scripts/validate_agent_ecosystem.py`).
