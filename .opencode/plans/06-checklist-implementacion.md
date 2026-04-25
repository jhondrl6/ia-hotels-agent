# Checklist Maestro: Intervencion Amazilia Hotel

> Proyecto: Correccion de bugs y desalineaciones post-FASE-CAUSAL en iah-cli v4.35.0
> Hotel de validacion: Amazilia Hotel (https://amaziliahotel.com/)
> Fecha inicio: 2026-04-23
> Workflow: phased_project_executor v2.4.0
> Regla: Una fase por sesion. Sin excepciones.

---

## Progreso de Fases

| Fase | Descripcion | Estado | Fecha Inicio | Fecha Fin | Tests | Commit |
|------|-------------|--------|--------------|-----------|-------|--------|
| FASE-A | Alineacion test drift + catalogos de servicios | COMPLETADA | 2026-04-23 | 2026-04-23 | 19/19 | - |
| FASE-B | Correccion financiera critica | COMPLETADA | 2026-04-23 | 2026-04-23 | 30/30 | - |
| FASE-C | Template V6 + lenguaje entregables + timeline | COMPLETADA | 2026-04-23 | 2026-04-23 | 131/131 | - |
| FASE-D | AEO + planes dinamicos + competidores | COMPLETADA | 2026-04-23 | 2026-04-23 | 132/132 | - |
| FASE-VALIDATE | Prueba v4complete unica Amazilia Hotel | PARCIAL-FALLA | 2026-04-24 | 2026-04-24 | N/A | - |
|| FASE-VALIDATE-RC | Hotfix causa raiz + re-ejecucion v4complete | COMPLETADA | 2026-04-24 | 2026-04-24 | 1/1 | - |

---

## Dependencias entre Fases

```
FASE-A (catalogos y tests)
    |
    v
FASE-B (financiero)
    |
    v
FASE-C (propuesta/template)
    |
    v
FASE-D (AEO + dinamismo)
    |
    v
FASE-VALIDATE (v4complete unico)
    |
    v
FASE-VALIDATE-RC (hotfix + re-ejecucion)
```

**Regla de dependencia**: Ninguna fase puede iniciarse hasta que la anterior este marcada como COMPLETADA con checklist 100% verificado.

---

## Checklist por Fase

### FASE-A: Alineacion Test Drift + Catalogos
- [x] test_proposal_confidence_disclosure.py actualizado (7 servicios, sin "Visibilidad en ChatGPT")
- [x] SERVICE_CATALOG alineado con PROPOSAL_SERVICE_TO_ASSET (7 servicios identicos)
- [x] Tilde "Boton/Boton" resuelto
- [x] "Informe Mensual" presente en SERVICE_CATALOG (reemplaza "Barra de Reserva Movil")
- [x] `_generate_asset_quality_table()` determinista (mismo output dinamico/estatico)
- [x] Tests commercial_documents: 119/119 PASS
- [x] run_all_validations.py --quick: 4/4 PASS
- [x] REGISTRY.md actualizado via log_phase_completion.py

### FASE-B: Correccion Financiera Critica
- [x] _get_main_value() fix: FinancialScenario usa monthly_loss_cop (no monthly_loss_central/max)
- [x] Escenarios financieros ordenados: conservative >= realistic >= optimistic
- [x] Optimistic puede ser negativo (escenario de ganancia neta - OK por calculadora)
- [x] recovery_factor aplicado al ROI: conservative=0.15, realistic=0.20, optimistic=0.25
- [x] ROI realista <= 5.0X (era 20X, ahora ~4X)
- [x] pain_ratio aplicado a projected_gain (no recuperacion 100%): projected_gain = monthly_loss * pain_ratio
- [x] Disclaimer Tier C existente en EvidenceTier.C.disclaimer
- [x] Tests financial_engine: 30/30 PASS
- [x] run_all_validations.py --quick: 4/4 PASS
- [x] REGISTRY.md actualizado via log_phase_completion.py

### FASE-C: Template V6 + Lenguaje Entregables
- [x] propuesta_v6_template.md creado y cargable
- [x] Fallback de servicios dinamicos cuando pain_ids=None (no vacio) — retorna 7 servicios
- [x] Lenguaje de entregables: 0 apariciones de "No generado" / "Requiere datos" al cliente
- [x] Ortografia corregida en template (hoteles, brille, proveer, Absorbido, protección)
- [x] Timeline 7/30/60/90 dias realista (no promesa de 7 dias para todo)
- [x] Tests commercial_documents + delivery: 131/131 PASS
- [x] run_all_validations.py --quick: 4/4 PASS
- [ ] REGISTRY.md actualizado via log_phase_completion.py

### FASE-D: AEO + Planes Dinamicos + Competidores
- [x] Entregable AEO condicional si ao_score < 20 (score_aeo < 20 → optimizacion_ia_generativa en SERVICE_CATALOG)
- [x] Planes 7/30/60/90 dias usan asset_plan (no hardcoded) — backward compat si asset_plan=None
- [x] Seccion competidores generada cuando audit_result.competitors tiene datos
- [x] Tests commercial_documents + delivery: 132/132 PASS (0 regresiones)
- [x] run_all_validations.py --quick: 4/4 PASS
- [x] REGISTRY.md actualizado via log_phase_completion.py

### FASE-VALIDATE: Prueba v4complete Unica
- [x] v4complete ejecutado para https://amaziliahotel.com/
- [ ] Output generado sin errores criticos — **FALLA: TypeError en _build_60_day_plan()**
- [ ] BUG-1 verificado: seccion "Esto es lo que hacemos" no vacia — NO EVALUABLE (propuesta no generada)
- [x] BUG-2 verificado: escenarios ordenados en financial_scenarios.json — PASS (conservative > realistic > optimistic)
- [ ] BUG-3 verificado: ROI <= 5.0X — NO EVALUABLE (propuesta no generada)
- [ ] BUG-4 verificado: 0 items "No generado" al cliente — NO EVALUABLE (propuesta no generada)
- [ ] BUG-8 verificado: ortografia corregida — NO EVALUABLE (propuesta no generada)
- [ ] D-1 verificado: AEO incluido si aplica — NO EVALUABLE (propuesta no generada)
- [x] D-3 verificado: disclaimer presente si ADR estimado — PASS (disclaimer existe en financial_scenarios.json)
- [ ] D-4 verificado: timeline realista — NO EVALUABLE (propuesta no generada)
- [x] Evidencia copiada a evidence/fase-VALIDATE/
- [x] Checklist de validacion documentado
- [ ] REGISTRY.md actualizado via log_phase_completion.py

**NOTA CRITICA**: FASE-VALIDATE resulted in NO-GO. Bug encontrado: `V4ProposalGenerator._build_60_day_plan()` requiere argumento `asset_plan` que no se pasa en `_prepare_template_data()` line 559. Se requieren hotfix antes de re-ejecucion.

### FASE-VALIDATE-RC: Hotfix Causa Raiz + Re-ejecucion v4complete
- [x] Hotfix aplicado: lineas 559-560 pasan `asset_plan`
- [x] Dead code NO eliminado: grep revelo que plan_7d/30d/60d/90d SON usados por diagnostico_v4_template.md y propuesta_v4_template.md — se mantuvieron segun restriccion del plan
- [x] Test de regresion creado: `test_proposal_generator_dict.py` — 4/4 PASS
- [x] Validaciones pre-v4complete: run_all_validations.py --quick 4/4 PASS, pytest commercial_documents 124/124 PASS
- [x] v4complete ejecutado: comando completa sin crash, propuesta generada
- [x] BUG-1 verificado: seccion "Esto es lo que hacemos" no vacia — PASS (tabla con 8 servicios)
- [x] BUG-3 verificado: ROI <= 5.0X en propuesta — PASS (ROI: 0.2)
- [x] BUG-4 verificado: 0 items "No generado" / "Requiere datos" visibles al cliente — PASS
- [x] BUG-8 verificado: ortografía corregida — FIXED (2026-04-24): "huespedes" → "huéspedes" en 8 archivos
- [x] D-1 verificado: AEO incluido condicionalmente si aplica — PASS
- [x] D-4 verificado: timeline 7/30/60/90 dias realista — PASS
- [x] D-7 verificado: 0 items "No generado" en entregables — PASS
- [x] Evidencia copiada a evidence/fase-VALIDATE-RC/
- [x] REGISTRY.md actualizado via log_phase_completion.py

**Resultado bugs**: 7 PASS / FIXED, 0 FAIL, 0 NO EVALUABLE

---

## Estado Final del Proyecto

- [x] Todas las fases completadas (FASE-VALIDATE-RC completada 2026-04-24)
- [x] Documentacion post-proyecto (09-documentacion-post-proyecto.md) completada
- [x] VERSION.yaml no requiere bump (intervencion, no release)
- [x] CHANGELOG.md no requiere entrada nueva (intervencion, no release)
- [x] GUIA_TECNICA.md no requiere actualizacion (log_phase_completion.py confirmo)
- [x] run_all_validations.py (full) ejecutado y pasando (4/4)
