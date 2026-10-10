# Acta de FASE-RELEASE — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-09)

**Plan:** `.opencode/plans/Archives/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/` (archivado en esta sesión, R2.5)
**Fase:** FASE-RELEASE (AC10) · **Versión dictada por el operador:** **4.80.0**
**HEAD al abrir:** `0f50ea4`, igual a `git ls-remote origin refs/heads/master` (paridad medida, no heredada)
**Árbol al cerrar:** **sin commit** — el operador autorizó «la subida de AC10 y la ejecución de la capa 2», y el
contrato reserva commit, L3 y push a instrucción literal propia de cada acción.

## Los cinco cortes, declarados

| Corte | Estado | Prueba |
|---|---|---|
| Implementación terminada | ✅ | AC10 publicada y verificada; documentación oficial convertida a 4.80.0 |
| Verificación terminada | ✅ | quick **13/13** con `EXIT=0` leído sin tubería; `--context`, integración y gobernanza en 0; POST 65 passed; **modo completo 16/18 con `EXIT=1`** (`11-modo_completo_crudo.txt`), con sus dos rojos atribuidos por medición en `13-atribucion_rojo_tests.txt` |
| Cierre documental | ✅ | 09 §A/§B/§D/§E, 06, README, dependencias, 00, CHANGELOG, GUIA_TECNICA, REGISTRY |
| Listo para revisión | ✅ | este acta + los 14 crudos del directorio |
| Espera de autorización | ✅ | commit / L3 / push no autorizados; el archivado queda como **rename staged** |

## AC10 — el plan se publicó a sí mismo con el writer curado

- **Paquete offline:** copia versionada `qmind-upload-10-analisis-cierre-4.80.0.md`, **byte-idéntica** al cuerpo
  (0 sustituciones por dictado del operador; la prueba inversa del conjunto vacío exige igualdad de sha256).
- **Publicación:** `--upload` + `--file` + `--title`, con el plan **aún en raíz** (R2.10). Banderas verificadas
  contra el `--help` del writer y del CLI antes de usarlas (L-VUP-9).
- **Registro (lo escribió el escritor):** cuarta entrada, schema 1.1, `fuente_id`
  `01a1239b-f8a2-7456-bbdb-f7d932a70b6e`, `sha_cuerpo` = `sha256` = `349b85c5b7a6f3e4e87d5d85dbe64c8b8de25d5c9d263ad8daa1ef46f0ffaef0`,
  40.970 B, instantánea con la huella **al final** del nombre (AC3).
- **Verificación por descarga + sha256:** racha **1/1**, byte-exacta (no por título, no por `SKIP`).
- **Dictamen del verificador:** `[FRESCO] CURA-INSTRUMENTOS-QMIND-S15-2026-10-07 :: ... promesa verificada por
  descarga+sha256`, y el `[CONTADOR]` pasó de `0 con fidelidad remota medida` a **`1`**
  (`2 dictaminada(s) por cuerpo, 1 con fidelidad remota medida, 1 NO-EVALUABLE por migracion, 2+1+0==3`).
- **Prueba de congelamiento:** tras el `git mv` y el `refs --fix`, el sha del cuerpo bajo `Archives/` sigue
  siendo el `sha_cuerpo` publicado. El archivado movió la ruta, no los bytes (AC5 ejercida por el caso real).

## Rojos que no se tapan, con dueño

| Rojo | Qué es | Dueño y disparador |
|---|---|---|
| `[FAIL] ... contenido: DUPLICADO-VIGENTE` (`--strict`, `EXIT=1`) | La fuente de la era G `01a0bfc9-5f5a…` nombra al padre y no está contable. **Hallazgo verdadero**, no regresión de esta fase | operador; se apaga solo por la vía (a) `vigente-historica` con autorización literal o por una decisión sobre contenido publicado (S-CIM-2) |
| `[18/18]` invocado sin `--strict` | Verde por ausencia del instrumento | S-CIM-1, **fuera de alcance por mandato** de este plan. Esta corrida lo imprimió **verde**: eso es el hueco de S-CIM-1, no una cura |
| `Tests` (modo completo, 16/18 con `EXIT=1`) | Rojo **heredado del padre** (S-CIM-8). **Excluido por medición que no lo introdujo esta fase:** la población que el `git mv` podía tocar —los **129** tests que leen `.opencode/plans` o `.opencode/context`— corre `129 passed` en el árbol final, y la selección literal del plan `65 passed` (`13-atribucion_rojo_tests.txt`). La causa exacta **no se nombra** aquí porque el crudo del runner recorta la salida de pytest a tres líneas y «and 7 more»; quedarse con ese recorte sería una prueba de ausencia cortada | operador / siguiente mandato sobre el check `Tests` del runner |
| Fidelidad remota del padre y del JEV en `NO-EVALUABLE` | Sus descargas fallaron en la corrida del verificador (CLI flaky, racha declarada) | S-CIM-8; la nuestra quedó medida por descarga |

## Yerros de esta sesión, escritos con su re-toma

1. **Encabezado borrado.** El Edit que insertó `## [4.80.0]` usó como ancla la línea `### FASE-B …` y no la
   re-emitió: la perdió. Medido (`sed -n '59,64p'`), restaurado por bytes y verificado. Es la trampa que ya está
   en la memoria del usuario.
2. **Arnés con escape truncado.** `temp/sello_release.py` llevaba `ra\u00ez` (truncado) → `SyntaxError` **antes**
   de cualquier escritura: `EXIT_SELO=1` y ningún documento tocado. Se corrigió el escape y volvió a correr.
3. **Backticks de la shell.** Un `python -c` con texto que contenía backticks y `$` fue interpretado por Git Bash
   (sustitución de comandos dentro del argumento): la deuda S-CIM-11 no se escribió en la primera intentona. Se
   llevó el arnés a archivo (`temp/deuda_slim11.py`). Lección: bajo Git Bash, el arnés documental va en archivo.
4. **`str` donde el instrumento pedía `Path`.** La primera prueba de descarga murió en `descargar_fuente()` con
   `AttributeError` **antes de tocar la red**; se declaró en el crudo y la re-toma casó byte-exacta en el intento 1.
5. **`EXIT=` leído del `tail`.** En el crudo de R2.10 los códigos salieron de la tubería, no del verificador
   (trampa propia ya documentada). Se re-midieron sin tubería: quick `EXIT=0`, `--strict` `EXIT=1`.
6. **S-CIM-11 (deuda nueva).** `log_phase_completion.py` toma `--archivos-mod` como lista de rutas separadas por
   comas y fabrica la columna «Cambio» desde el último segmento: pasarle prosa produjo dos rutas inventadas en el
   REGISTRY. La fila se re-escribió a mano **con errata visible dentro de la propia fila**, porque re-correr el
   escritor apilaría una entrada duplicada. Dueño: operador / siguiente mandato sobre los escritores documentales.

## Orden R2.10 ejecutado y probado

`--upload` (plan en raíz) → `build_lesson_index` → `git mv` a `Archives/` → `build_lesson_index` (publica la ruta
nueva) → `validate_opencode_refs.py --fix` (7 referencias reparadas, **ninguna** en el cuerpo congelado) →
`validate_plan_citations.py --update-baseline` (81 archivos, 745 citas; **acto visible declarado**) → quick.
Después del sello documental, el índice y las citas se volvieron a generar como **último paso** (374 IDs
definidos; `S-CIM-11` viaja como *citado sin definición*, estado explícito del escritor, no un rojo).

## Sello de la tanda «Git Commit + L3 + Push» (2026-10-09, despues de este acta)

El literal del operador llego al cerrar el corte documental y se ejecuto en el orden del contrato (commit → L3 → push):

- **Commit `ee28a50`** por **pathspec**, con 58 rutas: **14 renombradas** por el `git mv` del archivado, 14 modificadas y 30 nuevas de evidencia. Medido sobre el propio commit: **0 rutas ajenas dentro** y **0 archivos bajo `scripts/`, `tests/` o `modules/`**. Las 13 rutas staged del hermano REFACTOR-WHATSAPP (S-CIM-7) siguen staged y intactas, sin des-stagear.
- **El hook pre-commit no lo bloqueo**: la existencia del commit es la evidencia, y se declara que su stdout no se capturo en un crudo, asi que **no** se afirma el desglose por check de los ocho pasos.
- **L3 deep review sobre `0f50ea4..ee28a50`: 0 hallazgos.**
- **Push `0f50ea4..ee28a50`** con `EXIT=0`; paridad `origin/master..HEAD` = **0** y tip confirmado por `git ls-remote origin refs/heads/master` = `ee28a505e113dda7a7efa6129871c6d783afb581`.
- **Verificacion en el arbol del commit (L-VCF-15), ahora si hecha**: en un clon limpio de `ee28a50` (fuera del workspace, con `core.longpaths` y `core.autocrlf=input` dentro, y borrado despues) el cuerpo publicado sigue dando `349b85c5b7a6f3e4…` — o sea el commit no normalizo un byte del cuerpo, con `core.autocrlf=input` activo y **CR=0** en el archivo; el blob indexado y el blob de HEAD casan con el `sha_cuerpo` publicado. La seleccion literal re-corrida sobre el tip: **65 passed, `EXIT=0`** (el control S15 se autoclona HEAD, asi que esa corrida ejercita el arbol commiteado); quick **13/13 `EXIT=0`**; `--strict` **`EXIT=1`** con `[FRESCO]` de este plan y el rojo era-G declarado. Crudos `15-`, `15b-`, `15c-`, `15d-`, `16-`.
- **Yerro declarado de esta sub-tanda:** el primer clon de verificacion no traia interprete (el `venv/` esta excluido del repositorio), asi que la corrida de pytest dentro del clon no ocurrio y el fallback tampoco reso; se re-tomo la verificacion desde el worktree sobre el tip y seconserva la evidencia del sha en el clon. Tres archivos de 0 bytes (`**Total`, `**Ultima`, `**Version`) aparecieron en la raiz por el comando mangado de una tanda anterior (sustitucion de la shell dentro de un `python -c`): se borraron, eran de esta sesion, nunca estuvieron en el repo y su origen esta escrito en el crudo `13-`.
- **El sha de este sello no se estampa a si mismo**: lo cubre la primera corrida L3 de la siguiente tanda.

## Presupuesto (auto-reporte con unidad declarada)

**≈95 `tool_use` contados a mano sobre el transcript**, contra la referencia de **60** dictada por DA-CIM.10
para esta fase → **exceso declarado como CHECKPOINT**, no como segunda fase (cláusula del contrato §R2 intacta).
La unidad es `tool_use` de esta sesión; **no es comparable** con las corridas que usaron el instrumento canónico
`evidence/FASE-D/measure_iterations.py`, que sigue **FUERA DE SERVICIO** (pide el transcript del cliente y su
acceso está denegado; no se reintentó). En qué se fue: ≈17 lectura de mandato/contrato/executor/instrumento,
≈12 delegación read-only + inventarios, ≈4 versión y sync, ≈8 CHANGELOG/GUIA, ≈20 cuerpo+subida+verificación+R2.10,
≈18 sello documental y REGISTRY, ≈10 verificaciones, ≈12 **re-tomas por los seis yerros de arriba**.

## Lo que queda para quien commitee

1. Commit **por pathspec**, dejando fuera las 13 rutas staged del hermano REFACTOR-WHATSAPP (S-CIM-7), sin
   des-stagearlas (precedente de A3 y B).
2. **L3 y push** solo con literal propio; la L3 de esta tanda cubre desde `0f50ea4` hacia adelante, incluidos los
   sellos que quedaron sin revisar en sesiones anteriores.
3. Repetir la verificación sobre el **árbol del commit** (L-VCF-15): en esta sesión no existe porque no hubo commit.
4. `05-prompt-inicio-sesion-fase-RELEASE.md` ya no es reanudable: el plan está cerrado y archivado.
