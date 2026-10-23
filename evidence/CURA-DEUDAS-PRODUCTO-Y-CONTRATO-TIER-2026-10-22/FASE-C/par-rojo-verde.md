# Par rojo/verde — mutation check AC2 (FASE-C)

**Símbolo real del guard (R2.8)**: `TribunalJudge._compute_verdict` (valor de `VERDICT_CONDITIONAL`) y la clave `conditional_reason` del `acta_revision.json` que escribe `ActaWriter` real.

| Paso | Mutación | Resultado | Crudo |
|------|----------|-----------|-------|
| 1 | Árbol real (sin mutación) | **VERDE** — 349 passed, 9 skipped | `01-verde-suite-contrato.txt` |
| 2 | **M1**: restaurar el literal viejo en `VERDICT_CONDITIONAL = "APROBADO-CONDICIONAL-PENDING-ONBOARDING"` | **ROJO** — 8 failed (6 `test_conditional_reason` + `test_acta_json_serialization` + matriz multi-hotel) sobre una selección de 16 tests | `02-rojo-mutante-m1-literal-viejo.txt` |
| 3 | Restauración de M1 + **M2**: `return VERDICT_CONDITIONAL, None` en las dos salidas condicionales de `_compute_verdict` (causa eliminada) | **ROJO** — 6 failed (los 6 tests que leen `conditional_reason` del JSON real) sobre la selección de 7 tests de `test_conditional_reason.py` | `03-rojo-mutante-m2-causa-eliminada.txt` |
| 4 | Restauración completa (mutantes revertidos) | **VERDE** — 349 passed, 9 skipped | `04-verde-tras-restaurar.txt` |

**Poblaciones**: el verde del paso 1 usa la selección de 349 tests; los rojos usan subconjuntos (16 y 7) **reconstruidos de los crudos 02/03** y declarados en `baseline-pre-post.md` §Poblaciones de los rojos. No es un par like-for-like: los rojos prueban el diente sobre la superficie que lee el literal, no sobre las 349.

**Restauración verificada**: el paso 4 corre la misma suite del paso 1 con el mismo resultado; los `patch` de mutación y reversión quedan en la transcripción de la sesión.

**Qué certifica cada rojo**:
- M1 («restaurar el literal viejo» → grep/test en rojo): el veredicto serializado vuelve al nombre largo y el acta queda contradicha por el contrato AC2. El grep de población lo detectaría, pero **no se midió bajo M1** (no hay crudo): el diente se certifica por el rojo de los tests (crudo 02).
- M2 («eliminar la causa» → test en rojo): el acta sigue publicando `verdict` pero pierde `conditional_reason`; los protocolos sintéticos dejan de distinguir las tres causas.

**Lo que el par NO certifica** (L-R.4): no hay guard automático que impida re-introducir el literal fuera de esta suite (el barrido grep es manual y está declarado en `baseline-pre-post.md`); no se ejercitó `v4complete` (fuera de alcance de FASE-C).
