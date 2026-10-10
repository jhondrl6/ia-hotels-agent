# AC7 — Diagnostico medido del control S15 (FASE-B, 2026-10-09)

**HEAD de esta sesion:** `77e64ca94158266e9ed6c95836cf04c3dc718112` (medido con `git rev-parse HEAD`,
`git rev-parse origin/master` y `git ls-remote origin refs/heads/master`, los tres iguales).
**Instrumento del control negativo:** `6b02532:scripts/build_lesson_index.py`, 20.223 B,
`sha256=6442305f22296dcf…` (lee el blob con `git show`, no reimplementa el defecto).
**Interprete de las corridas:** `./venv/Scripts/python.exe` (Python 3.13.3). Crudos: `01-diagnostico-crudo.txt`,
`02-h2-crlf-del-clon.txt`. Arneses: `temp/s15_diag_faseb_ac7.py`, `temp/s15_diag_faseb_h2.py` (scratch de la
sesion, **no** versionados; el contrato prohibe `.py` bajo `evidence/`).

## 1. Lo que pierde y por que (la causa confirmada)

`test_el_control_defectuoso_de_la_revision_publicada_si_diverge` pierde en `:210` con la firma exacta que
traia el mandato (`'mtime' == 'mtime'` y luego `'nombre' == 'mtime'`). Reproducido contra el HEAD de esta
sesion: **1 failed / 3 passed, EXIT=1** (`tests_baseline_pre.txt`). Las otras tres funciones del archivo estan
verdes, incluido el corte positivo `test_dos_checkouts_con_mtimos_distintos_publican_bytes_identicos`.

La causa es la **hipotesis 1: el reloj del fixture contra el piso de fechas del corpus**. Mecanismo medido,
no supuesto:

- `_plan_date()` de `6b02532` devuelve la fecha del nombre del dueno y, si el nombre no la trae,
  `max(mtime)` formateada (`st_mtime`, linea 112 del blob).
- `build()` de esa revision ordena las definiciones de un ID con clave
  `(_plan_date(...)[0], plan)` y toma `ordered[0]`: **gana la fecha mas antigua**. El tier `mtime` participa
  del desempate de **duenio**, no solo del de la fecha.
- El fixture estampaba `MTO_A = 2020-01-02` y `MTO_B = 2031-06-06`. Medido sobre el corpus del clon: la fecha
  mas antigua que aparece en el nombre de un dueno es **2026-07-06** y la mas reciente **2026-10-09**
  (`01-diagnostico-crudo.txt`, seccion M2; 48 duenos con fecha en el nombre sobre 72).
- En el arbol A, el `mtime` 2020 queda por debajo de todo dueno cerrado y conserva el duenio: sale
  `fuente_fecha = mtime`. En el arbol B, el `mtime` 2031 queda **por encima de todo** el corpus, pierde el
  desempate y el duenio pasa a un plan cerrado: `fuente_fecha = nombre`. La asercion exige `mtime` en los dos
  arboles, asi que el rojo es correcto en su forma y falso en su premisa: **el fixture pidio que el defecto se
  manifestara solo como fecha, y le dio un reloj que lo manifiesta tambien como inversion de duenio**.

Consecuencia que el mandato no escribia: la inversion de duenio **es el mismo defecto de `mtime`**, visto por la
otra cara (el desempate de autoria tambien consume la fecha del reloj). No es un segundo bug ni un entorno
roto; por eso la cura goberna el reloj del fixture y no la asercion.

## 2. Banda de IDs divergentes contra el HEAD de esta sesion

Medida con el par literal del fixture (`2020-01-02` / `2031-06-06`) sobre el corpus de `77e64ca`, con el
generador de `6b02532` en los dos arboles. **11 IDs divergentes**, 7 de ellos por inversion de duenio:

| ID | arbol A | arbol B | firma |
|---|---|---|---|
| S-1 | `mtime 2020-01-02`, duenio `context/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL` | `nombre 2026-09-20`, duenio `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` | inversion de duenio |
| S-2 | idem A | `nombre 2026-09-20` `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` | inversion de duenio |
| S-3 | idem A | idem B | inversion de duenio |
| S-4 | idem A | idem B | inversion de duenio |
| S-5 | idem A | idem B | inversion de duenio |
| S-6 | idem A | idem B | inversion de duenio |
| S-7 | idem A | idem B | inversion de duenio |
| S-8 | `mtime 2020-01-02` `context/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL` | `mtime 2031-06-06`, mismo duenio | solo la fecha (lo que la asercion afirma) |
| S-9 | idem | idem | solo la fecha |
| S-10 | `mtime 2020-01-02` `context/CONTEXT-DT-3-TECH-DEBT-POST-DT2` | `mtime 2031-06-06`, mismo duenio | solo la fecha |
| S-11 | idem | idem | solo la fecha |

Los tres duenos que compiten por `S-1` estan listados en la seccion M6 del crudo:
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20/10-analisis-post-implementacion.md` (seccion `F. Deuda y seguimientos con
duenio`), `context/CONTEXT-DT-2-DELIVERY-CONTRACT-RESIDUAL.md` (seccion 5) y
`context/CONTEXT-DT-3-TECH-DEBT-POST-DT2.md` (seccion 6).

**Banda con el reloj gobernado** (par derivado: `2026-07-04` / `2026-07-05`, ambos bajo el piso): 11 divergentes,
`fuentes = ['mtime']`, los 11 por **solo la fecha**, y `S-1` y `S-11` siguen en la banda — que es lo que exige la
ultima asercion del control.

## 3. Hipotesis descartadas, con su medicion

**Hipotesis 2 (entorno del clon: CRLF / `autocrlf` / `longpaths` / ruta que no materializa) — DESCARTADA como
causa, CONFIRMADA como premisa falsa del fixture.** Medido dentro del clon: `core.autocrlf = 'true'` y
`core.longpaths` sin valor (`rc=1`). Las banderas `-c core.autocrlf=input -c core.longpaths=true` que el fixture
pasaba a `git clone` **no persisten**: el `git checkout` corre despues, dentro del clon, y lee la config del clon,
que hereda el `true` del ambito *system* de Windows. Los 438 `.md` del corpus materializado divergen de su blob de
HEAD (ejemplo medido: `CONTEXT-DT-2-…md` 24.149 B en disco contra 23.622 B commiteados, `sha` distinto). Es
exactamente la trampa S20 que `scripts/verify_index_in_committed_tree.py::clon_fiel` ya gobierna fijando la config
**dentro** del clon; el fixture de S15 no lo hacia. Que no es la causa se midio comparando el indice publicado
por el generador curado en dos arboles del mismo commit — receta actual (CRLF) contra patron S20 (LF): JSON
identico (`sha256 ace923719d40d883…`), MD identico (`ced6fce8b6b95643…`), **0** entradas con tier/fecha/duenio
distintos y la misma distribucion de tiers (`nombre=361 commit=11`). El verde del control no dependia del CRLF,
pero su docstring afirmaba un arbol fiel que no existia: se cura con la receta S20 y su diente.

**Hipotesis 3 (cambio de poblacion del corpus: archivado del padre y regeneracion del par del indice) —
DESCARTADA.** La banda se re-midio contra las dos revisiones del antecedente, materializadas por clon con
`git checkout <rev> -- .opencode/plans .opencode/context` y el mismo blob defectuoso: `98c190e` → 348 IDs,
**11 divergentes, 7 inversiones de duenio, piso 2026-07-06**; `086ce65` → **los mismos 11 con la misma firma y el
mismo piso**. El competidor que gana el duenio en B (`VERIFICADOR-ESCRITURA-QMIND-2026-09-20`, fila de su §F) ya
existia en `086ce65`. Por tanto la medicion del mandato (2026-10-07) **no** describe un cambio de poblacion
posterior: describe el mismo estado que encuentra esta sesion. La medicion propia de FASE-B es la de la seccion 2
de este archivo, tomada contra `77e64ca`, y la del mandato queda como antecedente referenciado, no como resultado.

## 4. Estado de la abstencion

El fixture ahora separa los tres estados (R2.9): ruta que no materializa → `NO-EVALUABLE` con la ruta nombrada y
**sin** la palabra divergencia (diente `test_el_clon_que_no_materializa_declara_no_evaluable_con_la_ruta`, con su
corte positivo sobre el arbol real); corpus sin duenos fechados → `NO-EVALUABLE` con el criterio buscado
(`_piso_y_techo`); arbol del clon que no casa con su blob → `NO-EVALUABLE` con la diferencia de bytes. Ninguno de
los tres colapsa en verde ni en «divergencia hallada».

## 5. Donde cae la cura: fixture, no generador

**La cura NO esta en `_plan_date`/`build()`** — no hace falta tocarlos: con el reloj del fixture derivado del piso
del corpus, la divergencia que produce el generador de `6b02532` es exactamente la fecha de `mtime` en los dos
arboles (medido en la seccion 2, 11 de 11), que es la propiedad que el control afirma. Por eso **FASE-C (AC9)
queda en «no aplica»** y no tiene mandato (su regla exige la frase «la cura esta en `_plan_date`/`build()`
porque <razon medida>», y esa razon no se obtuvo). `scripts/build_lesson_index.py` no se edito en esta fase
(medido: `git diff --stat` vacio sobre la ruta).
