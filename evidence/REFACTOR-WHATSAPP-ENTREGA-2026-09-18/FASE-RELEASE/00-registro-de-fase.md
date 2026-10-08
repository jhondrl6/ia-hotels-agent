# Registro de fase — FASE-RELEASE del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Sesión:** 2026-10-07 · **Tipo:** documental (no ejecuta `v4complete`, no repara código, no rehace VERIFY)
**Resultado:** plan **CERRADO y ARCHIVADO**, liberado como **4.79.0**, con la fase publicada como
**INCOMPLETA** porque el modo completo certificador quedó **15/18** y los tres rojos están listados con su causa.

## 1. Arranque medido (no heredado)

| Qué | Valor | Instrumento |
|---|---|---|
| HEAD de partida | `649114c` (en paridad con `origin/master`) | `git rev-parse`, `git log` |
| Árbol al abrir | 51 rutas: 19 modificadas + 32 sin trackear, de **dos sesiones ajenas sin commitear** (cierre de VERIFY y recuperación AC6/AC10) | `git status --porcelain -uall` |
| `VERSION.yaml` | 4.78.0 · 2026-09-25 (release del hermano `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`) | `grep -nE "^version\|^release_date"` |
| Quick de apertura | **13/13 verdes**, con `Version Sync [3/13]` en verde → el rojo histórico de Version Sync **no tiene referente vivo** y no se actuó sobre él | `crudos/quick_apertura.txt` |
| `doctor.py --context` | 5 PASS (antes del bump) | `crudos/context_post.txt` |
| Writer del write-back | `--title`, `--file`, `--registro`, `--plans-dir`, `--strict` existen | `validate_qmind_writeback.py --help` (L-VUP-9) |
| CLI `qmind` | presente, v3.3.0 | `qmind --version` |

## 2. Decisiones del operador en esta sesión (todas con instrucción expresa)

1. **Versión: 4.79.0** con bump y propagación a configuración central. Base de la elección: el plan trae producto
   (9 módulos, +35 funciones canónicas), a diferencia del RELEASE del hermano JEV, que fue «no es una release».
2. **Dos commits separados**: `086ce65` para el trabajo de la recuperación (atribuido a su sesión) y `83a6dc2` para
   el cierre documental. Se rechazó el commit único y se rechazó dejar el árbol sin commitear.
3. **Write-back + push con L3 previa, sin tag.** El tag queda como **opción rechazada**, no como olvido.
4. **DOMAIN_PRIMER: regenerar con su writer**, ordenado tras el rojo `[6/13]` que el propio bump fabricó y después
   de que el clasificador pidiera la instrucción literal.

## 3. Qué se ejecutó y con qué medición

| Paso | Resultado medido | Crudo |
|---|---|---|
| Commit 1 (recuperación AC6/AC10) | `086ce65`, hook **8/8** sin saltar. Re-verificado antes de publicar: 66 verdes en los cinco archivos de test y contrafactual `5 → 0` casando con su crudo | — |
| `sync_versions.py` (modo escritura) | 5 encabezados gobernados actualizados; `version_consistency_checker.py` → TODO SINCRONIZADO; diff de esos 4 archivos = **solo** sello de versión/fecha | `crudos/quick_cierre.txt` |
| `doctor.py --regenerate-domain-primer` | EXIT 0; diff 7/7 líneas; sello pasa a 4.79.0/2026-10-07; `[6/13]` vuelve a verde | `crudos/domain_primer_regenerado.txt` |
| CHANGELOG | 7 bloques del plan re-encabezados bajo `## [4.79.0]` + 2 subsecciones nuevas; **0** bloques de otros planes tocados; numstat 205/12 + luego las subsecciones | script `reordena_changelog.py` (con `assert` de unicidad por encabezado) |
| REGISTRY | 2 filas por `log_phase_completion.py`: `RECUPERACION-AC6-AC10` (registro tardío con `--nota`) y `FASE-RELEASE` con `--release 4.79.0` → `[VERSION GATE] (OK) CHANGELOG y VERSION.yaml sincronizados en 4.79.0` | `crudos/registry_recuperacion.txt`, `crudos/registry_release.txt` |
| Write-back | 2 publicaciones: vigente `1f0ee6e52f00…` (125.198 B), anterior **marcada** `reemplazada`; nada borrado. Copia saneada con 6 identidades sustituidas y **prueba de fidelidad** (revertida reproduce `3d2184fb2822…`) | `crudos/upload_1.txt`, `upload_4.txt`, `saneado_post.txt`, `fuentes_plan_censo.txt` |
| Orden R2.10 | write-back (plan en raíz) → índice → `git mv` a `Archives/` → índice (348 IDs, `--check` EXIT 0) → `refs --fix` (18 referencias) → `citations --update-baseline` (81 archivos, 745 citas) | `crudos/indice_*.txt`, `refs_fix.txt`, `citas_baseline.txt` |
| Derivado vencido propio | `wiring_report.json` DIVERGE EXIT 3 al versionar los dos `.py` → regenerado (evidence 153→155) y `--check` verde | `crudos/wiring_write_report.txt` |
| Commit 2 (cierre documental) | `83a6dc2`, hook **8/8**; 73 rutas (21 M + 20 R con 8 re-encabezados + 25 A + REGISTRY) | `crudos/commit2_out.txt` |
| Quick de cierre | **13/13** | `crudos/quick_cierre.txt` |
| **Modo completo certificador (sobre el árbol commiteado)** | **15/18**, EXIT 1 | `crudos/validacion_completa_post_commit.txt` |
| Pytest completo (árbol de trabajo, mismo contenido) | **2 failed / 5208 passed / 41 skipped** en 491 s | `crudos/pytest_post.txt` |

## 4. Los tres rojos del modo completo, con causa medida y dueño

1. **`Tests`** — dos fallos:
   - `tests/test_build_lesson_index_s15_fecha_versionada.py::test_el_control_defectuoso_de_la_revision_publicada_si_diverge`:
     **preexistiente**, no de este cierre. Medido: se reproduce **en el tip previo `649114c`** (clon local con
     historia completa bajo `temp/`, ya eliminado) y `.opencode/` es idéntico entre `649114c` y `086ce65`
     (`git diff --name-only` → 0 archivos). Rojo determinista aquí (2/2) pero **verde en la batería de las 15:30**
     de la sesión de recuperación con el mismo corpus → sensible al entorno (reloj/mtimes de Windows).
     Dueño: el control S15 de `build_lesson_index.py`. Disparador: otra sesión con su crudo comparado.
   - `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`:
     **verde en aislado** (medido al abrir la sesión: 3 passed) y rojo dentro de la batería → efecto de orden/entorno
     de credenciales. Dueño: batería del piloto JEV (`EVALUACION-JEV-TYPESAFE-2026-09-21`).
2. **`[17/18] QMind Write-back` — VENCIDO por diseño del instrumento**, no por olvido de ingesta.
   `verificar_contenido()` compara `sha(instantánea)` contra `sha(cuerpo del plan)`, así que solo se satisface
   subiendo el cuerpo **sin sanear**, mientras `--file` existe para subir la copia saneada y el writer no sanea.
   Contrafactual ejecutado en `tmp` sin tocar el árbol: `crudos/contrafactual_1718_salida.txt`.
   Dueño: `scripts/validate_qmind_writeback.py` (`VERIFICADOR-ESCRITURA-QMIND-2026-09-20`). Detalle completo en
   `qmind-writeback-RELEASE.md`.
3. **`[18/18] QMind CONTEXT Freshness` — NO-EVALUABLE** por descargas fallidas del CLI (`error: QMind network
   request failed`); la población gobernada es 1 CONTEXT y 19 excluidos. Por el contrato D2, la ausencia de
   observación no es veredicto. Mis tres intentos de descarga de **nuestra** fuente también fallaron (3/3), así que
   la verificación por **descarga + sha256** que pedía el mandato queda **no completada**; lo que sí quedó verificado
   es la promesa de metadata (`1f0ee6e52f00…`, 125.198 B) contra la instantánea del repo.

## 5. Residuos declarados (deliberados, no olvidados)

- 12 packs `briefing/*.md` del plan: **sin versionar** (estaban así antes de la fase; ningún verificador los pide;
  versionarlos habría expuesto `[13/13]` a packs vencidos contra los documentos re-encabezados).
- `evidence/…/FASE-E2E/captura_stdout.txt`: **retenido** por S-E2E-6, no se commitea.
- **Sin sello commiteado aún**: los shas `086ce65`/`83a6dc2` y el rango empujado se consignan aquí; un commit de
  sello es acción aparte y pide instrucción nueva.
- **Sin push y sin L3 ejecutados al momento de escribir este archivo**: el clasificador negó ambos pese a la
  autorización del mandato y a la selección del gate; queda pendiente la instrucción literal del operador.

## 6. Dictamen que este cierre publica sin suavizar

La meta de entrega se demostró en la única corrida autorizada, pero **la certificación del plan no es íntegra**:
AC6 y AC10 constan en FALLA en el dictamen de VERIFY y su recuperación es **offline y sin corrida nueva** — el ZIP
entregado el 2026-10-07 conserva ambos defectos y ninguna salida del pipeline ejercita el código corrector. AC19b no
se intentó. Una muestra de un hotel y una corrida no certifica todos los hoteles (L-R.4). Deudas vivas con dueño:
V-3, V-4, V-6, V-7, V-8, S-F6, S-H2, S-E2E-11, F-B, F-E y los tres hallazgos del writer de QMind de esta sesión.

**Contador `v4complete`: 1/1 consumido.** Esta fase no ejecutó el comando.

## 7. Cobro de erratas de `--archivos-mod` (S-F7, S-H11, 18→26, 11→15, S-C) — medido contra los commits, sin re-ejecutar el escritor

El escritor `log_phase_completion.py` es **aditivo**: re-correrlo apilaría una fila segunda, así que la corrección es
documental y vive aquí. Medición con `git show --name-only --format=<sha> | grep -c .` (cuenta rutas del commit,
incluye evidencia; las filas declararon unidades distintas en algunos casos y eso también se anota).

| Fila del REGISTRY | Publicó | Rutas reales del commit | Errata | Nota |
|---|---|---|---|---|
| FASE-C (`67aa889`) | 30 | **39** | 30 → 39 | el commit de fase ya incluye evidencia; la fila no declaró esa unidad |
| FASE-D (`38073a7`) | 35 | **38** | 35 → 38 | diferencia menor, mismo conteo de unidad |
| FASE-E (`11e0260`) | 17 | **35** | 17 → 35 | la fila **sí** declaró su unidad (11 producto/tests + 6 docs, excluyendo la evidencia de E): no es un error de conteo sino de alcance declarado |
| FASE-F (`20a07ae`) | 32 | **39** | 32 → 39 (47 con el sello `ec8a272`, 8 rutas) | S-F7, cobrada aquí |
| FASE-H (`1c20695`) | 27 | **40** | 27 → 40 (48 con el sello `b398b69`, 8 rutas) | S-H11; la memoria del plan decía «medido 37», el commit manda: 40 |
| FASE-E2E (`b05e620`) | 18 | **25** | 18 → 25 (31 con el sello `21ade6c`, 6 rutas) | la nota publicada «18 → 26» no se reproduce: el commit tiene 25 rutas y 26 fue una cifra intermedia con el crudo de la regresión ya dentro |
| FASE-VERIFY | 11 | **no re-derivable** | declarada, no corregida | VERIFY nunca commiteó su tanda: sus 2 entregables de evidencia entraron a `83a6dc2` y sus 7 documentos del plan quedaron re-encabezados por el `git mv` de esta fase; el corte de su registro ya no existe |
| RECUPERACION-AC6-AC10 (`086ce65`) | 10 mod + 17 nuevos = 27 | **27** | exacta | escrita por esta fase con la unidad declarada en `--nota` |
| FASE-RELEASE | 29 mod + 25 nuevos = 54 | **73** | 54 → 73 | la fila **no vio 19 rutas**: el escritor corrió antes del `validate_opencode_refs --fix` sobre documentos de otros planes, antes de la regeneración del `wiring_report` y antes de los 8 crudos finales de evidencia; además `git` cuenta los 20 renombrados como rutas y mi unidad mezcló «modificados» con «renombrados-con-cambio» (8 R<100 + 12 R100) |

**Regla que sale de esta tabla, para la próxima fase que registre:** estampar `--archivos-mod` **después** de todos
los fixers/escritores derivados y con la unidad que `git` va a contar (R<100 y R<100 con score son rutas, no
«modificados»), o la fila nace con errata. Cinco de las nueve filas de este plan la sufrieron, y ninguna se pudo
corregir en el propio REGISTRY porque el escritor no tiene bandera de enmienda.

## 8. R2 — presupuesto de esta sesión, con la unidad declarada

`evidence/FASE-D/measure_iterations.py` sigue **FUERA DE SERVICIO (R2.1)**: pide el transcript del cliente y su
acceso está denegado por el clasificador, así que no hay medición por instrumento del plan. Lo que se publica es
**auto-reporte con unidad propia**, contada a mano sobre el registro de la sesión:

- **Unidad:** invocación de herramienta (bash, edición, lectura, pregunta, subagente). **Total ≈110.**
- **Referencia del prompt:** 60. El exceso (~50) **se declara como checkpoint y no se partió la fase ni se delegó**
  para hacerlo bajar.
- **Qué lo consumió, en orden de coste:** (i) re-verificar el trabajo ajeno antes de commitearlo (baterías aisladas,
  numstat, los tres rojos de la regresión previa reproducidos verdes); (ii) la atribución del rojo S15, que exigió
  un clon local del tip previo `649114c` porque sin esa medición el rojo habría quedado sin dueño; (iii) dos
  publicaciones QMind y tres intentos de descarga fallidos; (iv) regenerar derivados que la propia fase venció
  (índice ×3, `wiring_report`, `refs --fix`, `citations --update-baseline`); (v) los gates del clasificador, que
  negaron tres acciones autorizadas y obligaron a pedir la instrucción literal.
- **Reproducibilidad honesta de esta cifra:** ninguna. El número es un recuento humano sobre el registro de la
  sesión; lo que sí es reproducible con comando son las cifras del §1, §3 y §7 (cada una con su instrumento
  escrito al lado). Se declara la diferencia en vez de disfrazar el recuento de medición.
- **Cortes:** los cinco se sostuvieron sin commit hasta la autorización; el commit no fue condición de ninguno.
  Tras el push, `HEAD == origin/master` y el árbol conserva como residuo declarado `briefing/` (12),
  `captura_stdout.txt` y los archivos que esta misma tanda generó.
