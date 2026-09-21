# FASE-A — AC17 (límites de cobertura) y corte de presupuesto R2.1

Medido el **2026-09-21** sobre HEAD `2deddee`. Artefacto primo: `informe.json`
→ `coverage_basis.families_not_covered[]`, `coverage_basis.excluded[]`.

## AC17 — `.agents/` intocado en escritura

```bash
git status --porcelain .agents/     # → (vacío)
```

Los dos documentos auditados no cambiaron ni un byte: workflow canónico **98.694** y template
**6.123** (mismos valores que `faseA_baseline_pre.txt` / la medición A7 del maestro). La corrección
de A1–A4 sigue siendo deuda **D1**, con instrucción literal del operador.

## Las cuatro familias que el verificador NO cubre (AC2, medidas, no enumeradas «de oído»)

| # | Familia | Medición del 2026-09-21 | Estado |
|---|---|---|---|
| (i) | **Prosa de conteo sin patrón** (`[N/M]` ni «check N»): «11 checks», «7 pasos», «pasa 4/4» | **3 coincidencias** en los dos documentos auditados tras quitar los corchetes ya auditados (comando: `grep -roE '[0-9]+ (checks\|validaciones\|pasos)' .agents/workflows/phased_project_executor.md`); **1** en el template excluido: `pasa 4/4`, que afirma un quick de 4 checks cuando mide 11 | **trabajo D1** (lint de prosa), límite declarado de FASE-A |
| (ii) | **Conteos fuera de los documentos de gobierno** | **245 instancias** en tres documentos: `AGENTS.md` **1** (`10/10 checks` — vencido: mide 11), `docs/GUIA_TECNICA.md` **107**, `docs/contributing/REGISTRY.md` **137** | **fuera del alcance del plan** (maestro §3); D1 decide |
| (iii) | **Pins de conteo en `tests/`** | **4 archivos** con etiquetas `[N/M]` dentro de `tests/`: `test_validate_plan_closure.py` assertiona `[5/7]` del hook, y **esta fase añadió 4 coincidencias del denominador 11** en `test_governance_numbers_reproduce_A1_A4.py` (el contrato AC1 escrito como literal). Además `tests/functional_test_gbp_integration.py` (3) y `tests/functional_test_hotel_visperas.py` (5) traen etiquetas propias | barrido por **AC5/AC16**; cubrirlo con el verificador es **D1**; el pin nuevo de esta fase tiene dueño declarado en `baseline-pre-post.md` |
| (iv) | **Fuentes dinámicas que no son etiqueta impresa** | **4.329** funciones de test en disk contra las **4.246** que publica `AGENTS.md` (diferencia por tráfico ajeno a este plan); umbrales (`≥0.8`, `≥95 %`) y tamaños (`263.973` bytes de A7) tampoco se contrastan | **límite permanente** de este verificador |

Ninguna de las cuatro se disfraza de cobertura: el verificador solo contrasta conteos **de checks**
contra una **etiqueta impresa por el código**.

## Exenciones de población (AC2: excluido ≠ silencio)

| Documento | Instancias detectadas | Motivo de la exclusión |
|---|---|---|
| `.agents/workflows/templates/prompt-fase-template.md` | 0 con patrón, 1 en prosa (`pasa 4/4`) | el maestro §1 fija como objetos auditados **dos** documentos; este tercero queda fuera y se mide aquí para que la exclusión sea legible. Su discrepancia de ruta (`evidence/fase-{N}/`) ya está declarada en `04-contrato-ejecucion.md` y viaja con **D1** |
| resto de `.agents/**` | no auditado | AC17: en FASE-A `.agents/` es solo lectura |
| menciones históricas congeladas | **8 instancias** | publicado en `historical_excluded[]` con su regla (H1/H2) y con la frase del workflow que la ampara (entrada v2.24.0 de `## Versiones`) |

## Corte de presupuesto (R2.1) — instrumento, corte y unidad declarada

* **Instrumento canónico**: `evidence/FASE-D/measure_iterations.py` (ruta legado declarada en el
  contrato), corte **hasta el commit de código**.
* **Precondición re-medida en esta sesión**: `find . -name "*.jsonl" -not -path "./venv/*" | wc -l`
  → **0**. El instrumento pide el transcript del cliente y no existe dentro del workspace: es la
  condición que ya documentó `D-V2.1` y que el contrato de este plan anticipó.
* **Consecuencia**: la métrica de iteraciones **se retira, no se estima** (prohibición del contrato
  §Corte). Se publica en su lugar una **unidad contable en disco**, con su comando:

  ```bash
  git status --porcelain | wc -l          # rutas tocadas por la fase
  wc -l scripts/validate_governance_numbers.py tests/quality_gates/governance_numbers/*.py | tail -1
  ```

  * **14 rutas** propias de la fase en el árbol de trabajo al cerrar (`git status --porcelain`,
    excluidas las ajenas de más abajo): el script, los 8 archivos de la selección de tests, los 9
    artefactos de `evidence/…/FASE-A/`, los 6 `.md` del plan re-escritos, el par del índice de
    lecciones regenerado y `docs/contributing/REGISTRY.md` + su `.last_doc_phase.json` (escritos por
    `log_phase_completion.py`, no a mano).
  * **933 líneas** de instrumento y **675** de la selección (675 = 576 en los 6 archivos `test_*`
    + 99 de `conftest.py`; `__init__.py` vacío)
    con el mismo comando (`wc -l scripts/validate_governance_numbers.py tests/quality_gates/governance_numbers/*.py`). El número que se publica como métrica
    de la fase es el conteo de funciones de test: **23**.
* **No comparable** con las cifras de iteraciones de otros planes: son unidades distintas
  (auto-reporte contable en disco vs `tool_use` medido). Se declara explícitamente y no se mezcla.

## Archivo ajeno ya sucio al abrir la sesión (declarado, no arrastrado)

`.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md` llegó **modificado por
otra sesión** (+18 líneas, decisión del operador del 2026-09-21: serializar el cierre del índice
compartido «hermano primero»). Esta fase **no** lo tocó, **no** lo commitea con su trabajo y **no**
lo revirtió. Su contenido sí afecta a este plan por el lado del orden de cierre: el hermano (este
plan) cierra antes de que JEV publique, y FASE-B de JEV se desbloquea en B+C de este plan — dato que
viaja al RELEASE, no a FASE-A.
