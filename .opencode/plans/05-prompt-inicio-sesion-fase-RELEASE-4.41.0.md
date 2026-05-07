# FASE-RELEASE-4.41.0: Documentación y Version Bump

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~40 iteraciones
**Dependencias:** TODAS las fases A-G ✅
**Fase siguiente:** Ninguna (fin del plan)

## Contexto

Todas las fases de implementación (A-G) están completadas. Esta fase ejecuta el flujo documental obligatorio:
1. Registrar cada fase en REGISTRY.md
2. Sincronizar versiones
3. Validar CHANGELOG.md y GUIA_TECNICA.md
4. Validaciones finales

**NO se modifica código fuente** en esta fase.

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |
| FASE-PROP-B | ✅ Completada |
| FASE-PROP-C | ✅ Completada |
| FASE-PROP-D | ✅ Completada |
| FASE-PROP-E | ✅ Completada |
| FASE-PROP-F | ✅ Completada |
| FASE-PROP-G | ✅ Completada |

## Tareas Específicas

### Tarea 1: Registrar fases A-G en REGISTRY.md
**Objetivo**: Cada fase tiene entrada en REGISTRY.md vía `log_phase_completion.py`.

**Criterios de aceptación**:
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-A (si no se ejecutó en su fase)
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-B
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-C
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-D
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-E
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-F
- [ ] Ejecutar log_phase_completion.py para FASE-PROP-G

Comandos (ejecutar uno por uno, verificando salida):
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-A --desc "Unificacion de Coherence Score" --check-manual-docs
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-B --desc "WhatsApp conflict status" --check-manual-docs
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-C --desc "Proyecciones financieras transparentes" --check-manual-docs
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-D --desc "Google Maps asset o redefinicion" --check-manual-docs
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-E --desc "SEO/AEO plan especifico" --check-manual-docs
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-F --desc "Tier C advertencia" --check-manual-docs
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-PROP-G --desc "Sobrescritura de evidencia" --check-manual-docs
```

### Tarea 2: Sincronizar versiones
**Objetivo**: VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md.

**Criterios de aceptación**:
- [ ] `VERSION.yaml` muestra `4.41.0`
- [ ] `sync_versions.py` ejecutado sin errores
- [ ] `version_consistency_checker.py` pasa (All in sync)

Comandos:
```bash
venv/Scripts/python.exe scripts/sync_versions.py
venv/Scripts/python.exe scripts/version_consistency_checker.py
```

### Tarea 3: Validar CHANGELOG.md
**Objetivo**: Entrada [4.41.0] con formato CONTRIBUTING.md.

**Criterios de aceptación**:
- [ ] Entrada `[4.41.0] - YYYY-MM-DD` existe
- [ ] Sección `### Objetivo`
- [ ] Sección `### Cambios Implementados`
- [ ] Sección `### Archivos Nuevos` (si aplica)
- [ ] Sección `### Archivos Modificados`
- [ ] Sección `### Tests`
- [ ] No hay entradas duplicadas

### Tarea 4: Validar GUIA_TECNICA.md
**Objetivo**: Nota técnica por cada fase A-G.

**Criterios de aceptación**:
- [ ] Cada fase tiene sección "Notas de Cambios v4.41.0"
- [ ] Incluye módulos afectados
- [ ] Incluye problema/solución
- [ ] Incluye backwards compatibility

### Tarea 5: Validación final
**Objetivo**: Todo el sistema pasa validaciones.

**Criterios de aceptación**:
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` ejecuta sin errores

Comandos:
```bash
venv/Scripts/python.exe scripts/run_all_validations.py --quick
venv/Scripts/python.exe scripts/doctor.py --status
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Notas |
|---------|---------------|-------|
| `docs/contributing/REGISTRY.md` | Modificación (auto) | vía log_phase_completion.py |
| `CHANGELOG.md` | Modificación | Entrada [4.41.0] |
| `docs/GUIA_TECNICA.md` | Modificación | Notas técnicas |
| `VERSION.yaml` | Modificación (auto) | vía sync_versions.py |
| `AGENTS.md`, `README.md`, `.cursorrules`, `CONTRIBUTING.md` | Sincronización (auto) | vía sync_versions.py |

## Criterios de Completitud (CHECKLIST)

- [ ] **7 fases registradas**: REGISTRY.md tiene entradas para A-G
- [ ] **Version sincronizada**: 4.41.0 en todos los archivos oficiales
- [ ] **CHANGELOG validado**: Formato CONTRIBUTING.md, sin duplicados
- [ ] **GUIA_TECNICA validada**: Nota por fase
- [ ] **Validaciones pasan**: `run_all_validations.py --quick` 4/4
- [ ] **Doctor limpio**: `doctor.py --status` sin errores

## Restricciones

- **NO modificar** código fuente — solo documentación
- **NO ejecutar** v4complete en esta fase
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**: marcar RELEASE como ✅
2. **Actualizar `06-checklist-implementacion.md`**: marcar todas las fases como completadas
3. **Actualizar `09-documentacion-post-proyecto.md`**: completar Sección E con todos los archivos afiliados
4. **Actualizar `README.md`**: marcar PROPOSAL-COMERCIAL-FIX como ✅ Completado

**Plan finalizado.**
