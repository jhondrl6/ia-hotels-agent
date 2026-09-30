# El aislado `tmp_test/venv-jev-sdk` y el check de wiring que lo toca (medido 2026-09-30)

Item 3 del README del plan: verificar la exclusion de Git del entorno aislado y el check de wiring que lo
toca. **No se instalo nada, no se borro nada, no se toco `scripts/validate_wiring.py`.**

## 1. La exclusion de Git, confirmada

| Comando | Resultado medido |
|---|---|
| `git ls-files tmp_test` | **0** rutas versionadas |
| `git check-ignore -v tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/main.py` | `.gitignore:28: tmp_test/` |
| `git status --porcelain -uno` | **0** lineas (el aislado no aparece: esta ignorado) |
| `du -sh tmp_test` | **28 MB** |
| `find tmp_test -name "*.py" \| wc -l` | **690** ficheros `.py` |

O sea: el aislamiento por Git esta bien hecho - nada del SDK entra al repositorio, y `git status` no lo
muestra. El problema no es de versionado.

## 2. Donde si entra: el wiring descubre el arbol por sistema de ficheros

`scripts/validate_wiring.py:188-205` (`archivos_en_alcance`) recorre `root.rglob("*.py")` y excluye por
**rol de directorio** con la tabla `EXCLUSIONES_POR_ROL` (`:119-135`). La tabla tiene `venv`, `.venv`,
`.venv-wsl`, `__pycache__`, `node_modules`, `temp`, `output`, `evidence`, `archives`, etc. **No tiene
`tmp_test`**, y el segmento del aislado se llama `venv-jev-sdk`, que no coincide con ninguna clave (la
comparacion es por nombre exacto de componente, no por prefijo).

Corrida medida, con salida explicita a `temp/` para no pisar el informe versionado (la bandera es
`--write-report`, y su `const` apunta al `DEFAULT_REPORT` de evidencia):

    python scripts/validate_wiring.py --write-report temp/wiring-pre.json --quiet    EXIT=0
    cobertura: archivos_en_alcance 1.368 | archivos_excluidos_por_rol 8.408
               llamadas_descubiertas 183 | receptores_no_resueltos 30
               receptores_no_resueltos_en_produccion 5

Y los cinco `receptores_no_resueltos_en_produccion`, archivo por archivo:

    tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/fields.py:989   field
    tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/fields.py:1084  field
    tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/fields.py:1091  field
    tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/fields.py:1147  sub_field
    tmp_test/venv-jev-sdk/Lib/site-packages/pydantic/v1/main.py:1097    field

**5 de 5 estan dentro del aislado ignorado por Git. Produccion real: 0.**

## 3. Consecuencia en la suite, atribuida

`tests/test_validate_wiring.py::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion` esta roja, y es
uno de los **3 rojos preexistentes** del baseline de la suite completa de esta sesion
(`3 failed, 4642 passed, 41 skipped, 4 xfailed`, `EXIT_SUITE=1`; los otros dos son
`tests/financial_engine/test_pricing_resolution_wrapper.py::...::test_function_default_flags` y
`tests/test_diagnostic_geo_metrics.py::...::test_diagnostic_includes_geo_metrics`, ambos ajenos a esta tanda).
Su mensaje nombra exactamente las cinco rutas de arriba. Tambien es el rojo que la bateria suelta de la
seleccion marca como unica causa: `1 failed, 17 passed`.

Lectura honesta del resultado: **el check no encontro un defecto de produccion; encontro su propio insumo**.

⟦**Re-investigado el mismo dia, 2026-09-30, por pedido del operador.** Este diagnostico se sostiene y se
refuerza con el desglose de los 30 no resueltos (25 bajo `tests/`, 5 bajo el aislado, **0** en cualquier otro
directorio) y con la causa de raiz que aqui no se veia: **`scripts/decision_client.py:137-139` si excluye
`tmp_test` y `site-packages`, y `EXCLUSIONES_POR_ROL` del wiring no** - la cura de S11 (`fdd397f`, 2026-09-23)
se aplico a un escaner y no al otro. Dos cosas mas, que no dependen de la eleccion: el script **sale
`EXIT 0` con los 5 presentes** (la unica cola lo registra verde), y el derivado versionado `.opencode/wiring_report.json`
publica `receptores_no_resueltos_en_produccion = 0` desde `d7ff932` (2026-09-20) sin que ningun `--check` lo
contra-verifique. **Y hay una tercera salida que este documento no preveia**: gobernar el alcance por la
declaracion del propio `.gitignore` (`git ls-files --others --ignored --exclude-standard`), medida sin tocar el
arbol - saca exactamente los 684 del aislado, **cero** ficheros fuera de `tmp_test`, deja `gobernadas_resueltas`
en 75 y baja el tiempo de 17,1 s a 9,8 s. Todo eso, con la rectificacion del coste de re-anclaje (aqui se
temia un re-anclaje de bateria que no existe: ningun test pinea 1.368 ni 183), esta en
`04-reinvestigacion-alerta-wiring-2026-09-30.md`.⟧
La clausula que governa ("ningun caller productivo quedo sin resolver") se esta midiendo contra el SDK de
terceros de un entorno que el propio `.gitignore` declara fuera del proyecto. Es la familia del
«rojo de herramienta que no ve su insumo», pero al reves: ve un insumo que no deberia estar en su poblacion.

## 4. Las dos salidas, con lo que cada una toca (queda con el operador)

**(a) ensanar la tabla de roles**: anadir una clave al aislado. Dos formas, con costes distintos:
  - `tmp_test` como entrada nueva de `EXCLUSIONES_POR_ROL`, motivo "entorno aislado gitignorado (`.gitignore:28`)".
    Efecto medible: los 5 receptores salen de la poblacion, `receptores_no_resueltos_en_produccion` pasa de
    **5 a 0** y el test rojo pasa. Coste: el conteo de la cobertura (`archivos_en_alcance 1.368`) baja, porque
    los 690 `.py` del aislado pasan a `archivados_excluidos_por_rol`; y hay tests que pinean esa
    poblacion (ver abajo), asi que se re-anclan con su nota datada.
  - regla por sufijo/prefijo (`venv-*`), mas general pero mas facil de que trague un directorio legitimo.
**(b) mudar el aislado fuera del repo** (p. ej. al mismo nivel del workspace): el check queda intacto, y el
    directorio deja de estar dentro de `ROOT`. Coste: rompe la ruta que el piloto usaba, y es una operacion
    sobre trabajo en curso del usuario - no la ejecuta esta sesion.

Por que no se aplique (a) en esta tanda, aunque el mandato de la orden autoriza `scripts/`: **convierte un rojo
de suite en verde**. La casa no apaga un rojo sin que el operador lo vea, y aqui hay ademas un efecto
colateral que hay que elegir en conciencia: los 1.368 ficheros en alcance son un denominador publicado en el
informe y citado por la bateria. Lo documentado en `tests/quality_gates/decision_client/conftest.py:104` ya
describe que las aserciones que consumian esa poblacion "escaneaban los 17.9xx `.py` del arbol"; cambiar la
poblacion del wiring es cambiar el suelo de esas pruebas.

Lo que si queda dicho sin ambiguedad: **ningun receptor sin resolver pertenece a codigo del proyecto.** Si el
operador prefiere no tocar ni la tabla ni la ruta, la alternativa es registrar la divergencia como conocida y
dejar el rojo con su attribucion, que es lo que este documento hace.

## 5. Lo que no se toco

`scripts/validate_wiring.py` intacto. `tmp_test/` intacto (ni movido ni borrado). `requirements.txt`,
`modules/providers/llm_provider.py`, `VERSION.yaml` intactos. Ninguna instalacion, ninguna red, ninguna
credencial.
