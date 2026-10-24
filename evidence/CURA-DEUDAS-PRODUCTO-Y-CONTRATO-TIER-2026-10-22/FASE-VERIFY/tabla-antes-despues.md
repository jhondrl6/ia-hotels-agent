# FASE-VERIFY — tabla antes/después (baseline 2026-10-12 → corrida 2026-10-24)

Narrativo-técnica, leída **solo** de los artefactos de las dos corridas. Ambos runs: `v4complete` sobre `https://www.donalfonsohotel.com/`, tier de evidencia `B+`, mismo `input_data` (11 habitaciones · ADR 330.000 COP `user_provided` · ocupación 0,42424… · canal directo 30 %).

| Aspecto | Baseline 2026-10-12 (`CURA-COSTURA-TRIBUNAL-2026-10-11`) | Corrida 2026-10-24 (`CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER`) | Qué cambió | AC |
|---------|----------------------------------------------------------|-------------------------------------------------------------|------------|----|
| Veredicto del tribunal | `BLOQUEADO` | `APROBADO-CONDICIONAL` | El primer piso deja de bloquear y publica la causa en el acta | AC2 |
| `conditional_reason` | ausente (`None`) | `ANALYTICS_CEILING` | La causa nombra el techo real; no es `ONBOARDING_INCOMPLETE` pese al dato de 94 días, porque el loader casó por URL | AC2 · AC7 |
| `summary.over_presentations` | **2** (CRITICAL) | **0** | Los dos claims de totalidad se neutralizan por tier en propuesta y diagnóstico | AC1 |
| `findings[]` | 3 | 1 (`WARNING`, `undisclosed_warnings: 1`) | Baja el hallazgo de sobre-presentación; queda el aviso no divulgado, que no es blocking | AC1 |
| Claims absolutos en los documentos | emitidos | 0 ocurrencias de «Protección total para usted» y «Transparencia total»; el diagnóstico imprime la variante honesta | Redirección de copy, no censura: se conservan «Fuga total» (diagnóstico) y «Total recuperación» (propuesta) | AC1 |
| Estado del paquete | `package_evidence.suppressed: true`, `donalfonsohotel_20261012.zip.tmp` | `suppressed: false`, `donalfonsohotel_20261024.zip` en `deliveries/` | El ZIP se publica porque el veredicto lo permite: enforcement con dientes | AC7 |
| Huella del paquete | sha `dc00cdb9…` (cuarentena) | 94.432 B, sha `eeae4001…`, 82 miembros, medidos en disco | SHA y tamaño verificados contra el acta, no contra un registro | AC7 |
| Miembros por generación | — (re-medido aquí en el ZIP nuevo) | 26 con `20261012` · 28 con `20261024` · 28 sin timestamp | Confirma el hallazgo 1 declarado al cerrar E2E: el empaquetador barre el directorio del hotel. Dueño Operador, no invalida AC7 | AC7 |
| Pérdida realista | 3.511.200 COP/mes | 3.511.200 COP/mes (`scenarios.realistic` y `expected_monthly_cop`) | **Re-medida con el mismo `input_data`; el valor coincide.** FASE-E cambió el denominador regional (`revpar_cop` por región, default 168.000) y la cifra del hotel no se movió: se declara la coincidencia para que la igualdad no se lea como cifra prestada | AC7 |
| Brechas `PainSolutionMapper` | `pain_ledger.json → entries = 11`; `revision_alineacion.json → brechas_en_ledger = 11` | idéntico: `entries = 11` y `brechas_en_ledger = 11` | Mismo denominador honesto en los dos runs; el contrato GBP no infló ni vació la lista | AC3 · AC7 |
| Gates de publicación | 13 gates, `READY_FOR_PUBLICATION`, 0 blocking fallidos | 13 gates, `READY_FOR_PUBLICATION`, 0 blocking fallidos | Los warnings bajan: `asset_confidence` de «2 assets bajo 0.7» a «1 asset» | AC7 |
| Coherencia | 0,96333 | 0,92697 | Sigue encima del umbral 0.8; cae por la composición del paquete y el nuevo render, no por contradicción (`hard_contradictions = 0` en ambos) | AC7 |
| Assets generados (P6.3) | `13/13` | `12/12` | Un asset menos en el catálogo de la corrida; PASS en ambos | AC7 |
| Acciones correctivas del acta | 2 | 0 | El tribunal ya no tiene que corregir sobre-presentación | AC1 · AC2 |
| Primer piso | `applied: true` («evidence_tier B+ → máximo condicional») | `applied: true` (misma razón, otro artefacto fuente) | La regla del primer piso no se movió: el techo sigue siendo real y se declara | AC2 |
| `P6.5` | `NOT_EVALUABLE` — Reservada para Bot 4 | `NOT_EVALUABLE` — Reservada para Bot 4 | **Intacta**, verificada por lectura; `T1_CERTIFIABLE_CLAUSES` sin cambios | fuera (valla del plan) |
| Onboarding | baseline sin preflight con la sede del loader | `preflight.json` publica `rama_efectiva_del_loader: YAML_DE_DIR_CLIENTES`, `loader_devolvio: Hotel Don Alfonso`, `domain_confirmed: true`, `frescura_declarada_vencida: true`, sha de copia y versionada idénticos | La procedencia del onboarding pasa a ser verificable por artefacto — lo que `L32` pidió y aquí se lee | AC7 |
| `hotel_name` del reporte | `Donalfonsohotel` | `Donalfonsohotel` | Sin cambio: el hallazgo 2 sigue vivo, declarado con dueño Operador | fuera |
| Score GBP impreso | `63/100` por `places_api_real` | `63/100` por `places_api_real` | El `/90` de la rúbrica no se imprime en esta corrida: pertenece al camino `v4audit`. Escala legítima según `L29` (tres escalas del mismo `geo_score`) | AC8 (límite declarado) |

## Lectura de conjunto

El baseline era un paquete **bloqueado** por dos claims de totalidad que el revisor real encontró; la corrida los emite neutralizados por tier, publica el ZIP y explica su condicionante con la causa exacta. Los tres números que el plan usó como ancla —2 → 0 sobre-presentaciones, `BLOQUEADO` → `APROBADO-CONDICIONAL`, cuarentena → ZIP real— se leen en los artefactos, y los dos que **no** cambiaron (pérdida y brechas) se declaran como re-medidos, no como evidencia de mejora.
