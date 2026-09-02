# Workflows Index (v4.72.2 — limpieza 2026-08-24)

> [!NOTE]
> El unico skill activo es `phased_project_executor`. Los 16 skills restantes fueron
> archivados en `archives/deprecated_workflows_20260824/` (motivo y restauracion en su README).
> La funcionalidad de la familia v4_* ya vive en codigo (`python main.py v4complete`).

## Workflows de Gestion de Proyectos

| Trigger (Cuando usar) | Skill | Estado |
|-----------------------|-------|--------|
| "Ejecuta por fases", "Continua en nueva sesion", "Divide en sprints" | [phased_project_executor.md](phased_project_executor.md) | Activo v2.18.0 |

**Nota**: `phased_project_executor` incluye un [template de prompts obligatorio](templates/prompt-fase-template.md) para estandarizar documentacion entre fases.

---

## Sistema de Validacion

El sistema incluye validacion nativa independiente:

| Comando | Uso |
|---------|-----|
| `python scripts/run_all_validations.py` | Validacion completa |
| `python scripts/run_all_validations.py --quick` | Validacion esencial |
| `python scripts/validate.py --plan` | Validar Plan Maestro |
| `python scripts/validate.py --security` | Detectar secretos |
| `python scripts/validate.py --content <file>` | Validar contenido |
| `pre-commit run --all-files` | Ejecutar hooks manuales |
