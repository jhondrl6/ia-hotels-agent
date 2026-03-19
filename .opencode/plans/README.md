# Plan: Evolución del Agent Harness - Patrones Superpowers-Inspired

## Objetivo

Implementar mejoras incrementales al agent_harness de iah-cli inspiradas en Superpowers, SIN adoptar el framework externo. El enfoque es evolución natural utilizando patrones que ya funcionan en el proyecto.

## Mejoras a Implementar

| # | Mejora | Archivo Objetivo | Tipo |
|---|--------|-----------------|------|
| 1 | TDD Gate (Step 0.5) | `.agents/workflows/phased_project_executor.md` | Process Enhancement |
| 2 | Parallel Execution | `.agents/workflows/audit_guardian.md` | Performance Optimization |

## Principios Rectores

- **Evolución, no inyección**: Mejorar lo que existe, no importar frameworks externos
- **Sesiones únicas por fase**: Cada fase se ejecuta en una sesión independiente
- **Cumplimiento riguroso**: Seguir CONTRIBUTING.md §5 para documentación obligatoria
- **Capability Contracts**: Verificar que las nuevas capacidades estén conectadas al flujo principal

---

## Estructura de Fases

| Fase | Descripción | Restricción |
|------|-------------|-------------|
| 1 | TDD Gate en phased_project_executor.md | Sesión única |
| 2 | Parallel Execution en audit_guardian.md | Sesión única |
| 3 | Validaciones y documentación final | Sesión única |

**Regla dorada**: NO continuar a la fase siguiente en la misma sesión. Cada fase debe completar con su checklist y cerrarse.

---

## Pre-requisitos de Validación

- [ ] Scripts de validación funcionan: `python scripts/run_all_validations.py --quick`
- [ ] Validaciones del proyecto pasan: `python scripts/run_all_validations.py`
- [ ] Sincronización de versiones: `python scripts/sync_versions.py --check`

---

## Criterios de Éxito del Plan

- [ ] Fase 1 completada: TDD Gate implementado en phased_project_executor.md
- [ ] Fase 2 completada: Parallel Execution implementado en audit_guardian.md
- [ ] Fase 3 completada: Validaciones passed, documentación actualizada
- [ ] Matriz de capacidades actualizada
- [ ] CHANGELOG.md con entrada de release
- [ ] 0 capacidades huérfanas

---

## Recursos

- **CONTRIBUTING.md**: Guía de contribución obligatoria (§5, §13)
- **phased_project_executor.md**: Workflow de referencia (v1.4.0)
- **AGENTS.md**: Contexto global v4.5.3

---

## siguiente fase

Ver `.opencode/plans/05-prompt-inicio-sesion-fase-1.md` para iniciar la Fase 1.
