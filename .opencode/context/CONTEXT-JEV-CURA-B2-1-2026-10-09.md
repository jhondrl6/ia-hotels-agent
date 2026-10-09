# CONTEXT — Lecciones de la cura B2-1 del piloto JEV (SESIÓN 2, 2026-10-09)

> **Qué es este archivo.** El Paso 0 del executor ordena capitalizar las lecciones de una sesión al corpus, y
> el corpus de **definiciones** del índice son los análisis de plan (`09-/10-…análisis…md`) y
> `.opencode/context/`. El análisis del plan dueño de esta cura (`EVALUACION-JEV-TYPESAFE-2026-09-21`) está
> **archivado y publicado en QMind**: escribir ahí habría vuelto a vencer la fuente que se verificó por
> descarga hoy, y una segunda publicación no estaba en el mandato. Las lecciones se definen aquí, que el
> índice lee igual, y se citan desde el expediente (`evidence/…/CURA-B2-1-2026-10-09/`), no desde los tres
> documentos que el verificador de frescura usa para gobernar contexts.
>
> **No declara `⟦Control de contexto⟧`.** La política del write-back es por aporte declarado, no por
> existencia (`verify_qmind_context_freshness.py`, executor v2.18.0): este archivo aparece en su salida como
> **excluido con su razón**, nunca como gobernado ni como vencido. No es un contexto gobernable: es la nota
> de capitalización de una sesión de cura.
>
> **Dueño de las lecciones:** `context/CONTEXT-JEV-CURA-B2-1-2026-10-09`. **Procedencia medida:** los crudos
> `05-`, `06-`, `07-`, `08-`, `10-`, `11-`, `12-` y `13-` de
> `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/CURA-B2-1-2026-10-09/`, y los commits `ec69570` (cura del
> runner y re-apunte del gate) y `fb13108` (sello del push), rango empujado `5249aed..fb13108`.

## 1. Lecciones capitalizadas (formato qué pasó / por qué / qué lo previene)

- **L-JEV.C1 — Una deuda de contabilidad no es una fila: es una familia que se ramifica por quién produce cada número, y cerrar el emisor no cierra a los hermanos.** / Qué pasó: `B2-1` se abrió con un enunciado concreto («el informe no compara `usage_normalized` contra los techos ni publica `cost_calculated`/`cost_billed`»). Al implementar el emisor aparecieron tres hijas con dueño distinto: `B2-1c` (el exceso no lo publicaba nadie), `B2-1e` (`reservar_presupuesto` cortaba por llamadas y reintentos pero nunca comparaba los tokens **observados** antes del envío siguiente) y `B2-1d` (la cuenta de etapa la persistía solo `run`, así que un brazo despachado por un arnés contaba en su memoria y no publicaba). Con las cuatro curadas, dos números que la documentación repetía resultaron falsos: el rebase del techo congelado de 139 era de **dos** brazos —jev 145 (+6) y el comparador deepseek 158 (**+19**)— y la cuenta publicada decía **2 llamadas cuando la real al cerrar era 4**. / Por qué: cada fila se abrió mirando un artefacto distinto (informe, ledger, `consumo.json`, registro del arnés) y nadie re-midió el resto de la familia; el escritor de la cuenta y el lector del arnés no eran el mismo código, de modo que la cifra publicada era la foto del primer brazo y el instrumento que debía delatar la diferencia no existía. / Qué lo previene: (1) cuando una cura cierra una fila de contabilidad, en la misma sesión se barre el **número** y sus vecinos de familia por todo el corpus, no solo el ID de la fila — así nació el censo de citas vencidas de esta tanda (crudo `12-`); (2) contabilidad y publicación son un solo acto: `registrar_envio_en_cuenta` suma y escribe `consumo.json` juntos, porque «quien cuenta» y «quien publica» separados fabrican esta misma bug; (3) el estampado dice la cifra rectificada **y** su antecedente, nunca la cifra sola.

- **L-JEV.C2 — Un gate de pre-commit que lee `HEAD` está leyendo el padre del commit que se intenta: con derivados divergentes corta el repo entero y no puede aprobar su propio fix.** / Qué pasó: el check `[8/8]` del hook corría `verify_packs_in_committed_tree.py` con su default `--rev HEAD`. En un pre-commit HEAD **es el commit anterior**. Como `5249aed` movió la fuente proyectada de los briefing packs sin regenerar los derivados, HEAD estaba divergente y el hook cortaba **todo** commit del repo — incluido el commit que reparaba esa divergencia, que se autocortaba. Medido en el árbol staged: `--rev HEAD` → DIVERGE/EXIT 1, y el mismo verificador sobre el índice materializado → 5/5 reproducidos, 0 divergentes, EXIT 0. / Por qué: el verificador fue escrito asumiendo «el árbol ya commiteado», que es cierto después del commit y falso antes; nadie separó las dos posiciones del reloj, y el gate quedó condicionado a que la cura que debía aprobar ya estuviera aprobada. Es un deadlock de auto-referencia, no un defecto de contenido. / Qué lo previene: (1) en un pre-commit se materializa el árbol del índice (`git write-tree` + `git commit-tree -p HEAD`) y se verifica **ese** árbol; la caída a HEAD existe pero imprime AVISO y no apaga ningún corte; (2) gobernar por test la identidad hook-instalado ≡ hook-versionado: un fix en `scripts/git_hooks/pre-commit` que no pasa por `install_git_hooks.py` no se ejecuta en ninguna corrida, así que el diente de identidad es lo que convierte el edit en comportamiento; (3) ante un gate rojo, la primera pregunta es **a qué árbol está mirando**, no «qué contenido está mal».

- **L-JEV.C3 — Un `load_dotenv()` en el import del entry point rompe la premisa de los tests de brazo, y el rojo que produce se atribuyó mal durante una tanda entera.** / Qué pasó: un test del brazo comparador, escrito sobre la premisa «no hay credencial», salía verde en su archivo y en la selección del piloto y caía en la suite grande. Se había registrado como «dependiente del orden de colección» (REL-5/D5). Medido con el orden invertido: **también cae**. El disparador tiene nombre y mecanismo: `tests/quality_gates/test_fase_d_veredicto_canonico.py` importa `main`, y `main.py:17` ejecuta `load_dotenv(env_path)` al importarse, inyectando `DEEPSEEK_API_KEY` en `os.environ` (comprobado **solo por presencia**: `False` antes de importar `main`, `True` después; nunca se imprimió el valor ni su longitud). / Por qué: la credencial la resuelve el entorno del proceso, no el test; el entry point carga configuración como efecto de lado de importarse, y cualquier selección que lo importe hereda un entorno que ya no es el premisado por el test. La atribución falsa («es del orden») vivió una tanda porque nadie invirtió el orden para medir: un rojo mal atribuido envejece mejor que un rojo mirado. / Qué lo previene: (1) hermeticidad del brazo: borrar las credenciales de proveedor en un fixture autouse de `tests/quality_gates/jev_pilot/conftest.py` y gobernar el par que hoy cae (esa cura es REL-5, declarada **terminal por decisión del operador**, con línea propia en el mandato de esta sesión); (2) antes de atribuir un rojo al orden de colección, invertir el orden y medir — la atribución es una hipótesis, no un hecho; (3) verificar este tipo de hallazgos por presencia y por nombre de variable, nunca imprimiendo el valor.

## 2. Qué NO se capitaliza aquí, y por escrito

- **El incidente del clasificador que escribe pese al bloqueo.** En esta sesión tres ediciones reportadas como
  bloqueadas escribieron igualmente y la anotación estampada quedó **triplicada**, con un `⟧` perdido del
  bloque hermano. Se midió, se curó y se registró en el crudo `11-` §3 («copias antes: 3 · copias después: 1 ·
  aperturas 14 = cierres 14»). No sube a lección con ID porque aún no tiene dueño de instrumento: la regla
  candidate —«un bloqueo notificado no prueba que la herramienta no escribió; se cuenta el resultado en
  disco»— necesita un verificador que la haga cumplir, no una nota.
- **La flacuencia del CLI de QMind** ya está capitalizada (deuda B2-4 y su cura del 2026-10-05: el rojo manda
  sobre la abstención, y una fuente que no baja se publica como `NO-EVALUABLE`, nunca como `VENCIDO`).
- **Las hermanas no curadas.** `B2-2`, `B2-3`, `B2-5` y las filas `REL-1…REL-5` siguen donde estaban. Que esta
  hoja cierre la familia B2-1 no se lee como «la deuda del plan está cerrada», y el censo `12-` lo lista.
- **El CHANGELOG vencido.** `CHANGELOG.md:764-765` afirma en presente que el informe no publica contabilidad y
  fija el exceso en un solo brazo: queda **vencido y sin curar**, con dueño — quien cierre el próximo release,
  que es donde el CHANGELOG se re-ancla. No se editó aquí porque esta sesión no mueve versión.
