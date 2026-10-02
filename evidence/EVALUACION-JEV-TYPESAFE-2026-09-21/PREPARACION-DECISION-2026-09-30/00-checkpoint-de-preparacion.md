# Paquete de decisiones de JEV — sesion de preparacion, no de fase (2026-09-30)

Destino unico de esta sesion sobre el plan `EVALUACION-JEV-TYPESAFE-2026-09-21` (archivado). Autorizacion:
el propio plan, `README.md` §«Texto para una sesion de preparacion y decision», items 1-3. Ninguna escritura
fuera de este directorio. **No se etiqueto, no se congelo la muestra, no se infirio nada, no hubo red, no se
ejecuto FASE-B/C/RELEASE** — que es justo lo que los items del README reservan para una persona o para los
permisos del operador.

Revision de partida medida: `7737347e1572b52cb50e527086d7df8cc3950b71`, paridad `0 0` con `origin/master`,
`git status --porcelain -uno` = 0.

## Re-medicion previa que el README exige, con su numero de hoy

| Comando | Medido hoy 2026-09-30 | Antecedente citado en el README |
|---|---|---|
| `git status --porcelain -uno` | **0** lineas | «es un antecedente fechado», no se copia |
| `git rev-parse --short HEAD` | `7737347` | — |
| `ls scripts/decision_client.py scripts/triage_lesson_relevance.py` | ambos presentes | idem |
| `python scripts/decision_client.py --provider-status` | `provider_status = NO-CONFIGURADO`, `motivo_clase = env-de-proveedor-sin-definir`, EXIT **1** | el mismo codigo tri-estado (0/1/3) de la costura |
| `python -m pytest tests/quality_gates/decision_client/ -q` | **87 passed**, EXIT 0 | la seleccion esta verde: hoy el gap de contrato no es un rojo, es una ausencia de superficie |
| `python scripts/validate_wiring.py --write-report temp/wiring-pre.json --quiet` | `archivos_en_alcance 1368`, `receptores_no_resueltos 30`, `receptores_no_resueltos_en_produccion 5`, EXIT 0 | los 5 son del aislado `tmp_test/` (ver `03-`), ninguno de produccion real |

Nota de instrumento, leida antes de correr: la bandera del informe es `--write-report`, y su `const` apunta al
`DEFAULT_REPORT` versionado. Correrla sin argumento habria re-escrito evidencia cerrada (la familia de «el
verificador que escribe pisa el pasado»). Se paso siempre ruta explicita a `temp/`.

## Los tres items, cada uno con su puerta

1. **Material para la decision humana de P1 (fila 2 del registro `33-`).** `02-material-muestra-y-umbrales.md`:
   la muestra BORRADOR queda disponible en este directorio como copia identica (sha y bytes declarados), con
   sus cuatro etiquetas `sin_revisar`, y los umbrales del protocolo con su justificacion y su estado
   «a-decidir». Nadie de esta sesion etiqueta ni acuerda: `human_reviewed` sigue en `false`.
   Lo que destraba: la firma de una persona designada, no capacidad tecnica.
2. **Delta de contrato de §Gap de contrato medido.** `01-gap-de-contrato.md`: las dos salidas con su coste
   medido contra la costura vigente, para que el operador elija. Prohibido y no hecho: segunda costura,
   duplicar `decision_client.py`, recortar AC1/AC2.
3. **Exclusion de Git del entorno aislado.** `03-aislado-y-wiring.md`: `git ls-files tmp_test` = **0**, el
   aislado existe en disco (28 MB, 690 `.py`), y el check de wiring que lo toca esta documentado con su
   hallazgo y sus dos salidas. No se instalo nada y no se movio nada.

## Lo que queda pendiente al cerrar esta preparacion, con su dueno

| Pendiente | Dueno | Que lo destraba |
|---|---|---|
| Etiqueta humana de los 4 pares y acuerdo de umbrales (P1 / D-D) | la persona designada (hoy `revision_humana = «obligatoria, pendiente de designar responsable»`) | su firma; ninguna sesion puede producirla |
| Elegir salida (a) o (b) del gap de contrato | Operador | lectura de `01-`; la eleccion abre el mandato de codigo correspondiente |
| Decidir `tmp_test/`: exclusion por rol (a), mudar el aislado (b), **o gobernar el alcance por la declaracion del `.gitignore` (c, la recomendada)** | dueno de `scripts/validate_wiring.py` | `03-` traza (a) y (b); `04-reinvestigacion-alerta-wiring-2026-09-30.md` trae las **tres** medidas y rectifica a `03-`: el re-anclaje que (a) temia no existe (ningun test pinea 1.368 ni 183), y (c) saca exactamente los 684 del aislado sin tocar ni un fichero del proyecto. Las tres apagan el rojo de suite, por eso ninguna se aplica sola. **Ninguna cierra los dos defectos que `04-` descubre: `EXIT 0` del verificador con la clausula rota, y el informe versionado vencido desde `d7ff932` sin `--check`** |
| FASE-B (2 bloqueantes humanos, corre sin red), FASE-C (preflight + presupuesto escrito, la unica con red), RELEASE | Operador, en ese orden | permisos explicitos; `README:95` sigue vigente: ninguna fase es ejecutable hoy |
| D7 + S10 (activar Jev como segundo proveedor detras de la costura), D3, D6, S14, S19 no es de este plan | sus filas en el registro `33-` del plan hermano | cada una con su puerta ajena |

## Inventarios de este directorio

    muestra-COPIA-IDENTICA.json      2.651 B  sha256 1abfaafe100159f02096d70a1e9a90cc61cee5d3300e8c8af739dcc316053698
    etiquetas-COPIA-IDENTICA.json      836 B  sha256 bf72272aa88837f81517f32d07958dee2c9c038f0dcd89b1c87229177d112dc0
    protocolo-COPIA-IDENTICA.json    1.311 B  sha256 fa327b5887ac36cdb2b225724499c62be6a4ba6b673618b8147d26bfb06a442d
    01-gap-de-contrato.md
    02-material-muestra-y-umbrales.md
    03-aislado-y-wiring.md
    04-reinvestigacion-alerta-wiring-2026-09-30.md    <- anadido el mismo dia, rectifica a `03-`

Las tres copias son **identicas byte a byte** a las piezas originales del plan
(`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/{muestra,etiquetas,protocolo}.json`), que no se tocaron: los
sha de arriba son los de las tres fuentes leidas, y las copias se escribieron con `shutil.copyfile`. Si al
cerrar la tanda las originales mueven su sha, esta nota queda vencida y hay que re-copiar, no re-firmar.

**Pero el sha de disco no es el sha del blob, y hay que declararlo porque aqui se publican shas.** Medido
comparando `sha256` del archivo contra `git show HEAD:<ruta>`:

| Pieza | sha256 en disco (bytes / CR) | sha256 del blob en `HEAD` (bytes / CR) |
|---|---|---|
| `muestra.json` | `1abfaafe100159f02096d70a1e9a90cc61cee5d3300e8c8af739dcc316053698` (2.651 B / 64 CR) | `ba14df1244d2492a5e1cf142b8a10af6e174ef995b02b22e38244c227833d51a` (2.587 B / 0 CR) |
| `etiquetas.json` | `bf72272aa88837f81517f32d07958dee2c9c038f0dcd89b1c87229177d112dc0` (836 B / 33 CR) | `276bda1b114ed71db3c2116fb35f4fd92d1905079fa9fa6f3d0cc48b913c4a12` (803 B / 0 CR) |
| `protocolo.json` | `fa327b5887ac36cdb2b225724499c62be6a4ba6b673618b8147d26bfb06a442d` (1.311 B / 45 CR) | `654b37d212b902997c15827e5e618f0428537b73f797993791383f6752eec2e0` (1.266 B / 0 CR) |

Es el artefacto de `core.autocrlf` del clon, no un cambio de contenido: el arbol de trabajo esta en CRLF y el
repositorio en LF. Consecuencia directa sobre la decision de la fila 1 (D-B): si el operador elige la salida
(a) y se publica un sha de candidato, ese sha tiene que viajar **con su comando de medicion y su delimitador
declarado**, porque sobre estas tres piezas el mismo contenido da dos shas segun donde se lea. Y la nota
queda vencida en cuanto alguien normalice las originales: se re-mide, no se re-firma de memoria.

⟦**Nota fechada 2026-10-02 — la fila `tmp_test/` de §«Lo que queda pendiente» esta vencida en su mitad (c), y
los dos defectos que descubrio `04-` tampoco siguen abiertos.** No se re-escribe la fila: se declara aqui su
estado medido hoy. Crudo de todas las mediciones de esta nota:
`../PREPARACION-DECISION-2026-10-02/01-re-medicion-2026-10-02.txt`, cada salida con su comando literal encima.

**La salida (c), verificada con tres mediciones independientes** (no por cita):
1. `grep -n "^tmp_test/" .gitignore` → `28:tmp_test/`. **Correccion de atribucion, y es la que le falla al
   prompt que pidio esta nota**: esa declaracion **no es nueva del 2026-10-01**. Medido con
   `git log --date=short --format="%h %ad %s" -S"tmp_test" -- .gitignore` da `ede7fcb 2026-03-26 chore:
   Actualizar .gitignore para excluir test outputs y agent memory`, y
   `git log --since=2026-09-29 --date=short --format="%h %ad %s" -- .gitignore` da **0 lineas**. El
   `.gitignore` declara el aislado desde antes de que este plan existiera; el `git ls-files tmp_test` de la
   fila de arriba (**0 lineas**) ya lo decia.
2. `python scripts/run_all_validations.py --quick` → el check `[11/13]` Wiring publica
   `… | 684 excluidos por declaracion de Git | …` y el cierre `TOTAL: 13/13 validations passed`.
3. `python scripts/validate_wiring.py --check` → **EXIT 0** con
   `derivado: .opencode/wiring_report.json conforme con el calculo en memoria (digest 6a1e66b443f7…)`.
   Un cuarto dato, leido del informe escrito con destino explicito a `temp/` (nunca al versionado):
   `cobertura.excluidos_por_declaracion_git` es `{"cantidad": 684, "estado": "GIT_OK", "ejemplo":
   "tmp_test/venv-jev-sdk/…"}` sobre `schema_version 1.2`.

**Cuando se aplico realmente (c)**, medido con
`git log --date=short --format="%h %ad %s" -S"excluidos_por_declaracion_git" -- scripts/validate_wiring.py`:
`abd181c 2026-09-30 fix(scripts): el alcance del wiring se goberna por la declaracion del propio Git (paso 1,
salida (c))` y `0731741 2026-10-01 feat(wiring): adopta la cura del derivado versionado del agente suspendido
(schema 1.2)`; `git merge-base --is-ancestor` confirma que los dos son ancestros de HEAD. Los dos **fuera de
este plan**, en la orden de calidad del hermano. Con las horas del mismo comando
(`git show -s --format="%h %ci %s"`): `abd181c` a las 16:18:59 del 2026-09-30, mientras el mtime de **este
archivo** es 14:20 de ese dia. O sea que la fila (c) de la tabla de arriba nacio vigente y **quedo vencida el
mismo dia, dos horas y media despues de escribirse**; la fecha que le asignaba el prompt de esta sesion
(2026-10-01) le borra el paso 1. Las salidas (a) y (b) de esa misma fila siguen sin aplicarse, pero ya no
tienen rojo que apagar: el rojo que las motivaba ya lo apago (c).

**Defecto 1 de `04-` — «EXIT 0 del verificador con la clausula rota»: no se reproduce hoy.** Leido en el
codigo: `scripts/validate_wiring.py` define `_hallazgos_del_criterio`, que convierte los dos rojos de la
clausula de produccion (`HUECO_DE_COBERTURA_EN_PRODUCCION`, `VERDE_VACIO_SIN_GOBERNADOS_RESUELTOS`) en
hallazgos que `verificar()` devuelve como `viol`, y un `viol` no vacio retorna **EXIT 1 antes** de que el
`--check` opine sobre el derivado. La cura es `5145173 2026-09-30 fix(scripts): la clausula de produccion del
wiring se codifica en el EXIT (paso 2)` (ancestro de HEAD) y su bateria esta versionada:
`git ls-files tests | grep -E "criterio_en_el_exit"` → `tests/test_validate_wiring_criterio_en_el_exit.py`.
Poblacion de hoy: `cobertura.receptores_no_resueltos_en_produccion` = **0**, y el filtro directo sobre
`poblacion` (`clasificacion == RECEPTOR_NO_RESUELTO` y `en_tests` falso) da **0** — dos lecturas del mismo
informe, no una cita. **Limite declarado de esta nota**: no se corrio un mutante, porque esta sesion no
puede escribir en `scripts/**`; el contrafactual lo prueba la bateria versionada, no esta re-medicion, y un
verde de hoy sobre una poblacion con cero huecos de produccion no afirma que la clausula muerda.

**Defecto 2 de `04-` — «el informe versionado esta vencido sin instrumento que lo corte»: curado.** La bandera
existe desde `fbfdc57 2026-09-30 feat(scripts): el derivado versionado del wiring se contra-verifica con
--check (paso 3)` (ancestro de HEAD), corre dentro del rapido en `[11/13]`, y su lectura de hoy es CONFORME
con digest impreso; su bateria `tests/test_validate_wiring_check_derivado_versionado.py` esta versionada.
**Lo que de `04-` sigue vigente y no se cura aqui**: la nota de instrumento del §«Nota de instrumento» de
arriba —el `const` de `--write-report` sigue apuntando al informe versionado, y correrla sin argumento
destino sigue re-escribiendolo.

**Dueno**: la fila original sigue siendo del dueno de `scripts/validate_wiring.py` y del registro `33-` del
hermano. Esta nota no la borra ni la re-escribe: declara que el 2026-10-02, sobre HEAD `ed44c51`, la salida
(c) esta aplicada y verificada por tres mediciones, y que los dos defectos de `04-` no sobreviven a la
re-medicion.⟧

