# Briefing pack — FASE-RELEASE

> **Artefacto generado. NO editar a mano.** Regenerar con:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
> La frescura la gobierna el sha256 de `sources[]` contra el arbol vigente:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check`.

- **plan**: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
- **fuente de lo declarado**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-RELEASE.md` (bloque «Prompt de ejecucion»)
- **estado del pack**: `COMPLETO`
- **declaracion de lectura en el prompt**: `DECLARADA`
- **procedencia**: HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`
- **tokens**: estimados por divisor 4, no recuento de tokenizer

## Lectura aparte obligatoria (el pack **no** la sustituye)

- `.agents/workflows/phased_project_executor.md` — 108017 bytes (~27004 tokens). se lee aparte mientras la deuda **D3** no rebane el workflow por fase; copiarlo aqui seria rebanar `.agents/` por la puerta de atras (AC17).
- `docs/CONTRIBUTING.md` — 19763 bytes (~4940 tokens). el prompt la declara pero vive fuera de `.opencode/`: copiarla dentro ampliaria la poblacion que escanea `validate_opencode_refs.py` ([8/11]).

## Que **no** incluye este pack

- 01-plan-maestro.md — 19801 bytes fuera de lo declarado (4, 6)
- 04-contrato-ejecucion.md — 23159 bytes fuera de lo declarado (Dos momentos del cierre, Carga total y frescura del pack, Orden del cierre)
- docs/CONTRIBUTING.md — declarada por el prompt pero vive fuera de `.opencode/`: se lee aparte para no ampliar la poblacion que escanea validate_opencode_refs.py

---

# Contenido declarado, copiado de su fuente

## Fuente: `05-prompt-inicio-sesion-fase-RELEASE.md` (documento completo)

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


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-RELEASE.md` · sha256 `b6b8eb825b61f450191a800050df7bff0cb2ed757b5baffa40b54c5a62ada934` · 31443 bytes copiados de 31443 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `01-plan-maestro.md` §4

## 4. Criterios de aceptación

**Tabla de ACs** (forma que lee `validate_lesson_capitalization.py` en C4). Cada AC declara
**el artefacto y la clave donde un humano lo leería** (R2.4); el detalle sigue debajo.

| AC | Criterio | Artefacto e instrumento esperado |
|---|---|---|
| AC1 | `validate_governance_numbers.py` reproduce **las aserciones normativas vivas** —las cuatro de §1— y **ninguna otra** sobre árbol vigente, con la regla de población de A8 aplicada; A5, A6 y A7 quedan fuera de su alcance y son la motivación de FASE-C y FASE-D | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]` con `assertion_id`, `document`, `claimed`, `observed`, `occurrences[]` |
| AC2 | Publica denominador: población mirada, **regla de población y su exclusión histórica aplicada**, exenciones y familias no cubiertas | ídem → `coverage_basis` |
| AC3 | Expresa `SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO` sin colapsar ninguno | ídem → `status` + tres tests por causa |
| AC4 | Mutation check **por aserción** sobre el símbolo real del guard | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` con rojo y verde |
| AC5 | El conteo del quick y del hook se preserva como **delta 0** con par pre/post | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md` |
| AC6 | Ningún archivo fuera de la costura importa SDK ni adapter alguno | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` (conteo + población) |
| AC7 | Proveedor no configurado o respuesta ilegible fallan explícitos, nunca con decisión por defecto | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` → `provider_status` |
| AC8 | Contract test de forma con proveedor falso y versión pineada | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` |
| AC9 | **Añadir un segundo proveedor es un cambio de un archivo**, demostrado con un proveedor falso adicional; ningún proveedor de pago se activa en este plan | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` → `files_changed_to_add_provider` |
| AC10 | El triaje **no elimina** ninguna fila anclada de §2 | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` → `removed: []` |
| AC11 | Índice ausente o vencido no se lee como «sin candidatos»; **`AUSENTE`, `VENCIDO` y `LECTOR-FALLIDO` son tres causas distinguibles y la frescura la comprueba el propio C** (⟦ruta (b) decidida 2026-09-23⟧) | ídem → `index_status` |
| AC12 | Umbral publicado con valor, base y acción por debajo, **aplicado a `confidence` de un `choice` de dos opciones** — no a `probabilidad_si` — y las propuestas van a **revisión humana**, no a §2 en automático (⟦decidido 2026-09-23⟧) | ídem → `threshold` |
| AC13 | ≥1 test contra corpus real archivado, con skip visible y declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` |
| AC14 | Mutation check sobre el guard real de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` |
| AC15 | Denominador del triaje con términos usados, ceros incluidos y familias no juzgadas, **más la aceptabilidad que dispara D6** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` |
| AC16 | El quick sigue en 11 checks y el hook en 7, en **todo** el plan | los cuatro `baseline-pre-post.md`, delta 0 |
| AC17 | `.agents/` intocado en escritura y límites de cobertura declarados | `coverage.json` → `families_not_covered[]` + `git status` sobre `.agents/` |
| AC18 | Capitalización, citas e índice verdes sobre los artefactos de este plan | salida de los tres verificadores sobre el mismo árbol final verificado (commit opcional posterior autorizado) |
| **AC19** | `build_phase_briefing.py` emite un pack por fase, **sin tocar `.agents/`**, declarando `no_incluye[]` y la lectura aparte obligatoria; **resuelve un plan también en su ruta archivada** (⟦bloque C 2026-09-24⟧: sin eso, el `--check` posterior al `git mv` del RELEASE no es ejecutable) | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` |
| AC20 | El **delta de carga total** de lectura se mide con el **mismo comando** antes y después, bytes exactos y tokens con el divisor declarado, contando **workflow obligatorio + coste de generar el pack + pack leído** (⟦bloque C 2026-09-24⟧ concatenar no es ahorrar) | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` + par pre/post con la resta |
| AC21 | Cada pack declara HEAD, fecha y sha por fuente; **la frescura la gobierna el sha de las fuentes relevantes, y HEAD es procedencia, no clave de caducidad** (⟦bloque C 2026-09-24⟧, para que el commit del propio generado no lo venza) | ídem → `provenance` ; prueba re-editando una fuente y re-midiendo en disco |
| AC22 | Sección declarada y no resuelta es un estado propio: **prohibido emitir un pack más corto en silencio** | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}` + tres tests |
| AC23 | Mutation check sobre el guard que impide el truncamiento silencioso | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` con rojo y verde |

Un AC cuya clave no existe en el artefacto está incompleto **antes** de ejecutarse (R2.4).

### FASE-A — `validate_governance_numbers.py` (determinista, sin modelo)

- **AC1** — El script, invocado suelto, reproduce sobre el árbol vigente **exactamente** las
  cuatro aserciones de §1 y ninguna otra. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json`, clave
  `findings[]` con `assertion_id ∈ {A1,A2,A3,A4}`, `document`, `claimed`, `observed` y
  `occurrences[]` (sitios donde esa aserción está escrita).
  **Regla de población (A8 — sin esto AC1 es innavegable):** la familia de aserción es **la
  atribución resoluble**, una afirmación que liga un conteo a un check o documento **nombrado**,
  con el `claimed` que el texto sostiene. El escaneo encuentra **22 instancias `[N/M]` y 2 formas
  «check N»** en los documentos de gobierno; de esas, cada una cae en una de tres clases y la clase
  decide si es hallazgo:
  - **VIVA (normativa):** sostiene una regla vigente del propio documento. Debe cuadrar con la
    etiqueta que imprime el código; si no cuadra → **finding** (esto son A1, A2, A3 y el `[10/10]`
    de A4).
  - **CONGELADA (histórica):** mención de medición fechada, o dentro de una entrada de changelog.
    El **propio objeto auditado** declara esta clase: la entrada `v2.24.0` del workflow dice que
    «las 4 menciones históricas de medición (dos en R2.10, dos en el changelog) se conservan
    literales». No es hallazgo, **pero tampoco silencio**: se publica en `historical_excluded[]`
    con su conteo y la frase que la ampara (L-HF1: un candado que excluye sin decirlo es peor que
    un candado que falla).
  - **VIGENTE Y CORRECTA:**cuadra con la fuente (p. ej. `[7/7]` del hook, los `[6/7]` del índice).
    Entra en `assertions_checked` con su `observed`; no genera hallazgo.
  Un verde de AC1 sin las tres clases publicadas no informa: diría «el árbol está limpio» sobre una
  población que el script recortó a mano.
- **AC2** — El mismo artefacto publica denominador (L-R.3): clave `coverage_basis` con
  `documents_scanned`, `assertions_checked`, `families_not_covered[]`, y `excluded[]` con cuántos
  planes quedaron exentos y por qué. Ninguna salida `SIN-HALLAZGOS` puede emitirse sin esta clave.
  **Familias que NO cubre, declaradas y medidas el 2026-09-20** (la lista no es un «etcétera»):
  (i) prose de conteo sin patrón `[N/M]` ni «check N» («11 checks», «once validaciones» en prosa);
  (ii) aserciones de conteo **fuera de los documentos de gobierno**, que este plan no toca y que hoy
  también están vencidas — `AGENTS.md` («Validación final (10/10 checks en modo rápido; 14 en el
  completo)», que mide 11 y 15), `docs/GUIA_TECNICA.md` y `docs/contributing/REGISTRY.md` con sus
  «check 8»/`[9/9]`/`[10/10]` históricos; (iii) **los pins de conteo en `tests/`** (hay al menos
  `tests/test_validate_plan_closure.py`, que assertiona `[5/7]` dentro del hook); (iv) cualquier
  otra fuente dinámica que no sea una etiqueta impresa (umbrales, tamaños, conteos de tests).
  Las cuatro familias se listan con su medición de AC2 y **D1** decide sobre (i)–(iii); AC5/AC16
  barre (iii) al medir quién afirma el 11 y el 7 (L-V2.3).
- **AC3** — Los tres estados de R2.9 son legibles y **no colapsan**: `sin hallazgos` dice sobre
  qué midió; `ausente` dice la ruta buscada; `lector fallido` dice el motivo y **nunca** sale
  como favorable ni como 0. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` clave `status`, más tres
  tests nombrados por su causa, uno por estado.
- **AC4** — Mutation check (R2.8) sobre el símbolo real que guarda la detección, **por aserción**
  y no una vez por fase. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` con el rojo (guard desactivado) y
  el verde (guard activo). Sin el lado rojo, AC4 queda ⚠️ (R2.4). Un verde obtenido a la primera
  sin rojo previo se declara sospechoso (L-VUP-5). **Anclaje de la aserción (L-V2.1, medida en
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** mutar la guarda de A2 y obtener «un hallazgo»
  no prueba nada si otro guard produjo ese hallazgo; cada mutante se afirma sobre **el `assertion_id`
  y el mensaje de esa detección**, y el rojo debe nombrar la aserción mutada.
- **AC5** — El plan no altera ningún conteo: `run_all_validations.py --quick` sigue en 11 checks
  y el hook en 7, formulado como **delta** con par `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/*_baseline_pre.txt` /
  `*_baseline_post.txt` y la resta comprobada (R2.3, R2.7, L-D3, L-V2.3). Artefacto:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md`, delta esperado **0**; una resta 0 con tests nuevos
  declarados = baseline contaminado y la fase no cierra en ✅.

### FASE-B — `decision_client.py` (costura de proveedor neutro)

- **AC6** — Ningún archivo fuera de `decision_client.py` importa el SDK del proveedor ni el
  adapter. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` con el conteo de coincidencias y la
  población escaneada (AC2 aplica: 0 sin denominador no es prueba).
- **AC7** — Proveedor no configurado **falla abierto a error explícito**, nunca a un resultado
  por defecto que pudiera leerse como decisión. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` clave
  `provider_status ∈ {RESUELTO, NO-CONFIGURADO, ILEGIBLE}`, con un test por estado (R2.9).
- **AC8** — Un contract test con proveedor falso fija la **forma** de la respuesta (elección,
  score, binario, confianza, probabilidades) y la versión de modelo pineada. Subir el SDK sin
  tocar la costura debe romper este test, no a las fases. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt`
  con el nombre del test y su salida. Prohibido pinear literales del conteo (L-V2.3).
- **AC9** — Con un solo proveedor en este plan, lo certificable no es «cuál gana» sino que **añadir
  el segundo sea un cambio de un archivo**. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` clave
  `files_changed_to_add_provider` (debe ser `1`, o explicarse) y `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt`
  con el test que registra un **proveedor falso adicional** a través de la costura sin tocar ningún
  otro archivo. La comparación real entre proveedores queda como deuda **D7**: un AC que exigiera
  medirla ahora se cerraría declarando `NO-EJERCITADO` y certificaría humo.

### FASE-C — `triage_lesson_relevance.py` (capa de pertinencia, aditiva)

- **AC10** — El triaje es **aditivo por construcción**: ningún ID ya presente en §2 de un plan
  puede desaparecer. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` con `anchored_before`,
  `anchored_after`, `removed` que **debe** ser `[]`; y un test que lo afirma.
- **AC11** — El suelo determinista es `lecciones_index.json`. Si falta, está vencido o no se puede
  leer, el script **no** emite «no hay candidatos»: emite `AUSENTE`, `VENCIDO` o `LECTOR-FALLIDO` con la
  ruta buscada y el comando de regeneración (L-PF6, L-PF10). Artefacto: clave `index_status` + tres
  tests, uno por causa.
  **Fuente de la decisión (Knowledge Center, `L-V2.2` de
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** «un verificador no debe apoyar su conclusión en
  el artefacto que genera otro gate» — ese plan lo capitalizó porque leer el JSON era lo obvio y el
  JSON lo produce `[6/7]`; la cura que implementó fue **calcular el índice en memoria** con
  `build_lesson_index.build()` (0,30 s medidos) y fallar con nombre propio si el cálculo cae.
  - **⟦ENMENDADA el 2026-09-23 por la orden de calidad §4.C — la elección queda CERRADA, no abierta para C⟧**
  **FASE-C elige la ruta (b): consumir el JSON con su propia comprobación de frescura.** Ya no hay
  elección que la sesión de C tenga que tomar; lo que tiene que implementar es esto, con su costo
  declarado:
  - C **ejecuta ella misma** la comprobación de frescura contra el árbol y a partir de ahí emite su
    estado. **`VENCIDO` es producto del check propio de C**, no de un `--check` ajeno, y por eso el
    estado sigue vivo (a diferencia de la ruta (a), que lo habría borrado).
  - **Prohibida la tercera vía**: leer el JSON confiando en que otro gate (el `[6/7]` del hook o la
    sesión anterior) lo regeneró. Que el archivo exista no es que esté fresco.
  - **Coste aceptado:** C es responsable de su suelo —si el árbol se movió después de la última
    regeneración, C lo dice aunque el hook esté verde— y mide dos lecturas del mismo JSON por corrida
    (la suya y la del check) en lugar de heredar un verde.
  - **Tres causas distinguibles, ninguna colapsable** (R2.9, y aquí con nombres propios porque el
    prompt las pide separadas): **`AUSENTE`** = no hay archivo en la ruta buscada → imprime la ruta y
    el comando de regeneración; **`VENCIDO`** = el archivo existe y se lee, pero **el check de frescura
    propio de C** no lo aprueba → imprime qué diff lo venció y el comando; **`LECTOR-FALLIDO`** = el
    archivo existe pero revienta al parsear o no es legible → imprime el motivo. **Un JSON roto jamás
    produce «sin candidatos» y `VENCIDO` no es `AUSENTE`.**
- **AC12** — El umbral de confianza se publica **con su valor y su efecto**, y los candidatos se
  separan en `propuesto` y `a-revisar-humano`. Ningún camino del código auto-filtra una lección.
  Artefacto: clave `threshold` con `value`, `basis`, `action_below`.
  - **⟦ENMENDADA el 2026-09-23 por la orden de calidad §4.C — forma de la pregunta binaria⟧**
  **La pregunta de pertinencia se formula como `choice` de dos opciones, no como `noul`.** Forma
  confirmada contra `scripts/decision_client.py` (no contra su documentación): `RespuestaEleccion`
  trae `eleccion` + `probabilidades` sobre **todas** las opciones + **`confidence` obligatoria**,
  mientras `RespuestaNoul` trae solo `probabilidad_si` y **`confidence = None` con su
  `confidence_motivo`** — la primitiva no la expone, y la puerta la **prohíbe** ahí.
  **Consecuencia operativa, que es el punto de la enmienda: la probabilidad de sí no es confianza y
  no pueden usarse indistintamente.** El `threshold` de AC12 se aplica a **`confidence`** (cuán seguro
  está el proveedor de haber leído bien la pregunta), y **`basis` debe nombrar el campo**; un umbral
  declarado sobre `probabilidad_si` sería otra cosa — cuánto se inclina por «sí» — y cerraría AC12 con
  una métrica que no es la que el AC describe. Publicar los dos números separados es válido y
  recomendado; **equipararlos, no**.
  - **⟦ENMENDADA el 2026-09-23 — qué se hace con las propuestas⟧**
  **Las propuestas del proveedor falso prueban mecánica y no entran en §2 en automático.** Con `D7`
  sin activar, quien contesta es un proveedor **falso determinista**: lo que su respuesta demuestra es
  que el camino funciona (aditividad, estados, umbral), **no** que la lección propuesta sea pertinente.
  Por eso ninguna fila propuesta puede escribirse en `00-lecciones-capitalizadas.md` §2 por el propio
  script ni por el cierre de la fase: **cada propuesta exige revisión humana explícita, y su
  aceptación o rechazo queda registrada con quién la decidió** (aceptada → entra con dueño y «qué
  cambia» reales; rechazada → se publica el rechazo con su motivo, no se borra). Esto es AC12 en su
  parte de `a-revisar-humano`, es AC10 (aditividad) del lado del documento, y es la familia de
  `VACUOUS_RECALL` que la matriz §2 ya descartó: **un verde con proveedor falso no es evidencia de
  pertinencia.**
- **AC13** — ≥1 test contra **corpus real archivado**, no contra fixture propio (R2.6). El skip
  por baseline ausente es `pytest.mark.skipif` explícito y la evidencia declara **si el test
  corrió o se saltó**. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` con el nombre del test y su marcador.
- **AC14** — Mutation check (R2.8) sobre el guard real de AC10 y AC11, con las dos salidas en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`.
- **AC15** — Denominador propio y **términos usados**: el artefacto imprime a cuántos de los 320
  IDs aplicó juicio, sobre qué población, con qué términos de búsqueda, y el conteo que arrojó la
  capa fría con esos términos (incluidos los ceros como en A5). Sin esto, el triaje repite el
  defecto que pretende curar. Publica además **aceptabilidad**: `acceptance` = candidatos propuestos
  que resultaron pertinentes sobre el total propuesto, con su muestra y su método. Ese número es el
  **disparador de la deuda D6** y lo único que decide si el lint de contradicciones se abre en este
  directorio o en uno nuevo. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json`.
  - **⟦DECLARADO el 2026-09-23 (orden §4.C): el tramo semántico de AC15 permanece NO-EJERCITADO, con
    motivo⟧** — y no es un descuido ni un ⚠️ prestado: con `D7` sin activar el único emisor de juicio es
    un proveedor **falso**, así que `acceptance` se publica como `NO-EJERCITADO` con el motivo literal y
    **D6 sigue dormida**. No se abre un lint de contradicciones semánticas sobre una base que nunca juzgó
    nada, y **no** se reemplaza el número por una aceptabilidad simulada con el falso para poder cerrar
    el AC: eso convertiría el disparador de una deuda en una cifra fabricada. Lo que C **sí** cierra con
    el falso es la mecánica —aditividad (AC10), estados del índice (AC11), umbral publicado (AC12),
    mutation check (AC14) y denominador con términos y ceros (AC15, su parte no semántica)— y lo que no,
    se declara con su nombre. **Re-evaluar D6 toca cuando exista un proveedor real, no antes.**

### FASE-D — `build_phase_briefing.py` (pack derivado y delta de lectura)

- **AC19** — El generador recorre los prompts de fase del plan, extrae la lista de lectura que cada
  uno **declara**, resuelve cada sección nombrada y emite un pack por fase. `.agents/` no se escribe
  ni se copia como sustituto. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` clave `packs[]` con
  `no_incluye[]` y `lectura_aparte_obligatoria[]` — el workflow canónico figura ahí, porque este plan
  no lo rebaná (D3).
- **AC20** — El delta de carga de lectura se mide con el **mismo comando** en los dos lados (`stat
  -c %s` por documento declarado; la estimación de tokens declara su divisor). Artefacto:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` con `before`, `after`, `method` por fase y total, más el par
  `*_baseline_pre.txt` / `*_baseline_post.txt` con la resta comprobada (R2.3, R2.7). El delta se
  reporta sobre las fases de **este** plan; la fila de `REFACTOR-WHATSAPP` se publica como
  referencia, no como objetivo. **Un delta cero o negativo es un resultado válido y se explica**: lo
  prohibido es afirmarlo sin medir.
  - **⟦Carga total, añadida el 2026-09-24 por el bloque C de la orden §4.C, fila `CONTEXTO/D`⟧**
  La resta de AC20 se saca entre **cargas totales**, no entre «bytes de las fuentes» y «bytes del
  pack». Cada lado publica los tres sumandos definidos en el contrato (§Carga total y frescura del
  pack): `workflow_obligatorio` (lo que la fase sigue leyendo aparte, con el workflow canónico a la
  cabeza mientras D3 no lo rebane), `coste_de_generacion` (la corrida del generador que la sesión
  ejecuta para obtener el pack) y `pack_consumido`. **Prohibido describir la concatenación como
  ahorro**: unir N documentos no reduce la suma de sus bytes y puede subirla. Lo que AC20 puede
  acreditar es cuánto deja de leerse porque **no** entró al pack, y eso solo se ve si se publica
  también lo omitido (`no_incluye[]`). Si la carga total sube, el resultado es ese y se explica.
- **AC21** — Cada pack declara `provenance` con `head`, `generated_at` y `sha256` por fuente;
  `--check` falla contra un árbol modificado. La prueba se hace **editando una fuente y re-midiendo
  en disco**, no leyendo el objeto en memoria (L-V2.3, R2.4).
  - **⟦Frescura por entradas relevantes, añadida el 2026-09-24 (orden §4.C, fila `CONTEXTO/D`)⟧**
  El predicado de caducidad es **el sha256 de cada fuente listada en `sources[]` contra el árbol
  vigente**, con sus tres causas distinguibles (`FUENTE-AUSENTE` / sha distinto / fuente ilegible).
  `head` identifica de qué árbol salió el pack; **no** es la llave de caducidad. Razón: el pack es un
  generado versionado, de modo que si HEAD gobernara, el commit que lo guarda lo dejaría vencido en
  el mismo commit — invalidación circular. Consecuencias probables y con test: HEAD distinto con
  fuentes idénticas **no** produce `VENCIDO` (se informa como procedencia distinta); el pack no está
  en su propio conjunto de fuentes; y mover una fuente sí lo vence.
  - **⟦Traslado del plan, mismo bloque⟧** AC19 obliga al generador a resolver un plan **también bajo
    `Archives/`**, porque el cierre del RELEASE regenera y verifica el pack **después** del `git mv`.
    El rojo de un `--check` llamado sobre rutas ya movidas no se repara editando código: se repara
    regenerando con la ruta vigente (§Orden del cierre del contrato).
- **AC22** — Tres estados, ninguno colapsado: `COMPLETO`, `SECCION-NO-RESUELTA` (nombra la sección
  pedida y las rutas intentadas) y `FUENTE-AUSENTE` (ruta buscada). **Prohibido emitir un pack más
  corto en silencio**: el recorte no resuelto es un estado, no una reducción. Un `except` que devuelva
  el pack parcial está prohibido (L-PF6, L-PF10).
- **AC23** — Mutation check sobre el símbolo real que niega el truncamiento, con rojo y verde en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/`. Sin el lado rojo, AC23 queda ⚠️ (R2.4).

### Transversales

- **AC16** — El conteo de checks del `--quick` y del hook queda inalterado en **todo** el plan
  (delta 0, par pre/post por fase, resta comprobada). Es la AC que abre la puerta a que este plan
  corra mientras otro está en vuelo. **La medición de «quién afirma el 11 y el 7» barre también
  `tests/`**, no solo los documentos: L-V2.3 se capitalizó justamente porque el rojo vivo estaba en
  un contract test. Medido el 2026-09-20: `tests/test_validate_plan_closure.py` assertiona `[5/7]`
  dentro del hook, y `tests/test_validate_lesson_capitalization.py` ya quedó re-atado a coherencia
  estructural (grupo derivado de `run_all`, ordinales exactos `1..D`) en lugar del literal.
- **AC17** — Este plan **no** modifica `.agents/`. Declara además, en su propia salida, las
  familias de aserción que no cubre (L-HF1, L-R.4). Artefacto: `coverage.json` clave
  `families_not_covered[]`, con **las cuatro familias de AC2 nombradas una por una** (prosa sin
  patrón; conteos fuera de los documentos de gobierno —`AGENTS.md`, `docs/GUIA_TECNICA.md`,
  `docs/contributing/REGISTRY.md` con «check 8»/`[9/9]`/`[10/10]`/`10/10…14`—; pins de conteo en
  `tests/`; y toda fuente dinámica que no sea etiqueta impresa) y, para cada una, si queda como
  límite permanente o como trabajo de **D1**. Un `families_not_covered[]` genérico no cierra AC17.
- **AC18** — Los artefactos del plan pasan, sobre el mismo árbol final verificado,
  `validate_lesson_capitalization.py` (C1–C8), `validate_plan_citations.py` y
  `build_lesson_index.py --check`. El commit es opcional, posterior y requiere autorización explícita:
  no condiciona ninguno de los cinco cortes. Ningún AC ni prompt cita `archivo:número` (R2.2).

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 25266 bytes copiados de 51507 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `01-plan-maestro.md` §6

## 6. Deuda con dueño y disparador

Los IDs coinciden con la tabla de `dependencias-fases.md`. Ninguna fila se cierra reinterpretando
en silencio una restricción del plan.

| # | Deuda | Dueño | Disparador |
|---|---|---|---|
| D1 | Corregir o retirar las aserciones A1–A4 en `.agents/` (eliminar la aserción del documento y dejar que el verificador la imprima es la opción que no se desfasa) | Este plan, FASE-RELEASE, **solo con instrucción literal del operador**: `.agents/` es configuración central | **Estado vigente: matriz §13 de la fuente única (§1); no se certifica aquí.** El disparador fue reformulado a verificador operativo con mutation check y decisión escrita del operador. **Antecedente retirado, no aceptación vigente:** «Verificador verde y decisión escrita sobre la forma de la corrección». **⟦El dictamen anterior decía EJECUTADA el 2026-09-23 por el bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, con instrucción literal del operador y ampliación expresa para tocar `lecciones-capitalizadas-template.md` (fuente de A4): las cuatro aserciones se retiraron desde su fuente, el árbol real sale `SIN-HALLAZGOS`, y A1–A4 quedaron como contraejemplo congelado con sus mutantes. El disparador circular («verificador verde») se reformuló en la fila D1 de `dependencias-fases.md` y se cumplió. Ver `dependencias-fases.md` §Ejecución del bloque B y la evidencia `…/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/`.⟧** |
| D2 | Promover `validate_governance_numbers.py` a un check adicional del `--quick`, renumerando de 11 a 12 y midiendo quién afirma el número (L-V2.3) | Plan propio, posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases en vuelo que pineen «11 checks». **⟦Estado del disparador, bloque C de la orden de calidad, 2026-09-24: su rama literal se cumplió en parte** — las instrucciones prospectivas de ese plan ya no pinean la cifra, que ahora imprimen la corrida y `validate_governance_numbers.py` —, **pero D2 no queda abierta por eso.** Su otra mitad sigue viva: renumerar toca los pins del denominador que FASE-A dejó en `tests/` (fila S8 de `10-analisis`) y contradice AC16, que exige delta 0. Dueño y decisión intactos; ver la aclaración datada en la fila D2 de `dependencias-fases.md`⟧ |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura por sesión: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B de `REFACTOR-WHATSAPP`; la cifra de concepción era 254.010 y venció el mismo día — ver A7) | Plan propio, posterior | Mismo disparador; exige medir qué parte del documento consume cada fase. **Distinto de FASE-D**: el pack unifica lecturas, no recorta la fuente. **⟦Adelanto parcial, no cierre (bloque B, 2026-09-23): los principios de proporcionalidad/reuso y los cinco cortes sin commit quedaron escritos como pautas del executor; el rebanado completo y su medición de carga siguen diferidos a este disparador, con el dueño original intacto («Plan propio, posterior»)⟧** |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** entre los prompts de fase y el estado real del plan (`validate_plan_semantics.py`): fila que sigue llamando PENDIENTE a una fase cerrada, dos ACs incompatibles, instrucción de fase que choca con una regla del executor. Con falsos positivos medidos contra los 27 archivados | Plan propio, posterior — **mismo directorio si el disparador se cumple dentro de la vigencia de este plan** | **Condicionado al resultado de FASE-C**: que el triaje de pertinencia entregue candidatos que el Paso 0 no ancló, con la aceptabilidad medida (propuestos que resultaron pertinentes sobre el total propuestos) publicada en el informe. Si el triaje sale inaceptable, D6 **no** se activa: no se apila un segundo consumidor sobre una base que no funcionó |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev): añadirlo como segundo proveedor detrás de `decision_client.py`, correr la comparación que AC9 ya no exige, y restituir «elegir midiendo» como AC | Plan propio posterior; el acceso existe desde 2026-09-20 por decisión del operador | Que AC9 haya cerrado en verde la costura y que algún consumidor real lo pida — el candidato natural es D6, porque es el único trabajo del lote genuinamente semántico |
| D8 | Re-ejecutar la consulta Q7 de QMind que esta concepción no pudo correr. **Premisa vencida y corregida el 2026-09-20: el CLI `qmind` v3.3.0 SÍ está disponible y autenticado** (cuatro `retrieve` reales contra el notebook, con hits de `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y `TRIBUNAL-OFFLINE-2026-09-09`). **Y el comando registrado en `00-lecciones-capitalizadas.md` está mal:** `--nb iah-cli-lecciones` devuelve `error: Bad request`; `--nb` exige el **ID** `01a04d98-b7bd-778c-8441-26fdc7e35f45` (medido con las dos formas) | Este plan, sesión previa a FASE-RELEASE — o **antes**, ya es ejecutable | Fallback re-escrito en `00-lecciones-capitalizadas.md` §4 con el comando que funciona |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice obligatoria después |
| **D10** | **Re-leer la interfaz del write-back antes del cierre.** `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE, con disparador anterior al `FASE-RELEASE` de `REFACTOR-WHATSAPP`) declara dentro de su alcance `scripts/validate_qmind_writeback.py` **y su connection en `scripts/run_all_validations.py`**, y piensa añadir `--title`/`--file` y fin de la degradación a PASS. El orden de cierre de este plan (§`04-contrato-ejecucion.md`) invoca ese script | Este plan, FASE-RELEASE | Que al llegar el RELEASE se ejecute `validate_qmind_writeback.py --help` contra el árbol vigente y el orden se re-escriba si la interfaz cambió. **No** es dependencia de ejecución: este plan puede correr antes o después, y AC16 (delta 0) sigue protegiendo el conteo |

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 6440 bytes copiados de 51507 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `04-contrato-ejecucion.md` §Dos momentos del cierre

## Dos momentos del cierre (añadido por el bloque C de la orden de calidad §4.C)

| Momento | Qué contiene | Red | Autorización | Qué se publica si falta |
|---|---|---|---|---|
| **Cierre offline** | Lecturas y verificadores sin escritura; sync, documentos, registro y derivados únicamente sobre destinos autorizados | **No** | Mandato de RELEASE más autorización literal de los archivos escribibles, comprobada en C0 del prompt RELEASE | Detenerse antes de escribir si falta un destino necesario: `PENDIENTE-AUTORIZACION`, no cierre cumplido |
| **Aceptación remota** | re-corrida de la consulta Q7 (D8) y `--upload` del `10-analisis` antes del `git mv` (D9) | **Sí** | **Literal y propia para cada una**, con presupuesto escrito | Estado `PENDIENTE-AUTORIZACION` con su causa, **no** un PASS ni un `[OK]` por omisión |

**Rectificación 2026-09-25:** «cierre propio de la fase» no otorgaba permiso sobre configuración central.
Rige **C0 del `05-prompt-inicio-sesion-fase-RELEASE.md`**: releer los destinos reales antes de escribir.
`sync_versions.py --check` no escribe; el sync en escritura requiere autorización literal para sus
consumidores de `scripts/sync_config.yaml`. `VERSION.yaml` es entrada, con permiso propio para cambiarla.
La alineación de política de DOMAIN_PRIMER no se autoriza mediante el sync de cabeceras. Tampoco se
actualizan baselines para absorber errores. Sin permiso suficiente, checkpoint previo, no cierre completo.

El archivado (`git mv`) es un **tercer** momento y conserva su autorización separada: no la concede el
cierre offline ni la sustituye una subida pendiente. Con la aceptación remota pendiente, el plan
**puede** archivar solo si el operador lo autoriza expresamente sabiendo que la fuente no se publicó;
si no, deja checkpoint. Nunca se promueve un resultado parcial a éxito del cierre (§Orden del cierre).

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md` · sha256 `c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5` · 1874 bytes copiados de 29211 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `04-contrato-ejecucion.md` §Carga total y frescura del pack

## Carga total y frescura del pack (añadido por el bloque C de la orden de calidad §4.C)

Las tres reglas anteriores dejan abiertos dos puntos que la fila `CONTEXTO/D` cerró: **qué se cuenta
como carga** y **qué mueve la frescura**.

**Carga total (AC20), no «bytes del pack».** El pack unifica lecturas; no las elimina. La medición de
`carga.json` publica por fase los tres sumandos y la resta se saca entre los dos totales, no entre el
pack y la lista de documentos:

| Sumando | Qué entra | Por qué no puede faltar |
|---|---|---|
| `workflow_obligatorio` | Los bytes de lo que la fase **sigue** leyendo aparte (`lectura_aparte_obligatoria[]`): el workflow canónico mientras D3 no lo rebane, y toda fuente declarada y no incluida | Si no se cuenta, el pack aparece como ahorro cuando la fase lee lo mismo más el pack |
| `coste_de_generacion` | La corrida del generador que la sesión ejecuta para obtener el pack (invocación publicada y, si el instrumento corre, su coste) | Un artefacto que hay que producir no es gratis para quien lo consume |
| `pack_consumido` | Los bytes del pack que la fase efectivamente lee | Es el único sumando que el pack reemplaza |

**Prohibido presentar la concatenación como ahorro.** Juntar N documentos en un archivo no baja la
suma de sus bytes; puede subirla (encabezados, procedencia al pie, `no_incluye[]`). El ahorro real
solo puede venir de lo que **no** se copia al pack, y eso se mide declarando qué se omitió. Un delta
cero o negativo sigue siendo resultado válido y se publica igual (AC20). La fila D3 del maestro conserva
su dueño: el recorte de la fuente **no** es lo que mide esta resta.

**Frescura por entradas relevantes; HEAD es procedencia.** AC21 fija el criterio: `--check` vence el
pack comparando **el sha256 de cada fuente listada en `sources[]` contra el árbol vigente**, y fallando
por una de tres causas distinguibles (`FUENTE-AUSENTE` / fuente con sha distinto / fuente ilegible).
`provenance.head` se publica para identificar **de qué árbol salió** el pack, no para invalidarlo: si
el sha de HEAD gobernara la caducidad, el propio commit que guarda el pack generado lo dejaría vencido
en el instante de publicarse — circularidad que la orden §4.C nombró expresamente. Consecuencias
operativas:
- el pack **no** está en su propio conjunto `sources[]`, ni tampoco el commit que lo transporta;
- un HEAD distinto con las fuentes idénticas **no** vencifica el pack: se informa el desfase como
  procedencia distinta, no como `VENCIDO`;
- la invalidación la produce un cambio en una fuente gobernada, nunca el acto de versionar el generado.

**Regeneración y verificación tras el traslado.** El `git mv` del RELEASE cambia las rutas que el pack
declara como fuentes, así que **`--check` después del traslado sin regenerar tiene que fallar**: ese
rojo es un paso del cierre, no una reparación. El orden queda fijado en §Orden del cierre: regenerar
el pack con la ruta ya trasladada y **después** verificarlo. Regenerar un artefacto derivado con su
propio generador es operación de cierre autorizada a RELEASE; **modificar `build_phase_briefing.py`
para que el check pase no lo es** (§Restricciones del prompt de RELEASE: RELEASE no modifica código).

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md` · sha256 `c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5` · 3250 bytes copiados de 29211 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `04-contrato-ejecucion.md` §Orden del cierre

## Orden del cierre (R2.5 / R2.10, no permutable)

**Paso 0 (D10, añadido en la auditoría del 2026-09-20):** antes de correr el bloque, verificar la
interfaz del writer contra el árbol vigente — `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --help`
— porque `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` puede haber añadido `--title`/`--file` o quitado la
degradación a PASS. Si cambió, se re-escribe este bloque **con su nota datada** antes de ejecutarlo.
Este paso es **de lectura**: corre aunque la aceptación remota siga sin autorizar.

**Cada línea lleva su momento (§Dos momentos del cierre).** Las marcadas `⟦remoto⟧` no se ejecutan con
el permiso del cierre documental: necesitan su autorización literal y su presupuesto, y si faltan se
declaran `PENDIENTE-AUTORIZACION` sin promover el cierre a éxito. La marcadas `⟦traslado⟧` requieren la
autorización propia del archivado.

```bash

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md` · sha256 `c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5` · 928 bytes copiados de 29211 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `00-lecciones-capitalizadas.md` (documento completo)

# Lecciones Capitalizadas — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> **Creado**: 2026-09-20, antes de `01-plan-maestro.md`. **Actualizado**: al cierre de cada fase.
> **Plan**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 · **Objetivo**: cerrar la mitad que
> `validate_lesson_capitalization.py` declara fuera de alcance (la **pertinencia**), la coherencia
> numérica entre el workflow canónico, sus templates y el código que ejecutan, y la **carga de
> lectura** que cada sesión de fase arrastra antes de tocar código.

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado medido |
|---|------|------------------|------------------|
| Q1 | Índice generado (capa fría) | `for id in L-R.1 L-R.3 L-R.4 L-NC10 L-PF6 L-PF10 L-D3 L-V2.3 L-T4A.5 L-VUP-5; do grep -oE "\\| \\\`${id}\\\`.*" .opencode/LECCIONES-INDEX.md; done` | **10 de 10** devuelven fila con dueño y conteo de citas |
| Q2 | Índice generado — corpus **completo** por síntoma | `grep -icE "numer" .opencode/LECCIONES-INDEX.md` · `… "fosiliz"` · `… "renumer"` · `… "denominador"` · `… "cobertura medida"` · `… "falso verde"` | 20 · 7 · 1 · 1 · 2 · 2 |
| Q3 | Índice generado — término buscado, **cero coincidencias** | `grep -icE "verificador mec" .opencode/LECCIONES-INDEX.md` | **0** — medido en vivo, ver §3-descarte D5 y AC15 |
| Q4 | Población del índice (denominador) | `head -18 .opencode/LECCIONES-INDEX.md` | **Re-medido tras cada regeneración**: 15 análisis + 36 `CONTEXT-*.md` como definiciones; **320** IDs con definición detectada; **50** citados sin definición; **402** `.md` como corpus de citas. La fila decía 14 / 49 / 389 al concebirla, pasó a 15 / 50 / 401 al entrarse el plan y a **402** al escribirse el prompt de FASE-D — tres valores en una sesión; ver maestro §1, medición **A6** |
| Q5 | Fuente de verdad dinámica de los conteos | `grep -nE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py` | 11 etiquetas `[N/11]` (quick) y 4 `[N/15]` (full). **La lectura útil es la asociación etiqueta ↔ `def _check_*`, no la lista**: `[12/15]` es `def _check_dependencies` y `[15/15]` es `def _check_qmind_writeback`. Omitir ese emparejamiento produjo la medición vencida de A3 (ver maestro §1, rectificación de A3 y medición A8) |
| Q6 | Memoria de proyecto (capa caliente) | `MEMORY.md` → entradas *verificador-medido*, *no-implementar-aun*, *quien-produce-el-dato-publicado* | 3 entradas leídas; la tercera fija que la cura de una aserción vencida es un **writer o un verificador**, no el edit |
| Q7 | Notebook QMind `iah-cli-lecciones` | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "…" --format agent --non-interactive` | **Concebida como NO EJECUTADA** («el CLI no está disponible en esta sesión»); **ejecutada el 2026-09-20 en la auditoría de la concepción**, con el CLI disponible y autenticado (v3.3.0, 49 fuentes en el notebook). Cuatro consultas: conteos desfasados, carga de lectura por fase, pertinencia del Paso 0, presupuesto de iteraciones. **El comando original con el nombre (`--nb iah-cli-lecciones`) devuelve `error: Bad request`: `--nb` exige el ID** (medido con las dos formas). Resultados capitalizados abajo como L-V2.1, L-V2.2 y D-V2.1; deuda **D8** re-escrita |
| Q10 | Re-medición de la premisa al abrir **FASE-B** (2026-09-21) — el prompt de FASE-A dejaba la herencia y B no la asumió | `git rev-parse --short HEAD` · `git status --porcelain` · `grep -cE 'print\(f?"\[[0-9]+/11\]'` sobre `run_all_validations.py` · `grep -cE '^#   \[[0-9]+/[0-9]+\]'` sobre el hook · `git ls-files '*.py' \| wc -l` · `git grep -cE '^\s*(import\|from)\s+(typesafe\|jev\|httpx2)' -- '*.py'` · `python -c "import importlib.util as u; print([u.find_spec(m) is not None for m in ('typesafe','jev','httpx2','tenacity')])"` bajo el venv del producto · `find . -name '*.jsonl' \| wc -l` · `stat -c %s` sobre los siete documentos de A7 | HEAD ya no era `e3c4573` sino **`74d8ff5`** (dos commits de barrido documental de FASE-A encima), árbol con **dos rutas ajenas** preexistentes y ninguna creada por B; quick **11**, hook **7**; **0** imports del SDK en los 678 `.py` rastreados (692 en el árbol de trabajo al cerrar; 690 en el primer escaneo) y el SDK **AUSENTE** del venv del producto — pero **presente en el disco** bajo `tmp_test/venv-jev-sdk`, exclusión publicada con su conteo; `*.jsonl` = **0** (D-V2.1 reproducida de nuevo, el instrumento de presupuesto otra vez fuera de servicio); A7 **263.973 bytes ≈ 65.993 tokens**, sin cambio |
| Q11 | **Re-medición tras el commit de FASE-B (2026-09-22)** — el barrido de citas que ese mismo commit venció | `git rev-parse --short HEAD` · `git status --porcelain` · `git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `git show --numstat --format="" 647f436 \| grep -cE '\\.py$'` · `git ls-files '*.py' \| wc -l` · `python scripts/decision_client.py --scan-imports` · `grep -cE 'print\\(f?"\\[[0-9]+/11\\]'` sobre `run_all_validations.py` · `grep -cE '^#   \\[[0-9]+/[0-9]+\\]'` sobre el hook · `find . -name '*.jsonl' -not -path './venv/*' \| wc -l` | HEAD **`647f436`** (el commit de B: 46 archivos, +4.412/−97, **13** de ellos `.py`) sobre `eecf246`, que **sigue sin empujar** — el remoto está en `74d8ff5`, paridad **`0/2`** a esa hora (`0/3` al cerrar el barrido que escribe esta fila: cada commit documental suma uno), con el push todavía sin autorizar a esa hora — **quedó hecho el mismo día: `origin/master` en `b764e8d`, paridad `0/0` re-medida tras `git fetch`, y el push publicó de paso el commit ajeno `eecf246`**; **una** ruta ajena sucia. El denominador que la fase publicó quedó refutado por su propio commit: `git ls-files '*.py'` **678 → 691**, mientras el escáner sigue viendo **692** y el numerador **no se mueve** (`SIN-HALLAZGOS`, 0 imports, 0 cargas dinámicas, 21 menciones). El residuo de 1 se **descompuso** con `comm` contra el `rglob` y es `.venv-wsl/bin/activate_this.py` → **S11** / **L-VCF-11**. Quick **11**, hook **7** (sin cambio), `*.jsonl` = **0** (sexta reproducción de D-V2.1, el instrumento de presupuesto sigue fuera de servicio); índice regenerado tras el barrido: **332** IDs definidos + 51 sin definición, **16** análisis y **416** `.md` citados (330 antes del barrido; el +2 son L-VCF-11 y L-VCF-12, y los análisis/.md se mueven por el plan hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`, entrado al corpus en `2c966f6` con 12 `.md`). **Y el propio re-muestreo pisó la evidencia cerrada de FASE-A** (`--report` con destino hardcodeado), medido y revertido → **L-VCF-12** / **S12** |
| Q13 | **Re-medición de la premisa al abrir FASE-D (2026-09-24) — la herencia de D no se asumió** | `git rev-parse --short HEAD` · `git status --porcelain \| wc -l` · `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `git status --porcelain .agents/` · los dos `grep -cE` del quick (11) y del hook (7) · `python scripts/run_all_validations.py --quick` · `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` · `stat -c %s .agents/workflows/phased_project_executor.md` · `python scripts/build_phase_briefing.py --listar-declarado --plan <este plan>` · recuento de prompts que declaran lectura: `Glob .opencode/plans/Archives/*/05-prompt-inicio-sesion-fase-*.md` filtrado por el parser · `python scripts/build_lesson_index.py --check` sobre un arbol extraido con `git archive HEAD` | HEAD **ya no era el `da382b1` que registro C: es `5817edd`** — el commit y el push del propio cierre de C movieron la cabecera despues de que C escribiera su evidencia (A6 sobre la fase anterior, medida al abrir la siguiente); paridad **`0 0`** verificada con `fetch` + `ls-remote`, no inferida. Arbol con **63 rutas sucias ajenas** al medir (ninguna creada por esta sesion al abrir) y **3 de ellas bajo `.agents/`** (executor y dos templates, del bloque B de la orden de calidad) — lo que hace **no verificable la casilla literal** «`git status .agents/` vacio al cerrar», reformulada como «cero bytes aportados por la fase» y afirmada con el observador de escrituras. Quick **11/11 `exit 0`** como par PRE y hook **7**. `*.jsonl` = **0** → **octava reproduccion** de la precondicion de **D-V2.1**, metrica retirada y auto-reporte con unidad declarada. **A7 vencida en su propio dato de entrada**: el workflow canónico pesa hoy **108.017 bytes**, no los **98.694** que publica el maestro §1 (+9.323 desde 2026-09-20, por las ediciones del bloque B), y la carga declarada de **este** plan es **5 fases · 34 fuentes**, con su total en `FASE-D/carga.json` (el número **no se copia aquí**: ver **L-VCF-19** — este `.md` entra en el pack que ese `stat` mide, y de hecho la corrida del cierre lo movió **dos veces**, una por cada barrido documental que se escribió después de medirlo). **Y la convencion que parsea el generador resulto minoritaria**: de **121** prompts archivados, **0** declaran su lectura con la cadena `Lee …`; los unicos **5** del repo estan en este plan → deuda **S16**. El `--check` del indice dio **FAIL** (`exit 1`) tambien sobre un arbol limpio extraido de `5817edd` con `git archive`; **regenerado en ese mismo arbol** paso a `exit 0` con **335** IDs — que es la firma de **S15**: 9 entradas con `fuente_fecha = mtime`, de modo que cada extraccion las vuelve a vencer y commitear el par desde otro arbol no lo cura. Nada del antecedente del prompt se copio como valor vigente |
| Q12 | **Re-medición de la premisa al abrir FASE-C (2026-09-24) — la herencia de C no se asumió** | `git rev-parse --short HEAD` · `git status --porcelain \| wc -l` · `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `python scripts/build_lesson_index.py --check` · `python scripts/run_all_validations.py --quick` · los dos `grep -cE` del quick (11) y del hook (7) · `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` · `python scripts/decision_client.py --scan-imports` · `ls .opencode/plans/Archives/ \| wc -l` y `ls .opencode/plans/Archives/*/00-lecciones-capitalizadas.md` | HEAD **sin cambio** respecto del antecedente publicado y **paridad verificada contra el remoto** (`fetch` + `ls-remote` + `0 0`), no inferida de la frase del README; árbol con **62 rutas sucias de trabajo ajeno** (las del bloque B, del bloque C de la orden y de `EVALUACION-JEV`), ninguna creada por esta sesión al medir; índice **fresco** con su cifra leída del comando (no pineada en ningún artefacto de C); quick **11/11 `exit 0`** como par PRE de AC16 y hook **7**; `*.jsonl` = **0** → **séptima reproducción** de la precondición de **D-V2.1**, el instrumento de presupuesto sigue fuera de servicio y C declara auto-reporte con unidad propia; AC6 `SIN-HALLAZGOS` / `exit 0` **antes** de escribir C. **Y la premisa de AC13 resultó vencida en su ruta**: el prompt decía `Archives/`, el `archives/` de raíz **no contiene planes**, y el corpus efectivo es `.opencode/plans/Archives/` con **27** archivados de los que **2** tienen `00-` que triar. Nada del antecedente del prompt se copió como valor vigente |
| Q9 | **Re-medición de la premisa al abrir FASE-A (2026-09-21)** — el prompt ordenaba no asumir el árbol | `git rev-parse --short HEAD` · `git status --porcelain | wc -l` · `git ls-remote origin refs/heads/master` · `grep -nE '^[[:space:]]*(def _check|print.f?"\[[0-9]+/[0-9]+\])' scripts/run_all_validations.py` · `grep -nE '^#[[:space:]]+\[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit` · `stat -c %s` sobre los siete documentos de A7 · `grep -rhoE '\[[0-9]+/[0-9]+\]' <los dos documentos> | wc -l` | HEAD ya **no** era `2c9d0c1`: es `2deddee`, con once commits de `EVALUACION-JEV-TYPESAFE-2026-09-21` encima; árbol **limpio** y paridad `0/0` con `origin/master` **conservadas**. El emparejamiento etiqueta ↔ `def _check_*` reproduce A1–A3 (`validate_plan_citations` 9/11, `validate_lesson_capitalization` 10/11, `validate_qmind_writeback` **15/15** solo en el modo completo); el hook sigue en **7** pasos; A7 sigue en **263.973 bytes** y la población A8 se reprodujo **exacta**: 22 instancias con corchete en 17 líneas + 2 formas «check N». **Ninguna premisa del plan caducó en la ventana de A salvo el HEAD anunciado**, que es justo lo que el prompt ordenaba medir |
| Q8 | Carga de lectura de una sesión de fase (medición A7) | `for f en los 7 documentos sumados (más 1 de evidencia excluido) que declara leer 05-prompt-inicio-sesion-fase-B.md del plan en vuelo; do stat -c %s "$f"; done` y sumar | Al concebir: **254.010 bytes ≈ 63.502 tokens**. **Re-medido el 2026-09-20: 263.973 bytes ≈ 65.993 tokens** (+9.963; crecieron `06-checklist`, `00-lecciones`, `dependencias-fases` y el propio `05-…-fase-B.md` al cerrarse FASE-G y FASE-B del plan medido). Divisor 4 declarado. El workflow canónico aporta 98.694 bytes, de los cuales ~20 KB son plantillas de cierre |

**Regla**: la consulta debe ser copy-pasteable. Q1–Q6 y Q8 se re-ejecutan tal cual; **Q7 solo con el
ID del notebook** (la forma con el nombre que aparece en el workflow canónico devuelve `Bad request`,
medido el 2026-09-20). **Toda cifra de Q4
y Q8 caduca al escribir cualquier `.md` del corpus** — ver maestro §1, mediciones A6 y A7.

## 2. Lecciones capitalizadas

| ID | Enunciado (una línea) | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|--------------------|-------------------------|-----------------|
| L-R.1 | Una regla que vive solo en el workflow y no en el artefacto que la fase rellena, se cumple por coincidencia | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | El plan existe porque las aserciones numéricas del workflow y de su template **no las sostiene ningún check**: se cumplen por coincidencia y hoy están vencidas | AC1 · FASE-A Tarea 1  · **aplicada el 2026-09-21 en FASE-A:** el verificador ahora contrasta contra la etiqueta impresa por el `def _check_*` que la ejecuta; las cuatro aserciones siguen vencidas sin que ningún gate las sostenga, y el guard existe (reporta, no reescribe) |
| L-R.3 | Un `[OK]` sin denominador no informa: el verificador publica la población que miró | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Ninguna salida del lint o del triaje puede decir «sin hallazgos» sin imprimir cuántas aserciones/IDs miró y quiénes quedaron exentos | AC2 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `coverage_basis` es obligatoria y el favorable está bloqueado sin ella (prueba `test_la_salida_favorable_no_existe_sin_denominador`); con denominador impreso: 24 miradas / 11 correctas / 8 congeladas / 0 no resueltas · **aplicada el 2026-09-21 en FASE-B (AC6/AC9):** el `0` de imports se publica con **dos** poblaciones (678 rastreados por `git grep` / 692 del árbol que ve el AST), los 4.379 nodos de import vistos, las 21 menciones-no-import aparte y los excluidos por directorio con su conteo; y el `1` de `files_changed_to_add_provider` sale de sha256 sobre la frontera copiada, no de una afirmación (L-VCF-8) · **aplicada el 2026-09-24 en FASE-D:** `coverage_basis` del informe imprime 5 packs por estado, 34 fuentes, 23 secciones pedidas / 23 resueltas y las cinco familias no cubiertas; y el corpus real se publica con su denominador de convencion (**0 de 121** prompts archivados declaran lectura) en lugar de un `[OK]` a secas |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Las tres reglas que este plan no cierra (promoción al quick, rebanado del workflow, arreglo de `.agents/`) se publican con dueño y disparador, no se callan | AC17 · `dependencias-fases.md` §Deuda  · **aplicada el 2026-09-21 en FASE-B:** la comparación de proveedores se declaró **fuera de alcance** en `extensibilidad.txt` con su porqué (D7) y la decisión de geometría que este plan **no** tomó salió con dueño y disparador nuevos: **S10** (L-VCF-9) |
| L-NC10 | Fosilización narrativa como clase de bug: templates con texto estático que ignoran la fuente dinámica de verdad | `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22` | Mismo defecto, otro artefacto: el template fija «`[10/10]` de `--quick»` cuando el código emite `[10/11]`. La cura es comparar contra la fuente, no reescribir la frase | AC1 · AC4  · **aplicada el 2026-09-21 en FASE-A:** la lista de aserciones se **descubrió** escaneando los dos documentos (24 instancias: 22 con corchete + 2 formas «check N»), no hardcodeada; A1 apareció en dos sitios que el patrón nunca había visto juntos · **aplicada el 2026-09-24 en FASE-D:** el generador no recibe ninguna lista de lecturas por configuracion: parsea la que el propio prompt declara. El test confronta `parsear_lista_lectura(prompt)` contra las fuentes del pack emitido, y `no_incluye[]` publica los bytes que quedaron fuera de lo declarado |
| L-PF6 | Un lector roto leído como ausencia real produjo un pain falso HIGH con cifra económica | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El triaje lee `lecciones_index.json` y el lint lee `.agents/`: ambos publican los tres estados, y un parser que revienta jamás devuelve «sin candidatos» | AC3 · AC11  · **aplicada el 2026-09-21 en FASE-A:** cuatro caminos de `LECTOR-FALLIDO` con motivo propio (fuente sin etiquetas, hook sin pasos, documento sin patrones, sujeto ambiguo por alias); ninguno devuelve «sin hallazgos» · **aplicada el 2026-09-21 en FASE-B (AC7):** la prohibición del default es el eje del módulo — `evaluar()` sin proveedor **falla** con 5 `motivo_clase` que no colapsan, y el mutante `M-AC7-proveedor-por-defecto` muestra que ceder un default sí fabricaría una decisión. Coste propio descubierto al medir: la regla «nadie más importa el SDK» aplicada sin graduar producía **16 hallazgos ajenos** (L-VCF-7) · **aplicada el 2026-09-24 en FASE-D:** el lector de la lista declarada falla ruidoso y por causas separadas — `--plan` inexistente = exit 2 con sus tres rutas intentadas; fuente ausente = el pack **no se emite** (exit 1) con la ruta buscada; meta sin sha = `FUENTE-ILEGIBLE`, que no colapsa con `FUENTE-AUSENTE` ni con `SHA-DISTINTO` |
| L-PF10 | Vacío ≠ ausente: la lista quedó vacía **porque el fix funcionó**, y el extractor devolvía `None` igual que cuando el dato no existe | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El estado `SIN-HALLAZGOS` del lint es un resultado positivo y debe decir sobre qué midió; `AUSENTE` debe imprimir la ruta buscada y el comando de regeneración | AC3 · AC11 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `SIN-HALLAZGOS` imprime sobre qué midió y `AUSENTE` la ruta buscada; un documento no vacío con 0 instancias es fallo de lectura, no «limpio» · **aplicada el 2026-09-21 en FASE-B:** `respuestas: []` es `ILEGIBLE` con causa `respuesta-vacia:list` (no «cero decisiones favorables»), `usage=None` **no** es consumo cero, y `noul.confidence` es `None` **con su motivo escrito**, no un 0.0 que FASE-C leería como certeza · **aplicada el 2026-09-24 en FASE-D:** al trío de AC22 hubo que sumarle un cuarto estado, `SIN-DECLARACION` (pack emitido con cero fuentes gobernadas), y el `--check` lo imprime como `SIN-FUENTES` en lugar de `OK` — con test que prohíbe la palabra OK en esa salida. Motivo medido: 121 prompts archivados no declaran lectura, y llamarlos «completos» era el verde vacio de L-HF1 |
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El invariante «el quick sigue en 11 checks» se formula como **delta** con par `*_baseline_pre/post.txt`, no como número absoluto | AC5 · AC16 · AC20  · **aplicada el 2026-09-21 en FASE-A:** los conteos se publicaron como delta con par pre/post y la resta (quick 0, hook 0, población A8 0); la métrica que sí se movió (tests, +23) se declaró aparte en lugar de maquillarla · **aplicada el 2026-09-21 en FASE-B:** quick 11→11, completo 4→4, hook 7→7, `.agents/` 98.694/6.123 idénticos y población AC6 678 sin mover y 690→**692** en el árbol (+2 por los instrumentos de la propia fase: nota 3 en `FASE-B/baseline-pre-post.md`) — con **+48 funciones / 53 casos** de tests publicados por separado. Y una elección de unidad: no se publicó un `tool_use` aproximado, porque no era medible (R2.1) · **aplicada el 2026-09-24 en FASE-D:** la carga de lectura se goberno como delta con par `faseD_carga_pre/post.txt` (`stat -c %s`) y resta **entre cargas totales**; cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py` (exit 0) y quick 11→11 / hook 7→7. Y un test planta una fuente diminuta para exigir que un delta **negativo** se publique con la misma identidad, no que se esconda |
| L-V2.3 | Renumerar el hook sin medir quién afirma el número de checks deja contrato huérfano | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Este plan **no renumera** nada: su AC5 y AC16 exigen medir la población que afirma los conteos antes de tocarla, y no pinear literales | AC5 · AC16 · AC8  · **aplicada el 2026-09-21 en FASE-A:** el barrido de `tests/` mostró que **esta fase añadió 4 pins del denominador 11** al fijar el contrato AC1 (L-VCF-5), declarados con dueño D1/D2 en vez de limar la aserción · **aplicada el 2026-09-21 en FASE-B (AC8):** el contract test afirma la **forma** y compara el modelo contra lo que el proveedor falso **declara**, nunca contra una cadena; el pin `jev-1.13.0` vive en `PIN_MODELO_DECLARADO` con `usado_por_el_codigo: false` y un test lo comprueba por AST (aparece una sola vez: su definición). FASE-B **no añadió** pins del 11 ni del 7 (4→4, medido) · **aplicada el 2026-09-24 en FASE-D:** AC21 se prueba **escribiendo la fuente en disco** y re-midiendo contra ese disco (y al revertir, verde); y AC23 se anclo con una cadena exclusiva del generador, porque «rutas intentadas» y «seccion pedida» ya vivian dentro de los documentos que el pack copia — un mutante anclado ahi daba rojo sin serlo |
| L-V2.1 | Un test que solo mira **qué check** disparó puede quedar verde por una rama distinta de la que pretendía observar | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Cada mutante de AC4 y AC14 se afirma sobre el `assertion_id`/la detección que dice atacar, no sobre «el script devolvió un hallazgo»: el rojo tiene que nombrar la aserción mutada | AC4 · AC14 |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto generado por **otro** gate | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | FASE-C lee `lecciones_index.json`, que produce `[6/7]`; la cura ya implementada por ese plan es **calcular el índice en memoria** con `build_lesson_index.build()` (0,30 s medidos). ⟦**Ruta CERRADA el 2026-09-23, contrato E2**: FASE-C consume el JSON **tras ejecutar él mismo** la comprobación de frescura, de modo que `VENCIDO` sea estado producido por su propio check y no por un `--check` ajeno; la ruta (a) queda descartada porque **borraría** el estado que AC11 exige, y sigue prohibida la tercera vía (leer el JSON confiando en que otro paso lo regeneró). Coste publicado: C es responsable de su suelo y hace dos lecturas del JSON por corrida⟧ | AC11 · AC15 |
| D-V2.1 | El instrumento canónico de R2.1 no alcanza el transcript de sesión bajo el cliente actual; la medición se publica como auto-reporte con **unidad declarada** | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` (definida allí; **reproducida en cuatro fases seguidas** por `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`) | El `04-contrato-ejecucion.md` de este plan ya aplica el patrón (instrumento, corte, y si no corre: unidad declarada, «no comparable», o métrica retirada — nunca estimada). Verificado el 2026-09-20: `find . -name "*.jsonl"` devuelve **0** dentro del workspace, la misma precondición del incidente | **AC5** · **AC16** (par pre/post por fase) · `04-contrato-ejecucion.md` §Corte de presupuesto |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Todo AC de detección del plan se cierra con mutation check sobre el símbolo real del guard, con las dos salidas en evidencia | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** seis mutantes sobre los símbolos reales del guard, con verde y rojo en disco — y el primer intento de anclaje (id posicional) **no** observaba la rama que decía certificar: ver L-VCF-1 · **aplicada el 2026-09-24 en FASE-D:** mutation check con las dos salidas en disco — apagado `GUARD_NO_TRUNCAMIENTO_ACTIVO` el pack conserva el estado `SECCION-NO-RESUELTA` pero **pierde la declaracion del recorte** y se achica en silencio (los dos tamaños y su diferencia viven en `FASE-D/mutation/resumen.txt`; **no se transcriben aquí**: este `.md` entra en el pack que lo mide → **L-VCF-19**). Un test aparte exige que el mutante NO cambie el estado: si lo cambiara, el rojo vendria de otra rama (L-V2.1) |
| L-VUP-5 | Una fase de extensión que no produce ni un rojo es un falso verde potencial | `Archives/VALIDADOR-URL-PROPIA-2026-08-30` | El verde de la primera corrida del lint se reporta **sospechoso** y se explica, nunca como éxito | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** el verde de la primera corrida **fue sospechoso y lo era**: la regla de población se rectificó dos veces y el mutation check nombraba a la aserción equivocada · **aplicada el 2026-09-21 en FASE-B:** la primera corrida de la selección dio **30 fallos** (f-string mal cerrado, `score` cayendo en `opciones` por argumento posicional, 8 aserciones mal apuntadas) y el primer mutante de forma apagaba la lista **entera**, que no aislaba a ningún guard (L-VCF-6). Rojos propios además de los buscados: AC8 guarda su `exit 1` en `contract.txt` |
| L-HF1 | Un candado con la cobertura equivocada pasa en verde mientras el artefacto miente | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El lint declara las familias de aserción que **no** cubre, una por una y medidas: prosa de conteo sin patrón, conteos fuera de los documentos de gobierno (`AGENTS.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`), pins de conteo en `tests/` y toda fuente dinámica que no sea etiqueta impresa. Ese límite es AC, no nota al pie | AC2 · AC17  · **aplicada el 2026-09-21 en FASE-A:** `families_not_covered[]` salió de la AC y del script: las cuatro familias medidas en el informe (3 / 245 / 4 archivos / 4.330 funciones en disk), y `git status --porcelain .agents/` quedó vacío · **aplicada el 2026-09-21 en FASE-B:** el escáner publica sus cuatro límites medidos (carga no literal → 16 sitios contados y no callados; dependencias declaradas → no miradas, es D7; menciones en prosa → aparte; exclusiones → con su conteo) y `git status --porcelain .agents/` volvió a quedar vacío con 98.694/6.123 bytes idénticos · **aplicada el 2026-09-24 en FASE-D:** `no_incluye[]` no vacio es exigido por test fase por fase, y del medir salio una regla nueva: lo que vive **fuera** de `.opencode/` se declara lectura aparte y no se copia, porque copiarlo dentro del plan ampliaba la poblacion que escanea `validate_opencode_refs.py` y un artefacto derivado le devolvio rojo al quick ([8/11]) por referencias ajenas |

Dueños distintos representados: **6** — TRIBUNAL-OFFLINE, REFACTOR-COHERENCIA-NARRATIVA, SR-PIPELINE-FIXES, ESTABILIZACION-PRE-TRIBUNAL, PASO0-VERIFICADOR-CAPITALIZACION y VALIDADOR-URL-PROPIA. Satisface C8 (≥2) con holgura y no repite solo al predecesor. **Doble corrección del 2026-09-20**: la fila decía **7** cuando las once originales ya tenían **6** dueños nombrables (L-R.3 aplicado a este propio archivo: el conteo se re-mide, no se copia), y las tres lecciones nuevas de la capa tibia **no suman dueño** — `D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, no en `TRIBUNAL-ENFORCEMENT-OBS`, que es donde la **reproducen** cuatro fases seguidas. Lo detectó `validate_lesson_capitalization.py` con su checks `C7` (atribución contra el índice), no una lectura humana: es el verificador de forma de este mismo plan funcionando sobre su propio `00-`.

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-A6, L-V4, L-H4 | Son la familia «la cita de línea cadura». Este plan no introduce citas de línea en ACs ni prompts y **no reescribe** las ajenas: `validate_plan_citations.py` ya las gobierna con alcance hacia delante + delta, y su política está recogida como restricción en `04-contrato-ejecucion.md`, no como trabajo nuevo |
| DA-HF3 | Misma política de alcance (hacia delante + delta, reporta sin reescribir). Ya está implementada en el verificador de citas; este plan la **hereda** como diseño de AC16, no la reconstruye |
| L-SR3, L-SR5 | Fuente única de verdad del estado de un servicio y gate bloqueante que no solo loggea: son del dominio de producto (promesas/métricas del pipeline v4). Ninguna fase de este plan toca el pipeline ni sus gates |
| L-VUP-1 | La baseline «13 rojos» que midió 14 por un test orden-dependiente del audit: este plan no ejecuta el audit ni hereda esa selección de tests |
| **D5** (no es ID: medición propia) | `grep -icE "verificador mec"` devolvió **0** sobre el índice, y sí existen verificadores nombrados en el corpus. Un cero de grep **no distingue** «no existe» de «busqué la palabra equivocada» — es la variante léxica de L-PF6. Se descarta el grep como única puerta de pertinencia y se registra como la evidencia que justifica FASE-C (AC15 obliga a publicar la población y el término usado) |

## 4. Cobertura declarada de este documento

- **Qué sí deja evidencia**: **catorce** consultas re-ejecutables (Q9 al abrir FASE-A; Q10 al abrir FASE-B; Q11 tras commitear B; Q12 al abrir FASE-C; **Q13 al abrir FASE-D, que es la que re-mide el workflow, la población de la convención `Lee …` y el índice sobre un árbol extraído con `git archive`**) — al concebir (Q9 el 2026-09-21 al abrir FASE-A; **Q10
  el 2026-09-21 al abrir FASE-B**, que es la que comprueba que la herencia de B no se asumió; **Q11 el
  2026-09-22 tras commitear B**, que desglosa la brecha entre las dos poblaciones de AC6) — al concebir
  eran ocho consultas re-ejecutables con su resultado medido, **catorce** lecciones con ID, dueño y un
  «qué cambia» que nombra un AC concreto (once al concebir + L-V2.1, L-V2.2 y D-V2.1, que trajo la capa
  tibia el 2026-09-20), cinco descartes con motivo y una medición propia (D5) que refuta el atajo obvio.
  **Al cerrar FASE-B se añaden cinco lecciones nuevas propias (L-VCF-6 a L-VCF-10, definidas con su
  medición en `10-analisis-post-implementacion.md`), dos más que escribieron el commit de la fase y su
  barrido (**L-VCF-11**: el denominador refutado al commitear; **L-VCF-12**: el verificador que pisó la
  evidencia de FASE-A por tener su destino hardcodeado), y deudas con dueño y disparador nuevos —
  **S10** (la geometría del `import` del SDK cuando D7 se active), **S11** (la exclusión no declarada del
  denominador) y **S12** (el default de `--report` sobre un registro cerrado; con guarda publicada en el
  README para que FASE-C no la re-pise, **guarda sin efecto desde el 2026-09-23** — ver la fila
  siguiente).**
- **Qué NO verifica el check mecánico**: la **pertinencia**. `validate_lesson_capitalization.py` comprueba forma y trazabilidad (C1–C8: consultas corpus-wide, ≥3 descartes, AC nombrado que existe, dueño publicado por el índice, ≥2 fuentes) y **ninguno de sus checks puede saber si la lección que debía capitalizarse era otra**. Un `[OK]` suyo significa «la forma exigida está». Ese límite declarado es exactamente el hueco que abre este plan.
- [x] **FASE-D cerró el 2026-09-24 con `build_phase_briefing.py` y sus 5 packs** dentro del plan
  (`…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`). Estado medido: **COMPLETO 4 ·
  SECCION-NO-RESUELTA 1 · FUENTE-AUSENTE 0** sobre 34 fuentes declaradas y 23 secciones pedidas
  (23 resueltas). La carga total de las cinco fases **bajó**, y el delta queda **muy por debajo del
  tercio** que el plan esperaba porque **el workflow canónico sigue entrando en los dos lados**: los
  dos totales, la resta y su comprobación los imprimen `FASE-D/carga.json` y `FASE-D/carga-pre-post.md`
  y su lectura métrica vive en `09` §D. **Aquí no se transcribe ninguna de esas cifras y eso es parte
  del hallazgo**: este documento entra en el pack que ese comando mide, así que copiar la carga en él
  la vence en el mismo gesto (**L-VCF-19**).
  Herencia de C aceptada sin reabrirla: la parte mecánica del triaje se exhibe en el pack, y su
  tramo semántico sigue `NO-EJERCITADO`, con **D6 dormida** (contrato E4). No se re-negoció E1–E5.
- [x] **La convención que parsea el generador es minoritaria y eso se midió, no se supuso**: de
  **121** prompts bajo `.opencode/plans/Archives/`, **0** declaran su lectura con la cadena
  `Lee …`; los únicos **5** del repo son los de este plan. Un test contra corpus real por eso
  afirma hoy el **corte** (el pack sale `SIN-DECLARACION` y su check `SIN-FUENTES`, no `OK`) y la
  escritura de la convención en `prompt-fase-template.md` quedó como deuda **S16**, con dueño y
  disparador, porque tocar `.agents/` es AC17/D1 y no compete a esta fase.
- [x] **El plan se auto-trió al cerrar FASE-C (2026-09-24), y el resultado NO se aplicó a sí mismo.**
  `scripts/triage_lesson_relevance.py` corrió sobre este propio `00-` con el **proveedor falso
  determinista** de la selección (el informe publica `coste.emisor = {nombre: falso-pertinencia,
  falso: true, credencial_env: null}`). Conteos del auto-triaje, con su artefacto:
  **propuestas aceptadas para §2: 0 · rechazadas: 0 · pendientes de revisión humana: 5**
  (`informe.json` → `buckets.propuesto`; 16 candidatos más quedaron en `a-revisar-humano` por
  `confidence` debajo del umbral o por rechazo confidente del emisor), y **11 de las 14 filas ancladas
  fueron juzgadas `no-pertinente` por el emisor y ninguna se borró** (`ac10_delta.json` →
  `removed: []`, `filas_cuestionadas_sin_borrar`). **Este §2 sigue teniendo las mismas catorce filas
  que tenía al cerrar FASE-B**, y esa invariancia es AC10, no olvido. Por qué cero aplicadas: una
  propuesta de un falso prueba la mecánica del camino, no la pertinencia (contrato **E3**), y aplicarla
  habría escrito aquí una fila cuya evidencia es sintética — lo que AC15 declara `NO-EJERCITADO`. Si
  alguna se revisa, entra con dueño, «qué cambia» real y la revisión que la avala registrada con quién
  decidió; si se rechaza, **se publica el rechazo con su motivo y la fila no desaparece**.
- [x] **Las cinco propuestas del piloto quedan declaradas PENDIENTES con su dueño (2026-09-25, cierre de
  `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22`).** `L-VCF-10`, `L-VCF-11`, `L-VCF-12`, `L-VCF-13` y
  `L-VCF-14` son las cinco que publica `informe.json` → `revision_humana.propuestas_pendientes`
  (`n_pendientes: 5`, `registros: []`), definidas cada una con su medición en
  `10-analisis-post-implementacion.md`. **Dueño: el operador**, a través de la revisión humana que fija el
  contrato **E3** — no es una fase ni un script: `seccion_dos_editada_por_este_script: false` sigue siendo
  cierto después de esta sesión. **Ninguna se aceptó, se rechazó ni se copió a §2**, que conserva sus
  catorce filas (**AC10**). Lo que cada una necesita para entrar: un «qué cambia» real que nombre un AC de
  este plan, la revisión que la avala registrada con quién decidió, y una evidencia que no sea la de un
  emisor falso mientras **D7** esté inactiva — por eso se declaran pendientes en lugar de cerrarse.
- [x] **El hueco que este archivo declaraba fuera de alcance ya tiene instrumento**: la limitación del
  párrafo anterior («Qué NO verifica el check mecánico: la pertinencia») sigue siendo cierta de
  `validate_lesson_capitalization.py` — su `[OK]` jamás significó «capitalicé bien» —, pero desde el
  2026-09-24 existe la otra mitad: `triage_lesson_relevance.py` pregunta por pertinencia, publica su
  denominador con sus ceros y **propone sin filtrar**. Lo que **no** cierra: el juicio semántico real,
  que espera proveedor (deuda **D7**), y por eso **D6** sigue dormida.
- [x] Este archivo es verificado por `scripts/validate_lesson_capitalization.py` (`[7/7]` del hook versionado en `scripts/git_hooks/pre-commit`) y por `scripts/build_lesson_index.py --check` (`[6/7]` del mismo hook).
- [x] **Limitación del Paso 0 registrada y SUPERADA el 2026-09-20**: la capa tibia (QMind `iah-cli-lecciones`) **no se consultó** en la concepción porque el CLI no estaba disponible en esa sesión; se aplicó el fallback del executor (memoria de proyecto + índice generado) y quedó registrado aquí y en `dependencias-fases.md`. En la auditoría de la concepción del mismo 2026-09-20 el CLI **sí** estuvo disponible y autenticado: se ejecutó Q7 con cuatro consultas y sus resultados se capitalizaron arriba (L-V2.1, L-V2.2, D-V2.1). **El comando con el nombre de notebook no es re-ejecutable**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; el identificador válido es `01a04d98-b7bd-778c-8441-26fdc7e35f45`. Queda como verificación de **D8** re-corrida antes de RELEASE por si el corpus cambió. ⟦**Re-fechada el 2026-09-25, al cerrar FASE-RELEASE**: la re-corrida **no** se hizo. D8 es operación de red y el mandato del cierre la dejó explícitamente fuera (checkpoint C1, `PENDIENTE-AUTORIZACION`). Lo que se declara es que **la premisa «el corpus del notebook cambió desde el 2026-09-20» quedó no comprobada**, que no es lo mismo que «no cambió», y que la capitalización de §2 sigue apoyada en la consulta de aquella auditoría. La limitación del comando con nombre sigue vigente: no es re-ejecutable tal cual⟧.
- [x] **Actualizado al cierre de FASE-A (2026-09-21)** con el balance de §5, la consulta Q9 re-ejecutable y las cinco lecciones nuevas de esa fase.
- [x] **Actualizado al cierre de FASE-B (2026-09-21)** con el balance de §6, la consulta Q10 re-ejecutable, las cinco lecciones nuevas de B (L-VCF-6 a L-VCF-10) y la deuda **S10**. Ocho de las diez lecciones filtradas por su prompt se ejercitaron y las dos restantes quedaron asignadas y declaradas (L-V2.1 y L-V2.2: la primera se volvió a caer, la segunda es de FASE-C). Sigue **sin** cerrarse el plan: faltan C, D y RELEASE, y el write-back de QMind se ejecuta **antes** del `git mv` a `Archives/` en esa última sesión (orden R2.5 / R2.10, con la interfaz del writer re-leída por D10).
- [x] **Actualizado el 2026-09-22, al commitear FASE-B** (`647f436`): la consulta **Q11** re-ejecutable,
  la lección **L-VCF-11** y la deuda **S11**, las tres nacidas del propio commit — que refutó una cifra
  que la fase acababa de publicar (678 → **691** `.py` rastreados) y dejó ver, al desglosar la
  brecha con el escáner, una exclusión no declarada en el denominador. Es A6 golpeando otra vez, ahora
  sobre el instrumento de la fase: **un cero medido sobre una población que nadie definió del todo**.
- [x] **Conciliada el 2026-09-23 (solo lectura, sin nueva instrumentación).** Las dos lecciones que
  escribió el commit de B — **L-VCF-11** y **L-VCF-12** — tenían su deuda asociada (**S11**, **S12**)
  corregida en código **por otro trabajo**: el bloque A de
  `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, commit **`fdd397f`**, que declaró explícitamente que lo
  suyo era *corrección técnica, no cierre contractual* porque la enmienda correspondía a este plan. **Esa
  enmienda es la que se registra ahora** en `dependencias-fases.md` §Conciliación, con las tres capas
  separadas: cierre original (`647f436`) / corrección (`fdd397f`, ajena) / aceptación (2026-09-23). Las
  lecciones **no caducan**: L-VCF-11 sigue siendo la regla de desglosar una brecha entre dos poblaciones
  archivo por archivo (hoy verificada por medición: 696 escaneados vs 691 rastreados → residuo 0) y
  L-VCF-12 sigue siendo la regla de mirar el default de escritura de un verificador antes de correrlo.
  Lo que sí se retira es su aplicación concreta: la guarda del README sobre `--report` sin destino, que
  S12 dejó sin objeto. Y **ninguna de las dos correcciones toca el rojo contractual**: A1–A4 siguen
  vencidas en `.agents/` (`exit 1` re-medido) porque ese es **D1**, con instrucción literal del operador.
  ⟦**Vencido ese cierre el 2026-09-25, con atribución**: el `exit 1` de A1–A4 describía el árbol antes de
  que el **bloque B** de la orden recibiera su autorización para editar `.agents/`. Re-medido en el cierre de
  FASE-RELEASE con el mismo instrumento y su modo de solo lectura
  (`validate_governance_numbers.py --report`, sin destino): **`status: SIN-HALLAZGOS`, `exit 0`**. El veredicto
  de **D1** no lo da esta línea ni ese número: lo da la **matriz §13** de la fuente única de B, donde aparece
  **CERRADA en su alcance**. Lo que la lección conserva intacta es su regla de procedimiento: **leer** el
  verificador no es **reparar** `.agents/`, y eso fue lo único que hizo este cierre⟧.
- [x] **Actualizado al cierre de FASE-RELEASE (2026-09-25, parte offline).** El plan cerró sus cinco fases:
  release **4.78.0** en la fuente única, cinco cabeceras por su writer, `DOMAIN_PRIMER.md` regenerado con el
  suyo, `[4.78.0]` en `CHANGELOG.md` y registro en `REGISTRY.md` por su **único** escritor. Sobre este
  archivo, lo que el cierre **no** tocó y lo que sí: **no** se aceptó ni se rechazó ninguna de las cinco
  propuestas de revisión humana (L-VCF-10…14 siguen `pendientes`, §2 conserva sus catorce filas — AC10 y
  contrato **E3**), y **no** se capitalizó por cuota. Lo que se re-fechó es la limitación de Q7/D8 (arriba)
  y la lectura de D1. El cierre deja dos defectos de instrumento declarados y sin cura en esta fase: los
  writers de texto que reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y la regla
  `readme_version_header`, que no goberna la fecha legible del `README.md`.
  ⟦**Ese «sin cura en esta fase» se cumplió y luego venció el mismo 2026-09-25**: el cierre no los curó
  (no tenía mandato de código) y quedaron registrados como **S17** y **S18**; una sesión posterior, con
  mandato de código del operador, los curo — tres escrituras con `newline="\n"` (la de `run_status`
  apareció al curar) y la regla de la fecha legible goberna y escribe por su escritor. Estado vigente:
  §S17/§S18 de `dependencias-fases.md`; prueba en
  `tests/test_sync_writers_lf_y_fecha_readme.py`. Ninguna de las dos fue una lección nueva de este
  archivo: no se capitalizó por cuota. Las reglas generales que las produjeron ya estaban escritas —
  mirar el default de escritura de un verificador antes de correrlo (**L-VCF-12**) y arreglar un dato
  en su escritor, no con un tercero que lo reescriba a mano⟧.

## 5. Balance de FASE-A (2026-09-21): qué se aplicó de verdad, lección por lección

Diez lecciones de §2 estaban filtradas como pertinentes a FASE-A en su prompt. Contrastadas una a una
contra lo que la fase produjo (ninguna quedó «citada sin aplicar», y ninguna se borró):

| ID | Estado al cerrar A | Evidencia o motivo |
|---|---|---|
| L-R.1 | **aplicada** | La regla vivía solo en el workflow; ahora vive en `scripts/validate_governance_numbers.py` con su prueba sobre el árbol real |
| L-NC10 | **aplicada** | Población descubierta por escaneo (24 instancias), no hardcodeada en las cuatro medidas |
| L-R.3 | **aplicada** | `coverage_basis` obligatoria; el favorable sin denominador está cortado por guard |
| L-PF6 | **aplicada** | Cuatro caminos de `LECTOR-FALLIDO` con motivo propio; ninguno devuelve «sin hallazgos» |
| L-PF10 | **aplicada** | Tres archivos de estado, uno por estado; documento no vacío con 0 instancias = fallo de lectura |
| L-T4A.5 | **aplicada, y descubrió un defecto propio** | El primer mutation check apagaba el guard de A1 y nombraba a A4: anclar en un id posicional no prueba nada → `assertion_key` invariante (L-VCF-1) |
| L-VUP-5 | **aplicada** | El verde de la primera corrida se declaró sospechoso **y lo era**: la regla de población se rectificó dos veces antes de reproducir A1–A4 |
| L-D3 | **aplicada** | Conteos como delta con resta comprobada; la métrica que sí se movió (+23 tests) publicada aparte |
| L-V2.3 | **aplicada con costo propio** | El barrido de `tests/` mostró que la fase añadió pins del 11 (L-VCF-5), declarados con dueño |
| L-HF1 | **aplicada** | Familias no cubiertas medidas y publicadas; exclusión histórica con su conteo y su frase de amparo |

De las tres lecciones del §2 que el prompt de FASE-A no filtraba: **L-V2.1 sí se ejercitó** (es la que
gobierna el anclaje del mutante, y fue la que cayó — L-VCF-1); **D-V2.1 se reprodujo** (el instrumento de
presupuesto no corre: `find . -name "*.jsonl"` = 0 en el workspace, métrica retirada y unidad contable
declarada en `evidence/…/FASE-A/ac17-y-presupuesto.md`); **L-V2.2** corresponde a FASE-C y sigue
pendiente de ejercitarse.

Cinco lecciones nuevas salen de esta fase (**L-VCF-1** a **L-VCF-5**), definidas con su medición en
`10-analisis-post-implementacion.md`; dos afectan a las fases que siguen: el disparador de D1 era
circular (L-VCF-4, ya re-escrito en `dependencias-fases.md`) y **la salida de un verificador también es
contrato** (L-VCF-3), cosa que FASE-B, C y D pueden repetir si imprimen estados con acentos.


---


## 6. Balance de FASE-B (2026-09-21): qué se aplicó de verdad, lección por lección

Siete lecciones de §2 venían filtradas por el prompt de FASE-B, más la herencia explícita de A. Ninguna
se citó «de adorno»: cada fila dice contra qué artefacto se confrontó.

| ID | Estado al cerrar B | Evidencia o motivo |
|---|---|---|
| L-PF6 | **aplicada, y con costo propio** | La prohibición del default es el eje del módulo (5 `motivo_clase` sin colapsar + mutante del proveedor por defecto). Costo: la primera regla de aislamiento leía «todo `import_module`» como contrabando y producía **16 hallazgos ajenos** → L-VCF-7 |
| L-PF10 | **aplicada** | `respuesta-vacia:list` con causa propia; `usage=None` ≠ consumo cero; `noul.confidence = None` **con** `confidence_motivo`, nunca `0.0` |
| L-R.3 | **aplicada** | El `0` de AC6 con dos poblaciones (678 / 692), 4.379 nodos vistos, 21 menciones aparte y exclusiones con su conteo; el `1` de AC9 medido por sha256 |
| L-R.4 | **aplicada** | La comparación de proveedores declarada fuera de alcance con su porqué (D7), y S10 registrada con dueño y disparador en vez de decideda en silencio |
| L-D3 | **aplicada** | Todo conteo gobernado como delta con resta (quick 0, completo 0, hook 0, `.agents/` 0/0, AC6 0); los +48 de tests publicados aparte |
| L-V2.3 | **aplicada** | Contract test de forma sin literales del proveedor; pin declarado y probado no-usado por AST; **0** pins nuevos del 11 o del 7 añadidos por B |
| L-VUP-5 | **aplicada y confirmada** | La primera corrida dio **30 fallos** y el primer mutante de forma no aislaba ningún guard (L-VCF-6). El rojo de AC8 (`exit 1`) quedó capturado en `contract.txt` |
| L-T4A.5 / L-V2.1 | **aplicadas** | Nueve mutantes sobre símbolos reales, cada uno con verde y rojo, y un test que exige que dos mutantes no compartan símbolo. L-V2.1 volvió a caer: la unidad de mutación de una **lista** de guards es su entrada, no la lista (L-VCF-6) |
| L-HF1 | **aplicada** | Cuatro límites del escáner medidos y publicados (cargas no resueltas 14, dependencias declaradas no miradas, menciones aparte, exclusiones con conteo); `.agents/` intacto y verificado |
| L-V2.2 | **no ejercitada todavía** | Es de FASE-C (el suelo determinista del índice). Queda pendiente de ejercitarse allí, no se borra |

De las dos lecciones del §2 que el prompt de FASE-B no filtraba: **L-V2.1 sí volvió a caer** (es la que
rige el anclaje del mutante, y el primer mutante de forma no aislaba nada → L-VCF-6) y **D-V2.1 se
reprodujo otra vez** (`find . -name "*.jsonl"` = 0: el instrumento de presupuesto sigue sin correr,
métrica retirada y unidad contable declarada en `evidence/…/FASE-B/baseline-pre-post.md`).


---


## 7. Balance de FASE-D (2026-09-24): qué se aplicó de verdad, lección por lección

Ocho lecciones venían filtradas por el prompt de la fase. Ninguna se citó de adorno: cada fila dice
contra qué artefacto se confrontó, y la que no se ejercitó queda escrita como tal.

| ID | Estado al cerrar D | Evidencia o motivo |
|---|---|---|
| L-D3 | **aplicada** | Delta con par `stat -c %s` y resta entre cargas totales; cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py` (`exit 0`) y un test que obliga a publicar un delta **negativo** |
| L-PF10 | **aplicada, y amplió el contrato** | Al trío de AC22 se sumó `SIN-DECLARACION` y el check imprime `SIN-FUENTES` en lugar de `OK`; sin esa cuarta salida, los 121 prompts archivados habrían dado 121 verdes vacíos |
| L-PF6 | **aplicada** | `exit 2` con tres rutas intentadas para un plan inexistente; fuente ausente = pack **no emitido**; meta sin sha = `FUENTE-ILEGIBLE`, causa distinta de `AUSENTE` y de `SHA-DISTINTO` |
| L-NC10 | **aplicada** | Cero configuración a mano: `parsear_lista_lectura(prompt)` se confronta contra las fuentes del pack emitido, fase por fase |
| L-V2.3 | **aplicada con costo propio** | AC21 se prueba escribiendo la fuente **en disco**; y el anclaje de AC23 hubo que re-hacerlo: «rutas intentadas» y «sección pedida» ya vivían en los documentos copiados (ver L-VCF-16) |
| L-R.3 | **aplicada** | `coverage_basis` con 5 packs por estado, 34 fuentes, 23 secciones pedidas/resueltas, cinco familias no cubiertas y el denominador de la convención (0 de 121) |
| L-HF1 | **aplicada y produjo una regla nueva** | `no_incluye[]` no vacío por test; y lo que vive fuera de `.opencode/` se declara lectura aparte: copiarlo dentro reabrió `[8/11] validate_opencode_refs.py` (medido: 2 referencias rotas por el pack, `docs/CONTRIBUTING.md`) |
| L-T4A.5 | **aplicada** | Verde y rojo del guard real en `FASE-D/mutation/`, con test de que el mutante no cambia el estado, solo la declaración. El par de tamaños **no** se copia en esta fila: vive en `mutation/resumen.txt` y este documento está dentro del pack medido (**L-VCF-19**) |

De las lecciones del §2 que el prompt **no** filtraba: **L-V2.1 volvió a caer** (el primer anclaje
del mutante miraba una frase que existía en el corpus copiado: un rojo que no observaba la rama que
decía observar → **L-VCF-16**) y **D-V2.1 se reprodujo por octava vez** (`find . -name "*.jsonl"` =
0 dentro del workspace: el instrumento de presupuesto sigue fuera de servicio; el corte de esta fase
fue «hasta listo para revisión»). **Y en D el auto-reporte tampoco se publicó**: la sesión pasó por una
compactación de contexto a mitad de fase, la cuenta de `tool_use` propios ya no era reconstruible, y
publicar un número de memoria habría sido el defecto que **L-VCF-18** capitaliza en esta misma fase. La
métrica se retiró y se sustituyó por **unidad contable en disco** con su comando —rutas propias,
líneas de instrumento y de selección, archivos de evidencia y corridas listadas—, declarada
**no comparable** con las corridas que sí usaron el instrumento. Los números están en
`baseline-pre-post.md` §4 y **no se re-transcriben aquí**: esta fila es fuente de uno de los packs que
la fase mide, y copiar un conteo de la propia evidencia lo vuelve a mover (**L-VCF-19**).)

Dos cosas que D **no** hizo y se declaran: no rebanó el workflow (deuda **D3**, dueño «plan propio,
posterior»), y no aceptó candidatos de pertinencia ni tocó el §2 del `00-` — heredó de C su parte
mecánica medida y su `NO-EJERCITADO`, y **D6 sigue dormida** con su causa escrita
(`dependencias-fases.md` §Deuda).

**Y una cosa que D midió sobre su propio cierre**: la primera corrida de la regresión
`tests/quality_gates` salió **roja (14 failed, 26 errors, `SueloNoLeible: VENCIDO`)** por el índice
vencido **por los packs y los `.md` de cierre que la propia fase escribió** (**L-VCF-17**, y en la
selección de C, no en la de D), y la tercera volvió a salir roja porque **esta sesión editó corpus
mientras corría la selección**. Las dos se conservan con su cifra y su atribución en
`evidence/…/FASE-D/regression_calidad.txt`, que también guarda la **cuarta** corrida —la de referencia
del cierre, verde, sobre el árbol ya asentado, con el par de índice regenerado después del último `.md`
y su `--check` en verde—. Su recuento **no se copia a este `.md`**: sería la quinta vez que una cifra
transcrita al corpus queda vencida por el propio acto de transcribirla (**L-VCF-19**).


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0` · 53192 bytes copiados de 53192 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `06-checklist-implementacion.md` (documento completo)

# Checklist de implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Leyenda de estados** (R2.4, no negociable): `PENDIENTE` · `VERIFICADO OFFLINE` (test verde **con
su mutation check**) · `⚠️ PARCIAL` (falta el rojo, falta la clave en el artefacto, o solo cubre un
estado) · `NO-EJERCITADO` (el camino no se ejercitó; con el motivo) · `FUERA DE ALCANCE`.
**No existe `SUPERADO EN E2E` en este plan**: no hay corrida (§5 del maestro) y no hay FASE-VERIFY.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está autorizado;
el bloque C y el piloto FASE-C no lo están. ⟦**Vencido en parte el 2026-09-24 y rectificado el
2026-09-24 al medirlo**: de esta frase queda en pie solo la segunda mitad — **el piloto FASE-C sí sigue sin
autorización**. El **bloque C** de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` **sí está autorizado y
ejecutado desde el 2026-09-24**, y lo que ejecutaron fueron **enmiendas documentales sobre los cuatro
planes**; su matriz y su veredicto viven en el único resumen de C,
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`.
**Y eso no es FASE-C**, en los dos sentidos que este plan distingue: las enmiendas no ejecutaron ninguna
fase de los cuatro planes, y lo único que separa el estado actual del cierre de la orden sigue siendo el
piloto. **Causa**: dos afirmaciones contradictorias vivas en este mismo archivo —más abajo ya se declaraba
el bloque C ejecutado y «eso no es FASE-C»—, sin que la cabecera se llevara detrás de esa corrección y sin
anotación alguna en torno a la frase falsa. **Autoría no atribuible por evidencia**: la frase no está en
`HEAD` y no la registra ni el expediente de B ni el de C, que comparten este mismo árbol sin commitear; no
se le inventa dueño.⟧ Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Las filas cerradas de FASE-A/B conservan su evidencia histórica, no certifican el árbol de B actual.

## Matriz de ACs

| AC | Fase | Enunciado corto | Artefacto donde se lee | Estado |
|---|---|---|---|---|
| AC1 | A | reproduce **las cuatro aserciones normativas vivas** A1–A4 y ninguna otra, con la regla de población de A8 aplicada | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]` (con `occurrences[]`) | **VERIFICADO OFFLINE** 2026-09-21 |
| AC2 | A | publica denominador: población, **las tres clases y las cuatro familias no cubiertas** | ídem → `coverage_basis`, `historical_excluded[]`, `excluded[]` | **VERIFICADO OFFLINE** 2026-09-21 |
| AC3 | A | tres estados sin colapsar | ídem → `status` + 3 archivos de test (un estado cada uno) | **VERIFICADO OFFLINE** 2026-09-21 |
| AC4 | A | mutation check **por aserción** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` (verde + 6 rojos anclados por `assertion_key`) | **VERIFICADO OFFLINE** 2026-09-21 |
| AC5 | A | conteo del quick y del hook como delta 0 | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md` | **VERIFICADO OFFLINE** 2026-09-21 (quick 0, hook 0; tests +23 declarado) |
| AC6 | B | aislamiento de imports | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` (conteo + población) | **VERIFICADO OFFLINE** 2026-09-21 (0 imports fuera de la puerta sobre **692** `.py` del árbol de trabajo / 678 rastreados por git; mutante `M-AC6-token` y `M-AC6-carga-dinamica` en `mutation/`) |
| AC7 | B | proveedor no configurado no decide | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` → `provider_status` | **VERIFICADO OFFLINE** 2026-09-21 (los tres estados provocados cada uno por su causa, 5 `motivo_clase` distintos sin colapsar; mutante `M-AC7-proveedor-por-defecto` muestra que un default sí fabricaría decisión) |
| AC8 | B | contract test de forma con proveedor falso | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` | **VERIFICADO OFFLINE** 2026-09-21 (verde exit 0 y **rojo exit 1 del mismo test** contra una copia del proveedor falso sin `confidence`; pin del modelo declarado y probado por AST como no-used) |
| AC9 | B | **extensión LOCAL**: añadir un 2º proveedor **falso** cuesta **un** archivo — no el coste de integrar un SDK real ⟦precisión declarada 2026-09-23⟧ | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` → `files_changed_to_add_provider` | **VERIFICADO OFFLINE** 2026-09-21 (valor **1**, `agregados=[falsos_proveedores/falso_segundo.py]`, `modificados=[]`; los dos proveedores se despachan por la misma puerta y contestan distinto. tests paralelos = 1, declarados aparte) · **re-medido 2026-09-23: `files_changed_to_add_provider = 1`, `exit 0`**, y el propio informe imprime `alcance_de_ac9` diciendo que **no** cubre dependencias ni autenticación de un SDK real (eso es S10/D7) |
| AC10 | C | el triaje **no elimina** fila anclada alguna **y tampoco escribe §2 por su cuenta** ⟦E3⟧ | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` → `removed: []` | **VERIFICADO OFFLINE 2026-09-24** (`anchored_before` = `anchored_after` = 14 filas del §2 real de este plan, `removed: []`, y **11 filas ancladas juzgadas `no-pertinente` por el emisor que NO desaparecieron**: el guard tuvo trabajo real. El script no escribe §2: `ESCRIBE_SECCION_DOS = False`, sha256 del `00-` idéntico antes y después de la corrida completa, y **cero operaciones de escritura observadas** dentro del directorio del plan) |
| AC11 | C | índice **ausente / vencido / lector-caído** ≠ sin candidatos; **frescura comprobada por el propio C** ⟦ruta (b) cerrada 2026-09-23, E2⟧ | ídem → `index_status` | **VERIFICADO OFFLINE 2026-09-24** — tres causas con su test propio y su `exit` propio (2 `AUSENTE` con ruta + comando, 4 `VENCIDO` producido por **el check de C**, que calcula el índice en memoria con el generador de la casa y lo compara con el disco nombrando **qué IDs** lo vencieron, 3 `LECTOR-FALLIDO` con cuatro sub-causas: ilegible, no-JSON, **forma equivocada**, y **cálculo propio caído**). Ninguna devuelve «sin candidatos»: `candidatos: null` con su nota. Coste publicado: **dos lecturas del JSON por corrida** |
| AC12 | C | umbral con valor, base y acción por debajo, **sobre `confidence` de un `choice` de dos opciones** ⟦E1⟧ | ídem → `threshold` | **VERIFICADO OFFLINE 2026-09-24** (`umbral.campo = confidence`, `value = 0.80`, `basis` nombra el campo y niega `probabilidad_si`, `action_below` = «va a `a-revisar-humano`, no se descarta»). Prueba de que gobierna `confidence` y no la probabilidad: con un emisor de **dos ejes independientes** existen a la vez un candidato con `por_si` 0.90 y `confidence` 0.41 (cae en `a-revisar-humano`) y candidatos con el **mismo** `por_si` en buckets distintos. Conservación: ningún candidato se pierde |
| AC13 | C | ≥1 test contra corpus real, skip declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` | **VERIFICADO OFFLINE 2026-09-24 — el test CORRIÓ, cero saltos** (`-v -rs`: 4 casos sobre los **2** planes archivados que tienen `00-`, de 27). **Desviación registrada**: el prompt decía `Archives/` y el `archives/` de raíz no contiene planes; el corpus efectivo es `.opencode/plans/Archives/` (skipif sobre el corpus real, no sobre la ruta del prompt — un skip sobre ruta inexistente sería verde vacío, L-HF1) |
| AC14 | C | mutation check del guard de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` | **VERIFICADO OFFLINE 2026-09-24** — símbolo real `triage_lesson_relevance.GUARD_ADITIVIDAD_ACTIVO`, leido por `guardar_filas_ancladas()` en el momento del filtrado. **VERDE**: 14→14, `removed: []`. **ROJO**: 14→**3**, `removed` = los 11 IDs cuestionados, y el rojo **nombra** al guard mutado (L-V2.1). Disciplina S13: destino por argumento obligatorio (probado por `inspect.signature`), ancla positiva con el **observador de escrituras compartido** y `huellas` (sha256+mtime+tamaño) del expediente de FASE-A intactas; su `resumen.txt` publica el **alcance declarado** del observador |
| AC15 | C | denominador, términos, ceros **y aceptabilidad** (dispara D6); con proveedor falso el tramo semántico es **`NO-EJERCITADO`, sin simular** ⟦E4⟧ | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` | **⚠️ PARCIAL por diseño del plan, no por ejecucion**: la parte no semantica esta **VERIFICADO OFFLINE** (poblacion leida del JSON en la propia corrida, no pineada —hay test que lo prohíbe—; `35 de 334` IDs juzgados; 10 terminos de la capa fria **con sus 5 ceros**, incluido `verificador mec = 0` que reproduce A5; familias del índice juzgadas `D, DA, L` y **`S` no juzgada**; IDs numéricos = 0 con su método; y el pool **no** sometido a juicio declarado). El tramo semantico: `acceptance = NO-EJERCITADO`, `valor: null`, con el motivo literal y **sin ratio simulada** (hay test que la busca y la niega). **D6 queda dormida** en `dependencias-fases.md` |
| AC16 | A,B,C,D | quick en 11 y hook en 7, inalterados en todo el plan | los cuatro `baseline-pre-post.md` | **A: delta 0** y **B: delta 0 verificados 2026-09-21** (quick 11→11, hook 7→7, `git diff` vacío en los cuatro scripts gobernados; +48 funciones de test declaradas aparte) · **C: delta 0 medido el 2026-09-24** (par `faseC_baseline_pre/post` y `faseC_quick_pre/post`, resta comprobada en `evidence/…/FASE-C/baseline-pre-post.md`; la composición del quick y del hook **no** se tocó, y los valores los imprime la corrida, no esta fila) · **D: delta 0 medido el 2026-09-24** (par `faseD_baseline_pre/post` y `faseD_quick_pre/post` con la resta comprobada en `evidence/…/FASE-D/baseline-pre-post.md` §1 y §5; quick **11/11 con `exit 0`** y hook **7** sobre el árbol final, `git diff` vacío en los cuatro scripts gobernados; HEAD sin cambio entre PRE y POST porque la fase no commiteó, y los 49 casos nuevos se declaran aparte, no como delta del quick) |
| AC17 | A,B,C,D | `.agents/` intocado; familias no cubiertas declaradas | `evidence/…/FASE-A/informe.json` → `families_not_covered[]` + `ac17-y-presupuesto.md` + `git status --porcelain .agents/` (vacio) | **A: VERIFICADO OFFLINE 2026-09-21** · **B: VERIFICADO OFFLINE 2026-09-21** (`git status --porcelain .agents/` vacío; 98.694 / 6.123 bytes idénticos en PRE y POST) · C: VERIFICADO OFFLINE 2026-09-24 (`git status --porcelain .agents/` vacío al cerrar; C no renumeró nada, no importó el SDK y declaró en su propio `coverage.json` las familias que **no** juzgó: `S`, los IDs numéricos y el pool del índice que su corte no miró) · **D: delta 0 medido el 2026-09-24** (par `faseD_baseline_pre/post` y `faseD_quick_pre/post`; quick 11/11 con `exit 0`, hook 7→7, composición del quick y del hook intactos, y los 49 casos nuevos de la fase publicados aparte en `baseline-pre-post.md`) |
| AC18 | A,B,C,D | capitalización, citas e índice verdes sobre el mismo árbol final verificado; commit opcional, posterior y autorizado, no condición de los cinco cortes | salida de los tres verificadores | **A: los tres verdes el 2026-09-21** (`[9/11]`, `[10/11]` en el quick 11/11 + indice regenerado) · cumplido en el mismo commit `a7564ae` · **B: quick 11/11 verde con el índice regenerado en el cierre de la fase**, y el par viajó **dentro** del commit `647f436` (2026-09-22) con los **7** checks del pre-commit en verde · **C: los tres verificadores verdes sobre el MISMO árbol final verificado el 2026-09-24** — `run_all_validations_quick_post.txt` (11/11 con `exit 0`, con `[9/11]` de citas y `[10/11]` de capitalización en `[OK]`), `build_lesson_index.py --check` en fresco tras regenerar el par sobre ese árbol, y `validate_lesson_capitalization.py` verde sobre el `00-` con sus **14** filas de §2 intactas (cero candidatos aceptados ⇒ cero escrituras: el caso «aplicar solo los aceptados» **no** se ejercitó en esta sesión y se declara). **Commit hecho el 2026-09-24** en `7f2e9f9` + `5817edd` (37 rutas propias, 7/7 del hook) **solo con lo propio de FASE-C**: el par generado y las fuentes del cierre viajan mezcladas con el trabajo ajeno declarado en `FASE-C/cero-red.txt` y quedan fuera del commit por decisión del operador. El push quedó hecho el mismo 2026-09-24 por instrucción literal (`da382b1..5817edd`, paridad **0/0** re-verificada tras `git fetch`), y ni el commit ni el push son condición de los cinco cortes — su verde se midió antes, sobre el árbol de trabajo · **D: los tres verificadores verdes sobre el MISMO árbol final verificado el 2026-09-24** — ver `evidence/…/FASE-D/baseline-pre-post.md` y `criterios-de-completitud.md`. Nota medida y no resuelta por D: los packs son `.md` **dentro del corpus del índice**, así que el acto de generarlos vuelve a vencer el par (medición A6 del maestro golpeando a un artefacto derivado); la cura es el paso 5 del contrato (regenerar sobre el árbol final), no editar el generado |
| AC19 | D | un pack por fase, declarando qué **no** incluye; **y resuelve un plan también bajo `Archives/`** ⟦bloque C 2026-09-24⟧ | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` | **VERIFICADO OFFLINE 2026-09-24** — 5 packs = las 5 fases del plan (A, B, C, D, RELEASE) dentro de `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`; `no_incluye[]` y `lectura_aparte_obligatoria[]` no vacíos exigidos por test fase por fase, con el workflow canónico a la cabeza (108.017 bytes) y **cero bytes aportados a `.agents/`** (observador de escrituras + sha256/size de los 4 archivos, iguales antes y después). Resolución bajo `Archives/` demostrada sobre archivados reales por nombre y por ruta vigente, que es la llamada del RELEASE tras el `git mv` |
| AC20 | D | delta de **carga total** con el mismo comando en ambos lados y los **tres sumandos** por fase ⟦bloque C 2026-09-24⟧ | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method`, `por_fase[].resta_comprobada` + par `faseD_carga_pre/post.txt` | **VERIFICADO OFFLINE 2026-09-24** — `stat -c %s` en los dos lados, divisor 4 declarado, `resta_comprobada: true` en las cinco fases y las cinco identidades del instrumento en verde. **El delta total no se transcribe en esta fila: este checklist es fuente de uno de los packs que ese comando mide, así que copiar la cifra la vence (**L-VCF-19**); la imprimen `carga.json` → `total` y `carga-pre-post.md`.** Lo que sí es estable y es el hallazgo: el ahorro queda **muy por debajo de un tercio**, porque el workflow canónico entra en los dos lados mientras D3 no lo rebane. Cada resta cierra con `omitido − andamiaje − coste` y `instrumentos/comprobar_resta_carga.py` comprueba cinco identidades con `exit 0`. Un test planta una fuente diminuta y exige publicar el delta **negativo** con la misma identidad |
| AC21 | D | proveniencia con HEAD, fecha y sha por fuente; **la frescura la gobierna el sha de `sources[]` y HEAD es procedencia, no llave de caducidad** ⟦bloque C 2026-09-24⟧ | ídem → `provenance`, `verificacion_check[]` | **VERIFICADO OFFLINE 2026-09-24** — probado **editando la fuente en disco y re-midiendo en disco** (no el objeto en memoria): revertida, vuelve a `exit 0`. Cuatro causas sin colapsar: `FUENTE-AUSENTE`, `SHA-DISTINTO` (imprime los dos sha), `FUENTE-ILEGIBLE` (meta sin sha) y `PACK-AUSENTE`. HEAD avanzado con fuentes idénticas **no** vence: se publica `procedencia_distinta` y el check pasa; el pack no figura en su propio `sources[]` (test) |
| AC22 | D | prohibido emitir un pack más corto en silencio | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}`, `packs_por_estado` | **VERIFICADO OFFLINE 2026-09-24** — un test por estado más uno que exige que los tres **no colapsen**. Medido sobre el plan: COMPLETO 4, SECCION-NO-RESUELTA 1, FUENTE-AUSENTE 0. El recorte nombra la sección pedida, las rutas intentadas y los títulos disponibles del documento, y conserva lo que sí se resolvió. **Ampliación medida**: hubo que añadir una cuarta salida, `SIN-DECLARACION` (pack emitido con cero fuentes gobernadas), porque 121 prompts archivados no declaran lectura y llamarlos COMPLETO era el verde vacío; su `--check` imprime `SIN-FUENTES`, con test que prohíbe el `OK` |
| AC23 | D | mutation check del guard de truncamiento | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` | **VERIFICADO OFFLINE 2026-09-24** — símbolo real `build_phase_briefing.GUARD_NO_TRUNCAMIENTO_ACTIVO`, leído por `_declarar_recorte()` al escribir el pack. **VERDE** `declara_recorte=True`; **ROJO** `declara_recorte=False` con el pack **más corto y el estado intacto** — se achica en silencio, que es justo lo que AC22 prohíbe. Los dos tamaños y su diferencia están en `mutation/resumen.txt` y **no** se copian a esta fila (**L-VCF-19**: el documento donde se copiarían está dentro del pack que se muta). Hay test de que el mutante no toque otra rama (L-V2.1). Destino por argumento obligatorio, ancla positiva con el observador de escrituras compartido y `huellas` del expediente de FASE-A intactas (S13); `instrumentos/correr_mutation_a_evidencia.py` publica el comando literal |

## FASE-A — `validate_governance_numbers.py` — **cerrada VERIFICADO OFFLINE el 2026-09-21** (AC1–AC5; y AC16/AC17/AC18 en la parte que corresponde a esta fase)

- [x] Script standalone, invocable sin tocar `run_all_validations.py`. **Verificado offline el 2026-09-21**: `--report`, `--json` y rutas inyectables (`--governance-doc`/`--source`/`--hook`) para probarlo sobre fixtures en `tmp_path`.
- [x] A1–A4 reproducidas y **cero hallazgos adicionales**: A1 `check 8` vs `9/11`, A2 `9/9` vs `10/11`, A3 `12/12` vs `15/15`, A4 `10/10` vs `10/11`; ademas 11 aserciones vigentes-correctas publicadas en `assertions_checked`.
- [x] **Regla de población aplicada y publicada (A8)**: viva-hallazgo **5 instancias en 4 aserciones** / vigente-correcta **11** / histórica congelada **8** / no resuelta **0** = **24** instancias (22 con corchete + 2 formas «check N»). Dos rutas de congelacion publicadas con su marca: `H1` (denominador de otra epoca dentro de `## Versiones`) y `H2` (clausula que narra un evento pasado). La frase del workflow que ampara la exclusion (`v2.24.0`) se copia en `historical_excluded[].authorized_by` y en `regla_de_poblacion.historical_authorizing_phrase`.
- [x] **Un hallazgo por aserción, con sus `occurrences[]`**: A1 sigue siendo **un** hallazgo con **dos** occurrences (el parrafo «Verificador mecanico» de R2.2 y la entrada v2.19.0 de `## Versiones`); demostrado tambien al inverso — un fixture con la frase escrita tres veces da 1 hallazgo con 3 occurrences.
- [x] `coverage_basis` con población, exenciones y `families_not_covered` — **las cuatro medidas en runtime**, no de oido: (i) prosa sin patron: **3** coincidencias en los documentos auditados (+1 en el template excluido: `pasa 4/4`); (ii) fuera de los documentos de gobierno: **245** instancias (`AGENTS.md` 1 —«10/10 checks», vencido—, `docs/GUIA_TECNICA.md` 107, `docs/contributing/REGISTRY.md` 137); (iii) pins en `tests/`: **4 archivos**, incluido el pin que **esta fase añadio**; (iv) fuentes dinamicas no etiqueta: **4.330** funciones en disk contra las 4.246 que publica `AGENTS.md`.
- [x] Tres archivos de estado, **cada uno cubriendo un solo estado**: `test_governance_numbers_sin_hallazgos.py`, `test_governance_numbers_ausente.py`, `test_governance_numbers_lector_fallido.py`. Nota de forma: la tabla de tests obligatorios del prompt lista **cinco** archivos y sus criterios de completitud decian «los cuatro tests pasan»; se escribieron los cinco mas el de mutantes (23 funciones, 28 casos).
- [x] `mutation/` con **verde + seis rojos** (`verde_baseline.txt`, `mutante_M-A1`, `M-A2`, `M-A3`, `M-A4`, `M-POBLACION`, `M-SUJETO`). El anclaje se afirmo **por `assertion_key`** (sujeto + afirmacion + documento), no por `assertion_id`: el primer intento con ids posicionales produjo un rojo que nombraba a otra asercion (perdia A4 al mutar el guard de A1) — eso es literalmente L-V2.1 y queda capitalizado en `10-analisis-post-implementacion.md`.
- [x] Medido con los mismos comandos en los dos lados. PRE: nada en `tests/` afirmaba el 11, y un `[5/7]` en `test_validate_plan_closure.py` afirmaba el hook. **POST: 4 coincidencias nuevas del denominador 11 creadas por esta fase** (`test_governance_numbers_reproduce_A1_A4.py`), declaradas con dueño D1/D2 en `baseline-pre-post.md` en lugar de limar la asercion.
- [x] Par `faseA_baseline_pre.txt` / `faseA_baseline_post.txt` + `baseline-pre-post.md` con la resta: quick **11→11 (0)**, hook **7→7 (0)**, poblacion A8 **22/17/2 → 22/17/2 (0)**. Y **sin** fingir delta 0 donde la fase si movio la metrica: seleccion de tests **0→23 funciones (+23)**, que es justo lo que AC5 exige publicar por separado.
- [x] `log_phase_completion.py --fase FASE-A --check-manual-docs` ejecutado y `build_lesson_index.py` regenerado el 2026-09-21. El commit se hizo con instruccion literal del operador el 2026-09-21 (`a7564ae`, 34 archivos) y **llevo el indice dentro**, como exige R2.10 y comprueba `[6/7]`.

## FASE-B — `decision_client.py` — **cerrada VERIFICADO OFFLINE el 2026-09-21** (AC6–AC9; y AC16/AC17/AC18 en su parte)

- [x] Un solo archivo importa SDK/adapter; verificado sobre el árbol real con población. **Medido**: `0`
      imports prohibidos fuera de la puerta sobre **692** `.py` del árbol de trabajo (4.379 nodos de
      import vistos), y `0` cargas dinámicas de paquete. El escáner es **AST, no grep**: distingue
      `import typesafe` (hallazgo) de `typesafe` en un docstring (mención: **21**, publicadas y no
      contadas como hallazgo). Población con sus exclusiones declaradas (`venv` 7.618,
      `site-packages` 8.889, `tmp_test` 690 —donde el plan hermano aisló el SDK real—, `temp` 65,
      `build` 14). Dos caminos con dientes propios: `M-AC6-token` (vaciar la lista de tokens devuelve
      un verde silencioso) y `M-AC6-carga-dinamica`/`M-AC6-superficie` (una carga con el nombre armado
      en runtime bajo un directorio `*proveedores*` **sí** es hallazgo; fuera de esa superficie es un
      límite publicado, no un silencio: **16** cargas no resueltas en el árbol real).
- [x] `provider_status` con los tres estados; ningún `except` produce una decisión. Cada estado
      provocado por su causa y **ningún test cubre dos**: `RESUELTO` (contract test), `NO-CONFIGURADO`
      (4 `motivo_clase` distintas que no colapsan: env sin definir, directorio sin definir, ruta
      inexistente —con la ruta impresa—, nombre no registrado —con los nombres que sí están—) e
      `ILEGIBLE` (6 guards de forma, cada motivo nombra al suyo). La conversión a tipos **no rellena
      campos**: con los seis guards apagados sigue sin producir decisión (`M-AC7-forma` apagado guard
      a guard, y el caso anti-default explícito `M-AC7-proveedor-por-defecto`).
- [x] Contract test que se pone rojo si cambia la forma del proveedor falso. `contract.txt` guarda el
      verde (`exit 0`) y el **rojo** (`exit 1`) corriendo **el mismo test** contra una copia de
      `falso_forma.py` a la que se le quitó `confidence`; el rojo nombra a los dos guards que cayeron
      (`campos-conocidos`, `forma-choice`), comprobado en el proceso padre porque la anchura del
      terminal del hijo trunca los motivos.
- [x] Versión de modelo pineada y declarada; sin literales del proveedor pineados.
      `PIN_MODELO_DECLARADO` = `jev-1.13.0` con su fuente, `verificado_desde_este_repo: false` y
      `usado_por_el_codigo: false`; un test lee el AST de la puerta y afirma que el pin aparece **una
      sola vez** (su definición), y otro afirma que ningún literal de este archivo de tests contiene
      un token prohibido. La comparación del contract test es contra lo que **el proveedor falso
      declara**, no contra una cadena.
- [x] `costura.json` con `files_changed_to_add_provider == 1`. Medido por sha256 sobre la copia
      temporal de la frontera completa (puerta incluida), no afirmado: `agregados =
      [falsos_proveedores/falso_segundo.py]`, `modificados = []`. Y el `1` no sirve si la puerta
      devuelve siempre el mismo módulo: los dos proveedores se despachan y **contestan distinto**.
      Los tests paralelos (`1`) se declaran aparte, como hace el AC1 del plan hermano.
- [x] **Cero llamadas de red** y cero credenciales en el árbol, la evidencia y los logs. Verificado,
      no afirmado (`cero-red.txt`): guard autouse que hace explotar `socket.socket`,
      `create_connection`, `getaddrinfo` y `gethostbyname` en **todos** los casos, con una prueba de
      que el guard está puesto y otra de que la costura llega a `RESUELTO` con el guard armado;
      denegatoria AST de 19 módulos capaces de hacer red sobre la puerta y sus proveedores; y el SDK
      **no instalado** en el venv del producto (`typesafe/jev/httpx2/tenacity = AUSENTE`). De la
      credencial solo se publica `presente` (bool) — hay dos tests que lo afirman, incluido que ni su
      longitud ni un preficio salen del volcado.
- [x] Ninguna comparación de proveedores intentada: es D7 y se dice en el cierre. `extensibilidad.txt`
      lo declara con su porqué (con un solo proveedor real no hay elección que medir, y exigir un
      número inexistente se cerraría como `NO-EJERCITADO` certificando humo).
- [x] **Commit cerrado el 2026-09-22 en `647f436`** (46 archivos, +4.412/−97) con instrucción literal,
      con el par del índice dentro y con los **7** checks del pre-commit en verde. **Push hecho el
      2026-09-22** por instrucción literal del operador: `origin/master` quedó en `b764e8d` y la paridad
      re-medida tras `git fetch` es **`0/0`** (antes: `0/2` al commitear la fase, `0/3` tras su barrido
      `612efd0`, `0/5` tras `cf64faf` — cada commit documental suma uno, por eso la cifra se re-mide y no
      se copia). El push publicó también el commit **ajeno** `eecf246` (ROADMAP v4.3), que era ancestro
      obligado de esta fase y no podía quedar atrás. El commit
      además **movió el denominador que la fase había publicado**: `git ls-files '*.py'` pasó de 678 a
      **691** (+13 archivos propios) y AC6 sigue en **0** re-medido con la puerta; la brecha restante
      contra los 692 del escáner se desglosó archivo por archivo y dio un nombre —
      `.venv-wsl/bin/activate_this.py`, exclusión no declarada en `iterar_py()` — que queda como
      **S11** con su lección **L-VCF-11**.
- [x] **Conciliación con la remediación del bloque A aceptada el 2026-09-23.** S11 y S12 quedaron
      corregidas en código **fuera de este plan**, por las sesiones del bloque A de
      `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` (commit **`fdd397f`**, superficie
      `decision_client.py` + `validate_governance_numbers.py` + sus tests). Ese bloque publicó que lo
      suyo era **corrección técnica, no cierre contractual**: faltaba la enmienda en este plan, y esa
      es la que se registra aquí. Re-medido offline en la misma fecha: `--scan-imports` → **0** imports
      sobre **696** `.py`, y `git ls-files '*.py'` = **696** → **residuo 0** (S11); `--report` sin
      destino → `exit 1` con A1–A4 y **sha256 de la evidencia de FASE-A intacto** (S12); `--costura` →
      `files_changed_to_add_provider = 1` con su `alcance_de_ac9` impreso (AC9 = extensión **local**, no
      integración de un SDK real); selección `decision_client` **87 passed**, `exit 0`. Cierre original
      (`647f436`), corrección (`fdd397f`) y aceptación (esta fila) van **separados** y no se atribuyen
      entre sí. **No** se volvió a registrar la fase ni se movió `VERSION.yaml`. Detalle con comandos y
      códigos: `dependencias-fases.md` §Conciliación y
      `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/`.

**Lo que esta fase no cerró, con su motivo**: activar el proveedor (**D7**), el lint que lo consumiría
(**D6**) y una decisión que este repo no puede tomar sola: dónde vivirá el `import` del SDK cuando
D7 se active. AC6 (solo la puerta importa) y AC9 (añadir cuesta un archivo) se satisfacen hoy con
**0 coincidencias**, pero con un proveedor real en un archivo propio la geometría exige elegir entre
(a) que la puerta posea el `import` y el archivo nuevo solo declare, o (b) re-anclar AC6 a «la puerta
y su directorio de proveedores». Queda escrito en `10-analisis-post-implementacion.md` para que D7 lo
decida, no para que esta fase lo reinterpretara.

## FASE-C — `triage_lesson_relevance.py`

**EJECUTADA y CERRADA el 2026-09-24** con mandato propio del operador y corte **«hasta listo para
revisión»**: el `git push` se hizo después, el mismo 2026-09-24 y también con instrucción literal (`da382b1..5817edd`, paridad **0/0** re-verificada). El `git commit` sí se hizo, el mismo 2026-09-24 y con
instrucción literal del operador (opción A2): `7f2e9f9` para el helper de BLOQUE-B que la fase reutiliza
y `5817edd` para las **37** rutas propias; los documentos del plan, el par de índice y `REGISTRY.md`
quedan **fuera** del commit. Las cinco decisiones que
el prompt dejaba abiertas **no** se tomaron en la sesión: se implementaron como estaban resueltas en
`04-contrato-ejecucion.md` §Enmiendas (E1–E5). Dos desviaciones fueron **declaradas por el operador y
registradas con su medición**, no aplicadas en silencio: el corpus real de AC13
(`.opencode/plans/Archives/`, no `Archives/` a secas) y el proveedor falso (solo existe montado por
entorno dentro de `tests/quality_gates/lesson_relevance/`). Evidencia:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/`. Antecedente, ya vencido: «Contractualmente
preparada el 2026-09-23, no ejecutada».

- [x] `removed: []` afirmado por un test sobre el §2 real de este plan (AC10).
- [x] `index_status` distingue **tres** causas: `AUSENTE` (ruta + comando) / `VENCIDO` (⟦E2⟧ lo produce
      **el check de frescura propio de C**, no el `[6/7]` del hook) / `LECTOR-FALLIDO` (JSON existente
      pero ilegible, con su motivo). Ninguna prueba puede decir «sin candidatos».
- [x] Umbral ⟦E1⟧ aplicado a **`confidence`** de una pregunta **`choice` de dos opciones**, con `basis`
      que nombra el campo y un test que afirme que `probabilidad_si` **no** es el campo gobernado.
- [x] `threshold` publicado con valor, base y `action_below`; ningún camino auto-filtra.
- [x] ⟦E3⟧ El script **no** escribe §2: cada propuesta pasa por **revisión humana explícita** y su
      **aceptación o rechazo queda registrado** con quién decidió. Aceptada → entra con dueño y «qué
      cambia»; rechazada → se publica el rechazo. Ninguna fila se borra.
- [x] Test contra planes reales de `Archives/` con `skipif` visible y su corrida declarada.
- [x] Mutation check sobre el símbolo real del guard de no-filtrado.
- [x] `coverage.json` con los términos usados y sus conteos, **incluidos los ceros**.
- [ ] ⟦E4⟧ `acceptance` = **`NO-EJERCITADO` con su motivo** bajo proveedor falso, **sin cifra
      simulada**; es el número que, con proveedor real, decidirá si **D6** se activa — y D6 sigue
      **dormida** al cerrar C.
- [x] ⟦E5⟧ C cerró leyendo el **workflow canónico vigente** y sin aplicar las mejoras generales de la
      orden de calidad (B autorizado, estado exclusivamente en la matriz vigente §13;
      bloque C y piloto **sin autorización**): cero renumeración (AC16 delta 0).
      ⟦**Vencido en parte el 2026-09-24**: el **bloque C** de esa orden se autorizó y ejecutó ese día
      como enmiendas documentales sobre los cuatro planes (§4.C y su resumen único en
      `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`); **el piloto
      FASE-C sí sigue sin autorización**, y es el piloto —no el bloque— lo que ejecutaría esta casilla.
      La restricción de E5 queda intacta: esas enmiendas no cambiaron el gobierno del proceso, así que
      C sigue debiendo cero renumeración (AC16 delta 0).⟧
- [x] §4 del `00-lecciones-capitalizadas.md` actualizado con el auto-triaje del plan y su resultado
      (propuestas aceptadas / rechazadas), **después** de la revisión humana, no antes.
**Cierre de la sección (2026-09-24, FASE-C).** Cada casilla de arriba se marcó contra su artefacto
en `evidence/…/FASE-C/`, no contra la intención. Lo que agregan los hechos medidos a lo que pedía el
prompt:

- **AC10 con el guard ejercitado**: 11 de las 14 filas ancladas fueron juzgadas `no-pertinente` por el
  emisor y **ninguna desapareció** (`ac10_delta.json`, `removed: []`). Sin esa oportunidad real de
  borrar, el `[]` habría sido un verde vacío (lección **L-VCF-13**). Sha256 del `00-` idéntico y cero
  escrituras observadas dentro del plan.
- **AC11 con dos sub-causas que la concepción no preveía**: `LECTOR-FALLIDO` por **forma que no cuadra**
  (JSON que se parsea y cuya clave `lecciones` no es lista) y por **cálculo propio caído** — parseable
  no es conforme (lección **L-VCF-14**). Los tres `exit` distintos: 2 `AUSENTE`, 4 `VENCIDO`, 3
  `LECTOR-FALLIDO`, más 7 `EMISOR-NO-CONFIGURADO` y 5 `TOPE-EXCEDIDO`.
- **AC12 probado por contraste**: el emisor falso publica `por_si` y `confidence` por ejes
  independientes, así que existe un candidato con `por_si` 0.90 y `confidence` 0.41 que **no** es
  propuesto, y candidatos con el mismo `por_si` en buckets distintos.
- **AC13 corrió**: 4 casos sobre los 2 planes archivados con `00-` (de 27), `SKIPPED = 0` con `-v -rs`.
- **AC14 con su rojo**: verde 14→14 y rojo 14→**3**, nombrando al guard mutado. Disciplina **S13**:
  destino por argumento obligatorio (probado con `inspect.signature`), ancla positiva con el observador
  de escrituras compartido y `huellas` (sha256+mtime+tamaño) del expediente de FASE-A intactas.
- **AC15 con sus 5 ceros** sobre 10 términos, incluido `verificador mec = 0` (A5 reproducido sobre el
  índice generado), y **ninguna cifra pineada** en el script: hay test que lo prohíbe.
- **Deuda nueva con dueño y disparador: S14** — `--plans-dir` sin `--context-dir` simétrico; apuntar el
  triaje a una copia compara un corpus mixto. Ver `10-analisis-post-implementacion.md`
  §Decisiones de FASE-C. No se cerró reinterpretando nada en silencio.
## FASE-D — `build_phase_briefing.py` — **cerrada VERIFICADO OFFLINE el 2026-09-24** (AC19–AC23; y AC16/AC17/AC18 en su parte)

- [x] `briefing/FASE-X.md` generado para **todas** las fases del plan, dentro del directorio del plan.
      Medido: **5 packs** (A, B, C, D, RELEASE) = las 5 fases que el plan tiene, en
      `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`. Estado por pack: COMPLETO **4**,
      SECCION-NO-RESUELTA **1** (RELEASE), FUENTE-AUSENTE **0**. Fuentes declaradas **34**, secciones
      pedidas **23**, resueltas **23**.
- [x] `no_incluye[]` y `lectura_aparte_obligatoria[]` no vacíos; el workflow canónico figura ahí.
      Con test que lo prohíbe vacío por fase. El workflow entra como lectura aparte con su peso publicado
      por `carga.json` (`workflow_canonico_bytes`, por fase) y por la fila «Carga de lectura A7» del
      `README.md` de este plan, y con la razón (D3); **la cifra no se copia en esta casilla** — este
      documento entra al pack que el generador mide (**L-VCF-19**). **No** se copia: hay test que busca una tajada de
      600 bytes del archivo y exige que no esté en ningún pack, más el observador de escrituras sobre
      `.agents/`.
- [x] `carga.json` con `method` literal, bytes exactos y divisor de tokens declarado, **y los tres
      sumandos de la carga total** por fase: `workflow_obligatorio`, `coste_de_generacion`,
      `pack_consumido` (contrato §Carga total y frescura del pack). Publica además
      `omitido_declarado_bytes` y `andamiaje_del_pack_bytes`, que son los dos únicos números con los
      que el delta se puede reconstructurar.
- [x] Par pre/post de **checks** (delta 0: quick 11→11, hook 7→7, en `faseD_baseline_pre.txt` /
      `faseD_baseline_post.txt` + `baseline-pre-post.md`) y par pre/post de **carga de lectura**
      (`faseD_carga_pre.txt` / `faseD_carga_post.txt`, ambos con `stat -c %s`), con la resta sacada
      **entre cargas totales**. La resta no se transcribe en este `.md`: **este checklist entra en el
      pack que ese `stat` mide**, así que copiar el total lo vence (**L-VCF-19**); los dos totales y el
      delta los imprimen `carga.json` y `carga-pre-post.md`. `instrumentos/comprobar_resta_carga.py`
      comprueba cinco identidades y sale `exit 0`; **la prueba no es la cifra, es que el `stat` del par
      cuadre con el JSON**.
- [x] Delta explicado por fase; cero o negativo declarado, no escondido. **La concatenación no se
      presenta como ahorro y se publica lo que el pack omitió.** Cada fase publica su `delta_bytes` con
      su porcentaje sobre su propio `before`, y cada uno cierra con la identidad
      `delta == omitido − andamiaje − coste` (`resta_comprobada: true` en las cinco). Un test planta una
      fuente diminuta y exige que el delta **negativo** se publique igual, con la misma identidad.
- [x] `--check` falla contra una **fuente** cuyo sha cambió y pasa al revertir (demostrado en disco,
      no en memoria); y **no** falla solo porque HEAD avanzó: HEAD es procedencia, no llave de
      caducidad, publicado como `procedencia_distinta`. Cuatro causas distinguibles con su prueba:
      `FUENTE-AUSENTE`, `SHA-DISTINTO`, `FUENTE-ILEGIBLE`, `PACK-AUSENTE`. El pack no figura en su
      propio `sources[]` (test).
- [x] El generador resuelve un plan **bajo `Archives/`** por nombre y por ruta vigente; demostrado
      sobre archivados reales, no plantados (es la llamada del RELEASE tras el `git mv`). Y un plan
      inexistente da `exit 2` con sus rutas intentadas, no un pack vacío.
- [x] Tres estados de resolución de secciones, **un test por estado** y una prueba de que no colapsan
      (los tres en un solo test comparativo). El recorte se declara con la sección pedida, las rutas
      intentadas y los títulos disponibles; un ítem declarado en prosa («los cuatro prompts de fase»)
      **no se adivina**.
- [x] Test contra una fase de un plan **archivado real**, con `skipif` visible y su corrida declarada
      (`r26.txt`). **Lo que midió esa corrida: 0 de 121 prompts archivados declaran la lectura en el
      formato que el generador parsea** → esos packs salen `SIN-DECLARACION` y su `--check` se publica
      `SIN-FUENTES`, no `OK` (ver deuda **S16**).
- [x] `mutation/` con **verde y rojo** del guard real `GUARD_NO_TRUNCAMIENTO_ACTIVO` (AC23): apagado,
      el pack de RELEASE conserva el estado pero **pierde la declaración del recorte** y se achica en
      silencio (los dos tamaños y su diferencia, en `mutation/resumen.txt` — no se copian aquí por
      **L-VCF-19**). El anclaje usa una cadena exclusiva del generador,
      porque «rutas intentadas» y «sección pedida» también aparecen en los documentos copiados y
      habrían dado un rojo que no era.
- [ ] → **reformulada**: «`git status .agents/` vacío al cerrar». **Medido al abrir: `.agents/` ya
      tenía 3 rutas sucias de trabajo ajeno** (executor y dos templates, del bloque B de la orden de
      calidad). Un `git status` lleno no prueba que esta fase escribió, así que la casilla se verifica
      como lo que goberna AC17: **cero bytes aportados por la fase**, con el observador de escrituras
      sobre `.agents/` (ancla positiva en el directorio de salida) y sha256+size de los 4 archivos,
      iguales antes y después. La deuda de esos 3 archivos sigue siendo del bloque B, no de esta fase.
- [x] Dependencia D6 **re-declarada con su causa**, no re-abierta: sigue **dormida** mientras AC15
      publique `NO-EJERCITADO` (rama inalcanzable sin D7 activa). Ver `dependencias-fases.md` §Deuda.
- [x] `.agents/`, prompts de fase ajenos, `run_all_validations.py`, el hook, `build_lesson_index.py`
      y los scripts de A/B/C: **intactos**. FASE-D no llamó a ningún proveedor ni abrió socket
      (guard autouse en los 49 casos, con su prueba de que dispara: `cero-red.txt`).


## FASE-RELEASE

- [ ] Q7 (QMind) re-ejecutada **solo con autorización literal y presupuesto propios** (momento remoto),
      o publicada `PENDIENTE-AUTORIZACION` con su causa y con la premisa «el notebook cambió» declarada
      como no comprobada. La limitación se re-fecha en §4 y en `dependencias-fases.md`; no se borra ni
      se cierra por omisión (D8).
- [ ] Sync de versiones, CHANGELOG, `GUIA_TECNICA` y `docs/contributing/REGISTRY.md` (cuatro módulos).
- [ ] D1 conciliada por referencia a la **matriz vigente §13** de la fuente única de B; la espera
      original de autorización es histórica, no se hereda el rojo A1–A4 ni un verde retirado.
      **Correr `validate_governance_numbers.py` aquí es leer el estado, no reparar `.agents/`.**
- [ ] D2/D3/D6/D7 con estado explícito tras leer el `acceptance` de C y el `carga.json` de D;
      D3 parcial, dueño **«Plan propio, posterior»**, sin diferir a C/D2 obligaciones de B; **D2 sin dar
      por satisfecho su disparador** por las enmiendas del bloque C sobre `REFACTOR-WHATSAPP`.
- [ ] Orden exacto, solo con autorización propia de las operaciones: write-back → índice → `git mv`
      → índice → **regenerar el pack con la ruta trasladada** → refs → citas → **check del pack** →
      quick. Verificación/cierre documental sin commit; archivado y eventual commit posterior requieren
      autorizaciones separadas (prompt RELEASE §Restricciones).
- [x] Ningún AC promocionado a ✅ sin su mutation check o su clave en el artefacto. **Ningún resultado
      parcial del momento remoto promocionado a éxito del cierre.**

### Estado del cierre de FASE-RELEASE (2026-09-25)

Cumplido en su parte offline, con la evidencia en `evidence/…/FASE-RELEASE/` (12 archivos):

- [x] **C0 ejercido antes de escribir**: mandato con destinos literales; el sync y la regeneración de
      `DOMAIN_PRIMER` se corrieron **después** de nombrarlos, y `VERSION.yaml` no se escribió hasta tener
      versión, fecha **y** codename (el codename quedó delegado y se registró con sus dos alternativas
      descartadas en `09-codename-y-bloqueador.txt`).
- [x] Sync de versiones, CHANGELOG `[4.78.0]` y `docs/contributing/REGISTRY.md` por su **único** escritor
      (`log_phase_completion.py --release 4.78.0`; el Version Sync Gate dio `(OK) CHANGELOG y VERSION.yaml
      sincronizados en 4.78.0`). `GUIA_TECNICA` movió su fecha por su propia regla.
- [x] **Defecto declarado, no absorbido**: la escritura final de `SyncEngine.sync_rule` en
      `scripts/sync_versions.py` y la de `run_regenerate_domain_primer` en `scripts/doctor.py` cierran con
      `write_text` sin `newline="\n"` y volvieron CRLF seis archivos que git almacena en LF; el detector de
      finales de línea del bloque B lo cortó (`[FAIL] Line endings`). Remedio de esta sesión: normalización
      byte a byte con `git diff -U0` verificado (sigue siendo solo tokens de versión/fecha/codename). La cura
      de fondo es editar `scripts/` y **no** está en este mandato. **→ deuda S17, con dueño y disparador en
      `dependencias-fases.md` (registrada el 2026-09-25 al cerrar la orden de calidad; no curada).**
      ⟦**Curada el mismo 2026-09-25, en la sesión con mandato de código**: `newline="\n"` en las **tres**
      escrituras de la familia (`SyncEngine.sync_rule`, `run_regenerate_domain_primer` y `run_status`, esta
      última hallada al curar), con prueba de bytes sobre escritores reales en temporales y control contra
      la versión commiteada. Estado vigente: §S17 de `dependencias-fases.md`.⟧
- [x] Segundo hueco declarado: la regla `readme_version_header` no goberna la fecha legible del
      `README.md` (su línea `**v…** -- … | Actualizado …`), que sigue diciendo «11 Septiembre 2026» con
      `release_date: 2026-09-25`. **No se editó a mano**: un
      dato con escritor se arregla en el escritor o con un verificador. **→ deuda S18, con dueño y
      disparador en `dependencias-fases.md` (registrada el 2026-09-25; no curada).**
      ⟦**Curada el mismo 2026-09-25**: `readme_version_header` llega hasta la fecha y emite `{date_text}`
      (forma larga, no ISO); su `--check` pasó a detectar el desfase — de `IN_SYNC` a `FAIL` sobre el
      README de la release — y la línea 5 se alineó **por su escritor**, con `README.md` autorizado como
      destino aparte. Estado vigente: §S18 de `dependencias-fases.md`.⟧
- [x] **Alineación de política de `DOMAIN_PRIMER`: declarada, NO alineada** (decisión del operador del
      2026-09-25, cierre de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`). Lo que sigue divergiendo es el
      **cuándo**: `AGENTS.md` §Flujo Documental dice «se regenera en FASE-RELEASE (no manualmente)» y
      `docs/CONTRIBUTING.md` Paso 5b dice «al cerrar cada fase de implementación regenerar» + validar solo
      en RELEASE — dos disparadores para el mismo artefacto, y generación y validación siguen siendo dos
      operaciones distintas. **No se editó configuración central**: alinearlo requiere mandato literal
      sobre `AGENTS.md` y `docs/CONTRIBUTING.md`, y un sync de cabeceras no lo cubre (contrato **C0**). Lo
      que sí se hizo en RELEASE fue regenerar el archivo **con su writer**, que es otra operación.
- [ ] **Q7 (D8)** y **`--upload` (D9)**: `PENDIENTE-AUTORIZACION`. La premisa de D8 («el notebook cambió
      desde la auditoría del 2026-09-20») quedó **no comprobada**, que no es lo mismo que verificada.
- [ ] **Archivado** (`git mv`), **commit** y **push**: pendientes, cada uno con su autorización propia. El
      plan sigue en `.opencode/plans/` y su producto, en el árbol de trabajo.
- [x] D1 leída por referencia a la **matriz §13** de la fuente única de B; D2/D3/D6/D7 con estado explícito
      (ver `03-tarea3-deuda.txt`); **ninguna** reparada ni promocionada aquí.
- [x] **D10 re-leída con su fecha**: la firma del writer no cambió (`--nb`, `--strict`, `--upload`; sin
      `--title` ni `--file`), así que el bloque de cierre no se re-escribe.

## Controles de cierre del plan

- [ ] `run_all_validations.py --quick` en verde con su **composición intacta** (AC16: delta 0 contra el
      par pre/post que mide la fase; el número lo imprime la corrida, no lo fija este checklist).
- [ ] `validate_governance_numbers.py` ejecutado sobre el árbol final **como lectura de estado**, con su
      denominador publicado.
- [ ] `build_phase_briefing.py` **regenerado con la ruta vigente del plan** y luego su `--check` en
      verde sobre el árbol final.
- [ ] `validate_lesson_capitalization.py` en verde sobre el `00-…` final.
- [ ] `validate_plan_citations.py` sin citas de línea en los archivos de este plan.
- [ ] `build_lesson_index.py --check` en verde **después** del archivado.
- [ ] Todos los ACs con estado alcanzable declarado, incluidos ⚠️ y `NO-EJERCITADO`.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/06-checklist-implementacion.md` · sha256 `6c0e55485119589fe477600ac360691f9301475e5be617bf5b4b104591dbc0b9` · 47550 bytes copiados de 47550 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `dependencias-fases.md` (documento completo)

# Dependencias y bloqueantes — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está **concluido
contractualmente** por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; **el piloto FASE-C de este
plan no lo estaba** y ninguna de sus fases se ejecutó ni se diseñó al conciliar.
**⟦Rectificado el 2026-09-24 al cerrar FASE-C⟧**: esa frase sigue siendo cierta sobre el **bloque C**
(enmiendas documentales) y ya no lo es sobre el **piloto**: el operador autorizó esa tarde, con mandato
propio y corte **«hasta listo para revisión»**, ejecutar FASE-C, que quedó **cerrada sin commit ni push**
(ver su fila en §Cadena y su evidencia en `evidence/…/FASE-C/`). Fuente única de
resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
D3 permanece parcial, con dueño **«Plan propio, posterior»**. Los cierres de FASE-A/B y la
conciliación del bloque A se conservan como históricos, distintos de la remediación del bloque B.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

## Cadena

```
FASE-A ──► FASE-B ──► FASE-C ──► FASE-D ──► FASE-RELEASE-4.xx.0
 (lint      (costura   (triaje    (pack       (docs, sync, REGISTRY,
  determ.)   proveedor) pertin.)   briefing +  write-back, archivar)
                                    delta de
                                    lectura)   └─ VERIFY no aplica (§4.6 cae en criterio 2)

A y B son técnicamente independientes; C consume a ambas y D consume a las tres.
Se mantienen secuenciales por la Regla de Sesión Única del executor.
```

**No ejecutar fases en paralelo ni encadenarlas dentro de una sesión.** Un checkpoint no
habilita la fase siguiente.

| Orden / prompt | Objetivo | Complejidad | Estado |
|---|---|---|---|
| 1 · [FASE-A](05-prompt-inicio-sesion-fase-A.md) | `validate_governance_numbers.py`: aserción contra fuente dinámica, con denominador y tres estados | MEDIA técnica / ALTA consecuencia: es el guard de las ediciones futuras sobre `.agents/` | **✅ CERRADA 2026-09-21 — VERIFICADO OFFLINE (AC1–AC5)** |
| 2 · [FASE-B](05-prompt-inicio-sesion-fase-B.md) | `decision_client.py`: costura neutra, contract test con proveedor falso y **un solo** proveedor configurable; AC9 certifica que añadir el segundo cuesta un archivo | MEDIA-ALTA: la superficie que cambia de proveedor sin que nadie más se entere | **✅ CERRADA 2026-09-21 — VERIFICADO OFFLINE (AC6–AC9; AC16/AC17/AC18 en su parte)**. **Conciliada el 2026-09-23** con la remediación del bloque A de la orden de calidad: **S11 y S12 aceptadas** (corrección técnica en `fdd397f`, no de esta sesión); AC9 declarado con su alcance local. Ver §Conciliación |
| 3 · [FASE-C](05-prompt-inicio-sesion-fase-C.md) | `triage_lesson_relevance.py`: capa de pertinencia **aditiva** sobre `lecciones_index.json`, nunca filtro | ALTA: es la mitad que el verificador de capitalización declara fuera de alcance | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE su mecánica (AC10–AC14 y AC15 en su parte no semántica; AC16/AC17/AC18 en su parte de C). AC15 queda ⚠️ PARCIAL con `acceptance = NO-EJERCITADO` (contrato E4), que es el techo alcanzable con D7 sin activar.** Cortes: la fase llegó **hasta listo para revisión** y se paró ahí. **Push hecho el 2026-09-24** por instrucción literal del operador: publicó `da382b1..5817edd`. ⟦**La paridad no se publica como cifra (2026-09-25)**: cualquier commit posterior la mueve, así que se lee con `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` — es la regla que este plan ya aplica a HEAD en su README⟧. **Commit hecho el 2026-09-24 con autorización explícita del operador y en dos tiempos**: `7f2e9f9` (el helper `tests/support_observador_escrituras.py`, creación de BLOQUE-B, viaja aparte por dependencia técnica: 3 tests de esta fase lo cargan en 8 puntos) y `5817edd` (las **37** rutas propias de FASE-C, +3.774 líneas, con los **7** checks del hook en verde). Quedan **fuera** por decisión del operador: los documentos del plan, el par de índice y `REGISTRY.md` — a nivel de hunk no se separa el cierre de C del trabajo de BLOQUE-B/C sobre esos archivos (164 hunks, **59** nombran FASE-C, 22 otro bloque, 83 sin marca). Consecuencia medida en un árbol extraído de HEAD con `git archive`: la suite de esta fase da **14 failed / 16 passed / 26 errors** (`SueloNoLeible: VENCIDO`, que es el guard de frescura haciendo su trabajo) y pasa a **56 passed** al regenerar el par con `build_lesson_index.py` en ese árbol; el `[6/7] --check` del hook valida contra el árbol de trabajo y **no** afirma coherencia interna del commit. Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` (`informe.json`, `ac10_delta.json`, `coverage.json`, `r26.txt`, `mutation/` con su verde y su rojo, `run_tests.txt`, `regression_calidad.txt`, `cero-red.txt`, `no-piso-pasado_ANTES/DESPUES.txt`, par pre/post de AC16). Métricas por fase: `09-documentacion-post-proyecto.md` §D, no este archivo. **D6 sigue dormida con causa medida** (ver su fila en §Deuda): `acceptance` no se ejercitó y no se simuló |
| 4 · [FASE-D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga de lectura medido** (AC19–AC23) | MEDIA: es determinista, pero gobierna lo que todas las sesiones futuras van a leer | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE (AC19–AC23; y AC16/AC17/AC18 en su parte).** Mandato propio del operador, corte **«hasta listo para revisión»**, **sin commit ni push** (instrucción separada como siempre). **Lo que produjo**: `scripts/build_phase_briefing.py` (determinista, cero proveedor, cero red) + **5 packs** en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, uno por fase del plan — COMPLETO **4**, SECCION-NO-RESUELTA **1** (RELEASE: el prompt nombra «los cuatro prompts de fase» en prosa y **no se adivina**), FUENTE-AUSENTE **0** — sobre **34** fuentes declaradas y **23** secciones pedidas, todas resueltas. ⟦**Re-medido el 2026-09-25 por la conciliación final de la orden de calidad**: ese `SECCION-NO-RESUELTA` era **conducta correcta del generador** (AC22: nombra la sección, las rutas intentadas y no adivina), y su causa —la prosa del prompt de RELEASE— se corrigió **en el prompt**, no en el generador. La corrida de hoy da **5 COMPLETO / 0 SECCION-NO-RESUELTA / 37 fuentes** (sus bytes y su porcentaje viven en la salida completa de `evidence/…/CONCILIACION-FINAL-ORDEN-2026-09-25/11-carga-corrida-3.txt`, no en esta fila). **`carga.json` NO se re-escribió** (evidencia cerrada de FASE-D, **S12**): lo que esta fila describía sigue siendo el estado que D certificó⟧. **AC20**: carga total medida en los dos lados con el mismo comando (divisor 4 declarado), con los tres sumandos por fase y la resta **entre cargas totales**; los dos totales y el delta **no se copian en este archivo**: viven en `carga.json` y `carga-pre-post.md` porque este `.md` está dentro del pack que ese `stat` mide (**L-VCF-19**); `instrumentos/comprobar_resta_carga.py` verifica cinco identidades y sale `exit 0`; el workflow canónico entra en los dos lados mientras **D3** no lo rebane, y por eso el ahorro real queda **muy por debajo de un tercio** (concatenar no es ahorrar). **AC21**: frescura por **sha256 de `sources[]`** contra el árbol, cuatro causas sin colapsar (`FUENTE-AUSENTE` / `SHA-DISTINTO` / `FUENTE-ILEGIBLE` / `PACK-AUSENTE`), HEAD publicado como procedencia y **con test que prohíbe que venza**; el pack no está en su propio `sources[]`; y el generador resuelve un plan **también bajo `Archives/`** (demostrado sobre archivados reales: es la llamada del RELEASE tras el `git mv`). **AC22**: a los tres estados del contrato se añadió una cuarta salida medida, `SIN-DECLARACION`, con su `--check` imprimiendo `SIN-FUENTES` en lugar de `OK`. **AC23**: `mutation/` con verde (declara) y rojo (no declara, y el pack se achica en silencio conservando el estado) del símbolo real `GUARD_NO_TRUNCAMIENTO_ACTIVO` — los dos tamaños, en `mutation/resumen.txt` y tampoco se copian aquí (**L-VCF-19**) —, destino por argumento obligatorio y expediente de FASE-A protegido por observador de escrituras + `huellas` (S13). **Tests**: 49 casos en `tests/quality_gates/phase_briefing/` (un estado por test, guard de cero red autouse). **AC17**: `.agents/` con **cero bytes aportados** — la casilla literal «`git status .agents/` vacío» **no era verificable** porque el árbol llegó con 3 rutas sucias ajenas del bloque B, y se afirmó como lo que goberna AC17: observador de escrituras + sha256/tamaño de los 4 archivos, iguales antes y después. **AC16**: delta 0 (quick 11/11 `exit 0`, hook 7→7) con los 49 casos declarados aparte. **Herencia de C aceptada sin reabrirla**: el pack exhibe la parte mecánica medida de C y su `acceptance = NO-EJERCITADO` **como lo que es**; E1–E5 no se renegociaron y **D6 sigue dormida** (ver su fila en §Deuda). **Deuda nueva con dueño y disparador: S16** — la convención `Lee …` que parsea el generador no está escrita en `prompt-fase-template.md`: medido, **0 de 121** prompts archivados la usan. Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/` (`informe.json`, `carga.json`, `carga-pre-post.md`, par `faseD_carga_pre/post.txt`, par `faseD_baseline/quick_pre/post.txt`, `baseline-pre-post.md`, `r26.txt`, `cero-red.txt`, `mutation/`, `instrumentos/`) |
| 5 · [FASE-RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre documental, sync, write-back y archivado en orden R2.5/R2.10 | MEDIA | **✅ CERRADA EN SU PARTE OFFLINE el 2026-09-25 — VERIFICADO sin red.** C0 ejercido (mandato con destinos literales, luego writers): release **4.78.0** `Gobernanza, costura, pertinencia y carga medida`, `release_date`/`date` 2026-09-25; cinco cabeceras por `sync_versions.py`; `DOMAIN_PRIMER.md` regenerado con su writer; `CHANGELOG.md` +90/0; `REGISTRY.md` por `log_phase_completion.py` (cabecera 2026-09-25). **Dos defectos de instrumento declarados con su cura pendiente en `scripts/`**: los writers reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y `readme_version_header` no goberna la fecha legible del README. **Sin autorización siguen**: Q7/D8 (premissa no comprobada), `--upload`/D9, `git mv`, `--fix`/`--update-baseline`, commit, push. Evidencia: `evidence/…/FASE-RELEASE/` (12 archivos) |

## Qué debe heredar cada fase

| Fase | Hereda de | Pieza concreta |
|---|---|---|
| A | — | **Estado medido del árbol, no asumido**: al publicarse la auditoría (`2c9d0c1`, 2026-09-20, paridad 0/0 con `origin/master` verificada con `git ls-remote`) el árbol está **limpio** y el índice viene regenerado y fresco; A re-mide HEAD/status al abrir porque la pareja del índice se comparte con las fases vivas de `REFACTOR-WHATSAPP`. Las cuatro aserciones vencidas A1–A4 medidas y copiadas en el maestro §1 (con **A3 rectificada: el write-back imprime `[15/15]`**), la medición A7 de carga de lectura re-medida (263.973 bytes) y la población A8 que obliga a la regla de clases de AC1 |
| A — **notas de ejecución (2026-09-21)** | lo que A encontró al medir de verdad: HEAD ya no era `2c9d0c1` sino `2deddee` (11 commits de `EVALUACION-JEV` encima) con paridad 0/0 conservada y árbol limpio; **A1–A4 siguen vencidas y A7 no se movió** (263.973 re-medidos); la población A8 se reprodujo exacta (22 + 17 líneas + 2). Dos hallazgos nuevos de la fase, con dueño: **(N1)** el disparador de **D1** era circular — «verificador verde» solo se cumple *después* de corregir `.agents/`, así que se reformuló a «verificador operativo con mutation check + decisión escrita del operador»; **(N2)** la propia prueba de AC1 **añadió 4 pins del denominador 11 en `tests/`** (familia iii de AC2), declarados en `baseline-pre-post.md` en vez de limar la aserción |
| B — **reutilizado, no reinventado** | A | `coverage_basis` con el mismo esqueleto de AC2 (`archivos_escaneados`, `poblacion`, `excluidos_por_directorio`, `limites`, `comando`, `medido_el`) y el tri-estado de AC3, que aquí se llama `provider_status` con sus `motivo_clase`. **Una adicción propia declarada**: el `status` de la puerta es binario en el escaneo (`SIN-HALLAZGOS`/`HALLAZGOS`) porque su tercer y cuarto camino (`AUSENTE`, `LECTOR-FALLIDO`) viven en la resolución del proveedor, no en el conteo — y ahí el tercero se llama `estado_lector`, no se colapsa con `NO-CONFIGURADO`. |
| B — **notas de ejecución (2026-09-21)** | lo que B encontró al medir | HEAD ya no era `e3c4573` sino `74d8ff5` (dos commits de barrido documental de FASE-A encima); `find . -name "*.jsonl"` sigue en **0** (D-V2.1 reproducida por quinta vez, métrica retirada y unidad contable declarada); **0** imports del SDK en el árbol y el SDK **no instalado** en el venv del producto (sí en `tmp_test/venv-jev-sdk`, excluido y publicado); la poblacion que `git grep` ve (678 `.py`) y la que ve el árbol de trabajo (692 en el árbol de trabajo; 690 en el primer escaneo de la fase) **difieren** y las dos se publican |
| C | A y B | La costura de B como única puerta al proveedor; los estados `AUSENTE`/`VENCIDO` de A aplicados al índice de lecciones. **Enmienda prospectiva aceptada el 2026-09-23 (orden de calidad §4.C, solo para CONTEXTO/C):** la pregunta binaria se formula como `choice` de dos opciones con `confidence` **independiente** (no con `noul`: su probabilidad de sí **no** es confianza — ver `decision_client.py`, que prohíbe `confidence` en `noul`); **AC11 elige la ruta (b)** (leer `lecciones_index.json` tras ejecutar C **ella misma** la comprobación de frescura, sin confiar en que otro gate lo regeneró), con `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` como tres causas distinguibles; y las propuestas del proveedor falso **no** entran a §2 del `00-` en automático: exigen **revisión humana explícita con aceptación o rechazo registrado**. Detalle en `05-prompt-inicio-sesion-fase-C.md` y en el maestro §4 |
| D | A, B y C | Los tres estados y `coverage_basis`; el informe de candidatos de C, que el pack exhibe como sección propia; y **el resultado no medido de C, que D acepta sin reabrirlo** (⟦bloque C, 2026-09-24⟧: con D7 inactiva el `acceptance` de AC15 solo puede ser `NO-EJERCITADO`, así que **no** es un disparador de D6 que D pueda encontrar «cumplido»). D hereda medido lo mecánico de C y **no** lo no medido. Reglas de carga total y frescura del pack: contrato §Carga total y frescura del pack |
| RELEASE | A, B, C y D | Los cuatro `coverage.json`/`informe.json`, los pares pre/post de las cuatro fases, el delta de carga **total** medido y el registro de deuda §6 del maestro. **Tres momentos con tres permisos** (contrato §Dos momentos del cierre): el cierre offline es de la fase; la consulta Q7 (D8) y el `--upload` (D9) son remotos y cada uno necesita autorización literal y presupuesto propios; el `git mv` es un tercer momento con autorización expresa. Y el pack se **regenera con la ruta trasladada antes** de verificarlo |

## Conflictos de archivo

| Archivo / ruta | Lo toca | Riesgo y regla |
|---|---|---|
| `.opencode/LECCIONES-INDEX.md`, `.opencode/lecciones_index.json` | **Este plan y las fases vivas de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`** | **Conflicto real, ya latente.** `[6/7]` del hook bloquea el commit con el índice vencido contra el árbol, así que **ambos planes lo regeneran**. Regla: regenerar en el mismo commit, nunca `--check` contra un índice ajeno; si aparece un diff que no proviene de tu edición, re-generar y volver a medir, no `git checkout` |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Solo FASE-D, y solo como **generado** (**existe desde el 2026-09-24: 5 packs**) | **Efecto colateral medido por D**: los packs son `.md` dentro del corpus que escanea `build_lesson_index.py`, así que **generarlos vuelve a vencer el par del índice** (A6 sobre un artefacto derivado). La cura no es editar el generado ni el JSON: es el paso 5 del contrato — regenerar el índice sobre el árbol final. Vive dentro del plan a propósito. En `.agents/workflows/` alteraría los contadores de skills (`validate_agent_ecosystem.py`, `sync_data.py`, `doctor.py` usan `glob("*.md")`) y exigiría seguimiento en su `README.md` — y AC17 prohíbe escribir en `.agents/` |
| `scripts/run_all_validations.py` | **Este plan: solo lectura** (AC16). **Pero no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance («su connection en `scripts/run_all_validations.py`») | Corregido el 2026-09-20: la cifra de 11 checks **no la pinea el prompt de FASE-C** de `REFACTOR-WHATSAPP` sino cuatro documentos suyos (arranque de FASE-B en su `README.md`, `06-`, `09-`, `10-`). **⟦Re-contado el 2026-09-24 por el bloque C de la orden de calidad: esa fila quedó vencida⟧** — su bloque de arranque ya no pinea la cifra, que fue sustituida por el comando que la imprime. Lo que hoy la contiene (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medido el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra) son **registros de fases cerradas**: evidencia histórica que no se reescribe. Consecuencia para AC16: el delta 0 se contrasta contra la corrida propia, no contra esas filas. Y ese tercer plan en vuelo puede cambiar **la etiqueta y la invocación** del write-back `[15/15]` — que es justamente la fuente de verdad de A3 y del fix de AC1. Regla: AC16 (delta 0) obliga a re-medir aquí; **D10** obliga a re-leer la interfaz del write-back antes del `--upload` de este RELEASE |
| `evidence/` (raíz) | **Nadie escribe en las rutas legadas** | Corregido el 2026-09-20: `evidence/FASE-A/` … `evidence/FASE-D/` **ya existen y son de `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`** (guardan `faseA_baseline_pre.txt`, `faseA_baseline_post.txt`, `faseB_baseline.txt`…), que son exactamente los nombres que produciría este plan si escribiera en la raíz: colisión y procedencia mezclada con un plan **archivado**. Toda la evidencia de este plan va a `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`, como hace `REFACTOR-WHATSAPP` con su subdirectorio. **Se conserva la cita de lectura** a `evidence/FASE-D/measure_iterations.py`, que es el instrumento canónico del executor y vive en esa ruta legado |
| `scripts/git_hooks/pre-commit` | **Nadie** | Sus 7 checks son la otra mitad de AC16 |
| `.agents/**` | **Nadie en escritura** | AC17. Es el objeto auditado y, desde FASE-D, también la fuente que se lee para componer el pack. Copiar una sección al pack **no** es editar la fuente |
| `scripts/build_lesson_index.py` | **Nadie** (solo ejecutar) | FASE-C lo consume como suelo determinista; modificarlo cambiaría la población que publican AC11 y AC15 |
| Los `05-prompt-inicio-sesion-fase-*.md` de **cualquier** plan | FASE-D solo **lectura** | El generador parsea la lista de lectura que cada prompt declara. Reescribir prompts ajenos es justamente lo que D2/D3 postergan hasta el RELEASE del otro plan |
| `00-lecciones-capitalizadas.md`, `06-checklist-implementacion.md`, `09-…`, `10-…`, `README.md`, `dependencias-fases.md` | Todas las fases, incremental | Cierre obligatorio del contrato §Cierres. Escritos por la fase que cierra, no diferidos a RELEASE |
| `scripts/validate_governance_numbers.py` · `decision_client.py` · `triage_lesson_relevance.py` · `build_phase_briefing.py` y sus tests | Una fase cada uno | Propiedad exclusiva; ninguna fase posterior reescribe sobre lo que la anterior serializó |

## Prerrequisitos y límites visibles

- **Ningún prerrequisito de autorización central, y ninguna credencial necesaria.** Por decisión del
  operador del 2026-09-20 **no entra Jev en este plan**: FASE-B prueba la costura contra proveedores
  **falsos** y AC9 certifica que añadir uno real es un cambio de un archivo. Activar el proveedor
  habilitado es la deuda **D7**, con su disparador. Consecuencia aceptada y escrita: ningún AC de
  este plan mide calidad de decisiones de un modelo real; miden forma, aislamiento y no-regresión.
- **La capa tibia del Paso 0 no se consultó al concebir; sí en la auditoría del 2026-09-20.** QMind
  `iah-cli-lecciones` no estaba accesible en la sesión de concepción (consulta Q7, declarada NO
  EJECUTADA en `00-lecciones-capitalizadas.md` §1 y §4) y se aplicó el fallback: memoria de proyecto +
  índice generado. En la auditoría el CLI estuvo disponible y la consulta se corrió cuatro veces; sus
  lecciones ya están en §2 (L-V2.1, L-V2.2, D-V2.1) y sus efectos en AC4, AC11 y el corte de
  presupuesto. **Lo que queda es D8 como re-correr, no como descubrir.** Límite que sigue en pie: el
  triaje de FASE-C calibra contra 320 IDs definidos y 50 citados sin definición (re-medido al
  regenerar el índice por la entrada de este plan, maestro §1 A6); si el notebook aporta lecciones
  fuera del repo, ese conjunto está incompleto y así se declara en el denominador de AC15.
- **FASE-D no reduce por sí sola la lectura de las fases del otro plan.** Sus nueve prompts siguen
  citando el workflow canónico; el recorte real de esa fuente es la deuda D3. Lo que AC20 puede
  cerrar es el delta sobre las fases de **este** plan, y un delta cero o negativo es resultado
  válido si se explica.
- **Este plan convive con otros dos en vuelo.** No comparte ACs, no comparte contador de corrida, no
  consume el intento `v4complete: 0/1` de `REFACTOR-WHATSAPP`. Pero las superficies compartidas **no
  son una, son tres** (medidas el 2026-09-20): la pareja del índice de lecciones con
  `REFACTOR-WHATSAPP`; la cifra de 11 checks que ese plan pinea en cuatro de sus documentos (hoy
  **cinco, todos ellos registros de fases cerradas** tras el arranque de su `README.md` pasar a mandar
  el comando — medido el 2026-09-24, §Conflictos de archivo); y
  `scripts/run_all_validations.py` + `scripts/validate_qmind_writeback.py`, que
  `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara **dentro de su alcance**. Este plan no los escribe;
  los lee como fuente de verdad, y de ahí salen AC16 (delta 0) y **D10**.
- **No hay FASE-VERIFY** y por tanto ningún AC puede certificarse contra output E2E. Techo
  alcanzable: `VERIFICADO OFFLINE` con mutation check, o `NO-EJERCITADO`.

## Deuda registrada (dueño y disparador, no silencio)

| # | Deuda | Dueño | Disparador |
|---|---|---|---|
| D1 | Corregir o eliminar las aserciones A1–A4 en `.agents/` | Este plan, FASE-RELEASE, con instrucción literal del operador; ejecución adelantada por mandato de B | **Estado vigente: matriz §13 de la fuente única, no certificado aquí.** Antecedente: **Disparador reformulado el 2026-09-21 (FASE-A):** era circular («verificador verde» no puede darse antes de la corrección que el verificador pide); pasa a *verificador operativo con su mutation check en disco* — cumplido el 2026-09-21 — **y** decisión escrita del operador sobre la forma de la corrección |
| D2 | Promover `validate_governance_numbers.py` a check del `--quick` con renumeración (11 → 12) | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases que pineen «11 checks». **⟦Aclaración del bloque C, 2026-09-24: las enmiendas de ese bloque sobre `REFACTOR-WHATSAPP` NO satisfacen este disparador⟧** — convirtieron en «el valor lo imprime la corrida» las **instrucciones prospectivas**, y dejaron intactos los registros de sus fases cerradas (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G), que son evidencia histórica. D2 sigue necesitando su propia sesión y su propia decisión |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura de A7: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B del plan en vuelo; los 254.010 de la concepción vencieron ese mismo día) | Plan propio, posterior | Mismo disparador para el rebanado completo; **D3 parcial**, no cerrada. La simplificación encargada a B no se difiere. **No** es FASE-D: el pack unifica lecturas declaradas, no recorta la fuente |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** (`validate_plan_semantics.py`): prompts de fase contra estado real del plan, con falsos positivos medidos contra los archivados | Plan propio posterior; **entra en este mismo directorio** si el disparador se cumple mientras está vigente | **Condicionado al resultado de FASE-C**: que el triaje entregue candidatos que el Paso 0 no ancló, con su aceptabilidad medida publicada en el informe. Si FASE-C sale inaceptable, **no se activa**: no se apila un segundo consumidor sobre una base que no funcionó. ⟦Precisión del bloque C, 2026-09-24⟧: mientras **D7** esté inactiva, la rama «salió aceptable» **no es alcanzable** — con proveedor falso `acceptance` solo puede publicarse `NO-EJERCITADO` (contrato **E4**), así que D6 queda **dormida con causa**, no «pendiente de que alguien consulte el número». Se re-evalúa al activar D7, no antes. **⟦Medido al cerrar FASE-C el 2026-09-24: la condición se cumplió literalmente — `coverage.json` publica `acceptance = NO-EJERCITADO` con su motivo y `valor: null`, sin cifra simulada (contrato E4). D6 queda DORMIDA y este plan no abre el lint semántico sobre una base que no juzgó nada; su re-evaluación sigue atada a D7⟧** **⟦Re-declarada al cerrar FASE-D el 2026-09-24 — no re-abierta ni re-asignada por interpretación: D leyó el `coverage.json` de C y encontró exactamente lo mismo que publicó C (`NO-EJERCITADO`, `valor: null`), así que la rama «el triaje salió aceptable» sigue sin ser alcanzable mientras D7 esté inactiva. D no reabrió C, no renegoció E1–E5 y no presentó la exhibición de candidatos en el pack como aceptabilidad obtenida. Lo único que activaría D6 es un proveedor real mediante (D7), y ese no es el estado de este plan⟧** |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev) como segundo proveedor detrás de `decision_client.py`; correr la comparación de proveedores y restituir «elegir midiendo» como AC | Plan propio posterior | Acceso existente desde 2026-09-20, pospuesto por decisión del operador. El consumidor natural es D6, el único trabajo genuinamente semántico del lote |
| D8 | Re-ejecutar la consulta Q7 de QMind. **Premisa vencida: el 2026-09-20 el CLI sí estaba disponible y la consulta se corrió en la auditoría de la concepción** (cuatro `retrieve`, resultados capitalizados como L-V2.1, L-V2.2 y D-V2.1). **Y su forma publicada es incorrecta**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; hay que pasar el ID `01a04d98-b7bd-778c-8441-26fdc7e35f45` | Este plan, sesión previa a FASE-RELEASE (re-corrida, no primera vez) | Que el notebook haya cambiado desde la auditoría, o que se quiera verificar el comando corregido con las citas que ya devolvió |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice después |
| **D10** | **Re-leer la interfaz del write-back antes de correr el cierre.** `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE, con disparador anterior al RELEASE de `REFACTOR-WHATSAPP`) piensa añadir `--title`/`--file` a `validate_qmind_writeback.py`, verificar contenido en vez de título, quitar la degradación a PASS y tocar su conexión en `run_all_validations.py` | Este plan, FASE-RELEASE | **CUMPLIDA en su lectura el 2026-09-25** (FASE-RELEASE): `validate_qmind_writeback.py --help` contra el árbol vigente → `--nb`, `--strict`, `--upload`; **sin** `--title` ni `--file`, decide por título y degrada a `exit 0` sin CLI. La firma **no** cambió (el mini-plan no se ejecutó), así que `04-contrato-ejecucion.md` **no** se re-escribió; lectura con su evidencia en `evidence/…/FASE-RELEASE/02-tarea1-firma-writer.txt`. Queda vigente la advertencia para quien sí corra la subida: verificar por contenido, no por título |

### Ejecución del bloque B de la orden de calidad (2026-09-23) — coordinación, no nuevo propietario

**Estado vigente: matriz §13 de la fuente única citada al inicio.** Las declaraciones de resolución
y suficiencia de pruebas que siguen son antecedentes retirados de §1–§12; no aceptación actual.

El operador autorizó el bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` y, dentro de él,
**adelantar D1 y la parte de D3 que B necesita** respecto de sus disparadores originales. Se registra
aquí sin crear un propietario paralelo: los dueños son los que fija el maestro §6 (D1 = «Este plan,
FASE-RELEASE»; D2/D3 = «Plan propio, posterior»); B ejecutó contenido bajo mandato, no reclamó la
propiedad. **Ampliación de alcance registrada:** el mandato B listaba el executor y
`prompt-fase-template.md`, pero retirar A4 (D1) exigía tocar su fuente,
`.agents/workflows/templates/lecciones-capitalizadas-template.md`; el operador autorizó expresamente
esa ampliación el 2026-09-23 y confirmó mantener los campos `version:` de frontmatter del executor
(v2.25.0) y de la plantilla (v1.6.0) como metadato documental, no bump de release (`VERSION.yaml`
intacto).

- **D1 — estado vigente en la matriz §13; no certificada aquí.** **Antecedente retirado** del
  2026-09-23: el dictamen decía «RESUELTA y revalidada». Las cuatro aserciones A1–A4 se corrigieron/retiraron **desde su
  fuente** (`.agents/`): el árbol vigente ya sale `SIN-HALLAZGOS` (`validate_governance_numbers.py`
  exit 0, vuelto a medir en la remediación). La decisión de forma fue retirar el denominador volátil
  en lugar de copiar la cifra vigente (la opción que el propio plan ya recomendaba: «dejar que el
  verificador la imprima es la que no se desfasa»). La detección no se debilitó: las cuatro
  aserciones quedaron reancladas a un **contraejemplo congelado** en
  `tests/quality_gates/governance_numbers/fixtures/` con sus mutantes, más una regresión del árbol
  honesto. Sin renumerar checks (**D2** sigue fuera).
- **S13 — estado vigente en la matriz §13; no certificada aquí.** **Antecedente retirado:** el
  dictamen del 2026-09-23 decía «RESUELTA, con la parte que faltaba hecha en la remediación del mismo día». El arnés
  `test_governance_numbers_mutation_por_asercion.py` ya no escribe en `evidence/…/FASE-A/mutation/`.
  El primer retiro **movió el destino pero seguía midiendo estado final** (instantáneas
  antes/después), y su control negativo definía una función de huellas propia dentro del test y
  provocaba el rojo con `os.utime`: no observaba escrituras. Ahora se observan las **operaciones de
  escritura** del escritor real con `tests/support_observador_escrituras.py` (alcance declarado:
  proceso de pytest, no procesos hijos), con ancla positiva, y los tres controles negativos del
  mandato (a escritor redirigido a destino protegido, b bytes idénticos, c mtime restaurado) sobre un
  **expediente desechable**. Se conserva la comparación de contenido y metadatos del expediente
  protegido. Cierre de la deuda que el bloque A dejó viva.
- **Controles negativos sobre el instrumento real (remediación, mismo día).** Ningún rojo por causa se
  produce ya reimplementando el defecto dentro del test:
  `test_control_negativo_el_escritor_permisivo_vuelve_a_afirmar_de_mas` corre el **escritor commiteado
  en `da382b1`** (leído con `git show`, materializado en un temporal —sin `checkout` ni `stash`—) y su
  `- [x] Tests passing` rompe la misma exigencia;
  `test_control_negativo_el_instrumento_versionado_re_llamaba_y_el_de_hoy_no` mide los **cálculos de
  verificador** en ese módulo versionado contra el del árbol, con la misma inyección y la misma conta
  (cifras PRE/POST y procedencia: resumen del bloque B, §4.1 y §4.3). Con eso
  el PRE queda anclado a una revisión, no a «el árbol que había cuando corri». ⟦Nombre rectificado el
  2026-09-23: la fila anterior citaba `…_recalcula_y_el_actual_no`, nombre que no existe en disco.⟧
- **D3 — ADELANTADA EN PARTE, NO CERRADA.** Se ejecutó lo que B requería: principio de
  proporcionalidad/reuso, retiro de cuotas «mínimo 3 lecciones», y **cortes utilizables sin commit**
  (los **cinco** terminan en espera de autorización; el commit es una acción posterior y separada,
  opcional, no el quinto corte). La remediación añadió lo que el
  primer pase dejó contradicho: la resolución de «RELEASE no registra» vs «registrar cada fase», y la
  sustitución de métricas copiadas en README/`09`/`10` por referencia a su fuente. Nada de eso se
  difiere a D2, al bloque C ni al piloto. El rebanado completo del workflow canónico (bajar la carga
  de lectura por fase) **sigue diferido** a su disparador (sesión previa a FASE-RELEASE de
  `REFACTOR-WHATSAPP`) y conserva su dueño del maestro §6: **«Plan propio, posterior»**, no se
  reasigna. No se declara D3 cumplida ni se midió reducción de carga (no hay ahorro D3 que afirmar).
- **Pendientes que B dejó y cómo están ahora.** ⟦Re-lectura el 2026-09-24 por el bloque C⟧ La fila
  original decía «el árbol de B está **sin commitear** (mandato: cero commit/push); el bloque C (enmiendas
  prospectivas a los cuatro planes) y el piloto FASE-C siguen pendientes de su autorización». De esas tres
  cosas, **dos cambiaron y una queda igual**:
  - **sin commitear**: sigue vigente y **no** lo mueve este bloque. El mandato del bloque C también
    prohíbe commit y push; su árbol —el de B y el de estas enmiendas— se entrega sin commitear y el
    commit es decisión separada del operador.
  - **bloque C**: **autorizado el 2026-09-24**, y ejecutado como enmiendas documentales sobre los cuatro
    planes (§Bloque C abajo). No es el piloto.
  - **piloto FASE-C**: **sigue sin autorización** y no se ejecutó. Su contrato está conciliado y su
    prompt listo; eso habilita pedir el mandato, no ejecutarlo.
  **Frontera de red:** la corrida `--check` **completa** que hizo la primera sesión de B
  incluye el check QMind y en esta máquina el CLI `qmind` está instalado, así que «cero red» **no puede
  afirmarse** y queda **NO DETERMINADO** (no se preservó su stdout; no se repite la llamada). El bloque C
  **tampoco** determinó esa fila: no corrió el `--check` completo ni hizo llamada alguna. Las citas
  «mandato §1…§8» tampoco apuntaban a nada versionado: el mandato llegó como adjunto del operador y se
  archivó como copia byte a byte en
  `evidence/…/BLOQUE-B-REMEDIACION-2026-09-23/99-mandato-de-remediacion-B-2026-09-23.txt`
  (sha256 `5a12e90f04a1ab3e4536bbe451c62d6dab1deac268706fbef02b1e12a9c31394`, procedencia y límites en
  `99-procedencia-del-mandato.md`).
  Fuente única de resultados de B:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
  (el resumen de la primera sesión, `…/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/00-resumen-bloque-B.md`,
  queda como antecedente con su cierre retirado).

## Bloque C de la orden de calidad (2026-09-24) — qué se concilió en este plan

Autorización: **solo enmiendas prospectivas sobre los documentos de los cuatro planes**, más el par del
índice de lecciones regenerado por su generador y la evidencia del bloque. Prohibido: código, tests,
`VERSION.yaml`, `AGENTS.md`, `.cursorrules`, `.agents/**`, hooks, configuración, `sync_versions.py`,
`build_lesson_index.py`, REGISTRY, red, QMind, pipeline, archivado, commit y push. Evidencia:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

| Fila §4.C | Qué quedó resuelto | Dónde |
|---|---|---|
| `CONTEXTO/C` | **Nada que renegociar.** E1–E5 se conservan y su forma se reconfirmó contra `scripts/decision_client.py` (la validación de `RespuestaEleccion` exige `confidence`; `RespuestaNoul` la fija en `None` y la puerta rechaza que un `noul` la reporte). **AC15 semántico `NO-EJERCITADO` y D6 dormida** quedan admitidos explícitamente en la fila D6 de arriba | contrato §Enmiendas + este archivo |
| `CONTEXTO/D` | **Carga total** con tres sumandos (`workflow_obligatorio`, `coste_de_generacion`, `pack_consumido`) y resta entre totales: concatenar no es ahorrar. **Frescura por sha de las fuentes relevantes; HEAD es procedencia, no llave de caducidad** (corta la invalidación circular por el commit del generado). **Regeneración del pack tras el traslado antes de verificarlo** y AC19 obliga a resolver rutas archivadas. **D acepta el resultado no medido de C** | contrato §Carga total y frescura del pack, §Cierres item 8, maestro AC19/AC20/AC21, prompt FASE-D |
| `CONTEXTO/RELEASE` | **Cuatro permisos, no tres** ⟦rectificado 2026-09-25; la etiqueta «tres momentos» sigue siendo el título-history del bloque por sus cinco referencias vivas⟧: **C0 destinos escribibles** (offline = sin red, **no** permiso de escritura: `sync_versions.py` sin `--check` puede reescribir `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md` según `sync_config.yaml`; `VERSION.yaml` es entrada y REGISTRY + `.last_doc_phase.json` salen del escritor del registro) · **cierre offline verificado** · **remoto** (D8 y D9, cada uno con autorización literal y presupuesto) · **traslado**. Se separa el mandato de la fase de esos permisos, con `PENDIENTE-AUTORIZACION` en vez de omisión. **Leer el estado ≠ reparar**: correr `validate_governance_numbers.py` es verificación y la reparación de `.agents/` no vuelve a hacerse aquí. **Sin writers automáticos**: `--fix` y `--update-baseline` salieron de la secuencia; los checks no escriben y ningún baseline se actualiza para absorber errores. **El `--check` posterior al traslado se apoya en una regeneración prevista**, y un rojo de un derivado no autoriza editar código. **D2 no se da por satisfecho** por las enmiendas de `REFACTOR-WHATSAPP` | contrato §Dos momentos del cierre y §Orden del cierre, prompt FASE-RELEASE |

**Qué este bloque NO tocó y por qué.** No ejecutó el piloto FASE-C ni ninguna fase; no activó D6 ni D7;
no movió `VERSION.yaml` ni las versiones documentales de `04-`/`06-`; no escribió en `AGENTS.md`,
`.agents/**`, hooks, `REGISTRY.md` ni su tracker auxiliar; no regeneró DOMAIN_PRIMER; no tocó la
evidencia histórica de FASE-A/B ni los prompts de fases cerradas. La **incompatibilidad declarada** que
queda fuera de su alcance: `AGENTS.md` (§Vinculo con la Documentación) sigue condensando DOMAIN_PRIMER
en «se regenera en FASE-RELEASE» y `docs/CONTRIBUTING.md` titula «Regenerar» a su Paso 5b mientras la
fila de su tabla dice «Se VERIFICA»; son documentos centrales que la fila `WHATSAPP` resuelve **para el
plan** (regenerar al cerrar cada fase, verificar en RELEASE), pero alinearlos a ellos exige instrucción
expresa aparte y no se hizo por arrastre.

## Rutas ajenas en el árbol al commitear FASE-B (medido, no supuesto)

Al cerrar FASE-B (2026-09-21) había **tres rutas ajenas** en el árbol. Al abrir su tramo de commit
quedaba **una**: `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`, que el
commit de esta fase **deja fuera** y sobre la que no se hace `git checkout` (es trabajo en curso de otra
sesión, no basura que limpiar; precedente: FASE-A excluyó a propósito sus dos rutas ajenas).

Las otras dos —`ROADMAP.md` y `.opencode/context/Refuerzo.md`— se las llevó la otra sesión en `eecf246`,
que ese día era el HEAD del repo y estaba **sin empujar** (`git rev-list --left-right --count
origin/master...HEAD` → `0/1`). Consecuencia declarada: **el commit de FASE-B se apoyaba sobre un commit
ajeno todavía no publicado** — y el push del mismo 2026-09-22 lo publicó con los cuatro de esta fase,
como queda escrito debajo, y el HEAD sobre el que esta fase midió su par pre/post (`74d8ff5`) ya no es
el HEAD. Las restas no se mueven —los cuatro archivos gobernados por AC16/AC17 no están en ninguno de los
dos commits y su `git diff --numstat` sigue vacío—, pero la premisa «el árbol de partida es solo mío»
queda refutada y así queda escrita (medición A6 del maestro, cumplida sobre esta propia fase). Detalle con
comandos y mtimes en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/baseline-pre-post.md`
§Rutas ajenas.

**Cerrado el 2026-09-22.** El commit de FASE-B está hecho — **`647f436`** (46 archivos, +4.412/−97), con
instrucción literal del operador y con el par del índice de lecciones dentro, así que `[6/7]` del hook no
lo cortó y los **7** checks pasaron. Dos consecuencias re-medidas para quien abra FASE-C: la paridad con
`origin/master` era **`0/2`** al cerrarlo, **`0/3`** tras su propio barrido de citas (`612efd0`) y
**`0/5`** tras el micro-barrido (`cf64faf`) — cada commit documental suma uno, así que la cifra se re-mide
y no se copia—; y **el push se hizo el 2026-09-22 con instrucción literal del operador**, que publicó
`74d8ff5..b764e8d` —los cinco commits, incluido el ajeno `eecf246` que era su ancestro obligado— y dejó
paridad **`0/0`** medida tras `git fetch`; y el propio commit movió el denominador que la fase había publicado — **678 → 691** `.py`
rastreados —, con lo que la resta de AC6 quedó rectificada con su nota y su residuo de un archivo
(`.venv-wsl/bin/activate_this.py`, exclusión no declarada) registrado como **S11** con su lección
**L-VCF-11**. Y el re-muestreo que hizo falta para medir esa rectificación **pisó la evidencia cerrada de
FASE-A**: `validate_governance_numbers.py --report` tiene su destino hardcodeado en
`evidence/…/FASE-A/informe.json`, así que el comando canónico del plan re-escribe el registro de otra
fase en cada corrida. Se revirtió (`git checkout --` sobre ese archivo) y se re-muestreó con destino
explícito, que da el mismo `HALLAZGOS` (A1–A4, 24 instancias, `exit 1`) sin tocarlo → **S12** /
**L-VCF-12**, con su guarda publicada en el README para quien abra FASE-C.

## Conciliación con la remediación del bloque A — aceptación de S11 y S12 (2026-09-23)

**Qué se acepta y de dónde viene (procedencia, no atribución a esta sesión).** Las dos deudas
nacidas del commit de FASE-B fueron corregidas **fuera de este plan**, por las cuatro sesiones
autorizadas del **bloque A** de `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, y el
código corregido entró al repo en **`fdd397f`** sobre la superficie
`scripts/decision_client.py`, `scripts/validate_governance_numbers.py`,
`tests/quality_gates/decision_client/` y `tests/quality_gates/governance_numbers/`. El resumen de esa
remediación (`evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/00-resumen-bloque-A.md` §4) dice de sí misma,
y se cita literal por ser el límite que esta fila respeta: **«lo aplicado es CORRECCIÓN TÉCNICA, no
cierre contractual»**, porque el traslado de S11/S12 a ese bloque exigía la enmienda registrada **en
este plan**, que era el pendiente. **Ese pendiente es lo que esta sección cierra**: el plan propietario
CONTEXTO acepta la remediación y registra el traslado. El mérito técnico es de esas sesiones y de `fdd397f`;
esta sesión **no** editó código ni tests.

**Alcance de lo aceptado** — solo S11 y S12, y solo en lo que el bloque A hizo:

| Deuda | Cura aceptada (en `fdd397f`) | Re-validación offline medida el 2026-09-23 |
|---|---|---|
| **S11** — `.venv-wsl` faltaba en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION` y las exclusiones se solapan | La exclusión entra en la lista **y su conteo se publica**; dos pruebas de población sobre árbol plantado; el escaneo se comparte entre aserciones del mismo árbol | `python scripts/decision_client.py --scan-imports` → `SIN-HALLAZGOS`, **0** imports prohibidos, `exit 0`; población escaneada **696** vs `git ls-files '*.py'` = **696** → **residuo 0** (la resta que en B cerró en 692−691 ya no existe); `.venv-wsl` figura en `excluidos_por_directorio` con **582** archivos |
| **S12** — `--report` sin destino re-escribía `evidence/…/FASE-A/informe.json` | El destino por defecto desaparece de los dos verificadores: `--report` a secas **imprime y no escribe**; el aviso va a stderr y el stdout queda JSON puro; **seis** tests nuevos en `tests/quality_gates/governance_numbers/` ⟦rectificado el 2026-09-23: esta fila decía «cinco»; corridos por nombre dan **6 funciones / 6 casos** en `test_governance_numbers_s12_report_no_escribe.py`, y el directorio completo **35 funciones / 40 casos**, `40 passed` con `EXIT=0`⟧ | `python scripts/validate_governance_numbers.py --report` sin destino → **`exit 1`** con `status: HALLAZGOS` y `assertion_ids = [A1,A2,A3,A4]`; `sha256` de `evidence/…/FASE-A/informe.json` **idéntico** antes y después de la corrida; `git status --porcelain evidence/` **vacío** |

**Los tres momentos van separados, y así quedan:** (1) **cierre original de FASE-B** — `647f436`
(2026-09-22), que cerró AC6–AC9 y **produjo** S11/S12 al mover el denominador y al re-muestrear;
(2) **corrección posterior** — `fdd397f` (2026-09-22), bloque A de la orden, técnica y probada por su
dueño; (3) **aceptación** — esta sección, 2026-09-23, que además re-mide offline. Ninguna de las tres
se atribuye a las otras dos.

**Qué NO cerró aquella aceptación (antecedente fechado).** El rojo contractual A1–A4 seguía vivo:
`validate_governance_numbers.py` salía `exit 1` porque aquella sesión no editaba `.agents/` (AC17,
D1/S1); la remediación del bloque A no lo tocó. Después B recibió autorización de corrección, pero
su estado vigente remite a la **matriz §13** de la fuente única, no a ese rojo ni a verdes retirados.
Y siguen abiertas, con dueño, **sin** convertirse en bloqueantes artificiales de una
FASE-C offline: **S10** (dónde vivirá el `import` del SDK cuando D7 se active), **D7** (activar el
proveedor) y **D6** (lint semántico, **dormida** porque su disparador es el `acceptance` de AC15).

**AC9 queda declarado con su alcance real** (no solo su cifra): certifica **extensión local** —
registrar un proveedor **falso** del repo a través de la costura, sin red ni credenciales, medido por
sha256 (`files_changed_to_add_provider = 1`, re-medido el 2026-09-23 con `--costura`, `exit 0`). **No**
certifica el coste total de integrar un **SDK real** en un archivo: dependencias y autenticación no se
midieron ni pueden medirse bajo la regla de cero red. El propio `--costura` ya imprime esa acotación
en su clave `alcance_de_ac9`, y la ubicación futura de ese SDK es **S10**/D7, coordinada con el plan
hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`.

**Instrumentos reutilizados, no nuevos.** Esta conciliación no añadió instrumentación: corrieron los
existentes de B (`--scan-imports`, `--costura`, `--provider-status`) y de A (`--report`), más la
selección `tests/quality_gates/decision_client` (**87 passed**, `exit 0`). **No se repitió la suite
completa por rutina**: su estado vigente es el que publicó la sesión 4 del bloque A, y lo que aquí se
ejecutó es la selección pertinente, distinguible de los resultados históricos de B. Crudos, comandos y
códigos en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/`.

### S16 — la convención que parsea el generador no está escrita en ninguna fuente (nueva, 2026-09-24)

**Hecho medido al cerrar FASE-D**: `build_phase_briefing.py` extrae la lista de lectura del prompt
desde la cadena `Lee …` dentro de un bloque fenced de «Prompt de ejecución». Sobre el corpus
completo: **121** prompts de fase bajo `.opencode/plans/Archives/` y **0** la usan; **5** prompts la
usan en todo el repo y son los cinco de este plan. Consecuencia directa y probada: el pack de un
plan archivado sale `SIN-DECLARACION` y su `--check` imprime `SIN-FUENTES` — el corte del
generador, no su defecto.

- **Dueño**: `.agents/workflows/templates/prompt-fase-template.md`, sección 8 (Prompt de Ejecución),
  y por arrastre los prompts de los planes vivos. **No es de FASE-D**: escribir en `.agents/` es
  AC17 y esa superficie es D1/con instrucción literal del operador.
- **Disparador**: la próxima vez que un mandato autorice tocar el template (precedente: el bloque B
  de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` autorizó `lecciones-capitalizadas-template.md` para
  retirar A4). Ahí se añade la forma canónica de la lista de lectura, y FASE-RELEASE de este plan
  **no** la reescribe.
- **Por qué se registra y no se calla**: sin esta fila, un lector de 2026-12 verá packs vacíos para
  los planes archivados y concluirá que el generador está roto. L-R.4: una regla de proceso sin
  verificador es publicable solo si la regla lo declara — y aquí lo declara el propio pack.
- **Alternativa descartada**: hacer que el generador adivine la lectura por heurística de rutas
  (`*.md` citados en el prompt). Convertiría `SECCION-NO-RESUELTA` en una invención silenciosa, que
  es la familia de defecto que L-PF6/L-PF10 trajeron a este plan.

### S17 — los writers de texto reescriben en CRLF archivos que git almacena en LF (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: la escritura final de `SyncEngine.sync_rule` en
`scripts/sync_versions.py` y la de `run_regenerate_domain_primer` en `scripts/doctor.py` cierran con
`write_text(..., encoding="utf-8")` **sin** `newline="\n"`. En Windows eso re-escribe en CRLF un
archivo que git almacena en `i/lf`. Medido en la corrida: **6** archivos quedaron
`[FAIL] Line endings` tras el sync y la regeneración (lo cortó el detector de finales de línea que el
bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` añadió a `validate_document_integration.py`), y
el expediente `FASE-RELEASE/12-normalizacion-lf.txt` registra la normalización byte a byte con
`git diff -U0` comprobando que el delta seguía siendo solo tokens de versión/fecha/codename. El
antecedente de la cura correcta vive en el propio repo: `scripts/log_phase_completion.py` pasa
`newline="\n"` y lo documenta junto a la escritura.

- **Dueño**: `scripts/sync_versions.py` y `scripts/doctor.py`. Es edición de `scripts/`, **no** de este
  plan ni de la orden: FASE-RELEASE tiene prohibido modificar código, y ese fue el motivo exacto por el
  que aquí se declaró el defecto en lugar de curarlo.
- **Disparador**: el próximo mandato que autorice literalmente editar esos dos writers. La cura es el
  parámetro en la escritura, no la normalización posterior del árbol.
- **Remedio vigente (provisional y declarado)**: normalizar por bytes al cerrar. No es la cura — deja el
  defecto en el escritor, que es la regla que este plan ya aplica a los datos: *un dato con escritor se
  arregla en el escritor o con un verificador, no con un tercero que lo reescriba a mano*.
- **Alternativa descartada**: fixedear los finales de línea en cada llamada desde los dos cierres del
  RELEASE sin tocar el writer (sería el mismo remiendo en dos sitios más) y reconfigurar `text`/`eol`
  de git: eso cambiaría el árbol de trabajo de archivos ajenos a este plan para tapar un defecto local.

**⟦CURADA el 2026-09-25 en una sesión aparte, con mandato de código del operador⟧.** El disparador de
arriba se cumplió ese mismo día: se autorizó editar `scripts/sync_versions.py` y `scripts/doctor.py` más
sus tests. Estado de la cura:

- **Tres escrituras**, no dos. Al curar apareció una tercera de la misma familia en el mismo archivo:
  `run_status` escribe `.agent/SYSTEM_STATUS.md`, y estaba dejando el árbol en `w/crlf` contra su propio
  `i/lf` (medido con `git ls-files --eol` antes de tocar nada). Las tres llevan ahora `newline="\n"`:
  `SyncEngine.sync_rule`, `run_regenerate_domain_primer` y `run_status`.
- **Prueba por comportamiento, no por parámetro**: `tests/test_sync_writers_lf_y_fecha_readme.py` corre
  los **escritores reales** sobre repositorios temporales y afirma sobre los bytes emitidos. Su control
  negativo ejecuta la versión **commiteada** de cada script (`git show HEAD:…`, sin `checkout` ni
  `stash`): el viejo escribe CRLF y el nuevo LF en el mismo entorno, así que la diferencia es
  atribuible al parámetro y no a la máquina.
- **Límite declarado**: la traducción `\n` → `\r\n` es propiedad del SO. La prueba **mide** si este SO
  traduce (`_traduce_a_crlf()`) y, donde no traduzca, las tres comprobaciones de bytes se saltan con
  motivo en vez de dar un verde que no observó nada. Las de S18 son portables.
- Con la cura hecha, el `--check` del sync volvió a `All files in sync` y la normalización manual por
  bytes del cierre de RELEASE (`12-normalizacion-lf.txt`) queda como antecedente: el próximo cierre no
  la necesita. No se re-escribió ese expediente cerrado (**S12**).

### S18 — `readme_version_header` no goberna la fecha legible de `README.md` (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: después del sync de cinco cabeceras, la línea de estado de
`README.md` seguía diciendo `Actualizado 11 Septiembre 2026` con `release_date: 2026-09-25` ya en la
fuente única. La regla `readme_version_header` de `scripts/sync_config.yaml` tiene patrón para el token
de versión pero no para esa etiqueta de fecha; la regla hermana `guia_tecnica_header` sí la goberna, y
`docs/GUIA_TECNICA.md` movió su fecha en la misma corrida.

- **Corte de cobertura declarado, no deducido**: el quick `[3/11] Version Sync` dio **PASS** con el
  README desfasado, así que la comprobación vigente no mira esa etiqueta. El rojo solo lo ve un lector
  humano — que es lo que lo encontró — y por eso se registra con deuda en vez de con un verde.
- **Dueño**: `scripts/sync_config.yaml` y el lector de esa regla en `scripts/sync_versions.py`.
- **Disparador**: el próximo mandato que autorice editar el config de sync o sus patrones de header; o
  la próxima release, si se quiere que la fecha del README salga por su escritor.
- **Alternativa descartada**: editar esa línea del README a mano. Crearía un segundo escritor sobre un
  dato que ya tiene uno — la familia exacta de la que `scripts/sync_config.yaml` retiró la regla
  `registry_last_update` el 2026-09-23.

**⟦CURADA el 2026-09-25, en la misma sesión que S17 y con el mismo mandato de código⟧.**

- El patrón llega ahora hasta la fecha (`… | Actualizado[^\n|]*`) y el template emite `{date_text}`, la
  forma larga que `_interpolate` ya sabía producir: «25 Septiembre 2026». **No** entra un ISO en la
  cabecera — hay prueba que lo prohíbe, porque cambiar el formato que el documento mostraba no era lo
  que pedía la deuda. `[^\n|]*` no cruza la línea ni el separador, así que no alcanza otras menciones
  de «Actualizado» (hay una línea de contexto con esa palabra como señuelo en la prueba).
- El corte de cobertura quedó cerrado en el árbol real, y se midió antes de celebrarlo: con la regla
  vigente, el `--check` del sync pasó de `IN_SYNC` a **`FAIL: README.md (readme_version_header) - needs
  update`** sobre el README que dejó la release. Ese rojo es la detección funcionando, no una regresión.
- Escribir `README.md` es destino central y no estaba en el mandato de código: se pidió y se autorizó
  aparte (`python scripts/sync_versions.py --rule readme_version_header`, 2026-09-25). Delta real: la
  **línea 5** (fecha). `git diff --numstat` contra `HEAD` marca 2/2 porque la cabecera de versión ya
  la movió la release; la separación se comprobó con `git diff -U0` y con huellas antes/después en
  `evidence/…/CIERRE-ORDEN-2026-09-25/07-guard-idempotencia-sync.txt`, donde una segunda corrida del
  mismo comando no mueve **ninguna** de las diez rutas vigiladas.
- El espejo de prueba allana **las dos** líneas que goberna la regla: con solo la cabecera allanada, el
  `FAIL` llegaba por la segunda sustitución y no por la fecha. Medido, y por eso está escrito.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` · sha256 `a38da8ea12a6a54ef5598925e54e6132881306439236419c6b597d2dd4696723` · 56768 bytes copiados de 56768 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `10-analisis-post-implementacion.md` (documento completo)

# Análisis Post-Implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Se crea **desde la concepción** del plan, no al final. Cada fase actualiza su fila, sus lecciones,
> sus referencias a métricas de `09-documentacion-post-proyecto.md` §D y sus seguimientos al cerrar.
> FASE-RELEASE consolida la matriz; aquí se analiza el delta sin transcribir cifras.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está concluido
contractualmente por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24 solo
como enmiendas prospectivas sobre los documentos de los cuatro planes; **el piloto FASE-C no lo está**.
Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Los dictámenes anteriores de D1/S13 se conservan debajo como antecedentes retirados. Las mediciones
fechadas de FASE-A/B no certifican el árbol actual; D3 es parcial, dueño **«Plan propio, posterior»**.

## Resumen de Ejecución

| Fase | Estado | Iteraciones medidas (unidad e instrumento) | Cortes autorizados | Notas |
|---|---|---|---|---|
| FASE-A | **VERIFICADO OFFLINE 2026-09-21** (AC1–AC5; AC16/AC17/AC18 en su parte de A) | Instrumento canónico **no corrió**: `find . -name "*.jsonl"` = 0 en el workspace (condición D-V2.1, re-medida el 2026-09-21). Se retira la métrica de iteraciones y se publica en unidad contable en disco: **14 rutas propias** en el árbol de trabajo, 933 líneas de instrumento, 23 funciones de test / 28 casos. **No comparable** con auto-reportes en `tool_use` de otros planes | Ninguno: la fase cerró su presupuesto documental y sus 3 tareas de código en la sesión (R3 permitía 4) | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/`: `informe.json`, `baseline-pre-post.md`, `ac17-y-presupuesto.md`, `mutation/` (verde + 6 rojos), par pre/post y las dos corridas del quick. **Commiteado el 2026-09-21 en `a7564ae`** con el par del índice de lecciones dentro (`[6/7]`) y con los dos archivos ajenos a la fase excluidos a propósito (instrucción literal del operador para el commit y, en una instrucción separada del mismo día, para el push: `a7564ae` y su barrido `e3c4573` ya están en `origin/master`, con el escaneo L3 ofrecido y saltado por el operador) |
| FASE-B | **VERIFICADO OFFLINE 2026-09-21** (AC6–AC9; AC16/AC17/AC18 en su parte de B) | Instrumento canónico **volvió a no correr**: `find . -name "*.jsonl"` = **0** en el workspace, medido hoy (precondición de D-V2.1). La métrica se **retira**, no se estima: no se publica un `tool_use` aproximado, porque contar bloques desde dentro de la sesión no es medible sin el transcript que falta. Unidad contable en disco, declarada no comparable: **11** archivos de código/tests (1 puerta + 2 proveedores falsos + 6 de tests + `conftest.py` + `__init__.py`) y **25** de evidencia (10 de ellos en `mutation/`, 2 en `instrumentos/`), ambos contados con su comando en `baseline-pre-post.md`, no estimados | Ninguno: 3 tareas de código y **0** comandos de larga duración (R3) | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/`: `informe.json`, `import_scanner.txt`, `contract.txt` (verde `exit 0` + rojo `exit 1`), `costura.json`, `extensibilidad.txt`, `cero-red.txt`, `run_tests.txt` (53 casos), `baseline-pre-post.md` con la resta y `mutation/` (verde + 9 mutantes). **Commiteada el 2026-09-22 en `647f436`** (46 archivos, +4.412/−97) con instrucción literal del operador y con el par del índice **dentro**; los **7** checks del pre-commit pasaron. Dos cosas quedan declaradas y no cerradas: la ruta ajena `EVALUACION-JEV/dependencias-fases.md` **excluida** a propósito del commit, y el **push hecho el 2026-09-22** por instrucción literal: `74d8ff5..b764e8d`, cinco commits publicados —los cuatro de esta fase más el ajeno `eecf246`, que es su ancestro obligado— y paridad `0/0` re-medida tras `git fetch` (los antecedentes de paridad del día: `0/2` al commitear la fase, `0/3` tras `612efd0`, `0/5` tras `cf64faf`: cada commit documental suma uno, así que se re-mide) |
| FASE-C | **VERIFICADO OFFLINE 2026-09-24 en su mecánica** (AC10–AC14 y AC15 en su parte no semántica; AC15 ⚠️ con `acceptance = NO-EJERCITADO` por contrato E4; AC16/AC17/AC18 en su parte de C) | Instrumento canónico **volvió a no correr**: `find . -name "*.jsonl" -not -path "./venv/*"` = **0** al abrir, medido con el comando que publica el README (séptima reproducción de la precondición de **D-V2.1**). La métrica se retira, no se estima: se publica **auto-reporte con unidad declarada** — `tool_use` con ids únicos, contados a mano sobre la sesión, **no comparable** con las tres horas de FASE-B ni con ninguna otra unidad. La cuenta y su método viven en `evidence/…/FASE-C/baseline-pre-post.md` §Presupuesto | **Hasta listo para revisión** (declarado por el operador): la fase llegó al corte y **se paró ahí**. **`git push` hecho el 2026-09-24** con instrucción literal del operador (`da382b1..5817edd`, paridad **0/0** re-verificada tras `git fetch`); los cinco cortes del proceso común se sostienen sin commitear y se verificaron antes de cualquier acción sobre el remoto. **El `git commit` se hizo el 2026-09-24 con instrucción literal del operador**: `7f2e9f9` (helper de BLOQUE-B por dependencia técnica) + `5817edd` (las 37 rutas propias, 7/7 del hook), dejando **fuera** documentos, par de índice y `REGISTRY` (ver **L-VCF-15**, que es la consecuencia medida de ese recorte) | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/`: `informe.json`, `ac10_delta.json`, `coverage.json`, `r26.txt` (el test contra corpus real **corrió**, no se saltó), `mutation/` (verde 14→14 y rojo 14→3 con su `resumen.txt` y el alcance del observador), `run_tests.txt` (56 casos), `regression_calidad.txt` (854 passed / 1 failed **preexistente y atribuido**), `cero-red.txt` (con el desglose del residuo de poblaciones), `no-piso-pasado_ANTES/DESPUES.txt` (expediente de FASE-A intacto por sha + mtime + tamaño y por escrituras observadas), el par `faseC_baseline_pre/post` y `baseline-pre-post.md` con la resta. Dos desviaciones **registradas con su medición, no aplicadas en silencio**: el corpus real de AC13 es `.opencode/plans/Archives/` (no `Archives/` a secas) y el proveedor falso solo existe bajo `tests/quality_gates/lesson_relevance/` montado por entorno. **No cerró** la orden de calidad §6, ni D6/D7/S10, ni FASE-D ni RELEASE |
| FASE-D | **VERIFICADO OFFLINE 2026-09-24** (AC19–AC23; AC16/AC17/AC18 en su parte de D) | Instrumento canónico **volvió a no correr**: `find . -name "*.jsonl" -not -path "./venv/*"` = **0** al abrir (octava reproducción de la precondición de **D-V2.1**). Ni se estima ni se inventa: se publica **auto-reporte con unidad declarada** (`tool_use` con ids únicos, contados sobre la sesión) y se declara no comparable con ninguna otra unidad. La cuenta y su método viven en `evidence/…/FASE-D/baseline-pre-post.md` §Presupuesto | **Hasta listo para revisión**: los cinco cortes se sostienen sin commitear y se verificaron sobre el árbol de trabajo. **Sin `git commit` y sin `git push`** —ninguno fue autorizado en esta sesión—, con la deuda documental declarada en `dependencias-fases.md` | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/`: `informe.json` (5 packs: 4 `COMPLETO` + 1 `SECCION-NO-RESUELTA`, 23/23 secciones resueltas, 0 `FUENTE-AUSENTE`), `carga.json` (tres sumandos por lado, `resta_comprobada: true` en las cinco fases), `carga-pre-post.md` con las cinco identidades de la resta, `cero-red.txt`, `r26.txt`, `run_tests.txt` (49 funciones / 49 casos), `regression_calidad.txt`, `mutation/` (verde y rojo del mismo pack, separados por la declaración que el mutante borra, cuyo tamaño publican los dos json), el par `faseD_baseline_pre/post` y `test_count_pre_post.txt`. **AC20 no cierra en el número que esperaba el plan**: el delta es de orden del **12 %** de la carga total, **no** «un tercio» —y la causa es que el workflow canónico sigue en ambos lados, que es lo que D3 prohíbe tocar. (El valor exacto no se transcribe aquí por A6 sobre un artefacto derivado: **este documento entra en el pack de FASE-RELEASE que ese comando mide**, así que copiar la cifra la vence; la imprimen `carga.json` y `carga-pre-post.md` con su `stat -c %s`.) Dos cosas se registran con su medición y no se esconden: **0 de 121** prompts archivados declaran su lectura con la convención que el generador parsea (**S16**), y los packs generados **re-vencen el índice de lecciones** porque son corpus nuevo en el directorio del plan (**L-VCF-17**). **No cerró** D6 ni D7/S10, ni la orden de calidad §6, ni FASE-RELEASE |
| FASE-RELEASE | PENDIENTE | — | — | — |

**FASE-VERIFY no aplica** (criterio 2 de §4.6 cae: no existe fase con ejecución E2E, y este plan tiene
prohibida la pipeline). Por tanto ningún AC de este plan puede alcanzar `SUPERADO EN E2E`.
⟦Precisión del bloque C, 2026-09-24⟧: la razón que se añadía antes —«además este plan no hace llamadas
de red»— era excesiva como frase global y contradecía el propio cierre: FASE-RELEASE contiene dos
operaciones remotas (D8 y D9). Lo vigente es lo que dice el contrato (§Regla de cero red y §Dos momentos
del cierre): **cero red en las cuatro fases de implementación**, y en RELEASE lo remoto es un momento
aparte con autorización y presupuesto propios.

## Matriz de Verificación de Hallazgos

| Hallazgo | Medición que lo sostiene | Qué lo previene ahora | ¿Verificable en el artefacto? |
|---|---|---|---|
| A1 — el workflow afirma que `validate_plan_citations.py` es el check 8 del quick | El método `def _check_plan_citations` imprime `[9/11]` | `validate_governance_numbers.py` (FASE-A) | Sí — `findings[]` |
| A2 — el workflow afirma `[9/9]` para la capitalización | `def _check_lesson_capitalization` imprime `[10/11]` | ídem | Sí |
| A3 — el workflow afirma `[12/12]` en el modo completo | **Rectificada el 2026-09-20**: la etiqueta real del write-back es `[15/15]` (la imprime `def _check_qmind_writeback`). La primera versión de esta fila decía `[12/15]`, que es la etiqueta de `def _check_dependencies` — el total (15) sí era correcto y el emisor no | ídem | Sí — y es el ejemplo vivo de por qué AC1 exige emparejar etiqueta ↔ método |
| A4 — el template de lecciones afirma `[10/10]` | La etiqueta real es `[10/11]`; su `[7/7]` del hook **sí** coincide | ídem | Sí |
| A5 — un grep de término devuelve 0 sobre un corpus que sí contiene lo buscado con otras palabras | `grep -icE "verificador mec"` devolvió 0 al concebir el plan | `triage_lesson_relevance.py` publica términos y ceros (AC15) | Sí — `coverage.json` |
| A6 — **las cifras del propio plan vencieron al crearse el plan**: decía 14 análisis / 49 IDs sin definición / 389 `.md` y el índice regenerado pasó a 15 / 50 / 401 | `build_lesson_index.py` contra `head -18 .opencode/LECCIONES-INDEX.md`, medido el 2026-09-20 al verificar este plan | Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha** y se re-mide al cerrar la fase; no se le cree a la salida de otro verificador | Sí — `00-…` Q4 y maestro §1 |
| A7 — una sesión de fase declara **263.973 bytes ≈ 65.993 tokens** de lectura antes de tocar código, en ocho lecturas, contra un presupuesto de 60 `tool_use` | `stat -c %s` sobre los **siete** documentos que suma la tabla (el octavo que declara leer la fase es un archivo de `evidence/` excluido de la suma), re-medido el 2026-09-20; al concebir dio 254.010 y creció +9.963 con los cierres del propio plan medido; tokens estimados por divisor 4 | `build_phase_briefing.py` (FASE-D) unifica las lecturas declaradas en un pack derivado; **AC20 mide el delta y lo publica aunque sea cero** | Sí — `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` |
| A8 — la población bajo el patrón de conteo es mayor que las cuatro aserciones: **22 instancias `[N/M]` en 17 líneas** más 2 formas «check N» en los documentos de gobierno | `grep -rnoE '\[[0-9]+/[0-9]+\]' .agents/` y `grep -rnoE 'check [0-9]+' .agents/`, medido el 2026-09-20; el propio workflow declara en su entrada `v2.24.0` que cuatro de esas menciones son históricas y «se conservan literales» | AC1 con regla de población (viva / histórica congelada publicada / vigente-correcta) y `findings[]` por aserción con `occurrences[]` | Sí — `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]`, `historical_excluded[]` |

**Lo que A7 no afirma.** No dice que la lentitud sea solo de tokens: la cadena del otro plan es de
doce fases secuenciales de una sesión y cada fase re-mide once validaciones. Nada de eso lo toca este
plan, y decirlo aquí es parte del cierre honesto.

## Lecciones Aprendidas

Sin cuota: «sin lecciones nuevas» es un resultado declarado, no un fracaso que rellenar (el ≥3
descartes de §3 mide consulta al corpus, no producción de lecciones). Formato: **qué pasó / por qué / qué lo previene** +
pertinencia **INCLUIR** o **EXCLUIR** para el siguiente plan.

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

**Catorce filas** capitalizadas: once al concebir (L-R.1, L-R.3, L-R.4, L-NC10, L-PF6, L-PF10, L-D3,
L-V2.3, L-T4A.5, L-VUP-5, L-HF1) más tres que aportó la **capa tibia consultada en la auditoría del
2026-09-20** (L-V2.1, L-V2.2, D-V2.1), sobre **6 dueños distintos** con su efecto concreto nombrado en
la columna «Qué cambia» del propio §2 — no aquí. *(Doble corrección del 2026-09-20: la fila publicaba
**7** dueños cuando las once originales ya tenían **6**, y las tres nuevas no suman ninguno porque
`D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` — `TRIBUNAL-ENFORCEMENT-OBS`
es donde la **reproducen**, en cuatro fases seguidas. Lo detectó
`validate_lesson_capitalization.py` por `C7`, es decir: el verificador de forma del corpus cazó la
atribución vencida del documento de este propio plan, y el conteo se corrigió re-midiéndolo.)*

### Lecciones nuevas de este plan (L-VCF-1+)

Cerradas en FASE-A (2026-09-21). Cada una con su medición, no con su impresión.

| ID | Qué pasó | Por qué | Qué lo previene | Pertinencia para el siguiente plan |
|---|---|---|---|---|
| **L-VCF-1** | El primer mutation check **falló nombrando a otra aserción**: al apagar el guard de A1 el rojo reportó «se perdió A4» | `assertion_id` se asigna por orden de aparición (así reproduce la tabla A1–A4 del maestro sin pinearla). Es **posicional**: en cuanto un hallazgo desaparece, los demás se re-numeran, y el rojo pasa a hablar de un tercero | `findings[]` publica además `assertion_key` (sujeto + afirmación + documento), que es invariante; todo anclaje de mutante, contract test o diff entre corridas mira la clave, nunca el id. Los seis archivos de `mutation/` muestran las dos columnas | **INCLUIR** — es L-V2.1 en una variante nueva y barata: «el anclaje del mutante no puede ser un entero de posición». Le aplica a cualquier verificador que numere hallazgos |
| **L-VCF-2** | Resolver el sujeto de cada mención por «el script más cercano» produjo un **hallazgo fantasma**: dentro del changelog, un `[6/7]` que *nombra el token* («las 5 referencias normativas al `[6/6]` se actualizan a `[6/7]»`) se atribuyó al verificador de capitalización y dio claimed 6 vs observed 7 | Una instancia puede ser **mención de sí misma** (metarreferencia) en vez de atribución, y la distancia textual no las distingue | Regla de dos partes publicada en el script: (a) una afirmación «del hook» se contrasta **solo por forma** (sus N pasos), sin sujeto; (b) las congeladas salen por H1 (denominador de otra época dentro de `## Versiones`) o H2 (cláusula de evento pasado). Prueba: el mutante `M-POBLACION` — apagar la regla convierte las 8 congeladas en **4 hallazgos extra** | **INCLUIR** — sirve a cualquier lector que empareje texto con código por proximidad |
| **L-VCF-3** | Dos defectos de la **salida**, encontrados al escribir la prueba de estados y no al leer el codigo: (1) la primera linea de la consola no era ASCII —el guion largo de la cabecera llegaba al lector convertido en caracter de reemplazo—; (2) la marca corta esta contenida en la larga, asi que buscar el veredicto con una prueba de subcadena **tambien** es verdad cuando el veredicto es el contrario | La salida legible por maquinas es parte del contrato del instrumento, y la consola de este entorno no es UTF-8 (leccion ya capitalizada: «evidencia de consola no es UTF-8») | `_estado_a_imprimir()` deja la marca en ASCII fija; `test_marca_de_estado_en_ascii` exige `isascii()` y el estado exacto, y los archivos de estado comparan la **primera linea**, no un `in` sobre todo el stdout | **INCLUIR** — para todo verificador cuyo verde se consume por grep o por log |
| **L-VCF-4** | El disparador de **D1** estaba redactado en círculo: «verificador verde y decisión escrita» — pero el verificador solo está verde *después* de la corrección que D1 pide, y esta fase, por diseño (AC17), no puede dar ese verde | Una condición de cierre que solo se cumple al ejecutar lo que condiciona no es un disparador: es una traba | Disparador re-escrito en `dependencias-fases.md` y en la matriz de deuda: *verificador operativo con su mutation check en disco* (cumplido el 2026-09-21) **+** decisión escrita del operador | **INCLUIR** — releer los disparadores de deuda «contra el árbol de la fase que los ejecuta», no solo contra la concepción |
| **L-VCF-6** | El primer mutation check de AC7 apagaba `VERIFICACIONES_DE_FORMA` **entera**, y con la lista vacía la puerta **seguía negándose** a decidir: la conversión a tipos se negó a rellenar la `confidence` ausente. El mutante no podía dar verde, así que no probaba nada sobre los seis guards | Un guard que es una **lista** de verificaciones no es un símbolo mutable atómico: apagarla entera borra seis guards a la vez y, si hay una segunda línea defensiva, el rojo deja de atribuirse a ninguno (L-V2.1 aplicado a una colección, no a un id posicional) | El mutante se re-escribió **uno por guard** (seis vueltas parametrizadas), cada una con un payload que **solo ese guard** ve, y con la aserción `disparados == {guard}` antes de apagar: si el verde no aísla, el test lo dice. Los otros tres mutantes (`M-AC6-token`, `M-AC6-carga-dinamica`, `M-AC6-superficie`) apuntan a símbolos distintos y un test final verifica que no comparten símbolo y que los seis siguen existiendo | **INCLUIR** — para cualquier guard implementado como registro de verificaciones: la unidad de mutación es la entrada, no la colección |
| **L-VCF-7** | La primera versión de la regla de aislamiento marcaba **cualquier** `import_module`/`exec_module` como sospechoso: sobre el árbol real eso producía **16 hallazgos ajenos** (fixtures de otros planes, cargadores de skills) y AC6 habría quedado rojo por diseño | Una regla pensada para un contrabando concreto, aplicada sin distinguir lo resoluble en estático de lo que no, convierte un candado en ruido; y el ruido invita a apagar el candado | Clasificación en dos: carga con argumento **literal** prohibido → hallazgo en cualquier archivo; carga con argumento **no literal** → límite publicado (`cargas_dinamicas_no_resueltas`) que solo escala a hallazgo dentro de la superficie `*proveedores*`, donde sí tiene sentido. Los 16 siguen publicados, con su conteo y sin contar como violación | **INCLUIR** — «un detector que marca todo lo que se parece al delito también marca la prueba del delito»: medir cuántos falsos produce antes de darlo por cerrado |
| **L-VCF-8** | El «0» de AC6 tiene **dos poblaciones** y no eran la misma: `git grep` ve **678** `.py` rastreados y el escáner AST ve **692** en el árbol de trabajo (los archivos de esta fase, aún sin commitear — **rectificado el 2026-09-22**: tras el commit git ve **691** y la diferencia no era toda de la fase, ver **L-VCF-11**). Y el SDK **sí está en el disco**: bajo `tmp_test/venv-jev-sdk`, donde lo aisló el plan hermano | Un «cero coincidencias» afirmado sobre una población que nadie definió se lee como «no existe», cuando lo medido es «nadie lo importa» | `import_scanner.txt` publica las dos cifras con su comando, los excluidos **por directorio con su conteo** (`venv` 7.618, `site-packages` 8.889, `tmp_test` 690, `temp` 65, `build` 14) y la diferencia entre rastreado y árbol; la ausencia del SDK del venv del producto se mide con `find_spec`, no se infiere del grep | **INCLUIR** — antes de afirmar «no hay», medir sobre qué universo y declarar qué exclusiones sostienen el cero |
| **L-VCF-9** | Apareció una contradicción **entre dos ACs del propio plan**, latente hasta que exista un proveedor real: AC6 dice «ningún archivo fuera de `decision_client.py` importa el SDK» y AC9 dice «añadir un proveedor es **un** archivo». Con el proveedor en su propio módulo, la primera obliga a que ese módulo no importe nada y la segunda prohíbe tocar la puerta | Los dos enunciados son ciertos hoy (0 imports, 1 archivo) pero no son compatibles en el único escenario para el que se escribió la costura: D7. Decidirlo aquí habría sido **reinterpretar una restricción del plan en silencio** | No se reinterpretó: quedó escrito (esta fila, el docstring de la puerta y **S10** en Seguimientos) con las dos salidas y su coste — (a) la puerta posee el `import` y el archivo nuevo solo **declara** el módulo, o (b) re-anclar AC6 a «puerta + su directorio de proveedores», que es edición de plan, no de código | **INCLUIR** — un par de ACs que hoy cuadran puede dejar de cuadrar en el caso que justificó el diseño; se detecta escribiéndolo, no esperándolo |
| **L-VCF-10** | «Cero llamadas de red» escrito como afirmación del informe no era verificable, y el primer intento de probarlo con `from conftest import RedProhibida` falló en colección: resolvía al `tests/conftest.py` **raíz**, no al de esta selección (1 test rojo antes de la corrección) | Un guard que no se ejecuta no existe; y en pytest `conftest` no es un importable único bajo colecciones anidadas (es la familia de «la cobertura del verificador se mide»: un ✅ no prueba ausencia) | El guard se expone **por fixture** y hay dos pruebas: que `socket.socket()` bajo el fixture produce `RedProhibida`, y que la costura llega a `RESUELTO` **con el guard armado**. Más la denegatoria AST de 19 módulos capaces de hacer red y el `find_spec` del SDK en el venv. Las tres, en `cero-red.txt` | **INCLUIR** — toda prohibición de proceso necesita un instrumento que falle si se viola; si su prueba depende de un import, que lo resuelva un fixture |
| **L-VCF-11** | Al commitear FASE-B, la resta que la propia fase había publicado **dejó de cerrar por un archivo**: git pasó de 678 a **691** `.py` (+13, los de la fase) pero el escáner seguía en **692**, así que la explicación escrita en `baseline-pre-post.md` («la diferencia son los archivos de esta fase, que aún no están commiteados») quedó refutada por el commit que debía reconciliarla | El denominador se construye excluyendo por **nombre de componente de ruta**, y `.venv-wsl` no está en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION`: su `bin/activate_this.py` entra al universo. Y las exclusiones se **solapan** (`site-packages` está anidada dentro de `venv`/`tmp_test`, y el walker incrementa los dos marcadores por la misma ruta), de modo que la suma de las exclusiones no reproduce el universo y no sirve de comprobación aritmética | Descomponer la brecha entre dos poblaciones **archivo por archivo** (`comm` entre `git ls-files '*.py'` y el `rglob` con las mismas exclusiones) en lugar de atribuirla a la fase por defecto. El 0 de AC6 **no se mueve**, y se dice por medición (ese archivo no importa el SDK), no por suposición. Queda como **S11** con su disparador; no se arregló en el barrido porque editar la puerta obliga a re-ejecuciones de sus 53 casos y sus 9 mutantes | **INCLUIR** — dos poblaciones con cifras cercanas no son la misma población: la resta se desglosa o se publica como no desglosada |
| **L-VCF-12** | Al re-medir AC6/A1–A4 para escribir este barrido, `python scripts/validate_governance_numbers.py --report` **sobrescribió la evidencia commiteada de FASE-A**: la ruta de escritura está hardcodeada como default (`REPORT_DEFAULT` → `evidence/…/FASE-A/informe.json`) y el comando canónico que el propio plan publica no lleva destino. Cambió tres campos: `generated_at`, `medido_el` y `funciones_test_en_disk` (4.330 → **4.378**, que es una medición **verdadera** escrita sobre el registro de otra fase). Se revirtió con `git checkout -- <ese archivo>` y se re-midió con destino explícito (`--report temp/…`), que deja FASE-A limpia y da el mismo `HALLAZGOS` con `exit 1` | Un verificador que además es **writer** gobierna dos artefactos, y aquí el segundo es un registro fechado de otra sesión: cada corrida re-escribe el pasado. Es la familia de L-VCF-11 (el instrumento afectado por su propio uso) y la de «quién produce el dato publicado», en su variante peligrosa: **el verde se publica pisando una evidencia ajena** | Separar lector de writer: `--report` sin destino debe **imprimir y no escribir** (o exigir `--out` explícito), y la evidencia de cada fase se escribe con su ruta nombrada en el comando publicado. Registrado como **S12**; mientras tanto, todo re-muestreo de este verificador se hace con destino explícito y se declara | **INCLUIR** — antes de correr cualquier verificador del repo con `--report`/`--write`: mirar si su default toca evidencia commiteada |
| **L-VCF-5** | Al medir «quién afirma el 11» (AC5/AC16, barrido de `tests/` por L-V2.3) resultó que **esta misma fase añadió 4 pins nuevos del denominador 11** en `tests/`: la aserción `observed == 9/11` del contrato AC1 es, literalmente, un pin | Un test que fija el valor observado de una fuente dinámica *es* una de las fuentes estáticas que el plan denuncia; la familia no cubierta (iii) de AC2 no era teoría | Se declaró en `baseline-pre-post.md` con dueño (D1/D2: al corregir `.agents/` o renumerar el quick, el test se re-ancla con su nota datada) en lugar de debilitar la aserción para que la resta quedara limpia | **INCLUIR** — «medir a quién le duele la renumeración» incluye medirse a uno mismo |

| **L-VCF-13** | El primer diseño del triaje **no podía perder**: el pool de candidatos se construía excluyendo por definición las filas ya ancladas en §2, así que `removed: []` era cierto sobre un conjunto donde no existía nada que borrar, y el mutante de AC14 no tenía rojo que producir. Hubo que **re-preguntar también por las ancladas** (opción por defecto activa) para que el emisor falso dijera `no-pertinente` sobre **once** filas y el guard tuviera trabajo real | Un candado aditivo probado sobre el conjunto vacío es la variante silenciosa de L-HF1: el verde no miente sobre el presente, miente sobre la **cobertura de la prueba**. El bug al que sobrevive un guard no está en el camino feliz, está en el camino que el fixture nunca instancia | El test de AC10 **exige** `filas_cuestionadas_sin_borrar` no vacío como condición de su propio verde (si el emisor no cuestiona nada, el test falla en vez de pasar); AC14 publica el rojo correspondiente: apagado `GUARD_ADITIVIDAD_ACTIVO`, §2 pasa de **14 filas a 3**. Y el rojo **nombra** lo que desaparece (`removed == cuestionadas`), que es lo que hace atribuible el mutante (L-V2.1) | **INCLUIR** — para todo verificador de «no se pierde nada»: antes de dar crédito al `[]`, medir si había algo que perder en el insumo |
| **L-VCF-14** | El check de frescura propio de C reventó con `AttributeError: 'str' object has no attribute 'get'` sobre un JSON de prueba que **sí existía y sí se parseaba**, pero cuya clave `lecciones` no era lista. Es decir: el lector caído se reportaba como excepción del programa, no como estado del artefacto, justo en el instrumento cuya tesis es que un lector roto no se lee como ausencia | R2.9 nombra tres causas (no está / vencido / no se puede parsear) y deja una cuarta implícita: **parseable no es conforme**. Un `except` que solo cubre `JSONDecodeError` traduce un problema de forma a traceback, y un traceback no es un estado publicable | Validación de forma dentro del lector (`dict` y `lecciones` en lista) que devuelve `LECTOR-FALLIDO` con su motivo de forma, más una sub-causa separada para «el cálculo propio no pudo correr» —que tampoco es `AUSENTE` ni `VENCIDO`—. Prueba parametrizada con tres artefactos rotos distintos (no-JSON, binario, forma equivocada) y un caso que patchea el generador para que el cálculo caiga | **INCLUIR** — al implementar estados de lectura: enumerar también «el artefacto se lee y no es lo que dice ser», que es el que aparece cuando alguien escribe el JSON a mano |
| **L-VCF-15** | Al commitear **solo** las 37 rutas propias de FASE-C, `git archive HEAD` extraído a un árbol limpio dio **14 failed / 16 passed / 26 errors** en la suite de esta misma fase, todos con `SueloNoLeible: VENCIDO`. Dos controles fallaron antes de dar con la causa: copiar el par de índice del árbol de trabajo **no** lo arregló, y copiar además los documentos de los cuatro planes **tampoco**. Pasó a **56 passed** únicamente al regenerar el par *dentro* de ese árbol. El hook había dado **7/7 en verde** durante el commit | `[6/7] build_lesson_index.py --check` corre contra el **árbol de trabajo**, así que su verde describe el árbol que se dejó, no el commit que se escribió. Y el par generado no es reubicable: es función de todo el corpus de `.opencode/plans/` —incluidas las fuentes de planes ajenos que tampoco están commiteadas—, por lo que copiarlo de otro árbol produce un artefacto que no corresponde a ningún corpus de ese árbol | Verificar la autosuficiencia de un commit **en el árbol del commit** (`git archive HEAD \| tar -x -C <scratch>` y correr ahí), nunca con la suite del árbol de trabajo; y tratar el artefacto generado como parte del conjunto atómico que viaja con sus fuentes. Cuando las fuentes no pueden viajar, el recorte se declara con su cifra de hunks (164, de los que **59** nombran a la fase), que es lo que convierte el límite en conocido y no en rojo inesperado | **INCLUIR** — para toda fase cuyo contrato consume un artefacto generado: «verde en mi árbol» no es «verde en mi commit», y la diferencia solo se ve si se corre dentro del commit. ⟦**Rectificado el mismo día, antes de cerrar**⟧ la causa no es solo el corpus: **9 de las 335 entradas del par llevan `fuente_fecha = mtime`** y `git archive` no preserva mtimes, así que `[6/7]` declara `VENCIDO` en **cualquier** extracción limpia —medido sobre `da382b1` **y** sobre `5817edd`, los dos `EXIT=1`, con documentos idénticos y con el par del árbol copiado dentro—. Regenerar dentro del árbol lo pone verde porque **re-sella la fecha de hoy**, no porque el par sea transferible entre máquinas. De ahí **S15**, y de ahí que commitear documentos + par **no** cure un `[FAIL]` de índice visto en un clon ⟦**Vencida esta fila el 2026-09-26 por la cura de S15 y por la medición de su propia prueba; se conserva el texto original porque describía el árbol de aquel día.** (a) La cifra: lo medido al cerrar S15 es **11 de 339** entradas con `mtime`, no 9 de 335, y viven en dos planes del `Historico` (DT-2 nueve, DT-3 dos), etiquetados por stem. (b) El instrumento que esta fila receta en la columna 3 ya no sirve para ese contrato: con la cura puesta, `git archive HEAD` extraído a un directorio limpio da `[fechas] nombre=328 commit=0 sin_fuente=11` y `EXIT=1`, porque `_git_fecha` devuelve `None` ante un árbol sin repositorio (lo declara su propio docstring en `scripts/build_lesson_index.py`, método `_git_fecha`) — falla **por diseño**, no por vencimiento. El sustituto medido es un **clon**, que sí trae historial, con `git config core.longpaths true` dentro del clon. Y ahí apareció lo que el hook no ve: `911f8d7` puro falló su `--check` con `commit=11 sin_fuente=0`, o sea rojo de **frescura** y no de fecha, causado por la décimoctava cita de `L-VCF-17` en una ruta sin stagear; `2a675fa`, con 481 archivos de mtime posterior a todos los commits, dio `[OK] 339 IDs / nombre=328 commit=11 sin_fuente=0 / EXIT=0`. La lección de fondo sigue viva y sigue sin verificador que la corte: **verde en mi árbol no es verde en mi commit**, y `[6/7]` lee el árbol de trabajo. Evidencia en `evidence/…/CIERRE-ORDEN-2026-09-25/17-cierre-s15-y-baseline.txt` §6⟧ |

| **L-VCF-16** | El primer ancla del mutante de AC23 **no atribuyó**: apagado `GUARD_NO_TRUNCAMIENTO_ACTIVO`, el pack de FASE-RELEASE perdía el bloque de declaración pero la aserción `nombra_la_fuente_pedida` seguía en `True`, porque el texto que miraba —el nombre de la sección pedida— también está en los documentos del corpus que el pack **copia**. El rojo existía en bytes y era ciego en lectura | Un mutante hay que anclarlo al **texto que el generador produce**, no al texto que el generador **traslada**: en un artefacto derivado de un corpus, casi cualquier cadena del artefacto pertenece al corpus, y ahí el ancla no distingue «el programa escribió» de «el programa copió». Es L-V2.1 en un terreno nuevo —no «el id equivocado» ni «la lista entera», sino «la cadena no es del mutado»| El ancla se re-escribió con una marca exclusiva del generador: `MARCA in cuerpo and "titulos disponibles en el documento" in cuerpo`, donde la segunda cadena **no aparece en ninguna fuente** (la produce solo `_declarar_recorte`). El `resumen.txt` publica los dos tamaños y la diferencia, así que el rojo es reproducible sin leer el test | **INCLUIR** — para todo mutation check sobre un artefacto generado a partir de un corpus: verificar que la cadena asertada es **imposible de obtener por copia**; si no, el rojo es del generador solo de nombre |
| **L-VCF-17** | Escribir los packs **rompió un gate ajeno**: `docs/CONTRIBUTING.md` entraba al pack por una sección declarada, y la regla de la fase era «el pack se escribe dentro del plan». Copiarlo a `.opencode/plans/<PLAN>/briefing/` dejó **2 referencias rotas** nuevas y el quick pasó de 11/11 a **10/11** con `[8/11]` en rojo — un verificador de integridad de rutas del corpus, que FASE-D no tocó ni leyó. Y en el mismo gesto el artefacto generado **volvió a envejecer el índice de lecciones**: 5 `.md` nuevos dentro del corpus que `build_lesson_index.py` recorre | Un artefacto derivado **no es neutro respecto al directorio donde cae**: pasa a ser corpus para todo verificador que lo recorra por glob, así que hereda las obligaciones de un documento escrito a mano (referencias válidas, presencia en el índice) sin tenerlas. El plan elegía la ruta del pack por conveniencia de cierre, no por el radio de acción de los gates que viven ahí | Regla nueva en el generador, nacida de la medición y no del diseño: **toda fuente declarada fuera de `.opencode/` se declara `lectura_aparte` y no se copia** — sale por `no_incluye` con su ruta y su motivo, y el pack queda gobernado por las shas de lo que sí copió. Además: regenerar el par del índice **después** de generar los packs, y declararlo (`[6/7]` los mira). Después de la regla, `refs` vuelve a `PASS`, las citas cierran con «743 históricas, 0 nuevas» y el quick recupera 11/11 | **INCLUIR** — antes de escribir un generado dentro de un corpus versionado: preguntar qué verificadores lo recorren por patrón de ruta. Y preferir la salida que **declara** la fuente en vez de copiarla, cuando copiarla la duplica en un territorio ajeno |
| **L-VCF-18** | FASE-D publicó en `09` §D un par `def test_` **4.360 → 4.404** («medido al abrir la fase»). Al cerrar, el **mismo comando canónico** no dio 4.360 sobre ningún árbol: disco **4.557**, `git grep` sobre `HEAD` **4.470**, y `disco − contribución propia` **4.508** — que es exacto el POST que publicó FASE-C. El par refutado no tenía crudo en `evidence/`, así que no había de dónde defenderlo | Es A6 y «quién produce el dato publicado» aplicados a mí mismo: una cifra **transcrita de memoria y redactada sin su comando al lado** entra al documento con la misma apariencia que una medida, y el plan no tiene cómo distinguirlas. El daño no es el número —la resta propia sí cuadraba con su contribución— sino que **se verificaba contra un minuendo que nadie midió** | Se retiró la cifra y se re-publicó con el comando y su crudo: `evidence/…/FASE-D/test_count_pre_post.txt` imprime las cuatro variantes (método canónico, exclusión de la selección propia, contribución propia, y `HEAD`), y la fila del §D dice ahora qué reproduce y qué no. Queda como regla de la casa: **ningún PRE entra en un documento de cierre sin su archivo de crudo**, y si no lo hubo, se llama «reconstruido» y se dice con qué se contrasta | **INCLUIR** — para toda fase que publique una resta: el minuendo necesita su comando y su crudo igual que el sustraendo; una resta aritméticamente impecable sobre un número no medido es la forma más creíble de error |

| **L-VCF-19** | FASE-D transcribió su propia medición de AC20 a tres documentos de cierre (`00` §4, `06` AC20/AC23, `10`), y **cada barrido documental posterior la venció**: al regenerar los packs tras escribir el cierre, el `before` y el `after` subieron los dos (más fuentes crecidas en ambos lados) y el total quedó **dos veces** desfasado del número publicado. Lo mismo con el par de tamaños de AC23, que cambió cuando la declaración dejó de incluir la ruta absoluta intentada. Las cifras se retiraron de los tres `.md` y quedaron solo en `carga.json` / `carga-pre-post.md` / `mutation/resumen.txt` | Es **A6 con un mecanismo nuevo**: no es que el documento envejezca al medir otra cosa — es que **el documento medido es parte de lo medido**. Un generador que embeddinga sus propias fuentes de gobierno crea un **punto fijo inestable**: cualquier cifra de tamaño que se publique en un `.md` que el pack copia cambia la próxima medición del tamaño. El verificador no está mal: lo que está mal es el *canal* | Regla escrita en el propio `06`: **ninguna cifra de carga o de tamaño de pack entra en un documento que el generador copia**; se publica el comando, el artefacto y la identidad comprobada (`resta_comprobada`, las cinco identidades del instrumento), y en el documento queda el **orden de magnitud** con su porqué (aquí: «muy por debajo de un tercio, porque el workflow está en los dos lados»). Legible en el artefacto: `carga.json` → `method.suma_de_lado` | **INCLUIR** — antes de copiar una métrica a un documento: comprobar si el instrumento que la produce **recorre ese documento**. Si sí, la cifra no cabe en el documento; solo cabe su comando |

## Seguimientos abiertos

| # | Tema | Dueño | Disparador |
|---|---|---|---|
| S1 | D1: corregir o retirar las aserciones A1–A4 en `.agents/` | FASE-RELEASE de este plan | **Estado vigente: matriz §13 de la fuente única; no certificada aquí. Antecedente retirado:** el dictamen del 2026-09-23 declaró «ACEPTADA/RESUELTA por el bloque B de la orden de calidad» (instrucción literal del operador, incluida ampliación para tocar la fuente de A4, `lecciones-capitalizadas-template.md`): las cuatro aserciones se retiraron de su fuente, el árbol real sale `SIN-HALLAZGOS` (`exit 0`) y A1–A4 quedaron como contraejemplo congelado con mutantes y su regresión. **Disparador reformulado el 2026-09-21 (era circular, L-VCF-4):** verificador operativo con mutation check en disco **y** decisión escrita del operador. Ver `dependencias-fases.md` §Ejecución del bloque B. Sin tocar D2 |
| S8 | Los **4 pins del denominador 11** que FASE-A escribió en `tests/` al fijar el contrato AC1 (`test_governance_numbers_reproduce_A1_A4.py`) | D1/D2 de este plan | **Antecedente técnico del 2026-09-23, sujeto a la matriz vigente §13, no cierre de D1:** `reproduce_A1_A4` y `por_asercion_no_por_linea` corren ahora contra el contraejemplo congelado en `fixtures/` (misma fuente de checks y hook reales → `observed` idéntico al maestro §1), con nota datada, **sin** limar la aserción (L-VCF-5); se sumó `test_arbol_real_honesto_tras_d1` sobre el árbol vigente. Los pins del denominador 11 siguen en pie sobre la fixture; solo se moverían con D2 |
| S9 | El verificador **no está cableado** a ningún gate: corre suelto (`python scripts/validate_governance_numbers.py --report`; el rojo A1–A4 y el posterior verde de D1 son antecedentes, no certificación actual: ver matriz vigente §13 de la fuente única y fila S1). Promoverlo al `--quick` es exactamente **D2** y rompería la cifra que `REFACTOR-WHATSAPP` pinea en cuatro documentos ⟦**Re-contado el 2026-09-24, bloque C**: ya no queda **ningún sitio vigente** de ese plan que pinee la cifra —su bloque de arranque ahora manda el comando—; los cinco archivos que la contienen (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G) son registros de fases cerradas. La conclusión de esta fila no cambia: promover D2 invalidaría mediciones ajenas ya publicadas⟧ | D2 | Sesión previa al `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` |
| S2 | D2/D3: promover el verificador al `--quick` y rebanar el workflow; D3 **parcial**, no cerrada por B | Plan propio, posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`; el rebanado completo conserva su dueño, la simplificación encargada a B no se difiere |
| S3 | **D6: lint de contradicciones semánticas** (`validate_plan_semantics.py`) | Plan propio posterior; entra en **este** directorio si el disparador se cumple vigente este plan | El `acceptance` que publique AC15 en FASE-C. Si el triaje sale inaceptable, **no se activa** |
| S4 | **D7: activar el proveedor de decisiones ya habilitado** y correr la comparación | Plan propio posterior | Decisión del operador del 2026-09-20 de no entrar ahora; AC9 dejó la costura probada **el 2026-09-21** (`files_changed_to_add_provider = 1`). Al activarlo cae la decisión de **S10** |
| S10 | **Dónde vivirá el `import` del SDK cuando D7 se active**: la puerta (y el archivo nuevo solo declara) o re-anclar AC6 a «puerta + directorio de proveedores». Las dos son coherentes con AC9; solo una con la letra de AC6 | Quien ejecute **D7** — no este plan: decidirlo aquí habría sido reinterpretar una restricción en silencio (L-VCF-9) | Que un proveedor real vaya a quedar detrás de la costura. Está escrito en el docstring de `decision_client.py`, en `extensibilidad.txt` y en la lección L-VCF-9 |
| S11 | **✅ ACEPTADA el 2026-09-23 — corregida fuera de este plan.** **El denominador de AC6 admitía un archivo de entorno no declarado**: `.venv-wsl/bin/activate_this.py` entraba en los 692 `.py` que escanea `iterar_py()` porque `.venv-wsl` no estaba en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION`. Y las exclusiones se solapan (`site-packages` anidada en `venv`/`tmp_test`), así que su suma no reproduce el universo. El numerador no se mueve: **0** imports prohibidos re-medido el 2026-09-22 | ~~Quien toque `decision_client.py`~~ → **bloque A de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`**, que la ejecutó en `fdd397f` con sus pruebas de exclusión y publicó el conteo ⟦**rectificado el 2026-09-23**: esta fila decía «con su test de población (2 funciones)». Medido con `git show fdd397f`, la cura de S11 vive en `tests/quality_gates/decision_client/test_decision_client_aislamiento_imports.py` (**+83/−11**, tres funciones: `test_un_directorio_de_venv_se_excluye_y_su_exclusion_se_publica_con_su_conteo`, `test_en_el_arbol_vigente_un_venv_presente_aparece_como_exclusion_publicada`, `test_exclusiones_solapadas_no_inflan_el_denominador`), **no** en `governance_numbers`⟧ | Cerrada por ese bloque con **corrección técnica**; el **cierre contractual** (la enmienda en este plan, que el propio resumen del bloque A §4 declaraba pendiente) quedó registrado el 2026-09-23 en `dependencias-fases.md` §Conciliación. **Re-validación offline de esta sesión:** población escaneada **696** vs `git ls-files '*.py'` **696** → **residuo 0**, `--scan-imports` con `exit 0` y `excluidos_por_directorio` publicando `.venv-wsl`: 582. **Sus pruebas también corrieron aquí:** selección `decision_client` → **87 casos, `EXIT=0`**, que es donde viven las tres funciones de exclusión de S11 |
| S12 | **✅ ACEPTADA el 2026-09-23 — corregida fuera de este plan.** **`validate_governance_numbers.py --report` escribía por default dentro de la evidencia commiteada de FASE-A** (`REPORT_DEFAULT`): cada corrida re-escribía `generated_at`, `medido_el` y el conteo inyectado, o sea **pisaba el registro fechado de otra fase**. Medido y revertido el 2026-09-22 (`git checkout --` sobre ese archivo; re-muestreo con destino explícito dejaba FASE-A limpia y el mismo `HALLAZGOS` con `exit 1`) | ~~FASE-RELEASE de este plan~~ → **bloque A de la orden de calidad**, que trasladó la ejecución a su §4.A (FASE-RELEASE tiene prohibido editar código) y la corrigió en `fdd397f` con **6 funciones** en `tests/quality_gates/governance_numbers/test_governance_numbers_s12_report_no_escribe.py` (**+97/0**, medido con `git show`) ⟦**rectificado el 2026-09-23**: esta celda decía «+ 5 tests»; la cuenta real es 6, y el directorio completo suma **35 funciones / 40 casos**⟧ | Cerrada por ese bloque con **corrección técnica**; el traslado contractual se aceptó el 2026-09-23. **Re-validación offline:** `--report` sin destino → `exit 1`, stdout JSON con A1–A4, stderr avisa que no escribió, y el `sha256` de `evidence/…/FASE-A/informe.json` queda **idéntico** antes y después con `git status --porcelain evidence/` vacío. **La guarda publicada en el README para FASE-C queda sin efecto** (rectificada el 2026-09-23); la lección **L-VCF-12** sigue vigente como regla general. **Sus pruebas sí corrieron en esta sesión** (era la deuda del cierre): las 6 regresiones por nombre → `6 passed, EXIT=0`, y la selección del directorio → `40 passed, EXIT=0` en `evidence/…/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/pytest_{seleccion_governance_numbers,s12_report_no_escribe}_2026-09-23.txt` |
| S13 | **Estado vigente: matriz §13 de la fuente única; no certificada aquí. Antecedente retirado:** el dictamen del 2026-09-23 declaró «RESUELTA por el bloque B de la orden de calidad». Original: el arnés de mutación de FASE-A escribía por ruta hardcodeada en evidencia de otra fase. `tests/quality_gates/governance_numbers/test_governance_numbers_mutation_por_asercion.py` (la constante `EVIDENCE`, definida junto a `SCRIPT` y sin parametro de destino) apuntaba a `evidence/…/FASE-A/mutation/`, así que correr el test **re-escribía 7 archivos cerrados de FASE-A** (`verde_baseline.txt` + los 6 mutantes), con `git status` limpio pero mtimes movidos — la familia **S12 / L-VCF-12** en un test que la cura del bloque A no cubrió. **Cura B:** se retiró la constante de escritura; ahora `_escribir_salidas(verde, destino)` vuelca en destino temporal explícito, hay `test_re_medir_no_reescribe_expedientes_cerrados` (compara hash **y** mtime sobre `evidence/…`), `test_el_arnes_no_conoce_ruta_de_evidencia_como_destino_de_escritura` (guard estructural). ⟦**Rectificado en la remediación de B, 2026-09-23:** el primer cierre añadía además «un control negativo comprueba que la observación (hash y mtime) detecta la reescritura de bytes idénticos», y eso **no observaba ninguna escritura**: el test definía su propia función de huellas y movía el mtime con `os.utime` artificial. Ahora se observan las **operaciones de escritura** del escritor real con `tests/support_observador_escrituras.py` (única implementación compartida; alcance declarado: proceso de pytest, no procesos hijos), con ancla positiva, y los tres controles del mandato (a escritor redirigido a destino protegido, b bytes idénticos, c mtime restaurado) sobre un **expediente desechable**; la comparación de contenido y metadatos se conserva además. Fuente única: `evidence/…/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`.⟧ | ~~Quien toque ese test~~ → **bloque B de la orden de calidad** (con mandato expreso del operador); se registra con dueño, no se lima | La declaración anterior «Cerrada por B» queda retirada: el estado vigente se lee en la matriz §13. **La regla para el mutation check propio de C (AC14) sigue vigente:** su evidencia va a `evidence/…/FASE-C/mutation/`, destino declarado por la ruta del propio cierre, no una constante al directorio de otra fase |
| S5 | D8: la consulta Q7 de QMind **sí se ejecutó** en la auditoría del 2026-09-20 (cuatro `retrieve`; el comando válido usa el ID del notebook, no su nombre) | FASE-RELEASE | Re-correr solo si el corpus del notebook cambió desde la auditoría, y verificar que las citas de L-V2.1/L-V2.2/D-V2.1 siguen en pie |
| S7 | **D10: re-leer la interfaz del write-back antes del cierre** — `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara dentro de su alcance `validate_qmind_writeback.py` y su conexión en `run_all_validations.py`, y piensa añadir `--title`/`--file` | FASE-RELEASE de este plan | Al llegar el cierre: `--help` contra el árbol vigente y re-escribir el orden de `04-contrato-ejecucion.md` si la firma cambió |
| S6 | D4/D5: verificadores de la resta pre/post (R2.7) y del par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda | Ya asignados antes que este plan; no se reasignan |
| S15 | **ESTADO VIGENTE 2026-09-26 — ✅ CERRADA, curada en `scripts/build_lesson_index.py` con el corte «último commit que tocó el documento», ratificado por el operador ese mismo día.** La fecha del índice ya no sale del sistema de archivos: `mtime` fue **retirado** de la lista de fuentes admitidas (no rebajado) y `_plan_date` tiene tres cortes — `nombre` (la fecha que trae el nombre del plan), `commit` (la fecha `%aI` del último commit que tocó el documento, recortada a 10 caracteres porque `%ad --date=short` re-formatearía en la zona horaria de quien lee y volveríamos a tener una fecha que depende del entorno), y `SIN-FUENTE` con fecha `0000-00-00` cuando no hay ninguna de las dos, que es un **estado publicado y no una aproximación** (antes solo existía `desconocida` si no había archivos). La cobertura del par publica `fechas_por_fuente` y tanto el writer como `--check` imprimen la línea `[fechas] nombre=… commit=… sin_fuente=…`, **en verde y en rojo**: un `[OK]` que no dice de dónde salieron las fechas no es auditable, que es como nació esta fila. **Divergencia con lo que prescribía esta fila, registrada para que no se lea como olvido:** abajo se leía «que la fecha salga de una fuente declarada en el documento»; **ese corte no es el que se aplicó.** El 2026-09-26 el operador ratificó el corte del commit, y la razón está medida: los dos únicos dueños que caían al tier 2 viven bajo `.opencode/context/Historico/` y **no declaran su fecha en el cuerpo**, así que fechar por documento habría obligado a editar dos documentos históricos que son evidencia fechada de otras fases. **Límite que la cura conserva, y que no se cura aquí:** el último commit que tocó un archivo **no es** la fecha en que se escribió. Hoy el orden se mantiene — DT-2 da `2026-07-26` y DT-3 da `2026-08-29`, el mismo orden que daba el `mtime` (`2026-07-24` y `2026-08-29`) —, pero un futuro `git mv` masivo de `Historico/` **colapsaría esas dos fechas a una sola y el desempate pasaría al nombre del plan** (`build()` ordena por `(fuente, fecha, plan)`). Sigue siendo **determinista**, que es lo que S15 exigía; pierde el semántico «el más antiguo define». Dueño: quien reorganice `.opencode/context/Historico/`. **La alternativa estaba medida y no mejora el corte:** con `--diff-filter=A` (el commit de creación) DT-2 y DT-3 dan **los dos** `2026-07-26` — DT-3 se creó en el mismo commit que DT-2 —, así que la fecha dejaría de distinguirlos y el dueño quedaría solo en el desempate por nombre; empobrece el criterio, no lo corrige. **Cifras de esta fila corregidas por medida (2026-09-26):** son **11 de 339** las entradas con `fuente_fecha = "mtime"`, y son de **dos planes y no de uno** — **9** de `context/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL` y **2** de `context/CONTEXT-DT-3-TECH-DEBT-POST-DT2`, ambos bajo `.opencode/context/Historico/`. Medido corriendo el generador **de `6b02532`** sobre el árbol vigente con `--out-dir` a scratch, sin tocar el par publicado. El índice etiqueta a los dueños por **stem** (`_sources` construye `context/{p.stem}`), por eso la carpeta `Historico/` no se veía en la medición del 2026-09-24, que habló de 9 entradas de un solo archivo. Con la cura esos mismos 11 salen `fuente_fecha = "commit"` y la cobertura queda `nombre 328 / commit 11 / SIN-FUENTE 0` sobre 339 IDs (16 análisis, 39 contexto, 422 `.md` escaneados). **Prueba:** `tests/test_build_lesson_index_s15_fecha_versionada.py`, 4 funciones (medidas `4 passed` el 2026-09-26) — dos clones `--local` **del mismo commit** con mtimos distintos y declarados (`2020-01-02` y `2031-06-06`, con precondición que falla si los dos mtimes coinciden, para que el verde no sea vacío) publican **bytes idénticos** el `.md` y el `.json`; el control negativo **no** reimplementa el defecto: lee el generador **commiteado** en `6b02532` (línea 112, `f.stat().st_mtime`) y **exige que diverja**, con ancla por id sobre la familia `S-1`…`S-11`; el tercer corte se ejercita sobre una copia **fuera del repo**, donde ningún commit es posible; y la fecha esperada se re-deriva de `git log` en vez de pinearse, porque el conjunto del tier 2 crece si alguien añade un CONTEXT sin fecha en el nombre. **El control queda anclado a `6b02532` y no a `HEAD`:** al commitear la cura, HEAD contiene el generador corregido y el control se quedaría sin rojo con el que compararse. **Lo que esta fila todavía no afirma:** que el commit sea autosuficiente. La prueba en el **propio árbol del commit** — `git archive` extraído a un directorio limpio y `--check` corrido ahí, con mtimes nuevos — se corre sobre el commit (b) al publicar y su resultado va al expediente de cierre; un verde del árbol de trabajo no la sustituye, que es justamente **L-VCF-15**, el origen de esta fila. **Antecedente fechado (medición del 2026-09-24, con sus cifras corregidas arriba):** ⟦**`[6/7] build_lesson_index.py --check` no es reproducible entre checkouts.** 9 de las 335 entradas del par llevan `fuente_fecha = mtime` (las de `CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL.md`) y `git archive` no preserva mtimes, así que un par generado en una máquina declara `VENCIDO` en cualquier otra. Medido el 2026-09-24 sobre extracciones limpias de **dos** revisiones ya publicadas —`da382b1` y `5817edd`—: ambas `[FAIL] Índice de lecciones vencido`, `EXIT=1`, con los documentos idénticos y con el par del árbol de trabajo copiado dentro. **La cura no es commitear el par**: es que la fecha salga de una fuente declarada en el documento, no del mtime.⟧ ⟦**Conciliación 2026-09-25 (orden de calidad), con S15 ABIERTA**: un verde **local** de `[6/7]` **no certifica otro checkout** — solo afirma que el par coincide con los bytes de *este* árbol con los mtimes de *esta* máquina en *este* momento—, y **reparar el generador** (`build_lesson_index.py`, la rama `fuente_fecha = "mtime"` de `_plan_date`) **es alcance técnico separado**: no lo autoriza ninguna fase de este plan, y FASE-RELEASE tiene prohibido modificar código —lo declararía con su dueño y dejaría checkpoint⟧ | Quien pueda tocar `build_lesson_index.py` (FASE-C lo tenía **prohibido** por mandato, así que no lo corrigió) — **ese dueño se presentó el 2026-09-26 con mandato del operador y la corrección está en `scripts/build_lesson_index.py`, sin commitear al cerrar esta fila** | ⟦Antes de confiar en un verde de `[6/7]` fuera de la máquina que generó el par⟧ — **corte curado el 2026-09-26**: la fecha no vuelve a depender del reloj de la máquina; el verde local ya no es la prueba, la prueba son los dos checkouts del mismo commit en `tests/test_build_lesson_index_s15_fecha_versionada.py` y la extracción del árbol del commit. **El segundo disparador sigue vigente como atribución histórica**: un `[FAIL]` de índice visto en un clon fresco **antes** del 2026-09-26 era S15 y no culpa de la fase que lo reportó (así quedaron leídos `da382b1` y `5817edd`); **después** de la cura, un `[FAIL]` en un clon con CRLF no es S15 sino el otro corte — hay que clonar con `-c core.autocrlf=input`, porque `git clone` no lee la config local del clon y el system `autocrlf` es `true`. Y mientras el commit (b) no se extraiga y se valide en su propio árbol, **esta fila cierra con su prueba pendiente de publicación, no de cura** |

| S16 | **La convención que parsea `build_phase_briefing.py` (`Lee …` dentro del bloque «Prompt de ejecución») no está escrita en ninguna fuente del proceso.** Medido al cerrar FASE-D: **121** prompts de fase bajo `.opencode/plans/Archives/` y **0** la usan; las únicas 5 que la usan son las de este plan. Corte del generador, no defecto: el pack de un plan archivado sale `SIN-DECLARACION` y su `--check` imprime `SIN-FUENTES`. Su texto, dueño, disparador y alternativa descartada viven en `dependencias-fases.md` §S16 (fuente única; esta fila no la re-transcribe) | `.agents/workflows/templates/prompt-fase-template.md` §8 — **no es de FASE-D**: tocar `.agents/` es AC17 y esa superficie exige instrucción literal | La próxima vez que un mandato autorice editar el template (precedente: el bloque B de la orden de calidad autorizó `lecciones-capitalizadas-template.md`). FASE-RELEASE **no** reescribe los prompts archivados para que tengan packs |

| S17 | **Dos writers de texto reescriben en CRLF archivos que git almacena en LF** — `SyncEngine.sync_rule` (`scripts/sync_versions.py`) y `run_regenerate_domain_primer` (`scripts/doctor.py`) cierran con `write_text` sin `newline="\n"`. Medido al cerrar FASE-RELEASE: **6** archivos `[FAIL] Line endings`, normalizados byte a byte con `git diff -U0` comprobado (`evidence/…/FASE-RELEASE/12-normalizacion-lf.txt`). Su texto, dueño, disparador, remedio provisional, alternativa descartada y **cura (2026-09-25, tres escrituras: `sync_rule`, `run_regenerate_domain_primer` y `run_status`)** viven en `dependencias-fases.md` §S17 (fuente única; esta fila no la re-transcribe). Prueba: `tests/test_sync_writers_lf_y_fecha_readme.py`, con su control contra la versión commiteada de cada script | `scripts/sync_versions.py` y `scripts/doctor.py` — edición de `scripts/`, **no** de este plan: FASE-RELEASE tiene prohibido modificar código y por eso se declaró en su día | **CUMPLIDO el 2026-09-25**: el operador autorizó editar esos dos writers (+ tests). Estado vigente: §S17 |

| S18 | **La regla `readme_version_header` no goberna la fecha legible de `README.md`**: tras el sync de cinco cabeceras, esa línea siguió con «11 Septiembre 2026» con `release_date: 2026-09-25` vigente; `guia_tecnica_header` sí goberna la suya. Corte de cobertura declarado: `[3/11] Version Sync` dio PASS con el README desfasado. Su texto, dueño, disparador, corte de cobertura, alternativa descartada y **cura (2026-09-25: el patrón alcanza la fecha y el template emite `{date_text}`, forma larga, no ISO)** viven en `dependencias-fases.md` §S18 (fuente única; esta fila no la re-transcribe) | `scripts/sync_config.yaml` y el lector de esa regla en `scripts/sync_versions.py` — tampoco es de esta fase | **CUMPLIDO el 2026-09-25**, con la escritura de `README.md` autorizada aparte (destino central): el `--check` pasó de `IN_SYNC` a `FAIL` y la línea 5 quedó alineada por su escritor. Estado vigente: §S18 |

### Decisiones de FASE-C (2026-09-24), cada una con su alternativa rechazada

Ninguna de estas seis fue reinterpretada dentro de la fase: cinco venían resueltas por el contrato
(E1–E5) y la sexta es de diseño local de C. La sexta queda además con deuda y dueño propios.

| # | Decisión tomada | Alternativa rechazada, y por qué |
|---|---|---|
| 1 | **El triaje propone y jamás descarta** (AC10). `guardar_filas_ancladas()` restaura lo que el filtro intentó sacar y publica el intento | **Rechazada: filtrar lo que el emisor marca `no-pertinente`**, que es la semántica normal de un triaje y la que hace útil el informe. Es exactamente la familia que cobró un plan: un filtro que descarta en silencio una premisa carga-estructura reprodujo `VACUOUS_RECALL` en `REFACTOR-WHATSAPP` y obligó a crear FASE-0 y AC20. Coste aceptado y dicho: §2 acumula filas cuestionadas y el informe es más largo de leer |
| 2 | **Nada entra en §2 por sí solo** (E3): el script no escribe el documento, y una decisión humana sin `decidio`/`fecha`/`motivo` sale `REVISION-INCOMPLETA` con `exit 6` | **Rechazada: aplicar las propuestas y documentar después**, que era lo que mandaba la versión original del paso 6 del post-ejecución de C. Con emisor falso habría escrito en §2 filas cuya evidencia es sintética —justo lo que AC15 declara `NO-EJERCITADO`— |
| 3 | **Suelo por ruta (b)** (E2): C consume el JSON **después** de ejecutar ella misma la comprobación de frescura | **Rechazada la ruta (a)** (calcular solo en memoria, la cura de `PASO0-VERIFICADOR-CAPITALIZACION`): habría **borrado** el estado `VENCIDO` que AC11 exige, dejando un AC de tres estados sobre un diseño de dos. **Y prohibida la tercera vía** (leer el JSON fiándose de `[6/7]` del hook). Coste aceptado y publicado: dos lecturas del mismo JSON por corrida |
| 4 | **Pregunta `choice` de dos opciones** con `por_si` y `confidence` publicados por separado (E1) | **Rechazada la pregunta `noul`**: `RespuestaNoul.confidence` es `None` con su motivo y la puerta **rechaza** que un `noul` la reporte, así que un umbral sobre `probabilidad_si` cerraría AC12 con una métrica que el AC no describe |
| 5 | **`acceptance = NO-EJERCITADO` y D6 dormida** (E4), sin ratio simulada — y con un test que busca el número y lo niega | **Rechazado: publicar la proporción mecánica** `propuesto/triado` como aceptabilidad para poder cerrar AC15 en verde. Convertiría el disparador de una deuda en una cifra fabricada y abriría un lint semántico sobre una base que nunca juzgó nada |
| 6 | **El guard se ejercita re-preguntando por las ancladas** (`--revisar-anclados` por defecto; `--solo-pendientes` para apagarlo) | **Rechazado: dejar el pool solo con lo no anclado**, que era el diseño inicial y producía un verde vacío (L-VCF-13). Contrapartida detectada al medir: el pool ya no es «solo candidatos nuevos», así que el denominador publica por separado ancladas re-preguntadas y pendientes |

**Deuda nueva abierta por esta fase — S14** (con dueño y disparador, no con silencio): la CLI de C
expone `--plans-dir` pero no su `--context-dir` simétrico, y el check de frescura siempre pasa
`DEFAULT_CONTEXT`. Mientras se corra sobre el árbol real no afecta a nada (y ningún AC se certifica
sobre esa variante), pero **apuntar `--plans-dir` a una copia compara un corpus mixto**: planes de la
copia contra definiciones del contexto real. Dueño: **este plan, FASE-D o RELEASE** (donde el triaje se
vuelve a llamar con rutas ya trasladadas tras el `git mv`); disparador: la primera llamada de C sobre un
directorio que no sea el del repo — que es justo el caso del cierre de RELEASE con el plan archivado.
Medido al escribir `test_triage_propuesta_no_escribe_seccion_dos.py`, que por eso corre sobre el árbol
real con el sha256 y el observador de escrituras como red, y no sobre una copia.

**⟦S14 re-examinada el 2026-09-25 por la conciliación final de la orden de calidad — sigue ABIERTA, con su
disparador corregido⟧.** Se comprobó leyendo la CLI real y el texto del cierre, no asumiendo: la
invocación prevista para el RELEASE de este plan es `git mv` **dentro del propio repositorio**
(`.opencode/plans/<PLAN>` → `.opencode/plans/Archives/`, ver `05-prompt-inicio-sesion-fase-RELEASE.md`
Tarea 4) y **ninguna de sus líneas llama a `triage_lesson_relevance.py` con `--plans-dir` apuntando a un
directorio trasladado o a una copia**. Por lo tanto **ese `git mv` no dispara S14 y no cambia el corpus
gobernado**: el corpus sigue siendo `.opencode/plans/` bajo la raíz, con el plan simplemente en otra ruta
hija. Lo que sí dispara la deuda es lo que su propia frase ya nombraba —**correr el triaje con
`--plans-dir` sobre una copia o un árbol extraído**, con las definiciones de `.opencode/context/` sin
trasladar—, y el paréntesis que equiparaba el caso del RELEASE con el de la copia **quedó rectificado**:
sobrestimaba el alcance del defecto. Consecuencia práctica y declarada: en el cierre **no** se hace
ninguna llamada al triaje sobre rutas trasladadas, y si alguien la hace, S14 se dispara con su evidencia.

### Decisiones de FASE-D (2026-09-24), cada una con su alternativa rechazada

Son siete. Seis son de diseño local del generador; la primera es la que estaba dictada por el contrato
(D3/AC17) y la que más caro le cuesta al delta de AC20.

| # | Decisión tomada | Alternativa rechazada, y por qué |
|---|---|---|
| 1 | **El pack no sustituye ninguna lectura canónica**: `.agents/workflows/phased_project_executor.md` se declara como `lectura_aparte_obligatoria` en la primera posición de `no_incluye` y **nunca** se copia (AC19/AC17) | **Rechazada: rebanar el workflow** para que el pack sí lo absorbiera — es exactamente **D3**, cuya superficie es configuración central del repo y exige instrucción literal. Coste aceptado y medido: el workflow entra en los dos lados de la resta con el peso que `carga.json` publica por fase como `workflow_canonico_bytes`, así que AC20 no cierra en «un tercio» sino en una fracción de él. **Ni ese peso ni ese porcentaje se copian en esta fila**: el porcentaje vigente —recalculado de `carga.json` el 2026-09-25 por la conciliación final de la orden de calidad— lo publica la fila «Carga de lectura A7» del `README.md` de este plan. ⟦**Rectificación con atribución, 2026-09-25**: esta fila publicitaba «108.017 bytes por fase» y «en el orden del **12 %**», y con eso **contradecía la regla que ella misma declara** en §Métricas de ejecución («sin transcribir cifras aquí: este documento entra al pack que ese comando mide», **L-VCF-19** ⟦la regla la fijó FASE-D al cerrar; el residuo era de la fila, no de la regla⟧). Las tres cifras que andaban copiadas por el plan (`13,08`, `12,8`, «12 %») no reproducían ninguna el artefacto: **13,15 %** es el valor recalculado y ya tiene una sola fuente. Sin ese peso en ambos lados el número sería otro y falso⟧ |
| 2 | **La resta va entre cargas totales**, con tres sumandos por lado (`workflow_obligatorio`, `coste_de_generacion`, `pack_consumido`) y la identidad `delta = omitido − andamiaje − coste` publicada como `resta_comprobada` | **Rechazada: `fuentes − pack`**, que era la lectura natural del enunciado de AC20 y habría publicado un ahorro de más de un tercio. Es la variante de «concatenar no es ahorrar»: el pack **copia** lo declarado, así que lo único ahorrado es lo que **no entró** (`omitido_declarado_bytes`), y contra eso juegan el andamiaje del propio pack (`andamiaje_del_pack_bytes`) y el coste de generarlo (`coste_de_generacion`) — las tres columnas, por fase y en total, en `carga.json`. Con delta **negativo** en alguna fase el resultado sigue siendo válido y se explica (L-D3) |
| 3 | **La caducidad la gobierna el `sha256` de las fuentes; HEAD es procedencia** y el pack **no** figura entre sus propias fuentes (`gobernada = False` sobre su prompt) | **Rechazada la caducidad por HEAD**: el commit que guarda el generado sería a la vez su causa de caducidad, así que `--check` no podría dar verde nunca después de commitearlo. Prueba directa: `test_briefing_head_no_es_la_llave_de_caducidad` fabrica un `provenance.head` inexistente, el pack sigue `exit 0` y el informe imprime `procedencia_distinta: true` (se reporta, no es fatal) |
| 4 | **Toda fuente declarada fuera de `.opencode/` sale como `lectura_aparte`, copiada no**: entra en `no_incluye` con su ruta y su motivo, y queda fuera del gobierno de `--check` | **Rechazada: copiarlas al directorio del pack**, que era la conducta de la primera versión y **rompió `[8/11]`** (2 referencias rotas nuevas, quick 10/11) y volvió a envejecer el índice de lecciones → **L-VCF-17**. Nace de la medición, no del diseño: el radio de acción de los gates que recorren el corpus por glob no estaba en el mandato |
| 5 | **Fuente ausente ⇒ el pack NO se emite** (`exit 1`, la ruta pedida nombrada en la salida) | **Rechazada: emitir con huecos** marcados «no encontrado» — convertiría un sobreentendido en un documento que se lee completo. AC22 lo distingue y hay un test por cada una de las cuatro causas del `--check` (`FUENTE-AUSENTE`, `SHA-DISTINTO`, `FUENTE-ILEGIBLE`, `PACK-AUSENTE`), más la denegatoria de que cero fuentes gobernadas imprima `[OK]`: imprime `[SIN-FUENTES]` |
| 6 | **Un prompt que nombra un documento en prosa, sin ruta, sale `SECCION-NO-RESUELTA` con `rutas_intentadas: []`** | **Rechazado: adivinar por heurística de rutas** (los `*.md` citados en el texto), que fabricaría una lectura que nadie declaró —la familia L-PF6/L-PF10— y cerraría AC22 en verde vacío. Contrapartida medida y registrada: sobre el corpus real eso deja el pack de FASE-RELEASE en `SECCION-NO-RESUELTA` y deja **0 de 121** prompts archivados triables → **S16**, con dueño y disparador. La alternativa opuesta (adivinar) habría dado packs llenos para los archivados y una cifra de cobertura fabricada |
| 7 | **AC23 muta el guard, no la clasificación**: el mutante apaga `GUARD_NO_TRUNCAMIENTO_ACTIVO` y deja el estado `SECCION-NO-RESUELTA` intacto | **Rechazado: mutar `_declarar_recorte` para que cambie el estado**, que habría probado la máquina de estados de secciones —ya cubierta por otros dos archivos— y no el guard. El rojo real: los cientos de bytes de declaración que desaparecen mientras el estado sigue diciéndolo todo (los dos tamaños, en `mutation/resumen.txt`); y su ancla tuvo que re-escribirse porque vivía en texto copiado del corpus → **L-VCF-16** |

## Métricas de Ejecución

- [x] **FASE-A (2026-09-21), en la misma base de medición que su par pre/post** (R2.3): quick
  11→11 (resta 0), hook 7→7 (resta 0), población A8 22/17/2 → 22/17/2 (resta 0), selección de tests
  0→23 funciones (+23, **no** 0: la fase agrega tests y lo dice), canónicas del repo
  4.307→4.330 (resta +23, coherente con la fila anterior). Crudos en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/`.
- [x] **FASE-B (2026-09-21), misma base de medición que su par pre/post** (R2.3): quick 11→11
  (resta 0), etiquetas del modo completo 4→4 (resta 0), hook 7→7 (resta 0), `git diff` de los cuatro
  scripts gobernados **vacío**, bytes de `.agents/` 98.694/6.123 **idénticos** (AC17), población AC6
  678→678 rastreados y 690→692 en el árbol (**+2**, no 0: los dos instrumentos que la fase escribió para generar su propia evidencia; ver `FASE-B/baseline-pre-post.md` nota 3), imports prohibidos fuera de la puerta 0→0, pins
  del 11 en `tests/` 4→4 (esta fase **no** añadió ninguno, a diferencia de A). Lo que sí se movió y se
  declara aparte: selección de tests 0→**48 funciones / 53 casos**; canónicas del repo
  4.330→4.378 (resta +48, coherente con la fila anterior). Crudos en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/`. **Rectificación medida el 2026-09-22, al
  commitear la fase (`647f436`)**: los `.py` rastreados pasaron de 678 a **691** (+13 propios) y el
  numerador de AC6 **sigue en 0** re-medido con la puerta sobre los mismos 692 del árbol; la resta
  692−691 se desglosó y dio `.venv-wsl/bin/activate_this.py` → **L-VCF-11** / **S11** (ver nota 4 del
  par pre/post).
- [x] **AC9 medido, no afirmado**: `files_changed_to_add_provider = 1` (`costura.json`) con
  `agregados = [falsos_proveedores/falso_segundo.py]`, `modificados = []`, y despacho de los dos
  proveedores por la misma puerta con respuestas **distintas** (si contestaran igual, el 1 sería humo).
- [x] **Lo que se pospuso (D7) y qué cuesta posponerlo.** No entra ningún proveedor real, y eso tiene
  cuatro consecuencias escritas: (i) ningún AC de este plan mide calidad de decisiones de un modelo —
  miden forma, aislamiento y no-regresión; (ii) **D6** queda sin su consumidor natural, así que su
  disparador depende del `acceptance` de FASE-C y no de un proveedor ya probado; (iii) la pregunta de
  geometría de **S10** se paga entera en D7 y su coste real puede ser una edición de plan (re-anclar
  AC6) si se elige la ruta (b); (iv) el manifiesto de dependencias del SDK no lo mide AC9, porque
  medirlo exigiría activarlo. Lo que **no** cuesta: la costura ya está, con su contract test y su
  coste de extensión verificado, así que D7 no reabre FASE-B.
- [x] **FASE-D (2026-09-24), en la misma base de medición que su par pre/post** (R2.3): quick 11→11
  (resta **0**), hook 7→7 (resta **0**), `git diff` de los cuatro scripts gobernados **vacío**, y
  `.agents/` con **cero bytes aportados por la fase** (AC17: el directorio llegó con 3 rutas sucias
  ajenas, así que la casilla literal «`git status --porcelain .agents/` vacío» no era evaluable sobre
  este árbol y se reformuló como contribución propia, medida con el observador de escrituras compartido
  y el `sha256` de todos sus `.md` en el par pre/post). Crudos, comandos y restas en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/faseD_baseline_pre.txt`,
  `…_post.txt` y `baseline-pre-post.md`; **los valores los imprime la corrida, no esta fila**. Lo que sí
  se movió y se declara aparte: selección de tests 0→**49 funciones / 49 casos**
  (`tests/quality_gates/phase_briefing/`, 12 archivos: **10 de test** (los 7 nombrados por el mandato + AC20 + AC23 + el del guard de red) + `conftest.py` + `__init__.py`), y
  canonicas del repo **4.508→4.557** (resta **+49**, reconstruida y cruda en
  `FASE-D/test_count_pre_post.txt` — ver **L-VCF-18**, que nace de ese recomputo).
- [x] Coherencia del índice de lecciones al commitear: `build_lesson_index.py` regenerado el
  2026-09-21 tras escribir los `.md` de esta fase; el commit debe llevar los dos archivos dentro
  (`[6/7]` del hook lo corta). **Cumplido en los dos commits**: `a7564ae` (FASE-A) y `647f436`
  (FASE-B, el 2026-09-22, con `LECCIONES-INDEX.md` 24+/17− y `lecciones_index.json` 100+/14− dentro y
  los **7** checks del hook en verde). **⟦FASE-D, 2026-09-24⟧ la obligación se reproduce sola y ahora
  con un escritor nuevo**: los packs generados son `.md` **dentro del corpus**, así que generan índice
  y a la vez lo vencen — el orden del cierre es generar packs → regenerar el par → comprobar
  `--check`, y **no** al revés (**L-VCF-17**). ⟦Y sigue vigente el límite de **S15**: commitear el par no
  cura el `[FAIL]` de un clon fresco, porque 9 entradas del par sellan su fecha en el `mtime`.⟧ **Ese «sigue
  vigente» se escribió el 2026-09-24 y quedó vencido el 2026-09-26: S15 está curada en
  `scripts/build_lesson_index.py`** (la rama `mtime` fue **retirada** de las fuentes admitidas; la fecha sale
  del nombre del plan, del último commit que tocó su documento, o del estado explícito `SIN-FUENTE`, y el
  `--check` imprime `[fechas] nombre=… commit=… sin_fuente=…` en verde **y** en rojo). Commitear el par dejó
  de ser la condición que se podía incumplir, y un `[FAIL]` de índice en un clon fresco ya no es S15: hay que
  leer primero esa línea. Las «9 entradas» eran **11 de 339**, de **dos** dueños y no de uno
  (`Historico/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL` 9, `Historico/CONTEXT-DT-3-TECH-DEBT-POST-DT2` 2,
  etiquetados por stem); su medición y el límite que la cura conserva están en la fila S15 de §Seguimientos,
  que es la fuente única. Lo que **este punto no** venció: el orden de la cola — escrituras → packs → par →
  dos `--check` → `--quick` — sigue siendo el que manda, porque escribir corpus sigue venciendo el par.
- [x] **Carga de lectura por fase, antes y después del pack (AC20)** — analizada por referencia a
  `09` §D y `carga.json`, con su comando (`stat -c %s`) y su divisor (4) y **sin transcribir cifras
  aquí**: este documento entra al pack de FASE-RELEASE que ese comando mide, así que cualquier número
  copiado de `carga.json` a esta fila queda vencido por la propia copia (A6 sobre un artefacto
  derivado). Lo que sí es estable y es el hallazgo: **el delta queda muy por debajo del tercio que el
  plan esperaba**, porque el workflow canónico sigue leyéndose aparte en los dos lados mientras D3 no se
  ejecute. ⟦Bloque C, 2026-09-24⟧ el delta se analiza **entre cargas totales** (workflow obligatorio +
  coste de generar el pack + pack leído), no entre «fuentes» y «pack»: concatenar no es ahorrar, y aquí
  solo se declara el ahorro que corresponde a lo que el pack **no** incluyó.
- [ ] Aceptabilidad del triaje (AC15): referencia a `09` §D y `coverage.json`; el tramo semántico queda
  `NO-EJERCITADO` con proveedor falso, sin simular una cifra. **⟦FASE-D, 2026-09-24⟧ sigue sin
  ejercitarse y D6 sigue dormida**: D no re-abrió C (mandato), y el `acceptance` de `coverage.json` no
  cambió de valor ni de motivo.
- [x] **Frescura del pack sin circularidad (AC21)**: la caducidad la gobierna el sha de las fuentes
  relevantes; HEAD es procedencia. Un HEAD distinto con fuentes idénticas no vence el pack, porque el
  commit que guarda el generado no puede ser su causa de caducidad. Referencia a la evidencia de FASE-D,
  sin transcribir cifras. **Aplicado y probado**: `test_briefing_head_no_es_la_llave_de_caducidad`
  fabrica el HEAD del pack y el veredicto no se mueve, `procedencia_distinta` se reporta sin ser fatal,
  y el pack **no** figura entre sus propias fuentes (`gobernada = False`). **Contrapartida medida**: la
  no-circularidad es con respecto al *commit*, no al *disco* — editar cualquiera de los documentos que
  el pack embeddinga sí lo vence, y por eso el cierre regenera los packs **después** de editar los
  documentos y vuelve a pasar el `--check` sobre ese árbol final.

## Decisiones Arquitectónicas

- [x] El pack se genera dentro del plan y **no** sustituye ninguna lectura canónica (alternativa
  descartada: rebanar `.agents/`, que es D3 y exige tocar configuración central en vuelo).
  **Aplicado el 2026-09-24 y legible en el artefacto**: cada pack abre su `no_incluye` con el workflow
  canónico declarado como `lectura_aparte_obligatoria`, y el `sha256` de todos los `.md` bajo `.agents/`
  sale idéntico en el par pre/post de FASE-D (AC17). Coste aceptado y dicho: es la razón por la que
  AC20 no cierra en el tercio que el plan esperaba.
- [ ] **El destino de un artefacto generado es parte de su contrato** (FASE-D, 2026-09-24): los packs se
  escriben en `<plan>/briefing/` porque `.opencode/plans/` es el único territorio que una fase de este
  plan puede escribir sin autorización extra, y eso los convierte en corpus para todo verificador que
  recorra el plan por patrón de ruta. Alternativas descartadas con su coste: (a) escribir en
  `evidence/<PLAN>/FASE-D/` — saca los packs del territorio del executor, que los busca junto al plan, y
  deja el briefing sin ruta canónica donde abrirlo; (b) escribir en `.agents/workflows/` — prohibida por
  AC17, que es precisamente la superficie que este plan no toca. La regla que queda: **generar →
  regenerar el índice → volver a comprobar**, y declarar las familias que el generado introduce
  (`coverage_basis.familias_no_cubiertas`) en vez de fingir que no son corpus (**L-VCF-17**).
- [x] FASE-B deja un solo proveedor configurable y **no** compara (alternativa descartada: mantener
  el AC9 de comparación, que con un solo proveedor se cerraba declarando `NO-EJERCITADO` y certificaba
  humo). **Aplicado el 2026-09-21 y legible en el artefacto**: `extensibilidad.txt` declara que la
  comparación es D7 y `costura.json` certifica la geometría con `1`.
- [x] La resolución del proveedor es **por entorno y sin default** (aplicado el 2026-09-21).
  Alternativas descartadas con su coste: (a) *proveedor por defecto si el entorno falta* — es
  exactamente lo que L-PF6 castiga: una decisión que nadie pidió; (b) *un registro central de
  proveedores que la puerta importa* — cerraba AC9 en **2** archivos (el nuevo más el registro), que es
  el número que la medición rechazó; (c) *descubrimiento por `entry_points` o paquetes instalados* —
  habría obligado a instalar el SDK para probar la costura, rompiendo el cero red y el «sin
  credencial». Coste de la ruta elegida: el directorio de proveedores lo nombra el entorno y no hay
  ruta por defecto que descubrir, así que `NO-CONFIGURADO` imprime la ruta que buscó.
- [x] La `confidence` es **obligatoria** en `choice`/`score` y **prohibida** en `noul`, y la puerta no
  rellena la que falta (aplicado el 2026-09-21, con su mutante `M-AC7-forma-choice` y su prueba
  anti-default). Alternativa descartada: aceptar un `noul` con confidence rellenada a 1.0, que
  fabricaría el eje con el que FASE-C separa «actué» de «no estoy seguro» (AC12).
- [ ] El triaje es aditivo y no filtro, con el coste de esa elección medido en FASE-C.
- [x] **⟦Contrato de C cerrado el 2026-09-23; su EJECUCIÓN sigue pendiente⟧** La pregunta de
  pertinencia es **`choice` de dos opciones**, no `noul`. Alternativa descartada y cara: usar `noul` y
  leer `probabilidad_si` como si fuera confianza — la puerta **prohíbe** `confidence` en `noul`
  (`RespuestaNoul.confidence = None` con su `confidence_motivo`), así que ese umbral gobernaría otra
  cosa y cerraría AC12 con una métrica que el AC no describe. Coste de la ruta elegida: cada candidato
  carga dos números y hay que publicarlos separados.
- [x] **⟦Contrato de C cerrado el 2026-09-23⟧ AC11 toma la ruta (b):** C consume
  `lecciones_index.json` **tras ejecutar él mismo** la comprobación de frescura. Alternativas
  descartadas con su coste: (a) `build_lesson_index.build()` en memoria — un solo lector y sin verde
  heredado, pero **borra el estado `VENCIDO`**, y AC11 pide tres estados; (c) la tercera vía prohibida
  por L-V2.2 — leer el JSON confiando en que `[6/7]` del hook lo regeneró, que es heredar un verde de
  otro gate. Coste de (b): C es responsable de su suelo y hace dos lecturas del JSON por corrida.
- [x] **⟦Contrato de C cerrado el 2026-09-23⟧ Una propuesta del proveedor falso NO entra en §2 sin
  revisión humana.** Alternativa descartada, que era la instrucción original del paso 6 del prompt de
  C («aplica lo que proponga»): auto-escribir en el documento de lecciones una fila cuya única
  evidencia es la respuesta de un fixture determinista — fabricaría la pertinencia que AC15 declara
  `NO-EJERCITADO`, y es la familia `VACUOUS_RECALL` que la matriz §2 ya rechazó. Coste aceptado: C no
  puede cerrar «se auto-trió y aplicó» en una sola sesión; el rechazo se publica igual que la
  aceptación, porque una fila de §2 no desaparece (AC10).
- [x] **⟦Contrato de C cerrado el 2026-09-23⟧ C conserva el workflow canónico y el proceso común
  vigentes** (orden de calidad §4.C: el bloque C y el piloto FASE-C siguen **sin autorización**;
  B está autorizado; su estado se consulta en la fuente única. Los dictámenes anteriores se conservan
  retirados; rige la matriz §13 de la fuente única indicada al inicio).
  ⟦**Vencido en parte el 2026-09-24**: el **bloque C** de esa orden se autorizó y ejecutó ese día como
  enmiendas documentales sobre los cuatro planes (§4.C y su resumen único en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`); **el piloto
  FASE-C sí sigue sin autorización**. Lo que esta entrada afirma no cambia: esas enmiendas no tocaron
  el gobierno del proceso, así que C conserva el workflow canónico y el proceso común vigentes.⟧
  Alternativa descartada: aprovechar la sesión piloto para «modernizar» el executor y `AGENTS.md` —
  colaría un cambio de gobierno por arrastre de una fase y rompería la comparabilidad de la medición
  D3/A7, que se hizo contra las reglas actuales. Coste: C vuelve a pagar la lectura de A7 sin alivio.
- [x] Forma de descubrir aserciones en los documentos: **patrón sobre la fuente, no lista fija**
  (decisión aplicada el 2026-09-21 en FASE-A). Alternativas descartadas, con su coste:
  (a) *hardcodear A1–A4* — cerraba AC1 en verde y dejaba el verificador ciego ante la aserción
  siguiente, que es el defecto L-NC10 que este plan denuncia;
  (b) *descubrir sin regla de clases* — producía 8+ hallazgos sobre menciones históricas que el
  propio workflow declara literales, es decir el rojo «por diseño, no por defecto» que A8 anticipó;
  (c) *excluir lo histórico sin publicarlo* — un candado que excluye en silencio (L-HF1).
  Coste de la ruta elegida: dos tablas de marcadores (`KIND_MARKERS`, `HISTORICAL_EVENT_MARKERS`)
  publicadas en el script y mutables: la exclusión es auditable y reversible, no magia.
- [x] FASE-A **no edita `.agents/`** ni toca la composición del `--quick` (AC17/AC16): el verificador
  reporta; la corrección de las cuatro aserciones es D1 con instrucción literal.
- [x] FASE-A **no se cablea** a ningún gate ni al hook: se promueve o no en D2, con la medición de
  quién afirma el 11 ya hecha (AC5/AC16).

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Los cuatro scripts en `scripts/`, con sus tests y su evidencia de mutation check.
- [ ] Ningún AC promocionado sin respaldo legible en el artefacto (R2.4).
- [ ] `--quick` y el hook con su **composición intacta** respecto del par pre/post que mide cada fase
      (AC16, delta 0). El número lo imprime la corrida; este checklist no lo fija.
- [ ] S1–S7 con dueño y disparador vigentes; **D6 declarada dormida con su causa** mientras AC15 publique
      `NO-EJERCITADO` (⟦bloque C⟧ la rama «activada» es inalcanzable sin D7, así que no se deja como
      opción abierta del cierre).
- [ ] Orden del cierre con sus **cuatro** permisos (⟦rectificado 2026-09-25: se escribieron «tres
      momentos»; el tercero era el traslado y faltaba el preflight⟧): **C0 destinos escribibles
      autorizados** → escrituras del cierre → write-back → `git mv` → **refs y citas sin `--fix` ni
      `--update-baseline`** → **regenerar el
      pack con la ruta trasladada** → índice → **check del pack** → `--check` del índice → quick (R2.5, R2.10). Lo remoto
      (D8, D9) y el archivado se ejecutan solo con su autorización propia; sin ella se declaran
      `PENDIENTE-AUTORIZACION`, no se omiten.

### Estado del cierre (2026-09-25, FASE-RELEASE ejecutada en su parte offline)

Cuatro de los cinco cortes están hechos y verificados sobre el árbol final; el quinto —espera de
autorización— es exactamente donde quedaron los permisos.

- **Hecho**: `VERSION.yaml` → 4.78.0 con su codename; sync de cinco cabeceras; `DOMAIN_PRIMER.md`
  regenerado con su writer; `[4.78.0]` en `CHANGELOG.md`; `REGISTRY.md` por su único escritor; y la cola
  derivada (packs → par del índice → dos `--check` → `--quick`) en exit 0. Evidencia:
  `evidence/…/FASE-RELEASE/`.
- **Medido y declarado, no absorbido**: la escritura final de `SyncEngine.sync_rule`
  (`scripts/sync_versions.py`) y la de `run_regenerate_domain_primer` (`scripts/doctor.py`)
  escriben sin `newline="\n"` y reintrodujeron CRLF en seis archivos que git almacena en LF; el detector de
  finales de línea lo cortó y se normalizó por bytes. Y `readme_version_header` no cubre la fecha legible del
  `README.md`, que sigue diciendo «11 Septiembre 2026». **Ninguno de los dos se arregló en código**: no es
  el mandato de esta fase. ⟦**Con dueño y disparador desde el cierre de la orden el 2026-09-25**: son las
  deudas **S17** y **S18**, registradas en `dependencias-fases.md` con su superficie (`scripts/`) y su
  disparador (el próximo mandato que autorice editar esos writers / ese config). Declaradas, **no**
  curadas — la orden lo pidió explícitamente así⟧ ⟦**Vencido ese «no curadas» el mismo 2026-09-25**: una
  sesión posterior, con mandato de código del operador, curó las tres escrituras de S17 y la regla de S18
  (`tests/test_sync_writers_lf_y_fecha_readme.py`, con control contra la versión commiteada). El registro
  de deuda no se reescribe: su estado vigente es §S17 y §S18 de `dependencias-fases.md`⟧.
- **Pendiente con su permiso propio**: consulta Q7 (D8) y `--upload` (D9) —la premisa de D8 quedó **no
  comprobada**—; archivado `git mv`; correcciones de corpus (`--fix`/`--update-baseline`); commit; push.
- **Tres decisiones del operador al cerrar `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` (2026-09-25)**,
  registradas aquí porque afectan el estado de este plan y con su fuente en la propia orden (§6):
  **(1)** el trabajo del **bloque A** de esa orden **permanece bajo «Sin publicar»** en `CHANGELOG.md` y
  `VERSION.yaml` — no se acredita a la entrada 4.78.0; **(2)** la **alineación de política de
  `DOMAIN_PRIMER`** (la divergencia entre «se regenera en FASE-RELEASE» de `AGENTS.md` y «al cerrar cada
  fase de implementación» de `docs/CONTRIBUTING.md` Paso 5b) **queda declarado y no se alinea**: no se
  editó configuración central, y su dueño sigue siendo un mandato literal sobre `AGENTS.md` /
  `docs/CONTRIBUTING.md`; **(3)** las cinco propuestas de revisión humana del piloto
  (`L-VCF-10…14`) se declaran **pendientes con su dueño**: el **operador**, vía la revisión humana que
  fija el contrato **E3** — con proveedor falso una propuesta prueba la mecánica del camino, no la
  pertinencia, así que ninguna entra en §2 por esta sesión y ninguna se rechaza.
- **Sin promociones**: AC15 sigue `NO-EJERCITADO`, D6 dormida con causa, D2/D3/D7/S10/S14/S15/S16
  abiertas con su dueño, y las cinco propuestas de revisión humana (`L-VCF-10…14`) siguen sin aceptar ni
  rechazar, ahora **con dueño nombrado** (casilla anterior). ⟦**S17 y S18 ya no están en esta lista**:
  se curaron el 2026-09-25 en una sesión con mandato de código, no en la del cierre de la orden. Su
  estado vigente es §S17/§S18 de `dependencias-fases.md`⟧. ⟦**S15 tampoco está en esa lista desde el
  2026-09-26**: se curó en `scripts/build_lesson_index.py` con el corte «último commit que tocó el
  documento» ratificado por el operador; de la enumeración original quedan vivas D2, D3, D7, S10, S14 y
  S16. Su estado vigente, sus cifras re-medidas y el límite que la cura conserva viven en la fila S15 de
  §Seguimientos⟧.
- **Lo que este cierre no afirma**: que los cuatro planes del lote estén terminados, ni que exista medida de
  pertinencia real, ni que el trabajo esté versionado: el producto de D, los cierres documentales y este
  expediente siguen **solo en el árbol de trabajo**.
  ⟦**Vencido el 2026-09-26 por la publicación de esta orden**: `970fa7d` lleva las nueve rutas del registro,
  `911f8d7` la cura de S15 con su par de índice y su test, y `2a675fa` las ocho rutas que ninguna de las dos
  listas cubría, incluido este documento. El árbol quedó en `git status --porcelain` = **0** rutas y la
  paridad en `0 3`. De la enumeración de arriba solo seguía en el árbol la nota que escribe esta línea, que
  viaja en el commit siguiente por la razón de siempre: un commit no puede nombrarse a sí mismo.⟧


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md` · sha256 `b66723f1c3c507cc29034b705c24709d72fa88493fba5277ff8f61382d3dc337` · 92574 bytes copiados de 92574 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `05-prompt-inicio-sesion-fase-A.md` (documento completo)

# FASE-A — Lint determinista de aserciones numéricas en documentos de gobierno

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-A
**Objetivo**: escribir `scripts/validate_governance_numbers.py`, que compara cada aserción sobre
un conteo en los documentos de gobierno contra la **fuente dinámica de verdad** (las etiquetas
que el código imprime), publica denominador y expresa los tres estados. Cubre AC1–AC5.
**Dependencias**: ninguna. Es la primera fase de la cadena.
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración
(R3 permite máximo 4 tareas y 0 comandos largos).
**Skill**: `phased_project_executor` (este plan) — no ejecuta la pipeline.

## Contexto

Los documentos de gobierno del repo afirman cuántos checks corren. Cuatro de esas afirmaciones
están hoy vencidas contra el código que las ejecuta, y **ningún check las sostiene**: se
cumplen por coincidencia (L-R.1). Esta fase escribe el verificador; **no** corrige el texto.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| — | Esta es la primera |

`REFACTOR-WHATSAPP-ENTREGA-2026-09-18` está en vuelo y **no es dependencia ni consumidor** de
esta fase. Sus superficies compartidas con usted, medidas el 2026-09-20, son **dos**: la pareja
`.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (la regenera cualquier `.md` de
plan que nombre un ID, y `[6/7]` del hook lo exige en el mismo commit) y **la cifra que ese plan
pinea** — 11 checks del `--quick` — que no está en su prompt de FASE-C sino en cuatro documentos
suyos: el bloque de arranque de FASE-B de su `README.md`, su `06-checklist-implementacion.md`, su
`09-documentacion-post-proyecto.md` y su `10-analisis-post-implementacion.md`. Por eso AC16 se formula
como delta 0. Y **hay un tercer plan en esa superficie**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`
(commiteado, PENDIENTE) declara dentro de su alcance `scripts/run_all_validations.py` — el archivo
cuyas etiquetas son la fuente de verdad de esta fase— y `scripts/validate_qmind_writeback.py`. Usted
**no** lo toca y **no** le pasa nada a FASE-A por eso; lo que cambia es el RELEASE de este plan, que
debe re-leer esa interfaz antes de correr el `--upload` (deuda **D10**).

### Base técnica disponible

- Fuente de verdad de los conteos: `def run_all` en `scripts/run_all_validations.py` ejecuta 11
  checks en modo `--quick` y 4 más solo en modo completo; cada check imprime su etiqueta
  `[N/M]` dentro de su propio método (`def _check_plan_citations`, `def _check_lesson_capitalization`).
- Otra fuente: `scripts/git_hooks/pre-commit`, que declara 7 pasos `[1/7]`…`[7/7]` en su cabecera.
- Objetos auditados (solo lectura): `.agents/workflows/phased_project_executor.md` y
  `.agents/workflows/templates/lecciones-capitalizadas-template.md`.
- Modelo a imitar en forma y alcance: `scripts/validate_plan_citations.py` (reporta, no
  reescribe; alcance hacia delante + delta) y `scripts/validate_lesson_capitalization.py`
  (aplica R2.9 a sí mismo).
- Tests: selecciones acumulativas por plan, no un número absoluto (L-D3).

### Lecciones capitalizadas aplicables a esta fase

Copiadas de `00-lecciones-capitalizadas.md` §2, filtradas por pertinencia a FASE-A.

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-R.1 | Regla que vive solo en el workflow y no en el artefacto, se cumple por coincidencia | Tarea 1: el verificador compara contra la etiqueta que el código imprime, no contra otra frase del documento |
| L-NC10 | Texto estático que ignora la fuente dinámica de verdad | Tarea 1: la lista de aserciones se descubre escaneando los documentos, no se hardcodea como las 4 medidas |
| L-R.3 | Un `[OK]` sin denominador no informa | Tarea 2 / **AC2**: `coverage_basis` es obligatoria; sin ella no puede existir `SIN-HALLAZGOS` |
| L-PF6 | Lector roto leído como ausencia produjo un pain falso con cifra económica | Tarea 2 / **AC3**: un `except` que devuelva «sin hallazgos» está prohibido |
| L-PF10 | Vacío ≠ ausente | Tarea 2 / **AC3**: tres estados, tres tests nombrados por su causa |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Tarea 3 / **AC4**: mutation check **por aserción**, sobre el símbolo real del guard |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: el verde a la primera se declara sospechoso y se explica |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC5**: el conteo se formula como delta con par pre/post, delta esperado 0 |
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | **AC5/AC16**: esta fase no renumera nada y mide quién afirma el 11 y el 7 |
| L-HF1 | Candado con la cobertura equivocada pasa en verde mientras el artefacto miente | **AC2/AC17**: declarar `families_not_covered[]` es AC, no nota al pie |

## Tareas

### Tarea 1: Escanear aserciones contra su fuente

**Objetivo**: `validate_governance_numbers.py` localiza, en los documentos de gobierno, toda
afirmación del tipo «este verificador es el check N de M» o «el hook corre K pasos», y la
contrasta contra las etiquetas impresas por el código.

**Archivos afectados**: `scripts/validate_governance_numbers.py` (nuevo),
`tests/quality_gates/governance_numbers/` (nuevo).

**Criterios de aceptación**: **AC1** — sobre el árbol vigente reproduce exactamente A1–A4 del
maestro §1 y ninguna otra; artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` con `findings[]`
(`assertion_id`, `document`, `claimed`, `observed`, `occurrences[]`). **La población tiene regla
explícita (medición A8 del maestro §1): sin ella este criterio es inalcanzable.** El escaneo de los
dos documentos de gobierno no devuelve cuatro coincidencias sino **22 instancias `[N/M]` en 17
líneas más 2 formas «check N»**; hay que clasificar cada una como **viva** (sostiene una regla
vigente → se contrasta y puede ser hallazgo), **histórica congelada** (mención fechada o dentro de
una entrada de changelog — el propio workflow declara en `v2.24.0` que sus menciones históricas «se
conservan literales» → se excluye **y se publica** en `historical_excluded[]` con su conteo y la
frase que la ampara) o **vigente y correcta** (entra en `assertions_checked` sin generar hallazgo).
Un hallazgo es **una aserción** con sus `occurrences[]`, no una línea: A1 está escrita en dos sitios
del workflow y sigue siendo un hallazgo. Cero coincidencias debe ser indistinguible de «no leí» solo
si falta `coverage_basis`: por eso AC2 es prerrequisito de AC1, no un extra.

### Tarea 2: Denominador y los tres estados

**Objetivo**: publicar la población mirada y distinguir `SIN-HALLAZGOS` / `AUSENTE` /
`LECTOR-FALLIDO`.

**Archivos afectados**: el mismo script y sus tests.

**Criterios de aceptación**: **AC2** (`coverage_basis` con `documents_scanned`,
`assertions_checked`, `families_not_covered[]`, `excluded[]`) y **AC3** (clave `status`, tres
tests nombrados por su causa, ninguno cubre dos estados).

### Tarea 3: Mutation check y par pre/post

**Objetivo**: probar que el verde es causado por el guard, y dejar constancia de que la fase no
alteró ningún conteo.

**Archivos afectados**: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/`, `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/*_baseline_pre.txt`,
`*_baseline_post.txt`, `baseline-pre-post.md`.

**Criterios de aceptación**: **AC4** (reversión por aserción sobre el símbolo real, dos salidas
en disco; sin el lado rojo AC4 queda ⚠️. **Anclaje L-V2.1**: cada mutante se afirma sobre el
`assertion_id` que dice atacar — mutar la guarda de A2 y obtener «un hallazgo» cualquiera no prueba
nada, porque otra rama puede producirlo) y **AC5** (delta 0 en 11 checks del quick y 7 del hook,
resta comprobada; una resta 0 con tests nuevos declarados = baseline contaminado y no se cierra.
**La pregunta «quién afirma el 11 y el 7» se responde barriendo también `tests/`, no solo los
documentos**: L-V2.3 se capitalizó exactamente porque el rojo vivo estaba en un contract test, y hoy
sigue habiendo uno (`tests/test_validate_plan_closure.py` assertiona `[5/7]` del hook).

## Tests obligatorios

| Test | Archivo | Criterio de éxito |
|------|---------|-------------------|
| `test_governance_numbers_reproduce_A1_A4.py` | `tests/quality_gates/governance_numbers/` | 4 hallazgos con sus `assertion_id` exactos y **nada adicional**; y el inverso de la misma moneda: `historical_excluded[]` publica las menciones congeladas **con su conteo** (A8), así que el verde no puede venir de haber recortado la población a mano |
| `test_governance_numbers_por_asercion_no_por_linea.py` | ídem | A1, escrita en dos sitios del workflow, produce **un** hallazgo con `occurrences[]` de dos entradas: el conteo de hallazgos no depende de cuántas veces se repita la frase |
| `test_governance_numbers_sin_hallazgos.py` | ídem | Estado `SIN-HALLAZGOS` imprime sobre qué midió |
| `test_governance_numbers_ausente.py` | ídem | Estado `AUSENTE` imprime la ruta buscada |
| `test_governance_numbers_lector_fallido.py` | ídem | Estado `LECTOR-FALLIDO` imprime el motivo y **nunca** un favorable ni un 0 |

**Comando de validación**

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/governance_numbers -v
./venv/Scripts/python.exe scripts/validate_governance_numbers.py --report
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — marcar FASE-A ✅ con fecha y notas de ejecución.
2. `README.md` del plan — progreso y contador de ACs con su estado real (⚠️ donde falte el rojo).
3. `06-checklist-implementacion.md` — casillas de AC1–AC5.
4. `09-documentacion-post-proyecto.md` — Sección A (módulo nuevo), B (funcionalidad), D (métricas), E (archivos afiliados).
5. `10-analisis-post-implementacion.md` — fila de FASE-A en el resumen, lecciones nuevas con su
   pertinencia INCLUIR/EXCLUIR, métricas reales, seguimientos, y decisiones con su rationale y
   las alternativas rechazadas.
6. `00-lecciones-capitalizadas.md` — anotar en «Qué cambia» lo que **realmente** pasó; una lección
   citada y no aplicada se marca como tal, **no se borra**; y actualizar §4 al estado del cierre.

Luego, y antes de cerrar la sesión:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A \
  --desc "validate_governance_numbers.py: asercion contra fuente dinamica, denominador y 3 estados (AC1-AC5)" \
  --archivos-mod "scripts/validate_governance_numbers.py,tests/quality_gates/governance_numbers" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

El índice se regenera **en el mismo commit**: esta fase escribió `.md` bajo `plans/` que nombra
IDs (L-R.1, L-NC10, …), y `[6/7]` del hook lo comprueba contra el árbol final (R2.10).

## Criterios de completitud

- [ ] Los cuatro tests pasan y **ninguno** cubre dos estados.
- [ ] `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` contiene el rojo y el verde (AC4). Si falta uno, AC4 es ⚠️.
- [ ] `baseline-pre-post.md` muestra la resta y delta 0 (AC5).
- [ ] `informe.json` tiene `coverage_basis` legible sin abrir el código (AC2).
- [ ] `run_all_validations.py --quick` verde **sin** haber tocado su composición (AC16).
- [ ] Ninguna aserción de `.agents/` fue editada (AC17).
- [ ] Rojos preexistentes ajenos declarados con dueño y causa, no arrastrados ni maquillados.
- [ ] Post-ejecución completa, incluidos `log_phase_completion.py` y el índice.

## Restricciones

- No modificar `scripts/run_all_validations.py`, `scripts/git_hooks/pre-commit`, `.agents/**`,
  `scripts/build_lesson_index.py` ni `scripts/validate_lesson_capitalization.py`.
- No ejecutar `v4complete`, `v4audit` ni la pipeline. No tocar `output/` en modo escritura: los
  artefactos de ahí son históricos y de otro plan.
- No escribir sobre ningún plan vivo, `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` en particular.
- No commitear ni empujar sin instrucción literal del operador.
- Presupuesto: instrumento y corte declarados (R2.1). Si el instrumento no corre bajo la
  política de permisos de la sesión, se publica en la unidad usada y se declara no comparable, o
  se retira la métrica. **Nunca estimada.**

## Prompt de ejecución

Copiar en una sesión nueva:

```text
Ejecuta únicamente FASE-A del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md §1 (la tabla A1-A4 con su rectificacion de
A3, la medicion A7 y la poblacion A8) y §4 (AC1-AC5 con la regla de poblacion, AC16, AC17),
04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4,
dependencias-fases.md y el workflow canónico. **Estado medido del árbol al publicarse la auditoría
(`2c9d0c1`, 2026-09-20, paridad 0/0 con `origin/master` verificada con `git ls-remote`): limpio, con
el índice de lecciones ya regenerado y fresco.** No lo des por supuesto: re-mide HEAD/status al abrir,
porque la pareja del índice la comparte con las fases vivas de `REFACTOR-WHATSAPP` y puede llegarte
modificada. No hay nada que rescatar de una fase anterior —A es la primera de este plan.
Re-mide antes de la primera tarea y publica el numero: git HEAD/status, la etiqueta que imprime CADA
def _check_* (emparejando etiqueta y metodo: [15/15] es el write-back de QMind y [12/15] es
dependencias; confundirlas fue el error de A3), los siete pasos del hook, y el tamano en bytes de los
siete documentos que suma A7 (263.973 al 2026-09-20, no 254.010).
Escribe scripts/validate_governance_numbers.py: compara cada asercion sobre un conteo en los
documentos de gobierno contra la etiqueta [N/M] que el codigo imprime, descubre las aserciones
escaneando los documentos (no hardcodeando las cuatro) **y aplica la regla de poblacion de A8: clase
viva, historica congelada publicada en historical_excluded[], y vigente-correcta contada en
assertions_checked; un hallazgo es una asercion con sus occurrences[], no una linea**, publica
coverage_basis con la poblacion mirada y las **cuatro** families_not_covered medidas (prosa sin
patron, conteos fuera de los documentos de gobierno -AGENTS.md, docs/GUIA_TECNICA.md,
docs/contributing/REGISTRY.md-, pins de conteo en tests/, y fuentes dinamicas que no sean etiqueta
impresa), y expresa los tres estados sin que ninguno colapse.
Reutiliza el disenno de validate_plan_citations.py (reporta, no reescribe) y de
validate_lesson_capitalization.py (R2.9 sobre si mismo).
No toques run_all_validations.py, el hook, .agents/, build_lesson_index.py ni ningun plan vivo.
Todo AC de detencion se cierra con mutation check sobre el simbolo real del guard, por asercion y
**afirmando el assertion_id del mutante (L-V2.1)**,
con las dos salidas en evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/. El conteo del quick (11) y del hook (7) se expresa como
delta con par pre/post y la resta comprobada, delta esperado 0, y la pregunta de quien afirma el 11 y
el 7 se responde barriendo tambien tests/ (L-V2.3).
Cada fase se registra a si misma con log_phase_completion.py y regenera el indice de lecciones
en el mismo commit. Deja checkpoint si falta autorizacion y conserva los ACs en el estado real
que puedan probar: VERIFICADO OFFLINE con rojo y verde, o ⚠️.
```


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-A.md` · sha256 `03cffe5f708db67a566f56dc5c8ecdb5e1b0e43bcd8022608974c052827469d2` · 15552 bytes copiados de 15552 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `05-prompt-inicio-sesion-fase-B.md` (documento completo)

# FASE-B — Costura de proveedor de decisiones, neutra y extensible

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-B
**Objetivo**: escribir `scripts/decision_client.py`, la única puerta del repo a un proveedor de
decisiones estructuradas, con contract test de forma y con **la extensión a un segundo proveedor
probada**. Cubre AC6–AC9.
**Dependencias**: FASE-A ✅ (reutiliza sus tres estados y su convención de `coverage_basis`).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

**Ningún proveedor de pago se activa en este plan.** El acceso existe y está habilitado desde
2026-09-20; el operador decidió posponerlo. Eso no vuelve innecesaria esta fase: la vuelve más barata
y más segura. Lo que se construye aquí es la **costura**, y lo que se certifica es que añadir el
proveedor pospuesto cuesta **un archivo** (AC9). Su activación real es la deuda **D7**, y el primer
consumidor natural es la deuda **D6**, el lint de contradicciones semánticas.

La razón de aislar el proveedor no es estética: el SDK del proveedor rompió compatibilidad dos veces en
sus primeros nueve días público (redefinió los criterios de una primitiva; migró de serializador). Si
el repo se acopla al nombre del proveedor, cada subida rompe fases.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| FASE-A | ✅ — reutilizar `status` de tres estados y `coverage_basis`; no reinventarlos |

### Base técnica disponible

- La costura resuelve el proveedor por variable de entorno. Los dos candidatos que pueden quedar
  detrás, cuando se active D7, son el SDK oficial del proveedor y el **adapter** que el propio
  proveedor publica como reemplazo respaldado por APIs de LLM — el adapter existe precisamente para
  comparar proveedor contra proveedor en costo, velocidad e inteligencia.
- Forma esperada de una respuesta: elección con probabilidades y confianza; nivel ordenado con
  leyenda; binario con probabilidad de sí. La confianza es lo que permite separar «actué» de «no estoy
  seguro», y es el eje que FASE-C usa en AC12.
- Límites que condicionan el diseño y que hay que dejar escritos en el módulo: solo acepta texto; su
  techo de contexto por solicitud es **menor** que la suma de los documentos de gobierno de este repo
  (de ahí que FASE-C chunkee, y que el lint de conteos de FASE-A sea determinista y no pase por aquí);
  y sus modos de fallo documentados son lectura literal, conteo y comparación de fechas.
- Credencial: solo por variable de entorno. **Nunca** se imprime, se pega en el chat ni se escribe en
  evidencia — una clave que aparece en un transcript obliga a rotarla. La evidencia registra
  `provider_status`, jamás el valor. En esta fase no hay credencial en absoluto.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | Tarea 2 / **AC8**: el contract test afirma la **forma**, no los literales del proveedor ni de su versión |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC7**: proveedor no configurado **no** puede producir una decisión por defecto |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC7**: `RESUELTO` / `NO-CONFIGURADO` / `ILEGIBLE`, tres estados, tres tests |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC6**: el escaneo de imports se publica con su población, no como «0 coincidencias» a secas |
| L-R.3 | Un `[OK]` sin denominador no informa | **AC6/AC9**: todo conteo lleva la población que lo sostiene |
| L-R.4 | Regla sin verificador es publicable solo si lo declara | **AC9 y D7**: la comparación de proveedores se declara **fuera de alcance**, no se omite |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: el verde sin rojo previo se reporta sospechoso |

## Tareas

### Tarea 1: La costura y sus tres estados

**Objetivo**: `decision_client.py` con contrato propio (`evaluar(state, preguntas) → respuestas
tipadas`), resolución de proveedor por entorno, y fallo explícito cuando no hay proveedor o la
respuesta es ilegible.

**Archivos afectados**: `scripts/decision_client.py` (nuevo),
`tests/quality_gates/decision_client/` (nuevo).

**Criterios de aceptación**: **AC6** (ningún archivo fuera del script importa SDK o adapter alguno;
artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` con conteo **y** población escaneada) y **AC7** (clave
`provider_status`, tres tests nombrados por su causa; prohibido el `except` que devuelve un valor que
pueda leerse como decisión). Sin proveedor configurado, `evaluar()` **falla**; no devuelve una
heurística.

### Tarea 2: Contract test de forma

**Objetivo**: fijar la forma de la respuesta para que una subida de SDK rompa **este** test y no a una
fase de otro plan.

**Criterios de aceptación**: **AC8** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` con el nombre del test
y su salida; versión de modelo pineada y declarada; se prueba que **alterar la forma del proveedor
falso lo pone rojo**. Prohibido pinear el número de checks ni literales del proveedor (L-V2.3).

### Tarea 3: Extensibilidad probada, no prometida

**Objetivo**: registrar un **segundo proveedor falso** a través de la costura y demostrar cuánto cuesta.
No se conecta ningún servicio real.

**Criterios de aceptación**: **AC9** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` con la clave
`files_changed_to_add_provider` (valor esperado `1`; si es mayor, se explica cuál y por qué) y
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt` con la salida del test que añade el segundo proveedor sin tocar
ningún otro módulo. **No hay comparación de proveedores en este plan**: con uno solo no hay elección
que medir, y exigirla produciría un `NO-EJERCITADO` que certifica humo. La comparación es deuda D7.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_decision_client_provider_no_configurado.py` | `NO-CONFIGURADO`, sin decisión por defecto |
| `test_decision_client_respuesta_ilegible.py` | `ILEGIBLE` con el motivo; nunca un favorable |
| `test_decision_client_contract_forma.py` | La forma fijada; alterarla rompe el test (**rojo**) |
| `test_decision_client_aislamiento_imports.py` | AC6 sobre el árbol real, con población |
| `test_decision_client_segundo_proveedor_un_archivo.py` | AC9; `files_changed_to_add_provider == 1` |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/decision_client -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-B ✅ con fecha y notas.
2. `README.md` — progreso y estado real de AC6–AC9.
3. `06-checklist-implementacion.md` — casillas correspondientes.
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D, E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas con pertinencia, métricas
   reales, seguimientos y decisiones: **qué se pospuso (D7) y qué coste tiene posponerlo**.
6. `00-lecciones-capitalizadas.md` — «Qué cambia» con lo que realmente pasó; §4 al estado del cierre.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B \
  --desc "decision_client.py: costura neutra, contract test de forma y extensibilidad a un segundo proveedor probada (AC6-AC9)" \
  --archivos-mod "scripts/decision_client.py,tests/quality_gates/decision_client" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] Los cinco tests pasan; ninguno cubre dos estados.
- [ ] `contract.txt` demuestra el rojo al alterar la forma y el verde con la forma actual (AC8).
- [ ] `costura.json` reporta `files_changed_to_add_provider`, con su valor o su explicación (AC9).
- [ ] Cero llamadas de red en toda la fase: verificable, no afirmado.
- [ ] Ninguna evidencia ni log contiene credencial alguna, ni parcial ni enmascarada.
- [ ] `--quick` verde sin haber tocado su composición (AC16).
- [ ] Post-ejecución completa, incluido el índice regenerado en el mismo commit.

## Restricciones

- **No se activa ningún proveedor real ni se hace una sola llamada de red.** Lo certificado aquí es la
  forma y el aislamiento.
- No importar el SDK ni el adapter en ningún otro archivo (es AC6, no estilo).
- No modificar `.agents/**`, `run_all_validations.py`, el hook, `build_lesson_index.py` ni
  `validate_governance_numbers.py` (es de FASE-A: consúmalo, no lo reescriba).
- No enviar a ningún proveedor contenido del plan `REFACTOR-WHATSAPP` ni material del cliente.
- No ejecutar la pipeline. No commitear ni empujar sin instrucción literal.
- Presupuesto con instrumento y corte declarados (R2.1); nunca estimado.

## Prompt de ejecución

```text
Ejecuta unicamente FASE-B del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-B.md, 01-plan-maestro.md §2 (las filas del proveedor y D7) y §4
(AC6-AC9, AC16, AC17), 04-contrato-ejecucion.md (permisos y la regla de cero red),
00-lecciones-capitalizadas.md §2, dependencias-fases.md y el workflow canónico.
Heredas de FASE-A los tres estados y la convencion coverage_basis: reutilizalos.
Escribe scripts/decision_client.py como unica puerta del repo a un proveedor de decisiones: contrato
propio, proveedor resuelto por variable de entorno, fallo explicito cuando no hay proveedor o la
respuesta es ilegible, y nunca una decision por defecto.
Cero llamadas de red: por decision del operador no entra Jev en este plan. AC6: ningun otro archivo
importa el SDK ni el adapter, con el conteo y su poblacion. AC8: contract test que se pone ROJO si
altera la forma del proveedor falso, sin pinear literales del proveedor. AC9: registra un segundo
proveedor falso a traves de la costura y publica files_changed_to_add_provider; si es mayor que 1, lo
explicas. La comparacion de proveedores NO es de este plan: es la deuda D7.
La credencial no se imprime, no se pega ni entra en evidencia: se registra provider_status.
No toques .agents/, run_all_validations.py, el hook, validate_governance_numbers.py ni ningun plan
vivo. Registra la fase con log_phase_completion.py y regenera el indice en el mismo commit. Deja
checkpoint si falta autorizacion.
```

---

## Nota de cierre de esta fase (2026-09-23) — no reconstruye las instrucciones de arriba

**Esta fase ya se ejecutó: FASE-B cerró VERIFICADO OFFLINE el 2026-09-21 y se commiteó el 2026-09-22
en `647f436`. Este prompt queda como histórico de esa sesión y no debe volver a ejecutarse.** Tres
rectificaciones que el texto de arriba no contenía cuando se escribió, y que la fase produjo al
commitearse:

- **S11 y S12** nacieron del propio commit de la fase y fueron corregidas **fuera de este plan** por el
  bloque A de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` (`fdd397f`); su **aceptación** por el plan
  propietario está en `dependencias-fases.md` §Conciliación. La guarda que esta fase publicó en el
  README sobre `validate_governance_numbers.py --report` sin destino **ya no aplica**.
- **AC9 se declaró con alcance local**: certifica añadir un proveedor **falso** del repo
  (`files_changed_to_add_provider = 1`, medido por sha256, sin red ni credenciales), **no** el coste de
  integrar un SDK real con sus dependencias y su autenticación. Su texto original («añadir el segundo
  cuesta un archivo») se leía como lo segundo.
- La instrucción de arriba sobre **`log_phase_completion.py` ya está cumplida y no se repite**: la fase
  tiene su entrada en `REGISTRY.md`. Volver a registrarla duplicaría la entrada, y ningún cierre de
  esta fase mueve `VERSION.yaml` (el bump pertenece a RELEASE).

Dónde quedó cerrado y qué quedó abierto (S10, D6, D7): `10-analisis-post-implementacion.md` y
`06-checklist-implementacion.md`.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-B.md` · sha256 `0f4e51282983f59cc79bb13d7536bf7bf0a732e38a275464a632757f1ef90006` · 12245 bytes copiados de 12245 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `05-prompt-inicio-sesion-fase-C.md` (documento completo)

# FASE-C — Capa de pertinencia sobre el índice de lecciones (aditiva, nunca filtro)

> **Estado de este prompt al 2026-09-24: CONTRACTUALMENTE PREPARADO, NO EJECUTADO.** FASE-C sigue
> siendo la sesión siguiente y **no** se corrió ni al conciliar FASE-B ni al redactar las enmiendas del
> bloque C de la orden de calidad. Contiene cinco enmiendas
> prospectivas ya resueltas por este plan (**E1–E5** en `04-contrato-ejecucion.md`, orden de calidad
> §4.C, con autorización local del operador sobre CONTEXTO/C): la elección de fuente de **AC11 está
> cerrada en la ruta (b)**, la pregunta binaria es **`choice` con `confidence` independiente**, las
> propuestas del proveedor falso **no** entran en §2 sin **revisión humana registrada**, el tramo
> semántico de **AC15** sigue `NO-EJERCITADO` con **D6 dormida**, y **C conserva el workflow canónico y
> el proceso común vigentes**. ⟦Actualizado el 2026-09-24⟧ el **bloque B está concluido
> contractualmente por su matriz §13** y el **bloque C de esa orden quedó autorizado solo como
> enmiendas prospectivas sobre los documentos de los cuatro planes**; **el piloto FASE-C —es decir,
> ejecutar este prompt— sigue sin autorización**. Fuente única de resultados y estados B/D1/S13:
> `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
> **§13, única matriz vigente**; §1–§12 y los dictámenes anteriores quedan como antecedentes
> rectificados, no aceptación actual. Evidencia de las enmiendas:
> `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`. Donde
> una instrucción de este archivo contradiga ese párrafo, manda el párrafo y está mal conciliado: decirlo.
>
> **Reconfirmación contra el cliente real (2026-09-24, sin renegociar).** E1 y E2 se volvieron a
> contrastar con `scripts/decision_client.py` y su forma sigue siendo la que asumen: `RespuestaEleccion`
> exige `confidence` en su validación y `RespuestaNoul` la fija en `None` con la puerta **rechazando**
> que un `noul` la reporte. Ninguna de las cinco enmiendas se mueve; lo que cambió en este bloque es lo
> que la fila `CONTEXTO/D` y `CONTEXTO/RELEASE` pedían, no la forma de la pregunta ni el destino de las
> propuestas.

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-C
**Objetivo**: escribir `scripts/triage_lesson_relevance.py`, la mitad que
`validate_lesson_capitalization.py` declara fuera de alcance: **si la lección capitalizada era la
pertinente y cuáles quedaron fuera**. Cubre AC10–AC15.
**Dependencias**: FASE-A ✅ (estados y denominador) y FASE-B ✅ (la costura es la única puerta al proveedor).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

El Paso 0 del executor produce `00-lecciones-capitalizadas.md` y su verificador corta en el
commit. Pero ese verificador dice de sí mismo, en su docstring, que un `[OK]` suyo significa
**«la forma exigida está», nunca «capitalicé bien»**: no puede saber si la lección que debía
capitalizarse era otra. Esta fase escribe exactamente esa otra mitad.

Y lo escribe con una restricción que nace de un hecho medido dos veces: un plan cuyo objetivo de
entrega era inalcanzable porque un hallazgo CRITICAL registrado en el corpus no lo cubría ninguna
fase, y hubo que crearle una fase y un AC nuevos. **Un filtro de pertinencia que descarte en
silencio una premisa carga-estructura reproduce ese fallo.** Por eso el triaje de este plan es
aditivo por construcción y eso es AC, no intención.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| FASE-A | ✅ — reutilizar `status` de tres estados y `coverage_basis` |
| FASE-B | ✅ — usar `decision_client.py`; prohibido importar el SDK directamente |

### Base técnica disponible

- Suelo determinista: `.opencode/lecciones_index.json`, generado por `scripts/build_lesson_index.py`.
  Población medida y **re-medida tras regenerar el índice al concebir el plan**: **320** IDs con
  definición detectada, **50** citados sin definición, 15 análisis + 36 `CONTEXT-*.md` como corpus
  de definiciones, **402** `.md` como corpus de citas. Las tres últimas cifras decían 14 / 49 / 389
  hasta que este propio plan entró al corpus (maestro §1, medición A6). El índice se regenera y
  `--check` lo corta en `[6/7]` del hook; **no se edita a mano**.
  **⟦Aviso añadido el 2026-09-23, familia A6⟧.** Esas cuatro cifras son **antecedentes fechados**, no el
  valor con el que se abre la sesión: al 2026-09-23 `build_lesson_index.py --check` reporta **332 IDs**
  definidas, y la cifra se mueve cada vez que alguien define un ID nuevo en cualquier `.md` del corpus —
  incluida esta sesión. **AC15 y AC11 calculan su denominador sobre la lectura que hace C de su propio
  check**, y publican cifra + comando + fecha; prohibido pinear 320/50/15/402 ni 332 en un test (L-V2.3).
  Comando de apertura: `python scripts/build_lesson_index.py --check`.
- Formatos a emular: `scripts/validate_lesson_capitalization.py` (checks C1–C8, R2.9 sobre sí
  mismo, reporta sin reescribir) y su artefacto de plan (§1 consultas, §2 capitalizadas con «qué
  cambia», §3 ≥3 descartes, §4 cobertura).
- Precedente del defecto que esta fase mide: al concebir el plan, `grep -icE "verificador mec"`
  devolvió **0** sobre el índice en un corpus que sí contiene verificadores nombrados con otras
  palabras. Un cero de grep no distingue «no existe» de «término equivocado».

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-R.3 | Un `[OK]` sin denominador no informa | Tarea 3 / **AC15**: población mirada, términos usados y cuántos IDs recibieron juicio |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC11**: un JSON del índice que reviente jamás devuelve «sin candidatos» |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC11**: `AUSENTE`, `VENCIDO` y `LECTOR-FALLIDO` son tres estados propios —el primero con ruta y comando de regeneración, el segundo con el check **propio** de C (⟦E2⟧), el tercero con el motivo del parseo |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto que genera **otro** gate | Tarea 1 / **AC11**, ⟦decisión cerrada el 2026-09-23⟧: C toma la **ruta (b)** — consume el JSON **tras** ejecutar él mismo la comprobación de frescura, con `VENCIDO` como estado propio y su costo publicado |
| L-VCF-12 | Antes de correr un verificador con `--report`/`--write`, mirar si su default toca evidencia commiteada | Cierre del plan: **la guarda particular cayó** (S12 aceptada el 2026-09-23; `validate_governance_numbers.py --report` sin destino ya imprime y no escribe), **la regla general sigue** — y aplica al `--report` del propio `triage_lesson_relevance.py`: C debe publicar el destino de su informe, no heredar una ruta por defecto dentro de la evidencia de otra fase |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC10**: la comparación §2 antes/después es un delta, no una lista que deba coincidir |
| L-HF1 | Candado con cobertura equivocada pasa en verde mientras el artefacto miente | **AC15/AC17**: decir qué familias de lección no se juzgan (IDs numéricos, familias fuera de `L-*`/`DA-*`/`D-*`/`S-*`) |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Tarea 2 / **AC14**: mutation check sobre el guard real de AC10, no sobre un duplicado dentro del test |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: sin rojo, AC14 es ⚠️ |
| L-R.4 | Regla sin verificador es publicable solo si lo declara | **AC12**: el umbral se publica con valor, base y acción por debajo |
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | Restricción: esta fase no toca el quick (11) ni el hook (7) |

## Tareas

### Tarea 1: Leer el suelo determinista sin colapsar estados

**Objetivo**: cargar `lecciones_index.json`, distinguir presente/faltante/vencido, y derivar el
conjunto de candidatos **sin** quitar ninguna fila ya anclada.

**Elección de fuente — ⟦RESUELTA el 2026-09-23 (orden §4.C / contrato E2)⟧: se toma la ruta (b).**
El suelo determinista es `.opencode/lecciones_index.json`, y **C ejecuta ella misma la comprobación de
frescura antes de apoyarse en él** (Knowledge Center, `L-V2.2` de
`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`: un verificador **no** apoya su conclusión en el artefacto
que genera otro gate — el JSON lo produce `[6/7]` del hook, y la cura que implementó ese plan fue
calcular el índice **en memoria** con `build_lesson_index.build()`, 0,30 s medidos). La elección ya está
tomada en el plan: C **no** decide de nuevo, **implementa** (b) y publica su costo:

- `VENCIDO` es **estado producido por el check propio de C**, no por un `--check` ajeno. (Con la ruta
  (a) este estado habría desaparecido y AC11 pediría tres estados a un diseño de dos — razón de cerrar
  la elección aquí y no en la sesión.)
- **Prohibida la tercera vía**: leer el JSON confiando en que otro paso lo regeneró. **Que el archivo
  exista no es que esté fresco.**
- **Tres causas, tres tests, ninguna colapsable** (R2.9): `AUSENTE` (no hay archivo en la ruta buscada →
  imprime ruta y comando de regeneración) ≠ `VENCIDO` (existe y se lee, pero el check propio no lo
  aprueba → imprime qué lo venció y el comando) ≠ `LECTOR-FALLIDO` (existe pero revienta al parsear →
  imprime el motivo). Un JSON roto **jamás** devuelve «sin candidatos».
- **Coste declarado:** C es responsable de su suelo y hace dos lecturas del JSON por corrida (la del
  check y la del consumo) en lugar de heredar un verde.

**Archivos afectados**: `scripts/triage_lesson_relevance.py` (nuevo),
`tests/quality_gates/lesson_relevance/` (nuevo).

**Criterios de aceptación**: **AC11** (`index_status`; `AUSENTE` imprime la ruta buscada y el
comando de regeneración; `VENCIDO` imprime qué check del hook lo detecta) y **AC10** (artefacto
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` con `anchored_before`, `anchored_after`, `removed: []` y un
test que lo afirma).

### Tarea 2: Juicio de pertinencia aditivo, con umbral declarado

**Objetivo**: por candidato no capitalizado, una pregunta binaria a través de `decision_client.py`;
separar `propuesto` de `a-revisar-humano` por confianza. **Nunca autofiltrar.**

**Forma de la pregunta — ⟦RESUELTA el 2026-09-23 (orden §4.C / contrato E1)⟧: `choice` de dos
opciones, y la confianza es un campo distinto de la probabilidad de sí.** Confirmado contra
`scripts/decision_client.py` (no contra su docstring): `RespuestaEleccion` lleva `eleccion` +
`probabilidades` sobre **todas** las opciones + **`confidence` obligatoria**, mientras `RespuestaNoul`
lleva solo `probabilidad_si` con **`confidence = None` y su `confidence_motivo`** — la primitiva no la
expone y la puerta la **prohíbe** ahí. Por eso:

- La pregunta de pertinencia **no** se formula como `noul`. Con `choice` de dos opciones se obtienen
  **los dos números por separado**: cuánto se inclina por «pertinente» y con cuánta confianza leyó la
  pregunta. Son cosas distintas y el AC12 pide una de las dos.
- El `threshold` se aplica a **`confidence`**, y su `basis` **nombra el campo**. Umbral sobre
  `probabilidad_si` = cerrar AC12 con una métrica que el AC no describe.
- Publicar ambos es válido y deseable (`por_si` y `confidence` en cada candidato); **equipararlos, no**.

**Qué se hace con lo propuesto — ⟦RESUELTA el 2026-09-23 (orden §4.C / contrato E3)⟧: nada en
automático.** Un candidato que sale del proveedor **falso** prueba la mecánica del camino, no que la
lección sea pertinente. Se va a `a-revisar-humano` y **sólo** entra en §2 del `00-` tras **revisión
humana explícita**, dejando **aceptación o rechazo registrados con quién lo decidió**. Un rechazo se
publica con su motivo: una fila de §2 no desaparece (AC10). El script **no** escribe §2.

**Criterios de aceptación**: **AC12** (clave `threshold` con `value`, `basis` —que nombra
`confidence`—, `action_below`) y **AC14** (mutation check sobre el símbolo real que impide el
filtrado: desactivado el guard, el test de AC10 debe ponerse rojo; evidencia en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`).

### Tarea 3: Denominador, términos y prueba contra corpus real

**Objetivo**: publicar a cuántos de los 320 IDs se aplicó juicio con qué términos, y probar al
menos un caso contra archivos **reales** de `Archives/`, no contra fixture propio.

**Criterios de aceptación**: **AC13** (test contra corpus real archivado con `skipif` explícito;
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` declara si el test **corrió o se saltó** — un skip silencioso es la
variante muda del mismo defecto) y **AC15** (`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` con población,
términos, ceros incluidos, familias no juzgadas y `acceptance`).

**Cómo se cierra AC15 sin proveedor activo** — y es el caso de este plan, porque el proveedor quedó
pospuesto (deuda D7): el triaje se ejercita contra el **proveedor falso determinista** que define
AC8/AC9 de FASE-B. Eso prueba la mecánica —aditividad, estados, umbral— pero **no** produce un número
de aceptabilidad real. Entonces `acceptance` se publica como `NO-EJERCITADO` con el motivo literal,
AC15 queda en ⚠️ y **D6 permanece dormida**: no se abre un lint de contradicciones sobre una base que
nunca juzgó nada. Re-evaluar D6 toca cuando exista proveedor real, no antes.

⟦Reafirmado el 2026-09-23 como contrato E4, para que no dependa de leer este párrafo⟧: **está
prohibido simular la aceptabilidad con el proveedor falso** para poder cerrar AC15 en verde. El
`acceptance` es el disparador medible de una deuda ajena (D6); fabricarlo convertiría un número
pendiente en evidencia falsa y, peor, abriría un lint semántico sobre una base que nunca juzgó nada.
Lo que C entrega aquí es la parte **no semántica** de AC15 —población, términos con sus ceros,
familias no juzgadas— y el `NO-EJERCITADO` con su motivo.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_triage_no_elimina_fila_anclada.py` | AC10; `removed == []` sobre §2 real de este plan |
| `test_triage_indices_ausente.py` | `AUSENTE` con ruta y comando; no «sin candidatos» |
| `test_triage_indices_vencido.py` | `VENCIDO` producido por **el check de frescura propio de C** (⟦E2⟧), no por un `--check` ajeno: árbol movido después de la última regeneración → `VENCIDO` con qué diff lo venció |
| `test_triage_indices_lector_fallido.py` | ⟦tercera causa, añadida el 2026-09-23⟧ JSON existente pero ilegible (roto / no-JSON) → `LECTOR-FALLIDO` con el motivo; **no** es `AUSENTE` ni `VENCIDO` ni «sin candidatos» |
| `test_triage_pregunta_es_choice_y_no_noul.py` | ⟦E1⟧ la pregunta de pertinencia se construye como `choice` de dos opciones; `basis` del umbral **nombra `confidence`** y hay una aserción de que `probabilidad_si` **no** es el campo gobernado |
| `test_triage_propuesta_no_escribe_seccion_dos.py` | ⟦E3⟧ con proveedor falso, una propuesta **no** toca `00-lecciones-capitalizadas.md` §2: va a `a-revisar-humano`, y el rechazo/aceptación queda registrado con quién lo decidió |
| `test_triage_umbral_publicado.py` | AC12 con valor, base y acción por debajo |
| `test_triage_corpus_real.py` | AC13, con `skipif` visible; la evidencia dice si corrió |
| `test_triage_acceptance_no_es_simulado.py` | ⟦E4⟧ sin proveedor real, `acceptance == NO-EJERCITADO` con su motivo; el test falla si la fase fabrica un número con el falso |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/lesson_relevance -v
./venv/Scripts/python.exe scripts/triage_lesson_relevance.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --report
./venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

*(Tabla reemplazada el 2026-09-23: la versión de la concepción listaba cinco tests y ninguno cubría la
tercera causa del índice, la forma `choice` del umbral, el bloqueo de escritura en §2 ni la no-simulación
de `acceptance`.)*

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-C ✅ con fecha y notas.
2. `README.md` — progreso y estado real de AC10–AC15.
3. `06-checklist-implementacion.md` — casillas correspondientes.
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D (fuente de métricas con enlace a la evidencia), E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas (o «sin lecciones nuevas»),
   análisis del delta por referencia a `09` §D, sin transcribir cifras; seguimientos y decisiones
   (incluida la de **no** dejar que el triaje filtre, y su alternativa rechazada).
6. `00-lecciones-capitalizadas.md` — ⟦RESCRITO el 2026-09-23 por la orden §4.C / contrato E3; la
   versión anterior mandaba «aplicar los candidatos que el triaje proponga», y esa instrucción ya **no**
   está vigente⟧. **El triaje se corre sobre el `00-` de este propio plan y se publica, pero sus
   propuestas no entran en §2 por sí solas.** Con proveedor **falso** una propuesta prueba la mecánica
   del camino, no que la lección sea pertinente; escribiría en §2 una fila cuya evidencia es sintética,
   que es justo lo que AC15 declara `NO-EJERCITADO`. El paso es ahora:
   - el script emite el informe con `propuesto` / `a-revisar-humano` y **no edita §2**;
   - cada propuesta recibe **revisión humana explícita**, y su **aceptación o rechazo queda registrada
     con quién la decidió** (fecha + motivo);
   - **aceptada** → entra en §2 con dueño y «qué cambia» reales, citando la revisión que la avala;
     **rechazada** → se publica el rechazo con su motivo. Una fila citada y no aplicada se marca como
     tal, **no se borra** (AC10);
   - en §4 se registra que el plan se auto-trió, con el conteo de propuestas aceptadas y rechazadas y su
     carácter de proveedor falso.
   Y una corrección de forma que este cierre dejó escrita: la guarda que el README publicaba sobre
   `validate_governance_numbers.py --report` **sin destino** quedó **sin efecto** al aceptarse **S12**
   (bloque A de la orden, `fdd397f`) — hoy imprimir sin escribir es el comportamiento por defecto. La
   regla general de la lección **L-VCF-12** sigue en pie.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C \
  --desc "triage_lesson_relevance.py: capa de pertinencia aditiva sobre el indice, umbral publicado y denominador (AC10-AC15)" \
  --archivos-mod "scripts/triage_lesson_relevance.py,tests/quality_gates/lesson_relevance" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] `ac10_delta.json` muestra `removed: []` y hay un test que lo afirma (AC10).
- [ ] Los **tres** estados del índice tienen su test nombrado por la causa; ninguno cubre dos:
      `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO`. ⟦E2, 2026-09-23⟧ `VENCIDO` lo produce **el check de
      frescura propio de C**, no el `[6/7]` del hook, y `LECTOR-FALLIDO` no se colapsa con `AUSENTE`.
- [ ] `mutation/` tiene rojo y verde del guard de no-filtrado (AC14). Sin rojo, ⚠️.
- [ ] `r26.txt` declara si el test contra corpus real **corrió** o se saltó, con el motivo (AC13).
- [ ] `coverage.json` tiene población, términos usados con sus conteos (ceros incluidos), familias
  no juzgadas y `acceptance` real o `NO-EJERCITADO` con motivo (AC15).
- [ ] ⟦E1⟧ El umbral de AC12 está aplicado a **`confidence`** de una pregunta `choice` de dos opciones,
  su `basis` **nombra el campo**, y hay prueba de que `probabilidad_si` no gobierna el umbral.
- [ ] ⟦E3⟧ Ninguna propuesta del proveedor falso entró en §2 sin **revisión humana explícita**; cada
  aceptación y cada rechazo están registrados con quién los decidió, y el script no editó §2.
- [ ] Con proveedor falso, AC15 está en ⚠️, su `acceptance` es `NO-EJERCITADO` con el motivo **y no se
  simuló ninguna cifra** (⟦E4⟧); **D6 quedó declarada dormida** en `dependencias-fases.md`.
- [ ] ⟦E5⟧ C cerró **sin** aplicar las mejoras generales de la orden de calidad: sigue leyendo el
  workflow canónico vigente, no renumeró checks y no tocó el proceso común.
- [ ] `validate_lesson_capitalization.py` sigue verde sobre `00-lecciones-capitalizadas.md` **después**
  de aplicar solo los candidatos **aceptados** (AC18).
- [ ] `--quick` verde sin haber alterado su composición (AC16).
- [ ] Post-ejecución completa e índice regenerado y comprobado sobre el mismo árbol final verificado.
      El commit es opcional, posterior y requiere autorización explícita; no condiciona ninguno de
      los cinco cortes del proceso común.

## Restricciones

- **El triaje propone; jamás descarta.** Ningún camino del código elimina una fila de §2 (AC10).
- ⟦E3, 2026-09-23⟧ **Y tampoco escribe §2 por su cuenta.** Proponer y aplicar son dos pasos: la aplicación
  exige revisión humana con su aceptación o rechazo registrado.
- No modificar `build_lesson_index.py`, `validate_lesson_capitalization.py`,
  `validate_governance_numbers.py`, `decision_client.py` (consúmalos), `.agents/**`,
  `run_all_validations.py` ni el hook.
- No escribir sobre los §2 de **otros** planes, vivos o archivados: el triaje corre sobre el plan
  que se le indique por argumento y su salida es un informe, no una edición.
- No enviar PII ni material del cliente de `REFACTOR-WHATSAPP` a ningún proveedor. Las entradas
  salen del corpus de lecciones del repo.
- ⟦Rectificada el 2026-09-23, porque contradecía el contrato⟧ **Cero red, en serio**: el contrato de
  ejecución no autoriza ninguna llamada real (§Permisos y §Regla de cero red), así que el «tope de 200
  llamadas por sesión» que publicaba esta fila **no es una licencia**: es el techo del `--report` contra
  el proveedor **falso** determinista, y sirve solo para acotar el costo de la corrida local. Si C
  necesita llamar a un servicio real, **para y deja checkpoint** (deuda D7, fuera de este plan).
- No commitear ni empujar sin instrucción literal.

**Deuda que C NO resuelve y no debe tomar como bloqueante** (⟦declarado el 2026-09-23⟧): **S10** (dónde
vivirá el `import` del SDK cuando D7 se active) y **D7** (activar el proveedor) son del tramo que
consume un proveedor **real**; **D6** está condicionada al `acceptance` semántico, que aquí es
`NO-EJERCITADO`. C cierra con proveedor falso **por diseño** del plan, y ninguna de las tres bloquea su
ejecución offline.

## Prompt de ejecución

```text
Ejecuta únicamente FASE-C del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Antes de la primera edicion: mide git status --porcelain, git rev-parse --short HEAD y la paridad con
origin/master con los comandos que publica el bloque «Inicio de la siguiente sesion» del README, y
re-medide el indice con `python scripts/build_lesson_index.py --check`. No copies cifras de este prompt:
son antecedentes fechados y la medicion A6 las mueve.
Lee 05-prompt-inicio-sesion-fase-C.md, 01-plan-maestro.md §1 (la medicion del grep con cero
coincidencias) y §4 (AC10-AC15, AC16, AC18) y §2 (las cuatro filas enmendadas el 2026-09-23),
04-contrato-ejecucion.md (permisos, regla de cero red y la seccion «Enmiendas prospectivas ya resueltas
para FASE-C» E1-E5), 00-lecciones-capitalizadas.md §1-§4, dependencias-fases.md (su fila de C y la
§Conciliacion) y el workflow canónico vigente.
Heredas de A los tres estados y coverage_basis, y de B la costura decision_client.py como unica
puerta al proveedor: no importes el SDK.
Escribe scripts/triage_lesson_relevance.py. Suelo determinista: .opencode/lecciones_index.json, pero
**C ejecuta ella misma la comprobacion de frescura antes de apoyarse en el** (E2; prohibido confiar en
que [6/7] del hook lo regenero). Distingue AUSENTE / VENCIDO / LECTOR-FALLIDO como tres causas con su
test cada una: un lector roto jamas devuelve «sin candidatos» y VENCIDO no es AUSENTE. Propone
candidatos de pertinencia que el Paso 0 no anclo. Es ADITIVO por construccion: ninguna fila de §2
puede desaparecer (AC10, con su test y su delta publicado) y el script tampoco escribe §2 (E3).
Pregunta binaria como `choice` de dos opciones, nunca `noul` (E1): el umbral de AC12 se aplica a
`confidence`, con `basis` que nombra el campo. **La probabilidad de si no es confianza**: son dos
numeros distintos y `RespuestaNoul` no expone confidence. Publication del umbral con valor, base y
accion por debajo. Mutation check sobre el simbolo real que impide el filtrado, con rojo y verde en
evidencia (AC14). Al menos un test contra planes reales de Archives/ con skipif visible, y la evidencia
dice si corrio o se salto (AC13).
Denominador con poblacion, terminos usados incluidos los ceros, familias no juzgadas y acceptance
(AC15). Como no hay proveedor activo, ejercita la mecanica con el proveedor falso determinista y
publica acceptance = NO-EJERCITADO con el motivo: **no simules una aceptabilidad con el falso** (E4);
AC15 queda en ⚠️ y la deuda D6 sigue dormida en dependencias-fases.md. No abras el lint de
contradicciones sobre una base que nunca juzgo nada.
Las propuestas del falso van a `a-revisar-humano` y **solo entran en §2 tras revision humana explicita,
con su aceptacion o rechazo registrado** (fecha, motivo, quien decidio). El rechazo se publica; una fila
no se borra.
C conserva el workflow canonico y el proceso comun vigentes (E5): el proceso comun que dejo el bloque B
de ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md, cuyo estado se lee en la matriz §13 de la fuente unica
citada al inicio, no en los dictamenes retirados. No apliques dentro de la fase ninguna otra mejora
general de esa orden: el bloque C de la orden autorizo enmendar documentos, no cambiar el gobierno del
proceso. Este prompt no se autoriza a si mismo: si tu mandato no nombra explicitamente la ejecucion del
piloto FASE-C, para y deja checkpoint. No renumeres checks: AC16 es delta
0 contra el par pre/post que mide la propia fase, y el numero lo imprime la corrida.
Cero red en serio: si necesitas llamar a un servicio real, para y deja checkpoint (es la deuda D7,
fuera de este plan). No toques build_lesson_index.py, validate_lesson_capitalization.py,
validate_governance_numbers.py, decision_client.py, .agents/, run_all_validations.py, el hook ni ningun
plan vivo. Regenera y comprueba el indice de lecciones sobre el mismo arbol final verificado y registra
la fase con log_phase_completion.py. Los cinco cortes no requieren commit: es opcional, posterior y
necesita autorizacion explicita. Deja checkpoint si falta autorizacion.
Al cerrar, reconcilia la seccion §6 de ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md por referencia: la
casilla del piloto se cierra con la evidencia de esta fase (instrumento, unidad declarada y limites),
y marca expresamente que ni los cuatro planes ni sus deudas externas (D2, D3 completa, D6, D7, S10)
quedan terminados por haber corrido el piloto. No re-transcribas cifras: enlaza a 09 §D y a tu evidencia.
```


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-C.md` · sha256 `ea361c4696797a9a36df482636378040e57c20797af5ec6efd1ef8fc37df0832` · 27571 bytes copiados de 27571 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

## Fuente: `05-prompt-inicio-sesion-fase-D.md` (documento completo)

# FASE-D — Generador de briefing pack por fase y delta de carga de lectura

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-D
**Objetivo**: escribir `scripts/build_phase_briefing.py`, que compone por cada fase un único
archivo con las secciones que su prompt declara leer, y medir el delta de carga de lectura que eso
produce. Cubre AC19–AC23.
**Dependencias**: FASE-A ✅ (estados y `coverage_basis`), FASE-B ✅ (costura, para el candidato de
pertinencia que el pack puede anotar), FASE-C (el triaje cuyo output el pack consume como sección
propia: de ahí se hereda su **parte mecánica medida**; su **aceptabilidad** es `NO-EJERCITADO` mientras
D7 esté inactiva y, por tanto, **no** activa la deuda D6 — contrato E4).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

Medido al diagnosticar este repo: una sesión de fase de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`
declara leer **ocho** documentos y lo hace en ocho lecturas separadas contra un presupuesto de 60
`tool_use`. Siete de ellos entran en la suma de A7 y el octavo es un archivo de `evidence/` que el pie
de esa tabla excluye. **La suma está re-medida el 2026-09-20: 263.973 bytes ≈ 65.993 tokens estimados
(divisor 4)**; al concebir el plan daba 254.010 y creció +9.963 con los cierres de FASE-G y FASE-B del
propio plan medido (maestro §1, A7 y A6). La
mitad de ese volumen es el workflow canónico, y una quinta parte de ese workflow son plantillas de
documentación que solo consumen el cierre y VERIFY.

Esta fase **no rebaná el workflow**: eso es deuda D3, exige tocar `.agents/` (AC17) y reescribir las
nueve citas al workflow canónico que hay en el plan en vuelo. Lo que hace es lo otro: construir el
artefacto derivado que unifica las lecturas declaradas, sin borrar ninguna fuente. Es el mismo
patrón que `build_lesson_index.py`: **se lee la fuente dinámica, se emite un generado, nunca se
edita a mano**.

### Estado de fases anteriores (confirmar en disco al abrir)

| Fase | Estado esperado | Qué aporta esta fase |
|---|---|---|
| FASE-A | ✅ | `status` de tres estados y convención `coverage_basis` |
| FASE-B | ✅ o con AC9 en ⚠️ | La costura; y el hecho de que **no** hay comparación de proveedores en este plan |
| FASE-C | ✅ | Los candidatos de pertinencia, que el pack exhibe como sección propia |

### Base técnica disponible

- Fuente de lo declarado: cada `05-prompt-inicio-sesion-fase-*.md` tiene su lista de lectura en el
  encabezado de tareas y en el bloque «Prompt de ejecución». El generador parsea **esa** lista; no
  se le pasa una configuración a mano.
- Plantilla de estructura de prompt: `.agents/workflows/templates/prompt-fase-template.md`
  (lectura: el generador se ajusta a sus secciones, no las modifica).
- Precedente de artefacto generado con verificador de frescura: `scripts/build_lesson_index.py`
  (`--check`, cortado por `[6/7]` del hook). Modelo de `--check` a emular.
- Salida: el subdirectorio `briefing/` **de este plan** (lo crea esta fase; al concebir el plan aún no
  existe). **Precisión corregida el 2026-09-20**: lo que hace fallar a `validate_opencode_refs.py` no es
  la forma absoluta de la ruta sino **que el destino no exista al escanear** — su regex extrae la cola
  `.opencode/...` incluso dentro de una ruta absoluta, y una referencia relativa a un directorio que
  aún no está creado rompe igual. La regla práctica sigue siendo la de la concepción: **no escribir la
  ruta del pack como referencia `.opencode/...` hasta que FASE-D lo cree**, y pasar `--plan` en el
  arranque cuando exista. **No** va a
  `.agents/workflows/`: los contadores de skills usan `glob("*.md")` no recursivo y un `.md` suelto ahí
  alteraría lo que reporta `validate_agent_ecosystem.py`, además de violar AC17.
- Cero dependencias de proveedor: esta fase es determinista y no llama a ningún modelo. El único
  contacto con el proveedor de decisiones es leer el informe que produjo FASE-C.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | Tarea 2 / **AC20**: el delta de lectura se formula como resta con par pre/post, no como «un tercio menos» |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC22**: una sección declarada y no resuelta **no** puede producir un pack más corto en silencio; es su propio estado |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC22**: si la fuente no existe o no se parsea, el pack se niega a emitirse |
| L-NC10 | Texto estático que ignora la fuente dinámica de verdad | Tarea 3 / **AC21**: el pack declara HEAD, rutas de origen y hash por fuente; `--check` lo vence contra el árbol |
| L-V2.3 | Medir la forma del artefacto equivocado deja pasar el rojo | Tarea 3 / **AC21**: se prueba contra el archivo generado en disco, no contra el objeto en memoria |
| L-R.3 | Un `[OK]` sin denominador no informa | **AC20/AC22**: bytes exactos + tokens **estimados** con el divisor declarado, y la población de secciones miradas |
| L-HF1 | Candado con la cobertura equivocada pasa en verde mientras el artefacto miente | **AC19**: el pack dice qué **no** incluye y qué sigue siendo obligatorio leer aparte |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | **AC23**: mutation check sobre el guard de truncamiento silencioso |

## Tareas

### Tarea 1: Componer el pack desde lo declarado

**Objetivo**: `build_phase_briefing.py --plan <PLAN>` recorre los prompts de fase del plan, extrae
su lista de lectura, resuelve cada sección nombrada y emite `briefing/FASE-X.md` con la sección
copiada y su procedencia al pie.

**Archivos afectados**: `scripts/build_phase_briefing.py` (nuevo),
`tests/quality_gates/phase_briefing/` (nuevo), `…/briefing/` (generado).

**Criterios de aceptación**: **AC19** — el pack se genera para **todas** las fases del plan y
declara `no_incluye[]` y `lectura_aparte_obligatoria[]` (el workflow canónico entra aquí: este plan
no lo rebaná). Ningún archivo bajo `.agents/` es modificado ni copiado como sustituto.

### Tarea 2: Medir la **carga total** de lectura del delta

**Objetivo**: publicar el antes y el después con el mismo comando, sobre las fases de **este** plan
(las de `REFACTOR-WHATSAPP` se reportan como referencia, no como objetivo: sus nueve citas al
workflow canónico siguen intactas).

**⟦Enmendado el 2026-09-24 por la orden de calidad §4.C, fila `CONTEXTO/D`⟧**: el delta no se saca
entre «suma de las fuentes declaradas» y «bytes del pack». Cada lado publica los **tres sumandos** y
la resta va entre totales:

| Sumando | Clave en `carga.json` | Qué contiene |
|---|---|---|
| Workflow y lecturas aparte | `workflow_obligatorio` | Lo que la fase **sigue** leyendo pese al pack: `lectura_aparte_obligatoria[]` completo, con el workflow canónico a la cabeza mientras D3 no lo rebane |
| Coste de producir el pack | `coste_de_generacion` | La invocación del generador que la sesión ejecuta para obtenerlo, publicada tal cual |
| Pack leído | `pack_consumido` | Los bytes del pack que la fase efectivamente lee |

**No equiparar concatenar con ahorrar.** Unir siete documentos en un archivo no baja la suma de sus
bytes y suele subirla (encabezado, procedencia al pie, `no_incluye[]`). El único ahorro que AC20 puede
atribuirse es lo que **dejó de leerse porque no entró al pack**, y eso solo es visible si se publica
también la omisión. Un delta total cero o negativo es resultado válido y se explica (L-D3: un baseline
absoluto hace que cumplir cuente como violación).

**Criterios de aceptación**: **AC20** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` con `before` y
`after` en **bytes exactos** y **tokens estimados con el divisor declarado**, por fase; `method`
con el comando literal de medición; y el par `*_baseline_pre.txt` / `*_baseline_post.txt` con la
resta comprobada (R2.3, R2.7). El delta se reporta por fase y en total; un delta negativo (pack más
grande que leer las fuentes) es un resultado válido y se explica, no se esconde.

### Tarea 3: Frescura por entradas relevantes, proveniencia y negativa a truncar

**Objetivo**: que el pack no pueda mentir por anticuado ni achicarse por error.

**⟦Enmendado el 2026-09-24 (orden §4.C, fila `CONTEXTO/D`) — dos puntos⟧**:

1. **Qué vence el pack.** El predicado de `--check` es el **sha256 de cada fuente listada en
   `sources[]` contra el árbol vigente**, con sus causas distinguibles (`FUENTE-AUSENTE` / sha
   distinto / fuente ilegible). `provenance.head` dice **de qué árbol salió** el pack; no es la llave
   de caducidad. Si HEAD gobernara, el commit que guarda este generado lo dejaría vencido dentro del
   mismo commit — circularidad que la orden prohibió. Por tanto: HEAD distinto con fuentes idénticas
   **no** produce pack vencido (se publica como procedencia distinta); el pack **no** figura en su
   propio `sources[]`; y el generador tiene que resolver un plan **también bajo `Archives/`**, porque
   el RELEASE regenera y verifica **después** del `git mv`.
2. **Qué hace D con lo que C no midió.** D **acepta** el resultado de C como está publicado: el tramo
   semántico de AC15 es `NO-EJERCITADO` y **D6 sigue dormida**. D no reabre C, no renegocia E1–E5 y no
   presenta la exhibición de candidatos en el pack como aceptabilidad obtenida. Lo que D hereda medido
   de C es su parte mecánica (estados del índice, umbral sobre `confidence`, aditividad, denominador
   con sus ceros), y esa es la que el pack puede mostrar.

**Criterios de aceptación**: **AC21** (clave `provenance` con `head`, `generated_at`, y `sources[]`
con sha por fuente; `--check` falla si cambió el sha de una fuente gobernada y **no** falla por el
solo hecho de que HEAD avanzó; la prueba se hace **re-editando una fuente
y re-midiendo en disco**, no leyendo el objeto en memoria) y **AC22** (los tres estados de R2.9:
`COMPLETO` / `SECCION-NO-RESUELTA`, con la sección pedida y las rutas intentadas /
`FUENTE-AUSENTE`; prohibido emitir un pack más corto sin declararlo; tres tests nombrados por su
causa). **AC23**: mutation check sobre el símbolo real que impide el truncamiento, con rojo y verde
en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/`.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_briefing_se_genera_por_fase.py` | AC19 con `no_incluye[]` no vacío |
| `test_briefing_seccion_no_resuelta.py` | AC22: nombra la sección pedida y las rutas intentadas; **no** emite pack corto |
| `test_briefing_fuente_ausente.py` | AC22: `FUENTE-AUSENTE` con la ruta buscada |
| `test_briefing_check_vence_con_arbol.py` | AC21: **cambiar el sha de una fuente** y que `--check` falle; revertir y que pase |
| `test_briefing_head_no_es_la_llave_de_caducidad.py` | ⟦bloque C, orden §4.C⟧ HEAD avanzado con fuentes idénticas **no** vence el pack: se publica la procedencia distinta y el check pasa |
| `test_briefing_resuelve_plan_archivado.py` | ⟦bloque C⟧ el generador resuelve un plan bajo `Archives/` (es la llamada que hace el RELEASE después del `git mv`) |
| `test_briefing_corpus_real.py` | R2.6: genera el pack de al menos **una fase de un plan archivado real**, con `skipif` visible y su corrida declarada |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/phase_briefing -v
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-D ✅, y **re-declarar D6 con el estado real de AC15**, no con una
   expectativa. ⟦Precisión del bloque C, 2026-09-24⟧: la rama «el triaje salió aceptable» **no es
   alcanzable mientras D7 esté inactiva**, porque con proveedor falso `acceptance` solo puede publicarse
   como `NO-EJERCITADO` (contrato **E4**). Así que D **no** activa D6 ni la re-asigna por interpretación:
   la deja **dormida con su causa escrita** y con el disparador intacto (proveedor real mediante). Si D
   encontrara un defecto mecánico en el output de C —estados colapsados, umbral sobre el campo
   equivocado, una fila que desaparece— eso **sí** se registra, con dueño y evidencia, y no se resuelve
   tocando el script de C desde D.
2. `README.md` — progreso, y el número real de ACs verificados (AC19–AC23).
3. `06-checklist-implementacion.md` — casillas de la fase.
4. `09-documentacion-post-proyecto.md` — Sección A (módulo nuevo), B, D (fuente de la métrica de carga
   y su delta, con comando y enlace a `carga.json`), E.
5. `10-analisis-post-implementacion.md` — fila de la fase y lecciones nuevas (o «sin lecciones nuevas»);
   analizar el delta respecto de **A7** por referencia a `09` §D y `carga.json`, sin transcribir cifras.
6. `00-lecciones-capitalizadas.md` — «Qué cambia» con lo que realmente pasó; si la fase descubrió
   una fuente que el Paso 0 no consultó, añadir la consulta y su descarte.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D \
  --desc "build_phase_briefing.py: pack derivado por fase, proveniencia con sha, negativa a truncar y delta de carga de lectura (AC19-AC23)" \
  --archivos-mod "scripts/build_phase_briefing.py,tests/quality_gates/phase_briefing" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] Los tests de la tabla pasan y ninguno cubre dos estados (⟦2026-09-24⟧ la tabla creció de cinco a
      siete al cubrir la no-circularidad de HEAD y la resolución del plan archivado).
- [ ] `carga.json` trae `method` con el comando literal, bytes exactos y el divisor declarado, **y los
      tres sumandos de la carga total** por fase (`workflow_obligatorio`, `coste_de_generacion`,
      `pack_consumido`).
- [ ] El par pre/post existe y la resta está comprobada **entre cargas totales**, no entre «fuentes» y
      «pack». La concatenación no se presenta como ahorro.
- [ ] Delta explicado por fase; cero o negativo declarado, no escondido.
- [ ] `--check` falla contra una **fuente** editada y pasa al revertir (demostrado en disco); y **no**
      falla solo porque HEAD avanzó.
- [ ] El generador resuelve un plan bajo `Archives/` (demostrado, no afirmado: es la llamada del
      RELEASE después del `git mv`).
- [ ] Tres estados de resolución de secciones, un test por estado.
- [ ] `mutation/` tiene rojo y verde del guard de truncamiento (AC23). Sin rojo, ⚠️.
- [ ] Test contra una fase de un plan **archivado real**, con `skipif` y su corrida declarada (R2.6).
- [ ] `git status .agents/` vacío al cerrar: `.agents/` sin un solo byte cambiado.
- [ ] `--quick` verde con su composición intacta (AC16, delta 0 con su par pre/post).
- [ ] Dependencia D6 **re-declarada, no re-abierta**: sigue **dormida** porque AC15 publicó
      `NO-EJERCITADO`, y D registra la causa en `dependencias-fases.md` sin reinterpretar el
      disparador ni reabrir C.
- [ ] Post-ejecución completa e índice regenerado y comprobado sobre el mismo árbol final verificado.
      El commit es opcional, posterior y requiere autorización explícita; no condiciona ninguno de
      los cinco cortes del proceso común.

## Restricciones

- **No toca `.agents/`** en modo escritura. El workflow canónico se lee, se referencia y se declara
  como lectura aparte; **no** se sustituye por el pack.
- No modifica ningún prompt de fase de ningún plan, incluido los de este: el generador los **lee**.
- No rebaná el workflow ni reescribe las nueve citas al canónico del otro plan (deuda D3).
- No llama a ningún proveedor de decisiones. Es determinista o no es.
- No ejecuta la pipeline ni toca `output/` en escritura. No commitea ni empuja sin instrucción literal.
- Presupuesto con instrumento y corte declarados (R2.1); nunca estimado.

## Prompt de ejecución

```text
Ejecuta unicamente FASE-D del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-D.md, 01-plan-maestro.md §1 (medicion A7 y la nota de divisor de
tokens), §4 (AC19-AC23, AC16, AC17), 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2,
dependencias-fases.md (cadena y la regla de donde vive el pack generado) y el workflow canonical.
Heredas de A los tres estados y coverage_basis, y de C el informe de candidatos.
Escribe scripts/build_phase_briefing.py: recorre los prompts de fase del plan, extrae la lista de
lectura que cada uno DECLARA, resuelve cada seccion nombrada y emite briefing/FASE-X.md con la
seccion copiada y su procedencia al pie. Modelo a emular: build_lesson_index.py (generado, con
--check, prohibido editar a mano).
Tres reglas duras. Una: el pack nunca se calla un recorte — seccion declarada y no resuelta es su
propio estado, con la seccion pedida y las rutas intentadas, y el script se niega a emitir un pack
mas corto en silencio. Dos: proveniencia con HEAD, fecha y sha por fuente, y --check vence contra
el arbol; la prueba se hace editando una fuente y re-midiendo en disco, no leyendo memoria. Tres:
declara no_incluye y la lectura aparte obligatoria, que incluye el workflow canonical.
AC20 mide el delta de carga de lectura con el mismo comando en antes y despues, bytes exactos y
tokens estimados con el divisor declarado, par pre/post y la resta comprobada. La resta se saca entre
CARGAS TOTALES, cada una con sus tres sumandos publicados: workflow_obligatorio (lo que la fase sigue
leyendo aparte, workflow canonico incluido mientras D3 no lo rebane), coste_de_generacion (la invocacion
del generador que la sesion ejecuta) y pack_consumido. Concatenar documentos no es ahorrar: unir siete
archivos en uno no baja la suma de sus bytes. El unico ahorro atribuible al pack es lo que dejo de
leerse porque no entro, y eso se publica con su omision. Un delta cero o negativo es resultado valido
y se explica.
AC21: la frescura la gobierna el sha256 de las fuentes listadas en sources[], con sus causas
distinguibles. head es procedencia, no llave de caducidad: si HEAD gobernara, el commit que guarda el
propio pack generado lo dejaria vencido dentro de ese commit. Por eso HEAD avanzado con fuentes
identicas NO vence el pack, y el pack no entra en su propio sources[]. El generador resuelve un plan
tambien bajo Archives/, porque el RELEASE regenera y verifica el pack despues del git mv; ese rojo se
resuelve regenerando, nunca editando codigo.
De C heredas su parte mecanica medida y aceptas su parte no medida: acceptance de AC15 es
NO-EJERCITADO y D6 sigue dormida. No reabras C, no renegocies E1-E5 y no presentes los candidatos
exhibidos en el pack como una aceptabilidad obtenida.
No toques .agents/ en escritura, ningun prompt de fase, run_all_validations.py, el hook,
build_lesson_index.py ni los scripts de las fases anteriores. No llames a ningun proveedor: esta
fase es determinista o no es. Re-declara D6 con su causa (dormida mientras D7 este inactiva), no la
actives por interpretacion. Registra la fase con log_phase_completion.py y regenera y comprueba el
indice sobre el mismo arbol final verificado.
Los cinco cortes no requieren commit: es opcional, posterior y autorizado por separado.
Deja checkpoint si falta autorizacion.
```


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-D.md` · sha256 `0251cea0a72a07ee99b5e5e0e06a3da17e366cbb7ab8001d9f0ae7a38070f591` · 19703 bytes copiados de 19703 del documento · HEAD `2a675fa` · generado `2026-09-26T17:49:31Z`

---

<!-- BEGIN BRIEFING-META
{
  "generado_por": "scripts/build_phase_briefing.py",
  "plan": "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
  "fase": "RELEASE",
  "estado": "COMPLETO",
  "declaracion": "DECLARADA",
  "provenance": {
    "head": "2a675fa",
    "generated_at": "2026-09-26T17:49:31Z"
  },
  "no_incluye": [
    "01-plan-maestro.md — 19801 bytes fuera de lo declarado (4, 6)",
    "04-contrato-ejecucion.md — 23159 bytes fuera de lo declarado (Dos momentos del cierre, Carga total y frescura del pack, Orden del cierre)",
    "docs/CONTRIBUTING.md — declarada por el prompt pero vive fuera de `.opencode/`: se lee aparte para no ampliar la poblacion que escanea validate_opencode_refs.py"
  ],
  "lectura_aparte_obligatoria": [
    ".agents/workflows/phased_project_executor.md",
    "docs/CONTRIBUTING.md"
  ],
  "sources": [
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md",
      "sha256": "1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7",
      "documento": "01-plan-maestro.md",
      "secciones": [
        "4",
        "6"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md",
      "sha256": "c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5",
      "documento": "04-contrato-ejecucion.md",
      "secciones": [
        "Dos momentos del cierre",
        "Carga total y frescura del pack",
        "Orden del cierre"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md",
      "sha256": "f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0",
      "documento": "00-lecciones-capitalizadas.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/06-checklist-implementacion.md",
      "sha256": "6c0e55485119589fe477600ac360691f9301475e5be617bf5b4b104591dbc0b9",
      "documento": "06-checklist-implementacion.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md",
      "sha256": "a38da8ea12a6a54ef5598925e54e6132881306439236419c6b597d2dd4696723",
      "documento": "dependencias-fases.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md",
      "sha256": "b66723f1c3c507cc29034b705c24709d72fa88493fba5277ff8f61382d3dc337",
      "documento": "10-analisis-post-implementacion.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-A.md",
      "sha256": "03cffe5f708db67a566f56dc5c8ecdb5e1b0e43bcd8022608974c052827469d2",
      "documento": "05-prompt-inicio-sesion-fase-A.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-B.md",
      "sha256": "0f4e51282983f59cc79bb13d7536bf7bf0a732e38a275464a632757f1ef90006",
      "documento": "05-prompt-inicio-sesion-fase-B.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-C.md",
      "sha256": "ea361c4696797a9a36df482636378040e57c20797af5ec6efd1ef8fc37df0832",
      "documento": "05-prompt-inicio-sesion-fase-C.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-D.md",
      "sha256": "0251cea0a72a07ee99b5e5e0e06a3da17e366cbb7ab8001d9f0ae7a38070f591",
      "documento": "05-prompt-inicio-sesion-fase-D.md",
      "secciones": [],
      "en_pack": true
    }
  ],
  "divisor_tokens": 4
}
END BRIEFING-META -->
