# Documentación post-proyecto — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Estado: PREPARACIÓN. Ninguna fase ejecutada. No sustituye la documentación incremental de cada fase ni permite registrar retrospectivamente todas las fases en RELEASE.

## Sección A: Módulos nuevos

| Módulo | Archivos | Descripción | Fase |
|---|---|---|---|
| Por medir | Ninguno implementado | Registrar solo lo realmente creado | Pendiente |

## Sección B: Funcionalidades nuevas

| Feature | Módulo | Descripción | Fase |
|---|---|---|---|
| Por medir | Ninguno implementado | Diferenciar refactor, fix y contrato ya existente | Pendiente |

## Sección D: Métricas acumulativas

| Métrica | Valor | Fase |
|---|---|---|
| HEAD de preparación | `7d91c9f` | Preparación |
| Corridas v4complete de este plan | 0; presupuesto total 1 | Preparación |
| Validaciones rápidas PRE | 9/10; único rojo Version Sync, ya presente en HEAD y no imputable al plan | Preparación |
| Causa del rojo Version Sync | Medido 2026-09-19: `sync_versions.py --check` y `version_consistency_checker.py` exit 0 sobre los 7 campos; el check del quick compara contra `full_version` de cuatro segmentos. Desacuerdo verificador↔escritor | Preparación |
| Sitio del hotel verificado en preparación | NXDOMAIN en la URL del warehouse; 200 en la del usuario; canal presente vía plugin, ausente del HTML estático que lee el detector (AC19) | Preparación |
| Índice PRE | 305 IDs, fresco | Preparación |
| Tests nuevos / casos recogidos / passed | No medidos; no confundir funciones con casos parametrizados | Pendiente |
| Coherencia / veredicto / ZIP | No hay corrida nueva | Pendiente |
| Presupuesto de iteraciones | Medir con instrumento canónico y corte; nunca estimar cumplimiento | Todas |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| Directorio de este plan | Diseño y prompts; sin implementación | Preparación |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Regeneración al terminar preparación | Pendiente |
| CHANGELOG.md / docs/GUIA_TECNICA.md / docs/contributing/REGISTRY.md | Cada fase registra su propio trabajo; no modificados en preparación | Pendiente |

## Registro documental por fase

Cada cierre anota: archivos exactos, tests añadidos, PRE/POST con misma unidad, resultados de mutaciones, limitaciones, estado real y autorización de commit si existe. No elevar versión en fases intermedias. Registrar con `scripts/log_phase_completion.py --check-manual-docs` solo la fase que acaba de completarse.

## Bloqueante documental preexistente

`run_all_validations.py --quick` devuelve 9/10 desde antes de crear el plan; el único rojo es Version Sync. Medido el 2026-09-19: `sync_versions.py --check` pasa los siete campos gobernados y el pre-commit `[1/7]`/`[2/7]` no bloquea, de modo que la causa es un desacuerdo entre el verificador del quick (cuatro segmentos) y el escritor canónico (tres), no documentos desincronizados. A decide a quién alinear; la resolución no exige tocar AGENTS.md ni .cursorrules, y no se modifican hooks, baseline de citas ni configuración para ocultar el rojo.
