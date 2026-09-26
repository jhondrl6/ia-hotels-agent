# Límites, lo que no se ejecutó y qué existe solo en el árbol de trabajo

**Sesión**: conciliación final previa al cierre de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`,
2026-09-25. HEAD de partida y de cierre: `5817edd`, rama `master`, `git diff --cached` vacío al abrir.

## 1. Verificaciones realmente ejecutadas (todas offline, sin escritura fuera de lo permitido)

| Instrumento | Modo | Resultado |
|---|---|---|
| `scripts/validate_wiring.py --ignore-known` | lectura AST | `183 llamadas · gobernadas 75 (conformes 21, omisiones 0) · amparadas por excepción 0 · violaciones 0 · exit 0` → base de la rectificación R5 |
| `scripts/build_phase_briefing.py --plan <CONTEXTO> --carga - --informe -` | genera 5 packs; `-` ⇒ **no escribe artefacto** | `exit 0`, `5 packs · COMPLETO 5 · SECCION-NO-RESUELTA 0 · FUENTE-AUSENTE 0 · 37 fuentes` |
| `scripts/build_lesson_index.py` | regenera el par | `exit 0`, 339 IDs definidos |
| `scripts/build_phase_briefing.py --plan <CONTEXTO> --check` | solo lectura | `exit 0`, cinco fases «fuentes frescas» |
| `scripts/build_lesson_index.py --check` | solo lectura | `exit 0`, «Índice de lecciones fresco (339 IDs)» |
| `scripts/validate_opencode_refs.py` | **sin `--fix`** | `exit 0`, todas las referencias existen |
| `scripts/validate_plan_citations.py` | **sin `--update-baseline`** | `exit 0`, `743 citas históricas, 0 nuevas y 0 crecimientos` |
| `scripts/validate_lesson_capitalization.py` | solo lectura | `exit 0` (declara expresamente: «NO verifica pertinencia») |
| `scripts/validate_document_integration.py` | solo lectura | `exit 0`, «All checks passed» |
| `scripts/validate_governance_numbers.py --report` | **sin destino** (no escribe) | `exit 0`, `status: SIN-HALLAZGOS`, 0 hallazgos |
| `scripts/run_all_validations.py --quick` | 11 checks locales | `11/11 passed`, `exit 0` |

Un rojo **propio** apareció y se corrigió por la vía correcta: tras la primera edición del `10-` de WHATSAPP,
`validate_plan_citations.py` dio `NUEVO con citas numericas (1)` porque esta sesión escribió una referencia
`archivo.md:52`. **No** se tocó el baseline (`--update-baseline`): se re-escribió la cita **por símbolo y
sección**, y el gate volvió a `0 nuevas y 0 crecimientos`.

## 2. Lo que **no** se ejecutó, con su causa

- **Ninguna suite de `pytest`.** El mandato dice «No autorizo código, tests…», así que la comprobación de
  regresión por tests queda **pendiente de quien la autorice**; la verificación de esta sesión es la tabla
  anterior. **No se afirma** que los tests estén en verde.
- **Nada de red**: ni QMind (`validate_qmind_writeback.py` ni con `--help`), ni `git fetch`, ni `ls-remote`,
  ni `run_all_validations.py` en modo completo (su `[15/15]` es remoto).
- **Ningún writer fuera del permiso**: `validate_opencode_refs.py --fix`,
  `validate_plan_citations.py --update-baseline`, `sync_versions.py` (salvo su lectura por `[3/…]` del quick),
  `log_phase_completion.py`, `doctor.py`.
- **Nada de git que mueva estado**: sin `add`, `commit`, `push`, `tag`, `stash`, `checkout`, `restore`,
  `reset`, `clean`, sin `git mv`, sin archivado.
- **Ninguna fase**: FASE-RELEASE no se abrió; A/B/C/D no se repitieron.
- **Ninguna decisión humana tomada ni atribuida**: las cinco propuestas `L-VCF-10…14` siguen pendientes
  (§B1 de `05-permisos-y-decisiones.md`); la muestra JEV sigue `BORRADOR`; la decisión del *gap* de
  interfaz sigue sin elegir ninguna de sus dos salidas.
- **Ninguna métrica inventada**: no hay tiempo activo, no hay conteo de iteraciones ni de tool calls
  reconstruido. El instrumento canónico (`find . -name "*.jsonl"`) **no se corrió** en esta sesión y por eso
  no se publica ninguna cifra de iteraciones.

## 3. Qué existe **solo en el árbol de trabajo** (no versionado)

Al cerrar esta sesión, HEAD sigue en `5817edd` y nada de lo siguiente está en un commit:

- **Toda esta conciliación**: las ediciones de la orden, de los cinco documentos de CONTEXTO tocados, del
  `10-` de WHATSAPP, del README y prompt B de JEV, y los **10 archivos de este expediente**.
- **El producto de FASE-D**: `scripts/build_phase_briefing.py` (sin rastrear), los 5 packs de
  `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, sus tests
  (`tests/quality_gates/phase_briefing/`) y todo su expediente de evidencia.
- **Los documentos de cierre de FASE-C** y el par del índice regenerado (las *rutas de código* de FASE-C sí
  entraron en `5817edd`; su cierre documental, no).
- **El trabajo ajeno preexistente**, conservado sin tocar: el bloque B (`.agents/**`, `AGENTS.md`,
  `docs/**`, `scripts/**`, `tests/**`), el bloque C documental, y las 18 líneas ajenas de
  `EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md` (`git diff --numstat` sigue `18 0`).

**Prueba de la frontera** (`12-huellas-post.txt` §G): el conjunto de rutas sucias `git status --porcelain`
de cierre es **idéntico** al de apertura (`00-arbol-inicial.txt`) — no se añadió ni desapareció ninguna —, y
`git status --porcelain evidence/ | grep '^ M'` está **vacío**: ninguna evidencia cerrada fue modificada por
esta sesión.

## 4. Consecuencia para el cierre de la orden

La orden queda **abierta y en «listo para revisión»**, con su criterio de cierre escrito en su §6. Cerrarla
ahora afirmaría tres cosas que no son: que los cuatro planes terminaron, que hubo calidad semántica medida
(AC15 `NO-EJERCITADO`, D6 dormida) y que la evidencia versionada acompaña a la ejecución (ver §3).
