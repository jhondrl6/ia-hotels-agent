# Bloque B — Proceso común e instrumentos (orden de calidad 2026-09-22)

> ## ⟦DICTÁMEN DE CIERRE RETIRADO — consérvese como antecedente, no como estado vigente⟧
>
> Los dos dictámenes de «B concluido» que se escribieron en este archivo **fueron retirados** el
> 2026-09-23 por la continuación correctiva de B. Lo que sigue debajo se conserva íntegro como
> antecedente de lo que aquella sesión creyó medir; **no es la fuente de resultados**. Nada de lo de
> abajo se borra ni se reescribe, y su evidencia no se reconstruye.
>
> Brechas por las que se retiró (la explicación y la prueba están en la fuente única
> `../BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`):
>
> 1. **«Fecha de REGISTRY … Cubierto por `tests/test_registry_fecha_documental.py`»** sobreafirmaba.
>    Esas pruebas nunca redirigieron las raíces del `SyncEngine` ni `VERSION.yaml` al mismo expediente
>    temporal, nunca corrieron la sincronización **en modo escritura**, no probaron fechas distintas
>    entre release y entrada ni el cambio de día, y no tenían control negativo. Además el escritor
>    real publicaba en cada entrada `- [x] Tests passing`, `- [x] Suite NEVER_BLOCK passing` y
>    `- [x] Capability contract verificado` sin haber ejecutado nada de eso.
> 2. **«S13 resuelto»** sobreafirmaba. Se movió el destino de escritura, pero la observación seguía
>    siendo de **estado final** (instantáneas antes/después), no de **operaciones de escritura**; y el
>    control negativo «por causa» definía su propia función de huellas (`pareja()`) dentro del test y
>    provocaba el rojo con `os.utime` artificial — las dos cosas que el mandato prohíbe expresamente.
> 3. **«Proceso común»** quedó a medias: se añadieron párrafos de principio que **contradicen**
>    instrucciones ejecutables vigentes del propio executor y de su plantilla (registro de fases en
>    §4.5 contra «RELEASE no registra» de §2.5; copiar métricas a README/09/10 paso a paso; «Cuatro
>    cortes» con el corte de R2.1 fijado «hasta el commit de código», que es circular cuando el commit
>    no está autorizado).
> 4. **Mediciones y operaciones finales omitidas**: este directorio no tenía ni un stdout preservado;
>    no se ejecutó el generador del índice de lecciones ni su comprobación de frescura sobre el árbol
>    final, ni `git diff --check`, ni el registro de B; y se declaró un `--check` **completo** (15
>    checks) cuyo camino QMind no corresponde a una sesión sin red.
> 5. **«Sin … red, QMind»** en el encabezado de abajo **no puede sostenerse**: se ejecutó
>    `run_all_validations.py --check` sin `--quick`, cuyo check `[15/15]` invoca
>    `validate_qmind_writeback.py`, y en esta máquina el CLI `qmind` **sí está instalado**
>    (medido con `shutil.which`). Como no se preservó la salida de esa corrida, no puede saberse si
>    hubo tráfico: queda **NO DETERMINADO**, no «cero red».
> 6. **PRE falseado y ya retractado abajo**: se conserva la retractación, pero véase también que el
>    «50 passed» y el «11/11» de abajo sí reproducen (medido de nuevo el 2026-09-23 a las 17:56, ver
>    `../BLOQUE-B-REMEDIACION-2026-09-23/instrumentos/PRE_*.txt`).

Ejecución del bloque B de `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`
el 2026-09-23, bajo mandato expreso del operador (fronteras del propio mandato de sesión).
No es FASE-B de CONTEXTO ni el piloto FASE-C. Sin commit, push, ~~red, QMind~~ (rectificado: ver
el punto 5 del retiro), SDKs, pipeline, archivado ni bump de versión.

## Qué se cerró

| Tramo | Qué cambió | Criterio §6 de la orden |
|---|---|---|
| B — fecha de REGISTRY | Un solo escritor (`log_phase_completion.py`, fecha de última entrada documental). `sync_config.yaml` retiró la regla `registry_last_update` que la re-escribía con `release_date`. Docs alineados (CONTRIBUTING, documentation_rules §8). | 3 (registro+sync ya no generan el conflicto) |
| B/D1 — cifras de gobierno vencidas | Retiradas de su fuente las 4 aserciones A1–A4 del árbol `.agents/` vigente (executor `check 8`/`[9/9]`/`[12/12]`, template `[10/10]`) → texto que dice que el valor vigente lo imprime la corrida. | 3 y 4 |
| S13 — arnés de mutación | El arnés ya no escribe en `evidence/…/FASE-A/mutation/`; vuelca en destino temporal explícito y prueba que re-medir no re-pisa expedientes cerrados (hash **y** mtime). | 3 |
| B — proceso común | Nueva sección «Proceso común: proporcionalidad y reuso» en el executor + checklist proporcional en la plantilla; se retiran las cuotas «mínimo 3 lecciones» y se permite «sin lecciones nuevas». | 4 |

## Qué NO se tocó (fronteras respetadas)

Composición de `run_all_validations.py`, `build_lesson_index.py`, hook, renumeración/promoción de
checks (**D2**), `.cursorrules`, producto hotelero, writer QMind, D7. No se ejecutó el piloto FASE-C
ni el bloque C de la orden.

## PRE → POST (medición honesta y retractación de una cifra previa)

> **RETRACTACIÓN.** Una versión anterior de este resumen publicaba un «PRE = 24 passed, 16 errors».
> **Esa cifra no era un PRE**: se midió sobre el árbol **ya modificado por D1 pero con los tests del
> árbol real aún sin re-anclar** — era un estado intermedio roto, no la línea base. Se retira. El
> único PRE comparable que se puede afirmar sin re-ejecutar el HEAD con stash es el del verificador
> sobre los **docs pre-D1**, que hoy viven congelados en `fixtures/`. No se reconstruye tiempo activo
> ni tool calls (no hay transcript con instrumento).

| Instrumento | PRE (docs pre-D1, congelados en `fixtures/` = línea base) | POST (árbol real de `.agents/` con B) |
|---|---|---|
| `validate_governance_numbers.py` contra esos docs | `[HALLAZGOS]` A1–A4, **exit 1** (24 instancias, 5 en 4 aserciones, 8 históricas) | `[SIN-HALLAZGOS]`, **exit 0** (19 instancias, 0 hallazgos, 8 históricas intactas) |
| Fecha de REGISTRY | dos escritores: `log_phase_completion` (hoy) y `sync_config` regla `registry_last_update` (`release_date`) → `sync --check` FAIL al día siguiente de loguear | un escritor (`log_phase_completion`); `sync_versions --check` no conoce REGISTRY |
| Arnés de mutación | escribía por constante `EVIDENCE` en `evidence/…/FASE-A/mutation/` (re-pisaba 7 archivos cerrados; `git status` limpio, mtimes movidos) | destino temporal explícito + observación hash **y** mtime + control negativo |
| Cierres/lecturas | `4/4` fijo en la plantilla, `10/10` en AGENTS vs 11 checks reales; cuotas «mínimo 3 lecciones» | cifras dinámicas (las imprime la corrida), «sin lecciones nuevas» permitido, pautas de proporcionalidad/reuso |

### Estado de la suite tras B (exit codes reales)

- `pytest tests/quality_gates/governance_numbers tests/test_registry_fecha_documental.py` → **50 passed, exit 0**.
  Incluye los re-anclajes a `fixtures/` + las pruebas nuevas: `test_arbol_real_honesto_tras_d1`,
  `test_re_medir_no_reescribe_expedientes_cerrados`, `test_la_huella_detecta_reescritura_de_bytes_identicos`
  (control negativo), `test_el_arnes_no_conoce_ruta_de_evidencia...`, y la interacción real
  `test_motor_de_sync_no_conoce_el_registry_temporal_estampado` + `test_sync_check_repetido_no_reescribe_la_fecha...`.
- `run_all_validations.py --quick` → **11/11, exit 0** (la puerta B). Durante la remediación se coló
  una cita de número de línea (`dependencias-fases.md:88`) en el maestro que rompió el check
  `Plan Citations` (R2.2); se corrigió a referencia por símbolo y `--quick` volvió a 11/11.
- `run_all_validations.py --check` → **15 checks**; `Plan Citations` ya pasa, pero el check `Tests`
  (corrida total de `pytest`) refleja **fallos preexistentes declarados por el bloque A**, ajenos a
  B (ver atribución más abajo); por eso el `--check` completo NO sale verde. No se achica la suite
  ni se relaja el check para forzar verde (política L-VCF-5).
- `validate_document_integration.py` → exit 0. `validate_governance_numbers.py` (árbol real) → exit 0.
- `build_lesson_index.py --check` → fresco (332 IDs). `git status --porcelain evidence/` → solo el dir B nuevo.

### Suite completa (exit codes reales): B no añade fallos

`pytest -q` sobre el árbol de B → **4 failed, 4406 passed, 41 skipped, 4 xfailed, exit 1**. Los 4
fallos son **los mismos que el bloque A atribuyó como ajenos** y ninguno toca `governance_numbers`,
`test_registry_fecha_documental` ni `decision_client` (las superficies de B):

- `test_function_default_flags` — pricing flaky (pasa aislado; mecanismo pendiente, fuera de B).
- `test_diagnostic_includes_geo_metrics` — falla igual en HEAD extraído (ajeno a B).
- `test_validate_lesson_capitalization[...TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]` — por el archivado de
  ese plan (ajeno).
- `test_validate_wiring` — contaminación de `tmp_test/venv-jev-sdk/` (0 rastreados; ajeno).

**Delta de conteo:** B sumó funciones (fixtures re-ancladas + `test_registry_fecha_documental.py` y
los tests nuevos de D1/S13/interacción) y **0 fallos nuevos**; los 4 fallos preexistentes se
conservan, atribuidos y no ocultados (§6.1). La corrida completa NO es la puerta de B: lo es
`--quick` (11/11) más las suites afectadas en verde.

## Correcciones de la auditoría interna (segunda pasada de B)

Un dictamen inicial de «B concluido» fue prematuro. Esta segunda pasada cerró lo que la auditoría
señaló, dentro de las fronteras y con la ampliación que el operador autorizó:

1. **Registro↔sincronización**: la prueba «idempotente» solo contaba cabeceras y pasaba con entradas
   duplicadas. Re-escrita: se afirma el comportamiento real (cabecera única coherente al repetir; el
   `append` por fase NO se vende como idempotencia) y se añadió interacción real sobre el mismo
   expediente (motor de sync no conoce el REGISTRY; `--check` repetido no toca contenido ni mtime).
2. **S13**: se añadió el control negativo que demuestra que la observación (hash + mtime) detecta la
   reescritura de bytes idénticos, no solo la compara.
3. **Propiedad D3**: el maestro §6 fija «Plan propio, posterior»; la nota inicial decía «este plan».
   Corregido a la etiqueta del maestro; D3 sigue **adelantada en parte, no cerrada**.
4. **D2 fuera**: no se renumeró ni promovió ningún check.
5. **Frontera de alcance**: `lecciones-capitalizadas-template.md` (fuente de A4) no estaba en la lista
   de B y se editó por arrastre; se obtuvo **ampliación expresa del operador el 2026-09-23** y queda
   registrada aquí y en `dependencias-fases.md`. Las versiones de frontmatter (executor v2.25.0,
   plantilla v1.6.0) se mantienen por decisión del operador (metadato documental, `VERSION.yaml` intacto).
6. **Registros conciliados**: maestro D1, contrato (rojo A1–A4 y restricción S13), análisis S1/S8/S13
   y orden §4.B/§5/§5-ter/E5 rectificados contra git (los commits `cea8259/d576368/da382b1` vencen las
   citas «sin commit/push pendiente» de la conciliación; el árbol de B sigue sin commitear por mandato).

## Antecedentes que NO son estado vigente (rectificación de frases vencidas)

`fdd397f`, `cea8259`, `d576368`, `da382b1` son antecedentes del bloque A y su higiene documental.
Al medir git: HEAD local = `da382b1`, `git rev-list --count origin/master..HEAD` = **0** (paridad con
origin). Por tanto «push pendiente»/«sin commit» de la remediación **no** describen el estado vigente;
el árbol actual de B sigue **sin commitear** (así lo pide el mandato: cero commit/push).

## Ahorro: real vs declarado como no medido

- **Real y estructural:** desaparece el rojo contractual A1–A4 que había que re-explicar en cada fase
  (`exit 1`→`exit 0`) y el conflicto repetido de la fecha de REGISTRY deja de ser posible (un solo
  escritor). El detector sigue con sus dientes: las 4 aserciones se prueban ahora contra un
  contraejemplo congelado, no debilitadas.
- **No medido (declarado, no inventado):** no se instrumentó el tiempo activo de la sesión ni el
  ahorro de «escaneos repetidos» del §2 de la orden. Sin transcript de herramienta no se reconstruyen
  iteraciones a partir del número de archivos (§B: «No reconstruyas tiempos activos»).

## Criterios §6 satisfechos vs pendientes (bloque C / piloto)

- §6.3 (conflicto de fechas / re-medir no pisa histórico): **satisfecho**.
- §6.4 (cada cifra con fuente identificada, no mantener el mismo dato a mano): **satisfecho** para
  las cifras tocadas (gobierno y REGISTRY).
- §6.2 (PRE/POST comparable, publicar ahorro aunque sea nulo): **parcial** — se publica el delta
  estructural y se declara no-medido el ahorro de tiempo.
- §6.1 (contraejemplos como regresiones que fallan antes/pasan después): cubierto con los fixtures
  congelados + mutantes.
- §6.5 (punto de reanudación coherente en los cuatro planes) y §6.6 (piloto informado): **pertenece
  al bloque C y al piloto**, no a B.
