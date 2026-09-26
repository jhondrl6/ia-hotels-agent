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
| AC16 | A,B,C,D | quick en 11 y hook en 7, inalterados en todo el plan | los cuatro `baseline-pre-post.md` | **A: delta 0** y **B: delta 0 verificados 2026-09-21** (quick 11→11, hook 7→7, `git diff` vacío en los cuatro scripts gobernados; +48 funciones de test declaradas aparte) · **C: delta 0 medido el 2026-09-24** (par `faseC_baseline_pre/post` y `faseC_quick_pre/post`, resta comprobada en `evidence/…/FASE-C/baseline-pre-post.md`; la composición del quick y del hook **no** se tocó, y los valores los imprime la corrida, no esta fila) · **D: delta 0 medido el 2026-09-24** (par `faseD_baseline_pre/post` y `faseD_quick_pre/post` con la resta comprobada en `evidence/…/FASE-D/baseline-pre-post.md` §1 y §5; quick **11/11 con `exit 0`** y hook **7** sobre el árbol final, `git diff` vacío en los cuatro scripts gobernados; HEAD sin cambio entre PRE y POST porque la fase no commiteó, y los 49 casos nuevos se declaran aparte, no como delta del quick) ⟦**Cifra vencida el 2026-09-26, verificación intacta.** El quick pasó a 12 checks y el modo completo a 16 por D2, ejecutada fuera de este plan por instrucción del operador. Las tres mediciones de esta fila (A, B, C) se hicieron contra 11 y contra 7 y siguen siendo el registro de su día: delta 0 significa que la fase no movió el denominador que encontró, no que ese denominador sea el de siempre.⟧ |
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
