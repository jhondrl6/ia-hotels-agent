# FASE-RELEASE-4.74.0 — Cierre y documentación oficial

**ID**: VALIDADOR-URL-PROPIA / FASE-RELEASE-4.74.0
**Objetivo**: Release 4.74.0 — version bump, sync a 6 archivos, CHANGELOG y GUIA_TECNICA oficiales, validaciones finales. NO modifica código fuente.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C ✅, FASE-D ✅, FASE-VERIFY ✅
**Duración estimada**: 1 hora (~38-48 iteraciones)
**Skill**: `phased_project_executor.md` v2.17.0 §Paso-7

## Modo de ejecución (regla del executor)

**DELEGABLE a subagente** — solo edita YAML/MD y ejecuta scripts (sin imports del proyecto; confirmado en BUGS-ONBOARDING-ADR: 18 tool calls / ~4 min). El agente principal verifica el diff al integrar.

## Contexto

Versión actual 4.73.0 (codename Reparacion-Pipeline-Salento-Real) → 4.74.0 con el guard de URL propia. Datos acumulados para CHANGELOG/GUIA_TECNICA: `09-documentacion-post-proyecto.md` (secciones A-E). Las fases A-D YA se registraron con `log_phase_completion.py` (verificar en REGISTRY); RELEASE NO registra fases anteriores (regla §2.5 anti-deuda).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A / B / C / D | ✅ Completadas |
| FASE-VERIFY | ✅ Completada (AC1-AC8 certificados) |
| FASE-RELEASE-4.74.0 | ⏳ En progreso (esta sesión) |

## Tareas (E1-E8b del executor + pasos obligatorios CONTRIBUTING)

1. **E1 Diagnóstico**: `python scripts/version_consistency_checker.py` + `python main.py --doctor`.
2. **Bump**: `VERSION.yaml` → `version: "4.74.0"`, codename sugerido `Guard-URL-Propia`, release_date actual, comentario de versión (fases A-D + VERIFY, ACs, tests nuevos, 0 regresiones).
3. **E2 Sync**: `python scripts/sync_versions.py` (VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md).
4. **E3 CHANGELOG.md** — entrada `## [4.74.0] - Guard de URL propia (VALIDADOR-URL-PROPIA) — YYYY-MM-DD` con secciones obligatorias: Objetivo / Cambios Implementados / Archivos Nuevos / Archivos Modificados / Tests.
5. **E4 GUIA_TECNICA.md** — "Notas de Cambios v4.74.0": módulos afectados, problema (GA-1/GA-2), solución (guard blocklistado ortogonal), backwards compatibility (sitios propios sin cambio; `--force` documentado).
6. **E5 Skills/workflows**: `ls .agents/workflows/*.md` vs README.md del directorio.
7. **E6 SYSTEM_STATUS**: `python scripts/doctor.py --status`.
8. **E7 DOMAIN_PRIMER**: `python scripts/doctor.py --regenerate-domain-primer` y en RELEASE `python scripts/doctor.py --context`.
9. **E8 Symlink + validación**: symlink `.agent/workflows` intacto; `python scripts/run_all_validations.py --quick` TOTAL PASS; `git diff --stat`.
10. **E8b README audit**: conteo real `pytest --collect-only -q | tail -1` + `find modules/ -name '*.py' ! -path '*__pycache__*' | wc -l` vs README (banner, Estado del Proyecto, Calidad Garantizada); fecha del banner actual.
11. **OBLIGATORIOS CONTRIBUTING (memoria — no están en E1-E8b)**:
    - `python scripts/validate_agents_md.py` → si FAIL (p. ej. gate_count drift), corregir AGENTS.md ANTES de continuar.
    - `python scripts/validate_document_integration.py`.
    - Regla: ANTES del commit final SIEMPRE `validate_agents_md.py` + `run_all_validations.py --quick` + `validate_document_integration.py` (3 gates independientes).
12. **Registro release**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.74.0 --desc "Release 4.74.0: Guard de URL propia (VALIDADOR-URL-PROPIA)" \
    --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md,AGENTS.md,README.md" \
    --check-manual-docs
```
13. Completar `10-analisis-post-implementacion.md` → Checklist de Cierre + Métricas de Ejecución finales; write-back final de lecciones (memoria + re-ingesta del 10-analisis a QMind `iah-cli-lecciones` ANTES de archivar).
14. Commit final.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md` → FASE-RELEASE ✅.
2. `06-checklist-implementacion.md` → fila RELEASE ✅; proyecto COMPLETADO.
3. `README.md` del plan → estado final.
4. Archivar el contexto disparador según convención: evaluar mover `.opencode/context/CONTEXT-GAP-URL-NO-PROPIA-SONDA-2026-08-29.md` a `.opencode/context/Historico/` (el contenido queda congelado; QMind no requiere acción por el move) — SOLO tras el write-back final.

## Criterios de Completitud (CHECKLIST)

- [ ] VERSION.yaml 4.74.0 + sync a 6 archivos verificado
- [ ] CHANGELOG con las 5 secciones obligatorias, sin duplicados
- [ ] GUIA_TECNICA con nota v4.74.0 completa
- [ ] `validate_agents_md.py` + `validate_document_integration.py` + `run_all_validations.py --quick` → PASS
- [ ] README audit (conteos reales) verificado
- [ ] 10-analisis cerrado + write-back de lecciones
- [ ] Commit final

## Restricciones

- **NO modifica código fuente** (si un gate exige código, marcar ⏳ INCOMPLETA y abrir sesión de recuperación).
- **NO ejecuta v4complete.**
- **Máximo 60 iteraciones** (R2).
- NO registrar fases anteriores (ya lo hicieron A-D).
