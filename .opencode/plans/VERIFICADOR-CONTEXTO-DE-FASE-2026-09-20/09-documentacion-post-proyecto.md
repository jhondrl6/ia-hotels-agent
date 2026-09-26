# Documentación Post-Proyecto — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Acumulativo. Cada fase de implementación lo actualiza al cerrar; es la fuente de datos de
> FASE-RELEASE para generar CHANGELOG y `GUIA_TECNICA`. **Se crea vacío y se llena por fases.**

## Sección A: Módulos nuevos

| Módulo / archivo | Qué hace | Entra por | Estado |
|---|---|---|---|
| `scripts/validate_governance_numbers.py` | Compara cada aserción sobre un conteo en los documentos de gobierno contra la etiqueta `[N/M]` que el código imprime; publica denominador y tres estados | FASE-A | **Escrito y verificado offline el 2026-09-21** (914 líneas, stdlib-only, standalone; `--report` / `--json` / inyectables `--governance-doc`/`--source`/`--hook`) |
| `scripts/decision_client.py` | Única puerta del repo a un proveedor de decisiones estructuradas: contrato propio (`choice`/`score`/`noul` con su confidence), proveedor resuelto por entorno, fallo explícito sin decisión por defecto, escáner AST de su propio aislamiento y medidor de lo que cuesta añadir un proveedor | FASE-B | **Escrito y verificado offline el 2026-09-21** (≈800 líneas con su docstring de límites, stdlib-only —`argparse`/`ast`/`importlib`/`json`/`os`/`re`/`sys`/`pathlib`/`tempfile`/`hashlib`/`shutil`—; CLI `--provider-status` / `--scan-imports` / `--costura` / `--report`; **ningún módulo de red importado**, ver `evidence/…/FASE-B/cero-red.txt`) |
| `tests/quality_gates/decision_client/falsos_proveedores/falso_forma.py` | Proveedor **falso** que cumple la forma: determinista, sin red y sin credencial. Es la materia sobre la que AC8 fija la forma y AC9 mide la extensión | FASE-B | Escrito el 2026-09-21 |
| `tests/quality_gates/decision_client/falsos_proveedores/falso_ilegible.py` | Proveedor **falso** que contesta fuera de forma (`choice` sin `confidence` + una pregunta sin responder): provoca el estado `ILEGIBLE` desde el lado del proveedor, no desde un mock del test | FASE-B | Escrito el 2026-09-21 |
| `scripts/triage_lesson_relevance.py` | Capa de pertinencia **aditiva** sobre `.opencode/lecciones_index.json`: propone lo que el Paso 0 no ancló y nunca elimina una fila anclada | FASE-C | **Escrito y verificado offline el 2026-09-24** (≈600 líneas con su docstring de estados y salidas, stdlib-only —`argparse`/`datetime`/`hashlib`/`importlib`/`json`/`os`/`re`/`subprocess`/`sys`/`pathlib`—; CLI `--plan` / `--report` / `--out` / `--coverage-out` / `--ac10-out` / `--decisiones` / `--solo-pendientes` / `--json`, con **siete salidas** que distinguen `TRIADO`/`AUSENTE`/`LECTOR-FALLIDO`/`VENCIDO`/`TOPE-EXCEDIDO`/`REVISION-INCOMPLETA`/`EMISOR-NO-CONFIGURADO`; **ningún módulo de red importado** y ninguna llamada real: ver `evidence/…/FASE-C/cero-red.txt`. Único acceso al proveedor: `decision_client.py` cargado por ruta) |
| `tests/quality_gates/lesson_relevance/` | La selección que ejerce C: 10 archivos de test nominal por causa + `conftest.py` con **guard de red autouse** y el proveedor falso montado en `tmp_path` por entorno | FASE-C | Escrito el 2026-09-24 (**46** funciones de test / **56** casos, todos verdes con el guard de red puesto) |
| `tests/quality_gates/lesson_relevance/falsos_proveedores_triage/falso_pertinencia.py` | Proveedor **falso** de pertinencia con **dos ejes deterministas independientes** (`por_si` por una regla y `confidence` por otra): es lo que permite probar que el umbral gobierna `confidence` y no la probabilidad. Sin red, sin credencial, sin SDK | FASE-C | Escrito el 2026-09-24 |
| `scripts/build_phase_briefing.py` | Compone por cada fase un pack derivado con las secciones que su prompt **declara** leer (parsea la cadena `Lee …` de su bloque «Prompt de ejecución»), con proveniencia (HEAD + sha256 por fuente), `--check` de frescura gobernado por el **sha de `sources[]`** y negativa a emitir un pack más corto en silencio | FASE-D | **Escrito y verificado offline el 2026-09-24** (1.062 líneas con docstring de estados y salidas, stdlib-only —`argparse`/`hashlib`/`json`/`re`/`subprocess`/`sys`/`unicodedata`/`datetime`/`pathlib`—; CLI `--plan` (repetible, y resuelve rutas bajo `Archives/`) / `--check` / `--informe` / `--carga` / `--listar-declarado` / `--fuentes-modulos` / `--briefing-dir`; **cuatro salidas sin colapsar**: `COMPLETO` / `SECCION-NO-RESUELTA` / `FUENTE-AUSENTE` / `SIN-DECLARACION` (esta última medida en la fase: 0 de 121 prompts archivados declaran lectura); stdout reservado para el JSON y el progreso en stderr, y **ningún artefacto se escribe sin ruta explícita** (S12/L-VCF-12); **cero imports de proveedor y cero red** verificados por guard autouse en los 49 casos)
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Directorio de **artefactos generados** dentro del plan (no en `.agents/workflows/`, que tiene contadores de skills) | FASE-D | **Generado el 2026-09-24: 5 packs**, uno por fase del plan. Efecto colateral medido y declarado: son `.md` dentro del corpus que escanea `build_lesson_index.py`, así que generarlos vuelve a vencer el par del índice (A6 sobre un derivado) — la cura es el paso 5 del contrato, no editar el pack |
| `tests/quality_gates/phase_briefing/` | La selección que ejerce D: 10 archivos de test (los **7 nombrados por el mandato**, + AC20, + AC23, + el del guard de red) + `conftest.py` con **guard de red autouse** y una **fábrica de planes plantados** en `tmp_path` (un prompt que declara lectura, sus documentos y su falso `.agents/`) | FASE-D | Escrito el 2026-09-24 (**49** funciones de test / **49** casos, todos verdes con el guard puesto; un estado por test, y un test que exige que los tres estados **no colapsen**) |
| `evidence/…/FASE-D/instrumentos/` (tres: `correr_mutation_a_evidencia.py`, `comprobar_resta_carga.py`, `reimprimir_par_carga.py`) | Los tres instrumentos del cierre (y `corridas-crudas-2026-09-24.zip`, que conserva el stdout literal de las cinco corridas que las tablas resumen): vuelcan verde/rojo de AC23 a un **destino pasado por argumento**, reimprimen el par `stat` de carga desde las rutas publicadas en `carga.json` y comprueban las cinco identidades de la resta de AC20 | FASE-D | Escritos el 2026-09-24. Ninguno hardcodea destino ajeno (S12/S13) y los tres se invocan con `--evidencia` / `--destino` explícitos, que es lo que hace que FASE-RELEASE pueda re-correrlos tras el `git mv` sin editar código | Escritos el 2026-09-24; ambos publican el comando literal de su corrida y ninguno define un destino por defecto (S13) |

## Sección B: Funcionalidades nuevas

- (FASE-A, **cerrada el 2026-09-21**) Detección mecánica de aserciones vencidas sobre conteos, con
  su población y sus familias no cubiertas. Sobre el árbol vigente reproduce **A1–A4 y ninguna
  otra** (`findings[]` con `assertion_id`, `claimed`, `observed`, `occurrences[]`), clasifica las
  **24 instancias** de la población en viva-hallazgo (5) / viva-correcta (11) / histórica congelada
  (8) / no resuelta (0), y publica `coverage_basis` con las cuatro familias no cubiertas medidas en
  runtime. Tres estados sin colapso (`SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO`), seis mutantes
  del guard real en `evidence/…/FASE-A/mutation/` y delta 0 en los conteos que otros planes pinean.
- (FASE-B, **cerrada el 2026-09-21**) Costura neutra de proveedor con contrato propio. Lo que
  quedó cerrado con medición: **AC6** `0` imports del SDK/adapter fuera de la puerta sobre **692** `.py`
  del árbol de trabajo (4.379 nodos de import; 21 menciones no-import publicadas aparte; exclusiones
  declaradas por directorio con su conteo) y **9 mutantes** que muestran que cada guard carga con lo
  suyo; **AC7** `provider_status` en sus tres estados, con 5 `motivo_clase` que no colapsan y con la
  conversión a tipos negativa a rellenar un campo ausente; **AC8** contract test verde (`exit 0`) y
  el **mismo test rojo** (`exit 1`) al quitarle `confidence` al proveedor falso, con el pin del modelo
  declarado y probado por AST como no-usado; **AC9** `files_changed_to_add_provider = 1` medido por
  sha256 sobre la frontera completa, con los dos proveedores despachados y contestando distinto.
  Sin llamadas de red —verificadas con guard de `socket` vivo, denegatoria AST de 19 módulos y SDK
  ausente del venv del producto— y sin credencial alguna en árbol, evidencia o logs. La comparación
  real entre proveedores **no** es de este plan: es la deuda **D7**.
- (FASE-C, **cerrada el 2026-09-24 con el corte «hasta listo para revisión» — sin commit ni push**)
  Capa de pertinencia **aditiva**, ejercitada contra el proveedor **falso determinista**, que es el
  techo que el plan previó para esta fase (D7 sin activar). Lo que quedó cerrado con medición:
  **AC10** aditividad con el guard ejercitado de verdad — 11 filas ancladas fueron juzgadas
  `no-pertinente` por el emisor y **ninguna desapareció** (`ac10_delta.json`, `removed: []`), y el
  script no escribe §2 (sha256 del `00-` idéntico + cero operaciones de escritura observadas dentro del
  plan); **AC11** tres causas del suelo sin colapsar y `VENCIDO` producido por el **check propio de C**
  (ruta (b) del contrato E2, con su coste publicado: dos lecturas del JSON por corrida); **AC12**
  umbral sobre `confidence` de una `choice` de dos opciones, con `basis` que nombra el campo y prueba
  de que `por_si` no gobierna; **AC13** test contra **corpus real archivado**, que **corrió** (4 casos
  sobre los 2 planes archivados con `00-`) y no se saltó — con la desviación de ruta registrada;
  **AC14** mutation check con su verde y su rojo en disco y la disciplina S13 (destino por argumento,
  observador de escrituras compartido, `huellas` del expediente de FASE-A intactas).
  **AC15 queda ⚠️**: su parte no semántica está medida (población leída de la corrida, 10 términos con
  **5 ceros** —entre ellos `verificador mec = 0`, la medición A5 reproducida—, familias no juzgadas y
  pool no sometido a juicio), y su tramo semántico es **`acceptance = NO-EJERCITADO`** con motivo
  literal y **sin ratio simulada** (E4). Consecuencia declarada: **D6 sigue dormida** y este plan no
  abre el lint semántico sobre una base que nunca juzgó nada.
  Lo que C **no** cierra y no frena: **D7** (activar el proveedor) y **S10** (dónde vivirá el `import`
  del SDK), que son del tramo que consume un proveedor real.
- (FASE-D) Unificación de la carga de lectura declarada por fase, y medición del delta con el mismo
  comando en los dos lados (AC20).

- (FASE-D, **cerrada el 2026-09-24**) Pack derivado por fase y **carga total de lectura medida**. Lo
  que quedó cerrado con medición: **AC19** 5 packs = las 5 fases del plan, con `no_incluye[]` y
  `lectura_aparte_obligatoria[]` no vacíos exigidos por test y **cero bytes aportados a `.agents/`**
  (observador de escrituras + sha256/tamaño); **AC20** delta **1.648.109 → 1.431.388 = 216.721 bytes
  (~54.180 tokens, divisor 4)** con los tres sumandos por fase y la resta **entre cargas totales**,
  comprobada por instrumento contra el par `stat -c %s` (cinco identidades, `exit 0`) — y publicada
  con su límite: el workflow canónico entra en los dos lados mientras **D3** no lo rebane, por eso el delta
  **no llega al tercio**; su porcentaje vigente —recalculado de `carga.json` el 2026-09-25 por la
  conciliación final de la orden de calidad, que retiró las tres cifras divergentes que el plan había ido
  copiando— lo publica la fila «Carga de lectura A7» del `README.md` de este plan y **no se re-transcribe
  aquí** (**L-VCF-19**); **AC21** frescura por **sha256 de cada fuente de
  `sources[]`** contra el árbol, con `FUENTE-AUSENTE` / `SHA-DISTINTO` / `FUENTE-ILEGIBLE` /
  `PACK-AUSENTE` sin colapsar, HEAD publicado como **procedencia que no vence** (test dedicado) y el
  pack fuera de su propio conjunto de fuentes; **AC22** el recorte nunca achica el pack en silencio:
  nombra la sección pedida, las rutas intentadas y los títulos disponibles, y a los tres estados del
  contrato se sumó una cuarta salida medida, `SIN-DECLARACION`, cuyo `--check` imprime `SIN-FUENTES`
  en lugar de `OK`; **AC23** verde y rojo del símbolo real `GUARD_NO_TRUNCAMIENTO_ACTIVO` (apagado,
  el pack pierde la declaración y se achica conservando el estado (los dos tamaños, en `mutation/resumen.txt`)). Dos hallazgos con dueño: **0 de 121** prompts
  archivados declaran la lectura en el formato que parsea el generador (**S16**), y copiar un
  documento que vive fuera de `.opencode/` hacia dentro **reabre `[8/11] validate_opencode_refs.py`**
  — la regla que salió de medir eso: lo externo se declara lectura aparte, no se copia.

## Sección C: Correcciones

- (FASE-B, **2026-09-21**) Dos cifras del propio cierre estaban estimadas y se corrigieron midiendo:
  «10 archivos de código» → **11** y «13 de evidencia» → **25**, ambas con su comando en
  `evidence/…/FASE-B/baseline-pre-post.md` §Presupuesto. Es la medición A6 del maestro golpeando a
  esta fase: el número se escribió antes de terminar de escribir los archivos.
- (FASE-B, **2026-09-21**) El `--quick` cayó a 10/11 al registrar la fase, por el mismo conflicto de
  los **dos escritores de la fecha** en `REGISTRY.md` que documentó FASE-A. Corregido con su writer
  (`sync_versions.py --rule registry_last_update`) y no a mano; el conflicto sigue sin dueño de
  reconciliación y esta es la segunda fase que lo paga. **Y sigue sin dueño después de esta
  conciliación**: la orden de calidad lo tiene en su **bloque B**, diferido y sin autorización, así que
  aquí no se cerró ni se declaró resuelto.
- **⟦Conciliación del 2026-09-23 — correcciones de documento, ninguna de código⟧**
  - **Rectificada una advertencia vigente del README** que ya no era cierta: la guarda «nunca correr
    `validate_governance_numbers.py --report` sin destino porque pisa la evidencia de FASE-A». **S12**
    fue corregida por el bloque A de la orden de calidad (`fdd397f`) y hoy ese comando imprime y no
    escribe — re-medido aquí con `sha256` idéntico y `exit 1` conservado. La **lección L-VCF-12**
    permanece como regla general; lo que caducó fue su aplicación a este script.
  - **Rectificada la fila de población AC6**: el residuo 692−691 que **S11** dejó publicado ya no
    existe. Re-medido 2026-09-23: escáner **696** vs `git ls-files '*.py'` **696**, con `.venv-wsl` ya
    declarado en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION` y su conteo publicado (582).
  - **Aceptadas S11 y S12 con su procedencia fuera de este plan**, separando tres momentos que antes se
    leían como uno: cierre original (`647f436`) / corrección técnica ajena (`fdd397f`) / aceptación
    (2026-09-23). El propio resumen del bloque A declaraba que el cierre **contractual** le tocaba a
    este plan: eso es lo que se cerró, y ningún mérito técnico se atribuye a esta sesión.
  - **Precisado AC9 en el documento**: certifica **extensión local** con un proveedor falso
    (`files_changed_to_add_provider = 1`), **no** el coste de integrar un SDK real con sus dependencias
    y su autenticación. La redacción anterior se leía como lo segundo.
  - **Cuatro enmiendas prospectivas de FASE-C conciliadas** en maestro §2 y §4, contrato
    (§Enmiendas E1–E5), prompt de C, checklist y este análisis — **no** basta una nota al margen cuando
    la instrucción ejecutable seguía diciendo lo contrario: el paso 6 del post-ejecución de C mandaba
    «aplicar lo que proponga el triaje», y esa frase fue reescrita. **Ninguna se implementó.**
  - **Lo que NO se corrigió** porque no corresponde a esta conciliación: `.agents/` con A1–A4 vencidas
    (**D1**, instrucción literal), la fecha de `REGISTRY.md` (bloque B de la orden, diferido) y los otros
    tres planes con D/RELEASE (fuera del alcance autorizado).



- Las aserciones A1–A4 medidas en `01-plan-maestro.md` §1 **no se corrigen** en este plan
  (AC17). Quedan como deuda D1 con su disparador.

## Sección D: Métricas acumulativas

| Métrica | Pre (a medir por cada fase) | Post | Notas |
|---|---|---|---|
| Checks de `run_all_validations.py --quick` | 11 | **11** (delta **0**, 2026-09-21) | Delta esperado **0** en las cuatro fases de implementación (AC16) — cumplido por FASE-A **y por FASE-B** |
| Checks del hook `scripts/git_hooks/pre-commit` | 7 | **7** (delta **0**) | Delta esperado **0** — cumplido. Quién lo afirma en `tests/`: `test_validate_plan_closure.py` (`[5/7]`) |
| `def test_` en `tests/` | **4.508** (PRE de FASE-D **reconstruido, no capturado en crudo al abrir**: `grep -rE "^\s*def test_" tests --include=*.py --exclude-dir=phase_briefing` = 4.508, que reproduce exacto el POST que publicó C. Crudo en `evidence/…/FASE-D/test_count_pre_post.txt`) | **4.557** (resta **+49**, verificada: 4.557 − 4.508 = 49 = `grep -rE "^\s*def test_" tests/quality_gates/phase_briefing --include=*.py`) ⟦**Antecedente refutado por su propio comando, 2026-09-24**⟧: esta misma celda publicaba PRE **4.360** / POST **4.404** y decía «medido al abrir la fase». **4.360 no reproduce sobre ningún árbol** —ni el de trabajo (4.557) ni `HEAD` (4.470, medido con `git grep -cE` sobre la revisión)— y no dejó crudo en `evidence/`. Se retira la cifra, no se justifica: es A6 y «quién produce el dato publicado» aplicados a un número que **yo mismo escribí en esta fase** sin su comando al lado. Manda el comando con su archivo | FASE-B: `tests/quality_gates/decision_client/` = 48 funciones / **53 casos** (parametrización de los 6 guards). ⟦Nota retirada de la pendiente actual el 2026-09-24 por el bloque C⟧: esta fila terminaba diciendo «la cifra canónica que publica `AGENTS.md` (4.246) sigue vencida por tráfico ajeno y su edición pide instrucción literal», y **eso ya no describe el árbol**: el bloque B dejó `AGENTS.md` con **una** fuente fechada (`Cobertura por Modulo`) y referencias desde los demás sitios, y publicó su medición y su límite en §8 de la fuente única de B. La instrucción literal sobre `AGENTS.md` sigue siendo regla general; lo que se retira aquí es el pendiente descriptivo. **⟦FASE-C, 2026-09-24⟧: POST medido con el método canónico = 4.508 funciones, de las que 46 son de `tests/quality_gates/lesson_relevance/` (56 casos al parametrizar); el PRE no se midió al abrir la sesión, así que la resta que se publica es POST − contribución propia, y se declara que el árbol traía 62 rutas de trabajo ajeno sin commitear —la resta total no es achacable a C. Manda el comando, no esta cifra** |
| IDs definidos en `.opencode/LECCIONES-INDEX.md` | 320 (re-medido el 2026-09-20) | re-medido al cerrar cada fase: lo publica `build_lesson_index.py` y FASE-A cerró con **325** | Cambia al archivar; lo regenera RELEASE. A6 documentó que esta cifra vence al escribir cualquier `.md` del corpus — **y FASE-B la vuelve a reproducir**: esta fase escribe IDs reales (L-V2.3, L-PF6, L-R.3…) en seis `.md` de plan, así que el índice se regenera en el cierre. **⟦FASE-C, 2026-09-24⟧: PRE re-medido al abrir con `python scripts/build_lesson_index.py --check` = 332 IDs; POST al cerrar, lo imprime la regeneración del cierre y su salida en `FASE-C/baseline-pre-post.md`. C **no** pinea esa cifra en ningún artefacto: `coverage.json` la lee del JSON en la propia corrida y hay un test que prohíbe literales (320/332/50/402) en el script. Y A6 vuelve a cumplirse sobre esta misma fila: escribir estos documentos de cierre mueve el número** |
| Imports del SDK/adapter fuera de la puerta (AC6) | **0** sobre 678 `.py` rastreados / **692** del árbol de trabajo (690 en el primer escaneo: +2 por los instrumentos propios) (medido al abrir FASE-B con el AST de la propia puerta) | **0** re-medido al cerrar (misma población) y **0 otra vez el 2026-09-22**, ya con **691** rastreados (el commit de la fase sumó sus 13 `.py`) sobre los mismos **692** del árbol | El SDK sí existe en el entorno, pero **aislado en `tmp_test/venv-jev-sdk`** y no instalado en el venv del producto; esa exclusión está publicada con su conteo en `import_scanner.txt`, no callada. **Y hay una exclusión que faltaba**: el residuo 692−691 es `.venv-wsl/bin/activate_this.py` (deuda **S11**, lección **L-VCF-11**), que no importa el SDK y por eso no mueve el 0. **⟦Cerrado el 2026-09-23⟧ S11 aceptada** (corrección técnica del bloque A de la orden, `fdd397f`): la exclusión está declarada y **re-medido offline: escáner 696 vs `git ls-files '*.py'` 696 → residuo 0**, con `--scan-imports` en `exit 0` y `excluidos_por_directorio` publicando `.venv-wsl`: 582. **⟦Re-medido al cerrar FASE-C el 2026-09-24: `--scan-imports` sigue en `SIN-HALLAZGOS` / `exit 0` con 0 imports y 0 cargas dinámicas. El desfase entre las dos poblaciones NO es una exclusión no declarada: es la diferencia entre medir en disco y medir en el índice de git sobre un árbol con trabajo ajeno sin commitear, y se desglosó archivo por archivo en `FASE-C/cero-red.txt` (15 rutas propias + 20 ajenas), incluida la auto-refutación de la primera medición de la sesión, que dio 34 antes de existir el instrumento de cierre**⟧ |
| Coste de añadir un proveedor (AC9) | sin instrumento (no existía la costura) | **1** archivo, medido por sha256 sobre la frontera copia+door (`costura.json`) | Tests paralelos: 1, declarado aparte y no escondido para inflar el «1». Con un proveedor **real** (D7) habría además manifiesto de dependencias: eso no está medido aquí porque ningún proveedor se activa |
| **Carga total de lectura de ESTE plan (AC20, medida por D el 2026-09-24)** | sin instrumento (el generador no existía) | **antes 1.648.109 bytes · después 1.431.388 bytes · delta 216.721 (~54.180 tokens, divisor 4 declarado) = 13,08 % de la carga total**; por fase A 36.247 (12,1 %) / B 48.010 (16,2 %) / C 53.628 (17,3 %) / D 45.936 (15,2 %) / RELEASE 32.900 (7,5 %), cada una cerrando con `omitido − andamiaje − coste`. **Es el POST de la última corrida, después del barrido documental**: los cuatro pares anteriores (1.528.896 / 1.632.454 / 1.639.929 / 1.646.414 de `before`) quedaron vencidos uno tras otro por escribir los cierres, y esa es la razón por la que esta tabla — y no un `.md` del corpus — es la fuente de la cifra (**L-VCF-19**: la carga que mide un pack no puede publicarse en un documento que ese pack copia). Fuente única: `evidence/…/FASE-D/carga.json` y el par `faseD_carga_pre/post.txt`; **la suma de los packs no es un ahorro si no se publica lo omitido** | 
| **Población de la convención que parsea el generador** | sin instrumento | **0 de 121** prompts archivados y **5 de 5** de este plan declaran su lectura con la cadena `Lee …` (medido el 2026-09-24 con `--listar-declarado` sobre el corpus); es el denominador de **S16** y por eso un pack de un archivado sale `SIN-DECLARACION` | 
| **Carga de lectura declarada por fase (bytes / ~tokens)** | **263.973 / ≈65.993** re-medidos el 2026-09-20 sobre las siete lecturas que suma A7 en el plan de referencia (al concebir: 254.010 / ≈63.502; maestro §1, A7 y A6) | **263.973 / ≈65.993** re-medidos el 2026-09-21 con `stat -c %s` sobre los siete archivos: **sin cambio** (las fases de `REFACTOR-WHATSAPP` no volvieron a escribirlos). FASE-A no reduce lectura: es FASE-D quien debe mover esta fila | **AC20 lo mide con el mismo comando en los dos lados**, sobre las fases de este plan; delta cero o negativo es resultado válido y se explica. **⟦Regla añadida el 2026-09-24 por el bloque C (orden §4.C, fila `CONTEXTO/D`)⟧: esta fila debe publicarse como CARGA TOTAL, con sus tres sumandos (`workflow_obligatorio` + `coste_de_generacion` + `pack_consumido`) y la resta sacada entre totales** — concatenar documentos no es ahorrar, y el único ahorro achacable al pack es lo que dejó de leerse porque no entró (contrato §Carga total y frescura del pack). Los valores de arriba son el PRE histórico de FASE-A, no la fórmula con la que FASE-D cierra |
| Población bajo el patrón de conteo (A8) | **22 instancias `[N/M]` en 17 líneas** + 2 formas «check N» en `.agents/` (medido el 2026-09-20) | **22 / 17 / 2, re-medido el 2026-09-21: idéntico** (el verificador las agrupa en 24 instancias auditables = 22 + 2) | El verificador las clasifica en viva / histórica congelada / vigente-correcta y publica las dos últimas con su conteo; sin esa regla AC1 no es verificable |
| **Denominador del triaje (AC15) — cuántos IDs recibieron juicio de pertinencia** | sin instrumento (la mitad de pertinencia no existía: `validate_lesson_capitalization.py` declara ese hueco fuera de su alcance) | **Lo publica `evidence/…/FASE-C/coverage.json` → `coverage_basis.denominador_juicio`**, leído de la corrida sobre la población que imprime el propio índice (no pineado). Con `--plan` del propio VERIFICADOR-CONTEXTO el pool triado es «el plan lo define o lo cita y §2 no lo ancla» **más** las filas ancladas re-preguntadas | **La aceptabilidad NO está medida**: `acceptance = NO-EJERCITADO` con `valor: null` porque el emisor es un proveedor falso determinista (contrato E4, deuda D7 sin activar). Es el único número de esta fila deliberadamente ausente, y su ausencia es el disparador que mantiene **D6 dormida**. Términos de la capa fría con sus **ceros** publicados (5 de 10 dan 0, incluido `verificador mec`, que reproduce A5) y familias no juzgadas (`S`) — un `[OK]` sin eso no informaba (L-R.3) |
| **FASE-RELEASE offline (2026-09-25)** | sin release previa del plan | **release 4.78.0** · `VERSION.yaml` `version`/`codename`/`release_date`/`date` = 2026-09-25 · **5** cabeceras sincronizadas por `sync_versions.py` · `DOMAIN_PRIMER.md` regenerado con su writer · **6** archivos normalizados de CRLF a LF (efecto del propio writer, declarado) · **1** entrada nueva en `CHANGELOG.md` (+90/0) y **1** entrada en `REGISTRY.md` por `log_phase_completion.py` (cabecera a 2026-09-25, total 501) · **0** operaciones de red, **0** de archivado, **0** de commit | Su evidencia es la fuente: `evidence/…/FASE-RELEASE/` (`11-cadena-release.txt`, `12-normalizacion-lf.txt`, `07-cierre-verificacion.txt`). Esta fila **no** re-transcribe los counts de los verificadores: los imprime la corrida. Lo que **no** cerró: D8, D9, archivado, `--fix`/`--update-baseline`, commit y push |

## Sección E: Archivos afiliados

- [ ] `CHANGELOG.md` (RELEASE)
- [ ] `GUIA_TECNICA.md` (RELEASE)
- [ ] `docs/contributing/REGISTRY.md` (RELEASE — los tres módulos nuevos)
- [ ] `VERSION.yaml` → sync a los seis archivos que lista el executor (RELEASE)
- [x] `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` (regenerados en cada commit que escribe `.md` de plan con IDs) — **FASE-B regeneró el par el 2026-09-21** al escribir sus seis documentos de cierre, y el commit que los llevaba dentro llegó con su instrucción literal: **`647f436`, el 2026-09-22** (`--numstat`: 24+/17− y 100+/14−), con `[6/7]` del hook verde en esa corrida. **FASE-C regeneró el par en su cierre del 2026-09-24 sobre el árbol final verificado, y sigue sin commitear: el par viaja con la mezcla de trabajo ajeno que declara `FASE-C/cero-red.txt`, no con un commit propio**
- (FASE-C, **sin tocar**) `.agents/` (AC17), `scripts/run_all_validations.py` y `scripts/git_hooks/pre-commit` (AC16), y `AGENTS.md` / `.cursorrules` (configuración central, instrucción literal). C leyó el workflow canónico vigente y **no** aplicó ninguna mejora general de la orden de calidad dentro de la fase (contrato E5): cero renumeración, cero cambios al proceso común.
- (FASE-B, **sin tocar**) `AGENTS.md`: configuración central, se edita con instrucción literal y no a
  mitad de fase. ⟦Rectificado el 2026-09-24 por el bloque C⟧: el motivo que se escribía aquí —«su cifra
  canónica de funciones de test está vencida contra disk (4.246 publicados / 4.378 medidos)»— **dejó de
  ser la razón vigente**: el bloque B redujo `AGENTS.md` a una fuente fechada con referencias alrededor,
  y esa familia quedó declarada como límite no cubierto por el verificador en §8 de su fuente única. Lo
  que sí sigue vigente en esta línea es la restricción (configuración central), no la cifra.

- (FASE-D, 2026-09-24) Nuevos en el árbol: `scripts/build_phase_briefing.py`,
  `tests/quality_gates/phase_briefing/` (8 archivos + `conftest.py` + `__init__.py`),
  `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` (5 packs generados) y
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/`, que se enumeran por **categoría** y no
  por lista cerrada —la lista cerrada de archivos la imprime `ls` sobre el directorio, y copiarla acá
  la envejece cada vez que se escribe una evidencia más (**L-VCF-19**): los dos informes
  (`informe.json`, `carga.json`), los tres instrumentos, `mutation/`, el par de checks
  (`faseD_baseline_pre/post`), el par de carga (`faseD_carga_pre/post`) con su `carga-pre-post.md`,
  el par de huellas (`no-piso-pasado_ANTES/DESPUES`), las corridas (`run_tests.txt`, `r26.txt`,
  `regression_calidad.txt`, `faseD_quick_pre/post`, `check_final.txt`,
  `ac18-tres-verificadores.txt`), la auditoría de proceso (`cero-red.txt`), el recompto del
  denominador (`test_count_pre_post.txt`), el par con la resta y el presupuesto
  (`baseline-pre-post.md`) y los criterios de completitud (`criterios-de-completitud.md`).
  Actualizados por su cierre documental: `README.md`, `dependencias-fases.md`,
  `00-lecciones-capitalizadas.md` (Q13, §2, §4 y balance §7), `06-checklist-implementacion.md`,
  `09-…` (esta sección) y `10-analisis-post-implementacion.md`. **No tocó** (AC17 y permisos del
  contrato): nada bajo `.agents/`, ningún `05-prompt-*.md` de plan alguno,
  `run_all_validations.py`, el hook, `build_lesson_index.py` ni los scripts de A/B/C.
