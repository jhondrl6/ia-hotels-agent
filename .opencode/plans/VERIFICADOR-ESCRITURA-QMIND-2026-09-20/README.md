# VERIFICADOR-ESCRITURA-QMIND-2026-09-20

**Estado: PENDIENTE de ejecución. Una sola fase, una sola sesión. Nada de este plan se ha implementado.**
No consume ni toca el presupuesto `v4complete` de ningún otro plan.

**Disparador y calendario:** sesión propia **antes de FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**,
porque ese cierre necesita publicar el `10-analisis` con un **título nuevo** y el writer de hoy no admite
títulos ni archivos explícitos. No se ejecuta dentro de la cadena `A → G → 0 → B → … → RELEASE`: FASE-0 es
evidencia del veredicto (AC20), VERIFY prohíbe fixes y tests nuevos, y RELEASE es documental y «no una fase
de reparación». Si el disparador vence sin ejecutarse, aplica el *fallback* del §5 del maestro.

Objetivo: que la ingesta de cierre de un plan sea **verificable por contenido y actualizable**, en lugar de
por la existencia de un título. Hoy `validate_qmind_writeback.py` da verde con contenido obsoleto y no tiene
vía de actualización; el corpus lo documenta desde el 2026-09-11 y nadie lo cerró.

## Índice

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): Paso 0 ejecutado, con las cuatro consultas reales y su corte.
- [Plan maestro](01-plan-maestro.md): premisas medidas, AC1–AC5, alcance y no-alcance, fallback.
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
- No ejecuta `v4complete` ni red ni scraping.
- No sube material del cliente: toda ingesta de prueba se hace sobre copia saneada, con la prueba de sha
  inverso que ya usa `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/qmind-writeback-G.md`.
