# Sello de publicacion de la cura del pendiente 5 (paso 1, salida (c)) — medido 2026-09-30

Cierra el circuito abierto por `04-reinvestigacion-alerta-wiring-2026-09-30.md`: ese documento
**medido** recomendó la salida (c) y dijo expresamente «no se aplica aqui», porque apagar el rojo
de suite del pendiente 5 era decision del operador. El operador la tomo con tres letras
separadas, y este crudo registra que cada accion tuvo su letra:

| Letra | Que autorizo | Que se hizo |
|---|---|---|
| «Letra 1: aplica el paso 1 (c) en `scripts/validate_wiring.py` con TDD … no toques los pasos 2 y 3 ni `decision_client.py`» | la cura, acotada | cura + bateria; sin commitear |
| «Commit + L3» | commitear y revisar en la capa profunda | dos commits; `git push` **no** estaba en la letra y no se corrio |
| «push» | el empuje | fast-forward de `382ad05..abd181c`, y despues la re-verificacion del remoto |

## Lo que viajo, en dos commits

| Commit | Contenido | Rutas | Hook |
|---|---|---|---|
| `2f9b662` | docs(EXPEDIENTE): la re-investigacion de la alerta del aislado | 4 (el propio `04-` mas los tres sellos que lo referencian), 214+/3- | 7/7 |
| `abd181c` | fix(scripts): el alcance del wiring se goberna por la declaracion del propio Git | 2 (`scripts/validate_wiring.py` 110+/11-; `tests/test_validate_wiring_alcance_por_declaracion_git.py` 466 lineas nuevas), 576+/11- | 7/7 |

Orden con motivo: el codigo cita la ruta de `04-` en su docstring, asi que la evidencia viaja
**antes** que la cita. Un commit de codigo que apunta a un archivo sin commitear deja de ser
verificable en su propio arbol.

## La cura, en su linea de medicion

Consulta en lote `git ls-files --others --ignored --exclude-standard -z` como segunda capa del
alcance; `EXCLUSIONES_POR_ROL` queda entera gobernando lo versionado. Antes y despues, medido
sobre el arbol de trabajo:

| Magnitud | Antes | Despues |
|---|---|---|
| archivos en alcance | 1.368 | **685** |
| llamadas descubiertas | 183 | **174** |
| receptores no resueltos | 30 (25 bajo `tests/`, 5 bajo el aislado) | **25** (todos bajo `tests/`) |
| `receptores_no_resueltos_en_produccion` | 5 | **0** |
| `gobernadas_resueltas` | 75 | **75** |
| `construir_reporte` | 17,1 s | **9,8 s** |
| excluidos por declaracion de Git | capa inexistente | **684**, 0 fuera de `tmp_test/` |

Linea impresa por el verificador despues de la cura (lo mismo que publica el check 11 del quick):

    [OK] Wiring: 174 llamadas descubiertas en 685 archivos | gobernadas 75 (conformes 21,
    omisiones 0) | amparadas por excepcion 0 | violaciones 0 | 684 excluidos por declaracion de
    Git | receptores no resueltos 25

## Verificacion, con el instrumento que la midio

- **TDD en orden**: la bateria nueva contra el script **sin curar** dio `10 failed, 1 passed`;
  contra el script curado, `12 passed`. El passed que sobrevive al rojo es
  `test_lo_versionado_sigue_excluyendose_por_rol`, que afirma una invariant anterior a la cura.
- **Hermana**: `tests/test_validate_wiring.py` → `18 passed`. El rojo que el pendiente 5 tenia
  senalado (`test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion`) se apago por la cura,
  no por editar la asercion.
- **Dientes**: dos mutantes con ancla unica y `ast.parse` previo. Apagar solo la consulta a Git
  reincorpora el aislado y su violacion; borrar solo la clave `evidence` de la tabla incorpora
  lo versionado. Mas el invariante de particion sobre el arbol real (alcance + rol + Git =
  `rglob`, sin duplicados, y el `cantidad` publicado cuadra con las rutas).
- **Control negativo**: anclado a `382ad05` (revision publicada, nunca HEAD), leido con
  `git show` y **ejecutado**; ese instrumento si mete el aislado en alcance. La premissa se
  corta: en esa revision no aparece la bandera de la consulta y su `archivos_en_alcance`
  devuelve dos baldes.
- **Suite completa** (arbol final, identico al commiteado):
  `2 failed, 4701 passed, 41 skipped, 4 xfailed, 230 warnings in 344,32 s`, `EXIT_SUITE=1`. Los
  dos rojos son los del baseline de la tanda anterior (`test_function_default_flags`,
  `test_diagnostic_includes_geo_metrics`); el tercero era el del pendiente 5 y ya no esta.
  Conteo: `4688 → 4701` = +13, que se desglosa en +12 funciones nuevas y el rojo que se volvio
  verde.
- **Cola**: `run_all_validations.py --quick` → `TOTAL: 13/13 validations passed`, con la guarda
  de denominador aprobando.
- **Verificado en el arbol del commit**, no en el de trabajo:
  `verify_packs_in_committed_tree.py --rev abd181c` → `EXIT 0`,
  `[OK] packs en el arbol de abd181c (5/5 reproducidos por el escritor, 0 divergentes, 0 no
  evaluables)`.

## Pre-vuelo y forma del empuje

- `git fetch` + paridad `0 2` (dos por delante, ninguno por detras).
- Fast-forward puro: `git merge-base origin/master HEAD` = `382ad05…` = el tip remoto.
- Alcance: 2 commits, 6 rutas, 790+/14-.
- Barrido de credenciales sobre los **blobs del rango** (`git grep -I -c` de los marcadores sobre
  las cuatro rutas de evidencia, el script y el test): `EXIT 1`, o sea **cero coincidencias**.
  Solo conteos; nunca se imprimio el contenido de una linea.
- Revision de seguridad en la capa profunda sobre ese conjunto de commits: sin hallazgos
  (`findings_count: 0`), corrida **antes** del empuje y sobre el mismo tip que se empujo.
- Empuje: `382ad05..abd181c  master -> master`.
- Despues: `git ls-remote origin refs/heads/master` = `git rev-parse HEAD` =
  `abd181c52d679b0da791b6f491e4cc9932689118`; paridad `0 0`; `git status --porcelain -uno` = 0
  rutas.

## Lo que este sello NO cierra, declarado en vez de barrido

1. **`AGENTS.md` sigue publicando 4.651 contra 4.663 versionados.** La dependencia que la casa
   declara ya se cumplio: las doce funciones viajaron **antes** que cualquier cabecera, asi
   que en `abd181c` los dos comandos ya cuadran (metodo canonico del arbol de trabajo: 4.663;
   `git grep -c` sumado sobre HEAD: 4.663). Falta solo la cabecera, y AGENTS.md es config
   central: letra propia.
2. **Paso 2**: el verificador continua sin codificar su criterio en el `EXIT`. Con la poblacion
   curada el cero es ahora correcto por contenido, pero el codigo no lo afirma: la clausula que
   `04-` senalado en su seccion 4 sigue abierta.
3. **Paso 3**: no hay `--check` sobre `.opencode/wiring_report.json`. El artefacto versionado
   sigue en `schema_version` 1.0 y `git_sha` `d7ff932` (2026-09-20) contra un emisor que ya es
   1.1, y **no se regenero** en esta letra: toca la misma clausula que goberna el paso 3.
4. **Los crudos de sesion no viajaron**: las corridas de suite, quick, packs y el informe de
   consulta quedaron bajo `temp/`, que `.gitignore` excluye. Este documento los transcribe por
   esa razon, y por la misma razon reproduce las lineas literales que los producen.
5. **Este sello no puede nombrarse a si mismo dentro del rango que sella**: se escribio despues
   de `abd181c` y del empuje, asi que su propio texto queda pendiente de un commit posterior,
   por letra.
