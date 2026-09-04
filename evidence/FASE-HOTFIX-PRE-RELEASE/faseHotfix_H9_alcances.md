# FASE-HOTFIX-PRE-RELEASE / H9 — población medida por alcance, antes de elegir

Comando canonico (dejado **en el propio verificador**, docstring y clave
`comando_de_medicion` del baseline):

    grep -rEoh "[A-Za-z0-9_/]+\.py:[0-9]+" .opencode/plans --include=*.md | wc -l

## Mediciones (2026-09-04)

| # | Que mide el numero | Valor |
|---|--------------------|-------|
| 1 | citas `*.py:LINEA` en **todo** `.opencode/plans` (comando canonico, grep literal) | **723** |
| 2 | citas `*.py:LINEA` solo en `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | **381** *(el prompt de la sesion declaro 382 al medir; la reforma de AC8-b en H5 reescribio la fila del README que llevaba 2 citas y esta sesion no anadio ninguna — delta −1)* |
| 3 | inventario del **verificador** (misma regla pero multi-extension: py/md/yaml/yml/json/txt/html/csv/lock/toml/ini/sh/bat) | **738** en **78** archivos |

⚠️ **1 y 3 no son la misma cifra y no son comparables**: miden universos distintos
(solo `.py` vs todas las extensiones documentales). Es la regla R2.3 del executor
aplicada a si misma — antes de comparar dos numeros, decir cual mide cada uno. El
verificador usa la 3; el comando canonico reporta la 1.

## Los tres alcances que el prompt pidio medir

| Alcance | Medido | Veredicto |
|---------|--------|-----------|
| **(1) Hacia delante** — planes creados despues del verificador + portadores que las sesiones futuras leen (`05-prompt-*`, `01-plan-maestro.md`, `README.md`) | 387 citas viven hoy en portadores, **0** en planes posteriores al verificador (no existe ninguno: se creo el 2026-09-04) | **elegido** — un plan nuevo no introduce ninguna cita numerica |
| **(2) Delta** — baseline con el inventario actual, fallar solo si **sube** | inventario fijado en `.opencode/plans/plan_citations_baseline.json` (78 archivos / 738 citas) | **elegido** — coherente con DA-V2; no reescribe historia |
| **(3) Por seccion** — solo dentro de secciones de AC y de tareas de fase | **179 de 738** (24 %) caen en secciones de AC/tareas/fases; **559 (76 %)** en prosa historica | **descartado por la medida**: exigir «por seccion» habria dejado fuera el 76 % y, para alinearlo, habria que reescribir registro historico |

**Decision escrita antes de medir (recomendacion del prompt): (1) + (2) combinadas.
La medida no la desmintio: la confirmo.

## Propiedad verificada: el verificador se dispara

`tests/test_validate_plan_citations.py` (9 casos) fuerza el rojo con un fixture de
plan nuevo con 2 citas (`NUEVO con citas numericas (2)`), fuerza el rojo delta
(`CRECIO 2 -> 3`), y comprueba que **un archivo simbólico no dispara** y que el
verificador **no reescribe** el archivo culpable (prohibido auto-arreglar: una
linea reescrita es la cita de S15 con apariencia de arreglada).

## Estado sobre el arbol real

    python scripts/validate_plan_citations.py
    [OK] Plan citations: 738 citas historicas, 0 nuevas y 0 crecimientos (78 archivos en el inventario)

Y como check 8 de `run_all_validations.py --quick`: **8/8** (ver
`faseHotfix_validaciones.txt`). Nota lateral: al entrar el check 8, las etiquetas de
progreso del runner decian «/7» y se corrigieron a «/8» (los tres checks de modo
completo pasaron a [9/11]-[11/11] para no duplicar numeros).

## Auto-aplicacion de la regla (lo que el gate me impuso a mi)

Las filas nuevas de `10-analisis`, `06-checklist`, `09` y `dependencias-fases.md` que
esta sesion escribio **no contienen ninguna cita `archivo:linea`**: si la contuvieran,
el check 8 daria `CRECIO` y la fase no cerraria en verde. El verificador restringio al
propio autor de la norma, que es la prueba de que no es letra muerta.
