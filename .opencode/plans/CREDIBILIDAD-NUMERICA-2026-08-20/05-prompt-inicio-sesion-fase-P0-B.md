# FASE-P0-B: Gate Bloqueante `pricing_compliance` (F1 — segunda mitad)

**ID**: CREDIBILIDAD-NUMERICA-2026-08-20 / FASE-P0-B
**Objetivo**: Crear el gate de publicación `pricing_compliance` (BLOCKING) que bloquea cuando el
pricing calculado incumple los ratios de `config/pricing.yaml` (`is_compliant: false` hoy no bloquea nada).
**Dependencias**: FASE-P0-A ✅ (fuente única de pricing ya implementada)
**Duración estimada**: 1 sesión (≤60 iteraciones)
**Skill**: `phased_project_executor.md` (ejecución DIRECTA)

## Modo de Ejecución

**DIRECTO con el agente principal.** Diseñar un gate nuevo dentro del orquestador de publication
gates es una decisión de diseño que requiere entender la taxonomía blocking/advisory existente.

## Contexto

CONTEXT §2 fallo **F1**: `financial_scenarios.json` de la corrida real reporta
`pricing.is_compliant: false` (pain_ratio 0.0724 > 0.06 del gate `max_ratio` de pricing.yaml)
y **ningún gate lo bloquea**. El plan P0 exige: "Gate bloqueante `pricing_compliance`
(is_compliant=false debe BLOQUEAR)".

**⚠️ DECISIÓN DE DISEÑO PRE-RESUELTA (01-plan-maestro §7 D1) — leer ANTES de implementar**:

El `is_compliant` actual (`pricing_calculator.py` L372/L417) compara `pain_ratio` contra los gates
GLOBALES (0.03-0.06). Para Zi One: precio floor 400K / fuga ~5.5M → ratio mínimo posible =
0.0724 > 0.06. **Matemática estructural**: para que exista ALGÚN precio ≥ operational_floor (400K)
que cumpla ratio ≤ 0.06, la fuga debe ser ≥ 400K/0.06 = $6.67M/mes. La fuga de Zi One NO está
garantizada en ese rango ni siquiera tras los fixes F5 (OTA 0.20) y F2/F4 — dependería del peso
del componente OTA.

Un gate BLOCKING sobre el criterio actual haría **imposible V12 (READY_FOR_PUBLICATION)** en el
E2E aunque TODOS los fixes funcionen. El plan se contradeciría a sí mismo (V2 exige gate
presente+correcto, V12 exige publicación).

**Precedente en el código vivo**: `coherence_validator._check_price_matches_pain` YA resolvió este
problema con PATCH-A ("max_ratio 0.50 para min_price floors" — L467). El sistema ya reconoce que
los floors inflan el ratio.

**Regla del gate a implementar (floor-aware)**:
- **BLOCKING**: `pain_ratio > pain_ratio_gate_max` del TIER (leer de pricing.yaml
  `tiers.<tier>.pain_ratio_gate_max`, hoy 0.32 boutique — ya existe, NO inventarlo)
- **WARNING (no bloquea)**: `pain_ratio` fuera del rango ideal 0.03-0.06 CUANDO el pipeline aplicó
  `operational_floor` (metadato disponible: `final_price == operational_floor` / pasos del pipeline
  en `metadata.pipeline_steps`)
- El mensaje del gate reporta: ratio real, umbral del tier aplicado, rango ideal, y si el floor
  fue aplicado (trazable para el hotelero)

Con esta regla: Zione (0.0724 < 0.32) → gate PASSED con warning → V2 y V12 compatibles.
Un hotel con ratio 0.5 (precio abusivo real) → BLOCKING. El gate NO se debilita; se alinea con
la taxonomía de umbrales que pricing.yaml ya define (globales ideales + tier máximos).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-P0-A | ✅ Completada (verificar en 06-checklist antes de iniciar) |

### Base Técnica Disponible
- `modules/quality_gates/publication_gates.py` (`PublicationGatesOrchestrator`, `PublicationGateConfig`, `GateStatus`)
- Taxonomía AGENTS.md: 9 gates blocking + 3 advisory (12 total); umbrales en `config/pricing.yaml` (gates: min_ratio 0.03, max_ratio 0.06; tiers.*.pain_ratio_gate_max: 0.32 boutique)
- Output de P0-A: fuente única de pricing
- Línea base: `evidence/BASELINE-TESTS-v4.71.0.txt` (capturada en P0-A T0) — "sin regresiones" = sin fallos NUEVOS

## Tareas

### T1: Diseñar e implementar el gate `pricing_compliance` (BLOCKING floor-aware)
**Archivos afectados**:
- `modules/quality_gates/publication_gates.py` (o el módulo de gates de dominio que corresponda tras investigar)
**Criterios de aceptación**:
- [ ] Gate registrado en el orquestador con severidad BLOCKING
- [ ] Lee `pricing.pain_ratio` + tier desde financial_scenarios y los umbrales desde `config/pricing.yaml` (gates globales + `pain_ratio_gate_max` del tier)
- [ ] BLOCKING si `pain_ratio > pain_ratio_gate_max` del tier (0.32 boutique) → bloquea publicación
- [ ] WARNING (no bloquea) si fuera del rango ideal 0.03-0.06 con `operational_floor` aplicado (regla floor-aware D1 — ver Contexto)
- [ ] Mensaje del gate explica ratio, umbral del tier y rango ideal (trazable para el hotelero)

### T2: Integración con el flujo v4complete + sincronizar AGENTS.md
**Criterios de aceptación**:
- [ ] El gate aparece en `gate_report.json` de las corridas
- [ ] **AGENTS.md actualizado EN ESTA FASE** (no dejarlo para RELEASE): "12 publication gates — blocking (9) + advisory (3)" → "13 publication gates — blocking (10) + advisory (3)", y la línea del gate en la tabla de FASE 4.5/§Módulos si aplica. Razón: el conteo en AGENTS.md es ESTÁTICO y `scripts/validate_agents_md.py` check_3 lo compara contra `self.gates` en publication_gates.py (FAIL si difiere). Nota: `run_all_validations.py --quick` NO ejecuta ese script → un drift quedaría invisible; por eso se valida explícitamente abajo

### T3: Tests del gate
**Criterios de aceptación**:
- [ ] Test: pain_ratio > pain_ratio_gate_max del tier → BLOCKING fail
- [ ] Test: pain_ratio 0.0724 (Zione) con floor aplicado → PASSED con warning (contrato D1)
- [ ] Test: pain_ratio dentro del rango ideal → PASSED sin warning
- [ ] Test: ratio en borde (pain_ratio_gate_max exacto) → comportamiento definido
- [ ] Suite `tests/quality_gates/` sin fallos NUEVOS vs línea base

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Gate pricing_compliance | `tests/quality_gates/test_pricing_compliance_gate.py` (nuevo) | Todos pasan (incluye contrato floor-aware D1) |
| Regresión gates | `pytest tests/quality_gates/ -v` | Sin fallos NUEVOS vs línea base |
| Coherencia AGENTS.md | `python scripts/validate_agents_md.py` | exit 0 (check_3 gate_count PASS con 13 gates) |

**Comando de validación**:
```powershell
.\venv\Scripts\python.exe -m pytest tests/quality_gates/ -v
.\venv\Scripts\python.exe scripts/validate_agents_md.py
.\venv\Scripts\python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. `dependencias-fases.md` y `06-checklist-implementacion.md`: marcar FASE-P0-B ✅.
2. `README.md` del plan: actualizar tabla de progreso.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E (documentar la decisión D1 floor-aware con su evidencia: pricing_calculator L372/L417, PATCH-A, fórmula fuga ≥ 6.67M).
4. `10-analisis-post-implementacion.md`: fila de ejecución + mínimo 3 lecciones.
5. **Registrar la fase**:
```powershell
.\venv\Scripts\python.exe scripts/log_phase_completion.py --fase FASE-P0-B --desc "Gate bloqueante pricing_compliance floor-aware (F1) + AGENTS.md 13 gates" --archivos-mod "modules/quality_gates/publication_gates.py,AGENTS.md" --tests "<N>" --check-manual-docs
```
6. Editar CHANGELOG.md y GUIA_TECNICA.md (template §6).

## Criterios de Completitud (CHECKLIST)

- [ ] Gate bloquea efectivamente cuando pain_ratio > pain_ratio_gate_max del tier (verificado por test, no por lectura)
- [ ] Contrato floor-aware verificado: ratio 0.0724 con floor → PASSED + warning (test)
- [ ] AGENTS.md actualizado a 13 gates y `validate_agents_md.py` exit 0
- [ ] Suite quality_gates sin fallos NUEVOS vs línea base
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Post-ejecución completada

## Restricciones

- Máximo 60 iteraciones.
- NO re-abrir el refactor de pricing (ya cerrado en P0-A).
- NO modificar comportamiento de los otros 12 gates existentes.
- NO ejecutar v4complete.
- NO usar `--check-domain-primer` en log_phase_completion (bug latente: variable `root_dir` no definida en L765 del script).
