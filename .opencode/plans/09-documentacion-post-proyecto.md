# Plan de Documentación Post-Proyecto

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada"  
**Fecha**: 2026-04-24  
**Versión target**: 4.35.1 (patch increment sobre 4.35.0)

---

## Estructura de Documentación

### Sección A: Módulos Afectados

| Módulo | Cambio | Fase |
|--------|--------|------|
| `README.md` | Corrección "6" → "9 gates" | FASE-TRAZABILIDAD-DOCS |
| `.agents/workflows/v4_complete.md` | Remover referencia a comando inexistente | FASE-TRAZABILIDAD-DOCS |
| `modules/quality_gates/publication_gates.py` | Docstring corregido | FASE-TRAZABILIDAD-DOCS |
| `AGENTS.md` | Sincronización coherence score | FASE-TRAZABILIDAD-DOCS |
| `main.py` | Cableado PublicationGatesOrchestrator | FASE-TRAZABILIDAD-GATES |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Template + gate_results param | FASE-TRAZABILIDAD-GATES |
| `tests/quality_gates/test_publication_gates.py` | NUEVO: 8-10 tests | FASE-TRAZABILIDAD-GATES |

### Sección B: Métricas Acumulativas

| Métrica | Antes | Después |
|---------|-------|---------|
| Publication Gates ejecutados | 1/9 (solo coherence) | 9/9 |
| Código muerto | 1062 líneas (publication_gates.py) | 0 líneas (cableado) |
| Tests | 0 para publication gates | 8-10 tests |
| Trazabilidad en output | 0% | 100% (gate_report.json + sección en doc) |
| Coherence Score | 0.84 (AGENTS.md) / 0.89 (último doc) | Sincronizado |

### Sección C: Archivos de Plan

| Archivo | Descripción |
|---------|-------------|
| `.opencode/plans/dependencias-fases.md` | Diagrama de dependencias + conflictos |
| `.opencode/plans/05-prompt-inicio-sesion-fase-trazabilidad-docs.md` | Prompt FASE 1 |
| `.opencode/plans/05-prompt-inicio-sesion-fase-trazabilidad-gates.md` | Prompt FASE 2 |
| `.opencode/plans/05-prompt-inicio-sesion-fase-trazabilidad-validate.md` | Prompt FASE 3 |
| `.opencode/plans/06-checklist-implementacion.md` | Checklist maestro |
| `.opencode/plans/09-documentacion-post-proyecto.md` | Este archivo |
| `.opencode/plans/README.md` | Índice del directorio |

### Sección D: Flujo Documental (Post-Completitud Total)

Una vez completadas las 3 fases, ejecutar en orden:

```bash
# 1. Registrar cada fase en REGISTRY.md
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-DOCS --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-GATES --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-TRAZABILIDAD-VALIDATE --desc "..." --check-manual-docs

# 2. Sincronizar versiones
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. Validar CHANGELOG
# Verificar formato: Objetivo / Cambios / Archivos / Tests

# 4. Validar GUIA_TECNICA.md
# Agregar nota técnica: "Notas de Cambios v4.35.1 - Trazabilidad Publication Gates"

# 5. Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

### Sección E: Checklist de Documentación Final

|| Verificación | Estado |
|-------------|--------|
| REGISTRY.md actualizado (3 fases) | ✅ |
| sync_versions.py ejecutado | ✅ |
| CHANGELOG.md formato correcto | ✅ |
| GUIA_TECNICA.md con nota técnica | ✅ |
| run_all_validations.py --quick (4/4) | ✅ |
| doctor.py --status sin errores | ✅ |
| DOMAIN_PRIMER.md actualizado | ✅ (sin cambios necesarios) |
| AGENTS.md actualizado | ✅ |
