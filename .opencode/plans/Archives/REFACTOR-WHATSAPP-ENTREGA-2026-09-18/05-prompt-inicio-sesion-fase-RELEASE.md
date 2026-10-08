# FASE-RELEASE — Documentación oficial, versionado y archivado

**Estado:** EJECUTADA 2026-10-07 (sesión de cierre). **Dependencia inmediata:** cumplida — FASE-VERIFY cerró el 2026-10-07 con dictamen y alcance explícitos, y la recuperación de AC6/AC10 se ejecutó después, offline y sin corrida. ⟦Lo que sigue es el mandato tal como se escribió; las decisiones que esta sesión resolvió con el operador están estampadas con `⟦RELEASE 2026-10-07⟧`⟧
**Complejidad técnica:** MEDIA: sincronización documental, orden de archivado y permisos.
**Scope R3:** 4 tareas, 0 comandos largos externos. Última fase; documental. **No ejecuta v4complete ni repara código.**

## Contexto e inicio

Ejecución futura con mandato propio. Lee `01-plan-maestro.md` §6 y §7; `04-contrato-ejecucion.md` §"Cierre incremental obligatorio"; `10-analisis-post-implementacion.md` con el dictamen de VERIFY; `docs/CONTRIBUTING.md`; `docs/contributing/documentation_rules.md`; `docs/contributing/validation.md` y el workflow canónico (FASE-RELEASE).
Versión objetivo: **la decide el mandato de esta fase con el operador** y se usa como `$VERSION_AUTORIZADA` en los comandos. ⟦RELEASE 2026-10-07: el operador autorizó **4.79.0** con propagación a los archivos gobernados; codename *WhatsApp verificado, orden real y entrega única de Don Alfonso*; `release_date` y `date` = 2026-10-07⟧. ⟦Puesta al día 2026-10-06: aquí constaba «Versión objetivo propuesta: **4.78.0**», y ese número ya está **ocupado**: `VERSION.yaml` publica `version: "4.78.0"` con `release_date: "2026-09-25"` (medido con `grep -nE "version|release_date" VERSION.yaml`) y el `CHANGELOG.md` lo encabeza como `## [4.78.0] - Gobernanza, costura, pertinencia y carga medida — 2026-09-25`, release del plan `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`. Proponer 4.78.0 inventaría una release ya hecha; el maestro y `10-analisis-post-implementacion.md` llevan su anotación datada⟧. La fuente única de la versión sigue siendo `VERSION.yaml`, y su propagación a los archivos gobernados es `sync_versions.py`. Si VERIFY dictaminó la meta de entrega como parcial o FALLA, RELEASE **publica ese límite** y no cierra como éxito integral.
Permisos: configuración central, commit, push, tag y subida a QMind requieren autorización expresa para esa acción, en este turno. Un permiso negado no se evade ni se reinterpreta.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-V.4 | VERIFY registra fallos con dueño; no los remedia. | RELEASE refleja el dictamen y los dueños; no convierte un FALLA en nota de éxito ni abre fixes. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | Los límites de muestra (un hotel, una corrida) se publican en la documentación oficial, no solo en el análisis interno. |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | Solo flags existentes y verificados (`sync_versions.py`, `log_phase_completion.py --release`, `doctor.py`, `build_lesson_index.py`, `validate_qmind_writeback.py`); no inventar parámetros ni rutas. |

## Tareas

1. **Diagnóstico y versionado.** Ejecutar `doctor.py --context` y `--status` para regenerar `.agent/SYSTEM_STATUS.md`; actualizar `VERSION.yaml` a la versión autorizada y propagar con `sync_versions.py` a los archivos gobernados. El rojo de Version Sync **no se hereda como prerrequisito**: re-medir el check en el quick de apertura de esta sesión (es el check `[3/13]`, etiqueta `Version Sync`; el número lo imprime la corrida). ⟦Puesta al día 2026-10-06: la cláusula mandaba «resolver el rojo preexistente de Version Sync registrado en el maestro §7» y **no tiene referente vivo** — ese rojo se cerró por re-medición el 2026-09-19, como declaran el maestro §7, `dependencias-fases.md` y `README.md` de este plan⟧. Si el check diera rojo en la corrida de esta sesión, se resuelve **solo con autorización expresa del operador** para tocar configuración central; sin ella, checkpoint con el rojo visible, no sincronización encubierta.
2. **Documentación oficial.** Consolidar CHANGELOG (Objetivo / Cambios / Archivos Nuevos / Archivos Modificados / Tests) con las subsecciones de fase ya escritas — que están bajo `## [Sin publicar]`, la forma vigente del archivo, y es aquí cuando se le da encabezado de versión a ese bloque, nunca antes ⟦Puesta al día 2026-10-06: así queda alineado con `04-contrato-ejecucion.md` paso 3⟧ —, nota técnica por fase en `docs/GUIA_TECNICA.md`, REGISTRY y `09-documentacion-post-proyecto.md` completo. DOMAIN_PRIMER en RELEASE se **verifica** (`doctor.py --context`/`--status`); **regenerar con su writer** (`doctor.py --regenerate-domain-primer`) es operación de cada cierre de fase de implementación (C, D, E, F, H), no de esta. ⟦Puesta al día 2026-10-06: este párrafo mandaba regenerar **también aquí** y lo presentaba como paso previo de la verificación; eso contradice la regla canónica del executor §E7 y de `docs/CONTRIBUTING.md` Paso 5b, que este mismo plan ya aplica en `04-contrato-ejecucion.md` paso 4. Si el operador quiere una regeneración en RELEASE, es instrucción expresa⟧. Lo que sí procede en esta fase: si alguna fase de implementación cerró sin regenerarlo por falta de mandato para escribir el archivo, esa regeneración **pendiente** se hace aquí solo con instrucción expresa, y si no la hay se arrastra el checkpoint declarado. Verificar y regenerar son dos operaciones distintas; ninguna sustituye a la otra. No editar a mano. `AGENTS.md`, `.cursorrules` y demás contexto global solo con instrucción explícita del operador en este turno.
3. **Validación y write-back.** Ejecutar validaciones documentales y de ecosistema; obtener TOTAL PASS real dentro del alcance autorizado o mantener la fase INCOMPLETA con los rojos listados. Write-back durable solo si está autorizado: revisar **qué** sube (sin material del hotel ni secretos), comprobar frescura y recordar que un SKIP por título no prueba publicación del cierre actualizado; si el contenido cambió, acordar título nuevo antes de subir. Sin autorización o sin acceso: checkpoint explícito del cierre, no simular éxito. ⟦Alineado el 2026-09-24 con `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` y con la orden de calidad §4.C⟧: **la validación es el cierre offline de esta fase y no depende de ninguna operación remota**; el write-back es un momento aparte, con autorización literal y presupuesto propios. Estar en el orden R2.10 no lo habilita. Lo que se publica sin red es todo lo demás; lo remoto queda `PENDIENTE-AUTORIZACION` con causa, y un resultado parcial no se promociona a cierre completo.

   **Tres condiciones mecánicas del write-back, medidas el 2026-09-20 en el propio validador y en R2.10 del executor** — no son advertencias genéricas:

   1. **Ya existe una ingesta de este plan, con el título de la era G:** `10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (lecciones aprendidas y decisiones)`, fuente `01a0bfc9-5f5a-783e-9492-16367bbff596`, subida y verificada por descarga al cerrar FASE-G. Correr `--upload` sin más responde **SKIP** y deja en el notebook el contenido de G creyéndolo el cierre. ⟦AC6-entrega de `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`, ejecutada el 2026-10-07: el writer **sí** expone `--title` y `--file`, así que este prompt **manda el writer** y deja de depender de que alguien recuerde un título pre-acordado ni de invocar el CLI a mano. El comando de cierre es:

      ```bash
      ./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload REFACTOR-WHATSAPP-ENTREGA-2026-09-18 \
        --file <copia saneada y versionada bajo el repo> \
        --title "10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (cierre $VERSION_AUTORIZADA, lecciones finales $FECHA_CIERRE)"
      ```

      Con `--title`/`--file` presentes se publica **ese** documento con **ese** título: la copia queda como **instantánea versionada** en `.opencode/qmind-writeback/instantaneas/` con su sha256, la entrada vigente anterior del mismo plan pasa a `reemplazada` (con `reemplazada_por`), y `--file` fuera del repo corta antes de subir nada. Re-usar un título ya vigente con contenido distinto es `[FAIL]`, no un duplicado silencioso: el backend no sobrescribe. La decisión que el mini-plan dejaba abierta —**marcar** la fuente anterior o **borrarla**— se tomó por **marcar**; `qmind source delete` sobre contenido publicado es irreversible y sigue pidiendo decisión escrita aparte del operador.

      **Dónde cae dentro de esta fase, y por qué se añade una razón nueva**: el write-back va **después** de que el contenido de este `10-analisis` quede final —incluidos los estados finales de la tarea 4, que también toca 09/10— y **antes** del índice y del `git mv`, que es el orden de la tarea 4. La novedad de esta entrega: la instantánea **congela el cuerpo**, así que cualquier edición del `10-analisis` posterior a la subida lo deja `[VENCIDO]` —la capa de contenido compara sha contra el cuerpo del repo, no la existencia del título— y la corrida completa que certifica el cierre sale roja por eso, no por un olvido de ingesta. Si hace falta tocar el cuerpo después de publicar, se **re-publica con título nuevo** (la anterior queda marcada como reemplazada); re-subir el mismo título con contenido distinto es `[FAIL]` explícito.⟧ Si el mini-plan no hubiera llegado a ejecutarse, aplica su §5 (CLI directo con el título nuevo, contenido saneado y verificación por descarga + sha256) sin declarar la fase incompleta por ese motivo.
   2. **El writer no sanea.** `do_upload()` toma el `10-analisis` por su ruta y `upload_source()` ejecuta `qmind source upload --file` sin reescritor: hay que producir y revisar antes una copia saneada, como hizo G (cinco identidades del cliente sustituidas con `assert count(old) == 1` a nivel de bytes y prueba de sha inverso). Verificar por **descarga + sha256**, nunca por título.
   3. **El orden R2.10 no se permuta, y el único check que lo cubre es condicional** (rectificada el 2026-09-20: este prompt decía que no existía ningún check — era falso, ver `evidence/…/FASE-G/qmind-writeback-G.md`): `scripts/run_all_validations.py` invoca el validador como **[17/18]** (cola del método `run_all()`, dentro de `if not self.quick:`), pero **solo en el modo completo** — nunca en `--quick` y nunca en un hook. ⟦Re-anclado el 2026-10-06: se publicó como `[15/15]`, la etiqueta que le correspondía cuando el modo completo llegaba a 15; hoy es **[17/18]** y el denominador subió a 18 porque nació el check hermano **[18/18]** de frescura `CONTEXT` (`verify_qmind_context_freshness.py`), que tampoco corre en `--quick`. Errata corregida el 2026-10-07 dentro del diff de AC6-entrega: este punto citaba el método del runner como `run()`, símbolo que no existe; el vigente es `run_all()`. La misma cita vive en el `10-analisis` del padre (fila L-ENT.14) y **esa queda con dueño: el RELEASE del padre al tocar su `10-analisis`**, no se corrigió aquí porque el archivo está sucio por el cierre de VERIFY⟧. Tres límites tenía su código, medidos en la FASE-UNICA del 2026-10-07: (a) escanea **solo `Archives/`**, así que con el plan en raíz no produce señal — **sigue vigente, es diseño y su dueño es el `git mv` de esta fase**; (b) sin el CLI `qmind` disponible degradaba a exit 0 y el resumen lo publicaba como PASS — **curado**: el check lo invoca con `--strict` y el código 2 es el estado propio `NO-EVALUABLE`, que corta rojo y se nombra; (c) decidía **por título**, de modo que la fuente obsoleta de la era G satisfacía el check — **curado**: la capa de contenido compara el sha de la **instantánea versionada** contra el cuerpo del plan y contra lo que el notebook entrega (`metadata.fileSha256` como primera vía, la descarga como verificación de esa promesa, `PROMESA-ROTA` si el índice miente), y una segunda fuente del mismo plan sin marca de reemplazo corta `[DUPLICADO-VIGENTE]`. Consecuencia que esta fase debe conocer: **mientras `.opencode/qmind-writeback/registro.json` no tenga entradas, `[17/18]` sale NO-EVALUABLE (rojo) en el modo completo** — es el verde hueco que se cerró, no una regresión; la primera publicación por `--upload` con el writer lo registra y lo vuelve verde. Correr el modo completo **después** del write-back y del `git mv` es la corrida que certifica el cierre.
4. **Archivado y cierre final.** Regenerar `build_lesson_index.py` y comprobar `--check`; actualizar estados finales de checklist, dependencias, índice del plan, 09/10 y de este prompt. Archivado en el orden obligatorio **write-back → índice → `git mv`** del directorio de este plan hacia `.opencode/plans/Archives/<este-plan>/` (destino creado por esta fase; no existe antes). Commit, tag y push solo con autorización expresa; si se autoriza push, ofrecer antes la revisión profunda de seguridad vigente y exigir confirmación escrita del operador. Sin autorización: entregar checkpoint con lo pendiente.

## Comandos

Sustituir variables por datos medidos antes de ejecutar:

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE --desc "REFACTOR-WHATSAPP-ENTREGA: release documental, versionado y archivado" --fecha "$FECHA_CIERRE" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs --release "$VERSION_AUTORIZADA"
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
./venv/Scripts/python.exe scripts/validate_document_integration.py
./venv/Scripts/python.exe scripts/run_all_validations.py
```

`--fecha` = fecha real de cierre; si el registro es tardío, `--nota` con el motivo. `log_phase_completion.py::parse_args` la declara obligatoria junto con `--fase` y `--desc` y la valida como fecha de calendario; `$FECHA_CIERRE` es variable a sustituir, como `$VERSION_AUTORIZADA`. ⟦Puesta al día 2026-10-06: el comando llevaba `--release 4.78.0`, versión ya liberada por `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`, y no llevaba `--fecha`⟧.

El flag `--release` es exclusivo de esta fase; ninguna fase intermedia lo usa, y su valor lo aporta el mandato de la sesión con el operador — no se fija en este prompt. `run_all_validations.py` sin `--quick` incluye tests: ejecutarlo con notificación de término y esperar finalización real del proceso antes de dictaminar.

**Derivados vencidos: un rojo puede no ser del cambio.** Si la fase añadió evidencia `.py` o editó documentos del plan, correr el fixer del derivado que cayó y **re-correr la validación**:

- `[8/13]` OpenCode References → `./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix`
- `[9/13]` Plan Citations → `./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline` (acto visible: lo hace quien documenta; no silencia un rojo)
- `[11/13]` Wiring → `./venv/Scripts/python.exe scripts/validate_wiring.py --write-report`
- `[13/13]` Packs → `./venv/Scripts/python.exe scripts/build_phase_briefing.py`

Las cuatro etiquetas son las que imprime el **modo rápido**; en el modo completo solo sus cinco checks exclusivos se etiquetan con denominador 18. El número lo imprime la corrida: no se copia a ningún documento.

## Delegación viable

`delegate_task`/`Agent` permitido para trabajo documental acotado dentro de la allowlist autorizada (CHANGELOG, GUIA_TECNICA, REGISTRY, 09/10, índices), con brief que prohíba tocar VERSION, configuración central, secretos, datos del hotel, evidencia histórica y fases ya cerradas. El principal decide versionado, permisos, archivado y cualquier operación git; verifica diff y artefactos antes de cerrar. VERIFY no se rehace aquí.

## Reglas

- No ejecutar v4complete, ni tests de producto para "mejorar" un AC, ni cambios de código: un defecto descubierto ahora se registra con dueño y disparador para otra sesión.
- No declarar certificación universal a partir de un hotel; los límites de VERIFY se conservan literalmente en la documentación pública.
- No modificar `evidence/FASE-P4/` ni reescribir informes históricos; F-P4.3 queda enlazado por su ID, no duplicado.
- No imprimir secretos ni propagarlos a documentación, QMind o commits; el estado de la credencial se publica sin su valor.

## Presupuesto y checklist

Referencia **60 tool_use**; fase sin código de producto: corte **documental** declarado aparte, sin fingir commit de código y **sin tratar la ausencia de commit como un corte «no consumado»** — los cinco cortes se sostienen sin commit y el commit es posterior, opcional y con autorización expresa. Instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`; sin transcript o con acceso denegado, **FUERA DE SERVICIO (R2.1)** con auto-reporte por unidad.

- [x] VERIFY cerrada y su dictamen reflejado sin suavizar; límites de muestra publicados. AC6 y AC10 constan en
  FALLA en el CHANGELOG (`## [4.79.0]` §Límites publicados), en la nota técnica y en el `10-analisis`; la
  recuperación de esos dos ACs se publica con su límite (offline, sin corrida, el ZIP del 2026-10-07 conserva los
  dos defectos) y no como éxito en flujo real.
- [x] VERSION y archivos gobernados sincronizados con autorización y con la versión que nombró el mandato:
  **4.79.0**. Version Sync se re-midió al abrir (quick **13/13**, `[3/13]` en verde) y no se actuó sobre él; el
  rojo que apareció después fue propio de esta sesión (`[6/13]` Document Integration por el sello de DOMAIN_PRIMER
  contra la versión nueva) y se resolvió con la regeneración autorizada.
- [x] CHANGELOG/GUIA_TECNICA/REGISTRY/09 completos. DOMAIN_PRIMER **verificado** con `--context`/`--status` y
  **regenerado con su writer por instrucción expresa del operador** (era la regeneración pendiente que C, D, E, F,
  H y E2E arrastraban desde FASE-C); las dos operaciones quedan declaradas por separado, no editado a mano.
- [ ] Validaciones con TOTAL PASS real en el alcance autorizado, o fase INCOMPLETA con los rojos listados. Se
  publica con su crudo en `evidence/…/FASE-RELEASE/`: quick de apertura, quick de cierre y **modo completo
  después del write-back y del `git mv`**, que es la corrida que certifica.
- [ ] Write-back final por el **writer con `--title` y `--file`**, con el plan **aún en raíz**, copia saneada
  revisada a mano, instantánea versionada con su sha256 y la fuente de la era G **marcada** como reemplazada;
  verificación por **descarga + sha256**. En curso: la copia saneada está producida y su fidelidad probada
  (`evidence/…/FASE-RELEASE/qmind-upload-10-analisis-cierre-4.79.0-saneado.md`).
- [ ] Archivado en orden write-back → índice → `git mv`; estados finales coherentes en los cinco documentos del
  plan (README, 06, dependencias, 09/10 y este prompt).
- [ ] Operaciones git solo con autorización expresa; push precedido de la revisión de seguridad vigente y
  confirmación escrita. Autorizados: dos commits (recuperación `086ce65` y cierre documental) + L3 + push. **No
  autorizado: `git tag`**, declarado como opción rechazada.
