---
description: Template de 00-lecciones-capitalizadas.md — output del Paso 0, se crea ANTES de diseñar fases
version: v1.1.0
---

# Template: Lecciones Capitalizadas (`00-lecciones-capitalizadas.md`)

> [!IMPORTANT]
> Este archivo se crea **antes** de escribir `01-plan-maestro.md` y los prompts de fase,
> y es el output verificable del Paso 0 del executor. No es un anexo del análisis final:
> el análisis (`10-analisis-post-implementacion.md`) se escribe cuando el plan ya cerró,
> y capitalizar a esas alturas ya no previene nada.

**Por qué existe (medido, no supuesto).** De 24 planes archivados, la sección
"Lecciones capitalizadas de planes anteriores" aparece en **6** (18 %), y la plantilla del
executor la marcaba `(si aplica)`. El plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` citaba
únicamente a su predecesor teniendo 24 planes más en el corpus; un defecto que hoy lleva
dueño y AC estaba documentado desde `EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31`.
Es L-R.1 en su forma exacta: *una regla que vive solo en el workflow y no en el artefacto
que la fase rellena, se cumple por coincidencia.*

---

## Estructura obligatoria

```markdown
# Lecciones Capitalizadas — [ID DEL PLAN]

> **Creado**: [fecha], antes de la FASE-1. **Actualizado**: al cierre de cada fase.
> **Plan**: [ID] · **Objetivo**: [una línea]

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado (n / IDs devueltos) |
|---|------|------------------|-------------------------------|
| Q1 | Índice generado (`.opencode/LECCIONES-INDEX.md`) | `grep -in "occupancy\|tier" .opencode/LECCIONES-INDEX.md` | [n IDs] |
| Q2 | Memoria de proyecto (`MEMORY.md`) | [términos buscados] | [n entradas] |
| Q3 | Notebook QMind `iah-cli-lecciones` | `qmind retrieve --nb <ID> -q "[consulta]" --format agent` | [n fuentes] |

**Regla**: la consulta debe ser copy-pasteable. "Revisé las lecciones" no es una consulta;
un comando que otra sesión puede re-ejecutar y obtener el mismo resultado, sí.
**Mínimo**: una consulta al corpus **completo** (índice o notebook), no solo al plan
predecesor. Consultar solo al predecesor es la señal de fallo de este documento.

## 2. Lecciones capitalizadas

| ID | Enunciado (una línea) | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|--------------------|-------------------------|-----------------|
| L-X1 | [enunciado] | `.opencode/plans/Archives/[PLAN]/10-analisis-post-implementacion.md` | [efecto concreto] | AC-N / Tarea N de FASE-Y / restricción del prompt |

**Regla anti-ceremonia**: la columna "Qué cambia" nombra un artefacto del plan (un AC, una
tarea, un archivo, una restricción). Si está vacía o dice "se tuvo en cuenta", la fila
**no cuenta**: no capitalizó nada, solo citó. Una fila con "no cambia nada, es contexto"
debe moverse a §3.

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|

**Obligatorio, mínimo 3 filas.** Es la única prueba de que se miró el corpus y no solo el
predecesor. Descartar con motivo es un resultado, no un fracaso.

## 4. Cobertura declarada de este documento

- Qué **sí** deja evidencia: las consultas re-ejecutables, las lecciones con dueño y ruta,
  los descartes con motivo.
- Qué **no** verifica el check mecánico: la **pertinencia**. Escribir el límite es
  obligatorio, y su forma debe poder comprobarse — una frase de las formas «no verifico…»,
  «no comprueba…» o «no garantiza…»:
  - [ ] Este archivo es verificado por `scripts/validate_lesson_capitalization.py`
    (check `[7/7]` del hook `scripts/git_hooks/pre-commit` y `[9/9]` de
    `run_all_validations.py --quick`), que comprueba **forma y trazabilidad**: consultas a
    una capa corpus-wide, ≥3 descartes, AC nombrado que existe en el plan maestro, ID con el
    dueño que publica el índice generado y ≥2 fuentes distintas. Un `[OK]` suyo significa
    «la forma exigida está», nunca «capitalicé bien».
  - [ ] Si el verificador aún no existiera, declararlo aquí con su dueño: una norma sin
    check automático solo es publicable si dice que no lo tiene (L-R.4).
- [ ] Actualizado al cierre de la última fase, y el write-back de QMind se ejecutó **antes**
  de archivar el plan (`git mv` a `Archives/`).
```

---

## Checklist del orquestador (al concebir el plan)

- [ ] `00-lecciones-capitalizadas.md` existe con §1, §2, §3 y §4 llenados → **C1, C2**
- [ ] §1 tiene ≥1 consulta al corpus completo, con el comando literal → **C3**
- [ ] §2 tiene ≥1 fila cuyo "Qué cambia" nombra un AC, tarea, archivo o restricción del plan
      → **C4**, que además exige que el AC nombrado **exista** en `01-plan-maestro.md`
- [ ] §3 tiene ≥3 descartes con motivo → **C5**
- [ ] §4 declara si existe verificador mecánico sobre este archivo → **C6** (nombrarlo y
      declarar el límite)
- [ ] Cada ID de §2 está definido en el corpus y atribuido al dueño que publica el índice, y
      las fuentes son ≥2 → **C7, C8**
- [ ] Los prompts de fase (§2 del executor) referencian las filas de §2 que les corresponden
      → **sin check mecánico**: el verificador no abre los prompts (límite declarado)

## Versión

- **v1.1.0** (2026-09-12): El §4 deja de enseñar la casilla «no tiene verificador mecánico
  (hasta que exista)», que el plan `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` convirtió en
  falsa al escribir `scripts/validate_lesson_capitalization.py`. Un template que manda declarar
  lo que ya dejó de ser cierto es la fosilización que el propio corpus nombra (L-NC10). El
  checklist marca ahora qué casilla sostiene cada check (C1–C8) y cuál sigue siendo humana.
- **v1.0.0** (2026-09-12): Primera versión. Sale de la evaluación del plan
  `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` (capitalización horizontal 0 %) y de la
  medición del corpus (6/24 planes con la sección, marcada `(si aplica)`).
