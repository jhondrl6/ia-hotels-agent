# FASE-RELEASE v4.60.0 — Cierre y Documentación

## Contexto

Esta fase finaliza el plan REFACTOR-CAPEX-BREAKDOWN. Todas las fases de implementación (FASE-1 a FASE-4) deben estar completadas (✅) antes de ejecutar RELEASE.

**Esta fase NO modifica código fuente.** Solo sincroniza versiones, actualiza documentación oficial, y valida consistencia del repositorio.

---

## Datos de Entrada (de FASE-1 a FASE-4)

| Fase | Finding | Archivos Modificados | Tests |
|------|---------|---------------------|-------|
| FASE-1 | F1: Template CAPEX fix | `propuesta_v6_template.md` | 1 nuevo (integridad pipes) |
| FASE-2 | F7+F8: Generator cleanup | `v4_proposal_generator.py` | 0 nuevos (regresión) |
| FASE-3 | F6: Coherence checklist | `v4_proposal_generator.py` | 0 nuevos (regresión) |
| FASE-4 | Verificación v4complete | (ninguno — solo verificación) | N/A |

---

## Tareas

### T1: Version Bump en VERSION.yaml

Editar `VERSION.yaml`:
```yaml
project: "IA Hoteles Agent CLI"
version: "4.60.0"
codename: "CAPEX-BREAKDOWN-FIX"
release_date: "2026-05-29"
plan_maestro_version: "v2.6.0"
```

### T2: Sincronizar Versiones

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Sync VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md
./venv/Scripts/python.exe scripts/sync_versions.py

# Verificar sincronización
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

**Nota:** Si `sync_versions.py` reporta WARN sobre README.md, es esperado y harmless.

### T3: Validar CHANGELOG.md

Verificar que la entrada `[4.60.0]` tiene todas las secciones requeridas por CONTRIBUTING.md:

```markdown
## [4.60.0] - CAPEX Breakdown Fix & Generator Cleanup — 2026-05-29

### Objetivo
Fix de tabla CAPEX corrupta (tablas markdown anidadas) + limpieza de código muerto en generator

### Cambios Implementados
- **F1**: Movido `${capex_breakdown_table}` a sección independiente (fix tablas anidadas)
- **F6**: Eliminado `_build_coherence_checklist()` (código muerto, placeholder inexistente) [o integrado]
- **F7**: Eliminadas 9 keys huérfanas del template data dict
- **F8**: Fallback de `_build_capex_breakdown_table()` ahora incluye header row

### Archivos Nuevos
(Ninguno — solo modificaciones)

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/templates/propuesta_v6_template.md` | CAPEX desglose movido a sección propia |
| `modules/commercial_documents/v4_proposal_generator.py` | Keys huérfanas eliminadas, fallback con header, coherence checklist resuelto |
| `tests/test_capex_rename.py` | Nuevo test de integridad de pipes |

### Tests
- 1 test nuevo (integridad de pipes en tabla CAPEX)
- 0 regresiones en tests existentes
- v4complete para Hotel Castilla Real: todos los fixes verificados
```

### T4: Validar GUIA_TECNICA.md

Verificar nota técnica para v4.60.0 con:
- [ ] Módulo afectado: `modules/commercial_documents/`
- [ ] Problema: tablas markdown anidadas + código muerto
- [ ] Solución: sección propia + cleanup
- [ ] Backwards compatibility: ✅ sin breaking changes
- [ ] Tests: integridad de pipes

### T5: run_all_validations.py

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Nota:** Si hay fallos de pre-commit o tests pre-existentes (NO relacionados con este plan), NO cuentan contra RELEASE. Verificar con `git stash` si es necesario distinguir fallos nuevos vs pre-existentes.

### T6: Git Tag y Push

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
git add -A
git commit -m "v4.60.0: CAPEX Breakdown Fix + Generator Cleanup (F1/F6/F7/F8)"
git tag v4.60.0
git push origin main --tags
```

---

## Criterios de Completitud

- [ ] **T1**: VERSION.yaml con version=4.60.0 y codename=CAPEX-BREAKDOWN-FIX
- [ ] **T2**: sync_versions.py ejecutado, sin errores críticos
- [ ] **T3**: CHANGELOG.md con entrada [4.60.0] completa (todas las secciones)
- [ ] **T4**: GUIA_TECNICA.md con nota v4.60.0
- [ ] **T5**: run_all_validations.py ejecutado (fallos pre-existentes documentados)
- [ ] **T6**: Commit + tag v4.60.0 + push exitoso

---

## Restricciones

- **NO modificar código fuente** (eso fue FASE-1 a FASE-3)
- **NO ejecutar v4complete** (eso fue FASE-4)
- **Máximo 60 iteraciones**
- **Cada fase se auto-registró** con log_phase_completion.py — RELEASE NO registra fases anteriores

---

## Budget de Iteraciones Estimado

```
T1 (VERSION.yaml): ~3 iters
T2 (sync_versions): ~5 iters
T3 (CHANGELOG): ~5-8 iters
T4 (GUIA_TECNICA): ~5 iters
T5 (validations): ~5-8 iters
T6 (git): ~5 iters
Docs cascade: ~10 iters

Total estimado: 38-44 iters (dentro de 60)
```
