# FASE-UNICA — Verificador de escritura y frescura del write-back a QMind

**Estado:** PENDIENTE. **Dependencia inmediata:** ninguna técnica. **Disparador:** sesión propia **antes de
FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**; si ese RELEASE llega primero, aplicar el §5 del
maestro y dejar AC2–AC4 abiertos con dueño.
**Complejidad técnica:** MEDIA: un writer, un verificador conectado al modo completo y tests con mutación.
**Scope R3:** 4 tareas, 0 comandos largos externos. **No ejecuta `v4complete` ni repara código de producto.**

## Contexto e inicio

Lee `01-plan-maestro.md` (premisas P1–P6, AC1–AC6, alcance), `00-lecciones-capitalizadas.md` (cuatro filas
capitalizadas y cinco descartes), `04-contrato-ejecucion.md` y `06-checklist-implementacion.md` del plan
padre `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (su prompt de RELEASE es el consumidor de AC6), y el workflow
canónico `.agents/workflows/phased_project_executor.md` en las reglas R2.2 (citar símbolos, no líneas),
R2.8 (rojo por mutación) y R2.10 (orden write-back → índice → `git mv`).

Re-medir antes de la primera tarea, sin heredar las cifras de este documento: `git HEAD` y `git status`,
`run_all_validations.py --quick`, `validate_plan_citations.py`, `build_lesson_index.py --check`, y el estado
real del notebook con `fetch_source_titles()` del propio validador (hoy: 49 fuentes y dos de
`TRIBUNAL-OFFLINE-2026-09-09`).

## Tareas

1. **Writer actualizable (AC1).** Añadir a `scripts/validate_qmind_writeback.py` `--title` y `--file`
   (explícitos, con validación de que `--file` está bajo el repo y de que el título no colisiona en silencio
   con una fuente vigente del mismo plan). `--upload <PLAN>` sigue funcionando igual si no se pasan.
2. **Frescura por contenido (AC2, AC4).** Guardar junto a la subida una **instantánea versionada** en el
   repo y hacer que la verificación compare el contenido ingerido contra esa instantánea —con la prueba de
   sha inverso del saneado, que ya existe en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/`—, y
   exigir que un plan no tenga dos fuentes vigentes sin marca de reemplazo. Decisión abierta que hay que
   tomar en voz alta: marcar la anterior o borrarla (borrar es irreversible sobre contenido publicado).
3. **Fin del verde por ausencia (AC3).** Que `_check_qmind_writeback()` invoque el script con `--strict` o
   distinga un tercer estado; el resumen no puede contar como PASS una medición que no ocurrió.
4. **Cierre (AC5, AC6).** Mutaciones que pongan rojo **por el guard** en los tres estados (título
   coincidente con contenido distinto; CLI ausente; dos fuentes vigentes), con árbol restaurado por sha256;
   tests offline y sin red real salvo la ingesta de prueba sobre copia saneada; y actualizar el prompt de
   FASE-RELEASE del plan padre para que mande el writer en lugar de depender de que alguien recuerde el
   título pre-acordado. Cierre incremental con la regla de siempre: `log_phase_completion.py` sin
   `--release`, `build_lesson_index.py` y su `--check`, quick y `validate_document_integration`.

## Reglas

- No tocar Tribunal (`_compute_verdict`, flags de bloqueo, umbrales), gates, `write/publish/suppress`, hooks,
  `VERSION.yaml`, `AGENTS.md` ni el workflow canónico sin instrucción explícita del operador.
- No subir material del cliente: toda prueba contra el servicio se hace sobre copia saneada y versionada.
- No ejecutar `v4complete` ni red ni scraping. No consumir presupuesto de corridas de otros planes.
- Citaciones en documentos: **símbolos, nunca números de línea** (R2.2; `validate_plan_citations.py` lo
  vuelve rojo).
- Commit, push, tag y write-back se piden por separado y con autorización literal: dejar checkpoint si falta.

## Presupuesto y checklist

Referencia **60 tool_use hasta el commit de código**, medida con el instrumento del contrato
(`evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`). Sin transcript o con acceso denegado:
**FUERA DE SERVICIO (R2.1)**, auto-reporte con **unidad contable declarada** (rutas tocadas, corridas de
baseline, mutaciones) y **sin comparar** con la referencia; no estimar.

- [ ] Premisas P1–P6 re-medidas al abrir, con sus comandos.
- [ ] AC1: `--title`/`--file` con sus tests, sin cambiar el default de `--upload <PLAN>`.
- [ ] AC2 y AC4: verificación por contenido y regla de una sola fuente vigente, con instantánea versionada.
- [ ] AC3: sin PASS por ausencia de instrumento; el estado «no medible» se ve en el resumen.
- [ ] AC5: 3/3 mutaciones en rojo por el guard, 0 por sintaxis o import, árbol restaurado por sha256.
- [ ] AC6: prompt de FASE-RELEASE del plan padre actualizado y [15/15] verde sobre él tras la ingesta de cierre.
- [ ] Cierre documental completo, índice regenerado y `--check` fresco, quick TOTAL PASS.

## Inicio de la sesión

Copiar en una sesión nueva:

```text
Ejecuta la FASE-UNICA del plan C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/. Lee 01-plan-maestro.md (premisas P1-P6 y AC1-AC6), 00-lecciones-capitalizadas.md, 05-prompt-inicio-sesion.md y el prompt de FASE-RELEASE del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18, que es el consumidor de AC6. Re-mide las premisas antes de la primera tarea: git HEAD y status, run_all_validations.py --quick, validate_plan_citations.py, build_lesson_index.py --check y el estado real del notebook con fetch_source_titles(). Objetivo: que el write-back sea actualizable (--title, --file) y que la verificación compruebe contenido y vigencia en lugar de la existencia del titulo, sin degradar a PASS cuando el CLI falta. Limites: no tocar Tribunal, gates, umbrales, write/publish/suppress, hooks, VERSION.yaml, AGENTS.md ni el workflow; no subir material del cliente (solo copia saneada y versionada); no ejecutar v4complete ni red ni scraping; citar simbolos y nunca numeros de linea en los documentos. R2: sin transcript declara FUERA DE SERVICIO con unidad contable propia y no compares. Commit, push, tag y write-back se piden por separado y con autorizacion literal: deja checkpoint si falta.
```
