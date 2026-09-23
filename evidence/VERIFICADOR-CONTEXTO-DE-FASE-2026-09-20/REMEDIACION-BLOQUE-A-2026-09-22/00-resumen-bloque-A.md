# Remediación bloque A — ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22

**Qué es:** evidencia de la remediación técnica focalizada que pide el bloque A de
`.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.A. Ubicación propia, como exige ese
bloque; el expediente de FASE-B sigue intacto y se referencia sin reescribirse.

**Qué no es:** no cierra FASE-C ni ninguna deuda de los cuatro planes, no registra ejecución en
`REGISTRY.md`, y no autoriza push. Los bloques B y C de la orden siguen pendientes de autorización
explícita por archivo (ver §5 de este documento).

**Fecha de la ejecución:** 2026-09-22. **HEAD al empezar:** `a3ab8f9` (los cambios están en el árbol de
trabajo, sin commitear).

---

## 1. Superficie tocada

| Archivo | Cambio |
|---|---|
| `scripts/decision_client.py` | Los cinco fixes del contrato + S11 + S12 + precisión de AC9 |
| `scripts/validate_governance_numbers.py` | S12: `--report` sin destino imprime y no escribe |
| `tests/quality_gates/decision_client/test_decision_client_remediacion_bloque_a.py` | Nuevo: 22 funciones de regresión |
| `tests/quality_gates/governance_numbers/test_governance_numbers_s12_report_no_escribe.py` | Nuevo: 5 funciones (S12) |
| `tests/quality_gates/decision_client/test_decision_client_aislamiento_imports.py` | Escaneo compartido + 2 funciones de población (S11) |
| `tests/quality_gates/decision_client/conftest.py` | Fixtures de sesión `dc_sesion` y `escaneo_arbol_real` |

No se tocó: `AGENTS.md`, `.cursorrules`, `.agents/**`, `docs/contributing/REGISTRY.md`, los cuatro
planes, ni ningún archivo bajo `evidence/…/FASE-A` o `FASE-B`.

> **Nota de la sesión 2**: la lista original de esta sección decía «`VERSION.yaml`, `CHANGELOG.md`»
> entre los no tocados — dejó de ser cierto cuando la sesión 1 ejecutó el cierre documental (§9), y
> la sesión 2 los editó de nuevo para retirar el bump sin release (§10). También se tocaron en la
> sesión 2 `tests/quality_gates/decision_client/test_decision_client_mutation_guards.py` y
> `tests/quality_gates/governance_numbers/test_governance_numbers_lector_fallido.py`.

## 2. Los cinco contraejemplos, como regresiones versionadas

Medido con un solo instrumento afirmando las mismas proposiciones sobre dos revisiones del módulo
(`git show HEAD:scripts/decision_client.py` para la anterior, sin `stash` sobre trabajo sin commitear):

```
PRE  (HEAD, revision original de FASE-B):  0/6 criterios del contrato cumplidos
POST (árbol de trabajo, tras el fix):      6/6 criterios del contrato cumplidos
```

Comando y salida completa: `instrumentos/veredicto_contraejemplos.py` →
`contraejemplos-antes-despues.txt`.

| Criterio |_contracto exigido_ | PRE | POST |
|---|---|---|---|
| CX1 | Un módulo de proveedor que no carga no se resuelve como ausencia | `ProveedorNoConfigurado` | `LectorFallido` |
| CX1b | La sonda lo nombra `LECTOR-FALLIDO`, no `NO-CONFIGURADO` | `NO-CONFIGURADO` | `estado_lector=LECTOR-FALLIDO` |
| CX2 | Un campo fuera de contrato en `noul` se reporta como ruptura | `motivos=[]` | `campos fuera de contrato ['campo_inventado']` |
| CX3a | `tipo` que no es texto produce motivos, no un `TypeError` | `TypeError: unhashable type` | motivo nombrando `tipo` |
| CX3b | `pregunta_id` que no es texto produce `ILEGIBLE`, no `TypeError` | `TypeError: unhashable type` | `ILEGIBLE` con dos guardas |
| CX4 | Un lote con ids repetidos se rechaza antes de cerrar en `RESUELTO` | `RESUELTO` con 1/2 respuestas | `ValueError` del lote |

CX1 contaba como dos criterios (excepción y sonda) porque la orden enumera cinco contraejemplos y la
corrección tiene dos superficies observables; el recuento honesto es 5 defectos / 6 proposiciones.

**Los fixes, y por qué cada uno no puede degenerar en un favorable:**

- **CX1** — `resolver_proveedor` ya no certifica ausencia sobre una lectura incompleta: si algún
  módulo del directorio no cargó, lo que se devuelve es el estado del lector, con los nombres que sí
  se leyeron y los fallos que no. Un `NO-CONFIGURADO` afirmaba «busqué y no está», cosa que nadie
  podía saber del archivo que no se pudo abrir.
- **CX2** — se eliminó la excepción `and tipo != "noul"` que perdonaba los campos extra solo a
  `noul`, la primitiva que ya redefinió sus criterios dos veces. `confidence` conserva su motivo
  propio y sigue sin reportarse dos veces, que es lo que necesita el mutante que aísla un guard.
- **CX3** — `tipo` y `pregunta_id` se validan como texto **antes** de usarse como clave: el
  `TypeError` no era un estado del contrato sino el instrumento caído, y su salida se leía como
  «sin coincidencias». Ningún `except` convierte el fallo en favorable: se sigue lanzando
  `RespuestaIlegible`, con el campo roto nombrado.
- **CX4** — la unicidad de ids es contrato del lote, así que se rechaza en `evaluar()` antes de
  despachar (como ya se hace con el lote vacío), no del lado de la respuesta. Además el guard de
  cobertura dejó de emparejar por posición: comparaba el `tipo` contra la pregunta que ocupaba el
  mismo índice, de modo que un proveedor que contesta en otro orden recibía el reproche de una
  primitiva que no era suya.
- **Códigos de salida** — `--provider-status` devolvía 2 para `LECTOR-FALLIDO`, que el propio
  docstring reservaba a `AUSENTE`; ahora devuelve 3, y la tabla del docstring describe lo que el CLI
  hace. Y `medir_costura` publica los `provider_status` reales en lugar del literal
  `["RESUELTO", "RESUELTO"]`, que hacía que su aserción no pudiera ponerse roja.

## 3. Retrabajo evitable: escaneos repetidos (PRE/POST comparable)

Mismo comando de la revisión de la orden
(`-m pytest tests/quality_gates/decision_client -q -p no:cacheprovider --durations=5`):

| | tests | escaneos del árbol real | duración |
|---|---|---|---|
| PRE | 53 | 3 | 23,51 s |
| POST | 75 | 1 | 10,21 s |

Verificable sin leer el relato: `git grep -c "escanear_aislamiento(raiz_repo)" HEAD --
tests/quality_gates/decision_client/` → 3; sobre el árbol de trabajo → 1.

Lo que se compartió y lo que **no**: las tres aserciones independientes leían el mismo árbol con la
misma configuración, así que comparten un `fixture(scope="session")`. Las pruebas que mutan el módulo
o el árbol siguen con `dc` de función y escaneando su propio `tmp_path`; y la sesión usa un módulo
cargado aparte (`dc_sesion`) para que el verde de AC6 no dependa del orden en que corrió un mutante.
No se saltó ninguna comprobación: se añadieron 22 funciones y aun así baja el tiempo.

**Límite declarado de esta cifra:** 23,51 s y 10,21 s son tiempo de comando, no tiempo activo del
agente, y miden una sola selección. No se comparan con las 2 h 59 min del intervalo PRE→POST de
FASE-B: la orden ya declara que ese intervalo no tiene reparto fiable.

## 4. S11 y S12

- **S11 (denominador).** Medido antes del cambio: `.venv-wsl/bin/activate_this.py` era **1** de los
  692 `.py` que leía `iterar_py()`, y el numerador no se movía (0 imports). Cura: la exclusión entra
  en la lista y su conteo se publica — dos pruebas, una con árbol plantado (`excluidos_por_directorio
  == {".venv-wsl": 1}`) y otra sobre el árbol vigente. No se tocó ningún umbral: la población sigue
  afirmándose en `> 600` y el árbol completo en `archivos_py_en_el_arbol`. **Sesión 2:** el solape de
  exclusiones que documenta L-VCF-11 dejó de inflar el total — `archivos_py_en_el_arbol` se cuenta
  con archivos **únicos** (`excluidos_archivos_unicos`) y la atribución por directorio se publica
  aparte.
- **S12 (volver a medir pisa el pasado).** Estaba asignado a FASE-RELEASE de CONTEXTO, que prohíbe
  editar código allí. Se ejecutó aquí, que es lo que la orden pide en su §4.A. Los dos verificadores
  perdieron su ruta de evidencia como destino por defecto: `--report` a secas imprime y dice
  «no se escribio ningun archivo»; escribir exige nombrar la ruta. Las constantes (`EVIDENCIA`,
  `REPORT_DEFAULT`) ya no existen y dos pruebas lo afirman estructuralmente. Los 5 tests existentes de
  gobernanza ya pasaban destino explícito, y ni `run_all_validations.py` ni el hook pre-commit
  invocan el verificador, así que ningún consumidor quedó roto. **Sesión 2:** el aviso de
  no-escritura salió de stdout a stderr; el stdout de `--report` sin destino es JSON parseable.
- **En los dos casos, lo aplicado es CORRECCIÓN TÉCNICA, no cierre contractual**: la deuda S11/S12
  vive en el plan CONTEXTO con dueño en FASE-RELEASE, y trasladarla a este bloque exige la enmienda
  registrada en ese plan, que sigue pendiente. La primera sesión presentó esto como «resuelto»; esa
  declaración queda retractada en §10.

## 5. Criterios de aceptación de la orden (§6) — estado tras el bloque A

> Rectificación de la sesión 2: la fila 2 se publicó como «CUMPLE» sin las salidas por defecto
> medidas, y el conjunto de esta tabla se leyó como cierre del bloque A. No lo era: ver §10.

| Criterio | Estado |
|---|---|
| Contraejemplos como regresiones que caen por su causa y pasan tras el fix | CUMPLE (0/6 → 6/6, `contraejemplos-antes-despues.txt`; verificado de nuevo en la sesión 2) |
| PRE/POST comparable demuestra reducción de escaneos sin saltar comprobaciones | CUMPLE (3 → 1, tiempos reales publicados; cifras de sesión 1, actualizadas en §10 con la selección final) |
| Registrar/verificar no genera el conflicto de fechas; re-medir no modifica evidencias históricas | PARCIAL: S12 con corrección técnica aplicada y probada (sesión 2: stdout JSON parseable); la **fecha de REGISTRY** es bloque B y sigue pendiente; el **cierre contractual** de S12 exige la enmienda en CONTEXTO |
| Cada estado/métrica con fuente identificada, sin mantener el mismo dato a mano en varios sitios | NO INICIADO: es bloque B (`AGENTS.md`, executor, plantilla) |
| Los cuatro planes con punto de reanudación coherente y contratos prospectivos | NO INICIADO: es bloque C, pide enmiendas expresas |
| El piloto informa defectos, retrabajo, tiempos y coste documental | NO INICIADO: FASE-C de CONTEXTO sigue sin mandato |

## 6. Lo que la orden deja fuera y se respetó

Sin commit ni push; sin ejecutar fases de los planes; sin pipeline, APIs, subidas ni archivado; sin
instalar SDKs ni rotar credenciales; sin editar `AGENTS.md`, `.cursorrules`, `.agents/**` ni trabajo
ajeno. El trabajo ajeno preexistente en `JEV/dependencias-fases.md` (18 líneas) sigue sin tocar.

**AC9, declarado con su alcance:** la medición publicada sigue siendo una **extensión local contra un
proveedor falso del repo**, no el coste certificado de integrar un SDK con sus dependencias y su
autenticación. Ahora viaja escrito en el propio artefacto
(`costura.coverage_basis.alcance_de_ac9`), con la ubicación futura del SDK apuntada a CONTEXTO/S10 y
D7, como pide el §4.A.

## 7. Corrida completa del repo y atribución de fallos

Comando: `PYTHONDONTWRITEBYTECODE=1 ./venv/Scripts/python.exe -m pytest tests/ -q -p no:cacheprovider`
→ **4377 passed, 4 failed, 41 skipped, 4 xfailed en 232,02 s** (`POST_suite_completa.txt`).

Ninguno de los cuatro lo produce este cambio; se atribuyen y se reportan en lugar de ocultarse, como
exige el §6 de la orden:

| Fallo | Causa medida | Relación con esta remediación |
|---|---|---|
| `test_pricing_resolution_wrapper::test_function_default_flags` | Ya declarado en `AGENTS.md` como flaky y ajeno al plan (registrado en `aba517a`) | Ninguna |
| `test_diagnostic_geo_metrics::test_diagnostic_includes_geo_metrics` | Ya declarado en `AGENTS.md` como fallo ajeno (mismo registro) | Ninguna |
| `test_validate_wiring::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion` | Los 5 receptores no resueltos están bajo `tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/…`, directorio **no trackeado** (`git ls-files tmp_test` vacío): un venv que otra sesión creó para JEV y que el verificador no excluye | Ninguna: esta sesión no escribió bajo `tmp_test/` |
| `test_validate_lesson_capitalization::test_medido_contra_el_predecesor…[TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]` | El plan fue **archivado** a `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y el `alcance` del índice pasó a listar solo los 4 planes vivos; la prueba sigue esperando al archivado | Ninguna: el índice y los archivos de planes no están entre lo modificado |

Los dos últimos son deuda de **otra** sesión con dueño propio (población del wiring frente a venvs
ajenos; coherencia índice↔archivado). La orden prohíbe expresamente editar bajo `Archives/` y limpiar
históricos, así que aquí se reportan sin tocarlos.

**Reproducción del veredicto de contraejemplos** (la copia PRE se extrae sin `stash`, que es lo que
permite medir la revisión anterior sobre trabajo sin commitear):

```bash
git show HEAD:scripts/decision_client.py > /tmp/decision_client_PRE.py
./venv/Scripts/python.exe evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/REMEDIACION-BLOQUE-A-2026-09-22/instrumentos/veredicto_contraejemplos.py \
    --modulo /tmp/decision_client_PRE.py --etiqueta PRE      # exit 1, 0/6
./venv/Scripts/python.exe evidence/…/instrumentos/veredicto_contraejemplos.py \
    --modulo scripts/decision_client.py --etiqueta POST      # exit 0, 6/6
```

Mientras `HEAD` sea `a3ab8f9` la etiqueta PRE es reproducible; después de un commit que toque la
puerta, el artefacto `contraejemplos-antes-despues.txt` es el registro, no una promesa de re-ejecución.

## 8. Cifras que este cambio mueve

> **Sesión 2**: las cifras de esta sección son las de la sesión 1 y quedaron vencidas por las diez
> funciones nuevas del cierre a–d. La cifra vigente está en §10; se conserva esta sección con su
> atribución en lugar de reescribirla.

- Funciones de test canónicas (método `grep -rE "^\s*def test_" tests --include=*.py`): **4.378 →
  4.405** (+27, todas de esta sesión: 22 en `decision_client`, 5 en `governance_numbers`). El valor
  **4.378 ya estaba en disk antes de esta sesión**: `AGENTS.md` publica 4.246, así que la
  desincronización es previa y no la produce este cambio.
- Donde quedó publicada la cifra tras el cierre documental (§9): `VERSION.yaml` en su bloque de
  comentario de release y `CHANGELOG.md` en su sección de Tests, ambas con el comando del método.
- Donde **no** se actualizó: `AGENTS.md` (línea de Estado Actual, bloque de Pruebas, tabla de
  «Cobertura por Modulo» y árbol de estructura). Su tabla marcaba 630 funciones para
  `tests/quality_gates/` cuando disk mide 736; rectificarla a mano sería otra cifra volátil más, y
  el §4.B de la orden propone justo retirar esas cifras en lugar de mantenerlas.

## 9. Cierre documental (autorización letra B, 2026-09-22)

Autorización recibida: «cifras canónicas y CHANGELOG/VERSION.yaml, sin tocar executor ni plantilla».

Ejecutado: `VERSION.yaml` a **4.77.4** con su bloque de comentario (cifra canónica incluida) y
entrada nueva en `CHANGELOG.md` con el formato que exige `CONTRIBUTING.md` (Objetivo / Cambios
Implementados / Archivos Nuevos / Archivos Modificados / Tests). El diff del CHANGELOG es
**puramente aditivo: 116 líneas añadidas, 0 eliminadas**, con los cinco encabezados `4.77.x` en orden.

**Un casi-accidente que vale la pena registrar:** la primera inserción del CHANGELOG usó como ancla
`# Changelog` + el encabezado `[4.77.3]`, y al reemplazarlo por la entrada nueva **el encabezado de la
entrada anterior desapareció** — su cuerpo quedó huérfano dentro de la nueva. Detectado al contar los
encabezados, no al leer el diff; restaurado y verificado con `git diff --numstat` (0 eliminaciones).
Es la familia de «editar estructura: verificar que no borre hermanos», y aquí el hermano era un
encabezado de release ajena.

### Lo que el bump arrastra y NO se resolvió

| Instrumento | Estado | Causa |
|---|---|---|
| `version_consistency_checker.py` | ✅ TODO SINCRONIZADO | Solo gobierna CHANGELOG ↔ VERSION.yaml ↔ REGISTRY |
| `sync_versions.py --check` | ❌ 7/7 reglas piden reescribir | El bump moved las cabeceras de `README.md`, `AGENTS.md` (×2), `.cursorrules`, `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` |
| `run_all_validations.py --quick` | **8/11** (antes 10/10) | Dos fallos por el arrastre de arriba + `Document Integration` (`DOMAIN_PRIMER=4.77.3` vs `VERSION.yaml=4.77.4`) |

El tercer fallo del quick no es de este cambio: `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md:118`
apunta a `.opencode/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, ruta que no existe (el documento vive
en `context/`). Es del propio documento de la orden, creado por otra sesión.

**Por qué se quedó así y no se corrigió a mano:** el hook `version-sync` corre `sync_versions.py` en
modo **escritura** con `always_run: true`, o sea que cualquier commit reescribiría esas siete cabeceras
— incluido `.cursorrules`, que la orden excluye expresamente en su §6 («no modificar `.cursorrules` por
arrastre de una sincronización no autorizada»). No hay subconjunto de reglas que deje el gate verde:
ninguna de las siete apunta a `CHANGELOG.md` ni a `VERSION.yaml`. La decisión sobre esas cabeceras es
del operador, no una consecuencia que este instrumento pueda tomar por su cuenta.

Mientras tanto el árbol queda **sin commitear**, que es el estado reversible: el bump está en la fuente
única, las cabeceras todavía dicen 4.77.3, y `git checkout -- VERSION.yaml CHANGELOG.md` deshace el
cierre documental sin tocar el código.

## 10. Cierre verificable (sesión 2, 2026-09-22) — retractación y estado final

**Retractación del cierre prematuro de la sesión 1.** La sesión 1 declaró el bloque A cerrado y
subió `VERSION.yaml` a 4.77.4. Ninguna de las dos cosas se sostiene: faltaban los pendientes
técnicos a–d de la orden, el cierre contractual de S11/S12 exige la enmienda en el plan CONTEXTO
(fuera del alcance autorizado), y el bump rompió Version Sync y Document Integration sin
autorización para editar a sus consumidores. La recomendación de §9 de deshacer con
`git checkout -- VERSION.yaml CHANGELOG.md` quedó obsoleta aquí: un checkout destruiría también la
normalización documental de esta sesión.

**Pendientes técnicos a–d completados en esta sesión.** Superficie: `scripts/decision_client.py`,
`scripts/validate_governance_numbers.py`, `tests/quality_gates/decision_client/` y
`tests/quality_gates/governance_numbers/`. Demostración por causa: `instrumentos/veredicto_pendientes_abcd.py`
→ `pendientes-abcd-antes-despues.txt` — **PRE (HEAD `a3ab8f9`) 0/6 con su causa, POST 6/6, exit 0**:

| Criterio | PRE (causa del rojo) | POST |
|---|---|---|
| a) Población vacía → `SIN-POBLACION` (no favorable, no exit 0) | `SIN-HALLAZGOS` sobre 0 archivos | `SIN-POBLACION` |
| a) Lectura incompleta → `LECTURA-INCOMPLETA` | `SIN-HALLAZGOS` con 1 no parseable | `LECTURA-INCOMPLETA` |
| a) Documento de gobierno vacío → `LECTOR-FALLIDO` exit 3 | exit 0 `[SIN-HALLAZGOS]` | exit 3 |
| b) Denominador con archivos únicos (solape no infla; L-VCF-11) | arbol=4 (suma de atribución) | arbol=3 + `excluidos_archivos_unicos` |
| c) Informe refleja escaneo+sonda+costura; sonda caída degrada | heredaba el status del escaneo | `componentes.sonda_tres_estados = SONDA-FALLIDA` |
| c) stdout de `--report` sin destino es JSON parseable | mezclaba relatos con JSON | JSON puro, aviso a stderr |

d) se retiró el acoplamiento a la partición exacta de 6 guards (correspondencia 1 a 1 **por
nombre**); las pruebas de mutación y el rojo contractual quedan intactos. Los cinco fixes, el
escaneo compartido y la salida sin escritura por defecto de la sesión 1 se preservaron; el trabajo
ajeno de `JEV/dependencias-fases.md` sigue sin tocar.

**Cifras vigentes (árbol final, comandos exactos):**

- Funciones canónicas (`grep -rE "^\s*def test_" tests --include=*.py | wc -l`): **4.415** (78 en
  `tests/quality_gates/decision_client/`, 30 en `tests/quality_gates/governance_numbers/`).
- Selección afectada: `pytest tests/quality_gates/decision_client
  tests/quality_gates/governance_numbers tests/regression -q -p no:cacheprovider` → **144 passed,
  exit 0** (17,67 s). Solo `decision_client`: 83 passed, 9,63 s con `--durations=5`.
- Suite completa (`sesion2_suite_completa.txt`, exit real 1): **4.387 passed, 4 failed, 41 skipped,
  4 xfailed en 264,13 s**. Los mismos 4 fallos atribuidos en §7; sus dos premisas se re-verificaron
  hoy (`git ls-files tmp_test` → 0 con `pydantic` en disco; `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/`
  existe). Ningún fallo nuevo.
- Batería de cierre sobre el árbol final: `run_all_validations.py --quick` → **11/11, exit 0**
  (Version Sync, Document Integration y OpenCode References vuelven a verde con el bump retirado y
  la referencia rota de la línea de arranque corregida); `sync_versions.py --check` → "All files in
  sync", exit 0; `validate_agents_md.py` → exit 0; `version_consistency_checker.py` → TODO
  SINCRONIZADO, exit 0.
- **Comparación retirada**: §9 publicó que el quick pasó «de 10/10 a 8/11». La cifra «10/10»
  corresponde a otro denominador y otra época que la corrida de 11 checks medida — comparación sin
  baseline, motivada por un bump que ya se retiró. El resultado vigente es **11/11** medido arriba.
- Evidencia nueva de esta sesión, con destino propio sin sobrescribir la de la sesión 1:
  `pendientes-abcd-antes-despues.txt`, `sesion2_suite_completa.txt`,
  `instrumentos/veredicto_pendientes_abcd.py`.

**Estado final del bloque A: LISTO PARA REVISIÓN, NO CERRADO CONTRACTUALMENTE.** Pendientes: (1)
registrar en el plan CONTEXTO la enmienda que traslada S11/S12 a este bloque; (2) commit del árbol
(decisión del operador, con la consecuencia conocida sobre las cabeceras vía hook `version-sync`);
(3) bloques B, C y piloto, cada uno con su autorización específica. Registro completo del alcance
autorizado en la orden §5-bis.

## 11. Auditoría del cierre y correcciones (sesión 3, 2026-09-22)

**Qué retracta esta sección.** El §10 declaraba los pendientes a–d completados y el bloque
«LISTO PARA REVISIÓN». La re-auditoría del árbol encontró tres sobreafirmaciones, todas corregidas
con prueba por causa, y dos límites que se declaran aquí en lugar de silenciarse:

| # | Lo que §10 afirmaba | Lo medido en la auditoría | Corrección (sesión 3) |
|---|---|---|---|
| 1 | «el informe refleja escaneo+sonda+**costura**» | El veredicto de costura era solo `files_changed==1`: con proveedores que no resolvían, repetidos o con respuestas idénticas el informe seguía saldando `SIN-HALLAZGOS` / exit 0 (reproducido en memoria antes de tocar nada) | `_veredicto_de_la_costura` exige doble `RESUELTO`, dos proveedores distintos y respuestas distintas; `--costura` comparte el veredicto y su exit respeta la tabla del docstring (1 sin despacho, 2 ruta ausente, antes moría en traceback) |
| 2 | «Conserva los hallazgos y las causas de incompletitud» (ítem a) | Cierto por componente, falso entre componentes: una ruta ausente mataba `--report` sin publicar el hallazgo ya obtenido del escaneo; en gobernanza un segundo documento ilegible borraba los hallazgos del primero y el stdout dejaba de ser JSON | `construir_informe` captura por componente (`fallos_de_componentes` con estado y causa) y emite informe **parcial** con exit 2/3 según causa; en gobernanza el `LectorFallido` se captura **por documento**, el status pasa a `LECTOR-FALLIDO` (exit 3), los hallazgos viajan en el informe y ningún destino se escribe con lectura incompleta |
| 3 | «partición de validadores desacoplada» | La igualdad de nombres contra la lista fija de seis seguía fijando la misma partición: un séptimo guard equivalente rompía el test de invariantes (reproducido con patch en memoria) | `GUARDS_DE_FORMA` se deriva de la puerta en colección; el test de invariantes solo afirma símbolos distintos y vivos; el guard extra cae por la función de payloads (precio contractual) y una prueba fija ese comportamiento |
| 4 | Instrumento «demostración por causa» de §10 | Su exit no gateaba el PRE; C1/C2 medían estados de función y no exits del CLI; no había criterio para d; se anunciaba como «a–d» siendo 6 criterios parciales | Nuevo instrumento `veredicto_cierre_a.py` (12 criterios): el PRE gatea el exit (baseline `a3ab8f9` intacta ⇒ todo PRE debe estar rojo o el instrumento sale 2), cada causa imprime el estado observado, se cubren wiring status→exit, costura, ambos informes parciales y d. El instrumento y el log de §10 quedan como antecedente, sin sobrescribir |

**Límites declarados (no afirmaciones).** (a) Los 4 fallos de la suite completa se publican con
premisas re-verificadas en disco, pero **sin reproducción mínima**: la atribución a trabajo ajeno
queda *pendiente de demostración*, no resuelta, y ningún validador se relajó para absorberlos.
(b) C1b/C2b del instrumento demuestran el **alambre** estado→exit del CLI inyectando el estado; el
estado por población vacía/incompleta real lo demuestra C1a/C2 sobre árboles plantados — el CLI no
puede apuntar su escaneo de raíz a un árbol vacío del repo sin tocarlo, y no se tocó.

**Medición de la sesión 3 (comandos y salidas reales):**

- Instrumento: `PYTHONDONTWRITEBYTECODE=1 ./venv/Scripts/python.exe instrumentos/veredicto_cierre_a.py`
  → `cierre-a-antes-despues.txt`: **PRE 12/12 rojo-por-causa, POST 12/12, exit 0**.
- Selección afectada: `pytest tests/quality_gates/decision_client tests/quality_gates/governance_numbers
  tests/regression -q -p no:cacheprovider` → **150 passed, exit 0** (87 + 37 + 26, 22,48 s).
- Suite completa: `pytest tests/ -q` → **4.393 passed, 4 failed, 41 skipped, 4 xfailed en 292,17 s**,
  exit real 1 (`sesion3_suite_completa.txt`) — los mismos 4 fallos, ninguno nuevo.
- Funciones canónicas (`grep -rE "^\s*def test_" tests --include=*.py | wc -l`): **4.421** (+6 sobre
  los 4.415 de §10).
- (La batería de validadores sobre el árbol final de esta sesión se registra al pie de esta sección
  tras ejecutarse: ver «Batería final sesión 3» más abajo.)

**Batería final sesión 3 (árbol final, todas de solo lectura, exit reales):**
`run_all_validations.py --quick` → **11/11, exit 0** · `sync_versions.py --check` → "All files in
sync", exit 0 · `validate_agents_md.py` → exit 0 · `version_consistency_checker.py` → TODO
SINCRONIZADO, exit 0.

## 12. Segunda auditoría del cierre (sesión 4, 2026-09-22) — causa comprobada, no impresa

**Qué retracta esta sección.** Una auditoría final de solo lectura encontró tres defectos técnicos
que las correcciones de §11 no cubrían; esta sesión los reprodujo antes de corregirlos y dejó las
correcciones con rojo/verde por causa:

| # | Defecto encontrado (medido antes de corregir) | Corrección (sesión 4) |
|---|---|---|
| 1 | El instrumento contaba los rojos del PRE pero **la causa se imprimía, no se comprobaba con un predicado**. Reproducido sabotajeando el fixture de C9 en una copia (solo C9 usa un segundo documento no vacío sin instancias): C9 quedaba rojo por fixture roto —su escenario ya no existía— y el instrumento certificó «todos cayeron en PRE por su causa» con **exit 0** (`sesion4_repro_defectos_antes.txt`) | Cada criterio lleva un **predicado de causa esperada** sobre lo observado, incluida la precondición del fixture; un rojo en PRE por causa no esperada hace salir 2 (INSTRUMENTO SOSPECHOSO). Control negativo con el mismo sabotaje: «rojos-PRE-con-causa-comprobada: 12/13», C9 señalizado, **exit 2** (`sesion4_control_negativo_causa.txt`) |
| 2 | El contract test `test_decision_client_contract_forma.py:145` anclaba el rojo a la **partición exacta** `{campos-conocidos, forma-choice}` por igualdad. Reproducido en memoria: un guard extra legítimo que también detecta la mutación producía un **falso rojo** mientras el superset `{campos-conocidos, forma-choice} ⊆ nombres` sostenía la atribución de causa (L-V2.1) | Relajado a comportamiento: el rojo debe **nombrar** a los guards que detectan la mutación (superset), sin enumerar la partición — coherente con el criterio d («sin partición fijada») y con la justificación documentada en el test |
| 3 | En gobernanza, una ruta AUSENTE disparaba una **puerta previa al análisis**: un doc legible + una ruta ausente → exit 2, stdout en prosa (JSON roto) y los 2 hallazgos del legible descartados (reproducido: doc legible solo → exit 1, JSON, 2 hallazgos; el mismo + ruta ausente → exit 2, prosa, hallazgos perdidos) | Población mixta: se analizan los legibles, la ruta ausente se publica con su causa en `fallos_de_lectura` («no existe (AUSENTE)»), estado `LECTOR-FALLIDO` con **exit 3**, ningún destino se escribe; el exit 2 queda reservado a la población sin nada analizable (todos los docs ausentes o fuente/hook ausentes). Semántica documentada en el docstring; cubierta por 3 tests nuevos y por el criterio **C11** del instrumento |

**Medición de la sesión 4 (comandos y salidas reales):**

- Instrumento fortalecido (13 criterios, +C11): `python instrumentos/veredicto_cierre_a.py` →
  `sesion4_veredicto_cierre_a.txt`: **PRE 13/13 rojos con causa-esperada: OK, POST 13/13, exit 0**
  («todos cayeron en PRE por la causa esperada, comprobada con predicado»). El log de §11
  (`cierre-a-antes-despues.txt`) queda como antecedente: sus causas estaban impresas, no comprobadas.
- Selección afectada: `pytest tests/quality_gates/decision_client tests/quality_gates/governance_numbers
  tests/regression -q -p no:cacheprovider` → **153 passed, exit 0** (29,50 s; +3 tests nuevos de
  gobernanza sobre los 150 de §11).
- Suite completa: `pytest tests/ -q -p no:cacheprovider` → **4.396 passed, 4 failed, 41 skipped,
  4 xfailed en 304,59 s**, exit real 1 (`sesion4_suite_completa.txt`) — **los mismos 4 fallos de
  §11, verificado por diff de la lista FAILED**; ninguno nuevo.
- Funciones canónicas (`grep -rE "^\s*def test_" tests --include=*.py | wc -l`): **4.424** (+3
  sobre los 4.421 de §11).
- (La batería de validadores sobre el árbol final de esta sesión se registra al pie tras
  ejecutarse: ver «Batería final sesión 4».)

**Nota de instrumento.** El control negativo del defecto 3 expuso además un `NameError` latente en
el camino de veredicto del instrumento fortalecido durante esta misma sesión: el elemento `(n, c)`
de las comprensiones de `rojos_post`/`causas_equivocadas` quedaba sin ligar y solo se evaluaba
cuando HABÍA una causa equivocada — justo en el camino de SOSPECHOSO. Corregido antes de medir el
POST; la corrida sana no lo detecta porque el filtro no pasa nunca.

### 12-bis. Auto-auditoría del propio cierre (sesión 4, segunda pasada) — tres brechas abiertas

Una revisión posterior del cierre encontró tres defectos en **la forma de cerrar**, no en el
producto, y esta sección los cierra con medición:

| # | Brecha | Medición que la cierra |
|---|---|---|
| 1 | **El predicado C7 seguía confundiendo síntoma con causa**: `except JSONDecodeError → causa_pre7 = True` aceptaba **cualquier** JSON inválido, incluido un exit 2 con `[AUSENTE]` (otra causa: puerta del verificador, no el veredicto mezclado). Comprobado con una observación inyectada: `causa_esperada_aceptada=True` ante exit 2 + `[AUSENTE]`. Consecuencia: «13/13 con causa comprobada» no cubría los caminos `except`, y el control de C9 no alcanzaba a C7 | C7 y C11 fueron los primeros extraídos a predicados con **firma positiva** del defecto nombrado (C7: exit 0/1 con resumen en stdout y sin puerta; C11: exit 2 que nombra la ruta del documento **y** fuentes del fixture presentes) y `_auto_test_predicados()` gatea el veredicto con exit 2. **El auto-test tuvo dientes desde su primera corrida**: cazó un error propio en un caso de control (sin `not`, y la rama de precondición sin aislar) → log `sesion4_veredicto_cierre_a_v2.txt`. Control de mutación: restaurar el predicado permisivo viejo en una copia deja la matriz en «13/13 con causa comprobada» y **solo** el auto-test lo detecta (`sesion4_controles_predicados.txt`). La generalización quedaba afirmada, no medida: se extrajeron entonces los **13** predicados a funciones puras y el auto-test pasó a 43 casos; forzar cada predicado a `lambda *a, **k: True` uno a uno hace fallar el auto-test y señala ese criterio, sin falsos OK (`sesion4_dientes_auto_test.txt`) |
| 2 | **Documentación sin conciliar**: el §12 prometía una «Batería final sesión 4» que no se había escrito, el CHANGELOG solo publicaba la suite de sesión 3, y «cerrado técnicamente» se afirmó antes de cerrar la brecha 1 | Escrito el bloque de batería con sus **cuatro** corridas reales (cada una etiquetada con el árbol que midió, incluido el log con el defecto de `EXIT=` tras `| tail`); añadidos la suite de sesión 4, el bullet de auto-auditoría y los controles del auto-test al CHANGELOG; la afirmación de cierre se re-escribe contra lo medido (§12-ter) |
| 3 | **Atribución de los 4 fallos por identidad, no por causa**: el diff de listas `FAILED` prueba población igual, no independencia | Medida cada causa (§12-ter). Dos caen igual en HEAD (geo, `lesson_capitalization`), una tiene causa demostrada como artefacto local ignorado (`tmp_test/venv-jev-sdk/`: 0 ficheros rastreados, regla `.gitignore:28`, y pasa en una extracción de HEAD sin ese directorio), y una —`test_function_default_flags`— queda **pendiente de mecanismo** (pasa aislado y pasa con `tests/financial_engine` completo; falla en las tres corridas completas). El intento de baseline completa en HEAD se declara inservible: 17 failed + 18 errors por estado local ignorado ausente |

### 12-ter. Medición y estado real tras la auto-auditoría (sesión 4)

- Instrumento final: `python -B instrumentos/veredicto_cierre_a.py` → `sesion4_veredicto_cierre_a_v4.txt`:
  **PRE 13/13 con causa-esperada OK, POST 13/13, auto-test OK (43 casos), exit 0**. Los logs v2 y v3
  quedan como mediciones de estados intermedios de esta sesión (v2: el auto-test cazando un error
  propio en un caso de control; v3: antes de extraer los 13 predicados a funciones).
- Controles (`sesion4_controles_predicados.txt`): sabotaje del fixture de C9 → INSTRUMENTO
  SOSPECHOSO exit 2 con C9 señalizado; mutación del predicado C7 permisivo → auto-test FALLA con
  exit 2 mientras la matriz sigue leyendo 13/13.
- Suite completa sesión 4 (`sesion4_suite_completa.txt`, `EXIT_PYTEST=1` en el propio log):
  **4.396 passed, 4 failed, 41 skipped, 4 xfailed en 304,59 s**; selección afectada **153 passed,
  exit 0**; funciones canónicas **4.424**.
- Atribución de los 4 fallos: demostrada para tres (dos fallan igual en HEAD; el de `wiring` es
  `tmp_test/` ignorado y pasa sin él); **pendiente de mecanismo** para
  `test_function_default_flags`, que además está fuera de la superficie autorizada. Independencia
  medida por referencias: 0 coincidencias de `decision_client`/`validate_governance_numbers` en los
  6 ficheros de los cuatro fallos (dos tests y sus validadores) y 0 en `modules/` ni en
  `scripts/run_all_validations.py`.
- **Cierre técnico, afirmación exacta**: los tres defectos encargados y los tres de la
  auto-auditoría quedaron corregidos con rojo reproducido y verde por causa; el instrumento
  distingue causa de síntoma en los **13** criterios y esa discriminación está medida, no leída del
  código (el bullet siguiente). Quedan abiertos, declarados y fuera de esta superficie: el mecanismo
  del fallo de pricing flaky y el cierre contractual (registro CONTEXTO de S11/S12, commit/push,
  bloque B/C y piloto).
- **Límite declarado del método (atribución por firma)**: el auto-test distingue las causas
  vecinas **enumeradas** —solución ya aplicada, estado intermedio, precondición del fixture
  apagada, puerta `AUSENTE`, lector caído, salida vacía—. Una causa desconocida que produjera
  exactamente la misma firma observada no se distinguiría: ese es el límite inherente de la
  atribución por firma y se declara, no se oculta. Auditado además el accept-set de C7: incluye la
  familia «palabra suelta `HALLAZGOS` sin marca bracketeada», que se comprobó **inalcanzable** en
  la revisión congelada — el GN de PRE imprime la marca bracketeada en todos los caminos que
  producen stdout (`git show a3ab8f9:scripts/validate_governance_numbers.py`, bloque
  `if not args.quiet`) — por lo que aceptarla no abre puerta a ninguna causa real; no se endureció
  por hipotético. Tras ese análisis, el archivo del instrumento cambió solo en docstring y una
  variable muerta: su salida re-corrida es **byte-idéntica** al log v4.
- **Cobertura del auto-test (afirmación medida, no leída del código)**: los **13** predicados de
  causa son funciones puras de la observación y el auto-test pasa **43 casos** sintéticos —por cada
  criterio, la firma baseline del defecto (contra sobre-tightening) y las firmas vecinas: la
  solución ya aplicada, el estado intermedio y la precondición del fixture apagada—. Los dientes se
  midieron predicado por predicado: forzar cada uno a `lambda *a, **k: True` hace que el auto-test
  falle **y señale ese criterio**; con los 13 forzados por separado, cero familias sin casos de
  rechazo y cero permisivos que pasaran inadvertidos (`sesion4_dientes_auto_test.txt`).
  - **Este párrafo retracta el anterior de la misma sección**, que declaraba un residuo («C1a…C10
    sin observación sintética») cuando el auto-test solo cubría C7 y C11. Ese residuo no era un
    límite del árbol sino trabajo propio sin hacer: quedó cerrado con la medición de arriba.

**Batería final sesión 4 (árbol final, todas de solo lectura):**
`run_all_validations.py --quick` → **11/11, exit 0** · `sync_versions.py --check` → "All files in
sync", exit 0 · `validate_agents_md.py` → exit 0 · `version_consistency_checker.py` → TODO
SINCRONIZADO, exit 0. Registro en cuatro destinos, cada uno con lo que realmente midió:
`sesion4_bateria_final.txt` (árbol previo a la auto-auditoría, códigos de salida correctos),
`sesion4_bateria_final2.txt` (mismo árbol que la 3 pero con **defecto de medición propio**: cada
`EXIT=` se capturó después de `| tail`, así que registraba el estado del `tail`, no el del
validador — queda como antecedente de ese error, detectado al releer el log),
`sesion4_bateria_final3.txt` (árbol tras extraer los predicados, sin tuberías) y
`sesion4_bateria_final4.txt` (**árbol final de la sesión**, con los 13 predicados y sus controles
ya escritos en estos documentos).
