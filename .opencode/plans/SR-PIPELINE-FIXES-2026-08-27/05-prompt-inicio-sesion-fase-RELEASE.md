# FASE-RELEASE — v4.73.0 (DELEGABLE)

**ID**: FASE-RELEASE-4.73.0
**Objetivo**: Publicar la versión **4.73.0** con los fixes SR-A…SR-G verificados en VERIFY. Ejecutar el flujo documental obligatorio completo (AGENTS.md §Flujo-Documental-Obligatorio): version sync → CHANGELOG → GUIA_TECNICA → validaciones → SYSTEM_STATUS → DOMAIN_PRIMER → registro con marker de release y Version Sync Gate.
**Dependencias**: FASE-VERIFY ✅ (veredicto global: fixes superados).
**Complejidad**: Baja · **Delegación**: ✅ DELEGABLE (TIP del executor §Paso-7 — pasos mecánicos E1-E8b con resultado binario; el orquestador revisa el resultado antes de cerrar el plan)
**Duración estimada**: 45-60 min · **Presupuesto**: 4 tareas + 0 comandos largos (R3)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones. R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.
- **Fuente única de versión**: `VERSION.yaml`. Nunca hardcodear versiones en código ni docs (L27).

## Contexto

**Lectura previa obligatoria**: AGENTS.md §Flujo-Documental-Obligatorio + executor §Paso-7 + `docs/contributing/documentation_rules.md` + `docs/contributing/validation.md`.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-H, FASE-VERIFY | ✅ Completadas |

### Entrada de la Fase
- `VERSION.yaml`: 4.72.2 → objetivo **4.73.0** (release_date: fecha de hoy)
- FASE-VERIFY: veredicto "fixes superados" + matriz AC 13/13
- `09-documentacion-post-proyecto.md`: notas por fase listas para CHANGELOG/GUIA_TECNICA

## Tareas

### T1: Version bump + sincronización (E1-E2)
**Criterios**:
- [ ] `VERSION.yaml` → `version: 4.73.0` + `release_date` de hoy
- [ ] `./venv/Scripts/python.exe scripts/sync_versions.py` → propaga a 6 archivos (AGENTS, README, .cursorrules, CONTRIBUTING, GUIA_TECNICA, REGISTRY)
- [ ] `./venv/Scripts/python.exe scripts/version_consistency_checker.py` sin divergencias

### T2: Documentación oficial (E3-E5)
**Criterios**:
- [ ] `CHANGELOG.md` con formato CONTRIBUTING: `### Objetivo / ### Cambios / ### Archivos Nuevos / ### Archivos Modificados / ### Tests`
- [ ] `GUIA_TECNICA.md`: nota técnica por fase (SR-A…SR-G + VERIFY)
- [ ] REGISTRY.md se actualiza vía el registro del cierre (T4)

### T3: Validaciones y estado del sistema (E6-E8b)
**Criterios**:
- [ ] `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` → TOTAL PASS (4/4 checks)
- [ ] `./venv/Scripts/python.exe scripts/validate_agents_md.py` → PASS (gate de coherencia AGENTS.md)
- [ ] `./venv/Scripts/python.exe scripts/validate_document_integration.py` → PASS (gate de no-regresión documental)
- [ ] `./venv/Scripts/python.exe scripts/doctor.py --status` (SYSTEM_STATUS.md) + `doctor.py --regenerate-domain-primer` (E7) + `doctor.py --context` (coherencia ≥ 0.8)
- [ ] E8b: README audit — tabla de progreso del plan al 100% (10/10 fases ✅)
- [ ] Suite de regresión 26/26 (`tests/regression/`)

### T4: Registro de release + cierre del plan
**Criterios**:
- [ ] Registro CON marker de release (ÚNICO con `--release` de todo el plan):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE-4.73.0 --desc "Release v4.73.0: pipeline fixes Salento Real (SR-A..SR-G) verificados en E2E (VERIFY); alignment/coherencia/preflight/canonicalizacion/self-healing" --fases SR-A SR-B SR-C SR-D SR-E SR-F SR-G SR-H VERIFY --check-manual-docs --release
```
- [ ] `evidence/FASE-RELEASE/` → diff acumulado (`git diff --stat` + `git diff --name-status` desde el inicio del plan) + salidas de validaciones
- [ ] `10-analisis` §checklist de cierre completado (última casilla)
- [ ] Plan completo 10/10 fases ✅ en `README.md` del plan

## Tests Obligatorios

| Test | Comando | Criterio de Éxito |
|------|---------|-------------------|
| Regresión permanente | `./venv/Scripts/python.exe -m pytest tests/regression/ -v > temp/fase_release_tests.txt 2>&1` | 26/26 |
| Validaciones quick | `scripts/run_all_validations.py --quick` | TOTAL PASS |
| Coherencia documental | `scripts/validate_document_integration.py` | PASS |
| Consistencia de versión | `scripts/version_consistency_checker.py` | 0 divergencias |

## Criterios de Completitud (CHECKLIST)

- [ ] `VERSION.yaml` = 4.73.0 y 6 archivos sincronizados
- [ ] CHANGELOG + GUIA_TECNICA en formato oficial
- [ ] Todas las validaciones en verde
- [ ] Registro de release hecho con `--release` (marker + Version Sync Gate)
- [ ] Plan 10/10 fases completadas; `evidence/FASE-RELEASE/` completo

## Restricciones

- NO modificar código funcional (solo docs + versión).
- NO ejecutar v4complete/v4audit (la corrida única ya ocurrió en SR-H).
- Si `validate_document_integration.py` falla → corregir los docs (NUNCA saltarse el gate).
- NO crear ramas/commits automáticos sin confirmación del usuario.
- Delegable; el orquestador revisa el resultado antes de declarar el plan terminado.
- AC10: la financiera ya está verificada en VERIFY — aquí solo consistencia de versión y docs.
