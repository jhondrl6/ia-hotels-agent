# Dependencias — COMMAND-VERIFICATION

## Diagrama de Dependencias

```
┌──────────────┐
│  FASE-CMD-A  │  Corrección de documentación
│  10 cambios │  AGENTS.md, CONTRIBUTING.md, procedures.md, README.md
│  ✅ 2026-05-24│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  FASE-CMD-B  │  Verificación + documentación post-fase
│  validación │  grep, run_all_validations, doctor, log_phase
│  ✅ 2026-05-24│
└──────────────┘
```

## Conflictos de Archivos

| Archivo | FASE-CMD-A | FASE-CMD-B |
|---------|-----------|-----------|
| AGENTS.md | Escribe (3 cambios) | Solo lee (grep verify) |
| CONTRIBUTING.md | Escribe (5 cambios) | Solo lee (grep verify) |
| procedures.md | Escribe (1 cambio) | Solo lee (grep verify) |
| README.md | Escribe (1 cambio) | Solo lee (grep verify) |

Sin conflictos — FASE-CMD-B solo verifica, no modifica los mismos archivos.

## Archivos NO Modificados

- `main.py` — NO se modifica (restricción del plan)
- `scripts/doctor.py` — NO se modifica (restricción del plan)
- `phased_project_executor.md` — Ya está limpio (26/26 comandos válidos)
- `ROADMAP.md` — NO se modifica
- `VERSION.yaml` — NO se modifica (doc-only, sin cambios de código)
