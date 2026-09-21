# Checklist de implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Leyenda de estados** (R2.4, no negociable): `PENDIENTE` · `VERIFICADO OFFLINE` (test verde **con
su mutation check**) · `⚠️ PARCIAL` (falta el rojo, falta la clave en el artefacto, o solo cubre un
estado) · `NO-EJERCITADO` (el camino no se ejercitó; con el motivo) · `FUERA DE ALCANCE`.
**No existe `SUPERADO EN E2E` en este plan**: no hay corrida (§5 del maestro) y no hay FASE-VERIFY.

## Matriz de ACs

| AC | Fase | Enunciado corto | Artefacto donde se lee | Estado |
|---|---|---|---|---|
| AC1 | A | reproduce **las cuatro aserciones normativas vivas** A1–A4 y ninguna otra, con la regla de población de A8 aplicada | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]` (con `occurrences[]`) | PENDIENTE |
| AC2 | A | publica denominador: población, **las tres clases y las cuatro familias no cubiertas** | ídem → `coverage_basis`, `historical_excluded[]` | PENDIENTE |
| AC3 | A | tres estados sin colapsar | ídem → `status` + 3 tests | PENDIENTE |
| AC4 | A | mutation check **por aserción** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` (rojo + verde) | PENDIENTE |
| AC5 | A | conteo del quick y del hook como delta 0 | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md` | PENDIENTE |
| AC6 | B | aislamiento de imports | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` (conteo + población) | PENDIENTE |
| AC7 | B | proveedor no configurado no decide | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` → `provider_status` | PENDIENTE |
| AC8 | B | contract test de forma con proveedor falso | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` | PENDIENTE |
| AC9 | B | añadir un 2º proveedor cuesta **un** archivo | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` → `files_changed_to_add_provider` | PENDIENTE |
| AC10 | C | el triaje **no elimina** fila anclada alguna | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` → `removed: []` | PENDIENTE |
| AC11 | C | índice ausente/vencido ≠ sin candidatos | ídem → `index_status` | PENDIENTE |
| AC12 | C | umbral con valor, base y acción por debajo | ídem → `threshold` | PENDIENTE |
| AC13 | C | ≥1 test contra corpus real, skip declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` | PENDIENTE |
| AC14 | C | mutation check del guard de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` | PENDIENTE |
| AC15 | C | denominador, términos, ceros **y aceptabilidad** (dispara D6) | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` | PENDIENTE |
| AC16 | A,B,C,D | quick en 11 y hook en 7, inalterados en todo el plan | los cuatro `baseline-pre-post.md` | PENDIENTE |
| AC17 | A,B,C,D | `.agents/` intocado; familias no cubiertas declaradas | `coverage.json` → `families_not_covered[]` + `git status .agents/` | PENDIENTE |
| AC18 | A,B,C,D | capitalización, citas e índice verdes en el mismo commit | salida de los tres verificadores | PENDIENTE |
| AC19 | D | un pack por fase, declarando qué **no** incluye | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` | PENDIENTE |
| AC20 | D | delta de carga de lectura con el **mismo comando** en ambos lados | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` | PENDIENTE |
| AC21 | D | proveniencia con HEAD y sha por fuente; `--check` vence | ídem → `provenance` | PENDIENTE |
| AC22 | D | prohibido emitir un pack más corto en silencio | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}` | PENDIENTE |
| AC23 | D | mutation check del guard de truncamiento | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` | PENDIENTE |

## FASE-A — `validate_governance_numbers.py`

- [ ] Script standalone, invocable sin tocar `run_all_validations.py`.
- [ ] A1–A4 reproducidas; cualquier hallazgo adicional se explica o se corrige el patrón.
- [ ] **Regla de población aplicada y publicada (A8)**: viva / histórica congelada / vigente-correcta,
  con los conteos de cada clase y la frase del workflow (`v2.24.0`) que ampara la exclusión.
- [ ] **Un hallazgo por aserción, con sus `occurrences[]`**: A1 en dos sitios sigue siendo un hallazgo.
- [ ] `coverage_basis` con población, exenciones y `families_not_covered` — **las cuatro medidas**:
  prosa sin patrón, conteos fuera de los documentos de gobierno (`AGENTS.md`, `docs/GUIA_TECNICA.md`,
  `docs/contributing/REGISTRY.md`), pins de conteo en `tests/`, y fuentes dinámicas no-etiqueta.
- [ ] Tres tests de estado, cada uno cubriendo **un** estado.
- [ ] `mutation/` con rojo y verde por aserción, **afirmando el `assertion_id` del mutante (L-V2.1)**.
- [ ] «Quién afirma el 11 y el 7» medido **también en `tests/`** (L-V2.3).
- [ ] Par pre/post con la resta comprobada, delta 0.
- [ ] `log_phase_completion.py --fase FASE-A` ejecutado; índice regenerado en el mismo commit.

## FASE-B — `decision_client.py`

- [ ] Un solo archivo importa SDK/adapter; verificado sobre el árbol real con población.
- [ ] `provider_status` con los tres estados; ningún `except` produce una decisión.
- [ ] Contract test que se pone rojo si cambia la forma del proveedor falso.
- [ ] Versión de modelo pineada y declarada; sin literales del proveedor pineados.
- [ ] `costura.json` con `files_changed_to_add_provider == 1`, o la explicación de por qué es mayor.
- [ ] **Cero llamadas de red** y cero credenciales en el árbol, la evidencia y los logs.
- [ ] Ninguna comparación de proveedores intentada: es D7 y se dice en el cierre.

## FASE-C — `triage_lesson_relevance.py`

- [ ] `removed: []` afirmado por un test sobre el §2 real de este plan.
- [ ] `index_status` distingue presente / `AUSENTE` (ruta) / `VENCIDO` (check del hook que lo detecta).
- [ ] `threshold` publicado con valor, base y `action_below`; ningún camino auto-filtra.
- [ ] Test contra planes reales de `Archives/` con `skipif` visible y su corrida declarada.
- [ ] Mutation check sobre el símbolo real del guard de no-filtrado.
- [ ] `coverage.json` con los términos usados y sus conteos, **incluidos los ceros**.
- [ ] `acceptance` publicado con muestra y método: es el número que decide si **D6** se activa.
- [ ] El triaje aplicado sobre `00-lecciones-capitalizadas.md` de este propio plan y su §4 actualizado.

## FASE-D — `build_phase_briefing.py`

- [ ] `briefing/FASE-X.md` generado para **todas** las fases del plan, dentro del directorio del plan.
- [ ] `no_incluye[]` y `lectura_aparte_obligatoria[]` no vacíos; el workflow canónico figura ahí.
- [ ] `carga.json` con `method` literal, bytes exactos y divisor de tokens declarado.
- [ ] Par pre/post de **checks** (delta 0) y par pre/post de **carga de lectura** (AC20), con la resta.
- [ ] Delta explicado por fase; cero o negativo declarado, no escondido.
- [ ] `--check` falla contra una fuente editada y pasa al revertir (demostrado en disco).
- [ ] Tres estados de resolución de secciones, un test por estado.
- [ ] Test contra una fase de un plan **archivado real**, con `skipif` y su corrida declarada.
- [ ] `git status .agents/` vacío al cerrar.
- [ ] Dependencias D6 re-evaluada con el `acceptance` de FASE-C y actualizada con la decisión.

## FASE-RELEASE

- [ ] Q7 (QMind) re-ejecutada o su limitación re-fechada en §4 y en `dependencias-fases.md` (D8).
- [ ] Sync de versiones, CHANGELOG, `GUIA_TECNICA` y `docs/contributing/REGISTRY.md` (cuatro módulos).
- [ ] D1 presentada con coste y decisión escrita del operador (o sigue debida, con dueño).
- [ ] D2/D3/D6/D7 con estado explícito tras leer el `acceptance` de C y el `carga.json` de D.
- [ ] Orden exacto: write-back → índice → `git mv` → índice → refs → citas → quick.
- [ ] Ningún AC promocionado a ✅ sin su mutation check o su clave en el artefacto.

## Controles de cierre del plan

- [ ] `run_all_validations.py --quick` en verde con **11** checks (composición intacta).
- [ ] `validate_governance_numbers.py` en verde sobre el árbol final.
- [ ] `build_phase_briefing.py --check` en verde sobre el árbol final.
- [ ] `validate_lesson_capitalization.py` en verde sobre el `00-…` final.
- [ ] `validate_plan_citations.py` sin citas de línea en los archivos de este plan.
- [ ] `build_lesson_index.py --check` en verde **después** del archivado.
- [ ] Todos los ACs con estado alcanzable declarado, incluidos ⚠️ y `NO-EJERCITADO`.
