# Dependencias entre Fases — SR-PIPELINE-FIXES-2026-08-27

**Plan**: SR-PIPELINE-FIXES-2026-08-27 · **Workflow**: phased_project_executor v2.16.0 · **R1**: 1 fase por sesión

## 1. Diagrama de Dependencias

```
                    ┌──────────────────────────────────────────────────────┐
                    │  PREPARACIÓN (completada 2026-08-27)                 │
                    └──────────────────────┬───────────────────────────────┘
                                           ▼
   ┌─────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ FASE-SR-A│────▶│ FASE-SR-B│────▶│ FASE-SR-C│────▶│ FASE-SR-D│
   │ helper   │      │ unificación│    │ self-heal │    │ target_id│
   └─────────┘      └─────────┘      └─────────┘      └────┬────┘
                                                           ▼
                                                      ┌─────────┐
                                                      │ FASE-SR-E│
                                                      │schema+pres│
                                                      └────┬────┘
                                                           ▼
                                                      ┌─────────┐
                                                      │ FASE-SR-F│   (SR-G puede
                                                      │ varianza │    ejecutarse
                                                      └────┬────┘    tras SR-C)
                                                           ▼
                                                      ┌─────────┐
                                                      │ FASE-SR-G│
                                                      │ display  │
                                                      └────┬────┘
                                                           ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │ FASE-SR-H — ÚNICA ejecución v4complete (Salento Real)  [delegate]  │
   └──────────────────────────────┬─────────────────────────────────────┘
                                  ▼
                        ┌──────────────────┐
                        │  FASE-SR-VERIFY  │  (certificación AC1-AC13)
                        └────────┬─────────┘
                                 ▼
                        ┌──────────────────────────┐
                        │ FASE-RELEASE-4.73.0      │  [delegable]
                        └──────────────────────────┘
```

## 2. Estado por Fase (checkpoint de sesiones)

| Fase | Estado | Sesión | Checkpoint |
|------|--------|--------|------------|
| Preparación | ✅ COMPLETADA | orquestación 2026-08-27 | 13 archivos del plan creados; 0 fases ejecutadas |
| FASE-SR-A | ✅ COMPLETADA | agente 2026-08-28 | Helper `compute_unresolved()` + guardián AST L-SR1; 148 tests aislados PASSED (6 nuevos, 0 regresiones); greps residuos 0; quick 5/6 (Version Sync preexistente → RELEASE E2) |
| FASE-SR-B | ✅ COMPLETADA | agente 2026-08-28 | D-PF1 implementada: promesa derivada de pain_ledger + present_in_production (RC1 ↔ matriz ↔ gate, fuente única); coverage sobre actionable 3/4=0.75 en corrida C (estado intermedio hasta SR-E); suite gates 57 PASSED (10 tests nuevos de contrato); 8 fallos preexistentes en test_proposal_dynamic certificados en HEAD (0 regresiones); greps residuos 0 ("sin costo (fallback)", conteos paralelos); quick 5/6 (Version Sync preexistente → RELEASE E2) |
| FASE-SR-C | ⏳ PENDIENTE | — | — |
| FASE-SR-D | ⏳ PENDIENTE | — | — |
| FASE-SR-E | ⏳ PENDIENTE | — | — |
| FASE-SR-F | ⏳ PENDIENTE | — | — |
| FASE-SR-G | ⏳ PENDIENTE | — | — |
| FASE-SR-H | ⏳ PENDIENTE | — | — |
| FASE-SR-VERIFY | ⏳ PENDIENTE | — | — |
| FASE-RELEASE-4.73.0 | ⏳ PENDIENTE | — | — |

## 3. Matriz de Conflictos de Archivos

| Archivo | SR-A | SR-B | SR-C | SR-D | SR-E | SR-F | SR-G | SR-H | Notas |
|---------|------|------|------|------|------|------|------|------|-------|
| `modules/quality_gates/alignment_result.py` | ✏️ ESCRIBE | ✏️ extiende | — | — | — | — | — | — | SR-B reutiliza el helper de SR-A → SR-A PRIMERO |
| `modules/quality_gates/publication_gates.py` | ✏️ (consumo) | ✏️ ESCRIBE | — | — | — | — | — | — | ídem |
| `modules/quality_gates/delivery_quality_report.py` | ✏️ (consumo) | ✏️ (conteo unificado) | — | — | — | — | — | — | ídem |
| `modules/commercial_documents/v4_proposal_generator.py` | — | ✏️ ESCRIBE | — | — | — | — | — | — | fuente de promesas |
| `modules/asset_generation/proposal_asset_alignment.py` | — | ✏️ ESCRIBE | — | — | — | — | — | — | taxonomía `actionable` |
| `modules/quality_gates/commercial_gate.py` | — | — | ✏️ ESCRIBE | — | — | — | ✏️ ESCRIBE | — | SR-C PRIMERO que SR-G |
| `main.py` | — | — | (posible, flujo regeneración) | ✏️ ESCRIBE | — | — | — | — | SR-C PRIMERO que SR-D |
| `modules/commercial_documents/pain_solution_mapper.py` | — | — | — | — | ✏️ ESCRIBE | ✏️ (fix mínimo) | — | — | SR-E PRIMERO que SR-F |
| `modules/data_validation/external_apis/rich_results_client.py` | — | — | — | — | ✏️ ESCRIBE | — | — | — | fix parser JSON-LD array (H7, revisión 2026-08-28) |
| `modules/auditors/v4_comprehensive.py` | — | — | — | — | ✏️ ESCRIBE | — | — | — | propagación error_message (H7) |
| `modules/asset_generation/site_presence_checker.py` | — | — | — | — | ✏️ ESCRIBE | — | — | — | contabilización única exists_with_issues (H7) |
| `modules/orchestration_v4/onboarding_controller.py` | — | — | — | ✏️ ESCRIBE | — | — | — | — | `generate_hotel_id` (añadido revisión 2026-08-28) |
| `modules/asset_generation/asset_catalog.py` | — | — | — | — | 📖 LEE | — | — | — | contrato fallback (sin cambios) |
| `agent_harness/memory.py` | — | — | — | 📖 LEE | — | — | — | — | solo lectura (find_latest) |
| `config/settings.yaml` | — | — | — | — | — | 📖 LEE | — | — | PageSpeed key (sin tocar secretos) |
| `tests/**` | ✏️ | ✏️ | ✏️ | ✏️ | ✏️ | ✏️ | ✏️ | — | cada fase sus archivos |

**Regla**: cuando dos fases escriben el mismo archivo, la de menor índice va primero y la dependencia es OBLIGATORIA (no reordenar sesiones).

## 4. Dependencias Explícitas

| Fase | Requiere | Razón |
|------|----------|-------|
| FASE-SR-B | FASE-SR-A ✅ | El helper `compute_unresolved()` de SR-A es insumo del conteo unificado; mismo archivo |
| FASE-SR-D | FASE-SR-C ✅ | `main.py` potencialmente tocado por SR-C (flujo de regeneración); evitar conflicto |
| FASE-SR-F | FASE-SR-E ✅ | Mismo archivo `pain_solution_mapper.py` |
| FASE-SR-G | FASE-SR-C ✅ | Mismo archivo `commercial_gate.py` |
| FASE-SR-H | FASE-SR-A…G ✅ (todas) | La corrida E2E certifica la integración de todos los fixes |
| FASE-SR-VERIFY | FASE-SR-H ✅ | Verifica ACs contra el output E2E real |
| FASE-RELEASE-4.73.0 | FASE-SR-VERIFY ✅ | Regla del executor: RELEASE requiere todas las previas ✅ |

## 5. Recuperación de Agotamiento (R2 — 60 iteraciones)

1. Actualizar este archivo: estado `⏳ INCOMPLETA — agotamiento en iteración Y`, último checkpoint, qué falta.
2. Guardar evidencia en `evidence/FASE-SR-X/` (outputs parciales también cuentan).
3. Nueva sesión: leer el checkpoint, continuar desde ahí, NO re-ejecutar lo ya hecho.
4. Si SR-H agota: la corrida puede haber terminado en background — verificar `output/salentoreal_final_v4c/` ANTES de asumir fallo (Protocolo de Evidencia Proactiva).
