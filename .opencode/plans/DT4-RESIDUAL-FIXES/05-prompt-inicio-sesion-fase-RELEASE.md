# FASE-RELEASE-v4.66.0 — Documentación Oficial + Version Bump

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (viable — solo YAML/MD + scripts, 0 imports de proyecto)
> **Iteraciones máx**: 60
> **Depende de**: FASE-6 ✅
> **Bloquea a**: —
> **⚠️ Última fase del proyecto**

## Contexto de Fases Anteriores

Todas las fases de implementación y E2E están completadas:
- **FASE-1**: pain_ledger_resolved injection → coverage gate integrado
- **FASE-2**: SitePresence normalization + wiring → boost aplicado en CoherenceValidator
- **FASE-3**: final_coherence_report → fuente única de score
- **FASE-4**: AlignmentResult DTO → reporting unificado
- **FASE-5**: Gate idempotency → ejecución única, sin mutaciones
- **FASE-6**: v4complete Zi One + verificación 14 criterios + análisis post-implementación

## Objetivo

Ejecutar el cierre documental oficial del repositorio: version bump, sincronización, CHANGELOG, GUIA_TECNICA, validaciones finales. **NO modificar código fuente.**

## Tareas

### T1: Diagnóstico inicial + Version bump + Sync

```bash
# 1a. Diagnóstico
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor

# 1b. Bump version en VERSION.yaml
# Cambiar:
#   version: "4.65.0" → version: "4.66.0"
#   codename: "...DT-4: Root cause reconciliation..." → codename: "DT-4 Residual Fixes: pain_ledger_resolved injection + SitePresence normalization + coherence/alignment unification + gate idempotency"
#   release_date: "2026-07-27" → release_date: "<HOY>"

# 1c. Sync versiones
./venv/Scripts/python.exe scripts/sync_versions.py
```

- [ ] version_consistency_checker.py pasa sin discrepancias graves
- [ ] doctor no reporta errores críticos
- [ ] VERSION.yaml actualizado a 4.66.0
- [ ] sync_versions.py ejecutado sin errores

### T2: CHANGELOG.md + GUIA_TECNICA.md

**CHANGELOG.md** — Nueva entrada `## [4.66.0] - DT-4 Residual Fixes — YYYY-MM-DD`:

```markdown
## [4.66.0] - DT-4 Residual Fixes — YYYY-MM-DD

### Objetivo
Corregir la causa raíz del coverage gate failure en DT-4: el pain_ledger_resolved
no se inyectaba en el assessment. Normalizar SitePresence, unificar coherence score,
unificar alignment reporting, y eliminar doble ejecución de gates.

### Cambios Implementados
- `modules/assessment_builder.py` — Agregado campo `pain_ledger_resolved` a AssessmentPayload + builder method `with_resolved_pain_ledger()`
- `main.py` — Carga e inyección de pain_ledger_resolved.json en assessment; SitePresence computado una vez y propagado; gates ejecutados una sola vez
- `modules/asset_generation/site_presence_adapter.py` — Nuevo adapter canónico para SitePresence (dataclass/dict/enum → dict unificado)
- `modules/asset_generation/v4_asset_orchestrator.py` — Expone pain_ledger_resolved en AssetGenerationResult; recibe y propaga site_presence_report; agrega final_coherence_report
- `modules/commercial_documents/coherence_validator.py` — 3 call sites ahora reciben site_presence_report normalizado
- `modules/quality_gates/publication_gates.py` — Eliminadas reconstrucciones fake de SitePresence y doble ejecución de gates; sin mutaciones al assessment
- `modules/quality_gates/alignment_result.py` — Nuevo AlignmentResult DTO canónico compartido
- `modules/quality_gates/delivery_quality_report.py` — Alineado con AlignmentResult del gate

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/site_presence_adapter.py` | Adapter canónico SitePresence dataclass/dict/enum |
| `modules/quality_gates/alignment_result.py` | AlignmentResult DTO compartido |
| `tests/quality_gates/test_coverage_gate_integration.py` | Test integrado reconciler→builder→gate |
| `tests/asset_generation/test_site_presence_adapter.py` | 5 tests de normalización SitePresence |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/assessment_builder.py` | Campo pain_ledger_resolved + with_resolved_pain_ledger() + with_coherence usa final |
| `modules/asset_generation/v4_asset_orchestrator.py` | Expone pain_ledger_resolved + recibe site_presence + final_coherence_report |
| `modules/commercial_documents/coherence_validator.py` | 3 call sites con site_presence_report |
| `modules/quality_gates/publication_gates.py` | Sin mutaciones, sin reconstrucciones fake, sin doble ejecución |
| `modules/quality_gates/delivery_quality_report.py` | Consume AlignmentResult canónico |
| `main.py` | Carga resolved ledger + SitePresence único + gates una vez |
| `VERSION.yaml` | 4.65.0 → 4.66.0 |

### Tests
- 1 test integrado coverage (reconciler→builder→gate)
- 5 tests normalización SitePresence
- 2 tests final_coherence
- 2 tests alignment consistency
- 3 tests gate idempotency
- 13 tests nuevos total; 0 regresiones en test suite existente
```

**GUIA_TECNICA.md** — Agregar sección "Notas de Cambios v4.66.0":

```markdown
### Notas de Cambios v4.66.0 — DT-4 Residual Fixes

**Módulos afectados**: assessment_builder, v4_asset_orchestrator, coherence_validator, publication_gates, main, delivery_quality_report

**Problema**: El coverage gate (coverage_no_silent_drop) fallaba porque el pain_ledger_resolved
generado por el PostOrchestratorReconciler nunca se inyectaba en el AssessmentPayload. SitePresence
se calculaba 4+ veces con shapes incompatibles. El score de coherencia no tenía fuente única. Los
gates se ejecutaban dos veces y mutaban el assessment.

**Solución**: 
1. Campo `pain_ledger_resolved` en AssessmentPayload + builder method + carga en main.py
2. Adapter canónico `normalize_site_presence()` que acepta dataclass/dict/enum
3. `final_coherence_report` como fuente única (pre/post conservados como trazabilidad)
4. `AlignmentResult` DTO compartido entre publication gates y delivery quality report
5. `check_publication_readiness()` ahora deriva de gate_results existentes sin re-ejecutar

**Backwards compatibility**: 
- Campos nuevos con default factory=list → consumidores existentes no afectados
- `check_publication_readiness()` mantiene firma original (gate_results es opcional)
- `CoherenceValidator.validate()` mantiene site_presence_report como keyword opcional
- AlignmentResult es nuevo; delivery_quality_report migrado para consumirlo
```

- [ ] CHANGELOG.md tiene entrada `[4.66.0]` con formato correcto (Objetivo, Cambios, Archivos, Tests)
- [ ] GUIA_TECNICA.md tiene nota técnica v4.66.0 con módulos, problema, solución, backwards compatibility
- [ ] No hay entradas duplicadas en CHANGELOG

### T3: Skills/Workflows + SYSTEM_STATUS + DOMAIN_PRIMER

```bash
# 3a. Validar skills/workflows
ls -la .agents/workflows/*.md

# 3b. Actualizar SYSTEM_STATUS.md
./venv/Scripts/python.exe scripts/doctor.py --status

# 3c. Regenerar DOMAIN_PRIMER (solo en RELEASE)
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] Skills/workflows listados correctamente
- [ ] SYSTEM_STATUS.md regenerado con versión 4.66.0
- [ ] DOMAIN_PRIMER.md regenerado (sin mojibake, encoding correcto)
- [ ] REGISTRY.md muestra versión 4.66.0

### T4: Symlink + Validación final + README audit + Commit

```bash
# 4a. Verificar symlink
ls -la .agent/workflows

# 4b. Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# 4c. README.md line-by-line audit
./venv/Scripts/python.exe -m pytest --collect-only -q 2>&1 | tail -1
find modules/ -name '*.py' ! -path '*__pycache__*' | wc -l

# 4d. Verificar cambios
git diff --stat

# 4e. Verificar pre-commit
git add -A && git commit -m "release: v4.66.0 — DT-4 Residual Fixes"
```

- [ ] Symlink `.agent/workflows` → `.agents/workflows` intacto
- [ ] `run_all_validations.py --quick` pasa (4/4)
- [ ] Test count en README.md coincide con `pytest --collect-only`
- [ ] Module count en README.md coincide con `find modules/`
- [ ] Fecha en banner README.md es la fecha actual
- [ ] Commit realizado con mensaje de release

## Criterios de Completitud

- [ ] T1: Version bump 4.65.0 → 4.66.0 + sync_versions OK
- [ ] T2: CHANGELOG + GUIA_TECNICA actualizados con formato correcto
- [ ] T3: SYSTEM_STATUS + DOMAIN_PRIMER regenerados, REGISTRY.md muestra v4.66.0
- [ ] T4: run_all_validations OK, README.md audit OK, commit realizado

## Restricciones

- **NO modificar código fuente** — solo documentación y versiones
- **NO modificar ROADMAP.md**
- **NO ejecutar v4complete**
- Máximo 60 iteraciones
- Si pre-commit hook falla: resolver issues, NO hacer commit con --no-verify

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.66.0 \
    --desc "Release 4.66.0: DT-4 Residual Fixes — pain_ledger_resolved injection + SitePresence normalization + coherence/alignment unification + gate idempotency" \
    --archivos-mod "VERSION.yaml,CHANGELOG.md,GUIA_TECNICA.md,REGISTRY.md,DOMAIN_PRIMER.md,README.md,AGENTS.md,.cursorrules,CONTRIBUTING.md,SYSTEM_STATUS.md" \
    --check-manual-docs
```

## 🏁 Fin del Proyecto

Después de esta fase, el proyecto DT-4 Residual Fixes está completo. El repositorio queda en v4.66.0 con todos los fixes integrados y documentados.
