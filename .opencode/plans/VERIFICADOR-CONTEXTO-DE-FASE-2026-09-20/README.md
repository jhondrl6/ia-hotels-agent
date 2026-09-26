# VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Estado: FASE-A ✅ CERRADA el 2026-09-21 (VERIFICADO OFFLINE, AC1–AC5), FASE-B ✅ CERRADA el
2026-09-21 (VERIFICADO OFFLINE, AC6–AC9), commiteada el 2026-09-22 en `647f436`, FASE-C ✅ CERRADA el
2026-09-24 (VERIFICADO OFFLINE en su mecánica: AC10–AC14, AC15 ⚠️ con `acceptance = NO-EJERCITADO`) y
FASE-D ✅ CERRADA el 2026-09-24 (VERIFICADO OFFLINE, AC19–AC23) —
4 de 4 fases de implementación ejecutadas. FASE-C cerró con el corte **«hasta listo para revisión»**:
**commit hecho el 2026-09-24 con instrucción literal del operador** (`7f2e9f9` el helper de BLOQUE-B que
la fase reutiliza + `5817edd` las 37 rutas propias, 7/7 del hook), **con el `git push` hecho el mismo 2026-09-24** (publicó `da382b1..5817edd`), y con su evidencia en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/`. FASE-B quedó además **conciliada el
2026-09-23** con la remediación del bloque A de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`: **S11 y
S12 aceptadas** (corrección técnica ajena, en `fdd397f`) y **AC9 declarado con su alcance local**.
**FASE-RELEASE ejecutada y cerrada en su parte offline el 2026-09-25** (release **4.78.0**: fuente única,
cabeceras por su writer, `DOMAIN_PRIMER` regenerado, CHANGELOG y registro en `REGISTRY` por su único
escritor). Sus cuatro momentos quedan así: **offline cerrado** · **remoto pendiente** (Q7/D8 y
`--upload`/D9, cada uno con autorización literal y presupuesto) · **traslado pendiente** (`git mv` a
`Archives/`) · **publicación pendiente** (commit y push, decisión del operador). FASE-D cerró con el mismo
corte («hasta listo para revisión») y **sin commit ni push**, que no fueron autorizados en su sesión: su
producto
(`scripts/build_phase_briefing.py`, 12 archivos de selección y los **5 packs** generados en
`briefing/`) está verificado sobre el árbol de trabajo y su deuda de viaje está declarada en
`evidence/…/FASE-D/baseline-pre-post.md` §6.
*(Esta cabecera estuvo vencida: decía «1 de 4» y «FASE-B pendiente» mientras la tabla de fases y el
contador de ACs del propio README ya contaban B por cerrada — el defecto que este plan caza,
reproducido sobre su propio índice de entrada y corregido el 2026-09-22 al medirlo. Con la misma regla
deliberada: la cabecera **no** publica cifra de HEAD ni de paridad, que son el dato más inestable que
este archivo escribe; esos se miden con los comandos de §Inicio de la siguiente sesión.)* Concepción:
AUDITADA y CORREGIDA el 2026-09-20 contra código vivo y contra el Knowledge Center (ver
§Correcciones aplicadas).
Renombrado desde `PASO0-VERIFICADOR-PERTINENCIA-2026-09-20` cuando entró FASE-D, porque el
contenido dejó de ser solo pertinencia.

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
se le inventa dueño.⟧ ⟦**Segunda rectificación del mismo 2026-09-24, por cierre de FASE-C**: queda
derogada la primera mitad de la corrección de arriba. El **piloto FASE-C también fue autorizado** esa
tarde, con mandato propio del operador, corte «hasta listo para revisión» y presupuesto escrito, **y se
ejecutó**. Las tres afirmaciones que siguen vivas y no se confunden entre sí: (a) el **bloque C** de la
orden son enmiendas documentales, (b) **FASE-C** es el piloto que corre el prompt de la fase, y (c)
ejecutar el piloto **no** cierra la orden de calidad ni las cuatro fases: siguen pendientes FASE-D y
FASE-RELEASE de este plan.⟧ Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Esto no reabre FASE-B de CONTEXTO ni habilita automáticamente la sesión de FASE-C.

**Contador de ACs (medido al cerrar FASE-D, 2026-09-24):** 19 `VERIFICADO OFFLINE` con su mutation
check o su rojo en disco (AC1–AC5 de FASE-A; AC6–AC9 de FASE-B; AC10–AC14 de FASE-C, con el rojo del
guard de no-filtrado en `evidence/…/FASE-C/mutation/` y el test contra corpus real archivado **corriendo**,
no saltado —ver `FASE-C/r26.txt`—; **AC19–AC23 de FASE-D**, con el rojo del guard de truncamiento en
`evidence/…/FASE-D/mutation/` —apagado el guard, el pack conserva el estado y se achica sin decirlo— y
su `r26.txt` también corriendo) · **1 con su tramo semántico NO-EJERCITADO: AC15** ⚠️ (su parte no
semántica —población, términos con sus ceros, familias no juzgadas— sí está verificada; su `acceptance`
es `null` con motivo literal, contrato E4, y por eso D6 sigue dormida: **D la re-declaró, no la re-abrió**)
· 3 con su parte verificada fase a fase y el resto abierto (**AC16, AC17 y AC18, con delta 0 en A, B, C
y D**; falta la parte que corresponde a FASE-RELEASE) · **0 pendientes**. Y **AC20 cerró con su medición
en la mano, no con el número que el plan esperaba**: el delta de carga quedó **muy por debajo del tercio**
que el plan esperaba, porque el workflow canónico sigue entrando en los dos lados mientras **D3** no se
ejecute. Su porcentaje no se transcribe aquí: vive con su derivación y su comando en la fila
**«Carga de lectura A7 (plan medido) y carga propia»** de este README y en su artefacto
`evidence/…/FASE-D/carga.json` (**L-VCF-19**: copiarlo en un documento que el propio generador mide lo
vence por la copia).
Ningún AC del plan puede llegar a `SUPERADO EN E2E` (no hay FASE-VERIFY ni corrida).

Objetivo: arreglar las tres cosas que hacen que un plan de este repo se lea caro, se juzgue mal y se
desfasen solo. **Coherencia** de las aserciones sobre conteos en los documentos de gobierno,
**pertinencia** de las lecciones que el Paso 0 capitaliza, y **carga de lectura** de una sesión de
fase: **263.973 bytes ≈ 65.993 tokens estimados** antes de tocar código, re-medidos el 2026-09-20
sobre la sesión de FASE-B del plan en vuelo (la medición A7 del maestro; al concebir daba 254.010 y
venció el mismo día).

Hermano de `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, que cerró la forma. Este cierra el juicio y
la economía de la lectura. **No forma parte de la cadena `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**:
no comparte ACs, no consume su contador de corrida, no toca sus archivos. Las superficies compartidas
son **tres**, medidas el 2026-09-20: el índice de lecciones (éste y las fases vivas de
`REFACTOR-WHATSAPP`), el archivo que este plan **no** escribe pero sí lee como fuente de verdad
(`scripts/run_all_validations.py`, declarado dentro del alcance del hermano
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20` → deuda **D10**), y la raíz `evidence/` (ver §Correcciones,
R5: la evidencia de este plan vive en su propio subdirectorio). Detalle en `dependencias-fases.md`
§Conflictos.

## Índice documental

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): ocho consultas re-ejecutables con su
  resultado medido, catorce lecciones con dueño y efecto concreto sobre ACs reales, cinco descartes, y
  la capa tibia (QMind) **ya consultada** el 2026-09-20 con su comando corregido, y el
  balance de lo que FASE-A aplicó de verdad (§5, 2026-09-21).
- [Plan maestro](01-plan-maestro.md): las mediciones A1–A8 (cuatro aserciones vencidas —con A3
  re-medida—, un grep con cero coincidencias, la auto-refutación A6, la carga de lectura A7 y la
  población bajo el patrón A8), la matriz de decisión, AC1–AC23 y la deuda D1–D10.
- [Contrato de ejecución](04-contrato-ejecucion.md): permisos, **regla de cero red**, reglas sobre el
  pack generado, corte de presupuesto y por qué no hay FASE-VERIFY.
- [Dependencias y bloqueantes](dependencias-fases.md): cadena, herencias, conflictos de archivo.
- [Checklist de implementación](06-checklist-implementacion.md): matriz de ACs con el artefacto donde
  cada uno se lee.
- [Prompts de fase](05-prompt-inicio-sesion-fase-A.md) A · B · C · [D](05-prompt-inicio-sesion-fase-D.md)
  · [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md).
- [Documentación post-proyecto](09-documentacion-post-proyecto.md) y
  [Análisis post-implementación](10-analisis-post-implementacion.md): acumulativos, se llenan por fase.

## Cinco sesiones, una fase por sesión

| Orden / prompt | Objetivo | Complejidad | Estado |
|---|---|---|---|
| 1 · [A](05-prompt-inicio-sesion-fase-A.md) | `validate_governance_numbers.py`: aserción contra fuente dinámica, denominador, tres estados. AC1–AC5 | MEDIA / alta consecuencia: es el guard de cualquier edición futura de `.agents/` | **✅ VERIFICADO OFFLINE 2026-09-21** (rojo y verde en `evidence/…/FASE-A/mutation/`) |
| 2 · [B](05-prompt-inicio-sesion-fase-B.md) | `decision_client.py`: costura neutra, contract test de forma, extensión a un segundo proveedor **probada**. AC6–AC9 | MEDIA-ALTA | **✅ VERIFICADO OFFLINE 2026-09-21** (`files_changed_to_add_provider: 1`, rojo del contract test en `contract.txt`, 9 mutantes en `mutation/`) |
| 3 · [C](05-prompt-inicio-sesion-fase-C.md) | `triage_lesson_relevance.py`: pertinencia **aditiva** sobre el índice generado, con su aceptabilidad medida. AC10–AC15 | ALTA | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE en su mecánica (AC10–AC14; AC15 ⚠️ con `acceptance = NO-EJERCITADO`).** Ejecutada con mandato propio del operador y corte «hasta listo para revisión». **Sus 37 rutas propias sí entraron al repositorio y sí se empujaron** (commit `5817edd`, con `7f2e9f9` delante por dependencia técnica; push `da382b1..5817edd` del 2026-09-24 por instrucción literal del operador), y **lo que quedó fuera del commit fueron sus documentos de cierre, el par del índice y `REGISTRY.md`** — «fase cerrada» no implica «fase versionada». ⟦**Rectificado el 2026-09-25 por la conciliación final de la orden de calidad**: esta fila decía «**sin commit y sin push**», y con eso contradecía la cabecera de este mismo README y la fila 3 de `dependencias-fases.md`. Separa los cuatro momentos: implementación y evidencia **cerradas**; código **commiteado y empujado**; documentos de cierre **sin commitear**⟧. Sus cinco enmiendas (E1–E5) se implementaron como estaban resueltas, no reinterpretadas: `choice` de dos opciones con umbral sobre `confidence`, check de frescura **propio** sobre el JSON, tres causas del suelo sin colapsar, propuestas que **no** entran en §2 y `acceptance` sin simular. Evidencia en `evidence/…/FASE-C/`. **No cierra la orden de calidad §6: eso lo declara su propio expediente.** |
| 4 · [D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga total de lectura**. AC19–AC23 | MEDIA: gobierna lo que todas las sesiones futuras van a leer | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE (AC19–AC23; AC16/AC17/AC18 en su parte).** Mandato propio del operador y corte **«hasta listo para revisión»**: sin commit ni push. **5 packs = las 5 fases del plan** (COMPLETO 4 · SECCION-NO-RESUELTA 1 · FUENTE-AUSENTE 0) dentro de `briefing/` del propio plan; `.agents/` con **cero bytes aportados** (observador de escrituras + sha256). Delta de carga medido con `stat -c %s` en los dos lados y con la resta **entre cargas totales** (concatenar no es ahorrar: el workflow canónico entra en los dos lados mientras **D3** no lo rebane); **sus bytes, sus tokens y su porcentaje no se copian en esta tabla** — viven en la fila «Carga de lectura A7» de este README y en su artefacto `evidence/…/FASE-D/carga.json` (**L-VCF-19**). Frescura por **sha de `sources[]`**, HEAD como procedencia (test que prohíbe que venza). **49 casos** en `tests/quality_gates/phase_briefing/`, mutación con rojo y verde, y D6 **re-declarada dormida** sin reabrir C. Evidencia: `evidence/…/FASE-D/`. **Lo que no cierra**: D3, D6, D7 y la escritura de la convención `Lee …` en el template (deuda nueva **S16**) |
| 5 · [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Sync, CHANGELOG, `REGISTRY.md`, decisión sobre D1 y D2/D3, write-back (re-leyendo su interfaz: **D10**) y archivado | MEDIA | **✅ CERRADA EN SU PARTE OFFLINE el 2026-09-25** — C0 ejercido: `VERSION.yaml` → **4.78.0** (`Gobernanza, costura, pertinencia y carga medida`), sync de cabeceras, `DOMAIN_PRIMER.md` regenerado con su writer, `[4.78.0]` en `CHANGELOG.md` y registro en `REGISTRY.md` por su único escritor. **Sin pipeline, sin red y sin subir nada**: Q7 (D8), `--upload` (D9), `git mv`, `--fix`/`--update-baseline`, commit y push siguen **PENDIENTE-AUTORIZACION** cada uno con su permiso propio. Evidencia: `evidence/…/FASE-RELEASE/` (12 archivos). Dos defectos de instrumento declarados en el CHANGELOG: los writers reescriben en CRLF y `readme_version_header` no goberna la fecha legible del README |

Cadena: **A → B → C → D → RELEASE**. A y B son técnicamente independientes; C consume a ambas y D a
las tres. **FASE-VERIFY no aplica**: §4.6 pide tres criterios y el de «fase con ejecución E2E» no
existe aquí, porque este plan tiene prohibida la pipeline y la red.

## Correcciones aplicadas (auditoría de la concepción, 2026-09-20)

Nueve fallos encontrados sobre **código vivo** y sobre el **Knowledge Center** (notebook
`iah-cli-lecciones`, cuatro `retrieve` ejecutados el mismo 2026-09-20). Ninguno tumba el diseño; todos
eran premisas publicadas como hechas. Cada fila dice qué se corrigió y dónde.

| # | Qué estaba mal | Corrección aplicada | Dónde quedó |
|---|---|---|---|
| **R1** | A3 publicaba como observado `[12/15]`, que es la etiqueta de `def _check_dependencies`. El write-back imprime `[15/15]` | Fila A3 re-escrita con su emisor correcto + rectificación datada que reconoce que el plan que caza cifras vencidas publicó una vencida | maestro §1 (tabla y nota de rectificación), Q5 de `00-`, `10-analisis` (matriz de hallazgos) |
| **R2** | AC1 exigía «exactamente A1–A4 y ninguna otra» sin regla de población: el escaneo encuentra **22 instancias `[N/M]` en 17 líneas** más 2 formas «check N» | Nueva medición **A8** + regla de población con tres clases (viva / histórica congelada / vigente-correcta), `occurrences[]`, `historical_excluded[]` y su publicación obligatoria | maestro §1 A8, §4 AC1 y AC2, `06-checklist`, prompt de FASE-A |
| **R3** | Se atribuía el pin «El quick son 11 checks.» al prompt de FASE-C de `REFACTOR-WHATSAPP` | Atribución corregida con los cuatro sitios medidos (README, 06, 09, 10 de ese plan). **⟦Antecedente del 2026-09-20; uno de los cuatro ya no existe: el bloque de arranque de su `README.md` fue de las enmiendas del bloque C de la orden de calidad y hoy manda el comando. Véase §Conflictos de archivo de `dependencias-fases.md`⟧** | maestro §2, README §Deja sin hacer, `dependencias-fases` |
| **R4** | «`run_all_validations.py`: nadie» era falso: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE) lo declara dentro de su alcance y cambia el writer del que depende el cierre | Fila de conflicto re-escrita + deuda **D10** (re-leer la interfaz del write-back en el RELEASE, sin convertirlo en dependencia de ejecución) | `dependencias-fases` §Conflictos, maestro §2 y §6, `04-contrato` |
| **R5** | La evidencia se escribía en `evidence/FASE-A/` … `FASE-D/`, que **ya están ocupadas** por `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` (con `faseA_baseline_pre.txt` y su par, nombres que el contrato de este plan repetiría) | Las 65 rutas del plan re-punteadas a `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`; la plantilla de `.agents/` sigue diciendo `evidence/fase-{N}/`, y eso queda **declarado** (no corregido: AC17) | los doce archivos del plan; nota en `04-contrato` |
| **R6** | Tres afirmaciones del README ya eran falsas al medirlas: «el índice aún refleja el nombre anterior» (está regenerado y fresco: `[OK] … (320 IDs)`, 0 coincidencias con el nombre viejo), «el árbol está limpio» (índice modificado sin commitear + plan sin trackear) y el valor vigente de A7 | Bloque de límites re-escrito con lo medido; el bloque de arranque deja de afirmar limpieza y ordena medir `git status`; A7 publicado con valor nuevo, comando y fecha | README, prompt de FASE-A |
| **R7** | D8 decía «re-ejecutar Q7, el CLI no está disponible»; y el comando publicado (`--nb iah-cli-lecciones`) devuelve `error: Bad request` | Q7 marcada como **ejecutada** el 2026-09-20 con sus resultados capitalizados (L-V2.1, L-V2.2, D-V2.1) y el comando corregido al ID del notebook | `00-lecciones` Q7 y §4, maestro §6 D8, README, prompt RELEASE |
| **R8** | Las familias no cubiertas se enumeraban «de oído» y faltaban las que hoy también están vencidas | AC2 y AC17 publican las cuatro familias medidas: prosa sin patrón, conteos fuera de los documentos de gobierno (**`AGENTS.md` con «10/10 … y 14»**, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`), **pins en `tests/`** (`tests/test_validate_plan_closure.py` assertiona `[5/7]`) y fuentes dinámicas que no son etiqueta impresa; AC16 barre `tests/` al medir quién afirma el 11 y el 7 | maestro §4, `06-checklist`, prompt FASE-A |
| **R9** | Tres precisiones: la razón por la que el pack no lleva ruta absoluta estaba mal explicada; el «Dato externo» del SDK se presentaba como medido; y el conteo de dueños del Paso 0 decía 7 con 6 nombres | Razonamiento corregido (lo que rompe una referencia es que su destino no exista al escanear, no la forma de la ruta), origen del dato declarado explícitamente como externo, y dueños corregidos a **6** — con la atribución de `D-V2.1` arreglada, que la cazó el propio `validate_lesson_capitalization.py` por `C7` al re-validar este `00-` | prompt FASE-D, maestro §2, `00-lecciones`, `10-analisis` |

**Lo que NO cambió en aquella auditoría del 2026-09-20** (antecedente, no estado actual de D1): las
cuatro aserciones vencidas seguían vivas en `.agents/` y ningún check las sostenía (A1 `[9/11]`, A2 `[10/11]`, A3 `[15/15]`, A4 `[10/11]`); el
hook sigue en 7; §4.6 sigue sin activar FASE-VERIFY (criterio 2 cae); el contrato de cero red, la
prohibición de tocar `.agents/`, `run_all_validations.py` y el hook, y la cadena A→B→C→D→RELEASE
quedan intactas.

## Lo que este plan deja deliberadamente sin hacer

- **No entra Jev. Decisión del operador del 2026-09-20**, con el acceso ya habilitado. FASE-B construye
  la costura y AC9 certifica que **añadir** el proveedor cuesta un archivo; la comparación de
  proveedores se pospone como deuda **D7**. Consecuencia aceptada: ningún AC mide calidad de
  decisiones de un modelo real — miden forma, aislamiento y no-regresión.
  **Precisión de AC9 declarada el 2026-09-23** (orden de calidad §4.A): lo certificado es **extensión
  local con un proveedor falso del repo** — `files_changed_to_add_provider = 1`, medido por sha256
  sobre la frontera copia+puerta, sin red ni credenciales. **No** es el coste total de integrar un
  **SDK real** en un archivo: sus dependencias y su autenticación no se midieron ni pueden medirse bajo
  la regla de cero red, y dónde vivirá ese `import` es **S10**/D7 (el propio `--costura` imprime ya
  esta acotación en su clave `alcance_de_ac9`).
- **No hace el lint de contradicciones semánticas** (`validate_plan_semantics.py`), que era la otra
  mitad del diagnóstico. Queda como deuda **D6** con un disparador medible: la **aceptabilidad** que
  publique FASE-C. Si el triaje sale inaceptable, D6 **no** se activa — no se apila un segundo
  consumidor sobre una base que no funcionó.
- **No altera el conteo de checks.** AC16 es un **delta 0** con su par pre/post por fase; el número
  vigente lo imprime la corrida y lo contrasta `validate_governance_numbers.py` (así lo dejó el bloque B de
  la orden de calidad, y así lo formula ya el contrato §Enmiendas E5). Motivo medido el 2026-09-20 y
  **re-contado el 2026-09-24**: en `REFACTOR-WHATSAPP` publican la cifra **cinco archivos, todos
  registros de fases cerradas** — `06-checklist`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de
  FASE-G (medido con `grep -rl` sobre `11/11` y `11 checks`; los prompts de A/0/B no la contienen) —,
  evidencia histórica que no se reescribe. Lo que antes incluía el bloque de arranque de su `README.md`
  ya no está, porque ese bloque se reconcilió con el punto de reanudación real y pasó a mandar el
  comando. **Promover algo aquí invalidaría la medición de fases ajenas y no satisface el disparador de
  D2** (deuda D2).
- **No edita `.agents/`.** Las cuatro aserciones vencidas se **reportan**, no se reescriben: quien
  corrige la frase a mano produce la fosilización siguiente (deuda D1, con instrucción literal).
- **No rebaná el workflow canónico** (deuda D3). FASE-D hace lo que sí puede hacerse sin tocarlo:
  **unificar** las lecturas que cada fase declara en un pack derivado, sin sustituir ninguna fuente.
- **No filtra lecciones.** El triaje propone, el umbral se publica con su acción por debajo y ninguna
  fila de §2 puede desaparecer: eso es AC10 con su test.
- **No promete velocidad sin número.** AC20 obliga a medir el delta de carga con el mismo comando en
  los dos lados; **un delta cero o negativo es resultado válido si se explica**.

## Prerrequisitos y límites visibles

- **Ninguna credencial es necesaria y no hay llamadas de red en ninguna fase** (contrato §Regla de cero
  red). Las pruebas de proveedor se hacen con proveedores falsos.
- **La capa tibia del Paso 0 SÍ se consultó, pero después de concebir.** Al concebir, QMind
  `iah-cli-lecciones` no estaba accesible en la sesión (consulta Q7, declarada NO EJECUTADA) y se
  aplicó el fallback del executor. La auditoría del 2026-09-20 lo ejecutó con el CLI disponible
  (v3.3.0) y sus resultados ya están capitalizados en `00-lecciones-capitalizadas.md` (L-V2.1,
  L-V2.2, D-V2.1). **Queda un fix de forma: `--nb` exige el ID del notebook, no su nombre** — la
  forma con el nombre, que es la que publica el workflow canónico, devuelve `error: Bad request`.
  D8 queda como re-correr la consulta antes de RELEASE, no como primera vez.
  Límite: el triaje calibra contra 320 IDs definidos y 50 citados sin definición — **re-medido**,
  porque al crearse este plan sus propias cifras vencieron (medición A6).
- **Commitir requiere regenerar el índice** en el mismo commit (`[6/7]` del hook): los archivos de este
  plan nombran IDs reales del corpus. Medido el 2026-09-20 al auditar: el índice **ya estaba regenerado
  y fresco** (`build_lesson_index.py --check` → `[OK] … (320 IDs)`; 0 coincidencias con el nombre
  anterior del directorio, 15 con el vigente) y sus dos archivos estaban **modificados sin commitear**,
  con el plan **sin trackear**. **Ese estado ya no existe**: la auditoría se commiteó y empujó con
  instrucción literal del operador el 2026-09-20 — `2c9d0c1`, paridad `0/0` con `origin/master`
  verificada con `git ls-remote`—, así que desde aquí el árbol de partida es limpio y lo que cada fase
  encuentra modificado proviene de su propia edición o de la fase viva de `REFACTOR-WHATSAPP`.
- **Las cifras de este README son estimaciones con divisor declarado** (bytes/4), no recuento de
  tokenizer. A7 suma **siete** documentos (el octavo que declara leer la fase medida es un archivo de
  `evidence/` y queda fuera de la suma, como dice su pie) y caducan cuando cambia cualquiera de ellos:
  **ya caducaron el mismo día de la concepción** (254.010 → 263.973 bytes; ver maestro §1, A7).
- Commit y push **no** están autorizados por la existencia de este plan; cada fase deja checkpoint y
  pide su propia instrucción literal. Así se hizo con la auditoría del 2026-09-20: `2c9d0c1` se
  commiteó y se empujó solo tras la instrucción escrita del operador (y tras ofrecer el escaneo L3, que
  el operador saltó).

## Inicio de la siguiente sesión

**FASE-A y FASE-B están cerradas (VERIFICADO OFFLINE el 2026-09-21), FASE-C está cerrada el 2026-09-24 (VERIFICADO OFFLINE en su mecánica, AC10–AC14, con AC15 ⚠️ `acceptance = NO-EJERCITADO`) y FASE-D está cerrada el 2026-09-24 (VERIFICADO OFFLINE, AC19–AC23, con sus cinco packs y su delta de carga medido). **FASE-RELEASE está ejecutada y cerrada en su parte offline el 2026-09-25** (release 4.78.0: fuente única, cabeceras por su writer, DOMAIN_PRIMER regenerado con el suyo, CHANGELOG y registro en REGISTRY por su único escritor). El plan ya no tiene fases que abrir: lo que resta son checkpoints, cada uno con su permiso propio y **ninguno concedido por este README** — C0 los destinos escribibles
(offline significa sin red, NO con permiso de escribir: el sync sin `--check` reescribe `README.md`, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md`), C1 la consulta Q7 (D8), C2 el `--upload` (D9), C3 el `git mv` de archivado, C4 las correcciones de corpus (`--fix`/`--update-baseline`), C5 commit y C6 push ⟦esta fila decía «el siguiente y último tramo es FASE-RELEASE, que requiere su propio mandato»; quedó vencido el mismo 2026-09-25⟧.** El estado
de B se lee en su
matriz vigente §13. **⟦Precisión del 2026-09-24⟧: lo que se autorizó y ejecutó ese día fueron dos cosas
distintas —el bloque C de la orden de calidad (enmiendas prospectivas sobre los documentos de los cuatro
planes) y, en una sesión posterior con mandato propio, el piloto FASE-C— y no son la misma cosa.** Lo que
cambia para quien abra la sesión: las filas `CONTEXTO/D` y
`CONTEXTO/RELEASE` del contrato dejaron de estar en contradicción (carga total, frescura no circular,
tres momentos con tres permisos — ⟦**ampliado el 2026-09-25**: a esos tres se les sumó **C0** como cuarto
permiso y momento previo: los destinos escribibles deben autorizarse literalmente antes de escribir;
offline significa sin red, no con permiso de escritura⟧). **E1–E5 se implementaron como estaban resueltas: no hubo elección que
tomar en la sesión de C.** El prompt canónico de FASE-D vive en `05-prompt-inicio-sesion-fase-D.md` y
**no se copia aquí**:
copiarlo sería fabricar la segunda fuente estática que este plan existe para cazar (medición A6).
Lo que sí se publica aquí es el estado re-medido, con su comando y su fecha, para que la siguiente fase
no lo asuma. **Con una excepción deliberada, añadida el 2026-09-22 tras tres commits que se vencieron
a sí mismos: la fila de HEAD y paridad ya no publica cifra, publica solo el comando.** El motivo es
medición A6 aplicada al dato más inestable del repo — cada commit documental mueve el HEAD y suma uno a
la paridad, así que cualquier cifra que escriba esta tabla nace refutada por el commit que la lleva
dentro. Lo que la tabla sí sostiene son los **hechos no numéricos** (FASE-B commiteada y empujada, su
barrido documental y su push con instrucción literal del 2026-09-22, `eecf246` ajeno publicado con ella,
qué ruta queda fuera del commit y cómo se trata; y que **FASE-C quedó parcialmente versionada**: sus 37
rutas propias entraron en `5817edd` y se empujaron, mientras sus documentos de cierre y el par del índice
siguen en el árbol de trabajo junto al de otras sesiones ⟦**rectificado el 2026-09-25**: la frase que aquí
afirmaba «FASE-C cerró sin commitear ni empujar» contradecía a la cabecera de este README y a
`dependencias-fases.md`⟧):

| Qué re-medir al abrir **FASE-RELEASE** (la tabla se escribió para abrir FASE-D y conserva sus mediciones; lo que cambió es el destinatario: **D está cerrada el 2026-09-24**) | Antecedente medido al cerrar la sesión anterior — **no es un valor para copiar**: la columna de la derecha manda el comando | Comando |
|---|---|---|
| HEAD y limpieza | **No se publica cifra de HEAD ni de paridad**: son el dato más inestable que este plan escribe y **cada commit documental las mueve** (antecedentes del 2026-09-22, ya refutados por el paso del tiempo: HEAD `612efd0`, paridad `0/3`). Lo que C sí necesita saber y no se deduce del comando: que **FASE-B está commiteada** (`647f436`) con sus dos barridos documentales encima; que **el push se hizo el 2026-09-22 por instrucción literal del operador y publicó hasta `b764e8d`**, con lo que quedó publicado también el commit **ajeno** `eecf246` (ROADMAP v4.3), ancestro obligado de esta fase — y que **un commit local posterior vuelve a dejar paridad sin empujar, así que el estado del remoto se mide, no se infiere de esta frase**. Y en `git status` queda **una** ruta ajena (`EVALUACION-JEV/dependencias-fases.md`, modificada), que no es de este plan y sobre la que **no** se hace `git checkout` | `git rev-parse --short HEAD`, `git status --porcelain`, `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD`, `git ls-remote origin refs/heads/master` |
| Checks del `--quick` | **11** (delta 0, AC16) | `grep -cE '^\\s*print\\(f?"\\[[0-9]+/11\\]' scripts/run_all_validations.py` |
| Pasos del hook | **7** (delta 0, AC16) | `grep -cE '^#   \\[[0-9]+/[0-9]+\\]' scripts/git_hooks/pre-commit` |
| Funciones de test canónicas (método grep) | **No se publica cifra**: la imprime el comando de la derecha. ⟦Asunto retirado de la pendiente actual por el bloque B⟧: esta fila decía además «`AGENTS.md` sigue publicando 4.246 y su cifra está vencida por tráfico ajeno», y eso **ya no describe el árbol** — el bloque B dejó una sola fuente (la tabla fechada `Cobertura por Modulo`) y las demás referencias apuntan a ella. El antecedente medido y su límite (la familia de conteos que `validate_governance_numbers.py` no cubre) vive en §8 de la fuente única de B, no aquí | `grep -rE '^\\s*def test_' tests --include=*.py \\| wc -l` |
| Herencia de forma para C — **ya consumida el 2026-09-24** | `coverage_basis` y el tri-estado, que C re-utilizó **sin reinventarlos**; y la costura de B como **única** puerta al proveedor (C no importó un SDK: es AC6, no estilo). ⟦**Lo que D hereda de C**, y lo hereda **aceptándolo, no reabriéndolo** (contrato §Cierres incrementales, punto 8): los tres estados del índice, el umbral sobre `confidence` de una pregunta `choice` de dos opciones, la aditividad con su rojo en `FASE-C/mutation/`, el denominador con sus ceros, y un tramo semántico que salió **`NO-EJERCITADO`** — D puede exhibir los candidatos de pertinencia pero **no** presentar esa exhibición como aceptabilidad obtenida (§E4). D6 sigue dormida y su disparador se evalúa con D7, no en D⟧ | `evidence/…/FASE-A/informe.json`, `evidence/…/FASE-B/informe.json` → `costura`, `evidence/…/FASE-C/informe.json`, `04-contrato-ejecucion.md` §Enmiendas y §Cierres |
| Población AC6 que D no debe mover | **0** imports del SDK/adapter fuera de `scripts/decision_client.py`. **Re-medido al cerrar FASE-C el 2026-09-24 con `SIN-HALLAZGOS` y `exit 0`; la cifra de población no se transcribe aquí — la imprimen los dos comandos de la derecha, y el desfase entre ambos (archivos sin commitear, que `git ls-files` no cuenta) se desglosó archivo por archivo en `evidence/…/FASE-C/cero-red.txt`, porque un residuo sin descomponer es lo que capitalizó S11 / L-VCF-11. C era el consumidor que podía tentar un import y no lo hizo: sus cargas por ruta son `decision_client.py`, `build_lesson_index.py` y el proveedor falso montado por entorno.** Antecedente del 2026-09-23: el escáner incluye **696** `.py` y `git ls-files '*.py'` cuenta **696** → **residuo 0**. **Antecedente vencido (S11, ya aceptada):** al cerrar B las dos cifras eran 692/691 y el residuo de 1 era `.venv-wsl/bin/activate_this.py`, una exclusión **no declarada** del denominador; el bloque A de la orden de calidad metió `.venv-wsl` en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION` (`fdd397f`) y hoy el escáner publica su conteo (582 archivos excluidos por ese directorio). Re-medir tras escribir los tests de C, porque C es el consumidor que podría tentar un import | `python scripts/decision_client.py --scan-imports`, `git ls-files '*.py' \| wc -l` |
| Índice de lecciones — **D añadió corpus al índice y eso lo vence** | Los packs generados son `.md` **dentro del corpus que escanea `build_lesson_index.py`** (viven bajo `.opencode/plans/<PLAN>/briefing/`), así que el acto de generarlos copia IDs y **vuelve a vencer el par**: es la medición A6 del maestro cayendo sobre un artefacto derivado, no un defecto del generador. Por eso el paso 5 del contrato obliga a regenerar el índice **sobre el mismo árbol final verificado**, y por eso el commit del plan tiene que llevar el par dentro. Medido al cerrar D: `--check` da FAIL sobre un árbol limpio extraído con `git archive HEAD` y pasa a `exit 0` al regenerar **en ese árbol** (S15, `fuente_fecha = mtime`) — commitear el par desde otro árbol **no** lo cura. Antecedente: el par `.md`+`.json` **viajó dentro de `647f436`** (`--numstat`: `LECCIONES-INDEX.md` 24+/17−, `lecciones_index.json` 100+/14−), así que `[6/7]` del hook ya no corta este cierre. **330 IDs** definidos al cerrar B y **332** re-medidos el 2026-09-22 tras el barrido de citas (sube porque el propio barrido define L-VCF-11 y L-VCF-12 — A6 otra vez: la cifra caduca al escribirla); re-medir al abrir D, y volver a medir al cerrarla: la escritura documental de la propia fase mueve la cifra (A6) | `python scripts/build_lesson_index.py --check` |
| Carga de lectura A7 (plan medido) y carga propia (este plan) | A7 sigue en **263.973 bytes ≈ 65.993 tokens** sobre `REFACTOR-WHATSAPP`. **Lo que D midió por primera vez sobre este propio plan: 5 fases · 34 fuentes declaradas · carga total 1.648.109 bytes antes del pack y 1.431.388 después (delta 216.721 ≈ 54.180 tokens, divisor 4) = **13,15 %** de la carga total — cifra recalculada el 2026-09-25 por la conciliación final de la orden de calidad como `216.721 ÷ 1.648.109` sobre `carga.json`; es el delta de **estos cinco packs medidos con este método**, no un ahorro general del proceso, ni un ahorro por fase, ni tiempo activo. Sustituye a las tres cifras divergentes que el plan había ido copiando de sí mismo (`13,08 %`, `12,8 %`, «en el orden del 12 %»), **ninguna de las cuales reproducía su propio artefacto**;
**y su vigencia está acotada al árbol que FASE-D midió**: la conciliación final del 2026-09-25 re-corrrió el
mismo comando sobre el árbol vigente y **confirmó el cambio de forma, no una nueva cifra**: el pack de
RELEASE pasó de `SECCION-NO-RESUELTA` (`fuentes_ausentes: ["los cuatro prompts de fase"]`) a **COMPLETO con
10 fuentes**, y el denominador de **4 COMPLETO + 1 SECCION-NO-RESUELTA / 34 fuentes** pasó a
**5 COMPLETO / 37 fuentes**. **Sus bytes y su porcentaje no se transcriben aquí**: cada corrida posterior
a esta fila mide un corpus que esta edición ya cambió (A6 cayendo sobre un artefacto autorreferente), así
que la re-medición vive con su salida completa en
`evidence/…/CONCILIACION-FINAL-ORDEN-2026-09-25/11-carga-corrida-3.txt` y su contraste en
`…/12-huellas-post.txt`. **No se re-escribió `carga.json`** — es evidencia cerrada de FASE-D
(**S12 / L-VCF-12**) y la corrida usó `--carga -` / `--informe -`; y **esta fila es la única fuente de esas cifras**: los cuatro documentos del corpus que el generador copia (`00`, `06`, `10` y `dependencias-fases`) las referencian y **no** las re-transcriben, porque copiarlas las vence (**L-VCF-19**). Dos cifras que la fase dejó medidas y que el RELEASE no debe re-copiar: el workflow canónico pesa hoy **108.017 bytes**, no los **98.694** que publica el maestro §1 (+9.323 por las ediciones del bloque B — A6 otra vez), y **0 de 121** prompts archivados declaran su lectura en el formato que parsea el generador (deuda **S16**). El pack de un archivado sale `SIN-DECLARACION` y su `--check` imprime `SIN-FUENTES`, no `OK` | `stat -c %s`, `python scripts/build_phase_briefing.py --listar-declarado --plan <plan>`, `python scripts/build_phase_briefing.py --plan <plan> --carga -` |
| Presupuesto (R2.1) | el instrumento **sigue sin correr**: `find . -name "*.jsonl"` (sin contar `venv/`) devuelve **0** también medido el **2026-09-22**, sexta reproducción de la precondición que capitalizó **D-V2.1**; **séptima al abrir FASE-C y octava al abrir FASE-D, el 2026-09-24: `find . -name "*.jsonl" -not -path "./venv/*"` volvió a dar 0.** D publicó su presupuesto como auto-reporte con unidad declarada (`tool_use`/ids únicos, **no comparable** con las corridas que sí usaron el instrumento) en `FASE-D/baseline-pre-post.md`; métrica retirada, nunca estimada (R2.1) | `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` |

Además, cuatro cosas que B midió y C no debe volver a descubrir: la costura resuelve al proveedor
**por entorno** (`IAH_DECISION_PROVIDER` + `IAH_DECISION_PROVIDERS_DIR`, sin default alguno) y su
`provider_status` es el tri-estado que C reutiliza; **ningún proveedor entra en este plan** (la deuda
**D7** sigue abierta y su consumidor natural es **D6**, no C); y donde B dejó escrito el problema que
C hereda sin resolverlo — **dónde vivirá el `import` del SDK cuando D7 se active** — está en
`10-analisis-post-implementacion.md`, no en el código. Y sigue en pie lo que A midió: el árbol de
`run_all_validations.py` **no está libre** (**D10**) y la regla de **orden de cierre** del hermano
`EVALUACION-JEV` deja este plan cerrarse antes de que aquel publique. Sobre la guarda operativa que este
barrido aprendió a costa de la evidencia de FASE-A, **la instrucción vigente es esta**:
`python scripts/validate_governance_numbers.py --report` **sin destino imprime y no escribe** — es el
comportamiento por defecto desde que se aceptó **S12** (bloque A de la orden, `fdd397f`)—, así que ya no
hace falta redirigirlo para re-muestrear. La regla general de la lección **L-VCF-12** sigue vigente y sí
aplica al `--report` del futuro `triage_lesson_relevance.py`: antes de correr un verificador con
`--report`/`--write`, mirar si su default toca evidencia commiteada.

> **[Rectificada el 2026-09-23; reescrita el 2026-09-24 para no dejar dos instrucciones contrapuestas.]**
> Ese default de escritura fue
> corregido por el **bloque A** de `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`
> (commit **`fdd397f`**, ajeno a este plan) y su aceptación está registrada en
> `dependencias-fases.md` §Conciliación. Medido de nuevo aquí sobre el árbol vigente:
> `python scripts/validate_governance_numbers.py --report` **sin destino imprime y no escribe** —
> `exit 1` con `HALLAZGOS` A1–A4 en stdout JSON puro (el aviso de no-escritura va a stderr), y el
> `sha256` de `evidence/…/FASE-A/informe.json` queda **idéntico** antes y después. **S12 queda
> aceptada**; la lección **L-VCF-12** sigue vigente como regla general (*antes de correr un verificador
> con `--report`/`--write`, mirar si su default toca evidencia commiteada*), pero ya no como guarda
> obligada para re-muestrear este script. **Antecedente de esa conciliación, no estado vigente:**
> el rojo contractual A1–A4 seguía presente porque aquella sesión no editaba `.agents/` (AC17, D1/S1).
> B recibió después autorización de corrección; ni ese rojo histórico ni los verdes de los dictámenes
> retirados certifican el estado actual. **D1/S13 remiten únicamente a la matriz vigente §13** de la
> fuente única indicada al inicio; no se re-transcribe aquí su estado.

## Cierre y aceptación

Cada fase incorpora su evidencia y su cierre incremental; no se difiere ningún control a RELEASE.
Techo alcanzable de un AC: `VERIFICADO OFFLINE` **con su mutation check en disco**, `⚠️ PARCIAL`, o
`NO-EJERCITADO` con motivo. Un `[OK]` sin denominador no informa (L-R.3) y un verde sin rojo previo se
declara sospechoso (L-VUP-5).
