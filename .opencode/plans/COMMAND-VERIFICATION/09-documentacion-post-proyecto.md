# Documentación Post-Proyecto — COMMAND-VERIFICATION

**Plan**: Corrección de comandos inválidos `main.py --doctor --<flag>` en documentación
**Tipo**: Doc-only (0 cambios de código Python)

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| — | — | Sin módulos nuevos (doc-only) | — |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| — | — | Sin funcionalidades nuevas (doc-only) | — |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Comandos inválidos corregidos | 10 ocurrencias en 4 archivos | FASE-CMD-A |
| Framing corregido | "Regenerable (1 comando)" → "(comandos directos)" en 2 archivos | FASE-CMD-A |
| Flag documentado agregado | `--agent` en README.md | FASE-CMD-A |
| Validaciones | run_all_validations --quick 4/4 | FASE-CMD-B |
| Archivos regenerados | SYSTEM_STATUS.md + DOMAIN_PRIMER.md | FASE-CMD-B |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| AGENTS.md | 3 cambios: L116 framing, L117 --status fix, L343 --agent fix | FASE-CMD-A |
| docs/CONTRIBUTING.md | 5 cambios: L122, L152, L154, L295, L297, L298 | FASE-CMD-A |
| docs/contributing/procedures.md | 1 cambio: L47 --regenerate-domain-primer fix | FASE-CMD-A |
| README.md | 1 cambio: L157-162 agregar --agent flag | FASE-CMD-A |
| .agent/SYSTEM_STATUS.md | Regenerado vía doctor.py --status | FASE-CMD-B |
| .agent/knowledge/DOMAIN_PRIMER.md | Regenerado vía doctor.py --regenerate-domain-primer | FASE-CMD-B |
| docs/contributing/REGISTRY.md | 2 entradas nuevas (FASE-CMD-A, FASE-CMD-B) | FASE-CMD-B |

---

> **NOTA**: Sin version bump — doc-only, VERSION.yaml no cambia. CHANGELOG queda ahead de VERSION.yaml (comportamiento esperado para doc-only phases).
