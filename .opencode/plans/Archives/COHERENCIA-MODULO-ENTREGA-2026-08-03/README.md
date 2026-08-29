# Plan: COHERENCIA-MODULO-ENTREGA-2026-08-03

> Refactorización por fases para eliminar 21 desconexiones módulo↔entrega (D1-D12 + N1-N9)
> detectadas en el diagnóstico V6 de Zione (2026-08-01, re-auditoría 2026-08-03).
> Workflow: `phased_project_executor.md` v2.13.0 · **1 fase por sesión, sin excepciones.**

## Archivos del plan

| Archivo | Propósito |
|---------|-----------|
| `01-plan-maestro.md` | Objetivo, alcance, fases, complejidad, riesgos |
| `02-prompt-fase-A.md` | FASE-A: D1+D2 — contenido veraz (DIRECTO) |
| `03-prompt-fase-B.md` | FASE-B: D3+D4+N1 — finanzas honestas (DIRECTO, **mayor complejidad**) |
| `04-prompt-fase-C-A.md` | FASE-C-A: D5+N2 — gates reales (DIRECTO) |
| `05-prompt-fase-C-B.md` | FASE-C-B: D6+D7+D8 — textos dinámicos (DELEGADO parcial) |
| `06-prompt-fase-D.md` | FASE-D: D9-D12+N4+N3+N5-N8 — pulido+freshness (DELEGADO parcial) |
| `07-prompt-fase-E.md` | FASE-E: E2E v4complete Zi One Luxury (DELEGADO, única ejecución) |
| `08-prompt-fase-RELEASE.md` | FASE-RELEASE-4.70.0: docs oficiales (DELEGABLE) |
| `09-checklist-implementacion.md` | Estado global de fases y criterios |
| `10-analisis-post-implementacion.md` | Fixes superados + lecciones aprendidas (se llena en E/RELEASE) |
| `11-documentacion-post-proyecto.md` | Datos acumulativos para CHANGELOG/GUIA_TECNICA |
| `dependencias-fases.md` | Diagrama, conflictos de archivos, matriz hallazgo→fase |

## Progreso

| Fase | Hallazgos | Estado | Sesión | Modo |
|------|-----------|--------|--------|------|
| FASE-A | D1, D2 | ✅ | 2026-08-03 | Directo |
| FASE-B | D3, D4, N1 | ✅ | 2026-08-03 | Directo ⚠️ |
| FASE-C-A | D5, N2 | ✅ | 2026-08-03 | Directo |
| FASE-C-B | D6, D7, D8 | ✅ | 2026-08-03 | Delegado parcial |
| FASE-D | D9-D12, N3-N8 (parcial) | ✅ | 2026-08-04 | Delegado parcial |
| FASE-E | E2E Zione | ✅ | 2026-08-04 | Delegado |
| FASE-RELEASE-4.70.0 | Docs | ✅ | 2026-08-04 | Delegable |

**Fase de mayor complejidad técnica**: FASE-B (ver `01-plan-maestro.md` §3).

## Cómo ejecutar

1. Abrir una **sesión nueva** de agente por fase.
2. El agente lee su `NN-prompt-fase-X.md` y lo ejecuta como mandato completo.
3. Al cerrar: checklist ✅ + `log_phase_completion.py` + actualizar `dependencias-fases.md`, este README y `11-documentacion-post-proyecto.md`.
4. Si la fase no completa (≤60 iteraciones): marcar ⏳ INCOMPLETA con checkpoint y retomar en sesión fresca.

## Fuentes

- Contexto: `/.opencode/context/Historico/CONTEXT-DIAGNOSTICO-COHERENCIA-MODULO-ENTREGA-2026-08-02.md`
- Baseline auditado: run 2026-08-01 (`output/v4_complete/`, ZIP zione_20260801)
- Onboarding real: `output/clientes/zi-one-luxury_onboarding.yaml` (Tier A: 34 hab, 800 res/mes, ADR 290K, canal 40%)
