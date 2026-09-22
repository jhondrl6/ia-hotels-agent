# Análisis Post-Implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Se crea **desde la concepción** del plan, no al final. Cada fase actualiza su fila, sus lecciones,
> sus métricas y sus seguimientos al cerrar. FASE-RELEASE consolida la matriz.

## Resumen de Ejecución

| Fase | Estado | Iteraciones medidas (unidad e instrumento) | Cortes autorizados | Notas |
|---|---|---|---|---|
| FASE-A | **VERIFICADO OFFLINE 2026-09-21** (AC1–AC5; AC16/AC17/AC18 en su parte de A) | Instrumento canónico **no corrió**: `find . -name "*.jsonl"` = 0 en el workspace (condición D-V2.1, re-medida el 2026-09-21). Se retira la métrica de iteraciones y se publica en unidad contable en disco: **14 rutas propias** en el árbol de trabajo, 933 líneas de instrumento, 23 funciones de test / 28 casos. **No comparable** con auto-reportes en `tool_use` de otros planes | Ninguno: la fase cerró su presupuesto documental y sus 3 tareas de código en la sesión (R3 permitía 4) | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/`: `informe.json`, `baseline-pre-post.md`, `ac17-y-presupuesto.md`, `mutation/` (verde + 6 rojos), par pre/post y las dos corridas del quick. **Commiteado el 2026-09-21 en `a7564ae`** con el par del índice de lecciones dentro (`[6/7]`) y con los dos archivos ajenos a la fase excluidos a propósito (instrucción literal del operador para el commit; push no autorizado) |
| FASE-B | PENDIENTE | — | — | — |
| FASE-C | PENDIENTE | — | — | — |
| FASE-D | PENDIENTE | — | — | — |
| FASE-RELEASE | PENDIENTE | — | — | — |

**FASE-VERIFY no aplica** (criterio 2 de §4.6 cae: no existe fase con ejecución E2E, y además este
plan no hace llamadas de red). Por tanto ningún AC de este plan puede alcanzar `SUPERADO EN E2E`.

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

Mínimo 3 por fase completada (regla del executor). Formato: **qué pasó / por qué / qué lo previene** +
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
| **L-VCF-5** | Al medir «quién afirma el 11» (AC5/AC16, barrido de `tests/` por L-V2.3) resultó que **esta misma fase añadió 4 pins nuevos del denominador 11** en `tests/`: la aserción `observed == 9/11` del contrato AC1 es, literalmente, un pin | Un test que fija el valor observado de una fuente dinámica *es* una de las fuentes estáticas que el plan denuncia; la familia no cubierta (iii) de AC2 no era teoría | Se declaró en `baseline-pre-post.md` con dueño (D1/D2: al corregir `.agents/` o renumerar el quick, el test se re-ancla con su nota datada) en lugar de debilitar la aserción para que la resta quedara limpia | **INCLUIR** — «medir a quién le duele la renumeración» incluye medirse a uno mismo |

## Seguimientos abiertos

| # | Tema | Dueño | Disparador |
|---|---|---|---|
| S1 | D1: corregir o retirar las aserciones A1–A4 en `.agents/` | FASE-RELEASE de este plan | **Disparador reformulado el 2026-09-21 (era circular, L-VCF-4):** verificador operativo con mutation check en disco (ya cumplido) **y** decisión escrita del operador sobre la forma de la corrección; configuración central |
| S8 | Los **4 pins del denominador 11** que FASE-A escribió en `tests/` al fijar el contrato AC1 (`test_governance_numbers_reproduce_A1_A4.py`) | D1/D2 de este plan | Al corregir `.agents/` (D1) o al promover el verificador a check 12 (D2): re-anclar el test con nota datada, **sin** limar la aserción (L-VCF-5) |
| S9 | El verificador **no está cableado** a ningún gate: corre suelto (`python scripts/validate_governance_numbers.py --report`, salida 1 con A1–A4 presentes). Promoverlo al `--quick` es exactamente **D2** y rompería la cifra que `REFACTOR-WHATSAPP` pinea en cuatro documentos | D2 | Sesión previa al `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` |
| S2 | D2/D3: promover el verificador al `--quick` y rebanar el workflow | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` |
| S3 | **D6: lint de contradicciones semánticas** (`validate_plan_semantics.py`) | Plan propio posterior; entra en **este** directorio si el disparador se cumple vigente este plan | El `acceptance` que publique AC15 en FASE-C. Si el triaje sale inaceptable, **no se activa** |
| S4 | **D7: activar el proveedor de decisiones ya habilitado** y correr la comparación | Plan propio posterior | Decisión del operador del 2026-09-20 de no entrar ahora; AC9 ya dejó la costura probada |
| S5 | D8: la consulta Q7 de QMind **sí se ejecutó** en la auditoría del 2026-09-20 (cuatro `retrieve`; el comando válido usa el ID del notebook, no su nombre) | FASE-RELEASE | Re-correr solo si el corpus del notebook cambió desde la auditoría, y verificar que las citas de L-V2.1/L-V2.2/D-V2.1 siguen en pie |
| S7 | **D10: re-leer la interfaz del write-back antes del cierre** — `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara dentro de su alcance `validate_qmind_writeback.py` y su conexión en `run_all_validations.py`, y piensa añadir `--title`/`--file` | FASE-RELEASE de este plan | Al llegar el cierre: `--help` contra el árbol vigente y re-escribir el orden de `04-contrato-ejecucion.md` si la firma cambió |
| S6 | D4/D5: verificadores de la resta pre/post (R2.7) y del par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda | Ya asignados antes que este plan; no se reasignan |

## Métricas de Ejecución

- [x] **FASE-A (2026-09-21), en la misma base de medición que su par pre/post** (R2.3): quick
  11→11 (resta 0), hook 7→7 (resta 0), población A8 22/17/2 → 22/17/2 (resta 0), selección de tests
  0→23 funciones (+23, **no** 0: la fase agrega tests y lo dice), canónicas del repo
  4.307→4.330 (resta +23, coherente con la fila anterior). Crudos en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/`.
- [x] Coherencia del índice de lecciones al commitear: `build_lesson_index.py` regenerado el
  2026-09-21 tras escribir los `.md` de esta fase; el commit debe llevar los dos archivos dentro
  (`[6/7]` del hook lo corta).
- [ ] **Carga de lectura por fase, antes y después del pack (AC20)** — con su comando y su divisor.
- [ ] Aceptabilidad del triaje (AC15): propuestos pertinentes / total propuestos.

## Decisiones Arquitectónicas

- [ ] El pack se genera dentro del plan y **no** sustituye ninguna lectura canónica (alternativa
  descartada: rebanar `.agents/`, que es D3 y exige tocar configuración central en vuelo).
- [ ] FASE-B deja un solo proveedor configurable y **no** compara (alternativa descartada: mantener el
  AC9 de comparación, que con un solo proveedor se cerraba declarando `NO-EJERCITADO` y certificaba
  humo).
- [ ] El triaje es aditivo y no filtro, con el coste de esa elección medido en FASE-C.
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
- [ ] `--quick` en 11 checks y hook en 7, composición intacta (AC16).
- [ ] S1–S7 con dueño y disparador vigentes; **D6 resuelta con el número de FASE-C, no con opinión**.
- [ ] Write-back → índice → `git mv` → índice, en ese orden (R2.5, R2.10).
