# TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Versión objetivo**: 4.77.0 (a confirmar en FASE-P1) · **Workflow**: `phased_project_executor.md` v2.21.0
> **Estado**: ⬜ 0/5 sesiones — plan esqueleto creado como handoff de FASE-VERIFY del plan TRIBUNAL-OFFLINE-2026-09-09 (certificación `e6161a3`)
> **Predecesor**: TRIBUNAL-OFFLINE-2026-09-09 **cerrado 9/9** el 2026-09-11 (`bd2bf57`, v4.76.0 local sin push) — certificación 15 ✅ + **AC8 ❌**, que abre este plan
> **Fuentes**: `10-analisis-post-implementacion.md` del predecesor → L-E2E.1, L-E2E.3, L-V.1–L-V.4, D-V.1–D-V.4, L-R.1–L-R.3, §Seguimientos abiertos; `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/MATRIZ-CERTIFICACION.md`; `05-prompt-inicio-sesion-fase-T1.md` del predecesor (matriz findings→veredicto)
> **Anclaje**: ROADMAP v4.2 §7.2 tramo externo (T3 onboarding con datos reales)
> ⚠️ El R2.5 del predecesor **ya se ejecutó**: sus documentos viven en `Archives/TRIBUNAL-OFFLINE-2026-09-09/` — este plan los cita por nombre de archivo, resolver la ruta al cargar.

## Problema

v4.76.0 cierra el tramo offline del tribunal como **capa de auditoría** (Sentido A: funciona — el acta dual y los 4 reportes se producen en el pipeline real y detectaron defectos vivos: `VACUOUS_RECALL`, `CG-WHATSAPP-LEAD`). Pero **no enforcea** (Sentido B): el Juez corre **antes** del packaging y `_compute_verdict` solo consume gates; los 4 revisores corren **después** (necesitan `MANIFEST.json`/`ASSETS/`, que solo existen tras `packager.package()` — single-write ZIP-only, L-E2E.1); `reviewer_reports` queda `[]` y las recomendaciones BLOQUEAR/DEVOLVER-PRUEBAS no afectan ni veredicto ni ZIP (L-E2E.3).

Completan el cuadro:
- **AC8 ❌**: `EMPTY_DELIVERY_TEMPLATE` no detecta en régimen ZIP-only real (causa raíz en 2 capas fijada por sonda: `_resolve_delivery_dir()` cae al `.zip` + `_is_template_stub()` cuenta `---`/boilerplate como contenido).
- **Fidelidad del acta**: reporta `evidence_tier C` cuando el MANIFEST real es `B` (timing Juez/packaging, L-E2E.1). Veredicto invariante, documento menos preciso.
- **Régimen Tier A nunca ejercitado**: con dato real el primer piso se levanta y `APROBADO-PARA-ENTREGA` se vuelve alcanzable — **precisamente el régimen donde el hueco advisory tiene consecuencias** (el veredicto puede decir "entrega" sin reflejar objeciones de los revisores).

## Solución (dos vías, una decisión)

| Vía | Qué | Depende de |
|-----|-----|-----------|
| **E — Enforcement** | Decisión de producto (¿debe el tribunal bloquear?) + refactor del ordenamiento de delivery si la respuesta es sí (opciones O1–O3, ver plan maestro) | Solo código (P1–P2) |
| **O — Observación** | Corrida con hotel de **datos reales** (Tier A) como diagnóstico, no como entrega a cliente; `APROBADO-PARA-ENTREGA` tratado como provisional hasta cerrar E | Datos operativos reales (T3) |

**Secuenciación recomendada**: decidir E antes de correr O **si el acta va a un cliente real** — Tier A es el único régimen donde el veredicto tiene dientes, y hoy no consume las objeciones de sus propios revisores.

## Progreso

| # | Fase | Objetivo | Complejidad | Modo | Estado |
|---|------|----------|-------------|------|--------|
| 1 | FASE-P1 | Decisión de enforcement (Q1–Q4) + contrato del veredicto enriquecido + ACs finales | MEDIA | DIRECTO | ⬜ Pendiente |
| 2 | FASE-P2 | Refactor de ordenamiento según opción elegida (O1/O2/O3) — solo si Q1 = sí | **ALTA** | DIRECTO | ⬜ Pendiente |
| 3 | FASE-P3 | Fixes localizados: AC8 (ZIP-only), tier del acta, whitelist barreda (D-V.1), versión del acta | MEDIA | DIRECTO | ⬜ Pendiente |
| 4 | FASE-P4 | Corrida de observación Tier A (hotel datos reales) + informe de comportamiento | MEDIA | MIXTO | ⬜ Pendiente |
| 5 | FASE-RELEASE-4.77.0 | Cierre documental + version bump + archivado (R2.5) | BAJA | DELEGABLE | ⬜ Pendiente |

## Alcance

**Dentro**: decisión de enforcement, refactor de ordenamiento (si procede), fixes localizados heredados, corrida de observación con datos reales, certificación formal (patrón VERIFY) y release.

**Fuera**: T5 (deploy FTP/WP + staging), T6 (throughput + gancho), corpus multi-hotel (S-V10 exige ≥3 hoteles — una corrida valida el camino Tier A, no da confianza estadística), decisión de producto sobre S-H2 (performance pain).

## Residuos heredados y su disposición

| Residuo | Disposición en este plan |
|---------|--------------------------|
| AC8 ❌ (detección de plantilla vacía rota en ZIP-only) | FASE-P3 — opción a fijar en P1 (Q2b): leer `IMPLEMENTATION_ORDER.md` del ZIP **o** recalibrar `_is_template_stub()` |
| Acta `evidence_tier C` vs MANIFEST `B` | FASE-P3 (leer tier de `financial_scenarios.breakdown.evidence_tier` — precedente: `_extract_evidence_tier` de `honesty_reviewer.py` ya lo hace) — converge con P2 si hay reordenamiento |
| Barreda `asset_path` (D-V.1: whitelist test-only) | FASE-P3 |
| Versión hardcodeada en el acta (`acta_writer.py`) | FASE-P3 — leer de `VERSION.yaml` |
| Endurecimiento del executor (D-V.3) | **Ejecutado** en RELEASE-4.76.0: executor v2.21.0 con R2.6 y R2.7. Lo pendiente es la otra mitad — ninguna de las dos tiene verificador mecánico → P1 |
| Deuda de gates medida en el R2.5 del predecesor | FASE-P1 — ver §Deuda de proceso en `06-checklist-implementacion.md` (6 ítems: verificadores R2.6/R2.7, cobertura 12,5 % de `validate_plan_closure.py`, campo `Version actual` del REGISTRY, reescrito ciego de `validate_opencode_refs.py --fix`, punto ciego de `version_consistency_checker.py` ante `FASE-RELEASE-x.y.z`, y L-R.1: la columna `Iteraciones` no obliga a medir) |
| S-HF1, resolución por `mtime`, `FASE_D_DELIVERIES_DIR` sin usar, citas de línea en `decision-integracion.md` | Backlog — P1 decide si entran al alcance (NR6 cubre `mtime` si se toca el resolutor) |

## Reglas transversales (heredadas del predecesor)

1. R1: una fase por sesión. Sin excepciones.
2. R2.1: presupuesto medido con instrumento (`evidence/FASE-D/measure_iterations.py`), corte en commit.
3. R2.2: sin números de línea — citar símbolos.
4. R2.3: no-regresión como delta con par pre/post.
5. R2.4: AC no legible en artefacto = ⚠️, nunca ✅.
6. R2.5: RELEASE termina archivando el plan.
7. R2.6: todo lector de artefactos del pipeline se prueba contra el baseline real (`output/FASE-D_salentoreal_post_guard/`), con `skipif` explícito y la evidencia declarando si el test corrió o se saltó.
8. R2.7: el delta NR1 se valida por resta — `suma_post − suma_pre == tests_nuevos`; diferencia 0 = baseline contaminado.
   ⚠️ R2.6 y R2.7 existen desde v2.21.0 y **ninguna tiene verificador mecánico** (deuda de P1).
9. R3: ≤4 tareas + 0 comandos largos, ó ≤3 tareas + 1 comando largo.
10. NR2: el tribunal NO reimplementa lógica de gates (verificar consistencia sí, recalcular no).
11. NR3: una sola ruta de bloqueo — el enforcement se integra en la existente (`blocks_delivery_zip` → ZIP-skip), nunca una cuarta.
12. NR5: el LLM extrae, el Juez decide (veredicto determinista).
