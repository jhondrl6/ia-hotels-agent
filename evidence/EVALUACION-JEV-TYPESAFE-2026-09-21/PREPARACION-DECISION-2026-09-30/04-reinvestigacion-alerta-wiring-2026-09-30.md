# Re-investigacion de la alerta `tmp_test/` vs `validate_wiring.py` (medido 2026-09-30, segunda pasada)

Abre por peticion del operador sobre el pendiente 5 de `00-resumen.md`. **No se toco nada**: ni
`scripts/validate_wiring.py`, ni `tmp_test/`, ni `.opencode/wiring_report.json`. Todo lo de aqui se midio en
memoria o contra el arbol de trabajo, y el arbol quedo como estaba (la unica ruta sucia al medir es el sello
del empuje, ajena a esta investigacion).

Este documento **rectifica dos afirmaciones de `03-aislado-y-wiring.md`** y anade una tercera salida que no
estaba en las dos que registro. Lo que `03-` acierta y no se repite: la exclusion de Git del aislado esta bien
hecha (`git ls-files tmp_test` = 0, `.gitignore:28`), y el check no encontro un defecto de produccion.

## 1. De que esta hecha la alerta, medida entrada por entrada

Corrida fresca de `construir_reporte(ROOT)` sobre el arbol de trabajo (17,1 s), sin escribir el informe:

| Clave de `cobertura` | Valor |
|---|---|
| `archivos_en_alcance` | **1.368** |
| `llamadas_descubiertas` | **183** |
| `receptores_no_resueltos` | **30** |
| `receptores_no_resueltos_en_produccion` | **5** |
| `gobernadas_resueltas` | **75** |
| `violaciones` | **0** |
| exit del script solo (`--quiet`, sin `--write-report`) | **0** |

Los 30 no resueltos se desglosan por primer segmento de ruta y el corte es limpio:

    tests     -> 25
    tmp_test  ->  5
    (ningun otro directorio) -> 0

O sea: **el numerador de produccion es exactamente el aislado, y no queda ni un receptor sin resolver en
`modules/`, `data_validation/`, `data_models/`, `agent_harness/`, `scripts/` ni en la raiz.** Los cinco son
llamadas a `validate(...)` sobre un receptor llamado `field` / `sub_field`, todas con `resolucion =
receptor_sin_binding`, dentro de `tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/{fields,main}.py`.

El mecanismo que las produce, en el propio script: `_metodo_de` compara **por nombre pelado** contra
`NOMBRES_GOBERNADOS = {detect_pains, validate, with_validation, _generate_dynamic_services_table}`; si el
AST no deduce el tipo del receptor, la entrada **se publica** como `RECEPTOR_NO_RESUELTO` en vez de
descartarse. Pydantic v1 llama a `field.validate(...)` por dentro: mismo nombre, otro mundo. La clausula
gobernada («ningun caller productivo quedo sin resolver») se esta midiendo contra codigo de terceros.

Cuantas veces pesa el aislado: de sus **690** `.py`, **684** entran en alcance (los otros 6 caen por un
componente excluido), o sea **el 50,0 % del denominador** del check (684 de 1.368). El aislado ocupa 28 MB.

## 2. El defecto real: dos lectores del mismo arbol con dos tablas de exclusion

Esto es lo nuevo, y es lo que convierte la alerta de «ruido» en «deuda»:

| Instrumento | Tabla | Contiene `tmp_test` | Contiene `site-packages` |
|---|---|---|---|
| `scripts/decision_client.py:137-139` (`ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION`) | 11 claves | **si** | **si** |
| `scripts/validate_wiring.py:119-135` (`EXCLUSIONES_POR_ROL`) | 18 claves | **no** | **no** |

La entrada del hermano no es casual: se anadio el **2026-09-23** como cura de la deuda **S11** (commit
`fdd397f`), y su leccion esta capitalizada en `L-VCF-11`: el residuo entre «medir en disco» y «medir en el
indice de Git» era una **exclusion no declarada en el denominador**. El mismo defecto existe en el wiring y no
se barro cuando se promociono la regla: la cura de S11 se aplico a un solo escaner.

Detalle adicional, y va en la misma direccion: `decision_client` compara componentes **en minuscula**
(`p.lower()`), `validate_wiring` los compara **exactos**. Con la tabla actual eso no muerde, pero es una
segunda divergencia silenciosa entre los dos instrumentos sobre la misma poblacion.

## 3. Rectificacion a `03-`: el coste de re-anclaje no era como lo describia

`03-` decia que ensanar la poblacion «es cambiar el suelo de esas pruebas» y citaba `conftest.py:104`. Medido:

- Nadie pinea **1.368** ni **183** como literal en `tests/`. Las unicas dos lecturas de las cifras del wiring
  son `tests/test_validate_wiring.py:381` (la asercion `== 0`, que **es el rojo**) y `:403`
  (`llamadas_descubiertas == len(poblacion)`, que es **auto-consistencia estructural**: sigue siendo verdad con
  cualquier poblacion).
- La nota de `tests/quality_gates/decision_client/conftest.py:104` habla del escaneo de
  `decision_client.escanear_aislamiento` sobre «los 17.9xx `.py` del arbol», que **no es la poblacion del
  wiring** y ya excluye `tmp_test`. No se re-ancla nada alla.
- Barrido de citas literales (`git grep -E "\b1368\b|1\.368|\b183 llamadas\b"` sobre todos los trazados): las
  unicas menciones vivas estan en `00-` y `03-` de esta propia preparacion y en expedientes historicos de otros
  planes, que son registro cerrado. Ningun documento de gobierno fija la cifra, que es ademas lo que ya declara
  `RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md` sobre las cifras de cobertura viva.

**Coste real de la cura: una linea en la tabla del script + su nota datada.** No el re-anclaje de una bateria.

## 4. Lo que si esta roto y la alerta tapaba: el verde del check no avala la clausula

Medido con el arbol tal cual, con los 5 presentes:

- `python scripts/validate_wiring.py --quiet` -> **EXIT 0**. `RECEPTOR_NO_RESUELTO` «se cuenta y publica», no
  viola.
- `run_all_validations.py --quick` -> `[11/13] Wiring` en **verde**, y su mensaje lleva el denominador (183 /
  1.368 / 30 no resueltos / 0 violaciones).
- `python -m pytest tests/test_validate_wiring.py -q` -> **`1 failed, 17 passed`**, y el unico fallo es la
  clausula de produccion.

Es decir: **la cola de validaciones puede estar 13/13 mientras la clausula que se supone que esa cola protege
esta roja.** El unico diente de la clausula vive en la suite, y la suite se entrega con tres rojos. No es un
problema de `tmp_test`: es que el verificador no codifica su propio criterio en el exit code (familia de la
leccion «la salida del verificador debe codificar el criterio»).

## 5. Y el derivado versionado esta vencido sin que nadie lo mida

`.opencode/wiring_report.json` **esta versionado** y hoy publica:

    git_sha d7ff932 | archivos_en_alcance 611 | llamadas 169
    receptores_no_resueltos 25 | receptores_no_resueltos_en_produccion 0
    GOBERNADA_CON_OMISION 3 | GOBERNADA_CONFORME 14

Contraste: el commit `d7ff932` es del **2026-09-20** y el aislado `tmp_test/` tiene `mtime`
**2026-09-24 11:38**. El informe publicado **no vio nunca el aislado**: describe un arbol que ya no existe, y
su linea `receptores_no_resueltos_en_produccion = 0` es la garantia que un lector razonadoiria como vigente.

Por que nadie lo corta: el script **no tiene `--check`**. Sus unicas banderas son `--root`, `--write-report`,
`--ignore-known`, `--json`, `--quiet` (medido en `main`). Y `run_all_validations.py:698` lo invoca **sin**
`--write-report`, o sea la cola re-calcula pero **no** publica ni compara: el artefacto versionado y la corrida
viva pueden divergir indefinidamente. Es la misma familia de S19 / L-VCF-17 («un derivado cuyo generador no se
verifica»), con la agravante de que aqui el derivado lleva un contador de seguridad.

Nota de procedimiento: `--write-report` sin argumento **pisa** `.opencode/wiring_report.json` porque su `const`
es `DEFAULT_REPORT`. Toda corrida de esta investigacion paso ruta explicita a `temp/` o trabajo en memoria.

## 6. Tercera salida, que no estaba en `03-`: gobernar por declaracion de Git, no por tabla de nombres

Las dos salidas de `03-` eran (a) anadir `tmp_test` (o una regla de prefijo `venv-*`) a `EXCLUSIONES_POR_ROL` y
(b) mudar el aislado fuera del repo. Hay una tercera que no mantiene una lista a mano:

> **(c) excluir del alcance lo que el propio `.gitignore` declara excluido**, resuelto en lote con
> `git ls-files --others --ignored --exclude-standard -z`.

Medida sin tocar el arbol, intersectando el conjunto ignorado con los 1.368 ficheros en alcance:

| Magnitud | Con el arbol de hoy |
|---|---|
| `.py` declarados ignorados por Git | 8.962 (venv 7.618, `tmp_test` 690, `.venv-wsl` 582, `temp` 72) |
| ficheros en alcance **que tambien** estan ignorados | **684** |
| esos 684 fuera de `tmp_test/` | **0** |
| alcance resultante | **1.368 -> 684** |
| `receptores_no_resueltos_en_produccion` resultante | **5 -> 0** (mismo resultado que (a)) |
| llamadas en poblacion | 183 -> 174 (las 9 del aislado: 5 no resueltas + 4 `EXCLUIDA_POR_CLASE_NO_GOBERNADA`) |
| `gobernadas_resueltas` | **75 -> 75** (no se pierde ninguna gobernanza) |
| `violaciones` / excepciones | 0 / 0 en los dos escenarios |
| tiempo de `construir_reporte` | **17,1 s -> 9,8 s** (−42 %) |

Ventaja sobre (a): el corte **no come ni un fichero del proyecto** hoy, y no necesita que nadie recuerde anadir
la clave cuando aparezca otro aislado manana. Las otras tres raices ignoradas (`venv`, `.venv-wsl`, `temp`) ya
estan en la tabla de roles, o sea la declaracion de Git **concuerda** con la tabla existente en todo menos en el
hueco que causo la alerta. La tabla de roles sigue siendo necesaria para lo ignorado-pero-versionado
(`evidence`, `archives`, `Archives`, `output`), que no cae por este camino.

Riesgo declarado de (c), con su direccion de fallo: si Git no esta disponible el conjunto ignorado sale **vacio**,
asi que el alcance vuelve a ser el de hoy (sobre-inclusivo, con el falso positivo otra vez a la vista) y **nunca**
se queda ciego a codigo del proyecto. Y hay que mantener el `en_tests` aparte: los 25 receptores bajo `tests/`
son legiblemente exentos por politica, no por ignorarse.

Contra (b): mover `tmp_test/` es una operacion sobre trabajo en curso del usuario y rompe la ruta que usaba el
piloto JEV; no la ejecuta esta sesion, y con (a) o (c) deja de ser necesaria.

## 7. Que queda, y con quien

- **Recomendacion**: **(c)**, con la tabla de `EXCLUSIONES_POR_ROL` intacta como capa para lo versionado, y una
  linea en el informe publicando `excluidos_por_declaracion_git` con su conteo (la regla de S11: una exclusion
  sin conteo publicado es el defecto original, no su cura).
- **No se aplica aqui** por la misma razon que en `03-` y con mas fuerza ahora: (c) **apaga el rojo de suite del
  pendiente 5**, y el pendiente 5 esta listado como decision del operador. Si el operador elige (a) en vez de
  (c), el resultado numerico es el mismo (5 -> 0) y solo cambia el mantenimiento.
- **Lo que no depende de la eleccion y esta abierto igualmente**: el `EXIT 0` del verificador con la clausula de
  produccion rota (§4) y la **ausencia de `--check` sobre `.opencode/wiring_report.json`**, que hoy publica
  `en_produccion = 0` desde un arbol del 2026-09-20 (§5). Curar la poblacion **no** cierra ninguno de los dos:
  sacados los 5 del aislado, el rojo de la clausula se apaga pero el verificador seguiria dando verde sin haber
  mirado su propio criterio, y el derivado seguiria vencido sin instrumento que lo corte.

## 8. Estado del arbol despues de medir

`scripts/validate_wiring.py`, `tmp_test/`, `.opencode/wiring_report.json`, `tests/` y todos los documentos
gobernados: **intactos**. Corridas con salida explicita a `temp/` o en memoria; ninguna escritura sobre el
informe versionado. `git status --porcelain -uno` al cerrar esta investigacion: **1 ruta** (el sello del empuje
en `00-resumen.md`), que es la unica escritura de la sesion y no toca esta alerta.
