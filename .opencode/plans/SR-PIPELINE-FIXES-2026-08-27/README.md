# SR-PIPELINE-FIXES-2026-08-27

> **Fixes del pipeline v4complete tras la E2E de Hotel Salento Real** — unificación de la contabilidad promesa/matriz/gate, self-healing de claims, canonicalización de `target_id`, fix de detección de schema + contabilización de presencia (revisión causa-raíz 2026-08-28), investigación de varianza y fixes de display comercial.
>
> **Versión**: v4.72.2 → **v4.73.0** · **Workflow**: phased_project_executor v2.16.0 · **1 fase por sesión**

## Tabla de Progreso

| Fase | Fixes/Contenido | Complejidad | Delegación | Estado | Sesión | Fecha |
|------|-----------------|-------------|------------|--------|--------|-------|
| FASE-SR-A | N1/rec#9 — Helper único `compute_unresolved()` + test estático guardián L-SR1 | Media | ❌ DIRECTO | ✅ Completada | agente | 2026-08-28 |
| FASE-SR-B ⚠️ | rec#1 — Unificación promesa/matriz/gate (L-SR3, L-NC10) | **MÁXIMA** (§4 plan maestro) | ❌ DIRECTO (DT-3) | ✅ Completada | agente | 2026-08-28 |
| FASE-SR-C | rec#2 — Self-healing loop CG-CLAIM-VS-EVIDENCE (L-SR5) | Alta | ❌ DIRECTO | ⏳ Pendiente | — | — |
| FASE-SR-D | rec#3/#10 — Canonicalización de `target_id` con `_normalize_url` + `generate_hotel_id` (L-SR2, L16) | Media | ❌ DIRECTO | ⏳ Pendiente | — | — |
| FASE-SR-E | rec#4/#11 (H7) — Fix falso negativo schema (JSON-LD array) + contabilización única `exists_with_issues` (revisión 2026-08-28) | Alta | ❌ DIRECTO | ⏳ Pendiente | — | — |
| FASE-SR-F | rec#5/#6 — Investigación varianza plan de assets + PageSpeed (OPS) | Media | ❌ DIRECTO | ⏳ Pendiente | — | — |
| FASE-SR-G | rec#8 — Display: CG-TIER-CONSISTENCY (L30) + CG-TECH-JARGON (L27) | Baja-Media | ❌ DIRECTO | ⏳ Pendiente | — | — |
| FASE-SR-H | **ÚNICA ejecución v4complete Salento Real** (baseline + evidencia + smoke) | Media (ejecución) | ✅ DELEGABLE (subagente terminal) | ⏳ Pendiente | — | — |
| FASE-SR-VERIFY | Certificación AC1-AC13 contra output E2E + diff antes/después | Media | ❌ DIRECTO (§4.6) | ⏳ Pendiente | — | — |
| FASE-RELEASE-4.73.0 | Docs oficiales + version bump + validaciones E1-E8b | Baja | ✅ DELEGABLE (subagente) | ⏳ Pendiente | — | — |

> **Preparación**: completada 2026-08-27 (sesión de orquestación). Fases de implementación pendientes.

## Archivos del Plan

| Archivo | Propósito |
|---------|-----------|
| `01-plan-maestro.md` | Diseño completo: fases, complejidad, R3, delegación, ACs |
| `dependencias-fases.md` | Diagrama de dependencias + tabla de conflictos de archivos |
| `05-prompt-inicio-sesion-fase-*.md` | Prompt de inicio por fase (1 por sesión de agente) |
| `06-checklist-implementacion.md` | Checklist maestro de estados |
| `09-documentacion-post-proyecto.md` | Acumulador documental (fuente de FASE-RELEASE) |
| `10-analisis-post-implementacion.md` | Matriz AC1-AC13, lecciones, decisiones, seguimientos |

## Contexto Fuente

- `.opencode/context/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27.md` — 6 hallazgos + N1-N4 + recomendaciones #1-#11, re-validados contra código vivo (2026-08-27). **Lectura previa obligatoria de toda fase.**
- Lecciones fuente: `.opencode/plans/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` (L-NC1–L-NC12).

## Reglas Clave del Plan

1. **R1**: Una fase por sesión. Sin excepciones.
2. **R2**: Máximo 60 iteraciones del agente por fase.
3. **R3**: Máx. 4 tareas + 0 comandos largos, ó 3 tareas + 1 comando largo por fase.
4. Cada fase de implementación ejecuta `log_phase_completion.py` al terminar (**SIN** `--release`). FASE-RELEASE no registra fases anteriores.
5. La única ejecución de `v4complete` del plan ocurre en **FASE-SR-H** (Hotel Salento Real, https://www.hotelsalentoreal.com/, con `--output output/salentoreal_final_v4c` para ejercitar la rama FASE-D S7 corregida). Si falla: NO re-ejecutar; aplicar el Protocolo de Recuperación de Agotamiento del executor y documentar.
6. Análisis post-implementación (`10-analisis-post-implementacion.md`) se actualiza al cierre de **cada** fase.
7. **Capa financiera INTACTA**: escenarios conservador/realista/optimista son deterministas y NO se tocan ($6.57M / $4.04M / $1.26M COP = referencia baseline corrida C).
8. **Suites pytest seguras**: nunca correr la suite completa en un solo proceso (memoria: `test_proposal_generator.py` fuga ~8GB); ejecutar archivos específicos con salida redirigida a archivo.

## Cómo Retomar

1. Leer este README + `06-checklist-implementacion.md` + `dependencias-fases.md`.
2. Identificar la primera fase con estado ⏳.
3. Abrir sesión nueva de agente con el prompt `05-prompt-inicio-sesion-fase-{X}.md` correspondiente.
