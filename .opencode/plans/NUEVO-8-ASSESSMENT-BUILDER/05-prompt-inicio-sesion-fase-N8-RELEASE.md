# 05-prompt-inicio-sesion-fase-N8-RELEASE

**Fase:** N8-RELEASE — Documentación + Version Bump + Validación Final
**Plan:** NUEVO-8-ASSESSMENT-BUILDER
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** N8-D ✅ (v4complete E2E exitoso)
**Bloquea a:** —
**Tipo:** DIRECTA (documentación, sin comandos largos)
**Target version:** v4.50.0

---

## Objetivo

Cerrar el plan NUEVO-8 con documentación oficial: version bump, CHANGELOG, GUIA_TECNICA, sync, y validación final.

## Contexto de Fases Anteriores

**N8-A ✅:** AssessmentPayload dataclass (`modules/assessment_builder.py`)
**N8-B ✅:** AssessmentBuilder class + main.py migrado al builder
**N8-C ✅:** Extractores simplificados (~129→~30 líneas) + campos muertos eliminados
**N8-D ✅:** v4complete E2E verificado para Hotel Castilla Real

**Cambios acumulados:**
- Nuevo módulo: `modules/assessment_builder.py` (AssessmentPayload + AssessmentBuilder)
- Modificado: `main.py` (L2663-2754 reemplazado por builder)
- Modificado: `modules/quality_gates/publication_gates.py` (extractores simplificados)
- Tests nuevos: `tests/test_assessment_builder.py` (~29 tests), `tests/quality_gates/test_extractors_simplified.py`
- Líneas netas: ~130 eliminadas (extractores + campos zombie + metrics + coherence_report + hotel_url fallback), ~230 agregadas (builder + tests)

## Tareas

### T1: Diagnosticar estado + sync_versions.py
- Verificar que todas las fases N8-A a N8-D están registradas en REGISTRY.md
- Ejecutar sync_versions.py para propagar v4.50.0:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/sync_versions.py
```
- Verificar sincronización:
```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```
- **NOTA:** `sync_versions.py` usa `datetime.now()` para `{date}` — `last_update` en AGENTS.md será la fecha de hoy, no la fecha de release. Esto es comportamiento conocido (ver `phased-project-executor` skill).

### T2: Actualizar CHANGELOG.md + GUIA_TECNICA.md

**CHANGELOG.md — Agregar entrada v4.50.0:**
```markdown
## [4.50.0] - AssessmentBuilder: Assessment Dict Tipado — 2026-05-30

### Objetivo
Centralizar la construcción del assessment dict en una clase tipada (`AssessmentBuilder`) 
con esquema validable, eliminar ~120 líneas de extractores multi-path redundantes, 
y eliminar campos zombie/fantasma acumulados por fases anteriores.

### Cambios Implementados
- Creado `modules/assessment_builder.py` con `AssessmentPayload` dataclass (28 campos tipados) 
  y `AssessmentBuilder` con API fluida (9 métodos `.with_*()` + `.build()`)
- Migrado `main.py:2663-2754` (~87 líneas en 3 etapas) al builder (~15 líneas)
- Simplificados 5 extractores multi-path en `publication_gates.py` (~129 → ~30 líneas)
- Eliminados campos zombie: `quality_gate_issues/blockers/warnings` (locals().get(), 0 consumers)
- Eliminados campos dead: `coherence_checks/errors/warnings` (0 consumers), 
  `critical_issues_detected` (duplicado tautológico de `critical_issues`), 
  `metrics` dict (0 consumidores — solo duplicaba coherence_score),
  `coherence_report` del assessment dict (0 consumidores post-simplificación),
  `consistency_report` inyección en assessment dict (variable sí usada en summary JSON)
- Simplificado `hotel_url or url` fallback en gate L836 (builder garantiza el campo)
- Agregados al schema: `proposal_services`, `hotel_url`, `site_presence_report` 
  (antes buscados por gates pero nunca inyectados — defaults salvaban)
- Evitada duplicación de `SitePresenceChecker` (se ejecutaba 2 veces)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/assessment_builder.py` | AssessmentPayload dataclass + AssessmentBuilder class |
| `tests/test_assessment_builder.py` | 30 tests unitarios (dataclass + builder) |
| `tests/quality_gates/test_extractors_simplified.py` | 5 tests de extractores simplificados |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | L2663-2754 reemplazado por AssessmentBuilder (~87 → ~15 líneas); L2838 consistency_report inyección eliminada |
| `modules/quality_gates/publication_gates.py` | 5 extractores simplificados a acceso directo (~129 → ~30 líneas) |

### Tests
- 34 tests nuevos, 0 regresiones
- v4complete E2E verificado: Hotel Castilla Real, coherence 0.83, 9/11 gates
```

**GUIA_TECNICA.md — Agregar nota técnica:**

Buscar la última sección de "Notas de Cambios" y agregar:
```markdown
### Notas de Cambios v4.50.0 — AssessmentBuilder

**Módulos afectados:**
- `modules/assessment_builder.py` (NUEVO)
- `modules/quality_gates/publication_gates.py`
- `main.py`

**Problema:** El diccionario `assessment` que alimenta los 11 publication gates se construía 
manualmente en 3 etapas separadas (~87 líneas) sin tipado ni validación. Cada gate implementaba 
4-6 fallbacks defensivos (~129 líneas de extractores) porque el dict no tenía schema. Campos 
zombie (`quality_gate_*`, `coherence_checks`) se acumulaban sin consumidores.

**Solución:** `AssessmentBuilder` centraliza la construcción en una clase con dataclass tipado 
(`AssessmentPayload`, 28 campos). API fluida: `.with_core().with_validation()...build()`. 
Los extractores se simplifican a acceso directo (ahorro ~100 líneas). Campos zombie eliminados.

**Backwards compatibility:** El builder produce un `Dict[str, Any]` idéntico al contrato 
existente de `run_publication_gates()`. No se rompe ninguna interfaz pública.

**Tests:** 34 tests nuevos. v4complete E2E verificado sin regresiones.
```

### T3: Actualizar skills/workflows afectados + SYSTEM_STATUS.md

**3a. Verificar si hay skills que referencien el assessment dict:**
```bash
grep -r "assessment\[" .hermes/skills/ .agents/workflows/ --include="*.md" 2>/dev/null | head -20
grep -r "L2663\|L2687\|L2713\|L2717" .hermes/skills/ .agents/workflows/ --include="*.md" 2>/dev/null
```

**3b. Actualizar SYSTEM_STATUS.md:**
- Agregar entrada para v4.50.0
- Estado: OPERATIONAL
- Último v4complete verificado: Hotel Castilla Real

**3c. Actualizar DOMAIN_PRIMER.md:**
- Si existe, actualizar la versión y fecha en header y footer (2 ocurrencias)
- Comando: `grep -n "4\.[0-9]*\.[0-9]*" docs/DOMAIN_PRIMER.md 2>/dev/null`
- Si no existe DOMAIN_PRIMER.md, documentar en el log

### T4: Validación final + commit

**4a. run_all_validations.py:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
- Esperado: 4/4 PASS

**4b. Test suite final:**
```bash
./venv/Scripts/python.exe -m pytest tests/ -x --timeout=120 -q
```
- Esperado: 0 regresiones

**4c. Commit:**
```bash
git add -A
git status
git commit -m "release: v4.50.0 — AssessmentBuilder: Assessment Dict Tipado (NUEVO-8)

- Nuevo: modules/assessment_builder.py (AssessmentPayload + AssessmentBuilder)
- Migrado: main.py assessment dict → builder (~87 → ~15 líneas)
- Simplificado: publication_gates.py extractores (~129 → ~30 líneas)
- Eliminado: campos zombie (quality_gate_* x3, coherence_checks/errors/warnings,
  critical_issues_detected, metrics, coherence_report, consistency_report injection)
- Simplificado: hotel_url or url fallback en gate (builder garantiza el campo)
- Agregado: proposal_services, hotel_url, site_presence_report al schema
- Tests: 34 nuevos, 0 regresiones
- v4complete E2E verificado: Hotel Castilla Real"
```

## Criterios de Completitud
- [ ] T1: sync_versions.py ejecutado + version_consistency_checker OK
- [ ] T2: CHANGELOG.md entrada v4.50.0 + GUIA_TECNICA.md nota técnica
- [ ] T3: Skills/workflows verificados + SYSTEM_STATUS.md actualizado + DOMAIN_PRIMER.md
- [ ] T4: run_all_validations.py 4/4 + test suite 0 regresiones + commit

## Restricciones
- Máximo 60 iteraciones
- **NO modificar código fuente** — solo documentación
- **NO ejecutar v4complete**
- **NO registrar fases anteriores** (N8-A a N8-D ya se registraron a sí mismas)
- Python path: `./venv/Scripts/python.exe`
- Working directory: `/mnt/c/Users/Jhond/Github/iah-cli`

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli && \
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase N8-RELEASE \
    --desc "Release v4.50.0 — AssessmentBuilder documentacion final" \
    --archivos-nuevos "" \
    --archivos-mod "CHANGELOG.md,docs/GUIA_TECNICA.md,VERSION.yaml,SYSTEM_STATUS.md,docs/DOMAIN_PRIMER.md" \
    --tests "0" \
    --check-manual-docs
```

## Fin del Plan NUEVO-8

Todas las fases completadas. El plan NUEVO-8-ASSESSMENT-BUILDER queda cerrado con v4.50.0.
