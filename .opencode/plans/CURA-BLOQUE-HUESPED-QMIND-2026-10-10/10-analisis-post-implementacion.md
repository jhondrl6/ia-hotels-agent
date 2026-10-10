# Análisis post-implementación — CURA-BLOQUE-HUESPED-QMIND-2026-10-10

**Estado: FASE-1 cerrada el 2026-10-10.** Plan de una fase; HEAD al abrir `01013ef`. Las métricas viven en
`09-documentacion-post-proyecto.md` §D y aquí se referencian, no se re-transcriben.

## A. Qué se hizo y por qué

El diagnóstico de la sesión anterior (`evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/00-acta.md`) midió que el
bloque huésped de `verificar_contenido()` solo se recorría en 4 de sus 12 rutas, y que dos de las 8 restantes se
tomaban por la red: cuando `descargar_fuente()` no respondía, la corrida imprimía `0 fuente(s) huesped(s)` y, si
ninguna otra entrada sostenía un rojo, bajaba el EXIT de 1 a 2. Un hallazgo de contabilidad —que se calcula con el
registro y el censo, sin bajar nada— quedaba supeditado a una observación que no necesita.

La cura se hizo por **forma**, no por parche: el dictamen de cada entrada pasó a un ámbito propio
(`_dictaminar()`) cuyos `return` reemplazan a los nueve `continue`, y el bloque huésped quedó como última
sentencia del bucle. Ya no existe un camino que lo salte, y el `[CONTADOR]` publica sobre cuántas entradas corrió.

## B. Decisiones de diseño

Las tres decisiones del maestro (DA-BH.1 evaluación por entrada sin de-duplicar por plan, DA-BH.2 extracción del
dictamen a su propio ámbito, DA-BH.3 orden impreso conservado) se ejecutaron como estaban escritas. A ellas se
suman dos decisiones tomadas al ejecutar:

**DA-BH.4 (tomada en FASE-1): el diente de AC-N1 ancla por título, no por id.** `_lineas_huesped()` recorta el id
a trece caracteres y el generador de ids del montaje comparte ese prefijo en todas sus fuentes, así que una
aserción por id habría pasado con cualquier huésped impresa: un ancla que no discrimina no ancla nada. Se ancla
por `TITULO_HISTORICO[:60]`, que sí distingue a la fuente.

**DA-BH.5 (tomada en FASE-1): el diente de caracterización de la deuda hermana se renombra, no se borra.**
`test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado` pasó a
`test_un_vencido_por_cuerpo_en_la_mesma_entrada_tambien_evalua_a_su_huesped`, invirtiendo las dos aserciones que
fijaban el límite y conservando las que probaban la coexistencia del `VENCIDO` con el rojo de contabilidad. El
nombre viejo queda referenciado en documentos **archivados** del plan hermano y en su **instantánea publicada**,
que son frozen por diseño (editar la instantánea la volvería `VENCIDO` contra su `sha_cuerpo`): la equivalencia de
nombres se declara aquí y en el maestro §5, deuda `S-BH-1`.

## D. Métricas y evidencia

Ver `09-documentacion-post-proyecto.md` §D. Resumen de trazabilidad: PRE 65 → POST 67 con resta exacta de 2
(R2.7), dos mutantes con sus dos salidas y restauración verificada por sha256 (R2.8), quick 13/13 antes y
después, y el modo completo en `05-modo_completo_post.txt`.

El primer POST salió **1 failed / 66 passed** y el rojo era del montaje del diente nuevo, no de la cura: la fuente
huésped se construyó con los mismos bytes del cuerpo, de modo que casaba por `sha_metadata`, entraba en
`prometidas` y la corrida intentaba dos bajadas. Se corrigió el montaje (bytes distintos para la huésped) y el
incidente quedó declarado dentro del propio test, que es donde un futuro lector lo va a buscar.

## E. Lecciones definidas por este plan

Serie `L-BH`, reservada tras medir **0** coincidencias de `L-BH` en `.opencode/LECCIONES-INDEX.md`.

| ID | Enunciado | Qué previene |
|---|---|---|
| **L-BH.1** | Un hallazgo que no necesita la observación que falta no puede vivir detrás de la rama que la espera: se coloca donde sus insumos están disponibles, no donde el flujo alcanza a llegar. | AC-N1. La forma elegida (ámbito propio + bloque al final del bucle) hace inalcanzable el salto; repetir la llamada en cada rama habría dejado ocho sitios donde olvidarla |
| **L-BH.2** | Un contador que publica un cero tiene que publicar también sobre cuántos casos miró, y ese denominador se cuenta donde se mide: si se deriva del total, un salto futuro no lo baja y nadie se entera. | AC-N2. El mutante M2 lo demuestra: contando solo en la ruta favorable el denominador impreso bajó a `0/2` y el diente cayó |
| **L-BH.3** | Un ancla que no discrimina no ancla nada: si el instrumento trunca el identificador que la aserción usa, todos los candidatos comparten el prefijo y el diente pasa por la razón equivocada. | DA-BH.4. Se ancla por el dato que el instrumento sí distingue (el título recortado a sesenta caracteres) |

## F. Hallazgos y sorpresas

| Hallazgo | Cómo se midió | Estado |
|---|---|---|
| La cura no rompió **ningún** diente existente: el literal del `[CONTADOR]` se extiende al final de la línea, y eso conserva la secuencia que anclan los dientes que afirman la aritmética seguida del recuento | POST final 67 passed con PRE 65: la resta es exactamente los dos dientes nuevos | Cerrado por medición |
| `S-CIM-9` y `DA-CIM.9` están en `citados_sin_definicion` del índice: no son capitalizables en el Paso 0 (C7 los cortaría) aunque la deuda exista y sea la antecesora directa de este plan | `duenos_del_corpus()` sobre los dos directorios; 374 IDs con dueño y esos dos ausentes | Cerrado: se referencian como prosa en el maestro §5, no como lecciones |
| El nombre del diente de caracterización está citado en la **instantánea publicada** del plan hermano, cuyo sha está fijado en el registro: renombrarlo deja una referencia histórica que no se puede corregir sin volver `VENCIDO` lo publicado | `grep -rn` del nombre viejo sobre el árbol | Declarado como `S-BH-1`, dueño operador |
| La consulta corpus-wide a QMind del Paso 0 falló (`knowledgeBaseAccountListFailed`), así que las lecciones salen del corpus versionado y del índice, que sí respondieron | Un intento, sin reintentos; se publicó el motivo y no un cero | Declarado como `S-BH-5`, dueño operador |
| La fila del registro enumera **5** archivos modificados y `git` cuenta **6**: falta `docs/contributing/.last_doc_phase.json`, que escribe el propio `log_phase_completion.py` y no se enumeró al invocarlo | `git diff --name-only` contra la entrada de `docs/contributing/REGISTRY.md` | **Declarado, no corregido**: el escritor es aditivo y se niega si la cabecera ya existe, así que re-ejecutarlo apilaría una entrada duplicada. Corregirlo a mano sería editar el registro fuera de su escritor |
| El crudo del modo completo (`05-modo_completo_post.txt`) se lanzó **antes** de que existieran los documentos del plan, el índice regenerado y la entrada del registro | Leído el crudo al terminar: **16/18, EXIT=1**, con dos rojos y ningún otro. La contaminación que se temía **no se materializó**: los checks que habrían podido salir vencidos (referencias, citas, capitalización, governance numbers, wiring, briefing packs sobre HEAD) pasaron en verde | Cerrado por lectura. Los dos rojos son conocidos y con dueño: `Tests` (ruido de deprecación de Pydantic en `data_models/canonical_assessment.py`, rojo preexistente del corpus) y `QMind Write-back` (el `[DUPLICADO-VIGENTE]` **deseado** de la era G, `S-CIM-2`, dueño operador) |
| **Confirmación en vivo de la cura** (`08-verificador_curado_en_vivo.txt`, solo lectura: 1 `source list` y sus bajadas, 0 escrituras) | La corrida real tuvo **una descarga fallida** (`01a125a0…`, cuya entrada se abstiene con «1 fuente(s) cuyo metadata casa no bajaron») y aun así imprimió `5 fuente(s) huesped(s)` y el denominador nuevo `4/4 entrada(s) con su bloque huesped recorrido`, con `2 con fidelidad remota medida` | El denominador cuenta la entrada que se abstuvo: el bloque corrió para las cuatro. **Límite de esta prueba, declarado:** en esta corrida la entrada del plan JEV sí bajó, así que sus cuatro huéspedes se habrían impreso también con el código viejo; lo que la corrida viva prueba es el denominador (AC-N2) y la universalidad del bloque, mientras que la supresión 5→1 por red queda probada por la matriz offline del diagnóstico y por el diente de AC-N1 |

## Deudas al cerrar

`S-BH-1` (referencia histórica al nombre viejo del diente, en documentos frozen), `S-BH-2` (packs no generados
para este plan), `S-BH-3` (sin bump de versión), `S-BH-4` (las cuatro fuentes huésped del plan JEV y la era G
siguen vigentes en el notebook: decisión de contenido publicado), `S-BH-5` (capa QMind sin observación en el Paso
0). Todas con dueño en el maestro §5.

## Cierre del plan

**COMPLETADO.** FASE-1 cerró los dos AC con sus dientes y sus mutantes; el rojo vivo de la era G sigue rojo por
diseño (este plan no borra fuentes ni marca reemplazos) y su dueño sigue siendo el operador. Al cerrar la fase el
árbol **quedó** en «listo para revisión» y en espera de autorización, sin commit ni push; esa espera terminó con la
orden del operador del mismo 2026-10-10, que publicó la fase en `c6a47c2` tras una L3 de cero hallazgos y el push
`01013ef..c6a47c2`. ⟦Este renglón estaba escrito en presente —«sin `git commit`, sin L3 y sin push»— y lo venció el
propio push que registraba; el sello lo re-ancla con fecha y queda así, sin borrar la espera que efectivamente
ocurrió.⟧
