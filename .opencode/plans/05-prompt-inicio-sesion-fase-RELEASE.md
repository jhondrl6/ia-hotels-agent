# FASE-RELEASE-4.47.0: Cierre Documental — ADVISORY-WARNINGS

**ID**: FASE-RELEASE-4.47.0
**Objetivo**: Version bump a 4.47.0, sincronizar documentación, CHANGELOG, GUIA_TECNICA, validaciones finales
**Dependencias**: FASE-A ✅, FASE-B ✅ (todas las fases de implementación completadas)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Todas las fases de implementación están completadas:
- FASE-A: Advisory warnings implementados (diagnóstico + delivery_quality_report) + 6 tests
- FASE-B: v4complete Hotel Castilla Real ejecutado y verificado

Esta fase cierra el proyecto con documentación oficial, version bump y validaciones. **NO modifica código fuente.**

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |

---

## Tareas

### E1: Diagnóstico Inicial
```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores críticos

### E2: Sincronización Automática
```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

- [ ] sync_versions.py ejecutado sin errores
- [ ] VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md

### E3: CHANGELOG.md
Crear entrada para v4.47.0:

```markdown
## [4.47.0] - ADVISORY-WARNINGS — YYYY-MM-DD

### Objetivo
Implementar advisory warnings visibles y persistentes para IA-Readiness Critical sin bloquear entregas.

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` - Alerta blockquote cuando IA-Readiness < 50
- `modules/quality_gates/delivery_quality_report.py` - Nuevo campo advisory_warnings con IA_READINESS_CRITICAL
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Variable para alerta advisory

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Agregada alerta advisory en tabla de métricas IA |
| `modules/quality_gates/delivery_quality_report.py` | Campo advisory_warnings: List[dict] + serialización |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Soporte para variable ia_critical_warning |

### Tests
- 6 tests nuevos en test_v4_diagnostic_generator.py y test_delivery_quality_report.py
- 0 regresiones
- Verificado con v4complete para Hotel Castilla Real
```

- [ ] CHANGELOG.md tiene entrada `[4.47.0]`
- [ ] Formato cumple con CONTRIBUTING.md (Objetivo, Cambios, Archivos, Tests)

### E4: GUIA_TECNICA.md
Agregar sección:

```markdown
### Notas de Cambios v4.47.0 — ADVISORY-WARNINGS

**Módulos afectados**: `v4_diagnostic_generator.py`, `delivery_quality_report.py`

**Problema**: IA-Readiness Critical (score < 50) aparecía como una fila más en la tabla de diagnóstico sin explicitar el riesgo comercial al hotelero. No quedaba registro persistente en los reportes de calidad.

**Solución**: 
- Alerta blockquote en diagnóstico cuando IA-Readiness es Critical
- Nuevo campo `advisory_warnings` en DeliveryQualityReport con entry `IA_READINESS_CRITICAL`
- `blocking=False` — no aborta ZIP ni afecta overall_confidence

**Backwards compatibility**: Total. Campo nuevo (`advisory_warnings`) con default `[]`. Template soporta nueva variable pero mantiene comportamiento existente.
```

- [ ] GUIA_TECNICA.md tiene nota técnica para v4.47.0
- [ ] Incluye módulos afectados, problema/solución, backwards compatibility

### E5: Skills/Workflows
```bash
ls -la .agents/workflows/*.md
```

- [ ] Workflows listados y actualizados

### E6: Regenerar SYSTEM_STATUS.md
```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [ ] SYSTEM_STATUS.md regenerado

### E7: Regenerar DOMAIN_PRIMER.md
```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] DOMAIN_PRIMER.md regenerado
- [ ] Context check pasa

### E8: Validación Final
```bash
ls -la .agent/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

- [ ] Symlink .agent/workflows → .agents/workflows intacto
- [ ] run_all_validations.py --quick pasa 4/4
- [ ] git diff --stat muestra todos los archivos modificados

---

## Post-Ejecución (OBLIGATORIO)

```bash
# Registrar release en REGISTRY.md
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.47.0 \
    --desc "Release 4.47.0 — ADVISORY-WARNINGS: alerta advisory IA-Readiness + delivery_quality_report warnings" \
    --archivos-mod "CHANGELOG.md,GUIA_TECNICA.md,VERSION.yaml" \
    --check-manual-docs

# Verificar consistencia
./venv/Scripts/python.exe scripts/version_consistency_checker.py

# Commit final
git add -A && git commit -m "v4.47.0: ADVISORY-WARNINGS — IA-Readiness advisory alerts + delivery_quality_report warnings"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] E1: Diagnóstico inicial pasa
- [ ] E2: sync_versions.py ejecutado
- [ ] E3: CHANGELOG.md entrada [4.47.0] creada
- [ ] E4: GUIA_TECNICA.md nota técnica agregada
- [ ] E5: Skills/workflows verificados
- [ ] E6: SYSTEM_STATUS.md regenerado
- [ ] E7: DOMAIN_PRIMER.md regenerado + context check
- [ ] E8: Validación final 4/4 pasa
- [ ] REGISTRY.md actualizado
- [ ] version_consistency_checker.py pasa
- [ ] Commit realizado

---

## Restricciones

- **NO modificar código fuente** (solo documentación y validaciones)
- **NO modificar ROADMAP.md**
- **NO ejecutar v4complete**
- **NO registrar fases anteriores** (FASE-A y FASE-B ya se registraron a sí mismas)
- **Máximo 60 iteraciones del agente**
