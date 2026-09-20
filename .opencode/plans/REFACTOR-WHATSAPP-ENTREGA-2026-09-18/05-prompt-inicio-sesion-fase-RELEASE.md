# FASE-RELEASE — Documentación oficial, versionado y archivado

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-VERIFY cerrada con dictamen y alcance de cierre explícitos.
**Complejidad técnica:** MEDIA: sincronización documental, orden de archivado y permisos.
**Scope R3:** 4 tareas, 0 comandos largos externos. Última fase; documental. **No ejecuta v4complete ni repara código.**

## Contexto e inicio

Ejecución futura con mandato propio. Lee `01-plan-maestro.md` §6 y §7; `04-contrato-ejecucion.md` §"Cierre incremental obligatorio"; `10-analisis-post-implementacion.md` con el dictamen de VERIFY; `docs/CONTRIBUTING.md`; `docs/contributing/documentation_rules.md`; `docs/contributing/validation.md` y el workflow canónico (FASE-RELEASE).
Versión objetivo propuesta: **4.78.0** (el maestro la declara propuesta; VERSION.yaml no se tocó durante la preparación). Si VERIFY dictaminó la meta de entrega como parcial o FALLA, RELEASE **publica ese límite** y no cierra como éxito integral.
Permisos: configuración central, commit, push, tag y subida a QMind requieren autorización expresa para esa acción, en este turno. Un permiso negado no se evade ni se reinterpreta.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-V.4 | VERIFY registra fallos con dueño; no los remedia. | RELEASE refleja el dictamen y los dueños; no convierte un FALLA en nota de éxito ni abre fixes. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | Los límites de muestra (un hotel, una corrida) se publican en la documentación oficial, no solo en el análisis interno. |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | Solo flags existentes y verificados (`sync_versions.py`, `log_phase_completion.py --release`, `doctor.py`, `build_lesson_index.py`, `validate_qmind_writeback.py`); no inventar parámetros ni rutas. |

## Tareas

1. **Diagnóstico y versionado.** Ejecutar `doctor.py --context` y `--status` para regenerar `.agent/SYSTEM_STATUS.md`; actualizar `VERSION.yaml` a la versión autorizada y propagar con `sync_versions.py` a los archivos gobernados. Resolver el rojo preexistente de Version Sync registrado en el maestro §7 **solo con autorización expresa del operador** para tocar configuración central; sin ella, checkpoint con el rojo visible, no sincronización encubierta.
2. **Documentación oficial.** Consolidar CHANGELOG (Objetivo / Cambios / Archivos Nuevos / Archivos Modificados / Tests) con las subsecciones de fase ya escritas, nota técnica por fase en `docs/GUIA_TECNICA.md`, REGISTRY y `09-documentacion-post-proyecto.md` completo. DOMAIN_PRIMER se regenera **solo con su writer**, según el mandato resuelto en A; no editar a mano. `AGENTS.md`, `.cursorrules` y demás contexto global solo con instrucción explícita del operador en este turno.
3. **Validación y write-back.** Ejecutar validaciones documentales y de ecosistema; obtener TOTAL PASS real dentro del alcance autorizado o mantener la fase INCOMPLETA con los rojos listados. Write-back durable solo si está autorizado: revisar **qué** sube (sin material del hotel ni secretos), comprobar frescura y recordar que un SKIP por título no prueba publicación del cierre actualizado; si el contenido cambió, acordar título nuevo antes de subir. Sin autorización o sin acceso: checkpoint explícito del cierre, no simular éxito.

   **Tres condiciones mecánicas del write-back, medidas el 2026-09-20 en el propio validador y en R2.10 del executor** — no son advertencias genéricas:

   1. **Ya existe una ingesta de este plan, con el título de la era G:** `10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (lecciones aprendidas y decisiones)`, fuente `01a0bfc9-5f5a-783e-9492-16367bbff596`, subida y verificada por descarga al cerrar FASE-G. Correr `--upload` sin más responde **SKIP** y deja en el notebook el contenido de G creyéndolo el cierre. El **título nuevo queda pre-acordado aquí:** `10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (cierre <versión final autorizada>, lecciones finales <fecha>)`. Medido en el `main()` del writer: **no expone `--title` ni `--file`**, de modo que ese título exige el CLI directo (`qmind source upload --nb … --file … --title …`) o ampliar el script. La ampliación con `--title` y un saneador es la cura de fondo y tiene plan propio: **`VERIFICADOR-ESCRITURA-QMIND-2026-09-20`**, cuyo disparador es la sesión inmediatamente anterior a esta. Si ese mini-plan no llegó a ejecutarse, aplica su §5 sin declarar la fase como incompleta por ese motivo: CLI directo con el título nuevo, contenido saneado y verificación por descarga + sha256.
   2. **El writer no sanea.** `do_upload()` toma el `10-analisis` por su ruta y `upload_source()` ejecuta `qmind source upload --file` sin reescritor: hay que producir y revisar antes una copia saneada, como hizo G (cinco identidades del cliente sustituidas con `assert count(old) == 1` a nivel de bytes y prueba de sha inverso). Verificar por **descarga + sha256**, nunca por título.
   3. **El orden R2.10 no se permuta, y el único check que lo cubre es condicional** (rectificada el 2026-09-20: este prompt decía que no existía ningún check — era falso, ver `evidence/…/FASE-G/qmind-writeback-G.md`): `scripts/run_all_validations.py` invoca el validador como **[15/15]** (cola del método `run()`, dentro de `if not self.quick:`), pero **solo en el modo completo** — nunca en `--quick` y nunca en un hook. Tres límites medidos en su código: (a) escanea **solo `Archives/`**, así que con el plan en raíz no produce señal; (b) sin el CLI `qmind` disponible degrada a exit 0 porque no corre `--strict`, o sea verde por ausencia de instrumento; (c) decide **por título**, de modo que la fuente obsoleta de la era G satisface el check y un contenido viejo pasa por cierre. Consecuencia para esta fase: correr `run_all_validations.py` **completo y con el CLI disponible, después del `git mv`** es la única corrida que pondría rojo un olvido — y ni aun así pone rojo la obsolescencia.
4. **Archivado y cierre final.** Regenerar `build_lesson_index.py` y comprobar `--check`; actualizar estados finales de checklist, dependencias, índice del plan, 09/10 y de este prompt. Archivado en el orden obligatorio **write-back → índice → `git mv`** del directorio de este plan hacia `.opencode/plans/Archives/<este-plan>/` (destino creado por esta fase; no existe antes). Commit, tag y push solo con autorización expresa; si se autoriza push, ofrecer antes la revisión profunda de seguridad vigente y exigir confirmación escrita del operador. Sin autorización: entregar checkpoint con lo pendiente.

## Comandos

Sustituir variables por datos medidos antes de ejecutar:

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
./venv/Scripts/python.exe scripts/doctor.py --status
./venv/Scripts/python.exe scripts/sync_versions.py
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-RELEASE --desc "REFACTOR-WHATSAPP-ENTREGA: release documental, versionado y archivado" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs --release 4.78.0
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
./venv/Scripts/python.exe scripts/validate_document_integration.py
./venv/Scripts/python.exe scripts/run_all_validations.py
```

El flag `--release` es exclusivo de esta fase; ninguna fase intermedia lo usa. `run_all_validations.py` sin `--quick` incluye tests: ejecutarlo con notificación de término y esperar finalización real del proceso antes de dictaminar.

## Delegación viable

`delegate_task`/`Agent` permitido para trabajo documental acotado dentro de la allowlist autorizada (CHANGELOG, GUIA_TECNICA, REGISTRY, 09/10, índices), con brief que prohíba tocar VERSION, configuración central, secretos, datos del hotel, evidencia histórica y fases ya cerradas. El principal decide versionado, permisos, archivado y cualquier operación git; verifica diff y artefactos antes de cerrar. VERIFY no se rehace aquí.

## Reglas

- No ejecutar v4complete, ni tests de producto para "mejorar" un AC, ni cambios de código: un defecto descubierto ahora se registra con dueño y disparador para otra sesión.
- No declarar certificación universal a partir de un hotel; los límites de VERIFY se conservan literalmente en la documentación pública.
- No modificar `evidence/FASE-P4/` ni reescribir informes históricos; F-P4.3 queda enlazado por su ID, no duplicado.
- No imprimir secretos ni propagarlos a documentación, QMind o commits; el estado de la credencial se publica sin su valor.

## Presupuesto y checklist

Referencia **60 tool_use**; fase sin código de producto: corte **documental** declarado aparte, sin fingir commit de código. Instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`; sin transcript o con acceso denegado, **FUERA DE SERVICIO (R2.1)** con auto-reporte por unidad.

- [ ] VERIFY cerrada y su dictamen reflejado sin suavizar; límites de muestra publicados.
- [ ] VERSION y archivos gobernados sincronizados, con autorización; rojo preexistente resuelto o visible en checkpoint.
- [ ] CHANGELOG/GUIA_TECNICA/REGISTRY/09 completos y DOMAIN_PRIMER regenerado solo por writer.
- [ ] Validaciones con TOTAL PASS real en el alcance autorizado; write-back autorizado, saneado y verificado (o checkpoint).
- [ ] Write-back final con **título distinto al de G** (el existente provoca SKIP), plan **aún en raíz**, contenido saneado revisado a mano y verificación por **descarga + sha256**, no por título.
- [ ] Archivado en orden write-back → índice → `git mv`; estados finales coherentes en los cinco documentos del plan.
- [ ] Operaciones git solo con autorización expresa; push precedido de la revisión de seguridad vigente y confirmación escrita.
