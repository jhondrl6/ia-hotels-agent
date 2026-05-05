# FASE-SCORING-C: Documentación Cascade

**ID**: FASE-SCORING-C
**Objetivo**: Ejecutar la cascada de documentación oficial: log_phase_completion para las 3 fases, CHANGELOG v4.40.1, GUIA_TECNICA, sync_versions, validaciones finales
**Dependencias**: SCORING-A ✅ Completada + SCORING-B ✅ Completada
**Duración estimada**: 30-45 min
**Skill**: `iah-cli-phased-execution`

---

## Contexto

SCORING-A y SCORING-B están completadas. El código ya refleja:
- `_build_scoring_breakdown()` muestra TODOS los factores con marcadores visuales (✅/~~tachado~~)
- Los 4 pilares (SEO, GEO, AEO, IAO) tienen breakdown en el diagnóstico

Esta fase NO modifica código fuente. Solo ejecuta documentación oficial del repositorio siguiendo `docs/CONTRIBUTING.md`.

**Contexto validado:** `.opencode/context/scoring-transparency-context.md` (2026-05-05)
**Plan maestro:** `.opencode/plans/SCORING-TRANSPARENCY/README.md`

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| SCORING-A | ✅ Completada |
| SCORING-B | ✅ Completada |

### Base Técnica Disponible

- `scripts/log_phase_completion.py` — registra fases en REGISTRY.md
- `scripts/sync_versions.py` — sincroniza VERSION.yaml → 6 archivos
- `scripts/version_consistency_checker.py` — verifica consistencia
- `scripts/run_all_validations.py` — validación final
- `scripts/doctor.py` — diagnóstico del ecosistema
- `docs/CHANGELOG.md` — entradas de versiones
- `docs/GUIA_TECNICA.md` — notas técnicas
- `docs/CONTRIBUTING.md` — formato oficial de documentación

---

## Tareas

### Tarea 1: Registrar las 3 fases en REGISTRY.md

**Objetivo**: Ejecutar `log_phase_completion.py` para SCORING-A, SCORING-B, SCORING-C

**Comandos**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# Fase SCORING-A
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-A \
    --desc "Fix de filtrado en _build_scoring_breakdown() para mostrar todos los factores con marcador visual" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "0" \
    --check-manual-docs

# Fase SCORING-B
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-B \
    --desc "Extension del scoring breakdown a los 4 pilares (SEO, GEO, AEO, IAO)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "0" \
    --check-manual-docs

# Fase SCORING-C (auto-referencia)
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-SCORING-C \
    --desc "Documentacion cascade: CHANGELOG v4.40.1, GUIA_TECNICA, REGISTRY, validaciones" \
    --archivos-mod "docs/CHANGELOG.md,docs/GUIA_TECNICA.md" \
    --check-manual-docs
```

**Criterios de aceptación**:
- [ ] REGISTRY.md tiene 3 nuevas entradas (SCORING-A, SCORING-B, SCORING-C)
- [ ] Ningún comando reporta error
- [ ] DOCUMENTATION AUDIT no muestra [GAP] (o si los muestra, proceder a Tarea 3)

### Tarea 2: Crear entrada CHANGELOG.md v4.40.1

**Objetivo**: Actualizar CHANGELOG.md con entrada para versión 4.40.1

**Formato (según `docs/CONTRIBUTING.md §78-85`)**:

```markdown
## [4.40.1] - Scoring Transparency — 2026-05-05

### Objetivo
Transparentar el sistema de scoring de los 4 pilares (SEO, GEO, AEO, IAO) en el diagnóstico generado por v4complete, mostrando todos los factores del checklist con marcadores visuales.

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_scoring_breakdown()` ahora muestra TODOS los factores (TRUE con ✅, FALSE con ~~tachado~~) en lugar de filtrar solo los TRUE
- `modules/commercial_documents/v4_diagnostic_generator.py` — Agregadas 3 asignaciones de template data (`seo_score_breakdown`, `aeo_score_breakdown`, `iao_score_breakdown`) para extender el breakdown a los 4 pilares
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Agregados 3 placeholders (`${seo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}`) para renderizar los breakdowns en el diagnóstico

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Fix L276-285: iteración completa con marcadores; extensión L697-700: 3 nuevas asignaciones |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | 3 nuevos placeholders de breakdown |

### Tests
- Validación vía v4complete con Hotel Castilla Real (hotelcastillareal.com)
- `run_all_validations.py --quick` pasa 4/4
- 0 regresiones, 2491 tests totales
```

**Criterios de aceptación**:
- [ ] Entrada `[4.40.1]` existe en CHANGELOG.md
- [ ] Tiene sección `### Objetivo`
- [ ] Tiene sección `### Cambios Implementados`
- [ ] Tiene sección `### Archivos Modificados`
- [ ] Tiene sección `### Tests`
- [ ] No hay entradas duplicadas
- [ ] Fecha correcta (2026-05-05)

### Tarea 3: Agregar nota técnica en GUIA_TECNICA.md

**Objetivo**: Agregar sección "Notas de Cambios v4.40.1" en GUIA_TECNICA.md

**Formato**:

```markdown
## Notas de Cambios v4.40.1 — Scoring Transparency

**Módulos afectados:**
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Problema:**
`_build_scoring_breakdown()` filtraba factores con valor `False`, ocultando información al cliente sobre qué indicadores faltaban. Además, solo GEO tenía breakdown en el diagnóstico; SEO, AEO e IAO tenían checklists, calculadores y extractores implementados pero sin representación en el output.

**Solución:**
- SCORING-A: Se modificó `_build_scoring_breakdown()` para iterar todo el checklist con marcadores visuales (✅ para TRUE, ~~tachado~~ para FALSE)
- SCORING-B: Se agregaron las invocaciones faltantes para SEO, AEO, IAO en el generator y sus placeholders en el template v6

**Backwards compatibility:**
✅ Total. El score calculado no cambia. Solo se modifica la presentación del breakdown. Los templates existentes que no usen los nuevos placeholders siguen funcionando igual.

**Tests:**
- Validación funcional vía v4complete con Hotel Castilla Real
- `run_all_validations.py --quick` pasa 4/4
```

**Criterios de aceptación**:
- [ ] GUIA_TECNICA.md tiene sección "Notas de Cambios v4.40.1"
- [ ] Incluye módulos afectados
- [ ] Incluye problema/solución
- [ ] Incluye backwards compatibility
- [ ] Incluye tests

### Tarea 4: Sincronización y validaciones finales

**Objetivo**: Ejecutar la cascada completa de sincronización y validación

**Comandos (en orden)**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Bump version a 4.40.1
venv/Scripts/python.exe scripts/sync_versions.py

# 2. Verificar consistencia
venv/Scripts/python.exe scripts/version_consistency_checker.py

# 3. Validación final
venv/Scripts/python.exe scripts/run_all_validations.py --quick

# 4. Diagnóstico del ecosistema
venv/Scripts/python.exe scripts/doctor.py --status
```

**Criterios de aceptación**:
- [ ] `sync_versions.py` ejecutado sin errores
- [ ] `version_consistency_checker.py` pasa sin discrepancias
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores críticos
- [ ] `git diff --stat` muestra todos los archivos modificados

---

## Tests Obligatorios

| Test | Criterio de Éxito |
|------|-------------------|
| `run_all_validations.py --quick` | 4/4 |
| `version_consistency_checker.py` | Sin discrepancias |
| `doctor.py --status` | Sin errores críticos |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase:

1. **`dependencias-fases.md`**
   - Marcar SCORING-C como ✅ Completada

2. **`README.md` del plan**
   - Actualizar tabla de progreso (las 3 fases completadas)

3. **`06-checklist-implementacion.md`**
   - Marcar items C1-C8

4. **`09-documentacion-post-proyecto.md`**
   - Marcar Sección E: Post-Fase SCORING-C (RELEASE)

5. **Git commit**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
git add -A
git commit -m "v4.40.1: Scoring Transparency — 4 pilares con breakdown completo en diagnóstico"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] REGISTRY.md tiene entradas para SCORING-A, SCORING-B, SCORING-C
- [ ] CHANGELOG.md tiene entrada `[4.40.1]` con formato correcto
- [ ] GUIA_TECNICA.md tiene nota técnica v4.40.1
- [ ] `sync_versions.py` ejecutado sin errores
- [ ] `version_consistency_checker.py` pasa
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` sin errores
- [ ] `dependencias-fases.md` actualizado (SCORING-C ✅)
- [ ] `git add -A && git commit` ejecutado

---

## Restricciones

- NO modificar código fuente
- NO modificar ROADMAP.md
- NO ejecutar `v4complete`
- NO crear tests nuevos
- Máximo 60 iteraciones del agente
- Esta fase es puramente documental
