# Guia de Contribucion - IA Hoteles Agent

> **Version Actual:** v4.8.0 (NEVER_BLOCK Architecture)
> **Coherence Score:** 0.91 (≥0.8) - Publication Ready
> **Ultima fase completada:** FASE-CAUSAL-01 (SitePresenceChecker)
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
| `v4_regression_guardian.py --quick` | Validacion post-cambios v4 |

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

**Version:** v4.8.0

Archivos sincronizados automaticamente desde VERSION.yaml:
- `AGENTS.md`, `README.md`, `.cursorrules`, `INDICE_DOCUMENTACION.md`

Archivos que se actualizan **manualmente** (ver `documentation_rules.md`):
- `CHANGELOG.md`, `GUIA_TECNICA.md`, `ROADMAP.md`
- `docs/PRECIOS_PAQUETES.md`, `.agents/workflows/README.md`
