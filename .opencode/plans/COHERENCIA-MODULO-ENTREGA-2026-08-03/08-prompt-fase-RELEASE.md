# FASE-RELEASE-4.70.0: Cierre y Documentación Oficial

**ID**: COHERENCIA-FASE-RELEASE-4.70.0
**Objetivo**: Version bump v4.69.0 → v4.70.0, documentación oficial (CHANGELOG, GUIA_TECNICA), validaciones finales y flujo documental obligatorio. NO modifica código fuente.
**Dependencias**: FASE-A ✅, FASE-B ✅, FASE-C-A ✅, FASE-C-B ✅, FASE-D ✅, FASE-E ✅ (TODAS).
**Duración estimada**: 1 sesión (~30 iteraciones de 60).
**Skill**: `phased_project_executor` v2.13.0 §Paso-7 (E1-E8b).

## Contexto

Todas las implementaciones del plan COHERENCIA-MODULO-ENTREGA están completas y verificadas en el E2E de FASE-E. Esta sesión ejecuta los pasos E1-E8b del executor y el Flujo Documental Obligatorio de AGENTS.md. Los datos acumulados están en `11-documentacion-post-proyecto.md` y el análisis post-implementación en `10-analisis-post-implementacion.md`.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A / B / C-A / C-B / D / E | ✅ Completadas |
| FASE-RELEASE-4.70.0 | ▶️ EN CURSO (esta sesión) |

## Modo de ejecución (delegate_task)

**DELEGABLE a subagente** (executor §Paso-7 TIP): solo edita YAML/MD y ejecuta scripts (`sync_versions.py`, `run_all_validations.py`, `doctor.py`), sin imports del proyecto. Confirmado en BUGS-ONBOARDING-ADR: ~18 tool calls / ~4 min. Si el agente principal tiene presupuesto completo puede ejecutarla directo.

> ⚠️ Única salvedad: la suite de tests por módulo (ver T7) usa el venv Windows;
> si se delega, ejecutarla desde el workspace Windows con `./venv/Scripts/python.exe`.

## Tareas (pasos E1-E8b del executor)

### T1 — Diagnóstico inicial (E1)
```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```
- [ ] Sin discrepancias de versión · sin errores críticos del doctor.

### T2 — Version bump + sync (E2)
- Actualizar `VERSION.yaml` a `4.70.0` (fuente única de versión).
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```
- [ ] VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md sincronizados.

### T3 — CHANGELOG.md (E3, manual)
Entrada formato CONTRIBUTING:
```markdown
## [4.70.0] - Coherencia Módulo-Entrega: 21 desconexiones corregidas — YYYY-MM-DD

### Objetivo
...

### Cambios Implementados
- FASE-A ... FASE-E (una línea por fase, desde 11-documentacion-post-proyecto.md)

### Archivos Nuevos
### Archivos Modificados
### Tests
```
- [ ] Entrada única [4.70.0], sin duplicados, describe archivos de las 6 fases.

### T4 — GUIA_TECNICA.md (E4, manual)
- [ ] Sección "Notas de Cambios v4.70.0" con: módulos afectados, problema/solución, backwards compatibility, tests.
- [ ] Nota explícita de cambio de comportamiento: pesos sobre N real (D2) y fórmula única de recuperación (N1) cambian cifras de todos los hoteles.

### T5 — Skills/workflows + SYSTEM_STATUS + DOMAIN_PRIMER (E5-E7)
```bash
ls -la .agents/workflows/*.md                      # todos en README.md
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
./venv/Scripts/python.exe scripts/doctor.py --context   # solo en RELEASE
```

### T6 — Symlink + validación final (E8)
```bash
ls -la .agent/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```
- [ ] Symlink intacto · validaciones 4/4.

### T7 — Suite de tests por módulo (riesgo timeout)
```bash
./venv/Scripts/python.exe -m pytest tests/ -q --co | tail -1    # conteo real
# Si la suite completa da timeout, ejecutar por módulo (lección 5 plan ZIP):
./venv/Scripts/python.exe -m pytest tests/commercial_documents tests/financial_engine tests/quality_gates tests/delivery -q
```
- [ ] Conteo real registrado en `11-documentacion-post-proyecto.md` sección D.

### T8 — README audit (E8b)
- [ ] Test count y module count del README coinciden con pytest --collect-only y find modules/ (corregir si hay discrepancia).

### T9 — Flujo Documental Obligatorio (AGENTS.md)
```bash
./venv/Scripts/python.exe scripts/validate_document_integration.py   # gate no-regresión documental
```
- [ ] Pasa sin gaps. Nota: las fases A-E ya se registraron a sí mismas con `log_phase_completion.py` (regla anti-deuda §2.5); si alguna quedó sin registro, registrarla AQUÍ antes del sync final.

## Post-Ejecución (OBLIGATORIO)

1. Marcar FASE-RELEASE ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md`, `README.md`.
2. Completar `10-analisis-post-implementacion.md` con el resumen de ejecución final (tabla de fases con sesiones/iteraciones/modo delegate_task) y `11-documentacion-post-proyecto.md` sección D final.
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE-4.70.0 \
    --desc "Release 4.70.0 — Coherencia Módulo-Entrega" \
    --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md" --check-manual-docs
```
4. `git add -A && git commit` (los pre-commit hooks agent-ecosystem + version-sync deben pasar).

## Criterios de Completitud (CHECKLIST)

- [ ] E1-E8b completos según checklists de T1-T8
- [ ] CHANGELOG [4.70.0] con formato CONTRIBUTING completo
- [ ] Version Sync Gate pasó (sin `(!)`)
- [ ] `validate_document_integration.py` OK
- [ ] `run_all_validations.py --quick` 4/4
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.70.0` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2).
- **NO modifica código fuente** (solo YAML/MD/docs y scripts de sincronización).
- **NO ejecuta v4complete** (ya ejecutado en FASE-E; única ejecución del plan).
- NO modifica ROADMAP.md.
- NO registra fases anteriores salvo que alguna haya quedado sin registro (excepción documentada).
