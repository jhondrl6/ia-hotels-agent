# Matriz de Capacidades - v4.5.4

> Estado: En evaluación durante implementación de mejoras

## Capability Contract

| Capability | Estado | Punto de Invocación | Output Observable | Severidad |
|------------|--------|---------------------|------------------|-----------|
| TDD Gate (nuevo) | por conectar | phased_project_executor.md:Step 0.5 | Test fallando documentado | HIGH |
| Parallel Execution (nuevo) | conectada | audit_guardian.md:Step 2-4 | Stages ejecutados en paralelo | MEDIUM |
| MetadataValidator | conectada | v4_comprehensive.py:_audit_metadata() | audit_result.metadata | HIGH |
| PublicationGates | conectada | main.py:FASE 4.5 | gate_results | CRITICAL |
| ConsistencyChecker | conectada | main.py:FASE 4.6 | consistency_report | HIGH |
| FinancialCalculatorV2 | conectada | main.py:FASE 3 | scenarios | CRITICAL |
| CoherenceValidator | conectada | commercial_documents/ | coherence_score | CRITICAL |
| QA Guardian | conectada | .agents/workflows/qa_guardian.md | QA report | HIGH |
| V4 Regression Guardian | conectada | .agents/workflows/v4_regression_guardian.md | regression_report | HIGH |

## Nuevas Capacidades a Integrar

### TDD Gate
- **Propósito**: Requerir test fallido antes de implementación de código
- **Archivo**: `.agents/workflows/phased_project_executor.md`
- **Punto de invocación**: Step 0.5 (nuevo)
- **Output**: Test en `tests/test_[feature].py` con estado inicial fallando
- **Severidad**: HIGH

### Parallel Execution
- **Propósito**: Ejecutar stages independientes en paralelo
- **Archivo**: `.agents/workflows/audit_guardian.md`
- **Punto de invocación**: Steps 2-4 (modificados)
- **Output**: Stages geo/seo/ia completados en paralelo
- **Severidad**: MEDIUM

## Verificación de Capacidad

```bash
# Verificar que TDD Gate está conectado
grep -n "0.5. TDD Gate" .agents/workflows/phased_project_executor.md

# Verificar que Parallel Execution está conectado
grep -n "parallel" .agents/workflows/audit_guardian.md
```

## Criterios de Evaluación

| Estado | Descripción |
|--------|-------------|
| **conectada** | Existe en código Y se invoca en runtime |
| **por conectar** | Existe en código PERO no se ha invocado aún (durante implementación) |
| **desconectada** | Existe en código PERO no se invoca en flujo principal |
| **huérfana** | Existe en código PERO no produce output observable |

---

## Historial de Cambios

| Fecha | Capability | Cambio |
|-------|------------|--------|
| 2026-03-17 | TDD Gate | Agregado (por conectar) |
| 2026-03-18 | Parallel Execution | Conectada |
