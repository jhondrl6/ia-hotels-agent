# FASE-F — Impacto del corpus histórico (Tarea F4)

**Fecha**: 2026-09-03 · **Script**: `temp/faseF_impacto_corpus.py` (copia preservada en `evidence/FASE-F/faseF_impacto_corpus.py`; no se ejecutó v4complete)

Re-evaluación de artefactos persistidos bajo el comportamiento nuevo:

| Tarea | Naturaleza del cambio | ¿Puede voltear un veredicto de publicación? |
|---|---|---|
| F1 (A4) | Un oráculo de presencia decide **y** narra (`is_present_in_production`) | No — converge narrativa y decisión |
| F2 (A1) | `NOT_EVALUATED` ≠ `passed`; defaults G9 unificados | No — contabilidad del resumen de delivery |
| F3 (N11/P9) | El gate de coherencia respeta `is_coherent` (umbral 0.8 intacto) | **Sí — único volteador** |

Veredicto de COHERENCIA ANTES = solo score (pre-F3). DESPUÉS =
`coherence_verdict_passes(score_final, 0.8, is_coherent_final)` — la función embarcada,
importada de `modules/quality_gates/coherence_gate.py` (misma que consume publication_gates).
El score/veredicto leído es el que el assessment de producción consume
(`coherence_score_final` / `final_coherence_report`, DT4-N4); los scores pre-gen de
`coherence_validation.json` NO rescatan corridas (dossier §12.2, C3). Veredicto de PAQUETE =
coherencia AND asset_confidence (corridas 100% ESTIMATED bloqueadas en ambos mundos).

**Corpus medido**: 28 corridas primarias + 4 copias de delivery (reconciliación con C2 §12.2 más abajo).

## Resultados clave

- **Corridas 100% ESTIMATED**: 11 (incluye copias) — **TODAS siguen bloqueadas** ✓ (`coherence_score_final=None` ⟹ gate de coherencia sin score; `asset_confidence` bloquea el paquete en ambos mundos). Coincide con el dossier §12.2/C3: no hay score canónico que las rescate.
- **Veredictos de paquete que cambian**: 4 — todos en dirección **READY → NOT_READY** (seguro): corridas con `final_coherence_report.is_coherent=False` persistido que el gate pre-F3 ignoraba por leer solo el score (la familia exacta de N11/P9; incluye la repro SalentoReal FASE-D: score 0.88 + is_coherent False).
- **Ninguna corrida pasa de bloqueada a lista** — F3 solo endurece.
- **F1/F2**: no mueven veredictos (narrativa y contabilidad); ver lectura al final.

## Corridas primarias

| Corrida | Tipo | Score final | is_coherent final | Coherencia ANTES | Coherencia DESPUÉS | Paquete ANTES | Paquete DESPUÉS | Cambio |
|---|---|---|---|---|---|---|---|---|
| `archives/outputs/Don Alfonso/v4_complete/donalfonsohotel` | CON_DATOS | 0.95 | — | PASSED | PASSED | READY | READY | — |
| `archives/outputs/Don Alfonso/v4_complete` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/Luxor/v4_complete/luxorhotel` | CON_DATOS | 0.80 | — | PASSED | PASSED | READY | READY | — |
| `archives/outputs/Luxor/v4_complete` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/Marzo/hotel_visperas_20260227_221039` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/Marzo/hotel_vísperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/Marzo/hotel_vísperas_20260228_214722` | CON_DATOS | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/Marzo/hotelvisperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/ZiOne/v4_complete/hotel_test_001/v4_complete/hotelvisperas` | CON_DATOS | 0.88 | False | PASSED | BLOCKED (is_coherent=False) | READY | NOT_READY | F3 (veredicto respeta is_coherent) |
| `archives/outputs/ZiOne/v4_complete` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/ZiOne/v4_complete/zi_one_luxury` | CON_DATOS | 0.86 | — | PASSED | PASSED | READY | READY | — |
| `archives/outputs/ZiOne/v4_complete/zione` | CON_DATOS | 0.95 | True | PASSED | PASSED | READY | READY | — |
| `archives/outputs/hotelvisperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/v4_complete V/amaziliahotel` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete V/hotel_visperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete V/hotel_vísperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete V/hotelvisperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete V/v4_complete_hotelvisperas_aoe/v4_complete/hotelvisperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete/amaziliahotel` | CON_DATOS | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete_baseline/hotelvisperas` | ESTIMATED_100% | None | — | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | — |
| `archives/outputs/v4_complete_fix_test/v4_complete/hotelcastillareal` | CON_DATOS | 0.81 | — | PASSED | PASSED | READY | READY | — |
| `archives/outputs/v4_complete_fix_test/v4_complete` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/v4_complete_fix_v2/v4_complete/hotelcastillareal` | CON_DATOS | 0.81 | — | PASSED | PASSED | READY | READY | — |
| `archives/outputs/v4_complete_fix_v2/v4_complete` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `archives/outputs/v4_verify_f4/v4_complete/hotelcastillareal` | CON_DATOS | 0.81 | — | PASSED | PASSED | READY | READY | — |
| `archives/outputs/v4_verify_f4/v4_complete` | SIN_ARTEFACTOS | — | — | — | — | — | — | — |
| `output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal` | CON_DATOS | 0.88 | False | PASSED | BLOCKED (is_coherent=False) | READY | NOT_READY | F3 (veredicto respeta is_coherent) |

## Copias de delivery (no se cuentan como corrida)

| Corrida (copia) | ANTES | DESPUÉS | Cambio |
|---|---|---|---|
| `archives/outputs/Marzo/deliveries/hotelvisperas_20260323/ASSETS` | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | — |
| `archives/outputs/ZiOne/v4_complete/deliveries/zione_20260801/ASSETS` | PASSED | BLOCKED (is_coherent=False) | F3 (veredicto respeta is_coherent) |
| `archives/outputs/v4_complete V/deliveries/hotel_visperas_20260325/ASSETS` | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | — |
| `output/FASE-D_salentoreal_post_guard/v4_complete/deliveries/hotelsalentoreal_20260831/ASSETS` | PASSED | BLOCKED (is_coherent=False) | F3 (veredicto respeta is_coherent) |

## Corridas 100% ESTIMATED — DEBEN seguir bloqueadas

| Corrida | Score final | Coherencia ANTES | Coherencia DESPUÉS | Paquete ANTES | Paquete DESPUÉS | ¿Sigue bloqueada? |
|---|---|---|---|---|---|---|
| `archives/outputs/Marzo/deliveries/hotelvisperas_20260323/ASSETS` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/Marzo/hotel_vísperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/Marzo/hotelvisperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/hotelvisperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete V/amaziliahotel` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete V/deliveries/hotel_visperas_20260325/ASSETS` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete V/hotel_visperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete V/hotel_vísperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete V/hotelvisperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete V/v4_complete_hotelvisperas_aoe/v4_complete/hotelvisperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |
| `archives/outputs/v4_complete_baseline/hotelvisperas` | None | BLOCKED (sin coherence_score) | BLOCKED (sin coherence_score) | NOT_READY | NOT_READY | SÍ |

**Resultado**: TODAS siguen bloqueadas ✓ (asset_confidence intacto)

## Veredictos de paquete que cambian (única vía: F3)

| Corrida | Score final | is_coherent final | Paquete ANTES | Paquete DESPUÉS | Dirección |
|---|---|---|---|---|---|
| `archives/outputs/ZiOne/v4_complete/deliveries/zione_20260801/ASSETS` | 0.92 | False | READY | NOT_READY | listo → bloqueado (seguro) |
| `archives/outputs/ZiOne/v4_complete/hotel_test_001/v4_complete/hotelvisperas` | 0.88 | False | READY | NOT_READY | listo → bloqueado (seguro) |
| `output/FASE-D_salentoreal_post_guard/v4_complete/deliveries/hotelsalentoreal_20260831/ASSETS` | 0.88 | False | READY | NOT_READY | listo → bloqueado (seguro) |
| `output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal` | 0.88 | False | READY | NOT_READY | listo → bloqueado (seguro) |

**Dirección**: todos READY → NOT_READY (seguro: el validador ya había declarado `is_coherent=False`; F3 hace que el gate lo escuche)


## Reconciliación con el corpus C2 (27 corridas)

El conteo C2 §12.2 (**27 corridas únicas, 10 hoteles**) se midió sobre `output/` en su
estado de 2026-09-03; desde entonces buena parte del histórico fue archivado a
`archives/outputs/`. Esta medición barre `output/` **y** `archives/outputs/`, tomando como
unidad la carpeta `v4_audit` (conjunto canónico de artefactos por corrida) y excluyendo
copias bajo `deliveries/*/ASSETS/`. Corridas sin artefactos de coherencia/asset quedan
como SIN_ARTEFACTOS (sin veredicto evaluable).

## Lectura F1/F2 sobre el corpus

- **F1 (A4)**: no mueve veredictos; elimina la divergencia narrativa (`missing` vs
  `present_assets`) en corridas con presencia `exists_with_issues`. Los artefactos con
  `proposal_asset_matrix.json` quedan cubiertos por el test anti-A4 (`test_alignment_result.py`).
- **F2 (A1)**: en corridas cuyo `delivery_quality_report.json` no tiene `proposal_asset_matrix.json`,
  G9 pasaba en verde vacuo; ahora se reporta `NOT_EVALUATED` y aparece en
  `human_review_items`. No bloquea ni libera nada.

> Nota: `evidence/FASE-F/` también aloja evidencia histórica del FASE-F de otro plan
> (RC1-RC2-ENTREGA-COHERENTE-2026-08-04, «Verificación de Fixes V1-V10»). Los archivos
> de esta fase son `impacto-corpus.md` y `faseF_*.txt`.
