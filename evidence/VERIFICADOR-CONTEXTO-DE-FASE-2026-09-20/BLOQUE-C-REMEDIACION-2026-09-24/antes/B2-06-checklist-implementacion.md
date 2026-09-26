# Checklist de implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Leyenda de estados** (R2.4, no negociable): `PENDIENTE` · `VERIFICADO OFFLINE` (test verde **con
su mutation check**) · `⚠️ PARCIAL` (falta el rojo, falta la clave en el artefacto, o solo cubre un
estado) · `NO-EJERCITADO` (el camino no se ejercitó; con el motivo) · `FUERA DE ALCANCE`.
**No existe `SUPERADO EN E2E` en este plan**: no hay corrida (§5 del maestro) y no hay FASE-VERIFY.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está autorizado;
el bloque C y el piloto FASE-C no lo están. Fuente única de resultados y estados D1/S13:
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
| AC10 | C | el triaje **no elimina** fila anclada alguna **y tampoco escribe §2 por su cuenta** ⟦E3⟧ | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` → `removed: []` | PENDIENTE |
| AC11 | C | índice **ausente / vencido / lector-caído** ≠ sin candidatos; **frescura comprobada por el propio C** ⟦ruta (b) cerrada 2026-09-23, E2⟧ | ídem → `index_status` | PENDIENTE (contrato **resuelto**, no la ejecución: C implementa, no elige) |
| AC12 | C | umbral con valor, base y acción por debajo, **sobre `confidence` de un `choice` de dos opciones** ⟦E1⟧ | ídem → `threshold` | PENDIENTE |
| AC13 | C | ≥1 test contra corpus real, skip declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` | PENDIENTE |
| AC14 | C | mutation check del guard de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` | PENDIENTE |
| AC15 | C | denominador, términos, ceros **y aceptabilidad** (dispara D6); con proveedor falso el tramo semántico es **`NO-EJERCITADO`, sin simular** ⟦E4⟧ | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` | PENDIENTE |
| AC16 | A,B,C,D | quick en 11 y hook en 7, inalterados en todo el plan | los cuatro `baseline-pre-post.md` | **A: delta 0** y **B: delta 0 verificados 2026-09-21** (quick 11→11, hook 7→7, `git diff` vacío en los cuatro scripts gobernados; +48 funciones de test declaradas aparte) · C/D pendientes |
| AC17 | A,B,C,D | `.agents/` intocado; familias no cubiertas declaradas | `evidence/…/FASE-A/informe.json` → `families_not_covered[]` + `ac17-y-presupuesto.md` + `git status --porcelain .agents/` (vacio) | **A: VERIFICADO OFFLINE 2026-09-21** · **B: VERIFICADO OFFLINE 2026-09-21** (`git status --porcelain .agents/` vacío; 98.694 / 6.123 bytes idénticos en PRE y POST) · C/D pendientes |
| AC18 | A,B,C,D | capitalización, citas e índice verdes sobre el mismo árbol final verificado; commit opcional, posterior y autorizado, no condición de los cinco cortes | salida de los tres verificadores | **A: los tres verdes el 2026-09-21** (`[9/11]`, `[10/11]` en el quick 11/11 + indice regenerado) · cumplido en el mismo commit `a7564ae` · **B: quick 11/11 verde con el índice regenerado en el cierre de la fase**, y el par viajó **dentro** del commit `647f436` (2026-09-22) con los **7** checks del pre-commit en verde |
| AC19 | D | un pack por fase, declarando qué **no** incluye | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` | PENDIENTE |
| AC20 | D | delta de carga de lectura con el **mismo comando** en ambos lados | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` | PENDIENTE |
| AC21 | D | proveniencia con HEAD y sha por fuente; `--check` vence | ídem → `provenance` | PENDIENTE |
| AC22 | D | prohibido emitir un pack más corto en silencio | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}` | PENDIENTE |
| AC23 | D | mutation check del guard de truncamiento | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` | PENDIENTE |

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

**Contractualmente preparada el 2026-09-23, no ejecutada.** Las casillas de abajo ya no admiten
elección durante la sesión: las cinco decisiones que el prompt dejaba abiertas quedaron resueltas en
`04-contrato-ejecucion.md` §Enmiendas (E1–E5) y en el maestro §2/§4. **El 2026-09-24 el bloque C de la
orden de calidad reconfirmó E1 y E2 contra `scripts/decision_client.py` y no movió ninguna de las cinco;
lo que cambió ese día está en las secciones FASE-D y FASE-RELEASE de este checklist.**

- [ ] `removed: []` afirmado por un test sobre el §2 real de este plan (AC10).
- [ ] `index_status` distingue **tres** causas: `AUSENTE` (ruta + comando) / `VENCIDO` (⟦E2⟧ lo produce
      **el check de frescura propio de C**, no el `[6/7]` del hook) / `LECTOR-FALLIDO` (JSON existente
      pero ilegible, con su motivo). Ninguna prueba puede decir «sin candidatos».
- [ ] Umbral ⟦E1⟧ aplicado a **`confidence`** de una pregunta **`choice` de dos opciones**, con `basis`
      que nombra el campo y un test que afirme que `probabilidad_si` **no** es el campo gobernado.
- [ ] `threshold` publicado con valor, base y `action_below`; ningún camino auto-filtra.
- [ ] ⟦E3⟧ El script **no** escribe §2: cada propuesta pasa por **revisión humana explícita** y su
      **aceptación o rechazo queda registrado** con quién decidió. Aceptada → entra con dueño y «qué
      cambia»; rechazada → se publica el rechazo. Ninguna fila se borra.
- [ ] Test contra planes reales de `Archives/` con `skipif` visible y su corrida declarada.
- [ ] Mutation check sobre el símbolo real del guard de no-filtrado.
- [ ] `coverage.json` con los términos usados y sus conteos, **incluidos los ceros**.
- [ ] ⟦E4⟧ `acceptance` = **`NO-EJERCITADO` con su motivo** bajo proveedor falso, **sin cifra
      simulada**; es el número que, con proveedor real, decidirá si **D6** se activa — y D6 sigue
      **dormida** al cerrar C.
- [ ] ⟦E5⟧ C cerró leyendo el **workflow canónico vigente** y sin aplicar las mejoras generales de la
      orden de calidad (B autorizado, estado exclusivamente en la matriz vigente §13;
      bloque C y piloto **sin autorización**): cero renumeración (AC16 delta 0).
      ⟦**Vencido en parte el 2026-09-24**: el **bloque C** de esa orden se autorizó y ejecutó ese día
      como enmiendas documentales sobre los cuatro planes (§4.C y su resumen único en
      `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`); **el piloto
      FASE-C sí sigue sin autorización**, y es el piloto —no el bloque— lo que ejecutaría esta casilla.
      La restricción de E5 queda intacta: esas enmiendas no cambiaron el gobierno del proceso, así que
      C sigue debiendo cero renumeración (AC16 delta 0).⟧
- [ ] §4 del `00-lecciones-capitalizadas.md` actualizado con el auto-triaje del plan y su resultado
      (propuestas aceptadas / rechazadas), **después** de la revisión humana, no antes.

## FASE-D — `build_phase_briefing.py`

- [ ] `briefing/FASE-X.md` generado para **todas** las fases del plan, dentro del directorio del plan.
- [ ] `no_incluye[]` y `lectura_aparte_obligatoria[]` no vacíos; el workflow canónico figura ahí.
- [ ] `carga.json` con `method` literal, bytes exactos y divisor de tokens declarado, **y los tres
      sumandos de la carga total** por fase: `workflow_obligatorio`, `coste_de_generacion`,
      `pack_consumido` (contrato §Carga total y frescura del pack).
- [ ] Par pre/post de **checks** (delta 0) y par pre/post de **carga de lectura** (AC20), con la resta
      sacada **entre cargas totales**, no entre «fuentes» y «pack».
- [ ] Delta explicado por fase; cero o negativo declarado, no escondido. **La concatenación no se
      presenta como ahorro y se publica lo que el pack omitió.**
- [ ] `--check` falla contra una **fuente** cuyo sha cambió y pasa al revertir (demostrado en disco); y
      **no** falla solo porque HEAD avanzó (HEAD es procedencia, no llave de caducidad).
- [ ] El generador resuelve un plan **bajo `Archives/`** (es la llamada que hace el RELEASE tras el
      `git mv`); demostrado, no afirmado.
- [ ] Tres estados de resolución de secciones, un test por estado.
- [ ] Test contra una fase de un plan **archivado real**, con `skipif` y su corrida declarada.
- [ ] `git status .agents/` vacío al cerrar.
- [ ] Dependencia D6 **re-declarada con su causa**, no re-abierta: sigue **dormida** mientras AC15
      publique `NO-EJERCITADO` (rama inalcanzable sin D7 activa).

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
- [ ] Ningún AC promocionado a ✅ sin su mutation check o su clave en el artefacto. **Ningún resultado
      parcial del momento remoto promocionado a éxito del cierre.**

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
