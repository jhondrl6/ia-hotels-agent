# 05-prompt-inicio-sesion-fase-RELEASE

**Fase:** RELEASE — Cierre documental v4.49.0 AGENTSMD-DRIFT
**Plan:** AGENTSMD-DRIFT
**Sesión:** Nueva (fresh)
**Iteraciones máx:** 60
**Depende de:** FASE-A-01a ✅, FASE-A-01b ✅, FASE-A-01c ✅
**Bloquea a:** —
**⚠️ FASE DOC-ONLY: NO modifica código fuente**

## Objetivo

Ejecutar el cierre documental de v4.49.0: version bump a 4.49.0, sincronización de headers, CHANGELOG, GUIA_TECNICA, SYSTEM_STATUS, DOMAIN_PRIMER, y validación final. Esta fase NO modifica código fuente — solo documentación y metadatos.

## Contexto de Fases Anteriores

**FASE-A-01a ✅:** AGENTS.md corregido (Solución 1: 9 pasos editoriales).
**FASE-A-01b ✅:** validate_agents_md.py creado (Solución 2: 6 checks) + integrado en CONTRIBUTING.md (Solución 4).
**FASE-A-01c ✅:** v4complete Hotel Castilla Real verificado (coherence report en 09-documentacion-post-proyecto.md).

**ROADMAP FASE A-01:** Este plan cierra FASE A-01 del ROADMAP (L377): "AGENTS.md auditado como contexto primario agente".

## Tareas

### T1: Diagnóstico inicial + sync_versions

**Diagnóstico:** Verificar el estado actual antes de modificar nada:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
cat VERSION.yaml | grep "^version:"
```

**Actualizar VERSION.yaml:**
Cambiar `version: "4.48.0"` → `version: "4.49.0"`
Cambiar `codename: "PIPELINE-FIX"` → `codename: "AGENTSMD-DRIFT"`
Cambiar `release_date: "2026-05-23"` → `release_date: "2026-05-26"`

**Sync versions:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/sync_versions.py
```

Esto sincroniza VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md.

**Verificar sincronización:**
```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### T2: CHANGELOG.md + GUIA_TECNICA.md

**Agregar entrada en CHANGELOG.md** (al inicio, después del header):

```markdown
## [4.49.0] - AGENTSMD-DRIFT — AGENTS.md Audit + validate_agents_md Gate + E2E Castilla Real — 2026-05-26

### Objetivo
Cerrar el drift documental en AGENTS.md (4 secciones desactualizadas post-FASE-0 + PIPELINE-FIX) e implementar un gate automatizado de coherencia documental.

### Cambios Implementados
- **Solución 1:** AGENTS.md corregido en 9 pasos editoriales — conteo tests 2,491→2,743, gates 9→11, módulos FASE-0 documentados, evidence_ledger marcado DEPRECADO, árbol data_validation refleja estructura real
- **Solución 2:** Creado `scripts/validate_agents_md.py` — 6 checks automáticos (modules_exist, test_count, gate_count, fase0_modules, no_deprecated_active, scripts_exist)
- **Solución 4:** Integrado validate_agents_md.py en `docs/CONTRIBUTING.md` §Post-Fase como Paso 5.5 obligatorio
- **E2E:** v4complete Hotel Castilla Real verificado (coherence: ver 09-documentacion)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `scripts/validate_agents_md.py` | Validador de coherencia AGENTS.md contra código vivo (6 checks) |
| `.opencode/plans/AGENTSMD-DRIFT/` | Plan completo de 4 fases + prompts + checklist |
| `evidence/FASE-A-01c/` | Evidencia v4complete Hotel Castilla Real |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `AGENTS.md` | 9 pasos editoriales — sincronización completa con código vivo |
| `docs/CONTRIBUTING.md` | Agregado Paso 5.5: validate_agents_md.py en flujo post-fase |
| `VERSION.yaml` | 4.48.0 → 4.49.0 (AGENTSMD-DRIFT) |

### Tests
- 0 tests nuevos (cambios editoriales + script de validación)
```

**Actualizar docs/GUIA_TECNICA.md:**

Agregar nota técnica para v4.49.0:

```markdown
### Notas de Cambios v4.49.0 — AGENTSMD-DRIFT

**Módulos afectados:** AGENTS.md, scripts/validate_agents_md.py, docs/CONTRIBUTING.md

**Problema:** AGENTS.md tenía drift factual en 4 secciones post-FASE-0 y PIPELINE-FIX. El header se sincronizaba vía version-sync pero el body no tenía mecanismo de auditoría. ROADMAP.md sí estaba actualizado.

**Solución:**
1. Corrección editorial one-shot de AGENTS.md (9 pasos)
2. Script `validate_agents_md.py` con 6 checks automáticos
3. Integración en flujo post-fase de CONTRIBUTING.md

**Backwards compatibility:** Total. Cambios editoriales en documentación y nuevo script de validación. Sin cambios en API, pipeline, ni lógica de negocio.

**Tests:** Sin cambios en suite de tests (2,743 tests, 0 regresiones).
```

### T3: Skills/workflows + SYSTEM_STATUS.md

**Actualizar SYSTEM_STATUS.md** (si existe) o crear entrada:
```bash
cat docs/SYSTEM_STATUS.md 2>/dev/null || echo "No existe, crear nueva entrada"
```

Si existe, agregar entrada v4.49.0 con estado de los subsistemas post-AGENTSMD-DRIFT.

**Skills/workflows:** No se requieren cambios en skills para este plan (es documental). Si `validate_agents_md.py` amerita una skill, documentarlo pero no crear ahora.

### T4: DOMAIN_PRIMER + validación final + commit

**Actualizar DOMAIN_PRIMER.md** (si existe):
```bash
ls docs/DOMAIN_PRIMER.md 2>/dev/null
```
Si existe, actualizar header con versión 4.49.0 y codename AGENTSMD-DRIFT.

**Validación final:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```
Debe pasar 4/4.

**Validar AGENTS.md con el nuevo script:**
```bash
./venv/Scripts/python.exe scripts/validate_agents_md.py
```
Debe dar 6/6 PASS.

**Commit:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
git add VERSION.yaml AGENTS.md docs/CONTRIBUTING.md docs/CHANGELOG.md docs/GUIA_TECNICA.md scripts/validate_agents_md.py .opencode/plans/AGENTSMD-DRIFT/ evidence/FASE-A-01c/ 09-documentacion-post-proyecto.md
git commit -m "release: v4.49.0 AGENTSMD-DRIFT — AGENTS.md audit + validate_agents_md gate + E2E Castilla Real"
```

**log_phase_completion.py (FASE-RELEASE):**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.49.0 \
    --desc "Cierre documental v4.49.0 AGENTSMD-DRIFT: version bump, sync, CHANGELOG, GUIA_TECNICA, SYSTEM_STATUS, DOMAIN_PRIMER, validaciones" \
    --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md" \
    --archivos-nuevos "scripts/validate_agents_md.py" \
    --tests "0" \
    --check-manual-docs
```

**Actualizar 09-documentacion-post-proyecto.md final:**
- Marcar todas las secciones con datos acumulados de A-01a, A-01b, A-01c
- Sección D final: métricas acumuladas de todo el plan

## Criterios de Completitud

- [ ] VERSION.yaml: 4.49.0, codename AGENTSMD-DRIFT
- [ ] sync_versions.py ejecutado (6 archivos sincronizados)
- [ ] version_consistency_checker.py: PASS
- [ ] CHANGELOG.md: entrada [4.49.0] con formato correcto
- [ ] docs/GUIA_TECNICA.md: nota técnica v4.49.0 agregada
- [ ] SYSTEM_STATUS.md: actualizado (si existe)
- [ ] DOMAIN_PRIMER.md: actualizado (si existe)
- [ ] run_all_validations.py --quick: 4/4 PASS
- [ ] validate_agents_md.py: 6/6 PASS
- [ ] Git commit realizado
- [ ] log_phase_completion.py ejecutado
- [ ] 09-documentacion-post-proyecto.md completo

## Restricciones

- Máximo 60 iteraciones
- **NO modificar código fuente (.py excepto validate_agents_md.py ya creado en A-01b)**
- **NO ejecutar v4complete ni v4audit**
- **NO modificar ROADMAP.md** (es manual por CONTRIBUTING.md L142)
- Solo documentación, metadatos, y commit
