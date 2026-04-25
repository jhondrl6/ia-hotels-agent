# Dependencias de Fases: Intervencion Amazilia Hotel

```
                     +------------------+
                     |   FASE-RELEASE   |
                     |     4.35.0       |
                     +--------+---------+
                              |
                              v
+-------------------------------------------------+
| FASE-A: Alineacion Test Drift + Catalogos       |
| - test_proposal_confidence_disclosure.py        |
| - service_catalog.py vs proposal_asset_alignment|
| - Determinismo _generate_asset_quality_table    |
+-------------------------------------------------+
                              |
                              v
+-------------------------------------------------+
| FASE-B: Correccion Financiera Critica           |
| - Orden escenarios (conservative<=realistic<=opt)|
| - recovery_factor en ROI                        |
| - pain_ratio aplicado a recuperacion            |
| - Disclaimer Tier C                             |
+-------------------------------------------------+
                              |
                              v
+-------------------------------------------------+
| FASE-C: Template V6 + Lenguaje Entregables      |
| - Crear propuesta_v6_template.md                |
| - Fallback servicios dinamicos (no vacio)       |
| - Lenguaje positivo en tabla entregables        |
| - Timeline realista 7/30/60/90 dias             |
+-------------------------------------------------+
                              |
                              v
+-------------------------------------------------+
| FASE-D: AEO + Planes Dinamicos + Competidores   |
| - Entregable AEO condicional                    |
| - Planes dinamicos desde asset_plan             |
| - Seccion competidores desde GBP data           |
+-------------------------------------------------+
                              |
                              v
+-------------------------------------------------+
| FASE-VALIDATE: Prueba v4complete Unica          |
| - Hotel: Amazilia Hotel                         |
| - URL: https://amaziliahotel.com/               |
| - Unica ejecucion API del proyecto              |
+-------------------------------------------------+
                              |
                              v
+-------------------------------------------------+
| FASE-VALIDATE-RC: Hotfix Causa Raiz           |
| - Corregir TypeError _build_60_day_plan        |
| - Eliminar dead code legacy plan_*d            |
| - Test de regresion dict completo              |
| - Re-ejecucion v4complete (unica)              |
+-------------------------------------------------+
```

---

## Tabla de Progreso

|| Fase | Estado | Fecha inicio | Fecha fin | Tests ||
||------|--------|-------------|-----------|--------|
|| FASE-A | ✅ Completada | 2026-04-23 | 2026-04-23 | 132/132 ||
|| FASE-B | ✅ Completada | 2026-04-23 | 2026-04-23 | 132/132 ||
|| FASE-C | ✅ Completada | 2026-04-23 | 2026-04-23 | 132/132 ||
|| FASE-D | ✅ Completada | 2026-04-23 | 2026-04-23 | 132/132 ||
|| FASE-VALIDATE | ⚠️ Parcial-Falla | 2026-04-24 | 2026-04-24 | N/A ||
||| FASE-VALIDATE-RC | ✅ Completada | 2026-04-24 | 2026-04-24 | 1/1 ||

---

## Tabla de Conflictos Potenciales

| Archivo | Fases que lo modifican | Tipo de conflicto | Estrategia |
|---------|------------------------|-------------------|------------|
| `modules/commercial_documents/v4_proposal_generator.py` | FASE-B, FASE-C, FASE-D, FASE-VALIDATE-RC | Secuencial (mismo archivo) | Orden estricto: B -> C -> D -> RC |
| `modules/commercial_documents/service_catalog.py` | FASE-A, FASE-D | Secuencial | A antes que D |
| `modules/financial_engine/calculator_v2.py` | FASE-B | Unica | Ninguno |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | FASE-C | Nuevo archivo | Ninguno |

---

## Notas de Ejecucion

- FASE-A es la unica que puede ejecutarse en paralelo conceptualmente, pero la regla de "una fase por sesion" aplica igual.
- FASE-VALIDATE revelo un bug de ejecucion (TypeError) que impidio generar la propuesta. Sus archivos de diagnostico se generaron correctamente.
- FASE-VALIDATE-RC resolvio el TypeError y re-ejecuto v4complete. Nota: las variables legacy `plan_7d/30d/60d/90d` NO son dead code — son consumidas por `diagnostico_v4_template.md` y `propuesta_v4_template.md`. Se mantuvieron segun restriccion del plan. Se creo test de regresion `test_proposal_generator_dict.py` (4/4 PASS).
- Si FASE-VALIDATE-RC revela bugs nuevos no detectados, se crea FASE-VALIDATE-RC2 y se agenda nueva sesion. NO se re-ejecuta v4complete sin hotfix previo.
