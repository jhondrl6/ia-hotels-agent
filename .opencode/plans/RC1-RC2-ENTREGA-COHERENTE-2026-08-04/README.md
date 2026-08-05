# Plan: Coherencia Propuesta↔Diagnóstico + Gates + Entrega (RC1/RC2/RC3)

**ID**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04
**Fuente**: `.opencode/context/CONTEXT-VALIDACION-COHERENCIA-PLAN-ENTREGA-2026-08-04.md`
**Skill rectora**: `.agents/workflows/phased_project_executor.md` v2.14.0 (R1/R2/R3 estrictas)
**Versión actual**: 4.70.0 → **Release objetivo: 4.71.0**
**Tests baseline**: 3,215 (pytest --collect-only, 2026-08-04)

---

## Objetivo

Eliminar las 3 causas raíz identificadas en la validación de coherencia del plan
`COHERENCIA-MODULO-ENTREGA-2026-08-03` y certificar los fixes con **UNA única
ejecución E2E de `v4complete`** contra **Zi One Luxury** (https://zione.co/) con
onboarding real (`output/clientes/zi-one-luxury_onboarding.yaml`).

| Causa raíz | Hallazgos | Severidad | Fase |
|------------|-----------|-----------|------|
| **RC1** — fuente de verdad de costos aplicada a medias (propuesta hardcodeada) | N10, N17, N18, N19 | ALTA | FASE-B |
| **RC2** — gates comerciales: inputs no cableados + veredicto oculto pero enviado | N11, N15, N16 (+N21) | MEDIA | FASE-C, FASE-D |
| **RC3** — higiene documental sin enforcement | N12, N13, N14, N20 | BAJA | FASE-E |
| **Prerrequisito** — tests patológicos L1/L11 sin diagnosticar | 3 archivos | CRÍTICO | FASE-A |
| **Seguimientos heredados** — S5 (occupancy "regional"), S7 (loader onboarding) | S5, S7 | MEDIA | FASE-D |

## Tabla de Fases (1 fase = 1 sesión, sin excepciones — R1)

| Fase | Sesión | Alcance | Modo ejecución | Delegate task |
|------|--------|---------|----------------|---------------|
| **FASE-A** | 1 | Triage tests patológicos (prerrequisito RC1) | Agente principal DIRECTO | ❌ No (código+tests puro, sin overhead — §Regla código+tests) |
| **FASE-B** | 2 | RC1: parametrizar tabla de servicios de la propuesta desde `opportunity_scores` | Agente principal DIRECTO | ❌ No (decisión arquitectónica cross-module — §Regla DT-3) |
| **FASE-C** | 3 | RC2-a: fix CG-CLAIM-VS-EVIDENCE (N11) + cablear CG-TIER-CONSISTENCY (N15) | Agente principal DIRECTO | ❌ No (mismos archivos, trabajo secuencial) |
| **FASE-D** | 4 | RC2-b: política ZIP entrega (N16/N21) + S7 loader onboarding + S5 occupancy | **Subagentes vía delegate_task** (3 tracks independientes) | ✅ Sí |
| **FASE-E** | 5 | RC3: higiene documental R3.1-R3.4 + enforcement `_check_prompts_no_release` en `run_all_validations.py` | **Subagente vía delegate_task** (MD/YAML + 1 script stdlib-only, sin imports) | ✅ Sí |
| **FASE-F** | 6 | E2E: v4complete Zione + verificación de TODOS los fixes + análisis post-implementación | **delegate_task para v4complete** (timeout=900) + parent verifica | ✅ Sí (solo el comando largo) |
| **FASE-RELEASE-4.71.0** | 7 | Version bump, CHANGELOG, GUIA_TECNICA, sync, validaciones | **Subagente vía delegate_task** (sin imports del proyecto — §Paso-7 TIP) | ✅ Sí |

## ⚠️ Fase de MAYOR complejidad técnica: FASE-B (RC1)

Razones:
1. **Decisión arquitectónica cross-module**: el generador de propuesta debe consumir
   `opportunity_scores` del pipeline (financial_engine → report → proposal) mediante un
   **mapa inverso** `asset_type → brecha_id` (construido invirtiendo
   `pain_solution_mapper.PAIN_SOLUTION_MAP[bid]["assets"]`) — toca 4 hallazgos a la vez
   (N10 costos, N17 mapeo invertido, N18 hardcode L1250, N19 servicio fantasma).
   **Nota CR-1**: `ASSET_TO_PAIN_ID` (L1185-1191) solo cubre 6/8 services; el mapa
   inverso desde `pain_solution_mapper` cubre los 8 y desempata ambigüedad multi-brecha.
2. **Riesgo de regresión comercial**: son cifras de fuga que ve el cliente; un error
   reproduce exactamente la incoherencia que el plan elimina.
3. **Zona con tests patológicos**: los tests del área de propuesta son los que causaron
   bloqueos reales (~8GB RAM, cuelgues) — por eso FASE-A es prerrequisito.
4. Requiere evidencia mixta dinámica+estática (L7) y forense de regresión con backup (L4/L5).

**NO es delegable** por la regla de decisión arquitectónica del executor (lección DT-3).

## Criterios de Éxito Globales

- [ ] `BREACH_BY_ASSET` eliminado/reemplazado por construcción dinámica desde
      `opportunity_scores` vía mapa inverso `pain_solution_mapper` (gate D10).
      Costos, ranks y labels de la tabla de servicios de la propuesta == `opportunity_scores`
      del mismo run.
- [ ] CG-CLAIM-VS-EVIDENCE no dispara falso positivo con texto condicional "si...no aparece".
- [ ] CG-TIER-CONSISTENCY valida inputs reales (o falla explícitamente; nunca pasa vacuo).
- [ ] ZIP de entrega sin `commercial_gates_report*` BLOCKING junto a doc PASSED, y sin
      artefactos de runs anteriores.
- [ ] `v4complete` para Zione carga onboarding real ("Onboarding data loaded" en log,
      NO "Using defaults") y coherencia ≥ 0.8.
- [ ] Check de cierre OBLIGATORIO: costos/numeración de brechas IDÉNTICOS en diagnóstico
      Y propuesta del run E2E.
- [ ] `run_all_validations.py --quick` TOTAL PASS en RELEASE (conteo dinámico del script; desde FASE-E incluye el check **"Prompts No Release"**) + `validate_agents_md.py` PASS.
- [ ] Análisis post-implementación con lecciones aprendidas en FASE-F.
- [ ] S7 verificado en aislamiento ANTES de lanzar v4complete (CR-6, lección L13/L14).
- [ ] V10: 0 blocking failures + READY_FOR_PUBLICATION (no "12/12" — conteo es dinámico).

## Protocolo transversal (lecciones L1-L15 capitalizadas)

1. NUNCA suite completa de `tests/commercial_documents` ni `tests/financial_engine` (L1/L11).
2. `log_phase_completion.py` SIN `--release` en fases intermedias (L3/L9).
3. Backup `Copy-Item` + `git checkout HEAD --` + restaurar siempre (L4/L5; `git stash` DENEGADO).
4. Conteo de tests nuevos desde `git diff tests/` (L8).
5. Verificación de texto/costos con Python UTF-8 o ripgrep, nunca Select-String (L15).
6. Pytest siempre redirigido a archivo, nunca pipeado (L6).
7. Evidencia proactiva en `evidence/{fase}/` inmediatamente tras v4complete (executor §Evidencia).
8. Si el usuario interviene: `git diff --stat` + `git status --short` primero (L10).

## Estructura del plan

```
RC1-RC2-ENTREGA-COHERENTE-2026-08-04/
├── README.md                                    (este archivo)
├── dependencias-fases.md
├── 01-plan-maestro.md
├── 05-prompt-inicio-sesion-fase-A.md
├── 05-prompt-inicio-sesion-fase-B.md
├── 05-prompt-inicio-sesion-fase-C.md
├── 05-prompt-inicio-sesion-fase-D.md
├── 05-prompt-inicio-sesion-fase-E.md
├── 05-prompt-inicio-sesion-fase-F.md
├── 05-prompt-inicio-sesion-fase-RELEASE.md
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
└── 10-analisis-post-implementacion.md
```

**Regla de dependencia**: FASE-RELEASE-4.71.0 solo se ejecuta cuando A-F estén ✅.

## Progreso

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | ✅ Completa | 2026-08-05 | Cuarentena 3 archivos (40 tests). 3175 collected. Lista segura: 13 archivos. |
| FASE-B | ✅ Completa | 2026-08-05 | RC1: `_build_dynamic_breach_map` + cableado opportunity_scores. 9 tests nuevos, 0 regresiones. |
| FASE-C | ✅ Completa | 2026-08-05 | RC2-a: CG-CLAIM-VS-EVIDENCE split+condicionales (N11) + CG-TIER-CONSISTENCY cableado (N15). 20 tests nuevos, 0 regresiones. |
| FASE-D | ✅ Completa | 2026-08-05 | RC2-b: ZIP sin gate reports + filtro run + fallback loader + occupancy label. 23 tests nuevos. |
| FASE-E | ✅ Completa | 2026-08-05 | RC3: prompts sin --release + enforcement + conteos fuente viva + evidencia N3. |
| FASE-F | ✅ Completa | 2026-08-05 | Run E2E único OK (coherence 0.9238). V1-V10: 10/10 PASS tras recuperación S5b (main.py FASE-K + PrecisionValidator). |
| FASE-RELEASE | ⬜ Pendiente | — | Desbloqueada: A-F ✅. |
