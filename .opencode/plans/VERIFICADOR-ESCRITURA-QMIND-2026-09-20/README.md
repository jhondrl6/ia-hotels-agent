# VERIFICADOR-ESCRITURA-QMIND-2026-09-20

**Estado (reconciliado el 2026-09-24 por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`):
FASE ÚNICA NO EJECUTADA, con su contrato ahora dividido en dos momentos.** Ninguna línea de este plan
está implementada: `scripts/validate_qmind_writeback.py` sigue sin `--title` ni `--file`, sigue decidiendo
**por título** y sigue degradando a `exit 0` cuando falta el CLI (medido otra vez el 2026-09-24 con
`grep` sobre su `main()` y su `_check_qmind_writeback`). Lo que cambió no es el estado de la fase sino su
**estructura de aceptación**: **entrega offline verificable** (maestro §6) frente a **aceptación remota**,
que es la que necesita red, autorización y presupuesto propios. Este mini-plan **no consume ni toca el
presupuesto `v4complete` de ningún otro plan.**

**Disparador y calendario:** sesión propia **antes de FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**,
porque ese cierre necesita publicar el `10-analisis` con un **título nuevo** y el writer de hoy no admite
títulos ni archivos explícitos. No se ejecuta dentro de la cadena `A → G → 0 → B → … → RELEASE`: FASE-0 es
evidencia del veredicto (AC20), VERIFY prohíbe fixes y tests nuevos, y RELEASE es documental y «no una fase
de reparación». Si el disparador vence sin ejecutarse, aplica el *fallback* del §5 del maestro.

> **⟦Circularidad resuelta el 2026-09-24 (orden §4.C, fila `ESCRITURA-QMIND`)⟧.** La fila **AC6** exigía
> como prueba «`[15/15]` verde sobre el plan padre **tras la ingesta de cierre**», y a la vez esta sesión
> está concebida para correr **antes** de esa ingesta. Con esa redacción, AC6 no podía cerrarse nunca: si
> la sesión cumplía su disparador, el evento que produce su evidencia aún no había ocurrido; y si esperaba
> a que ocurriera, ya había vencido el disparador y era tarde para el writer que el padre necesita. El
> defecto no era de cronología sino de **una sola AC con dos momentos mezclados**. Se separan (maestro §2 y
> §6): **AC6-entrega** — cambiar el prompt de RELEASE del padre para que mande el writer con `--title`, y
> dejar el instrumento capaz de hacerlo — se prueba **offline, en esta sesión, con `diff` y tests**;
> **AC6-aceptación** — que `[15/15]` dé verde sobre el padre **después** de su ingesta de cierre — se
> declara **diferida con dueño y disparador**, y **no** es condición para cerrar esta fase. Una fase
> entregada con AC6-aceptación pendiente es un resultado **parcial explícito**, no un fracaso ni un éxito.


Objetivo: que la ingesta de cierre de un plan sea **verificable por contenido y actualizable**, en lugar de
por la existencia de un título. Hoy `validate_qmind_writeback.py` da verde con contenido obsoleto y no tiene
vía de actualización; el corpus lo documenta desde el 2026-09-11 y nadie lo cerró.

## Índice

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): Paso 0 ejecutado, con las cuatro consultas reales y su corte.
- [Plan maestro](01-plan-maestro.md): premisas medidas, **AC1–AC6** (⟦el índice publicaba «AC1–AC5» cuando el maestro define seis; la sexta es justamente la que estaba mal formulada⟧), alcance y no-alcance, **§6 los dos momentos**, y fallback.
- [Prompt de inicio de sesión](05-prompt-inicio-sesion.md): el bloque listo para pegar.

## Por qué esto merece su propia sesión y no un comentario en el plan padre

Medido el 2026-09-20, tres hechos que el plan padre no puede arreglar sin romperse:

1. `scripts/run_all_validations.py` invoca el validador como check **[15/15]**, pero solo en el modo
   completo (cola del método `run()`, dentro de `if not self.quick:`); no corre con `--quick` ni en
   `scripts/git_hooks/pre-commit`. Ninguna fase intermedia lo ve.
2. `_check_qmind_writeback()` lo lanza **sin `--strict`**: si el CLI `qmind` no está disponible, el
   validador degrada a exit 0 y el resumen muestra PASS. Es un verde producido por la ausencia del
   instrumento.
3. `is_ingested()`, en `validate_qmind_writeback.py`, decide **por título**. Una fuente publicada a
   mitad de plan satisface el check para siempre. Consecuencia observada en el notebook hoy: 49 fuentes, y
   `TRIBUNAL-OFFLINE-2026-09-09` tiene **dos** (`(lecciones aprendidas y decisiones)` de 2026-09-10 y
   `(cierre v4.76.0, lecciones finales 2026-09-11)`), que es exactamente el residuo que ese plan describió
   al cerrar y decidió tolerar.

## Límites declarados de este mini-plan

- No arregla la idempotencia del servicio: `qmind source upload` no sobrescribe. Si algo se puede cambiar es
  lo que el repo verifica y cómo lo invoca, no lo que el backend permite.
- No toca Tribunal, gates, umbrales, `write/publish/suppress`, hooks ni `VERSION.yaml`.
- **No ejecuta `v4complete` ni red ni scraping.** ⟦Precisión del bloque C de la orden de calidad,
  2026-09-24⟧: esta prohibición es **de esta sesión de preparación y de las pruebas de la fase**, y
  **no** debe leerse como que una prohibición de red permita una subida — la lectura contraria era parte
  de la circularidad que la orden §4.C pidió resolver. Las operaciones remotas existen, están en el
  maestro §6, y cada una exige **autorización literal y presupuesto propios** del operador. Esta sesión
  **no concede ninguna de las dos y no ejecuta acceso remoto alguno**.
- No sube material del cliente: toda ingesta de prueba se hace sobre copia saneada, con la prueba de sha
  inverso que ya usa `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/qmind-writeback-G.md`.
  **El saneado no es opcional ni postuesto**: `do_upload()` ejecuta `qmind source upload --file` crudo, sin
  reescritor, así que lo que hay que sanear es el archivo **antes** de pasarlo al writer. Verificar siempre
  por **descarga + sha256**, nunca por título.
