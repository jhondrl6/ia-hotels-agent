# REFACTOR-COHERENCIA-NARRATIVA-2026-08-22

> **Refactorización de la capa narrativa de documentos comerciales** — eliminación de 7 manifestaciones de fosilización narrativa (bugs B1-B7) con una única causa raíz: templates que ignoran el pain_ledger.
>
> **Versión**: v4.72.0 → **v4.72.1** · **Workflow**: phased_project_executor v2.15.0 · **1 fase por sesión**

## Tabla de Progreso

| Fase | Bugs/Contenido | Complejidad | Estado | Sesión | Fecha |
|------|----------------|-------------|--------|--------|-------|
| FASE-R0-A | B2 — Quick Win #1 texto ↔ condición | Baja | ✅ Completada | Sesión 1 | 2026-08-22 |
| FASE-R0-B ⚠️ | B1+B4 — Sección 4 dinámica | **MÁXIMA** (§4 plan maestro) | ✅ Completada | Sesión 2 | 2026-08-24 |
| FASE-R0-C | B3+B5 — Título Sección 1 condicional + contador Sección 6 | Baja-Media | ✅ Completada | Sesión 3 | 2026-08-24 |
| FASE-R0-D | B6+B7 — Propuesta condicional | Baja-Media | ✅ Completada | Sesión 4 | 2026-08-24 |
| FASE-R0-E | E2E — única ejecución v4complete Zione (delegate_task) | Media (ejecución) | ✅ Completada | Sesión 5 | 2026-08-24 |
| FASE-R0-F | Verificación AC1-AC12 + análisis post-implementación | Media | ✅ Completada | Sesión 6 | 2026-08-24 |
| FASE-RELEASE-4.72.1 | Docs oficiales + version bump (delegable) | Baja | ⏳ Pendiente | — | — |

## Archivos del Plan

| Archivo | Propósito |
|---------|-----------|
| `01-plan-maestro.md` | Diseño completo: fases, complejidad, R3, delegación, ACs |
| `dependencias-fases.md` | Diagrama de dependencias + tabla de conflictos de archivos |
| `05-prompt-inicio-sesion-fase-*.md` | Prompt de inicio por fase (1 por sesión de agente) |
| `06-checklist-implementacion.md` | Checklist maestro de estados |
| `09-documentacion-post-proyecto.md` | Acumulador documental (fuente de FASE-RELEASE) |
| `10-analisis-post-implementacion.md` | Lecciones, matriz de verificación B1-B7/AC1-AC12, decisiones |

## Contexto Fuente

- `.opencode/context/CONTEXT-REFACTOR-COHERENCIA-NARRATIVA-FUGAS-WHATSAPP-2026-08-22.md` — análisis completo validado contra código vivo (2026-08-22). **Lectura previa obligatoria de toda fase.**

## Reglas Clave del Plan

1. **R1**: Una fase por sesión. Sin excepciones.
2. **R2**: Máximo 60 iteraciones del agente por fase.
3. **R3**: Máx. 4 tareas + 0 comandos largos, ó 3 tareas + 1 comando largo por fase.
4. Cada fase de implementación ejecuta `log_phase_completion.py` al terminar (**SIN** `--release`). FASE-RELEASE no registra fases anteriores.
5. La única ejecución de `v4complete` del plan ocurre en **FASE-R0-E** (Zi One Luxury, https://zione.co/, onboarding real auto-cargado desde `output/clientes/`). **Nota recuperación 2026-08-24**: la corrida inicial fue bloqueada por un falso BLOCKED del gate tier_c (regresión externa: `FinancialFactors` sin import en `run_v4_complete_mode`); se aplicó el Protocolo de Recuperación con re-ejecución AUTORIZADA por el usuario en la misma sesión (fix + 6 tests + corrida 20260824_113525 → 7/7 smoke ✅).
6. Análisis post-implementación (`10-analisis-post-implementacion.md`) se actualiza al cierre de **cada** fase.

## Cómo Retomar

1. Leer este README + `06-checklist-implementacion.md` + `dependencias-fases.md`.
2. Identificar la primera fase con estado ⏳.
3. Abrir sesión nueva de agente con el prompt `05-prompt-inicio-sesion-fase-{X}.md` correspondiente.
