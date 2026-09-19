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
| Validaciones rápidas PRE | 9/10 el 2026-09-18 (rojo Version Sync por cuatro documentos sucios en el árbol) y 10/10 al re-medir el 2026-09-19 | Preparación |
| Causa del rojo Version Sync | **Causa real, medida 2026-09-19:** el quick del 2026-09-18 fallaba porque `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol; hoy esos cuatro archivos son idénticos a HEAD (revertidos fuera de esta sesión, mtime 11:06-11:10) y el quick da 10/10. `_check_version_sync` se limita a invocar `sync_versions.py --check`, así que la hipótesis de un desacuerdo verificador↔escritor queda retractada: era estado transitorio del working tree, ya resuelto. | Preparación |
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

## Rojo documental del PRE, cerrado por re-medición

`run_all_validations.py --quick` dio 9/10 el 2026-09-18 y **10/10** al re-medirlo el 2026-09-19. La causa medida del rojo: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol y hoy son idénticos a HEAD tras una reversión ajena a esta sesión. Se retracta la explicación previa por cuatro segmentos: `_check_version_sync` solo ejecuta `sync_versions.py --check`. Regla conservada: re-medir el quick al abrir cada fase y no modificar hooks, baselines de citas ni configuración para forzar un verde.
