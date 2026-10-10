# Acta de FASE-B — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-09)

**HEAD al abrir (medido):** `77e64ca94158266e9ed6c95836cf04c3dc718112`, igual en `git rev-parse HEAD`,
`git rev-parse origin/master` y `git ls-remote origin refs/heads/master` (paridad 0/0).
**Quick de apertura:** `13/13`, `EXIT=0` (leido en consola, no archivado; el de cierre si, `08-quick_cierre.txt`).
**Árbol al abrir:** 13 rutas staged de otra sesión (deuda S-CIM-7: los doce `briefing/FASE-*.md` del plan padre
archivado y `evidence/REFACTOR-WHATSAPP-…/FASE-E2E/captura_stdout.txt`). **No se tocaron, no se des-stagearon, no
entran en ningún conteo ni en ningún verde de esta fase.**

## Estado de los cinco cortes

Implementación terminada (AC7 y AC8 landed en el árbol de trabajo) → verificación terminada (selección literal
`8 passed`, hermanas `18`/`36`, mutantes con su rojo, `[fechas]` en verde y en rojo) → **cierre documental**
(checklist, 09 §A/B/D/E, 10, 00 §2/§4, CHANGELOG, GUIA_TECNICA, `log_phase_completion.py`, derivados con su
escritor) → **listo para revisión** → **espera de autorización**: no hubo instrucción literal de commit en el chat,
así que el árbol queda **sin commitear** y el `git commit` se declara acción posterior y separada, no condición de
ningún corte.

## Qué se hizo, en orden

1. **Re-medición** del estado (git, quick, lectura del archivo de control, del generador curado y del blob de
   `6b02532` por `git show`, nunca reimplementando el defecto).
2. **AC7 — diagnóstico con medición, sin tocar código** (`diagnostico.md` + `01-diagnostico-crudo.txt` +
   `02-h2-crlf-del-clon.txt`). Hipótesis 1 **confirmada**: el par pineado `2020-01-02 / 2031-06-06` deja el `mtime`
   de B por encima del piso de fechas-en-nombre del corpus (2026-07-06), y como `_plan_date()` de `6b02532` alimenta
   con esa fecha el **desempate de dueño**, 7 de los 11 IDs divergentes cambian de dueño y salen `nombre` en B.
   Hipótesis 2 **descartada como causa, declarada como premisa rota** (el clon heredaba `core.autocrlf=true` del
   ámbito *system*: 438 `.md` divergiendo de su blob; y el índice curado es idéntico en árbol CRLF y LF — `sha
   ace923719d40d883…`, 0 entradas con tier/fecha/dueño distintos). Hipótesis 3 **descartada** (`98c190e` y
   `086ce65` dan la misma banda de 11 y el mismo piso).
3. **AC8 — cura con el diente intacto**: reloj derivado del corpus (`_piso_y_techo()`, `_par_de_mtimes()`, sobre el
   `_sources`/`DATE_RE` del instrumento), clon fiel por patrón S20, tres estados de abstención. La aserción
   `… == "mtime" and … == "mtime"` **no se tocó**; `REV_CONTROL_DEFECTUOSO` sigue en `6b02532` con diente en contra;
   el contrafactual del flip quedó **ejercitado**, no barrido.
4. **Dientes**: +4 funciones (4 → 8). Selección literal PRE `1 failed, 3 passed` → POST `8 passed`, `EXIT=0`, resta 4.
5. **Mutantes sobre copia aislada** (`temp/s15_mutantes_faseb.py`): M1 clamp del piso apagado → `EXIT=1` con
   `'nombre' == 'mtime'` en el control y «no queda bajo el piso del corpus» en su diente; M2 clon sin config dentro →
   `EXIT=1` con `NO-EVALUABLE` y `core.autocrlf`. sha256 del test vivo idéntico antes y después
   (`f913afb86b20c8bed78c5b985eb4979b75e79450830e6a4fb3d5f0ae68657b36`); blob de HEAD pre-cura
   `97c7af4d67694bea9d6025f2824786a7c89ce3006c7ee72f559dd6166bc349cc`.
6. **Tarea 4 — cierre con las hermanas**: `tests/test_build_lesson_index.py` 18 casos (`16` funciones por
   `grep -cE "^\s*def test_"`), `tests/test_verify_qmind_context_freshness.py` 36/36, ambas `EXIT=0` y ambas
   **intactas** (`git diff --stat` vacío sobre las dos y sobre `scripts/build_lesson_index.py`). `[fechas]` en las dos
   vías (`361/11/0`). Quick de cierre `EXIT=0`.

## FASE-C: «no aplica», con la medición que lo declara

Su regla exigía la frase «la cura está en `_plan_date`/`build()` porque <razón medida>». No se obtuvo: con el reloj
bajo el piso, el generador de `6b02532` da 11 divergentes y **los 11 son `mtime` en ambos árboles**. Escrito en
`diagnostico.md` §5, en `09` §B y en la fila 5 de `dependencias-fases.md`. El plan cierra sin AC9; AC10 (RELEASE) no
depende de C.

## Restricciones del mandato — cumplimiento medido

- `scripts/build_lesson_index.py`: **no editado** (diff vacío). No se re-ancoró `REV_CONTROL_DEFECTUOSO`, no se
  re-fijó baseline, la aserción no se convirtió en pertenencia.
- `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, workflow, hooks: **sin tocar**; no se liberó versión.
- Cero comandos `v4complete`/`v4audit`; **cero operaciones remotas** en esta fase (no hizo falta: AC7/AC8 se miden
  sobre clones locales y blobs commiteados). Cero escrituras a `.opencode/qmind-writeback/`.
- Evidencia nueva solo bajo `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-B/`; **ningún `.py` bajo
  `evidence/`** — los dos arneses y el driver de mutantes corrieron como scratch en `temp/` y se declaran
  no versionados.
- Ninguna aserción existente rebajada: las 2 líneas `assert` eliminadas están re-emitidas con la misma o mayor
  fuerza y nombradas en `baseline-pre-post.md`.

## Presupuesto (auto-reporte con unidad declarada)

**Unidad:** `tool_use` contados a mano por el agente; el instrumento canónico
(`evidence/FASE-D/measure_iterations.py`) sigue **FUERA DE SERVICIO** (R2.1: pide el transcript del cliente y su
acceso está denegado), así que este número **no es comparable** con las fases que lo usaron.
**Referencia dictada para FASE-B:** 90 `tool_use` (DA-CIM.10), al corte que la sesión tenga autorizado — aquí
«listo para revisión», sin commit.
**Consumo al cierre documental:** ≈90 (desglose aproximado, misma forma que declaró A1: ≈45 código + tests +
mutantes + arneses de diagnóstico, ≈30 lectura de estado y corridas, ≈15 cierre documental). **Sin exceso** que
declare checkpoint, aunque queda al filo de la referencia: la fase consumió una tanda de re-medición del mandato y
dos arneses de diagnóstico que el prompt no presupuestaba.
**Delegaciones:** 0 (fase DIRECTA; no se delegó ni el inventario de dueños, que se publicó desde el propio lector
del instrumento).

## Límites y deudas que deja la fase

- **S-B.1 (nueva, dueño: operador / próximo mandato sobre el hook):** el control S15 y su familia **no** están
  cableados a `[6/8]` del hook — lo que goberna el hook es `build_lesson_index.py --check`. El rojo que el maestro
  atribuía a «cada commit» era en rigor un rojo de **pytest**, no del hook; la fila del maestro §1 («gobierna `[6/8]`
  del hook versionado, o sea cada commit») describe el diente, no el gate. Declarado, no corregido: tocar el hook o
  `run_all_validations.py` está prohibido a esta fase.
- **S-B.2 (nueva, dueño: FASE-RELEASE del plan):** el fixture del control ahora **deriva** su reloj del corpus, así
  que un `git mv` masivo de `Historico/` o un plan nuevo con fecha muy antigua cambian el piso y, con él, el par
  estampado. Eso es lo queridos (la premisa ya no está pineada), pero el denominador del tier `commit` (11) y el
  `piso` (2026-07-06) quedan publicados en `09` §D para que un rojo futuro sea atribuible.
- **L-CIM.8 del hermano sigue vivo y esta fase lo volvió a ver:** los `.md` untracked ajenos bajo `.opencode/`
  entran en la población del derivado, así que un verde del índice en el worktree no se reproduce en el árbol del
  commit sin esas rutas. No se tocó.

## Verificación en el árbol del commit (L-VCF-15)

**NO aplica a esta fase**: no hubo commit, así que no existe árbol propio que verificar. Todos los verdes de arriba
corresponden al **árbol de trabajo** de `77e64ca`, y esa etiqueta está en cada crudo. Si el operador autoriza el
commit, la verificación se repite sobre el árbol del commit antes de estampar paridad.
