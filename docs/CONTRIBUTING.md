# Guia de Contribucion - IA Hoteles Agent

> **Version Actual:** v4.10.0 (NEVER_BLOCK Architecture + AEO Re-Architecture)
> **Coherence Score:** 0.84 (≥0.8) - Publication Ready
> **Ultima fase completada:** FASE-I-01 (Integración Autonomous Researcher)
> **Version del sistema de docs:** v2.3.0 (Version Sync Gate + Documentation Audit)
> **Consultar REGISTRY para historial de fases:** `docs/contributing/REGISTRY.md`

---

## Indice de Secciones

| Seccion | Ubicacion | Contenido |
|---------|-----------|-----------|
| Procedimientos | [procedures.md](contributing/procedures.md) | Reglas de version, skills, modulo, TDD |
| Documentacion | [documentation_rules.md](contributing/documentation_rules.md) | Checklist obligatoria, archivos manuales |
| Validacion | [validation.md](contributing/validation.md) | Pre-commit, regression, troubleshooting |
| Capabilities | [capabilities.md](contributing/capabilities.md) | Capability contracts, matriz de capacidades |
| Registro de Fases | [REGISTRY.md](contributing/REGISTRY.md) | **Auto-generado** - historial de fases completadas |

---

## Flujo de Documentacion Post-Fase

Cuando ejecutes `.agents/workflows/phased_project_executor.md`:

```
FASE completada
    │
    ├── Paso 6: Documentacion Post-Fase
    │   ├── Leer docs/contributing/documentation_rules.md §5
    │   ├── Ejecutar: python scripts/log_phase_completion.py --fase N
    │   │   ├── Registra en REGISTRY.md (auto)
    │   │   └── Muestra POR_HACER para docs manuales
    │   └── Verificar capability contracts (capabilities.md §13)
    │
    └── Validar con:
        python scripts/run_all_validations.py --quick
```

### Version Sync Gate (Release Final)

Cuando una fase marca un **release** (nueva version), usar el Version Sync Gate:

```bash
# Al completar fase final de un release
python scripts/log_phase_completion.py --fase FASE-X \
    --desc "Descripcion del release" \
    --archivos-mod "modules/foo.py" \
    --release 4.10.0 \
    --auto-sync

# O en dos pasos:
# Paso 1: Registrar sin gate
python scripts/log_phase_completion.py --fase FASE-X \
    --desc "Descripcion del release" \
    --archivos-mod "modules/foo.py"

# Paso 2: Verificar sincronizacion (BLOCKING si hay gap)
python scripts/log_phase_completion.py --fase FASE-X \
    --release 4.10.0 \
    --check-manual-docs
```

**El gate verifica:**
1. CHANGELOG.md tiene entrada `[X.Y.Z]`
2. CHANGELOG y VERSION.yaml coinciden en X.Y.Z
3. Documentacion manual (GUIA_TECNICA.md) menciona la fase

**Si hay desincronizacion:**
```
FAIL: Version desincronizada entre CHANGELOG y VERSION.yaml
Pasos:
  1. python scripts/version_consistency_checker.py  # Diagnosticar
  2. python scripts/sync_versions.py                # Sincronizar
  3. Reintentar con --release
```

**Consistency checker autonomo:**
```bash
python scripts/version_consistency_checker.py       # Verificar todo
python scripts/version_consistency_checker.py --fix # Auto-reparar si es posible
```

---

## Conexiones Clave

| Archivo | Proposito | Conexion |
|---------|-----------|----------|
| `AGENTS.md` | Contexto global canónico | §7 → CONTRIBUTING, executor |
| `phased_project_executor.md` | Motor de ejecucion por fases | Paso 6 → documentation_rules.md |
| `CONTRIBUTING.md` | Reglas de documentacion | Index → fragmentos + REGISTRY |
| `REGISTRY.md` | Registro auto de fases | Actualizado por log_phase_completion.py |

---

## Scripts de Mantenimiento

| Script | Uso |
|--------|-----|
| `log_phase_completion.py` | Registrar fase completada → REGISTRY.md |
| `sync_versions.py` | Sincronizar VERSION.yaml → archivos de contexto |
| `run_all_validations.py --quick` | Validacion antes de commit |
| `.agents/workflows/v4_regression_guardian.py --quick` | Validacion post-cambios v4 |

---

## Comandos CLI Activos

| Comando | Descripcion |
|---------|-------------|
| `v4complete` | Flujo completo con coherencia ≥0.8 |
| `v4audit` | Auditoria con APIs externas |
| `spark` | Diagnostico rapido <5min |
| `execute` | Implementa paquete recuperado |
| `deploy` | Despliegue remoto FTP/WP-API |

---

## Version y Sincronizacion

**Version:** v4.10.0

Archivos sincronizados automaticamente desde VERSION.yaml:
- `AGENTS.md`, `README.md`, `.cursorrules`

Archivos que se actualizan **manualmente** (ver `documentation_rules.md`):
- `CHANGELOG.md`, `GUIA_TECNICA.md`, `ROADMAP.md`, `INDICE_DOCUMENTACION.md`
- `.agents/workflows/README.md`
