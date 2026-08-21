# FASE-RELEASE-4.72.0: Cierre y Documentación Oficial — "Credibilidad Numérica y Verdad del Sitio Vivo"

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-RELEASE-4.72.0
**Objetivo**: Version bump a 4.72.0, sincronización de versión en los 6 archivos, CHANGELOG y
GUIA_TECNICA oficiales (desde los datos acumulados en `09-documentacion-post-proyecto.md`),
validaciones finales y regeneración de SYSTEM_STATUS/DOMAIN_PRIMER. **NO modifica código fuente.**
**Dependencias**: FASE-E2E-ZIONE ✅ (regla de dependencia del executor — TODAS las implementaciones completas)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` §Paso-7 (pasos E1-E8) — **fase DELEGABLE vía `delegate_task`**

## Modo de Ejecución — delegate_task (OPCIONAL)

Según el TIP del executor, FASE-RELEASE es delegable: solo edita YAML/MD y ejecuta scripts
stdlib (`sync_versions.py`, `run_all_validations.py`, `doctor.py`), sin imports del proyecto.
Confirmado históricamente: ~18 tool calls / ~4 min.

```
SI el agente principal tiene presupuesto limitado:
  → delegate_task(
      goal="Ejecutar FASE-RELEASE-4.72.0 del plan CREDIBILIDAD-NUMERICA-2026-08-20",
      context="""
        Seguir .agents/workflows/phased_project_executor.md §Paso-7 (E1-E8).
        Version objetivo: 4.72.0. Datos acumulados en
        .opencode/plans/CREDIBILIDAD-NUMERICA-2026-08-20/09-documentacion-post-proyecto.md.
        NO modificar codigo fuente. NO ejecutar v4complete. NO registrar fases anteriores
        (cada fase ya ejecuto log_phase_completion.py al cerrar).
      """,
      timeout=600,
      toolsets=["file", "terminal"]
    )
  → Agente principal verifica VERSION.yaml == 4.72.0 + run_all_validations --quick
SI presupuesto suficiente → ejecución DIRECTA.
```

**Regla anti-deuda (§2.5)**: FASE-RELEASE NO registra las fases P0/P1/P2/E2E — cada una ya
ejecutó `log_phase_completion.py` al terminar. RELEASE solo sincroniza y valida.

## Contexto

Cierre oficial del plan CREDIBILIDAD-NUMERICA-2026-08-20 (v4.71.0 → v4.72.0). Los datos de todas
las fases (módulos nuevos, funcionalidades, métricas, archivos) están acumulados en
`09-documentacion-post-proyecto.md`. El análisis post-implementación (matriz V1-V13, lecciones,
métricas E2E) está en `10-analisis-post-implementacion.md`.

### Estado de Fases Anteriores (gate de entrada — verificar ANTES de iniciar)
| Fase | Estado requerido |
|------|------------------|
| FASE-P0-A/B/C, FASE-P1-A/B/C/D, FASE-P2-A/B | ✅ |
| FASE-E2E-ZIONE | ✅ (con matriz V1-V13 y veredicto registrados) |

**Si alguna NO está ✅ → ABORTAR** (Plan de Recuperación del executor: RELEASE sin implementaciones
completadas → abortar).

## Tareas (E1-E8 del executor §Paso-7)

### E1: Diagnóstico inicial
```powershell
.\venv\Scripts\python.exe scripts/version_consistency_checker.py
.\venv\Scripts\python.exe main.py --doctor
```
- [ ] version_consistency_checker pasa sin discrepancias
- [ ] doctor sin errores críticos

### E2: Version bump + sincronización
- Actualizar `VERSION.yaml` a `version: "4.72.0"`, codename "Credibilidad Numérica y Verdad del Sitio Vivo", release_date actual.
```powershell
.\venv\Scripts\python.exe scripts/sync_versions.py
```
- [ ] sync_versions ejecutado sin errores (sincroniza AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md)

### E3: CHANGELOG.md (formato CONTRIBUTING)
Entrada `## [4.72.0] - Credibilidad Numérica y Verdad del Sitio Vivo — YYYY-MM-DD` con secciones:
`### Objetivo`, `### Cambios Implementados`, `### Archivos Nuevos`, `### Archivos Modificados`, `### Tests`.
Describir TODAS las fases (P0-A/B/C, P1-A/B/C/D, P2-A/B, E2E) usando los datos de `09-documentacion-post-proyecto.md`.
- [ ] Entrada 4.72.0 existe, sin duplicados, describe archivos nuevos y modificados de cada fase

### E4: GUIA_TECNICA.md
Agregar sección "Notas de Cambios v4.72.0" con: módulos afectados, problema/solución, backwards compatibility.
- [ ] Nota técnica presente con los campos requeridos

### E5: Skills/Workflows
- [ ] Todos los `.md` en `.agents/workflows/` listados en su README (sin skills huérfanos)

### E6: SYSTEM_STATUS.md
```powershell
.\venv\Scripts\python.exe scripts/doctor.py --status
```
- [ ] SYSTEM_STATUS.md regenerado con versión 4.72.0

### E7: DOMAIN_PRIMER.md
```powershell
.\venv\Scripts\python.exe scripts/doctor.py --regenerate-domain-primer
.\venv\Scripts\python.exe scripts/doctor.py --context   # solo en RELEASE
```
- [ ] DOMAIN_PRIMER regenerado; todo módulo en `modules/` documentado

### E8: Symlink + validación final
```powershell
ls -la .agent/workflows    # debe apuntar a .agents/workflows
.\venv\Scripts\python.exe scripts\run_all_validations.py --quick
.\venv\Scripts\python.exe scripts\validate_agents_md.py
git diff --stat
```
- [ ] Symlink intacto; `run_all_validations.py --quick` TOTAL PASS
- [ ] `validate_agents_md.py` pasa (gate count de AGENTS.md == `self.gates` del código; P0-B ya
      lo actualizó a 13 — decisión D5; `--quick` NO ejecuta este check, por eso se llama explícito)

### E8b: README.md + AGENTS.md line-by-line audit
Verificar test count y module count en README.md (y el conteo de tests de AGENTS.md, tabla
"Estado Actual": "3,233 funciones, 261 archivos") contra realidad:
```powershell
.\venv\Scripts\python.exe -m pytest --collect-only -q
```
- [ ] Test count en README coincide con `pytest --collect-only`
- [ ] Conteo de tests en AGENTS.md actualizado si las fases del plan agregaron tests
- [ ] Si hay discrepancia → corregir y commit separado post-release

## Registro de RELEASE (último paso)
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-RELEASE-4.72.0 --desc "Release 4.72.0 - Credibilidad Numerica y Verdad del Sitio Vivo" --check-manual-docs
.\venv\Scripts\python.exe scripts/version_consistency_checker.py
```
- [ ] Version Sync Gate pasó (no hubo `(!)`)

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-RELEASE-4.72.0 ✅.
2. `README.md` del plan: marcar plan COMPLETADO.
3. `10-analisis-post-implementacion.md`: llenar **Checklist de Cierre** y Métricas de Ejecución finales.
4. `git add -A && git commit` (con mensaje de release).

## Criterios de Completitud (CHECKLIST)

- [ ] VERSION.yaml == 4.72.0 y sync_versions aplicado a los 6 archivos
- [ ] CHANGELOG 4.72.0 con formato CONTRIBUTING completo
- [ ] GUIA_TECNICA con nota v4.72.0
- [ ] SYSTEM_STATUS y DOMAIN_PRIMER regenerados
- [ ] run_all_validations.py --quick TOTAL PASS
- [ ] version_consistency_checker pasa; Version Sync Gate OK
- [ ] Checklist de Cierre en 10-analisis marcado

## Restricciones

- Máximo 60 iteraciones.
- **NO modifica código fuente** (solo YAML/MD + scripts de sincronización).
- NO edita ROADMAP.md.
- NO ejecuta v4complete.
- NO registra fases anteriores (ya lo hicieron al cerrar).
