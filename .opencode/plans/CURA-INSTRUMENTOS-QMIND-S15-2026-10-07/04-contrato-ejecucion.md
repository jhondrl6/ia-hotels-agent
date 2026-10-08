# Contrato de ejecución — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07)

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro (`01-plan-maestro.md`) y las filas
pertinentes de `00-lecciones-capitalizadas.md`. Este archivo **no** reemplaza a
`.agents/workflows/phased_project_executor.md`: concreta su aplicación a este plan. Si contradicen al executor,
manda el executor y la fase lo declara.

## Límites y precedencias

- **Una fase por sesión (R1).** Esta sesión preparó documentos; cada fase posterior requiere su propia sesión y
  su mandato. Ningún prompt autoriza empezar la siguiente.
- **Fases intermedias no tocan:** `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, `ROADMAP.md`, el workflow, los
  hooks, los umbrales de publication gates ni el pipeline. Ninguna fase de este plan libera versión: eso
  pertenece a FASE-RELEASE con la versión que dicte el operador.
- **Prohibido editar cualquier documento de** `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/`
  (plan cerrado, archivado y publicado) ni su evidencia. Se leen y se referencian. Su deuda S-3 del hermano ya
  pidió una errata en ese archivo y **no** se la cobra este plan.
- **No se propaga material del cliente** a documentación, commits ni al notebook. La receta canónica del padre,
  revalidada en su registro: sustituir identidades a nivel de **bytes** con `assert count(old) == N` y prueba de
  sha inverso (revertir las sustituciones reproduce el sha del crudo). Su arnés vive en
  `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-RELEASE/sanear_copia.py` — **se lee como referencia, no se
  copia ni se ejecuta sobre el árbol del padre**.
- **No se lee ni se imprime ningún valor de secreto.** Las respuestas del CLI `qmind` traen `originUrl` y
  `metadata.originalFileUri` con credencial y firma de object storage: si una salida se archiva, se redactan
  esas líneas y se conservan `id`, `title`, `status`, `metadata.fileSha256` y `fileSize`. Un enlace firmado
  redactado a medias es igualmente una fuga.
- **`qmind source delete` no se invoca en ninguna fase.** Borrar contenido publicado es irreversible y exige
  decisión escrita aparte del operador (AC6, maestro §2 DA-CIM.4).
- **Evidencia nueva, solo bajo** `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-<ID>/`. Ningún arnés
  apunta por constante al directorio de otra fase ni del plan padre. **No se escriben archivos `.py` bajo
  `evidence/`**: hoy el wiring los ampara por exclusión declarada (medido en el quick de apertura: `evidence`
  bruto=155, versionada=155), así que la tentación de dejar un arnés ahí es un riesgo que este plan no corre —
  los arneses van en `tests/` o se ejecutan en `tmp_path`.
- **Commit, L3 y push** solo con instrucción **literal** en el chat de la sesión correspondiente. El push exige
  además la revisión profunda L3 antes, y una selección de formulario no vale como confirmación. Sin
  autorización: se deja el árbol sin commitear y se declara — los cinco cortes se sostienen sin commit.
- **Un permiso negado no se evade ni se reintenta.** Si el clasificador niega la subida, la descarga o la
  lectura de un artefacto, la fase registra la denegación con el motivo que imprimió y cierra con el estado
  que le corresponde (NO-EVALUABLE o PENDIENTE-AUTORIZACION), no con un verde.

## Inicio de cada fase

1. Leer su prompt, `01-plan-maestro.md` §1 y §4, `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md`
   §2 y §4, `dependencias-fases.md` y el workflow canónico.
2. **Re-medir antes de escribir la primera línea:** `git log --oneline -3`, `git rev-parse HEAD`,
   `git rev-parse origin/master`, `git status --porcelain -uall` y `python scripts/run_all_validations.py --quick`.
   Las líneas del maestro §1 se re-anclan al HEAD de la sesión: dos de sus filas ya caducaron entre el mandato y
   la preparación. Los archivos untracked ajenos **no** se tocan, se declaran.
3. Revalidar por símbolo los anclajes que el prompt cita (R2.2: se citan símbolos, nunca números de línea). Si
   un símbolo cambió de nombre o de archivo, se corrige la cita en el prompt y se avisa en la evidencia.
4. Verificar la firma real del instrumento antes de usarlo (`--help`, o `argparse` leído): AC5 existe porque se
   midió una bandera que sí funciona y otra que no.
5. Tomar PRE antes de editar código o tests, sobre la selección literal que se va a comparar, con el intérprete
   declarado y `EXIT=$?` **dentro** del archivo. Esperar el PID real: una notificación de segundo plano informa
   el código de la cadena shell, no el del pytest.

## R2 — presupuesto e instrumento

Presupuesto de referencia por sesión: **60 `tool_use` al corte que la sesión tenga autorizado**. El instrumento
canónico (`evidence/FASE-D/measure_iterations.py`) está **FUERA DE SERVICIO (R2.1)**: pide el transcript del
cliente y su acceso está denegado (medido el 2026-10-07, R2.1 del mandato). No se reintenta para “ver si hoy
va”. Cada fase cierra con auto-reporte **en la unidad usada** (`tool_use`, `ids únicos`, lo que su cliente mida)
y declara que no es comparable con las que usaron el instrumento. No se mezcla unidades en un total y no se
reporta cumplimiento estimado. Un exceso produce checkpoint y fase INCOMPLETA, no una segunda fase.

**Qué corte se toma.** Con commit autorizado: hasta el commit de código. Sin esa autorización —caso normal de
este plan hasta que el operador la dé—: hasta **«listo para revisión»**, declarándolo. El commit no es condición
de ningún corte (executor, proceso común del bloque B).

## Tests, mutantes y evidencia

- **Python:** `./venv/Scripts/python.exe` es el intérprete del proyecto; si una selección corre con otro
  intérprete se declara cuál (la corrida de preparación usó el Python del sistema, 3.13.3, porque la selección
  no importa módulos del proyecto). No se reinstalan dependencias para hacer funcionar un subagente.
- **PRE/POST** de la **misma** selección y entorno, en `tests_baseline_pre.txt` / `tests_baseline_post.txt`,
  con exit code y las sumas de `failed`/`passed`/`skipped`/`xffailed`. La resta se comprueba y se publica en
  `baseline-pre-post.md`: `suma_post − suma_pre == tests nuevos de ESTA fase`. Una resta 0 con tests nuevos
  declarados es baseline contaminado y la fase no cierra en verde (R2.7).
- **Ninguna aserción existente se re-baja para conseguir verde.** Los 23 dientes de
  `tests/test_validate_qmind_writeback_escritura.py` y los 4 de
  `tests/test_build_lesson_index_s15_fecha_versionada.py` viajan intactos salvo que la fase demuestre con un
  mutante que la aserción vieja afirmaba una propiedad **falsa**, y entonces se re-escribe con su registro en el
  mismo commit (L-G3), nunca se debilita.
- **Prohibido tocar la numeración de los checks** de `run_all_validations.py` sin re-atar antes los dos dientes
  que leen la **fuente** del runner (`test_el_check_del_runner_invoca_con_strict_y_trata_el_dos_como_estado_propio`
  aserta `cuerpo.count("passed=True") == 1` dentro de `_check_qmind_writeback`;
  `test_el_check_queda_cableado_al_modo_completo_y_no_al_rapido` aserta la posición tras el
  `if not self.quick:` de `run_all`). Medido al capitalizar L-V2.3.
- **Todo AC detector o bloqueante cierra con mutation check (R2.8)** sobre el símbolo real
  (`verificar_contenido`, `registrar_publicacion`, `do_upload`, `cuerpo_del_plan`, `main`), en copia temporal o
  proceso aislado, nunca en el worktree vivo durante PRE. Se archivan **las dos salidas** (rojo con el guard
  apagado, verde con el fix) y la restauración verificada por sha256. Se ancla la **aserción que pierde** y la
  razón del fallo, no el token que el guard apaga; con dos guards sobre el mismo token, se afirman las dos.
- **Los controles negativos se ejecutan sobre el instrumento versionado** (`git show <rev>:<ruta>` y correr
  ese blob), no reimplementando el defecto dentro del test. La revisión fija del control S15 es `6b02532`;
  re-ancorarla a HEAD está prohibido por AC8.
- **Un verde aditivo necesita oportunidad de perder:** si la población de un censo está vacía, el diente que lo
  afirma es verde vacío y se declara. Ningún mutante se conforma con `ast.parse`.
- **Tres estados (R2.9)** en todo lector nuevo o curado: sin hallazgos (con su denominador), ausente (con la
  ruta buscada), lector fallido (con el motivo). Ningún camino los colapsa; ningún `except` devuelve el valor
  favorable. La abstención **nunca** se pinta de VENCIDO y el rojo manda sobre la abstención (contrato D2 del
  hermano, que AC2 conserva).
- **No auditar el verde con el instrumento que lo produjo:** el `[17/18]` curado no certifica su propio cierre.
  FASE-RELEASE corre el modo completo y archiva su crudo con el estado de cada check.
- **Cada verde lleva la etiqueta del árbol donde corrió** (L-VCF-15). Un verde del árbol de trabajo no sustituye
  la prueba en el árbol del commit; si la fase commitea, la verificación se repite sobre el árbol del commit.

## delegate_task / subagentes

Este plan es de **ejecución directa**: el agente principal decide y edita. Se permite delegar solo inventarios
`read-only` sin escritura (censos de rutas, listado de símbolos, conteos por el método canónico), con el brief
inline: objetivo, archivos permitidos y prohibidos, prohibición de ejecutar pytest, de mutar, de tocar `git`,
y de iniciar fases futuras. Los datos que la delegación devuelve **se re-verifican** antes de publicarse
(precedente medido del padre: una cifra traída por subagente sin re-medir obligó a retractar cuatro documentos).
Las mutaciones, los controles negativos, las corridas de cierre y todo comando `git` son del agente principal.

## Cierre incremental obligatorio de cada fase

Forma parte de la tarea 4 del prompt; no se difiere a RELEASE.

1. Marcar el checklist propio (`06-checklist-implementacion.md`), el estado del prompt, `dependencias-fases.md`
   y el README del plan con el estado **real** (INCOMPLETA con checkpoint si falta algo).
2. Actualizar `09-documentacion-post-proyecto.md` (Secciones A/B/D/E — **D es la fuente del número por fase**) y
   `10-analisis-post-implementacion.md` (fila de la fase, lecciones nuevas de la serie `L-CIM` o «sin lecciones
   nuevas», métricas **referenciando** 09 §D y la corrida, seguimientos, decisiones).
3. Actualizar `00-lecciones-capitalizadas.md`: en §2 la columna «Qué cambia» con lo que **realmente** pasó; si la
   fase descubrió una fuente que el Paso 0 no consultó, su consulta y su descarte; §4 con el estado real de la
   cobertura. Sin cuota de lecciones.
4. Nota de fase en `CHANGELOG.md` **bajo `## [Sin publicar]`** y en `docs/GUIA_TECNICA.md`. No darle encabezado
   de versión a una fase intermedia: eso inventaría una release.
5. `scripts/log_phase_completion.py` con las tres obligatorias `--fase`, `--desc`, `--fecha` (YYYY-MM-DD real de
   **esa** fase), `--archivos-mod` y `--tests` **medidos después** de los fixers derivados y contando lo que
   `git` cuenta (los renombrados son rutas, no un conteo). El escritor es aditivo: **no se vuelve a correr sobre
   una fase ya cerrada**; los deltas se declaran en `--nota`. Fases intermedias sin `--release`.
6. **Regenerar los derivados que la propia edición venció, con su escritor, y como último paso**:
   - `python scripts/build_lesson_index.py` — cualquier `.md` de `plans/` que nombre un ID vence el conteo de
     citas y el dueño con su ruta (R2.10). Su `--check` es `[6/8]` del hook y bloquea el commit si va vencido.
   - `python scripts/validate_opencode_refs.py --fix` — si entraron rutas nuevas bajo `.opencode/`.
   - `python scripts/validate_plan_citations.py --update-baseline` — solo si la fase añadió citas históricas;
     es un **acto visible de quien documenta** y se declara en el cierre, nunca un silencio.
   - `python scripts/validate_wiring.py --write-report` — solo si entran archivos `.py` **nuevos** al árbol
     versionado. Editar un `.py` existente no añade población, pero el `--check` manda: si vence, se regenera
     con su escritor. EXIT 3 del wiring no es un rojo de cableado, es un problema del insumo.
   - `python scripts/doctor.py --regenerate-domain-primer` al cerrar cada fase de **implementación** (con su
     mandato para escribir el derivado; si no lo tiene, se declara el checkpoint), y `doctor.py --context` solo
     en FASE-RELEASE. Nunca a mano.
7. `python scripts/validate_document_integration.py` y `python scripts/run_all_validations.py --quick`; si la
   fase tocó la capa de contenido del write-back, también el modo completo con su crudo archivado. El número que
   imprime la corrida **no se copia** a ningún documento del plan: se referencia el comando.
8. Revisar `git diff` y `git status`, cerrar el auto-reporte de presupuesto y terminar la sesión. No iniciar la
   fase siguiente.

## Orden del cierre documental y la subida remota

El write-back **no** es consecuencia automática del cierre: es una operación remota con autorización literal
propia (L-QW.4: se desglosa en entrega offline y aceptación remota). Sin esa autorización, la fase entrega el
paquete offline completo —copia saneada versionada con su prueba de sha inverso, título propuesto, sha del
cuerpo— y lo declara `PENDIENTE-AUTORIZACION`. Con ella, el orden R2.10 es fijo y no se permuta:

```bash
python scripts/validate_qmind_writeback.py --upload <PLAN>          # 1. SIEMPRE con el plan aun en raiz
python scripts/build_lesson_index.py                                 # 2. el plan cerrado, consultable
git mv .opencode/plans/<PLAN> .opencode/plans/Archives/              # 3. archivar, por ultimo
python scripts/build_lesson_index.py                                 # 3b. publica la ruta NUEVA
python scripts/validate_opencode_refs.py --fix
python scripts/validate_plan_citations.py --update-baseline          # acto visible, declarado
python scripts/run_all_validations.py --quick                        # verde
```

Con AC5 landed, `<PLAN>` puede ir con prefijo `Archives/` para el modo verificación, pero la **publicación** se
hace siempre antes del `git mv`; archivar primero deja el hueco consumado y sin señal. La instantánea congela el
cuerpo: editar el `10-analisis` después de publicar lo deja vencido por AC2 — que es exactamente la puerta que
este plan está curando, así que la regla se respeta igual.

## Corridas y límites de certificación

Ninguna fase ejecuta `v4complete`, `v4audit`, scraping ni comandos de auditoría externa. Las operaciones remotas
de este plan son: `qmind source list` (censo), `qmind source download` (verificación de promesa, con su racha
contada) y `qmind source upload` (una publicación por cierre autorizado). **No existe segunda subida por parseo
fallido** (AC3 y DA-CIM.3, con AC4). Si la red falla, se declara NO-EVALUABLE con la racha y el crudo; no se re-intenta en
bucle ni se atribuye la caída al instrumento.
