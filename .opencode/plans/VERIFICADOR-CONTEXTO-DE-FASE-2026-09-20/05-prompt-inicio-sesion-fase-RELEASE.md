# FASE-RELEASE — Cierre documental, write-back y archivado

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-RELEASE
**Objetivo**: sincronizar versiones, publicar CHANGELOG y `GUIA_TECNICA`, cerrar `REGISTRY.md` con los
**cuatro** módulos nuevos, re-evaluar la deuda D1–D10 con los números que dejó la ejecución, y archivar
el plan en el orden fijo de R2.5/R2.10.
**Dependencias**: FASE-A, FASE-B, FASE-C y FASE-D ✅. Si alguna quedó con un AC en ⚠️ o
`NO-EJERCITADO`, **ese estado viaja al cierre**: no se promociona a ✅ en RELEASE.
**Duración / scope**: 1 sesión; **4 tareas** documentales + **0** comandos de larga duración.
**Regla**: RELEASE **NO modifica código fuente** y **NO** registra fases ajenas.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está concluido
contractualmente por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24 solo
como enmiendas prospectivas sobre los documentos de los cuatro planes. ⟦**Conciliación final 2026-09-25**:
este párrafo decía que «el piloto FASE-C y este RELEASE no están autorizados y ninguna de sus operaciones
se ejecutó»; **el piloto FASE-C y FASE-D se autorizaron y cerraron el 2026-09-24**, cada uno con su mandato
propio, y su evidencia está en `evidence/…/FASE-C/` y `evidence/…/FASE-D/`. Lo que sigue sin autorización es
**esta fase** y, dentro de ella, cada momento por separado⟧.
**Lo que RELEASE no reabre**: E1–E5 no se renegocian, **AC15 sigue `NO-EJERCITADO`**, **D6 sigue dormida con
causa**, y **D7 no se activa** aquí.
Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

**Tres momentos, tres permisos (⟦orden de calidad §4.C, fila `CONTEXTO/RELEASE`; contrato §Dos
momentos del cierre⟧).** ⟦**Cuarto momento, previo, desde la rectificación 2026-09-25: C0** (abajo). La
etiqueta «tres momentos» se conserva porque **cinco documentos vivos** del plan la citan por ese título
(este prompt, `README.md`, `09`, `10` y `dependencias-fases.md`) y los **cinco packs** generados la copian.
**No es una referencia mecánica** —los `§` que resuelve el generador son los del contrato (§Dos momentos
del cierre, §Carga total y frescura del pack, §Orden del cierre)—, así que renombrar el título solo dejaría
a esos cinco documentos describiendo **tres** permisos donde ya son cuatro: desincronización de prosa, no
rojo de herramienta. Se anota en su lugar. **La cuenta vigente es cuatro permisos**:
C0 destinos escribibles · cierre offline verificado · remoto (D8, D9, cada uno aparte) · traslado⟧.
Esta fase concentraba una contradicción ejecutable: el contrato declaraba
«cero red» y a la vez su §Orden del cierre mandaba una consulta a QMind y una subida. Se resuelve por
separación, no borrando ninguna de las dos mitades:

| Momento | Operaciones | Qué lo habilita | Si falta el permiso |
|---|---|---|---|
| **Offline** | Lecturas y verificadores sin escritura; documentos, sync, registro y derivados solo sobre destinos autorizados en C0 | Mandato de RELEASE **más autorización literal de los archivos escribibles**; offline significa sin red, no permiso de escritura | Detenerse en C0 antes de escribir; declarar `PENDIENTE-AUTORIZACION`, no cierre offline cumplido |
| **Remoto** | re-corrida de la consulta Q7 (D8) y `--upload` del `10-analisis` (D9) | **Autorización literal propia + presupuesto escrito**, por separado para cada uno | Estado `PENDIENTE-AUTORIZACION` con su causa. **Prohibido** el PASS por omisión y prohibido promover el cierre parcial a éxito |
| **Traslado** | `git mv` a `Archives/` y lo que se le sigue | **Autorización propia del archivado** (no la concede el cierre documental) | Checkpoint con la operación pendiente nombrada |

## C0 — Permisos de escritura antes de iniciar RELEASE

**Rectificación 2026-09-25:** la versión anterior incluía `sync` en «OFFLINE (tu mandato)» y a la vez
reservaba permisos para sus destinos centrales. Esa autorización implícita queda retirada: este prompt
describe operaciones, **no concede permisos** sobre sus salidas. Antes de cualquier escritura de RELEASE,
contrastar el mandato literal con las entradas y salidas reales de cada writer; si falta un destino,
pedir autorización y detenerse. Solo pueden continuar las lecturas ya autorizadas.

- `sync_versions.py --check` **no escribe**. Sin `--check`, el writer puede modificar `README.md` de la
  raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md`, según las reglas
  vigentes de `scripts/sync_config.yaml`. El permiso debe nombrar esos destinos y limitarse a sus campos
  de versión/fecha/codename. Releer el config al retomar: esta lista no autoriza futuras reglas.
- `VERSION.yaml` es una **entrada** del sync, no una salida. Cambiarla requiere autorización propia con
  versión y fecha aprobadas; no elegir un incremento por el nombre de la fase ni para corregir un rojo.
- La escritura de contenido en `CHANGELOG.md`, `docs/GUIA_TECNICA.md`, documentos del plan, el registro
  `docs/contributing/REGISTRY.md` y su tracker `docs/contributing/.last_doc_phase.json` (si se pasa
  `--archivos-mod`) requiere destinos explícitos en el mandato. Igual para `briefing/`, el par del índice
  y el expediente nuevo de RELEASE. Preservar los
  cambios preexistentes; no re-registrar fases ya registradas.
- La alineación de política de **DOMAIN_PRIMER** es una decisión separada de sincronizar cabeceras.
  Presentar la propuesta para `AGENTS.md` y `docs/CONTRIBUTING.md`; si no se autoriza literalmente,
  conservarla pendiente, sin aplicarla ni regenerar `.agent/knowledge/DOMAIN_PRIMER.md` por arrastre.
- `--fix`, `--update-baseline` y hooks no son vías para eludir C0. No actualizar baselines para absorber
  errores. Red, archivado, commit y push conservan sus checkpoints separados.

Si falta permiso para una escritura necesaria, el resultado es **preflight incompleto / checkpoint C0**,
no «sync realizado» ni cierre offline completo. Ningún verde de solo lectura demuestra autorización.

**⟦Valores de release decididos por el operador el 2026-09-25⟧** — registro, no ejecución:
`version: 4.78.0`, `release_date: 2026-09-25`, `date: 2026-09-25` (debe ir igual a `release_date`).
**Falta el `codename`**, así que `VERSION.yaml` **no se escribió** en esa sesión: fijar la versión con el
codename de `4.77.3` sería propagar a las cinco cabeceras una release nueva con el nombre de la anterior.
La autorización para correr `sync_versions.py` sigue **sin conceder** (el operador la dejó explícitamente
apartada). Fuente: `evidence/…/FASE-RELEASE/05-valores-release.txt`, con la secuencia ordenada y su razón.
Orden que resulta de esto: **codename → VERSION.yaml → sync → diff de cabeceras → `--check` y
`version_consistency_checker` → CHANGELOG `[4.78.0]` → REGISTRY por su escritor** (registrar antes de fijar
la versión estamparía `4.77.3`).

## Contexto

Entran al repo cuatro scripts nuevos y un directorio de artefactos generados (`briefing/` dentro de
este plan). El índice de lecciones gana las lecciones de este plan para que el Paso 0 del siguiente las
consulte. El único momento en que el write-back a QMind funciona es con el plan todavía en `plans/`
raíz (R2.10), y la segunda regeneración del índice es obligatoria porque el `git mv` cambia rutas que el
índice publica con su dueño.

### Estado de fases anteriores (a confirmar en disco al abrir la sesión)

| Fase | Estado esperado | Qué trae |
|---|---|---|
| FASE-A | ✅ | `validate_governance_numbers.py`, AC1–AC5, informe con `coverage_basis` |
| FASE-B | ✅ | `decision_client.py`, contract test de forma, `files_changed_to_add_provider` |
| FASE-C | ✅ con AC15 en ⚠️ si no hubo proveedor | `triage_lesson_relevance.py`, AC10–AC14, y `acceptance = NO-EJERCITADO` |
| FASE-D | ✅ | `build_phase_briefing.py`, los packs, y `carga.json` con el delta **medido** |

## Tareas

### Tarea 1: Verificar la capa tibia (ya consultada en la auditoría del 2026-09-20)

La consulta Q7 de `00-lecciones-capitalizadas.md` **ya no está pendiente como descubrimiento**: se
ejecutó en la auditoría de la concepción el 2026-09-20 con el CLI disponible y autenticado, y sus
resultados están capitalizados en §2 (L-V2.1, L-V2.2, D-V2.1). Quedan dos cosas por hacer aquí, y son
de **dos momentos distintos**:

1. **Re-correr solo si el notebook cambió** desde esa fecha (nuevas fuentes ingeridas por otros
   planes), y publicar el resultado con la forma **correcta** del comando: `--nb` exige el ID
   `01a04d98-b7bd-778c-8441-26fdc7e35f45` — la forma con el nombre (`--nb iah-cli-lecciones`), que es
   la que publica el workflow canónico, devuelve `error: Bad request` (medido el 2026-09-20).
   ⟦Bloque C, 2026-09-24⟧ **Esto es una llamada de red** y pertenece al momento *remoto*: no se ejecuta
   con el mandato del cierre documental. Sin autorización literal propia, D8 se publica como
   `PENDIENTE-AUTORIZACION` y **no** como verificada; la alternativa no es saltársila en silencio, es
   declarar que la premisa («el notebook cambió») no se comprobó.
2. **Re-leer la interfaz del write-back antes del orden de cierre (deuda D10)**:
   `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara dentro de su alcance
   `scripts/validate_qmind_writeback.py` y su conexión en `scripts/run_all_validations.py`. Correr
   `validate_qmind_writeback.py --help` contra el árbol vigente y **re-escribir el bloque de cierre de
   este prompt si la firma cambió** (`--title`/`--file`, o el fin de la degradación a PASS). Si sigue
   igual, se publica esa verificación con su fecha. **`--help` es lectura de la firma, no una llamada
   remota**: este paso pertenece al momento *offline* y corre con el mandato de la fase.
   ⟦Estado medido el 2026-09-24, como antecedente para quien abra el cierre⟧: contra el árbol vigente
   el writer acepta `--nb`, `--strict` y `--upload`, **no** expone `--title` ni `--file`, decide **por
   título** y degrada a `exit 0` cuando falta el CLI — o sea la firma que D10 anticipaba **no** cambió,
   porque el mini-plan no se ejecutó. Re-medir al abrir el RELEASE; no copiar esta lectura.
   Criterio: **AC18** (y **AC16**: que la composición del `--quick` no cambie respecto del par
   pre/post que mide la fase, sea cual sea el número que la corrida imprima).

### Tarea 2: Sincronizar versiones y publicar documentación

**Solo tras completar C0.** Ejecutar las escrituras autorizadas: sync → CHANGELOG → `GUIA_TECNICA` →
`docs/contributing/REGISTRY.md` por su escritor, sin duplicar entradas, y las Secciones A/B/D/E de `09`.
Verificar con `version_consistency_checker.py` sin `--fix` y `sync_versions.py --check`.
Si faltan permisos, no ejecutar sync ni un subconjunto no aprobado: registrar el checkpoint con los
destinos pendientes. Un desajuste puede bloquear los checks del commit, pero **no** autoriza repararlo;
si el check ya pasa, tampoco prueba que se haya escrito nada. Commit sigue siendo una acción separada.

### Tarea 3: Cerrar la deuda con números, no con opinión

Presentar **sin ejecutar** las decisiones que este plan abrió. Cada una sale con su coste medido y su
dueño nombrado:

- **D1** — la elección de corregir o retirar A1–A4 y la espera de instrucción sobre `.agents/` eran
  pendientes de la concepción. ⟦Orden §4.C, fila `CONTEXTO/RELEASE`⟧ Aquí había una contradicción entre
  dos frases: la tabla de validaciones pedía «verificador verde» y la regla de la fase prohibía tocar
  `.agents/`. Se separan las dos operaciones: **ejecutar el verificador de solo lectura para conocer el
  estado** es verificación, y **corregir las aserciones** es la reparación que ya se hizo desde su
  fuente. B recibió autorización y realizó correcciones; su aceptación **no se presume ni se rehace**:
  RELEASE lee el estado de D1 en la **matriz vigente §13** de la fuente única, sin heredar el rojo
  histórico ni un verde retirado, y **sin ejecutar aquí otra corrección de `.agents/`**. Si el
  verificador diera un hallazgo nuevo, el resultado de RELEASE es declararlo con su dueño, no
  corregirlo.
- **D2 / D3** — D2 sigue debida con su disparador, y **las enmiendas del bloque C sobre
  `REFACTOR-WHATSAPP` no lo dan por cumplido**: lo que esas enmiendas hacen es convertir en «el valor
  lo imprime la corrida» las **instrucciones prospectivas** de ese plan; los registros de sus fases
  cerradas conservan su cifra histórica y no se reescriben. Sigue habiendo fases de ese plan que
  publican el número, así que D2 no se activa por arrastre documental. D3 está **parcial**, dueño
  **«Plan propio, posterior»**: el rebanado completo sigue pendiente; la simplificación expresamente
  encargada a B no se difiere a D2, al bloque C ni al piloto. No se reinterpretan aquí.
- **D6** — el lint de contradicciones semánticas: **solo puede activarse si AC15 publicó una
  aceptabilidad real**. Con `acceptance = NO-EJERCITADO`, D6 queda **dormida** y se registra así, con la
  causa. Un lint de pertinencia sobre una base que nunca juzgó nada es deuda apilada sobre humo.
  ⟦Bloque C, 2026-09-24⟧ Esa rama es la **única** alcanzable mientras D7 esté inactiva: con proveedor
  falso no existe aceptabilidad que medir, así que ningún cierre de RELEASE puede encontrar D6
  «activada» sin traicionar E4.
- **D7** — activar el proveedor: confirmar que la costura quedó probada (`files_changed_to_add_provider`)
  y que el coste de entrada es **un archivo**. No activarlo en el cierre.
- **D8 / D9** — son las dos operaciones del **momento remoto** (Tarea 1 y Tarea 4). Su estado en el
  cierre es el que dé la autorización, no el que dé la costumbre: ejecutadas con permiso propio, o
  `PENDIENTE-AUTORIZACION` con causa y presupuesto. Ninguna se cierra por existir el comando.
- **D4 / D5** — siguen con dueño en `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`; no se reasignan.

### Tarea 4: Cierre en orden y verificación final

El orden es el del contrato (§Orden del cierre, R2.5/R2.10) y **no es permutable**. Cada línea lleva
su momento; las de `⟦remoto⟧` no se ejecutan con el mandato del cierre documental y las de `⟦traslado⟧`
necesitan la autorización propia del archivado.

**Regla de cola que fija esta conciliación (2026-09-25), leída de las entradas y salidas reales de los
generadores**: `build_phase_briefing.py` escribe `<plan>/briefing/FASE-*.md` **dentro del corpus que
`build_lesson_index.py` recorre** (todo `**/*.md` bajo `.opencode/plans/`), y `validate_opencode_refs.py
--fix` reescribe `.md` de `.opencode/**`. Por lo tanto **el orden que cierra es: writers de corpus → packs
→ par del índice → verificación sin escritura**, y esa cola se corre **después de la última escritura de
documentos** (incluido el apartado «Post-ejecución» de este prompt), no antes. Cualquier otro orden deja un
derivado `SHA-DISTINTO` o el par `VENCIDO` por construcción (**L-VCF-17**, **L-VCF-19**). El generador de
packs **no tiene bandera por fase**: cada corrida reescribe los **5** packs del plan, así que la última
cosa que se toca es lo primero que se vence.

```bash
# ⟦remoto⟧ — aceptación remota: autorización literal y presupuesto propios
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_lesson_index.py
# ⟦traslado⟧ — tercer momento, con autorización expresa
git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
# ---- cola fija del cierre: se corre DESPUES de la ultima escritura de documentos ----
# (1) comprobaciones sin escritura; no absorber errores actualizando baselines
./venv/Scripts/python.exe scripts/validate_opencode_refs.py
./venv/Scripts/python.exe scripts/validate_plan_citations.py
# Si hacen falta correcciones, solicitar sus destinos antes de escribir; luego regenerar derivados.
# (2) el pack con la ruta ya trasladada (contrato §Carga total y frescura)
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan>
# (3) el par del indice DESPUES de los packs: los packs son corpus del indice
./venv/Scripts/python.exe scripts/build_lesson_index.py
# (4) verificar sin escribir
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan> --check
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Trampa declarada, con su evidencia.** El comando de reproducción que el propio generador publica
(`build_phase_briefing.py`, y `carga.json` → `method.reproduccion`) lleva `--carga
evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json`: **copiarlo tal cual pisa evidencia
cerrada de FASE-D** (`--informe` hace lo mismo). En el cierre se usa `--carga -` / `--informe -` (stdout) o
una ruta **nueva** dentro del expediente de FASE-RELEASE. **Nunca** el destino por defecto de otro
expediente (**S12 / L-VCF-12**, que es exactamente esta familia).

**Qué se hace con un rojo de después del traslado.** El `--check` del pack llamado sobre rutas ya
movidas falla **por diseño** si el pack no se regeneró: la cura es regenerar el derivado con su propio
generador, que es operación de cierre. **No** es editar `build_phase_briefing.py` ni su `provenance` a
mano, y **no** es «reparar código»: si tras regenerar sigue rojo, eso es un defecto del generador, su
dueño es FASE-D, y RELEASE lo declara con evidencia y deja checkpoint en vez de arreglarlo (§Regla:
RELEASE no modifica código fuente).

**Qué se publica si el momento remoto no está autorizado.** Las dos líneas `⟦remoto⟧` salen como
`PENDIENTE-AUTORIZACION` con su causa y su dueño (orden de calidad §5, decisión «Entrega y permisos
remotos»), y el resto del cierre se completa y se reporta como **cierre documental offline**. Un
resultado parcial no se promociona a éxito del plan: `REGISTRY` registra lo que se hizo, `09`/`10`
dicen qué quedó pendiente, y ningún `[OK]` se imprime por omisión.

## Tests y validaciones obligatorias

| Verificación | Criterio de éxito |
|---|---|
| `validate_lesson_capitalization.py` | C1–C8 verdes sobre el `00-…` final, tras la consulta Q7 o con su `PENDIENTE-AUTORIZACION` declarado |
| `validate_governance_numbers.py` (el de FASE-A) | Salida conforme sobre el árbol final, con su denominador. **Ejecutarlo es leer el estado, no repararlo**: D1 ya se resolvió desde su fuente y aquí no se vuelve a corregir `.agents/` (ver Tarea 3) |
| `build_phase_briefing.py --check` (el de FASE-D) | Verde contra el árbol **después** del archivado **y después de haber regenerado el pack** con la ruta trasladada |
| `validate_plan_closure.py` (`[5/7]` del hook) | Sin filas pendientes en `10-analisis-post-implementacion.md` que contradigan un cierre declarado — con las operaciones `PENDIENTE-AUTORIZACION` escritas como tales |
| `build_lesson_index.py --check` (`[6/7]`) | Índice reflejando el árbol después del `git mv` |
| `run_all_validations.py --quick` | Verde con composición intacta (AC16, delta 0 contra su par pre/post; el número lo imprime la corrida) |

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-RELEASE ✅ y la tabla de deuda **D1–D10** con su estado real tras la
   Tarea 3. D6 **dormida con su causa** mientras AC15 siga en `NO-EJERCITADO`; la rama «activada» no es
   alcanzable sin proveedor real (D7), así que no se escribe como opción abierta de este cierre.
2. `README.md` — estado final, ruta nueva en `Archives/`, ACs con el nivel alcanzado.
3. `06-checklist-implementacion.md` — casillas de cierre.
4. `10-analisis-post-implementacion.md` — matriz final, análisis por referencia a las métricas de
   `09` §D y su evidencia (incluido el delta de carga de lectura, **por referencia a
   `evidence/…/FASE-D/carga.json` y a la fila «Carga de lectura A7» del README, sin transcribir sus
   cifras ni su porcentaje**: este documento entra al pack que ese comando mide, **L-VCF-19**), límites
   y seguimientos S1–S7.
5. `00-lecciones-capitalizadas.md` — §4 al estado del cierre y Q7 resuelta o limitación re-fechada.
   **Las propuestas de revisión humana pendientes (E3) no se aceptan ni se rechazan desde el RELEASE**: si
   el operador no decidió, viajan al cierre como `pendientes` con su dueño; **§2 no se edita por defecto**.
6. `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-RELEASE/` — salidas de las validaciones de la tabla anterior.

7. **COLA FINAL — después de los seis puntos anteriores, y no antes** (son escrituras de documentos que
   alimentan los derivados): re-correr los pasos **(2) → (3) → (4)** de la cola de Tarea 4, es decir
   **regenerar los packs → regenerar el par del índice → verificar con los dos `--check` y el `--quick`**
   sobre el árbol final. Si el `git mv` del traslado ya ocurrió, la cola se corre con la ruta ya
   trasladada. **El orden de verificación es: escrituras → packs → índice → checks**; invertir produce un
   pack `SHA-DISTINTO` o un índice `VENCIDO` que la sesión reporta como verde ajeno (**L-VCF-17**).
   ⟦**S15 declarado, no absorbido**: el verde de `[6/7]` en esta máquina **no** certifica otro checkout; si
   el `--check` da `FAIL` en un árbol extraído, es S15 y se declara con su dueño, no se re-registra el par
   «para que cuadre» ni se toca `build_lesson_index.py` (RELEASE no repara código).⟧
   **Este punto se escribió para una sesión en la que S15 seguía abierta y tocar el generador estaba
   prohibido; las dos premisas cambiaron el 2026-09-26**: S15 quedó curada en `scripts/build_lesson_index.py`
   con mandato de código del operador y el corte «último commit que tocó el documento» (fuente versionada, con
   estado explícito `SIN-FUENTE` cuando no la hay). Lo que **perdura** de este punto, y no se retira: un verde
   de `[6/7]` en esta máquina **no** es la prueba — la prueba son los dos checkouts del mismo commit en
   `tests/test_build_lesson_index_s15_fecha_versionada.py` y la extracción del árbol del propio commit; y si
   el `--check` da `FAIL`, **tampoco se re-registra el par «para que cuadre»**: se lee primero la línea
   `[fechas] nombre=… commit=… sin_fuente=…` que el check imprime en verde y en rojo, y se declara el corte
   que falla. Lo que **cambia** para quien reabra este prompt: un `FAIL` en un clon ya no se atribuye a S15
   (atribución histórica: los vistos sobre `da382b1` y `5817edd` sí lo fueron); hay que clonar con
   `-c core.autocrlf=input`, porque el `system` es `true` y `git clone` no lee la config local del clon.

RELEASE **no** invoca `log_phase_completion.py` sobre fases ajenas: solo sincroniza y valida.

## Criterios de completitud

- [ ] Write-back ejecutado **con el plan aún en raíz** (es el único paso que deja de funcionar tarde)
      **o** declarado `PENDIENTE-AUTORIZACION` con su causa. Las dos salidas son legítimas; la que no lo
      es: pasar por alto el paso y cerrar como si hubiera corrido.
- [ ] Índice regenerado **dos** veces, con la segunda después del `git mv`.
- [ ] Pack **regenerado con la ruta trasladada antes de verificarse**, y su `--check` verde contra el
      árbol final, no contra el de mitad de cierre. El rojo de un pack sin regenerar no se repara
      editando código.
- [ ] Ningún AC promocionado a ✅ sin su mutation check o su clave en el artefacto (R2.4).
- [ ] `--quick` verde con su composición intacta respecto del par pre/post (AC16, delta 0);
      `validate_governance_numbers.py` ejecutado **como lectura de estado**, no como reparación.
- [ ] D1 referenciada a la **matriz vigente §13** de B, sin certificación adelantada; D2 con dueño
      y disparador, **sin dar por satisfecho su disparador por las enmiendas del bloque C**; D3 parcial
      con dueño **«Plan propio, posterior»**; **D6 con su causa declarada**.
- [ ] D8 y D9 con su momento y su permiso nombrados (ejecutados con autorización propia o pendientes).
- [ ] Delta de **carga total** de lectura referenciado desde `09` §D **aunque sea cero o negativo**
      (AC20), con su comando y sus tres sumandos.
- [ ] CHANGELOG, `GUIA_TECNICA` y `REGISTRY.md` sync; `[1/7]` y `[2/7]` en verde.
- [ ] Plan archivado y las referencias vivas apuntando a la ruta nueva.

## Restricciones

- No modifica código fuente. **Regenerar un artefacto derivado con su generador sí le corresponde**;
  cambiar ese generador, su `provenance` o cualquier `scripts/*.py` para que un check pase, no. Un
  defecto de FASE-D descubierto en el cierre se declara con su dueño y deja checkpoint.
- No abre ni cierra deuda de `REFACTOR-WHATSAPP`. No ejecuta la pipeline.
- **No activa el proveedor de decisiones** (D7). Las dos operaciones remotas (D8, D9) **no** se ejecutan
  con el mandato del cierre documental: cada una necesita su autorización literal y su presupuesto, y sin
  ellas se declaran pendientes en vez de omitirse (§Tres momentos, tres permisos).
- No toca `.agents/**` salvo instrucción literal del operador resultante de la Tarea 3.
- La verificación y el cierre documental se declaran sobre el árbol final verificado, sin commit.
  El archivado requiere autorización propia y conserva el orden R2.5/R2.10; no lo autoriza el cierre
  documental. Un eventual commit de RELEASE + archivado es una acción posterior y separada, opcional,
  con autorización explícita; tampoco autoriza push ni condiciona ninguno de los cinco cortes.
  Si falta un permiso, se registra el checkpoint y la operación pendiente, no un cierre total ficticio.

## Prompt de ejecución

```text
Ejecuta unicamente FASE-RELEASE del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-RELEASE.md, 01-plan-maestro.md §4 y §6, 04-contrato-ejecucion.md
(§Dos momentos del cierre, §Carga total y frescura del pack y §Orden del cierre),
00-lecciones-capitalizadas.md completo, 06-checklist-implementacion.md, dependencias-fases.md,
10-analisis-post-implementacion.md, los cuatro prompts de fase nombrados uno por uno —
`05-prompt-inicio-sesion-fase-A.md`, `05-prompt-inicio-sesion-fase-B.md`,
`05-prompt-inicio-sesion-fase-C.md` y `05-prompt-inicio-sesion-fase-D.md` —, docs/CONTRIBUTING.md y el
workflow canonical (FASE-RELEASE).
Primero re-mide en disco el estado real de A, B, C y D: un AC en ⚠️ o NO-EJERCITADO viaja al cierre con
ese estado, no se promociona.
Antes de cualquier escritura, completa C0: este prompt no autoriza cambios centrales por llamarse
RELEASE ni por ser offline. Contrasta el mandato literal con scripts/sync_config.yaml y los writers.
Sin --check, sync_versions.py puede escribir README.md de raiz, AGENTS.md, .cursorrules,
docs/CONTRIBUTING.md y docs/GUIA_TECNICA.md: exige autorizacion literal para esos destinos y sus campos
de version/fecha/codename. VERSION.yaml es una entrada: modificarla exige version y fecha aprobadas.
CHANGELOG, contenido de GUIA_TECNICA, REGISTRY y trackers, documentos del plan, packs, indice y expediente
nuevo tambien deben estar nombrados como destinos autorizados. Si falta alguno necesario, detente antes
de escribir: checkpoint C0, no cierre offline cumplido. Solo continúan las lecturas autorizadas,
como sync_versions.py --check, validate_qmind_writeback.py --help y verificadores sin escritura.
Alinear la politica de DOMAIN_PRIMER requiere otra decision literal; no lo autoriza el sync de cabeceras.
REMOTO (D8 y D9): la re-corrida de Q7 y el --upload; cada uno necesita
autorizacion literal propia y presupuesto escrito. Sin ellos se declaran PENDIENTE-AUTORIZACION con su
causa y su dueno, no se omiten y no se cierran como hechos. TRASLADO: el git mv a Archives tiene su
propia autorizacion, separada del cierre documental.
Tarea 3: concilia la deuda sin ejecutarla. D1 se lee desde la unica matriz vigente, §13 de la fuente
unica de B citada al inicio; no heredes el rojo A1-A4 historico ni verdes retirados. Correr
validate_governance_numbers.py es LEER el estado, no reparar .agents/: si sale un hallazgo nuevo, se
declara con su dueno, no se corrige aqui. El bloque C de la orden esta autorizado solo como enmiendas
documentales. El piloto FASE-C y FASE-D ya se ejecutaron y cerraron el 2026-09-24 con mandato propio: no los
reabras, no los re-midas como si fueran pendientes y no promociones su parte NO-EJERCITADA (AC15, D6
dormida) a verde. D2 sigue debida y su disparador NO se da por satisfecho porque las
enmiendas del bloque C convirtieran instrucciones prospectivas de REFACTOR-WHATSAPP en comando: los
registros de sus fases cerradas conservan su cifra. D3 es parcial, dueno «Plan propio, posterior».
D6 queda DORMIDA: con D7 inactiva AC15 solo puede publicar NO-EJERCITADO, asi que la rama activada no es
alcanzable y no se la deja como opcion abierta. D7 se confirma con files_changed_to_add_provider y no se
activa aqui.
Tarea 4: consulta, subida y archivado conservan sus permisos y dependencias; sin ellos no se ejecutan.
Tras las escrituras autorizadas y, solo si fue autorizado, el traslado: refs y citas SIN --fix ni
--update-baseline -> REGENERAR los packs en la ruta vigente -> REGENERAR el par del indice -> check del
pack -> check del indice -> quick. No actualizar baselines para absorber errores. Si hacen falta
correcciones de corpus, pedir permiso para sus archivos y hacerlas ANTES de generar los derivados;
el indice va DESPUES de los packs porque son .md dentro de su corpus (L-VCF-17).
La cola de generacion y comprobacion se corre al final, despues de las ultimas
escrituras documentales del Post-ejecucion (paso 7), no solo a mitad de fase. El --check del pack despues
del traslado falla por diseno si no lo regeneraste: la
cura es regenerar el derivado, nunca editar build_phase_briefing.py ni su proveniencia para que pase. Si
regenerado sigue rojo, es un defecto de FASE-D: se declara con su dueno y deja checkpoint.
Nunca uses el comando de reproduccion que publica carga.json con su --carga apuntando a
evidence/.../FASE-D/carga.json: pisa evidencia cerrada de otra fase (S12). En el cierre es --carga - o una
ruta nueva dentro del expediente de FASE-RELEASE.
El cierre documental y la verificacion no requieren commit; archivado y eventual commit posterior se
autorizan por separado (Restricciones). Referencia el delta de CARGA TOTAL desde
evidence/.../FASE-D/carga.json y desde la fila «Carga de lectura A7» del README de este plan, aunque sea
cero o negativo, con sus tres sumandos; no transcribas el porcentaje en 10- ni en 09 (L-VCF-19). Su valor
recalculado el 2026-09-25 es 13,15 % de la carga total (216.721 / 1.648.109) y es cifra de estos cinco
packs medidos asi, no un ahorro general del proceso.
No modifiques codigo fuente, no registres fases ajenas, no ejecutes la pipeline, no commitees ni empujes
sin instruccion literal, y no hagas ninguna llamada remota sin su autorizacion propia.
```
