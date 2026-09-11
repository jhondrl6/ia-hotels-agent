# Rectificación NR1 — FASE-T4-B (2026-09-11)

> **Propósito**: registrar qué se midió mal en el criterio NR1 y por qué, **sin borrar el registro original**. Los archivos `tests_baseline_pre.txt` y `tests_baseline_post.txt` quedan intactos: destruir evidencia no es corregir evidencia.
> **Disparador**: auditoría forense de sola lectura del 2026-09-11, hallazgo D3 (ALTO), tarea R4 del dossier `.opencode/context/CONTEXT-AUDITORIA-FORENSE-FASE-T4B-REMEDIACION-2026-09-11.md`.

---

## 1. Qué se publicó

`evidencia-final.md` declaraba NR1 con este par y esta explicación:

| Elemento | Publicado por la fase |
|---|---|
| `tests_baseline_pre.txt` | `8 failed, 3993 passed, 32 skipped, 4 xfailed` (suma 4.037) |
| `tests_baseline_post.txt` | `3 failed, 3998 passed, 32 skipped, 4 xfailed` (suma 4.037) |
| Delta | "+5 tests (no +7 como se esperaba)" |
| Verificación | "3998 = 3993 pre + 7 nuevos − 2 que dejaron de fallar" |
| Causalidad | "5 tests que fallaban pre-T4-B ahora pasan post-T4-B … la implementación de `HonestyReviewer` corrigió indirectamente algún comportamiento" |

## 2. Por qué es incorrecto

1. **Sumas idénticas**: pre y post suman **4.037** los dos. Si la fase agregó 7 tests, la suma del post debe exceder a la del pre en 7. Una resta que da 0 es la firma de un baseline contaminado.
2. **El "pre" ya contenía los tests de la fase**: medido hoy, `pytest tests/ --collect-only -q` da **4.036** y el mismo comando con `--ignore=tests/quality_gates/tribunal/test_honesty_reviewer.py` da **4.029**. Diferencia = 7. Por tanto el snapshot tomado "antes" se tomó **después** de crear el archivo de tests, con cinco de sus siete tests en rojo (de ahí los `8 failed` del pre: 3 preexistentes + 5 rojos del TDD).
3. **La aritmética publicada es imposible**: `3993 + 7 − 2 = 3998` cuadra como álgebra pero el relato se contradice en el mismo documento ("−2" vs "5 tests que fallaban pre-T4-B ahora pasan").
4. **La causalidad es falsa**: no hubo ningún efecto indirecto de `HonestyReviewer` sobre otros tests. Los cinco fallos que desaparecen son cinco de sus **propios** tests, que pasaron de rojo a verde cuando el fix del regex de sobre-presentación (L-T4B.2) se aplicó dentro de la misma fase.

## 3. Cuál es la realidad

El NR1 **sí se cumple**. Baseline pre-fase real medido el 2026-09-11 (`tests_baseline_pre_T4B_fase_real.txt`, suite completa excluyendo el archivo de tests de la fase y los tres de su remediación):

```
3 failed, 3991 passed, 32 skipped, 4 xfailed
```

| Comprobación | Resultado |
|---|---|
| `passed_post = passed_pre + tests_nuevos` | `3998 = 3991 + 7` ✅ sin términos de corrección ad-hoc |
| Suma pre vs post | `4.037 − 4.030 = 7` = `tests_nuevos` ✅ |
| Skipped (NR2) | `32 → 32`, delta 0 ✅ |
| Fallos | los 3 preexistentes registrados en `aba517a`, cancelan en ambos lados ✅ |

## 4. Regla operativa fijada

Para toda fase futura:

1. El snapshot `pre` se toma **antes de crear el archivo de tests** de la fase.
2. Se verifica `passed_post = passed_pre + tests_nuevos`.
3. Se verifica que la suma `failed+passed+skipped+xfailed` **difiere** entre pre y post en exactamente `tests_nuevos`. Si la resta da 0, el baseline está contaminado y **NR1 no puede declararse**.
4. Endurecimiento propuesto para el workflow `phased_project_executor.md` (fuera del alcance de esta fase → seguimiento en `10-analisis` §Seguimientos, a aplicar en FASE-VERIFY/RELEASE).

## 5. Archivos

| Archivo | Estado |
|---|---|
| `tests_baseline_pre.txt`, `tests_baseline_post.txt` | Conservados íntegros (registro original de la fase) |
| `tests_baseline_pre_T4B_fase_real.txt` | **Nuevo** — baseline pre-fase medido |
| `tests_baseline_post_T4B_remediacion.txt` | **Nuevo** — suite completa tras la remediación (+22 tests) |
| `evidencia-final.md` §NR1 | Corregido, apuntando a esta nota |
