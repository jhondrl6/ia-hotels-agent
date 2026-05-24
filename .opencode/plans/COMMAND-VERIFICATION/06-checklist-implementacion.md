# Checklist Maestro — COMMAND-VERIFICATION

**Plan**: COMMAND-VERIFICATION (corrección de comandos inválidos en docs)
**Fecha inicio**: 2026-05-24

## Estados

| Fase | Descripción | Estado | Fecha completada |
|------|-------------|--------|-----------------|
| FASE-CMD-A | Corrección de documentación (10 cambios) | ✅ COMPLETADA | 2026-05-24 |
| FASE-CMD-B | Verificación + documentación post-fase | ✅ COMPLETADA | 2026-05-24 |

## Criterios Globales de Completitud

- [ ] `grep -rn "main.py --doctor --" AGENTS.md docs/CONTRIBUTING.md docs/contributing/procedures.md` retorna 0
- [ ] `grep "Regenerable (1 comando)" AGENTS.md docs/CONTRIBUTING.md` retorna 0
- [ ] README.md documenta los 5 flags de doctor.py
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `scripts/doctor.py --status` ejecuta sin errores
- [ ] `scripts/doctor.py --regenerate-domain-primer` ejecuta sin errores
- [ ] `log_phase_completion.py` ejecutado para ambas fases
- [ ] `09-documentacion-post-proyecto.md` actualizado

## Dependencias

```
FASE-CMD-A ──→ FASE-CMD-B
```
FASE-CMD-B solo se ejecuta cuando FASE-CMD-A está ✅.
