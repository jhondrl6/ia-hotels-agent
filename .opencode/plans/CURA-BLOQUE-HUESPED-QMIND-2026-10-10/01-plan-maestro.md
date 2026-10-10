# Plan maestro — CURA-BLOQUE-HUESPED-QMIND-2026-10-10

**Estado: FASE-1 abierta el 2026-10-10.** HEAD al concebir: `01013ef` (paridad `0 0` con `origin/master`,
verificado por `git ls-remote`). Plan de **una sola fase**: la medición de §1 colapsó la FASE-2 dentro de la
FASE-1. No libera versión: `VERSION.yaml` publica `4.80.0` y la decisión de bump es del operador (§5, `S-BH-3`).

**Objetivo:** que el hallazgo de contabilidad del write-back de QMind deje de depender de la red. Hoy el bloque
que emite `[DUPLICADO-VIGENTE]` por fuente huésped solo se recorre en 4 de las 12 rutas del bucle de
`verificar_contenido()`; en las otras 8 —dos de ellas tomadas cuando `descargar_fuente()` falla— el instrumento
no mira, y su `[CONTADOR]` publica un cero que se lee como dato del censo.

**Fuente de partida:** el §7 del acta `evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/00-acta.md`, que dictaminó
el hueco con medición (mapa de control de flujo, censo vivo en una llamada, matriz offline 2x2 y cobertura
0 de 57) y dejó la cura como mandato de una fase futura con su AC, su diente y su mutante. Workflow canónico:
`.agents/workflows/phased_project_executor.md`.

## 1. Revalidación del estado que traía el mandato (medido el 2026-10-10, no heredado)

Ninguna fila es cortesía del mandato: cada una se midió en esta sesión y dos rectifican su letra.

| Punto | Qué decía el mandato | Qué se midió | Consecuencia para el plan |
|---|---|---|---|
| **Rectificado: el nombre del AC** | «AC-N.1» (así lo llama el acta §7) | `AC_TOKEN_RE` de `scripts/validate_lesson_capitalization.py` es `\bAC-?[A-Z]{0,2}\d+\b`: admite `AC-N1`, **no** admite el punto. Un AC con punto no satisface C4 y el check `[7/8]` del hook cortaría el commit | Los AC se instancian como **AC-N1** y **AC-N2**. El acta queda como está (versionada y empujada): la equivalencia se declara aquí y en `00-lecciones-capitalizadas.md`, no se re-escribe el pasado |
| **Rectificado: la FASE-2 no se difiere, se fusiona** | «abre la FASE-1 y difiere la FASE-2 con dueño si su medición no la hace barata» | El coste del denominador del `[CONTADOR]` es **bajo y medido**: su literal vive en 2 archivos (el productor y su familia de tests), 8 ocurrencias en tests, 15 líneas de aserción, y la aritmética `N+M+K==T` aparece 6 veces en un solo archivo. Además **los dos AC tocan las mismas aserciones**: AC-N1 cambia el número de huéspedes que esos dientes fijan y AC-N2 cambia la línea donde se leen | FASE-2 no se difiere: se **fusiona** en FASE-1 con sus dos AC. Separarlos obligaría a re-anclar dos veces las mismas 5 aserciones de huésped y a correr dos rondas de mutantes sobre el mismo símbolo. La condición del mandato («si su medición no la hace barata») no se cumple |
| **Confirmado: la deuda hermana no es capitalizable** | El acta remite a `S-CIM-9` como la deuda que declara la familia | `S-CIM-9` y `DA-CIM.9` están en `citados_sin_definicion` del índice, **no** definidos: citarlos en §2 de `00-lecciones-capitalizadas.md` cortaría C7 | `S-CIM-9` se referencia como prosa en §5 de este maestro y en el análisis, y no como lección capitalizada. Su fila vive en un plan **archivado** que este plan no edita |
| **Confirmado: no hay packs que generar** | — | El check `[8/8]` del hook y el `[13/13]` del modo completo miran una población fija: solo el plan canónico `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`. Un plan nuevo sin packs no los rompe | `briefing/` **NO GENERADO** para este plan, con dueño y motivo en §5 (`S-BH-2`). Precedente: la fila `S-CIM-5` del plan hermano |
| **Confirmado: el PRE de la fase** | Referencia vigente 65 passed, EXIT=0 | Corrido en la sesión de diagnóstico sobre `4d35a42` con la selección literal de las dos familias: **65 passed, EXIT=0**, crudo archivado en `evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/01-pre_seleccion_dos_familias.txt`. Quick **13/13, EXIT=0** antes y después del acta | FASE-1 re-mide su propio PRE al abrir y publica el crudo en su evidencia; no re-transcribe el del diagnóstico |
| **Confirmado: el índice ajeno** | 13 rutas staged ajenas, no tocarlas | `git status -uall` da 13 rutas `A ` bajo `Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/briefing/` y `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/` (deuda `S-CIM-7` del plan hermano) | Ningún `git commit` sin pathspec en este índice, incluido `--amend`. Los commits de este plan nombran su directorio explícitamente |
| **Nuevo, medido: el escritor no puede producir dos vigentes del mismo plan** | — | `registrar_publicacion()` marca `reemplazada` toda entrada vigente del plan antes de appendear la nueva | DA-BH.1: el bloque huésped se evalúa **por entrada** y no se de-duplica por plan, porque por construcción del escritor hay una sola vigente por plan. Se declara el supuesto y su diente de contorno |

**Anclas por símbolo, todas re-leídas en esta sesión.** El bucle y sus nueve `continue` viven en
`verificar_contenido()`; la selección de huéspedes en `_huespedes_sin_contabilidad()`; sus líneas en
`_lineas_huesped()`; la etiqueta del resumen en `causas_del_rojo()`; la bajada en `descargar_fuente()` con su
caché por corrida en `_hash_bajado()` y `_CACHE_BAJADAS`; el censo en `fetch_sources()`, invocado una sola vez
por `main()`. El consumidor es `scripts/run_all_validations.py::_check_qmind_writeback`, con `--strict` y solo en
el modo completo.

## 2. Criterios de aceptación

| AC | Enunciado | Diente (nombre por su causa) | Mutante (R2.8) | Estado |
|---|---|---|---|---|
| **AC-N1** | El hallazgo de contabilidad se evalúa en **todas** las rutas del bucle de `verificar_contenido()`, incluidas las ocho que hoy cortan antes: las dos abstenciones locales, las dos de vigencia (`VENCIDO` por cuerpo y por instantánea), `PROMESA-ROTA`, las dos abstenciones por bajada fallida y el `VENCIDO` por título coincidente. Una bajada que falla **no** suprime a la huésped de su entrada ni cambia el EXIT de la corrida por esa vía | `test_una_bajada_que_falla_no_suprime_a_su_huesped_de_contabilidad` (nuevo) y re-anclaje de `test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado`, que **debe ponerse rojo por diseño** y se re-escribe como diente de la cura | Apagar el bloque huésped universal (devolver la evaluación a una sola rama): el diente nuevo cae por la causa nombrada (líneas de huésped y EXIT), no por un fallo de montaje. Restauración verificada por sha256 | **CERRADO** en FASE-1: mutante M1 rojo por `salio == 1` (dio 2) y verde restaurado |
| **AC-N2** | El `[CONTADOR]` publica su **denominador de observación**: cuántas entradas recorrieron el bloque huésped, contado en el sitio donde corre y no derivado de `len(vigentes)`. Así `0 fuente(s) huesped(s)` solo puede imprimirlo una corrida que sí miró, y un `continue` nuevo baja el denominador y lo delata | `test_el_contador_publica_su_denominador_de_observacion` (nuevo): montaje de dos entradas donde una toma una ruta que antes cortaba; se exige el denominador completo y su caída bajo mutante | Contar el denominador solo en la ruta favorable: el diente cae porque el denominador impreso baja. Restauración verificada por sha256 | **CERRADO** en FASE-1: mutante M2 rojo con el denominador impreso en `0/2`, y verde restaurado |

**DA-BH.1 (decisión de diseño de este plan): la huésped se evalúa por entrada, sin de-duplicar por plan.**
Motivo medido: `registrar_publicacion()` garantiza una sola entrada vigente por plan, así que la suma por entrada
y el conjunto de fuentes distintas coinciden en toda población que el escritor pueda producir. **Alternativa
rechazada:** de-duplicar por `(plan, id)` — habría cambiado el significado del contador sin un AC que lo pidiera y
sin población real donde se observara la diferencia.

**DA-BH.2 (decisión de diseño de este plan): la cura se hace extrayendo el dictamen por entrada a un ámbito cuyo
`return` reemplaza al `continue`, y dejando el bloque huésped como última sentencia del bucle.** Motivo: es la
forma mínima que hace **inalcanzable** el salto del bloque, en lugar de añadir una llamada en cada una de las ocho
ramas (ocho sitios que un cambio futuro puede volver a saltar). **Alternativa rechazada:** duplicar la llamada en
cada rama — mismo resultado observable, ocho veces más superficie, y el diente de AC-N2 no distinguiría una rama
olvidada de una rama nueva.

**DA-BH.3: el orden impreso se conserva.** Las líneas de huésped siguen saliendo después del veredicto de su
entrada, con la etiqueta de esa entrada. **Alternativa rechazada:** agrupar todas las huéspedes al final, que
habría roto la atribución por entrada que el crudo del diagnóstico usa para leer el hallazgo.

## 3. Alcance y restricciones

- **Sí:** `scripts/validate_qmind_writeback.py` (símbolos `verificar_contenido()`, `_huespedes_sin_contabilidad()`
  y su docstring, que describe el estado anterior) y `tests/test_validate_qmind_writeback_escritura.py` (un diente
  nuevo por AC, un re-anclaje gobernado y los dientes cuyo literal del `[CONTADOR]` se mueva).
- **No:** el notebook (cero `source upload`, cero `source delete`; `source list` y `source download` de solo
  lectura y con racha contada), las cinco fuentes huésped reales del plan JEV (decisión de contenido publicado,
  del operador: `S-BH-4`), `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, documentos de planes archivados, y el
  acta de diagnóstico ya versionada.
- **R2.2:** citar por símbolo, nunca por número de línea. **R2.8:** cada AC cierra con mutation check y sus dos
  salidas en `evidence/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/FASE-1/`. **R2.9:** los tres estados en todo lector.
- **Commits:** siempre por pathspec, nunca `git commit` a secas ni `--amend` en este índice.
- **Rojo vivo que no se toca:** `--strict` cierra EXIT=1 por `[DUPLICADO-VIGENTE]` de la era G
  (`01a0bfc9-5f5a-783e-9492-16367bbff596`), dueño el operador. Tras la cura ese rojo **sigue** rojo: este plan no
  borra fuentes ni marca reemplazos.

## 4. Dónde corre y cómo se observa

El check que consume este verificador es `[17/18]` del modo completo de `scripts/run_all_validations.py`
(`_check_qmind_writeback`, invocado con `--strict`); el quick **no** lo corre. Por eso la evidencia de la fase se
compone de: la selección literal de las dos familias (el diente gobierna), el quick (los gates documentales) y,
si el presupuesto alcanza, el modo completo con `PYTHONUTF8=1`. La observación en vivo del contador contra el
notebook real es **opcional y de solo lectura**: no es requisito de ningún AC, y una descarga que falle hoy ya no
cambia el veredicto de contabilidad (eso es justamente AC-N1).

## 5. Deudas, diferidos y dueños

| ID | Deuda o diferido | Dueño | Disparador |
|---|---|---|---|
| `S-BH-1` | La fila `S-CIM-9` del plan archivado `Archives/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07` queda **sin cerrar formalmente**: este plan cura su familia completa, pero no puede editar un plan archivado para marcarla | operador | Decidir si se anota el cierre en un documento vivo (por ejemplo el análisis de este plan) o se deja la fila histórica como está |
| `S-BH-2` | `briefing/` NO GENERADO para este plan | operador | Que un futuro check amplíe su población más allá del plan canónico |
| `S-BH-3` | Sin bump de versión: este plan cambia un instrumento, no una capacidad de producto | operador | Decidir `4.81.0` en el cierre, o dejar la versión del plan hermano |
| `S-BH-4` | Las cuatro fuentes huésped del plan JEV siguen vigentes en el notebook y la era G sigue sin marcar | operador | Decisión sobre contenido publicado: marcar reemplazo, o publicar el cierre que las reemplace |
| `S-BH-5` | La capa QMind quedó sin observación en el Paso 0 (lector fallido en la consulta corpus-wide) | operador | Que el servicio responda; entonces re-ejecutar la consulta y completar `00-lecciones-capitalizadas.md` §1 |

## 6. Presupuesto y política de subagentes

**Presupuesto:** 90 `tool_use` para esta sesión (analogy con A2/A3/B/C del plan hermano), con checkpoint declarado
si se excede y sin segunda sesión implícita. La unidad se cuenta por enumeración de bloques de herramienta; no
existe comando que la imprima, y ese límite va declarado aquí.

**Subagentes: pertinentes para leer, prohibidos para escribir.** Medido en esta misma sesión:

- **Pertinente (y usado):** el relevamiento del contrato de creación de plan —nueve puntos sobre executor,
  templates, cinco validadores y el escritor del registro— se delegó a un subagente de solo lectura y volvió con
  comandos verbatim en una llamada. Coste ahorrado al agente principal: del orden de 15 a 20 `tool_use` de
  lecturas que habrían ocupado el presupuesto de la fase.
- **No pertinente:** escribir cualquiera de los artefactos gobernados (índice de lecciones, `REGISTRY.md`,
  sincronización de versiones, este maestro, el código y los tests). Cuatro razones medidas: (i) los escritores
  son **compartidos y aditivos** —`log_phase_completion.py` apila y se niega si la cabecera ya existe, y el índice
  se regenera de una pieza—, así que dos actores sobre el mismo derivado serializan de todos modos; (ii) el
  clasificador bloquea escrituras fuera del workspace, de modo que el scratch de un subagente aterriza **dentro**
  del árbol y un `.py` suelto mueve los contadores del gate `--check` del wiring; (iii) los mutation checks exigen
  restaurar el árbol y verificarlo por sha256 —un fallo delegado deja un mutante versionable en el repo—; y
  (iv) todo cambio delegado hay que re-leerlo para verificarlo, que cuesta más que hacerlo.
- **Regla de este plan:** subagentes para relevamiento y medición de solo lectura; el agente principal escribe,
  muta, restaura, valida y commitea. Ningún commit se delega.

## 7. Cierre

Los cinco cortes del flujo documental se declaran y verifican **sin commitear**, y los cinco terminan en espera de
autorización: implementación terminada, verificación terminada, cierre documental, listo para revisión y espera de
autorización. `git commit`, L3 y push solo con literal del operador. El registro de la fase lo escribe
`scripts/log_phase_completion.py` al cerrar, con `--fase FASE-1 --fecha 2026-10-10`, y no se re-ejecuta sobre una
fase ya registrada.
