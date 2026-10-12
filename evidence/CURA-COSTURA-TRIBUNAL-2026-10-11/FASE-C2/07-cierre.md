# Cierre de FASE-C2 (2026-10-12) — los cinco cortes, declarados sin commit

## Corte declarado

| Corte | Estado |
|-------|--------|
| Implementación terminada | ✅ T1 (fila 2 sin `is_ok`, fila 3 intacta) + T2 (la acción nombra el hallazgo) + T3 (acta generada leída en JSON y MD) |
| Verificación terminada | ✅ tribunal + AC20: **331 passed / 9 skipped / 0 failed**; `--quick` **13/13**; índice de lecciones **fresco (385 IDs)**; `wiring_report --check` conforme (digest `2d837fbb8c48`) |
| Cierre documental | ✅ `09` §B/§D/§E · `10-analisis` Resumen + fila 17 de la matriz + `DEC-C2` + cierre de la escalada en Seguimientos + `L-CST-3`/`L-CST-5` con su «Real FASE-C2» · README y `dependencias-fases` en ✅ · `log_phase_completion.py --fase FASE-C2` ejecutado (`REGISTRY.md:12356`) |
| Listo para revisión | ✅ este archivo |
| Espera de autorización | ⏸ **sin `git commit`**: requiere autorización explícita y pathspec (ver rutas abajo) |

## Delta R2.3 (verificado restando)

`grep -rE "^\s*def test_" tests --include=*.py | wc -l` = **5321** (árbol de trabajo).
`git grep -c -E "^\s*def test_" HEAD -- tests` sumado = **5309** (`cea999a`, sin tocar el árbol).
Delta **+12** funciones; 12 funciones = **17** tests recolectados (dos parametrizaciones de 3 y una de 2).

## Lo que quedó intacto (restricciones del prompt)

`ReviewerStatus` (enum y `blocks_approval`), `bloque_extraccion`, `_STATUS_LABELS`, el knob
`GATE_BLOCKING_ENABLED`, `T1_CERTIFIABLE_CLAUSES`, la fila 3 (`verified_return_for_tests` conserva su
`is_ok`), `honesty_reviewer.py`, `alignment_reviewer.py`, `publication_gates.py`, `main.py` (`S-CST-1`).
En `judge.py` **solo** cambió el docstring de la matriz.

## Hallazgos declarados

1. **El prompt abría sobre un tip que ya no existía.** Su línea de dependencias fija `6494939`; medido
   `cea999a` (el commit que corrigió esa misma línea del prompt), árbol limpio y paridad `0 0`.
   `git diff --name-only 6494939..HEAD` lista un solo archivo: el propio prompt. No bloqueante.
2. **El blast radius heredado era 4 líneas; son 3 con aserción** (`test_fase_0_ac20:269` es prosa del
   docstring) y el **re-anclaje esperado «0–2» se midió en 0**. Publicado en `pre-imagen.md` (L-CST-3).
3. **El post-ejecución item 5 estaba vencido.** Pide «filas L-CST-3 y L-CST-5 con su *Real FASE-C2*» en
   `00-lecciones-capitalizadas.md` §2, pero ese §2 solo espeja lecciones **de planes anteriores**
   (L-T4A.\*, L-VERIFY.4…); las celdas de `L-CST-1..5` viven en `10-analisis` → *Lecciones nuevas de este
   plan* (líneas 73 y 76) y desde ahí las lee `build_lesson_index.py`. Se escribió ahí; el enunciado del
   prompt no se reescribió (es historial de la fase).
4. **Un control mío estaba mal fabricado y el rojo lo dijo.** La primera versión del control
   WARNING-only usaba `tier=None` para evitar el CRITICAL; al no escribir `financial_scenarios_*.json`,
   Bot 4 emitió `MISSING_SCENARIO` (**CRITICAL**) y el control certificaba otra cosa. El guard
   `assert all(severity != CRITICAL)` dentro del test lo cortó. La vía definitiva: un payload
   WARNING-only escrito a mano (el corpus no produce ese insumo) + un control real sin hallazgos, y la
   recomendación del primero reproduce la regla del propio revisor (`_compute_verdict`: WARNING sin
   CRITICAL → `DEVOLVER-PRUEBAS`), declarado en el docstring.
5. **Presupuesto R2.1 excedido:** ~45 tool calls contra ~35 presupuestados (≈29 %). Lo consumieron el
   hallazgo 4 (re-hacer el control), la localización real de las celdas `L-CST-*` y los derivados
   (`wiring_report`, índice de lecciones).
6. **`briefing/` del plan sigue ausente** (`PACK-AUSENTE` para las seis fases al `--check`). No lo
   produjo esta fase: `git ls-tree -r HEAD -- .opencode/plans/CURA-COSTURA-TRIBUNAL-2026-10-11/briefing`
   está vacío, y el check de packs del árbol commiteado sigue en 5/5. No se generaron: no es mandato del
   plan y tocar ese derivado cambiaría el conteo que verifica `verify_packs_in_committed_tree.py`.

## Rutas que cubre el commit de esta fase (pathspec, pendiente de autorización)

Modificadas: `modules/quality_gates/tribunal/outcome.py` · `modules/quality_gates/tribunal/judge.py` ·
`.opencode/wiring_report.json` · `.opencode/lecciones_index.json` ·
`.opencode/plans/CURA-COSTURA-TRIBUNAL-2026-10-11/{README,dependencias-fases,09-documentacion-post-proyecto,10-analisis-post-implementacion}.md` ·
`docs/contributing/REGISTRY.md` · `docs/contributing/.last_doc_phase.json` (ensuciada por el escritor, va
en el mismo pathspec).
Nuevas: `tests/quality_gates/tribunal/test_fase_c2_ac19_critical_bloquea_sin_is_ok.py` ·
`evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-C2/` (**17 archivos**, medido con
`find evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-C2 -type f | wc -l`; cuenta 16 más este propio archivo,
escrito después de esa medición).

`DOMAIN_PRIMER.md` regenerado (`doctor.py --regenerate-domain-primer`, 211 archivos / 396 clases): **no
aparece en `git status`**, es decir la proyección quedó byte-idéntica — esta fase no añadió módulos ni
clases, así que su aporte al primer es nulo y eso se declara en lugar de afirmar un cambio.

## Aporte durable de `CONTEXT-*.md`

**Ninguno**: esta sesión no escribió ningún `CONTEXT-*.md`, así que no hay pregunta de aporte durable
(item 9 del post-ejecución) que responder.

## Addendum (2026-10-12, segunda pasada de esta misma sesión)

La tabla de arriba quedó **vencida por su propia tanda**: registra el corte declarado («espera de
autorización, sin commit») y la autorización llegó después con la letra **«Git Commit + L3 + Push»**. No se
reescribe lo estampado; se estampa al lado, con lo medido:

- `git commit` por pathspec sobre las 12 rutas de arriba → **`fa4c93e`**, padre `cea999a`, **28 archivos**,
  1217 inserciones / 28 borrados. Antes de stagear: `SIN_ETAPAR=0`, `ETAPADO=28` (las dos rutas nuevas
  explotaron a 17 archivos de evidencia + 1 test).
- Hook pre-commit: **«All checks PASSED - Commit allowed»**, los 8 checks, ninguno saltado.
- La cifra publicada se reprodujo **en el árbol del commit**: `git grep -c -E "^\s*def test_" HEAD -- tests`
  = **5321**; y `git status --porcelain` quedó en `SUCIOS=0`.
- Las cuatro notas de sello que este addendum arrastra (`README`, `dependencias-fases`, `06-checklist` y
  `10-analisis`, más el encabezado de este último) viajaron en un commit **posterior** de la misma tanda: el
  sha de ese commit de sellos no puede estamparse a sí mismo en esta nota, y **el tip publicado es el que
  imprime `git ls-remote` al leerla**; la L3 de la tanda se corre sobre el último commit del rango y su
  cobertura se enuncia con ese rango, nunca como «tanda limpia».
