# FASE-VERIFY — pre-vuelo de la certificación

**Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22` · **Fase**: FASE-VERIFY · **Fecha**: 2026-10-24
**Objetivo**: certificar AC1–AC8 contra los artefactos que el sistema produjo (E2E-PRE + E2E + evidencia de fases), no contra los tests.

## Modo de ejecución y uso del presupuesto

- **DIRECTO, sin la excepción delegable.** El prompt autoriza un único `Agent` de solo lectura para enumerar los cuatro greps residuales de la Tarea 4 si el tope de 60 `tool_use` aprieta. **No se usó**: los cuatro greps se corrieron y se re-ejecutaron desde el hilo principal, cada uno con su población y su predicado escritos aquí. Ausencia de delegación = certificación directa, conforme a §4.6 del executor.
- Tope 60 `tool_use`: se declara **no verificable con instrumento** (`measure_iterations.py` es legado y no se probó contra este runtime — fila heredada de `10-analisis` §Seguimientos). Auto-reporte en unidad `tool_use`, **no comparable**.

## Insumos leídos (artefactos reales, no resúmenes de terceros)

| Insumo | Ruta |
|--------|------|
| Corrida post-cura | `evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-E2E/` (`corrida/`, `preflight.json`, `stdout-corrida.txt`, `tabla-antes-despues.md`, `inventario-paquete.json`) |
| Ensayo determinista | `evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-E2E-PRE/` (`judge/acta_revision.json`, `review/revision_honestidad.json`, `review/chequeo-por-documento.txt`, `package/`) |
| Baseline congelado | `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/corrida/donalfonsohotel/v4_audit/` |
| ZIP real publicado | `output/v4_complete/deliveries/donalfonsohotel_20261024.zip` (medido en disco, no desde un registro) |
| Evidencia por fase | `evidence/…/FASE-{A,B,C,D,E,F,H1,H2}/` (pares rojo/verde y crudos citados en la matriz) |

## Predicados usados (para que la certificación sea re-ejecutable)

1. **Claves del acta y del revisor**: lectura JSON de `summary.over_presentations`, `findings[]`, `verdict`, `conditional_reason`, `clauses`, `first_floor_rule`, `evidence_tier`, `package_evidence`. **No** se leyó `critical_count`: la clave no existe en `revision_honestidad.json` (medido: `has critical_count key: False`), tal como fija la sección «Claves exactas» del prompt.
2. **ZIP**: `sha256` y tamaño sobre los bytes del archivo en `deliveries/`, recuento de miembros y su generación por timestamp, cruzados contra `package_evidence` del acta.
3. **Greps residuales**: tres por poblaciones de fuente (`.py`/`.md`/`.yaml`/`.json` versionados, `__pycache__` excluido) y dos por **AST** (`SUPERPOSITION_FACTOR`, claves inglesas del perfil, `found=True` del stub), conforme a §4.10 del plan (a) y (b).
4. **Exit codes** leídos **sin tubería** (`> archivo 2>&1; echo "EXIT=$?"`) en los tres casos publicados: `spark`, `validate_benchmark_sync.py` y `run_all_validations.py --quick` — `L21`. En el primer intento del sync check se usó `| tail`, y el exit que imprimió era el de `tail`: se re-corrió y el crudo `03-sync-check-crudo.txt` es el que se cita.

## Hallazgos de FASE-E2E que se citan, no se re-litigan (fuera del alcance)

1. **El ZIP mezcla dos generaciones** — re-medido aquí con el mismo resultado que declaró la fase: 82 miembros, **26** con timestamp `20261012`, **28** con `20261024`, 28 sin timestamp de corrida. Queda como `L33`, dueño Operador. **No invalida AC7**: el AC se lee sobre existencia, `suppressed:false`, sha y tamaño del ZIP real.
2. **`v4_complete_report.hotel_name` sale del slug** — re-medido: `hotel_name = "Donalfonsohotel"` mientras el preflight declara `loader_devolvio = "Hotel Don Alfonso"` y `hotel_name = "Hotel Don Alfonso"`. Dueño Operador, no se certifica ni se corrige aquí.

## Lo que esta fase encontró y no estaba escrito (dos correcciones de sede, ninguna de producto)

1. **`brechas_en_ledger` no vive en `pain_ledger.json`.** El `01-plan-maestro.md` §1 (AC3 y AC7) y la Tarea 2 de este prompt la citan como clave de `pain_ledger.json`. Medido: `pain_ledger.json` publica `entries` (11) y `pain_ledger_version`; la clave `brechas_en_ledger` la publica **`revision_alineacion.json`** (`summary.brechas_en_ledger`, valor 11 en la corrida y en el baseline). La propiedad se certifica igual —la cifra es legible en un artefacto real—, pero **la sede del plan está mal nombrada** y se corrige en la matriz con la ruta verdadera. Va como lección nueva `L34`.
2. **El residuo del literal viejo está solo en bytecode.** 0 ocurrencias en la población de fuente; **6** en `.pyc` bajo `tests/**/__pycache__/`, artefacto de compilación **gitignorado** (`.gitignore:4`) forjado antes del renombre de FASE-C. No es residuo de código ni de tests; se declara con su causa y su vía de extinción (la próxima recompilación lo borra).

## Aislamiento y no-modificación

- **No** se modificó código, templates ni configuración. **No** se ejecutó `v4complete`. **No** se tocó `P6.5`, `T1_CERTIFIABLE_CLAUSES` ni archivos congelados: se verificó su estado por lectura (`T1_CERTIFIABLE_CLAUSES = ("P6.1", "P6.3", "P6.4", "P6.6")` en `judge.py`, fila `P6.5` `NOT_EVALUABLE` en las dos actas).
- Los únicos comandos con efecto en disco fueron de lectura y tres escrituras controladas: los crudos `01`/`02`/`03` de este directorio, la salida redirigida del sync check y `main.py spark` (centinela que no genera paquete).
- Cinco cortes declarados y verificados **sin commit**: implementación (lectura y medición) → verificación (los tres crudos y la selección de dientes re-corrida) → cierre documental (matriz, lecciones, `09`/`10`/`00`/`dependencias`/`README`) → listo para revisión → **espera de autorización del Operador para cualquier `git commit`**.
