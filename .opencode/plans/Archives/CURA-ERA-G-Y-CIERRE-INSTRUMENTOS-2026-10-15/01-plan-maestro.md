# Plan Maestro — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> **Fecha**: 2026-10-15 · **Versión objetivo**: 4.81.1 (patch: comportamiento observable de instrumentos, sin cambios de producto) · **Estado**: PREPARACIÓN (prompts generados; ninguna fase ejecutada)
> **Origen**: el hallazgo `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/13-segunda-via-ciega.txt` abrió la tanda de la segunda vía; su cura se ejecutó y se empujó (`2e048e6` + `1f95e84`), y de esa sesión quedaron dos cabos que este plan cierra en un solo ciclo: el **cierre documental** de la tanda (commits ya empujados, evidencia en `temp/`, registro `D-QW-1`/`D-QW-2` sin commitear) y la **deuda era-G** que mantiene el modo completo en rojo.
> **Mandato del operador (2026-10-15)**: «Guarda el plan para ejecutar en una nueva sesión que cubra ambas», tras elegir la vía consolidada: una sola unidad de versión (4.81.1) que cubra las tres curas — la segunda vía de gobernación, el reemplazo por documento y la era-G.
> **Decisión de reparto**: el bump queda rehén de era-G a propósito. Los commits de FASE-A y B pueden ir por delante (son documentales) y el `4.81.1` espera a FASE-RELEASE, que es donde el CHANGELOG publica las tres curas juntas.

## §1 Criterios de Aceptación (verificación al cierre de cada fase; AC1..AC6 se cierran en su fase, AC7 en RELEASE)

Cada AC declara **dónde se lee** (R2.4: un ✅ cuyo único respaldo es «el string está en el código» no existe).

| AC | Enunciado | Artefacto y clave donde se lee |
|----|-----------|-------------------------------|
| AC1 | Las rutas que registran la deuda del writer quedan **versionadas y empujadas**: el contexto `CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md`, el crudo `14-deuda-writer-context-sin-registro.txt` y el par del índice regenerado, con `build_lesson_index.py --check` verde y `validate_opencode_refs.py` PASS **en el árbol del commit** | `git show` del commit de FASE-A + las dos corridas en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/` |
| AC2 | Los crudos de la tanda de instrumentos (frescura pre/post, quick, write-back, hook del commit, recorrido del writer) quedan **persistidos** bajo `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/` con numeración que no colisiona con el `14-` existente, y cada uno con su sha256 en el acta del cierre documental | `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/acta-cierre-documental.md` con el listado y los shas |
| AC3 | Existe el **censo de la deuda era-G**: cada fuente del notebook que dispara `[DUPLICADO-VIGENTE]` —5 fuentes sobre 2 planes en la corrida del 2026-10-15— y cada fuente contada como huésped sin contabilidad (5 en el `[CONTADOR]` de esa corrida), con id, título, sha de metadata y la razón medida de su falta de contabilidad | `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md` + el crudo de la corrida |
| AC4 | Cada fuente del censo tiene **decisión escrita del Operador** en la sesión de FASE-B (marcar como reemplazada / borrar del notebook / dejar con motivo declarado) y el mecanismo de la cura queda especificado con su coste: primitivo nuevo del writer o cero líneas de código. Ninguna fila queda sin decisión | Tabla de decisiones en el informe de FASE-B, con la respuesta del Operador registrada en la sesión |
| AC5 | Tras la cura, `validate_qmind_writeback.py` sale **sin ninguna línea `[DUPLICADO-VIGENTE]`** y con `0 fuente(s) huesped(s) sin contabilidad` en su `[CONTADOR]`, con el par rojo-antes (crudo de FASE-B) y verde-después (crudo de FASE-C) en evidence: sin el rojo medido no hay ✅ (R2.8) | Los dos crudos + la línea `[CONTADOR]` de la corrida final |
| AC6 | No-regresión por delta (R2.3) con pares pre/post por fase de código y `run_all_validations.py --quick` verde al cierre de cada fase (el número lo imprime la corrida, no este archivo) | Pares en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-*/` + corridas |
| AC7 | La release **4.81.1** queda sincronizada (hook version-sync sin rojo), el CHANGELOG publica las tres curas (segunda vía de gobernación, reemplazo por documento, era-G), `docs/cobertura-historia.md` gana la nota de ronda por los 9 tests de la tanda de instrumentos (root test files 1241→1250 y total 5.321→5.330; los mide el comando canónico, no este texto) y `DOMAIN_PRIMER` se regenera; el cierre ejecuta write-back → índice → `git mv` en el orden de R2.10 | Entrada del CHANGELOG + nota de ronda + fila del REGISTRY + plan archivado |

## §2 Causa raíz → fases

1. **La tanda de instrumentos quedó empujada pero sin cerrar su documental**: los commits `2e048e6` y `1f95e84` viajaron, pero los 4 archivos del registro `D-QW-1`/`D-QW-2` siguen sin commitear, los crudos viven en `temp/` (gitignored) y ninguna acta los reúne. → **FASE-A**.
2. **La deuda era-G no es curable sin censo ni decisión**: el rojo `[DUPLICADO-VIGENTE]` señala 5 fuentes que nombran a su plan sin marca de reemplazo, y el `[CONTADOR]` declara 5 huéspedes sin contabilidad. Qué se marca, qué se borra (irreversible) y qué se deja declarado es decisión del Operador, y hoy no existe el censo que la sostenga. → **FASE-B**.
3. **La cura puede o no necesitar código**: si el mecanismo elegido es «marcar en el registro», puede exigir un primitivo nuevo del writer (hoy `registrar_publicacion()` exige instantánea y archivo); si es «dejar con motivo declarado», puede ser política pura. → **FASE-C**.
4. **Una sola unidad de versión**: 4.81.1 publica las tres curas juntas, con la nota de ronda que los 9 tests de la segunda vía reclaman. → **FASE-RELEASE-4.81.1**.

## §3 Fases (R1: una fase por sesión — sin excepciones)

| Fase | Tipo | Complejidad técnica | Modo de ejecución | Presupuesto (R2.1, unidad declarada) |
|------|------|--------------------|-------------------|--------------------------------------|
| FASE-A | Cierre documental (commits + evidencia + acta) | **Baja** — sin código; comandos ya corridos y verificados | **DIRECTO** | ~30 tool calls; corte: hasta listo para revisión (el commit requiere autorización del Operador en la sesión) |
| FASE-B | Investigación (censo era-G + decisión) | **Media** — exige red (censo del notebook) y al Operador en el bucle | **DIRECTO** (la decisión es del Operador; no delegable) | ~35 tool calls; corte: hasta listo para revisión |
| FASE-C | Implementación (cura era-G) | **Media** — puede ser un primitivo del writer con dientes o una política sin código, según FASE-B | **DIRECTO** | ~40 tool calls; corte: hasta listo para revisión |
| FASE-RELEASE-4.81.1 | Cierre y release | **Baja** — docs + bump + write-back + archivado | **DIRECTO** (no delegable: toca VERSION/CHANGELOG/REGISTRY y el `git mv`) | ~35 tool calls; corte: hasta listo para revisión |

**Criterios de activación FASE-VERIFY (§4.6)**: se evalúan y **no aplica** — no hay ejecución E2E ni ≥3 fases de implementación (solo FASE-C toca código, y de forma posiblemente nula). La certificación de ACs la hace cada fase en su cierre, con AC5 verificada por la corrida real del writer.

## §4 Decisiones y restricciones globales

- **DEC-1 (el bump cubre las tres curas)**: 4.81.1 es la unidad de versión de la segunda vía + reemplazo por documento + era-G. Decisión del Operador (2026-10-15) al elegir el plan consolidado; el coste aceptado es que la release espera a era-G.
- **DEC-2 (el `10-analisis` de CURA está congelado)**: prohibido editarlo en cualquier fase — su `sha_cuerpo` publicado (`5c54f5ed3cb9345e…`) casa byte a byte con el disco y editarlo lo deja VENCIDO.
- **DEC-3 (los dos CONTEXT publicados están congelados)**: `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` y `CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` se publicaron el 2026-10-15 (sha `f6e14e735e51…` y `3cebfeb58e48…`); editarlos los deja VENCIDO hasta una re-publicación con título nuevo que conserve el stem.
- **DEC-4 (borrar en el notebook es del Operador, escrito)**: el writer solo marca; `qmind source delete` es irreversible sobre contenido publicado y ninguna fase borra sin la decisión por fuente de AC4 registrada en la sesión.
- **DEC-5 (el `10-analisis` del plan se crea desde la concepción)**: este plan lo trae esqueleto; cada fase lo actualiza en su Post-Ejecución.
- **Citas**: símbolos, nunca `archivo:línea` (R2.2) — el plan nace sin citas numéricas y así no entra al inventario de `plan_citations_baseline.json`.
- **Cinco cortes sin commit**: implementación terminada → verificación terminada → cierre documental → listo para revisión → espera de autorización. Ningún prompt de este plan autoriza commit por sí mismo; cada commit requiere la letra del Operador y **pathspec explícito** (L-SECF.2: `git commit -- <ruta>` no toma untracked).
- **Trabajo ajeno**: al concebir este plan el árbol trae los 4 archivos del registro `D-QW` sin commitear. Son de este plan: FASE-A los commitea con pathspec.
- **Sello de la tanda 2026-10-15** (additivo, no re-escribe la fila de arriba): las cuatro rutas y los 11 archivos del plan quedaron versionados en `85ab952` — 15 rutas, `git add` previo y pathspec explícito, hook 8/8 y quick 13/13 con el staged en el índice. En `26bd0f5` los dos contexto cerrados pasaron a `context/Historico/` con un mv de bytes intactos y las 7 roturas absorbidas en `refs_baseline.txt` (5 entradas por par). Lo que la fase sigue debiendo son sus crudos y el acta.
- **Modo completo** (`run_all_validations.py` sin `--quick`) exige `PYTHONUTF8=1` (S-CIM-10).
- **Fuera de alcance**: la rama por defecto del writer (`D-QW-1`/`D-QW-2`), el cableado del gate `hard_contradictions` (`S-CST-1`), `P6.5` del Tribunal, el plan que nazca del contexto plantilla-tier y cualquier cambio de producto.

## §5 Deudas diferidas con dueño

| Deuda | Dueño | Camino de cierre |
|-------|-------|------------------|
| `D-QW-1` / `D-QW-2` — la rama por defecto de `--upload` publica CONTEXT sin registrarlos, y las dos copias del detector de autodeclaración divergen | Operador | Fase propia (o absorción en FASE-C si el censo de FASE-B toca esa rama): registrar en el bucle de `scan_context_declarations()` y unificar el predicado con `declara_durable()`; exige dientes propios. Definidas en `.opencode/context/CONTEXT-DEUDAS-WRITER-QMIND-2026-10-15.md` |
| `S-CIM-1` — el `[18/18]` se invoca sin `--strict` | Operador | AC propia; el disparador es la política de invocación del runner, no el writer |
| `S-CST-1` — el gate blocking `hard_contradictions` no puede fallar en producción (`ValidationSummary.conflicts` hardcoded) | Operador | Fase propia: cablear motor→gate; toca `main.py`, `Conflict` y `publication_gates.py` |
| `P6.5` del Tribunal — el acta niega al revisor que corrió | Operador | Misma forma que AC12 curó en P6.2; decisión de cláusula registrada en CURA §Seguimientos |
| Anotaciones «sin commit» de FASE-RELEASE 4.81.0 que el push venció | Operador | Sello datado con los shas `2e048e6`/`1f95e84`; **no** se toca el `10-analisis` de CURA (congelado, DEC-2) — la vía es un addendum fechado en `evidence/…/FASE-RELEASE/` |
| `S-SEC-1` — el Secrets Check puede publicar `SIN_HALLAZGOS` sin leer su insumo: el diff staged ilegible por su decodificación heredada (sin `encoding=`) revienta el hilo lector, `run()` devuelve `stdout=None` sin excepción y los guards de `_check_staged_content` cierran en verde (fail-open) | Operador | Fase propia (fuera de este plan), con fix **fail-closed** (lectura en bytes + decodificación tolerante + abstención o rojo ante insumo ilegible) en los cuatro sitios de `run_all_validations.py` que comparten el raigambre (`_check_staged_content`, `_git_staged_paths`, `_git_tracked_files`, `_run_command`), con dientes propios y par de crudos legible/ilegible. Mecanismo medido, alcance por consumidor y repro: `dependencias-fases.md` §Determinación post-FASE-B (fuente única de esta determinación) |
