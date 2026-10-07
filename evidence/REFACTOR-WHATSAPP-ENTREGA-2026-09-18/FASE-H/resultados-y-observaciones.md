# FASE-H — onboarding derivado, recorrido offline y runner de intento único (2026-10-06)

**HEAD de partida:** `ec8a272` (punta de `origin/master`, FASE-F sellada y empujada).
**Mandato:** `05-prompt-inicio-sesion-fase-H.md`. **Sin commit, sin push, sin tag, sin QMind, sin
`DOMAIN_PRIMER`, sin rotación de credenciales**: el mandato de ejecución no los autorizaba y los cinco cortes
se sostienen sin ellos (`04-contrato-ejecucion.md` §Límites y precedencias). El sha y el rango de H van al
sello documental de RELEASE, cobrando la decisión de C/D/E/F de no abrir sellos recursivos por acciones git.
**Contador v4complete: 0/1** — nada de esta fase ejecutó `main.py v4complete`.

⟦**Commit + L3 + Push EJECUTADOS el 2026-10-06 por orden literal «Git Commit + L3 + Push»:** commit único **`1c20695`** (40 archivos, +6.780/−92, **8/8** checks del pre-commit sin saltar), revisión L3 sobre `ec8a272..1c20695`: **0 hallazgos**, push de ese rango con paridad **0/0** verificada por `git ls-remote` (remoto en `1c20695`). Lo escrito antes describe el mandato de ejecución y se conserva como histórico: la orden no se reescribe sobre él, se **añade** (precedente `ec8a272` de FASE-F). **Sigue sin autorización: tag, write-back a QMind, rotación de credenciales, `DOMAIN_PRIMER` y las erratas S-H10/S-H11/S-F7**, que se cobran en el sello de RELEASE. El stamping del sha se hace aquí porque la propia orden lo hizo necesario; la decisión de no abrir sellos recursivos sigue en pie para sellos que nobody pidió.⟧

**Estado: COMPLETADA EN SUS CONTRATOS OFFLINE y NO HABILITANTE DE LA ARISTA A E2E.** El preflight que la fase
produce es **NO FAVORABLE**: 12 requisitos favorables y 1 en contra (`consentimiento_datado_sobre_la_url_viva`),
que FASE-A decidió que no puede emitir el agente. El operador eligió esta lectura entre tres opciones
(«cerrar H con preflight NO favorable»), no saltarse el requisito.

**Lectura declarada de Tarea 4.** El prompt dice «dejar H INCOMPLETA si algún prerrequisito no pasa». Medido y
por escrito: los prerrequisitos técnicos de H (identidad, rama del loader, frescura fail-closed, runner,
reserva, aislamiento de memoria) están verificados; el que no pasa es un acto del operador que el propio plan
le reserva. La fase cierra entonces como COMPLETADA EN CONTRATO / NO HABILITANTE, y la arista a E2E queda
cerrada por el mecanismo que el plan diseñó para eso: el preflight. Reabrirla exige el documento S-H1, no una
re-lectura de esta fase. Si el operador prefiere la etiqueta literal de INCOMPLETA, el cambio es de estado
documental y no toca ningún verde/rojo medido aquí.

## Cortes consumados (los cinco, sin commit)

| Corte | Estado | Cómo se midió |
|---|---|---|
| Implementación terminada | HECHO | `run_once.py` (runner stdlib), `derivar_onboarding.py`, `integracion_offline.py`, dos baterías nuevas de tests (58 funciones canónicas). **0 archivos de producto modificados**: el allowlist de H acota el código nuevo al runner |
| Verificación terminada | HECHO | PRE S1 **367 passed / EXIT 0** → POST S1 **367 passed / EXIT 0** (delta 0, misma selección y entorno); POST extendido **425 / EXIT 0**; S2 aislada **17 passed / 4 skipped** igual en PRE y POST; **13/13 mutantes rojos por su guard, 13/13 restaurados por sha256, 0 por import/sintaxis, 0 anclajes no únicos** |
| Cierre documental | HECHO | prompt H, checklist (fila H + AC9/AC12/AC13/AC14/AC15/AC17 + controles del intento único), `dependencias-fases.md` (filas H y E2E), 00 (§Aplicación efectiva H), 09 (§Cierre FASE-H), 10 (fila H + seguimientos), CHANGELOG bajo `## [Sin publicar]`, `docs/GUIA_TECNICA.md`, `log_phase_completion.py` sin GAP, derivados regenerados con su escritor |
| Listo para revisión | HECHO | quick final y `validate_document_integration.py`: los imprime la corrida (`quick_final.txt`); sin promesa de sha porque no hay commit que lo pinee |
| Espera de autorización | EN CURSO | Quedan pendientes de instrucción propia: commit+push de H y su L3, `DOMAIN_PRIMER`, write-back QMind, **emisión del consentimiento S-H1**, rotación de credenciales S-F6 y las erratas de REGISTRY (S-F7/S-C) |

## 1. Lo que se midió antes de editar (Tarea 1)

| Superficie | Instrumento | Resultado |
|---|---|---|
| Quick de apertura | `run_all_validations.py --quick` | **13/13, EXIT 0** (`quick_pre.txt`) sobre HEAD limpio |
| Colección conjunta | `pytest tests/e2e tests/delivery` en los dos órdenes | 3 errores de colección; **cada ruta colecciona sola sin errores**; causa: `tests/e2e/conftest.py` instala un stub de `selenium` en `sys.modules` (deuda S-H4) |
| Parser | `main.build_parser()` | `--permission-mode` existe y su default es `auto`; **`--onboarding-file` no existe**; `--force/--skip-check/--dry-run` existen y no van en el argv |
| Loader | `main._load_latest_onboarding_data` | con la URL del warehouse devuelve la observación re-convertida; con la URL de la corrida y sin derivado devuelve **None → `Using defaults` silencioso** |
| Tres identidades | productores reales | `hotel_donalfonsohotel.com` / `Hotel Don Alfonso` (slug `hotel_don_alfonso`) / `donalfonsohotel.com`: tres valores distintos, los tres fijados en el preflight |
| Puerta de permisos | `check_permission` | `auto` permite la auditoría externa de pago (~0,03 USD); `chat` la omite y el pipeline sigue con `audit_result=None` — mismo exit code, otro resultado (S-H5) |
| Memoria compartida | `MemoryManager` | `find_latest_analysis("donalfonsohotel.com")` **encuentra** `output/TAREA7-2026-09-19/v4_complete`; `cleanup_old_sessions(days=20)` borraría **8 de 10** sesiones al correr E2E (S-H6) |
| Frescura | presencia, nunca valor | `ONBOARDING_FRESHNESS_HOURS` no está en el entorno, ni en `.env`, ni en `.env.template`; el bloque `if freshness_hours:` no corre; edad medida del dato: **76 días** |
| Revocación | `evidence/…/FASE-F/credential_status.json` | una acreditación del operador (2026-09-18) y el resto `PENDIENTE-SIN-EVIDENCIA-OPERATIVA` (S-F6 sigue abierto) |

**Dos premisas del prompt cayeron contra el artefacto (`L-V.3`, cuarta vez que le pasa a este plan):**

1. El maestro §5 y el prompt de H decían que el `hotel_id` del reporte sale de `"hotel_id": args.url` en
   `run_v4_complete_mode`. Medido: esa asignación está en los payloads financieros y en `run_execution_mode`
   (main.py:923); el reporte escribe `state.hotel_id`, que produce
   `OnboardingController.generate_hotel_id()` = `"hotel_" + netloc normalizado`. El valor publicado por la
   corrida de TAREA7 (`hotel_donalfonsohotel.com`) sigue siendo el correcto; el productor citado no era el productor.
2. El prompt afirmaba que un hallazgo previo «cambia el flujo real: se reutiliza en vez de auditar». Medido por
   AST sobre `run_v4_complete_mode`: `discovered_analysis` tiene 1 asignación y 2 lecturas, y las dos son
   inofensivas (el guard `if` de la línea 1737 y el `print` de la 1738) — `consumos_que_cambian_el_flujo = []`.
   La reutilización real (`DeliveryContext.from_analysis_json`) vive en `run_execution_mode`. La exigencia del
   preflight se mantiene igual: el hallazgo existe, contamina la evidencia de aislamiento y hay que excluirlo o
   declarar la dependencia (L-PF11), pero por la razón medida, no por la afirmada.

## 2. Producto de la fase (todo dentro del allowlist)

| Artefacto | Qué hace |
|---|---|
| `evidence/…/FASE-H/run_once.py` | Runner stdlib: `reservar` con creación exclusiva (`O_CREAT` + `O_EXCL`) **antes** del spawn; `transicionar` con máquina de estados terminales y `attempts` que nunca baja; `lanzar_unico` (verifica preflight → reserva → proceso → captura redactada → exit code observado); `vigilar` (mira el PID, nunca relanza; muerto sin exit code ⇒ `DUDOSO` terminal); `inventario_memoria` (snapshot previo con sha256 y espejo del glob real de `cleanup_old_sessions`); `redactar_salida` y `_serializar_control` (el sumidero de F antes de disco y de consola); `preflight`/`emitir_preflight` (`intentos: 0`); `preservar_resultado` (inventario con hash, cuarentena clasificada, faltantes nombrados); `verificar_preflight` (argv, requisitos y hashes congelados) |
| `evidence/…/FASE-H/derivar_onboarding.py` | Deriva con el transformador real, cambia **solo** `hotel.url`, exige `fecha_captura` (si falta, rechaza), declara `no_disponible` lo que `_FIELD_MAP` no propaga, verifica el hash de la fuente antes y después, y decide la **rama del loader por contenido** (no por la clave `fuente`, que el transformador también escribe) |
| `evidence/…/FASE-H/integracion_offline.py` + `.json` | Recorrido offline con la red cortada (y prueba de que el corte tiene diente): parser, identidades, puerta de permisos, loader, frescura, pre-gate de D con su par permitir/bloquear, lector AC9 de D sobre el baseline real, resolvedor de E y snapshot previo de memoria |
| `output/…/clientes/hotel_don_alfonso_onboarding.yaml` | El derivado (gitignored por `output/*/`): cuatro campos con productor, `fecha_captura: 2026-07-22`, `campos_confirmados` realmente presentes, URL de la corrida |
| `evidence/…/FASE-H/onboarding_provenance.json` | Hash de la fuente, selector único, URLs original/solicitada y su normalización, atribución al operador, ruta+hash del derivado, productor por campo, respaldo de FASE-A con su límite y la rama efectiva |
| `evidence/…/FASE-H/preflight.json` | `intentos: 0`, argv congelado con `--permission-mode auto` explícito, 10 hashes congelados, las tres identidades, snapshot previo de `.agent/memory` y 12 requisitos nombrados con su causa |

**Por qué el runner carga el sumidero por ruta de archivo y no por import:** `modules/utils/__init__.py`
importa `horarios_detector`, que importa `selenium` (medido). Un `from modules.utils.redaction import …`
arrastraría el grafo productivo y `.env` dentro del runner, que es lo que el mandato de H prohíbe. Lo gobiernan
dos dientes: `test_el_runner_es_stdlib_y_no_arrastra_providers_ni_credenciales` (AST de imports) y
`test_importar_el_runner_no_carga_selenium_ni_dotenv` (proceso limpio que solo importa el runner).

## 3. Veredicto por AC

* **AC14 — VERIFICADO OFFLINE.** Selector único sobre la fuente real (1 de 6 observaciones); cero y múltiples
  coincidencias detienen; hash de la fuente idéntico antes y después; URL atribuida al operador con su
  normalización, **sin** afirmar equivalencia universal de dominios ni redirección comprobada; `fecha_captura`
  presente y conservada (sin fecha la derivación **rechaza**: falla cerrado, porque el bloque del loader no
  corre); `adr_cop` y `occupancy_rate` declarados `no_disponible` y ausentes del derivado (DA-P1.9: frontera de
  transformación trazable, no llenada); **rama del loader medida dos veces** y ambas en `YAML_DE_DIR_CLIENTES`;
  el contrafactual con la URL histórica devuelve None → `Using defaults` silencioso (ese es el riesgo que el AC
  goberna); un `monkeypatch` sobre el transformador no anula al loader; con `ONBOARDING_FRESHNESS_HOURS=24` el
  loader **sí** rechaza el dato viejo. El fixture viejo se declara descartado como modelo.
* **AC17 — VERIFICADO OFFLINE con hijo falso stdlib.** Reserva exclusiva antes del proceso; el intento se
  consume al crear el proceso y queda consumido tras fallo y tras timeout; `exit_code` solo si se observó la
  terminación (en timeout queda `None`, nunca fabricado); segundo lanzamiento rechazado **antes** de crear
  proceso, incluso después de fallo (dos hilos con barrera: uno gana, el perdedor no instancia nada);
  vigilancia reanudable sin relanzamiento; `DUDOSO` terminal; `attempts` no baja; argv congelado validado contra
  el parser real; divergencia de hashes y argv no autorizado detienen el spawn **sin crear el control**; el
  control productivo de FASE-E2E sigue inexistente (aserción explícita de la batería). La rama real (spawn
  efectivo) es de E2E.
* **AC13 — CERRADA LA INTEGRACIÓN CON EL RUNNER (S-F5 y S-F8).** stdout y stderr del hijo falso traen una forma
  de credencial armada por concatenación dentro del proceso; lo que llega a disco y a consola está redactado,
  no existe ningún crudo en el directorio de capturas, y `assert_redacted` del contrato de F tiene por fin un
  llamador en el producto (aserción AST). El propio `run_control.json` pasa el mismo guard: un argv con forma de
  credencial no llega a escribirse. **La revocación sigue sin certificar por tests** (S-F6, dueño operador).
* **AC9 — VERIFICADO OFFLINE para el lector nuevo de H.** `leer_control` distingue `ABSENT`, `READ_ERROR` (JSON
  roto, raíz que no es objeto, ruta que no es archivo) y `READ_OK` con **vacío válido** (`data == {}`: archivo
  que existe y no declara nada, que no es fuente ausente — L-PF10). Baseline real: el `preflight.json` que
  escribió la fase, leído por ese mismo lector (no un fixture).
* **AC12 — PARCIAL (H re-ejecuta el par de E y aporta el suyo).** El par permitir/bloquear con
  `DeliveryPackager` y `ActaWriter` reales sigue en
  `tests/quality_gates/tribunal/test_fase_e_snapshot_resolvedor.py`; un test de H assertiona los tres nombres
  para que no se borren y mide que `write/publish/suppress`, el Juez y `outcome.py` no cambiaron en esta fase
  (`git diff HEAD --name-only` vacío, y los cuatro archivos están en el inventario que el spawn coteja). Lo que
  H certificó es su propio par: con preflight favorable en un control de test se crea proceso; con preflight en
  contra no se crea proceso **ni** se crea el control. La rama de la corrida única la cierra VERIFY.
* **AC15 — VERIFICADO OFFLINE.** PRE/POST con la misma selección literal y entorno, delta 0 en S1; +58
  explicado por los dos archivos nuevos; las 58 funciones canónicas contabilizadas aparte; 13 mutantes con
  guard, test, causa impresa, exit codes y restauración por sha256; el rojo ajeno y orden-dependiente del piloto
  JEV se conserva en la regresión en vez de excluirse.

## 4. Mediciones del cierre

| Medición | Valor | Artefacto |
|---|---|---|
| Quick de apertura | 13/13, EXIT 0 | `quick_pre.txt` |
| PRE S1 (10 rutas conjuntas) | **367 passed / 0 failed / EXIT 0** | `tests_baseline_pre.txt` |
| PRE S2 (`tests/e2e`, aislada) | 17 passed / 4 skipped / EXIT 0 | `tests_baseline_pre_e2e_aislado.txt` |
| POST S1 (misma selección) | **367 passed / EXIT 0 (delta 0)** | `tests_baseline_post.txt` |
| POST extendido (S1 + baterías de H) | **425 passed / EXIT 0** | `tests_post_extended.txt` |
| POST S2 aislada | 17 passed / 4 skipped / EXIT 0 (delta 0) | `tests_baseline_post_e2e_aislado.txt` |
| Funciones canónicas | **4.982 en HEAD → 5.040 en el árbol (+58)** | `git grep -c -E "^\s*def test_" HEAD -- tests` y el grep del árbol |
| Casos frente a funciones de la selección | 367 casos sobre 325 funciones en PRE (42 de parametrización) | `seleccion_pertinente.txt` |
| Mutantes | **13 / 13 rojos por su guard / 13 restaurados por sha256 / 0 por import o sintaxis / 0 anclajes no únicos** | `run_mutations.py` → `mutation_report.json`, crudo en `mutaciones_crudo.txt` |
| Regresión completa (sello, una sola corrida) | **1 failed / 5.122 passed / 41 skipped / 4 xfailed en 359,83 s (EXIT 1)** sobre el árbol definitivo. El único rojo es el ajeno y orden-dependiente del piloto JEV (`test_jev_pilot_deepseek_brazo.py`), que pasa **15/15** en su archivo y **141/141** en su directorio aislados — el mismo que declararon C, D, E y F | `tests_postfull_regresion.txt`; tres corridas desechadas se archivan en `descartados_por_superposicion_de_corridas/` (ver §7) |
| Archivos de la fase (medidos al cerrar) | **39 = 13 modificados + 26 sin versionar** (excluyendo `briefing/` y `__pycache__/`, que cae bajo la regla de `.gitignore`), excluyendo `briefing/` (decisión del plan: no versionar los packs): 2 baterías de tests, 21 artefactos en `FASE-H/` —incluidos los tres crudos desechados—, 9 documentos del plan y de gobierno (`00`, `05-H`, `06`, `09`, `10`, `dependencias`, `CHANGELOG`, `docs/GUIA_TECNICA.md`, `.opencode/wiring_report.json`, `.opencode/LECCIONES-INDEX.md`, `.opencode/lecciones_index.json`, `docs/contributing/REGISTRY.md`, `docs/contributing/.last_doc_phase.json`). **0 archivos de producto modificados** | `git diff --name-only HEAD` y `git status --porcelain -uall` |
| Red del recorrido | cortada con prueba de diente (`AssertionError` al intentar `socket.create_connection`) | `integracion_offline.json §red` |

**Reutilización declarada (y por qué sigue vigente):** el PRE se tomó antes de la primera edición y no se
reutilizó para el POST. El `sanitization_report.json` de FASE-F **no** se reutilizó: H midió su propia boca de
captura sobre hijo falso. El par de AC12 de FASE-E se re-ejecutó como test, no se citó su verde heredado. La
regresión completa se corrió sobre el árbol definitivo, después de las mutaciones restauradas y verificadas.

## 5. Deuda declarada con dueño

| ID | Qué | Dueño | Condición para cerrarla |
|---|---|---|---|
| S-H1 | **Consentimiento datado sobre la URL viva inexistente**: el preflight lo nombra y `spawn_autorizado=false`. El de FASE-P4 ampara `hoteldonalfonso.com` y declara expresamente que no es entrega | operador (FASE-A decidió que el agente no puede emitirlo) | documento `evidence/…/FASE-H/consentimiento-corrida.md` con bloque `iah-consentimiento` (`url_amparada` exacta, `fecha_captura_aceptada`, `limite_de_frescura_dias`, `autoriza` con «entrega», `declarado_por`, `fecha`). **Ventana medida y cerrada: el límite debe caer en [76, 90]** porque `EDAD_MAXIMA_DIAS = 90` en el runner; **último día útil: 2026-10-20** (edad 90). Desde el 2026-10-21 la edad es 91 y ningún consentimiento alcanza: haría falta una **captura nueva** del hotel, y el maestro §5 prohíbe editar la fecha. Con el documento emitido, `--emitir-preflight` queda favorable y **no consume la reserva** |
| S-H2 | Anclaje por `run_id` de los JSON timestamped (`gate_report_*`, `pain_ledger`, `financial_scenarios`), deuda que FASE-E asignó a H | E2E/VERIFY; la cura es de `review_inputs.py`, fuera del allowlist de H | E2E declara las rutas efectivas de su corrida; otra sesión con mandato de producto cierra el anclaje |
| S-H3 | `legacy-ancestor-walk` sigue siendo el fallback sin manifiesto (deuda de E, dueño H/E2E) | E2E/VERIFY | en una corrida real el manifiesto existe y la rama no se toma; se declara sin curar |
| S-H4 | `tests/e2e/conftest.py` inyecta un stub de `selenium` en `sys.modules` y rompe la colección de las rutas que lo siguen, **en cualquier orden de argumentos** | arnés de tests (fuera del allowlist de H) | poblar los nombres que el producto pide o importar el stub solo dentro del directorio; mientras, la selección se mide en dos unidades y se declara |
| S-H5 | El argv congelado fija `--permission-mode auto`, que autoriza llamadas externas de pago (~0,03 USD por auditoría) | operador, antes del spawn | confirmación expresa del modo y del gasto; con `chat` la corrida sería otra cosa con el mismo exit code |
| S-H6 | El spawn borra estado compartido: `cleanup_old_sessions(days=20)` eliminaría **8 de 10** sesiones de `.agent/memory` | E2E (preservación) | respaldo o aceptación explícita, con el snapshot previo ya guardado en `preflight.json` |
| S-H7 | `find_latest_analysis` devuelve un **directorio** porque `main.py:3830` guarda `analysis_path=output_dir`, no el `analisis_completo.json` | producto (memoria/assessment), dueño VERIFY | decidir si la referencia debe ser el archivo; hoy el consumidor de `execute` abriría un dir |
| S-H8 | La normalización de URL vive en dos definiciones: `main._normalize_url` y una copia privada en `OnboardingController.generate_hotel_id` (su comentario declara que no es importable) | identidad/calidad, fuera de H | unificar sin invertir la dependencia; H fija los valores medidos de las tres identidades |
| S-H9 | `DOMAIN_PRIMER` **no se regeneró**: el mandato de H no autoriza escribir `.agent/knowledge/DOMAIN_PRIMER.md` (está versionado). Checkpoint arrastrado desde C | RELEASE, con instrucción expresa | `doctor.py --regenerate-domain-primer` solo con mandato de escritura |
| S-H10 | Erratas de registro heredadas (S-F7 de FASE-F y la de FASE-C) siguen esperando el sello de RELEASE | RELEASE | mismo commit documental del release |
| S-H11 | **Errata propia:** el registro publicó `--archivos-mod 27` (medido antes de regenerar derivados) y el conteo final es **39** (13 modificados + 26 sin versionar, excluyendo `briefing/` y `__pycache__/`). El conteo crece con cada corrida desechada que se archiva: se publica el medido al cerrar, no el del momento del registro. El escritor no tiene bandera de corrección y re-correrlo duplicaría la fila | RELEASE | rectificación en el sello documental del release, no en REGISTRY (precedente idéntico: C y F) |

## 6. Lo que la sesión midió sobre su propio instrumento

1. **La red no se puede cortar antes de importar.** La primera versión sustituía `socket.socket` antes de
   `import main`: `ssl` hereda de `socket` y el import revienta con `TypeError: function() argument 'code' must
   be code, not str`. El corte se instala **después** de los imports y sustituye `create_connection`/`getaddrinfo`,
   con una prueba de diente que exige el `AssertionError`.
2. **Un verde que depende del orden de recolección no es un verde.** La contaminación de `selenium` se midió en
   los dos órdenes de argumentos y con cada ruta aislada antes de dividir la selección en dos unidades: la
   división es por el defecto del arnés, no para ocultar un rojo (S-H4).
3. **Dos mutantes en un solo hunk no prueban un guard.** Apagar `O_EXCL` sin apagar el pre-chequeo de
   `leer_control` dejaba la batería verde: el rechazo venía de la otra pata. La reserva tiene dos guardas y el
   mutante M1 quita las dos, o el rojo no prueba lo que dice probar.
4. **El ancla de un mutante no puede ser una clave de dict que depende del scheduling.** M1 buscaba la clave
   `'b'` y perdía el motivo según qué hilo ganara; el ancla estable es la palabra que imprimen las dos
   representaciones, y quedó escrito en el arnés.
5. **La forma de una credencial no puede quedar literal en un archivo versionado.** La batería la construye por
   concatenación **dentro del proceso hijo**, porque `main.py` persiste el argv en `run_control.json` y la pata
   `staged` de `_check_no_secrets` (que no aplica la exclusión de cuarentena, medido por FASE-F al commitear) lo
   cortaría. Es la lección `L-F-RED` aplicada antes de que el hook la aplique a golpes.
6. **El sello se corre al final, y una corrida propia puede invalidar a otra corrida propia.** La primera
   regresión completa se tomó antes de las últimas ediciones documentales de la propia fase (las filas de métricas
   de `09` y `10`, que leen validadores de gobernanza e integración documental). Ese crudo se archiva en
   `descartados_por_superposicion_de_corridas/` con su número y se re-corrió la regresión sobre el árbol
   definitivo: **el sello publicado es el último**, no el primero. Es el mismo error de FASE-F (su corrida
   `regresion_1_vencida_por_edicion_propia.txt`) repetido a los tres días por otra sesión: la regla no estaba en
   el contrato, estaba en el informe de F, y un informe de fase no es un mecanismo.

## 7. Sello de regresión

`tests_postfull_regresion.txt` guarda la corrida completa sobre el árbol definitivo de la fase, corrida **sola**,
sin ningún otro pytest concurrente: **1 failed / 5.122 passed / 41 skipped / 4 xfailed en 359,83 s (EXIT 1)**. El
único rojo es ajeno a H y orden-dependiente:
`tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`,
que en este árbol pasa **15/15** en su archivo aislado y **141/141** en su directorio. Es el mismo rojo que
declararon C, D, E y F, con dueño (piloto JEV) y no se cura aquí.

**Cuatro corridas anteriores quedan desechadas y archivadas, no reutilizadas**, en
`descartados_por_superposicion_de_corridas/`:

| Crudo desechado | Por qué | Su número |
|---|---|---|
| `tests_postfull_regresion.txt` (primera) | se superpuso con la segunda: dos `pytest tests/` sobre el mismo árbol | 2 failed / 5.121 passed — el rojo extra era `test_verify_packs_in_committed_tree.py::test_un_destino_relativo_no_escribe_dentro_del_clon`, que en aislado pasa **7/7** |
| `tests_postfull_regresion_crudo.txt` | la otra mitad de la misma superposición | 1 failed / 5.122 passed |
| `tests_postfull_vencida_por_edicion_documental_propia.txt` | quedó vencida por ediciones documentales de la propia fase (las filas de métricas de `09` y `10`, que leen los validadores de gobernanza e integración documental) | 1 failed / 5.122 passed en 371,15 s |
| `tests_postfull_vencida_por_dos_ediciones_posteriores.txt` | vencida por dos ediciones posteriores de la propia fase: la cita textual del item de revocación en `run_once.py` y la ventana del consentimiento en los documentos | 1 failed / 5.122 passed en 375,45 s |
| `tests_postfull_vencida_por_la_ultima_prosa.txt` | vencida por la última corrección de prosa de este informe (la propia cifra del sello y la tabla de desechadas) | 1 failed / 5.122 passed en 361,46 s |

Las cuatro devuelven el mismo conteo (1 failed / 5.122 passed) y el mismo rojo ajeno: lo único que cambió entre ellas fue el árbol que medían y el tiempo de pared. **Consecuencia para quien lea el sello: lo publicado son los conteos y el crudo; el tiempo de pared es de la corrida publicada y no se re-corre por edits de prosa.**

Lección de instrumento, y es la segunda vez que le ocurre a este plan: FASE-F archivó su
`regresion_1_vencida_por_edicion_propia.txt` por el mismo motivo tres días antes. La regla no estaba en el contrato,
estaba en un informe de fase, y **un informe de fase no es un mecanismo**: mientras no haya un verificador que la
fuerce, la caducidad del sello depende de que quien lo corre lo recuerde.

## 8. R2 — presupuesto e instrumento

**FUERA DE SERVICIO (R2.1).** `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>` pide el
transcript del cliente y su acceso no está disponible; es la misma condición que declararon A, G, 0, C, D, E y
F. No se estimó cumplimiento ni se comparó con la referencia de 60.

**Auto-reporte en unidad propia, separado del instrumento:** ~100 intervenciones de herramienta hasta «listo para
revisión» (recuento a ojo de la propia sesión, con esa unidad declarada; el corte autorizado fue «listo para
revisión» porque no hubo mandato de commit). Desglose contable: 12 corridas de pytest de selección (PRE, POST,
extendido, S2 en PRE y POST, dos baterías de la fase re-ejecutadas tras cada arreglo de instrumento, el arnés de
packs en aislado y las dos baterías otra vez tras refrescar evidencia), **13 mutantes × 2 corridas** del arnés,
**3 regresiones completas** (dos desechadas y archivadas: una por superponerse dos corridas, otra vencida por
edición documental propia), 4 corridas del quick, 3 emisiones del preflight, 2 pasadas de la cadena de derivados
(packs → índice → `--check` → refs → citas → wiring) y 1 pregunta al operador por el requisito que no podía
emitir. Por encima de la referencia de 60: se registra como **checkpoint** y no se partió la fase ni se recortó su
alcance. No comparable con tramos medidos por el instrumento.

## 9. Para quien commitee H

* El inventario congelado del spawn incluye `evidence/…/FASE-H/run_once.py`: si ese archivo se edita al
  commitear, el preflight queda vencido y hay que re-emitirlo (`--emitir-preflight`) en el mismo commit.
* Derivados que esta fase venció y se regeneraron con su escritor: `wiring_report.json` (los `.py` nuevos de
  `evidence/` suman al alcance), `LECCIONES-INDEX.md`/`lecciones_index.json` (la fila §Aplicación efectiva H),
  citas del plan y `docs/contributing/.last_doc_phase.json`.
* `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/` está gitignored por `output/*/`: el YAML derivado **no**
  viaja en el commit. Su hash y su rama viven en `onboarding_provenance.json`, que sí viaja. En otra máquina se
  re-deriva con `derivar_onboarding.py`, no se copia a mano.
* La pata `staged` de `_check_no_secrets` leerá este informe y `preflight.json`: no citan valores crudos, pero
  cualquier edición posterior que introduzca una forma de credencial en la evidencia cortará el commit
  (precedente: el commit de F, `20a07ae`).
* `scripts/validate_wiring.py --write-report` escribió `.opencode/wiring_report.json` con CRLF y `core.autocrlf` lo normaliza al indexar: el aviso de `git add` es esperable y el blob será LF (precedente medido por FASE-F; si se promete un sha del archivo, prometer el del objeto, no el del disco).
* El sha de los commits de H y su rango van al **sello documental de RELEASE**, como los de C, D, E y F.
* **No autoriza E2E**: primero S-H1 (consentimiento del operador), luego `--emitir-preflight` y su verificación
  en la sesión de E2E, que es la única que puede lanzar el proceso.
