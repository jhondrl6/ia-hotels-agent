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
| FASE-V3 | ⬜ | ⬜ Pendiente | 0 | ⬜ | cierre documental y archivado |

## 2. Lecciones Aprendidas nuevas

Formato obligatorio: qué pasó / por qué / qué lo previene / pertinencia (INCLUIR o EXCLUIR).

| ID | Enunciado | Qué pasó | Por qué | Qué lo previene | Pertinencia |
|----|-----------|----------|---------|-----------------|-------------|
| L-V2.1 | Un test que solo mira **qué check** disparó puede quedar verde por una rama distinta de la que pretendía observar | El runner de NR7 mutó dos guards (C4a «ninguna fila nombra un AC» y C7a «la celda no es un ID») y sus tests siguieron en verde: otra rama del mismo check producía una violación con el mismo código | Los dos tests asertaban sobre `v.check`, una etiqueta compartida por varias detecciones. El verde no estaba midiendo la rama, medía el rótulo | Anclar la aserción al **mensaje** de la violación, no solo al identificador del check; el mutation check es lo que lo descubre, porque un verde sin rojo previo es sospechoso (L-VUP-5) | **INCLUIR** |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto generado por otro gate | C7/C8 necesitan el mapa `{ID → dueño}`. Leer `.opencode/lecciones_index.json` era lo obvio, pero ese archivo lo produce otro check (`[6/7]`): si ese gate no corrió —otro clon, hook no instalado— el verificador nuevo hereda un verde prestado | Un artefacto derivado solo es evidencia mientras su productor haya corrido, y el consumidor no tiene forma de saberlo desde el archivo | Calcular el índice en memoria con `build_lesson_index.build()` (0,30 s medidos) y fallar con nombre propio si el cálculo cae (`LECTOR-FALLIDO`) | **INCLUIR** |
| L-V2.3 | Una medición de seguridad sobre el artefacto equivocado deja pasar el rojo que pretendía descartar | Para renumerar el hook, Q10 midió «0 contract tests afirman el número de checks» buscando en `tests/` quién menciona `run_all_validations`. El riesgo real era la **numeración del hook**, y ahí sí había un contract test: `test_registrado_como_check_5_en_el_hook`, rojo y sin declarar desde `4a066e1`, que cambió `[5/5]` a `[5/6]` sin seguirlo | La búsqueda se hizo sobre el artefacto que tenía el número en la cabeza (el resumen de validaciones), no sobre el archivo que la fase iba a editar | Antes de cambiar un artefacto, grep de los tests que asertan **sobre ese artefacto**; y si un test pina una etiqueta de numeración, atarlo además a la coherencia interna de la numeración, no solo al valor literal | **INCLUIR** |

## 3. Matriz de verificación de ACs

| AC | Criterio (resumen) | Artefacto y clave | Estado | Cómo se leyó |
|----|--------------------|-------------------|--------|--------------|
| AC-A1…AC-A5 | decisiones Q1–Q5 | `evidence/FASE-V1/decision-verificador.md` | ✅ | lectura de las secciones `## Q1`…`## Q5` |
| AC-B1…AC-B5 | script, tests, NR7, cableado, cobertura | `evidence/FASE-V2/` | ✅ | B1 `--help` sin `--fix` + hash del artefacto inalterado tras una corrida con violaciones (`test_b1_sin_fix_y_sin_reescribir_los_artefactos`); B2 29 tests nombrados por su causa, tres estados cubiertos; B3 `nr7-<id>-{rojo,verde}.txt` × 13; B4 `hook-bloquea.txt` con `exit_code_del_hook=1` y la línea `[9/9] Lesson Capitalization` en `--quick` 9/9; B5 línea `cobertura:` con los cuatro conteos |
| AC-C1, AC-C2 | docs sin fósiles y deuda cerrada | `git diff` de V3 + checklist del predecesor | ⬜ | — |

## 4. Métricas de Ejecución

- Población a la que aplica el verificador: **1** plan en alcance de **27** directorios
  (25 archivados excluidos por regla, 1 exento por fecha anterior al corte, 0 sin fecha).
- Cobertura publicada por el script en su propia salida: línea `cobertura:` con los cuatro
  conteos y los nombres de los exentos (AC-B5).
- Funciones de test canónicas: **4.079** pre → **4.108** post (par en
  `evidence/FASE-V2/baseline-pre-post.md`, resta = 29 = tests nuevos de V2).
- Checks del hook: **6** → **7**. Checks de `--quick`: **8** → **9**.
- Detecciones con mutation check (NR7): **13** de 13, con sus dos salidas.

## 5. Seguimientos abiertos detectados

- **S-V2.1 — el conteo canónico de `AGENTS.md` va 16 funciones por detrás del árbol**: la
  tabla de cobertura por módulo publica **4.063** funciones (medición de v4.76.0) y el
  conteo real antes de esta fase era **4.079**. Mismo mecanismo que L-R.2 (un dato publicado
  sin writer ni verificador): `sync_versions.py` sincroniza versiones, no conteos de tests.
  **Dueño**: el cierre documental que toque `AGENTS.md` después de esta fase; **no** se
  maquilla en este commit porque el número cambiaría otra vez al cerrar V2 (4.108).
- **D-V2.1 — el instrumento canónico de R2.1 no alcanza el transcript de sesión bajo el
  cliente actual**: ver `06-checklist-implementacion.md` §Deuda.
- Resto de deuda registrada en `06-checklist-implementacion.md` §Deuda: promoción a R2.11,
  verificador de conteos declarados en §4, prompts de fase contra §2 del `00-`, y migración
  del `[7/7]` si se activa la Opción 2 del pre-commit.

## 6. Decisiones Arquitectónicas

| ID | Decisión | Alternativas rechazadas y por qué |
|----|----------|-----------------------------------|
| ⬜ (rellena al cierre de V3) | | |
