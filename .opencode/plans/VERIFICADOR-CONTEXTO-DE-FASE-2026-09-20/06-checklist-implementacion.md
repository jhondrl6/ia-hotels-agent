# Checklist de implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Leyenda de estados** (R2.4, no negociable): `PENDIENTE` · `VERIFICADO OFFLINE` (test verde **con
su mutation check**) · `⚠️ PARCIAL` (falta el rojo, falta la clave en el artefacto, o solo cubre un
estado) · `NO-EJERCITADO` (el camino no se ejercitó; con el motivo) · `FUERA DE ALCANCE`.
**No existe `SUPERADO EN E2E` en este plan**: no hay corrida (§5 del maestro) y no hay FASE-VERIFY.

## Matriz de ACs

| AC | Fase | Enunciado corto | Artefacto donde se lee | Estado |
|---|---|---|---|---|
| AC1 | A | reproduce **las cuatro aserciones normativas vivas** A1–A4 y ninguna otra, con la regla de población de A8 aplicada | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]` (con `occurrences[]`) | **VERIFICADO OFFLINE** 2026-09-21 |
| AC2 | A | publica denominador: población, **las tres clases y las cuatro familias no cubiertas** | ídem → `coverage_basis`, `historical_excluded[]`, `excluded[]` | **VERIFICADO OFFLINE** 2026-09-21 |
| AC3 | A | tres estados sin colapsar | ídem → `status` + 3 archivos de test (un estado cada uno) | **VERIFICADO OFFLINE** 2026-09-21 |
| AC4 | A | mutation check **por aserción** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` (verde + 6 rojos anclados por `assertion_key`) | **VERIFICADO OFFLINE** 2026-09-21 |
| AC5 | A | conteo del quick y del hook como delta 0 | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md` | **VERIFICADO OFFLINE** 2026-09-21 (quick 0, hook 0; tests +23 declarado) |
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
| AC16 | A,B,C,D | quick en 11 y hook en 7, inalterados en todo el plan | los cuatro `baseline-pre-post.md` | **A: delta 0 verificado 2026-09-21** · B/C/D pendientes |
| AC17 | A,B,C,D | `.agents/` intocado; familias no cubiertas declaradas | `evidence/…/FASE-A/informe.json` → `families_not_covered[]` + `ac17-y-presupuesto.md` + `git status --porcelain .agents/` (vacio) | **A: VERIFICADO OFFLINE 2026-09-21** · B/C/D pendientes |
| AC18 | A,B,C,D | capitalización, citas e índice verdes en el mismo commit | salida de los tres verificadores | **A: los tres verdes el 2026-09-21** (`[9/11]`, `[10/11]` en el quick 11/11 + indice regenerado) · cumplido en el mismo commit `a7564ae` |
| AC19 | D | un pack por fase, declarando qué **no** incluye | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` | PENDIENTE |
| AC20 | D | delta de carga de lectura con el **mismo comando** en ambos lados | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` | PENDIENTE |
| AC21 | D | proveniencia con HEAD y sha por fuente; `--check` vence | ídem → `provenance` | PENDIENTE |
| AC22 | D | prohibido emitir un pack más corto en silencio | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}` | PENDIENTE |
| AC23 | D | mutation check del guard de truncamiento | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` | PENDIENTE |

## FASE-A — `validate_governance_numbers.py` — **cerrada VERIFICADO OFFLINE el 2026-09-21** (AC1–AC5; y AC16/AC17/AC18 en la parte que corresponde a esta fase)

- [x] Script standalone, invocable sin tocar `run_all_validations.py`. **Verificado offline el 2026-09-21**: `--report`, `--json` y rutas inyectables (`--governance-doc`/`--source`/`--hook`) para probarlo sobre fixtures en `tmp_path`.
- [x] A1–A4 reproducidas y **cero hallazgos adicionales**: A1 `check 8` vs `9/11`, A2 `9/9` vs `10/11`, A3 `12/12` vs `15/15`, A4 `10/10` vs `10/11`; ademas 11 aserciones vigentes-correctas publicadas en `assertions_checked`.
- [x] **Regla de población aplicada y publicada (A8)**: viva-hallazgo **5 instancias en 4 aserciones** / vigente-correcta **11** / histórica congelada **8** / no resuelta **0** = **24** instancias (22 con corchete + 2 formas «check N»). Dos rutas de congelacion publicadas con su marca: `H1` (denominador de otra epoca dentro de `## Versiones`) y `H2` (clausula que narra un evento pasado). La frase del workflow que ampara la exclusion (`v2.24.0`) se copia en `historical_excluded[].authorized_by` y en `regla_de_poblacion.historical_authorizing_phrase`.
- [x] **Un hallazgo por aserción, con sus `occurrences[]`**: A1 sigue siendo **un** hallazgo con **dos** occurrences (el parrafo «Verificador mecanico» de R2.2 y la entrada v2.19.0 de `## Versiones`); demostrado tambien al inverso — un fixture con la frase escrita tres veces da 1 hallazgo con 3 occurrences.
- [x] `coverage_basis` con población, exenciones y `families_not_covered` — **las cuatro medidas en runtime**, no de oido: (i) prosa sin patron: **3** coincidencias en los documentos auditados (+1 en el template excluido: `pasa 4/4`); (ii) fuera de los documentos de gobierno: **245** instancias (`AGENTS.md` 1 —«10/10 checks», vencido—, `docs/GUIA_TECNICA.md` 107, `docs/contributing/REGISTRY.md` 137); (iii) pins en `tests/`: **4 archivos**, incluido el pin que **esta fase añadio**; (iv) fuentes dinamicas no etiqueta: **4.330** funciones en disk contra las 4.246 que publica `AGENTS.md`.
- [x] Tres archivos de estado, **cada uno cubriendo un solo estado**: `test_governance_numbers_sin_hallazgos.py`, `test_governance_numbers_ausente.py`, `test_governance_numbers_lector_fallido.py`. Nota de forma: la tabla de tests obligatorios del prompt lista **cinco** archivos y sus criterios de completitud decian «los cuatro tests pasan»; se escribieron los cinco mas el de mutantes (23 funciones, 28 casos).
- [x] `mutation/` con **verde + seis rojos** (`verde_baseline.txt`, `mutante_M-A1`, `M-A2`, `M-A3`, `M-A4`, `M-POBLACION`, `M-SUJETO`). El anclaje se afirmo **por `assertion_key`** (sujeto + afirmacion + documento), no por `assertion_id`: el primer intento con ids posicionales produjo un rojo que nombraba a otra asercion (perdia A4 al mutar el guard de A1) — eso es literalmente L-V2.1 y queda capitalizado en `10-analisis-post-implementacion.md`.
- [x] Medido con los mismos comandos en los dos lados. PRE: nada en `tests/` afirmaba el 11, y un `[5/7]` en `test_validate_plan_closure.py` afirmaba el hook. **POST: 4 coincidencias nuevas del denominador 11 creadas por esta fase** (`test_governance_numbers_reproduce_A1_A4.py`), declaradas con dueño D1/D2 en `baseline-pre-post.md` en lugar de limar la asercion.
- [x] Par `faseA_baseline_pre.txt` / `faseA_baseline_post.txt` + `baseline-pre-post.md` con la resta: quick **11→11 (0)**, hook **7→7 (0)**, poblacion A8 **22/17/2 → 22/17/2 (0)**. Y **sin** fingir delta 0 donde la fase si movio la metrica: seleccion de tests **0→23 funciones (+23)**, que es justo lo que AC5 exige publicar por separado.
- [x] `log_phase_completion.py --fase FASE-A --check-manual-docs` ejecutado y `build_lesson_index.py` regenerado el 2026-09-21. El commit se hizo con instruccion literal del operador el 2026-09-21 (`a7564ae`, 34 archivos) y **llevo el indice dentro**, como exige R2.10 y comprueba `[6/7]`.

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
