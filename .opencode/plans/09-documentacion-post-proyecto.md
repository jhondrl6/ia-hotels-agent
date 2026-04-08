# Documentacion Post-Proyecto: Bugfix Sprint post-FASE-B

> **Fuente normativa**: `docs/CONTRIBUTING.md` - Flujo Post-Fase Obligatorio (Paso 6)
> **Checklist**: `docs/contributing/documentation_rules.md` §5 + §36-58
> **Version Base**: 4.25.3
> **Fecha**: 2026-04-08
> **Estado**: PENDIENTE DE EJECUCION (se ejecuta DESPUES de cada fase)

---

## Como Usar Este Documento

Este documento es el **procedimiento paso a paso** de documentacion post-fase para el bugfix sprint. Se ejecuta **al completar cada fase** (C, D, E, F). No es un resumen -- es un checklist ejecutable.

**Regla**: "Actualiza los registros" = ejecutar TODOS los pasos de esta seccion para la fase completada.

---

## Paso 1: Registrar Fase Completada (AUTO)

```bash
python scripts/log_phase_completion.py --fase FASE-X
```

**Que hace**:
- Registra entrada en `docs/contributing/REGISTRY.md` (automatico)
- Muestra POR_HACER para docs manuales (si los hay)

**Verificacion**:
- [ ] `REGISTRY.md` tiene entrada para FASE-X con fecha, descripcion, archivos, validaciones

---

## Paso 2: Sincronizacion Automatica de Versiones (AUTO)

```bash
# Verificar si hay desincronizacion
python scripts/sync_versions.py --check

# Si hay desincronizacion, auto-reparar
python scripts/sync_versions.py --fix
```

**Que sincroniza** (desde VERSION.yaml):
- `AGENTS.md` -- version + fecha (HTML comment + header banner)
- `README.md` -- version + fecha
- `.cursorrules` -- version + fecha
- `docs/CONTRIBUTING.md` -- version header + footer
- `docs/GUIA_TECNICA.md` -- version + fecha
- `docs/contributing/REGISTRY.md` -- fecha ultima actualizacion

**Verificacion**:
- [ ] `sync_versions.py --check` reporta "All files in sync"
- [ ] No hay discrepancias de version entre archivos

---

## Paso 3: Verificar/Actualizar CHANGELOG.md (MANUAL)

> **Formato obligatorio**: `docs/contributing/documentation_rules.md` §36-58

### Plantilla de Entrada

```markdown
## v4.25.x - Bugfix Sprint: FASE-{X} (2026-04-08)

### Objetivo
{Descripcion breve del cambio realizado en esta fase}

### Cambios Implementados
- `ruta/archivo.py` - Descripcion del cambio realizado

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| (ninguno si no aplica) | |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `ruta/existente.py` | Descripcion del cambio |

### Tests
- Baseline: 1782 funciones, 140 archivos, 52 regresion
- Post-fase: {N} funciones (sin regresion)
```

### Checklist CHANGELOG

- [ ] CHANGELOG.md tiene entrada para la version actual de VERSION.yaml
- [ ] La entrada describe archivos nuevos/modificados de esta fase
- [ ] Formato sigue plantilla de documentation_rules.md §36-58
- [ ] No hay entradas duplicadas
- [ ] Seccion "Tests" documenta baseline y post-fase

---

## Paso 4: Verificar/Actualizar GUIA_TECNICA.md (MANUAL)

> Solo si la fase afecta arquitectura, stack o flujos

### Plantilla de Seccion

```markdown
### Notas de Cambios v4.25.x - Bugfix Sprint FASE-{X}

**Resumen**: {Descripcion tecnica concisa}

**Modulos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` - {cambios}
- `modules/auditors/v4_comprehensive.py` - {cambios}

**Arquitectura**: {Cambios arquitectonicos si los hay, o "Sin cambios arquitectonicos"}

**Backwards compatibility**: {Impacto en backwards compat, o "Totalmente backwards compatible"}

**Archivos modificados con descripcion**:
| Archivo | Cambio |
|---------|--------|
| `ruta/archivo.py` | Descripcion |
```

### Checklist GUIA_TECNICA

- [ ] GUIA_TECNICA.md tiene nota tecnica para la fase (si aplica arquitectura/stack/flujos)
- [ ] La nota incluye modulos afectados
- [ ] La nota incluye archivos modificados con descripcion
- [ ] Backwards compatibility documentado

---

## Paso 5: Verificar Capability Contracts (MANUAL)

> Solo si la fase agrega/modifica capacidades del sistema

```bash
python scripts/validate_agent_ecosystem.py
```

### Checklist Capabilities

- [ ] 0 capacidades sin invocacion en runtime (no huerfanas)
- [ ] 0 capacidades sin output observable
- [ ] Toda capacidad nueva tiene punto de invocacion identificado
- [ ] Toda capacidad nueva tiene output serializable (to_dict/export/report)

---

## Paso 6: Regenerar SYSTEM_STATUS.md (AUTO)

```bash
python main.py --doctor --status
```

**Verificacion**:
- [ ] `.agent/SYSTEM_STATUS.md` regenerado sin errores
- [ ] Doctor no reporta warnings nuevos

---

## Paso 7: Verificar Symlink .agent/ vs .agents/ (AUTO)

```bash
python main.py --doctor
```

**Verificacion**:
- [ ] `.agent/workflows/` es symlink que apunta a `.agents/workflows/`
- [ ] Doctor no reporta error de "Symlink integrity"

**Si esta roto**:
```bash
ln -sf ../.agents/workflows .agent/workflows
```

---

## Paso 8: Validacion Final Pre-Commit

```bash
# Validacion rapida
python scripts/run_all_validations.py --quick

# Verificar que no hay cambios no intencionados
git diff --stat
```

**Verificacion**:
- [ ] `run_all_validations.py --quick` pasa sin errores
- [ ] `git diff --stat` solo muestra archivos intencionados
- [ ] Tests pasan: `python -m pytest tests/ -x --tb=short -q`

---

## Resumen por Fase

### FASE-C: 4 Bugs Criticos

| Paso | Comando/Archivo | Estado |
|------|-----------------|--------|
| 1 | `log_phase_completion.py --fase FASE-C` | ✅ Completado |
| 2 | `sync_versions.py --check` | ✅ All files in sync |
| 3 | CHANGELOG.md entrada v4.25.3 FASE-C | ✅ Completado |
| 4 | GUIA_TECNICA.md (no aplica - solo bug fixes) | ✅ Verificado - sin cambios |
| 5 | Capability contracts (no aplica - sin nuevas capacidades) | ✅ Verificado |
| 6 | `scripts/doctor.py --status` | ✅ SYSTEM_STATUS.md regenerado |
| 7 | Symlink check | ✅ .agent/workflows -> ../.agents/workflows |
| 8 | `run_all_validations.py --quick` | ✅ 4/4 PASS |

**Archivos de FASE-C**:
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | 4 fixes: import logging, overall_score attr, open_graph attr, mobile_score is_not_None |

---

### FASE-D: 5 Bugs Medios + Serializacion

| Paso | Comando/Archivo | Estado |
|------|-----------------|--------|
| 1 | `log_phase_completion.py --fase FASE-D` | ✅ Completado |
| 2 | `sync_versions.py --check` | ✅ All files in sync |
| 3 | CHANGELOG.md entrada v4.25.3 FASE-D | ✅ Completado |
| 4 | GUIA_TECNICA.md (serializacion seo_elements) | ✅ Completado |
| 5 | Capability contracts (seo_elements_detection verificado) | ✅ Verificado |
| 6 | `scripts/doctor.py --status` | ✅ SYSTEM_STATUS.md regenerado |
| 7 | Symlink check | ✅ .agent/workflows -> ../.agents/workflows |
| 8 | `run_all_validations.py --quick` | ✅ 4/4 PASS |

**Archivos de FASE-D**:
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | 5 fixes: dead code elimination, dup keys, confidence case, pipe dup, /100 suffix |
| `modules/auditors/v4_comprehensive.py` | Serializacion seo_elements en to_dict() + executed_validators |

---

### FASE-E: OG Detection HTML Reuse

| Paso | Comando/Archivo | Estado |
|------|-----------------|--------|
| 1 | `log_phase_completion.py --fase FASE-E` | Pendiente |
| 2 | `sync_versions.py --check` | Pendiente |
| 3 | CHANGELOG.md entrada v4.25.x FASE-E | Pendiente |
| 4 | GUIA_TECNICA.md (elimina request HTTP, afecta flujo de auditoria) | Pendiente |
| 5 | Capability contracts (no cambia) | Pendiente |
| 6 | `main.py --doctor --status` | Pendiente |
| 7 | Symlink check | Pendiente |
| 8 | `run_all_validations.py --quick` | Pendiente |

**Archivos de FASE-E**:
| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | Eliminar 2da HTTP request, reutilizar HTML del schema audit, logging defensivo OG |

---

### FASE-F: Zombies + Code Smells

| Paso | Comando/Archivo | Estado |
|------|-----------------|--------|
| 1 | `log_phase_completion.py --fase FASE-F` | Pendiente |
| 2 | `sync_versions.py --check` | Pendiente |
| 3 | CHANGELOG.md entrada v4.25.x FASE-F | Pendiente |
| 4 | GUIA_TECNICA.md (limpieza, no afecta arquitectura -- puede omitirse) | Opcional |
| 5 | Capability contracts (no cambia) | Pendiente |
| 6 | `main.py --doctor --status` | Pendiente |
| 7 | Symlink check | Pendiente |
| 8 | `run_all_validations.py --quick` | Pendiente |

**Archivos de FASE-F**:
| Archivo | Cambio |
|---------|--------|
| `templates/diagnostico_ejecutivo.md` | Eliminar fila IAO (ZMB-1) |
| `templates/diagnostico_v4_template.md` | Eliminar filas IAO+Voice (ZMB-2) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | ZMB-3 + MEN-1..7 (~20 lineas) |
| `modules/utils/benchmarks.py` | ZMB-4: eliminar iao_score key |

---

## Commit Messages Recomendados (por Fase)

| Fase | Mensaje |
|------|---------|
| FASE-C | `fix(FASE-C): 4 critical bugs in v4_diagnostic_generator - logging import, citability attr, OG attr, mobile_score short-circuit` |
| FASE-D | `fix(FASE-D): 5 medium bugs + seo_elements serialization in v4_comprehensive` |
| FASE-E | `fix(FASE-E): reuse schema audit HTML for OG detection, eliminate redundant HTTP request` |
| FASE-F | `fix(FASE-F): remove zombie IAO/voice refs + fix 7 code smells in v4_diagnostic_generator` |

---

## Validacion Final Post-Sprint (despues de FASE-F)

```bash
# 1. Diagnostico completo del ecosistema
python scripts/version_consistency_checker.py
python main.py --doctor

# 2. Sincronizacion final
python scripts/sync_versions.py

# 3. CHANGELOG verificado para todas las fases
# (entradas C, D, E, F presentes)

# 4. GUIA_TECNICA actualizada
# (notas tecnicas para D y E)

# 5. Skills/workflows verificados
# (sin cambios en este sprint)

# 6. SYSTEM_STATUS regenerado
python main.py --doctor --status

# 7. Symlink verificado
# (.agent/workflows -> .agents/workflows OK)

# 8. Validacion final
python scripts/run_all_validations.py --quick
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es
```

---

*Documento alineado con docs/CONTRIBUTING.md (Flujo Post-Fase Obligatorio, Paso 6)*
*Formato CHANGELOG sigue docs/contributing/documentation_rules.md §36-58*
