# FASE-C — Ítem C: veredicto condicional con causa estructurada

**ID**: FASE-C · **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
**Objetivo**: que el veredicto condicional distinga **por qué** es condicional (`ANALYTICS_CEILING`, `ONBOARDING_INCOMPLETE`, `UNCERTIFIABLE_CLAUSES`) sin codificar la causa en un nombre largo; `P6.5`/`D21` quedan fuera y no se tocan.
**Dependencias**: FASE-B ✅.
**Complejidad técnica**: MEDIA · **Duración estimada**: 2-3 horas
**Modo de ejecución**: **DIRECTO** (decisión de contrato cross-module; no delegable).

## Contexto

`_compute_verdict` devuelve `VERDICT_CONDITIONAL` en dos lugares: por primer piso (`first_floor["applied"]`) y por tier A con cláusulas no certificables o revisores no leídos. Un nombre con dos estados cubriría solo la primera causa y dejaría la segunda sin nombre honesto. La solución estable es `APROBADO-CONDICIONAL` + `conditional_reason` en el acta. Además, el juez no recibe un indicador de onboarding completo: `has_onboarding` existe en `main.py`, pero no viaja al tribunal. **Decisión del Operador: `D21`/`P6.5` no se absorben; la fila `P6.5` y `T1_CERTIFIABLE_CLAUSES` no se tocan.**

Superficie medida del literal viejo: **8 ocurrencias en `.py`** (constante en `judge.py`, etiqueta en `acta_writer.py`, 6 tests). La población “viva” para AC2 es esa; no se incluyen `VERSION.yaml`, `CHANGELOG.md`, `context/`, `Archives/`, `evidence/`, `qmind-writeback/` ni `temp/`, que son históricos o scratch.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A | ✅ |
| FASE-B | ✅ |

### Base Técnica Disponible
- `modules/quality_gates/tribunal/judge.py` (`VERDICT_CONDITIONAL`, `_compute_verdict`, `FIRST_FLOOR_TIERS`)
- `modules/quality_gates/tribunal/acta_writer.py` (etiqueta humana del veredicto)
- `modules/quality_gates/tribunal/outcome.py` (`TribunalOutcome`, serialización)
- `modules/quality_gates/tribunal/review_inputs.py` (manifiesto de revisión)
- `main.py` (`has_onboarding`, captura de `review_inputs`, `TribunalJudge.evaluate()`)
- Tests con el literal: `test_ac_g4_g5_multi_hotel_matrix.py`, `test_fase_0_ac20_evidencia_veredicto.py`, `tests/quality_gates/tribunal/*`

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-P3A.2 | La clave correcta la dicta el parser | El nombre y la causa se validan contra el acta serializada, no contra el diccionario en memoria |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | El test lee el JSON del writer real y provoca las tres causas |
| L-CST-7 | Curar una cláusula no cura a sus hermanas | `P6.5` no se toca; la cura se limita al veredicto y su causa |
| L-R.4 | Regla sin verificador solo publicable si lo declara | El grep del literal viejo se declara con su población |

## Tareas

### Tarea 1: Contrato del veredicto y de la causa
**Objetivo**: definir `APROBADO-CONDICIONAL` como valor estable y `conditional_reason` con tres valores: `ANALYTICS_CEILING` (tier B+ con onboarding verificado y sin analytics), `ONBOARDING_INCOMPLETE` (tier B/C sin onboarding verificado) y `UNCERTIFIABLE_CLAUSES` (tier A con cláusulas no certificables o revisores no leídos).
**Archivos afectados**: `modules/quality_gates/tribunal/judge.py`, `modules/quality_gates/tribunal/outcome.py`, `modules/quality_gates/tribunal/acta_writer.py`.
**Criterios de aceptación**:
- [ ] `_compute_verdict` devuelve el veredicto y la causa; no hay dos nombres largos que oculten la tercera causa
- [ ] `BLOCKING_VERDICTS` no incluye `APROBADO-CONDICIONAL`; el paquete sigue publicando
- [ ] `P6.5` y `T1_CERTIFIABLE_CLAUSES` no cambian

### Tarea 2: Transportar `has_onboarding` al tribunal
**Objetivo**: que la causa `ANALYTICS_CEILING` vs `ONBOARDING_INCOMPLETE` se decida con un dato real, no inferida solo de `evidence_tier`.
**Archivos afectados**: `main.py`, `modules/quality_gates/tribunal/review_inputs.py`.
**Criterios de aceptación**:
- [ ] `has_onboarding` viaja en el manifiesto de revisión (o en el contrato equivalente) y el juez lo lee
- [ ] Un hotel con onboarding verificado y sin analytics produce `ANALYTICS_CEILING`
- [ ] Un hotel sin onboarding produce `ONBOARDING_INCOMPLETE`

### Tarea 3: Renombrar la superficie viva
**Objetivo**: actualizar la constante, la etiqueta humana y los 6 tests; el literal viejo desaparece de la población de código/tests.
**Criterios de aceptación**:
- [ ] Grep del literal viejo: 0 en `modules/`, `tests/` y `main.py` (crudo en evidencia)
- [ ] La etiqueta humana del acta no dice “Pendiente de onboarding” para el caso de techo de analytics
- [ ] Los históricos (`VERSION.yaml`, `context/`, `Archives/`, `evidence/`, `qmind-writeback/`, `temp/`) se declaran fuera de la población, no se editan

### Tarea 4: Tests de las tres causas (AC2)
**Objetivo**: acta serializada con el veredicto y la causa legibles; mutation check: restaurar el literal viejo o eliminar la causa → grep/test en rojo.
**Criterios de aceptación**:
- [ ] Test de serialización lee el JSON del writer real (R2.4)
- [ ] Las tres causas se provocan con protocolos sintéticos y se leen en el acta
- [ ] Par rojo/verde en `evidence/…/FASE-C/`

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| acta con veredicto y causa | `tests/quality_gates/tribunal/test_acta_serialization.py` (o nuevo) | `verdict == APROBADO-CONDICIONAL`; `conditional_reason` legible |
| tres causas | `tests/quality_gates/tribunal/` (nuevo o extensión) | `ANALYTICS_CEILING`, `ONBOARDING_INCOMPLETE`, `UNCERTIFIABLE_CLAUSES` |
| grep del literal viejo | barrido de fase | 0 en la población declarada |

**Comando de validación**: `./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal -q` + `run_all_validations.py --quick`. Par pre/post (R2.3).

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-C ✅.
2. `README.md`: progreso por referencia a `09` §D.
3. `09-documentacion-post-proyecto.md`: B/D/E de la fase.
4. `10-analisis-post-implementacion.md`: decisión del contrato, fila, lecciones y seguimientos (`D21`/`P6.5` fuera).
5. `00-lecciones-capitalizadas.md`: anotar las lecciones citadas.
6. `evidence/…/FASE-C/`: pares rojo/verde, grep con población y `baseline-pre-post.md`.

Registro:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-C --fecha <fecha-de-cierre-de-esta-fase> \
    --desc "Ítem C: APROBADO-CONDICIONAL + conditional_reason (3 causas) y has_onboarding; P6.5 intacta (AC2)" \
    --archivos-mod "<rutas>" --tests "N" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] `conditional_reason` con las tres causas y `has_onboarding` transportado
- [ ] 0 literales viejos vivos en la población declarada; acta legible
- [ ] `P6.5`/`T1_CERTIFIABLE_CLAUSES` intactas
- [ ] Mutation check con par rojo/verde; `--quick` verde; cinco cortes sin commit
- [ ] `dependencias-fases.md` actualizado; lecciones registradas; evidencia preservada

## Restricciones

- Presupuesto: tope **60 tool-use**; corte «listo para revisión»; instrumento legado/no comparable si no aplica.
- **No tocar** `P6.5`, `T1_CERTIFIABLE_CLAUSES`, la evaluabilidad de `P6.2`, archivos congelados, plantillas (FASE-B) ni umbrales (FASE-F). Sin `v4complete`. Citas por símbolos (R2.2).

## Prompt de Ejecución

```bash
Actúa como especialista en el repo iah-cli. Ejecuta únicamente FASE-C del plan .opencode/plans/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22.
Lee 05-prompt-inicio-sesion-fase-C.md, 01-plan-maestro.md §1, §2, §4 y §5, 00-lecciones-capitalizadas.md §2, dependencias-fases.md y workflow canónico.
OBJETIVO: veredicto APROBADO-CONDICIONAL con conditional_reason de tres causas y has_onboarding; P6.5 intacta.
TAREAS: 1 contrato del veredicto/causa, 2 transportar has_onboarding, 3 renombrar superficie viva, 4 tests de las tres causas.
CRITERIOS: AC2 (acta legible, 0 literal viejo en la población, P6.5 intacta); par rojo/verde en evidence.
VALIDACIONES: pytest tribunal; --quick; log_phase_completion.py al cierre.
```
