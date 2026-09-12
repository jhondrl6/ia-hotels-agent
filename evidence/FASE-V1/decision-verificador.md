# evidence/FASE-V1 — Decisiones Q1–Q5 y contrato del verificador

**Plan**: `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` · **Fecha**: 2026-09-12
**Regla de la fase**: decidir con medición antes de escribir una línea de código. Nada de este archivo se
hereda del §Deuda del plan predecesor: cada hecho está re-medido hoy (L-V.2).

## Q1 — Alcance → **hacia delante por fecha, con `Archives/` fuera** (elegida la opción 2 del usuario)

Medición:

| Comando | Resultado |
|---------|-----------|
| `find .opencode/plans -name "00-lecciones-capitalizadas.md" \| wc -l` | `1` (el de este plan) |
| `find .opencode/plans -maxdepth 1 -type d ! -name plans ! -name Archives \| wc -l` | `1` plan vivo |
| `find .opencode/plans/Archives -maxdepth 1 -type d ! -name Archives \| wc -l` | `25` archivados |
| `ls .opencode/plans/Archives \| grep -cE "2026-(09-(1[2-9]\|[23][0-9])\|1[0-2])"` | `0` archivados con fecha ≥ 2026-09-12 |
| `ls .opencode/plans/Archives \| grep -cvE "2026-[0-9]{2}-[0-9]{2}"` | `6` archivados **sin** fecha parseable |

Consecuencia fijada: `CUTOFF_DATE = date(2026, 9, 12)` (fecha de executor v2.22.0, medida con
`grep -nE "^- \*\*v2\.2[0-9]\.0" .agents/workflows/phased_project_executor.md`), `--cutoff` para medir sin
cambiar código, `Archives/` excluido, y **los exentos se listan en la salida** (C0): una exención silenciosa
es el defecto L-R.3 con otro nombre.

Descartado: *baseline de exentos* (cada plan nuevo exigiría editar un JSON, y un baseline mal mantenido
exonera en silencio) y *todos los planes* (25 fallos permanentes → el gate se ignora y el `--no-verify` se
vuelve costumbre).

## Q2 — Qué verifica un script sin juicio semántico → **C0–C8, todos de forma o trazabilidad**

Contrato completo en `01-plan-maestro.md` §3. Dos decisiones de diseño que salen de la medición:

- **C4 no mide longitud ni presencia de adjetivos**: comprueba que el token `AC-*` nombrado en §2 **existe
  en la tabla de ACs del maestro**. Es la diferencia entre «la fila tiene pinta de efecto» y «el efecto
  apunta a algo que el plan prometió».
- **C7/C8 leen el índice calculado en memoria**, no `.opencode/lecciones_index.json`. Coste medido de
  `build_lesson_index.build()`: **0,30 s** sobre 346 `.md` y 246 IDs. Motivo: ese JSON es la salida de otro
  gate (`[6/6]`); fiarle la conclusión al artefacto de otro verificador es tener un verde prestado.

Factibilidad medida antes de fijar umbrales (L-D3: con un número mal elegido, cumplir pasa por violar):
sobre el único `00-` real del repo — 18 filas en §2, **18/18** dueños coincidentes con el índice, 0 IDs sin
definición, **5 dueños distintos** (la ejecución de este propio archivo, 2026-09-12), 6 filas de §3 y 10
consultas en §1. Los umbrales (≥1 AC existente, ≥3 descartes, ≥2 dueños) los cumplen sin esfuerzo.

## Q3 — Dónde vive → **doble cableado: `[7/7]` del hook + `[9/9]` de `--quick`** (opción 1 del usuario)

| Hecho medido | Cómo |
|--------------|------|
| El hook versionado **es** el activo: 0 diferencias | `diff -q .git/hooks/pre-commit scripts/git_hooks/pre-commit` → `IDENTICOS` |
| `.pre-commit-config.yaml` no bloquea nada | Su propia decisión registrada (`.opencode/context/Historico/CONTEXT-DECISION-PRE-COMMIT-FRAMEWORK-2026-08-29.md`) lo dice con todas las letras: el archivo está «declarado completo (13 hooks) pero **sin enforcement real**» y «mientras tanto, la Opción 1 queda vigente: hook custom versionado (`scripts/git_hooks/`)». Corroborado en vivo: el único `pre-commit` en `.git/hooks/` es el script del proyecto, no el del framework |
| Precedente de la familia | `grep -c "validate_plan_closure\|build_lesson_index" scripts/run_all_validations.py` → `0`: los dos verificadores de disciplina de plan son **hook-only**; `validate_plan_citations.py` y `validate_opencode_refs.py` están en los dos sitios |
| Coste de renumerar | `grep -rln "run_all_validations" tests/` → ningún contract test afirma el número de checks (el único hit es `tests/commercial_documents/test_hook_pdf_generator.py`, que lo menciona en un mensaje) |

**Las 7 referencias al `[6/6]` del executor se clasifican, no se reescriben a ciegas:**

| Tipo | Dónde | Qué se hace |
|------|-------|-------------|
| Normativa (dice dónde vive el check hoy) | §R2.5, §R2.10 (regla del orden), §R2.10 (pata dura), §0 capa fría | Se actualiza a `[7/7]` con nota datada en FASE-V3 (AC-C1) |
| Histórica (relata una medición de un commit concreto) | §R2.10 «dos menciones nuevas… y `[6/6]` bloqueó ese commit», §R2.10 origen no-lección, changelog v2.23.1 y v2.23.0 | **No se toca**: es el registro de lo que pasó; reescribirlo sería falsificar la medición, el mismo criterio que declara `validate_plan_citations.py` en su docstring |

## Q4 — Qué declara no poder verificar

**La pertinencia.** El script verifica forma y trazabilidad; jamás «capitalicé bien». Escrito en tres
sitios para que lo vea quien solo tiene el artefacto (R2.4):

1. Docstring del script, sección `LÍMITE DECLARADO`.
2. Última línea de cada corrida: `cobertura: N planes en alcance / M exentos … | NO verifica pertinencia`.
3. §4 de cada `00-lecciones-capitalizadas.md` — y **C6 lo exige**: el §4 debe nombrar al verificador y
   contener una frase de límite. Si el día de mañana un check semántico existiera, C6 obligaría a actualizar
   la frase, que es la cura de la fosilización (L-NC10).

## Q5 — Cierre sin bump (opción 1 del usuario)

`VERSION.yaml` = `4.76.0` (medido) y el plan predecesor tiene reservado `FASE-RELEASE-4.77.0` en su propio
checklist. Este plan añade tooling de validación, no código de producción: la regla de validación-only del
executor indica subsection en `CHANGELOG.md`. Consecuencia verificable: `git diff` de FASE-V3 sobre
`VERSION.yaml` debe estar **vacío** (AC-A5).

## Consecuencia para el predecesor

El ítem **(i)** de su §Deuda («Deuda que queda (pertinencia)… verificador propio
(`validate_lesson_capitalization.py`), con su cobertura declarada. Dueño sugerido: nuevo tramo con AC»)
pasa a tener dueño ejecutante: este plan. FASE-V3 deja constancia en su `06-checklist-implementacion.md`
con fecha y resultado (AC-C2), porque una deuda re-asignada sin registro es la S-C3/S-C4/S-E2 del plan
`ESTABILIZACION-PRE-TRIBUNAL` (DA-V5: seis filas re-asignadas y nunca ejecutadas).

## Estado para FASE-V2

- Script nuevo: `scripts/validate_lesson_capitalization.py` (docstring con POR QUÉ / QUÉ VERIFICA / LÍMITE /
  uso; sin `--fix`; exit codes `0/1/2`).
- Tests: `tests/test_validate_lesson_capitalization.py` (una familia por check + los tres estados de R2.9).
- Cableado: `scripts/git_hooks/pre-commit` `[7/7]` y `run_all_validations.py` check `[9/9]` rápido.
- NR7 por check con las dos salidas en este directorio.
