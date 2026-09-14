# 10 — Análisis Post-Implementación: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

> **Creado desde la concepción** (executor §4, v2.11.0 en adelante): este archivo existía antes de la
> primera fase para que las lecciones no se escriban de memoria cuando ya se perdieron.
> **Advertencia de formato**: el check de cierre de planes (`[5/6]` del hook hoy, `[5/7]` tras la
> renumeración de FASE-V2, script `validate_plan_closure.py`) prohíbe que una **cabecera** de cierre
> afirme el cierre por completo mientras quede alguna fila `⬜ Pendiente` en el Resumen de Ejecución (§1).
> Al cerrar: actualizar §1 primero, y solo después titular la sección de cierre.

## 1. Resumen de Ejecución

| Fase | Fecha | Estado | Tests nuevos | Regresiones | Nota |
|------|-------|--------|--------------|-------------|------|
| Paso 0 | 2026-09-12 | ✅ | n/a | n/a | 10 consultas, 18 lecciones capitalizadas, 6 descartes, 5 hallazgos sin efecto |
| FASE-V1 | 2026-09-12 | ✅ | 0 | 0 | Q1–Q5 decididas con medición; contrato C0–C8 |
| FASE-V2 | 2026-09-12 | ✅ | 29 | 0 | script C0–C8 sin auto-fix, 13 detecciones con NR7, cableado `[7/7]` + `[9/9]`, conteo canónico 4.079 → 4.108 |
| FASE-V3 | 2026-09-12 | ✅ | 0 | 0 | template v1.1.0, executor v2.24.0, CHANGELOG sin bump, deuda (i) del predecesor cerrada, write-back + archivado en orden R2.10 |

## 2. Lecciones Aprendidas nuevas

Formato obligatorio: qué pasó / por qué / qué lo previene / pertinencia (INCLUIR o EXCLUIR).

| ID | Enunciado | Qué pasó | Por qué | Qué lo previene | Pertinencia |
|----|-----------|----------|---------|-----------------|-------------|
| L-V2.1 | Un test que solo mira **qué check** disparó puede quedar verde por una rama distinta de la que pretendía observar | El runner de NR7 mutó dos guards (C4a «ninguna fila nombra un AC» y C7a «la celda no es un ID») y sus tests siguieron en verde: otra rama del mismo check producía una violación con el mismo código | Los dos tests asertaban sobre `v.check`, una etiqueta compartida por varias detecciones. El verde no estaba midiendo la rama, medía el rótulo | Anclar la aserción al **mensaje** de la violación, no solo al identificador del check; el mutation check es lo que lo descubre, porque un verde sin rojo previo es sospechoso (L-VUP-5) | **INCLUIR** |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto generado por otro gate | C7/C8 necesitan el mapa `{ID → dueño}`. Leer `.opencode/lecciones_index.json` era lo obvio, pero ese archivo lo produce otro check (`[6/7]`): si ese gate no corrió —otro clon, hook no instalado— el verificador nuevo hereda un verde prestado | Un artefacto derivado solo es evidencia mientras su productor haya corrido, y el consumidor no tiene forma de saberlo desde el archivo | Calcular el índice en memoria con `build_lesson_index.build()` (0,30 s medidos) y fallar con nombre propio si el cálculo cae (`LECTOR-FALLIDO`) | **INCLUIR** |
| L-V2.3 | Una medición de seguridad sobre el artefacto equivocado deja pasar el rojo que pretendía descartar | Para renumerar el hook, Q10 midió «0 contract tests afirman el número de checks» buscando en `tests/` quién menciona `run_all_validations`. El riesgo real era la **numeración del hook**, y ahí sí había un contract test: `test_registrado_como_check_5_en_el_hook`, rojo y sin declarar desde `4a066e1`, que cambió `[5/5]` a `[5/6]` sin seguirlo | La búsqueda se hizo sobre el artefacto que tenía el número en la cabeza (el resumen de validaciones), no sobre el archivo que la fase iba a editar | Antes de cambiar un artefacto, grep de los tests que asertan **sobre ese artefacto**; y si un test pina una etiqueta de numeración, atarlo además a la coherencia interna de la numeración, no solo al valor literal | **INCLUIR** |
| L-V3.1 | Una documentación que describe un gate que no corre enseña a no verificarlo | Al actualizar los conteos de `docs/contributing/validation.md` se leyó su §13.3: «el gate se ejecuta automáticamente en el hook `agent-ecosystem` de pre-commit vía `run_all_validations.py --quick`». Medido: el hook activo es el versionado (`scripts/git_hooks/pre-commit`, 7 checks) y **no** invoca `run_all_validations.py`; `agent-ecosystem` pertenece a `.pre-commit-config.yaml`, que la propia decisión del 2026-08-29 declara «sin enforcement real» | La frase describe la intención del stack declarado, no el árbol instalado, y ningún check compara doc contra hook instalado | La documentación de enforcement se escribe contra el artefacto que corre (hook versionado + su instalador), y donde no hay automation se dice que no la hay | **INCLUIR** |
| L-V3.2 | Un gate que compara contra «hoy» no informa nada: su rojo y su verde son igualmente mudos | `--quick` dio **9/9** al cierre de FASE-V2 (2026-09-12) y **8/9** al reanudar la sesión el 2026-09-13 sin que se tocara ninguno de los archivos implicados. `[3/9] Version Sync` exige que cuatro cabeceras (`agents_version_comment`, `cursorrules_header`, `guia_tecnica_header`, `registry_last_update`) carryen la fecha que resuelve `sync_versions.py`, y como `VERSION.yaml` no define la clave `date` esa fecha sale de `datetime.now()` | La aserción compara contra una variable que muta sin intervención humana: el rojo no señala desincronización y el verde no certifica coherencia, así que el gate ocupa una posición bloqueante del suite sin aportar información | Un verificador compara contra un **hecho cerrado** —aquí ya existe en `VERSION.yaml`: `release_date`— y no contra el reloj; si la fecha «de hoy» es deliberada, el check no debe ser bloqueante en `--quick`. Registrado con dueño en **D-V3.1** | **INCLUIR** |
| L-V3.3 | Al archivar un plan se consume el testimonial con el que sus propios tests evitaban ser vacíos, y eso rompe la suite en el commit de cierre | El `git mv` de R2.5 sacó a este plan de `plans/` y, con él, al único `00-lecciones-capitalizadas.md` en alcance. `test_el_unico_artefacto_real_del_repo_pasa_todos_los_checks` exigía `pobo["alcance"]` no vacío y puso rojo con el artefacto intacto; el test hermano pineaba además una medición (el C6 del predecesor) que la propia fase acababa de invalidar al corregir ese §4 | Un test toma como garantía de no-vacuidad una **clasificación de alcance** que depende de dónde vive el archivo y de qué fecha declare, y no sobre el archivo mismo. Como R2.5 archiva todo plan que cierre, todo test así nace con fecha de caducidad = su propio cierre | La no-vacuidad se ancla al **artefacto** (recorrer `00-*` reales con `rglob`, vivo o archivado, y exigir `≥1` testigo), y una medición que la fase puede invalidar se escribe en el docstring como historia, no como aserción. Y antes de dar por buena una corrección documental, correr la suite de los tests que la miden | **INCLUIR** |

## 3. Matriz de verificación de ACs

| AC | Criterio (resumen) | Artefacto y clave | Estado | Cómo se leyó |
|----|--------------------|-------------------|--------|--------------|
| AC-A1…AC-A5 | decisiones Q1–Q5 | `evidence/FASE-V1/decision-verificador.md` | ✅ | lectura de las secciones `## Q1`…`## Q5` |
| AC-B1…AC-B5 | script, tests, NR7, cableado, cobertura | `evidence/FASE-V2/` | ✅ | B1 `--help` sin `--fix` + hash del artefacto inalterado tras una corrida con violaciones (`test_b1_sin_fix_y_sin_reescribir_los_artefactos`); B2 29 tests nombrados por su causa, tres estados cubiertos; B3 `nr7-<id>-{rojo,verde}.txt` × 13; B4 `hook-bloquea.txt` con `exit_code_del_hook=1` y la línea `[9/9] Lesson Capitalization` en `--quick` 9/9; B5 línea `cobertura:` con los cuatro conteos |
| AC-C1, AC-C2 | docs sin fósiles y deuda cerrada | `git diff` de V3 + checklist del predecesor | ✅ | C1: template v1.1.0 y executor v2.24.0 nombran al verificador, con las **5** referencias normativas al `[6/6]` actualizadas a `[6/7]` y las **4** mediciones históricas conservadas literales (verificable con `grep -n "\[6/6\]" .agents/workflows/phased_project_executor.md`). C2: ítem (i) de §Deuda del predecesor pasado a `[x]` con fecha, commit y cobertura medida |

## 4. Métricas de Ejecución

- Población a la que aplica el verificador: **1** plan en alcance de **27** directorios
  (25 archivados excluidos por regla, 1 exento por fecha anterior al corte, 0 sin fecha).
- Cobertura publicada por el script en su propia salida: línea `cobertura:` con los cuatro
  conteos y los nombres de los exentos (AC-B5).
- Funciones de test canónicas: **4.079** pre → **4.108** post (par en
  `evidence/FASE-V2/baseline-pre-post.md`, resta = 29 = tests nuevos de V2).
- Checks del hook: **6** → **7**. Checks de `--quick`: **8** → **9**.
- Detecciones con mutation check (NR7): **13** de 13, con sus dos salidas.
- **Al cierre de FASE-V3 (2026-09-13)**: medición canónica vigente **4.108** funciones en **295**
  archivos `test_*.py` (825 en `tests/*.py`, 573 en `tests/quality_gates/`). La cifra publicada
  **4.063** tiene **7** menciones vivas (`AGENTS.md` ×4, `CHANGELOG.md` ×1, `REGISTRY.md` ×2) más
  **3** registros archivados que **no** se reescriben por ser medición congelada. No se parchea a
  mano en este cierre: eso es exactamente lo que denuncia **S-V2.1** (un dato publicado sin writer),
  y el parche manual dejaría de servir a la próxima fase que añada un test.

## 5. Seguimientos abiertos detectados

- **S-V2.1 — el conteo canónico de `AGENTS.md` va 16 funciones por detrás del árbol**: la
  tabla de cobertura por módulo publica **4.063** funciones (medición de v4.76.0) y el
  conteo real antes de esta fase era **4.079**. Mismo mecanismo que L-R.2 (un dato publicado
  sin writer ni verificador): `sync_versions.py` sincroniza versiones, no conteos de tests.
  **Dueño**: el cierre documental que toque `AGENTS.md` después de esta fase; **no** se
  maquilla en este commit porque el número cambiaría otra vez al cerrar V2 (4.108).
- **D-V2.1 — el instrumento canónico de R2.1 no alcanza el transcript de sesión bajo el
  cliente actual**: ver `06-checklist-implementacion.md` §Deuda.
- **D-V3.1 — `[3/9] Version Sync` compara las cabeceras contra `datetime.now()`**: se puso rojo
  solo por avanzar el calendario (9/9 → 8/9 sin tocar los archivos). Dueño: quien mantenga
  `sync_versions.py`; la regla general está escrita como **L-V3.2** en el §2.
- Resto de deuda registrada en `06-checklist-implementacion.md` §Deuda: promoción a R2.11,
  verificador de conteos declarados en §4, prompts de fase contra §2 del `00-`, y migración
  del `[7/7]` si se activa la Opción 2 del pre-commit.

## 6. Decisiones Arquitectónicas

| ID | Decisión | Alternativas rechazadas y por qué |
|----|----------|-----------------------------------|
| DA-V1 | Alcance **hacia delante por fecha** del nombre del plan (`≥ 2026-09-12`), con `Archives/` fuera y los exentos listados en la salida | *Baseline de exentos* (estilo `plan_citations_baseline.json`): cada plan nuevo exigiría editar un JSON y un baseline mal mantenido exonera en silencio. *Todos los planes*: 25 fallos permanentes, que es el ruido que aprende a ignorarse (L-HF1). Medido: con el corte entran 0 archivados y 1 plan real |
| DA-V2 | **Doble cableado**: `[7/7]` del hook versionado y `[9/9]` de `--quick` | *Solo hook*: no corre en un clon donde nadie ejecutó `install_git_hooks.py` — el mismo límite de entorno que R2.6 midió con su baseline fuera del repo. *Solo `--quick`*: depende de que alguien lo ejecute, que es la disciplina manual que el plan vino a quitar. *.pre-commit-config.yaml*: rechazado con el dato, ese archivo declara 13 hooks sin enforcement y su propia decisión del 2026-08-29 mantiene vigente el hook custom |
| DA-V3 | El verificador **calcula el índice en memoria** (`build_lesson_index.build()`) en vez de leer `.opencode/lecciones_index.json` | Leer el JSON era lo obvio y más barato, pero ese archivo lo mantiene fresco otro gate: fiarle la conclusión al artefacto de otro verificador produce un verde prestado (L-V2.2). Coste medido de la alternativa elegida: 0,30 s |
| DA-V4 | Los checks se escriben sobre la **propiedad**, no sobre la forma de la fila: `C4` exige AC existente en el maestro y `C7/C8` dueño real y ≥2 fuentes | Un check de presencia de texto («la fila no está vacía») habría dado verde al artefacto del predecesor y a cualquiera ceremonial. Medido en FASE-V2 con `--cutoff 2026-09-11` sobre el artefacto humano del predecesor: 18/18 atribuciones correctas y **una** violación genuina (C6, su §4 declaraba que el verificador no existía) — listón ni inflado ni decorativo (L-D3, L-HF1). **Desenlace en FASE-V3**: ese §4 se corrigió, la violación dejó de existir y el test que la pineaba como medición se reescribió (**L-V3.3**) |

## 7. Cierre del plan

El plan queda **COMPLETADO** el **2026-09-13** (V1 y V2 cerraron el 2026-09-12; el cierre documental y
el archivado de V3 se ejecutaron al día siguiente), sin bump de versión (decisión Q5; `4.77.0` sigue
reservado por `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`).

- AC-A1…AC-A5, AC-B1…AC-B5, AC-C1 y AC-C2 leídos en su artefacto (R2.4), sin ⚠️ abiertos.
- NR7 (R2.8) cumplido por detección: 13 de 13, con el par rojo/verde en `evidence/FASE-V2/`, y
  **recertificado 13/13 en el corte de cierre** sobre el script vigente.
- R2.9 (NR8) aplicado al propio verificador: `SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO` con test propio cada uno.
- NR1 con la resta de R2.7 verificada en las dos bases (`29 = 29`) y el flaky declarado.
- R2.2: 0 citas de línea nuevas; `--quick` 9/9 y suite con los 3 rojos ajenos ya publicados.
- Write-back de QMind ejecutado **antes** del `git mv` y el índice regenerado en los dos puntos del orden (R2.10).
- **Dos tests de V2 los rompió este cierre, no un defecto ajeno**: archivar el plan consumió el
  testimonial con el que evitaban ser vacíos. Reescritos anclando la no-vacuidad al artefacto y no a
  la clasificación de alcance (`29 passed`) → lección **L-V3.3**, medición en
  `evidence/FASE-V3/cierre-y-orden-R2.10.md` §5.
- **Estado del gate al cerrar**: población **0** planes en alcance (este plan ya está archivado y el
  predecesor está exento por fecha). Su verde hasta el próximo plan bajo v2.24.0 significa
  «no hay nada que mirar», y la línea `cobertura:` lo publica en cada corrida.
- Deuda heredada cerrada con dueño (ítem (i) del predecesor) y deuda nueva registrada con dueño:
  D-V2.1, S-V2.1, D-V3.1, R2.11, verificador de conteos declarados, prompts de fase vs §2 y migración del
  `[7/7]` si se activa la Opción 2 del pre-commit.
- **Lo que este plan no hizo y dice por qué**: no promovió la norma a R2.11, no tocó `VERSION.yaml`,
  no tocó `main.py` ni `modules/`, y no empujó nada. Su verificador sigue sin poder evaluar la
  pertinencia, y así está escrito en su salida.
