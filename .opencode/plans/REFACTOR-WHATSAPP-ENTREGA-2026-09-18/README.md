# REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Estado (reconciliado el 2026-09-24 por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, §4.C y §3).** Cerradas y empujadas: **A** (`3e97d95`), **G** (`66e17bd`), **0** (`7c6e75f`, paridad 0/0 verificada entonces) y **B**. **Contador v4complete: 0/1. Punto real de reanudación: FASE-C.**

> **Por qué esta línea vale más que la cabecera que deroga.** Hasta hoy el README decía «Pendientes sin empezar: B–RELEASE» y «Siguiente sesión: FASE-B», y su tabla marcaba B como `PENDIENTE`. Eso estaba **vencido**, no en contradicción técnica: `473ed0f` llevó el código de producto de B (su mensaje aún declaraba la fase INCOMPLETA por una decisión de alcance), `05d0cc6` **cerró B con deuda registrada** re-ancorando AC5 de D-E a **C-D** con el fixture y el test que caracterizan el pase trivial, y `7553f51` barrió las citas de push. La fila de `dependencias-fases.md` y la de `06-checklist-implementacion.md` ya lo decían. **Nadie debe leer esa cabecera antigua como una orden de repetir B**: las fases cerradas conservan su evidencia y no se rehacen. Lo que queda por hacer de B es su **deuda AC5**, y esa es insumo de C, no prerrequisito suyo.

**Revisión 2 (2026-09-19).** El plan se re-midió contra código vivo y contra una corrida real ya archivada (`output/TAREA7-2026-09-19/`, mismo hotel y URL del §5, 2026-09-19 15:01). Cuatro premisas del maestro cayeron, se añadieron **AC20** y **FASE-0**, **G adelanta a segunda sesión** y **AC19 se parte en 19a (aditivo) y 19b (diferido)**. Motivo central: la corrida medida terminó `BLOQUEADO` con ZIP suprimido **con los 13 gates verdes y readiness `READY_FOR_PUBLICATION`**, por un único hallazgo CRITICAL (`VACUOUS_RECALL`) que ninguna fase cubría y que el Knowledge Center registró el 2026-09-11 como "fix candidato fuera de este plan". Sin FASE-0, la meta de entrega de este plan era inalcanzable con independencia de B–H. Detalle en maestro §1, §2, §4 y §7.

Objetivo: alinear promesas y entrega WhatsApp con los datos realmente utilizables, impedir botones inseguros y conservar causas y evidencia de bloqueo. La meta de entrega no autoriza ocultar bloqueos legítimos ni prometer READY.

## Índice documental

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): antecedentes contrastados y límites de las consultas.
- [Plan maestro](01-plan-maestro.md): decisiones, alcance, AC1–AC20 y única corrida.
- [Contrato de ejecución](04-contrato-ejecucion.md): permisos, PRE/POST, R2 y cierre incremental.
- [Dependencias y bloqueantes](dependencias-fases.md): cadena secuencial, archivos compartidos y condiciones de avance.
- [Checklist de implementación](06-checklist-implementacion.md): estados, aceptación y controles de cierre.
- [Documentación post-proyecto](09-documentacion-post-proyecto.md): cierre documental previsto.
- [Análisis post-implementación](10-analisis-post-implementacion.md): matriz final, límites y seguimientos previstos.

Los enlaces a prompts y documentos de cierre identifican los destinos previstos del plan; esta escritura no verifica su existencia ni declara que se hayan ejecutado.

## Doce sesiones, una fase por sesión

| Orden / prompt | Objetivo | Complejidad técnica | Estado |
|---|---|---|---|
| 1 · [A](05-prompt-inicio-sesion-fase-A.md) | Baseline, ratificación de contratos (incluida FASE-0 y AC19a/AC19b) y resolución de prerrequisitos | ALTA: producto, identidad y permisos transversales | **CERRADA 2026-09-19 (`3e97d95`, empujado)** |
| 2 · [G](05-prompt-inicio-sesion-fase-G.md) | Descubrimiento AST de callers y retirada del contrato muerto. **Adelantado: es el guard de las ediciones de B–F** | ALTA: cobertura sin lista fija y firmas compartidas | **CERRADA 2026-09-20** (`66e17bd`, empujado) |
| 3 · [0](05-prompt-inicio-sesion-fase-0.md) | **Nueva.** Evidencia del veredicto serializada: recall fundado, hallazgos en el acta y hash del paquete publicado | MEDIA técnica / ALTA consecuencia: decide si puede existir un ZIP entregable | **CERRADA 2026-09-20** con código (AC20 VERIFICADO OFFLINE, par contrafactual medido, 6/6 mutaciones rojas por el guard), **commiteada y empujada el mismo día (`7c6e75f`, paridad 0/0)** |
| 4 · [B](05-prompt-inicio-sesion-fase-B.md) | Pains, promesas y guía de setup sin número | ALTA: mapper, catálogo y productores de narrativa/coverage | **CERRADA CON DEUDA REGISTRADA 2026-09-20** (`473ed0f` el código; `05d0cc6` decide A4 con O5, caracteriza el pase trivial y re-ancla la **deuda AC5** al tramo **C-D**; `7553f51` barre las citas de push). AC1 y AC2 **VERIFICADO OFFLINE**; AC19a-consumo cerrado. La arista a C está **habilitada**: su deuda entra en C como insumo, no como prerrequisito que rehaga B |
| 5 · [C](05-prompt-inicio-sesion-fase-C.md) | Confianza, campo validado, destino seguro del botón y AC19a aditivo | ALTA: precedencia del dato, falso VERIFIED y dos lectores que hay que unificar | **PENDIENTE ← punto de reanudación.** Arrastra la **deuda AC5** de B (dueño C-D): el test que caracteriza el pase trivial del gate debe ponerse rojo cuando AC5 lo gobierne |
| 6 · [D](05-prompt-inicio-sesion-fase-D.md) | Veredicto único, fail-fast y causas serializadas | ALTA: gates y consumidores del assessment | PENDIENTE |
| 7 · [E](05-prompt-inicio-sesion-fase-E.md) | Writer real, resolvedor único de artefactos y snapshot interno revisable | ALTA: orden temporal y separación interno/cliente | PENDIENTE |
| 8 · [F](05-prompt-inicio-sesion-fase-F.md) | Redacción de salidas (sumidero único) y estado operativo de credencial | MEDIA-ALTA: seguridad de salidas y prueba externa de revocación | PENDIENTE |
| 9 · [H](05-prompt-inicio-sesion-fase-H.md) | Integración offline, onboarding derivado con procedencia y runner acotado | ALTA: entorno, identidad, reserva y evidencia antes de gastar el único intento | PENDIENTE |
| 10 · [E2E](05-prompt-inicio-sesion-fase-E2E.md) | Única invocación real y conservación inmediata de evidencia | MEDIA técnica / ALTA operativa: APIs y un solo intento | PENDIENTE |
| 11 · [VERIFY](05-prompt-inicio-sesion-fase-VERIFY.md) | Análisis directo de artefactos y matriz de certificación AC1–AC20 | ALTA: atribución causal y límites de una sola muestra | PENDIENTE |
| 12 · [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre y sincronización documental autorizados | MEDIA: coherencia y orden documental | PENDIENTE |

Cadena estricta: **A → G → 0 → B → C → D → E → F → H → E2E → VERIFY → RELEASE**. No ejecutar fases en paralelo ni encadenarlas dentro de una sesión. Un checkpoint no habilita la fase siguiente.

A–H no ejecutan auditorías externas ni v4complete. H prepara tests/runner sin nuevos flags CLI. Solo E2E puede consumir el intento mediante ese runner; no se lanza el comando hijo por separado. Un fallo o timeout no concede otra corrida. VERIFY es directo, sin delegación, cambios de código, tests nuevos ni nueva ejecución; lee evidencia existente. RELEASE es documental, no una fase de reparación ni otra corrida.

## Prerrequisitos y límites visibles

- **Nueva (revisión 2):** la meta certificable de E2E es **ZIP publicado con veredicto no bloqueante**, no `READY_FOR_PUBLICATION`. Medido: readiness READY y 13/13 gates verdes convivieron con `BLOQUEADO` y ZIP suprimido. El techo con tier B es `APROBADO-CONDICIONAL-PENDING-ONBOARDING`; `APROBADO-PARA-ENTREGA` exige tier A (GA4+GSC verificados) y hoy el tier sale **B por defecto**.
- **Nueva:** FASE-0/AC20 es prerrequisito del intento único. Sin él, la supresión se reproduce pase lo que pase en B–H.
- **Nueva:** `--output` no aísla la corrida. `v4complete` muta `.agent/memory`, puede borrar sesiones de más de 20 días y reutiliza análisis previo por `canonical_url` (`L-PF11`). H congela `--permission-mode` (default `auto`, que autoriza APIs de pago) y snapshot de memoria antes del spawn.
- El PRE quick del 2026-09-18 fue **9/10** por Version Sync y la re-medición del 2026-09-19 da **10/10**: eran cuatro documentos sucios en el árbol, hoy idénticos a HEAD. No queda prerrequisito de autorización central; A vuelve a medir el quick al abrir la fase.
- **DOMAIN_PRIMER: regeneración y validación son dos operaciones distintas, y el pendiente ya no existe.**
  ⟦Resuelto por el bloque C de la orden de calidad §4.C, leyendo la gobernanza⟧ La instrucción que estaba
  vigente en este README («A debe resolver la divergencia documental sobre cuándo regenerar DOMAIN_PRIMER,
  sin editar reglas centrales para silenciarla») quedó **desfasada por dos hechos**: la resolvió **A el
  2026-09-19** sin tocar ningún documento central —como registra la fila «Cierre documental central» de
  `dependencias-fases.md`— y **G ya ejecutó una regeneración** con su writer (`doctor.py
  --regenerate-domain-primer`). La regla operativa de este plan es por tanto: **regenerar** con su writer
  al cerrar **cada fase de implementación** (executor §E7 y su tabla de estándares; `docs/CONTRIBUTING.md`
  Paso 5b y su regla 4) y **validar** con `doctor.py --context`/`--status` **solo en FASE-RELEASE**. Son
  pasos distintos: ni la validación del RELEASE sustituye a la regeneración de la fase, ni la regeneración
  de la fase se reporta como verificación. Dos cosas se **declaran** y no se tocan desde aquí: el bloque de
  `AGENTS.md` que condensa ambas patas en «se regenera en FASE-RELEASE», y la fila de la tabla de
  `CONTRIBUTING` que dice «Se VERIFICA (paso 5b)» mientras el propio Paso 5b se titula «Regenerar» — son
  configuración central y su alineación pide instrucción literal expresa. Cada regeneración ensucia un
  archivo versionado, así que **no** se regenera DOMAIN_PRIMER en una sesión sin mandato para escribirlo.
- El límite del write-back a QMind (writer sin título ni archivo explícitos, verificación por título y check solo en el modo completo) **tiene plan propio**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`, con disparador en la sesión previa a FASE-RELEASE y fallback documentado en su §5. No altera la cadena A → G → 0 → B → … ni consume el intento de corrida. ⟦Bloque C, 2026-09-24⟧ Ese mini-plan separó ahora **entrega offline** de **aceptación remota**: el trabajo que la sesión previa al RELEASE debe dejar hecho es verificable sin red, y la subida real tiene su propia autorización y presupuesto. Su disparador sigue siendo ése; lo que ya no puede leerse es que «hace falta ejecutar el mini-plan» autorice una subida.

- La deuda **F-B de privacidad** permanece diferida: no transportar WhatsApp/PII en warehouse ni cambiar formulario/esquema sin decisión escrita. No confundir esta deuda con la sesión B.
- Fuente Don Alfonso: observación del **2026-07-22**. A resuelve vigencia y H contrasta `ONBOARDING_FRESHNESS_HOURS` efectivo; no cambiar fechas, desactivar frescura ni sustituir por defaults.
- Binding explícito y local: URL original **https://hoteldonalfonso.com/**; solicitada **https://www.donalfonsohotel.com/**. Conservar ambas y su procedencia; no afirmar redirección ni crear alias global.
- La revocación de una key expuesta no es inferible del código, tests o una key nueva: requiere evidencia operativa sin secreto; mientras falte, permanece pendiente.
- QMind fue accesible para consulta según las lecciones, y eso **no** autoriza upload. **G ejecutó la subida el 2026-09-20 con autorización literal separada**, sobre una instantánea saneada de su `10-analisis` y verificada por descarga + sha256 (`evidence/…/FASE-G/qmind-writeback-G.md`). El título de RELEASE queda pre-acordado en `dependencias-fases.md`, porque el de G ya existe y `--upload` respondería SKIP.

## Inicio de la siguiente sesión

Copiar en una sesión nueva. **Nota de higiene, corregida el 2026-09-24:** este bloque se reescribe en cada
cierre y su frescura la vigila **una lectura humana del árbol, no un verificador automático**:
`validate_plan_closure.py` solo compara la sección «Cierre del plan» con las filas `⬜ Pendiente` del
§1 de `10-analisis-post-implementacion.md`. Esa era la afirmación que este README daba por hecha, y es
justo la razón por la que el bloque pudo quedar diciendo «FASE-B» semanas después de cerrarse B. El
bloqueo automático de un lead vencido **no existe**: quien abre la fase re-mide.

**Qué se cambió aquí y por qué.** La versión anterior de este bloque era el prompt de ejecución de
**FASE-B** con sus instrucciones, sus límites de FASE-0, sus rojos preexistentes y su cifra de checks.
B está cerrada, así que mantenerlo era la segunda fuente estática que contradice a su propio prompt
canónico —y copiar el prompt de C aquí sería repetir el defecto. El bloque queda reducido a lo que **no**
vive en otro archivo: el destino, los hechos de estado que no se deducen de un comando y la lista de lo
que hay que re-medir.

```text
Ejecuta únicamente FASE-C del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/.
Lee 05-prompt-inicio-sesion-fase-C.md, 01-plan-maestro.md, 04-contrato-ejecucion.md,
00-lecciones-capitalizadas.md, dependencias-fases.md, 06-checklist-implementacion.md y el workflow
canónico. Ese prompt canónico es la autoridad de la fase: no reproduzcas sus instrucciones ni sus
cifras desde este README.
Hechos de estado que C no debe volver a descubrir: A, G, 0 y B están cerradas y empujadas; B cerró CON
DEUDA y su AC5 (S-B1) tiene dueño C-D, así que entra en C como insumo, no como prerrequisito que rehaga
B; la arista B→C está habilitada. El contador v4complete sigue en 0/1 y C no lo consume.
Re-mide antes de la primera edición, y no copies el valor de ningún documento: `git status --porcelain`,
`git rev-parse --short HEAD`, `git fetch origin --quiet && git rev-list --left-right --count
origin/master...HEAD`, `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` (el número lo
imprime la corrida), `./venv/Scripts/python.exe scripts/build_lesson_index.py --check` y el baseline
`output/TAREA7-2026-09-19/` (lectura sí, escritura nunca; sus artefactos son históricos).
Conserva lo que la orden de calidad ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md §4.C nombró como
inamovible: la deuda AC5 con su
dueño, los contratos aditivos (AC19a), la prueba de que el botón inseguro queda bloqueado (AC3), el
aislamiento entre lo interno y lo que ve el cliente, la corrida única de E2E y la lectura directa de
VERIFY sin delegación. No toques Juez, umbrales, `BLOCKING_VERDICTS`, `GATE_BLOCKING_ENABLED` ni
`write/publish/suppress`; no ejecutes v4complete; no regeneres DOMAIN_PRIMER sin mandato para escribirlo.
Deja checkpoint si falta autorización.
```

## Cierre y aceptación

Cada fase incorpora su evidencia y cierre incremental; no se difieren todos los controles a RELEASE. R2
toma como referencia 60 `tool_use` **hasta el corte que esta sesión tenga autorizado**, medidos con el
instrumento del contrato. ⟦Alineado el 2026-09-24 con el proceso común que dejó el bloque B de la orden
de calidad⟧: los **cinco cortes son utilizables sin commit** —implementación terminada, verificación
terminada, cierre documental, listo para revisión, espera de autorización— y el `git commit` **no** es el
quinto corte ni condición de ninguno: es una acción posterior, separada y opcional que requiere
autorización explícita. Cuando el commit de código **sí** está autorizado, el corte de R2 puede tomarse
hasta él; cuando no, el corte utilizable es **«hasta listo para revisión»**, y la sesión **declara cuál de
los dos usó**. Sin transcript, declarar **FUERA DE SERVICIO (R2.1)** y registrar el auto-reporte con su
unidad, no estimar cumplimiento. En sesiones sin código, registrar el corte documental separado.

**Filas con evidencia (reconciliado el 2026-09-24 leyendo los cierres reales, no esta cabecera):** AC7 y AC16 **VERIFICADO OFFLINE (G)**, AC15 **VERIFICADO OFFLINE (G y 0)**, AC20 **VERIFICADO OFFLINE (0, 2026-09-20)**, AC12 **PARCIAL (0)** — su rama publish quedó cubierta offline y falta el par del flujo real —, y **AC1 y AC2 VERIFICADO OFFLINE (B, `473ed0f` + `05d0cc6`)** con **AC2 cargando la deuda AC5** cuyo dueño es **C-D**, más **AC19a-consumo** cerrado por B. Lo que permanece PENDIENTE es **AC3–AC6, AC8–AC11, AC13, AC14, AC17–AC19** y el resto de AC20 en el flujo real; ninguno de los verificados llega a SUPERADO EN E2E por tener tests verdes. Tests offline y resultados realmente ejercitados por Don Alfonso se informarán por separado. READY requiere gates y acta favorables, además de ZIP válido; exit code cero no basta. Un bloqueo legítimo o un caso no ejercitado no se etiqueta como superado. **Alcance ejecutado a 2026-09-19:** la preparación del 2026-09-18 fue read-only y no ejecutó nada; la revisión 2 del 2026-09-19 sí ejecutó validaciones y lecturas de artefactos, y su cierre documental entró en el repo con el commit `9b0af4f` (anclas medidas sobre `938f59f`) y `master` en paridad con `origin/master`. Lo que sigue **sin** ejecutar y sin autorización: `v4complete` (contador 0/1), publicación, entrega a cliente y cualquier subida de material del cliente. **Commit y push de FASE-0 ejecutados el 2026-09-20 con instrucción literal del operador** (`7c6e75f` → `origin/master`, paridad verificada contra `git ls-remote`, 7/7 checks del hook en verde sin saltar ninguno). Única salida autorizada y ejecutada hasta hoy: la instantánea **saneada** del `10-analisis` de G a QMind (2026-09-20, verificada por descarga).
