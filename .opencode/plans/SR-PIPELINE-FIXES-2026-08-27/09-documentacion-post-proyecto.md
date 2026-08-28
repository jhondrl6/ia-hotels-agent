# Documentación Post-Proyecto — SR-PIPELINE-FIXES-2026-08-27

> **Fuente de datos para FASE-RELEASE-4.73.0** (CHANGELOG + GUIA_TECNICA). Cada fase completa SUS filas al cerrar (executor §4, template §5.3).

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (ninguno previsto — refactor de módulos existentes) | | | |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Helper único de conteo `unresolved` | `modules/quality_gates/alignment_result.py` | `AlignmentResult.compute_unresolved()` consumido por gate_report y delivery_quality_report (fin de la divergencia 4-vs-1) | SR-A |
| Guardián estático L-SR1 | `tests/test_main_static_guards.py` | Test AST que impide símbolos no definidos (`logger.`) en ramas no ejercitadas de main.py | SR-A |
| Promesa derivada de fuente única | `modules/commercial_documents/v4_proposal_generator.py` + `modules/asset_generation/proposal_asset_alignment.py` | Servicios prometidos derivados del pain_ledger + present_in_production; NO_BREACH fuera del coverage (fin del bloqueo estructural) | SR-B |
| Self-healing de claims | `modules/quality_gates/commercial_gate.py` + flujo de regeneración | CG-CLAIM-VS-EVIDENCE cicla: regenera con suggestion + re-valida; persistencia → BLOCKED real | SR-C |
| target_id canónico | `main.py` | URL normalizada vía `_normalize_url()` antes de construir target_id (fin de fragmentación por UTM) | SR-D |
| Preflight con confianza de fuentes | `modules/commercial_documents/pain_solution_mapper.py` | Confianza del asset desde fuentes para construirlo (GBP/web); respeta fallback del catálogo | SR-E |
| Determinismo del plan de assets | `pain_solution_mapper.py` (o cache) | Hipótesis de varianza 7→5 verificada/fixeada | SR-F |
| Display sincronizado con fuente | `modules/quality_gates/commercial_gate.py` | CG-TIER-CONSISTENCY deriva de fuente financiera; jerga reducida en vista gerencia | SR-G |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests totales (baseline) | 3,379 | — |
| Tests nuevos SR-A | (contar al cerrar) | SR-A |
| Tests nuevos SR-B | (contar al cerrar) | SR-B |
| Tests nuevos SR-C | (contar al cerrar) | SR-C |
| Tests nuevos SR-D | (contar al cerrar) | SR-D |
| Tests nuevos SR-E | (contar al cerrar) | SR-E |
| Tests nuevos SR-F | (contar al cerrar) | SR-F |
| Tests nuevos SR-G | (contar al cerrar) | SR-G |
| Coherence corrida final | (llenar en SR-H) | SR-H |
| Gates PASSED corrida final | (llenar en SR-H) | SR-H |
| readiness corrida final | (llenar en SR-H) | SR-H |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/quality_gates/alignment_result.py` | Helper compute_unresolved unificado | SR-A |
| `modules/quality_gates/publication_gates.py` | Consumo del helper; gate excluye NO_BREACH | SR-A/SR-B |
| `modules/quality_gates/delivery_quality_report.py` | G9 consume helper único | SR-A |
| `modules/commercial_documents/v4_proposal_generator.py` | Promesas derivadas del pain_ledger | SR-B |
| `modules/asset_generation/proposal_asset_alignment.py` | Taxonomía única / actionable como fuente | SR-B |
| `modules/quality_gates/commercial_gate.py` | Self-healing + tier display + jerga | SR-C/SR-G |
| `main.py` | Canonicalización target_id | SR-D |
| `modules/commercial_documents/pain_solution_mapper.py` | Preflight confianza de fuentes + determinismo | SR-E/SR-F |

## Notas de Ejecución por Fase

### FASE-SR-A
- (llenar al cerrar: decisiones, desviaciones, incidentes)

### FASE-SR-B
- (llenar al cerrar)

### FASE-SR-C
- (llenar al cerrar)

### FASE-SR-D
- (llenar al cerrar)

### FASE-SR-E
- (llenar al cerrar)

### FASE-SR-F
- (llenar al cerrar)

### FASE-SR-G
- (llenar al cerrar)

### FASE-SR-H
- (llenar al cerrar: corrida, smoke, evidencia)

### FASE-SR-VERIFY
- (llenar al cerrar: ACs, diff, lecciones)

### FASE-RELEASE-4.73.0
- (llenar al cerrar)
