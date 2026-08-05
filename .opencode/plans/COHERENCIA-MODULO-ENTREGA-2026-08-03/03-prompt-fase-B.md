# FASE-B: Finanzas Honestas — D3 (costo único) + D4 (escenarios reales) + N1 (recuperación 6m única)

**ID**: COHERENCIA-FASE-B
**Objetivo**: Una sola fuente de verdad por concepto monetario: costos de brecha (D3), escenarios financieros (D4) y recuperación proyectada 6m (N1).
**Dependencias**: FASE-A ✅ (los costos se calculan sobre el N real de brechas).
**Duración estimada**: 1 sesión (~55 iteraciones de 60) — **la fase más ajustada del plan**.
**Skill**: `phased_project_executor` v2.13.0 · skills de apoyo: `iah-cli-code-modification`, `iah-cli-data-provenance-forensics`.

> ⚠️ **FASE DE MAYOR COMPLEJIDAD TÉCNICA DEL PLAN** — contiene 2 decisiones
> arquitectónicas cross-module (D3 y N1) que afectan múltiples consumidores.

## Contexto

El run 2026-08-01 publicó TRES sistemas de dinero independientes:
- **D3**: `opportunity_scores` del JSON report ($3.667.920) ≠ costos del doc ($2.996.906) para la MISMA brecha.
- **D4**: los escenarios reales del módulo (conservative=19.6M prob 0.70, realistic=7.19M prob 0.20, optimistic=−6.8M prob 0.10) nunca aparecen; el doc usa un rango sintético ±20% cuyo techo (8.63M) NO contiene el peor caso (19.6M). Además "70% de confianza" está mal atribuido (será N8 en FASE-D, pero la raíz se corrige aquí).
- **N1**: "recuperación proyectada 6m" diverge 3.2× entre artefactos del MISMO run: diagnóstico $3.020.634 vs propuesta $9.691.220 (curva de maduración) vs pain_ratio 0.0724 del pricing.

Fuente completa: contexto §5 FASE-2 (D3/D4/N1) y §3.4 (matemática N1).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada (detección única de brechas; N real disponible) |
| FASE-B | ▶️ EN CURSO (esta sesión) |

### Base Técnica Disponible
- Tests base: 3,185 + tests FASE-A.
- Baseline: `output/v4_complete/v4_complete_report.json` (opportunity_scores L320-377), `output/v4_complete/zione/v4_audit/financial_scenarios_20260801_170528.json`.

## Modo de ejecución (delegate_task)

**DIRECTO con el agente principal — NO DELEGABLE.** Regla executor §Regla-de-Decisión (branch decisión arquitectónica, lección DT-3 FASE-2): esta fase elige entre opciones de diseño no triviales que afectan múltiples consumidores en archivos distintos; un subagente carece del contexto completo. Aunque el perfil sea "código puro", la regla de decisión arquitectónica PREVALECE.

## Decisiones arquitectónicas (resolver ANTES de codificar)

### DEC-B1 — Fuente única de costos de brecha (D3)
- **Opción A (recomendada por el contexto)**: `_compute_opportunity_scores` (v4_diagnostic_generator.py L3217-3230) recibe los pesos normalizados de `_get_brecha_pesos` y los usa como `estimated_monthly_cop` → el JSON report queda idéntico al doc.
- **Opción B**: el doc consume `estimated_monthly_cop` del scorer (con channel multipliers), renormalizando a la suma total.
- **Decisión por defecto si no hay evidencia en contra**: Opción A (una sola dirección de datos: pesos → scorer).

### DEC-B2 — Fórmula única de recuperación proyectada 6m (N1)
- **Opción A (recomendada)**: la curva de maduración de `pillar_maturity_curve.py` (CURVA_4_PILARES=[0.15,0.35,0.60,0.80,0.95,1.00], Σ=3.85) ES la fórmula correcta (recuperación crece mes a mes, más honesta) → el diagnóstico la adopta. `recuperacion_6m = fuga_mensual × 0.35 × 3.85` en AMBOS documentos vía UNA función compartida.
- **Opción B**: mantener pain_ratio×recovery en ambos y eliminar la curva de la propuesta.
- **Decisión por defecto**: Opción A. El `pain_ratio` (0.0724) del pricing se reconcilia o se documenta como métrica distinta (relación precio/fuga), NUNCA como recuperación.
- Verificación: `grep -rn "recuperacion_proyectada_6m\|total_recuperacion_6m" modules/` → UNA definición compartida.

### DEC-B3 — Semántica de escenarios (D4)
- **Opción A (recomendada)**: el doc muestra los 3 escenarios reales con labels honestos: "Peor caso (conservador) 19.6M — 70%", "Más probable 7.19M — 20%", "Mejor caso (optimista) −6.8M (recuperación/ganancia neta proyectada) — 10%". Explicar explícitamente que −6.8M es GANANCIA.
- **Opción B**: corregir semántica en `scenario_calculator.py` (conservative = límite inferior) y recalcular.
- **Decisión por defecto**: Opción A (NO tocar fórmulas de pérdida, ver contexto §4.2).
- El `financial_value_range` [5.75M, 8.63M] se renombra a "rango ±20% del escenario más probable" o se amplía para contener el peor caso.

## Decisiones tomadas (2026-08-03, FASE-B)

> Verificadas contra código vivo y baseline auditado 2026-08-01. Se aplican las
> opciones por defecto recomendadas; ninguna contradice la evidencia.

### ✅ DEC-B1 — Opción A (D3, costo único)
`_compute_opportunity_scores` (v4_diagnostic_generator.py) sobreescribe
`estimated_monthly_cop` con los pesos normalizados de `_get_brecha_pesos`
(`base_value × impacto/100`, donde `base_value = monthly_loss_central o max`),
alineados por `pain_id`. El JSON report queda byte-igual al costo del doc
(`_get_brecha_costo` usa la misma base y proporción). El scorer conserva su
scoring/ranking interno; solo el `estimated_monthly_cop` publicable se unifica.
`_inject_brecha_scores` usa `monthly_loss_central` como base del `impacto_pct`
para que el % coincida con el peso normalizado del doc.

### ✅ DEC-B2 — Opción A (N1, recuperación 6m única)
La curva de maduración de `pillar_maturity_curve.py` ES la fórmula única.
Nueva función compartida `calcular_recuperacion_6m(fuga_mensual, recovery_factor_max)`
(= `aplicar_curva_4_pilares(...).total_recuperacion_6m` = fuga × recovery × 3.85).
Diagnóstico (`recuperacion_proyectada_6m`), propuesta (`net_benefit_6m`/`roi`,
`total_recuperacion_6m`, `recuperacion_proyectada_6m`, `recovered_6m`,
`net_benefit_6m` template) consumen ESA función. El `pain_ratio` se documenta
como métrica distinta (porción direccionable de la fuga / relación precio-fuga),
NUNCA como factor de recuperación: `pain_ratio_note` de diagnóstico y propuesta
se actualizan en consecuencia. Cifra Zione: 7.192.000 × 0.35 × 3.85 = $9.691.220
en AMBOS documentos (corrección de verdad documentada, riesgo §8 fila 2).

### ✅ DEC-B3 — Opción A (D4, escenarios honestos)
- Tabla de escenarios del doc muestra los 3 escenarios REALES del módulo con
  labels: "Peor caso (conservador)" / "Más probable" / "Mejor caso (optimista)",
  cada uno con su probabilidad (70/20/10). El valor negativo del optimista se
  etiqueta "Ganancia neta proyectada" (break-even superado).
- `CG-SCENARIO-ORDER` (commercial_gate.py) se ajusta a la semántica real:
  conservative = peor caso = MAYOR pérdida → orden válido en pérdida
  `conservative ≥ realistic ≥ optimistic` (optimistic < 0 = ganancia → PASS).
  El gate YA se ejecuta en `validate_diagnostic` (generator L605-627); el fix es
  su semántica + PERSISTIR el resultado.
- El `CommercialGateReport` del diagnóstico se persiste SIEMPRE en
  `output_dir/hotel_id/v4_audit/commercial_gates_report_diagnostic_<ts>.json`
  (con timestamp → NO colisiona con `commercial_gates_report.json` de la propuesta).
- `financial_value_range` [min, max] del escenario realista se mantiene como
  metadata y se etiqueta explícitamente: `financial_value_range_label` =
  "rango ±20% del escenario más probable (no incluye peores casos)". NO se
  amplía a [−6.8M, 19.6M] porque `hook_pdf_generator.py:273-276` lo mostraría
  como "fuga mínima negativa" (inaceptable comercialmente).
- `financial_method` se deriva de la fuente real de pesos:
  `dynamic_impact_normalized` si DynamicImpactCalculator participó,
  `pain_weights_normalized` si no (nunca más el hardcode genérico).
- Raíz de N8: `_build_urgencia_content` deja de atribuir "70% de confianza" al
  valor central; cita el escenario más probable con su probabilidad real (20%).

## Tareas

### T1 — Implementar DEC-B1 (D3): costo único
**Archivos**: `modules/commercial_documents/v4_diagnostic_generator.py` (`_compute_opportunity_scores`), `modules/financial_engine/opportunity_scorer.py` (L566 `estimated_monthly_cop` hoy usa `monthly_loss_max` del rango sintético).

- [x] `estimated_monthly_cop` sale de la MISMA fuente que `_get_brecha_costo` (pesos normalizados).
- [x] Report JSON y doc muestran cifras idénticas por brecha.

### T2 — Implementar DEC-B3 (D4): escenarios honestos + gate CG-SCENARIO-ORDER
**Archivos**: `v4_diagnostic_generator.py` (L1063-1079 workaround FASE-A E1, L1087-1099 labels "Mínimo garantizable/Más probable/Máximo alcanzable"), `modules/quality_gates/commercial_gate.py` (`_check_scenario_order` L297-348, ID CG-SCENARIO-ORDER).

> ⚠️ Dato verificado (2026-08-03): `validate_diagnostic` YA se ejecuta dentro de `generate()` (v4_diagnostic_generator.py:605-627) y YA corre `_check_scenario_order` (commercial_gate.py:148-149). El problema NO es que el gate no corra: es que su resultado SOLO va a `logging.warning`/alertas internas y NUNCA se persiste a disco. El commercial_gates_report.json solo lo escribe la propuesta (y solo en branch de error). FASE-B T2 NO debe "cablear el gate" (ya está cableado) sino **persistir el resultado del diagnóstico** en un artefacto del run.

- [x] El doc muestra los 3 escenarios reales del módulo con labels y probabilidades coherentes.
- [x] Label de confianza "70%" deja de atribuirse al valor central (prepara N8).
- [x] **Persistir el `CommercialGateReport` del diagnóstico** en `output_dir/hotel_id/v4_audit/commercial_gates_report_diagnostic_<ts>.json` (o sumarlo a la evidencia del run) para que CG-SCENARIO-ORDER aparezca en la evidencia del run — no solo en logs. Si el run actual los persiste en `v4_audit/`, verificar que la ruta del diagnóstico NO colisione con la de la propuesta.
- [x] `financial_method: "proportional_normalized"` (L1240) se deriva de la fuente real usada o se elimina.

### T3 — Implementar DEC-B2 (N1): recuperación 6m única
**Archivos**: `modules/financial_engine/pillar_maturity_curve.py` (función compartida), `v4_proposal_generator.py` (L1062 `recuperacion_proyectada_6m`), `v4_diagnostic_generator.py` (sección recuperación, doc:203-204).

> ⚠️ Dato verificado (2026-08-03): la propuesta tiene **DOS cálculos de recuperación**: (a) `net_benefit_6m`/`roi` (v4_proposal_generator.py:591-596) usan `pain_ratio × recovery_realistic` (0.20 × 0.20) — cifra distinta; (b) `total_recuperacion_6m`/curva (L786-925, `aplicar_curva_4_pilares`) = $9.691.220. El diagnóstico usa `pain_ratio 20% × recovery 35%` (doc:203-204). FASE-B T3 debe unificar (a), (b) y el diagnóstico en UNA fórmula.

- [x] Diagnóstico y propuesta consumen la MISMA función (todos los puntos: net_benefit/ROI, total_recuperacion_6m, tabla de curva y sección de recuperación del diagnóstico).
- [x] `pain_ratio` reconciliado o documentado como métrica distinta (relación precio/fuga), NUNCA como recuperación.

### T4 — Tests y fixtures
**Archivos**: `tests/financial_engine/`, `tests/commercial_documents/`.

- [x] Test: `estimated_monthly_cop` del report == costo del doc para la misma brecha.
- [x] Test: escenarios del doc == valores de `financial_scenarios.json` (labels + probs).
- [x] Test: recuperación 6m idéntica en diagnóstico y propuesta.
- [x] Test: CG-SCENARIO-ORDER presente en el gate_report del pipeline.
- [x] Actualizar fixtures/golden files rotos por el cambio de cifras (riesgo §8 fila 1-2).

## Tests Obligatorios

| Test | Comando | Criterio |
|------|---------|----------|
| Suites afectadas | `./venv/Scripts/python.exe -m pytest tests/financial_engine tests/commercial_documents -q` | 0 regresiones |
| Validaciones | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | 4/4 |

## Post-Ejecución (OBLIGATORIO)

1. Marcar FASE-B ✅ en `dependencias-fases.md`, `09-checklist-implementacion.md`, `README.md`.
2. Actualizar `11-documentacion-post-proyecto.md` (A, B, D, E) — incluir las decisiones DEC-B1/B2/B3 tomadas.
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B \
    --desc "D3 costo único + D4 escenarios honestos + N1 recuperación 6m única" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/v4_proposal_generator.py,modules/financial_engine/opportunity_scorer.py,modules/financial_engine/pillar_maturity_curve.py" \
    --tests "<N nuevos>" --check-manual-docs
```
> ⚠️ NO usar `--release` en fases intermedias (L3/L9) — solo en FASE-RELEASE.

## Criterios de Completitud (CHECKLIST)

- [x] DEC-B1/B2/B3 decididas y documentadas en el plan (sección decisiones)
- [x] D3, D4, N1 cerrados según criterios de T1/T2/T3
- [x] Tests T4 pasan + 0 regresiones
- [x] `run_all_validations.py --quick` 4/4
- [x] `log_phase_completion.py` ejecutado

## Restricciones

- Máximo 60 iteraciones (R2). Si el presupuesto se agota, priorizar: T2 (D4) > T1 (D3) > T3 (N1) y marcar ⏳ INCOMPLETA con checkpoint.
- NO delegar a subagente (decisión arquitectónica cross-module).
- NO ejecutar v4complete (única ejecución: FASE-E).
- NO tocar fórmulas de pérdida de `scenario_calculator.py` (contexto §4.2 — valores correctos).
- NO tocar `publication_gates.py` (FASE-C-A).
- Documentar el cambio de cifras para TODOS los hoteles como corrección de verdad (riesgo §8).
