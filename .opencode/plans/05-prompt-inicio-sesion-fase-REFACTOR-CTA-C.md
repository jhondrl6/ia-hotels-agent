# Prompt de Inicio de Sesion — FASE-REFACTOR-CTA-C (Documentacion Post-Fase)

## Contexto

Las fases A (fix codigo+tests) y B (v4complete+verificacion) estan completadas. Esta fase C ejecuta el **flujo documental obligatorio** segun `phased_project_executor.md` §4.5 y `AGENTS.md`.

**Cambio resumen:** Refactorizacion del CTA de onboarding en diagnostico Tier C para listar explicitamente los 4 datos requeridos (habitaciones, reservas mensuales, valor promedio de reserva COP, porcentaje canal directo).

## Tareas Especificas

### Tarea 1: Registrar fase en REGISTRY.md

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-REFACTOR-CTA-ONBOARDING \
    --desc "Refactoriza CTA de onboarding en Tier C para listar explicitamente los 4 datos requeridos. Verificado con v4complete en Hotel Castilla Real." \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,tests/commercial_documents/test_precision_rendering.py" \
    --tests "1" \
    --check-manual-docs
```

Verificar que no haya `[GAP]` en el DOCUMENTATION AUDIT del output.

### Tarea 2: Sincronizar versiones

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### Tarea 3: Actualizar CHANGELOG.md y GUIA_TECNICA.md

**CHANGELOG.md:**
- Agregar entrada PATCH (ej: `[4.40.2] - Fecha`) si aun no existe
- Secciones requeridas: `### Objetivo`, `### Cambios Implementados`, `### Archivos Modificados`, `### Tests`

**GUIA_TECNICA.md:**
- Agregar seccion "Notas de Cambios v4.40.2" (o version correspondiente)
- Campos: Modulos afectados, Problema, Solucion, Backwards compatibility

```markdown
### Notas de Cambios v4.40.2

**Modulos afectados:** `modules/commercial_documents/v4_diagnostic_generator.py`, `tests/commercial_documents/test_precision_rendering.py`

**Problema:** El CTA de onboarding en diagnostico Tier C decia "complete el onboarding con sus datos reales" sin especificar cuales datos.

**Solucion:** Se refactorizo el string `show_onboarding_cta` para listar explicitamente los 4 datos: numero de habitaciones, reservas mensuales promedio, valor promedio de reserva (COP) y porcentaje de canal directo.

**Backwards compatibility:** Si. Solo cambio de string, sin modificacion de APIs ni estructuras de datos.
```

### Tarea 4: Validacion final

```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

Verificar:
- `run_all_validations.py --quick` pasa 4/4
- `doctor.py --status` sin errores criticos
- `version_consistency_checker.py` sin discrepancias

## Criterios de Completitud

- [ ] Fase registrada en REGISTRY.md (sin GAPs)
- [ ] VERSION.yaml sincronizado con AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md
- [ ] CHANGELOG.md tiene entrada PATCH con formato correcto
- [ ] GUIA_TECNICA.md tiene nota tecnica con modulos, problema, solucion, backwards compatibility
- [ ] `run_all_validations.py --quick` pasa
- [ ] `doctor.py --status` ejecutado

## Restricciones

- **Maximo 60 iteraciones** por sesion (R2)
- **No modificar codigo fuente** — solo documentacion
- **No ejecutar v4complete**

## Post-Ejecucion

1. Marcar FASE-REFACTOR-CTA-C como ✅ en `.opencode/plans/06-checklist-implementacion.md`
2. Este proyecto **NO requiere FASE-RELEASE separada** (PATCH-level, ya integrado en docs cascade)
3. Todo el proyecto REFACTOR-ONBOARDING-CTA estara completado
