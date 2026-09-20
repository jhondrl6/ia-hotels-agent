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
| HEAD de preparación | `7d91c9f` (v4.77.0) · **HEAD de la revisión 2: `938f59f` (v4.77.3)** | Preparación / revisión 2 |
| Corridas v4complete de este plan | 0; presupuesto total 1 | Preparación |
| Validaciones rápidas PRE | 9/10 el 2026-09-18 (rojo Version Sync por cuatro documentos sucios en el árbol) y 10/10 al re-medir el 2026-09-19 | Preparación |
| Causa del rojo Version Sync | **Causa real, medida 2026-09-19:** el quick del 2026-09-18 fallaba porque `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol; hoy esos cuatro archivos son idénticos a HEAD (revertidos fuera de esta sesión, mtime 11:06-11:10) y el quick da 10/10. `_check_version_sync` se limita a invocar `sync_versions.py --check`, así que la hipótesis de un desacuerdo verificador↔escritor queda retractada: era estado transitorio del working tree, ya resuelto. | Preparación |
| Sitio del hotel verificado en preparación | NXDOMAIN en la URL del warehouse; 200 en la del usuario. **Rectificado en la revisión 2:** el detector **sí observa** el canal en la raíz — medición con `SitePresenceChecker._check_html_element` devuelve `found=True` vía `css_class: joinchat …` y la corrida real archivó `whatsapp_button: exists / 0.85`. Lo que no aporta es número. La redacción anterior ("ausente del HTML estático que lee el detector") queda retractada | Preparación + revisión 2 |
| **Nueva (revisión 2): corrida de referencia ya archivada** | `output/TAREA7-2026-09-19/` — v4complete del 2026-09-19 15:01 sobre el hotel y la URL del §5: readiness `READY_FOR_PUBLICATION`, 13/13 gates, **veredicto `BLOQUEADO` y ZIP suprimido** por un único CRITICAL `VACUOUS_RECALL`; `pain_ledger` sin pain de WhatsApp; `whatsapp_verified` en verde vacuo. Es baseline medido del plan, no consume el intento | Revisión 2 |
| **Nueva (revisión 2): contrafactual de AC20** | `TribunalJudge._compute_verdict` ejecutado en memoria sobre esa acta: con el hallazgo → `BLOQUEADO`; con `details.critical_issues_count` fundado y recomendación recalculada → `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (no bloqueante). Intermedio falso descartado: zero de `critical_count` sin recalcular `recommendation` no volta el veredicto | Revisión 2 |
| **Nueva (revisión 2): blast radius de AC19** | 8 consumidores del reporte canónico de presencia; 816 funciones de test canónicas en 52 archivos del vecindario, 4 asserts de igualdad exacta de forma — esas tres cifras y los 866 casos collectados se reproducen. **476 en 26 archivos con estado hardcodeado no se reproduce**: con el criterio redactado da 31 archivos / 545 funciones y doce variantes medidas dan una banda 22/427 → 32/552 sin tocar el par (anexo `mediciones_de_la_revision_2`, fila `M4-blast-radius`). La división AC19a/AC19b se apoya en las cifras reproducidas, no en esa | Revisión 2 |
| Índice | 305 IDs, fresco (preparación) · **314** tras la intervención del 2026-09-19 · **316 tras la revisión 2** (nacen `L-ENT.10` y `L-ENT.11`); «citados sin definición» permanece en **43**, sin citas huérfanas nuevas | Preparación / revisiones |
| Tests nuevos / casos recogidos / passed | No medidos; no confundir funciones con casos parametrizados | Pendiente |
| Coherencia / veredicto / ZIP | **Ninguna corrida de este plan.** Baseline leído de una corrida ajena ya archivada: coherencia 0.8633, `readiness: READY_FOR_PUBLICATION`, veredicto `BLOQUEADO`, ZIP suprimido tras `member_count: 52` | Revisión 2 (lectura de `output/TAREA7-2026-09-19/`) |
| Presupuesto de iteraciones | Medir con instrumento canónico y corte; nunca estimar cumplimiento | Todas |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| Directorio de este plan | Diseño y prompts; sin implementación | Preparación |
| **Revisión 2 (2026-09-19): archivos del plan tocados** | `README.md`, `01-plan-maestro.md` (§1, §2, §3, §4, §5, §6, §7), `04-contrato-ejecucion.md` (límite de lectura de corridas ajenas), `00-lecciones-capitalizadas.md` (§1bis nuevo, Q7-Q10, siete filas en §2, §3bis, §4), `06-checklist-implementacion.md`, `dependencias-fases.md`, `09`, `10-analisis`, `05-…-fase-VERIFY` corregidos; **nuevo** `05-prompt-inicio-sesion-fase-0.md`; A/B/C/G/H/E2E actualizados al nuevo orden. **Sin cambios de código, tests, VERSION ni evidencia** | Revisión 2 |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Regenerados tras la revisión 2 (316 IDs); cada fase vuelve a regenerarlos al cerrar | Revisión 2 |
| CHANGELOG.md / docs/GUIA_TECNICA.md / docs/contributing/REGISTRY.md | Cada fase registra su propio trabajo; no modificados en preparación ni en la revisión 2 | Pendiente |

## Registro documental por fase

Cada cierre anota: archivos exactos, tests añadidos, PRE/POST con misma unidad, resultados de mutaciones, limitaciones, estado real y autorización de commit si existe. No elevar versión en fases intermedias. Registrar con `scripts/log_phase_completion.py --check-manual-docs` solo la fase que acaba de completarse.

## Rojo documental del PRE, cerrado por re-medición

`run_all_validations.py --quick` dio 9/10 el 2026-09-18 y **10/10** al re-medirlo el 2026-09-19. La causa medida del rojo: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados en el árbol y hoy son idénticos a HEAD tras una reversión ajena a esta sesión. Se retracta la explicación previa por cuatro segmentos: `_check_version_sync` solo ejecuta `sync_versions.py --check`. Regla conservada: re-medir el quick al abrir cada fase y no modificar hooks, baselines de citas ni configuración para forzar un verde.
