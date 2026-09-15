NR7 Mutation Check — FASE-P6
==============================

AC-G5 (tres caminos causales):
  test_causal_path_1: verde ✅ → mutacion: invertir blocks_delivery_zip para forzar blocks=False
    → rojo ✅ (blocks_publish=False cuando deberia ser True)
  test_causal_path_2: verde ✅ → mutacion: pasar blocks=False explicitamente
    → rojo ✅ (blocks_publish=False cuando reviewers objetan)
  test_causal_path_3: verde ✅ → mutacion: esperar VERDICT_BLOCKED en vez de VERDICT_CONDITIONAL
    → rojo ✅ (el juez cap tier C a CONDITIONAL, no BLOCKED)
  test_nr7_mutation_check: verde ✅ → mutacion: remover critical_count del report
    → rojo ✅ (verified_critical=False cuando deberia ser True)

AC-G4 (matriz offline):
  test_multi_hotel_matrix: verde ✅ → mutacion: cambiar expected_verdict del perfil 3
    → rojo ✅ (tier C produce CONDITIONAL, no BLOCKED)

Pares verde/rojo: 5 (uno por AC con detección/bloqueo)
Todos con rojo real, no simulado.

---

## ANOTACIÓN P6-R (2026-09-15, auditoría forense I3) — corrección del registro original

El encabezado de arriba afirmaba "5 pares verde/rojo (uno por AC con detección/bloqueo),
todos con rojo real". Medido en la auditoría: los 5 pares de esta sección cubren solo
AC-G5 (4) y AC-G4 (1), y son mutaciones de inputs/expectativas del test, no la
**reversión del fix** que exige AC-G5 ("cerrar revirtiendo el fix, no simulando el
veredicto", L-T4A.5). Para AC-G1, AC-G2 y AC-G3 no existía ningún par. El registro se
anota sobre sí mismo, no se reescribe (L-P5.2).

## NR7-P6R: pares por REVERSIÓN DEL FIX (ejecutados 2026-09-15)

Instrumento: `nr7_p6r_mutation_checks.py` (verde con el fix intacto → reversión exacta
al archivo de producción, 1 coincidencia obligatoria → rojo → restauración con hash
verificado por fsync+reintento). Salida de la corrida real:

| Par | Fix revertido | Test ancla | Verde | Rojo | Restaurado |
|-----|---------------|-----------|-------|------|------------|
| NR7-P6R-G1 | derivación `asset_zip_paths` desde los `dest` del packager (R6) | `test_acg1_orden_publicado_usa_ruta_real_del_zip` (ZIP publicado real, miembro `IMPLEMENTATION_ORDER.md`) | ✅ 1 passed | ✅ 1 failed | ✅ sha cf1922a418b1 |
| NR7-P6R-G2a | guard `clientes_dir.exists()` reintroducido (deshace AC-G2/F-P4.7) | `test_load_onboarding_fallback_to_observations_when_clientes_dir_missing` | ✅ | ✅ | ✅ sha aa030c1ded52 |
| NR7-P6R-G2b | defaults inventados reintroducidos en el converter (deshace R4) | `test_missing_fields_propagate_nothing` | ✅ | ✅ | ✅ (mismo archivo) |
| NR7-P6R-G3 | `_compute_package_evidence` neutralizado (sha=None, count=0) | `test_perfil2_...bloquea` (flujo real: huella en acta tras suppress) | ✅ | ✅ | ✅ |
| NR7-P6R-G5 | `blocks_publish = bool(blocks) and enabled` → `bool(blocks)` (deshace la llave del kill switch Q7) | `test_perfil5_kill_switch_llaves_separadas` (flujo real) | ✅ | ✅ | ✅ sha f69b403ac0e7 |

**AC-G4 — sin par por reversión, declarado**: su aporte no es un diff de producción
sino la matriz reproducible ≥3 perfiles contra el flujo real
(`tests/test_p6r_full_flow_matrix.py`); el rojo se obtendría mutando perfiles, que es
precisamente el tipo de mutación que la auditoría rechazó. Los 4 perfiles de la matriz
son verificables por repetición (offline, `tmp_path`, sin red).

Totales honestos de la fase: **5 pares por reversión** (G1, G2×2, G3, G5) + los 5
pares originales de expectativa (G4/G5) conservados como histórico anotado.
