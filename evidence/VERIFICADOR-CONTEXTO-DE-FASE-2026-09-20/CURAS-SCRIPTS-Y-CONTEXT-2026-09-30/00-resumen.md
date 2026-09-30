# Tanda CURAS-SCRIPTS-Y-CONTEXT — 2026-09-30 (resumen y checkpoint)

Orden unificada de sesion unica: curas en `scripts/` + verificador de frescura de `CONTEXT` + cierre de
pendientes de VCF y JEV. Esta sesion **no re-evaluo los planes**: los ejecuto, con los veredictos de la
evaluacion de solo lectura del 2026-09-30 como anclas.

Revision de partida: `7737347e1572b52cb50e527086d7df8cc3950b71`. Paso 0.1 medido: paridad con
`origin/master` = **0 0**, `git status --porcelain -uno` = **0**, y el porcelain completo mostro **solo** los
tres crudos del registro del 2026-09-29 (33-, 34-, m-33-), como anunciaba el parte.

## Estado por tarea

| Tarea | Estado | Verificacion |
|---|---|---|
| **T1** D-F5: `--fecha` (ISO estricta) y `--nota` en `log_phase_completion.py` | **HECHA** | 26 passed; tres mutantes con su caida atribuida (A/B/C) y un control negativo con el escritor de `7737347` que **reproduce** el defecto. Crudo `04-` |
| **T2** S19(d) salida (c): quinto patron + emision de `generado_por_sha` | **HECHA** (el coste del 21-c6 sigue sosteniendose, no hubo que PARAR) | 5 passed + 127 passed en las cuatro baterias hermanas; par re-medido y publicado (abajo). Crudos `01-`, `05-`, `10-`, `15-` |
| **T3** `scripts/verify_qmind_context_freshness.py`, ID **S34** | **HECHA** | 17 passed sin red; corrida real EXIT 0 sobre el notebook de 56 fuentes; fila S34 en `dependencias-fases.md` con espejo en `10-analisis` y cabecera desambiguada; cableado al completo 17->18 con sus pines. Crudos `03-`, `07-`, `12-`, `15-` |
| **T4** fila 10 (sub-punto de S29): gobernar la **descripcion** del alcance | **HECHA** | 12 passed + 30 passed de la hermana; mutante D (revertir la cura a-prima) corta **C9=2** con EXIT 1 leido sin tuberia; control negativo con el instrumento de `7737347`. Crudo `06-` |
| **T5** paquete de decisiones de JEV | **HECHA en su alcance de preparacion** | tres documentos + tres copias byte-identicas + crudo de shas, **solo** bajo `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-09-30/`. Sin etiquetas, sin congelar, sin red, sin B/C/RELEASE |
| **T6** sellos datados de las seis divergencias | **HECHOS** | seis sellos, texto original intacto, anclas por seccion, cero `archivo:linea` nuevos en el corpus. Crudo `13-` |
| **T7** registros, cola de writers y checkpoint | **HECHO** | sellos en las filas 4, 5, 10 y 11 del registro 33-; cifra de `AGENTS.md` movida y verificada; cola canonica en verde. Crudos `09-`, `11-`, `14-`, `15-`, `16-` |

## Pipeline final, con sus numeros

- Baseline **pre** (crudo `00-`): `3 failed, 4642 passed, 41 skipped, 4 xfailed`, `EXIT_SUITE=1`. Los tres
  rojos, atribuidos por nombre: `test_function_default_flags`, `test_diagnostic_includes_geo_metrics`,
  `test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion`.
- Baseline **por poblacion** (crudo `02-`): T1 14 passed, T2 7, briefing 57, T4 30, denominador 5, wiring
  **1 failed / 17 passed**, indice 9, gobernanza 54 — todo EXIT 0 salvo el rojo de wiring, ya atribuido.
- Suite **post**, re-corrida **despues de todas** las correcciones (crudo `18-`): `3 failed, 4688 passed, 41 skipped, 4 xfailed` en 316,52 s, `EXIT_SUITE=1`. `17-` es la corrida anterior a las tres ultimas correcciones y `11-` la anterior a ellas: los tres dan el mismo numero y los mismos tres nombres, que es la razon de re-correr en vez de extrapolar.
  **Mismos tres nombres** que el baseline: ningun rojo nuevo. `4642 -> 4688` = **+46** funciones-test nuevas,
  que es exactamente lo que anaden las cuatro baterias de la tanda (12 + 5 + 17 + 12).
- Baterias por poblacion **post** (crudo `16-`): 11 selecciones, todas EXIT 0 —
  T1 26, T2 5, T3 17, T4-c9 12, hermana T4 30, briefing 57, gobernanza 54, denominador 5, packs 7, indice 9,
  costura 87.
- `--strict` del hermano: `[PASS] QMind Write-back: 13/13`, EXIT 0. Frescura de CONTEXT: `[OK] 1 fresco, 0
  problemas`, EXIT 0. Gobernanza: `[SIN-HALLAZGOS]`, EXIT 0.
- Cola de writers: packs -> indice -> `--check` de ambos -> `--quick`, **13/13**, con la guarda de denominador
  aprobando la convivencia 13/18. `git diff --check`: EXIT 0.

## El par del parte 19-, publicado (T2 lo movio, como anunciaba el Paso 0.5)

| Concepto | Antecedente 09-29 | **Medido 2026-09-30** |
|---|---|---|
| numerador (lineas con sello UTC) | 53 | **53** (no se movio: es propiedad del escritor) |
| denominador (lineas de los cinco packs) | 9.481 -> 9.991 | **13.819** (serie: 9.481, 9.621, 9.636, 9.991, 10.630, **13.819**) |
| lineas que normalizan los cuatro patrones | 58 | **58** |
| lineas que normalizan los **cinco** | — | **63** (los +5 son la emision de `generado_por_sha`) |
| ratio | 0,56 % | **0,38 %** — y ahi esta la razon de publicar el conteo y no el ratio: el ratio es un derivado que se mueve solo |

## Los cinco cortes, y donde quedan

| Corte | Estado |
|---|---|
| Implementacion terminada | **SI** — cinco archivos de `scripts/` curados o anadidos, cuatro baterias |
| Verificacion terminada | **SI** — suite completa + 11 selecciones + quick + tres estrictos, con el crudo de cada corrida |
| Cierre documental | **SI** — este expediente, sellos en el registro 33-, fila S34 con su espejo, sellos T6, cifra de `AGENTS.md` |
| Listo para revision | **SI** — `git status --porcelain -uno` = 24 rutas modificadas + 4 rutas nuevas de codigo/tests, todas nombradas abajo |
| Espera de autorizacion | **SI, y aca para** — la orden reserva commit y push para letra propia. **Medido al cerrar: el commit quedo autorizado y ejecutado con esa letra (ver el sello de publicacion abajo); el push sigue sin autorizar** |

Rutas tocadas (24 modificadas): `AGENTS.md`; `scripts/` (5 modificados + 1 nuevo); `tests/` (2 modificados +
3 nuevos); los cinco packs de `briefing/`; el par `.opencode/LECCIONES-INDEX.md` + `lecciones_index.json`;
seis documentos de los dos planes archivados (VCF README, 06, 09, 10-analisis, dependencias-fases; JEV README,
01, 04, 10-analisis). Sin tocar: `docs/CONTRIBUTING.md`, `.agents/`, `VERSION.yaml`, `DOMAIN_PRIMER`,
`muestra.json`/`etiquetas.json`/`protocolo.json`, `dependencias-fases.md` de JEV (protegido), y la fuente
`01a0e4d9-…` del notebook (borrado irreversible, letra propia).

## Checkpoint final: lo que queda pendiente, por plan, con su dueno

**Verificado y cerrado en esta sesion**: filas 4 (D-F5), 5 (S19(d)(c)), 10 (sub-punto S29) y 11 (verificador de
frescura, con ID **S34** tras el censo) del registro unico.

**Sigue pendiente, y todo ello es acto del operador o de otra puerta**:

| # | Pendiente | Dueno | Que hace falta |
|---|---|---|---|
| 1 | **D-B** (AC3: versionar candidatos con `original_sha256` o enmendar la clausula) | Operador | decision (a)/(b). Esta tanda aporto la re-medicion: **0 de 4** shas originales casan (3.190 rutas / 3.110 blobs en HEAD; 9.307 ficheros en el arbol de trabajo), pero **4 de 4 `sanitized_sha256` si son reproducibles** con el `sha256_text` del propio runner, y el disco esta en CRLF mientras el blob esta en LF (dos shas para el mismo contenido). Esta en `02-material-…` y `05-…` de la preparacion |
| 2 | **D-D + P1** (revision humana de la muestra y mandato JEV-B) | Persona que se designe | firma. La muestra queda **disponible** en `PREPARACION-DECISION-2026-09-30/` con sus cuatro etiquetas `sin_revisar` y los umbrales propuestos con su justificacion; **no** se etiqueto ni se congelo |
| 3 | **JEV B -> C -> RELEASE** | Operador, en ese orden | permisos; `README:95` sigue vigente |
| 4 | **Gap de contrato de JEV** (seis campos que la puerta no expone) | Operador | elegir (a) extender la costura o (b) mover el ledger al runner. Las dos salidas con su coste medido estan en `01-gap-de-contrato.md`; lo medido que inclina la decision: la costura hace **una** llamada sin bucle, asi que `attempts`/`error_kind` no puede producirlos ella |
| 5 | **Aislado `tmp_test/` contra el wiring** | dueno de `scripts/validate_wiring.py` | `test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion` esta roja **por los 5 receptores de pydantic dentro del aislado** (produccion real: 0). **Re-investigado el 2026-09-30 por pedido del operador: todo esto en `PREPARACION-DECISION-2026-09-30/04-reinvestigacion-alerta-wiring-2026-09-30.md`, que rectifica dos cosas de esta fila.** (i) **«mueve una poblacion que otra bateria pinea» no es cierto**: ningun test pinea 1.368 ni 183 - las unicas dos lecturas son la asercion `== 0` que es el rojo y una auto-consistencia estructural; la nota de `conftest.py:104` que se cito pertenece al escaner de `decision_client`, otra poblacion. (ii) **hay una tercera salida medida, y es la recomendada**: gobernar el alcance por lo que declara el propio `.gitignore`, que saca exactamente los 684 del aislado, cero ficheros fuera de `tmp_test`, deja `gobernadas_resueltas` en 75 y baja el tiempo de 17,1 s a 9,8 s. Y sale ademas el defecto que la alerta tapaba: el script **sale `EXIT 0` con los 5 presentes** (la cola lo registra verde) y `.opencode/wiring_report.json` publica `en_produccion = 0` desde `d7ff932` (2026-09-20) sin `--check` que lo contra-verify. No se aplico nada: la cura del pendiente apaga un rojo de suite, y esos dos cortes quedan abiertos sea cual sea la eleccion |
| 6 | **D7 + S10** (activar Jev detras de la costura) y **D6** (dormida detras de D7), **D3**, **S14**, el **sub-punto del `--fix`** de S17 y **D-H** | sus filas | credencial + presupuesto; el disparador de S14; mandatos propios |
| 7 | **Borrar la fuente vencida `01a0e4d9-…`** del notebook (56 fuentes) | Operador, letra propia | `qmind source delete` es irreversible; la decision (a) del 09-29 dejo la forma original + cierre |
| 8 | **Documentacion del CLI del escritor** (la lista de usos en el workflow y en `docs/CONTRIBUTING.md` ahora le falta `--fecha`) | Operador | consecuencia de hacer obligatoria la bandera; CONTRIBUTING esta fuera de esta tanda por el limite de S32 y el workflow es config central |
| 9 | ~~**Push** de lo ya commiteado~~ **CERRADO 2026-09-30** | Operador, **por letra**; el L3 se pregunta al empujar | La letra fue «Push con L3». El L3 se corrio sobre los commits ya publicados y no dio hallazgos; el empuje fue fast-forward. Su sello esta en el bloque «Sello de publicacion» mas abajo, y el antecedente de esta celda («`d37c200` esta **delante** de `origin/master`») describe al arbol que escribio la fila, no al remoto de hoy |

## Defectos propios de esta sesion, declarados

1. Un mutante salio con **SyntaxError** y dio «22 failed» que no median nada; se repitio con pre-chequeo
   `ast.parse`. Un mutante se verifica sintacticamente antes de fiarse de su rojo.
2. El EXIT de un mutante se leyo detras de un `| tail` (el `0` era del `tail`); se re-midio redirigiendo a
   archivo. Igual con `validate_opencode_refs.py`.
3. Un parche del arnes inyecto una constante antes de `from __future__` y el rojo salio `NO-PRODUCIDO`, no
   `DIVERGE`.
4. Dos controles negativos fallaban **por el arnes, no por el instrumento**: la copia versionada no resolvia a
   sus hermanos (`ModuleNotFoundError`) ni su insumo de indice. Se resolvio con `PYTHONPATH` y con el
   differential en proceso.
5. Un sello mio metio literalmente una ruta de plan **que ya no existe** y el quick lo corto 12/13 (y el pack
   heredo la referencia). Se re-redacto la medicion sin esa ruta y se re-corrio la cola. Leccion: en el corpus,
   una ruta es una afirmacion, no un adorno.
6. Caracteres CJK colaron **dos veces** en prosa propia de esta tanda (U+6388 U+6743 en `01-gap-de-contrato.md`
   y U+63A8 U+65AD en la fila S34) y una tercera vez en el resumen que estaba escribiendo este parrafo, que es
   la razon de citarlos por codepoint y no reproducirlos: reproducirlos hace rojo el control que los mide. Los
   tres se barraron y el control se corrio **despues** de redactar (CJK propio en verde). Ademas aparecio un
   cuarto, **preexistente** (U+5236 U+5F3A en el docstring de `verificar_docs_manuales`, en HEAD desde antes de
   esta sesion): se reparo y se declara aqui porque no lo escribio esta tanda.
9. Al reubicar los cuatro sellos dentro de su fila de la tabla del registro (la primera version los dejo
   como linea suelta, que parte la tabla), el conteo de celdas revelo un **defecto preexistente ajeno a
   esta tanda**: la fila 11 tiene un `|` sin escapar dentro de ``git grep -E 'source download|fileSha256'``,
   o sea seis celdas donde la tabla define cinco. Se deja y se declara: arreglarlo es editar el registro de
   otra sesion por dentro, y la regla de la casa es anadir sellos, no re-escribir el registro.
7. El listado en crudo que produjo el censo de `CONTEXT` llevaba URLs firmadas con credenciales. Se leyo
   desde `temp/` y **se borro** al cerrar: en evidencia quedan solo `id`, `titulo`, `status` y
   `metadata.fileSha256` (la corroboracion no necesita publicar el enlace firmado).
8. La cifra de la cabecera de `AGENTS.md` se movio y su nota anterior sigue diciendo «en el commit que lleva
   esta nota los dos comandos dan 4,584»: eso describe al commit que la escribio, no a este. Ya venia advertido
   en el propio parrafo y se deja la advertencia donde esta.

## Sello de publicacion (medido, no citado de memoria)

La letra del operador fue «Commit». No fue «push», y no se simulo: `git rev-list --left-right --count
origin/master...HEAD` sigue diciendo que el commit esta por empujar, y el L3 no se corrio porque su pregunta
va con el empuje.

| Momento | Comando | Medido |
|---|---|---|
| Pre-commit | `git status --porcelain -uno` / conteo de staged | 24 modificadas + 4 nuevas; **28 rutas staged**, 0 sin stagear |
| Hook versionado | `scripts/git_hooks/pre-commit` (7 checks) | **7/7 PASSED — Commit allowed** (version, files, refs, citas, cierre de planes, indice, capitalizacion) |
| Commit | `git commit -F` (mensaje en archivo, sin letras problematicas) | `d37c200` — 28 archivos, **2.344+ / 123-** |
| Verificacion **en el arbol commiteado** | `python scripts/verify_packs_in_committed_tree.py --rev d37c200` | **EXIT 0**, `[OK] packs en el árbol de d37c200 (5/5 reproducidos por el escritor, 0 divergentes, 0 no evaluables)` |
| Idem, indice y gobernanza | `build_lesson_index.py --check` / `validate_governance_numbers.py --quiet` | **fresco (340 IDs)** / **SIN-HALLAZGOS** |
| Suite sobre ese mismo estado | `python -m pytest tests/ -q` (crudo `18-`) | `3 failed, 4688 passed, 41 skipped, 4 xfailed`, `EXIT_SUITE=1`, con los tres nombres del baseline |

**Lo que el verificador de packs en el arbol commiteado prueba aqui, y no era trivial**: es la primera vez que
el quinto patron de `NORMALIZAR` y la emision de `generado_por_sha` se miden **juntos sobre un commit** — el
escritor commiteado sella su identidad y el verificador commiteado la estabiliza. En scratch la prueba pasaba
por construccion (misma copia, mismo sha); sobre `d37c200` pasa con dos lados independientes.

**Este sello no puede nombrarse a si mismo**: viaja dentro del commit de la evidencia, que es el segundo de la
tanda. El primero (`d37c200`) lleva codigo, tests, packs, indice y corpus; este lleva expedientes.

## Sello del empuje (medido despues del hecho, no previsto)

La segunda letra del operador fue «Push con L3». Con esa letra el L3 **dejo de ser una pregunta abierta**: era
el modo pedido, asi que se resolvio la configuracion, se corrio la revision sobre los commits ya publicados y
solo despues se empujo. Orden real: escanear, empujar, re-verificar el remoto.

| Momento | Comando | Medido |
|---|---|---|
| Alcance antes de empujar | `git fetch` + `git rev-list --left-right --count origin/master...HEAD` | **`0 2`** — dos commits propios por delante, ninguno detras |
| Forma del empuje | `git merge-base origin/master HEAD` contra `git rev-parse origin/master` | el remoto estaba en `7737347`, que **es** el merge-base: fast-forward puro, sin rebase y sin historial ajeno en el medio |
| Barrido de credenciales del rango | `git grep -F` sobre las rutas de `git diff --name-only 7737347..HEAD` | **0 coincidencias** (ademas de las firmas OSS ya redactadas en el Paso 0) |
| Revision L3 | `qodersec review --layer=l3` sobre los cambios commiteados | **`findings_count: 0`** — sin hallazgos que pasar por la puerta de remediacion |
| Empuje | `git push origin master` | `7737347..382ad05  master -> master` |
| Remoto despues del empuje | `git ls-remote origin refs/heads/master` contra `git rev-parse HEAD` | los dos `382ad05cc23531a76d5361eed58cba8f79f5a228` |
| Paridad y arbol | `git rev-list --left-right --count origin/master...HEAD` / `git status --porcelain -uno` | **`0 0`** y **0 rutas** sucias de trazados |

**Lo que este sello no puede afirmar sin mentir**: que viaja con el rango que sella. El bloque se escribio
**despues** de `382ad05`, asi que su propio texto queda pendiente de un tercer commit; si ese commit llega, el
remote vuelve a moverse y las dos celdas de arriba (`0 2` y `7737347..382ad05`) pasan a ser el antecedente de
este empuje, no el estado del remoto. Es la misma regla que ya declara la fila 9: **el estado del remoto se
mide, no se infiere de esta frase**.
